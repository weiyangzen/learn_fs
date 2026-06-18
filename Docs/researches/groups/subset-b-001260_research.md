# subset-b-001260 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ppc4xx/adma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ppc4xx/adma.c Research

## Purpose
`adma.c` is the PPC440SPe asynchronous DMA and RAID acceleration driver. It binds the two PPC440SPe DMA engines and the XOR engine into Linux dmaengine/async_tx so clients can offload memcpy, XOR, RAID5 validation, and RAID6 P/Q generation and validation. It also performs platform-wide RAID hardware setup for the I2O and Memory Queue DCR blocks and exposes driver sysfs controls for RAID6 activation and Galois polynomial selection.

## Important APIs, Types, and Functions
The driver-private objects are declared in `adma.h` and used throughout this file: `struct ppc440spe_adma_device` wraps one hardware engine and embedded `struct dma_device`; `struct ppc440spe_adma_chan` owns the single dmaengine channel, descriptor slot pool, active chain, tasklet, and helper DMA pages; `struct ppc440spe_adma_desc_slot` is the software wrapper around either a DMA CDB or XOR CB.

Public integration is through the dmaengine methods populated by `ppc440spe_adma_init_capabilities()`: `ppc440spe_adma_alloc_chan_resources()`, `ppc440spe_adma_free_chan_resources()`, `ppc440spe_adma_tx_submit()`, `ppc440spe_adma_issue_pending()`, `ppc440spe_adma_tx_status()`, `ppc440spe_adma_prep_dma_memcpy()`, `ppc440spe_adma_prep_dma_xor()`, `ppc440spe_adma_prep_dma_xor_zero_sum()`, `ppc440spe_adma_prep_dma_pq()`, `ppc440spe_adma_prep_dma_pqzero_sum()`, and `ppc440spe_adma_prep_dma_interrupt()`. `ppc440spe_async_tx_find_best_channel()` is exported for async_tx channel selection and ranks channels by capability, idleness, RAID6 enable state, and whether RXOR-friendly source layout is available.

Low-level descriptor helpers initialize and patch hardware blocks: `ppc440spe_desc_init_memcpy()`, `ppc440spe_desc_init_xor()`, `ppc440spe_desc_init_dma01pq()`, `ppc440spe_desc_init_dma2pq()`, `ppc440spe_desc_init_dma01pqzero_sum()`, source/destination/multiplier setters, link setters, and RXOR cursor helpers. Platform bring-up is split between `ppc440spe_configure_raid_devices()`, `ppc440spe_adma_probe()`, IRQ setup/release helpers, and `ppc440spe_adma_init()`/`ppc440spe_adma_exit()`.

## Control Flow
Driver initialization runs at `arch_initcall()`. `ppc440spe_configure_raid_devices()` finds the I2O and MQ nodes, maps DCRs, allocates shared DMA FIFO backing memory, resets I2O/DMA, programs FIFO base registers, sets the MQ HB alias and default RAID polynomial, and initializes global engine status. The platform driver then probes compatible DMA and XOR nodes. Probe determines whether the node is DMA0/DMA1 or XOR, claims and maps MMIO, allocates a coherent descriptor pool sized for the engine, resets/configures hardware, creates one dmaengine channel, allocates helper P/Q pages for DMA engines, adds the channel to the global async_tx list, requests end-of-transfer and error IRQs, sets dmaengine capabilities, and registers the dma_device.

Client control flow starts with a prepare method. Each prepare path calculates required slots, allocates contiguous free descriptor slots from `all_slots`, initializes operation-specific CDB/CB fields, fills DMA addresses, byte counts, and RAID multipliers, then returns a `dma_async_tx_descriptor`. `tx_submit` assigns a cookie, splices the descriptor group into the channel chain, links it after the prior tail when needed, increments pending operation count, and appends to hardware when the threshold is reached. `issue_pending` also appends and enables the hardware engine.

