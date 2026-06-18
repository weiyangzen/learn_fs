# sources/distributed-fs/juicefs/pkg/meta/sql.go

## Purpose

`sql.go` is the primary SQL implementation of the JuiceFS `Meta` engine. It maps filesystem metadata operations onto relational tables through xorm, supporting SQLite, MySQL, and PostgreSQL backends through build tags and companion driver files. The file owns schema models, engine construction, transaction/retry behavior, inode and directory namespace mutations, chunk/slice reference tracking, session lifecycle, quota and directory statistics persistence, changelog emission, JSON metadata dump/load, clone support, ACL storage, delegation tokens, and batched directory fetching.

## Important APIs, Types, And Functions

The table model structs are the core persistence contract: `setting`, `counter`, `edge`, `node`, `chunk`, `sliceRef`, `delslices`, `symlink`, `xattr`, `flock`, `plock`, `session`, `session2`, `sustained`, `delfile`, `dirStats`, `detachedNode`, `dirQuota`, `userGroupQuota`, `acl`, `delegationToken`, and `changeLog`. `node` stores inode attributes and splits sub-millisecond timestamp remainder into `Atimensec`, `Mtimensec`, and `Ctimensec`; `parseAttr` and `parseNode` are the translation points between SQL rows and the public `Attr` shape.

`dbMeta` embeds `baseMeta` and stores the `xorm.Engine`, reusable session pool, optional fast-dump snapshot, SQL statement map, and table prefix. `newSQLMeta` parses DSN query options such as `max_open_conns`, `max_idle_conns`, `max_idle_time`, `max_life_time`, and `table_prefix`, normalizes backend-specific details, configures xorm logging and connection pools, installs the table mapper, initializes prefixed statements, and returns a `Meta`.

Transaction helpers are central: `txn` handles write transactions with read-only rejection, inode batch locks, backend-specific retry detection, and exponential-ish backoff; `roTxn` opens repeatable-read read-only transactions when supported; `simpleTxn` reuses pooled sessions for simple read paths and retries transient failures. `shouldRetry` recognizes SQLite busy/locked errors, MySQL duplicate/restart/bad-connection cases, PostgreSQL retry-safe or serialization/deadlock errors, and connection exhaustion messages.

Namespace operations include `doLookup`, `doGetAttr`, `doSetAttr`, `doMknod`, `doUnlink`, `doRmdir`, `doRename`, `doLink`, `doReaddir`, `doBatchUnlink`, `doAttachDirNode`, and the cursor-based `getDirFetcher`. They enforce type checks, permission checks through `Access`, immutable/append-only flags, sticky-bit rules, case-insensitive resolution when configured, trash handling, parent mtime throttling via `SkipDirMtime`, nlink updates, open-file sustained inode handling, and changelog entries.

File data operations include `appendSlice`, `upsertSlice`, `doTruncate`, `doFallocate`, `doRead`, `doList`, `doWrite`, `CopyFileRange`, `deleteChunk`, `doDeleteFileData`, `doCleanupDelayedSlices`, `doCompactChunk`, `ListSlices`, and scan helpers for trash/pending slices and files. These functions persist chunk slice buffers, maintain `chunk_ref` reference counts, add zero slices for holes/truncation, and trigger object deletion once reference counts drop to zero.

Administrative APIs include `syncAllTables`, `doInit`, `Reset`, `doLoad`, session functions (`doNewSession`, `GetSession`, `ListSessions`, `doRefreshSession`, stale-session cleanup), volume stats (`doSyncVolumeStat`, `doFlushStats`), directory stats (`doUpdateDirStat`, `doSyncDirStat`, `doGetDirStat`), quotas (`doGetQuota`, `doSetQuota`, `doDelQuota`, `doLoadQuotas`, `doFlushQuotas`, `cleanUgUsage`), changelog scanning/cleanup, ACL methods, delegation-token methods, and clone methods.

## Control Flow

