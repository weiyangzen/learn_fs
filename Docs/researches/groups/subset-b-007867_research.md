# subset-b-007867 research

Grouped research for SeaweedFS filer stores, metadata replication, remote reads, chunk readers, mount peer registration, SQL generators, and POSIX lock management. Each source file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/foundationdb/foundationdb_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/foundationdb/foundationdb_store.go

## Purpose

`foundationdb_store.go` implements SeaweedFS's filer metadata store on FoundationDB behind the `foundationdb` build tag. It registers `FoundationDBStore` as a filer store, maps file entries into FoundationDB directory subspaces, provides a separate KV subspace, and adds FoundationDB-specific safeguards around transaction size, transaction duration, directory-list limits, and optional write batching.

## Important APIs, Types, and Functions

The exported store surface is the filer store contract: `GetName`, `Initialize`, `BeginTransaction`, `CommitTransaction`, `RollbackTransaction`, `InsertEntry`, `UpdateEntry`, `FindEntry`, `DeleteEntry`, `DeleteFolderChildren`, directory listing methods, `KvPut`, `KvGet`, `KvDelete`, and `Shutdown`. `FoundationDBStore` holds the opened `fdb.Database`, `seaweedfsDir`, `kvDir`, configurable directory prefix, timeout fields, and batching controls.

The private `writeOp` and `writeBatcher` types buffer put/delete operations into FoundationDB transactions. `genKey` packs `(dirPath, fileName)` into the metadata subspace using a pooled `tuple.Tuple`; `extractFileName` unpacks scan keys back to names.

## Control Flow

Initialization sets defaults for cluster file, API version, timeout strings, directory prefix, and disabled-by-default batching, validates durations, calls `fdb.APIVersion`, opens the database, creates/open the metadata and KV directory subspaces, and starts `writeBatcher` only when configured. Entry writes encode attributes and chunks, optionally gzip large chunk lists, reject values larger than the 10 MB FDB transaction limit, then either write into an ambient context transaction, submit through the batcher, or run a one-operation transaction.

Reads use an ambient transaction when present, otherwise `ReadTransact`; not-found nil values are translated to `filer_pb.ErrNotFound`. Listings compute an FDB range over the directory tuple prefix, optionally bracket a filename prefix with `fdb.Strinc`, apply a capped limit, decode each value, and call the filer list callback. `DeleteFolderChildren` intentionally ignores any outer transaction and recursively deletes children in batches of 100 entries using independent transactions.

## State and Persistence Behavior

Metadata is persisted under `directoryPrefix` as tuple keys `(directory, filename)` and encoded `filer.Entry` bytes. Generic KV state is persisted under `directoryPrefix/kv` as tuple-packed byte keys. Context transactions hold uncommitted mutations until explicit commit, but recursive folder deletion is not atomic with a caller transaction. Optional batching preserves durability before returning because `submit(..., wait=true)` waits for the batch transaction result.

## Dependencies and Integration Points

The file depends on Apple's FoundationDB Go bindings, FDB directory layers, tuple packing, SeaweedFS filer entry encoding, and SeaweedFS utility gzip helpers. It integrates with SeaweedFS's store registry, metadata replication/replay through the shared filer store interface, and any component using the filer KV API for offsets or auxiliary state.

## Risks and Edge Cases

FDB's transaction limits drive most risk: a single oversized entry is rejected, and large recursive deletes are reliable but non-atomic. Directory listings are capped to 1000 even when callers pass larger limits, so pagination must be correct. Prefix scans rely on tuple ordering and `Strinc`; malformed keys are skipped with warnings. The context transaction is stored via `context.Value`, so callers must use the returned context. Batcher shutdown closes the stop channel and flushes pending ops, but write latency increases by the configured interval.

## Test Signals

Useful tests cover config parsing, API-version/cluster availability, key round trips, not-found error translation, transaction double-begin/commit/rollback states, batched versus non-batched insert benchmarks, KV benchmarks, and large/nested `DeleteFolderChildren` behavior both inside and outside ambient transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/foundationdb/foundationdb_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/foundationdb/foundationdb_store_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/foundationdb/foundationdb_store_test.go

## Purpose

`foundationdb_store_test.go` exercises and benchmarks the FoundationDB filer store. It is guarded by the same `foundationdb` build tag and skips tests when no local FoundationDB cluster file is available, making it an integration-test suite rather than a pure unit suite.

## Important APIs, Types, and Functions

The tests cover `Initialize`, `initialize`, `GetName`, `genKey`, `extractFileName`, `FindEntry`, `KvGet`, transaction lifecycle methods, `InsertEntry`, `DeleteFolderChildren`, and `ListDirectoryEntries`. Helpers include `getTestClusterFile`, `createBenchmarkStore`, `createBenchmarkStoreWithBatching`, `getTestStore`, and `containsString`.

## Control Flow

Config tests create Viper-backed configuration values, initialize a store, and assert default/custom fields or expected parse failures. Key tests initialize a real store and check tuple key creation for root, nested, spaces, and Unicode paths. Error handling checks missing entry/KV lookups and transaction operations without an active context. Benchmarks pre-create or repeatedly write entries and compare direct commit mode with batched mode, including parallel insert workloads.

The large delete test creates hundreds of entries, then verifies `DeleteFolderChildren` outside a transaction, inside a transaction that is rolled back, and across nested directories. The expected behavior documents the implementation contract: deletions survive the outer rollback because the operation manages its own transactions.

## State and Persistence Behavior

Tests write real metadata and KV state into the configured FoundationDB cluster under the configured directory prefix. Many paths include timestamps to avoid collisions. Benchmark helpers create stores with configurable batching state and a `benchmark` prefix. No cleanup of the entire FDB directory layer is performed, so repeated benchmark runs can leave data unless the backing cluster is reset externally.

## Dependencies and Integration Points

The file depends on an operational FoundationDB service and `FDB_CLUSTER_FILE` or `/var/fdb/config/fdb.cluster`. It integrates with Go's testing/benchmark framework, SeaweedFS filer entry types, and FDB's actual transaction semantics.

## Risks and Edge Cases

Because most tests skip on missing FDB, CI without FoundationDB will not validate this backend. Tests that initialize the same directory prefix can interact with existing data if the cluster is shared. The custom `containsString` wrapper is simple but less idiomatic than `strings.Contains`. The large-delete test intentionally asserts non-atomic behavior, which is important because future refactors may otherwise try to make it transactional and reintroduce FDB transaction-limit failures.

## Test Signals

Strong signals are successful initialization against a real cluster, correct not-found errors, transaction state errors, key unpacking for Unicode and spaces, no entries remaining after large deletes, and benchmark deltas between batching modes under serial and parallel insertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/foundationdb/foundationdb_store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/gateway_upload.go -->
# sources/distributed-fs/seaweedfs/weed/filer/gateway_upload.go

## Purpose

`gateway_upload.go` factors shared gateway upload behavior into a reusable helper that uploads an `io.Reader` as one SeaweedFS chunk and returns the corresponding `filer_pb.FileChunk`. It is designed for NFS, WebDAV, filer gateway paths, and future gateway integrations that need common chunk assignment/upload semantics.

## Important APIs, Types, and Functions

`GatewayChunkUploader` is a small interface satisfied by `operation.Uploader`, making uploads mockable without importing the full operation package in callers. `GatewayChunkUploadRequest` carries filer client, optional uploader, reader, logical path, filename, offset, timestamp, assign-placement options, upload options, and volume-server access mode. `SaveGatewayDataAsChunk` is the main helper; `lastSlashIndex` is a local filename fallback helper.

## Control Flow

The helper rejects nil filer clients and readers, constructs a default uploader when one is not supplied, derives `Filename` from the final `FullPath` segment, creates `operation.UploadOption`, and defines a URL generator. In normal mode it emits `http://host/fileId`; in `filerProxy` mode with `FilerHTTPAddress`, it emits a proxy URL carrying `proxyChunkId`. It then builds an `AssignVolumeRequest`, calls `UploadWithRetry`, validates the returned upload result, and converts it to a protobuf file chunk using the requested offset and timestamp.

## State and Persistence Behavior

The file itself holds no persistent state. Persistence happens through the filer assignment RPC and subsequent volume-server upload performed by the uploader. The returned `FileChunk` is not installed into any filer entry here; callers must update metadata separately. This keeps the helper single-purpose and avoids hidden entry mutations.

## Dependencies and Integration Points

The code depends on `operation.NewUploader`, `operation.UploadOption`, `operation.UploadResult`, and `filer_pb.FilerClient`/`AssignVolumeRequest`. It integrates with gateway write paths that already know the logical file path and later call filer entry update APIs.

## Risks and Edge Cases

`VolumeServerAccess` only has special behavior for `filerProxy` when `FilerHTTPAddress` is non-empty; other values currently fall back to direct host URLs. A nil `UploadResult` or non-empty result error is treated as failure even if no Go error is returned. Filename derivation for trailing slashes falls back to the whole path. The helper reads through `UploadWithRetry`; short reads or content-length issues are delegated to the uploader implementation.

## Test Signals

Mock uploader tests should cover nil client/reader errors, default filename derivation, explicit filename, proxy URL generation, assign request fields, upload errors, upload-result errors, nil results, and returned chunk offset/timestamp correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/gateway_upload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/hbase/hbase_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/hbase/hbase_store.go

## Purpose

`hbase_store.go` implements SeaweedFS filer metadata storage on HBase. It registers `HbaseStore`, creates or verifies the target table with metadata and KV column families, and stores filer entries as encoded bytes keyed by full path.

## Important APIs, Types, and Functions

`HbaseStore` contains a gohbase client, table bytes, KV family name, metadata family name, and column qualifier. It implements the filer store CRUD/list interface with `Initialize`, `InsertEntry`, `UpdateEntry`, `FindEntry`, `DeleteEntry`, `DeleteFolderChildren`, `ListDirectoryEntries`, `ListDirectoryPrefixedEntries`, no-op transaction methods, and `Shutdown`.

## Control Flow

Initialization opens a gohbase client, sets family names (`kv`, `meta`) and column `a`, probes the table, and creates it via an admin client if HBase reports `TableNotFound`. Entry insertion encodes attributes/chunks, gzips large chunk lists, and writes to the metadata family with optional HBase TTL. Reads fetch the row from the metadata family, translate `filer.ErrKvNotFound` to `filer_pb.ErrNotFound`, and decode the entry.

Listing uses `NewScanRange` from `dirPath.Child(prefix)` with no explicit stop row, then breaks when returned rows no longer have the expected prefix. Each row is filtered so only direct children of the requested directory are returned. Delete-folder-children scans the same prefix and deletes only direct children, not arbitrary descendants.

## State and Persistence Behavior

Metadata rows are stored under row key `entry.FullPath`, family `meta`, qualifier `a`. Generic KV rows use family `kv` in `hbase_store_kv.go`. Entry TTL is forwarded to HBase puts when positive, using HBase's TTL option. Transactions are no-ops, so multi-step filer operations are not atomic at this layer.

## Dependencies and Integration Points

The file depends on `github.com/tsuna/gohbase`, HBase scanner semantics, SeaweedFS filer entry encoding, and SeaweedFS store registration. It integrates with HBase table administration during startup and the shared filer store interface used by metadata replay and normal filer RPCs.

## Risks and Edge Cases

Scans have no upper stop row and rely on prefix checks to stop. `DeleteFolderChildren` only deletes direct children, so recursive semantics depend on higher layers if needed. HBase durability is set by the lower helper to `AsyncWal`, trading safety for performance. `FindEntry` maps non-not-found read errors through unchanged except for `filer.ErrKvNotFound`; caller behavior should be checked for transient HBase failures.