Completion enters through `ppc440spe_adma_eot_handler()` or the shared DMA error handler. EOT acknowledges DMA FIFO or XOR status, updates zero-sum result bits when DCHECK status reports a mismatch, clears RXOR activity, and schedules the channel tasklet. The tasklet walks the chain up to the current hardware descriptor, invokes callbacks and dependencies, updates `completed_cookie`, and frees acknowledged slots. XOR append has extra refetch handling because hardware may need a software-linked CB list patched and refetched after the core becomes idle.

## State and Persistence
No filesystem state is persisted. Long-lived state is kernel and hardware state: global engine init codes, global channel list, shared DMA FIFO buffer, MQ DCR mapping, RAID6 enabled flag, selected polynomial register, RXOR active bit, last submitted/linked descriptor pointers, per-device coherent descriptor pools, per-channel slot lists and hardware chains, and helper P/Q pages. Runtime request state lives in descriptor slots until completion and cleanup. Sysfs attributes expose and mutate hardware state: `devices` reports engine probe status, `enable` writes the RAID6 key and runs a self-test, and `poly` reads or changes the RAID polynomial on PPC440SPe variants where it is configurable.

## Dependencies and Integration Points
The file depends on Linux dmaengine, async_tx, DMA mapping, OF platform probing, IRQ APIs, tasklets, PowerPC DCR access, I2O/MQ DCR register definitions, and local hardware layouts from `adma.h`, `dma.h`, and `xor.h`. It registers `ibm,dma-440spe` and `amcc,xor-accelerator` devices. Its main consumers are async_tx RAID code and any dmaengine clients using the exported channel capabilities. It also relies on the platform device tree containing compatible I2O and MQ nodes; without those global nodes the driver cannot configure the shared DMA/RAID infrastructure.

## Risks and Edge Cases
Descriptor lifetime is the main risk. Slot allocation requires contiguous free slots and carefully marks `slots_per_op`, `slot_cnt`, and `group_head`; cleanup must not free the currently executing descriptor or unprocessed zero-sum DCHECK descriptors. Hardware chain linking is fragile because DMA engines use command FIFOs while XOR uses linked CBs and refetch bits; stale `xor_last_submit`, `xor_last_linked`, or `do_xor_refetch` state can stall or corrupt chains. RAID6 paths rely on RXOR source contiguity, 512-byte block alignment, correct region detection, and explicit multiplier handling for P parity where a zero multiplier is not safe on this hardware. Many error paths call `BUG()` for impossible descriptor layouts, so malformed inputs or unanticipated hardware state are fatal rather than recoverable. Sysfs RAID6 enabling depends on a magic key and a self-test; until enabled, PQ channel selection deliberately rejects RAID6 acceleration.

## Test Signals
Useful signals include successful probe of all three engines in `devices`, `enable` accepting the RAID6 key and passing `ppc440spe_test_raid6()`, dmaengine memcpy and XOR tests, async_tx RAID5/RAID6 parity generation and validation, PQ and PQ zero-sum tests with P-only, Q-only, P+Q, destination-as-source, and non-contiguous source layouts, interrupt/error IRQ handling under load, slot exhaustion/reuse, module remove cleanup, and sysfs polynomial read/write behavior on PPC440SPe versus fixed-polynomial PPC440SP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ppc4xx/adma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ppc4xx/adma.h -->
# sources/distributed-fs/ceph-client/drivers/dma/ppc4xx/adma.h Research

## Purpose
`adma.h` defines the software object model and PPC440SPe ADMA constants used by `adma.c`. It bridges the generic Linux dmaengine/async_tx types with the PPC440SPe DMA and XOR hardware descriptors declared in `dma.h` and `xor.h`.

## Important APIs, Types, and Functions
The conversion macros `to_ppc440spe_adma_chan()`, `to_ppc440spe_adma_device()`, and `tx_to_ppc440spe_adma_slot()` recover driver-private containers from generic dmaengine objects. Constants define engine IDs (`PPC440SPE_DMA0_ID`, `PPC440SPE_DMA1_ID`, `PPC440SPE_XOR_ID`), maximum byte counts, default RAID polynomial, operation threshold, and the RXOR-active bit.