Initialization starts in `newSQLMeta`, where the DSN is parsed and normalized, an engine is created, `Ping` verifies connectivity, connection-pool limits are applied, and xorm table mapping is prefixed. `doInit` then creates or migrates all tables, loads the existing `format` row if present, applies feature transition cleanup for directory stats and user/group quotas, writes the new format, and inserts root/trash nodes plus counters for a fresh database.

Most mutating filesystem calls follow the same pattern: open a `txn`, load relevant `node`/`edge` rows, perform permission and flag checks, update normalized rows and counters, emit `genLog` if changelog is enabled, then update in-memory accounting after commit. Deletion paths split between moving entries into trash, decreasing nlink, moving open deleted files into `sustained`, adding closed files to `delfile`, and deleting side tables such as `xattr` and `symlink`.

Chunk writes append serialized slice records to a `(inode, indx)` `chunk` row and insert a `sliceRef` with ref count 1. Copy and clone paths duplicate chunk rows and increment refs. Compaction replaces old slice records with a compacted slice and either stores delayed slice cleanup in `delslices` or immediately decrements old refs. Cleanup paths scan `sliceRef.refs <= 0`, `delfile`, and `delslices` to delete object data outside the SQL transaction.

Dump/load has an older JSON tree path in this file. `DumpMeta` optionally builds an in-memory `dbSnap` for fast full-root dumps, emits format/counter/sustained/deleted/quota metadata, recursively serializes the tree and trash, and strips secrets unless requested. `LoadMeta` validates the target is empty, creates tables, concurrently inserts nodes/edges/chunks/xattrs/misc rows through channels, updates deduplicated chunk refs and hardlink nlinks, and loads dumped quotas.

## State And Persistence Behavior

The relational schema is normalized around inode attributes (`node`), directory names (`edge`), file extents (`chunk`), object reference counts (`chunk_ref`), xattrs, symlinks, locks, sessions, trash/deletion queues, quotas, and ACL/token tables. `counter` rows store global counters such as `nextInode`, `nextChunk`, `nextSession`, `usedSpace`, `totalInodes`, `nextCleanupSlices`, and `nextTrash`. Changelog rows are append-only records with the wall timestamp, operation text, session id, and transaction id.

Durability depends on SQL transactions plus xorm row locks (`ForUpdate`) for critical rows. SQLite writes are globally serialized by passing inode `1` into the batch lock. Directory stats, quota usage, and global space/inode counters are partly buffered in memory and flushed separately, so the implementation includes sync/repair paths for reconciliation.

## Dependencies And Integration Points

This file integrates with `baseMeta`, the `Meta` interface, the open-file cache (`m.of`), quota helpers, ACL helpers from `pkg/acl`, slice encoding helpers, dump/load JSON types, progress bars in `pkg/utils`, xorm, database/sql transaction options, logrus, and backend driver registration through `engineCreator` and `Register` in companion files. Build tags keep it active when at least one SQL backend is included.

## Risks And Edge Cases

The highest-risk areas are transactional correctness under multiple SQL dialects, retry behavior that treats duplicate-key errors as transient in some paths, parent nlink and mtime updates that convert zero affected rows to backend-specific errors, chunk reference count drift after clone/copy/delete/compaction, stale session cleanup racing with active clients, trash handling for hardlinks, and large directory or batch operations that must respect backend parameter limits. `LoadMeta` uses goroutines that call `logger.Fatalf` on insert errors, which is abrupt and makes load failures process-fatal rather than ordinary returned errors.

## Test Signals

`sql_test.go` exercises SQLite end-to-end through `testMeta`, validates batch clone chunk-ref accounting via `TestSQLiteBatchUpdateChunkRefs`, covers backend creation for MySQL/PostgreSQL when available, checks PostgreSQL `search_path` rejection, and tests DSN helper behavior. Broader behavior is likely covered by shared meta tests invoked through `testMeta`, but the complex rename/trash/quota/session/changelog paths need integration coverage against all supported SQL backends to catch dialect-specific locking and retry differences.
