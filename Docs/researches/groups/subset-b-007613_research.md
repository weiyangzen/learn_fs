# Research: subset-b-007613

This grouped report covers JuiceFS transactional KV metadata backends/utilities and Azure/B2/BOS object storage adapters. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv.go -->
# sources/distributed-fs/juicefs/pkg/meta/tkv.go

## Purpose
`tkv.go` is the main JuiceFS metadata engine implementation backed by a transactional key/value store. It defines the generic `tkvClient`/`kvtxn` contracts, the `kvMeta` engine, key encodings, transaction retry policy, and almost all filesystem metadata operations: lookup, attribute mutation, create/unlink/rmdir/rename/link, directory listing, file chunk writes, copy range, quotas, dir stats, garbage collection, changelog, JSON dump/load, clone, ACL, Kerberos delegation token, and directory fetch pagination.

## Important APIs, Types, and Functions
Core interfaces are `kvtxn`, `iterKvTxn`, `tkvClient`, and optional `tkvChangelogClient`. `kvMeta` embeds `baseMeta` and implements `Meta` and `engine`. Key helpers include `fmtKey`, `inodeKey`, `entryKey`, `chunkKey`, `sliceKey`, `delfileKey`, lock/session/quota/ACL/token keys, `packCounter`, `parseCounter`, `packEntry`, `packDirStat`, and `packQuota`. The high-value operation methods are `txn`, `doInit`, session methods, `genLog`, `ScanChangelog`, `doCleanupChangelog`, `doMknod`, `doUnlink`, `doBatchUnlink`, `doRmdir`, `doRename`, `doLink`, `doReaddir`, `doWrite`, `CopyFileRange`, `doCleanupSlices`, `doCompactChunk`, quota methods, `DumpMeta`, `LoadMeta`, clone methods, ACL methods, and token methods.

## Control Flow and State
All mutations funnel through `m.txn`, which checks read-only mode, applies per-inode batch locking, retries backend write conflicts up to a configurable limit, records transaction metrics, and backs off with randomized sleeps. Read paths use `simpleTxn`, `get`, or `scanValues` where possible. The keyspace is prefix-oriented: inode records and their entries/chunks/xattrs/parent links live under `A`, deleted files under `D`, slice refs under `K`, delayed/trash slices under `L`, sessions under `SE`/`SI`/legacy `SH`, dir stats under `U`, quotas under `QD`/`QU`/`QG`, ACLs under `R`, and extension keys under `X...`. Filesystem operations load parent and inode attrs, enforce permissions/flags/quota, update entries and attrs atomically, then perform out-of-transaction callbacks for stat/quota/cache/data-delete side effects.

## State and Persistence Behavior
Persistent state is entirely KV encoded, with counters stored little-endian and timestamp-like values stored big-endian. Changelog entries are written inside mutating transactions when enabled and use backend transaction ids, with special TiKV sharding delegated through `tkvChangelogClient`. File data metadata is append-only slice records per chunk plus reference counters, with delayed slice cleanup and negative refs driving object deletion. Open-but-unlinked files become sustained session entries. `DumpMeta` can scan a full snapshot into a tree, while `LoadMeta` imports JSON dumps into an empty database with batched writes and hardlink parent reconstruction.

## Dependencies and Integration Points
This file is the central integration point between backend adapters (`memkv`, `badger`, `etcd`, `fdb`, `tikv`), `baseMeta`, ACL package, open-file cache, quota/stat accounting, changelog consumers, metadata backup/dump code, and object-slice garbage collection. Backend-specific behavior enters via `tkvClient.config`, `rewind`, `shouldRetry`, `scan`, `reset`, and optional changelog methods.

## Risks and Test Signals
Major risks are transaction conflict storms, inconsistent post-transaction stat/quota updates, malformed key/value panics, append-only chunk bloat, slice reference underflow, hardlink parent drift, changelog id gaps, large directory memory pressure, and backend-specific scan consistency. Tests should exercise cross-backend `testMeta`, create/delete/rename/link semantics, sustained cleanup, chunk copy/refcounts, quota edge cases, ACL id reuse, dump/load round trips, changelog cleanup, and retries under conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_badger.go -->
# sources/distributed-fs/juicefs/pkg/meta/tkv_badger.go

## Purpose
`tkv_badger.go` adapts BadgerDB v4 into the generic transactional KV metadata interface, enabled when the `nobadger` build tag is absent. It provides an embedded local metadata backend.

