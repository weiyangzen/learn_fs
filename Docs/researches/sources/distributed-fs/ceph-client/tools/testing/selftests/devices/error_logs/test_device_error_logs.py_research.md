# sources/distributed-fs/ceph-client/tools/testing/selftests/devices/error_logs/test_device_error_logs.py

## Purpose

`test_device_error_logs.py` scans `/dev/kmsg` for kernel error-or-worse messages tagged with `DEVICE=` and reports one failed KTAP test per affected device.

## Important APIs, Types, and Functions

It imports `ksft`, parses kmsg lines with `RE_log`, parses continuation tags with `RE_tag`, defines `PREFIX_ERROR = 3`, and implements `parse_kmsg()` and `generate_per_device_error_log()`.

## Control Flow

The script opens `/dev/kmsg`, switches it nonblocking, iterates available log lines, accumulates structured log dictionaries, groups logs whose priority prefix is <= 3 by `DEVICE`, then emits a KTAP plan equal to the number of devices with errors. Each such device produces a failed test and prints the messages; zero devices prints an informational message and a zero-test plan.

## State and Persistence Behavior

It reads kernel log state but does not clear or mutate it. Parsed logs are held in memory.

## Dependencies and Integration Points

It depends on `/dev/kmsg` readability, kernel device log tags, Python regex parsing, and `ksft` from the kselftest tree.

## Risks and Edge Cases

Existing historical kmsg errors can fail the test even if unrelated to the current run. Nonblocking iteration may miss logs written after the initial read. The last `current_log` is appended only when a new log line arrives, so the final log can be dropped.

## Test Signals

No device error logs is success with zero tests. Any device with error/critical logs is a failure named by device id and accompanied by messages.
