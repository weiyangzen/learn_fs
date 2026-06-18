# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockScanner.java

## Purpose
`TestBlockScanner` validates DataNode block scanner and volume scanner behavior: block iteration, scan scheduling, scan rate limiting, corrupt block detection, cursor persistence across DataNode restarts, multiple block pools, suspect-block rescans, misplaced block handling, append-while-scan safety, recent-access skipping, shutdown join behavior, and iterator robustness when replicas disappear.

## Important APIs, Types, and Functions
- `BlockScanner`, `VolumeScanner`, `VolumeScanner.Statistics`, and `FsVolumeSpi.BlockIterator` are the primary systems under test.
- `TestContext` starts a one-DataNode MiniDFSCluster, optionally federated, collects filesystem handles, block pool IDs, DataNode, scanner, dataset, and volume references.
- `TestScanResultHandler` is a pluggable `ScanResultHandler` configured through `INTERNAL_VOLUME_SCANNER_SCAN_RESULT_HANDLER`; it records good and bad blocks and can block progress with a semaphore.
- `testVolumeIteratorImpl`, `testScanAllBlocksImpl`, `waitForRescan`, and `testDatanodeShutDown` encapsulate shared flows.
- Configuration keys include scanner bytes/sec, scan period, cursor save interval, join timeout, skip-recent-access, and internal scan period in milliseconds.

## Control Flow and Behavior
Iterator tests create files, iterate blocks, save cursor state, rewind, load a saved iterator, and assert no unknown or duplicate unexpected blocks. Scanner enablement tests validate zero or negative bytes/sec disables scanning. Scan-all tests install the recording handler, create ten blocks, release the scanner, and wait for all blocks or repeated rescans depending on scan period. Rate-limit tests throttle scanning to 4096 bytes/s and assert no more than one 4096-byte block per second.

Corruption and cursor tests manipulate real replicas. Corrupt-block handling corrupts one block on disk and expects it in `badBlocks`. Cursor persistence blocks after five scans, shuts down the DataNode, checks `scanner.cursor` under the block pool directory, restarts, and verifies scanning resumes from the saved point. Multiple block-pool scanning waits for three scans in a federated setup and checks aggregate bytes and block counts.

Suspect-block tests mark a scanned block as suspect, verify it is rescanned quickly, then verify recent suspect rate limiting prevents an immediate duplicate rescan. Misplaced-block handling makes one materialized replica unreachable and confirms it is ignored rather than counted good or bad. Append-while-scanning schedules a suspect rescan and appends to the file while scanner reads, expecting no false corruption. Shutdown tests inject scanner interrupt delay and assert DataNode shutdown honors configured join timeout. `testNextBlock` deletes one replica's data and metadata while iterator ordering crosses subdirectories and verifies iteration skips the missing block.

## State and Persistence
This suite heavily exercises on-disk DataNode state: block files, checksum files, scanner cursor files, volume directories, block-pool directories, and materialized replicas. Scanner statistics track bytes scanned in the past hour, blocks scanned since restart/current period, scan errors, scan count, and EOF state. `TestScanResultHandler.infos` is static cross-handler state keyed by storage ID.

## Dependencies and Integration Points
The tests integrate MiniDFSCluster, federated NameNodes, DFS client file creation and append, `FsDatasetSpi`, `FsVolumeImpl`, block iterators, `MaterializedReplica`, `DataNodeFaultInjector`, `VolumeScannerCBInjector`, scanner configuration, and DataNode shutdown. It is both a scanner unit test and a persistent-storage integration test.

## Risks and Edge Cases
Covered risks include stale iterator caches, cursor save/load correctness, scanning too aggressively, corrupt metadata/data handling, scanner persistence across restarts, multiple block-pool traversal, suspect-block priority and rate limiting, ignoring misplaced/unreachable replicas, false positives during append, skipping recent-accessed files, shutdown hanging on scanner threads, and missing files during directory iteration. Static handler state can leak between tests if storage IDs collide, but randomized cluster paths reduce that risk.

## Test Signals
Signals include expected iterator block counts and saved/loaded block equality, scanner enabled/disabled state, good and bad block sets, scanner statistics, presence of `scanner.cursor`, post-restart scan counts, federated scan counts, rate-limited block count bounds, suspect rescan inclusion/exclusion, no bad blocks during append, zero scans for recent-access skipping, and shutdown duration bounded by join timeout.
