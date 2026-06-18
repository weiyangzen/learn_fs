# subset-b-008471 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/DiskQueue.cpp -->
## sources/storage-engines/foundationdb/fdbserver/kvstore/DiskQueue.cpp

### Purpose
`DiskQueue.cpp` implements FoundationDB's `IDiskQueue` durable append/read/pop queue on top of two asynchronously accessed files. It is the low-level persistence log used by the in-memory key-value store and log-system testing paths. The core design is a dynamically resizable two-file ring buffer: one file is logically older, the other is the active append target, and the implementation swaps/truncates/replaces files as data is popped and space can be reclaimed.

### Important APIs, Types, and Functions
The exported entry point is `openDiskQueue(...)`, which returns `DiskQueue_PopUncommitted`, a wrapper around `DiskQueue` that guards against popping data beyond the committed point. `DiskQueue` implements `IDiskQueue` methods: `push`, `pop`, `commit`, `read`, `initializeRecovery`, `readNext`, `getNextReadLocation`, `getNextPushLocation`, `getCommitOverhead`, `dispose`, and `close`. `RawDiskQueue_TwoFiles` owns the two `IAsyncFile` handles, file sizes, popped offsets, page buffers, and file open/truncate/swap logic. `StringBuffer` provides arena-backed aligned append buffers. `SyncQueue` serializes file sync futures so a commit waits for all writes that preceded its sync request. `Tracked<T>` is a local lifetime guard for actors that hold raw object pointers.

### Control Flow
Writes accumulate in `DiskQueue::pushed_page_buffer` as fixed-size 4 KiB pages with a packed `PageHeader`. `push()` copies payload bytes into page payloads, allocating new pages as needed. `commit()` seals the last page by storing the current durable pop point, zero-padding unused payload bytes, computing the page checksum, then delegates to `RawDiskQueue_TwoFiles::pushAndCommit()`. The raw queue serializes push order through `readyToPush`, writes pages to file 1, extends or swaps files if necessary, syncs all touched files, waits for the previous commit, then advances durable popped bytes. Reads use `readPages()` to map logical queue locations to physical file/page offsets and strip page headers back into the byte stream. Recovery starts with `readFirstAndLastPages()`, orders the two files by their first page sequence number, binary-searches the active file for the last valid page, then `readNext()` streams pages until EOF or an invalid page and truncates after the last good page.

### State and Persistence Behavior
The on-disk unit is `DiskQueue::Page`, exactly `_PAGE_SIZE`, with sequence number, popped location, payload size, implementation version, magic, and checksum. Versions select legacy `hashlittle2`, CRC32C, or XXH3 checksums; new queues use V2. The logical byte sequence is monotonic and independent of which file currently stores a page. Durable deletion is represented by committing a page whose `popped` field names the safe pop point; raw file truncation is an optimization after recovery and file swaps. Opening is intentionally strict: both queue files must exist or neither must exist. Creation uses atomic write/create flags followed by sync so recovery only reasons over durable files.

### Dependencies and Integration Points
This file depends on `IDiskQueue.h`, `IAsyncFile`, Flow actors/futures, simulator hooks, `SERVER_KNOBS`, CRC32C, XXHash, and trace/probe infrastructure. It is integrated by `KeyValueStoreMemory.cpp` for mutation-log storage and by any component opening an `IDiskQueue`. It uses `g_network->getDiskBytes()` to report storage availability and simulator `buggify()` paths to exercise truncation, extension, and small-read edge cases.

### Risks
The main correctness risks are around crash recovery, page checksum compatibility, async lifetime, and the historical issue of popping uncommitted data. The code uses raw pointers and self-deleting `dispose`/`close` actors, so `Tracked` coverage is important. Reads can race with overwritten files in simulation and may throw `io_error`. File replacement/truncation is platform-specific, and partial page/header recovery relies on strict checksum and sequence ordering.