## Important APIs, Types, and Functions
The key types are `badgerTxn` and `badgerClient`. `badgerTxn` implements `id`, `get`, `gets`, `scan`, `exist`, `set`, `append`, `incrBy`, and `delete`. `badgerClient` implements `tkvClient` with `txn`, `simpleTxn`, `scan`, `reset`, `close`, `gc`, `shouldRetry`, `rewind`, and `name`. `newBadgerClient` opens the database and registers `drivers["badger"]`.

## Control Flow and State
Each transaction creates a writable Badger transaction, runs the caller closure, converts recovered Badger errors into returned errors, and commits unless the closure failed. `scan` can optimize prefix scans when `end == nextKey(begin)` and suppress value prefetch for keys-only scans. Top-level `scan` uses a read transaction and a prefetched iterator. `reset(nil)` drops all data; prefix reset calls `DropPrefix`.

## State and Persistence Behavior
Badger stores the full metadata keyspace on local disk at the configured path. Transaction ids combine Badger read timestamp and a local atomic sequence so changelog keys are less likely to collide. A background hourly ticker repeatedly runs Badger value-log GC at discard ratio 0.7 until no more work is available. `close` stops the ticker and closes the DB.

## Dependencies and Integration Points
It depends on `github.com/dgraph-io/badger/v4` and JuiceFS logger utilities. It plugs into `newKVMeta("badger", ...)`, `tkv.go` transaction retry handling, dump/load, and the shared backend test suite.

## Risks and Test Signals
Risks include large transaction failures such as `badger.ErrTxnTooBig`, iterator lifetime mistakes, value-log GC goroutine leaks if `close` is skipped, and prefix/drop behavior deleting too much if prefixes are wrong. Tests cover `TestBadgerClient`, `TestBadgerKV`, keys-only scan nil values, and a too-large delete transaction returning `ErrTxnTooBig`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_badger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_bak.go -->
# sources/distributed-fs/juicefs/pkg/meta/tkv_bak.go

## Purpose
`tkv_bak.go` implements the newer KV-native metadata backup and restore path using protobuf batch segments. It complements the JSON `DumpMeta`/`LoadMeta` path in `tkv.go` with source-key scans and batched inserts.

## Important APIs, Types, and Functions
Primary entry points are `kvMeta.dump`, `prepareLoad`, and `LoadMetaV2`. Dump helpers include `dumpCounters`, `dumpMix`, `dumpSustained`, `dumpDelFiles`, `dumpSliceRef`, `dumpACL`, `dumpQuota`, `dumpDirStat`, and `dumpChangeLog`. Load helpers include `insertKVs`, `loadFormat`, `loadCounters`, `loadNodes`, `loadChunks`, `loadEdges`, `loadSymlinks`, `loadSustained`, `loadDelFiles`, `loadSliceRefs`, `loadAcl`, `loadXattrs`, `loadQuota`, `loadDirStats`, and `loadParents`.

## Control Flow and State
`dump` runs a fixed sequence of segment dumpers. For TiKV it requires a `startTS` from the backend config to ensure consistency and stores it in the context for snapshot reads. `dumpMix` parallelizes the `A...` inode keyspace by first byte ranges, decodes node/edge/chunk/symlink/xattr/parent records into pooled protobuf objects, and emits batches of up to `kvDumpBatchSize`. Other dumpers scan their specialized prefixes. `LoadMetaV2` checks that the target database is empty, reads `BakFormat` segments, converts each segment to KV pairs, and flushes sorted batches bounded by transaction count and byte size.

## State and Persistence Behavior
The backup format preserves counters, metadata graph records, sustained/deleted files, slice refs, ACLs, quotas, dir stats, and a tail of changelog entries. Slice refs are stored as exported refs and reloaded as internal `refs - 1` counters. ACL max id is recomputed from loaded ACL ids. Etcd uses a much smaller transaction batch limit than other backends.

## Dependencies and Integration Points
This file depends on `pkg/meta/pb`, protobuf, `BakFormat`, `dumpResult`, segment type constants, key encoders from `tkv.go`, and backend snapshot support through `tkvClient.config("startTS")`. It integrates with JuiceFS backup/load commands that prefer the V2 segment format.

## Risks and Test Signals
Risks include inconsistent dumps if a backend lacks a stable snapshot, goroutine/channel cancellation leaks, pool object reuse after emission, missing segment types during load, batch sizes exceeding backend transaction limits, and incorrect endian/key decoding. Tests should cover V2 dump/load round trips across backends, TiKV snapshot enforcement, ACL counter restoration, quota variants, changelog tails, and malformed keys/segments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_bak.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_etcd.go -->
# sources/distributed-fs/juicefs/pkg/meta/tkv_etcd.go

