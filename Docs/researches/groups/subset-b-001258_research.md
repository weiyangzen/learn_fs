# subset-b-001258 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mcf-edma-main.c -->
# sources/distributed-fs/ceph-client/drivers/dma/mcf-edma-main.c

## Purpose
ColdFire-family platform glue for the Freescale/NXP eDMA DMAEngine implementation. It binds legacy platform-data-described ColdFire eDMA hardware to the shared `fsl-edma-common` channel implementation and exposes private slave/cyclic DMA channels to board code.

## Important APIs, Types, And Functions
`mcf_edma_tx_handler` and `mcf_edma_err_handler` service transfer and error IRQs by reading eDMA interrupt/error bitmaps and dispatching to `fsl_edma_tx_chan_handler` or `fsl_edma_err_chan_handler`. `mcf_edma_irq_init` and `mcf_edma_irq_free` acquire grouped platform IRQ resources named `edma-tx-00-15`, `edma-tx-16-55`, optional `edma-tx-56-63`, and optional `edma-err`. `mcf_edma_probe` allocates `struct fsl_edma_engine`, initializes `struct fsl_edma_chan` entries and DMAEngine callbacks, and registers the DMA device. `mcf_edma_filter_fn` matches a DMA request source id against this driver.

## Control Flow
Probe requires `struct mcf_edma_platform_data`, chooses the platform-supplied channel count or 64 channels, maps MMIO, initializes each virtual channel/TCD pointer, clears pending interrupt state, requests IRQs, then registers a DMAEngine device with private slave and cyclic capabilities. Transfer IRQs scan the 64-bit interrupt map, clear channel interrupt state through `regs->cint`, and hand completion to the common eDMA code. Error IRQs scan low and high error registers, disable requests, clear channel errors, and mark the channel or invoke the common error handler. Remove frees IRQs, cleans virtual channels, and unregisters the DMA device.

## State And Persistence
Runtime state is held in the devm-allocated `fsl_edma_engine`, channel array, MMIO register block, vchan lists, and platform filter map. Persistent hardware state includes TCD CSR clearing during probe, global interrupt clearing, and round-robin arbitration enabled through `EDMA_CR_ERGA | EDMA_CR_ERCA`. There is no filesystem persistence.

## Dependencies And Integration Points
Depends on Linux platform devices, legacy `platform_data/dma-mcf-edma.h`, DMAEngine, virt-dma through the common eDMA layer, and `fsl-edma-common.h`. Board files or platform data provide slave maps and IRQ names. DMA clients integrate through DMAEngine channel filtering with `mcf_edma_filter_fn` and the shared `fsl_edma_*` preparation/status callbacks.

## Risks And Edge Cases
IRQ initialization returns `-1` for missing mandatory grouped resources and can leak already-requested IRQs if a later request fails because error paths do not call `mcf_edma_irq_free`. The error handler returns `IRQ_NONE` if low error bits are empty even when high error bits may be pending, so high-half-only errors can be missed. The high-half error path sets `DMA_ERROR` without calling the common error handler, unlike low channels. Channel count from platform data is trusted against the fixed 64-channel interrupt/error bitmap assumptions.

## Test Signals
Useful signals are successful platform probe, DMAEngine registration, channel filtering by source id, cyclic/slave transfers completing through `fsl_edma_tx_chan_handler`, and injected hardware error IRQs updating channel status. IRQ resource naming and the high-half error path should be covered on ColdFire board or emulation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mcf-edma-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mediatek/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dma/mediatek/Kconfig

## Purpose
Defines the MediaTek DMAEngine configuration options for High-Speed DMA, Command-Queue DMA, and UART APDMA drivers.

## Important APIs, Types, And Functions
The file declares `CONFIG_MTK_HSDMA`, `CONFIG_MTK_CQDMA`, and `CONFIG_MTK_UART_APDMA`. HSDMA and CQDMA depend on `ARCH_MEDIATEK || COMPILE_TEST`, select `DMA_ENGINE` and `DMA_VIRTUAL_CHANNELS`, and CQDMA additionally selects `ASYNC_TX_ENABLE_CHANNEL_SWITCH`. UART APDMA depends on device tree support and `SERIAL_8250_MT6577` and selects DMAEngine plus virtual channels.

## Control Flow
There is no runtime control flow. Kconfig selection controls whether the matching object files in the directory build and whether common DMAEngine/virtual-channel support is pulled into the kernel configuration.

## State And Persistence
Configuration state is persisted in the kernel `.config`. No runtime state exists in this file.

## Dependencies And Integration Points
Integrates MediaTek DMA drivers with the kernel Kconfig dependency graph, the 8250 MediaTek UART driver, and compile-test coverage for non-MediaTek builds. The selected symbols are consumed by the directory Makefile.

## Risks And Edge Cases
`MTK_UART_APDMA` is tied to `SERIAL_8250_MT6577`, so APDMA is not offered without the matching serial driver. HSDMA/CQDMA can be compile-tested off target, but real runtime still depends on matching device-tree bindings, clocks, IRQs, and SoC-specific register layouts.

