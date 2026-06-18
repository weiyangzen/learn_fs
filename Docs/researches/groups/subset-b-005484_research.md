# subset-b-005484 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/hcd.c

## Purpose

`hcd.c` is the core Linux host-controller-driver implementation for the Synopsys DesignWare HS OTG (`dwc2`) controller in host mode. It bridges the Linux USB core `hc_driver` callbacks to DWC2 hardware programming, queue-head/transfer-descriptor scheduling, root-hub emulation, OTG role switching, DMA/slave-mode transfer setup, suspend/resume, hibernation, and partial power-down handling.

The file is not related to Ceph semantics despite its path under `distributed-fs/ceph-client`; it is Linux USB host-controller code embedded in the source tree.

## Important APIs, types, and functions

- Core initialization and hardware setup:
  - `dwc2_core_init()` programs global USB/AHB config, initializes PHY, selects host/device operating state, and enables common interrupts.
  - `dwc2_core_host_init()` configures host clocking, descriptor DMA mode, dynamic FIFO layout, FIFO flushing, port power, ACG, and host interrupts.
  - `dwc2_config_fifos()` and `dwc2_calculate_dynamic_fifo()` size Rx, non-periodic Tx, and periodic Tx FIFOs using controller parameters and hardware FIFO depth.
  - `dwc2_calc_frame_interval()` calculates `HFIR` frame interval from PHY type and port speed.
- Host channel lifecycle:
  - `dwc2_hc_init()` writes `HCCHAR`, `HCSPLT`, and channel interrupt masks from `struct dwc2_host_chan`.
  - `dwc2_hc_start_transfer()` sets up slave/buffer-DMA transfers through `HCTSIZ`, `HCDMA`, `HCSPLT`, and `HCCHAR`.
  - `dwc2_hc_start_transfer_ddma()` programs descriptor-DMA transfer metadata and starts a channel using a descriptor list DMA address.
  - `dwc2_hc_continue_transfer()` queues follow-up slave-mode IN/OUT requests.
  - `dwc2_hc_halt()` handles channel halt semantics for normal completion, dequeue, AHB error, queue-space limitations, DMA, and descriptor DMA.
  - `dwc2_hc_cleanup()` clears channel interrupts and software transfer state.
- Scheduling and queuing:
  - `dwc2_hcd_select_transactions()` moves QHs from ready/inactive schedules onto free host channels.
  - `dwc2_hcd_queue_transactions()` dispatches periodic and non-periodic work to `dwc2_process_periodic_channels()` and `dwc2_process_non_periodic_channels()`.
  - `dwc2_queue_transaction()` chooses between descriptor DMA, buffer DMA, ping, halt-on-queue, initial transfer start, and continued slave-mode transfer.
- URB integration:
  - `_dwc2_hcd_urb_enqueue()` adapts a Linux `struct urb` into `struct dwc2_hcd_urb`, creates or reuses an endpoint QH, allocates a QTD, links the URB to the USB core, and starts scheduling.
  - `dwc2_hcd_urb_enqueue()` initializes and adds the QTD to a QH, then opportunistically queues transactions if SOF scheduling is not currently active.
  - `_dwc2_hcd_urb_dequeue()` and `dwc2_hcd_urb_dequeue()` halt in-process channels when needed, unlink/free QTDs, and give the URB back.
  - `dwc2_host_complete()` copies final lengths and isochronous frame statuses back to the Linux URB and calls `usb_hcd_giveback_urb()`.
  - `dwc2_map_urb_for_dma()` / `dwc2_unmap_urb_for_dma()` wrap HCD DMA mapping with DWC2-specific temporary aligned buffers for unaligned transfer buffers.
- Root hub and OTG:
  - `dwc2_hcd_hub_control()` implements one-port root hub class requests including power, reset, suspend/resume, status, overcurrent, test mode, and L1 status change clearing.
  - `_dwc2_hcd_hub_status_data()` reports root-port status-change bits.
  - `dwc2_conn_id_status_change()` handles connector ID changes and switches between peripheral and host paths.
  - `dwc2_hcd_connect()` and `dwc2_hcd_disconnect()` update software port flags, kill URBs, clean channels, and handle reconnect races.