## Test Signals

Validation should cover table auto-creation, insert/find/delete, TTL propagation, list prefix and start-file behavior, direct-child filtering, scanner close behavior, and failure modes for missing tables or HBase connectivity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/hbase/hbase_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/hbase/hbase_store_kv.go -->
# sources/distributed-fs/seaweedfs/weed/filer/hbase/hbase_store_kv.go

## Purpose

`hbase_store_kv.go` provides the HBase-backed generic KV operations used by the filer for auxiliary state such as metadata replication offsets. It also centralizes HBase put/get/delete helpers for both KV and metadata families.

## Important APIs, Types, and Functions

The public methods are `KvPut`, `KvGet`, and `KvDelete`. Shared helpers are `doPut`, `doPutWithOptions`, `doGet`, and `doDelete`. `COLUMN_NAME` defines the single qualifier `a` used in each family.

## Control Flow

`KvPut` calls `doPut` with family `kv` and no TTL. `doPut` chooses HBase options: `AsyncWal` always, plus `TTL` when `ttlSecond > 0`. `doPutWithOptions` builds a nested family/qualifier value map and calls gohbase `Put`. `doGet` builds a family-restricted `Get`, returns the first cell value, and maps empty results to `filer.ErrKvNotFound`. `doDelete` builds a qualifier-specific delete and sends it with async WAL durability.

## State and Persistence Behavior

KV values are stored in the same HBase table as metadata but under the `kv` column family. Metadata helper calls use the `meta` family and may apply TTL from the entry. All writes use async WAL durability, so acknowledged writes may be more exposed to region-server failure than fully synced WAL writes.

## Dependencies and Integration Points

The code depends on gohbase `hrpc` request builders and the `HbaseStore` table/client fields. It is used by the HBase metadata store and by filer components that call `FilerStore.Kv*`, including replication offset storage.

## Risks and Edge Cases

`doGet` uses `context.Background()` instead of the caller's context when constructing the HBase get, so cancellation/deadline propagation is incomplete for reads. It returns only the first cell and assumes one qualifier. Empty value and missing key are indistinguishable for callers because empty cell sets yield `ErrKvNotFound`.

## Test Signals

Tests should cover put/get/delete round trips, not-found mapping, caller context cancellation behavior, TTL option behavior for metadata puts, and HBase failures from each RPC path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/hbase/hbase_store_kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/interval_list.go -->
# sources/distributed-fs/seaweedfs/weed/filer/interval_list.go

## Purpose

`interval_list.go` implements a generic, locked interval list used to model visible byte ranges and overwritten write regions. It keeps ordered half-open intervals with timestamps and value payloads that can be cloned and retargeted when intervals split.

## Important APIs, Types, and Functions

`IntervalValue` requires `SetStartStop` and `Clone`. `Interval[T]` stores `StartOffset`, `StopOffset`, `TsNs`, `Value`, and linked-list pointers. `IntervalList[T]` has sentinel head/tail nodes and an `RWMutex`. Public methods include `NewIntervalList`, `Front`, `AppendInterval`, `Overlay`, `InsertInterval`, and `Len`; private methods implement ordered insertion, splitting, and overwrite behavior.

## Control Flow

`Overlay` inserts a new interval by replacing all overlapping visible ranges regardless of timestamp. It finds the first interval ending after the new start and the last interval starting before the new stop, preserves left/right fragments around the overlay, and splices the new interval between them. `InsertInterval` is timestamp-aware: newer intervals split or replace older overlaps, while older intervals are inserted only into gaps not covered by newer ranges.

`insertInterval` iterates through the ordered list while the candidate still has uncovered range. It clones values for left/right fragments, calls `SetStartStop` when fragment boundaries change, and uses `insertBetween` to preserve list links.

## State and Persistence Behavior

The structure is in-memory only. It persists no data beyond the process and is protected by the list mutex for modifications and length calculation. `Front` returns an internal pointer without locking, so callers must coordinate if concurrent mutation is possible.

## Dependencies and Integration Points

The file depends only on `math` and `sync`. It integrates with SeaweedFS filer chunk visibility/read paths, where intervals represent file chunk views and overwrite generations.

## Risks and Edge Cases

Pointer/link correctness is critical because sentinels are partly linked lazily. `Overlay` reuses existing `Value` pointers for preserved fragments, while `InsertInterval` clones values for fragments, so value mutability semantics differ. Zero-length overlays are ignored, but zero/negative `InsertInterval` input is not explicitly rejected. `Len` counts from head and subtracts one, so broken links could hide corruption.

## Test Signals

Tests should exercise overlapping left/right splits, complete replacement, timestamp ordering, adjacent intervals, zero-length input, struct payload clone behavior, and concurrent access patterns where callers hold the appropriate lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/interval_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/interval_list_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/interval_list_test.go

## Purpose

`interval_list_test.go` validates the interval overlay and timestamp-aware insertion algorithms with many boundary combinations. It documents expected segment counts for overwrites and timestamp precedence.

## Important APIs, Types, and Functions

The file defines `IntervalInt` and `IntervalStruct` as test payloads satisfying `IntervalValue`. Test functions cover `Overlay` cases 1 through 11, `InsertInterval` cases 1 through 11, and struct payload insertion.

## Control Flow

Each test builds a new list, applies ordered operations, prints the resulting ranges for human debugging, and asserts final list length. Overlay tests cover full cover, left and right partial cover, same start/end, adjacent writes, and ignored zero-length overlay. Insert tests cover older/newer interval interactions, gaps, and splitting around existing intervals.

## State and Persistence Behavior

All state is in-memory and local to each test. The tests do not validate persistent side effects. `IntervalStruct.SetStartStop` has a value receiver, so it does not mutate the struct in the test; this limits coverage for payload boundary mutation.

## Dependencies and Integration Points

The tests use `stretchr/testify/assert` and the interval list APIs in the filer package. They indirectly cover reader/chunk-view behavior that depends on interval ordering.

## Risks and Edge Cases

The tests assert mostly counts rather than exact interval boundaries, and many tests print to stdout instead of using structured assertions. This can miss value aliasing, incorrect timestamp assignment, or wrong start/stop values if the number of intervals is unchanged.

## Test Signals

Useful added signals would assert exact interval sequences, payload start/stop mutation, clone identity, zero-length insert behavior, and race detection under representative read/write locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/interval_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb/leveldb_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/leveldb/leveldb_store.go

## Purpose

`leveldb_store.go` implements the original single-LevelDB filer metadata store. It persists entries in one local LevelDB database, supports direct CRUD/listing, offers a batch insert helper, and exposes a debug dump of stored keys.

## Important APIs, Types, and Functions

`LevelDBStore` wraps `*leveldb.DB` and implements the filer store methods plus `BatchInsertEntries`, `Shutdown`, and `Debug`. Helper functions `genKey`, `genDirectoryKeyPrefix`, and `getNameFromKey` encode keys as `dirPath + 0x00 + fileName`. The store also satisfies `filer.Debuggable`.

## Control Flow

Initialization creates the configured directory, verifies writability, opens LevelDB with larger cache/write buffers and a Bloom filter, and recovers corrupted DBs when possible. Inserts encode/gzip entry metadata and write by key. Reads fetch by key and translate `leveldb.ErrNotFound` to `filer_pb.ErrNotFound`. Listing seeks to either the directory prefix or the start filename, stops when the prefix no longer matches, applies include-start and limit logic, decodes entries, and invokes the callback.

`DeleteFolderChildren` scans direct keys with the directory prefix and writes a single LevelDB batch delete. `BatchInsertEntries` encodes multiple entries into one LevelDB write batch for bulk operations.

## State and Persistence Behavior

All metadata and KV data share the same LevelDB keyspace because KV operations in the companion file use raw caller keys. Entry keys include a null separator to preserve directory grouping. Transactions are no-ops, so multi-operation atomicity is limited to explicit LevelDB batches such as `BatchInsertEntries` and `DeleteFolderChildren`.

## Dependencies and Integration Points

The file depends on `goleveldb`, SeaweedFS filer entry encoding, gzip helpers, and local filesystem permissions. It integrates with embedded/single-node filer deployments and tests that instantiate `filer.NewFiler` with a local store.

## Risks and Edge Cases

KV raw keys can collide with metadata keys if callers choose keys that look like `dir 
name`. Delete-folder batching can become large for huge directories. Iterator errors are not checked after `Release`, so low-level iteration failures may be missed. `getNameFromKey` assumes a separator exists; malformed keys return the whole key after index underflow behavior is avoided by loop termination at -1.

## Test Signals

Tests should cover create/find/list root and nested paths, empty root, batch insert atomicity, large directory deletion, debug output, corruption recovery, iterator error handling, and KV/metadata keyspace collision assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb/leveldb_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb/leveldb_store_kv.go -->
# sources/distributed-fs/seaweedfs/weed/filer/leveldb/leveldb_store_kv.go

## Purpose

`leveldb_store_kv.go` adds generic KV operations to the single-LevelDB filer store. It lets shared filer components persist auxiliary byte values in the same local LevelDB database.

## Important APIs, Types, and Functions

The methods are `KvPut`, `KvGet`, and `KvDelete` on `LevelDBStore`. They call LevelDB `Put`, `Get`, and `Delete` directly and wrap errors with operation-specific context. Missing keys become `filer.ErrKvNotFound`.

## Control Flow

Each KV call uses the caller-provided raw byte key without transformation. `KvGet` checks `leveldb.ErrNotFound` before wrapping other errors. Put and delete return nil on successful LevelDB writes.

## State and Persistence Behavior

KV bytes are persisted in the same LevelDB keyspace as metadata entries. Values are stored exactly as provided, without compression, TTL, namespacing, or transaction support.

## Dependencies and Integration Points

The file depends on `goleveldb` and the filer KV error contract. It is used by metadata replication offsets, caches, and other filer subsystems that only need byte-key/byte-value persistence.

## Risks and Edge Cases

The absence of a KV namespace means accidental key collisions with file metadata are possible unless callers use disciplined key prefixes. Empty values are valid because not-found is detected by LevelDB error, not value length. Deletes of missing keys are treated as successful by LevelDB.

## Test Signals

KV round-trip, overwrite, delete, missing-key, empty-value, binary-key, and collision-prefix tests would validate the intended contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb/leveldb_store_kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb/leveldb_store_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/leveldb/leveldb_store_test.go

## Purpose

`leveldb_store_test.go` tests the single-LevelDB store through a real `filer.Filer`, ensuring basic create/find/list behavior and empty-root handling. It also benchmarks direct store insertion.

## Important APIs, Types, and Functions

The file covers `LevelDBStore.initialize`, `filer.NewFiler`, `SetStore`, `CreateEntry`, `FindEntry`, `ListDirectoryEntries`, and direct `InsertEntry` in `BenchmarkInsertEntry`.

## Control Flow

`TestCreateAndFind` creates a temp LevelDB directory, attaches it to a filer, creates a nested file, finds it, lists the containing directory, and lists root to verify parent directory creation behavior. `TestEmptyRoot` verifies an empty store lists no root children. The benchmark writes generated `/fileN.txt` entries with current timestamps.

## State and Persistence Behavior

Each test uses `t.TempDir`, so LevelDB state is isolated and removed after the test. Tests exercise filer-level parent directory metadata creation in addition to raw store persistence.

## Dependencies and Integration Points

The tests depend on the SeaweedFS filer orchestration layer, protobuf server discovery stubs, and local filesystem LevelDB storage. They validate the store as used by filer entry APIs rather than only direct store calls.