## Test Signals
Kconfig tests should confirm symbol visibility under MediaTek and compile-test configurations, automatic selection of `DMA_ENGINE` and `DMA_VIRTUAL_CHANNELS`, and object inclusion when each symbol is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mediatek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mediatek/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dma/mediatek/Makefile

## Purpose
Build glue for the MediaTek DMAEngine driver objects in this directory.

## Important APIs, Types, And Functions
Maps `CONFIG_MTK_UART_APDMA` to `mtk-uart-apdma.o`, `CONFIG_MTK_HSDMA` to `mtk-hsdma.o`, and `CONFIG_MTK_CQDMA` to `mtk-cqdma.o`.

## Control Flow
There is no runtime control flow. Kbuild includes each object when the corresponding Kconfig symbol is built-in or modular.

## State And Persistence
No state beyond build outputs generated by Kbuild.

## Dependencies And Integration Points
Consumes symbols declared in the sibling Kconfig and integrates the drivers into the kernel DMAEngine build.

## Risks And Edge Cases
The file is intentionally simple; risk is limited to symbol/object name drift if Kconfig entries or source filenames change.

## Test Signals
A build with each MediaTek DMA symbol as `y` or `m` should compile the matching object and not compile disabled drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mediatek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mediatek/mtk-cqdma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/mediatek/mtk-cqdma.c

## Purpose
DMAEngine driver for MediaTek Command-Queue DMA controllers used for memory-to-memory copies. It exposes many virtual DMA channels over a smaller set of physical command-queue engines.

## Important APIs, Types, And Functions
Core state is split into `struct mtk_cqdma_device`, `struct mtk_cqdma_vchan`, `struct mtk_cqdma_pchan`, and `struct mtk_cqdma_vdesc`. Register helpers `mtk_dma_read/write/rmw/set/clr` isolate MMIO access. `mtk_cqdma_prep_dma_memcpy` splits large copies into parent/child descriptors capped by `MTK_CQDMA_MAX_LEN`. `mtk_cqdma_issue_pending`, `mtk_cqdma_start`, `mtk_cqdma_irq`, and `mtk_cqdma_tasklet_cb` move work from vchan lists to physical queues and complete it. Resource hooks allocate/free physical channels by reference count, and probe/remove register the DMAEngine and OF DMA controller.

## Control Flow
Probe allocates the device, reads `dma-requests` and `dma-channels` with defaults, maps one resource and IRQ per physical channel, initializes virtual channels, registers the DMA device and OF xlate, enables clocks/runtime PM, resets physical channels, and creates per-PC tasklets. A memcpy request becomes one or more CVDs linked by `tx->next`; issue-pending moves issued vdesc entries onto the chosen physical channel queue. If the queue was empty, `mtk_cqdma_start` programs source/destination low and high registers, length registers, interrupt enable, and engine enable. IRQ clears the per-PC interrupt flag, disables that IRQ, and schedules a tasklet. The tasklet consumes one queued child descriptor, subtracts parent residue, completes the parent only after all children finish, starts the next queued child, runs dependencies, frees child descriptors, and reenables the IRQ.

## State And Persistence
Persistent runtime state includes each VC's current PC assignment, completion object, synchronization flag, each PC's queue/refcount/tasklet/lock, descriptor residues, and hardware registers. Clocks and runtime PM are enabled for the driver lifetime. No filesystem persistence exists.

## Dependencies And Integration Points
Depends on DMAEngine, `virt-dma`, platform resources, device tree `dma-requests`/`dma-channels`, `of_dma_xlate_by_chan_id`, clocks, IRQs, and runtime PM. It advertises `DMA_MEMCPY`, 4-byte widths, memory-to-memory direction, and segment residue granularity. CQDMA Kconfig also selects async_tx channel switching for dependencies.

## Risks And Edge Cases
`kzalloc_objs(*cvd, nr_vd, GFP_NOWAIT)` allocates an array of pointers; any allocation failure after `cvd` itself leaks that pointer array, and the function does not free the array after successful descriptor creation. Parent/child lifetime is subtle because only children are explicitly freed in the tasklet and the parent is freed by `desc_free`. Termination cannot abort a hardware-active transfer immediately; it waits for active VC completion. IRQ disabling/enabling per PC must stay paired with tasklet cleanup. Device-tree `dma-channels` controls both resource count and IRQ count, so binding/resource mismatches fail probe.

## Test Signals
Use dmatest memcpy on supported MediaTek CQDMA hardware for short and >`MTK_CQDMA_MAX_LEN` transfers, verify residues during active transfers, test multiple VCs sharing PCs, terminate while active, and remove with pending IRQs. Fault-injection around allocation and missing `dma-requests`/`dma-channels` properties should exercise defaults and cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mediatek/mtk-cqdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mediatek/mtk-hsdma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/mediatek/mtk-hsdma.c

## Purpose
DMAEngine driver for MediaTek High-Speed DMA memory-to-memory copy engines. It multiplexes several virtual channels over one ring-based physical engine.

