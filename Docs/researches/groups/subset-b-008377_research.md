# Research: subset-b-008377

Grouped research for Badger source files in `sources/storage-engines/badger`. Each section is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/db2_test.go -->
# sources/storage-engines/badger/db2_test.go

## Purpose
`db2_test.go` is a high-risk regression and stress test suite for Badger database behavior that is not fully covered by the smaller API tests. It focuses on value-log truncation and replay, large key/value limits, compaction table selection, value-log GC interactions, Windows mmap recovery, drop operations, version accounting, stream-writer key counts, and startup/read-only guarantees.

## Important APIs, Types, and Functions
- `TestTruncateVlogWithClose`, `TestTruncateVlogNoClose*`: exercise value-log truncation after clean close and manual crash-style reopen scenarios.
- `TestBigKeyValuePairs`, `TestPushValueLogLimit`, `TestBigValues`: validate boundary handling around key sizes, value sizes, and value-log file limits; most are manual due to resource cost.
- `BenchmarkDBOpen`: measures read-only open cost against a prebuilt Badger directory.
- `TestCompactionFilePicking`, `addToManifest`, `createTableWithRange`: build synthetic SST tables and manifest entries to verify compaction ordering heuristics.
- `TestReadSameVlog`: repeatedly reads values from the same value log in plain and encrypted configurations.
- `TestL0GCBug`: disabled regression scenario for `KeepL0InMemory` with value-log GC.
- `TestWindowsDataLoss`: Windows-only recovery regression for value-log mmap expansion and simulated crash.
- `TestDropPrefixWithNoData`, `TestDropAllDropPrefix`: validate prefix/drop concurrency and no-op prefix drops.
- `TestIsClosed`, `TestMaxVersion`, `TestTxnReadTs`, `TestKeyCount`, `TestAssertValueLogIsNotWrittenToOnStartup`: cover lifecycle, timestamp, stream writer, and read-only startup invariants.

## Control Flow and State
Most tests create temporary Badger directories, open a DB with targeted options, perform transactional writes, close or intentionally simulate a crash, reopen, and then verify reads or internal counters. Crash simulations release directory guards and avoid normal close paths to expose replay behavior. Compaction tests write table files directly through `table.CreateTable`, register manifest changes, insert tables into selected levels, and then call compaction heuristics. Drop tests coordinate goroutines retrying on `ErrBlockedWrites` to verify serialization around destructive operations.

## Persistence Behavior
The file heavily exercises durable state: value-log files (`*.vlog`), SST manifests, table metadata, timestamps, and read-only reopen behavior. `TestTruncateVlogWithClose` physically truncates `000001.vlog`; `TestWindowsDataLoss` manipulates mmap/file handles and expects all original keys after reopen; `TestAssertValueLogIsNotWrittenToOnStartup` asserts read-only open and reads do not mutate latest vlog size.

## Dependencies and Integration Points
Tests integrate with `Open`, `OpenManaged`, `DB.Update`, `DB.View`, `RunValueLogGC`, `DropPrefix`, `DropAll`, `MaxVersion`, stream writer APIs, the levels controller, manifest changes, table builders, and `ristretto/z` mmap helpers. They use `testify/require`, `pb.ManifestChange`, `table.Table`, Badger options, and low-level `y` key helpers.

## Risks and Edge Cases
The riskiest paths are crash recovery after partial value-log records, massive values near `math.MaxInt32`, large manual tests that are skipped by default, Windows-only mmap behavior, and direct manipulation of level internals. Several tests are manual or disabled, so they document expected behavior but do not protect normal CI unless explicitly enabled.

## Test Signals
This is itself a test file. It provides strong regression signals for storage durability, GC, compaction picking, version handling, and read-only startup. Manual skips should be treated as reduced automated coverage for extreme value-size and long-running stream-writer scenarios.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/db2_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/db_test.go -->
# sources/storage-engines/badger/db_test.go

## Purpose
`db_test.go` is the main Badger database API and integration test suite. It covers ordinary and concurrent reads/writes, iterator behavior, transaction limits, loading/reopen, value-log GC, read-only locking, LSM-only mode, sequences, sync/checksum behavior, namespace bans, cache sizing, close races, and package examples.

## Important APIs, Types, and Functions
- Test helpers: `waitForMessage`, `summary`, `getTestOptions`, `getItemValue`, `txnSet`, `txnDelete`, `runBadgerTest`, `dirSize`, `randBytes`, `removeDir`.
- Core API tests: `TestWrite`, `TestUpdateAndView`, `TestConcurrentWrite`, `TestGet`, `TestGetAfterDelete`, `TestTxnTooBig`.
- Iterator and load tests: `TestReverseIterator`, `TestIterate2Basic`, `TestLoad`, `TestIterateDeleted`, `TestIterateParallel`, `TestIteratorPrefetchSize`.
- Persistence and GC tests: `BenchmarkDbGrowth`, `TestDeleteWithoutSyncWrite`, `TestExpiryImproperDBClose`, `TestForceFlushMemtable`, `TestCompactL0OnClose`.
- Locking/lifecycle tests: `TestPidFile`, `TestReadOnly`, `TestOpenDBReadOnly`, `TestCloseDBWhileReading`, `TestIsClosed` in `db2_test.go`.
- Feature tests: `TestSequence*`, `TestLSMOnly`, `TestMinReadTs`, `TestSyncFor*`, `TestVerifyChecksum`, `TestBannedPrefixes`, `TestIterateWithBanned`, `TestBannedAtZeroOffset`.
- Documentation examples: `ExampleOpen`, `ExampleTxn_NewIterator`.

## Control Flow and State
The test flow repeatedly creates temporary directories, opens Badger with mode-specific options, executes transactional writes and reads, then validates behavior through public APIs or carefully chosen internals. Some tests manipulate memtables or filesystem permissions to assert recovery and read-only behavior. Namespace-ban tests build namespaced keys, call `BanNamespace`, and validate both direct operations and iterator skipping. Close-race tests run concurrent `View` loops until `DB.Close` makes reads return `ErrDBClosed`.

