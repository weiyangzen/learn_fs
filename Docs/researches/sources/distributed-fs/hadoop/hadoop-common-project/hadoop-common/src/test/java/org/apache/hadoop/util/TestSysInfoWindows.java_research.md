# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestSysInfoWindows.java

Purpose: Tests `SysInfoWindows` parsing and refresh behavior using a mock subclass instead of invoking Windows shell commands. It validates the comma-separated `winutils`/shell system-info contract, cache refresh intervals, and CPU usage normalization for single-core and multi-core systems.

Important APIs/types/functions: `SysInfoWindowsMock` overrides `getSystemInfoInfoFromShell()` and `now()`, stores a mutable `infoStr`, and advances mock time through `advance(long)`. Test methods cover `parseSystemInfoString()`, `refreshAndCpuUsage()`, `refreshAndCpuUsageMulticore()`, and `errorInGetSystemInfo()`.

Control flow: Tests inject a CSV line with virtual memory, physical memory, available memory, processor/core count, CPU frequency, cumulative CPU time, storage bytes, and network bytes. Accessor calls trigger refresh if the mock clock exceeds `SysInfoWindows.REFRESH_INTERVAL_MS`; otherwise cached values are reused. CPU usage is unavailable until two valid samples exist, then computed from cumulative CPU-time deltas over elapsed wall time and normalized by core count for percentages.

State and persistence behavior: `SysInfoWindows` retains the last parsed metrics and last refresh timestamp, while the mock controls both the next shell output and clock. The no-refresh assertions verify that changed shell output does not leak into public values before the refresh interval. Bad/null shell output is intentionally tolerated without assertions on metric changes, indicating defensive parsing should not throw on malformed command output.

Dependencies and integration points: Depends on Hadoop `SysInfoWindows`, `CpuTimeTracker`, JUnit 5, and `@Timeout` to prevent hanging shell-like paths. It protects Hadoop resource reporting on Windows where values originate from native utilities.

Risks: The CSV positional ABI is fragile: adding/removing fields in the native command requires synchronized parser and tests. CPU calculations assume cumulative CPU time units are milliseconds and core count is the denominator for percentage only. The test does not assert exact fallback values after malformed output, so regressions that silently preserve stale metrics may need additional coverage.

Test signals: Exact parsed numeric values, first-sample unavailable CPU usage, unchanged cached memory before refresh, recalculated memory and CPU after advancing mock time, and absence of exceptions for null/empty shell output are the main signals.