`struct ppc440spe_adma_device` contains the parent `struct device`, mapped DMA/XOR/I2O register pointers, hardware id, coherent descriptor pool virtual and DMA addresses, pool size, IRQ numbers, and embedded `struct dma_device`. `struct ppc440spe_adma_chan` contains the channel lock, active chain, all-slot pool, last-used cursor, pending count, hardware-chain initialization flag, completion tasklet, helper pages, and helper DMA addresses. `struct ppc440spe_rxor` is a cursor for encoding RXOR source groups. `struct ppc440spe_adma_desc_slot` wraps one hardware descriptor, async_tx descriptor, list nodes, grouping metadata, source/destination counts, flags, RXOR reverse bits, RXOR cursor, and zero-sum/CRC result pointer.

## Control Flow
The header itself has no executable control flow, but its fields directly drive `adma.c` flows. Probe fills `ppc440spe_adma_device` and creates one `ppc440spe_adma_chan`. Channel resource allocation creates many `ppc440spe_adma_desc_slot` objects and attaches them to `all_slots`. Prepare functions form transaction groups through `group_list`, `group_head`, `slot_cnt`, and `slots_per_op`. Submit and completion move those slots through the channel `chain` and use flags such as `PPC440SPE_DESC_WXOR`, `PPC440SPE_DESC_RXOR`, `PPC440SPE_DESC_PCHECK`, and `PPC440SPE_DESC_QCHECK` to interpret hardware results.

## State and Persistence
All definitions describe in-memory kernel state. Descriptor slots persist for the lifetime of allocated channel resources and are reused across submitted transactions. Device and channel structures persist from probe until remove. The header does not define filesystem persistence or user-visible ABI, but the structures back the sysfs-driven RAID6 enable and polynomial state implemented in `adma.c`.

## Dependencies and Integration Points
This header includes Linux types plus the local hardware layout headers `dma.h` and `xor.h`. It integrates with dmaengine through embedded `struct dma_device`, `struct dma_chan`, and `struct dma_async_tx_descriptor`; with async_tx through descriptor flags and callback/cookie state; and with PowerPC PPC440SPe hardware through the DMA CDB and XOR CB storage referenced by `hw_desc`.

## Risks and Edge Cases
The descriptor metadata is compact and stateful. Incorrect `slot_cnt`/`slots_per_op` values can make cleanup free the wrong slots. `reverse_flags[8]` assumes enough bits for RXOR operand tracking across the supported descriptor layout. The union of zero-sum and CRC result pointers relies on operation flags to interpret it correctly. Engine IDs are used as array indices in `adma.c`, so they must stay aligned with `PPC440SPE_ADMA_ENGINES_NUM` and the global arrays.

## Test Signals
Build coverage for the PPC440SPe ADMA driver is the primary header test. Runtime evidence comes indirectly from descriptor allocation/reuse, successful dmaengine callbacks, RAID6 self-test, zero-sum result reporting, and absence of slot accounting assertions during mixed memcpy/XOR/PQ traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ppc4xx/adma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ppc4xx/dma.h -->
# sources/distributed-fs/ceph-client/drivers/dma/ppc4xx/dma.h Research

## Purpose
`dma.h` describes the PPC440SPe DMA engine command descriptor format, DMA/I2O register maps, and bit definitions used by the ADMA driver. It is the low-level hardware contract for DMA0 and DMA1.

## Important APIs, Types, and Functions
There are no functions. Important constants include two DMA engines, two maximum destinations, FIFO sizes, FIFO enable bit, DMA priority settings, force-alignment configuration, UIC interrupt bits, I2O interrupt mask bits, CDB address/status masks, CDB opcodes (`MV_SG1_SG2`, `MULTICAST`, `DFILL128`, `DCHECK128`), cued XOR address markers, multiplier and RXOR region offsets, and SG role selectors.

