# subset-b-008379 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/skl/skl.go -->
# sources/storage-engines/badger/skl/skl.go

## Purpose
This file implements Badger's arena-backed concurrent skiplist, used as the ordered in-memory index for memtables. It is adapted from RocksDB's inline skiplist but simplified around Badger's key comparator, arena allocator, overwrite semantics, and lock-free/CAS pointer updates.

## Important APIs, Types, and Functions
- `Skiplist` owns the head node, arena, current height, reference count, and optional `OnClose` callback.
- `node` stores a key offset/size, atomically encoded value offset/size, height, and per-level next offsets.
- `NewSkiplist`, `IncrRef`, and `DecrRef` manage lifecycle; `DecrRef` clears arena/head when the final reference leaves.
- `Put`, `Get`, `Empty`, `MemSize`, and iterator constructors form the public surface used by Badger memtables.
- `findNear` and `findSpliceForLevel` are the core search primitives.
- `Iterator` supports bidirectional movement; `UniIterator` adapts it to Badger's `y.Iterator` style with optional reverse traversal.

## Control Flow and State Behavior
Nodes are allocated in an `Arena`, and node fields store offsets rather than heap pointers for compactness and stable memory layout. `Put` first searches from the current height downward. If the key is already present, it atomically stores a new value reference without creating a node. Otherwise it creates a random-height node, possibly raises list height via CAS, then links the node from level 0 upward with compare-and-swap on tower offsets. If a CAS conflict exposes that another goroutine inserted the same key at level 0, the existing node is overwritten.

`Get` seeks to the first key greater-or-equal to the timestamped key and then verifies `y.SameKey`, returning a decoded `ValueStruct` whose `Version` is parsed from the stored key. Iterators hold a skiplist reference and must be closed to release the arena. Reverse movement uses `findNear` with `less=true`.

## Dependencies and Integration Points
The file depends on `github.com/dgraph-io/badger/v4/y` for key comparison, timestamp parsing, assertions, and `ValueStruct`, plus `ristretto/v2/z.FastRand` for randomized height. It integrates with Badger memtables through the unidirectional iterator and through arena memory accounting.

## Risks and Edge Cases
Correctness depends on keys fitting `uint16` key sizes while values can be larger because values are stored through arena value offsets/sizes. The code is intentionally concurrent but lock-free insertion is subtle: base-level insertion must happen before higher levels, and overwrite races must only resolve at level 0. Reference counting is a lifecycle contract; failing to close iterators keeps arena memory live, while accessing after final `DecrRef` is invalid. Value replacement appends a new value in the arena, so repeated overwrites grow memory until the memtable is flushed.

## Test Signals
`skl_test.go` covers empty-list behavior, overwrites, large values, concurrent writes and reads, same-key write races, `findNear` boundary conditions, forward/reverse iteration, seek semantics, and read/write benchmarks against a map baseline.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/skl/skl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/skl/skl_test.go -->
# sources/storage-engines/badger/skl/skl_test.go

## Purpose
This test file validates the concurrent skiplist implementation in `skl.go`. It focuses on correctness of lookup/overwrite behavior, search boundary semantics, iterator traversal, concurrent insertion, large values, reference counting, and basic performance characteristics.

## Important Tests and Helpers
- `newValue`, `randomKey`, and `length` create deterministic values, random timestamped keys, and exact list length checks.
- `TestEmpty` validates empty `Get`, all `findNear` variants, iterator invalid states, and reference-counted close behavior.
- `TestBasic` checks insertion, timestamped lookup, overwrites for a logical key at a newer timestamp, metadata preservation, and values larger than `uint16`.
- `TestConcurrentBasic`, `TestConcurrentBasicBigValues`, and `TestOneKey` stress concurrent `Put`/`Get`, including many goroutines updating one key.
- `TestFindNear`, `TestIteratorNext`, `TestIteratorPrev`, and `TestIteratorSeek` verify exact search and traversal contracts.
- Benchmarks compare skiplist mixed read/write behavior to a locked map and measure concurrent writes.

## Control Flow and State Behavior
Tests build skiplists with a fixed arena size, insert timestamped keys using `y.KeyWithTs`, and assert results through `Get` and direct iterator reads. The refcount check in `TestEmpty` intentionally decrements the list before closing an iterator, proving the iterator's extra reference keeps the arena valid until `Close`.

Concurrent tests use `sync.WaitGroup` to launch many writers, then readers, and verify list length to ensure duplicate node insertion did not happen. The one-key test accepts nondeterministic final value but enforces that all observed values are from the valid write set and only one node remains.

## Dependencies and Integration Points
The tests use `testify/require`, Go's `sync`, `sync/atomic`, `rand`, and `testing` packages, plus Badger's `y` key helpers. They directly access unexported skiplist internals because they are in package `skl`.

## Risks and Edge Cases
The tests exercise concurrency but do not make outcomes deterministic enough to prove every interleaving. Benchmarks are not pass/fail correctness gates. The large-value tests validate arena value storage beyond small fixed widths, but they do not exhaust arena capacity failure behavior.

## Test Signals
The strongest behavioral signals are the `findNear` matrix for less/greater and equal/non-equal cases, iterator seek boundary checks before first/after last, and length assertions after concurrent duplicate-key writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/skl/skl_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/stream.go -->
# sources/storage-engines/badger/stream.go

## Purpose
This file implements Badger's `Stream` framework: a concurrent, snapshot-based scanner that partitions the keyspace into ranges, converts keys into protobuf KV lists, batches them into buffers, and serially calls a user-supplied `Send` callback. It is intended for backups, replication, and fast export/import workflows.

