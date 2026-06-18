# Research: subset-b-007612

Grouped research for the JuiceFS SQL metadata backend files in `sources/distributed-fs/juicefs/pkg/meta`. Each section preserves the original source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/sql.go -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/sql.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/sql_bak.go -->
# sources/distributed-fs/juicefs/pkg/meta/sql_bak.go

## Purpose

`sql_bak.go` implements the protobuf-based SQL metadata backup and restore path. It complements the older JSON tree dump/load code in `sql.go` with segmented dump/load handlers for format, counters, nodes, chunks, edges, symlinks, sustained open-deleted files, delayed-delete files, slice refs, ACLs, xattrs, quotas, and directory stats. The build tag matches the SQL backends.

## Important APIs, Types, And Functions

`sqlDumpBatchSize` controls row batching at 100,000. `dump` orders all dump segment functions and uses one repeatable-read read-only transaction when `DumpOption.Threads == 1`; multithreaded dumps warn that the database must be externally read-only for consistency. `execTxn` reuses a dump-scoped transaction when present, otherwise uses `roTxn`.

`sqlQueryBatch` partitions id ranges and uses `errgroup` with `opt.Threads` as a concurrency limit. Dump functions map SQL rows to `pkg/meta/pb` messages: `dumpNodes`, `dumpChunks`, `dumpEdges`, `dumpSymlinks`, `dumpCounters`, `dumpSustained`, `dumpDelFiles`, `dumpSliceRef`, `dumpACL`, `dumpXattr`, `dumpQuota`, and `dumpDirStat`. `dumpEdges` also derives `pb.Parent` records for hardlink parent counts.

The restore dispatcher `load` routes segment types to `loadFormat`, `loadCounters`, `loadNodes`, `loadChunks`, `loadEdges`, `loadSymlinks`, `loadSustained`, `loadDelFiles`, `loadSliceRefs`, `loadAcl`, `loadXattrs`, `loadQuota`, and `loadDirStats`. `insertRows` is the common batched insert helper. `insertSliceRefs`, `upsertSliceRef`, and `genMultiSQL` handle backend-specific insert-ignore/upsert behavior for `chunk_ref`.

## Control Flow

Dumping starts by optionally opening a single read-only transaction and installing it in context. Each segment function scans the relevant table, batches protobuf records, and sends `dumpedResult` messages to the output channel. Node dumping first emits trash nodes, then scans normal inode id ranges. Chunk and edge dumping scan by table `id`, while small tables are read whole. Restore reverses that mapping by converting protobuf messages back into xorm beans and writing them in transaction-sized chunks.

## State And Persistence Behavior

The code serializes the SQL backend's normalized state instead of walking only a directory tree. This preserves non-tree metadata such as counters, sustained inodes, deleted files, slice refs with non-default ref counts, ACL rows, xattrs, quotas, and dir stats. Chunk loading inserts chunk rows first, then derives default `sliceRef` rows from chunk slice buffers. Explicit `SliceRefs` segments then upsert non-default reference counts.

## Dependencies And Integration Points

The file depends on xorm sessions from `dbMeta`, protobuf message types in `pkg/meta/pb`, ACL rule encoding/decoding, `errgroup`, `proto.Message`, and the same SQL transaction helpers from `sql.go`. It integrates with the generic metadata dump/load framework through segment constants such as `segTypeNode` and `segTypeQuota`.

## Risks And Edge Cases

Multithreaded dump mode can produce inconsistent backup data unless callers enforce database quiescence. `sqlQueryBatch` logs the row count before `eg.Wait`, so the debug count may be incomplete at log time. Large whole-table reads for symlinks, sustained rows, deleted files, ACLs, xattrs, quotas, and dir stats may be memory-heavy. Restore correctness depends on chunk-ref insertion/upsert semantics matching each backend dialect and on duplicate handling not masking real data corruption.

## Test Signals