## Risks and Edge Cases

The tests do not call `Shutdown` explicitly in all paths, so resource cleanup relies on process teardown for some DB handles. Assertions are limited to counts and full path equality; encoded attributes, chunk metadata, deletes, and KV behavior are not covered.

## Test Signals

Useful signals include successful nested create/find, root parent listing count, empty-root no-error result, and insert benchmark allocation/throughput data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb/leveldb_store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb/object_size_metric_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/leveldb/object_size_metric_test.go

## Purpose

`object_size_metric_test.go` verifies that filer object-size metrics are recorded when new file entries are created with the LevelDB store. It guards the user-facing Prometheus histogram behavior rather than LevelDB internals.

## Important APIs, Types, and Functions

`histogramState` snapshots `stats.FilerObjectSizeBytesHistogram`. `TestCreateEntryRecordsObjectSize` uses `filer.CreateEntry` with files and a directory, then inspects histogram sample counts and buckets.

## Control Flow

The test initializes a temp LevelDB-backed filer, captures histogram state, creates a small file, a 5 MB file, a directory, and then overwrites the small file. It expects only the two new file creates to increment the histogram and checks that they landed in expected bucket ranges.

## State and Persistence Behavior

The histogram is global process state, so the test compares before/after counts rather than expecting an empty histogram. File metadata is persisted only in a temp LevelDB directory. Directory creation and overwrite update the store but should not count as new object-size samples.

## Dependencies and Integration Points

The file depends on Prometheus DTO metric encoding, SeaweedFS `stats`, the filer create path, and LevelDB as a concrete store. It validates metrics integration at the filer layer.

## Risks and Edge Cases

Global metric state can be affected by other tests running in the same process. Bucket assertions are cumulative, so they check lower bounds rather than exact placement. The test assumes the create path distinguishes new files from directories and overwrites.

## Test Signals

Signals are a sample-count delta of two, one <=1024-byte bucket increment for the small file, and one object in the 1 MB to 100 MB cumulative range for the 5 MB file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb/object_size_metric_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb2/leveldb2_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/leveldb2/leveldb2_store.go

## Purpose

`leveldb2_store.go` implements a sharded local LevelDB filer store. It spreads directories across a fixed number of LevelDB databases by MD5 hash, improving write/read concurrency and reducing single-DB hot spots compared with the original LevelDB store.

## Important APIs, Types, and Functions

`LevelDB2Store` holds `dbs`, `dbCount`, and `ReadOnly`. It implements standard filer store methods. Helpers `genKey`, `genDirectoryKeyPrefix`, `getNameFromKey`, and `hashToBytes` encode keys as `md5(directory) + filename` and derive partition ID from the last hash byte.

## Control Flow

Initialization creates the root directory, checks writability, and opens `dbCount` subdirectories named `00`, `01`, etc. with Bloom filters, cache settings, and optional read-only mode. Each metadata operation hashes the directory to choose one partition, then operates within that LevelDB. Listing and child deletion only scan the partition for that directory hash, so all names in a directory remain colocated and sorted by filename suffix.

## State and Persistence Behavior

Metadata is persisted across multiple LevelDB folders. The key no longer stores the directory string, only its MD5 digest plus filename, so collisions are theoretically possible but unlikely. Transactions are no-ops; deletes for one directory use a batch within one partition.

## Dependencies and Integration Points

The file depends on `goleveldb`, MD5 hashing, local filesystem storage, SeaweedFS entry encoding, and the filer store registry. It is suitable for local filer deployments that want directory-level sharding without a remote database.

## Risks and Edge Cases

Changing `dbCount` after data exists changes partition mapping and makes existing entries unreachable. MD5 hash collisions would merge directory keyspaces. `ReadOnly` still calls `MkdirAll`/writability checks during initialization. Iterator errors are not inspected after release. Large single-directory deletes can create large write batches.

## Test Signals

Tests should cover create/find/list with multiple partitions, stable hashing for a fixed db count, read-only initialization behavior, delete-folder children in one partition, and failure when db count changes across restarts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb2/leveldb2_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb2/leveldb2_store_kv.go -->
# sources/distributed-fs/seaweedfs/weed/filer/leveldb2/leveldb2_store_kv.go

## Purpose

`leveldb2_store_kv.go` adds generic KV operations to the sharded LevelDB2 store. It distributes KV keys across the same fixed set of databases by using the last byte of the raw key.

## Important APIs, Types, and Functions

The public methods are `KvPut`, `KvGet`, and `KvDelete`. `bucketKvKey` maps a key to `int(key[len(key)-1]) % dbCount`.

## Control Flow

Each method derives the partition from the raw key, then performs a LevelDB put/get/delete in that partition. Missing keys map to `filer.ErrKvNotFound`; other errors include the partition number in the message.

## State and Persistence Behavior

KV state is spread across the same LevelDB partitions as metadata, but partitioning is by last key byte rather than directory hash. Values are stored as raw bytes without compression or TTL.

## Dependencies and Integration Points

The file depends on LevelDB2's opened partition slice and the filer KV contract. It supports metadata offset and other auxiliary state for LevelDB2-backed filers.

## Risks and Edge Cases

`bucketKvKey` panics on an empty key because it indexes `key[len(key)-1]`. Distribution depends entirely on the last byte, so structured keys with a constant suffix can hot-spot one DB. KV keys can collide with metadata keys within a partition if prefixes are not disciplined.

## Test Signals

Tests should include binary KV round trips across multiple suffixes, missing keys, empty-key rejection or panic behavior, partition distribution, and collision assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb2/leveldb2_store_kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb2/leveldb2_store_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/leveldb2/leveldb2_store_test.go

## Purpose

`leveldb2_store_test.go` validates basic filer behavior on the sharded LevelDB2 store. It mirrors the single-LevelDB smoke tests while initializing two database partitions.

## Important APIs, Types, and Functions

The tests call `LevelDB2Store.initialize`, `filer.NewFiler`, `SetStore`, `CreateEntry`, `FindEntry`, and `ListDirectoryEntries`.

## Control Flow

`TestCreateAndFind` creates a nested file through the filer, verifies it can be found, lists the containing directory, and verifies the root listing contains one top-level child. `TestEmptyRoot` ensures listing root in a fresh store returns no entries and no error.

## State and Persistence Behavior

Temp directories isolate the two LevelDB partition folders per test. The tests exercise partition selection indirectly through path hashing but do not assert which partition is used.

## Dependencies and Integration Points

The file depends on SeaweedFS filer behavior and local LevelDB storage. It verifies that LevelDB2 satisfies the same basic contract as LevelDB.

## Risks and Edge Cases

Coverage is shallow: no delete, KV, partition distribution, read-only mode, db-count migration, or hash collision behavior is tested. Assertions focus on counts and path identity.

## Test Signals

The key signals are successful nested create/find, correct one-entry listings for parent and root, and empty-root behavior with a two-partition store.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb2/leveldb2_store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb3/leveldb3_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/leveldb3/leveldb3_store.go

## Purpose

`leveldb3_store.go` implements a bucket-aware local LevelDB filer store. It stores normal metadata in a default LevelDB and maps S3 bucket contents under `/buckets/<bucket>/...` into separate per-bucket LevelDB databases so whole buckets can be opened, closed, or dropped independently.

## Important APIs, Types, and Functions

`LevelDB3Store` holds the root directory, a map of database name to `*leveldb.DB`, a lock guarding the map, and `ReadOnly`. Store methods mirror LevelDB2. `findDB`, `createDB`, and `closeDB` manage bucket database selection. Key helpers use `md5(directory) + filename` within the selected DB.

## Control Flow

Initialization opens the default `_main` database. `findDB` returns default DB for paths outside `/buckets/`; for bucket paths it extracts the bucket name, rewrites the path to the bucket-local short path, and lazily creates the bucket DB if needed. CRUD/list/delete operations call `findDB`, encode/decode entries, and operate on the chosen DB. Deleting folder children at a bucket root closes and removes the entire bucket DB directory; otherwise it scans and batch-deletes direct children in the selected DB.

## State and Persistence Behavior

The store persists metadata in one LevelDB folder per bucket plus `_main`. Bucket-local keys use short paths, while entries retain full SeaweedFS paths when decoded for callers. Transactions are no-ops. Whole-bucket deletion removes a filesystem directory with `os.RemoveAll` after closing the DB.

## Dependencies and Integration Points

The file depends on LevelDB, filesystem directories, MD5 hashing, SeaweedFS bucket path conventions, and `filer.BucketAware` implemented in the companion bucket file. It integrates with S3 bucket lifecycle paths that can notify the store about bucket creation/deletion.

## Risks and Edge Cases

Bucket name extraction depends on `/buckets/` path shape. `findDB` may create a bucket DB during reads/listing for a missing bucket. Whole-bucket deletion uses `RemoveAll`, so incorrect bucket names or root paths would be destructive. Changing the path convention or hash algorithm would make existing data unreachable. Iterator errors are not checked after release.

## Test Signals

Needed tests include normal and bucket path CRUD, lazy bucket DB creation, whole-bucket drop, concurrent `findDB`/`createDB`, listing path rewrites, and behavior for `/buckets/<bucket>` with and without children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb3/leveldb3_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb3/leveldb3_store_bucket.go -->
# sources/distributed-fs/seaweedfs/weed/filer/leveldb3/leveldb3_store_bucket.go

## Purpose

`leveldb3_store_bucket.go` provides the bucket lifecycle hooks for `LevelDB3Store`, making it explicitly implement SeaweedFS's `filer.BucketAware` interface.

## Important APIs, Types, and Functions

The file declares the interface assertion and implements `OnBucketCreation`, `OnBucketDeletion`, and `CanDropWholeBucket`.

## Control Flow

Bucket creation calls `createDB(bucket)` to ensure the per-bucket LevelDB is opened. Bucket deletion closes the DB if present, then removes the bucket directory from the store root. `CanDropWholeBucket` returns true, advertising that the store can cheaply delete all metadata for a bucket as a unit.

## State and Persistence Behavior

Creation opens or creates a persistent LevelDB folder named after the bucket. Deletion removes that folder recursively. The default `_main` DB is unaffected.

## Dependencies and Integration Points

The hooks are called by higher-level bucket lifecycle code through `filer.BucketAware`. They depend on `leveldb3_store.go` map locking and DB loading/closing behavior.

## Risks and Edge Cases

The deletion path guards only against an empty bucket string; bucket names with path separators or unexpected characters rely on upstream validation. `RemoveAll` is irreversible at the filesystem level. Errors from `createDB` in `OnBucketCreation` are ignored because the interface has no return value.

## Test Signals

Tests should verify interface implementation, DB map changes on create/delete, on-disk directory removal, empty bucket no-op behavior, and upstream validation of bucket names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb3/leveldb3_store_bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb3/leveldb3_store_kv.go -->
# sources/distributed-fs/seaweedfs/weed/filer/leveldb3/leveldb3_store_kv.go

## Purpose

`leveldb3_store_kv.go` implements generic KV operations for LevelDB3. Unlike metadata, all KV data is kept in the default `_main` database rather than per-bucket databases.

## Important APIs, Types, and Functions

The methods are `KvPut`, `KvGet`, and `KvDelete` on `LevelDB3Store`. They operate directly on `store.dbs[DEFAULT]`.

## Control Flow

Each method performs a raw LevelDB operation. `KvGet` maps `leveldb.ErrNotFound` to `filer.ErrKvNotFound`; other errors are wrapped. Put and delete return wrapped errors on failure.

## State and Persistence Behavior