## Important APIs, Types, And Functions
Important structures are `mtk_hsdma_device`, `mtk_hsdma_vchan`, `mtk_hsdma_pchan`, `mtk_hsdma_ring`, hardware descriptor `mtk_hsdma_pdesc`, virtual descriptor `mtk_hsdma_vdesc`, and per-descriptor callback metadata `mtk_hsdma_cb`. `mtk_hsdma_alloc_pchan/free_pchan` allocate and program coherent TX/RX rings. `mtk_hsdma_issue_pending_vdesc` reserves ring entries and emits physical descriptors. `mtk_hsdma_free_rooms_in_ring` reclaims completed RX descriptors, updates residues, completes VDs, and reissues pending work. SoC data `mt7623_soc` and `mt7622_soc` define DDONE/LS0 bit positions.

## Control Flow
Probe maps registers, loads SoC match data, gets the clock and IRQ, initializes vchans, registers DMAEngine/OF DMA, enables runtime PM and global DMA settings, then requests the IRQ. Channel allocation lazily allocates the single physical ring on first user and reference-counts later users. A memcpy prep stores source, destination, length, and residue in one vdesc. Issue-pending reserves as many ring slots as are available, emits TX/RX descriptor pairs in chunks of `MTK_HSDMA_MAX_LEN`, tags the last physical descriptor for completion, writes the TX CPU pointer, and leaves partially emitted VDs on `desc_issued` until space returns. IRQ disables RXDONE, scans completed RX descriptors up to ring size, subtracts residue, completes tagged VDs, recycles descriptors, advances the RX CPU pointer, optionally acks status, and immediately tries to submit more pending VDs.

## State And Persistence
State lives in coherent descriptor rings, callback side arrays, atomic free-slot count, vchan issued/hardware-processing/completed lists, residues, refcounts, clocks/runtime PM, and HSDMA registers. The ring is allocated only while at least one virtual channel holds resources.

## Dependencies And Integration Points
Depends on DMAEngine, `virt-dma`, coherent DMA memory, MediaTek device-tree compatibles, clocks, runtime PM, OF DMA xlate by channel id, and platform IRQs. It advertises `DMA_MEMCPY`, memory-to-memory direction, 4-byte bus widths, and segment residue granularity.

## Risks And Edge Cases
`mtk_hsdma_hw_init` ignores its return value in probe, so clock/runtime PM failures can be hidden. Termination does not stop descriptors already on hardware; it waits until the ring completes them. Correctness depends on memory barriers around coherent descriptor updates and on callback metadata being cleared exactly once. Ring-space accounting and partial issue of a large VD are concurrency-sensitive because IRQ context and issue path share `nr_free` and vchan lists. Residue is modified in place as chunks are emitted and completed, so status for partially issued VDs must be checked under the VC lock.

## Test Signals
Run dmatest memcpy with many parallel virtual channels, transfer sizes larger than one physical descriptor, ring-full pressure, tx_status polling, terminate while active, and suspend/remove IRQ races. Hardware coverage should include both MT7622 and MT7623 compatible data because descriptor done bits differ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mediatek/mtk-hsdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mediatek/mtk-uart-apdma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/mediatek/mtk-uart-apdma.c

## Purpose
DMAEngine slave driver for MediaTek UART APDMA virtual FIFO channels. It supports one-scatterlist UART TX or RX transfers for the MediaTek 8250 UART driver.

## Important APIs, Types, And Functions
`struct mtk_uart_apdmadev` owns the DMA device, clock, address-width capability, and channel count. `struct mtk_chan` holds a virt-dma channel, slave config, active descriptor, direction, MMIO base, IRQ, and RX residue. `mtk_uart_apdma_start_tx` and `mtk_uart_apdma_start_rx` program VFF ring registers. `mtk_uart_apdma_irq_handler` dispatches TX/RX completion handlers and calls `vchan_cookie_complete`. DMAEngine hooks include resource allocation/free, `prep_slave_sg`, `slave_config`, `issue_pending`, `pause`, `terminate_all`, and `tx_status`. Runtime/system PM callbacks gate the APDMA clock.

## Control Flow
Probe gets the clock, derives DMA mask width from compatible data, creates one channel per `dma-requests` resource, maps each channel base, records IRQs, enables runtime PM, registers DMAEngine, and registers OF DMA xlate by channel id. Allocating a channel resumes the device, clears VFF registers, warm-resets the FIFO, requests the channel IRQ, clears high address state if supported, then drops the runtime PM reference without fully suspending. A slave SG prep accepts exactly one SG entry and stores address/length/direction. Issue-pending starts TX or RX if no descriptor is active. TX initializes the VFF address/length/threshold, advances WPT by available length, enables interrupts, and kicks flush when needed. RX configures the VFF receive ring and enables interrupts. IRQ clears/halts the relevant direction, computes RX residual bytes from read/write pointers, completes the descriptor, and clears `c->desc`. Terminate flushes, stops, clears IRQ state, synchronizes IRQ, and frees all descriptors.

