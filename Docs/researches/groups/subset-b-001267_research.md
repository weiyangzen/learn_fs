# Research Group: subset-b-001267

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/timb_dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/timb_dma.c

## Purpose
`timb_dma.c` is a Linux dmaengine platform driver for the Timberdale FPGA DMA engine. It exposes private slave DMA channels, with even/odd channel pairing used to distinguish RX (`DMA_DEV_TO_MEM`) and TX (`DMA_MEM_TO_DEV`) instances. It relies on board-supplied `struct timb_dma_platform_data` rather than device tree discovery.

## Important APIs, Types, and Functions
The central types are `struct timb_dma`, `struct timb_dma_chan`, and `struct timb_dma_desc`. `timb_dma` embeds a `struct dma_device`, the global MMIO base, one tasklet, and a flexible channel array. Each channel owns an MMIO subregion, `active_list`, `queue`, `free_list`, direction, bytes-per-line, descriptor pool sizing, and an `ongoing` flag. Each descriptor contains a dmaengine `txd`, a DMA-mapped byte descriptor list, its length, and an interrupt flag.

Key dmaengine hooks are `td_alloc_chan_resources`, `td_free_chan_resources`, `td_prep_slave_sg`, `td_tx_submit`, `td_issue_pending`, `td_tx_status`, and `td_terminate_all`. Hardware programming is concentrated in `td_fill_desc`, `__td_start_dma`, `__td_finish`, `__td_start_next`, `__td_dma_done_ack`, `td_irq`, and `td_tasklet`.

## Control Flow
Probe validates platform data, reserves and maps the MMIO resource, programs 32-bit addressing in `TIMBDMA_ACR`, clears and disables interrupts, installs a shared IRQ, initializes each configured channel, and registers the dmaengine device. Per-channel setup computes RX/TX register base from channel id and platform RX flag, initializes lists and locks, and stores descriptor count, descriptor element count, direction, and video-specific bytes-per-line.

`td_alloc_chan_resources` preallocates a platform-data-controlled number of `timb_dma_desc` objects. Each descriptor owns a software descriptor byte array that is mapped once with `dma_map_single`. `td_prep_slave_sg` checks the requested direction, takes an ACKed descriptor from `free_list`, fills one 8-byte hardware descriptor per SG element, rejects unaligned or too-large SG lengths, syncs the list for device access, and returns the dmaengine descriptor. `td_tx_submit` assigns a cookie and either starts immediately when no active descriptor exists or queues the descriptor. The engine is started by writing the descriptor list physical address to RX/TX descriptor low registers; RX additionally writes bytes-per-line and enables RX.

Completion is interrupt and tasklet driven. `td_irq` reads `TIMBDMA_IPR`, disables all Timberdale interrupts, and schedules `td_tasklet`. The tasklet filters `TIMBDMA_ISR` through `__td_ier_mask`, acknowledges completed channels, calls `__td_finish`, starts the next queued descriptor if present, and rewrites `TIMBDMA_IER` for currently interrupting transfers. `td_issue_pending` can also poll/ack completion and start the next queued descriptor. `td_terminate_all` moves queued descriptors to free and calls `__td_finish` on the active descriptor.

## State and Persistence
All runtime state is in memory and hardware registers. The driver does not persist anything across unload. Channel list state is protected by `td_chan->lock`; tasklet paths use the same lock. Descriptor buffers are mapped for DMA for the lifetime of channel resources and freed in `td_free_chan_resources`.

## Dependencies and Integration Points
The driver depends on dmaengine core helpers, Linux DMA mapping, platform resources, interrupts, MMIO accessors, and `linux/timb_dma.h` platform data. It registers a platform driver named `timb-dma` and uses `DMA_SLAVE` plus `DMA_PRIVATE` capabilities.

## Risks and Review Signals
The driver assumes valid platform data and fixed RX/TX channel parity. TX stop is explicitly unsupported in the commented-out branch of `__td_finish`, so termination may not halt TX hardware cleanly. `td_prep_slave_sg` checks `desc_usage > desc_list_len` before appending, which deserves boundary review because equality before an append can still overflow by one descriptor. Error paths after descriptor allocation must return descriptors to the free list; the no-space path currently returns `NULL` without putting the descriptor back. Tests should exercise SG length alignment, descriptor-list capacity, RX/TX direction mismatch, IRQ completion with queued follow-on transfers, terminate while active, and module probe/remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/timb_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/txx9dmac.c -->
# sources/distributed-fs/ceph-client/drivers/dma/txx9dmac.c

