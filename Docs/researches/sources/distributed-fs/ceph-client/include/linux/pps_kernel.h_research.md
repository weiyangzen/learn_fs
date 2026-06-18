# sources/distributed-fs/ceph-client/include/linux/pps_kernel.h

Purpose: declares the kernel PPS source API for timestamping Pulse Per Second assert/clear events and exposing them through character devices.

Important APIs and types: `struct pps_source_info` supplies name, path, allowed modes, echo callback, module owner, and parent device. `struct pps_event_time` stores real and optionally raw timestamps. `struct pps_device` stores source info, current params, assert/clear sequence numbers and timestamps, current mode, last/fetched event IDs, wait queue, source ID, lookup cookie, device, async queue, and spinlock. APIs register/unregister cdevs and sources, emit PPS events, look up devices by cookie, convert timespec to PPS ktime, capture timestamps with `ktime_get_snapshot()`, and subtract known delays.

Control flow: a hardware driver registers a PPS source, captures event timestamps with `pps_get_ts()` at interrupt time, optionally compensates delay with `pps_sub_ts()`, and calls `pps_event()` with assert/clear event data. PPS core updates sequences/timestamps, wakes waiters, emits async notifications, and optionally feeds NTP raw timestamps.

State and persistence: runtime PPS state includes parameters, last assert/clear timestamps, sequences, wait queues, lookup cookie, cdev/device lifetime, and async queue. No persistent state is stored.

Dependencies and integration points: integrates with PPS UAPI, cdev/device core, timekeeping snapshots, optional NTP PPS raw time, wait queues, fasync, and driver echo callbacks.

Risks and test signals: risks include timestamping too late, raw/real timestamp mismatch, sequence races, unregister with consumers, lookup-cookie lifetime, and incorrect delay compensation. Test interrupt timestamp paths, assert/clear modes, poll/read/fasync delivery, NTP PPS integration, unregister/open races, and delay compensation vectors.
