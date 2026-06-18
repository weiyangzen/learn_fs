# sources/distributed-fs/ceph-client/drivers/pps/generators/pps_gen-dummy.c

Purpose: debug PPS generator that never drives real hardware and reports missed-pulse events after a randomized timer delay.

Important APIs/functions: global `pps_gen`, `ktimer`, `get_random_delay()`, `pps_gen_ktimer_event()`, `pps_gen_dummy_get_time()`, `pps_gen_dummy_enable()`, and `pps_gen_dummy_info`.

Control flow: module init registers a generator source and sets up a timer. Enabling arms the timer for 1-16 seconds based on a random low nibble; disabling deletes it. Timer callback reports `PPS_GEN_EVENT_MISSEDPULSE` through `pps_gen_event()`. Time reads return a realtime snapshot.

State/dependencies: singleton generator state, timer wheel, random byte helper, system time snapshot, and PPS generator core. No persistent configuration.

Risks: timer callback is one-shot and not rescheduled, so each enable produces at most one missed event unless userspace toggles enable; no real pulse output; global state supports one instance.

Test signals: load module, see `/dev/pps-genN`, read `system` and `time` sysfs, enable/disable through ioctl or sysfs, wait for missed-pulse event, and unload cleanly with timer pending.