## Purpose
`txx9dmac.c` implements the TXx9 SoC DMA controller driver. It supports both a public memcpy channel and private slave DMA channels, with channel capabilities determined by platform data and the companion register/header definitions in `txx9dmac.h`.

## Important APIs, Types, and Functions
The implementation uses `struct txx9dmac_dev` for the controller and `struct txx9dmac_chan` for per-channel dmaengine devices. It operates on `struct txx9dmac_desc`, where a first descriptor returned to the client may own child descriptors in `tx_list` for multi-segment transfers. Important functions include the register access wrappers, `txx9dmac_desc_get/put/alloc`, `txx9dmac_dostart`, `txx9dmac_dequeue`, `txx9dmac_scan_descriptors`, `txx9dmac_handle_error`, `txx9dmac_prep_dma_memcpy`, `txx9dmac_prep_slave_sg`, `txx9dmac_issue_pending`, `txx9dmac_terminate_all`, and the controller/channel probe paths.

## Control Flow
The module registers two platform drivers: the parent `txx9dmac` controller and the child `txx9dmac-chan` channels. Parent probe maps controller registers, records whether registers are 64-bit, disables the controller, optionally registers a shared controller IRQ, programs the master control register, and stores `txx9dmac_dev`. Channel probe creates a separate `dma_device`, sets either memcpy or slave hooks, registers per-channel IRQs when no shared IRQ is present, initializes lists and locks, resets the channel, and registers the channel with dmaengine.

Transfer prep allocates one or more DMA-mapped descriptors. Memcpy prep splits large transfers by `TXX9_DMA_MAX_COUNT` and applies documented TX49 errata workarounds around suspicious transfer lengths. Slave prep validates `struct txx9dmac_slave`, direction, and register width, then builds chained descriptors from the SG list. Descriptors link through their hardware `CHAR` field; when simple-chain support is not configured, SAIR/DAIR/CCR fields are written per descriptor.

Submit assigns the dmaengine cookie and queues the descriptor on `dc->queue`. `txx9dmac_issue_pending` scans active descriptors, dequeues pending descriptors into `active_list`, starts idle hardware with `txx9dmac_dostart`, and dynamically extends an active chain on hardware that supports `SMPCHN`. Interrupt handlers disable the IRQ and schedule tasklets. Tasklets read either per-channel CSR or shared MCR bits and call `txx9dmac_scan_descriptors`, which compares the hardware chain pointer to active descriptors, completes descriptors that the hardware passed, handles abnormal chain completion, and restarts queued work.

## State and Persistence
Runtime state is held in per-channel `active_list`, `queue`, `free_list`, `descs_allocated`, and `ccr`, plus controller register state. Descriptors are DMA-mapped one by one and recycled through the free list after callbacks. Suspend and shutdown turn the controller off; resume recreates the master control register but does not persist queued transfers.

## Dependencies and Integration Points
The file depends on dmaengine, platform devices, raw MMIO accessors, DMA mapping, tasklets, and platform data structures from `asm/txx9/dmac.h`. It also depends heavily on compile-time choices in `txx9dmac.h`, including 32-bit versus 64-bit register layout and TX49 simple-chain behavior.

## Risks and Review Signals
The driver intentionally pretends some erroneous descriptors completed because dmaengine has limited error reporting here. Locking is delicate because callbacks are invoked while the channel lock is held in some completion paths, relying on dmaengine callback rules. Dynamic chain extension is hardware-feature-sensitive and should be tested with and without `SMPCHN`. Probe ordering between parent and channel platform devices is important. Test signals include memcpy splitting at errata boundaries, slave direction validation, shared and per-channel IRQ modes, abnormal CSR flags, terminate/reset behavior, suspend/resume MCR restoration, and descriptor reuse after async ACK.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/txx9dmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/txx9dmac.h -->
# sources/distributed-fs/ceph-client/drivers/dma/txx9dmac.h

## Purpose
`txx9dmac.h` defines the TXx9 DMA controller register layouts, bit definitions, software channel/device/descriptor structures, and compile-time helper functions used by `txx9dmac.c`.

## Important APIs, Types, and Functions
The header defines 64-bit and 32-bit channel register layouts (`struct txx9dmac_cregs`, `struct txx9dmac_cregs32`), controller register layouts (`struct txx9dmac_regs`, `struct txx9dmac_regs32`), and descriptor formats (`struct txx9dmac_hwdesc`, `struct txx9dmac_hwdesc32`). Driver state structures include `struct txx9dmac_chan`, `struct txx9dmac_dev`, and `struct txx9dmac_desc`.