## Important APIs, Types, and Functions
- `Stream` exposes `Prefix`, `NumGo`, `LogPrefix`, `ChooseKey`, `KeyToList`, thread-id aware callbacks, `Send`, `SinceTs`, and soft `MaxSize`.
- `SendDoneMarkers` enables per-stream completion markers.
- `ToList` is the default highest-key-to-all-valid-versions conversion.
- `produceRanges` asks the DB for range splits and feeds them largest-first.
- `produceKVs` owns per-worker transactions, iterators, allocators, stream IDs, and per-range conversion.
- `streamKVs` serially drains producer buffers, slurps additional buffers up to `MaxSize`, logs rates, and calls `Send`.
- `Orchestrate` wires goroutines, cancellation, channels, defaults, and error propagation.
- `BufferToKVList` and `KVToBuffer` convert between protobuf KVs and `z.Buffer` slice records.

## Control Flow and State Behavior
`Orchestrate` creates a cancellable context, a range channel, and a bounded KV buffer channel. One goroutine produces key ranges. `NumGo` producer goroutines open read-only transactions at `readTs` when managed or a normal snapshot otherwise. Each range iterator scans all versions with optional prefix and `SinceTs`, skips duplicate logical keys by tracking `prevKey`, applies `ChooseKey` only to the highest version, and calls either `KeyToList` or `KeyToListWithThreadId`. Returned KVs receive a per-range `StreamId` and are encoded into `z.Buffer` batches.

The sender goroutine is deliberately single-threaded. It releases every buffer after send, tracks ETA/rate logging, and merges immediately available producer buffers into larger send batches until `MaxSize` is exceeded. Context cancellation stops producers if sending fails.

## Dependencies and Integration Points
The code depends on Badger `DB`, `Txn`, `Iterator`, protobuf package `pb`, `y` utilities, `z.Buffer` and `z.Allocator`, and `humanize` for logs. It integrates directly with `StreamWriter`: KVs include `StreamId` and optional `StreamDone` markers that the writer uses to demultiplex sorted streams.

## Risks and Edge Cases
`Send` is serial, but `ChooseKey` and key-to-list callbacks are concurrent and must be thread-safe unless the thread-id API is used. Custom `KeyToList` must stop on the first mismatching key or it can consume keys owned by the stream framework. The batch limit is soft: a single oversized list can exceed `MaxSize`. Buffer and allocator lifetimes are owned by the framework; retaining returned slices outside `Send` requires copying.

## Test Signals
`stream_test.go` verifies full and prefix scans, `ChooseKey`, thread-id propagation, manual large streams and max-size behavior, and a custom `KeyToList` regression around allocator ownership.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/stream.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/stream_test.go -->
# sources/storage-engines/badger/stream_test.go

## Purpose
This file tests the `Stream` export framework over managed Badger databases. It validates range streaming, prefix filtering, key selection, thread-id exposure, manual large-dataset behavior, and custom key-to-list callback ownership.

## Important Tests and Helpers
- `keyWithPrefix`, `keyToInt`, and `value` create predictable key/value fixtures.
- `collector.Send` decodes stream buffers with `BufferToKVList`, clones KVs, and ignores stream done markers.
- `TestStream` writes three prefixes at a managed timestamp and checks full export, prefix export, even-key selection within a prefix, and even-key selection across all prefixes.
- `TestStreamMaxSize` and `TestBigStream` are manual large tests that temporarily reduce `maxStreamSize` and stream millions of keys.
- `TestStreamWithThreadId` verifies each iterator's `ThreadId` is below `NumGo`.
- `TestStreamCustomKeyToList` checks a prior allocator double-free bug path by returning a custom list that copies item key/value data.

## Control Flow and State Behavior
Tests use `OpenManaged`, create transactions at `math.MaxUint64`, commit at timestamp 5, and stream at `math.MaxUint64` to include all data. The collector accumulates decoded protobuf KVs, then assertions count keys per prefix and verify values. `ChooseKey` is reassigned between orchestrations, demonstrating that a stream object can be reused serially after resetting relevant fields.

## Dependencies and Integration Points
The tests use `badger.Stream`, managed transactions, `pb.KV`, `z.Buffer`, protobuf cloning, and Badger item value APIs. They rely on `ctxb = context.Background()` and on test helpers such as `removeDir`.

## Risks and Edge Cases
The manual tests are skipped unless a manual flag is set, so routine test runs do not cover very large streams or soft max-size behavior. `collector.Send` ignores done markers, which is appropriate for these assertions but not a full restore protocol validation. The custom callback test intentionally returns only one version per key, so it validates callback ownership more than default version enumeration.

## Test Signals
The file gives strong evidence that `Stream.Orchestrate` respects prefix and `ChooseKey`, preserves values, supports thread IDs, and tolerates custom `KeyToList` without allocator lifetime regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/stream_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/stream_writer.go -->
# sources/storage-engines/badger/stream_writer.go

## Purpose
This file implements `StreamWriter`, Badger's fast ingest path for data produced by streams. It writes sorted, non-overlapping stream ranges directly into SSTables and value logs, bypassing normal transactional write amplification and compactions. It supports destructive restore (`Prepare`) and incremental ingest (`PrepareIncremental`).

## Important APIs, Types, and Functions
- `DB.NewStreamWriter` constructs a writer with shared throttle and per-stream sorted writers.
- `Prepare` drops all existing data and installs a `done` callback to restore DB services.
- `PrepareIncremental` stops writes/compactions, checks memtables are empty, finds a target level above existing data, and may call `Flatten`.
- `Write` decodes protobuf KVs from a `z.Buffer`, groups by `StreamId`, writes values to the value log, feeds per-stream `sortedWriter`s, and handles `StreamDone` markers.
- `Flush` closes all writers, updates the oracle for unmanaged DBs, waits on asynchronous table creation, sorts level tables, syncs directories, and validates levels.
- `Cancel` unblocks writer goroutines and restores services without calling `dropAll`.
- `sortedWriter.Add`, `send`, `Done`, and `createTable` enforce sorted keys and build/register SSTables.

## Control Flow and State Behavior
`Write` first scans the incoming buffer. It tracks closed stream IDs within the buffer and panics if a KV appears after a done marker. It updates `maxVersion`, initializes `prevLevel` to the number of levels on first full write, converts protobuf fields into `Entry` values with timestamped keys, and groups them into value-log write requests. Under `writeLock`, the value log is written before requests are sent to sorted writer goroutines. Each sorted writer consumes requests serially, converts entries to `ValueStruct`s or value pointers, and appends to a table builder. Capacity boundaries flush builders asynchronously through a throttle.