## Purpose
`tkv_etcd.go` adapts etcd v3 to the transactional KV metadata interface, enabled unless `noetcd` is set. It lets JuiceFS metadata live in an etcd cluster under a path-derived prefix.

## Important APIs, Types, and Functions
Key types are `etcdTxn` and `etcdClient`. Transaction methods implement point gets, batched gets capped at 128 keys, range scans, prefix existence checks, buffered set/delete, append, and counter increments. Client methods implement transaction execution, conflict detection, paginated scans, reset, TLS config parsing, and `newEtcdClient`.

## Control Flow and State
`etcdTxn` records observed mod revisions for reads and buffers writes. `commmit` builds compare conditions from observed revisions and then put/delete ops from the buffer; unsuccessful compares return the package-level `conflicted` error so `kvMeta.txn` retries. To avoid huge etcd transactions, `set` auto-commits when the buffer reaches 128 operations and clears observations. Top-level scans establish a current revision, then page through ranges with `WithMaxModRev`, serializable reads, and duplicate skipping across pages.

## State and Persistence Behavior
All metadata persists in etcd under `u.Path + "\xFD"` via `withPrefix`. Etcd transaction ids and changelog rewind are currently zero, so generic changelog id generation is effectively unavailable for etcd. Prefix reset deletes all keys under the supplied prefix. The client uses optional URL user/password and TLS query parameters.

## Dependencies and Integration Points
It depends on `go.etcd.io/etcd/client/v3`, etcd transport TLS helpers, URL parsing, and `prefixClient`. It integrates with `newKVMeta("etcd", ...)`, generic KV metadata operations, and tests requiring `ETCD_ADDR`.

## Risks and Test Signals
Risks include partial logical transactions because auto-commit can split large buffered writes, no useful transaction id for changelog, scanning stale/revision-limited data, 128-op transaction limits, and TLS/host parsing mistakes. Tests include `TestEtcdClient`, `TestEtcd`, and shared `testTKV`; further coverage should stress large metadata mutations and changelog-enabled etcd behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_etcd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_fdb.go -->
# sources/distributed-fs/juicefs/pkg/meta/tkv_fdb.go

## Purpose
`tkv_fdb.go` adapts FoundationDB to the generic transactional KV metadata layer behind the `fdb` build tag.

## Important APIs, Types, and Functions
Key types are `fdbTxn` and `fdbClient`. `newFdbClient` sets API version 630, opens the configured cluster file/path, applies a query `prefix` through `withPrefix`, and registers `drivers["fdb"]`. Transaction methods map to FoundationDB `Get`, parallel `gets`, range scans, `Set`, `AppendIfFits`, atomic `Add` counters, and `Clear`.

## Control Flow and State
`fdbClient.txn` wraps the closure in FoundationDB `Transact`, relying on FDB's built-in retry loop. Top-level `scan` uses repeated snapshot read transactions with a large range limit and advances by appending a zero byte to the last key when a page is full. `reset` clears the prefix range. `id` combines the FDB read version with an atomic client-local sequence to generate changelog ids.

## State and Persistence Behavior
Metadata is persisted in FoundationDB under the selected prefix plus `0xFD`. Atomic counter increments use FDB's little-endian add semantics over the same encoding as `packCounter`. `close` is a no-op, so lifecycle is owned by the FDB binding/database handle.

## Dependencies and Integration Points
It depends on `github.com/apple/foundationdb/bindings/go/src/fdb`, build tags, URL parsing, and `prefixClient`. It integrates with `newKVMeta("fdb", ...)`, generic KV operations, changelog generation, and FDB-specific tests.

## Risks and Test Signals
Risks include build-tag drift, API version incompatibility, `AppendIfFits` not matching arbitrary append semantics for large values, scan pagination gaps, and `shouldRetry` returning false because retries are delegated to FDB. Tests in `tkv_fdb_test.go` call `testMeta` and `testTKV` against a local FoundationDB cluster.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_fdb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_fdb_test.go -->
# sources/distributed-fs/juicefs/pkg/meta/tkv_fdb_test.go

## Purpose
`tkv_fdb_test.go` contains FoundationDB-specific integration tests behind the `fdb` build tag.

## Important APIs, Types, and Functions
`TestFdbClient` creates a full metadata engine with `newKVMeta("fdb", "/etc/foundationdb/fdb.cluster?prefix=test2", testConfig())` and runs `testMeta`. `TestFdb` creates a raw FDB transactional KV client with prefix `test1` and runs shared `testTKV`.