KV state persists in `_main`, shared with non-bucket metadata. It is not dropped when individual bucket databases are deleted, which is important for global filer state such as replication offsets.

## Dependencies and Integration Points

The file depends on the default DB having been opened by `initialize`. It supports filer subsystems that require byte-key persistence independently of bucket metadata.

## Risks and Edge Cases

If `_main` is missing from the map due to failed initialization or shutdown races, these methods can panic. Raw KV keys can collide with default metadata keys if not namespaced. There is no transaction or TTL support.

## Test Signals

Tests should cover KV persistence before/after bucket deletion, missing key mapping, binary keys, empty values, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb3/leveldb3_store_kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb3/leveldb3_store_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/leveldb3/leveldb3_store_test.go

## Purpose

`leveldb3_store_test.go` provides basic filer smoke tests for the bucket-aware LevelDB3 store. It verifies that the store still satisfies normal filer create/find/list behavior outside bucket-specific paths.

## Important APIs, Types, and Functions

The tests call `LevelDB3Store.initialize`, `filer.NewFiler`, `SetStore`, `CreateEntry`, `FindEntry`, and `ListDirectoryEntries`.

## Control Flow

`TestCreateAndFind` creates a nested file, finds it, lists its parent, and lists root. `TestEmptyRoot` initializes a fresh store and verifies root listing is empty.

## State and Persistence Behavior

Each test uses a temp root directory and the default `_main` DB. Bucket DB creation/deletion is not exercised.

## Dependencies and Integration Points

The tests depend on local LevelDB and the SeaweedFS filer layer. They ensure the LevelDB3 implementation remains compatible with generic filer operations.

## Risks and Edge Cases

The suite does not test the primary LevelDB3 differentiator: per-bucket DB routing and whole-bucket deletion. It also omits KV, concurrent DB creation, and path rewrite checks.

## Test Signals

Signals are successful nested create/find, one-entry parent/root listings, and empty root behavior using the default database.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/leveldb3/leveldb3_store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/meta_aggregator.go -->
# sources/distributed-fs/seaweedfs/weed/filer/meta_aggregator.go

## Purpose

`meta_aggregator.go` implements live metadata aggregation among filer peers. It subscribes to remote filer local metadata streams, stores received events in an in-memory aggregate log buffer for clients, optionally replays changes into the local store when filers do not share the same store signature, and persists per-peer offsets in the filer KV store.

## Important APIs, Types, and Functions

`MetaAggregator` holds the local filer, self address, gRPC dial option, aggregate `LogBuffer`, peer subscription stop channels, and listener condition state. Key methods are `NewMetaAggregator`, `OnPeerUpdate`, `HasRemotePeers`, `HasPeer`, `loopSubscribeToOneFiler`, `doSubscribeToOneFiler`, `traversePeerMetadata`, `readFilerStoreSignature`, `readOffset`, and `updateOffset`. `GetPeerMetaOffsetKey` formats KV keys for peer signatures, and `filerClient` adapts a gRPC client to lookup functions.

## Control Flow

Peer updates add or remove subscription goroutines. Each subscription loop reconnects from the last timestamp and sleeps between failures. On first contact with a peer with a different store signature, the aggregator reads the saved offset; if absent, it performs a full BFS metadata traversal excluding system logs, inserts newer peer entries, then starts streaming from one minute before the traversal start to cover clock skew and concurrent changes.

During streaming, the code subscribes with batching and metadata chunk support, accumulates `LogFileRefs`, decodes referenced persisted logs via `pb.ReadLogFileRefs`, processes direct and batched events, writes every event to `MetaLogBuffer`, calls `Replay` when replication is needed, notifies local filer listeners, and periodically persists offsets.

## State and Persistence Behavior

The aggregate log buffer is in-memory and not re-persisted to disk. Durable state is the per-peer last timestamp stored via `FilerStore.KvPut` under a key derived from peer store signature. Replicated metadata is persisted through the local filer store. Peer subscription state and listener wait counts are process-local.

## Dependencies and Integration Points

The file depends on SeaweedFS master cluster updates, filer gRPC clients, protobuf metadata events, log buffers, metadata replay, persisted log refs, chunk stream readers, and the filer store KV API. It is central to multi-filer metadata convergence and client metadata subscriptions.

## Risks and Edge Cases

Offset keys are based only on peer signature, so signature uniqueness matters. Bootstrap traversal uses entry mtime to resolve insert conflicts but stream timestamps to resume, which is deliberate but easy to confuse. Replaying events can duplicate work, relying on upsert/delete idempotence. Subscription errors loop forever. Listener broadcast only happens when waiters exist. A peer with the same store signature is aggregated for clients but not replayed into the same shared store.

## Test Signals

Tests should cover peer add/remove cancellation, `HasPeer`, first-sync traversal and offset write, offset resume, persisted log refs plus batched events, duplicate local subscription handling, same-signature no-replay behavior, and replay idempotence with duplicate overlap events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/meta_aggregator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/meta_replay.go -->
# sources/distributed-fs/seaweedfs/weed/filer/meta_replay.go

## Purpose

`meta_replay.go` applies one metadata event from a subscribed filer stream to a `FilerStore`. It is the low-level replay primitive used by metadata aggregation and replication.

## Important APIs, Types, and Functions

The single public function is `Replay(filerStore FilerStore, resp *filer_pb.SubscribeMetadataResponse) error`.

## Control Flow

`Replay` reads `resp.EventNotification`. If `OldEntry` is present, it constructs the old full path from `resp.Directory` and old name, then deletes that entry from the store. If `NewEntry` is present, it chooses `message.NewParentPath` when set, otherwise `resp.Directory`, converts the protobuf entry to a filer `Entry`, and inserts it into the store.

## State and Persistence Behavior

All persistence is delegated to `DeleteEntry` and `InsertEntry` on the supplied store. The function does not open transactions, so rename-like delete/create events are only as atomic as the underlying event and store operations make them.

## Dependencies and Integration Points

The file depends on filer protobuf event shapes, `FromPbEntry`, SeaweedFS path utilities, and the shared `FilerStore` interface. It is called by `MetaAggregator` for remote metadata replication.

## Risks and Edge Cases

The function assumes `resp` and `EventNotification` are non-nil; callers must filter freshness events. Delete happens before insert, so a failure between steps can leave partial replay for move/update events. `InsertEntry` is used for new entries, so stores must treat insert as upsert or replay duplicates may fail.

## Test Signals

Tests should cover delete-only, create-only, rename with `NewParentPath`, update replacement, duplicate replay idempotence, nil event handling at caller boundaries, and partial failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/meta_replay.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/metadata_event_context.go -->
# sources/distributed-fs/seaweedfs/weed/filer/metadata_event_context.go

## Purpose

`metadata_event_context.go` provides a context flag to suppress automatic metadata event emission for nested filer operations that are part of one higher-level change.

## Important APIs, Types, and Functions

`WithSuppressedMetadataEvents` returns a derived context containing a private key. `metadataEventsSuppressed` reads the flag and treats nil contexts as not suppressed.

## Control Flow

Callers wrap a context before invoking lower-level filer operations. Event-producing code checks `metadataEventsSuppressed(ctx)` and skips local event emission when true.

## State and Persistence Behavior

There is no persistent state. Suppression is scoped to the context tree and disappears when the context is discarded.

## Dependencies and Integration Points

The file depends only on Go `context`. It integrates with filer operations such as rename or composite updates that would otherwise emit duplicate create/delete notifications.

## Risks and Edge Cases

The key type is private, avoiding collisions. Suppression does not cross goroutines unless the context is explicitly passed. Overuse can hide legitimate metadata events and break subscribers.

## Test Signals

Unit tests should verify nil context behavior, inherited suppression through derived contexts, and that composite filer operations emit only the intended outer event.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/metadata_event_context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/metadata_event_sink.go -->
# sources/distributed-fs/seaweedfs/weed/filer/metadata_event_sink.go

## Purpose

`metadata_event_sink.go` implements a request-scoped sink for capturing the metadata event emitted while serving a filer request. It lets RPC handlers return or inspect the event without subscribing to the global metadata log.

## Important APIs, Types, and Functions

`MetadataEventSink` stores the last `SubscribeMetadataResponse`. `WithMetadataEventSink` attaches a sink to a context. `metadataEventSinkFromContext` retrieves it. `Record` saves a non-nil event, and `Last` returns the saved event.

## Control Flow

The request handler creates a context/sink pair, passes the context through normal filer operations, and event emission calls `Record` if a sink exists. Only the most recent event is retained.

## State and Persistence Behavior

State is in-memory and context-scoped. The sink is documented as single-goroutine request state, so it uses no mutex. It does not affect durable metadata logs.

## Dependencies and Integration Points

The file depends on Go `context` and filer protobuf event types. It integrates with `Filer.NotifyUpdateEvent` and RPC code that needs to expose the event generated by a mutation.

## Risks and Edge Cases

Concurrent use would race because the sink has no lock. Multiple event emissions overwrite earlier events. Nil sink or nil event inputs are ignored, making it safe for optional paths.

## Test Signals

Tests should cover context attachment/retrieval, nil behavior, overwrite semantics, and integration with a real notify call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/metadata_event_sink.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/metadata_event_sink_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/metadata_event_sink_test.go

## Purpose

`metadata_event_sink_test.go` verifies that `Filer.NotifyUpdateEvent` records a request metadata event into a context-attached `MetadataEventSink`.

## Important APIs, Types, and Functions

The test uses `WithMetadataEventSink`, constructs a minimal `Filer` with signature and local log buffer, calls `NotifyUpdateEvent`, and inspects `sink.Last()`.

## Control Flow

The test creates a delete-like event for `/dir/file.txt`, then asserts the sink captured an event with directory `/dir`, old entry name `file.txt`, signatures containing the caller-provided signature and filer signature, and a non-zero timestamp.

## State and Persistence Behavior

The log buffer is in-memory and configured with a no-op flush callback. The captured sink event is request-local; no store writes are involved.

## Dependencies and Integration Points

The test depends on `log_buffer.NewLogBuffer`, SeaweedFS path utilities, and `Filer.NotifyUpdateEvent`. It validates the integration between event emission and the sink helper.

## Risks and Edge Cases

The test covers one old-entry event shape, not create/update, multiple events, nil sink, or suppression context interactions. Signature order is asserted and could break if notify semantics intentionally change.

## Test Signals

The key signals are non-nil captured event, correct directory/name, signature propagation, and non-zero event timestamp.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/metadata_event_sink_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/mongodb/mongodb_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/mongodb/mongodb_store.go

## Purpose

`mongodb_store.go` implements SeaweedFS filer metadata storage using MongoDB. It stores each entry as one document keyed by `(directory, name)`, creates a unique index, supports TLS/auth configuration, and implements directory listing with sorted Mongo queries.

## Important APIs, Types, and Functions

`MongodbStore` holds the Mongo client, database name, and collection name. `Model` maps document fields `directory`, `name`, and `meta`. The store implements initialization, TLS setup, unique index creation, no-op transactions, entry upsert/find/delete, directory child deletion, prefixed listing, and shutdown.

## Control Flow

Initialization reads URI, pool, TLS, credential, and database configuration, builds `options.Client`, optionally configures TLS and explicit credentials, connects with a 10-second timeout, and creates a unique index on `directory,name`. Entry update validates against null bytes, encodes/gzips metadata, then uses `UpdateOne` with upsert and BSON builders. Find validates path parts, queries by directory/name, maps no document or empty meta to `ErrNotFound`, and decodes the entry.

Listing builds a query on `directory`, optional anchored regex for prefix using `regexp.QuoteMeta`, and `$gt`/`$gte` for pagination, sorts by `name`, limits results, decodes each document, and invokes the callback.