`Flush` is the durability barrier. For unmanaged mode, it stops and recreates the oracle so future transaction timestamps advance beyond streamed versions and marks watermarks complete. Table creation reserves file IDs, writes in-memory or disk SSTables, records manifest create changes, inserts tables into the target level, and releases the table open reference.

## Dependencies and Integration Points
This code integrates with `DB.dropAll`, `prepareToDrop`, compaction control, value log write requests, manifest changes, level controller, table builder/opening, and oracle timestamp management. It consumes buffers produced by `Stream.KVToBuffer` and protobuf `pb.KV`.

## Risks and Edge Cases
The API is dangerous on active DBs: `Prepare` deletes existing data and assumes exclusive bootstrap use. Input must be sorted per stream and streams must not overlap; `sortedWriter.Add` rejects non-increasing timestamped keys. `StreamDone` closes a stream permanently. Partial writes after `Cancel` remain until a later `Prepare` drops them. Incremental mode refuses non-empty memtables and relies on level placement to avoid compaction conflicts.

## Test Signals
`stream_writer_test.go` covers normal, managed, and in-memory restore; post-restore writes/deletes; oracle reinitialization; boundary keys; same-user-key table grouping; cancel behavior; done markers and closed-stream panics; encrypted writes; large values; and repeated incremental ingestion.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/stream_writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/stream_writer_test.go -->
# sources/storage-engines/badger/stream_writer_test.go

## Purpose
This test file validates `StreamWriter` restore and incremental-ingest behavior across normal, managed, in-memory, encrypted, large-value, and stream-marker scenarios. It is the main behavioral evidence for direct SSTable ingestion.

## Important Tests and Helpers
- `getSortedKVList` builds a `z.Buffer` of protobuf KVs sorted by big-endian uint64 key.
- `TestStreamWriter1` verifies basic restore and reads in normal, managed, and in-memory modes.
- `TestStreamWriter2` and `TestStreamWriter3` check post-restore deletes and inserts through normal transactions.
- `TestStreamWriter4` validates oracle reinitialization after restore.
- `TestStreamWriter5` checks extreme byte-prefix keys survive reopen.
- `TestStreamWriter6` ensures multiple versions of the same logical key stay in the same table.
- `TestStreamWriterCancel`, `TestStreamDone`, `TestSendOnClosedStream`, and `TestSendOnClosedStream2` cover lifecycle and stream closure.
- `TestStreamWriterEncrypted`, `TestStreamWriterWithLargeValue`, and `TestStreamWriterIncremental` exercise encryption, large values, and incremental mode.

## Control Flow and State Behavior
Most tests create serialized KV buffers, call `NewStreamWriter`, `Prepare` or `PrepareIncremental`, `Write`, and `Flush`, then verify through Badger reads and iteration. Managed-mode tests set transaction read/commit timestamps explicitly after restore. Incremental tests repeatedly add small non-overlapping sets, verify existing data remains visible, and check that an intervening normal write leaves memtable data that causes `PrepareIncremental` to fail.

Closed-stream tests construct buffers with `StreamDone` markers and assert that sending another KV for the same stream either later or within the same buffer panics. The cancel test intentionally omits `Flush` and calls `Cancel` to ensure goroutines unblock and cleanup is idempotent enough for deferred use.

## Dependencies and Integration Points
The tests use Badger test helpers (`runBadgerTest`, `getTestOptions`), protobuf `pb.KV`, `z.Buffer`, direct transaction APIs, DB reopen, table metadata via `db.Tables`, and encryption options.

## Risks and Edge Cases
The tests assume sorted input unless deliberately testing same-key grouping. They validate many lifecycle hazards but do not prove safe concurrent calls from many goroutines despite `Write` being documented thread-safe. Some assertions rely on reopen success to catch manifest/table registration problems.

## Test Signals
The strongest signals are oracle timestamp repair, closed-stream panic enforcement, encrypted restore plus reopen, large-value managed mode, and incremental refusal when memtables contain data.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/stream_writer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/structs.go -->
# sources/storage-engines/badger/structs.go

## Purpose
This file defines core Badger storage structs shared by transaction, value-log, and table-writing code: value pointers, value-log entry headers, and user-facing `Entry` values.

## Important APIs, Types, and Functions
- `valuePointer` identifies value-log location by file ID, length, and offset.
- `valuePointer.Less`, `IsZero`, `Encode`, and `Decode` support ordering, sentinel checks, and compact unsafe byte representation.
- `header` stores value-log entry metadata: key length, value length, expiration, internal meta, and user meta.
- `header.Encode`, `Decode`, and `DecodeFrom` serialize/deserialize the value-log header with varints.
- `Entry` is the user-facing mutation object used by transactions and stream writer.
- `NewEntry`, `WithMeta`, `WithDiscard`, `WithTTL`, and `withMergeBit` configure entries.
- `estimateSizeAndSetThreshold` and `skipVlogAndSetThreshold` decide whether values are inline or value-log pointers.

## Control Flow and State Behavior
`valuePointer.Encode` allocates a fixed-size byte slice and writes the struct into it. `Decode` copies bytes into the receiver rather than assigning through an unsafe pointer, avoiding alignment issues. `header.Encode` writes fixed meta bytes followed by unsigned varints for key/value lengths and expiration. `DecodeFrom` reads from a `hashReader` while tracking bytes read, allowing value-log parsing to include checksum accounting.

`Entry` carries mutable internal fields such as commit version, value-log offset, header length, and threshold cache. Size estimation stores the threshold the first time it is used, then estimates either key+value+metas for inline values or key+pointer+metas for value-log values.

## Dependencies and Integration Points
`Entry` is consumed by `Txn.modify`, write batching, value-log writes, and `StreamWriter`. `valuePointer` is encoded into `ValueStruct.Value` with the `bitValuePointer` meta bit and decoded by readers that need to fetch value-log data. `header` is the on-disk value-log record prefix.