## Persistence Behavior
This suite verifies reopening with and without encryption/compression, read timestamp recovery, value-log persistence after unsynced deletes, directory creation, checksum verification, sync visibility, memtable flush state, filesystem read-only permissions, and table-file garbage collection via `levelsController.getSummary`. It also checks that read-only opens can coexist while write opens are excluded on supported platforms.

## Dependencies and Integration Points
It integrates nearly every public Badger API: `Open`, `OpenManaged`, transactions, write batches, stream/managed write batches, iterators, sequences, `Flatten`, `RunValueLogGC`, `StreamDB`, `VerifyChecksum`, `CacheMaxCost`, namespace banning, and `Sync`. It depends on `options`, `pb`, `y`, `z.Buffer`, the filesystem, and `testify/require`.

## Risks and Edge Cases
Several tests are intentionally manual because they are expensive or long running. The suite reaches into internal fields (`db.orc`, `db.mt`, `db.imm`, `lc`, `nextMemFid`), which gives strong regression coverage but couples tests to implementation. Time-based TTL and goroutine leak tests can be sensitive to scheduling. Read-only behavior differs on Windows/Plan9 through platform-specific errors.

## Test Signals
This is the primary automated health signal for Badger's public API and many storage invariants. It includes benchmarks and manual stress tests that complement normal unit coverage, plus examples that validate user-facing documentation output.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/db_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/dir_aix.go -->
# sources/storage-engines/badger/dir_aix.go

## Purpose
`dir_aix.go` implements AIX-specific directory locking and directory sync abstractions for Badger. It handles AIX's file/process locking semantics, which differ from descriptor-scoped flock behavior on Unix.

## Important APIs, Types, and Functions
- `directoryLockGuard`: records the absolute pid-file path and whether the lock is read-only.
- `aixFlock`: shared process-local lock state containing one open file, reference count, and read-only mode.
- `aixFlockMap` and `aixFlockMapLock`: process-local registry preventing multiple descriptors for the same AIX lock file.
- `acquireDirectoryLock(dirPath, pidFileName, readOnly)`: creates or reuses a lock file, applies `unix.FcntlFlock`, writes pid for read-write mode, and returns a guard.
- `(*directoryLockGuard).release`: decrements refcount, removes pid file for read-write locks, closes the file, and deletes map state.
- `openDir`, `syncDir`: AIX directory open/sync adapters; `syncDir` is a no-op because AIX does not support fsync on directories.

## Control Flow and State
Lock acquisition resolves the pid path to an absolute path, locks the global map, and either reuses a compatible read-only lock or creates a new file lock. Read-write and read-only locks are mutually exclusive in the in-process map. Release is refcounted and only closes/removes the underlying file on the final release.

## Persistence Behavior
Read-write acquisition writes the process id into the pid file. Final release truncates and removes the pid file. `syncDir` intentionally does not fsync directory entries, so crash durability for file creation/removal metadata is weaker on AIX than on Unix platforms with directory fsync.

## Dependencies and Integration Points
This file is selected only by the `aix` build tag and is consumed by Badger open/close paths through `acquireDirectoryLock`, `release`, `openDir`, and `syncDir`. It depends on `golang.org/x/sys/unix`, `os`, `filepath`, `sync`, and Badger's `y.Wrapf` helpers.

## Risks and Edge Cases
The main risk is mismatch between AIX lock semantics and Badger's normal expectation that multiple descriptors can coexist. The map/refcount approach is process-local and does not replace kernel inter-process locking. The no-op directory sync can affect crash consistency of directory entries.

## Test Signals
No AIX-specific tests are in this file. Cross-platform DB locking tests such as `TestPidFile` and `TestReadOnly` exercise the shared behavior when run on AIX.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/dir_aix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/dir_other.go -->
# sources/storage-engines/badger/dir_other.go

## Purpose
`dir_other.go` provides directory locking and syncing for `js` and `wasip1` builds, where normal OS-level flock support is unavailable.

## Important APIs, Types, and Functions
- `directoryLockGuard`: holds an open directory file, absolute pid-file path, and read-only flag.
- `acquireDirectoryLock`: opens the directory, skips actual flocking, writes pid file for read-write mode, and returns a guard.
- `(*directoryLockGuard).release`: removes pid file for read-write locks and closes the directory handle.
- `openDir`, `syncDir`: open and fsync a directory path using `os.File.Sync`.

## Control Flow and State
Acquisition resolves the pid path, opens the directory, and deliberately avoids flock calls. For read-write mode it overwrites the pid file. Release removes the pid file before closing the directory handle.

## Persistence Behavior
The pid file is advisory only and is not backed by an exclusive kernel lock in these targets. `syncDir` attempts to fsync directory entries, returning wrapped open/sync/close errors.

## Dependencies and Integration Points
Selected by `js || wasip1` build tags. It supports the same Badger open/close integration points as other `dir_*` files, allowing the rest of the codebase to call `acquireDirectoryLock`, `release`, and `syncDir` uniformly.

## Risks and Edge Cases
The absence of real locking means concurrent writers are not prevented by this implementation. Environments with limited filesystem support may also make `os.Open`, pid writes, or `Sync` behave differently than POSIX hosts.

## Test Signals
No target-specific tests are present. General DB locking tests would not fully validate the missing flock behavior unless run in JS/WASI-like environments.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/dir_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/dir_plan9.go -->
# sources/storage-engines/badger/dir_plan9.go

## Purpose
`dir_plan9.go` implements Badger directory locking and syncing for Plan 9. It uses Plan 9's exclusive-use file semantics instead of flock and explicitly rejects read-only mode.

## Important APIs, Types, and Functions
- `directoryLockGuard`: stores the locked pid file handle and absolute path.
- `acquireDirectoryLock`: rejects read-only with `ErrPlan9NotSupported`, ensures the pid file has `os.ModeExclusive`, opens it exclusively, and writes the pid.
- `(*directoryLockGuard).release`: removes the pid file, closes the file handle, and clears guard state.
- `openDir`, `syncDir`: open and fsync a directory.
- `lockedErrStrings`, `isLocked`: classify Plan 9 lock-related error text.

