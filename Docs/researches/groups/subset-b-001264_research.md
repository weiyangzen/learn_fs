# Research: subset-b-001264

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/stm32/stm32-mdma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/stm32/stm32-mdma.c

## Purpose
`stm32-mdma.c` is the DMAEngine provider for the STM32 MDMA controller. It exposes slave, cyclic, and memcpy capabilities, translating DMAEngine descriptors into STM32 MDMA channel registers and hardware linked-list descriptors. The driver supports software-triggered memory copies, hardware-request peripheral transfers, cyclic audio-style transfers, and a special memory-to-memory hardware-triggered mode where STM32 DMA can trigger MDMA through `peripheral_config`.

## Important APIs, Types, and Functions
The main device state is `struct stm32_mdma_device`, which owns the DMAEngine `dma_device`, MMIO base, clock, IRQ, channel count, request count, secure-channel mask, and AHB address masks. `struct stm32_mdma_chan` wraps `virt_dma_chan` and holds the active descriptor, slave config, parsed OF channel config, burst/width residue helpers, and busy state. Descriptors are `struct stm32_mdma_desc`, a flexible array of `struct stm32_mdma_desc_node`; each node owns a DMA-pool allocated, 64-byte aligned `struct stm32_mdma_hwdesc` matching the controller linked-list layout.

Key DMAEngine entry points are `stm32_mdma_alloc_chan_resources()`, `stm32_mdma_free_chan_resources()`, `stm32_mdma_prep_slave_sg()`, `stm32_mdma_prep_dma_cyclic()`, `stm32_mdma_prep_dma_memcpy()`, `stm32_mdma_issue_pending()`, `stm32_mdma_tx_status()`, `stm32_mdma_pause()`, `stm32_mdma_resume()`, `stm32_mdma_terminate_all()`, and `stm32_mdma_synchronize()`. The low-level transfer setup path runs through `stm32_mdma_set_xfer_param()`, `stm32_mdma_setup_xfer()`, `stm32_mdma_setup_hwdesc()`, and `stm32_mdma_start_transfer()`.

## Control Flow
Probe reads `dma-channels`, `dma-requests`, and optional `st,ahb-addr-masks`, maps registers, enables/reset the controller, initializes one virtual channel per hardware channel, filters out channels marked secure by `CCR.SM`, requests the shared IRQ, registers DMAEngine, and registers OF DMA translation. OF clients pass five cells: request line, priority, transfer config, mask address, and mask data. Those populate `chan_config`.

Transfer preparation allocates one MDMA descriptor per SG entry or period, computes CTCR/CCR/CTBR fields, chooses memory width and burst size based on alignment and length, selects AHB/AXI bus bits from address masks, fills hardware descriptors, and queues via virt-dma. `issue_pending()` marks issued descriptors and starts the first queued descriptor if the channel is idle. `stm32_mdma_start_transfer()` writes the first hardware descriptor into channel registers, clears stale status, enables the channel, and raises `SWRQ` for software-request memcpy.

The IRQ handler finds the channel from `GISR0`, validates enabled interrupt bits, clears transfer/error flags, completes descriptors on channel-transfer-complete, advances `curr_hwdesc` and invokes cyclic callbacks on block-transfer-complete, and starts the next queued descriptor after non-cyclic completion.

## State and Persistence
All persistent state is runtime kernel state: MMIO registers, DMA-pool descriptors, virt-dma queues, `chan->desc`, `curr_hwdesc`, `busy`, `mem_burst`, `mem_width`, channel configuration, and runtime PM clock state. No on-disk state is written. Runtime PM disables/enables the controller clock. System suspend refuses to proceed if any channel is still enabled, then force-suspends runtime PM; resume restores clocking through PM.

## Dependencies and Integration Points
The driver depends on DMAEngine, virt-dma, OF DMA, platform devices, clocks, reset controls, runtime PM, DMA pools, scatterlists, and MMIO polling helpers. It integrates with STM32 DT bindings via `st,stm32h7-mdma`, `dma-channels`, `dma-requests`, `st,ahb-addr-masks`, and the five-cell DMA specifier. It advertises `DMA_SLAVE`, `DMA_PRIVATE`, `DMA_CYCLIC`, and `DMA_MEMCPY`, 1/2/4/8-byte widths, burst residue granularity, and descriptor reuse.