## Risks and Edge Cases
Unsafe encoding ties `valuePointer` layout to architecture assumptions; the file mitigates decode alignment issues but still relies on fixed struct size. Header max size must track the field set and varint limits. `WithMeta` sets `UserMeta`, not internal `meta`, which is intentional public API behavior but easy to misread. Threshold caching means callers should not expect changing DB thresholds to alter a reused entry's estimate.

## Test Signals
`structs_test.go` checks that maximum-width header fields encode without panic and that `header` still has five fields, guarding `maxHeaderSize` assumptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/structs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/structs_test.go -->
# sources/storage-engines/badger/structs_test.go

## Purpose
This small regression test file protects value-log header encoding assumptions from `structs.go`.

## Important Tests
- `TestLargeEncode` constructs a `header` with maximum `uint32`, `uint64`, and `uint8` field values and asserts `Encode` does not panic when given a `maxHeaderSize` buffer.
- `TestNumFieldsHeader` asserts `header` has exactly five fields.

## Control Flow and State Behavior
The tests do not write a value log. Instead, they validate the sizing contract around varint-encoded headers and the structural field count that `maxHeaderSize` comments depend on.

## Dependencies and Integration Points
The tests use `math`, `reflect`, `testing`, and `testify/require`. They are in package `badger`, so they can access the unexported `header` type and `maxHeaderSize`.

## Risks and Edge Cases
This is a narrow guard. It does not round-trip decode, test `DecodeFrom`, or validate malformed input. Its main value is catching accidental header field additions or max-size underestimation.

## Test Signals
The file signals that changing `header` layout or encoded-size assumptions must be accompanied by updates to `maxHeaderSize` and related value-log parsing expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/structs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/table/builder.go -->
# sources/storage-engines/badger/table/builder.go

## Purpose
This file builds Badger SSTable files. It accumulates sorted key/value pairs into prefix-compressed blocks, optionally compresses and encrypts blocks, writes per-block checksums, builds a FlatBuffer table index with bloom filters and table metadata, and returns either bytes or structured build data for file creation.

## Important APIs, Types, and Functions
- `Builder` owns allocator state, current block, block list, size counters, key hashes, options, max version, stale data size, and optional compression workers.
- `NewTableBuilder` initializes allocator/block state and starts block worker goroutines when compression or encryption is enabled.
- `Add`, `AddStaleKey`, `addInternal`, and `addHelper` append entries and split blocks.
- `finishBlock` writes entry offsets and checksum and queues background compression/encryption.
- `ReachedCapacity` estimates whether the table is near configured capacity.
- `Finish` and `Done` finalize all blocks, build the index, and compute final table size.
- `encrypt`, `compressData`, `buildIndex`, and block-offset writers implement format details.

## Control Flow and State Behavior
Each block starts with a base key. Subsequent entries store a 4-byte `header` with overlap and diff length, followed by the key suffix and encoded `ValueStruct`. Entry offsets are collected for binary search. When `shouldFinishBlock` estimates the next entry would exceed `BlockSize`, the current block is finalized and a fresh block is allocated.

If compression or encryption is active, finalized blocks are sent to worker goroutines. `Done` closes the channel, waits for workers, builds an optional bloom filter from parsed user-key hashes, writes FlatBuffer `TableIndex` metadata, optionally encrypts the index, and appends index/checksum length footers. `buildData.Copy` lays blocks, index, index length, checksum, and checksum length into the final byte sequence.

## Dependencies and Integration Points
The builder is consumed by table creation, normal flush/compaction paths, and `StreamWriter.sortedWriter`. It depends on Badger flatbuffers (`fb`), protobuf checksums (`pb`), compression libraries (`s2`, ZSTD helpers), encryption helpers, options, and `z.AllocatorPool`.

## Risks and Edge Cases
The builder assumes keys are added in sorted order by callers; it does not enforce ordering itself. Size estimates are intentionally rough and include comments noting discrepancies. Compression/encryption workers must be drained by `Done`; `Close` should return the allocator after finish. Unsafe header encode/decode must match iterator expectations. Encryption appends IVs, so readers must use matching `DataKey`.

## Test Signals
`builder_test.go` validates block indexes under no compression, encryption, compression, and both; invalid decompression errors; bloom filter behavior; empty builders; and performance benchmarks for compression/encryption modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/table/builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/table/builder_test.go -->
# sources/storage-engines/badger/table/builder_test.go

## Purpose
This file tests SSTable builder output, table indexes, compression/encryption compatibility, bloom filters, empty builders, and builder performance.

## Important Tests and Benchmarks
- `TestTableIndex` writes 100,000 keys and verifies that index block offsets contain exactly the first key of each block across four option combinations: plain, encrypted, compressed, and compressed+encrypted.
- `TestInvalidCompression` opens a ZSTD-built table with correct and incorrect compression options and expects the incorrect option to fail.
- `TestBloomfilter` checks `DoesNotHave` with and without bloom filters in forward and reverse iteration.
- `TestEmptyBuilder` asserts an empty builder finishes to an empty byte slice.
- `BenchmarkBuilder` measures building 1.3M entries under no compression, encryption, Snappy, and multiple ZSTD levels.

## Control Flow and State Behavior
`TestTableIndex` mirrors the builder's own `shouldFinishBlock` decisions to track expected block first keys, then creates a table and reads the FlatBuffer index back for comparison. The test also checks key ID behavior in unencrypted mode and max version metadata.

Bloom tests build tables with and without filters, iterate all entries to verify present keys are never rejected, then probe an absent hash to confirm filters are active only when configured.

## Dependencies and Integration Points
The tests use `table.CreateTable`, `buildTestTable` from `table_test.go`, Badger options, FlatBuffer table indexes, protobuf data keys, Ristretto index cache for encryption, and `y` hashing/timestamp helpers.

## Risks and Edge Cases
The test reads indexes directly but does not independently parse raw SST bytes. Random file names in temp directories require cleanup via table close/remove. The invalid compression test reuses a table mmap and relies on open-time decode behavior to detect the mismatch.