`struct dma_cdb` is the 32-byte command descriptor block consumed by DMA0/DMA1. It carries attributes, opcode, SG1 source address, byte count, and SG2/SG3 destination or check operands. `struct dma_regs` maps the DMA engine MMIO region, including command/status FIFO ports and pointers, destination status, configuration, active command pointer, byte pointer registers, error address/status, operation, and FIFO-size register. `struct i2o_regs` maps the shared I2O block used for interrupt masking and FIFO base/size configuration.

## Control Flow
This header is declarative, but `adma.c` uses it throughout control flow. Probe programs `fsiz`, `cfg`, and `dsts` through `struct dma_regs`. Submit writes CDB physical addresses with `DMA_CDB_NO_INT` into the command FIFO. Completion reads status FIFO entries, masks physical addresses with `DMA_CDB_ADDR_MSK`, interprets `DMA_CDB_STATUS_MSK` for zero-sum failures, and clears DMA error status. RAID6 descriptor setup encodes cued XOR base/HB addresses, multipliers, and RXOR regions into the upper SG fields defined here.

## State and Persistence
The header defines hardware-visible state layout rather than persistent software state. CDB contents live in coherent DMA memory allocated by `adma.c`, while register fields persist in the device until reset, remove, or reconfiguration. I2O FIFO base programming points at the shared DMA FIFO backing buffer allocated during global initialization.

## Dependencies and Integration Points
It depends only on Linux fixed-width types. It is included by `adma.h`, and therefore by `adma.c`. It integrates with PPC440SPe hardware documentation, the I2O node discovered from device tree, and PowerPC register accessors used by the driver. The `CONFIG_440SP` conditional changes cued multiplier and region bit placement, so the same driver source can target PPC440SP and PPC440SPe variants.

## Risks and Edge Cases
The structures must match hardware offsets exactly. Any padding or field width mismatch would make MMIO and descriptor programming unsafe. The CDB address mask assumes 16-byte descriptor alignment. The conditional multiplier offsets are especially sensitive because RAID6 math correctness depends on encoding coefficients into the exact bits expected by the hardware. FIFO size constants are used to derive descriptor pool size and I2O FIFO backing size, so changes affect memory allocation and command FIFO capacity.

## Test Signals
Compile tests for PPC440SP/PPC440SPe configurations check the conditional constants. Runtime signals include correct DMA FIFO setup, successful CDB submission/completion, zero-sum status reporting, no DMA destination status errors, and RAID6 parity correctness across WXOR/RXOR paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ppc4xx/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ppc4xx/xor.h -->
# sources/distributed-fs/ceph-client/drivers/dma/ppc4xx/xor.h Research

## Purpose
`xor.h` describes the PPC440SPe XOR accelerator command block and register layout. It supports the XOR engine portion of the ADMA driver, including linked command blocks, completion interrupts, error status, refetch, and up to 16 operands per command.

## Important APIs, Types, and Functions
There are no functions. Constants define one XOR engine, the maximum operand count, command block control bits (`LNK`, `TGT`, `CBCE`, result-not-zero enable, XNOR), operand-count mask, status bits, control set/reset bits, and interrupt-enable bits.

`struct xor_cb` is the packed hardware command block. It contains control, byte count, status, target address, link address, and sixteen packed operand high/low address entries. `struct xor_regs` maps operand address registers, command block control/status/target/link registers, control set/reset registers, current command block address, PLB config, interrupt enable, parity error count, status, and revision ID.

## Control Flow
`adma.c` allocates coherent `struct xor_cb` objects from the device descriptor pool. XOR prepare functions set `cbc`, `cbbc`, target address, operands, and optional completion interrupt bits. Submit and append flows link command blocks using `cblal`/`cblah`, program the first command block address into `cblalr`/`cblahr`, and start or refetch the engine using `XOR_CRSR_XAE_BIT` and `XOR_CRSR_RCBE_BIT`. IRQ handling reads and clears `sr`, retries read-timeout cases by resubmitting the current address, and appends pending software-linked command blocks when the core becomes idle.

## State and Persistence
State exists in coherent command block memory and in the XOR MMIO register file. The current command block address and status register persist until hardware advances or software clears/resets them. No filesystem state is involved.