- Linux HCD registration:
  - `dwc2_hc_driver` supplies `start`, `stop`, `urb_enqueue`, `urb_dequeue`, endpoint, frame, hub, bus suspend/resume, and DMA mapping callbacks.
  - `dwc2_hcd_init()` creates the `usb_hcd`, initializes lists/work/timers/channels/caches/status buffers, registers the bus via `usb_add_hcd()`, and enables global interrupts.
  - `dwc2_hcd_remove()` removes the HCD, clears OTG host registration, destroys caches, releases channels/lists/timers/workqueues, and drops the HCD reference.
- Power management:
  - `_dwc2_hcd_suspend()` / `_dwc2_hcd_resume()` integrate with USB bus suspend/resume.
  - `dwc2_backup_host_registers()` / `dwc2_restore_host_registers()` persist host registers across low-power states.
  - `dwc2_host_enter_hibernation()` / `dwc2_host_exit_hibernation()` implement host hibernation sequencing through `GPWRDN`, `HPRT0`, `PCGCTL`, and register backups.
  - `dwc2_host_enter_partial_power_down()` / `dwc2_host_exit_partial_power_down()` implement partial power-down.
  - `dwc2_host_enter_clock_gating()` / `dwc2_host_exit_clock_gating()` implement lower-cost clock gating.

## Control flow

Initialization starts in `dwc2_hcd_init()`: it validates USB availability, configures DMA masks and `hc_driver` flags, creates a `usb_hcd`, stores `hsotg` in private wrapper data, disables global interrupts, runs `dwc2_core_init()`, creates workqueue/timer state, initializes all periodic and non-periodic scheduler lists, allocates host-channel descriptors, status buffers, descriptor DMA caches, and unaligned DMA buffers, then calls `usb_add_hcd()`. The USB core invokes `_dwc2_hcd_start()`, which sets `L0`, marks hardware accessible, reinitializes host state through `dwc2_hcd_reinit()`, powers VBUS, and resumes the root hub.

Normal URB submission enters `_dwc2_hcd_urb_enqueue()`. The function exits low-power modes if necessary, derives endpoint type/direction/max packet data, allocates a DWC2 URB wrapper and QTD, creates an endpoint QH if absent, links the URB to the USB core under `hsotg->lock`, and calls `dwc2_hcd_urb_enqueue()`. The lower helper initializes the QTD and adds it to the QH. If scheduling can proceed immediately, it selects transactions and queues them.

Transaction selection first drains periodic ready QHs while host channels remain, then non-periodic inactive QHs subject to available channel accounting. `dwc2_assign_and_init_hc()` binds the first QTD of a QH to a free `dwc2_host_chan`, initializes endpoint, split, direction, PID, buffer/DMA address, DMA alignment, and descriptor-list fields, then programs the hardware channel via `dwc2_hc_init()`. Queuing then starts transfers directly in DMA mode, fills FIFO requests in slave mode, or delegates to `hcd_ddma.c` via `dwc2_hcd_start_xfer_ddma()` when descriptor DMA is enabled.

Interrupt-driven progress is split across this file and interrupt-handler files declared in `hcd.h`. Completion eventually calls `dwc2_host_complete()` for URB giveback and deactivates/requeues QHs through queue helpers. Descriptor DMA completion is delegated to `dwc2_hcd_complete_xfer_ddma()` in `hcd_ddma.c`.

Disconnect and stop flows set root-hub status-change flags, mask host interrupts, kill all URBs across all QH lists, clean or halt active channels, reset software channel ownership, clear root-hub host flags, and turn off port power when appropriate. Endpoint disable waits for QTDs to drain, unlinks the QH, frees QTDs, clears `ep->hcpriv`, and frees QH resources outside the spinlock.

## State and persistence behavior

Persistent runtime state lives primarily in `struct dwc2_hsotg`, `struct dwc2_qh`, `struct dwc2_qtd`, `struct dwc2_host_chan`, and `struct dwc2_hcd_urb`. `hcd.c` owns multiple linked-list schedules: `non_periodic_sched_inactive`, `non_periodic_sched_waiting`, `non_periodic_sched_active`, `periodic_sched_inactive`, `periodic_sched_ready`, `periodic_sched_assigned`, `periodic_sched_queued`, `free_hc_list`, and `split_order`.