## Test Signals
These tests provide strong format-level confidence for index offsets, encryption/index-cache requirements, compression option mismatches, bloom filter presence, and empty-output handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/table/builder_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/table/iterator.go -->
# sources/storage-engines/badger/table/iterator.go

## Purpose
This file implements SSTable block iteration, table iteration, and concatenated table iteration. It decodes the prefix-compressed block format produced by `builder.go`, navigates across table blocks, and exposes forward or reversed `y.Iterator` behavior.

## Important APIs, Types, and Functions
- `blockIterator` holds decoded block state: data, entry index, base key, current key/value, offsets, table/block IDs, and overlap cache.
- `setBlock`, `setIdx`, `seek`, `seekToFirst`, `seekToLast`, `next`, and `prev` implement in-block navigation.
- `Iterator` wraps a `Table` and a `blockIterator`, with `NewIterator`, `Close`, `Seek`, `Rewind`, `Next`, `Key`, `Value`, and `ValueCopy`.
- Constants `REVERSED` and `NOCACHE` configure direction and block-cache use.
- `ConcatIterator` lazily opens table iterators over non-overlapping tables and moves between them.

## Control Flow and State Behavior
`blockIterator.setIdx` reconstructs the current key by decoding the entry header, reusing previous overlap state to avoid unnecessary base-key copies, and slicing the encoded value bytes. Invalid indexes set `io.EOF`. A recovery block adds detailed table/block/index diagnostics if malformed block data panics during slicing.

`Iterator.seekFrom` binary-searches table block offsets for the block whose smallest key bounds the target, then seeks inside that block. If the target is beyond that block, it advances to the next block. Forward and reverse public methods dispatch to internal `next`/`prev` based on `REVERSED`. `Close` releases the current block and decrements the table reference.

`ConcatIterator` assumes its tables are ordered and non-overlapping. It increments table refs on construction, lazily constructs table iterators, seeks to the table whose range can contain the key, and advances table-by-table.

## Dependencies and Integration Points
The file depends on `Table.block`, FlatBuffer block offsets, builder's block header encoding, and `y.CompareKeys`/`ValueStruct`. It is used by Badger levels, compaction, reads, and merge iterators.

## Risks and Edge Cases
Correctness depends on block offset metadata, prefix-compression decode alignment, and table range ordering for concat iteration. `seekForPrev` performs a forward seek and then `prev`, with a TODO noting possible optimization. `Close` must be called to release table and block refs. `Iterator.Valid` reflects `itr.err == nil`; callers should not use `Key`/`Value` after invalidation.

## Test Signals
`table_test.go` exercises seek boundaries, forward/backward movement, full scans, reverse iteration, concat iteration over multiple tables, and large values.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/table/iterator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/table/merge_iterator.go -->
# sources/storage-engines/badger/table/merge_iterator.go

## Purpose
This file implements a duplicate-suppressing merge iterator over multiple sorted `y.Iterator`s. It is used to merge overlapping table, level, or memtable iterator streams while choosing one value for duplicate keys and supporting forward or reverse traversal.

## Important APIs, Types, and Functions
- `MergeIterator` stores left/right merge tree nodes, the currently selected node (`small`), current key copy, and direction.
- Internal `node` wraps a `y.Iterator` and caches concrete `MergeIterator` or `ConcatIterator` pointers for faster calls.
- `node.setIterator`, `setKey`, `next`, `rewind`, and `seek` abstract over raw, merge, and concat iterators.
- `fix` enforces which child should be current and advances duplicate keys on the right side.
- `Next`, `Rewind`, `Seek`, `Valid`, `Key`, `Value`, and `Close` implement `y.Iterator`.
- `NewMergeIterator` recursively builds a balanced binary merge tree.

## Control Flow and State Behavior
The merge iterator compares the selected node against the other node. In forward mode it keeps the smallest key; in reverse mode it keeps the largest key. When both keys compare equal, `fix` advances the right iterator and may swap selected nodes. `Next` also skips any key equal to the previously emitted `curKey`, so repeated duplicates within one child are suppressed.

`Rewind` and `Seek` reposition both children, call `fix`, and copy the selected key into `curKey`. `Value` delegates to the currently selected iterator. The recursive constructor returns nil for zero iterators, the original iterator for one, and nested merge iterators for larger sets.

## Dependencies and Integration Points
The implementation depends only on `bytes` and Badger `y.Iterator`/`CompareKeys`, with fast paths for `MergeIterator` and `ConcatIterator`. It is central to composing level/memtable views where newer sources should appear earlier in iterator ordering to win duplicate suppression.

## Risks and Edge Cases
Duplicate winner semantics depend on iterator ordering. In forward duplicates, the left side wins; in reverse, tests show the winner can be the later duplicate within the selected iterator due to reverse traversal. `Valid` assumes `small` has been initialized by `Rewind` or `Seek`; callers should position before use. `Close` closes both child iterators and wraps errors.

## Test Signals
`merge_iterator_test.go` covers zero/single/nested/many iterators, duplicates within and across iterators, forward/reverse seek, invalid seeks, close-count ownership, and winner behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/table/merge_iterator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/table/merge_iterator_test.go -->
# sources/storage-engines/badger/table/merge_iterator_test.go

## Purpose
This file tests duplicate suppression, ordering, seeking, reversal, nesting, and ownership semantics for `MergeIterator`.

## Important Tests and Helpers
- `SimpleIterator` is a minimal `y.Iterator` implementation with configurable reverse behavior and global close counting.
- `newSimpleIterator`, `getAll`, `reversed`, and `closeAndCheck` support compact assertions.
- `TestSimpleIterator`, `TestMergeSingle`, and `TestMergeSingleReversed` verify baseline iterator behavior and single-iterator passthrough.
- `TestMergeMore`, `TestMergeIteratorNested`, and `TestMergeIteratorDuplicate` cover multiple iterators, nested merge construction, and duplicate winner semantics.
- `TestMergeIteratorSeek`, `TestMergeIteratorSeekReversed`, and invalid variants validate seek boundaries.
- `TestMergeDuplicates` stresses repeated duplicate keys in every child.