## Dependencies and Integration Points
The header depends on Linux types and is included by `adma.h`. It integrates with dmaengine through `adma.c` and with the `amcc,xor-accelerator` device tree node. Its packed layouts are hardware ABI, not normal C-only data structures.

## Risks and Edge Cases
Packed structure layout must remain byte-accurate. Operand count is limited to 16, so `adma.c` must split larger XOR operations into multiple slots. Link handling is sensitive because the driver may update software `hw_next` links before hardware link bits are patched. Error bits for invalid command blocks, invalid commands, parity, and read PLB timeout need clear handling to avoid stuck chains.

## Test Signals
Signals include successful XOR engine probe/reset, dmaengine XOR tests with more and fewer than 16 sources, command block completion interrupts, linked-list refetch under queued traffic, and error-path logging if invalid CB or timeout bits are injected or observed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ppc4xx/xor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/pxa_dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/pxa_dma.c Research

## Purpose
`pxa_dma.c` implements the Marvell/PXA peripheral DMA controller as a Linux dmaengine provider. It supports slave scatter-gather transfers, memory-to-memory copies, cyclic audio-style transfers, dynamic assignment of virtual channels to physical DMA channels, debugfs inspection, platform-data and device-tree channel lookup, residue reporting, and termination/synchronization through the virt-dma framework.

## Important APIs, Types, and Functions
The hardware descriptor is `struct pxad_desc_hw` with DDADR, DSADR, DTADR, and DCMD words. `struct pxad_desc_sw` wraps a virt-dma descriptor, the coherent hardware descriptor array, length, first DMA address, misalignment flag, cyclic flag, and descriptor pool pointer. `struct pxad_phy` models a physical channel and current virtual-channel owner. `struct pxad_chan` embeds `struct virt_dma_chan`, stores requestor mapping (`drcmr`), required priority, current slave config, physical channel assignment, descriptor pool, bus-error cookie, and waitqueue. `struct pxad_device` is the controller and owns the dma_device, MMIO base, physical channels, and debugfs state.

Core dmaengine methods are `pxad_alloc_chan_resources()`, `pxad_free_chan_resources()`, `pxad_prep_memcpy()`, `pxad_prep_slave_sg()`, `pxad_prep_dma_cyclic()`, `pxad_config()`, `pxad_tx_submit()`, `pxad_issue_pending()`, `pxad_tx_status()`, `pxad_terminate_all()`, and `pxad_synchronize()`. Hardware helpers include `lookup_phy()`, `pxad_free_phy()`, `phy_enable()`, `phy_disable()`, `pxad_launch_chan()`, `pxad_try_hotchain()`, `clear_chan_irq()`, and the IRQ handlers. Probe helpers are `pxad_init_phys()`, `pxad_dma_xlate()`, `pxad_init_dmadev()`, and `pxad_probe()`.

## Control Flow
Probe maps MMIO, reads channel/requestor counts from OF or platform data, configures dmaengine capabilities, initializes physical channel IRQ handling, creates one virt channel per physical slot, registers the dma_device, optionally registers an OF DMA controller, and creates debugfs files. Client configuration stores address, width, and burst information in `chan->cfg`. Prepare paths allocate one hardware descriptor per transfer segment plus one updater descriptor, fill descriptor chains, set source/target addresses and DCMD width/burst/flow bits, mark misalignment when needed, and pass the descriptor to virt-dma.

Submit finalizes the updater descriptor, assigns a cookie, and either hot-chains onto a still-running physical channel or queues the descriptor in `desc_submitted`. Cold chaining links submitted descriptors when alignment mode remains compatible. `issue_pending()` moves submitted descriptors to issued and launches the first one if the channel cannot be hot-chained.

Interrupt flow handles either per-channel IRQs or a shared controller IRQ via `DINT`. `pxad_chan_handler()` clears DCSR status, walks issued descriptors, uses the updater descriptor to decide completion, completes normal descriptors, invokes cyclic callbacks without removing the cyclic descriptor, records bus-error cookies, stops on errors, and relaunches the next issued descriptor after STOPSTATE. Termination disables hardware, frees physical mapping, gathers all virt-dma descriptors, and frees them without callbacks.