No direct tests in `sql_test.go` target this protobuf backup path. Indirect confidence comes from shared metadata dump/load code and SQL backend tests, but backup consistency, multithreaded dump behavior, hardlink parent reconstruction, and chunk-ref upsert behavior need backend-specific integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/sql_bak.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/sql_lock.go -->
# sources/distributed-fs/juicefs/pkg/meta/sql_lock.go

## Purpose

`sql_lock.go` implements SQL-backed BSD flock and POSIX byte-range lock persistence for `dbMeta`. It keeps lock state in the `flock` and `plock` tables so locks are visible across JuiceFS clients sharing the same SQL metadata backend.

## Important APIs, Types, And Functions

`Flock` handles whole-file read/write/unlock operations. It maps the caller owner to signed int64, removes rows on `F_UNLCK`, or loads all flock rows for an inode under `ForUpdate`, checks conflicts, and inserts or updates the caller's row with `Ltype` `R` or `W`.

`Getlk` inspects `plock` rows for conflicting POSIX byte-range locks and returns the first conflict by mutating `ltype`, `start`, `end`, and `pid`. `Setlk` inserts, updates, or deletes byte-range records for the caller after conflict detection against other session/owner pairs. `ListLocks` returns both POSIX and flock states for diagnostics.

## Control Flow

Both `Flock` and `Setlk` perform conflict checks inside write transactions. The code first validates the target inode exists by locking the corresponding `node` row, then locks and reads all relevant `flock` or `plock` rows for that inode. Own locks are ignored for conflict purposes. Nonblocking calls return `EAGAIN` on conflict; blocking calls sleep and retry until the lock succeeds, a non-retry error occurs, or the context is canceled.

For `Setlk`, unlock requests load the caller's serialized byte-range records, call `updateLocks`, and either delete the `plock` row or update its `Records` blob. Lock requests compare ranges with all other owners, merge/update the caller's records, then insert or update the serialized blob only when it changed.

## State And Persistence Behavior

Whole-file locks are one row per `(inode, sid, owner)` with a single lock type byte. POSIX locks are one row per `(inode, sid, owner)` with a serialized `Records` blob produced by `dumpLocks` and parsed by `loadLocks`. Successful state changes emit changelog operations such as `FLOCK`, `SETLK`, and unlock variants. Stale session cleanup in `sql.go` deletes both `flock` and `plock` rows by session id.

## Dependencies And Integration Points

The code depends on lock constants (`F_UNLCK`, `F_RDLCK`, `F_WRLCK`), serialized `plockRecord` helpers (`loadLocks`, `updateLocks`, `dumpLocks`), `ownerKey`, diagnostic item types, `dbMeta.txn`, xorm row locking, and the session id `m.sid`. It integrates with `ListSessions(detail=true)` through the same persisted lock tables.

## Risks And Edge Cases

Blocking locks use polling sleeps rather than database wait/notify, so high contention can add latency and transaction churn. `Getlk` reads with `m.db.Rows` outside `roTxn`, so it has weaker snapshot/retry behavior than the transactional update paths. Owner values are cast from uint64 to int64; callers using values above max int64 would wrap. Conflict reporting returns the first map iteration conflict, which is not deterministic.

## Test Signals

The listed `sql_test.go` file does not directly test SQL locks. Lock behavior is likely exercised through shared meta tests, but SQL-specific persistence, stale-session cleanup, blocking cancellation, owner casting, and byte-range merge/split behavior warrant focused tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/sql_lock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/sql_mysql.go -->
# sources/distributed-fs/juicefs/pkg/meta/sql_mysql.go

## Purpose

`sql_mysql.go` contains MySQL-specific registration and engine creation for the SQL metadata backend. It adapts MySQL duplicate-entry detection, password handling, and transaction isolation configuration before delegating the rest of metadata behavior to `newSQLMeta`/`dbMeta`.

## Important APIs, Types, And Functions