Root hub state is persisted in `hsotg->flags` bitfields for connect, enable, suspend, reset, overcurrent, and L1 change reporting. Power state is persisted in `lx_state`, `bus_suspended`, `hibernated`, `in_ppd`, and `op_state`. Descriptor DMA and buffer DMA resources are persisted in `status_buf`, descriptor kmem caches, unaligned DMA cache, channel descriptors, and HCD private wrapper data.

Low-power persistence uses `hsotg->gr_backup` and `hsotg->hr_backup`. `dwc2_backup_host_registers()` stores `HCFG`, `HFLBADDR`, `HAINTMSK`, all per-channel host registers, `HPRT0`, `HFIR`, and `HPTXFSIZ`, then marks the backup valid. Restore consumes that valid bit and rewrites the registers, so restore without a valid backup returns `-EINVAL`.

The code uses spinlocks around schedule, channel, and root-hub state updates; drops the lock around sleeping operations, regulator operations, USB PHY suspend calls, and USB giveback where required by kernel locking rules.

## Dependencies and integration points

This file depends on Linux USB core APIs (`usb_hcd`, `urb`, hub class requests, bandwidth accounting, DMA mapping, root hub resume/giveback/link/unlink helpers), Linux kernel concurrency and memory APIs (`spin_lock_irqsave`, workqueues, timers, kmem caches, DMA coherent/single mappings, regulators, PHY APIs), and DWC2 core helpers/register definitions from `core.h` and `hcd.h`.

It integrates laterally with:

- `hcd.h` for QH/QTD/channel declarations and helper prototypes.
- `hcd_queue.c` for QH/QTD creation, queue insertion/removal, deactivation, scheduler timing, and data-toggle save helpers.
- `hcd_intr.c` or equivalent interrupt logic through `dwc2_handle_hcd_intr()` and channel halt status handling.
- `hcd_ddma.c` through descriptor-DMA start, completion, QH init/free, and channel transfer programming.
- Device-mode/gadget code through role switching in `dwc2_conn_id_status_change()` and common power-management helpers.

## Risks and edge cases

- Register programming is order-sensitive. Incorrect sequencing around `HCCHAR_CHENA`, `HCCHAR_CHDIS`, `HCSPLT_SPLTENA`, `HCTSIZ`, and `HCDMA` can hang channels or corrupt transfer state.
- DMA alignment handling is subtle. The code uses temporary aligned buffers for unaligned URBs and split IN DMA; missed copy-back or mapping errors can corrupt data.
- URB dequeue and completion race with hardware interrupts and USB giveback callbacks. Several paths explicitly clear channel interrupts or check halt status to avoid use-after-free on QH/QTD state.
- Descriptor DMA is conditionally enabled only on supported hardware and may be disabled at runtime if caches cannot be created or full-speed descriptor DMA conditions are not met.
- Low-power flows depend on valid backup registers and precise timing delays. Hibernation and partial power-down paths can leave the controller inaccessible if wake/restore sequencing fails.
- Root-hub status emulation must keep software flags coherent with `HPRT0`; missed clearing or setting can cause enumeration, suspend/resume, or reconnect failures.
- Some comments mark TODO/FIXME areas: FIFO allocation could fail for small total FIFO depth, descriptor DMA periodic rollover handling is incomplete, and older debug comments suggest legacy integration assumptions.

## Test signals

Useful validation signals include successful `usb_add_hcd()` registration, root hub enumeration, control transfer setup/status completion, bulk IN/OUT transfers, interrupt and isochronous periodic scheduling, disconnect while URBs are active, endpoint disable/reset, unaligned DMA URBs, split transactions through a high-speed hub, VBUS regulator balance on start/stop and hub power requests, suspend/resume across all configured power-down modes, hibernation restore with remote wakeup and reset, and descriptor-DMA fallback on unsupported hardware.

Kernel dynamic debug around `dev_dbg`/`dev_vdbg`, USB core URB status/actual-length checks, frame-number behavior, and warnings from `WARN_ON_ONCE()` or timeout logs in endpoint disable/channel halt paths are direct runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/hcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/hcd.h -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/hcd.h

## Purpose

`hcd.h` is the host-mode interface and state contract for the DWC2 host controller driver. It declares the software representations of host channels, URB wrappers, queue heads, queue transfer descriptors, transaction types, transaction translator accounting, frame helpers, root-hub/HCD entry points, and descriptor-DMA hooks used by `hcd.c`, `hcd_ddma.c`, interrupt handling, and queue scheduling code.

