# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SysInfoWindows.java

Purpose: `SysInfoWindows` implements `SysInfo` by invoking `winutils systeminfo` and parsing a comma-separated metrics line.

Important APIs/types/functions: public getters cover all `SysInfo` metrics. Internal methods include `now`, `reset`, `getSystemInfoInfoFromShell`, and synchronized `refreshIfNeeded`. `REFRESH_INTERVAL_MS` throttles shell refreshes to once per second.

Control flow: every getter calls `refreshIfNeeded`. Refresh compares monotonic time to `lastRefreshTime`, snapshots the previous cumulative CPU time, resets all metrics to `-1`, executes `winutils systeminfo`, parses the first CRLF-terminated line into 11 fields, and computes aggregate CPU usage from cumulative CPU delta over refresh interval. CPU percentage divides aggregate usage by processor count; vcores used divides by 100.

State and persistence behavior: instance fields cache the latest shell-reported memory, CPU, storage, and network counters plus the last refresh timestamp. Failures leave metrics at `-1` until the next successful refresh.

Dependencies and integration points: depends on `Shell.getWinUtilsFile`, `ShellCommandExecutor`, `Time.monotonicNow`, and `StringUtils.stringifyException`. It serves Windows deployments through the shared `SysInfo` contract.

Risks: parsing depends on exact comma count and CRLF output from `winutils systeminfo`. The first refresh cannot compute CPU usage because there is no previous cumulative value. If `numProcessors` remains `-1` or zero due to partial parsing, percentage math can be misleading. Shell execution errors are logged and converted into unavailable values.

Test signals: tests should mock command output with correct/incorrect field counts, verify refresh throttling, first-sample CPU unavailability, second-sample CPU computation, and error handling when `winutils` is absent.
