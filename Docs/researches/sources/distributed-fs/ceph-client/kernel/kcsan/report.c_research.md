# sources/distributed-fs/ceph-client/kernel/kcsan/report.c

## Purpose
Builds and prints KCSAN race reports. It coordinates the thread that consumes a watchpoint with the thread that originally installed it, filters and rate-limits reports, formats stack traces/access descriptions, and handles unknown-origin races.

## Important APIs, Types, and Functions
Uses `struct access_info`, `struct other_info`, `struct report_time`, global `other_infos`, `report_times`, and `report_lock`. Main helpers are `rate_limit_report`, `skip_report`, `get_access_type`, `sanitize_stack_entries`, `print_report`, `prepare_report_producer`, `prepare_report_consumer`, and exported `kcsan_report_set_info`, `kcsan_report_known_origin`, `kcsan_report_unknown_origin`.

## Control Flow
The racing access that consumes a watchpoint calls `kcsan_report_set_info`, fills the per-watchpoint `other_info`, and optionally stalls for verbose task data. The original watchpoint owner calls `kcsan_report_known_origin`, waits for that info, verifies encoded and real address overlap, filters by value-change/config/debugfs/rate limit, prints the report, and releases the slot. Unknown-origin reporting bypasses `other_info` and prints a single-sided report.

## State and Persistence
Per-watchpoint `other_infos` are reused and marked valid by nonzero size. `report_times` stores recent report frame pairs for boot-time rate limiting. No reports are persisted beyond the kernel log.

## Dependencies and Integration Points
Depends on stacktrace, kallsyms for frame/function lookup, debugfs filters, lockdep/IRQ trace helpers, printk, panic-on-warn, and watchpoint matching from `encoding.h`.

## Risks
Report generation runs in sensitive contexts, so it disables KCSAN and lockdep around printk paths. Producer/consumer waiting must avoid deadlocks while still keeping task data valid. Formatting is consumed by tests and users, so wording changes can break expectations.

## Test Signals
KUnit captures console output and matches report title plus access lines. Counters in debugfs track data races, assert failures, report races, unknown-origin races, and encoding false positives.