`isMySQLDuplicateEntryErr` recognizes `*mysql.MySQLError` number `1062` for unique-key conflicts. `recoveryMysqlPwd` recovers percent-decoded passwords in DSNs by parsing a synthetic URL around the password segment. `createMySQLEngine` parses the DSN, ensures `Params` exists, tries to set repeatable-read isolation through `transaction_isolation`, falls back to legacy `tx_isolation` when the first variable is unknown, pings the engine to verify the setting, and returns a ready xorm engine. `isUnknownTransactionIsolationErr` detects the fallback condition. `init` appends duplicate checking, installs the engine creator, and registers the `mysql` metadata scheme.

## Control Flow

MySQL engine creation starts with `mysql.ParseDSN(recoveryMysqlPwd(dsn))`. It then tries two possible system variable names because MySQL/MariaDB/TiDB variants differ. Each attempt creates an xorm engine, pings it, returns on success, closes it on failure, and only continues when the error says the chosen isolation variable is unknown. Any other ping failure is returned immediately.

## State And Persistence Behavior

This file does not define metadata tables directly. Its persistent effect is to force repeatable-read transaction isolation through DSN parameters before `dbMeta` begins using the engine. Duplicate-entry detection feeds shared retry and conflict logic in `sql.go` and `sql_bak.go`.

## Dependencies And Integration Points

It depends on `github.com/go-sql-driver/mysql`, xorm, and shared package globals `dupErrorCheckers`, `engineCreator`, and `Register`. `newSQLMeta` calls `engineCreator["mysql"]` when the driver is MySQL.

## Risks And Edge Cases

The DSN password recovery logic relies on locating the first colon and last at sign; unusual usernames or network addresses could make this brittle, though tests cover several special-character password cases. Setting isolation through connection parameters can fail for managed or proxy databases; the code only tolerates unknown variable names, not permission or unsupported value errors. MySQL duplicate-entry errors are also treated as retryable elsewhere, which can hide whether a conflict is expected or a real invariant violation.

## Test Signals

`TestRecoveryMysqlPwd` covers empty passwords and special characters including `@`, `|`, and `:` in encoded and direct forms. `TestMySQLClient` attempts end-to-end metadata testing against `root:@/dev` when the environment provides a database.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/sql_mysql.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/sql_pg.go -->
# sources/distributed-fs/juicefs/pkg/meta/sql_pg.go

## Purpose

`sql_pg.go` provides PostgreSQL-specific registration for the SQL metadata backend. It imports the pgx stdlib driver, detects unique-constraint errors, and registers the `postgres` scheme with the shared SQL metadata constructor.

## Important APIs, Types, And Functions

`isPGDuplicateEntryErr` checks whether an error is `*pgconn.PgError` with SQLSTATE `23505`, PostgreSQL's unique-violation code. The `init` function appends that checker to `dupErrorCheckers` and calls `Register("postgres", newSQLMeta)`.

## Control Flow

There is no runtime control flow beyond package initialization. `newSQLMeta` in `sql.go` rewrites the logical `postgres` driver to `pgx`, prefixes the address with `postgres://`, validates that `search_path` contains at most one schema, and sets that schema on the xorm engine after connection.

## State And Persistence Behavior

This file does not persist metadata itself. It controls how PostgreSQL duplicate-key errors are classified by the shared SQL backend, affecting transaction retry, id collision handling, and backup restore upserts.

## Dependencies And Integration Points

It depends on `github.com/jackc/pgx/v5/pgconn` and imports `github.com/jackc/pgx/v5/stdlib` for driver registration. It integrates with `dupErrorCheckers`, `Register`, and the PostgreSQL branch in `newSQLMeta`.

## Risks And Edge Cases

Only direct `*pgconn.PgError` values are recognized; wrapped errors may not match unless upstream preserves the concrete type. PostgreSQL duplicate-key errors can represent either benign races or real data corruption depending on call site, so the shared retry behavior must remain carefully scoped.