## State And Persistence
State includes per-channel VFF registers, the active descriptor pointer, saved slave config, direction, RX status/residue, runtime PM clock state, and virt-dma lists. No persistent storage exists.

## Dependencies And Integration Points
Depends on DMAEngine, `virt-dma`, OF DMA, MediaTek 8250 UART clients, clocks, runtime PM, platform resources, and compatible data indicating 32- to 35-bit DMA addressing. It advertises one-byte slave bus widths, device-to-memory and memory-to-device directions, and segment residue granularity.

## Risks And Edge Cases
`tx_status` always reports `c->rx_status`, which is meaningful for RX but questionable for TX. `alloc_chan_resources` calls `pm_runtime_resume_and_get` and then `pm_runtime_put_noidle`, while `free_chan_resources` calls `pm_runtime_put_sync`, so runtime PM reference symmetry deserves scrutiny. The driver supports only `sglen == 1`; callers expecting multi-SG UART DMA are rejected. RX residue depends on wrap-bit pointer math and the configured port window size. Stop/flush polling failures are logged but termination still frees descriptors.

## Test Signals
Test with the MediaTek 8250 UART driver for TX and RX DMA, especially ring wrap, high DMA addresses on compatibles with `support_ext_addr`, pause/terminate during active UART I/O, runtime suspend/resume, and tx_status residue for RX. Missing or mismatched per-channel resources should fail probe cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mediatek/mtk-uart-apdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/milbeaut-hdmac.c -->
# sources/distributed-fs/ceph-client/drivers/dma/milbeaut-hdmac.c

## Purpose
DMAEngine slave driver for Socionext Milbeaut M10V HDMAC, handling peripheral memory-to-device and device-to-memory scatterlist transfers.

## Important APIs, Types, And Functions
`milbeaut_hdmac_device` owns the DMA device, clock, global base, and flexible channel array. `milbeaut_hdmac_chan` stores a virt-dma channel, current descriptor, channel register base, slave id, and slave config. `milbeaut_hdmac_desc` stores copied SG entries and current SG index. `milbeaut_chan_start` programs source/destination, burst, width, interrupt, and transfer-count registers. `milbeaut_hdmac_interrupt` advances SG entries and completes descriptors. `milbeaut_hdmac_xlate` assigns a slave id from DT arguments.

## Control Flow
Probe counts IRQs to size channels, sets a 32-bit DMA mask, maps registers, enables the clock, fills DMAEngine slave/private callbacks, initializes one channel per IRQ, registers DMAEngine, and registers an OF DMA controller. Prep copies the caller's SG array into driver-owned memory. Issue-pending moves the next descriptor out of the vchan queue and starts the first SG. Each interrupt acknowledges and disables channel IRQ bits, advances the SG index, completes the virt descriptor when all SG entries are done, otherwise starts the next SG. Terminate disables the channel, terminates any active vdesc, collects queued descriptors, and frees them. Remove synchronously terminates every channel before unregistering and disabling the clock.

## State And Persistence
State is per-channel current descriptor, copied scatterlist array, slave config, slave request id, register state, and vchan lists. Hardware global enable and channel registers persist until remove/termination; there is no filesystem persistence.

## Dependencies And Integration Points
Depends on DMAEngine, `virt-dma`, OF DMA custom xlate, platform IRQs, clocks, field-prep register macros, and device-tree compatible `socionext,milbeaut-m10v-hdmac`. Clients pass slave request ids through the DMA specifier and bus widths/bursts through `dma_slave_config`.

## Risks And Edge Cases
Transfer count is computed as `len / (burst * width) - 1`; invalid zero or non-divisible lengths, unset burst, or unsupported burst sizes can underflow or misprogram hardware because prep does not validate them. Residue calculation initializes `txstate->residue` by subtracting the in-flight progress from zero before adding queued SG lengths, which is subtle and can report wrong values if not exactly balanced. Interrupt ack disables EI/CI and relies on restart for the next SG. Remove aborts if `dmaengine_terminate_sync` fails, intentionally warning about possible resource leakage.

## Test Signals
Exercise MEM_TO_DEV and DEV_TO_MEM SG transfers with 1/2/4-byte widths and burst sizes 4/8/16, residue polling during an active SG, pause/resume, terminate active transfer, and DT xlate with valid/invalid one-argument slave ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/milbeaut-hdmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/milbeaut-xdmac.c -->
# sources/distributed-fs/ceph-client/drivers/dma/milbeaut-xdmac.c

## Purpose
DMAEngine memcpy driver for Socionext Milbeaut M10V XDMAC channels.

## Important APIs, Types, And Functions
`milbeaut_xdmac_device` owns the DMA device, global register base, and flexible channel array. `milbeaut_xdmac_chan` stores a virt-dma channel, active descriptor, and channel register base. `milbeaut_xdmac_desc` carries length, source, and destination. `milbeaut_chan_start` programs byte count, source/destination addresses, default burst settings, and enables transfer/end interrupts. `milbeaut_xdmac_interrupt` acknowledges completion and starts the next queued descriptor. `enable_xdmac` and `disable_xdmac` gate the global engine bit.