## Control Flow and State Behavior
The tests build ordered key/value slices, call `NewMergeIterator`, position with `Rewind` or `Seek`, then drain with `getAll`. For duplicate cases, expected values encode which iterator should win. Reverse tests mutate `SimpleIterator.reversed` and expect descending keys with corresponding winner changes. Close tests verify that the merge iterator owns and closes every underlying iterator.

## Dependencies and Integration Points
The file uses `testify/require`, `sort`, `testing`, and Badger `y` helpers. Its simple iterator implements exactly the public iterator contract consumed by the merge logic, making it independent of table storage.

## Risks and Edge Cases
The tests focus on string keys at timestamp zero, so they do not separately exercise timestamp ordering beyond `y.KeyWithTs`. They do not call `Valid` before positioning, which matches expected use. Because `closeCount` is global, tests are structured serially rather than parallel.

## Test Signals
The suite gives clear evidence that merge iteration suppresses duplicates, preserves direction, handles invalid seeks, closes owned children, and respects iterator input order for conflict resolution.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/table/merge_iterator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/table/table.go -->
# sources/storage-engines/badger/table/table.go

## Purpose
This file implements loading, reading, caching, checksum verification, decryption, decompression, metadata access, and lifecycle management for Badger SSTable files.

## Important APIs, Types, and Functions
- `Options` configures table size, block size, bloom filters, checksum verification, compression, encryption, block/index caches, metrics, and allocator pool.
- `Table` wraps an mmap file, cheap index metadata, optional full index, table key bounds, file ID, checksum/index positions, refcount, and options.
- `CreateTable`, `OpenTable`, and `OpenInMemoryTable` create or load tables.
- Metadata methods include `MaxVersion`, `BloomFilterSize`, `UncompressedSize`, `KeyCount`, `OnDiskSize`, `CompressionType`, `Smallest`, `Biggest`, `ID`, `KeyID`, and `StaleDataSize`.
- `block`, `fetchIndex`, `readTableIndex`, `VerifyChecksum`, `DoesNotHave`, `KeySplits`, `ParseFileID`, `IDToFilename`, and `NewFilename` implement read and utility behavior.
- `Block` owns decoded block bytes, entry offsets, checksum, and refcount/freeing state.

## Control Flow and State Behavior
`CreateTable` finalizes a builder, mmaps a newly created file, copies build data, msyncs it, and opens the table. `OpenTable` validates filename ID, initializes refcount, reads table index/footer/checksum, initializes smallest and biggest keys, and optionally verifies checksums. `initIndex` reads footer checksum length, checksum, index length, and index bytes; verifies the index checksum; reads the FlatBuffer index; caches cheap metadata; and records whether a bloom filter exists.

For reads, `block` checks block cache, increments block refs safely, reads the block bytes, decrypts and decompresses as configured, parses checksum and entry offset metadata, verifies block checksums according to mode, and optionally admits the block to cache. `DecrRef` deletes cached blocks and the table file when the final reference drops. Encrypted tables do not retain `_index` directly and require an index cache.

## Dependencies and Integration Points
The table layer integrates with builder output, iterators, Ristretto block/index caches, level controller table lifecycle, manifest-created SST files, options, protobuf checksums, FlatBuffers, mmap files, and encryption/compression helpers.

## Risks and Edge Cases
Reference counting is critical: iterators, levels, and caches must not use deleted files or freed decompression buffers. Compression options must match the file; wrong options can produce decode/checksum errors. Encrypted workloads require `IndexCache`. `blockCacheKey` assumes IDs and indexes fit `uint32`. Corrupt metadata can panic in initialization paths, though recovery diagnostics are added for index crashes.

## Test Signals
`table_test.go` and `builder_test.go` cover opening, iteration, seek boundaries, bloom filters, checksum corruption, compression mismatch, large values, max version, concurrent `DoesNotHave`, and benchmarks.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/table/table.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/table/table_test.go -->
# sources/storage-engines/badger/table/table_test.go

## Purpose
This file provides broad tests and benchmarks for SSTable reading, iteration, concatenation, merge behavior with real tables, checksum validation, large values, bloom filters, race-sensitive lookup, and max-version metadata.

## Important Tests and Helpers
- `getTestTableOptions`, `buildTestTable`, and `buildTable` create sorted test SSTables.
- `TestTableIterator`, `TestSeekToFirst`, `TestSeekToLast`, `TestSeek`, `TestSeekForPrev`, `TestIterateFromStart`, `TestIterateFromEnd`, `TestTable`, `TestIterateBackAndForth`, and `TestUniIterator` validate table iterator navigation.
- `TestConcatIteratorOneTable` and `TestConcatIterator` validate ordered table concatenation forward and reverse.
- `TestMergingIterator`, reversed variants, and take-one/take-two cases test merge iterator behavior with actual table iterators.
- `TestTableBigValues`, `TestTableChecksum`, `TestDoesNotHaveRace`, and `TestMaxVersion` cover storage edge cases.
- Benchmarks measure full scans, read-and-build, merged reads, checksum algorithms, and random reads.

## Control Flow and State Behavior
The helper sorts input key/value pairs, adds timestamped keys to a builder, creates an SSTable in the temp directory, and returns an open table whose ref must be decremented. Iterator tests position internal or public iterators, then compare parsed user keys and decoded values. Concat and merge tests compose table iterators to validate cross-table ordering and duplicate winner behavior.

Checksum testing deliberately corrupts table mmap bytes after building with checksum verification enabled and expects open/verification to panic or fail with checksum evidence. The race test concurrently calls `DoesNotHave` to exercise bloom/index access.

## Dependencies and Integration Points
The tests depend on `table.Builder`, `Table`, `Iterator`, `ConcatIterator`, `MergeIterator`, Badger `options`, `y` helpers, Ristretto cache, and standard hashing libraries for benchmarks.

