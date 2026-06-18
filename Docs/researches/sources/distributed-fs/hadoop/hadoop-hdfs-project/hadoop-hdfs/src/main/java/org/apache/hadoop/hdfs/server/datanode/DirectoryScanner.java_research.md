# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DirectoryScanner.java

Purpose: `DirectoryScanner` periodically reconciles finalized block files on DataNode volumes with the in-memory dataset block map. It detects missing block files, missing metadata files, blocks present on disk but absent in memory, mismatched generation/length, and duplicate block records.

Important APIs and types: lifecycle methods are `start`, `run`, `shutdown`, `reconcile`, `scan`, and `getVolumeReports`. `Stats` stores per-block-pool counters. `ScanInfoVolumeReport` groups scan results per volume and block pool. `BlockPoolReport` is a multimap of block pool IDs to sorted `ScanInfo` rows. Inner `ReportCompiler` asks a volume to `compileReport` while applying throttling.

Control flow: `start` schedules `run` at a randomized initial delay and fixed scan interval. `run` calls `reconcile` and records dataset finish time. `reconcile` calls `scan`, waits on a fault-injection hook, then iterates `diffs` and invokes `dataset.checkAndUpdate` in batches with sleeps to reduce long lock holds. `scan` compiles reports in parallel, skips PROVIDED volumes, sorts disk and memory records, then merges by block ID to classify differences.

State and persistence: persistent state lives in the dataset, not this scanner. The scanner keeps transient `diffs`, `stats`, timing counters, executor services, scan intervals, throttle settings, and `shouldRun`. If `retainDiffs` is false, differences are cleared after reconciliation or shutdown. Dataset updates may add, delete, or correct block records based on on-disk files.

Dependencies and integration points: it integrates with `FsDatasetSpi`, `FsVolumeSpi`, `FsVolumeSpi.ScanInfo`, `DataNodeFaultInjector`, `FileUtil`, Guava `ListMultimap`, and DFS config keys for scan interval, thread count, throttle, and reconciliation batch behavior. Volume implementations provide traversal through `compileReport`.

Risks: the merge logic is sensitive to sorted order and duplicate block IDs. Scans intentionally skip PROVIDED storage. Interrupts in `ReportCompiler` return `null` and cause the whole volume report list to be cleared. Batch sleeps happen while synchronized on `diffs`, which avoids concurrent mutation but can extend lock ownership.

Test signals: test missing block/meta/memory/mismatch/duplicate classification, deletion-in-progress suppression, PROVIDED-volume exclusion, report compiler interruption, throttle timing counters, invalid config fallbacks, batch reconciliation sleep behavior, shutdown clearing when `retainDiffs` is false, and dataset `checkAndUpdate` calls in diff order.