## Test Signals

`TestPostgreSQLClient` runs shared metadata tests when a local PostgreSQL database is available and `SKIP_NON_CORE` is not true. `TestPostgreSQLClientWithSearchPath` verifies that multiple schemas in `search_path` are rejected with the expected message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/sql_pg.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/sql_sqlite.go -->
# sources/distributed-fs/juicefs/pkg/meta/sql_sqlite.go

## Purpose

`sql_sqlite.go` provides SQLite-specific registration for the SQL metadata backend. It detects SQLite constraint errors, exposes the SQLite busy error to shared retry logic, and registers the `sqlite3` scheme.

## Important APIs, Types, And Functions

`isSQLiteDuplicateEntryErr` checks whether an error is a `sqlite3.Error` with code `sqlite3.ErrConstraint`. The `init` function sets package-level `errBusy` to `sqlite3.ErrBusy`, appends the duplicate checker, and registers `sqlite3` with `newSQLMeta`.

## Control Flow

The only control flow is package initialization. SQLite-specific DSN defaults are handled in `newSQLMeta`: shared cache is enabled unless explicitly configured, WAL journaling is selected by default, busy timeout defaults to 5000 ms, and `DirBatchNum["db"]` is reduced to respect SQLite variable limits.

## State And Persistence Behavior

This file does not write metadata directly. Its main persistence impact is making SQLite lock contention retryable and making unique-constraint detection available to shared insertion, clone, restore, and session-id conflict paths.

## Dependencies And Integration Points

It depends on `github.com/mattn/go-sqlite3` and shared globals `errBusy`, `dupErrorCheckers`, and `Register`. The `txn` function in `sql.go` serializes SQLite writers by using a single inode batch lock key.

## Risks And Edge Cases

The duplicate checker only matches unwrapped `sqlite3.Error` values. SQLite's single-writer model means high write concurrency is bottlenecked even with retry and WAL mode. Constraint errors are broad; treating all `ErrConstraint` values as duplicate-entry conflicts may conflate unique conflicts with other constraint failures.

## Test Signals

`TestSQLiteClient` runs the shared metadata test suite against a temporary SQLite database. `TestSQLiteBatchUpdateChunkRefs` specifically validates SQLite clone/delete behavior for chunk reference counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/sql_sqlite.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/sql_test.go -->
# sources/distributed-fs/juicefs/pkg/meta/sql_test.go

## Purpose

`sql_test.go` contains focused tests for SQL metadata backend construction, backend-specific DSN behavior, and SQLite chunk-reference correctness around batch clone and chunk deletion. It also invokes the shared `testMeta` suite for SQLite, MySQL, and PostgreSQL when those databases are available.

## Important APIs, Types, And Functions

`TestSQLiteClient` creates a temporary SQLite metadata database and runs `testMeta`. `TestSQLiteBatchUpdateChunkRefs` sets up source and destination directories, writes two slices to a source file, clones that file through `BatchClone`, verifies `chunk_ref` counts increase from 1 to 2, deletes the cloned chunk, and verifies counts decrease to 1 without triggering deletion callbacks. `sqlSliceRefCount` is a helper that reads a `sliceRef` row and validates its stored size.

`TestMySQLClient` and `TestPostgreSQLClient` instantiate SQL metadata backends for external databases and run `testMeta`; comments mark them as mutate tests. `TestPostgreSQLClientWithSearchPath` checks the one-schema `search_path` guard. `TestRecoveryMysqlPwd` validates MySQL password recovery cases. `TestGetCustomConfig` checks extraction and deletion of custom URL query parameters.

## Control Flow

The SQLite chunk-ref test initializes metadata, creates directories and a file, allocates two slices, writes both slices into the same chunk, checks initial reference counts, collects directory entries, invokes `BatchClone`, checks cloned file lookup and doubled refs, installs an `OnMsg(DeleteSlice)` callback that fails the test if deletion is attempted, calls `deleteChunk` on the clone, and finally verifies refs are decremented but still present.

