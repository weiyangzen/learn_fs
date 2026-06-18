# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockScanner.java

## Purpose

`BlockScanner` is the DataNode-level coordinator for periodic on-disk block verification. It owns one `VolumeScanner` per storage volume, configures scan rate/staleness/cursor behavior, starts and stops scanner threads as volumes appear or disappear, marks suspicious blocks for prompt rescans, and exposes scanner statistics through an HTTP servlet.

## Important APIs, types, and functions

- `BlockScanner(DataNode, Configuration)` builds a cached `Conf`, initializes scanner shutdown join timeout, and logs whether scanning is enabled.
- `Conf` reads scanner-specific configuration: bytes per second, scan period, max staleness, cursor save interval, skip-recent-accessed flag, and optional test-only `ScanResultHandler`.
- `isEnabled()` gates all scanner creation and suspect-block handling on positive scan period and positive target bytes/sec.
- `addVolumeScanner(FsVolumeReference)` creates and starts a `VolumeScanner`, stores it by storage ID, and keeps or releases the volume reference according to success.
- `removeVolumeScanner`, `removeAllVolumeScanners`, `enableBlockPoolId`, and `disableBlockPoolId` manage scanner lifecycle and block-pool participation.
- `markSuspectBlock(String storageId, ExtendedBlock block)` forwards urgent scan requests to the matching volume scanner.
- `Servlet.doGet` emits plain text scanner statistics from the DataNode web UI.

## Control flow

The constructor snapshots configuration. When the DataNode registers or adds a storage volume, `addVolumeScanner` checks `isEnabled`, rejects duplicate storage IDs, constructs `VolumeScanner(conf, datanode, ref)`, starts the thread, and records it in the `TreeMap`. If scanner creation fails or scanning is disabled, it closes the `FsVolumeReference` so the volume is not leaked.

Removal is synchronized. Single-volume removal shuts down the scanner, removes it from the map, and joins for five minutes. Full shutdown first broadcasts `shutdown()` to all scanners, then joins each using the configurable `joinVolumeScannersTimeOutMs`, then clears the map. Block-pool enable/disable events are broadcast to all active volume scanners.

`markSuspectBlock` is a fast path from other DataNode components, such as read failures in `BlockSender`, to prioritize a likely-corrupt block. It is intentionally best-effort: disabled scanners or missing volume scanners are logged and ignored.

## State and persistence behavior

`BlockScanner` itself keeps only in-memory state: `TreeMap<String, VolumeScanner> scanners`, current `Conf`, and join timeout. Persistent scanner cursors and result handling are delegated to `VolumeScanner`; `Conf.cursorSaveMs` and `maxStalenessMs` are passed down but not persisted here. Synchronization on public lifecycle methods serializes mutations to the scanner map.

## Dependencies and integration points

The class integrates with `DataNode`, `VolumeScanner`, `FsVolumeReference`, `FsVolumeSpi`, `ExtendedBlock`, servlet context attribute `datanode`, `DFSConfigKeys`, and Guava `Uninterruptibles`. It is a downstream consumer of corruption signals from block transfer code, and an upstream coordinator for per-volume verification workers.

## Risks and edge cases

Resource ownership is the main local risk: `FsVolumeReference` must be closed when a scanner is not retained, and scanner threads must not block DataNode shutdown indefinitely. Disabled scanner configuration is represented by negative or zero scan periods or zero throughput; callers must tolerate no-op add/remove/suspect paths. Duplicate storage IDs are logged as errors and ignored, which is safer than running two scanners over the same volume but may hide volume identity bugs.

## Test signals

Tests should validate configuration edge cases, especially scan period zero compatibility behavior, disabled scanner behavior, duplicate add handling, reference cleanup on add failure, block-pool broadcast, suspect-block routing, shutdown timeout behavior, and servlet output for enabled and disabled scanner states. `Conf.allowUnitTestSettings` and internal config keys provide explicit test hooks.