### Test Signals
There is a performance test case at the end of the file that opens a V2 queue, recovers it, pushes 10 MB values, reads older locations, pops, and pipelines commits. Numerous `CODE_PROBE`, `ASSERT`, `ASSERT_WE_THINK`, and `buggify()` branches serve as simulation test signals for file swaps, truncation, invalid pages, high page counts, and pop/commit edge cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/DiskQueue.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/FDBExecHelper.cpp -->
## sources/storage-engines/foundationdb/fdbserver/kvstore/FDBExecHelper.cpp

### Purpose
`FDBExecHelper.cpp` provides helper-process execution support for storage snapshot workflows and stores per-storage-engine version information for trace output. It lets FoundationDB invoke an external snapshot command in production-like environments while providing deterministic copy-based behavior under simulation.

### Important APIs, Types, and Functions
`ExecCmdValueString` owns a command value string, parses the first space-delimited token as the binary path, and stores remaining tokens as binary arguments. `spawnProcess(...)` is the platform abstraction for executing a binary and returning an integer status. On Windows, macOS, and Intel compiler builds it is a stub returning success after a yield. On supported Linux-like builds, `fork_child(...)` creates a pipe, forks, redirects child stdout/stderr to the pipe, and calls `execv`. `setupTraceWithOutput(...)` attaches bounded child output to trace events. `execHelper(...)` delegates to `execHelperImpl(...)`, which builds snapshot command arguments. `setDataVersion`, `setDataDurableVersion`, and `printStorageVersionInfo` maintain a map from local `NetworkAddress` to storage UID version/durable-version pairs.

### Control Flow
For non-simulated execution, `execHelperImpl` reads the configured binary path and user arguments, appends FoundationDB-managed arguments such as `--path`, optional `--tlog-spill-path`, `--version`, `--role`, and `--uid`, then awaits `spawnProcess`. In simulation it instead creates a snapshot directory with `/bin/mkdir` and copies the source folder with `/bin/cp -a`; these process calls use deterministic delays to preserve simulator behavior. `spawnProcess` optionally delays async calls in simulation, forks the child, sets the pipe read end nonblocking, loops with `waitpid(..., WNOHANG)`, drains output up to `SERVER_KNOBS->MAX_FORKED_PROCESS_OUTPUT`, handles timeout, and traces nonzero exit or spawn failures.

### State and Persistence Behavior
This file does not persist data directly. Its side effects are external process execution and, in simulation, filesystem directory creation/copying for snapshots. The global `workerStorageVersionInfo` map is process-local state keyed by network address and storage UID. Child output is bounded before entering trace fields, avoiding unbounded trace payloads.

### Dependencies and Integration Points
The implementation depends on Flow futures, tracing, network/simulator globals, `FDB_VT_VERSION`, server knobs, Boost.Process headers where available, and POSIX process APIs on supported platforms. It integrates with storage snapshot callers through `FDBExecHelper.h` and with simulator lifecycle through `destroyChildProcess`, which destroys a simulated child process after a parent close future and resets transport connections.

### Risks
Command parsing is intentionally simple: it splits only on spaces and does not implement shell quoting. The POSIX path passes mutable string buffers into `execv`, so arguments must remain alive until the forked child execs. Timeout handling returns `-1` but does not explicitly kill a long-running child in the shown parent loop. The function writes child output to stdout as well as trace setup, which may be noisy if invoked frequently.

### Test Signals
There is no local `TEST_CASE`. Test signals are simulator-specific branches, trace events such as `SpawnProcessFailure`, `SpawnProcessCommandStatus`, and `SnapDelaySpawnProcess`, plus the storage version tracing functions that can be checked in snapshot-related tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/FDBExecHelper.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/IKeyValueContainer.h -->
## sources/storage-engines/foundationdb/fdbserver/kvstore/IKeyValueContainer.h

### Purpose
`IKeyValueContainer.h` defines the default in-memory ordered key-value container used by `KeyValueStoreMemory`. It wraps `IndexedSet<KeyValueMapPair, uint64_t>` with a small map-like API and tracks per-node byte weights for memory accounting.

