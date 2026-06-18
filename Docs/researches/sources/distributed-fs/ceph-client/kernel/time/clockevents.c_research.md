# sources/distributed-fs/ceph-client/kernel/time/clockevents.c

Purpose: manages registered `struct clock_event_device` instances, their state transitions, frequency configuration, event programming, release/replacement, suspend/resume, CPU hotplug cleanup, and optional sysfs control.

Important APIs and flow: `clockevents_register_device()` initializes a device as detached, fixes missing CPU masks, adds it to `clockevent_devices`, and asks tick code to select it. `clockevents_switch_state()` funnels state changes through device callbacks and enforces feature support for periodic, oneshot, and stopped states. `clockevents_program_event()` converts absolute monotonic expiry to device cycles, handles hrtimer-backed devices, coupled clocksource devices, minimum-delta fallback, forced events, and past expiries. `clockevents_config_and_register()` and `clockevents_update_freq()` compute mult/shift and min/max nanosecond bounds. Unbind paths coordinate `clockevents_mutex`, `clockevents_lock`, and CPU-local replacement via `smp_call_function_single()`.

State and persistence: global lists track active and released devices; per-device state, `next_event`, min/max delta, retries, owner module references, and forced-event state persist until exchange/unbind/hotplug removal. Sysfs exposes current and unbind controls for per-CPU and broadcast devices.

Dependencies and integration: tightly coupled to `tick-internal.h`, tick broadcast, CPU hotplug, clockchips, hrtimer broadcast devices, sysfs, module ownership, SMP callbacks, and optional generic min-delta adjustment/coupled-clockevent configs.

Risks and test signals: event programming is sensitive to overflow in latch-to-ns math, zero `mult`, devices with too-small min deltas, remote unbind races, and broadcast-device replacement. Test with periodic/oneshot devices, failing `set_next_event`, frequency changes while active, CPU offline paths, sysfs unbind failures, and coupled clocksource conversion.
