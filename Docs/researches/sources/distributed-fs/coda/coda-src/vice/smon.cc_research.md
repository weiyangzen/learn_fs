# sources/distributed-fs/coda/coda-src/vice/smon.cc

## Purpose
`smon.cc` implements the server monitor daemon that periodically reports vice server call statistics, resolution statistics, overflow events, and optional raw machine statistics to a Mond monitoring service.

## Important APIs, types, and functions
- `SmonInit` initializes this server's monitor identity (`SmonViceId`), overflow entry, RVM resolution queue, and init flag.
- `rvmrese` captures a snapshot of per-volume resolution stats and reports it with `SmonReportRVMResStats`.
- `smon_entry` stores an overflow event window and count.
- `CheckCallStat` reports RPC/callback/resolution/voldump call counts and raw statistics every `callReportInterval`.
- `CheckRVMResStat` drains queued resolution-stat events, or periodically snapshots `ResStatsList` into the queue.
- `CheckSOE` reports pending overflow state.
- `ValidateSmonHandle` rate-limits binding attempts, creates an RPC2 binding to `SmonHost:SmonPort`, and establishes a Mond connection.
- `CheckSmonResult` unbinds and resets the handle on report failure.
- `GetRawStatistics` returns platform-dependent kernel stats on old Mach paths and is effectively a no-op on other platforms.
- `SmonDaemon` is the LWP entry point that initializes and then runs the hourly reporting timer.

## Control flow
The server starts `SmonDaemon` as an LWP from `srv.cc`. The daemon sleeps using `IOMGR_Select`, and on timer expiry invokes call-stat, RVM-resolution-stat, and overflow checks. Each check first verifies initialization/enabled state and a valid Mond handle. Binding is retried no more often than `SmonBindInterval`; report failures drop the handle so future cycles can rebind.

## State and persistence behavior
Monitor state is in memory: `SmonHandle`, identity, pending overflow event, pending `RVMResList`, last bind attempt, and last report times. It reports live server counters and resolution stats but does not persist anything locally. Queued RVM resolution entries survive only until process exit.

## Dependencies and integration points
The file depends on RPC2, Mond client stubs, callback and resolution counter arrays, `ResStatsList`, LWP/IOMGR timing, host identity, and server globals `SmonHost`/`SmonPort` configured in `srv.cc`. It is optional telemetry: failed monitor reporting should not stop file serving.

## Risks
`SmonEnabled` defaults to 0 in this file and must be enabled elsewhere for reports to send. `CheckRVMResStat` uses `malloc` for C++-typed `rvmrese` objects containing `olink`, which is only safe if the type remains POD-like enough. The queued stats list is unbounded by explicit size, though comments assume one set at a time. The raw statistics path is obsolete and platform-specific. Reporting failures can cause repeated rebind churn every bind interval.

## Test signals
Use a fake Mond endpoint to validate bind, establish, report, failure, and rebind paths. Exercise call-stat intervals, resolution-stat queue drain, pending overflow reporting, disabled mode, and monitor host/port configuration from `srv.cc`. Logs from `ValidateSmonHandle`, `CheckRVMResStat`, and `CheckSmonResult` are useful diagnostics.