### Important APIs, Types, and Functions
`KeyValueMapPair` owns an `Arena`, `KeyRef`, and `ValueRef`. Its constructor deep-copies key and value into the arena sized from `expectedSize()`, and its comparison operators compare only by key. The free `compare` and `operator<` overloads allow `IndexedSet` lookups using compatible key-like types without building a full pair. `IKeyValueContainer` exposes `find`, `begin`, `end`, `lower_bound`, `upper_bound`, `previous`, `erase`, `insert`, bulk `insert`, `sumTo`, and static `getElementBytes`.

### Control Flow
Callers insert by constructing a `KeyValueMapPair`, then pass both the pair and its memory weight into `IndexedSet::insert`. Range clears are simple iterator erases between lower-bound positions. Forward and reverse range reads are implemented by callers using `lower_bound`, `previous`, and iterators; this container itself does not impose FoundationDB read limits or range semantics beyond sorted storage.

### State and Persistence Behavior
All state is process memory held in the private `IndexedSet`. It does not persist independently; durability comes from `KeyValueStoreMemory` replaying logged operations into this container. `sumTo` gives cumulative byte accounting over sorted nodes, and `size()` currently returns a placeholder tuple of zeros rather than forwarding detailed container metrics.

### Dependencies and Integration Points
The only direct include is `flow/IndexedSet.h`, but the type relies on FoundationDB `Arena`, `KeyRef`, `ValueRef`, and `StringRef` definitions transitively. `KeyValueStoreMemory<IKeyValueContainer>` uses it as the normal memory backend, while the radix-tree backend provides an alternative container with a compatible API.

### Risks
Copy and assignment on `IKeyValueContainer` are declared private and unimplemented, preventing accidental expensive copies. The placeholder `size()` may under-report if external callers expect real tuple values. Correct memory accounting depends on passing `pair.arena.getSize() + data.getElementBytes()` consistently during inserts and bulk loads.

### Test Signals
There are no local tests. Coverage is indirect through memory key-value store tests, range read/write behavior, and any tests that compare memory accounting or sequential bulk insert paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/IKeyValueContainer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/IKeyValueStore.cpp -->
## sources/storage-engines/foundationdb/fdbserver/kvstore/IKeyValueStore.cpp

### Purpose
`IKeyValueStore.cpp` implements the central factory `openKVStore(...)`, which maps `KeyValueStoreType` enum values to concrete storage-engine constructors. It is a dispatch layer, not a storage implementation.

### Important APIs, Types, and Functions
The only function defined here is `openKVStore(KeyValueStoreType storeType, std::string const& filename, UID logID, int64_t memoryLimit, bool checkChecksums, bool checkIntegrity, Reference<AsyncVar<ServerDBInfo> const> db, int64_t pageCacheBytes)`. It returns an `IKeyValueStore*` created by one of the backend helpers declared in `IKeyValueStore.h`.

### Control Flow
The function switches on `storeType`. `SSD_BTREE_V1` and `SSD_BTREE_V2` open SQLite-backed stores with version-specific checksum behavior. `MEMORY` opens `keyValueStoreMemory` with the provided memory limit. `SSD_REDWOOD_V1` opens Redwood using database info and page-cache bytes. RocksDB and sharded RocksDB variants dispatch to their respective constructors, with sharded RocksDB receiving checksum and integrity options. `MEMORY_RADIXTREE` reuses `keyValueStoreMemory` but passes extension `"fdr"` and store type `MEMORY_RADIXTREE`.

### State and Persistence Behavior
This file owns no persistent state. Persistence behavior is selected by backend: memory stores use a disk queue log, SQLite/RocksDB/Redwood persist to their own formats, and checksum/integrity flags are forwarded only to backends that support them. The V1 SQLite path intentionally passes `CheckChecksums::False`; V2 forwards the caller's checksum choice.

### Dependencies and Integration Points
It includes `ServerDBInfo`, `IKeyValueStore.h`, and Flow basics. This factory is a high-level integration point used by storage server initialization and tests that need to instantiate a store from configuration.