## Control Flow and State
Lock acquisition first normalizes the pid path, updates an existing pid file's exclusive bit when needed, and then relies on `os.OpenFile` with `os.ModeExclusive` to fail if another process has the file open. Release removes the pid file before closing the handle.

## Persistence Behavior
The pid file persists while the DB is open and records the process id. `syncDir` fsyncs the directory for metadata durability where supported by Plan 9's filesystem.

## Dependencies and Integration Points
This platform implementation plugs into Badger open/close via the same functions used by Unix and Windows implementations. It depends on `os`, `filepath`, string error matching, and `y.Wrap`.

## Risks and Edge Cases
Plan 9 read-only DB mode is unsupported. Lock detection depends on known error substrings from Plan 9 filesystems; an unfamiliar filesystem error could be misclassified. Cleanup ordering intentionally removes the pid file before closing the exclusive handle.

## Test Signals
Shared tests like `TestReadOnly` should observe `ErrPlan9NotSupported` on Plan 9. There are no dedicated unit tests for `isLocked` or exclusive-bit repair.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/dir_plan9.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/dir_unix.go -->
# sources/storage-engines/badger/dir_unix.go

## Purpose
`dir_unix.go` is the default non-Windows, non-Plan9, non-JS/WASI, non-AIX directory locking implementation. It uses `flock` on an open directory file and fsyncs directories for crash-safe metadata updates.

## Important APIs, Types, and Functions
- `directoryLockGuard`: holds the flocked directory file, absolute pid-file path, and read-only mode.
- `acquireDirectoryLock`: opens the directory, applies exclusive or shared nonblocking `unix.Flock`, writes pid file for read-write locks, and returns a guard.
- `(*directoryLockGuard).release`: removes pid file for read-write locks and closes the directory file to release flock.
- `openDir`, `syncDir`: open a directory and call `Sync`, wrapping errors.

## Control Flow and State
The open DB path calls `acquireDirectoryLock` for the data/value directories. Read-write mode uses `LOCK_EX|LOCK_NB`; read-only uses `LOCK_SH|LOCK_NB`, allowing multiple readers but excluding writers. Releasing removes the advisory pid file before closing the flocked directory handle.

## Persistence Behavior
`syncDir` fsyncs directory entries after file creation, deletion, or rename. This is important for manifest/key-registry/table-file durability across crashes.

## Dependencies and Integration Points
This file depends on `golang.org/x/sys/unix`, `os`, `filepath`, and `y.Wrapf`. It is used by DB open/close, key-registry rewrite directory sync, and any path that needs durable directory metadata.

## Risks and Edge Cases
Locking is advisory and depends on all users respecting the same mechanism. Read-only shared locking only works on platforms selected by this file. If pid-file removal fails, release returns that error even if close succeeds.

## Test Signals
`TestPidFile`, `TestReadOnly`, and reopen/read-only tests exercise this behavior on Unix-like CI. Directory fsync errors are indirectly tested through successful DB open/close and registry rewrite paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/dir_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/dir_windows.go -->
# sources/storage-engines/badger/dir_windows.go

## Purpose
`dir_windows.go` implements Badger directory open, locking, and sync behavior on Windows. It uses a temporary delete-on-close lock file because Windows lacks the Unix flock model used elsewhere.

## Important APIs, Types, and Functions
- `openDir`, `openDirWin`: open directories using `CreateFile` with `FILE_FLAG_BACKUP_SEMANTICS`.
- `directoryLockGuard`: stores a Windows handle and lock path.
- `acquireDirectoryLock`: rejects read-only with `ErrWindowsNotSupported`, creates a lock file with no sharing and delete-on-close semantics, and returns a guard.
- `(*directoryLockGuard).release`: closes the handle, which releases and deletes the lock file.
- `syncDir`: no-op because Windows does not support directory fsync through this path.

## Control Flow and State
Lock acquisition computes an absolute lock path and calls `CreateFile` with zero access/share and `OPEN_ALWAYS`. Failure indicates another process holds the lock. Release clears the path and closes the handle.

## Persistence Behavior
No pid text is written; the lock file is temporary and deleted when the handle closes. Directory sync is intentionally a no-op, so crash-safety depends on Windows filesystem behavior and explicit file flushes elsewhere.

## Dependencies and Integration Points
Selected by the `windows` build tag. It integrates with Badger open/close lock acquisition and uses `syscall`, `os.NewFile`, and Badger error wrapping.

## Risks and Edge Cases
Read-only mode is unsupported on Windows. Directory metadata is not fsynced. The lock-file mechanism is simpler than `LockFileEx` and relies on `CreateFile` sharing behavior.

## Test Signals
`TestWindowsDataLoss` is Windows-specific and exercises mmap/reopen behavior, while read-only tests expect `ErrWindowsNotSupported`. Lock behavior is covered indirectly by DB open tests on Windows.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/dir_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/discard.go -->
# sources/storage-engines/badger/discard.go

## Purpose
`discard.go` implements a persistent, mmap-backed accounting table that tracks how many bytes in each value-log file are discardable. Badger uses this data to choose good value-log GC candidates.

## Important APIs, Types, and Functions
- `discardStats`: embeds `sync.Mutex` and `*z.MmapFile`, stores `Options`, and tracks `nextEmptySlot`.
- `discardFname`: constant `DISCARD`.
- `InitDiscardStats`: opens/creates the mmap file under `opt.ValueDir`, initializes sentinel zero entries, finds the first empty slot, sorts entries, and logs state.
- Sort interface: `Len`, `Less`, `Swap` keep active 16-byte entries sorted by file id.
- Raw helpers: `get`, `set`, `zeroOut`, `maxSlot`.
- `Update(fidu, discard)`: query, reset, increment, or create per-file discard counters under lock.
- `Iterate`, `MaxDiscard`: scan active entries and return the file with the largest discard count.

## Control Flow and State
The file format is a flat array of 16-byte slots: 8 bytes file id and 8 bytes discard bytes, big-endian. Slot zero with file id 0 is the termination sentinel. `Update` binary-searches sorted active slots, mutates counters, appends new positive entries when needed, grows the mmap file by truncating to double size when full, zeroes the next sentinel, and resorts.

