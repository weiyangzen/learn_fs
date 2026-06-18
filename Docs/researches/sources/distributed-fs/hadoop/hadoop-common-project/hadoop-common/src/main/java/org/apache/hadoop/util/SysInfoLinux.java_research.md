# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SysInfoLinux.java

Purpose: `SysInfoLinux` implements `SysInfo` by parsing Linux procfs and sysfs files: `/proc/meminfo`, `/proc/cpuinfo`, `/proc/stat`, `/proc/net/dev`, `/proc/diskstats`, and `/sys/block/<disk>/queue/hw_sector_size`.

Important APIs/types/functions: constructors allow real paths or test-supplied file paths plus jiffy length. Public metrics implement all `SysInfo` getters. Internal readers include `readProcMemInfoFile`, `readProcCpuInfoFile`, `readProcStatFile`, `readProcNetInfoFile`, `readProcDisksInfoFile`, `readDiskBlockInformation`, `safeParseLong`, `getCurrentTime`, `setReadCpuInfoFile`, and `getJiffyLengthInMillis`. Static `PAGE_SIZE` and `JIFFY_LENGTH_IN_MILLIS` come from `getconf`.

Control flow: memory and CPU topology files are cached after first read unless memory availability explicitly requests a reread. `/proc/stat`, network, and disk counters are reread on each relevant getter. CPU usage is computed by `CpuTimeTracker` from cumulative user/nice/system jiffies and wall time, then divided by logical processor count for percentage or by 100 for vcores used. Disk stats skip loop and ram devices, cache per-disk sector sizes, and multiply sector counts by the sector size.

State and persistence behavior: instance fields cache procfs paths, jiffy length, parsed memory totals/free values, CPU counts/frequency, network and disk counters, read-once flags, `CpuTimeTracker`, and a synchronized `perDiskSectorSize` map. There is no persistence beyond process memory.

Dependencies and integration points: depends on Java NIO file reads, regex patterns, `ShellCommandExecutor` for `getconf`, `CpuTimeTracker`, and SLF4J. It integrates with system metrics and resource monitoring in Linux deployments.

Risks: parser regexes reflect specific Linux procfs formats and may miss device names or newer fields. `safeParseLong` converts invalid/overflowing memory values to zero, which avoids crashes but may under-report. CPU frequency stores the last `cpu MHz` line seen. `getCpuUsagePercentage` divides by `getNumProcessors`; malformed CPU info producing zero processors could be problematic. Disk device filtering and the diskstats regex exclude partitions and may not cover NVMe/mapper naming consistently. File closing is manual rather than try-with-resources.

Test signals: tests should supply fake procfs files for memory variants including `Inactive(file)`, hardware-corrupted and huge pages, malformed swap values, CPU topology, jiffy-based CPU deltas, network loopback exclusion, disk sector fallback, and missing file behavior.