## Important APIs, types, and functions

- `struct dwc2_host_chan` models one hardware host channel and stores endpoint address/direction/type/speed, max packet, PID, transfer buffer/DMA positions, split transaction metadata, halt flags, descriptor-DMA metadata, interrupt snapshot, QH ownership, and list links.
- `struct dwc2_hcd_pipe_info` stores normalized endpoint data copied from Linux USB pipe/endpoint descriptors.
- `struct dwc2_hcd_iso_packet_desc` mirrors per-packet isochronous offset, length, actual length, and status for DWC2's internal URB wrapper.
- `struct dwc2_hcd_urb` wraps a Linux URB with DWC2-owned fields including buffer/setup DMA, length, actual length, status, error count, interval, flags, pipe info, and flexible isochronous packet descriptors.
- `enum dwc2_control_phase` tracks control transfer phase: setup, data, status.
- `enum dwc2_transaction_type` communicates whether scheduling found periodic, non-periodic, both, or no work.
- `struct dwc2_tt` stores DWC2-specific transaction-translator refcounting and low-speed/full-speed periodic bitmaps in `usb_tt->hcpriv`.
- `struct dwc2_hs_transfer_time` describes high-speed schedule time slices used by periodic scheduling.
- `struct dwc2_qh` stores static endpoint scheduling state and dynamic QTD/channel ownership: endpoint type/direction/speed, toggles, ping state, split state, host/device bus time, intervals, next active frame, descriptor-DMA list state, TT information, timers, and scheduling flags.
- `struct dwc2_qtd` stores transfer-local state: control phase, in-process bit, data toggle, split/isoc progress, error/NAK counters, descriptor counts, URB pointer, QH pointer, and list link.
- Inline helpers provide:
  - HCD conversion: `dwc2_hsotg_to_hcd()`.
  - Safe HPRT0 read-modify-write base: `dwc2_read_hprt0()`.
  - Pipe classification/accessors such as `dwc2_hcd_is_pipe_isoc()`, `dwc2_hcd_is_pipe_in()`, and `dwc2_hcd_get_maxp()`.
  - Debug filtering: `dbg_hc()`, `dbg_qh()`, `dbg_urb()`, `dbg_perio()`.
  - Frame arithmetic with rollover: `dwc2_frame_idx_num_gt()`, `dwc2_frame_num_le()`, `dwc2_frame_num_gt()`, `dwc2_frame_num_inc()`, `dwc2_frame_num_dec()`, `dwc2_full_frame_num()`, `dwc2_micro_frame_num()`.
  - Interrupt masking/status: `disable_hc_int()`, `dwc2_read_core_intr()`.
  - URB status and isochronous descriptor accessors.
  - Bandwidth helpers using endpoint `hcpriv`.
  - `dwc2_hcd_qtd_unlink_and_free()` for QTD removal/free.
- Exported/prototyped functions include host init/remove, channel cleanup/halt/DDMA transfer start, transaction select/queue, QH/QTD management from `hcd_queue.c`, descriptor DMA QH lifecycle and completion, interrupt handling, stop, B-host detection, dump, data-toggle save, TT info management, speed lookup, and completion.

## Control flow

The header defines the dataflow between Linux USB URBs and hardware channel programming. A Linux URB is represented by `dwc2_hcd_urb`, attached to a `dwc2_qtd`, linked under a `dwc2_qh`, and eventually assigned to a `dwc2_host_chan`. QH/QTD scheduling functions decide when work is eligible; `hcd.c` binds QHs to channels and programs registers; interrupt and DDMA completion code update QTD/URB state and free or requeue QHs.

Frame helpers are used throughout periodic scheduling and descriptor DMA to compare frame numbers modulo the hardware frame counter. The `dwc2_tt` and periodic bitmap fields support full/low-speed traffic through high-speed transaction translators by reserving low-speed schedule slices per TT/port.

## State and persistence behavior

The types in this header define nearly all host-mode persistent state outside `struct dwc2_hsotg`. `dwc2_host_chan` persists per-channel hardware ownership and transfer progress until cleanup or release. `dwc2_qh` persists endpoint-level scheduling state across multiple URBs. `dwc2_qtd` persists one URB's progress until completion/dequeue. `dwc2_hcd_urb` persists the DWC2 view of a Linux URB and is freed at giveback or dequeue.