## Control Flow and State
Both tests require a FoundationDB cluster file at `/etc/foundationdb/fdb.cluster`. The tests use separate prefixes to avoid colliding engine-level and raw-KV coverage. The file uses comments indicating mutate-test skipping and disables unchecked error linting.

## State and Persistence Behavior
The tests write real FoundationDB state and rely on `testTKV` resetting its backend. `testMeta` exercises complete JuiceFS metadata behavior over persistent FDB keys.

## Dependencies and Integration Points
The tests integrate `tkv_fdb.go`, `tkv_test.go` shared raw KV tests, and broader metadata tests from the package.

## Risks and Test Signals
Risks are environmental: missing FDB build tag, missing cluster file, or unavailable local cluster. Passing tests signal that the FDB adapter can support both the generic KV contract and full metadata engine semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_fdb_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_lock.go -->
# sources/distributed-fs/juicefs/pkg/meta/tkv_lock.go

## Purpose
`tkv_lock.go` implements advisory BSD flock and POSIX byte-range locks for the KV metadata backend.

## Important APIs, Types, and Functions
Important types and helpers are `lockOwner`, `marshalFlock`, `unmarshalFlock`, `marshalPlock`, and `unmarshalPlock`. Public metadata methods are `Flock`, `Getlk`, `Setlk`, and `ListLocks`.

## Control Flow and State
Flock state is a map from `{sid, owner}` to `R`/`W`/unlock serialized under `F<inode>`. POSIX locks are a map from `{sid, owner}` to serialized `plockRecord` ranges under `P<inode>`. `Flock` and `Setlk` run transactional read/modify/write loops; conflicts return `EAGAIN`, and blocking callers sleep briefly and retry until success or context cancellation. `Getlk` removes the caller's own owner from consideration and returns the first conflicting lock. `ListLocks` decodes both lock families for diagnostics.

## State and Persistence Behavior
Locks are persisted in the metadata KV store and include the JuiceFS session id. Stale-session cleanup in `tkv.go` scans `F` and `P` prefixes and removes lock owners whose `sid` expired. Empty lock maps delete their key.

## Dependencies and Integration Points
It depends on lock constants and range helpers from `utils.go`, transaction/changelog helpers from `tkv.go`, and session cleanup. It implements the lock portions of the `Meta` interface for KV backends.

## Risks and Test Signals
Risks include unfair blocking spin loops, stale lock retention if session cleanup fails, large lock maps per inode, range merge/split bugs in `updateLocks`, and pid visibility only for same-session locks. Tests should cover shared/exclusive conflicts, unlock range splitting, blocking cancellation, stale session cleanup, and `ListLocks` decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_lock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_mem.go -->
# sources/distributed-fs/juicefs/pkg/meta/tkv_mem.go

## Purpose
`tkv_mem.go` implements the in-memory `memkv` transactional KV backend used for tests and lightweight local runs.

## Important APIs, Types, and Functions
Types are `memTxn`, `kvItem`, and `memKV`. It registers `memkv` in `init`. `nextKey` is defined here and shared by other KV backends. `newMockClient` loads a persisted `setting` snapshot from `/tmp/juicefs.memkv.setting.json`.

## Control Flow and State
`memTxn` buffers writes and records observed versions during reads/scans/existence checks. Commit locks the B-tree, validates observed versions for optimistic concurrency, optionally persists the transaction buffer when it contains `setting`, then applies buffered puts/deletes. Scans operate over a locked store for transaction scans and over a cloned B-tree snapshot for client-level scans.

## State and Persistence Behavior
Most data is process-local in a Google B-tree. Only a transaction buffer containing the `setting` key is JSON-written to `settingPath`, allowing basic format persistence between mock-client creations. Transaction ids are monotonic local integers. `reset(nil)` replaces the B-tree; prefix reset scans and deletes matching keys transactionally.

## Dependencies and Integration Points
It depends on `github.com/google/btree`, JSON, and the generic KV metadata interfaces. It is the default raw test backend for `testTKV` and the full metadata `TestMemKVClient`.

## Risks and Test Signals
Risks include returning internal value slices without copying, coarse locking, limited persistence semantics, `nextKey` panic on all-0xFF prefixes, and optimistic conflict behavior diverging from real backends. Tests exercise full metadata behavior and generic scans, gets, counters, zero-byte keys, and large scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_mem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_prefix.go -->
# sources/distributed-fs/juicefs/pkg/meta/tkv_prefix.go