Macros define MCR, CCR, and CSR bits, transfer-size encodings, endian selection (`CCR_LE`, `MCR_LE`), and register padding through `TXX9_DMA_REG32`. Inline helpers include `txx9_dma_have_SMPCHN`, `__is_dmac64`, `is_dmac64`, `txx9dmac_chan_INTENT`, `txx9dmac_chan_set_INTENT`, `txx9dmac_desc_set_INTENT`, `txx9dmac_chan_set_SMPCHN`, and `txx9dmac_desc_set_nosimple`.

## Control Flow and State Model
The header controls driver behavior at compile time. With `CONFIG_MACH_TX49XX`, the driver enables simple-chain support and declares `SMPCHN` available. Without simple-chain support, the descriptor type aliases to the full channel register layout so each descriptor can carry increment and control-register fields. Endianness macros decide whether little-endian mode is programmed in CCR or MCR depending on machine configuration.

`struct txx9dmac_chan` contains its own `dma_device`, tasklet, IRQ, channel CCR template, spinlock, and active/queued/free descriptor lists. `struct txx9dmac_dev` contains MMIO base, optional shared tasklet/IRQ, channel pointers, a 64-bit-register flag, and descriptor size. `struct txx9dmac_desc` deliberately places the hardware descriptor first so the DMA-mapped address points at the exact bytes consumed by hardware, followed by list nodes, child list, dmaengine descriptor, and transfer length.

## Dependencies and Integration Points
The header includes `linux/dmaengine.h` and `asm/txx9/dmac.h`, binding it to TXx9 platform data and `TXX9_DMA_MAX_NR_CHANNELS`. It is private to the driver and not a general kernel API.

## Risks and Review Signals
The main risks are ABI-like layout assumptions: register padding varies by endian and address width, and the hardware descriptor must remain first in `struct txx9dmac_desc`. Compile-time branches create materially different runtime behavior, so both simple-chain and full-descriptor builds need coverage. Review should check that field widths match hardware documentation, that 32-bit and 64-bit `CHAR` handling remains consistent, and that `TXX9_DMA_CCR_XFSZ(__ffs(width))` only sees supported power-of-two widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/txx9dmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/uniphier-mdmac.c -->
# sources/distributed-fs/ceph-client/drivers/dma/uniphier-mdmac.c

## Purpose
`uniphier-mdmac.c` is a slave-only dmaengine driver for the Socionext UniPhier MIO DMAC. It uses the shared `virt-dma` helper to handle cookies, descriptor queues, callbacks, and freeing while the driver programs one SG segment at a time into MDMAC channel registers.

## Important APIs, Types, and Functions
Driver-specific state is in `struct uniphier_mdmac_device`, `struct uniphier_mdmac_chan`, and `struct uniphier_mdmac_desc`. A descriptor stores the original SG list, SG length, current SG index, and transfer direction. Important routines are `uniphier_mdmac_next_desc`, `uniphier_mdmac_handle`, `uniphier_mdmac_start`, `uniphier_mdmac_abort`, `uniphier_mdmac_interrupt`, `uniphier_mdmac_prep_slave_sg`, `uniphier_mdmac_terminate_all`, `uniphier_mdmac_tx_status`, `uniphier_mdmac_issue_pending`, and probe/remove channel setup.

## Control Flow
Probe counts IRQs to determine channel count, sets a 32-bit DMA mask, maps registers, enables the clock, initializes the dmaengine capability mask, creates each channel with a channel-specific IRQ, registers the dmaengine device, and registers an OF DMA controller using `of_dma_xlate_by_chan_id`.

Preparation validates a slave direction, allocates a small descriptor with `GFP_NOWAIT`, stores the SG list and direction, and calls `vchan_tx_prep`. `issue_pending` moves submitted descriptors to the issued list with `vchan_issue_pending` and starts the hardware if the channel has no current descriptor. Starting removes the next issued descriptor, stores it in `mc->md`, and calls `uniphier_mdmac_handle`. `handle` chooses fixed or incrementing source/destination modes based on direction, writes source/destination addresses, transfer size, clears and enables the DONE interrupt, and starts the channel through the common command register.

The IRQ handler locks the virt-dma channel, reads detected interrupts, ignores shared-line interrupts for other channels, clears latched bits, and checks `mc->md`. A `NULL` current descriptor means an abort is in progress. Otherwise it advances `sg_cur`, completes the descriptor with `vchan_cookie_complete` at the end of the SG list, pulls the next descriptor if available, and programs the next segment.

