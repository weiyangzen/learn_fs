# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/DataNodeDiskMetrics.java

## Purpose

`DataNodeDiskMetrics` periodically detects slow DataNode disks by applying `OutlierDetector` to per-volume metadata, read, and write latency means. It records slow-disk latency by operation and optionally derives a bounded list of slow disks to exclude.

## Important APIs, Control Flow, and State

The constructor reads detection thresholds from configuration, creates `OutlierDetector`, marks the service running, and starts a daemon. The daemon loops while `shouldRun`, obtains `FsVolumeReferences` from the DataNode dataset, collects each volume's `DataNodeVolumeMetrics` means keyed by base URI path, closes references, calls `detectAndUpdateDiskOutliers`, sorts outlier disks by maximum recorded latency, and stores up to `maxSlowDisksToExclude`.

State includes volatile detection thresholds, volatile `diskOutliersStats`, mutable `slowDisksToExclude`, and a test-only `overrideStatus` flag that prevents daemon updates after `addSlowDiskForTesting`. Runtime persistence is absent; slow-disk reports are in-memory observations. `shutdownAndWait` flips `shouldRun`, interrupts the daemon, and joins it.

## Dependencies, Integration, Risks, and Tests

Dependencies include `DataNode`, `FsDatasetSpi`, `FsVolumeSpi`, `DataNodeVolumeMetrics`, `SlowDiskReports.DiskOp`, and `OutlierDetector`. It integrates with DataNode slow-disk reporting and volume exclusion logic.

Risks include stale `slowDisksToExclude` when no current outliers exist, daemon interruption still logging an error during normal shutdown, mutable maps exposed by getter, empty stats loops that immediately continue without sleeping, and test override state suppressing real updates. Tests should cover threshold setters, outlier detection per operation, max exclusion ordering, reference closing on exceptions, shutdown, and manual slow-disk injection.
