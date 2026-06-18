# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsVolumeList.java

`FsVolumeList` maintains the active `FsVolumeImpl` set. It chooses volumes for new blocks, aggregates usage/capacity, coordinates block-pool scans, tracks failed and removing volumes, integrates `BlockScanner`, and maintains same-disk tiering mount metadata.

State includes a `CopyOnWriteArrayList` of active volumes, synchronized failed-volume `TreeMap`, `ConcurrentLinkedQueue` of removed volumes waiting for references to drain, a check-dirs lock/condition, a `VolumeChoosingPolicy`, optional disk metrics, `MountVolumeMap`, and capacity ratio configuration.

Volume selection filters by storage type, excludes slow disks from `DataNodeDiskMetrics`, invokes the configured chooser, and obtains a reference. If the selected volume is closed, it is removed from the candidate list and selection retries. Same-disk tiering can directly select a volume by mount and storage type if enabled and sufficiently available.

Adding a volume appends it, updates mount maps and configured capacity ratios, registers the block scanner or releases the reference when no scanner exists, clears failure info, and logs. Removing a volume removes active/scanner/tiering state, closes and shuts down the volume, and queues it until refcounts reach zero. `handleVolumeFailures` records failure info, removes volumes, and waits for reference release. Block-pool map loading and block-pool addition run one thread per volume and aggregate exceptions into `AddBlockPoolException`.

The class stores runtime state rather than durable files, but it delegates volume scanning, block-pool shutdown, and deletion work. Dependencies are `FsDatasetImpl`, `FsVolumeImpl`, `BlockScanner`, `VolumeChoosingPolicy`, `StorageLocation`, `MountVolumeMap`, `DataNodeDiskMetrics`, and DataNode block report types.

Risks include leaked references delaying removal, chooser behavior with empty candidates, URI mismatches in capacity ratio config, partial parallel scan failures, and same-disk tiering duplicate storage-type constraints. Tests should cover slow-disk exclusion, closed-volume retry, transient volume choice, same-mount lookup, add/remove scanner integration, failure info lifecycle, capacity ratio application, and multi-volume exception aggregation.