The header also codifies pointer ownership conventions: endpoint `hcpriv` points to a `dwc2_qh`, Linux URB `hcpriv` points to a `dwc2_hcd_urb`, `dwc2_hcd_urb->qtd` points to its QTD, QTDs live on `qh->qtd_list`, and channels point back to their active QH. Descriptor-DMA state is held in QH descriptor list fields and mirrored into the channel at assignment.

## Dependencies and integration points

`hcd.h` depends on DWC2 register constants and core structures from `core.h`/included compilation units, Linux USB endpoint and URB definitions, kernel list/timer/hrtimer types, DMA address types, and USB speed/endpoint constants.

It is the shared contract among:

- `hcd.c` for HCD registration, URB, channel, root-hub, and power-management operations.
- `hcd_ddma.c` for descriptor-list allocation, frame-list programming, descriptor scanning, and DDMA transfer completion.
- `hcd_queue.c` for QH/QTD scheduling and periodic reservation.
- Interrupt handling for `dwc2_handle_hcd_intr()`, channel interrupt masking, halt statuses, and data-toggle save.

## Risks and edge cases

- Bitfield widths in `dwc2_host_chan` assume USB and DWC2 register field limits; widening endpoint, address, packet, PID, or speed values without adjusting them could truncate state.
- Frame arithmetic helpers rely on modulo assumptions (`FRLISTEN_64_SIZE`, `HFNUM_MAX_FRNUM`) and are critical for rollover-safe scheduling.
- `dwc2_hcd_qtd_unlink_and_free()` only unlinks and frees the QTD; callers must handle URB wrapper cleanup, completion, and QH deactivation correctly.
- Debug helper behavior changes under `CONFIG_USB_DWC2_DEBUG_PERIODIC`, which can significantly increase log volume.
- The header exposes many functions implemented elsewhere; mismatched assumptions about locking are a risk because several prototypes require callers to hold or not hold `hsotg->lock` as documented in implementation comments rather than encoded in types.

## Test signals

Compile-time coverage is a major signal: this header ties together many translation units and will expose prototype/type drift. Runtime signals include stable endpoint `hcpriv` lifecycle, correct URB `hcpriv` cleanup, no frame rollover scheduling regressions in periodic traffic, correct TT refcount allocation/free for hubs, and absence of use-after-free or double-cleanup when channel/QH/QTD ownership changes during dequeue, disconnect, or descriptor-DMA completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/hcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/hcd_ddma.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/hcd_ddma.c

## Purpose

`hcd_ddma.c` implements host-mode descriptor DMA support for the DWC2 controller. It allocates and frees QH descriptor lists, manages the periodic frame list, initializes descriptor rings for control/bulk/interrupt/isochronous transfers, starts descriptor-DMA channels, scans completed descriptors from interrupt context, updates DWC2 URB/QTD state, gives completed URBs back to the USB core, and releases or requeues host channels.

## Important APIs, types, and functions

- Descriptor and frame index helpers:
  - `dwc2_frame_list_idx()` maps frame numbers to the 64-entry periodic frame list.
  - `dwc2_desclist_idx_inc()` / `dwc2_desclist_idx_dec()` wrap descriptor indexes using high-speed isochronous or generic descriptor-list sizes.
  - `dwc2_max_desc_num()` chooses descriptor-list capacity based on endpoint type and speed.
  - `dwc2_frame_incr_val()` converts QH interval to frame-list increment.
  - `dwc2_frame_to_desc_idx()` maps frame-list index to descriptor index, using 8-descriptor alignment for high-speed isochronous endpoints.
- Allocation and lifecycle:
  - `dwc2_desc_list_alloc()` allocates a DMA descriptor list from the generic or high-speed isochronous kmem cache, maps it for DMA, and allocates the `n_bytes` side array.
  - `dwc2_desc_list_free()` unmaps/frees descriptor memory and `n_bytes`.
  - `dwc2_frame_list_alloc()` / `dwc2_frame_list_free()` allocate/map/free the host periodic frame list.
  - `dwc2_per_sched_enable()` / `dwc2_per_sched_disable()` program `HFLBADDR` and `HCFG_PERSCHEDENA`.
  - `dwc2_hcd_qh_init_ddma()` initializes DDMA fields for a QH and enables periodic scheduling on the first periodic QH.
  - `dwc2_hcd_qh_free_ddma()` frees DDMA QH resources, releases still-assigned channels, and tears down the frame list when appropriate.