## Control Flow
Probe counts IRQs, maps MMIO, initializes DMA_MEMCPY callbacks, creates one channel per IRQ, globally enables XDMAC, registers DMAEngine, and registers OF simple xlate. Prep allocates one descriptor for a memcpy request. Issue-pending moves the next vchan descriptor to `mc->md` and starts hardware if idle. IRQ clears status, completes the active descriptor, and starts the next one. Terminate clears channel enable, terminates the active vdesc, collects queued descriptors, and frees them. Remove terminates all channels, unregisters OF/DMAEngine, and disables XDMAC.

## State And Persistence
State consists of vchan queues, one active descriptor per channel, channel registers, and the global XDMAC enable register. There is no persistent storage.

## Dependencies And Integration Points
Depends on DMAEngine, `virt-dma`, platform IRQ/MMIO resources, OF simple DMA xlate, and compatible `socionext,milbeaut-m10v-xdmac`. It advertises `DMA_MEMCPY` with 1/2/4/8-byte bus width capabilities.

## Risks And Edge Cases
The driver uses `md->len - 1` without guarding zero-length requests. It reports status through plain `dma_cookie_status`, so there is no residue calculation. It does not set an explicit DMA mask. Termination assumes clearing `CE` halts the channel promptly. Remove has the same terminate-failure resource-leak warning pattern as HDMAC.

## Test Signals
Use dmatest memcpy per channel, queue multiple descriptors to verify IRQ-driven chaining, terminate active copies, remove with idle and active channels, and check OF channel allocation through simple xlate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/milbeaut-xdmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mmp_pdma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/mmp_pdma.c

## Purpose
DMAEngine driver for Marvell MMP peripheral DMA controllers, including legacy 32-bit PDMA and Spacemit K1 64-bit/LPAE PDMA variants. It supports memcpy, slave SG, and cyclic DMA.

## Important APIs, Types, And Functions
`mmp_pdma_device` owns hardware, physical channels, operation table, and DMAEngine device. `mmp_pdma_chan` is a software channel with pending/running lists, descriptor pool, physical-channel binding, request-line mapping, and cyclic state. `mmp_pdma_phy` represents a hardware channel. `mmp_pdma_ops` abstracts 32-bit versus 64-bit register/descriptor address handling and run bits. Key functions include `lookup_phy`, `start_pending_queue`, `mmp_pdma_tx_submit`, descriptor prep for memcpy/slave SG/cyclic, `mmp_pdma_residue`, IRQ handlers, and `dma_do_tasklet` completion cleanup.

## Control Flow
Probe maps registers, enables optional clock/reset, selects ops from DT compatible, determines channel count, requests either one shared IRQ or per-channel IRQs, initializes physical and software channels, sets DMAEngine capabilities and masks, registers the device, and registers OF xlate. Channel resources create a DMA pool and reset state. Prep functions build linked hardware descriptors in the pool, assign source/destination and `DCMD`, link descriptors through DDADR, mark final descriptors with STOP/ENDIRQEN, and for cyclic link the last descriptor back to the first. Submit assigns cookies to all child descriptors and moves them to the pending list. Issue-pending calls `start_pending_queue`, which allocates a free physical channel if needed, maps request lines, writes the first descriptor address, and starts hardware. IRQ clears DCSR/DINT, schedules the channel tasklet, and the tasklet completes cookies through ENDIRQEN descriptors, invokes callbacks, frees descriptor entries, marks idle, and starts queued work.

## State And Persistence
State includes DMA pool descriptors, pending/running descriptor lists, physical-channel ownership, request-line DRCMR mappings, DALGN byte-align bits, cyclic first descriptor, channel idle flag, slave config, and hardware registers. State is runtime-only and tied to channel resource allocation.

## Dependencies And Integration Points
Depends on DMAEngine core helpers, platform data or device tree, OF DMA xlate, DMA pools, optional clocks/resets, platform IRQs, and compatible data `marvell,pdma-1.0` or `spacemit,k1-pdma`. It exposes private slave, memcpy, and cyclic capabilities and sets DMA masks according to hardware address width.

## Risks And Edge Cases
In `mmp_pdma_prep_slave_sg`, the loop uses `sg_dma_len(sgl)` instead of `sg_dma_len(sg)`, which can mis-size every entry after the first. 64-bit descriptors write low/high fields, but some slave paths assign `new->desc.dsadr` or `dtadr` directly for device addresses, bypassing ops high-word helpers. `mmp_pdma_residue` depends on current source/destination register values falling inside descriptor bounds and has special cyclic behavior. Terminate disables hardware and frees lists without callback completion. Physical-channel priority/ownership and request-line mapping are shared across channels and require `phy_lock`/`desc_lock` ordering discipline.

## Test Signals
Run dmatest memcpy, slave SG with multi-entry SG lists, cyclic audio-style transfers, 64-bit DMA addresses on Spacemit K1, shared and per-channel IRQ configurations, tx_status residue polling, terminate while active, and OF xlate request-line mapping. A targeted test should catch the `sg_dma_len(sgl)` multi-SG length issue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mmp_pdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mmp_tdma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/mmp_tdma.c

