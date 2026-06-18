# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-timer.c

## Purpose
Shared EHCI hrtimer event engine. It serializes deferred controller work: async/periodic schedule state polling, controller-death cleanup, interrupt and async QH unlink completion, delayed iTD/siTD freeing, IAA watchdog recovery, schedule disable delays, and I/O watchdog scans.

## Important APIs, types, and functions
`ehci_set_command_bit()` and `ehci_clear_command_bit()` update cached USBCMD and flush posted writes. `event_delays_ns[]` and `event_handlers[]` must match `enum ehci_hrtimer_event`. `ehci_enable_event()` schedules pending events. Handlers include `ehci_poll_ASS()`, `ehci_poll_PSS()`, `ehci_handle_controller_death()`, `ehci_handle_start_intr_unlinks()`, `ehci_handle_intr_unlinks()`, `start_free_itds()`, `end_free_itds()`, `ehci_iaa_watchdog()`, `turn_on_io_watchdog()`, and `ehci_hrtimer_func()`.

## Control flow
Callers enable an event with optional timeout refresh. The timer tracks the lowest-numbered pending event rather than a sorted queue. On expiration, `ehci_hrtimer_func()` takes `ehci->lock`, snapshots enabled events, clears the set, handles expired events, and re-enables unexpired ones. Poll handlers wait for hardware status bits to match command bits before enabling/disabling schedules. Unlink handlers age QHs through wait lists. The IAA watchdog fabricates progress when hardware loses or delays IAA. Controller death disables configured flag/interrupts and runs cleanup work.

## State and persistence behavior
Timer state is `enabled_hrtimer_events`, `next_hrtimer_event`, `hr_timeouts[]`, poll counters, unlink cycles/lists, `iaa_in_progress`, cached command bits, and delayed descriptor free sentinels. Hardware state includes USBCMD, USBSTS, configured flag, and interrupt enable registers.

## Dependencies and integration points
Depends on EHCI core lock discipline, queue/scheduler unlink functions from `ehci-q.c` and `ehci-sched.c`, hrtimer APIs, and the common `ehci_work()` scan path.

## Risks and edge cases
The enum, delay array, and handler array must stay in identical order. Timer callbacks run under spinlock, so handlers cannot sleep. Event priority is approximate and may delay work up to roughly twice its nominal delay. Lost IAA and controller-death paths are recovery-critical.

## Test signals
Async and periodic schedule enable/disable races, delayed empty-QH unlink, interrupt QH unlink wait, active async unlink, lost IAA injection, controller halt/death, isoch descriptor free delay, I/O watchdog scans, and suspend/remove with pending events are key tests.