## State and Persistence
The only durable state is hardware register state during runtime. Queue state is owned by `virt_dma_chan`; the active descriptor is tracked in `mc->md`. Termination marks the active descriptor terminated, clears `mc->md`, polls for abort acknowledgment, gathers all queued descriptors, unlocks, then frees them through `vchan_dma_desc_free_list`.

## Dependencies and Integration Points
The driver depends on clk, OF DMA, platform IRQ/resource APIs, `readl_poll_timeout`, dmaengine, and `virt-dma`. It advertises `DMA_PRIVATE`, supports `DMA_MEM_TO_DEV` and `DMA_DEV_TO_MEM`, and reports segment-level residue granularity.

## Risks and Review Signals
Residue accounting reads `CH_SIZE` for the active segment and then adds queued SG lengths from `sg_cur`, so tests should validate whether the hardware register reports remaining bytes rather than programmed bytes. The code does not consume `dma_slave_config` addresses; the register side is represented by address zero and fixed mode, so this is tightly coupled to MIO DMAC hardware semantics. Remove handles terminate failures by returning early to avoid freeing live hardware state, which intentionally leaks resources in a severe failure. Test signals include shared IRQ filtering, abort polling timeout, residue for active and queued SG elements, clock disable on probe/remove error paths, and OF channel translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/uniphier-mdmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/uniphier-xdmac.c -->
# sources/distributed-fs/ceph-client/drivers/dma/uniphier-xdmac.c

## Purpose
`uniphier-xdmac.c` implements the UniPhier external DMA controller. Unlike the MIO DMAC driver, it supports both memory copy and slave SG transfers. It uses `virt-dma` for queueing and callbacks and programs one software node at a time into per-channel XDMAC registers.

## Important APIs, Types, and Functions
Core types are `struct uniphier_xdmac_device`, `struct uniphier_xdmac_chan`, `struct uniphier_xdmac_desc`, and `struct uniphier_xdmac_desc_node`. Nodes hold source, destination, burst size, and burst count. Key functions include `uniphier_xdmac_next_desc`, `uniphier_xdmac_chan_start`, `uniphier_xdmac_chan_stop`, `uniphier_xdmac_start`, `uniphier_xdmac_chan_irq`, `uniphier_xdmac_prep_dma_memcpy`, `uniphier_xdmac_prep_slave_sg`, `uniphier_xdmac_slave_config`, `uniphier_xdmac_terminate_all`, `uniphier_xdmac_issue_pending`, and `of_dma_uniphier_xlate`.

## Control Flow
Probe reads `dma-channels`, caps it at 16, maps the register bank, initializes all channels, registers one shared IRQ, registers dmaengine, and registers an OF DMA provider. OF translation takes two arguments: channel id and request factor; it stores them in the selected channel before returning a slave channel.

Memcpy preparation rejects transfers above the hardware maximum and creates one or more nodes split by `XDMAC_MAX_WORD_SIZE` and `XDMAC_MAX_WORDS`. Slave SG preparation uses the stored `dma_slave_config` to choose device address, bus width, and max burst. It rejects maxburst values above the dmaengine maximum, unaligned SG lengths relative to burst-size units, and node burst counts above hardware capacity. `issue_pending` moves descriptors into the issued list and starts the channel if idle.

`uniphier_xdmac_chan_start` writes transfer factor, 64-bit source/destination addresses, source/destination address modes, transfer size, transfer count, interrupt enable bits, and start request. The shared IRQ handler walks all channels and calls `uniphier_xdmac_chan_irq`. On error, the channel is stopped and an error is logged. On end interrupt, the current node advances; completion calls `vchan_cookie_complete` and starts the next descriptor, while intermediate nodes are immediately programmed.

## State and Persistence
Runtime state is held in the virt-dma lists, active descriptor pointer `xc->xd`, per-channel slave config, channel id, and request factor. There is no persistent state. Removal synchronously terminates every channel before unregistering the OF DMA controller and dmaengine device.

## Dependencies and Integration Points
The file depends on OF DMA, platform devices, `virt-dma`, bitfield helpers, MMIO accessors, and dmaengine slave/memcpy APIs. It advertises `DMA_MEMCPY` and `DMA_SLAVE`, supports `DMA_DEV_TO_MEM`, `DMA_MEM_TO_DEV`, and `DMA_MEM_TO_MEM`, and reports burst-level residue granularity while using plain `dma_cookie_status` for status.