## State and Persistence Behavior

Metadata persists as BSON documents in the `filemeta` collection. The unique compound index enforces one row per directory/name. No MongoDB transactions are used, so multi-entry operations are not atomic. Delete-folder-children deletes documents whose `directory` exactly equals the requested path, i.e. direct children only.

## Dependencies and Integration Points

The file depends on the official MongoDB Go driver, TLS certificate files, SeaweedFS entry encoding, and the filer store registry. It integrates with MongoDB auth/TLS deployments and shared filer operations.

## Risks and Edge Cases

TLS configuration requires client cert/key and CA files whenever `ssl` is true; it does not support system-root-only TLS in this path. `FindEntry` logs and returns `ErrNotFound` for non-no-document query errors, which can hide backend failures. Prefix listing uses regex plus sort; index usage depends on Mongo's query planner and collation. Null-byte validation is defense-in-depth.

## Test Signals

Tests should cover unique index creation, TLS config errors, credential override while preserving URI auth options, upsert/find/delete, direct-child deletion, prefix and pagination ordering, null-byte rejection, and backend error mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/mongodb/mongodb_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/mongodb/mongodb_store_kv.go -->
# sources/distributed-fs/seaweedfs/weed/filer/mongodb/mongodb_store_kv.go

## Purpose

`mongodb_store_kv.go` implements the generic filer KV API on top of the same MongoDB `filemeta` collection used for metadata. It maps arbitrary byte keys into synthetic directory/name document fields.

## Important APIs, Types, and Functions

The public methods are `KvPut`, `KvGet`, and `KvDelete`. `genDirAndName` pads keys shorter than eight bytes and splits the first eight bytes into `directory` and the remainder into `name`.

## Control Flow

KV put computes synthetic directory/name, then performs an upsert setting `meta` to the raw value. KV get finds one matching document, maps query failure or empty meta to `filer.ErrKvNotFound`, and returns the stored bytes. KV delete removes one matching document.

## State and Persistence Behavior

KV state persists in the `filemeta` collection with the same fields and unique index as metadata. Values are raw bytes in `meta`. Short keys are zero-padded locally before splitting, so the effective key is padded to at least eight bytes.

## Dependencies and Integration Points

The file depends on `MongodbStore` connection fields, Mongo BSON builders, and the filer KV error contract. It is used by shared filer components such as metadata offset tracking.

## Risks and Edge Cases

KV documents share the metadata collection and could collide with real metadata documents if synthetic directory/name values overlap. Empty values are treated as not found because `KvGet` checks `len(data.Meta) == 0`. `genDirAndName` mutates its local slice by appending zeros, which is safe for caller data but important for key semantics.

## Test Signals

Tests should cover short and long binary keys, empty value behavior, put/get/delete, collision isolation from metadata paths, and query error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/mongodb/mongodb_store_kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/mount_peer_registry.go -->
# sources/distributed-fs/seaweedfs/weed/filer/mount_peer_registry.go

## Purpose

`mount_peer_registry.go` implements an in-memory registry of active mount servers. It supports the first tier of mount peer chunk sharing by letting mounts heartbeat their address/locality to the filer and list currently alive peers.

## Important APIs, Types, and Functions

`MountPeerRegistry` holds a lock, map of peer address to entries, and injectable clock. `MountPeerInfo` is the public listing record. `NewMountPeerRegistry`, `Register`, `List`, `Len`, and `Sweep` are the public operations. Constants cap entries at 10,000 and TTL at one hour.

## Control Flow

`Register` rejects empty addresses, normalizes non-positive TTL to 60 seconds, caps large TTLs, creates or renews an entry under a write lock, and rejects new entries when at capacity while still allowing renewals. `List` takes an RLock, filters expired entries without deleting them, and returns public info. `Sweep` takes a write lock and deletes expired entries.

## State and Persistence Behavior

All registry state is process-local and lost on filer restart. It stores peer address, data center, rack, expiry, and last-seen time. It deliberately does not store per-file or per-chunk state.

## Dependencies and Integration Points

The file depends only on `sync` and `time`. It integrates with mount registration/list RPCs and peer chunk-sharing code that ranks peers by locality.

## Risks and Edge Cases

Expired entries remain in memory until `Sweep`, so sweep cadence matters under churn. Capacity rejection is silent. Locality strings are not validated. The registry is not replicated across filers and should be treated as advisory.

## Test Signals

Tests should cover registration, renewal, expiry filtering, sweep eviction counts, TTL default/cap behavior, empty address rejection, capacity limit, and concurrent list/register/sweep under race detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/mount_peer_registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/mount_peer_registry_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/mount_peer_registry_test.go

## Purpose

`mount_peer_registry_test.go` validates the in-memory mount peer registry's TTL, renewal, listing, sweep, and capacity semantics using an injectable clock.

## Important APIs, Types, and Functions

The tests use `newMountPeerRegistryWithClock`, `Register`, `List`, `Len`, `Sweep`, `maxMountPeerRegistryTTL`, and `maxMountPeerRegistryEntries`. `testClock` is a small helper retained for future tests.

## Control Flow

Tests register peers, advance a mutable clock, and assert list contents or registry length. They verify renewal extends expiry and updates rack, `List` filters but does not delete expired entries, `Sweep` deletes expired entries and counts them, negative TTL defaults to 60 seconds, huge TTLs are capped, empty address is ignored, and a full registry rejects a new address but accepts renewal.

## State and Persistence Behavior

State is local to each test registry. The injected clock makes TTL behavior deterministic without sleeping.

## Dependencies and Integration Points

The test file depends on Go `testing`, sorting for stable list assertions, and the registry API. It validates behavior expected by mount registration RPCs.

## Risks and Edge Cases

Filling 10,000 entries is acceptable but relatively heavier than other unit tests. The tests do not cover concurrent access or data-center fields beyond empty strings.

## Test Signals

Important signals are deterministic expiry, Len retaining expired entries until Sweep, TTL cap/default behavior, and capacity behavior preserving existing renewals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/mount_peer_registry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/mysql/mysql_collation.go -->
# sources/distributed-fs/seaweedfs/weed/filer/mysql/mysql_collation.go

## Purpose

`mysql_collation.go` detects whether the MySQL `filemeta.name` column uses byte-ordered collation. If not, it forces generated listing SQL to use `BINARY name` so S3 listings remain byte-lexicographic.

## Important APIs, Types, and Functions

`ConfigureListOrdering` inspects the live database and mutates `SqlGenMysql.ForceBinaryCollation`. `nameColumnCollation` queries `information_schema.COLUMNS`. `isBinaryCollation` recognizes empty, `binary`, and `*_bin` collations.

## Control Flow

On initialization, MySQL stores call `ConfigureListOrdering`. It queries the effective column collation; on query failure it logs at verbosity 1 and leaves default SQL unchanged. If the collation is not binary, it flips the generator flag and logs a warning explaining correctness and performance implications.

## State and Persistence Behavior

No durable state is changed. The generator flag affects subsequent list SQL generation in memory. Operators must alter the database schema themselves for indexed byte ordering.

## Dependencies and Integration Points

The file depends on `database/sql`, `abstract_sql.DEFAULT_TABLE`, `SqlGenMysql`, and SeaweedFS logging. It integrates with S3 list semantics and SQL store initialization.

## Risks and Edge Cases

The fallback `BINARY` expression can prevent index-ordered scans and cause filesorts. If the collation check fails, the store may keep locale ordering and produce list order mismatches. The information-schema query assumes the current database is the active schema.

## Test Signals

Unit tests cover `isBinaryCollation`; integration tests should cover real binary and non-binary columns and verify generated SQL changes after configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/mysql/mysql_collation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/mysql/mysql_sql_gen.go -->
# sources/distributed-fs/seaweedfs/weed/filer/mysql/mysql_sql_gen.go

## Purpose

`mysql_sql_gen.go` generates MySQL SQL statements for SeaweedFS's abstract SQL filer store. It supports configurable table creation/drop, optional upsert, and byte-order fallback for listings.

## Important APIs, Types, and Functions

`SqlGenMysql` implements `abstract_sql.SqlGenerator`. It provides `GetSqlInsert`, `GetSqlUpdate`, `GetSqlFind`, `GetSqlDelete`, `GetSqlDeleteFolderChildren`, list query methods, create/drop methods, and the private `nameExpr`. `DefaultUpsertQuery` uses `ON DUPLICATE KEY UPDATE`.

## Control Flow

Each method formats a table name into a template. Insert uses a configured upsert template when present, otherwise plain insert. List queries use `nameExpr`, which returns `BINARY name` when `ForceBinaryCollation` is set, and apply the same expression to pagination comparisons, prefix `LIKE`, and `ORDER BY`.

## State and Persistence Behavior

The file does not execute SQL itself. It determines the statements used by `abstract_sql.AbstractSqlStore` to persist metadata rows keyed by `dirhash`, `name`, and `directory`.

## Dependencies and Integration Points

It depends on the MySQL driver import for registration and the abstract SQL store interface. MySQL and MySQL2 stores install this generator during initialization.

## Risks and Edge Cases

Custom templates must match placeholder order expected by `abstract_sql`. `DefaultUpsertQuery` intentionally uses `VALUES(meta)` for MariaDB compatibility; changing to MySQL 8 row-alias syntax could break MariaDB. Binary fallback may sacrifice index use.

## Test Signals

Tests should cover upsert/default insert generation, table quoting, binary list expressions for exclusive/inclusive pagination, and custom template formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/mysql/mysql_sql_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/mysql/mysql_sql_gen_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/mysql/mysql_sql_gen_test.go

## Purpose

`mysql_sql_gen_test.go` tests MySQL SQL generation and collation helper behavior. It guards compatibility choices around default upsert syntax and byte-ordered list SQL.

## Important APIs, Types, and Functions

Tests cover `SqlGenMysql.GetSqlInsert`, list query generation, `ForceBinaryCollation`, `DefaultUpsertQuery`, and `isBinaryCollation`.

## Control Flow

The tests instantiate generators with and without upsert templates, inspect generated SQL strings, and assert expected substrings or absent substrings. Collation tests classify known binary and case-insensitive collation names.

## State and Persistence Behavior

No database state is touched; these are pure string-generation tests.

## Dependencies and Integration Points

The file uses Go's testing package and string containment checks. It protects SQL consumed by `abstract_sql.AbstractSqlStore`.

## Risks and Edge Cases

String-substring tests can miss placeholder ordering errors or invalid SQL grammar. They do not execute generated SQL against MySQL or MariaDB.

## Test Signals

Signals include `ON DUPLICATE KEY UPDATE` in default upsert, no MySQL 8 alias syntax, plain insert when no template is configured, and `BINARY name` applied consistently to ordering, prefix filter, and pagination comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/mysql/mysql_sql_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/mysql/mysql_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/mysql/mysql_store.go

## Purpose

`mysql_store.go` initializes the non-bucket MySQL filer store. It configures DSN/TLS/connection pooling, installs the MySQL SQL generator, enables upsert by default, and configures retry handling for deadlocks and lock wait timeouts.

## Important APIs, Types, and Functions

`MysqlStore` embeds `abstract_sql.AbstractSqlStore` and implements `GetName` and `Initialize`. `initialize` handles all connection and generator setup. `maskedDSN` redacts passwords for error messages. `CONNECTION_URL_PATTERN` builds a default utf8mb4 binary-collated DSN.

## Control Flow

