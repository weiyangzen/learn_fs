# sources/distributed-fs/ceph-client/drivers/pps/clients/pps-ktimer.c

Purpose: debug PPS client that synthesizes one assert event per second from a kernel timer.

Important APIs/functions: global `pps`, `ktimer`, `pps_ktimer_event()`, `pps_ktimer_init()`, `pps_ktimer_exit()`, and static `pps_source_info`.

Control flow: module init registers a PPS source with assert capture, offset, echo, wait, and timespec capabilities, initializes a timer, and schedules it for `jiffies + HZ`. Each timer callback timestamps with `pps_get_ts()`, emits `PPS_CAPTUREASSERT`, and reschedules itself one second later. Exit deletes the timer synchronously and unregisters the source.

State/dependencies: global singleton state, PPS core, timer wheel, jiffies, module ownership. No persistent configuration.

Risks: intended only for debugging; timer jitter makes it unsuitable as a precision reference; global state supports one source only; callback assumes registration succeeded and `pps` remains valid until timer deletion.

Test signals: load/unload module, observe `/dev/ppsN`, `assert` sysfs sequence increments approximately once per second, blocking `PPS_FETCH`, and clean unload while userspace has the device open.