## Purpose
`tkv_prefix.go` scopes a `tkvClient` to a fixed byte prefix so multiple JuiceFS metadata namespaces can share one backend safely.

## Important APIs, Types, and Functions
Types are `prefixTxn`, `prefixIterator`, and `prefixClient`. Key functions are `realKey`, `origKey`, transaction wrappers, `scan`, `reset`, optional changelog delegation, and `withPrefix`.

## Control Flow and State
`prefixTxn` prepends the namespace prefix to every key before delegating to the underlying transaction and strips the prefix from scan/iterator keys before returning them. `prefixClient.simpleTxn` and `txn` wrap the closure with a prefixed transaction. `scan` scans the physical prefixed range and returns logical keys. `reset` only accepts `nil` and maps it to a physical prefix reset.

## State and Persistence Behavior
The wrapper has only in-memory prefix state. Persistence is in the underlying backend with all keys physically namespaced. If the wrapped backend implements `tkvChangelogClient`, changelog key creation/range scanning is delegated; otherwise generic logical `XLOG` keys are used inside the prefix.

## Dependencies and Integration Points
It depends on the generic KV interfaces and `nextKey`. Etcd, TiKV, and FDB constructors use this wrapper to isolate path or query-prefix namespaces.

## Risks and Test Signals
Risks include prefix stripping panics if an underlying backend returns keys outside the prefix, reset rejecting non-nil prefixes, and optional iterator support requiring the wrapped transaction to implement `iterKvTxn`. Shared `TestMemKV` wraps `memkv` with a prefix and runs `testTKV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_prefix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_test.go -->
# sources/distributed-fs/juicefs/pkg/meta/tkv_test.go

## Purpose
`tkv_test.go` provides shared test coverage for transactional KV clients and selected backend integrations.

## Important APIs, Types, and Functions
Backend tests include `TestMemKVClient`, `TestTiKVClient`, `TestBadgerClient`, `TestEtcdClient`, `TestBadgerKV`, `TestEtcd`, and `TestMemKV`. `testTKV` is the reusable raw-client contract test. Badger-specific regression tests are `TestBadgerScanKeysOnlyNilValues` and `TestBadgerDeleteTxnTooBig`.

## Control Flow and State
`testTKV` resets the backend, verifies empty existence, set/append/get/gets, client and transaction scans over ranges/prefixes, deletes, counter increments including negative values, keys containing zero bytes, and large ordered scans over 100,000 generated key/value pairs. Full metadata tests create `kvMeta` engines and delegate to package-level `testMeta`.

## State and Persistence Behavior
Tests mutate real backends and usually isolate data via temp dirs, prefixes, or configured external endpoints. Badger tests use temporary directories except one legacy `test_badger` path. Etcd and TiKV tests depend on external services and have skip comments/environment guards.

## Dependencies and Integration Points
The file ties all KV adapters to the shared metadata test suite. It depends on Badger for direct regression setup and on environment variables such as `ETCD_ADDR` and `SKIP_NON_CORE`.

## Risks and Test Signals
Passing `testTKV` signals backend compliance for ordering, prefix scans, nil values, append, delete, counters, and high-volume iteration. Gaps include transaction conflict simulation, changelog semantics, crash recovery, and large real metadata operations beyond what `testMeta` covers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_tikv.go -->
# sources/distributed-fs/juicefs/pkg/meta/tkv_tikv.go

## Purpose
`tkv_tikv.go` adapts TiKV transaction KV storage to JuiceFS metadata, enabled unless `notikv` is set. It also provides TiKV-specific changelog sharding and GC handling.

## Important APIs, Types, and Functions
Important types are `tikvTxn`, `tikvClient`, `logMergeHeap`, and `logMergeItem`. Key functions include `newTikvClient`, `tiKVChangeLogShards`, `logKey`, `scanLogRange`, `rewind`, `simpleTxn`, `txn`, `scan`, `reset`, and `gc`.

## Control Flow and State
Client creation parses `tikv://`-style addresses, configures TLS security from query parameters, sets PingCAP logging level, parses `gc-interval`, creates a txnkv client, optionally enables TSO follower proxy and max TSO batch wait, and wraps the KV store in a path prefix. Normal writes begin a TiKV transaction, optionally at a context-provided startTS, run the closure, then enable 1PC and async commit before commit. `simpleTxn` begins with `math.MaxUint64` startTS for latest point reads and rejects writes. Scans use low-priority snapshots and restart after GC-too-early errors.

