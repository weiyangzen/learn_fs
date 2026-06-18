# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/migrate.go

## Purpose
Implements entry migration for BeeGFS paths, supporting two migration mechanisms: background chunk rebalancing through metadata server RPCs and legacy temporary-file replacement. It determines source target or buddy-group placement from current entry metadata, maps user-provided source/destination entities through management mappings, optionally updates directory storage-pool assignment, and emits asynchronous `MigrateResult` values through `util.ProcessPaths`.

## Important APIs, Types, And Functions
Key public surface is `MigrateEntries(ctx, pm, cfg)`, `MigrateCfg`, `MigrateResult`, `MigrateStats`, and `MigrateStatus`. Internal execution is handled by `migrateEntry`, `tmpFileMigrate`, `tmpFileMigrateLink`, `tmpFileMigrationPossible`, `didFileChange`, and `chunkRebalanceMigrate`. The file depends on helper functions/types from the same package that are not defined here, notably `GetEntry`, `getMigrationForEntry`, `newPackedEntryMap`, and `SetEntryCfg`/`setEntry`.

## Control Flow
`MigrateEntries` validates rebalancing licensing when requested, globally sets process umask to zero, builds `util.Mappings`, expands configured source targets from targets, nodes, and pools, optionally maps storage targets to buddy groups, then resolves destination pool/targets/groups. If directory updates are enabled it validates a `SetEntryCfg` for destination pool updates. Each path is processed by `migrateEntry`.

`migrateEntry` rejects its own temp-file prefix, fetches verbose entry details, handles directories by either setting their pool or skipping them, tracks non-inlined hard-linked entries in a bounded recent-entry map, computes the source/destination ID pairs, and branches to rebalancing or temp-file migration. Rebalancing sends `StartChunkBalanceMsg` with exponential backoff and jitter on `OpsErr_AGAIN`. Temp-file migration creates a replacement file or symlink with the target pattern, copies xattrs/content/ownership, checks inode/mtime/ctime/size/link count just before rename, overwrites the original, and restores timestamps.

## State And Persistence
Persistent effects include metadata-server chunk-balance jobs, new stripe placement, temporary files named `.beegfs_tmp_migrate.<basename>`, overwritten files/symlinks, copied xattrs, ownership/mode, timestamps, and directory pattern changes. Process-global state includes `syscall.Umask(0)` with no local restore and random jitter via `math/rand`. In-memory state includes source/destination maps, the bounded `recentHardLinks` cache, and accumulated stats.

## Dependencies And Integration Points
Integrates with BeeGFS management (`VerifyLicense`), management/entity mappings (`util.GetMappings`), node store TCP BeeMsg RPCs (`MakeFileWithPattern`, `StartChunkBalance`), BeeGFS client filesystem provider methods (`Lstat`, copy helpers, `OverwriteFile`), ioctl symlink creation, and path streaming/filtering from `ctl/pkg/util`.

## Risks And Edge Cases
The global umask change affects the whole process and callers must reset it if needed. Temp-file migration refuses `000` permissions and hard links; rebalancing is required for hard-linked entries. The hard-link dedupe cache is bounded, so very large hard-link sets can still submit duplicates. Temp files from failed prior migrations are removed and retried, but paths matching the temp prefix are categorically refused. Symlink migration to specific IDs is unsupported without a destination pool. `didFileChange` compares only nanosecond components for mtime/ctime, not seconds, which may miss changes across second boundaries with equal nsec values. Rebalancing queue-full handling can retry indefinitely if configured with negative retries.

## Test Signals
No tests are present in this file. Behavior is high-risk because it mutates data placement and file contents; useful tests would cover `didFileChange`, temp-file preflight, rebalancing retry exhaustion, destination ID selection, and directory update behavior with mocked mappings/node-store/filesystem providers.