## State and Persistence
All state is in memory and MMIO registers. Persistent runtime state includes channel/requestor mappings in DRCMR registers, active physical channel ownership, DALGN alignment bits, descriptor pools, descriptor queues managed by virt-dma, bus-error cookie, waitqueue state, and debugfs dentries. There is no filesystem persistence beyond debugfs views.

## Dependencies and Integration Points
The driver depends on Linux dmaengine, virt-dma, DMA pool allocation, platform device APIs, OF DMA translation, platform data from `linux/platform_data/mmp_dma.h`, request parameters from `linux/dma/pxa-dma.h`, interrupt APIs, waitqueues, and optional debugfs. It integrates with clients via either OF two-cell DMA specs (`requestor`, `priority`) or legacy filter parameters in `struct pxad_param`.

## Risks and Edge Cases
The updater descriptor completion scheme is subtle: the final descriptor writes to the previous descriptor's address so software can detect whether hardware reached the end. Residue must read current DSADR/DTADR before completion testing to avoid reordering. Hot chaining is intentionally refused when a pending descriptor would require switching into misaligned mode, otherwise DALGN could be wrong for active hardware. Bus errors mark a cookie as `DMA_ERROR` and disable the physical channel. Cyclic transfers require period length alignment and period size under the hardware DCMD length mask. `pxad_terminate_all()` appears to clear `phy->vchan` both through `pxad_free_phy()` and again after, so concurrency assumptions around `phy_lock` matter.

## Test Signals
Useful tests include dmatest memcpy, slave SG transfers in both directions with several widths and bursts, cyclic DMA callbacks, OF xlate and legacy filter lookup, hot-chain stress with back-to-back descriptors, misaligned and aligned transfer mixtures, residue reporting during active transfers, bus-error injection if available, terminate/synchronize while running, shared versus per-channel IRQ configurations, and debugfs state/descriptors/requesters output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/pxa_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dma/qcom/Kconfig Research

## Purpose
This Kconfig fragment defines build-time options for Qualcomm DMA drivers under `drivers/dma/qcom`. In this subset it is most relevant because it declares `CONFIG_QCOM_BAM_DMA`, the symbol that builds `bam_dma.c`.

## Important APIs, Types, and Functions
There are no runtime APIs. The entries are `QCOM_ADM`, `QCOM_BAM_DMA`, `QCOM_GPI_DMA`, `QCOM_HIDMA_MGMT`, and `QCOM_HIDMA`. Each is a tristate except `QCOM_GPI_DMA` is also tristate and limited to `ARCH_QCOM`. All select `DMA_ENGINE`; ADM, BAM, and GPI also select `DMA_VIRTUAL_CHANNELS`.

`QCOM_BAM_DMA` is titled `QCOM BAM DMA support`, depends on `ARCH_QCOM || (COMPILE_TEST && OF && ARM)`, and enables the BAM DMA controller used by on-chip devices.

## Control Flow
Kconfig evaluation exposes these symbols to kernel configuration. If `QCOM_BAM_DMA` is enabled, the qcom DMA Makefile adds `bam_dma.o` to the build. Dependency expressions allow native Qualcomm builds and constrained compile-test builds with OF and ARM.

## State and Persistence
The selected values persist in the kernel `.config` and determine built-in or module output. The file has no runtime state.

## Dependencies and Integration Points
This file integrates with the parent DMA Kconfig menu and qcom DMA Makefile. The `select DMA_VIRTUAL_CHANNELS` dependency is required by BAM and ADM source code because they use the virt-dma helper layer.

## Risks and Edge Cases
Incorrect dependencies can either hide useful compile coverage or allow invalid builds. BAM compile-test is limited to `OF && ARM`, which reflects its device-tree and architecture assumptions. HIDMA management and channel options do not select virtual channels, matching their separate implementation model.