## State and Persistence Behavior
Metadata persists in TiKV under the configured prefix. Transaction ids are TiKV start timestamps and are used for changelog ordering. Changelog keys are sharded as `XLOG<shard><id>` with a configurable shard count, and scans merge shard iterators using a heap. `config("startTS")` exposes a timestamp for consistent V2 dumps. `gc` advances TiKV safe point according to `gcInterval`.

## Dependencies and Integration Points
It depends on PingCAP/TiKV client-go, PD options, oracle timestamp helpers, and `prefixClient`. It integrates with `tkv.go` changelog/dump logic, slice cleanup GC, and external TiKV tests.

## Risks and Test Signals
Risks include service dependency complexity, GC-too-early scan restarts, changelog shard merge bugs, timestamp rewind windows missing logs, TLS/query misconfiguration, and write-conflict string matching. Tests include `TestTiKVClient` and shared metadata behavior, but TiKV changelog sharding and GC need targeted integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/tkv_tikv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/utils.go -->
# sources/distributed-fs/juicefs/pkg/meta/utils.go

## Purpose
`utils.go` contains shared metadata constants, error translation, permission/lock helpers, recursive remove and summary traversal logic, atime policy checks, and transaction method-name diagnostics.

## Important APIs, Types, and Functions
Constants include counter names, fallocate flags, clone modes, atime modes, and permission masks. Key types are `msgCallbacks`, `freeID`, `queryMap`, `plockRecord`, `ownerKey`, `PLockItem`, and `FLockItem`. Important functions are `errno`, `accessMode`, `align4K`, `parseOwnerKey`, `loadLocks`, `dumpLocks`, `updateLocks`, `emptyDir`, `emptyEntry`, `Remove`, `GetSummary`, `getDirSummary`, `GetTreeSummary`, `getTreeSummary`, `atimeNeedsUpdate`, `relatimeNeedUpdate`, `txMethod.name`, and `callerName`.

## Control Flow and State
`errno` normalizes Go errors to syscall errno values and logs stacks for unexpected errors. Recursive deletion descends directories with bounded concurrency, batches non-directory unlink operations, retries non-trash directories on `ENOTEMPTY`, and honors cancellation. Summary functions either use stored dir stats or recursively list children and aggregate counts/space with bounded goroutines. `updateLocks` splits, updates, removes, sorts, and merges POSIX lock ranges. `callerName` lazily discovers the outer non-anonymous caller unless the context has an explicit transaction method.

## State and Persistence Behavior
Most state is transient. Summary and removal mutate metadata through `baseMeta` APIs, so persistence is delegated to the active engine. Atime checks influence later persisted attr updates. Counter names define persistent KV counter keys.

## Dependencies and Integration Points
It is used by KV and non-KV metadata engines, lock implementations, quota/stat accounting, command query parsing, and tests. It depends on Redis nil handling, JuiceFS utilities, runtime stack/caller inspection, and platform-specific constants from `utils_*.go`.

## Risks and Test Signals
Risks include errno masking unexpected failures as `EIO`, recursive delete races, summary double-counting when dir stats are stale, lock range merge errors, and caller-name instability. Tests cover atime/relatime and caller-name behavior; broader integration tests should cover recursive remove and summary under concurrent mutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/utils_darwin.go -->
# sources/distributed-fs/juicefs/pkg/meta/utils_darwin.go

## Purpose
`utils_darwin.go` defines Darwin-specific errno, flock, and xattr constants for metadata code.

## Important APIs, Types, and Functions
It exports `ENOATTR`, `F_UNLCK`, `F_RDLCK`, `F_WRLCK`, `XattrCreateOrReplace`, `XattrCreate`, and `XattrReplace`.

## Control Flow and State
There is no runtime control flow. The file maps package-level constants to `syscall` and `golang.org/x/sys/unix` values selected by the Darwin build.

## State and Persistence Behavior
No state is stored. These constants affect how metadata operations interpret platform lock and extended attribute flags.

## Dependencies and Integration Points
It integrates with lock code, xattr create/replace handling in `tkv.go`, and portable metadata APIs. It depends on Go's `syscall` package and `x/sys/unix`.

## Risks and Test Signals
Risks are mostly portability regressions if Darwin constants diverge from kernel/FUSE expectations. Platform-specific xattr and locking tests on macOS are the best signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/utils_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/utils_linux.go -->
# sources/distributed-fs/juicefs/pkg/meta/utils_linux.go

## Purpose
`utils_linux.go` defines Linux-specific errno, flock, and xattr constants for metadata code.

## Important APIs, Types, and Functions
It exports `ENOATTR` as `syscall.ENODATA`, lock constants from `syscall`, and xattr create/replace constants from `golang.org/x/sys/unix`.