- Periodic frame list:
  - `dwc2_update_frame_list()` enables/disables channel bits in the 64-entry frame list based on QH interval, syncs it to the device, and computes channel `schinfo`.
  - `dwc2_calc_starting_frame()` and `dwc2_recalc_initial_desc_idx()` choose a safe initial isochronous descriptor index by skipping current/near-current frames to avoid hardware racing newly activated descriptors.
- Descriptor initialization:
  - `dwc2_fill_host_isoc_dma_desc()` fills one isochronous descriptor, records original byte count, marks it active, advances QTD isochronous progress, and sets IOC at URB boundaries.
  - `dwc2_init_isoc_dma_desc()` activates a bounded set of isochronous descriptors from queued QTDs, handles descriptor-list fullness, and sets IOC on the last activated descriptor.
  - `dwc2_fill_host_dma_desc()` fills one non-isoc descriptor for control/bulk/interrupt traffic, splits large transfers at hardware limits, rounds IN transfers to packet boundaries, handles SETUP descriptors, and advances channel DMA/length state.
  - `dwc2_init_non_isoc_dma_desc()` builds a descriptor chain across one or more QTDs, marks active descriptors in hardware-safe order, and sets IOC/EOL/A on the final descriptor.
- Start/completion:
  - `dwc2_hcd_start_xfer_ddma()` chooses initialization logic by endpoint type, updates the frame list for periodic endpoints, and starts the channel through `dwc2_hc_start_transfer_ddma()`.
  - `dwc2_cmpl_host_isoc_dma_desc()` syncs one isochronous descriptor from device, computes actual length/status, completes URBs when all packets are done, and decrements QH descriptor count.
  - `dwc2_complete_isoc_xfer_ddma()` scans active isochronous descriptors and handles normal IOC, session continuation, dequeue, AHB error, and babble error.
  - `dwc2_update_non_isoc_urb_state_ddma()` interprets descriptor status and halt reason for control/bulk/interrupt URBs.
  - `dwc2_process_non_isoc_desc()` syncs one non-isoc descriptor, updates QTD/URB state, advances control phases, saves toggles, and completes failed or finished URBs.
  - `dwc2_complete_non_isoc_xfer_ddma()` scans descriptor chains for non-isoc endpoints, updates QH data toggle and ping state, and leaves unfinished QTDs queued.
  - `dwc2_hcd_complete_xfer_ddma()` is the external completion entry point used by interrupt handling. It dispatches isoc vs non-isoc completion, releases channels/frame-list entries, requeues QHs with remaining work, selects new transactions, and queues them.

## Control flow

Descriptor-DMA setup begins when a QH is created and `dwc2_hcd_qh_init_ddma()` is called. Split transfers are rejected because DDMA does not support them here. The QH receives a descriptor list and `n_bytes` side array. Periodic QHs also ensure a frame list exists and periodic scheduling is enabled in `HCFG`.

When `hcd.c` selects a QH and assigns a host channel, `dwc2_hcd_start_xfer_ddma()` initializes descriptors. Non-isoc endpoints get a linear descriptor chain, then `dwc2_hc_start_transfer_ddma()` programs `HCTSIZ`, `HCDMA`, and enables the channel. Interrupt endpoints additionally mark frame-list entries. Isochronous endpoints calculate an initial descriptor index only at the start of a session, fill descriptors at interval-spaced indexes, enable frame-list bits, set `chan->ntd` to the maximum descriptor count, and start the channel only once for the session.

Completion enters `dwc2_hcd_complete_xfer_ddma()` from channel interrupt handling with a halt status. Isochronous traffic is special: normal transfer-complete scans descriptors and may continue the session without releasing the channel if queued QTDs remain; serious errors or session end complete remaining QTDs, halt/release the channel, and unlink the QH. Non-isoc completion scans descriptor chains, completes or advances URBs/QTDs, releases the channel, unlinks the QH, and re-adds it if QTDs remain.

