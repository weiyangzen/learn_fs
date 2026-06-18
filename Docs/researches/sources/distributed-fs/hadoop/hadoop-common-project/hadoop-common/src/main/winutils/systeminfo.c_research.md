# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/systeminfo.c

Purpose: implements `winutils systeminfo`, producing a comma-separated resource snapshot for memory, CPU, disk, and network counters.

Important APIs/functions: `SystemInfo` gathers `GetPerformanceInfo`, `GetSystemInfo`, `GetSystemTimes`, `CallNtPowerInformation`, and aggregate PDH counters; `GetDiskAndNetwork` opens a PDH query and reads wildcard network/disk counters; `ReadTotalCounter` sums raw counter array values unless `_Total` is present; `SystemInfoUsage` documents output order.

Control flow: memory and CPU totals are collected first; processor power information supplies max MHz; disk/network counters are added, collected, and read; stdout receives one CSV row of sizes, counts, CPU time, and IO totals. Any failure reports to stderr and exits failure.

State and persistence: read-only system inspection, with temporary PDH query handles and allocated buffers.

Dependencies/integration: uses PSAPI, PowrProf, PDH, `winutils.h`, and Windows performance counter names. Called from `main.c` and likely consumed by process/resource monitors.

Risks and test signals: localized or missing PDH counter names, unavailable power APIs, counter wildcard behavior, and `_Total` handling can vary by Windows version. Tests should verify CSV field count/types, graceful PDH failure, and non-negative resource values on supported Windows hosts.