### Risks
The default case and trailing statement are both `UNREACHABLE`, so adding a new `KeyValueStoreType` requires updating this switch. Backend-specific parameters are uneven by design; for example, `pageCacheBytes` matters for Redwood but not memory, and `checkIntegrity` is ignored by some backends. Wrong dispatch here can silently choose a different on-disk format or extension.

### Test Signals
There are no local tests. Signals come from backend open/recovery tests for each `KeyValueStoreType` and from compile-time exhaustiveness pressure when new enum values are added.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/IKeyValueStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/IPager.cpp -->
## sources/storage-engines/foundationdb/fdbserver/kvstore/IPager.cpp

### Purpose
`IPager.cpp` currently exists to host pager-related unit-test linkage. It includes `IPager.h` and defines a focused checksum corruption test for `ArenaPage`.

### Important APIs, Types, and Functions
The main item is `TEST_CASE("/fdbserver/IPager/ArenaPage/PageContentChecksum")`. It constructs an `ArenaPage`, initializes it with `EncodingType::XXHash64` and `PageType::BTreeNode`, fills the payload with deterministic random bytes, sets write info, runs `preWrite`, corrupts one payload byte, verifies the header with `postReadHeader`, then expects `postReadPayload` to throw `page_decoding_failed`. `forceLinkIPagerTests()` is an empty function used to force this translation unit and its tests to link.

### Control Flow
The test follows the intended page lifecycle: allocate, initialize, mutate payload, stamp physical page/write metadata, pre-write encode/checksum, simulate storage corruption, post-read header verification, and post-read payload verification. The header check should still pass because only payload bytes are corrupted; payload decoding should fail because the XXHash payload checksum no longer matches.

### State and Persistence Behavior
No persistent state is written. The test uses an 8 KiB logical and buffer page size and a random physical page ID. It validates that payload checksums are seeded by physical page ID and catch post-write byte mutation.

### Dependencies and Integration Points
The file depends on `IPager.h`, Flow encryption/random/test utilities, and standard limits. It complements pager implementations by testing the common `ArenaPage` format used by Redwood/DWAL-style page storage.

### Risks
The file defines a local `_PAGE_SIZE` constant in the test because the page abstraction does not expose one, and the comment calls this out. If `ArenaPage` expectations change, this test may lag the implementation. It only covers payload corruption under XXHash64, not header corruption, wrong physical page IDs, deprecated XOR decoding, or multi-page buffers.

### Test Signals
The test itself is the signal. A passing run proves that `postReadPayload` detects payload corruption after `preWrite`, while a failure would indicate broken checksum encoding/decoding or lifecycle ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/IPager.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/IPager.h -->
## sources/storage-engines/foundationdb/fdbserver/kvstore/IPager.h

### Purpose
`IPager.h` defines the common pager interfaces and the `ArenaPage` physical page format used by FoundationDB storage engines such as Redwood/DWAL pager implementations. It specifies page identifiers, event classifications, page encoding/checksum behavior, snapshot reads, and the `IPager2` virtual API.

### Important APIs, Types, and Functions
The header defines `LogicalPageID`, `PhysicalPageID`, `QueueID`, invalid sentinel constants, `PagerEvents`, `PagerEventReasons`, `EncodingType`, and `PageType`. `ArbitraryObject` is a small type-erased ownership hook that can hold a raw pointer or `Reference<T>` with destructor callback. `ArenaPage` owns 4 KiB-aligned arena memory, exposes raw and payload accessors, and implements `init`, `clone`, `getSubPage`, `setWriteInfo`, `setLogicalPageInfo`, `preWrite`, `postReadHeader`, and `postReadPayload`. `IPagerSnapshot` exposes versioned page reads. `IPager2` is the main closable pager interface with allocation, reads, writes, atomic update, free/remap, extent, snapshot, commit, storage accounting, initialization, and oldest-readable-version operations.

### Control Flow
New pages are created by `ArenaPage::init`, which writes `PageHeader`, selects header version 1, computes encoding-header and payload offsets, initializes forensic fields, and exposes the payload region. Before disk write, callers set physical/logical metadata and call `preWrite`; this writes the encoding-specific payload checksum or legacy XOR encoding, then updates the Redwood header checksum over all non-payload bytes. After disk read, callers call `postReadHeader` to validate header checksum and physical page ID, then `postReadPayload` to validate/decode the payload.