## Risks and Review Signals
Memcpy node count is computed as `1 + len / XDMAC_MAX_WORD_SIZE`, which can over-allocate for exact multiples and can produce a zero-length final node depending on the loop inputs. Slave SG rejects residue-sized tails, so clients must configure maxburst carefully. IRQ handling scans every channel and always returns handled, which is typical for shared hardware summary IRQs but can mask unrelated interrupts if the line is shared externally. Tests should cover OF request-factor programming, memcpy boundary sizes, slave unaligned SG rejection, channel stop timeout, error interrupt behavior, and remove with active descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/uniphier-xdmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/virt-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/virt-dma.c

## Purpose
`virt-dma.c` implements the exported non-inline parts of the dmaengine virtual channel helper. It centralizes cookie submission, descriptor lookup, callback/tasklet completion, descriptor freeing, and channel initialization for DMA drivers that want common list and callback handling while programming their own hardware.

## Important APIs, Types, and Functions
The file operates on `struct virt_dma_chan` and `struct virt_dma_desc` from `virt-dma.h`. Exported functions are `vchan_tx_submit`, `vchan_tx_desc_free`, `vchan_find_desc`, `vchan_dma_desc_free_list`, and `vchan_init`. The internal `vchan_complete` tasklet drains completed descriptors and cyclic callbacks.

## Control Flow
Drivers allocate a descriptor embedding `struct virt_dma_desc`, call `vchan_tx_prep` from the header, and later the dmaengine core invokes `vchan_tx_submit`. `vchan_tx_submit` locks the virtual channel, assigns a cookie, and moves the descriptor from `desc_allocated` to `desc_submitted`. Driver `issue_pending` hooks call `vchan_issue_pending` to move submitted work to `desc_issued`, then program hardware from `vchan_next_desc`.

When hardware completes a descriptor, the driver calls `vchan_cookie_complete`, which completes the cookie, moves the descriptor to `desc_completed`, and schedules `vc->task`. `vchan_complete` splices completed descriptors locally, snapshots a pending cyclic callback if present, releases the lock, invokes callbacks, and finalizes each completed descriptor with `vchan_vdesc_fini`. Descriptor finalization either returns reusable descriptors to `desc_allocated` or calls the driver's `desc_free` hook. `vchan_tx_desc_free` supports explicit freeing of reusable descriptors by removing the descriptor from whatever list it is on and invoking `desc_free`.

## State and Persistence
All state is per-channel and volatile: five descriptor lists, one cyclic callback pointer, a spinlock, and a tasklet. The helper does not store hardware state. `vchan_init` initializes cookies, lock, lists, tasklet, connects the channel to the dma_device, and appends it to the device channel list.

## Dependencies and Integration Points
This file exports GPL-only symbols and is used by many dmaengine drivers. It depends on dmaengine callback helpers, tasklets, spinlocks, list APIs, and the local `dmaengine.h` wrapper. Its contract requires most list operations to be performed under `vc->lock`, with callbacks invoked outside the lock by the helper tasklet.

## Risks and Review Signals
Drivers must remove an issued descriptor from `desc_issued` before or as part of completion when their hardware model requires it; the helper does not infer hardware progress. `vchan_find_desc` only searches `desc_issued`, so residue/status support for active descriptors must be compatible with that list model. `vchan_synchronize` kills the tasklet and frees terminated cyclic descriptors, so callers must prevent new callbacks before invoking it. Tests should cover descriptor reuse, cyclic callback ordering, terminate followed by synchronize, explicit reusable descriptor free, and lockdep expectations around helper calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/virt-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/virt-dma.h -->
# sources/distributed-fs/ceph-client/drivers/dma/virt-dma.h

## Purpose
`virt-dma.h` is the shared helper interface for virtual dmaengine channels. It defines the channel and descriptor data structures and provides inline operations for descriptor preparation, queue promotion, completion, cyclic callbacks, termination, resource cleanup, and synchronization.

## Important APIs, Types, and Functions
`struct virt_dma_desc` wraps a dmaengine transaction descriptor, a `dmaengine_result`, and a list node protected by the channel lock. `struct virt_dma_chan` embeds `struct dma_chan`, a completion tasklet, a driver-supplied `desc_free` hook, a spinlock, descriptor lists for allocated/submitted/issued/completed/terminated states, and a cyclic descriptor pointer.

The header declares the exported functions implemented in `virt-dma.c` and defines inline helpers: `to_virt_chan`, `vchan_tx_prep`, `vchan_issue_pending`, `vchan_cookie_complete`, `vchan_vdesc_fini`, `vchan_cyclic_callback`, `vchan_terminate_vdesc`, `vchan_next_desc`, `vchan_get_all_descriptors`, `vchan_free_chan_resources`, and `vchan_synchronize`.