Initialization sets defaults for idle connections and upsert, reads configuration, selects the upsert template, configures `SqlGenMysql`, sets a retry callback for MySQL error 1213 and 1205, parses or builds a DSN, optionally installs a per-connector TLS config, opens a `sql.DB` via `mysql.NewConnector`, configures pool sizes/lifetime, pings the database, and runs collation detection.

## State and Persistence Behavior

Persistent metadata behavior is handled by `abstract_sql`: rows in the default table keyed by `dirhash`, `name`, and `directory`. This store does not support bucket-specific tables. Runtime state includes the DB pool, generator, and retry callback.

## Dependencies and Integration Points

The file depends on `go-sql-driver/mysql`, TLS certificate loading, `abstract_sql`, and MySQL collation detection. It integrates with all common filer store methods through the embedded abstract SQL store.

## Risks and Edge Cases

TLS config is per connector, avoiding global driver config conflicts. Empty CA means system trust roots are used. If either client cert or key path is set, both must load. Custom DSNs can override defaults and may not use binary collation. Retryable errors are limited to deadlock and lock-wait timeout.

## Test Signals

Integration tests should cover DSN parsing, password masking, TLS with system roots and mTLS, upsert default/disable, retry callback behavior, pool settings, collation fallback, and basic abstract store CRUD/list operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/mysql/mysql_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/mysql2/mysql2_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/mysql2/mysql2_store.go

## Purpose

`mysql2_store.go` initializes the bucket-aware MySQL filer store. It uses the same MySQL SQL generator as the normal store but enables abstract SQL support for per-bucket tables and creates the default table during startup.

## Important APIs, Types, and Functions

`MysqlStore2` embeds `abstract_sql.AbstractSqlStore`, implements `filer.BucketAware`, and provides `GetName`, `Initialize`, and `initialize`. It uses `mysql.SqlGenMysql` and `mysql.DefaultUpsertQuery`.

## Control Flow

Initialization sets defaults, reads create-table and connection options, enables `SupportBucketTable`, chooses an upsert template, builds a MySQL connection URL with optional `interpolateParams`, opens the DB via `database/sql`, configures the pool, pings, creates the default table unless the error text says it already exists, and configures list ordering based on collation.

## State and Persistence Behavior

Metadata persists through abstract SQL tables, with bucket support enabled so bucket lifecycle can map data into separate tables. Runtime state is the DB pool plus generator. Unlike `mysql_store.go`, TLS and arbitrary DSN support are not present in this older-style initializer.

## Dependencies and Integration Points

The file depends on the MySQL driver, `abstract_sql`, MySQL SQL generator/collation helpers, and `filer.BucketAware`. It integrates with bucket create/drop paths through embedded abstract SQL behavior.

## Risks and Edge Cases

The error path after `sql.Open` calls `store.DB.Close()` even when `store.DB` may be nil if open failed before assignment. Existing-table detection relies on substring text. Password redaction uses a separately built adapted URL. TLS options available in `mysql_store.go` are not exposed here.

## Test Signals

Tests should cover default table creation, bucket table create/drop behavior, existing table errors, upsert enable/disable, collation fallback, connection pool settings, and failure handling for bad credentials or unavailable DB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/mysql2/mysql2_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/persisted_log_cache.go -->
# sources/distributed-fs/seaweedfs/weed/filer/persisted_log_cache.go

## Purpose

`persisted_log_cache.go` caches decoded metadata log chunks used by SubscribeMetadata replay. It reduces repeated volume-server fetch and protobuf decode cost when multiple subscribers replay the same flushed metadata log chunks.

## Important APIs, Types, and Functions

`persistedLogCache` is an LRU cache keyed by chunk file ID. It uses a mutex, list/index map, current byte estimate, max bytes, `singleflight.Group`, and weighted semaphore. `getOrLoad`, `lookup`, `store`, `evictIdle`, `loadGuarded`, `estimateEntriesBytes`, `loadLogFileEntries`, and `decodeLogRecords` are the core functions. `logCacheItem` stores decoded immutable `LogEntry` slices.

## Control Flow

`getOrLoad` checks the cache, coalesces concurrent misses by file ID, limits in-flight load bytes with a semaphore, calls a loader, and only caches successful cacheable decodes. A background goroutine evicts entries idle for five minutes. `loadLogFileEntries` fetches a full chunk through volume lookup and decodes it. `decodeLogRecords` parses 4-byte length-prefixed protobuf `LogEntry` records, requiring positive size, bounded size, positive strictly increasing timestamps, and complete record boundaries.

## State and Persistence Behavior

The cache is process-local and bounded by byte estimate, defaulting to 256 MiB retained and 128 MiB concurrent load budget. It does not persist entries; source-of-truth logs remain persisted filer log chunks. Cached slices are shared read-only.

## Dependencies and Integration Points

The file depends on SeaweedFS chunk fetch helpers, `wdclient.MasterClient`, protobuf unmarshalling, `singleflight`, semaphores, and the `LogFileIterator` in `filer_notify_read.go`, which switches to stream fallback when chunks do not decode standalone.

## Risks and Edge Cases

Corrupt or partial chunks must not be cached because later complete reads may succeed. `proto.Unmarshal` can accept arbitrary bytes, so timestamp/order invariants are used as additional alignment checks. The background eviction goroutine lives for process lifetime. Byte estimates are conservative but not exact. Load weight is clamped so oversized chunks cannot deadlock on the semaphore.

## Test Signals

Tests should cover cache hits/misses, uncacheable results, singleflight coalescing, LRU budget eviction, idle eviction, clean/incomplete/corrupt decode, oversized load weight clamping, chunk filtering by timestamp, and stream fallback when records span chunk boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/persisted_log_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/persisted_log_cache_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/persisted_log_cache_test.go

## Purpose

`persisted_log_cache_test.go` validates the metadata persisted-log cache, chunk decoder, and `LogFileIterator` integration paths. It uses stub loaders to avoid real volume-server reads.

## Important APIs, Types, and Functions

Helpers include `logEntriesAt`, `encodeLogRecords`, `stubChunkLoader`, `logFileEntry`, and `collectTs`. Tests cover `persistedLogCache.getOrLoad`, `decodeLogRecords`, `newLogFileIterator`, cache eviction, stream fallback, and load error propagation.

## Control Flow

Cache tests assert first-load/second-hit behavior, uncacheable reloads, singleflight across 20 goroutines, and LRU/idle eviction. Decode tests build size-prefixed protobuf buffers and truncate or corrupt them to expect `errLogChunkIncomplete`. Iterator tests stub chunk loading, filter timestamps, skip cold chunks based on flush time, share decoded chunks across replays, fall back to whole-file streaming when records span chunks, skip already-yielded records after fallback, and surface loader errors.

## State and Persistence Behavior

All cache state is in-memory. Loader functions are temporarily swapped via package variables and restored with `t.Cleanup`. Encoded log file entries simulate persisted chunks without touching actual filer storage.

## Dependencies and Integration Points

The tests depend on protobuf marshal/unmarshal, the filer log iterator from `filer_notify_read.go`, and `wdclient` type signatures for stubbed loaders. They validate subscriber replay behavior around persisted log chunks.

## Risks and Edge Cases

Global function swaps would be unsafe under parallel tests; these tests do not call `t.Parallel`. The cache constructor starts background eviction goroutines, so many tests create goroutines that live until process exit. Stringified slice comparisons are simple but sufficient for timestamp order.

## Test Signals

Strong signals include exactly one coalesced load, no caching for uncacheable results, correct timestamp filtering, no duplicate records after stream fallback, and correct rejection of implausible zero/non-increasing timestamp records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/persisted_log_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/posixlock/manager.go -->
# sources/distributed-fs/seaweedfs/weed/filer/posixlock/manager.go

## Purpose

`posixlock/manager.go` implements the concurrent, per-filer authority for POSIX advisory locks across inode keys. It wraps per-inode `Set` objects with a mutex, tracks which sessions hold locks on which keys, and reaps stale leased sessions efficiently.

## Important APIs, Types, and Functions

`Manager` holds `byKey`, `bySid`, and `lastSeen`. Public methods include `NewManager`, `Renew`, `ReapExpired`, `TryLock`, `Track`, `Snapshot`, `Reassert`, `Unlock`, `GetLk`, `ReleasePosixOwner`, `ReleaseFlockOwner`, and `ReleaseSession`. Internal helpers maintain the session index.

## Control Flow

`TryLock` creates a set on demand, calls `Set.Acquire`, indexes the session on success, and returns conflicts on failure. `Track` inserts already-granted locks without arbitration for client-side mirrors. `Reassert` renews a session lease, removes that session's current locks on the key, tries to reacquire asserted locks against other sessions, records conflicts, and prunes empty sets/index entries. Release methods delegate to `Set` then call `afterRelease`.

`ReapExpired` scans only sessions that have called `Renew`, releases their locks across indexed keys when the last heartbeat is older than the TTL, and removes lease/index state.

## State and Persistence Behavior

All lock state is transient in memory and intentionally not replicated through metadata logs. `bySid` is an index for O(locks-held) cleanup, while `lastSeen` determines which sessions are lease-managed. Restarting a filer loses authoritative lock state unless clients reassert.

## Dependencies and Integration Points

The manager depends on the pure `Set` algorithm in `posixlock.go`. It integrates with FUSE/mount lock RPCs, owner-filer routing by path or hardlink key, mount keepalives, and reassertion after owner changes.

## Risks and Edge Cases

Sessions that never renew are never reaped, preserving backward compatibility but risking stale locks if keepalives are absent. Reassertion can conflict with locks acquired during an owner migration gap and reports those conflicts without double-granting. The manager serializes all keys with one mutex, which is simple but can become contended under high lock churn.

## Test Signals

Tests should cover conflict/grant, index pruning, partial unlock, GETLK, namespace-specific owner releases, session-wide release, stale leased reaping, concurrent flock mutual exclusion, reassert rebuild/idempotence/conflict, and lease renewal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/posixlock/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/posixlock/manager_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/posixlock/manager_test.go

## Purpose

`posixlock/manager_test.go` validates the concurrent manager around the pure lock set. It focuses on indexing, cleanup, session reaping, namespace-specific release, GETLK behavior, and mutual exclusion under concurrent flock churn.

## Important APIs, Types, and Functions

Tests use `NewManager`, `TryLock`, `Unlock`, `GetLk`, `ReleasePosixOwner`, `ReleaseSession`, `Renew`, `ReapExpired`, and direct inspection of `byKey`, `bySid`, and `lastSeen`.

## Control Flow

The tests acquire locks on keys, attempt conflicts, unlock ranges, and assert map cleanup. Session reaping tests mark one session stale, one fresh, and one never-renewed, then verify only stale leased locks are removed. The concurrency test runs 16 goroutines repeatedly acquiring a whole-file flock, using atomics to detect simultaneous holders.

## State and Persistence Behavior

All state is in-memory. Some tests directly mutate `lastSeen` to simulate stale heartbeats. No external filer or mount RPCs are involved.

## Dependencies and Integration Points

The tests depend on `runtime.Gosched`, `sync`, atomics, and the manager/set lock algorithm. They validate server-side behavior expected by distributed FUSE lock handling.

## Risks and Edge Cases

Direct inspection of unexported maps couples tests tightly to implementation. The concurrency test is probabilistic but high-iteration enough to catch obvious mutual exclusion errors. Time-based tests use `time.Now` and manual backdating rather than an injected clock.

## Test Signals

Signals include no stale index entries after unlock/reap, flock surviving posix-owner release, session 2 lock surviving session 1 release, only stale leased sessions reaped, and zero overlap count in concurrent flock churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/posixlock/manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/posixlock/posixlock.go -->
# sources/distributed-fs/seaweedfs/weed/filer/posixlock/posixlock.go