## Persistence Behavior
State lives in `ValueDir/DISCARD` and is memory mapped through Ristretto `z.MmapFile`. Because updates write directly into mmap memory, the file survives DB reopen; tests verify counters reload. Growth uses `Truncate`, and initialization creates a 1 MiB file that can store 65,536 entries.

## Dependencies and Integration Points
Integrated with the value-log subsystem via `db.vlog.discardStats` and value-log GC candidate selection. Depends on `encoding/binary`, `sort`, `sync`, `filepath`, `os`, `github.com/dgraph-io/ristretto/v2/z`, and Badger `y` helpers.

## Risks and Edge Cases
Entry with file id 0 doubles as sentinel, so using fid 0 as a real value would be ambiguous; Badger value logs start at 1 in normal operation. `Iterate` is not internally locked, so callers need to use it in safe contexts or through locked methods like `MaxDiscard`. Mmap flush semantics are not explicit in this file.

## Test Signals
`discard_test.go` covers initialization, increments, resets, iteration values, `MaxDiscard` default, and reload persistence across DB reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/discard.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/discard_test.go -->
# sources/storage-engines/badger/discard_test.go

## Purpose
`discard_test.go` verifies the mmap-backed value-log discard statistics implemented in `discard.go`.

## Important APIs, Types, and Functions
- `TestDiscardStats`: initializes stats, checks empty state, writes 20 counters, iterates expected values, resets the first 10, and verifies reset vs retained values.
- `TestReloadDiscardStats`: opens a DB, updates discard stats, closes, reopens, and checks counters survived.

## Control Flow and State
Both tests create temporary directories and `DefaultOptions`. The first uses `InitDiscardStats` directly; the second reaches discard stats through `db.vlog.discardStats` to validate real DB integration.

## Persistence Behavior
`TestReloadDiscardStats` is the key persistence signal: values written before `db.Close` are expected to be visible after `Open` on the same directory.

## Dependencies and Integration Points
Depends on `os.MkdirTemp`, `testify/require`, `DefaultOptions`, `Open`, `DB.Close`, and `removeDir` from `db_test.go`.

## Risks and Edge Cases
The tests do not force mmap growth beyond the initial 1 MiB file and do not test concurrent `Update` calls. They do cover reset semantics using negative discard values.

## Test Signals
Strong focused coverage for the basic discard-stat lifecycle, but not for large numbers of value-log files, fsync behavior, or race conditions.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/discard_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/doc.go -->
# sources/storage-engines/badger/doc.go

## Purpose
`doc.go` provides the package-level documentation for Badger. It describes Badger as an embeddable Go key-value database with MVCC, transactions, serializable snapshot isolation, and an LSM tree plus value-log architecture.

## Important APIs, Types, and Functions
This file declares only `package badger`; its main API surface is the package comment. It names the primary user-facing types: `DB`, `Txn`, `Item`, and `Iterator`.

## Control Flow and State
No executable control flow is present. The comment explains how operations happen through transactions and how read-only/read-write transactions interact with items and iterators.

## Persistence Behavior
The documentation explains the architectural persistence model: keys live in an LSM tree while values are separated into value logs to reduce write amplification and keep the LSM smaller.

## Dependencies and Integration Points
The package comment is consumed by Go documentation tooling and helps orient users before reading examples in `db_test.go`.

## Risks and Edge Cases
The documentation is high level and does not enumerate platform-specific locking differences, value-log GC behavior, or transaction API caveats such as item lifetime.

## Test Signals
No tests are attached to this file directly. Documentation examples in `db_test.go` provide executable usage validation for the documented API style.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/errors.go -->
# sources/storage-engines/badger/errors.go

## Purpose
`errors.go` centralizes exported Badger sentinel errors and one option limit constant. These errors define much of the public contract for invalid options, transaction misuse, missing keys, GC outcomes, encryption failures, platform support, and closed DB access.

## Important APIs, Types, and Functions
- `ValueThresholdLimit`: max permissible `Options.ValueThreshold`, derived from `math.MaxUint16 - 16 + 1`.
- Public sentinel errors include `ErrKeyNotFound`, `ErrTxnTooBig`, `ErrConflict`, `ErrReadOnlyTxn`, `ErrDiscardedTxn`, `ErrEmptyKey`, `ErrInvalidKey`, `ErrBannedKey`, `ErrThresholdZero`, `ErrNoRewrite`, `ErrRejected`, `ErrManagedTxn`, `ErrNamespaceMode`, `ErrInvalidDump`, `ErrZeroBandwidth`, `ErrWindowsNotSupported`, `ErrPlan9NotSupported`, `ErrTruncateNeeded`, `ErrBlockedWrites`, `ErrNilCallback`, `ErrEncryptionKeyMismatch`, `ErrInvalidDataKeyID`, `ErrInvalidEncryptionKey`, `ErrGCInMemoryMode`, `ErrGCInReadOnlyMode`, and `ErrDBClosed`.

## Control Flow and State
There is no runtime control flow beyond package initialization of error values. Because these are sentinel `errors.New` values, callers and tests can compare with `==` where errors are not wrapped, or inspect wrapped messages in platform paths.

## Persistence Behavior
No direct persistence. Errors such as `ErrTruncateNeeded`, `ErrEncryptionKeyMismatch`, and `ErrInvalidDataKeyID` are part of persistence and recovery workflows elsewhere.

## Dependencies and Integration Points
Used across DB opening, transactions, iterators, value-log GC, namespace filtering, encryption/key registry, stream/load APIs, and platform directory locking. Depends only on stdlib `errors` and `math`.

## Risks and Edge Cases
Changing error text can break tests and user code that matches strings. Wrapping sentinel errors with context may affect direct equality unless the caller uses `errors.Is` where supported by the wrapper type.

## Test Signals
Many tests assert these errors: missing keys, read-only transactions, invalid keys, banned prefixes, platform read-only support, GC modes, and encryption mismatch.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/fb/BlockOffset.go -->
# sources/storage-engines/badger/fb/BlockOffset.go