### State and Persistence Behavior
The page format is byte-packed and persistent: `PageHeader`, `RedwoodHeaderV1`, optional encoding header, then payload. XXHash64 is the current normal encoding, while deprecated encryption enum values remain reserved for compatibility and old simulation files. `RedwoodHeaderV1` stores page type/subtype/format, first physical page ID, last known logical IDs, write time, write version, and header checksum. `ArenaPage::extra` and `IPagerSnapshot::extra` are runtime-only extension hooks.

### Dependencies and Integration Points
This header depends on FDB client types, Flow futures/errors/arena/reference counting/fast allocation, protocol versioning, encryption utilities, and XXHash. Concrete pagers implement `IPager2`; B-tree and queue code use `ArenaPage` instances as disk payload carriers. The event/reason enums feed page-cache and pager metrics.

### Risks
Persistent enum values and packed header layout are compatibility-sensitive. `ArbitraryObject::destructOnly` does not null fields by itself, so assignment/reset paths must be used carefully to avoid double destruction. Deprecated XOR support is simulation-only and requires `legacyXorWith` to be initialized. `postReadHeader` and `postReadPayload` must be called in the right order; payload access before initialization is unsafe. The `readPage` signature names `PhysicalPageID pageIDs` despite returning by page ID, which may be confusing beside logical/physical remapping APIs.

### Test Signals
The paired `IPager.cpp` unit test checks XXHash payload corruption detection. Additional coverage should come from concrete pager tests exercising commits, snapshots, remap queues, extent handling, old-version retention, and wrong page ID/header checksum failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/IPager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/KeyValueStoreCompressTestData.cpp -->
## sources/storage-engines/foundationdb/fdbserver/kvstore/KeyValueStoreCompressTestData.cpp

### Purpose
`KeyValueStoreCompressTestData.cpp` implements a testing-only `IKeyValueStore` wrapper that compresses simple repeated-byte values before forwarding writes to an underlying store. It exists to simulate much larger logical data sets with less physical disk usage during tests.

### Important APIs, Types, and Functions
`KeyValueStoreCompressTestData` is a final `IKeyValueStore` implementation holding a raw `IKeyValueStore* store`. It forwards lifecycle, type, storage accounting, clear, and commit operations. It overrides `set`, `readValue`, `readValuePrefix`, and `readRange` to pack values on write and unpack values on read. The exported factory is `keyValueStoreCompressTestData(IKeyValueStore* store)`.

### Control Flow
`set` writes the original key and `pack(value)` into the wrapped store. `readValue` awaits the wrapped store and unpacks if present. `readValuePrefix` reads and unpacks the full value, then truncates to `maxLength`. `readRange` reads a range from the wrapped store and rewrites each returned `value` in the result arena after unpacking. `dispose` and `close` forward to the wrapped store and then delete the wrapper.

### State and Persistence Behavior
The wrapper itself has no durable state, but it changes the byte representation stored by the wrapped engine. Empty values stay empty. Values whose first byte is zero, or values not made entirely of one repeated nonzero byte, are stored as a leading zero marker plus original bytes. A repeated nonzero byte string is stored as five bytes: the repeated byte followed by a little-endian `int` count. Reads reconstruct the logical value.

### Dependencies and Integration Points
It includes `IKeyValueStore.h` and can wrap any backend that implements that interface. It is explicitly not customer-facing and is intended for tests that need large logical values without proportional disk use.

### Risks
The encoding uses host `int` layout and unaligned casts, which is acceptable only for this internal test helper. `readValuePrefix` has an "atomic bomb" caveat: it expands the full compressed value before applying the prefix. Malicious or very large repeated values can allocate large buffers on read. The wrapper assumes all data in the underlying store was written through the same pack format.