## Control Flow and State Model
The state machine is explicit. Prepared descriptors enter `desc_allocated`; submit moves them to `desc_submitted`; `vchan_issue_pending` moves them to `desc_issued`; drivers pull from `desc_issued` with `vchan_next_desc`; completion moves them to `desc_completed`; the tasklet invokes callbacks and either frees or recycles descriptors. Terminated descriptors move to `desc_terminated` and are released during synchronization or resource cleanup.

`vchan_tx_prep` initializes dmaengine descriptor fields, sets the common submit and reusable-free callbacks, initializes result state to `DMA_TRANS_NOERROR`, and appends to the allocated list. `vchan_cookie_complete` must be called with the lock held and schedules callback processing. `vchan_get_all_descriptors` drains all lists into a caller-provided list, which is why terminate and free-resource paths can gather state under lock and free after unlocking.

## Dependencies and Integration Points
The header depends on dmaengine, interrupts/tasklets, and the local dmaengine helper header. It is used across many DMA drivers, including the UniPhier and Xilinx XDMA drivers in this work item.

## Risks and Review Signals
The helper is small but central, so misuse is more likely than internal complexity. Drivers must honor lock requirements, must set `vc->desc_free` before descriptors can be freed, and must not schedule new callbacks while synchronizing. Because `vchan_free_chan_resources` clears reuse on every drained descriptor before freeing, reusable descriptor clients need tests around final release. Review signals include lockdep warnings, list corruption after termination, double completion of cyclic descriptors, and drivers that forget to remove active descriptors from issued state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/virt-dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/xgene-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/xgene-dma.c

## Purpose
`xgene-dma.c` is the Applied Micro X-Gene SoC DMA engine driver. Its exposed dmaengine functionality is focused on async_tx RAID offload, specifically XOR and PQ generation, rather than generic memcpy or slave DMA.

## Important APIs, Types, and Functions
Important hardware/software types are `struct xgene_dma_desc_hw`, `struct xgene_dma_desc_sw`, `struct xgene_dma_ring`, `struct xgene_dma_chan`, and `struct xgene_dma`. Descriptor helpers include `xgene_dma_init_desc`, `xgene_dma_set_src_buffer`, `xgene_dma_lookup_ext8`, `xgene_dma_prep_xor_desc`, `xgene_dma_prep_xor`, and `xgene_dma_prep_pq`. Queue and completion paths include `xgene_dma_tx_submit`, `xgene_chan_xfer_request`, `xgene_chan_xfer_ld_pending`, `xgene_dma_cleanup_descriptors`, `xgene_dma_run_tx_complete_actions`, and `xgene_dma_clean_running_descriptor`. Hardware setup functions include ring creation/deletion, interrupt setup, memory bring-up, and async registration.

## Control Flow
Probe maps four MMIO regions: DMA CSR, ring CSR, ring command CSR, and efuse CSR. It optionally enables a clock, brings ring-manager and DMA RAM out of shutdown, sets a 42-bit coherent DMA mask, initializes channel software state, allocates per-channel TX/RX hardware rings, requests one error IRQ and one RX-ring IRQ per channel, enables the DMA engine, and registers one dmaengine device per hardware channel.

Capabilities are selected per channel. Channel 1 exposes PQ and XOR if PQ is enabled by efuse. Channel 0 exposes XOR only when PQ is disabled, avoiding a documented hardware hang when channel 0 and channel 1 run XOR/PQ simultaneously. Prep functions allocate software descriptors from a DMA pool, build one or two hardware descriptors per request chunk, and chain all chunk descriptors through the returned descriptor's `tx_list`. XOR/PQ transfers are split into chunks no larger than the hardware buffer length.

Submit assigns a cookie only to the client-visible descriptor and splices the descriptor group into `ld_pending`. `issue_pending` pushes pending descriptors to the TX hardware ring until `max_outstanding` is reached. The hardware reports completions through RX rings initialized with an empty signature. The channel ISR disables the RX IRQ and schedules a tasklet. The tasklet cleans completed RX descriptors, reports descriptor-level errors, notifies hardware that completions were consumed, decrements pending counts, starts more pending work, invokes callbacks, completes cookies, runs dependencies, and frees or parks descriptors depending on async ACK state.