## Purpose
`fb/BlockOffset.go` is generated FlatBuffers Go code for table block-offset metadata. It gives Badger's table code zero-copy accessors/builders for a block key, offset, and length.

## Important APIs, Types, and Functions
- `BlockOffset`: wrapper around `flatbuffers.Table`.
- `GetRootAsBlockOffset`, `Init`, `Table`: initialize access to serialized buffers.
- Accessors/mutators: `Key`, `KeyLength`, `KeyBytes`, `MutateKey`, `Offset`, `MutateOffset`, `Len`, `MutateLen`.
- Builder helpers: `BlockOffsetStart`, `BlockOffsetAddKey`, `BlockOffsetStartKeyVector`, `BlockOffsetAddOffset`, `BlockOffsetAddLen`, `BlockOffsetEnd`.

## Control Flow and State
Accessors compute vtable offsets and return default zero values when fields are absent. Mutators delegate to FlatBuffers slot/vector mutation helpers. Builder functions must be called in FlatBuffers reverse-construction order by table-building code.

## Persistence Behavior
This code defines the binary layout API for serialized SST table index data. The source is generated and should match `flatbuffer.fbs`; manual edits risk on-disk incompatibility.

## Dependencies and Integration Points
Depends on `github.com/google/flatbuffers/go`. Used by Badger table index encoding/decoding code outside this subset.

## Risks and Edge Cases
Generated code lacks semantic validation of vector bounds or schema compatibility beyond FlatBuffers mechanics. Regeneration with a different flatc version or schema can affect binary compatibility.

## Test Signals
No direct tests in this subset. Table read/write, iterator, checksum, and load tests indirectly exercise serialized table metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/fb/BlockOffset.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/fb/TableIndex.go -->
# sources/storage-engines/badger/fb/TableIndex.go

## Purpose
`fb/TableIndex.go` is generated FlatBuffers code for Badger table index metadata. It exposes block offsets, bloom filter bytes, max version, key count, size metrics, and stale-data size.

## Important APIs, Types, and Functions
- `TableIndex`: wrapper around `flatbuffers.Table`.
- `GetRootAsTableIndex`, `Init`, `Table`: buffer initialization.
- Accessors/mutators: `Offsets`, `OffsetsLength`, `BloomFilter`, `BloomFilterLength`, `BloomFilterBytes`, `MutateBloomFilter`, `MaxVersion`, `KeyCount`, `UncompressedSize`, `OnDiskSize`, `StaleDataSize`, and their mutators.
- Builder helpers: `TableIndexStart`, `TableIndexAddOffsets`, `TableIndexStartOffsetsVector`, `TableIndexAddBloomFilter`, `TableIndexStartBloomFilterVector`, `TableIndexAddMaxVersion`, `TableIndexAddKeyCount`, `TableIndexAddUncompressedSize`, `TableIndexAddOnDiskSize`, `TableIndexAddStaleDataSize`, `TableIndexEnd`.

## Control Flow and State
The code is a thin generated layer over FlatBuffers. Accessors check whether a field offset exists and otherwise return zero/empty defaults. `Offsets` initializes a supplied `BlockOffset` from an indirect vector element.

## Persistence Behavior
This schema-backed metadata is part of SST table persistence. `MaxVersion` supports iterator and compaction filtering; bloom filter and offset data support efficient reads; size/stale metrics support compaction and GC decisions.

## Dependencies and Integration Points
Depends on `flatbuffers/go` and `BlockOffset`. Integrated with table builder/reader code and indirectly with iterator, level handler, checksum, and loading tests.

## Risks and Edge Cases
As generated persistence code, schema drift is the major risk. Absence defaults can mask malformed or older table index buffers unless higher layers validate required fields.

## Test Signals
Indirectly covered by table creation, DB load, iterator prefix picking, checksum verification, and compaction tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/fb/TableIndex.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/fb/gen.sh -->
# sources/storage-engines/badger/fb/gen.sh

## Purpose
`fb/gen.sh` regenerates Go FlatBuffers bindings from `flatbuffer.fbs`.

## Important APIs, Types, and Functions
This shell script sets `set -e`, checks for `flatc`, invokes `install_flatbuffers.sh` if missing, runs `flatc --go flatbuffer.fbs`, moves generated files from `fb/*` to the current directory, and removes the temporary `fb` directory.

## Control Flow and State
The script must be run from the `fb` directory so relative paths resolve. It exits on the first failing command. It assumes generated Go files land under a nested `fb` directory.

## Persistence Behavior
It rewrites generated source files such as `BlockOffset.go` and `TableIndex.go`; these files affect Badger's persisted table-index format through schema-compatible generated code.

## Dependencies and Integration Points
Depends on Bash, `flatc`, `flatbuffer.fbs`, `mv`, and `rmdir`. It may call `install_flatbuffers.sh`, which can use network/package managers.

## Risks and Edge Cases
The script is not hermetic: if `flatc` is absent, installation behavior varies by OS and may require sudo/network. Running from the wrong directory can move or remove unexpected paths. It does not pin the flatc version.

## Test Signals
No tests. Correctness is validated indirectly by generated code compiling and table/index tests passing.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/fb/gen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/fb/install_flatbuffers.sh -->
# sources/storage-engines/badger/fb/install_flatbuffers.sh

## Purpose
`fb/install_flatbuffers.sh` installs the FlatBuffers compiler for regenerating Badger's generated Go metadata bindings.

## Important APIs, Types, and Functions
- `install_mac`: requires Homebrew and runs `brew install flatbuffers`.
- `install_linux`: checks for `curl`, `cmake`, `g++`, and `make`; creates a temp build dir; fetches the latest FlatBuffers release from GitHub; builds and tests it; copies `flatc` to `/usr/local/bin`.
- OS dispatch through lowercased `uname -s` for `linux` and `darwin`.

## Control Flow and State
The script exits on errors. Linux installation runs inside `sudo bash -c` with the function body injected. It downloads the current latest release at runtime and removes its temp directory after copying `flatc`.

## Persistence Behavior
It installs `/usr/local/bin/flatc`, changing system state outside the repository. It does not modify Badger source directly unless called by `gen.sh` and followed by generation.