## Control Flow and State
There is no executable flow. Build selection ensures Linux metadata code uses Linux's xattr missing-value errno and native FUSE/lock flag values.

## State and Persistence Behavior
No state is persisted. Constants influence syscall-compatible return values and xattr flag validation in metadata operations.

## Dependencies and Integration Points
It is consumed by xattr and lock code throughout the meta package and by tests running on Linux. It depends on `syscall` and `x/sys/unix`.

## Risks and Test Signals
Risks are low but include wrong errno mapping for xattr absence or mismatched lock constants. Linux xattr create/replace and lock integration tests validate this file indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/utils_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/utils_test.go -->
# sources/distributed-fs/juicefs/pkg/meta/utils_test.go

## Purpose
`utils_test.go` tests metadata utility behavior for atime update policy and transaction method-name discovery.

## Important APIs, Types, and Functions
Tests are `TestRelatimeNeedUpdate`, `TestAtimeNeedsUpdate`, and `Test_getCallerName`.

## Control Flow and State
`TestRelatimeNeedUpdate` checks that relatime updates when atime is older than 24 hours, older than ctime, older than mtime, and not when timestamps match. `TestAtimeNeedsUpdate` exercises `NoAtime`, `RelAtime`, and `StrictAtime`, including strict mode's greater-than-one-second threshold. `Test_getCallerName` verifies explicit context override and stack-derived caller name.

## State and Persistence Behavior
The tests use in-memory `Attr` and `baseMeta` structs only. No metadata backend is touched.

## Dependencies and Integration Points
They cover utility functions consumed by readlink/atime update paths, transaction logging/metrics, and user-facing metadata behavior.

## Risks and Test Signals
Passing tests signal correct core time-policy logic, but they do not cover nanosecond boundary combinations, timezone irrelevance, or caller-name behavior under deeper anonymous stack frames beyond the simple closure case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/utils_windows.go -->
# sources/distributed-fs/juicefs/pkg/meta/utils_windows.go

## Purpose
`utils_windows.go` provides Windows-compatible metadata constants for xattrs and locks where POSIX constants are not natively available.

## Important APIs, Types, and Functions
It exports `ENOATTR`, synthetic `F_UNLCK`/`F_RDLCK`/`F_WRLCK`, and synthetic xattr create/replace constants.

## Control Flow and State
There is no runtime flow. The file defines constants selected by Windows builds.

## State and Persistence Behavior
No state is stored. The constants allow shared lock/xattr metadata logic to compile and use stable symbolic values on Windows.

## Dependencies and Integration Points
It depends only on `syscall` for `ENODATA`. It integrates with the same lock and xattr code paths as Unix platforms but maps to package-defined values rather than OS flock constants.

## Risks and Test Signals
Risks include semantic mismatch between synthetic constants and Windows/FUSE behavior, and returning `ENODATA` where callers expect another Windows error. Windows-specific lock and xattr API tests are needed for confidence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/utils_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/azure.go -->
# sources/distributed-fs/juicefs/pkg/object/azure.go

## Purpose
`azure.go` implements the `wasb` object storage backend for Azure Blob Storage.

## Important APIs, Types, and Functions
The `wasb` type embeds `DefaultObjectStorage` and `tierStorage` and holds Azure container/blob clients plus auth mode. It implements `String`, `Create`, `Head`, `Get`, `Put`, `Copy`, `Delete`, `List`, and `Restore`. Helper functions include `toValue`, `str2Tier`, `createAzureCredential`, `normalizeSASToken`, `domainFromHost`, `autoWasbEndpoint`, and `newWasb`.

## Control Flow and State
`newWasb` parses endpoint/container, then selects authentication in priority order: `AZURE_STORAGE_CONNECTION_STRING`, SAS token or managed identity when account key is absent, and shared key otherwise. It auto-detects public or China cloud endpoint suffixes when the host lacks a domain. `Put` applies storage tier and optional validated tag. `Copy` either changes tier/tags in place when tier context targets the same key, or performs server-side copy; shared-key copy uses a short-lived source SAS URL while token auth uses the direct source URL. `List` uses flat paging and rejects delimiter mode.

## State and Persistence Behavior
Persistent state is Azure containers and blobs. Local state records the container name, client handles, tier configuration, and whether token auth is in use. Deletes treat missing blobs as success. Azure archive restore is unsupported because Azure tier changes are permanent rather than temporary restore requests.

