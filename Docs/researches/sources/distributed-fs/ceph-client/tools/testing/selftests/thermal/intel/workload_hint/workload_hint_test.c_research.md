# sources/distributed-fs/ceph-client/tools/testing/selftests/thermal/intel/workload_hint/workload_hint_test.c

## Purpose
Interactive/polling selftest for Intel workload type hints and slow workload hints exposed through sysfs on PCI device `0000:00:04.0`.

## Important APIs, Types, and Functions
Constants name sysfs attributes for `notification_delay_ms`, `workload_hint_enable`, `workload_slow_hint_enable`, and `workload_type_index`. `workload_types` maps indices to `idle`, `battery_life`, `sustained`, and `bursty`. Globals `wlt_slow` and `wlt_enable_attr` select normal or slow hint mode. Functions are `workload_hint_exit()`, `update_delay()`, and `main()`.

## Control Flow
`main()` prints usage, parses optional delay values and `slow`, writes notification delay if provided, installs signal handlers, selects the enable attribute, writes `1\n`, then loops opening and polling `workload_type_index`. On each `POLLPRI`, it rereads the index, converts it to a workload type string, and prints it. The signal handler writes `0\n` to the selected enable attribute.

## State and Persistence Behavior
The test changes sysfs enable and notification-delay state on the platform device. It runs indefinitely until interrupted and relies on handled signals to disable hints. No output files are persisted.

## Dependencies and Integration Points
Depends on Intel thermal workload-hint sysfs attributes, pollable status notifications, permissions to write sysfs, and the fixed PCI BDF.

## Risks and Edge Cases
The argument loop parses `argv[1]` for every non-`slow` argument instead of `argv[i]`, so multiple non-slow args are mishandled. `sscanf` failure check uses `ret < 0` rather than `ret != 1`. Fixed BDF and infinite loop limit automation. Index bounds must be checked before using `workload_types`.

## Test Signals
Signals include successful delay write, enable write for normal or slow mode, poll wakeups, valid workload index-to-name printing, and disable on handled termination.