## Dependencies and Integration Points
Used by `gen.sh` when `flatc` is missing. Depends on network access, GitHub release API format, build tooling, sudo permissions, and Homebrew on macOS.

## Risks and Edge Cases
Using "latest" makes builds non-reproducible. `grep -oP` is GNU-specific and may not work everywhere. `sudo` and `/usr/local/bin` writes are unsuitable for locked-down CI. No default branch handles unsupported OS values.

## Test Signals
No automated tests. Failures surface when regenerating FlatBuffers code.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/fb/install_flatbuffers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/histogram.go -->
# sources/storage-engines/badger/histogram.go

## Purpose
`histogram.go` builds and prints key-size and value-size histograms for a Badger database, optionally restricted to a key prefix.

## Important APIs, Types, and Functions
- `(*DB).PrintHistogram(keyPrefix)`: user-facing printer that handles nil DB and prints key/value histograms.
- `histogramData`: stores bin upper bounds, per-bin counts, total count, min/max, and sum.
- `sizeHistogram`: groups key and value histograms.
- `newSizeHistogram`: initializes key bins from `2^1` through `2^16` and value bins from `2^1` through `2^30`.
- `createHistogramBins`: builds power-of-two bin boundaries.
- `(*histogramData).Update`: updates min/max/sum/count and assigns a value to the first bin with `value < bound`, or overflow.
- `(*DB).buildHistogram`: scans a read transaction iterator and updates key/value sizes.
- `histogramData.printHistogram`: prints totals, min, max, mean, and non-empty ranges.

## Control Flow and State
`buildHistogram` creates a read-only transaction and iterator, seeks to the prefix, and loops while `ValidForPrefix` is true. Each item contributes `Item.KeySize()` and `Item.ValueSize()` without necessarily materializing full values. Printing walks non-empty bins and formats half-open ranges.

## Persistence Behavior
No persisted state is changed. The function reads a snapshot through a Badger transaction.

## Dependencies and Integration Points
Depends on `DB.NewTransaction`, iterators, item size methods, `fmt`, and `math`. It integrates with CLI/diagnostic usage that wants size distribution insight.

## Risks and Edge Cases
`printHistogram` divides by `totalCount`; empty databases or prefixes can produce `NaN` mean and min/max initialized to extreme values. Bin assignment uses strict `<`, so exact powers of two fall into the next bin.

## Test Signals
`histogram_test.go` validates same-size and mixed-size key/value distributions, counts, sums, min/max, and bin allocation for small values.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/histogram.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/histogram_test.go -->
# sources/storage-engines/badger/histogram_test.go

## Purpose
`histogram_test.go` verifies the internal histogram builder for key and value sizes.

## Important APIs, Types, and Functions
- `TestBuildKeyValueSizeHistogram`: two subtests for uniform one-byte entries and mixed one/two/three-byte entries.

## Control Flow and State
Each subtest uses `runBadgerTest`, writes entries in a single update transaction, calls `db.buildHistogram(nil)`, and validates both key and value histogram fields.

## Persistence Behavior
The tests use normal Badger writes in a temporary directory but inspect the in-memory histogram result, not persisted histogram state.

## Dependencies and Integration Points
Depends on `runBadgerTest`, `DB.Update`, `NewEntry`, and `testify/require`.

## Risks and Edge Cases
The tests do not cover prefix-restricted histograms, empty databases, large values, overflow bins, or printed output formatting.

## Test Signals
Good focused signal for binning and aggregate math on small keys/values. It also indirectly exercises iterator-based size collection.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/histogram_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/integration/testgc/main.go -->
# sources/storage-engines/badger/integration/testgc/main.go

## Purpose
`integration/testgc/main.go` is a standalone long-running integration harness for exercising Badger value-log garbage collection under concurrent writes and reads.

## Important APIs, Types, and Functions
- Globals: `maxValue`, `suffix`.
- `testSuite`: mutex-protected `vals` map plus atomic `count`.
- `encoded`: big-endian uint64 key/value prefix helper.
- `(*testSuite).write`: in one transaction, overwrites random existing keys and appends new never-overwritten keys.
- `(*testSuite).read`: reads a random key, checks value length, and verifies observed versions never go backward for tracked keys.
- `main`: opens DB at `/mnt/drive/badgertest`, starts pprof HTTP server, runs value-log GC goroutine, starts 10 workload goroutines, runs for five minutes, then iterates and validates tracked values.

## Control Flow and State
The workload maintains a monotonic counter. Writes use that counter both as new key source and as value version marker. Reads update an in-memory expectation map guarded by a mutex. A `z.Closer` coordinates shutdown across one GC goroutine and ten worker goroutines.

## Persistence Behavior
The harness deletes and recreates `/mnt/drive/badgertest`, writes real Badger data with `SyncWrites(false)`, runs `RunValueLogGC(0.1)` repeatedly, and finally scans persisted data to check value monotonicity after GC activity.

## Dependencies and Integration Points
Depends on public Badger APIs, `net/http/pprof`, `sync/atomic`, `ristretto/z.Closer`, and Badger `y.AssertTruef`. It is meant for manual/integration execution rather than package unit tests.

## Risks and Edge Cases
The hard-coded `/mnt/drive/badgertest` path and destructive `os.RemoveAll` are hazardous outside a controlled environment. The pprof server listens on localhost:8080 without error handling. The random workload is nondeterministic and uses non-cryptographic `math/rand`.

## Test Signals
Provides high-value manual stress coverage for value-log GC under concurrency. It is not automatically run by `go test` unless invoked as a standalone program.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/integration/testgc/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/iterator.go -->
# sources/storage-engines/badger/iterator.go

## Purpose
`iterator.go` implements Badger `Item`, iterator options, and `Iterator` behavior. It is the core read path for scanning MVCC keys across pending writes, memtables, and SST levels while handling value-log pointers, prefetching, versions, deletes, expiry, prefixes, banned namespaces, and reverse iteration.