## Purpose
DMAEngine driver for Marvell two-channel DMA blocks, mainly cyclic slave DMA for audio/SQU-style peripherals.

## Important APIs, Types, And Functions
`mmp_tdma_device` owns two `mmp_tdma_chan` entries and a DMAEngine device. `mmp_tdma_chan` tracks register base, SRAM descriptor array, direction, peripheral address, burst/bus width, status, cyclic buffer geometry, and a reusable `dma_async_tx_descriptor`. `mmp_tdma_config_chan` programs TDCR for ADMA or PXA910 SQU variants. `mmp_tdma_prep_dma_cyclic` allocates descriptors from an SRAM gen_pool and chains periods into a ring. `mmp_tdma_tx_status` reports residue from current hardware position.

## Control Flow
Probe identifies the variant from DT, maps MMIO, obtains an `asram` gen_pool for descriptors, requests either shared or per-channel IRQs, initializes two channels, configures DMAEngine cyclic slave callbacks, registers DMAEngine, and registers OF DMA xlate. Resource allocation initializes the reusable descriptor and optionally requests per-channel IRQ. Prep validates slave direction, idle status, and period size, writes channel config, allocates a descriptor array, fills source/destination/next fields for each period, enables interrupts if requested, and returns the reusable descriptor. Submit immediately writes the descriptor physical address to TDNDPR and fetches it. Issue-pending sets channel enable. IRQ clears completion and schedules a tasklet, which invokes the descriptor callback. Pause/resume toggle channel enable; terminate aborts and disables IRQ.

## State And Persistence
State is stored in the channel descriptor array allocated from on-chip SRAM, the descriptor physical address, channel status, current position, buffer/period lengths, slave config, and TDMA registers. `descriptor_reuse` is enabled, so the same descriptor object represents the cyclic stream.

## Dependencies And Integration Points
Depends on DMAEngine, OF DMA, platform IRQ/MMIO resources, `gen_pool` SRAM named `asram`, and compatible strings `marvell,adma-1.0` and `marvell,pxa910-squ`. Clients select channels by one DT argument through a filter function.

## Risks And Edge Cases
`mmp_tdma_tx_submit` returns cookie 0 and does not use normal cookie assignment, which is unusual for DMAEngine clients. The file calls `dmaenginem_async_device_register`, which appears to be a misspelling of `dmaengine_async_device_register` unless a local compatibility macro exists elsewhere. Prep does not explicitly validate `buf_len % period_len`, so a partial final period is silently ignored by `num_periods = buf_len / period_len`. Descriptor memory requires an `asram` pool. Residue position logic assumes channel 0 reads source position and channel 1 reads destination position.

## Test Signals
Build coverage should verify the registration symbol typo. Runtime tests should cover cyclic playback/capture on both variants, callback cadence per period, pause/resume/terminate, residue over wrap, OF xlate channel selection, and failure when `asram` is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mmp_tdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/moxart-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/moxart-dma.c

## Purpose
DMAEngine slave driver for MOXA ART SoC APB/AHB DMA, supporting up to four peripheral channels with virt-dma queued scatterlist transfers.

## Important APIs, Types, And Functions
`moxart_dmadev` owns the DMAEngine device and four `moxart_chan` objects. `moxart_chan` holds a virt-dma channel, active descriptor, slave config, request line, SG index, and error flag. `moxart_desc` stores direction, device address, data width encoding, transfer cycles, and a flexible array of SG address/length pairs. `moxart_slave_config`, `moxart_prep_slave_sg`, `moxart_dma_start_desc`, `moxart_dma_interrupt`, and `moxart_tx_status` implement configuration, descriptor prep, execution, completion, and residue/error reporting.

## Control Flow
Probe maps the shared DMA base, parses IRQ, initializes four channels at fixed register strides, registers one shared IRQ, registers the DMAEngine device, and registers OF xlate that assigns a request line number. Slave config programs burst mode, address increment, bus width, APB/AHB selection, and request-line fields based on direction. Prep validates direction and width, copies SG entries into a flexible descriptor, and queues it through virt-dma. Issue-pending starts the next descriptor if idle. Each SG segment programs source/dest and cycle count then enables DMA and interrupts. The shared IRQ scans allocated channels, clears finish/error status, starts the next SG or completes the virt descriptor, and records errors. tx_status reports queued or in-flight residue and returns `DMA_ERROR` when the channel error flag is set.

## State And Persistence
State includes channel allocation flags, request-line number, active descriptor, SG index, transfer cycle counter, slave config, error flag, and APB DMA registers. It is runtime-only.

## Dependencies And Integration Points
Depends on DMAEngine, `virt-dma`, OF DMA, platform IRQ/MMIO resources, and compatible `moxa,moxart-dma`. It advertises private slave DMA and integrates with clients through one DT argument specifying request line.

