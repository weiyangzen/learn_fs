<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/VolumeScanner.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/VolumeScanner.java

## Purpose

`VolumeScanner` scans one DataNode volume in its own daemon thread, verifying block data through `BlockSender` and reporting bad blocks. It is managed by `BlockScanner` and balances periodic full-volume scanning with prioritized suspect-block rescans.

## Important APIs, Types, And Functions

- `Statistics` snapshots bytes scanned, block counts, error counts, next scan timing, last block, and EOF state.
- `ScanResultHandler` handles successful scans, missing blocks, write races, and bad-block reports.
- `runLoop(ExtendedBlock)` performs rate limiting, block-pool iterator selection, block selection, scan execution, cursor saving, and stats updates.
- `scanBlock` resolves the current stored block, sends bytes to a null output stream with a throttler, and updates metrics.
- `enableBlockPoolId`, `disableBlockPoolId`, `markSuspectBlock`, `shutdown`, and `printStats` are the external control surface.

## Control Flow

The thread initializes minute counters and result handler, then loops until stopped. Each iteration waits for a timeout if needed, pops a suspect block if queued, and otherwise picks a usable block iterator. It throttles based on bytes scanned over the past hour, skips recently accessed blocks when configured, periodically saves iterator cursors, scans via `BlockSender`, and updates stats in a `finally` block.

## State And Persistence

Runtime state includes the held `FsVolumeReference`, volume, per-block-pool iterators, current iterator, suspect-block queue, recent-suspect cache, rolling scanned-byte ring buffer, throttler, null stream, stop flag, and stats. Persistent scanner state is the block iterator cursor saved through `BlockIterator.save()` and reloaded by `volume.loadBlockIterator`.

## Dependencies And Integration Points

It integrates `BlockScanner.Conf`, `DataNode`, `DataNodeMetrics`, `FsVolumeSpi`, `BlockIterator`, `BlockSender`, `DataTransferThrottler`, block local path metadata, and test callbacks through `VolumeScannerCBInjector`.

## Risks And Edge Cases

Block files can disappear or move during writes; `FileNotFoundException` is treated as a likely race. Rate calculation uses monotonic minutes while iterator rescan periods use wall-clock time because cursor files persist across reboot. Suspect blocks are deduplicated for ten minutes to avoid repeated rescans. Cursor cleanup and volume-reference release must happen even on thread failure.

## Test Signals

Tests should cover rate throttling math, iterator rotation and rescan delay, cursor save/load, suspect-block priority and deduplication, skip-recent-access behavior, handling missing/corrupt blocks, bad-block reporting, stats snapshots, shutdown callbacks, and volume-reference cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/VolumeScanner.java -->