## Important APIs, Types, and Functions
- `Item`: reusable iterator result with key, value pointer or inline value, version, expiry, metadata, prefetch state, and transaction pointer.
- Item methods: `Key`, `KeyCopy`, `Version`, `Value`, `ValueCopy`, `IsDeletedOrExpired`, `DiscardEarlierVersions`, `EstimatedSize`, `KeySize`, `ValueSize`, `UserMeta`, `ExpiresAt`, `String`.
- Internal item helpers: `yieldItemValue`, `prefetchValue`, `hasValue`, `runCallback`.
- `IteratorOptions`: `PrefetchSize`, `PrefetchValues`, `Reverse`, `AllVersions`, `InternalAccess`, `Prefix`, `SinceTs`, and internal `prefixIsKey`.
- Table filtering: `compareToPrefix`, `pickTable`, `pickTables`.
- `DefaultIteratorOptions`.
- `Iterator`: merge iterator wrapper with item reuse lists, last-key tracking, scan accounting, optional `ThreadId`, and allocator.
- Iterator constructors and methods: `Txn.NewIterator`, `Txn.NewKeyIterator`, `Item`, `Valid`, `ValidForPrefix`, `Close`, `Next`, `Seek`, `Rewind`, plus internal `parseItem`, `fill`, `hasPrefix`, `prefetch`.

## Control Flow and State
`NewIterator` increments transaction iterator count, snapshots pending writes/memtables/level iterators, increments value-log iterator count, and merges all iterators. `Seek` clears prefetched data, sets timestamp-adjusted seek keys, and prefetches. `Next` waits for current item prefetch, recycles it, and parses until a visible item is found. `parseItem` filters internal keys, future versions, `SinceTs`, banned namespaces, duplicate older versions, deletes, and expiry. Reverse iteration has special handling because keys store timestamps descending.

## Persistence Behavior
The iterator does not persist state but reads persisted SST and value-log data. `yieldItemValue` decodes `valuePointer` and reads from `db.vlog`; inline values are copied from `ValueStruct`. `Close` decrements value-log iterator count, which can matter for value-log GC and file lifecycle.

## Dependencies and Integration Points
Integrates with transactions, pending write iterators, memtables, `levelsController.appendIterators`, table merge/concat iterators, value-log reads, namespace banning, metrics, and Badger key/timestamp helpers in `y`. It depends on `table`, `z.Allocator`, `crc32`, `math`, `sort`, `sync`, and `time`.

## Risks and Edge Cases
Items are reused; `Key` and `Value` lifetimes are limited until `Next`, iterator close, or transaction end. Async value prefetch uses goroutines and must be waited on during `Close` to avoid leaks. `yieldItemValue` logs value-log read errors and returns nil error, which can hide corruption from callers. Empty or incorrect prefix handling can over-scan; reverse iteration is particularly subtle around versions and deletes.

## Test Signals
Covered by broad iterator tests in `db_test.go` and focused tests in `iterator_test.go`: prefix/table picking, `SinceTs`, pending writes, read-only empty DB, benchmarked key prefix lookup, reverse iteration, prefetch size, deleted/expired skipping, namespace bans, and concurrent iterator behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/iterator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/iterator_test.go -->
# sources/storage-engines/badger/iterator_test.go

## Purpose
`iterator_test.go` provides focused coverage for iterator table selection, timestamp filtering, prefix/key iteration, read-only empty iteration, and a benchmark for prefix-optimized single-key lookups.

## Important APIs, Types, and Functions
- `tableMock`: minimal `table.TableInterface` for `pickTable`.
- `TestPickTables`: validates prefix overlap logic and a regression involving binary prefixes.
- `TestPickSortTables`: builds real SST tables and validates `IteratorOptions.pickTables` range filtering.
- `TestIterateSinceTs`: writes many keys and asserts iterator versions are at or above `SinceTs`.
- `TestIterateSinceTsWithPendingWrites`: verifies pending transaction writes with version 0 are still visible.
- `TestIteratePrefix`: manual, multi-cache-mode prefix/key iterator coverage.
- `TestIteratorReadOnlyWithNoData`: ensures read-only empty DB iterator construction does not crash.
- `BenchmarkIteratePrefixSingleKey`: measures lookup performance with `Prefix` set for a single key.

## Control Flow and State
The tests mix pure table-range logic, real table construction with `buildTable`, and DB-level write/read flows. Prefix iteration tests use `NewIterator` and `NewKeyIterator`; benchmark setup writes enough keys to produce many SSTables, then repeatedly seeks random keys with prefix filtering.

## Persistence Behavior
Real DB tests persist temporary SST/value-log data and reopen in read-only mode for one scenario. The table-picking tests rely on generated SST table metadata, including smallest/biggest keys and max versions.

## Dependencies and Integration Points
Depends on `IteratorOptions`, table builders, Badger test helpers, `options.OnTableAndBlockRead`, `y.KeyWithTs`, `DB.Ranges`, and filesystem walking for SST counts.

## Risks and Edge Cases
`TestIteratePrefix` is manual, leaving broad prefix counting mostly outside normal CI. Benchmarks are performance signals, not correctness gates. `TestPickSortTables` uses table refs and defers `DecrRef`, so future table refcount changes could affect test setup.

## Test Signals
Strong signal for prefix table pruning and timestamp filtering. Complements `db_test.go` iterator coverage by exercising internal picker functions directly.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/iterator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/key_registry.go -->
# sources/storage-engines/badger/key_registry.go

## Purpose
`key_registry.go` manages Badger data-encryption keys. It persists generated data keys in `KEYREGISTRY`, validates the user storage key through encrypted sanity text, supports key rotation, and rewrites registry files atomically.

## Important APIs, Types, and Functions
- Constants: `KeyRegistryFileName`, `KeyRegistryRewriteFileName`.
- `sanityText`: plaintext used to validate the storage key.
- `KeyRegistry`: synchronized map of `pb.DataKey` by id, `lastCreated`, `nextKeyID`, file pointer, and options.
- `KeyRegistryOptions`: registry directory, read-only flag, storage encryption key, rotation duration, and in-memory mode.
- Lifecycle: `newKeyRegistry`, `OpenKeyRegistry`, `Close`.
- Iteration/read: `keyRegistryIterator`, `newKeyRegistryIterator`, `validRegistry`, `(*keyRegistryIterator).next`, `readKeyRegistry`.
- Persistence: `WriteKeyRegistry`, `storeDataKey`.
- Access/rotation: `DataKey`, `LatestDataKey`.