## State And Persistence Behavior

The tests directly inspect `chunk_ref` rows for correctness, which is important because SQL clone/copy/delete operations rely on reference counts to decide when object slices can be physically deleted. The DSN tests verify that custom query parameters are consumed before the remaining DSN is passed to drivers.

## Dependencies And Integration Points

The file depends on test helpers such as `testConfig`, `testFormat`, `testMeta`, `Background`, and the public `Meta` methods. It also calls internal `dbMeta` methods (`Reset`, `Init`, `deleteChunk`, `getBase().BatchClone`) because the tests are in package `meta`.

## Risks And Edge Cases

External MySQL/PostgreSQL tests require local services and can mutate databases, making them environment-dependent. The SQLite chunk-ref test covers batch clone but not `CopyFileRange`, compaction, delayed slice cleanup, hardlink clone semantics, or failure retries. `TestPostgreSQLClientWithSearchPath` calls `err.Error()` without guarding nil, relying on the constructor to fail.

## Test Signals

The strongest signal is `TestSQLiteBatchUpdateChunkRefs`, which targets a previously risky persistence invariant: cloned chunks must increment `chunk_ref` and deleting a clone must not delete still-referenced slices. Shared `testMeta` invocations provide broad behavioral coverage when databases are configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/sql_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/status.go -->
# sources/distributed-fs/juicefs/pkg/meta/status.go

## Purpose

`status.go` implements high-level filesystem status collection for any `Meta` backend. It loads sanitized format settings, active sessions, filesystem capacity/inode statistics, and optional trash/pending-deletion object statistics into a `Sections` result.

## Important APIs, Types, And Functions

`Statistic` is the status data model. It includes used/available space and inodes, plus optional JSON-omitted counters and sizes for trash files, pending deleted files, trash slices, and pending deleted slices. `Sections` groups the sanitized `Format`, session list, and computed `Statistic`. `Status` is the main API.

## Control Flow

`Status` first calls `m.Load(true)` to read the format and then calls `RemoveSecret` to redact credentials/tokens. It calls `m.ListSessions()` for active sessions. It initializes `Statistic`, calls `m.StatFS` on `RootInode`, and computes used space as `totalSpace - AvailableSpace`.

When the `trash` flag is true, it creates a progress instance with four double spinners and calls `m.ScanDeletedObject`. The supplied callbacks accumulate slice sizes, pending slice sizes, trash file counts/sizes, and pending deleted file sizes. After scanning, the spinners are finalized and their counts are copied into the `Statistic`. If a `Sections` pointer is provided, the function stores format, sessions, and statistics before returning.

## State And Persistence Behavior

`Status` is read-oriented and does not directly persist metadata. It may trigger backend scans through `ScanDeletedObject`, which can be expensive and may interact with backend cleanup scan logic, but the callbacks here only count and always return `false` for cleanup.

## Dependencies And Integration Points

The function depends on the `Meta` interface methods `Load`, `ListSessions`, `StatFS`, and `ScanDeletedObject`; `Background` and `WrapContext` context helpers; `utils.NewProgress`; and filesystem constants such as `RootInode`. It is backend-independent and consumes the SQL backend through the same interface as Redis, TiKV, or other metadata engines.

## Risks And Edge Cases

`UsedSpace = totalSpace - AvailableSpace` assumes the backend returns a consistent pair and can underflow if a backend reports invalid values. Trash scans can be expensive on large metadata stores and add progress UI side effects even though this is a status function. Errors are wrapped by phase (`load setting`, `list sessions`, `stat fs`, `statistic`) but partial results are not returned unless all requested work succeeds.

## Test Signals

The listed SQL tests do not directly target `Status`. It should be covered by backend-agnostic status or CLI tests that verify secret redaction, session listing, StatFS integration, and trash scan counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/status.go -->