After completion/release, the file immediately calls the normal scheduler (`dwc2_hcd_select_transactions()` and `dwc2_hcd_queue_transactions()`) to fill newly available channels. Isochronous continuation can force periodic queueing even when no new QH was selected.

## State and persistence behavior

The QH owns persistent DDMA state: `desc_list`, `desc_list_dma`, `desc_list_sz`, `n_bytes`, `ntd`, `td_first`, `td_last`, and per-QTD isochronous descriptor indexes. `n_bytes` persists the original programmed byte count for each descriptor because hardware overwrites descriptor status with remaining bytes. The host controller state owns the global periodic frame list (`frame_list`, `frame_list_dma`, `frame_list_sz`) and frame-number cache.

DMA synchronization is explicit. Descriptor and frame-list writes are synced for device before hardware consumption; completion paths sync individual descriptors for CPU before reading status. Descriptor lists are mapped with `dma_map_single()` and unmapped during QH free. Frame-list access is protected by `hsotg->lock` during enable/disable/free and synced when modified.

Channel release updates scheduler channel accounting, clears frame-list bits for periodic QHs, cleans hardware channel state, moves channels back to `free_hc_list`, clears `chan->qh`, clears `qh->channel`, resets `qh->ntd`, and zeros the descriptor list if present.

## Dependencies and integration points

`hcd_ddma.c` depends on:

- `hcd.h` for QH/QTD/channel structures, frame helpers, channel cleanup/halt/start, QH queue helpers, URB completion, data-toggle save, and transaction scheduling.
- DWC2 register and descriptor definitions from `core.h`, especially descriptor status bits such as `HOST_DMA_A`, `HOST_DMA_IOC`, `HOST_DMA_EOL`, `HOST_DMA_STS_PKTERR`, byte-count masks, and `HCFG`/`HFLBADDR`.
- Linux DMA APIs for map/unmap/sync, kmem caches for descriptor-list allocation, and USB endpoint/speed constants.

Its main integration point with `hcd.c` is descriptor-DMA transfer start from `dwc2_queue_transaction()` and hardware channel programming through `dwc2_hc_start_transfer_ddma()`. Its main integration point with interrupt handling is `dwc2_hcd_complete_xfer_ddma()`.

## Risks and edge cases

- The allocation path maps descriptor lists as `DMA_TO_DEVICE` but error/free paths unmap with `DMA_FROM_DEVICE` in this source; that direction mismatch is worth auditing against the DMA API expectations for this platform.
- Isochronous descriptor indexing is complex and race-prone. The code skips frames to prevent hardware fetching newly programmed descriptors out of order, and comments acknowledge alternative channel-retention behavior and frame rollover TODOs.
- `dwc2_cmpl_host_isoc_dma_desc()` computes `frame_desc_idx` by masking with `usb_urb->number_of_packets - 1`, which assumes power-of-two packet counts for correct modulo behavior; this deserves scrutiny if arbitrary isochronous packet counts reach this path.
- DDMA rejects split transfers outright. Any configuration enabling descriptor DMA while needing split traffic must fall back or fail cleanly.
- Completion can call into URB giveback callbacks that dequeue more URBs. Several checks guard against continuing after `DWC2_HC_XFER_URB_DEQUEUE`, but this remains a high-risk lifecycle area.
- Descriptor active-bit ordering matters. The code delays setting `HOST_DMA_A` on previous descriptors until later descriptors are populated to avoid hardware seeing partially built chains.
- Serious isochronous errors complete all queued URBs with failure status, even if some descriptors may have succeeded; this is conservative but can affect class drivers expecting per-packet partial success.

## Test signals

Strong runtime signals include descriptor-DMA control transfers completing setup/data/status phases, bulk IN/OUT transfers larger than one descriptor, interrupt endpoint scheduling through the frame list, high-speed and full-speed isochronous streams with correct per-packet status and `start_frame`, URB dequeue from completion callbacks, AHB/babble/stall/xact error handling, NYET-to-ping-state propagation, and channel reuse after DDMA release.

Instrumentation should watch descriptor `A/IOC/EOL` bits, `qh->ntd`, `td_first/td_last`, frame-list bits, DMA sync warnings, `chan->qh` ownership, `free_hc_list` membership, and absence of leaks in descriptor caches/frame-list allocation after endpoint disable and HCD remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/hcd_ddma.c -->