## Control Flow and State
`OpenKeyRegistry` validates encryption-key length, short-circuits in-memory mode, opens or creates `KEYREGISTRY`, reads existing keys, and keeps the file open for append in read-write mode. `validRegistry` reads IV and sanity text and decrypts it when a storage key exists. `LatestDataKey` returns the current key if it is within the rotation duration, otherwise it generates random key bytes and IV, appends an encrypted protobuf record, updates in-memory state, and returns the plaintext key.

## Persistence Behavior
The registry file layout is IV + sanity text + repeated records of 4-byte length, 4-byte Castagnoli CRC, and marshaled `pb.DataKey`. Data-key bytes are XOR-encrypted with the storage key and per-key IV before writing, then restored in memory. `WriteKeyRegistry` writes a complete temp file (`REWRITE-KEYREGISTRY`), closes it, renames it over `KEYREGISTRY`, and calls `syncDir`.

## Dependencies and Integration Points
Used by Badger encryption paths and value-log/table encryption through data key lookup. Depends on `pb.DataKey`, protobuf marshal/unmarshal, AES block size, random bytes, CRC, Badger `y` crypto/file helpers, and platform `syncDir`.

## Risks and Edge Cases
`storeDataKey` mutates `k.Data` in place while encrypting/decrypting, so error paths must restore plaintext carefully. Map iteration in `WriteKeyRegistry` is nondeterministic, though `readKeyRegistry` reconstructs by key id. Read-only open of a missing registry returns an empty registry. File append in `LatestDataKey` writes but does not explicitly call file sync here.

## Test Signals
`key_registry_test.go` covers build/reopen, rewrite after deletion, storage-key mismatch, encryption/decryption round-trip, and in-memory behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/key_registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/key_registry_test.go -->
# sources/storage-engines/badger/key_registry_test.go

## Purpose
`key_registry_test.go` validates Badger encryption key registry creation, persistence, rewrite, mismatch detection, decryption, and in-memory mode.

## Important APIs, Types, and Functions
- `getRegistryTestOptions`: helper for `KeyRegistryOptions`.
- `TestBuildRegistry`: creates two rotated keys, closes, reopens, and checks both keys are present.
- `TestRewriteRegistry`: creates keys, deletes one from memory, calls `WriteKeyRegistry`, and verifies the rewritten file has one key.
- `TestMismatch`: verifies opening with a different storage key returns `ErrEncryptionKeyMismatch`.
- `TestEncryptionAndDecryption`: checks a generated data key round-trips through disk.
- `TestKeyRegistryInMemory`: verifies in-memory registry can generate multiple keys without disk paths.

## Control Flow and State
Tests generate 32-byte random storage keys, use temp directories, call `OpenKeyRegistry`, force rotation by setting `lastCreated = 0`, and close/reopen as needed. The rewrite test mutates the in-memory map to simulate compaction of registry contents.

## Persistence Behavior
Disk tests verify `KEYREGISTRY` contents survive close/reopen, can be atomically rewritten, and cannot be opened with the wrong storage key. In-memory mode intentionally avoids disk persistence.

## Dependencies and Integration Points
Depends on `crypto/math rand` style random bytes from `math/rand` in this file, `os.MkdirTemp`, `testify/require`, and registry APIs.

## Risks and Edge Cases
Tests do not cover invalid encryption-key lengths, checksum corruption, partial records, concurrent `LatestDataKey`, or read-only registry behavior. The random source is `math/rand`, which is adequate for tests but not representative of production key generation.

## Test Signals
Focused coverage for key-registry persistence and encryption-key validation. Complements DB-level encryption tests in `db_test.go` and `db2_test.go`.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/key_registry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/level_handler.go -->
# sources/storage-engines/badger/level_handler.go

## Purpose
`level_handler.go` manages one LSM level's table set, size accounting, table replacement/deletion, point lookup, iterator construction, and overlap calculations. It is a core part of Badger's levels controller and compaction/read paths.

## Important APIs, Types, and Functions
- `levelHandler`: synchronized table slice, total size, stale size, level number/string, and DB pointer.
- Size/lifecycle: `isLastLevel`, `getTotalStaleSize`, `getTotalSize`, `initTables`, `close`.
- Mutation: `deleteTables`, `replaceTables`, `addTable`, `sortTables`, `tryAddLevel0Table`, `addSize`, `subtractSize`, `decrRefs`.
- Query/read: `numTables`, `getTableForKey`, `get`, `appendIterators`.
- Overlap: `levelHandlerRLocked`, `overlappingTables`.

## Control Flow and State
Level 0 tables are sorted by file id/time and may overlap; newer tables are considered first for reads. Levels >=1 are sorted by smallest key and assumed non-overlapping. Mutations copy or rebuild table slices so iterators can safely keep previous slices. `replaceTables` increments refs for new tables, sorts, unlocks, then decrements removed refs to avoid holding locks during slow close/delete work.

## Persistence Behavior
The handler itself is in-memory, but it owns references to persisted SST files. It must be updated in coordination with manifest changes elsewhere; comments note removed tables should only be dereferenced after manifest updates are durable. Size and stale-size counters reflect table metadata used for compaction decisions.

## Dependencies and Integration Points
Used by `levelsController`, compaction, DB loading, `DB.get`, and iterator construction. Depends on `table.Table`, table iterators, Badger `y` key comparison/hash/metrics helpers, and `IteratorOptions`.

## Risks and Edge Cases
Correctness depends on preserving L0 recency ordering and non-overlap ordering for lower levels. Refcount increments/decrements are critical for safe concurrent iterators and compactions. `getTableForKey` for levels >=1 returns the first table whose biggest key is >= target without explicitly verifying smallest <= key, relying on iterator seek to miss if not contained.

## Test Signals
`TestCompactionFilePicking` directly manipulates level handlers and compaction sort behavior. Many DB/iterator/load tests indirectly cover table replacement, point lookup, iterator appending, and close paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/level_handler.go -->
