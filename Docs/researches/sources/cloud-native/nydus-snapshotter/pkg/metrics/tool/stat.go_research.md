# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/tool/stat.go

This file reads Linux `/proc` process data for metrics and daemon startup profiling. `Stat` stores CPU times, thread count, start time, RSS, fd count, and system uptime. `ClkTck` and `PageSize` are package globals initialized from `common.go`.

`CalculateCPUUtilization` computes CPU percent between two stat samples. `GetProcessMemoryRSSKiloBytes` derives RSS in KiB. `GetProcessStat` reads `/proc/uptime`, `/proc/<pid>/stat`, splits after the process name's closing parenthesis, reads `/proc/<pid>/fdinfo`, and maps selected fields. `GetProcessRunningState` reads the process state field. `IsZombieProcess` checks for state `"Z"`.

State is read-only from `/proc`. Integration points include metrics server resource collection, daemon startup CPU profiling, and socket-wait retry behavior. Risks include Linux-only paths, parsing assumptions around `/proc/<pid>/stat`, ignored float parse errors, potential division by zero in CPU utilization, fdinfo permission failures, and state tests differing across init systems. Unit coverage only checks PID 1 running state contains `Ss` or `S`.
