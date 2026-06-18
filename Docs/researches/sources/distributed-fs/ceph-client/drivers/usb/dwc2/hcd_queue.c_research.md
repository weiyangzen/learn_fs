# sources/distributed-fs/ceph-client/drivers/usb/dwc2/hcd_queue.c

## Purpose
`hcd_queue.c` owns host-side Queue Head and Queue Transfer Descriptor management for DWC2. It builds QHs from URB endpoint metadata, adds/removes QTDs, reserves and releases periodic bandwidth, computes microframe schedules for high-speed and split transactions, and moves QHs among inactive, ready, assigned, queued, waiting, and unreserved states.

## Important APIs, Types, And Functions
- Public QH/QTD APIs: `dwc2_hcd_qh_create()`, `dwc2_hcd_qh_free()`, `dwc2_hcd_qh_add()`, `dwc2_hcd_qh_unlink()`, `dwc2_hcd_qh_deactivate()`, `dwc2_hcd_qtd_init()`, and `dwc2_hcd_qtd_add()`.
- Periodic reservation: `dwc2_schedule_periodic()`, `dwc2_deschedule_periodic()`, `dwc2_do_reserve()`, `dwc2_do_unreserve()`, and `dwc2_unreserve_timer_fn()`.
- Bitmap scheduler: `pmap_schedule()` and `pmap_unschedule()` reserve repeating time slices in high-speed or low/full-speed maps using `gcd(interval, periods_in_map)`.
- Split scheduling: `dwc2_uframe_schedule_split()` coordinates TT-side low/full-speed time and high-speed start/complete split slots.
- High-speed and low-speed wrappers: `dwc2_uframe_schedule_hs()`, `dwc2_uframe_schedule_ls()`, `dwc2_uframe_schedule()`, and `dwc2_uframe_unschedule()`.
- Frame progression: `dwc2_pick_first_frame()`, `dwc2_next_for_periodic_split()`, and `dwc2_next_periodic_start()`.
- Retry timer: `dwc2_wait_timer_fn()` moves NAK-delayed non-periodic QHs back to the inactive schedule.

## Control Flow
URB submission creates or reuses a QH, initializes endpoint attributes in `dwc2_qh_init()`, initializes a QTD with `dwc2_hcd_qtd_init()`, then attaches it with `dwc2_hcd_qtd_add()`. Adding a QTD first ensures the QH is scheduled via `dwc2_hcd_qh_add()`. Non-periodic QHs enter the inactive list immediately unless `want_wait` is set, in which case they enter the waiting list and an hrtimer later requeues them. Periodic QHs call `dwc2_schedule_periodic()`.

Periodic scheduling first validates maximum transfer size, cancels pending delayed unreserve if present, and reserves bandwidth if needed. With `uframe_sched` enabled, `dwc2_uframe_schedule()` chooses high-speed, low/full-speed, or split scheduling. Without it, reservation is a simpler channel-count plus aggregate-usec check. Once reserved, `dwc2_pick_first_frame()` chooses `next_active_frame`, then the QH is linked into ready or inactive periodic lists depending on descriptor DMA and frame timing.

Split scheduling is the most complex path. It schedules the low-speed TT map first, rejects illegal or unsupported placements, derives high-speed start split and complete split microframes, estimates per-microframe durations, then reserves matching high-speed slots. If high-speed placement fails, it rolls back all partial reservations, unschedules the low-speed slot, advances the low-speed search position, and retries.

Deactivation is called from interrupt-side completion. Non-periodic QHs are unlinked and re-added if QTDs remain. Periodic QHs compute the next frame, account for missed frames, and either unlink if empty or move to ready/inactive based on `next_active_frame`.

## State And Persistence Behavior
All state is in memory and protected by `hsotg->lock` where required. The file mutates QH fields including endpoint type/direction, speed, max packet values, split/TT metadata, `host_us`, `device_us`, intervals, schedule map positions, `hs_transfers[]`, active frame numbers, `want_wait`, and `unreserve_pending`. It mutates HCD counters and bitmaps such as `periodic_channels`, `non_periodic_channels`, `periodic_usecs`, `periodic_qh_count`, `hs_periodic_bitmap`, and TT `periodic_bitmaps`. It also starts/cancels kernel timers for delayed unreserve and NAK retry. There is no disk persistence.

## Dependencies And Integration Points
The code integrates with `hcd_intr.c`, which calls `dwc2_hcd_qh_deactivate()` after transfer interrupts, and with transaction-selection code that consumes the schedule lists. It uses USB core helpers such as `usb_calc_bus_time()`, TT metadata from `dwc2_host_get_tt_info()` and `dwc2_host_put_tt_info()`, Linux bitmap APIs, timers/hrtimers, DMA descriptor initialization/free helpers, DWC2 frame-number helpers, and register access for `HPRT0` and `GINTMSK`.

## Risks
- `pmap_schedule()` relies on `gcd()` adjustment to handle intervals not aligned to map size. Bugs here can overcommit periodic bandwidth or reject valid schedules.
- Split scheduling assumptions explicitly skip some partial OUT cases because other DWC2 code cannot handle them. Removing those guards without fixing transfer code can break interrupt and isochronous devices behind hubs.
- Delayed unreserve uses timer and lock races intentionally. Incorrect cancellation or freeing order can lead to use-after-free or leaked bandwidth reservations.
- `dwc2_next_periodic_start()` handles missed frames under tight interrupt-latency assumptions; changes can duplicate periodic transfers in the same frame or starve endpoints.
- `dwc2_hcd_qh_free()` must not be called with the spinlock held because it waits for timers; violating that contract can deadlock.
- Schedule list membership is encoded by `qh_list_entry` emptiness and list position. Incorrect list movement can make transactions disappear or double schedule.

## Test Signals
- Run USB host tests with interrupt and isochronous devices at high, full, and low speed, including devices behind single-TT and multi-TT hubs.
- Stress URB submit/complete loops to verify delayed unreserve preserves bandwidth for quick resubmission and releases it after idle.
- Trigger repeated NAKs and confirm `want_wait` hrtimer requeues QHs without CPU interrupt storms.
- Enable `DWC2_PRINT_SCHEDULE` or schedule debug output to inspect high-speed and low-speed bitmaps after scheduling and unscheduling.
- Test large periodic endpoints near `max_transfer_size` and bus-time limits to confirm `-ENOSPC` behavior is deterministic.
- Exercise endpoint disable/dequeue while timers are pending to catch list and timer lifetime regressions.