### Test Signals
There are no local tests. Useful coverage would write empty values, zero-prefixed values, mixed-byte values, repeated nonzero values, range reads, and prefix reads, verifying that logical values round-trip and that storage size shrinks for repeated-byte test data.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/KeyValueStoreCompressTestData.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/KeyValueStoreMemory.cpp -->
## sources/storage-engines/foundationdb/fdbserver/kvstore/KeyValueStoreMemory.cpp

### Purpose
`KeyValueStoreMemory.cpp` implements an `IKeyValueStore` backed by an in-memory ordered container plus an `IDiskQueue` mutation/snapshot log. It provides the normal memory store and the radix-tree memory variant, and it is also used by log-system tests through `keyValueStoreLogSystem`.

### Important APIs, Types, and Functions
`KeyValueStoreMemory<Container>` implements `IKeyValueStore` methods: lifecycle, `getType`, `getSize`, `getStorageBytes`, `set`, `clear`, `commit`, `readValue`, `readValuePrefix`, `readRange`, `resyncLog`, `enableSnapshot`, and `uncommittedBytes`. Internally, `OpType` enumerates log records (`OpSet`, `OpClear`, `OpSnapshotItem`, `OpSnapshotEnd`, `OpSnapshotAbort`, `OpCommit`, `OpRollback`, `OpSnapshotItemDelta`, and others). `OpQueue` buffers uncommitted mutations. `commit_queue`, `log_op`, `recover`, `fullSnapshot`, `snapshot`, and `commitAndUpdateVersions` are the main implementation functions. Factories are `keyValueStoreMemory(...)` and `keyValueStoreLogSystem(...)`.

### Control Flow
Writes go to `queue` unless the transaction is large, in which case they apply directly to `data`. `commit()` waits for recovery, handles replace-content snapshot accounting, either takes a full snapshot for large transactions or applies/logs queued operations, notifies the background snapshot actor of committed bytes, writes `OpCommit`, commits the disk queue, resets transaction counters, and schedules a pop of the previous snapshot region after the disk commit completes. Reads wait for recovery and then use the ordered container for point, prefix, forward range, or reverse range reads.

### State and Persistence Behavior
Durable state is a stream of records in `IDiskQueue`: an `OpHeader`, key bytes, value/range-end bytes, and a one-byte sentinel. Recovery reads records sequentially. `OpCommit` applies the recovery queue to permanent `data`; `OpRollback` discards uncommitted recovery state; short or zero-filled tails are treated as the end unless exact recovery is requested. Snapshot records periodically rewrite the full data set so old log regions can be popped. Snapshot deltas prefix-compress consecutive keys with a one-byte common-prefix length. Memory pressure is tracked through container byte sums, queued mutation bytes, transaction bytes, and a configured memory limit.

### Dependencies and Integration Points
The implementation depends on `IDiskQueue`, `IKeyValueContainer`, `RadixTree`, Flow actors, `NotifiedVersion`, server/client knobs, transaction state debug hooks, and `ServerDBInfo`. `openKVStore` selects this file for `MEMORY` and `MEMORY_RADIXTREE`; the memory backend opens a V2 XXHash disk queue with extension `fdq` or `fdr`.

### Risks
Out-of-space behavior returns `Never()` from `commit` and drops later modifications while unavailable. Large transactions switch mode based on transaction size relative to committed data, which changes when mutations apply to `data`. Recovery uses packed headers and sentinel bytes; malformed lengths can create large reads if not constrained elsewhere. Snapshot correctness depends on the ordering between `notifiedCommittedWriteBytes`, snapshot item writes, and `OpCommit`. `reserved_buffer` is only allocated for the radix-tree path and must be respected by container key extraction.

### Test Signals
There are no local `TEST_CASE`s, but the file is heavily instrumented with trace events and probes: recovery start/complete, skipped zero-fill, exact recovery failure, large transaction mode, many writes at once, full snapshot end, and commit queue size warnings. Indirect tests should cover crash recovery, partial tail repair, snapshot abort/resync, range ordering in both directions, radix-tree mode, sequential commit batching, and memory-limit behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/KeyValueStoreMemory.cpp -->