## Test Signals
Configuration tests should verify that enabling `QCOM_BAM_DMA=m` builds `bam_dma.ko`, that disabling it omits `bam_dma.o`, and that `COMPILE_TEST` configurations only expose it when OF and ARM constraints are satisfied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dma/qcom/Makefile Research

## Purpose
This Makefile maps Qualcomm DMA Kconfig symbols to objects built by Kbuild.

## Important APIs, Types, and Functions
There are no runtime functions. `obj-$(CONFIG_QCOM_ADM)` builds `qcom_adm.o`; `obj-$(CONFIG_QCOM_BAM_DMA)` builds `bam_dma.o`; `obj-$(CONFIG_QCOM_GPI_DMA)` builds `gpi.o`; `obj-$(CONFIG_QCOM_HIDMA_MGMT)` builds the composite `hdma_mgmt.o` from `hidma_mgmt.o` and `hidma_mgmt_sys.o`; and `obj-$(CONFIG_QCOM_HIDMA)` builds composite `hdma.o` from `hidma_ll.o`, `hidma.o`, and `hidma_dbg.o`.

## Control Flow
During Kbuild traversal, the selected configuration symbols decide which object files are compiled and linked into the kernel image or modules. For this subset, `CONFIG_QCOM_BAM_DMA=y/m` directly controls whether `bam_dma.c` participates in the build.

## State and Persistence
The Makefile affects build artifacts only. It has no runtime state or persistent data.

## Dependencies and Integration Points
It depends on symbols declared in the sibling Kconfig file and integrates with the parent `drivers/dma` Kbuild hierarchy. Composite object declarations for HIDMA ensure multiple C files link into one module/object.

## Risks and Edge Cases
Symbol/object mismatches would silently omit drivers or try to build the wrong source. The double space in `obj-$(CONFIG_QCOM_HIDMA) +=  hdma.o` is harmless to Kbuild but worth noting as cosmetic. BAM has a simple one-symbol-to-one-object mapping.