## Purpose

`posixlock/posixlock.go` implements the pure byte-range advisory lock algorithm for one inode. It handles fcntl and flock namespaces, read/write conflict rules, same-owner upgrades/downgrades, range coalescing, splitting, and owner/session release.

## Important APIs, Types, and Functions

Constants `Read`, `Write`, and `Unlock` define platform-independent lock types. `Range` describes inclusive `[Start,End]` locks with session, owner, pid, and flock namespace. `Set` stores sorted held locks. Public methods are `Conflict`, `Acquire`, `Grant`, `Release`, `ReleaseOwner`, `ReleaseFlockOwner`, `ReleasePosixOwner`, `ReleaseSession`, `HasPosix`, `Locks`, and `Empty`.

## Control Flow

`Conflict` scans held locks and returns the first overlapping lock in the same namespace from a different owner where at least one side is a write. `Acquire` calls `Conflict`, then inserts if clear. `insert` removes/adjusts same-owner overlaps: same-type ranges are widened/coalesced, different-type overlaps are split around the new range, and adjacent same-type ranges merge without overflowing at `MaxUint64`. `remove` drops or splits matching locks across a range, supporting unlock and owner/session cleanup.

## State and Persistence Behavior

`Set` is in-memory and has no internal synchronization; callers must serialize. The stored slice is sorted by start offset and aliases internal state when returned by `Locks`. Lock end offsets are inclusive; `math.MaxUint64` represents EOF.

## Dependencies and Integration Points

The file depends only on `math` and `sort`. It is used by `Manager` for server-side lock authority and by client-side mirrors for reassertion.

## Risks and Edge Cases

Same owner identity includes `(Sid, Owner)` for conflicts but `sameOwner` ignores `IsFlock`; namespace checks are performed separately by callers in conflict/insert paths. Off-by-one errors around inclusive ranges and `MaxUint64` adjacency are safety-critical. `Locks` exposes mutable internal slice content by contract, so callers must not mutate it.

## Test Signals

Tests should cover read/read sharing, write conflicts, same-owner type replacement, coalescing, splitting, whole-file locks, namespace separation, session identity, owner/session releases, and max-end overflow avoidance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/posixlock/posixlock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/posixlock/posixlock_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/posixlock/posixlock_test.go

## Purpose

`posixlock/posixlock_test.go` is the core unit test suite for the pure `Set` range-lock algorithm. It documents POSIX/flock semantics and many boundary cases.

## Important APIs, Types, and Functions

The tests use helper `mustAcquire` plus `Set.Acquire`, `Conflict`, `Release`, `ReleaseOwner`, `ReleasePosixOwner`, `ReleaseFlockOwner`, `ReleaseSession`, `HasPosix`, `Empty`, and direct `s.locks` inspection.

## Control Flow

Tests build sets, acquire ranges with different owners/sessions/namespaces, assert conflicts or grants, release partial ranges, and inspect resulting ranges. Cases cover shared reads, write/read and write/write conflicts, same-owner upgrade/downgrade, adjacent coalescing, mid-range splitting, whole-file locks, namespace separation, flock/posix owner releases, `MaxUint64` adjacency, and session-aware owner identity.

## State and Persistence Behavior

All lock state is local to a `Set`. Tests do not use the concurrent `Manager` except indirectly through shared types.

## Dependencies and Integration Points

The file depends on Go's `testing` and `math`. It protects the algorithm used by distributed FUSE lock management.

## Risks and Edge Cases

Direct slice assertions are valuable but couple tests to sorted storage. Tests do not run randomized interval fuzzing, so unusual interleavings of many locks could still hide bugs.

## Test Signals

Signals include exact split ranges after unlock/type replacement, no false merge at `MaxUint64`, same owner numbers in different sessions conflicting, flock and fcntl not conflicting, and empty set after releasing all locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/posixlock/posixlock_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/posixlock/reassert_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/posixlock/reassert_test.go

## Purpose

`posixlock/reassert_test.go` tests lock reassertion, the recovery path used when a mount's lock mirror is sent to a fresh or changed owner filer.

## Important APIs, Types, and Functions

The tests use two `Manager` instances as client mirror and owner authority, plus `Track`, `Snapshot`, `Reassert`, `TryLock`, `Renew`, and `ReapExpired`. `maxEnd` aliases `^uint64(0)` for whole-file locks.

## Control Flow

`TestReassertRebuildsOnFreshOwner` tracks locks in a client manager, snapshots them, reasserts them into a fresh owner, and verifies foreign locks now conflict. `TestReassertIdempotent` reasserts the same list repeatedly and expects no state change. `TestReassertReportsConflict` verifies an incumbent lock acquired during a migration gap blocks reassertion. `TestReassertRenewsLease` verifies reassertion refreshes the session lease.

## State and Persistence Behavior

State is in-memory in manager maps. Reassertion rebuilds transient lock state after restart/ownership changes and does not persist to metadata.

## Dependencies and Integration Points

The tests validate mount keepalive/reassertion behavior expected by distributed lock ownership routing. They depend on reflect equality for lock slices and time-based lease reaping.

## Risks and Edge Cases

The tests cover one-key and multi-key snapshot flows but not partial reassert lists, empty lists on existing sessions, or concurrent reassert while other locks churn.

## Test Signals

Key signals are conflict-free rebuild on fresh owner, idempotent repeated reassertion, incumbent lock conflict reporting, and fresh lease preventing immediate reap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/posixlock/reassert_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/postgres/pgx_conn.go -->
# sources/distributed-fs/seaweedfs/weed/filer/postgres/pgx_conn.go

## Purpose

`postgres/pgx_conn.go` preserves a small compatibility entry point for opening PostgreSQL connections with pgx-backed utilities. It lets existing callers keep using `postgres.OpenPGXDB` while centralizing implementation in `util/pgxutil`.

## Important APIs, Types, and Functions

The only function is `OpenPGXDB(sqlUrl, adaptedSqlUrl string, pgbouncerCompatible bool, maxIdle, maxOpen, maxLifetimeSeconds int) (*sql.DB, error)`.

## Control Flow

The function immediately delegates to `pgxutil.OpenDB` with the same arguments and returns its result.

## State and Persistence Behavior

No state is held here. The returned `sql.DB` pool and its persistence behavior are controlled by `pgxutil.OpenDB` and the PostgreSQL server.

## Dependencies and Integration Points

The file depends on `database/sql` and `github.com/seaweedfs/seaweedfs/weed/util/pgxutil`. It is used by both postgres and postgres2 filer stores.

## Risks and Edge Cases

The wrapper can hide changes in the underlying utility from callers. Since it is a compatibility alias, removing it would break postgres2 and external package references.

## Test Signals

Coverage is mostly through postgres store initialization tests. A unit test could verify argument forwarding with a fake only if the utility were abstracted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/postgres/pgx_conn.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/postgres/postgres_collation.go -->
# sources/distributed-fs/seaweedfs/weed/filer/postgres/postgres_collation.go

## Purpose

`postgres_collation.go` detects whether PostgreSQL list ordering for `filemeta.name` is byte-ordered. If not, it configures SQL generation to use `COLLATE "C"` so S3 listings remain byte-lexicographic.

## Important APIs, Types, and Functions

`ConfigureListOrdering` mutates `SqlGenPostgres.ForceBinaryCollation`. `nameColumnCollation` queries the column collation and database default collation. `isByteOrderedCollation` recognizes `C`, `POSIX`, `C.UTF-8`, and `C.UTF8`.

## Control Flow

At store startup, the function queries information schema and `pg_database`. If a column collation is null or empty, it uses the database default. Query failures are logged and leave default SQL unchanged. Locale-aware collations trigger generator fallback and a warning.

## State and Persistence Behavior

No schema is changed. The in-memory generator flag changes future list SQL to use `name COLLATE "C"`, which may be slower unless the schema/index supports that collation.

## Dependencies and Integration Points

The file depends on `database/sql`, `abstract_sql.DEFAULT_TABLE`, Postgres SQL generator, and logging. It protects S3 ListObjects ordering behavior for PostgreSQL-backed filers.

## Risks and Edge Cases

If detection fails, listings may remain locale-ordered. The fallback can require sorts and reduce index effectiveness. ICU or custom collations are treated as locale-aware unless explicitly recognized.

## Test Signals

Unit tests cover collation classification; integration tests should check real C and locale databases, generated SQL after configuration, and list order with mixed-case/non-ASCII names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/postgres/postgres_collation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/postgres/postgres_sql_gen.go -->
# sources/distributed-fs/seaweedfs/weed/filer/postgres/postgres_sql_gen.go

## Purpose

`postgres_sql_gen.go` generates PostgreSQL SQL statements for the abstract SQL filer store. It supports optional upsert, table create/drop templates, and `COLLATE "C"` fallback for byte-ordered listings.

## Important APIs, Types, and Functions

`SqlGenPostgres` implements `abstract_sql.SqlGenerator`. It defines `DefaultUpsertQuery`, `GetSqlInsert`, update/find/delete/delete-children, inclusive/exclusive list queries, create/drop methods, and `nameExpr`.

## Control Flow

Methods format a quoted table name into SQL strings with `$1`-style placeholders. Insert uses configured upsert when available; the default upsert uses `ON CONFLICT (dirhash, name)` and updates `directory` and `meta`. List queries apply `nameExpr` consistently to pagination comparisons, prefix `like`, and ordering.

## State and Persistence Behavior

The generator does not persist state directly. Its statements are executed by `abstract_sql.AbstractSqlStore` against rows keyed by `dirhash`, `name`, and `directory`.

## Dependencies and Integration Points

It depends on pgx stdlib driver registration and the abstract SQL generator interface. Postgres and Postgres2 stores install it during initialization.

## Risks and Edge Cases

Custom templates must preserve placeholder order and conflict semantics. The default conflict target omits `directory`, matching the abstract schema's uniqueness expectations; mismatched schemas can break upsert. Collation fallback may cost performance.

## Test Signals

Tests should cover quoted table names, upsert/plain insert switching, conflict-safe default, and consistent `COLLATE "C"` use in list comparisons/order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/postgres/postgres_sql_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/postgres/postgres_sql_gen_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/postgres/postgres_sql_gen_test.go

## Purpose

`postgres_sql_gen_test.go` tests PostgreSQL SQL generation and byte-ordered collation classification. It protects default upsert behavior and list SQL correctness.

## Important APIs, Types, and Functions

The tests cover `SqlGenPostgres.GetSqlInsert`, list query generation with and without `ForceBinaryCollation`, `DefaultUpsertQuery`, and `isByteOrderedCollation`.

## Control Flow

Tests instantiate generators, inspect generated SQL strings, assert presence/absence of `ON CONFLICT` and `COLLATE`, and classify known byte-ordered versus locale-aware collation names.

## State and Persistence Behavior

No database is used. The tests validate string generation only.

## Dependencies and Integration Points

The file depends on Go `testing` and `strings`. It protects SQL used by abstract SQL stores.

## Risks and Edge Cases

Substring tests do not execute SQL and may miss invalid placeholder ordering or schema mismatch. Collation classification is a whitelist and may need expansion for platform-specific byte-ordered names.

## Test Signals

Signals are default `ON CONFLICT` presence, plain insert fallback, no default collation forcing, `COLLATE "C"` applied to order/filter/pagination when forced, and correct collation classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/postgres/postgres_sql_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/postgres/postgres_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/postgres/postgres_store.go

## Purpose

`postgres_store.go` initializes the non-bucket PostgreSQL filer store using pgx. It configures connection strings, SSL parameters, schema/search path behavior, upsert defaults, and list-order detection for the abstract SQL backend.