## State and Persistence
Runtime state lives in ring head pointers, ring descriptors, `pending`, `max_outstanding`, and three descriptor lists: `ld_pending`, `ld_running`, and `ld_completed`. There is no persistent state. Remove unregisters dmaengine devices, masks interrupts, disables hardware, frees IRQs, kills tasklets, deletes rings, and disables the clock.

## Dependencies and Integration Points
The driver supports OF compatible `apm,xgene-storm-dma` and ACPI id `APMC0D43`. It depends on dmaengine async_tx XOR/PQ APIs, DMA pools, coherent ring allocation, platform resources, IRQ APIs, optional clocks, and efuse state.

## Risks and Review Signals
The descriptor error status indexes into sparse error string arrays; unexpected status values could produce invalid lookup if not constrained by hardware. IRQ cleanup has a suspicious loop in the request-error path that assigns `chan = &pdma->chan[i]` inside a `for (j = 0; j < i; j++)`, likely freeing the wrong channel repeatedly. Descriptor grouping relies on only the last descriptor having the client cookie. Tests should cover PQ efuse-enabled and disabled systems, max outstanding ring pressure, 64-byte descriptor paths, completion error descriptors, IRQ request failure unwinding, async ACK delayed freeing, and probe/remove after partial setup failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/xgene-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/xilinx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dma/xilinx/Makefile

## Purpose
This Makefile selects the Xilinx DMA-family objects built for the kernel based on Kconfig symbols. It is a build integration file, not runtime code.

## Important Entries
The file maps `CONFIG_XILINX_DMA` to `xilinx_dma.o`, `CONFIG_XILINX_XDMA` to `xdma.o`, `CONFIG_XILINX_ZYNQMP_DMA` to `zynqmp_dma.o`, and `CONFIG_XILINX_ZYNQMP_DPDMA` to `xilinx_dpdma.o`. The SPDX tag is `GPL-2.0-only`.

## Control Flow and State
There is no runtime control flow or persistent state. Kbuild evaluates the `obj-$(CONFIG_...)` assignments and includes the matching objects in the driver build.

## Dependencies and Integration Points
The integration point is the kernel Kbuild system and the corresponding Kconfig symbols. The `xdma.o` entry is the build hook for `sources/distributed-fs/ceph-client/drivers/dma/xilinx/xdma.c`.

## Risks and Test Signals
The main risk is configuration drift: if a source file is renamed, split, or gated by a different symbol, this Makefile must stay synchronized. Test signals are simple: build with each Xilinx DMA config enabled individually and together, and confirm the intended object files are compiled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/xilinx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/xilinx/xdma-regs.h -->
# sources/distributed-fs/ceph-client/drivers/dma/xilinx/xdma-regs.h

## Purpose
`xdma-regs.h` defines the AMD/Xilinx XDMA register offsets, descriptor format, control/status bit masks, and helper macros consumed by `xdma.c`.

## Important APIs, Types, and Constants
The header defines a 64 KiB register space, up to four H2C and four C2H channels, descriptor-block constants, and `struct xdma_hw_desc`. Hardware descriptors are 32-byte little-endian records with control, byte count, source address, destination address, and next-descriptor pointer. `XDMA_DESC_CONTROL`, `XDMA_DESC_CONTROL_LAST`, and `XDMA_DESC_CONTROL_CYCLIC` construct descriptor control words with magic, adjacent descriptor count, and flags.

Channel register offsets cover identifier, control, status, completed descriptor count, alignment, interrupt enable, and SGDMA descriptor pointer registers. Macros such as `XDMA_CHAN_CHECK_TARGET` validate channel presence and direction by identifier magic. Interrupt register definitions cover user and channel interrupt enable/request/pending registers and vector-number tables.

## Control Flow and State Model
There is no runtime flow in this file, but its constants drive the `xdma.c` state machine. Descriptor block sizing determines allocation from DMA pools and limits cyclic descriptors to one adjacent block. Channel control masks decide which hardware conditions are treated as start bits, interrupts, and errors. Interrupt vector constants define how MSI-X vectors are packed four per register.

## Dependencies and Integration Points
The header expects Linux bit helpers such as `BIT`, `GENMASK`, and `FIELD_PREP` to be available through including C files. It is private to the Xilinx XDMA driver directory and integrated directly by `xdma.c`.

## Risks and Review Signals
Register definitions are hardware-contract sensitive. Any wrong offset, endian assumption, descriptor size, block alignment, or control-bit mask can produce silent DMA corruption. `XDMA_DESC_BLEN_MAX` subtracts `PAGE_SIZE` from a 28-bit max, so tests should include transfer splitting around that boundary. Review should validate channel magic values, vector packing, descriptor block boundary constraints, and error-mask coverage against current XDMA hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/xilinx/xdma-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/xilinx/xdma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/xilinx/xdma.c

