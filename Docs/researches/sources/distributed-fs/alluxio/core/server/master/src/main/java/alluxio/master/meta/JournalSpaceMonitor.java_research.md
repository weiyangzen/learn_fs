# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/JournalSpaceMonitor.java

## Purpose
`JournalSpaceMonitor` is a heartbeat executor that monitors free disk space for the embedded journal path on Linux and emits warnings/metrics when capacity is low.

## Important APIs, types, and functions
The configuration constructor reads `MASTER_JOURNAL_FOLDER` and `MASTER_JOURNAL_SPACE_MONITOR_PERCENT_FREE_THRESHOLD`. `getRawDiskInfo()` executes `df -k -P -T`. `getDiskInfo()` parses `df` output into `JournalDiskInfo`, updates an atomic metric-info map, and registers free-bytes and free-percent gauges per disk. `getJournalDiskWarnings()` returns warning strings below threshold. `heartbeat(long)` logs warnings.

## Control flow
Construction validates that the journal path exists. Each disk-info read shells out, skips the header, tokenizes lines, parses size fields, records metric source data, and registers gauges that read the latest `AtomicReference` map. Warning generation filters current disk info by percent available.

## State and persistence behavior
State is in-memory only: journal path, threshold, and latest disk info for metrics. It does not persist state or modify disk contents.

## Dependencies and integration points
It depends on POSIX `df`, `ShellUtils`, `MetricsSystem`, `JournalDiskInfo`, Alluxio URI escaping, and heartbeat framework. `DefaultMetaMaster` starts it only for embedded journals on Linux; REST metrics/overview endpoints read it.

## Risks
The parser assumes `df -P -T` column layout and indexes `data.get(6)` while filtering only `data.size() >= 6`, which looks like an off-by-one guard and should require at least 7 tokens. Shelling out can be slow or unavailable. Gauge names include escaped device URIs and remain registered even if devices change.

## Test signals
Tests should cover constructor path validation, df parse success/failure, multiple filesystems, short/malformed lines, threshold warnings, metric gauge values after refresh, and heartbeat logging.