## Important APIs, Types, and Functions

`PostgresStore` embeds `abstract_sql.AbstractSqlStore` and implements `GetName`, `Initialize`, and `initialize`. It uses `SqlGenPostgres`, `DefaultUpsertQuery`, and `OpenPGXDB`.

## Control Flow

Initialization sets defaults for idle connections and upsert, reads connection/SSL/schema/pgbouncer settings, enables non-bucket mode, selects the upsert template, builds a pgx connection string with `connect_timeout=30`, redacts password in the adapted URL, omits `search_path` when pgbouncer-compatible mode is requested, opens the DB through `OpenPGXDB`, and configures list ordering.

## State and Persistence Behavior

The embedded abstract SQL store persists metadata in the default table and keeps runtime state in the `sql.DB` pool and generator. This store does not create the table itself in this file and does not support bucket tables.

## Dependencies and Integration Points

The file depends on pgx, `abstract_sql`, `pgxutil` via `OpenPGXDB`, and Postgres collation detection. It integrates with normal filer metadata operations through the embedded store.

## Risks and Edge Cases

Connection string assembly is manual; values containing spaces or special characters rely on pgx keyword parsing behavior. Pgbouncer compatibility disables search path injection. Upsert is enabled by default to avoid duplicate-key errors poisoning PostgreSQL transactions.

## Test Signals

Integration tests should cover SSL options, schema versus pgbouncer behavior, upsert enable/disable, password redaction, collation fallback, and basic abstract store CRUD/listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/postgres/postgres_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/postgres2/postgres2_store.go -->
# sources/distributed-fs/seaweedfs/weed/filer/postgres2/postgres2_store.go

## Purpose

`postgres2_store.go` initializes the bucket-aware PostgreSQL filer store. It shares pgx connection logic and SQL generation with the normal Postgres store while enabling abstract SQL bucket-table support and creating the default table.

## Important APIs, Types, and Functions

`PostgresStore2` embeds `abstract_sql.AbstractSqlStore`, asserts `filer.BucketAware`, and implements `GetName`, `Initialize`, and `initialize`. It uses `postgres.SqlGenPostgres`, `postgres.DefaultUpsertQuery`, and `postgres.OpenPGXDB`.

## Control Flow

Initialization reads create-table, upsert, connection, SSL, schema, pgbouncer, and pool settings; sets `SupportBucketTable`; builds a pgx connection string and redacted version; opens the DB; creates the default table; and runs collation configuration.

## State and Persistence Behavior

Metadata persists through abstract SQL tables with bucket table support enabled. Bucket lifecycle operations can create/drop tables via embedded abstract SQL behavior. Runtime state is the DB pool and generator.

## Dependencies and Integration Points

The file depends on the postgres package's generator/connection helper, `abstract_sql`, and bucket-aware filer integrations. It is used for deployments that want bucket-level table separation.

## Risks and Edge Cases

Manual connection string assembly has the same escaping considerations as the normal store. Default table creation errors abort initialization. Custom create-table templates must match abstract SQL expectations and collation needs.

## Test Signals

Tests should cover default table creation, bucket table lifecycle, pgbouncer/search-path behavior, SSL options, upsert defaults, collation fallback, and failure on bad create-table templates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/postgres2/postgres2_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/read_remote.go -->
# sources/distributed-fs/seaweedfs/weed/filer/read_remote.go

## Purpose

`read_remote.go` contains helpers for entries backed only by remote storage and for mapping paths between local mount points and remote storage locations. It also exposes a client helper to cache a remote object into the local SeaweedFS cluster.

## Important APIs, Types, and Functions

`Entry.IsInRemoteOnly` detects entries with no local chunks and positive remote size. `MapFullPathToRemoteStorageLocation` maps a local full path under a mounted directory into a remote location. `MapRemoteStorageLocationPathToFullPath` performs the inverse mapping. `CacheRemoteObjectToLocalCluster` calls the filer RPC to cache remote data locally.

## Control Flow

Mapping helpers copy remote location name/bucket/path and append the relative path between the local mount root and target full path. The inverse strips the remote mount path prefix and appends the remainder to the local mount directory. The caching helper opens a filer client, sends `CacheRemoteObjectToLocalClusterRequest` with directory/name and concurrency settings, and returns the updated protobuf entry.

## State and Persistence Behavior

Mapping functions are pure. Caching state changes happen remotely through the filer RPC, which downloads remote object data into local chunks and updates the entry. Concurrency values of zero defer to server defaults.

## Dependencies and Integration Points

The file depends on filer protobuf clients, remote storage protobufs, and path utilities. It integrates with remote mount/cache features and callers that need to materialize remote-only entries before local reads.

## Risks and Edge Cases

The path mapping functions assume `fp` starts with `localMountedDir` and `remoteLocationPath` starts with `remoteMountedLocation.Path`; otherwise slicing can produce invalid paths or panic. `IsInRemoteOnly` treats zero-size remote objects as not remote-only because it requires `RemoteSize > 0`.

## Test Signals

Tests should cover normal/inverse mappings, trailing slash behavior, invalid prefix inputs, zero-size remote entries, cache RPC success/error paths, and explicit versus default concurrency settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/read_remote.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/read_write.go -->
# sources/distributed-fs/seaweedfs/weed/filer/read_write.go

## Purpose

`read_write.go` provides small client helpers for reading and writing filer entries through gRPC. It handles both inline entry content and chunk-backed content for reads, and create-or-update behavior for inline content writes.

## Important APIs, Types, and Functions

`ReadEntry` looks up an entry and writes either inline content or streamed chunk content into a buffer. `ReadInsideFiler` returns only inline entry content. `SaveInsideFiler` creates or updates an inline-content entry.

## Control Flow

`ReadEntry` calls `LookupEntry`; if `Entry.Content` is non-empty it writes directly to the buffer, otherwise it calls `StreamContent` over the entry chunks for the computed file size. `SaveInsideFiler` looks up the target; on `ErrNotFound` it creates a new file entry with timestamps, mode, file size, and inline content. On success it mutates the existing entry's content, mtime, and file size and sends `UpdateEntry`.

## State and Persistence Behavior

Persistence is remote through filer RPCs. Inline content is stored directly in the filer entry metadata, while chunk-backed reads stream from volume servers through `StreamContent`. `SaveInsideFiler` does not manage chunks; it stores small content inline.

## Dependencies and Integration Points

The file depends on filer protobuf lookup/create/update helpers, `wdclient.MasterClient`, `StreamContent`, and `FileSize`. It is used by internal code that stores small control/config files in the filer namespace.

## Risks and Edge Cases

`ReadInsideFiler` ignores chunk-backed content and returns only inline bytes. `SaveInsideFiler` does not handle lookup errors other than not found. Updating inline content on an entry that previously had chunks may leave chunk fields unchanged unless `UpdateEntry` semantics clear or ignore them upstream.

## Test Signals

Tests should cover inline read, chunk-stream read, create on missing entry, update existing inline content, non-not-found lookup errors, and behavior on existing chunk-backed entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/read_write.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/reader_at.go -->
# sources/distributed-fs/seaweedfs/weed/filer/reader_at.go

## Purpose

`reader_at.go` implements random/sequential `io.ReaderAt` access over SeaweedFS file chunk views. It reconstructs sparse files from visible intervals, zero-fills holes, reads chunk slices from cache or volume servers, uses parallel fetching for multi-chunk sequential reads, and triggers prefetch.

## Important APIs, Types, and Functions

`ChunkReadAt` holds master client, interval-list chunk views, file size, reader cache, read-pattern detector, last chunk file ID, prefetch count, and context. Public methods include `NewChunkReaderAtFromClient`, `Size`, `Close`, `ReadAt`, and `ReadAtWithTime`. `LookupFn` builds a legacy volume lookup function. Internal helpers include `doReadAt`, `readChunkSliceAt`, `readChunkSliceAtForParallel`, `zero`, and `chunkReadTask`.

## Control Flow

`ReadAt` records access pattern, locks the chunk interval list for reading, and delegates to `doReadAt`. `doReadAt` walks visible chunk intervals, records gaps to zero-fill, builds read tasks for overlapping chunk slices, then either reads sequentially for one chunk/random mode or uses an `errgroup` with concurrency bounded by prefetch count and `minReadConcurrency`. It aggregates bytes and max modified timestamp, triggers prefetch for following chunks in sequential mode, zero-fills trailing sparse regions up to file size, and returns `io.EOF` when the requested range reaches or passes file size.

`LookupFn` caches volume lookup responses up to 10,000 volume IDs, prefers same data center URLs, shuffles targets for load spreading, and is marked deprecated in favor of `wdclient.FilerClient`.

## State and Persistence Behavior

Reader state is in-memory: read pattern, last chunk ID, cache contents, and lookup cache. It does not mutate filer metadata or chunk data. Sparse regions are represented by absent chunk intervals and returned as zeroes.

## Dependencies and Integration Points

The file depends on interval lists, `ChunkView`, `ReaderCache`, `ReaderPattern`, volume lookup RPCs, `wdclient`, chunk fetch helpers, and `errgroup`. It integrates with mount, WebDAV, query, and streaming reads that need `ReaderAt` semantics.

## Risks and Edge Cases

Sparse zero-fill must overwrite caller buffers or stale bytes can leak; tests cover this. Parallel reads write into disjoint buffer slices, so task boundaries must be correct. The legacy lookup cache is bounded but has no eviction/TTL and can become stale after volume moves. `ReadAt` returns EOF when the requested end reaches file size, consistent with many ReaderAt users but important for callers to handle.

## Test Signals

Tests should cover gapped chunks, sparse files, EOF boundaries, random versus sequential mode, parallel multi-chunk reads, cache prefetch/un-cache behavior, lookup cache limits, same-DC ordering, and context cancellation propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/reader_at.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/reader_at_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/reader_at_test.go

## Purpose

`reader_at_test.go` verifies `ChunkReadAt` reconstruction over visible intervals, especially sparse/gapped behavior and EOF semantics. It uses a mock chunk cache that returns deterministic byte values by file ID.

## Important APIs, Types, and Functions

The file defines `mockChunkCache`, `TestReaderAt`, `testReadAt`, `TestReaderAt0`, `TestReaderAt1`, `TestReaderAtGappedChunksDoNotLeak`, and `TestReaderAtSparseFileDoesNotLeak`. It uses `NewIntervalList`, `addVisibleInterval`, `ViewFromVisibleIntervals`, `NewReaderCache`, and `NewReaderPattern`.

## Control Flow

Tests construct visible intervals with file IDs like `1`, `3`, and `7`, build a `ChunkReadAt`, and call `doReadAt` with offsets/sizes. Most tests assert byte count and EOF behavior. The leak-prevention tests seed the destination buffer with non-zero bytes and assert holes are zeroed instead of preserving old contents.

## State and Persistence Behavior

All data is synthetic and in-memory. The mock cache fills buffers with a byte equal to the numeric file ID and does not persist cache state.

## Dependencies and Integration Points

The tests depend on interval-list chunk view construction and reader cache interfaces. They validate behavior relied on by FUSE/mount and other chunked read paths.

## Risks and Edge Cases

The mock cache always succeeds and ignores offsets, so tests do not validate partial chunk data correctness or remote fetch failures. Parallel read behavior is not directly stressed because the mock and test sizes are small.

## Test Signals

Strong signals include correct EOF at/after file size, byte counts for partial reads, zero-filled gaps between chunks, and fully sparse files returning zeroes rather than leaking preexisting buffer contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/reader_at_test.go -->