## Purpose
`xdma.c` is the AMD/Xilinx DMA/Bridge Subsystem driver for PCIe-attached XDMA platform devices. It exposes H2C and C2H slave DMA channels and supports normal SG transfers, cyclic transfers, interleaved transfers, repeat/load-EOT semantics, and exported user interrupt helpers.

## Important APIs, Types, and Functions
Core types are `struct xdma_device`, `struct xdma_chan`, `struct xdma_desc`, and `struct xdma_desc_block`. The driver uses `virt-dma` for dmaengine queueing and callback dispatch, `regmap` for MMIO access, and DMA pools for hardware descriptor blocks. Important functions include `xdma_alloc_channels`, `xdma_channel_init`, `xdma_alloc_desc`, `xdma_link_sg_desc_blocks`, `xdma_link_cyclic_desc_blocks`, `xdma_fill_descs`, `xdma_xfer_start`, `xdma_xfer_stop`, `xdma_prep_device_sg`, `xdma_prep_dma_cyclic`, `xdma_prep_interleaved_dma`, `xdma_issue_pending`, `xdma_terminate_all`, `xdma_synchronize`, `xdma_tx_status`, `xdma_channel_isr`, `xdma_irq_init/fini`, and exported `xdma_enable_user_irq`, `xdma_disable_user_irq`, and `xdma_get_user_irq`.

## Control Flow
Probe reads platform data, IRQ resource range, and MMIO resource, creates a regmap, detects available H2C and C2H channels by reading channel identifiers, initializes each channel, registers dmaengine capabilities, registers the dmaengine device, and assigns channel/user interrupt vectors. Channel allocation scans up to `pdata->max_dma_channels`, validates direction-specific identifier magic, initializes `virt_dma_chan`, and records register base and transfer direction.

Channel resources allocate a descriptor-block DMA pool on the parent PCI device. Prep paths allocate enough descriptor blocks, fill hardware descriptors with split chunks no larger than `XDMA_DESC_BLEN_MAX`, and then call `vchan_tx_prep`. SG prep uses `dma_slave_config` source or destination address as the device-side address and increments it by SG length. Cyclic prep limits period size and period count to one descriptor block. Interleaved prep creates descriptors for the template frame segments and records repeat/cyclic metadata.

`issue_pending` promotes submitted descriptors and starts the channel if possible. `xdma_xfer_start` clears run/stop, validates request direction, points hardware at the first uncompleted descriptor block, programs adjacent descriptor count, starts the engine, marks the channel busy, clears stop state, and reinitializes the last-interrupt completion. The ISR reads clear-on-read status, marks errors, reads completed descriptor count, and updates descriptor progress. Non-cyclic SG may restart at the next descriptor block when a hardware completion reports exactly the maximum block count. Cyclic and repeat interleaved transfers invoke `vchan_cyclic_callback`; finite transfers remove the descriptor from the issued list and complete the cookie.

## State and Persistence
Runtime state is volatile: per-channel busy/stop flags, completions, slave config, descriptor pools, virt-dma lists, descriptor progress counters, and hardware registers. Termination stops the engine, completes and terminates the active descriptor, drains all virt-dma lists into the terminated list, and synchronization waits for a final interrupt if hardware is still busy before killing callbacks.

## Dependencies and Integration Points
The driver depends on platform data from `linux/platform_data/amd_xdma.h`, exported AMD XDMA user IRQ API declarations, PCI parent discovery for descriptor pools, regmap MMIO, dmaengine, `virt-dma`, and constants from `xdma-regs.h`. It registers as platform driver id `xdma` and exports user IRQ control symbols for companion drivers.

## Risks and Review Signals
The code assumes platform data is present; probe dereferences `pdata` before checking for `NULL`. `xdma_issue_pending` ignores `xdma_xfer_start` errors. Interleaved repeat logic uses list inspection around the active node and should be stress-tested with `DMA_PREP_REPEAT` and `DMA_PREP_LOAD_EOT`. Error interrupts mark `desc->error` but do not obviously complete or terminate the descriptor immediately, so client-visible error progress should be verified. Test signals include channel detection for missing H2C/C2H channels, IRQ-vector packing with user IRQs, SG splitting across descriptor blocks, cyclic residue, terminate/synchronize while busy, missing PCI parent handling, and exported user IRQ boundary checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/xilinx/xdma.c -->
