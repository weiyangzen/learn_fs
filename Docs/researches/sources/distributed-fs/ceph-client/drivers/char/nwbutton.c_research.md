# sources/distributed-fs/ceph-client/drivers/char/nwbutton.c

## Purpose
`nwbutton.c` implements the NetWinder front-panel button driver. It registers `/dev/nwbutton` as a misc device, counts button presses delivered by a board IRQ, groups presses into sequences using a timer, exposes the count to blocking readers, can invoke kernel callbacks for specific press counts, and optionally asks init to reboot on a configured count.

## Important APIs, Types, and Functions
- `button_add_callback()` and `button_del_callback()` allow other kernel code to register callbacks keyed by press count.
- `button_handler()` is the IRQ handler. It increments `button_press_count` and arms/modifies `button_timer`.
- `button_sequence_finished()` runs after `BUTTON_DELAY` jiffies without another press. It checks reboot behavior, consumes matching callbacks, formats the count into `button_output_buffer`, resets the count, and wakes readers.
- `button_read()` sleeps on `button_wait_queue` and copies the last formatted count to userspace.
- `nwbutton_init()` checks `machine_is_netwinder()`, registers the misc device with fixed `BUTTON_MINOR`, and requests `IRQ_NETWINDER_BUTTON`.

## Control Flow
On a NetWinder machine, init registers the misc node and IRQ. Every interrupt increments the global count and moves the sequence deadline. When the timer expires, the sequence is finalized and readers waiting in `button_read()` are woken. Module exit frees the IRQ and deregisters the misc device.

## State and Persistence
State is global and volatile: `button_press_count`, `button_timer`, a 32-byte output buffer, `bcount`, configurable delay and reboot count variables, and a static callback array of 32 entries. No state persists across reboot or module unload.

## Dependencies and Integration Points
The driver depends on ARM NetWinder machine detection, `IRQ_NETWINDER_BUTTON`, misc core, timers, wait queues, and optional CAD reboot signaling through `kill_cad_pid(SIGINT, 1)`. The callback registration functions are declared in `nwbutton.h` for other code.

## Risks
- The source explicitly notes lack of locking. IRQ, timer, callbacks, and readers share global state without synchronization.
- `button_read()` does not recheck a condition after scheduling and does not account for signal interruption, so reads may return stale or uninitialized data in edge cases.
- Callback registration can race with timer callback iteration.
- Multiple readers all consume the same global `button_output_buffer`; there is no per-open state.

## Test Signals
Hardware or emulated IRQ tests should verify press grouping by timer, blocking read wakeups, reboot-count behavior when configured, callback add/delete ordering and capacity errors, and cleanup of IRQ/device registration. Static analysis should flag the intentional locking gaps around callback and sequence state.