## Risks and Edge Cases
Tests use temp files and rely on `DecrRef` for cleanup. Some benchmarks contain performance-only paths and are not routine correctness gates. `TestTableChecksum` mutates mmap data directly and accepts either panic or checksum error, reflecting multiple possible corruption detection points.

## Test Signals
The suite strongly validates iterator boundary behavior, block crossing, reverse traversal, concat range selection, duplicate merge behavior, corruption detection, big value decoding, bloom filter concurrency, and `MaxVersion` metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/table/table_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/test.sh -->
# sources/storage-engines/badger/test.sh

## Purpose
This shell script orchestrates Badger's local/CI test workflow. It runs Go tests with jemalloc tags, optional coverage collection, root tests, a stream benchmark/leak check, and manual memory-intensive tests in sequence.

## Important Functions and Commands
- Global setup prints `go version`, configures CI coverage flags, computes Badger package list via `go list`, and sets `tags="-tags=jemalloc"`.
- It builds the `badger` CLI before test execution.
- `root` runs root package tests with race detector, parallelism 16, timeout 25 minutes, and fail-fast.
- `stream` runs `badger benchmark write/read`, `badger stream`, and checks log output for zero allocated bytes at program end.
- `manual` runs all packages with race detector and a set of `--manual=true` targeted tests, including truncation, large key/value, value log limit, iteration, stream, goroutine leak, and get-more cases.
- `write_coverage` appends package coverage output into `cover.out` in CI.

## Control Flow and State Behavior
The script exits on errors via `set -eo pipefail`. In CI it prepares atomic coverage mode and a shared coverage file. It exports `packages` before setting `GOFLAGS` to preserve `go list` output format. The manual path sets `GOTOOLCHAIN=go1.25.0+auto`, iterates packages, and then runs individual manual tests. At the bottom, parallel execution is commented out; the active order is `root`, `stream`, `manual`.

The stream leak check creates a temp directory under `badger`, runs CLI operations, counts occurrences of `"at program end: 0 B"`, removes the temp directory, and fails unless four zero-allocation lines are present.

## Dependencies and Integration Points
The script depends on Bash, Go tooling, the Badger CLI package under `badger`, jemalloc build tags, `truncate`, and test flags such as `--manual=true`. It integrates with CI coverage collection through `cover.out`.

## Risks and Edge Cases
The script mutates global Go env with `go env -w GOTOOLCHAIN=...` inside `manual`. It assumes leak log text remains stable. Coverage merging uses `sed -i`, which is GNU-specific. Manual tests are expensive and run with race detector, so total runtime can be high. The stream temp directory is removed, but failures before cleanup inside some paths could leave artifacts.

## Test Signals
The script is itself a test runner rather than unit-tested code. Its signal is the sequencing of root, stream/leak, and manual stress tests used by the project.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/test_extensions.go -->
# sources/storage-engines/badger/test_extensions.go

## Purpose
This file adds lightweight test-only extension fields and helper methods to production Badger types without importing `testing`. It lets tests observe internal lifecycle events and capture discard statistics while keeping production behavior effectively no-op unless channels/maps are configured.

## Important APIs, Types, and Functions
- Constants `updateDiscardStatsMsg` and `endVLogInitMsg` define synchronization messages for tests.
- `testOnlyOptions` adds a `syncChan` to `Options`.
- `testOnlyDBExtensions` adds `syncChan` and `onCloseDiscardCapture` to `DB`.
- `(*DB).logToSyncChan` sends a message on the DB sync channel if present.
- `(*DB).captureDiscardStats` copies value-log discard stats into `onCloseDiscardCapture` during close if configured.

## Control Flow and State Behavior
The file relies on embedding or composition elsewhere in `Options` and `DB`. `logToSyncChan` silently does nothing when `syncChan` is nil; otherwise it sends synchronously, so tests can block until specific internal milestones happen. `captureDiscardStats` locks the value-log discard stats structure, iterates its contents, and copies ID/value pairs into a test-provided map.

## Dependencies and Integration Points
It integrates with value-log initialization, discard stats updates, and DB close paths that call these helper methods. It intentionally avoids importing `testing` so production package dependencies do not change.

## Risks and Edge Cases
Because this is compiled into production, a non-nil unbuffered `syncChan` can block production code if accidentally set outside tests. The comments note a possible future build-tag split. `captureDiscardStats` assumes `db.vlog` and its `discardStats` are valid when called. The map is caller-owned and not internally synchronized beyond the discardStats lock.

## Test Signals
There is no direct test file in this subset, but other Badger tests can use these hooks to wait for background events and inspect close-time discard accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/test_extensions.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/trie/trie.go -->
# sources/storage-engines/badger/trie/trie.go

## Purpose
This file implements a prefix trie with optional wildcard byte positions, used to map Badger match prefixes to table or stream IDs. It supports adding, deleting, and querying IDs associated with prefixes, including "holes" specified by index ranges.

## Important APIs, Types, and Functions
- `node` stores byte children, a wildcard `ignore` child, and IDs that match at that prefix.
- `Trie` owns a root node and is constructed by `NewTrie`.
- `parseIgnoreBytes` parses comma-separated indices and ranges like `"3, 5-8"`.
- `Add`, `AddMatch`, `Delete`, and `DeleteMatch` mutate the trie.
- Internal `fix` performs add/delete traversal for both exact and ignore-byte paths.
- `Get` and recursive `get` collect all IDs matching prefixes along a key path.
- `removeEmpty` prunes empty nodes after deletion; `numNodes` is a test helper.

## Control Flow and State Behavior
`AddMatch` parses ignore bytes into a boolean slice extended to the prefix length. For each prefix byte, exact positions traverse or create `children[byte]`, while ignored positions traverse or create the `ignore` branch. IDs are stored only at the terminal node for the prefix. Nil and empty prefixes attach IDs to the root, making them match every key.

`Get` starts at root, adds IDs at each visited node, recurses into the wildcard child if present with one byte consumed, and recurses into the exact child for the current byte. Results are deduplicated in a `map[uint64]struct{}`. Deletion removes matching IDs from the terminal node and then prunes empty branches without removing the root.

