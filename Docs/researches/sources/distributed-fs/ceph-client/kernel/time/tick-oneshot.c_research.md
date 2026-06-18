# sources/distributed-fs/ceph-client/kernel/time/tick-oneshot.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/tick-oneshot.c` manages switching CPU-local tick devices from periodic mode to oneshot mode for high-resolution timers and NO_HZ. It also programs the next oneshot event and resumes stopped oneshot devices. The complete 146-line source was read.

## Important APIs, Types, and Functions

External functions are `tick_program_event`, `tick_resume_oneshot`, `tick_setup_oneshot`, `tick_switch_to_oneshot`, `tick_oneshot_mode_active`, and, under `CONFIG_HIGH_RES_TIMERS`, `tick_init_highres`. The code operates on per-CPU `tick_cpu_device`, `struct clock_event_device`, and event handlers such as `hrtimer_interrupt`.

## Control Flow

`tick_switch_to_oneshot` validates that the current CPU has a functional oneshot-capable clockevent device, sets the per-CPU tick mode to oneshot, installs the requested event handler, switches the device state, and asks broadcast code to switch to oneshot as well. `tick_setup_oneshot` configures a replacement device with a handler and initial event. `tick_program_event` handles `KTIME_MAX` by stopping the device, restarts a stopped oneshot device when a real deadline appears, and delegates programming to clockevents. `tick_resume_oneshot` restarts oneshot mode at `ktime_get()` after resume. `tick_init_highres` switches the handler to `hrtimer_interrupt`.

## State and Persistence Behavior

The file mutates per-CPU tick device mode, event handler, clockevent state, and `next_event`. It owns no independent storage.

## Dependencies and Integration Points

Dependencies include clockevents, per-CPU tick devices, hrtimer interrupt handling, broadcast oneshot transition, and high-resolution timer configuration. It is called by `tick-common.c` during device setup/replacement and by `tick-sched.c` during NO_HZ activation.

## Risks and Edge Cases

Switching fails if no device exists, the device is dummy/nonfunctional, or it lacks oneshot support. Programming `KTIME_MAX` must stop the device cleanly so deep NO_HZ idle can avoid unnecessary interrupts. Resume forces an immediate event to resynchronize timers. Broadcast must be switched along with local devices or CPUs with stopped local timers can miss ticks.

## Test Signals

Signals include high-resolution timer enablement, low-resolution NO_HZ switching, device replacement while in oneshot mode, `KTIME_MAX` stop/restart paths, suspend/resume in oneshot mode, and boot tests on systems lacking oneshot support to verify graceful failure.