## Dependencies and Integration Points
It depends on Azure SDK `azblob`, `azcore`, `azidentity`, blob/container/SAS packages, AWS helper pointers for request ids, and JuiceFS object abstractions including `ObjectStorage`, `AttrGetter`, tiers, tags, and registration via `Register("wasb", newWasb)`.

## Risks and Test Signals
Risks include auth-mode confusion, SAS token handling with leading `?`, short SAS expiry during copy, delimiter listing unsupported by callers, nil response fields, endpoint auto-detection DNS failures, and missing request-id handling on errors. Tests should cover all auth priorities, public/China endpoint detection, tier/tag put and copy, missing-object mapping, ranged get, and list pagination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/azure.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/b2.go -->
# sources/distributed-fs/juicefs/pkg/object/b2.go

## Purpose
`b2.go` implements the Backblaze B2 object storage backend using `go-backblaze`.

## Important APIs, Types, and Functions
The `b2client` type wraps a `backblaze.Bucket` and implements `String`, `Create`, `Head`, `Get`, `Put`, `Copy`, `Delete`, and `List`. `getFileInfo` retrieves metadata through a small ranged download fallback. `newB2` parses the endpoint, authenticates, finds or creates the bucket, and registers `b2`.

## Control Flow and State
`Head` calls `getFileInfo`, maps B2 404 to `os.ErrNotExist`, and returns object metadata. `Get` chooses full-object or ranged download; unlimited ranged reads use a large artificial end. `Put` uploads a file in one call. `Copy` resolves the source file id and calls B2 server-side copy with destination bucket id. `Delete` resolves the file version then deletes it, treating not-found errors as success. `List` clamps limit to 1000 and maps B2 file records to JuiceFS objects.

## State and Persistence Behavior
Remote B2 bucket objects hold all persistent state. The client keeps only a bucket pointer. There is no multipart implementation in this file, and a TODO notes possible S3-client-based multipart support.

## Dependencies and Integration Points
It depends on `gopkg.in/kothar/go-backblaze.v0`, HTTP status codes, JuiceFS object interfaces, and storage registration. It integrates with generic object storage selection through `Register("b2", newB2)`.

## Risks and Test Signals
Risks include metadata lookup requiring tiny downloads, empty-file range edge cases, no multipart support for large efficient writes, library-specific error string matching in delete, and list token semantics tied to `NextFileName`. Tests should cover empty files, range reads, delete idempotence, bucket creation/finding, copy, and list pagination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/b2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/bos.go -->
# sources/distributed-fs/juicefs/pkg/object/bos.go

## Purpose
`bos.go` implements the Baidu BOS object storage backend with storage class/tag support and multipart upload/copy support.

## Important APIs, Types, and Functions
`bosclient` embeds `DefaultObjectStorage` and `tierStorage`, stores the bucket and BOS client, and implements object APIs plus multipart APIs: `Limits`, `CreateMultipartUpload`, `UploadPart`, `UploadPartCopy`, `AbortUpload`, `CompleteUpload`, and `ListUploads`. Helpers are `autoBOSEndpoint` and `newBOS`.

## Control Flow and State
`Create` creates the bucket and optionally sets default storage class, ignoring already-exists errors. `Head` maps BOS 404 to `os.ErrNotExist`. `Get` selects ranged or full reads; full reads verify checksum using user metadata or BOS CRC32. `Put` materializes the reader into bytes, applies tier storage class and encoded tags, and uploads. `Copy` applies storage class and optional tag replacement. `List` clamps limit to 1000, includes common prefixes for delimiter listings, and sorts mixed entries. Multipart methods map JuiceFS parts to BOS upload APIs.

## State and Persistence Behavior
Persistent state lives in BOS buckets, objects, object metadata/tags, and multipart upload state. Local state is the bucket name, BOS client, and tier config. `newBOS` can auto-discover bucket location from `bcebos.com`, uses environment credentials if explicit credentials are absent, disables SDK retries, and sets JuiceFS user agent.

## Dependencies and Integration Points
It depends on Baidu BCE/BOS SDK packages, JuiceFS checksum helpers, tier/tag utilities, object multipart abstractions, and storage registration via `Register("bos", newBOS)`.

## Risks and Test Signals
Risks include memory pressure from buffering entire `Put` readers, checksum compatibility, endpoint auto-location failures, no SDK retry policy, tag directive behavior during copy, delete string matching for `NoSuchKey`, and multipart part-size boundaries. Tests should cover create existing bucket, storage class/tag put/copy, checksum-verified get, delimiter list ordering, multipart upload/copy/abort/complete, and environment credential fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/object/bos.go -->
