# sources/distributed-fs/ceph-client/drivers/pps/kapi.c

Purpose: exported kernel API for PPS source drivers. It registers PPS sources, unregisters them, and records timestamped assert/clear events.

Important APIs/functions: exported `pps_register_source()`, `pps_unregister_source()`, and `pps_event()`. Helpers include `pps_add_offset()` and default echo callback `pps_echo_client_default()`.

Control flow: source registration validates that defaults are supported by capabilities and that a timestamp format is advertised, allocates `pps_device`, initializes API version, params, copied source info, default echo if needed, waitqueue and spinlock, then creates the char device through `pps_register_cdev()`. `pps_event()` requires assert or clear, converts realtime timestamp, takes the device spinlock, optionally calls echo, applies configured offsets, stores assert/clear timestamps and sequence counters, sends kernel-consumer hardpps notification, wakes blocking readers, and signals fasync.

State/dependencies: per-source params, info, timestamps, sequences, waitqueue, fasync queue, and spinlock. Unregister first removes kernel consumer binding and then cdev/device state. Depends on PPS core cdev helpers and optional kernel consumer wrappers in `kc.h`.

Risks: `pps_event()` uses `BUG_ON()` for invalid event masks; echo callback runs under spinlock and must not sleep; source registration error path returns `ERR_PTR(err)` but must ensure `err` is initialized; offsets mutate a single timestamp copy reused for assert and clear when both captured.

Test signals: register invalid/default capability combinations, emit assert/clear/both events, verify sysfs and ioctl sequence updates, echo callbacks, fasync notification, kernel consumer binding, and unregister with open file descriptors.
