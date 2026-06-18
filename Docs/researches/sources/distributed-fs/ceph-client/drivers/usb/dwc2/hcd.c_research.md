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