## Risks And Edge Cases
`moxart_set_transfer_params` uses `len >> es_bytes[d->es]`; if `es_bytes` stores byte counts, this shifts by 1/2/4 rather than dividing by 1/2/4, so cycle programming deserves verification. There is no explicit validation that SG lengths align to data width or fit `APB_DMA_CYCLES_MASK`. Terminate frees the active descriptor directly under lock and disables interrupts, so races with shared IRQ handling must be considered. Error status is sticky until the next prep clears `ch->error`.

## Test Signals
Test all supported bus widths, MEM_TO_DEV and DEV_TO_MEM, multi-SG chaining, error interrupt reporting, residue during active SG, terminate while active, and DT request-line mapping. Hardware tests should validate programmed cycle counts for byte/halfword/word transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/moxart-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mpc512x_dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/mpc512x_dma.c

## Purpose
DMAEngine driver for Freescale MPC512x and MPC8308 DMA controllers using eDMA-style transfer control descriptors. It supports memory-to-memory copies and limited peripheral slave SG.

## Important APIs, Types, And Functions
`mpc_dma_regs` and `mpc_dma_tcd` model the hardware register block and transfer descriptors. `mpc_dma` owns the DMAEngine device, channel array, register/TCD MMIO, IRQs, and saved error status. `mpc_dma_chan` keeps free/prepared/queued/active/completed lists plus peripheral configuration. `mpc_dma_desc` wraps a software descriptor and coherent TCD. Important functions include `mpc_dma_execute`, `mpc_dma_irq_process`, `mpc_dma_process_completed`, `mpc_dma_tx_submit`, resource allocation/free, memcpy/slave SG prep, `mpc_dma_device_config`, and terminate.

## Control Flow
Probe maps IRQs and MMIO, identifies MPC8308 versus MPC512x, requests one or two IRQs, initializes DMAEngine callbacks and channel lists, configures arbitration/error/interrupt registers, registers DMAEngine, and optionally registers OF xlate by channel id. Allocating channel resources allocates a coherent TCD array and software descriptors, populates the free list, and enables error interrupts. Memcpy prep chooses the largest aligned transfer size, fills one TCD, and puts it on the prepared list. Slave SG prep currently accepts only one SG element, validates peripheral config and alignment, fills TCD fields for peripheral flow or MPC8308 software start, and prepares it. Submit moves the descriptor to queued, starts execution immediately if idle, and assigns a cookie. Execution moves queued descriptors to active, chains mem-to-mem TCDs through scatter/gather, marks final interrupt, copies the first TCD into hardware, and starts by software request or external request. IRQ captures error state, clears per-channel interrupt/error bits, marks active descriptors as error on error IRQs, moves active to completed, and starts more queued descriptors. The tasklet logs detailed error reasons, invokes callbacks/dependencies, recycles completed descriptors, and updates completed cookies.

## State And Persistence
State includes coherent TCD pools per allocated channel, descriptor lists, peripheral FIFO addresses/burst widths, active error status, channel cookies, and DMA controller registers. No filesystem persistence exists.

## Dependencies And Integration Points
Depends on DMAEngine core, OF address/IRQ/DMA helpers, platform devices, big-endian MMIO accessors, coherent DMA memory, and compatible strings `fsl,mpc5121-dma` and `fsl,mpc8308-dma`. Slave clients configure peripheral addresses and maxburst through `dma_slave_config` and request channels by OF channel id.

## Risks And Edge Cases
Slave SG refuses `sg_len != 1`, matching the file header limitation. It calls `list_first_entry(&mchan->free, ...)` before checking whether the free list is empty, which can dereference an invalid list head under descriptor exhaustion. Terminate splices prepared/queued/active back to free after clearing requests but does not handle completed callbacks. `mpc_dma_issue_pending` is a no-op because submit starts hardware immediately, which may surprise clients expecting delayed issue semantics. Error status is global and only the first pending hardware error is preserved until the tasklet drains it.

## Test Signals
Use dmatest memcpy across alignments and lengths, peripheral slave single-SG transfers with invalid and valid bus widths/maxburst, descriptor exhaustion tests, MPC8308 dual-IRQ path, error injection for DMAES decoding, terminate while active, and OF channel id lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mpc512x_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mv_xor.c -->
# sources/distributed-fs/ceph-client/drivers/dma/mv_xor.c

## Purpose
DMAEngine/async_tx driver for Marvell XOR engines. It offloads memcpy, XOR, and interrupt operations, primarily for RAID/async_tx acceleration, across Orion and Armada variants.

## Important APIs, Types, And Functions
The file uses `struct mv_xor_device`, `struct mv_xor_chan`, and `struct mv_xor_desc_slot` from `mv_xor.h`. Descriptor helpers initialize hardware descriptors, set operation mode, next pointer, and source addresses. `mv_xor_tx_submit`, `mv_chan_slot_cleanup`, `mv_xor_tasklet`, `mv_xor_status`, and `mv_xor_issue_pending` manage descriptor chains and cookies. Prep functions implement DMA_XOR, DMA_MEMCPY as one-source XOR, and DMA_INTERRUPT as a dummy minimum XOR. Probe/channel-add code configures MBUS windows, maps resources, allocates descriptor pools and dummy buffers, runs self-tests, registers per-channel DMA devices, and handles suspend/resume state.