## Dependencies and Integration Points
The trie uses `pb.Match` for prefix and `IgnoreBytes` inputs, and `y.Check`/`AssertTrue` for simple error/assert handling. It likely supports match-based routing for stream/table selection where ranges can ignore timestamp or variable bytes.

## Risks and Edge Cases
The trie is not synchronized; callers must protect concurrent mutation/query if needed. `parseIgnoreBytes` does not reject reversed ranges explicitly, resulting in no range marks when start is greater than end. Invalid integer text propagates as errors. Wildcard recursion can branch exponentially with many ignore nodes, though expected match sets are likely small.

## Test Signals
`trie_test.go` validates basic prefix matching, nil/empty prefix behavior, deletion and pruning, ignore-byte parsing, wildcard matching with ranges, and deletion of wildcard matches.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/trie/trie.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/trie/trie_test.go -->
# sources/storage-engines/badger/trie/trie_test.go

## Purpose
This file tests the prefix trie in `trie.go`, including normal prefixes, nil/empty prefixes, deletion and pruning, ignore-byte parsing, and wildcard prefix matching.

## Important Tests
- `TestGet` adds overlapping prefixes and confirms that root/nil IDs and shorter prefix IDs are returned for matching keys.
- `TestTrieDelete` validates ID removal, deletion of nil-prefix IDs, idempotent deletion of absent IDs, and pruning back to a single empty root.
- `TestParseIgnoreBytes` checks single indices, zero index, and comma/range syntax with spaces.
- `TestPrefixMatchWithHoles` adds exact and wildcard matches, verifies expected match sets for several keys, then deletes wildcard and exact matches and checks node pruning.

## Control Flow and State Behavior
Tests call `Trie.Add`, `AddMatch`, `Get`, `Delete`, and `DeleteMatch`, then compare returned ID maps or sorted ID slices. `numNodes` is used as a structural signal that deletion prunes empty nodes. The wildcard test constructs `pb.Match` values with `IgnoreBytes` strings and uses sorted output to avoid map-order nondeterminism.

## Dependencies and Integration Points
The tests use `testify/require`, `sort`, `testing`, and protobuf `pb.Match`. They are in package `trie`, so they can inspect unexported helpers such as `parseIgnoreBytes` and `numNodes`.

## Risks and Edge Cases
The tests do not cover invalid ignore-byte strings, reversed ranges, negative indices, or concurrent access. They also do not benchmark wildcard-heavy tries. The existing coverage is focused on intended valid syntax and deletion idempotence.

## Test Signals
The test suite confirms that root IDs match all keys, shorter prefixes match longer keys, wildcard positions consume exactly one byte, and delete operations remove IDs and compact unused branches.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/trie/trie_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/txn.go -->
# sources/storage-engines/badger/txn.go

## Purpose
This file implements Badger transactions and the oracle that assigns timestamps, tracks pending reads/writes, detects conflicts, and provides serializable snapshot isolation for normal mode plus timestamp control for managed mode.

## Important APIs, Types, and Functions
- `oracle` tracks `nextTxnTs`, read and transaction watermarks, discard timestamp, committed transaction conflict keys, and locks for timestamp/write-channel ordering.
- `newOracle`, `readTs`, `newCommitTs`, `doneRead`, `doneCommit`, `discardAtOrBelow`, and cleanup methods manage MVCC timestamps and conflict history.
- `Txn` stores read/commit timestamps, DB pointer, read fingerprints, conflict keys, pending writes, duplicate managed writes, iterator count, lifecycle flags, and size/count accounting.
- `pendingWritesIterator` overlays uncommitted writes for iterators in update transactions.
- Mutation APIs include `Set`, `SetEntry`, `Delete`, and internal `modify`.
- Read/lifecycle/commit APIs include `Get`, `Discard`, `Commit`, `CommitWith`, `ReadTs`, `NewTransaction`, `View`, and `Update`.

## Control Flow and State Behavior
In unmanaged mode, `oracle.readTs` assigns a snapshot timestamp as `nextTxnTs-1`, marks the read, and waits for all transactions up to that timestamp to finish writing. Update transactions track read key fingerprints for conflict detection and write key fingerprints for committed conflict history. `newCommitTs` runs conflict checks under oracle lock, assigns or uses commit timestamps, begins transaction watermark tracking, and records committed conflict keys when enabled.

`Txn.modify` validates writeability, lifecycle, key/value sizes, banned prefixes, DB bans, and batch size limits; then records conflict keys and stores the entry in `pendingWrites`, preserving duplicate versions in managed mode. `Get` first checks pending writes for read-your-own-write behavior, then records read keys for update transactions and queries `db.get` at `KeyWithTs(key, readTs)`.

`commitAndSend` serializes commit timestamp assignment with write-channel submission, appends timestamp suffixes to keys, adds transaction markers when all writes share one timestamp, sends entries to the write channel, and returns a callback that waits for durability before marking the commit timestamp done. `Commit` blocks on that callback; `CommitWith` runs it asynchronously.

## Dependencies and Integration Points
Transactions integrate with DB write channel, value log/LSM writes, iterators, key timestamp helpers, oracle watermarks, managed transaction APIs, conflict detection, and compaction discard timestamps. They depend on `y.WaterMark`, `z.Closer`, `z.MemHash`, Badger errors, and internal meta bits such as `bitTxn`, `bitFinTxn`, and `bitDelete`.

## Risks and Edge Cases
The transaction object itself is not thread-safe except for read-key tracking needed by multiple iterators. Failing to call `Discard` can hold read watermarks and delay discard/compaction. Managed mode requires `CommitAt`/explicit timestamps; committing timestamp zero with transaction markers is rejected. Conflict detection uses hashed keys, so theoretical hash collisions can cause false conflicts. `CommitWith` callbacks run in goroutines and must handle errors.

## Test Signals
This subset does not include `txn_test.go`, but many stream writer tests exercise transactions after restore, managed timestamp setup, deletes, writes, and oracle reinitialization. Broader Badger tests likely cover SSI and iterator integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/txn.go -->