## Test Signals
Build tests should toggle each qcom DMA symbol and inspect whether the expected `.o` or module is produced. For this work item, enabling `CONFIG_QCOM_BAM_DMA` should compile `drivers/dma/qcom/bam_dma.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/bam_dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/qcom/bam_dma.c Research

## Purpose
`bam_dma.c` implements the Qualcomm BAM (Bus Access Manager) DMA engine as a dmaengine slave provider. BAM hardware uses an external-memory descriptor FIFO per pipe/channel; the driver writes descriptors into a circular FIFO, advances the event register to start transfers, handles pipe/global interrupts, supports remotely controlled or remotely powered BAM instances, and integrates runtime PM and device-tree channel translation.

## Important APIs, Types, and Functions
`struct bam_desc_hw` is the packed hardware descriptor with buffer address, size, and flags. `struct bam_async_desc` is a virt-dma descriptor plus temporary descriptor array, transfer length, flags, current descriptor pointer, active-list node, direction, and total length. `struct bam_chan` embeds `struct virt_dma_chan` and stores channel id, slave config, FIFO virtual/DMA addresses, circular head/tail indices, initialized/paused/reconfigure flags, and active descriptor list. `struct bam_device` owns MMIO registers, dma_device, channel array, execution environment id, remote-control flags, clock, IRQ, register layout, active-channel count, and controller tasklet.

Register layout is abstracted by `enum bam_reg`, `struct reg_offset_data`, per-version layout tables for v1.3, v1.4, and v1.7, and `bam_addr()`. Core methods include `bam_alloc_chan()`, `bam_free_chan()`, `bam_slave_config()`, `bam_prep_slave_sg()`, `bam_issue_pending()`, `bam_tx_status()`, `bam_dma_terminate_all()`, `bam_pause()`, `bam_resume()`, `bam_start_dma()`, `process_channel_irqs()`, and `bam_dma_irq()`.

## Control Flow
Probe matches the compatible string to a register layout, maps MMIO, gets the IRQ, reads the `qcom,ee` execution environment, reads remote-control/power flags, gets the BAM clock or static channel/EE counts when no clock is available, enables the clock, initializes global BAM state, creates channels, requests the IRQ, sets dmaengine slave capabilities, registers dmaengine and OF DMA controller, and enables runtime PM autosuspend.

Channel allocation allocates a write-combined 32 KiB descriptor FIFO. If the BAM is remotely powered and this is the first active channel, the driver resets the BAM. Slave configuration copies `struct dma_slave_config` and marks the channel for reconfiguration. `bam_prep_slave_sg()` validates direction, splits SG entries into descriptors no larger than the FIFO payload size, applies command/fence/interrupt flags, and returns a virt-dma descriptor.

`bam_issue_pending()` moves pending descriptors to issued and calls `bam_start_dma()` if FIFO space is available. `bam_start_dma()` runtime-resumes the device, initializes pipe hardware on first use, applies maxburst configuration, chooses how many descriptors fit in the circular FIFO, sets EOT or INT flags on the last descriptor chunk as needed, copies descriptors into the FIFO with wrap handling, moves the async descriptor to `desc_list`, issues a write barrier, and writes `BAM_P_EVNT_REG` with the new tail offset. The controller tasklet starts more work after IRQs free FIFO space.

Interrupt flow first calls `process_channel_irqs()`, which reads the EE-specific IRQ sources, clears pipe status, computes hardware-consumed FIFO offset from `BAM_P_SW_OFSTS`, advances the channel head, completes fully consumed descriptors through virt-dma, or requeues partially consumed descriptors. The top-level IRQ schedules the tasklet for pipe IRQs and separately clears global BAM error/status IRQs under runtime PM.

## State and Persistence
Runtime state is all in memory, descriptor FIFO DMA memory, MMIO registers, and runtime PM/clock state. Per-channel FIFO `head` and `tail` mirror hardware descriptor consumption and software production. `desc_list` tracks descriptors committed to hardware but not fully consumed. `initialized` controls pipe reset/setup. `paused` changes status reporting to `DMA_PAUSED`. `reconfigure` defers slave config effects until the next start. `active_channels` coordinates remotely powered BAM reset behavior. No filesystem state is persisted.

## Dependencies and Integration Points
The driver depends on dmaengine, virt-dma, OF DMA controller APIs, platform devices, clocks, runtime PM, scatterlist helpers, circular buffer helpers, write-combined DMA allocation, and Qualcomm BAM device-tree bindings with compatibles `qcom,bam-v1.3.0`, `qcom,bam-v1.4.0`, and `qcom,bam-v1.7.0`. Clients request a channel through one OF argument selecting the BAM pipe number. The Kconfig symbol is `QCOM_BAM_DMA`, and the Makefile maps it to `bam_dma.o`.

## Risks and Edge Cases
Circular FIFO accounting is the highest-risk area. The driver reserves one descriptor slot, aligns FIFO base, handles wraparound copies, and must keep software `head`/`tail` consistent with `BAM_P_SW_OFSTS`. Partial descriptor submission means a single dmaengine transaction can be committed in chunks and requeued until all descriptors are consumed. Termination resets pipe hardware before freeing descriptors because connected peripherals can otherwise continue accessing freed FIFO memory. Remote-controlled and remotely powered BAMs cannot always be reset or clocked like local BAMs, so probe and channel allocation have special paths. Runtime PM is used in IRQ, start, pause/resume, and free paths; a failed `pm_runtime_get_sync()` can leave cleanup incomplete. The descriptor address field is 32-bit, so DMA mask and platform addressing assumptions matter.

## Test Signals
Useful tests include OF channel xlate for valid and invalid pipe ids, slave SG transfers in both directions, SG entries larger than `BAM_FIFO_SIZE`, FIFO wraparound, transfer chunks larger than available FIFO space, pause/resume status, terminate while hardware has active descriptors, runtime autosuspend/resume under repeated traffic, remotely controlled/powered DT configurations, global and pipe interrupt handling, residue reporting for queued and active descriptors, and compile coverage for all supported BAM register layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/bam_dma.c -->