## Risks and Edge Cases
Transfer setup rejects unsupported bus widths, non-power-of-two bursts, burst-width products above 128 bytes, block lengths above 64 KiB, invalid cyclic sizes, bad OF requests, and unsupported directions. Residue calculation depends on `CLAR` matching descriptor links and rounds to memory burst granularity; this is sensitive to linked-list state and the `m2m_hw` request-active path. Pause disables the channel and waits for channel-transfer-complete, so timeout handling can leave higher layers with `-EBUSY`. The `m2m_hw` mode mutates request/mask fields from `peripheral_config` and clears mask registers for some MEM_TO_DEV SG descriptors, so client-side contract correctness matters. Secure channels are filtered only at request time.

## Test Signals
Useful signals include successful probe registration, OF channel request validation, DMAEngine memcpy tests at sizes below and above 64 KiB, slave SG with several SG entries, cyclic transfer callbacks per period, pause/resume/terminate behavior, residue/in-flight bytes during active transfers, runtime PM get/put around channel resource allocation, suspend rejection while active, and error IRQ logging from `CESR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/stm32/stm32-mdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/sun4i-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/sun4i-dma.c

## Purpose
`sun4i-dma.c` is the DMAEngine provider for older Allwinner A10/sun4i and suniv/F1C100s DMA controllers. The hardware has separate normal DMA and dedicated DMA channel banks, no hardware linked-list support, and differing endpoint limits per SoC. The driver presents a virtual-channel DMAEngine interface for memcpy, slave SG, and cyclic transfers while serializing SG segments in software.

## Important APIs, Types, and Functions
`struct sun4i_dma_config` captures SoC variant properties: normal/dedicated channel counts, virtual channel counts, data-width encoders, burst conversion, SDRAM DRQ IDs, max burst, and reset availability. `struct sun4i_dma_dev` owns the DMAEngine device, physical channels, virtual channels, used-channel bitmap, MMIO base, clock, reset, IRQ, and global lock. `struct sun4i_dma_pchan` represents one hardware channel. `struct sun4i_dma_vchan` wraps `virt_dma_chan` plus endpoint, config, current physical channel, active promise, and active contract. `struct sun4i_dma_contract` is the virt-dma descriptor and contains lists of pending and completed `struct sun4i_dma_promise` segments.

Core functions include `generate_ndma_promise()`, `generate_ddma_promise()`, `generate_dma_contract()`, `__execute_vchan_pending()`, `configure_pchan()`, `sun4i_dma_prep_dma_memcpy()`, `sun4i_dma_prep_slave_sg()`, `sun4i_dma_prep_dma_cyclic()`, `sun4i_dma_interrupt()`, `sun4i_dma_tx_status()`, and `sun4i_dma_terminate_all()`.

## Control Flow
Probe selects variant data from OF, maps registers, obtains IRQ, enables the clock, optionally deasserts reset, sets DMAEngine capabilities, allocates physical channels, virtual channels, and the used bitmap, initializes normal and dedicated register bases, clears bootloader-left IRQ state, registers the IRQ, registers DMAEngine, and registers OF translation.

Clients request channels through two DMA specifier cells: dedicated-vs-normal and endpoint. `sun4i_dma_of_xlate()` validates both and stores them in the chosen vchan. Preparation builds a contract. Memcpy creates one promise using SDRAM-to-SDRAM DRQ IDs. Slave SG creates one promise per SG segment with endpoint DRQ/address mode fields. Cyclic preparation may double the hardware programmed period and use half-transfer interrupts to reduce reprogramming frequency.

`issue_pending()` calls `__execute_vchan_pending()`, which finds a suitable physical channel from the normal or dedicated bank, takes the first pending contract and promise, enables half/end interrupts, and writes channel registers. The IRQ handler processes half and end interrupt bits. End interrupts move the active promise to the completed list; cyclic contracts immediately select the next promise, reprogram the same pchan, and invoke the cyclic callback. Non-cyclic completions release the pchan and scan all vchans for more work.

## State and Persistence
The driver persists only in-memory state: promise and contract lists, physical-channel ownership bitmap, active `processing` and `contract` pointers, vchan endpoint/type config, and hardware channel registers. No persistent storage is used. Removing the driver disables the IRQ and unregisters OF DMA; devm allocations cover the rest.

## Dependencies and Integration Points
The driver depends on DMAEngine, virt-dma, OF DMA, platform devices, clocks, optional reset controls, spinlocks, bitmaps, and MMIO access. It exposes `DMA_PRIVATE`, `DMA_MEMCPY`, `DMA_CYCLIC`, and `DMA_SLAVE`, 1/2/4-byte widths, burst residue granularity, and a 4-byte copy alignment. Compatible strings are `allwinner,sun4i-a10-dma` and `allwinner,suniv-f1c100s-dma`.

## Risks and Edge Cases
SG and cyclic preparation have TODO paths where allocation failure after partial promise creation can leak earlier promises until caller cleanup is possible. The software-SG model depends on promptly handling interrupts; long IRQ work is mitigated by only looping once for newly pending interrupts. Dedicated DMA uses hard-coded SPI timing parameters for all supported slave transfers, which is documented as empirical. `sun4i_dma_tx_status()` only reports hardware residual for the first pending promise when a pchan exists. Termination clears configuration and disables IRQs, but stale interrupts can still arrive and are guarded by null `vchan` checks.

## Test Signals
Exercise probe on both A10 and F1C100s variants, OF xlate rejection for invalid type/endpoint, memcpy through normal and dedicated channels, slave SG with multiple segments, cyclic audio-style callbacks with half interrupts enabled, residue reporting during active and queued contracts, terminate while IRQs are pending, and channel reuse after release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/sun4i-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/sun6i-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/sun6i-dma.c

## Purpose
`sun6i-dma.c` is the DMAEngine provider for newer Allwinner DMA controllers starting with A31 and covering A23/A83T/H3/V3s/A64/A100/H6/D1-style variants. Unlike the sun4i driver, this hardware supports linked-list items, so SG and cyclic transfers are represented as DMA-pool allocated LLIs consumed by the controller.

## Important APIs, Types, and Functions
`struct sun6i_dma_config` holds variant-specific channel/request/vchan counts, clock-autogate callback, register field encoders for burst, DRQ and mode, supported burst lengths and address widths, and flags for high address and MBUS clock support. `struct sun6i_dma_dev` owns the DMAEngine device, MMIO, clocks, reset, IRQ, tasklet, pending vchan list, descriptor pool, physical channels, virtual channels, and variant config. `struct sun6i_dma_lli` is the hardware descriptor with a CPU-only `v_lli_next`. `struct sun6i_desc` wraps the first physical and virtual LLI pointers in a virt-dma descriptor. `struct sun6i_pchan` tracks current and completed descriptors for a hardware channel; `struct sun6i_vchan` tracks the virtual channel, slave config, pending-list node, port, IRQ type, assigned physical channel, and cyclic flag.

Key functions are `sun6i_dma_lli_add()`, `sun6i_dma_start_desc()`, `sun6i_dma_tasklet()`, `sun6i_dma_interrupt()`, `set_config()`, `sun6i_dma_prep_dma_memcpy()`, `sun6i_dma_prep_slave_sg()`, `sun6i_dma_prep_dma_cyclic()`, `sun6i_dma_tx_status()`, pause/resume/terminate functions, and `sun6i_dma_probe()`.

## Control Flow
Probe obtains variant data, maps registers, gets clocks and reset, creates the LLI DMA pool, initializes pending and channel structures, reads or derives channel/request/vchan counts, deasserts reset, enables clocks including optional MBUS, requests the IRQ, registers DMAEngine and OF DMA, and enables variant clock autogating if needed.

OF translation takes one cell, the DRQ port, validates it against `max_request`, allocates any slave channel, and stores the port. Preparation allocates one or more LLIs. Memcpy creates a single SDRAM-to-SDRAM LLI. Slave SG creates an LLI per SG entry with direction-dependent DRQ and linear/IO modes. Cyclic creates one LLI per period and links the last physical LLI back to the first.

`issue_pending()` adds the vchan to the controller pending list and schedules the tasklet. The tasklet first advances channels whose previous descriptor completed, then assigns free physical channels to pending vchans, and starts descriptors by programming interrupt type, LLI address, and channel enable. The IRQ handler reads/clears status registers, invokes cyclic callbacks on package interrupts, completes non-cyclic descriptors on queue interrupts, marks `pchan->done`, and schedules the tasklet to continue or free the channel.

## State and Persistence
State is in memory and MMIO only: LLI chains in the DMA pool, pending vchan list, pchan/vchan associations, active and done descriptors, cyclic flag, IRQ type, and tasklet shutdown flag. No file or disk state is written. Remove unregisters OF/DMAEngine, disables interrupts, kills tasklets, disables clocks, asserts reset, and removes channels from the DMAEngine list.

## Dependencies and Integration Points
The driver uses DMAEngine, virt-dma, OF DMA, platform devices, clocks, reset controls, DMA pools, tasklets, spinlocks, and Allwinner DT compatibles for A31, A23, A83T, H3, V3s, D1, A64, A100, and H6. It advertises private memcpy/slave/cyclic DMA with variant-specific address widths, burst support, and burst residue granularity. Newer variants can encode high address bits in LLI `para` and may require an MBUS clock.

## Risks and Edge Cases
`sun6i_dma_tx_status()` calls `to_sun6i_desc(&vd->tx)` before checking whether `vd` is non-null, so active-descriptor status paths must avoid null dereference assumptions. Cyclic descriptors deliberately form a physical ring; free paths walk the CPU `v_lli_next` chain, which remains non-cyclic, so preserving that invariant is important. High address handling only stores two upper bits. Pause of an unassigned vchan removes it from the pending list; resume re-adds it only when issued descriptors exist. Interrupt channel indexing shifts status by groups of eight and depends on `num_pchans` and status layout matching the hardware.

## Test Signals
Validate probe across variants with fixed and DT-derived channel counts, MBUS-clock variants, high-address transfers, memcpy, slave SG with multiple LLIs, cyclic period callbacks, pause/resume before and after pchan assignment, terminate of cyclic and non-cyclic transfers, residue for pending versus active descriptors, and tasklet shutdown during remove/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/sun6i-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/switchtec_dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/switchtec_dma.c

## Purpose
`switchtec_dma.c` is a PCI DMAEngine driver for Microchip Switchtec PCIe switch DMA engines. It exposes private memcpy channels backed by hardware submission and completion queues in coherent memory, with MSI-X interrupts for per-channel completions and channel status/pause errors.

## Important APIs, Types, and Functions
`struct switchtec_dma_dev` owns the DMAEngine device, RCU-protected PCI device pointer, mapped BAR, channel array, channel count, and status IRQ. `struct switchtec_dma_chan` owns one DMAEngine channel, MMIO pointers for hardware and firmware channel registers, control/submit/completion locks, tasklet, ring state, SQ/CQ coherent memory, queue indices, phase tag, CID counter, IRQ, and software descriptor ring. Hardware queue entries are `struct switchtec_dma_hw_se_desc`; completions are `struct switchtec_dma_hw_ce`; software descriptors are `struct switchtec_dma_desc`.

Important functions include channel control helpers `halt_channel()`, `unhalt_channel()`, `reset_channel()`, `pause_reset_channel()`, `enable_channel()`, `disable_channel()`, ring processing `switchtec_dma_cleanup_completed()`, abort/stop/synchronize functions, descriptor preparation `switchtec_dma_prep_desc()` and `switchtec_dma_prep_memcpy()`, submission `switchtec_dma_tx_submit()`, doorbell `switchtec_dma_issue_pending()`, channel resource allocation/free, PCI channel enumeration, and `switchtec_dma_probe()`/`remove()`.

## Control Flow
PCI probe enables the device, sets a 64-bit coherent DMA mask, requests BAR regions, enables bus mastering, maps BAR0, initializes MSI-X vectors, requests a channel-status IRQ, reads channel count, initializes each channel, and registers a private DMAEngine memcpy device. Channel initialization maps per-channel firmware and hardware register windows, pause-resets the channel, programs performance tuning fields, configures an SE threshold, requests the per-channel completion IRQ from firmware `int_vec`, initializes locks/tasklet, and adds the DMA channel to the DMAEngine list.

Channel resource allocation creates coherent SQ and CQ rings, initializes all software descriptors to point into SQ slots, writes SQ/CQ base and size registers, enables/resets/unhalts the hardware channel, marks rings active, initializes cookies, and logs performance config. `prep_memcpy()` validates maximum size and fills the next available SQ descriptor under `submit_lock`; `tx_submit()` advances `head` with release ordering and assigns a cookie. `issue_pending()` writes the software head to hardware `sq_tail` because the device names the producer index oppositely.

Completions arrive through an IRQ tasklet or polling in `tx_status()`. `switchtec_dma_cleanup_completed()` compares CQ phase tags, computes residue/result, logs CE details on errors, advances CQ head to hardware, handles out-of-order completions by marking descriptors completed, and completes contiguous descriptors from `tail` with callbacks and unmapping.

## State and Persistence
All state is volatile: PCI BAR registers, coherent SQ/CQ memory, descriptor ring slots, head/tail/cq_tail/phase_tag/cid, active flags, and RCU `pdev` lifetime. No persistent storage is used. Removal releases channel IRQs, stops channels, nulls the RCU PCI pointer, synchronizes RCU, unregisters DMAEngine, unmaps BAR, releases PCI regions, and disables the device.

## Dependencies and Integration Points
The driver depends on PCI/MSI-X, DMAEngine, coherent DMA allocation, tasklets, spinlocks, RCU, circular-buffer helpers, MMIO polling, and Switchtec PCI IDs/class matching. It registers only `DMA_MEMCPY` and `DMA_PRIVATE`, with 8-byte copy alignment. The PCI ID table covers Microsemi/Microchip Switchtec PFX/PSX/PFXA/PSXA generations and EFAR IDs with class-code filtering.

## Risks and Edge Cases
The ring constants are large and used as masks, so power-of-two assumptions are fundamental. `SWITCHTEC_DMA_RING_SIZE`, `SQ_SIZE`, and `CQ_SIZE` are byte-size constants reused as entry counts, which is intentional only if hardware queue size fields and allocation sizing agree. `switchtec_dma_prep_desc()` leaves `submit_lock` held for `tx_submit()`; caller misuse would deadlock, though DMAEngine expects this pattern. Completion handling supports out-of-order CEs but only invokes callbacks for contiguous completed descriptors from tail. Terminate pauses/resets and disables completion processing; `synchronize()` aborts descriptors and reinitializes hardware/software indices. RCU guards hot-unplug/removal, but many register paths return early if `pdev` is gone.

## Test Signals
Test PCI probe/remove, MSI-X vector allocation, per-channel allocation/free cycles, memcpy sizes up to and above `SWITCHTEC_DESC_MAX_SIZE`, ring-full behavior, interrupt-driven and polling completion, out-of-order completion ordering, CE error logging/result mapping, pause/resume, terminate/synchronize reuse, and removal while rings are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/switchtec_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/tegra186-gpc-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/tegra186-gpc-dma.c

## Purpose
`tegra186-gpc-dma.c` is the DMAEngine provider for NVIDIA Tegra GPCDMA controllers on Tegra186, Tegra194, and Tegra234. It supports slave SG, cyclic peripheral DMA, memory copy, and memset using per-channel MMIO programming rather than hardware descriptor rings. It also programs memory-controller stream IDs for IOMMU integration.

## Important APIs, Types, and Functions
`struct tegra_dma_chip_data` captures SoC-specific channel count, channel register stride, maximum count, pause support, and termination method. `struct tegra_dma` owns the DMAEngine device, reset, base address, channel mask, stream-ID reservation bitmaps, and flexible array of channels. `struct tegra_dma_channel` wraps `virt_dma_chan`, channel identity, IRQ, slave ID, active descriptor, slave config, stream ID, status, and channel base offset. `struct tegra_dma_desc` is a virt-dma descriptor containing an array of `struct tegra_dma_sg_req`; each request stores a segment length and the exact channel register values to program.

Core paths are `tegra_dma_slave_config()`, `tegra_dma_prep_slave_sg()`, `tegra_dma_prep_dma_cyclic()`, `tegra_dma_prep_dma_memcpy()`, `tegra_dma_prep_dma_memset()`, `tegra_dma_issue_pending()`, `tegra_dma_start()`, `tegra_dma_configure_next_sg()`, `tegra_dma_isr()`, `tegra_dma_tx_status()`, `tegra_dma_terminate_all()`, pause/resume helpers, and probe/remove/PM functions.

## Control Flow
Probe matches chip data from OF, allocates channel storage, maps registers, resets the controller, obtains an IOMMU stream ID, reads `dma-channel-mask` or uses the default mask reserving channel 0, initializes enabled channels with IRQ numbers, base offsets, names, virt-dma state, and programmed stream IDs, registers DMAEngine capabilities, and registers OF DMA translation. OF translation allocates any slave channel and stores the request slave ID from the first specifier cell.

Preparation validates configuration and alignment, reserves slave IDs per direction to prevent conflicting MEM_TO_DEV or DEV_TO_MEM users, computes CSR/MMIOSEQ/MCSEQ fields, and records per-segment register images. Memcpy and memset require word-aligned addresses/lengths and single descriptors. Slave SG and cyclic split into one request per SG entry or period. Cyclic clears `ONCE` and wraps `sg_idx` on completion.

`issue_pending()` starts the next virt-dma descriptor if no descriptor is active. `tegra_dma_start()` writes WCOUNT, CSR, source/destination/high-address, fixed pattern, MMIO sequence, MC sequence, then enables the channel. The ISR decodes and clears errors, handles EOC, updates bytes transferred, invokes cyclic callbacks and preloads the next cyclic segment, or advances SG segments until completion. Completion frees the slave-ID reservation and clears the active descriptor.

## State and Persistence
State is volatile: channel registers, active descriptor pointer, SG index/count, bytes requested/transferred, pause status, channel mask, programmed stream IDs, and direction-specific slave-ID reservation bitmaps. No persistent storage is used. System suspend rejects busy channels. Resume resets the controller and reprograms each enabled channel stream ID.

## Dependencies and Integration Points
The driver uses DMAEngine, virt-dma, OF DMA, platform devices, resets, interrupts, IOMMU stream ID lookup, Tegra memory-controller DT bindings, MMIO polling, and scatterlists. It registers `DMA_SLAVE`, `DMA_PRIVATE`, `DMA_MEMCPY`, `DMA_MEMSET`, and `DMA_CYCLIC`, with 4-byte copy/fill alignment and burst residue granularity. Compatible strings are `nvidia,tegra186-gpcdma`, `nvidia,tegra194-gpcdma`, and `nvidia,tegra234-gpcdma`.

## Risks and Edge Cases
The driver requires 4-byte aligned memory addresses and lengths and rejects segments above the SoC maximum. Several error returns after `tegra_dma_sid_reserve()` in slave/cyclic preparation do not visibly free the reservation before returning, so repeated bad preparations for a slave ID can be a risk. Termination behavior differs by SoC: Tegra186 changes request selection and waits for TX/RX inactive, Tegra194 pauses, and Tegra234 ignores pause errors to recover flush states. `tegra_dma_get_residual()` uses EOC and word count state, which is delicate for cyclic transfers that may already have advanced. Pause/resume are exposed only for chips with hardware pause support.

## Test Signals
Validate probe with channel masks and stream-ID programming, OF xlate slave ID assignment, word-alignment rejection for memcpy/memset/slave, slave ID reservation conflicts by direction, SG chaining, cyclic callbacks and next-period preprogramming, pause/resume on Tegra194/234, Tegra186 stop-client termination, residue while running and paused, error register decode paths, suspend busy rejection, and resume stream-ID restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/tegra186-gpc-dma.c -->