## Control Flow
Probe maps low/high XOR register regions, determines hardware variant from DT or platform data, configures MBUS windows, enables an optional clock, limits engines/channels by CPU count, and adds each channel from DT children or platform data. Channel add maps dummy buffers, allocates a write-combined descriptor pool, installs DMAEngine callbacks based on capabilities, requests IRQ, configures operation mode, initializes lists/cookies/tasklet, runs memcpy and XOR self-tests when enabled, then registers the DMA device. Prep allocates a descriptor slot from the free list, initializes the hardware descriptor, validates/creates MBUS windows for IO addresses, and returns an async descriptor. Submit assigns a cookie, appends to the chain, links the previous hardware descriptor if needed, and starts a new chain if hardware is idle. Issue-pending activates hardware once the pending threshold is reached. IRQ logs errors, schedules the tasklet, and clears completion causes. Cleanup scans the chain for successful descriptors, unmaps, invokes callbacks, runs dependencies, moves slots to completed or free lists based on ack state, updates completed cookies, and restarts pending descriptors if the engine is idle.

## State And Persistence
State includes hardware descriptor pool memory, chain/free/allocated/completed slot lists, pending activation counter, dummy DMA mappings, saved suspend registers, cached MBUS windows, channel cookies, and XOR engine registers. It persists only for the driver/channel lifetime.

## Dependencies And Integration Points
Depends on DMAEngine and async_tx APIs, platform data or OF child nodes, IRQs, optional clocks, Marvell MBUS helpers (`mv_mbus_dram_info`, `mvebu_mbus_get_io_win_info`), coherent/write-combined DMA memory, and platform compatible strings for Orion, Armada 380, and Armada 3700. Built in through `builtin_platform_driver`.

## Risks And Edge Cases
The driver uses `BUG()`/`BUG_ON()` in descriptor mode paths and length limits, so invalid internal state can panic the kernel. `mv_xor_add_io_win` dynamically consumes a limited set of MBUS windows and can fail with `-ENOMEM`. Self-tests sleep for fixed short intervals and can disable a slow but otherwise functional channel. DMA_INTERRUPT relies on dummy buffers mapped for the driver lifetime. Error handling ignores decode errors but warns on other hardware errors; cleanup relies on descriptor success bits and current descriptor reads to avoid freeing active slots. The global `mv_xor_engine_count` is declared but not incremented in this file, so engine limiting may be ineffective depending on external context.

## Test Signals
Boot/probe self-tests for memcpy and XOR are strong signals. Additional coverage should use async_tx RAID/XOR workloads, dmatest memcpy, interrupt-only descriptors, IO-window address targets, suspend/resume register restoration, descriptor pool exhaustion, IRQ error causes, and both descriptor-mode and register-mode hardware variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mv_xor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mv_xor.h -->
# sources/distributed-fs/ceph-client/drivers/dma/mv_xor.h

## Purpose
Private definitions for the Marvell XOR DMAEngine driver, including register offsets, descriptor layout, constants, and software channel/device structures.

## Important APIs, Types, And Functions
Defines descriptor pool sizing, byte-count limits, operation modes, interrupt/error bits, channel register-address macros, MBUS window register macros, and the `WINDOW_COUNT`. `struct mv_xor_device` stores register bases, optional clock, channel pointers, variant type, and cached MBUS windows. `struct mv_xor_chan` tracks descriptor slot lists, DMAEngine channel/device objects, IRQ/tasklet, dummy buffers, mode, and saved PM registers. `struct mv_xor_desc_slot` wraps one hardware descriptor slot and async descriptor. `struct mv_xor_desc` describes the 64-byte hardware descriptor with endian-specific field ordering and `mv_phy_src_idx` abstracts descriptor-swap indexing.

## Control Flow
No executable control flow is implemented here, but macros drive register access and descriptor construction in `mv_xor.c`. Endianness conditionals alter hardware descriptor field order and source index mapping at compile time.

## State And Persistence
The header defines the in-memory state layout used by the driver: descriptor pools, linked lists, dummy DMA buffers, cached windows, and saved register values. Actual state is allocated and mutated by `mv_xor.c` at runtime.

## Dependencies And Integration Points
Depends on Linux types, I/O accessors, DMAEngine types, and IRQ types. It is included by the Marvell XOR source and must match the hardware descriptor ABI exactly, including 64-byte slot size and endian layout.

## Risks And Edge Cases
Incorrect descriptor layout, slot sizing, or endian source indexing would corrupt hardware command interpretation. `MV_XOR_MIN_BYTE_COUNT` and `MV_XOR_MAX_BYTE_COUNT` constrain prep functions. Register macros assume `mv_xor_chan` has valid low/high MMIO bases and channel indices less than `MV_XOR_MAX_CHANNELS`.

## Test Signals
Compile coverage for little- and big-endian configurations, probe self-tests from `mv_xor.c`, and hardware validation of memcpy/XOR descriptors are the main signals that these definitions match the engine ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mv_xor.h -->
