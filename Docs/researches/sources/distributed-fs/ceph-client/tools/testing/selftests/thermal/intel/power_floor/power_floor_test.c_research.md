# sources/distributed-fs/ceph-client/tools/testing/selftests/thermal/intel/power_floor/power_floor_test.c

## Purpose
Interactive/polling selftest for Intel power floor notifications exposed through fixed sysfs attributes under PCI device `0000:00:04.0`.

## Important APIs, Types, and Functions
Constants are `POWER_FLOOR_ENABLE_ATTRIBUTE` and `POWER_FLOOR_STATUS_ATTRIBUTE`. Function `power_floor_exit()` disables notifications on SIGINT/SIGHUP/SIGTERM. `main()` enables notifications, opens the status file, waits for `POLLPRI`, rereads status, and prints changes.

## Control Flow
`main()` installs signal handlers, opens the enable attribute and writes `1\n`, then loops forever. Each loop opens the status attribute, reads initial status, polls indefinitely for priority data, seeks back, reads the new status, prints it, and closes the fd. Signal handler writes `0\n` to disable notifications and exits.

## State and Persistence Behavior
The test toggles a persistent sysfs enable knob on the platform device. If killed by an unhandled signal, the feature may remain enabled. It does not write output files.

## Dependencies and Integration Points
Depends on Intel thermal/power-limit sysfs support at `/sys/bus/pci/devices/0000:00:04.0/power_limits/`, pollable sysfs notification semantics, and permissions to write the enable attribute.

## Risks and Edge Cases
The hard-coded PCI BDF is platform-specific. The loop is infinite and intended for manual interruption. Error paths inside the signal handler call `exit(1)` and may leave descriptors open. `status_str` is a three-byte buffer and printed as a string even though reads may not NUL-terminate it.

## Test Signals
Signals include successful enable write, `POLLPRI` wakeups on status changes, printed status values, and disable write on handled termination.
