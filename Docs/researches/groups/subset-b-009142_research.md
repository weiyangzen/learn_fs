# subset-b-009142 research

Grouped research report for selected Kopia internal files under `sources/sync-backup/kopia/internal`. Each section title preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/epoch/epoch_utils_test.go -->
# sources/sync-backup/kopia/internal/epoch/epoch_utils_test.go

Purpose: exercises epoch utility behavior used by Kopia repository epoch compaction and checkpoint bookkeeping. The tests cover parsing epoch numbers from blob IDs, grouping blob metadata by epoch number, integer sentinel constants, oldest-uncompacted epoch selection, and helper iterator transforms.

Important APIs/types/functions: `epochNumberFromBlobID`, `groupByEpochNumber`, `oldestUncompactedEpoch`, `getOldestUncompactedAfterEpoch`, `filterLowerThan`, `CurrentSnapshot`, `RangeMetadata`, `blob.Metadata`, `compactedEpochBlobPrefix`, and `rangeCheckpointBlobPrefix`. Local helpers synthesize single-epoch compaction sets and longest compacted ranges.

Control flow: table-driven tests feed representative blob IDs and snapshot states into unexported package functions. `TestOldestUncompactedEpoch` is the main behavioral matrix, mixing contiguous and non-contiguous single-epoch compaction sets with range checkpoint metadata and asserting either the next uncompacted epoch or `errInvalidCompactedRange`.

State/persistence behavior: no durable repository state is written, but the metadata shapes mirror persisted compaction and checkpoint blobs. The compatibility signal is important: non-contiguous single-epoch sets are intentionally accepted for older clients, while invalid compacted ranges are rejected.

Dependencies/integration: integrates with `repo/blob` metadata and epoch package internals. It also protects assumptions shared by epoch manager code that consumes compacted epoch sets and range checkpoint sets.

Risks/test signals: broad table coverage catches off-by-one errors around range ends, threshold filtering, and unsorted epoch input. The tests depend on access to unexported package functions and will need updates when epoch blob naming or compaction metadata semantics change.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/epoch/epoch_utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/faketime/faketime.go -->
# sources/sync-backup/kopia/internal/faketime/faketime.go

Purpose: provides deterministic and controllable time sources for tests. It avoids direct dependence on wall-clock time by returning functions compatible with code that expects `func() time.Time`.

Important APIs/types/functions: `Frozen`, `AutoAdvance`, `TimeAdvance`, `NewTimeAdvance`, `NewAutoAdvance`, `TimeAdvance.NowFunc`, `TimeAdvance.Advance`, `ClockTimeWithOffset`, `NewClockTimeWithOffset`, and `ClockTimeWithOffset.Advance`. `TimeAdvance` stores nanosecond deltas in `atomic.Int64`; `ClockTimeWithOffset` protects a mutable offset with a mutex.

Control flow: `Frozen` returns a closure over a fixed timestamp. `AutoAdvance` creates a `TimeAdvance` whose `NowFunc` atomically adds `autoDt` and returns the previous position, yielding `start`, then `start+dt`, and so on. Manual `Advance` mutates the same delta so future reads observe the jump.

State/persistence behavior: all state is in memory and test-scoped. `TimeAdvance` is monotonic under concurrent calls if advances are positive; `ClockTimeWithOffset` follows real `clock.Now()` plus a mutable offset rather than a frozen base.

Dependencies/integration: imports `internal/clock` for real clock reads in offset mode. It is used by storage/cache tests that need deterministic expiry or timestamp generation.

Risks/test signals: `NowFunc` returns a new closure each call but all closures share the same receiver state. Negative manual advances are not prohibited, so callers that require monotonic test time must avoid them.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/faketime/faketime.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/faketime/faketime_test.go -->
# sources/sync-backup/kopia/internal/faketime/faketime_test.go

Purpose: validates deterministic test-clock helpers, including frozen values, auto-advancing sequences, manual advancement, and concurrent use.

Important APIs/types/functions: `Frozen`, `AutoAdvance`, `NewTimeAdvance`, `NewAutoAdvance`, `TimeAdvance.Advance`, and returned `NowFunc` closures. The tests also use `clock.Now`, `sync.WaitGroup`, and randomized manual advances.

Control flow: `TestFrozen` checks repeated reads for fixed timestamps. `TestAutoAdvance` launches three goroutines, records 60 returned timestamps, and asserts uniqueness. `TestTimeAdvance` checks manual advancement from a fixed base. `TestTimeAdvanceConcurrent` mixes random calls to `Advance` with auto-advance reads and checks per-goroutine order plus global uniqueness.

State/persistence behavior: no persistent state. The tests stress shared atomic state in `TimeAdvance`, especially that concurrent auto increments do not duplicate timestamps.

Dependencies/integration: these tests protect consumers such as cache expiry tests from flakes caused by wall-clock timing. They also indirectly validate that `TimeAdvance.NowFunc` closures share one receiver.

Risks/test signals: the concurrency test uses `math/rand` without a fixed seed and validates broad invariants rather than exact sequences. It would not catch negative `Advance` misuse because only positive advances are generated.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/faketime/faketime_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/fault/fault.go -->
# sources/sync-backup/kopia/internal/fault/fault.go

Purpose: defines a configurable single fault used by test doubles and storage wrappers to inject delays, callbacks, and replacement errors.

Important APIs/types/functions: `Fault`, `New`, `ErrorInstead`, `ErrorCallbackInstead`, `Before`, `Repeat`, and `SleepFor`. Internal fields include `repeatCount`, `sleep`, `callback`, and `errCallback`, all protected by a mutex.

Control flow: builder-style methods lock the fault, mutate one behavior field, unlock, and return the same receiver for chaining. `ErrorInstead` wraps a fixed error in a callback; `ErrorCallbackInstead` stores dynamic error computation; `Before` stores a side-effect callback; `Repeat` controls how many extra invocations the fault remains queued; `SleepFor` sets a delay.

State/persistence behavior: state is in-memory and mutable. The fault itself does not execute; `fault.Set` owns call counting, queue consumption, sleeps, and callback invocation.

Dependencies/integration: uses only `sync` and `time`, but is tightly coupled to `fault_set.go` which reads these fields under locks. It is typically used by tests that need deterministic failure injection in repository or blob operations.

Risks/test signals: multiple builder calls overwrite prior callbacks or errors. The repeat counter semantics are implemented externally, so callers must understand that `Repeat(n)` means the fault is observed while the set decrements the count before removing it.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/fault/fault.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/fault/fault_set.go -->
# sources/sync-backup/kopia/internal/fault/fault_set.go

Purpose: manages queues of injectable faults per method and records method call counts for tests.

Important APIs/types/functions: `Method`, `Set`, `NewSet`, `AddFault`, `AddFaults`, `NumCalls`, `VerifyAllFaultsExercised`, and `GetNextFault`. The set stores `map[Method][]*Fault` and `map[Method]int` behind a locker.

Control flow: methods add faults to a FIFO queue. `GetNextFault` increments the call counter, selects the first queued fault, locks both set and fault long enough to decrement `repeatCount` or remove the fault, then releases locks before sleeping and invoking callbacks. If an error callback exists, it returns `(true, err)`; otherwise it returns `(false, nil)` even if a before-callback or sleep ran.

State/persistence behavior: all state is memory-local. Queued faults are consumed over time, and `VerifyAllFaultsExercised` fails a test if any configured fault remains.

Dependencies/integration: depends on `testing` for verification, `context` plus repository logging for debug messages, and `Fault` internals from `fault.go`. Integrates with test-only storage or service wrappers that call `GetNextFault` before real methods.

Risks/test signals: callbacks run without locks, which is good for deadlock avoidance but means callbacks observe external state only. `time.Sleep` ignores context cancellation. There are no direct tests in this subset, so coverage likely comes from packages that use fault injection.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/fault/fault_set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/feature/feature.go -->
# sources/sync-backup/kopia/internal/feature/feature.go

Purpose: models repository/client feature compatibility and produces user-facing messages when a client does not understand a required feature.

Important APIs/types/functions: `IfNotUnderstood`, `Feature`, `Required`, `Required.UnsupportedMessage`, `GetUnsupportedFeatures`, and `isSupported`. JSON tags indicate these structures are serialized in repository metadata or manifests.

Control flow: `GetUnsupportedFeatures` iterates required features and appends those absent from the supported feature slice. `UnsupportedMessage` composes a base message with optional custom text, documentation URL, and upgrade recommendation.

State/persistence behavior: the package has no mutable runtime state. Persistence concerns are in the JSON shape, especially optional fields under `IfNotUnderstood`.

Dependencies/integration: uses `slices.Contains` for feature membership. Upstream code can fail, warn, or guide upgrades based on returned unsupported `Required` values.

Risks/test signals: matching is exact string equality with no version ranges or aliases. `IfNotUnderstood.Warn` is stored but not interpreted here, so callers must enforce warning-versus-failure behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/feature/feature.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/feature/feature_test.go -->
# sources/sync-backup/kopia/internal/feature/feature_test.go

Purpose: verifies feature compatibility filtering and unsupported-feature message composition.

Important APIs/types/functions: `feature.Required`, `feature.Feature`, `feature.GetUnsupportedFeatures`, `Required.UnsupportedMessage`, and `IfNotUnderstood` fields `Message`, `URL`, and `UpgradeToVersion`.

Control flow: `TestFeature` runs table cases for nil inputs, partial support, and full support. `TestFeatureUnsupportedMessage` maps representative `Required` values to exact expected strings.

State/persistence behavior: no persistent state is used. The tests indirectly protect JSON-facing field semantics by exercising zero-value behavior and optional message fragments.

Dependencies/integration: uses `testify/require`. The tests define package `feature_test`, so they exercise only the exported API.

Risks/test signals: message assertions are exact, so intended wording changes require test updates. The tests do not cover `Warn` because warning policy is implemented by callers rather than this package.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/feature/feature_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/freepool/freepool.go -->
# sources/sync-backup/kopia/internal/freepool/freepool.go

Purpose: wraps `sync.Pool` with typed generics and a mandatory cleanup step before objects are returned to the pool.

Important APIs/types/functions: `Pool[T]`, `Take`, `Return`, `New`, and `NewStruct`. `NewStruct` creates a pool that resets returned values to a supplied clean struct value.

Control flow: `Take` calls `sync.Pool.Get` and type-asserts to `*T`; pool `New` guarantees a pointer if callers do not insert invalid values. `Return` calls the configured cleaner before putting the object back. `New` wires the allocation and cleanup callbacks into `sync.Pool.New`.

State/persistence behavior: the pool is process-local and non-deterministic like `sync.Pool`; the runtime may drop cached values. No persistence or ordering guarantees exist.

Dependencies/integration: uses only `sync`. Intended for reusable structures that are expensive enough to benefit from pooling and can be safely reset.

Risks/test signals: `Return(nil)` or an invalid object inserted through `sync.Pool` would panic or misbehave; the API does not guard against nil. Cleanup correctness is entirely caller-provided except for `NewStruct`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/freepool/freepool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/freepool/freepool_test.go -->
# sources/sync-backup/kopia/internal/freepool/freepool_test.go

Purpose: validates typed object pooling, cleanup-on-return, and basic reuse behavior.

Important APIs/types/functions: `freepool.NewStruct`, `freepool.New`, `Pool.Take`, and `Pool.Return`. The tests use integer and simple struct values.

Control flow: `TestNewStruct` takes a clean struct, mutates it, returns it, and expects the next taken value to be reset. `TestNew` performs the same pattern with explicit maker and cleaner callbacks. `TestPool_MultipleItems` checks that two simultaneously checked-out items are distinct before and after return.

State/persistence behavior: no persistent state. The tests assume immediate reuse from `sync.Pool`, which usually holds within one test but is not a strict long-term guarantee across GC boundaries.

Dependencies/integration: exercises only exported freepool APIs. There are no concurrency tests.

Risks/test signals: the tests do not cover nil returns, panic behavior, or runtime pool eviction. They do catch accidental removal of cleanup or typed allocation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/freepool/freepool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/fshasher/fshasher.go -->
# sources/sync-backup/kopia/internal/fshasher/fshasher.go

Purpose: computes a deterministic hash of a Kopia `fs.Entry` tree for tests by serializing metadata and file contents as a tar stream and hashing it with BLAKE2s-256.

Important APIs/types/functions: `Hash`, `write`, `header`, `writeDirectory`, and `writeFile`. It consumes `fs.Entry`, `fs.Directory`, `fs.File`, `fs.Symlink`, `fs.GetAllEntries`, `tar.Writer`, `blake2s.New256`, and `iocopy.JustCopy`.

Control flow: `Hash` creates the hasher and tar writer, then recursively writes the root entry. `write` emits a tar header, then dispatches by entry type: directories are listed, sorted by name, and recursively serialized; files are opened and copied; symlinks rely on link target in the header.

State/persistence behavior: no state is persisted. Directory modification times are zeroed, all times are truncated to second precision and UTC, and directory entries are sorted to reduce filesystem-dependent noise.

Dependencies/integration: integrates with Kopia's virtual filesystem interfaces and logging. Used as a test fingerprint when comparing restored or mock filesystem trees.

Risks/test signals: tar header semantics mean permissions, size, symlink targets, and truncated times affect hashes. File content reads are streamed, so read/open errors propagate. The second-resolution timestamp normalization may intentionally hide subsecond differences.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/fshasher/fshasher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/fshasher/fshasher_test.go -->
# sources/sync-backup/kopia/internal/fshasher/fshasher_test.go

Purpose: verifies that filesystem tree hashes are stable for equivalent trees and change for structural, content, and permission differences.

Important APIs/types/functions: `Hash`, `mockfs.NewDirectory`, `AddFile`, `AddDir`, `testlogging.Context`, and `testify/require`.

Control flow: the test builds a mock root with a file and directory, hashes it, mutates the tree by adding another directory, and asserts the root hash changes. It then compares two equivalent subdirectories, adds an extra file to one, and checks inequality. Finally it creates directories/files with differing permission attributes and asserts different hashes.

State/persistence behavior: all filesystem state is in-memory `mockfs`. The test targets deterministic serialization rather than durable files.

Dependencies/integration: validates integration between `fshasher`, `mockfs`, Kopia `fs` interfaces, and test logging context.

Risks/test signals: the final file-permission scenario appears to construct a directory similar to a previous one and primarily catches metadata sensitivity. The test does not cover symlink targets, timestamp truncation, or file read errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/fshasher/fshasher_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/fusemount/fusefs.go -->
# sources/sync-backup/kopia/internal/fusemount/fusefs.go

Purpose: implements go-fuse node adapters that expose a Kopia `fs.Directory` tree as a read-only FUSE filesystem on supported Unix platforms.

Important APIs/types/functions: `fuseNode`, `fuseFileNode`, `fuseFileHandle`, `fuseDirectoryNode`, `fuseSymlinkNode`, `goModeToUnixMode`, `populateAttributes`, `Getattr`, `Open`, `Read`, `Release`, `Lookup`, `Readdir`, `Readlink`, `entryToFuseMode`, `newFuseNode`, and `NewDirectoryNode`. Compile-time assertions ensure go-fuse interfaces are implemented.

Control flow: directory lookup asks the underlying `fs.Directory` for a child, maps missing entries to `ENOENT`, creates the appropriate node, and populates attributes. Readdir iterates all children into `fuse.DirEntry` values. File open obtains an `fs.Reader`; reads seek to the requested offset, read into FUSE's buffer, and return `fuse.ReadResultData`. Symlink reads delegate to `fs.Symlink.Readlink`.

State/persistence behavior: node state wraps immutable snapshot entries plus open file handles. File handle state is protected by a mutex because FUSE may issue concurrent reads on the same handle. No writes, creates, deletes, or persistence mutations are implemented.

Dependencies/integration: depends on `github.com/hanwen/go-fuse/v2`, Kopia `fs` interfaces, and repository logging. Build tags exclude Windows, OpenBSD, and FreeBSD.

Risks/test signals: unsupported entry types return `EIO` through lookup creation. Attributes use a fake block size and set uid/gid from entry owner metadata. There are no tests in this subset, so integration coverage likely comes from mount-level tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/fusemount/fusefs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/gather/gather_bytes.go -->
# sources/sync-backup/kopia/internal/gather/gather_bytes.go

Purpose: represents binary data as a logical byte sequence backed by multiple slices, avoiding mandatory contiguous allocation for large buffers.

Important APIs/types/functions: `Bytes`, `ErrInvalidOffset`, `FromSlice`, `Length`, `AppendSectionTo`, `ReadAt`, `Reader`, `AppendToSlice`, `ToByteSlice`, `WriteTo`, and internal `bytesReadSeekCloser`. The invalidation sentinel uses a generated UUID byte slice.

Control flow: `AppendSectionTo` walks slices to locate the starting offset, writes the first partial slice, then writes whole or partial subsequent slices until `size` is satisfied. `bytesReadSeekCloser.ReadAt` performs similar offset lookup and copies into caller-provided memory, returning `ErrInvalidOffset` for negative offsets and `io.EOF` when data is exhausted. `Reader` returns a seekable read closer over a value copy of `Bytes`.

State/persistence behavior: `Bytes` is a view over existing slices; it does not own or copy them except in `ToByteSlice`. `WriteBuffer.Close` can invalidate exposed `Bytes`, after which methods panic via `assertValid`.

Dependencies/integration: used across content buffering, HMAC, blob storage, and gather write buffers. Implements common I/O interfaces expected by storage code.

Risks/test signals: `Bytes.ReadAt` currently returns `len(p)` with the error from `AppendSectionTo`, so the more precise `ReaderAt` behavior lives in `bytesReadSeekCloser`. Consumers must not use `Bytes` after the owning buffer closes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/gather/gather_bytes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/gather/gather_bytes_test.go -->
# sources/sync-backup/kopia/internal/gather/gather_bytes_test.go

Purpose: exhaustively tests logical byte operations over empty, nil, single-slice, and multi-slice `Bytes` values.

Important APIs/types/functions: `Bytes.Length`, `Reader`, `ToByteSlice`, `WriteTo`, `AppendSectionTo`, `ReadAt` via `io.ReaderAt`, `WriteBuffer`, `ErrInvalidOffset`, `iotest.TestReader`, and `testutil.EnsureType`.

Control flow: `TestGatherBytes` iterates many slice layouts and all start/end section ranges, verifying appended sections equal the corresponding contiguous subslice and write errors propagate. Reader tests build large `WriteBuffer` contents around allocator chunk boundaries and run `iotest.TestReader`. Error-response tests cover negative offsets, huge offsets, zero-length reads, and variable read buffer sizes.

State/persistence behavior: tests are in-memory and rely on `WriteBuffer` chunk allocation. `TestGatherBytesPanicsOnClose` intentionally closes a buffer then verifies exposed `Bytes` panic on use, documenting lifetime rules.

Dependencies/integration: exercises gather with `WriteBuffer`, `testing/iotest`, `testutil`, and `pkg/errors`. It is the main regression suite for byte-slice boundary handling.

Risks/test signals: broad boundary coverage catches EOF and slice-index bugs. The tests assume the default allocator chunk size for some cases, so allocator changes may require test adjustment.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/gather/gather_bytes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/gather/gather_write_buffer.go -->
# sources/sync-backup/kopia/internal/gather/gather_write_buffer.go

Purpose: provides a thread-safe append-oriented buffer backed by pooled chunks and exposed as `gather.Bytes`.

Important APIs/types/functions: `WriteBuffer`, `Close`, `MakeContiguous`, `Reset`, `Write`, `AppendSectionTo`, `Length`, `ToByteSlice`, `Bytes`, `Append`, `Dup`, `NewWriteBuffer`, and `NewWriteBufferMaxContiguous`.

Control flow: `Append` lazily allocates a chunk, appends as much data as fits, and allocates additional chunks as needed. `MakeContiguous` resets the buffer and chooses the typical, max-contiguous, or raw allocation path based on requested length. `Close` and `Reset` release owned chunks to their allocator and invalidate old `Bytes` views.

State/persistence behavior: buffer state is in-memory and guarded by a mutex. `Bytes` returns the internal view, not a deep copy, so lifetime is tied to the buffer until `Dup` or `ToByteSlice` is used. `Dup` creates a new buffer with a contiguous copy.

Dependencies/integration: depends on `chunkAllocator` from `gather_write_buffer_chunk.go` and repository logging. Implements `io.Writer` for callers that stream into gather buffers.

Risks/test signals: forgetting to close buffers can retain chunks, especially with large contiguous allocators. `MakeContiguous` can allocate non-pooled memory for lengths larger than the max contiguous allocator and leaves `alloc` nil for that case.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/gather/gather_write_buffer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/gather/gather_write_buffer_chunk.go -->
# sources/sync-backup/kopia/internal/gather/gather_write_buffer_chunk.go

Purpose: implements chunk allocation, freelist reuse, allocation statistics, and optional leak tracing for gather write buffers.

Important APIs/types/functions: `chunkAllocator`, `allocChunk`, `releaseChunk`, `trackAlloc`, `dumpStats`, `DumpStats`, and globals `defaultAllocator`, `typicalContiguousAllocator`, `maxContiguousAllocator`, and `trackChunkAllocations`.

Control flow: allocation increments counters, reuses the last freelist entry when available, or creates a zero-length slice with configured capacity. Release ignores non-owned capacity, deletes active tracking metadata, increments freed counters, and stores reset slices until `maxFreeListSize` is reached. `DumpStats` logs allocator counters and active allocation stack snippets.

State/persistence behavior: allocator state is process-local global state. `activeChunks` is populated only when `KOPIA_TRACK_CHUNK_ALLOC` or tests enable tracking; it is intended for diagnostics, not persistence.

Dependencies/integration: uses `runtime`, `unsafe`, environment variables, and repository logging. Chunk sizes are tuned for normal buffers and encryption/splitter contiguous buffers.

Risks/test signals: release is capacity-based, so slices with matching capacity are accepted as pool-owned. Freelist entries are not zeroed, so callers must treat newly allocated chunks as length zero and overwrite before reading. Tracking uses unsafe slice pointers for diagnostics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/gather/gather_write_buffer_chunk.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/gather/gather_write_buffer_chunk_test.go -->
# sources/sync-backup/kopia/internal/gather/gather_write_buffer_chunk_test.go

Purpose: validates chunk allocator reuse, contiguous allocator sizing, and diagnostic allocation tracking.

Important APIs/types/functions: `chunkAllocator.allocChunk`, `releaseChunk`, `freeListHighWaterMark`, `maxContiguousAllocator`, `splitter.SupportedAlgorithms`, `DumpStats`, and `trackChunkAllocations`.

Control flow: `TestWriteBufferChunk` uses a small allocator, releases chunks, and asserts LIFO reuse by observing old bytes in reset-length slices. `TestContigAllocatorChunkSize` checks the max contiguous chunk can hold every supported splitter max segment size plus overhead. `TestTrackAllocation` enables tracking, logs stats before allocation, after append, and after close, and checks leaked-chunk diagnostics appear and disappear.

State/persistence behavior: all state is in-memory global allocator/test allocator state. The test temporarily mutates `trackChunkAllocations` and restores it with defer.

Dependencies/integration: integrates with `repo/splitter` to keep allocator sizing aligned with splitter algorithms. Uses logging to a buffer for diagnostics assertions.

Risks/test signals: the reuse test intentionally confirms old data remains in pooled capacity, documenting that callers cannot assume zeroed memory. It does not exercise concurrent allocator use.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/gather/gather_write_buffer_chunk_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/gather/gather_write_buffer_test.go -->
# sources/sync-backup/kopia/internal/gather/gather_write_buffer_test.go

Purpose: tests append, section extraction, allocator selection, and large-buffer chunking behavior for `WriteBuffer`.

Important APIs/types/functions: `NewWriteBuffer`, `WriteBuffer.Append`, `Write`, `ToByteSlice`, `Length`, `AppendSectionTo`, `Reset`, `MakeContiguous`, `NewWriteBufferMaxContiguous`, and `Bytes`.

Control flow: `TestGatherWriteBuffer` appends strings and repeated bytes across chunk boundaries, checks slice counts, extracts a section, and resets. `TestGatherDefaultWriteBuffer` verifies lazy default allocation. Contiguous tests assert small and mid-size lengths choose the expected allocator while over-max lengths use raw allocation. The max-contiguous test writes millions of small chunks and verifies slice counts grow by 16MB-sized chunks.

State/persistence behavior: in-memory buffer state is closed with defer in most tests. The tests inspect package internals because they are in package `gather`.

Dependencies/integration: exercises `fmt.Fprintf` through the `io.Writer` implementation and internal allocator globals.

Risks/test signals: tests protect allocator selection thresholds and chunk-boundary behavior. Very large append loops can be somewhat expensive but directly validate high-volume behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/gather/gather_write_buffer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/grpcapi/Makefile -->
# sources/sync-backup/kopia/internal/grpcapi/Makefile

Purpose: documents and automates regeneration of Go protobuf and gRPC bindings for the repository server API.

Important APIs/types/functions: `rebuild` invokes `protoc` with `--go_out`, `--go_opt=paths=source_relative`, `--go-grpc_out`, and `--go-grpc_opt=paths=source_relative` against `repository_server.proto`. `install-tools` installs protobuf and Go plugins through Homebrew.

Control flow: running `make rebuild` regenerates `repository_server.pb.go` and `repository_server_grpc.pb.go` in-place with source-relative paths. `make install-tools` is a convenience target for macOS-like Homebrew environments.

State/persistence behavior: regeneration overwrites generated Go files and must be kept in sync with the `.proto` schema and generator versions. No runtime state is involved.

Dependencies/integration: depends on `protoc`, `protoc-gen-go`, and `protoc-gen-go-grpc`. The generated files are compiled into Kopia's internal gRPC API package.

Risks/test signals: `install-tools` is platform-specific and not hermetic. Generator version drift can produce large diffs even for unchanged schema semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/grpcapi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/grpcapi/repository_server.pb.go -->
# sources/sync-backup/kopia/internal/grpcapi/repository_server.pb.go

Purpose: generated Go protobuf bindings for `repository_server.proto`, defining message structs, enum types, oneof wrappers, getters, reflection descriptors, and raw descriptor metadata.

Important APIs/types/functions: `NotificationEventArgType`, `ErrorResponse_Code`, message structs such as `ContentInfo`, `ManifestEntryMetadata`, `RepositoryParameters`, request/response types, `SessionRequest`, `SessionResponse`, oneof wrapper structs, `File_repository_server_proto`, `file_repository_server_proto_rawDescGZIP`, and `file_repository_server_proto_init`.

Control flow: generated getters return zero values for nil receivers. `Reset`, `String`, `ProtoMessage`, and `ProtoReflect` methods satisfy protobuf runtime contracts. `init` builds descriptors, registers oneof wrapper sets for session request/response, and releases temporary go type/dependency slices.

State/persistence behavior: the file encodes the wire contract for repository sessions. Persistent compatibility is tied to field numbers, enum numeric values, map encodings, and oneof tags from the proto schema.

Dependencies/integration: depends on `google.golang.org/protobuf` reflection/runtime packages. It is consumed by Kopia gRPC clients and servers along with `repository_server_grpc.pb.go`.

Risks/test signals: this file should not be hand-edited; semantic changes belong in the proto. The main risks are schema incompatibility, generator/runtime version mismatch, or stale generated output after editing `repository_server.proto`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/grpcapi/repository_server.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/grpcapi/repository_server.proto -->
# sources/sync-backup/kopia/internal/grpcapi/repository_server.proto

Purpose: defines Kopia's internal bidirectional streaming repository API, including content, manifest, retention, notification, error, and session initialization messages.

Important APIs/types/functions: messages `ContentInfo`, `ManifestEntryMetadata`, `ErrorResponse`, `RepositoryParameters`, operation-specific request/response pairs, `SessionRequest`, `SessionResponse`, enum `NotificationEventArgType`, nested enum `ErrorResponse.Code`, and service `KopiaRepository.Session`.

Control flow: clients open one streaming `Session`, send `SessionRequest` messages with `request_id` and exactly one operation in a `oneof`, and receive `SessionResponse` messages with matching `request_id`, `has_more` for multi-response operations, and either an error or matching typed response. `InitializeSessionRequest` is documented as the first request.

State/persistence behavior: field numbers and enum values are wire-persistent API state. `RepositoryParameters` carries hash/HMAC/splitter/compression support; content and manifest messages mirror repository metadata.

Dependencies/integration: generated by protoc into Go bindings and gRPC service code. Integrates repository content APIs, manifest APIs, retention policy application, prefetching, and notification delivery over one multiplexed stream.

Risks/test signals: oneof extensions require preserving existing field numbers and adding new fields carefully. `hmac_secret` is transmitted as bytes, so transport security and access control are critical. No tests are in this file; compatibility is validated by generated code compilation and API integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/grpcapi/repository_server.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/grpcapi/repository_server_grpc.pb.go -->
# sources/sync-backup/kopia/internal/grpcapi/repository_server_grpc.pb.go

Purpose: generated gRPC-Go bindings for the `KopiaRepository` service declared in `repository_server.proto`.

Important APIs/types/functions: `KopiaRepositoryClient`, `NewKopiaRepositoryClient`, `KopiaRepositoryClient.Session`, `KopiaRepositoryServer`, `UnimplementedKopiaRepositoryServer`, `UnsafeKopiaRepositoryServer`, `RegisterKopiaRepositoryServer`, `_KopiaRepository_Session_Handler`, `KopiaRepository_ServiceDesc`, and stream aliases for client/server session streams.

Control flow: client `Session` calls `NewStream` with the service stream descriptor and wraps it in a generic bidirectional client stream. Server registration checks that `UnimplementedKopiaRepositoryServer` is embedded by value when detectable, then registers a single bidirectional stream handler that delegates to `srv.Session`.

State/persistence behavior: no persistent state, but service and method names are part of the RPC contract: `/kopia_repository.KopiaRepository/Session`.

Dependencies/integration: depends on `google.golang.org/grpc`, status/codes, and generated message types. Requires gRPC-Go v1.64.0 or later via compile-time assertion.

Risks/test signals: generated code should not be manually edited. Server implementations must embed `UnimplementedKopiaRepositoryServer` for forward compatibility unless they deliberately opt into unsafe behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/grpcapi/repository_server_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/hmac/hmac.go -->
# sources/sync-backup/kopia/internal/hmac/hmac.go

Purpose: appends and verifies HMAC-SHA256 checksums for gathered byte sequences, mainly to protect cached data from corruption or tampering.

Important APIs/types/functions: `Append`, `VerifyAndStrip`, `gather.Bytes`, `gather.WriteBuffer`, `crypto/hmac`, `sha256`, and `io.CopyN`.

Control flow: `Append` writes the original input to output, writes the same input to an HMAC hasher, and appends the 32-byte signature. `VerifyAndStrip` rejects inputs shorter than the signature, streams all but the signature into both the hasher and output, reads the trailing signature, and compares with `hmac.Equal`.

State/persistence behavior: no internal state is kept. The output format is data followed by raw SHA-256 HMAC bytes; callers persist it where needed, such as list cache blobs.

Dependencies/integration: integrates with gather buffers and `listcache`. Uses constant-time comparison through `hmac.Equal`.

Risks/test signals: `Append` ignores write errors because `gather.WriteBuffer` writes are expected not to fail; a different output implementation is not supported. `VerifyAndStrip` writes plaintext into output before signature validation completes, so callers must discard output on error.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/hmac/hmac.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/impossible/impossible.go -->
# sources/sync-backup/kopia/internal/impossible/impossible.go

Purpose: provides a tiny helper for code paths that consider an error impossible and prefer panic over repetitive error handling.

Important APIs/types/functions: `PanicOnError`.

Control flow: the function checks `err != nil` and panics with the error value if present; nil is a no-op.

State/persistence behavior: no state is stored or persisted. Its effect is immediate control-flow termination through panic.

Dependencies/integration: no external dependencies. Intended for internal use where an API returns an error for interface reasons but the caller believes failure cannot occur.

Risks/test signals: misuse can convert recoverable runtime errors into panics. Callers should reserve it for truly impossible branches or test helpers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/impossible/impossible.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/impossible/impossible_test.go -->
# sources/sync-backup/kopia/internal/impossible/impossible_test.go

Purpose: verifies `PanicOnError` no-ops for nil and panics with the original error message for non-nil errors.

Important APIs/types/functions: `impossible.PanicOnError`, `errors.New`, and `require.PanicsWithError`.

Control flow: the test calls `PanicOnError(nil)`, then creates a sentinel error and asserts that invoking the helper panics with that error text.

State/persistence behavior: no persistent state. The test is pure control-flow validation.

Dependencies/integration: package `impossible_test` uses the exported helper only, with `testify/require`.

Risks/test signals: narrow by design; it does not test panic recovery behavior beyond matching the error string.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/impossible/impossible_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/indextest/indextest.go -->
# sources/sync-backup/kopia/internal/indextest/indextest.go

Purpose: provides detailed diffing for `repo/content/index.Info` values in tests.

Important APIs/types/functions: `InfoDiff`, `index.Info`, `Timestamp`, `reflect.TypeFor`, and optional string-prefix ignore filters.

Control flow: `InfoDiff` compares each relevant exported field and derived timestamp, appending human-readable differences. It then checks the method count on `index.Info` to force maintainers to revisit this helper when the type's behavior changes. Finally it filters differences whose messages start with any ignored prefix.

State/persistence behavior: no state is persisted. It inspects in-memory index metadata that corresponds to repository content index records.

Dependencies/integration: used by content index tests to produce clearer mismatch output than a raw struct comparison. It integrates with `repo/content/index` type evolution.

Risks/test signals: field coverage is manual. The reflection method-count guard catches some API drift but not newly added fields, so maintainers still need to update comparisons when `index.Info` changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/indextest/indextest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/insecureserverbind/insecureserverbind.go -->
# sources/sync-backup/kopia/internal/insecureserverbind/insecureserverbind.go

Purpose: prevents unauthenticated insecure Kopia servers from binding to public network interfaces unless an explicit dangerous escape hatch is set.

Important APIs/types/functions: `AllowDangerousUnauthenticatedNetworkFlag`, `AllowDangerousUnauthenticatedNetworkFlagHelp`, `ErrDisallowedPublicBind`, `RestrictionApplies`, `ValidateListenAddressIfRestricted`, `ValidateListenerAddrIfRestricted`, `ParseListenHost`, `ValidateListenAddressFlag`, and `ValidateListenerAddr`.

Control flow: restriction applies only when the server is insecure, has no password, and the dangerous flag is not set. Address validation strips leading HTTP/HTTPS, treats `unix:` as safe, parses hostnames, accepts empty only for Unix sockets, accepts `localhost` and loopback IPs, and rejects public IPs, wildcard binds, and non-localhost hostnames. Listener validation accepts Unix listeners and loopback TCP addresses after binding.

State/persistence behavior: no state is stored. The important behavioral state is CLI flag configuration and bound listener address.

Dependencies/integration: integrates with server startup and CLI flag handling. Uses `net`, `net/url`, and wrapped errors so callers can detect `ErrDisallowedPublicBind`.

Risks/test signals: DNS names other than literal `localhost` are rejected even if they resolve locally, which is conservative. Unknown listener types are rejected unless their network string is `unix`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/insecureserverbind/insecureserverbind.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/insecureserverbind/insecureserverbind_test.go -->
# sources/sync-backup/kopia/internal/insecureserverbind/insecureserverbind_test.go

Purpose: validates insecure server bind restrictions across flag combinations, string listen addresses, bound listener addresses, Unix sockets, loopback IPs, and unknown address types.

Important APIs/types/functions: `RestrictionApplies`, `ValidateListenAddressIfRestricted`, `ValidateListenerAddrIfRestricted`, `ParseListenHost`, `ValidateListenAddressFlag`, `ValidateListenerAddr`, `ErrDisallowedPublicBind`, and `stubAddr`.

Control flow: parallel table tests check when validation is skipped or enforced. Address parsing covers HTTP, HTTPS, hostless binds, IPv4/IPv6 loopback, Unix socket forms, public IPs, and hostnames. Validation tests assert allowed loopback/Unix cases and ensure rejected cases wrap `ErrDisallowedPublicBind` and mention the escape-hatch flag.

State/persistence behavior: no durable state. The tests model startup configuration and post-listen socket validation.

Dependencies/integration: uses `net.TCPAddr`, `net.UnixAddr`, custom `net.Addr`, and `testify/require`. The suite is package-internal, so it covers unexported `ParseListenHost` behavior too.

Risks/test signals: tests intentionally reject `0.0.0.0`, hostless addresses, public test-net IPs, and arbitrary hostnames. They do not perform DNS resolution, matching the production conservative policy.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/insecureserverbind/insecureserverbind_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/iocopy/iocopy.go -->
# sources/sync-backup/kopia/internal/iocopy/iocopy.go

Purpose: wraps `io.Copy` with reusable 64 KiB buffers to reduce allocation pressure while preserving standard fast paths.

Important APIs/types/functions: `BufSize`, `GetBuffer`, `ReleaseBuffer`, `Copy`, and `JustCopy`. Global buffer storage is protected by a mutex.

Control flow: `Copy` first delegates to `src.(io.WriterTo)` or `dst.(io.ReaderFrom)` when available, matching `io.Copy` fast-path behavior. Otherwise it obtains a shared buffer, defers release, and calls `io.CopyBuffer`. `JustCopy` discards the byte count.

State/persistence behavior: global buffer freelist is process-local and grows when buffers are released. Buffer contents are not cleared before reuse.

Dependencies/integration: used by `fshasher` and likely other streaming paths. It depends only on `io` and `sync`.

Risks/test signals: `ReleaseBuffer` accepts any slice and does not enforce `BufSize`, so misuse can pollute the pool. Because buffers are reused without clearing, callers must not rely on zeroed memory.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/iocopy/iocopy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/iocopy/iocopy_test.go -->
# sources/sync-backup/kopia/internal/iocopy/iocopy_test.go

Purpose: tests shared-buffer allocation/reuse and copy behavior for normal and error paths.

Important APIs/types/functions: `iocopy.GetBuffer`, `ReleaseBuffer`, `Copy`, `JustCopy`, `errorWriter`, `customReader`, and `customWriter`.

Control flow: buffer tests check length and pointer reuse after release. Copy tests stream a fixed string into `bytes.Buffer`, assert byte count and content, and verify write errors propagate through both `Copy` and `JustCopy`. Custom reader/writer wrapper types avoid standard fast paths and exercise the buffer-copy path.

State/persistence behavior: tests mutate the package-global buffer pool by releasing and retaking a buffer. No durable state exists.

Dependencies/integration: uses `strings.Reader`, `bytes.Buffer`, `io`, and `testify/require`.

Risks/test signals: tests do not cover concurrent buffer use or invalid buffer release. Pointer-reuse assertion relies on immediate freelist reuse, which matches current implementation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/iocopy/iocopy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/listcache/listcache.go -->
# sources/sync-backup/kopia/internal/listcache/listcache.go

Purpose: wraps a `blob.Storage` to cache `ListBlobs` results for selected prefixes in a separate cache storage, with HMAC verification and write/delete invalidation.

Important APIs/types/functions: `listCacheStorage`, `cachedList`, `saveListToCache`, `readBlobsFromCache`, `ListBlobs`, `PutBlob`, `DeleteBlob`, `FlushCaches`, `isCachedPrefix`, `invalidateAfterUpdate`, and `NewWrapper`.

Control flow: `ListBlobs` bypasses caching for unconfigured prefixes. For cached prefixes it reads and verifies cache data, falls back to listing the underlying storage, stores a JSON `cachedList` with expiry, and replays cached metadata to the callback. Writes and deletes delegate to underlying storage and then invalidate any cached prefix matching the blob ID. `FlushCaches` flushes the underlying storage and deletes cache blobs for all cached prefixes.

State/persistence behavior: cached list entries are persisted as HMAC-protected JSON blobs under their prefix IDs in `cacheStorage`. Expiry uses `cacheTimeFunc`, defaulting to `clock.Now`, and cached results can temporarily hide out-of-band storage changes until expiry or invalidation.

Dependencies/integration: depends on `repo/blob`, `internal/gather`, `internal/hmac`, `internal/clock`, JSON encoding, and repository logging. It is a consistency/performance layer around blob listing.

Risks/test signals: invalidation runs even if the underlying write/delete returns an error, which may drop caches conservatively. Cache storage failures are logged and ignored. HMAC protects integrity but not confidentiality.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/listcache/listcache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/listcache/listcache_test.go -->
# sources/sync-backup/kopia/internal/listcache/listcache_test.go

Purpose: validates list caching, expiry, HMAC rejection, invalidation on wrapped writes/deletes, explicit flushing, and non-cached prefix passthrough.

Important APIs/types/functions: `NewWrapper`, `listCacheStorage`, `blobtesting.NewMapStorage`, `AssertListResultsIDs`, `faketime.NewTimeAdvance`, `PutBlob`, `DeleteBlob`, `FlushCaches`, and `ListBlobs`.

Control flow: the test builds real and cache map storages with independent fake clocks, wraps selected prefixes, and verifies the first list writes a cache blob. It mutates underlying storage directly to show cached invisibility, advances cache time to expire entries, writes/deletes through the wrapper to trigger invalidation, corrupts cache data to force HMAC rejection, flushes caches, and checks callback errors are propagated.

State/persistence behavior: uses in-memory map storages as stand-ins for persistent blob stores. Cached JSON/HMAC blobs are visible in the cache storage under prefix IDs.

Dependencies/integration: integrates listcache with blobtesting, faketime, gather bytes, and test logging. Package-internal access allows replacing `cacheTimeFunc`.

Risks/test signals: broad behavior coverage for cache consistency. It does not simulate cache storage put/delete failures beyond corrupted cache content.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/listcache/listcache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/logfile/logfile.go -->
# sources/sync-backup/kopia/internal/logfile/logfile.go

Purpose: attaches CLI flags and configures console, CLI file, and content log output for Kopia with rotation, sweeping, formatting, and cache-directory markers.

Important APIs/types/functions: `loggingFlags`, `Attach`, `setup`, `initialize`, `setupConsoleCore`, `setupLogFileBasedLogger`, `setupLogFileCore`, `jsonOrConsoleEncoder`, `shouldSweepLog`, `sweepLogDir`, `logLevelFromFlag`, and `onDemandFile` methods `Write`, `Sync`, `closeSegmentAndSweep`.

Control flow: `setup` registers kingpin flags and a pre-action initializer. `initialize` computes timestamp/suffix, builds zap cores for console and file logs, optionally creates content log writer, and installs the logger factory on the CLI app. File logging creates directories, cache markers, an on-demand segmented writer, and sweep callbacks. `onDemandFile.Write` opens the next segment lazily, rotates before overflow, updates `latest.log`, and writes bytes.

State/persistence behavior: persists log files under `cli-logs` and `content-logs`, with mode `0700` directories and cache markers. Sweeping removes old log files by count, aggregate size, or age, excluding nonmatching files and cache markers.

Dependencies/integration: depends on Kingpin, zap/zapcore, Kopia CLI app, cachedir/ospath/zaplogutil, and repository logging. It is attached to CLI test runners and real command startup.

Risks/test signals: log sweeping runs asynchronously unless configured to wait, so race windows exist around file listing. Symlink creation is best-effort. Size-based sweeping uses sorted newest-first cumulative size and can delete many segments when budgets shrink.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/logfile/logfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/logfile/logfile_test.go -->
# sources/sync-backup/kopia/internal/logfile/logfile_test.go

Purpose: validates CLI logging flags, console formatting/color, file log formatting, rotation limits, size sweeping, and cache marker creation.

Important APIs/types/functions: `logfile.Attach`, `testenv.NewInProcRunner`, `testenv.NewCLITest`, `verifyFileLogFormat`, `verifyJSONLogFormat`, `getTotalDirSize`, and CLI commands such as `repo create`, `snap create`, and `snap ls`.

Control flow: `TestLoggingFlags` runs real in-process CLI commands with different logging flags and verifies stderr content, timestamps, colors, and JSON/content log files. Rotation tests force tiny segment sizes and max file counts. Total-size tests create a source tree, run commands, then repeatedly shrink log budgets and assert directory size decreases. Cache marker test verifies both log subdirectories contain cache markers.

State/persistence behavior: tests create real temporary repositories, source directories, and log directories. Log segments, `latest.log`, and cache marker files are inspected on disk.

Dependencies/integration: high-level integration coverage across CLI, logging setup, snapshot commands, cachedir, clock, and filesystem. Regexes encode expected log line formats for UTC and local timezone.

Risks/test signals: these tests are broader and slower than unit tests because they run CLI workflows. Format assertions can fail on intentional logging format changes. Size sweeping has tolerance checks rather than exact file lists.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/logfile/logfile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metricid/id_mapping.go -->
# sources/sync-backup/kopia/internal/metricid/id_mapping.go

Purpose: provides compact conversion between maps keyed by well-known metric names and slices indexed by persistent numeric IDs.

Important APIs/types/functions: `Mapping`, `MapToSlice`, `SliceToMap`, `NewMapping`, and `inverse`.

Control flow: `NewMapping` stores the provided name-to-index map, builds an inverse map for positive IDs, and computes `MaxIndex`. `MapToSlice` allocates a slice of length `MaxIndex`, drops unknown or zero-index keys, and stores values at `id-1`. `SliceToMap` walks input positions and emits only positions present in `IndexToName`.

State/persistence behavior: mappings are in-memory structures, but their numeric IDs define persisted compact JSON positions for metrics. Missing IDs produce zero-value holes in slices.

Dependencies/integration: used by `metricid/metricid.go` to define stable IDs for counters and distributions.

Risks/test signals: duplicate IDs in input maps are not rejected here and would overwrite inverse entries; the separate mapping tests enforce uniqueness/consecutiveness for built-in mappings. Unknown metric names are silently dropped during map-to-slice conversion.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metricid/id_mapping.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metricid/id_mapping_test.go -->
# sources/sync-backup/kopia/internal/metricid/id_mapping_test.go

Purpose: verifies generic map/slice conversion behavior for metric ID mappings.

Important APIs/types/functions: `metricid.NewMapping`, `MapToSlice`, and `SliceToMap`.

Control flow: `TestMapToSlice` builds a mapping with a gap, checks nil and partial maps, verifies the gap is represented by a zero value, and confirms unknown key `c` is dropped. `TestSliceToMap` checks short, exact, and overlong slices, ensuring only mapped indexes appear in the result.

State/persistence behavior: no durable state. The tests model compact persisted JSON shapes where slice positions correspond to metric IDs.

Dependencies/integration: uses `testify/require` and package `metricid_test`, covering exported behavior only.

Risks/test signals: tests do not cover duplicate or zero IDs in mappings; built-in mapping validation handles part of that separately.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metricid/id_mapping_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metricid/metricid.go -->
# sources/sync-backup/kopia/internal/metricid/metricid.go

Purpose: defines stable numeric IDs for well-known Kopia metric names so snapshots can be serialized compactly.

Important APIs/types/functions: global mappings `Counters`, `DurationDistributions`, and `SizeDistributions`, all created with `NewMapping`.

Control flow: package initialization builds mappings from literal metric-name maps. Counter IDs cover blob, content compression, encryption, hashing, read/write, and upload/download metrics. Duration distribution IDs cover blob storage latency by method. Size distribution mapping is currently empty but reserved.

State/persistence behavior: these numeric IDs are persistent compatibility state; comments require adding new items with consecutive values. Reordering or renumbering existing entries would break compact historical metric decoding.

Dependencies/integration: consumed by metric snapshot serialization/deserialization paths outside this subset. Names include label suffixes such as `[method:GetBlob-full]`.

Risks/test signals: manual maintenance is required when adding metrics. Empty `SizeDistributions` is valid but means no compact IDs are currently assigned for size distributions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metricid/metricid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metricid/metricid_test.go -->
# sources/sync-backup/kopia/internal/metricid/metricid_test.go

Purpose: validates built-in metric ID mappings for duplicate IDs, inverse consistency, consecutiveness, and max-index accuracy.

Important APIs/types/functions: `metricid.Counters`, `DurationDistributions`, `SizeDistributions`, `Mapping.NameToIndex`, `IndexToName`, and `MaxIndex`.

Control flow: `TestMappings` calls `verifyMapping` for each global mapping. The helper builds its own ID-to-name map, fails on duplicates, verifies every forward entry is present in the inverse mapping, and asserts the number of IDs equals the maximum ID.

State/persistence behavior: no state is persisted during tests. The tested data is persistent compatibility metadata, so failures indicate an unsafe mapping edit.

Dependencies/integration: uses `testify/require`. The empty size distribution mapping passes because both length and max are zero.

Risks/test signals: the test enforces consecutive positive IDs but not semantic stability of names assigned to existing IDs. Review is still required for renames.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metricid/metricid_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metric_test.go -->
# sources/sync-backup/kopia/internal/metrics/metric_test.go

Purpose: provides a shared test helper for finding Prometheus metrics by name, type, and exact label set.

Important APIs/types/functions: `mustFindMetric`, `prometheus.DefaultGatherer.Gather`, `io_prometheus_client.MetricType`, and Prometheus metric families/labels.

Control flow: the helper gathers all registered metrics, scans for the desired family/type, then searches metric instances with the same label count and matching label values. On failure it logs all gathered metrics for diagnostics and fails the test.

State/persistence behavior: reads process-global Prometheus registry state. No durable state is used.

Dependencies/integration: used by counter, distribution, and throughput tests to verify Prometheus exporter integration in addition to Kopia snapshot state.

Risks/test signals: because it uses the default Prometheus gatherer, tests can be sensitive to global metric registration and name reuse across packages. Exact label matching avoids false positives among label variants.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metric_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_aggregation.go -->
# sources/sync-backup/kopia/internal/metrics/metrics_aggregation.go

Purpose: aggregates multiple metric snapshots into one combined snapshot.

Important APIs/types/functions: `AggregateSnapshots`, `Snapshot`, `createSnapshot`, and `Snapshot.mergeFrom`.

Control flow: `AggregateSnapshots` initializes an empty snapshot and calls `mergeFrom` for each input. Counters are summed, and distribution states merge count, sum, min/max, and buckets via `mergeFrom`.

State/persistence behavior: returns a new in-memory snapshot. It does not currently set aggregate start/end/user/host fields, so callers should treat it as value aggregation rather than a full identity-preserving snapshot.

Dependencies/integration: relies on registry snapshot structures in `metrics_registry.go` and distribution merge behavior in `metrics_distribution.go`.

Risks/test signals: aggregate behavior assumes compatible bucket layouts for distributions with the same name. If bucket counts differ, `mergeScaledFrom` skips bucket merging after initializing state, potentially losing bucket details.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_aggregation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_aggregation_test.go -->
# sources/sync-backup/kopia/internal/metrics/metrics_aggregation_test.go

Purpose: verifies snapshot aggregation for counters, size distributions, and duration distributions.

Important APIs/types/functions: `metrics.AggregateSnapshots`, `metrics.Snapshot`, `DistributionState`, and helper `toJSON`.

Control flow: the test constructs four snapshots with overlapping and distinct counters plus matching distribution states. It aggregates them, asserts counter sums, and compares marshaled JSON for merged distributions including min, max, sum, count, and bucket counts.

State/persistence behavior: no persistent state. JSON comparisons mirror how distribution states appear in serialized output.

Dependencies/integration: uses `time.Duration` distribution states and `testify/require`.

Risks/test signals: exact JSON comparisons catch field-level regressions but do not verify start/end time handling. Bucket compatibility mismatch is not tested.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_aggregation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_counter.go -->
# sources/sync-backup/kopia/internal/metrics/metrics_counter.go

Purpose: implements monotonic integer counters backed by both an atomic in-memory state and a Prometheus counter.

Important APIs/types/functions: `Counter`, `Add`, `Snapshot`, `newState`, and `Registry.CounterInt64`.

Control flow: `Add` is nil-safe, increments Prometheus by `float64(v)`, and atomically adds to local state. `Snapshot(false)` loads current state, while `Snapshot(true)` swaps it to zero and returns the previous value. The registry method uses name plus label suffix as a map key and creates a Prometheus counter on first request.

State/persistence behavior: local counter state is in memory and resettable by snapshots; Prometheus counters remain monotonic and are not reset by `Snapshot(true)`. Registry maps retain created counters for the registry lifetime.

Dependencies/integration: depends on Prometheus client helpers defined elsewhere in the metrics package and registry locking in `metrics_registry.go`.

Risks/test signals: Prometheus counters should not receive negative values; this code does not guard against negative `Add`. Label suffix construction is order-sensitive because maps are iterated without sorting.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_counter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_counter_test.go -->
# sources/sync-backup/kopia/internal/metrics/metrics_counter_test.go

Purpose: validates nil-safe counters, unlabeled counters, labeled counters, snapshots, reset behavior, and Prometheus counter export.

Important APIs/types/functions: `metrics.NewRegistry`, `Registry.CounterInt64`, `Counter.Add`, `Counter.Snapshot`, and `mustFindMetric`.

Control flow: nil-registry test verifies calls on nil counters are no-ops. Unlabeled test creates a counter, observes Prometheus value at zero, adds values, checks Prometheus and snapshot totals, then resets local state. Labeled test creates two label variants and verifies independent Prometheus series and totals.

State/persistence behavior: uses process-global Prometheus registry and per-registry in-memory state. Snapshot reset does not reset Prometheus, and the tests only assert local reset after checking Prometheus totals.

Dependencies/integration: uses Prometheus client model types and `testify/require`.

Risks/test signals: global metric names in tests must remain unique to avoid duplicate registration conflicts. Negative counter behavior is not covered.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_counter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_distribution.go -->
# sources/sync-backup/kopia/internal/metrics/metrics_distribution.go

Purpose: implements generic numeric distributions for durations and sizes, recording min, max, sum, count, bucket counters, and Prometheus histograms.

Important APIs/types/functions: `realNumber`, `DistributionState[T]`, `mergeFrom`, `mergeScaledFrom`, `Mean`, `Distribution[T]`, `Observe`, `Snapshot`, `newState`, `Registry.DurationDistribution`, and `Registry.SizeDistribution`.

Control flow: `Observe` reads current state pointer, computes the bucket using thresholds, emits a scaled Prometheus observation, then locks and updates sum/count/min/max/bucket count. `Snapshot(false)` copies current state; `Snapshot(true)` swaps in a fresh state with initialized buckets. Registry constructors build Prometheus bucket slices from configured thresholds and reuse distributions by full name.

State/persistence behavior: distribution state is in-memory and resettable for repository metric snapshots; Prometheus histograms are cumulative. `DistributionState` JSON omits thresholds, but thresholds are retained internally for future aggregation.

Dependencies/integration: uses Prometheus histograms, generic constraints, and threshold definitions. Duration values are exported to Prometheus in milliseconds or nanoseconds depending on threshold set.

Risks/test signals: `Observe` loads the state pointer before locking; reset can swap state concurrently, so observations around resets may land in the old state. Label suffix ordering has the same map-order risk as counters. Bucket merges assume compatible bucket lengths.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_distribution.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_distribution_test.go -->
# sources/sync-backup/kopia/internal/metrics/metrics_distribution_test.go

Purpose: verifies binary-search bucket selection over distribution thresholds.

Important APIs/types/functions: `bucketForThresholds`, `IOLatencyThresholds.values`, and `math.MaxInt64`.

Control flow: the test checks a value below the first threshold maps to bucket zero. For every threshold it verifies `threshold-1` and exact threshold map to the current bucket, while `threshold+1` maps to the next bucket. A huge value maps to the overflow bucket.

State/persistence behavior: no mutable or persistent state. It validates pure threshold logic used by distributions.

Dependencies/integration: package-internal access to threshold values and helper function. Uses `testify/assert`.

Risks/test signals: focused on integer-like duration thresholds; it does not test floating-point threshold behavior even though the generic helper permits floats.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_distribution_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_duration_distribution_test.go -->
# sources/sync-backup/kopia/internal/metrics/metrics_duration_distribution_test.go

Purpose: validates duration and size distribution creation, observation, snapshot state, reset behavior, label separation, nil safety, and Prometheus histogram export.

Important APIs/types/functions: `Registry.DurationDistribution`, `Registry.SizeDistribution`, `Distribution.Observe`, `Distribution.Snapshot`, `IOLatencyThresholds`, `ISOBytesThresholds`, and `mustFindMetric`.

Control flow: nil tests ensure nil registries/distributions are safe. Duration tests observe one or two values, verify Prometheus sample counts/sums in milliseconds, and assert min/max/sum/count/mean for labeled series. Size tests do the same for byte values and confirm `Snapshot(true)` resets local state.

State/persistence behavior: local distribution snapshots are resettable; Prometheus histograms are cumulative. Labels produce independent registry entries and Prometheus series.

Dependencies/integration: uses Prometheus client model and `testify/require`.

Risks/test signals: tests cover representative buckets and aggregates but not every threshold. They assume globally unique Prometheus metric names.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_duration_distribution_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_registry.go -->
# sources/sync-backup/kopia/internal/metrics/metrics_registry.go

Purpose: owns metric instances, captures snapshots, logs metrics, and tracks registry lifetime for leak detection.

Important APIs/types/functions: `Registry`, `Snapshot`, `Snapshot.mergeFrom`, `createSnapshot`, `Registry.Snapshot`, `Close`, `Log`, `NewRegistry`, and `labelsSuffix`.

Control flow: `NewRegistry` initializes metric maps and records creation with `releasable`. `Snapshot` collects every counter and distribution, then locks registry metadata to set start/end times and optionally reset the registry start time. `Log` emits counters and non-empty distributions. `Close` is nil-safe and marks the registry released.

State/persistence behavior: registry state is in-memory; snapshots are serializable and carry start/end/user/host plus metric maps. Snapshot reset clears local metric states but does not remove metric objects or reset Prometheus exporters.

Dependencies/integration: depends on `internal/clock`, `internal/releasable`, and repository logging. Other metric files attach counters, throughput, and distributions to this registry.

Risks/test signals: `Snapshot` iterates metric maps without holding `r.mu`, so concurrent metric registration could race with snapshotting. `labelsSuffix` iterates maps without sorting, which can make full names unstable for multi-label maps.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_registry_test.go -->
# sources/sync-backup/kopia/internal/metrics/metrics_registry_test.go

Purpose: validates nil-safe registry logging/closing and the log output produced for counters, throughput, duration distributions, and size distributions.

Important APIs/types/functions: `metrics.NewRegistry`, `Registry.CounterInt64`, `Throughput`, `DurationDistribution`, `SizeDistribution`, `Registry.Log`, and `Registry.Close`.

Control flow: nil test calls `Log` and `Close` on a nil registry. Non-nil test writes log output to a buffer, records several metrics, logs them, closes the registry, sorts lines, and compares exact structured log output.

State/persistence behavior: uses in-memory registry state and buffer-backed logging. The test exercises release tracking through `Close` but does not inspect it directly.

Dependencies/integration: integrates metrics with repository logging's writer adapter and `testify/require`.

Risks/test signals: exact log-line assertions catch output format changes. The test uses single-label-free metrics and does not cover snapshot time metadata.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_registry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_thresholds.go -->
# sources/sync-backup/kopia/internal/metrics/metrics_thresholds.go

Purpose: defines reusable bucket thresholds for size, IO latency, and CPU latency distributions plus the helper that maps values to bucket indexes.

Important APIs/types/functions: `Thresholds[T]`, `ISOBytesThresholds`, `IOLatencyThresholds`, `CPULatencyThresholds`, and `bucketForThresholds`.

Control flow: threshold globals provide sorted bucket boundary slices, Prometheus scaling factors, and metric-name suffixes. `bucketForThresholds` performs binary search and returns the first index whose threshold is greater than or equal to the observed value, or the overflow index after the last threshold.

State/persistence behavior: thresholds are process-global constants in practice. Bucket layout affects serialized distribution bucket counters and Prometheus histogram buckets, so changes alter metric interpretation.

Dependencies/integration: used by `metrics_distribution.go` constructors and tests. Duration thresholds use `time.Duration` values.

Risks/test signals: threshold slices must stay sorted for binary search correctness. Changing thresholds can break historical comparison of bucket counters unless versioned elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_thresholds.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_throughput.go -->
# sources/sync-backup/kopia/internal/metrics/metrics_throughput.go

Purpose: represents throughput as two counters: total bytes/items and total duration in nanoseconds.

Important APIs/types/functions: `Throughput`, `Observe`, and `Registry.Throughput`.

Control flow: `Observe` is nil-safe and adds `size` to the `_bytes` counter and `dt.Nanoseconds()` to the `_duration_nanos` counter. The registry method reuses throughput instances by full name or creates the two backing counters on first use.

State/persistence behavior: state is stored in the two backing counters and participates in registry snapshots and Prometheus export as counters. The `Throughput` wrapper has no independent persisted state.

Dependencies/integration: depends on `CounterInt64` and `labelsSuffix`. Consumers derive rates from the paired counters.

Risks/test signals: `Registry.Throughput` accesses `allThroughput` without locking, unlike counter/distribution constructors, so concurrent creation can race. Negative sizes or durations are not guarded.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_throughput.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_throughput_test.go -->
# sources/sync-backup/kopia/internal/metrics/metrics_throughput_test.go

Purpose: validates nil-safe throughput observations and Prometheus export of backing byte and duration counters.

Important APIs/types/functions: `metrics.NewRegistry`, `Registry.Throughput`, `Throughput.Observe`, and `mustFindMetric`.

Control flow: nil test obtains throughput from a nil registry and calls `Observe`. Non-nil test creates a throughput metric, checks both Prometheus counters start at zero, records two observations, and verifies total bytes and total nanoseconds.

State/persistence behavior: uses in-memory registry state plus process-global Prometheus counters. No snapshot reset is tested.

Dependencies/integration: uses Prometheus client model and `testify/require`.

Risks/test signals: tests confirm counter naming suffixes but do not cover labels, snapshot content, or concurrent throughput creation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_throughput_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_timeseries.go -->
# sources/sync-backup/kopia/internal/metrics/metrics_timeseries.go

Purpose: converts metric snapshots into time series by spreading snapshot values proportionally over time buckets and aggregating by user, host, or all snapshots.

Important APIs/types/functions: `TimeSeries`, `TimeSeriesPoint`, `AggregateByFunc`, `AggregateByUser`, `AggregateByHost`, `AggregateAll`, `AggregateMetricsOptions`, `SnapshotValueAggregator`, and `CreateTimeSeries`.

Control flow: `CreateTimeSeries` defaults to user@host aggregation and daily resolution. For each snapshot it extracts a value, computes the first and last time buckets, then walks buckets from `StartTime` to `EndTime`, computing the fraction of snapshot duration in each bucket and delegating scaled aggregation to the value handler. Finally it converts nested maps to sorted point slices.

State/persistence behavior: output is a newly allocated map of sorted time series. Snapshot values are read only. The function assumes non-zero snapshot duration to avoid invalid ratio calculations.

Dependencies/integration: works with counter and distribution aggregators from sibling files and time resolution functions from `metrics_timeseries_timeres.go`.

Risks/test signals: integer aggregators truncate fractional contributions. Zero-length snapshots can divide by zero. `minTime` and `maxTime` are computed but not used in output.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_timeseries.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_timeseries_counter.go -->
# sources/sync-backup/kopia/internal/metrics/metrics_timeseries_counter.go

Purpose: implements a `SnapshotValueAggregator` for counter time series.

Important APIs/types/functions: `CounterValue`, `TimeseriesAggregator`, `FromSnapshot`, and `Aggregate`.

Control flow: `CounterValue` returns an aggregator bound to one counter name. `FromSnapshot` reads that counter from a snapshot map and reports whether it exists. `Aggregate` adds a ratio-scaled incoming value to the existing aggregate, truncating to `int64`.

State/persistence behavior: no internal state beyond the metric name. It reads snapshot counter maps and writes aggregate values in `CreateTimeSeries`.

Dependencies/integration: used by `metrics_timeseries.go` tests and callers that need counter history by time period.

Risks/test signals: fractional scaling truncates, so totals can lose small values when snapshots are split across many periods. Missing counters are skipped entirely.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_timeseries_counter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_timeseries_durations.go -->
# sources/sync-backup/kopia/internal/metrics/metrics_timeseries_durations.go

Purpose: implements a snapshot aggregator for duration distribution time series.

Important APIs/types/functions: `DurationDistributionValue`, `DurationDistributionValueAggregator`, `FromSnapshot`, `Aggregate`, and the compile-time `SnapshotValueAggregator` assertion.

Control flow: `FromSnapshot` selects a named duration distribution from a snapshot. `Aggregate` initializes an empty `DistributionState` if needed, then merges the incoming distribution with bucket counters scaled by the time-overlap ratio.

State/persistence behavior: aggregation mutates and returns the accumulated distribution state for a time bucket. It carries count/sum/min/max from incoming states without scaling count or sum, while bucket counters are scaled.

Dependencies/integration: works with generic distribution merge logic and `CreateTimeSeries`.

Risks/test signals: `mergeScaledFrom` scales buckets but not `Count` or `Sum`, so time-sliced distribution time series may have bucket counts proportionally split while count/sum remain fully accumulated. This may be intentional but is a semantic hotspot.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_timeseries_durations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_timeseries_sizes.go -->
# sources/sync-backup/kopia/internal/metrics/metrics_timeseries_sizes.go

Purpose: implements a snapshot aggregator for size distribution time series.

Important APIs/types/functions: `SizeDistributionValue`, `SizeDistributionValueAggregator`, `FromSnapshot`, `Aggregate`, and the compile-time `SnapshotValueAggregator` assertion.

Control flow: the aggregator extracts a named size distribution from a snapshot and merges it into a per-time-bucket accumulated `DistributionState[int64]`, scaling bucket counters according to snapshot overlap ratio.

State/persistence behavior: no standalone state beyond the metric name; aggregation mutates bucket-level accumulated distribution states in the time-series builder.

Dependencies/integration: mirrors duration distribution aggregation and uses generic distribution merge behavior.

Risks/test signals: like duration aggregation, bucket counters are scaled but count and sum are not scaled, creating possible interpretation differences for partially overlapping snapshots. Missing distribution names skip snapshots.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_timeseries_sizes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_timeseries_test.go -->
# sources/sync-backup/kopia/internal/metrics/metrics_timeseries_test.go

Purpose: validates time-series creation for counters and distribution buckets across users, hosts, aggregation modes, and time resolutions.

Important APIs/types/functions: `CreateTimeSeries`, `CounterValue`, `DurationDistributionValue`, `SizeDistributionValue`, `AggregateByHost`, `AggregateAll`, `TimeResolutionByHour`, `TimeResolutionByDay`, `TimeResolutionByMonth`, `TimeSeries`, and helpers `dayOf`/`monthOf`.

Control flow: counter tests construct snapshots with controlled start/end times and values, then assert exact bucket allocation for single-period, multi-period, host aggregation, all aggregation, default daily resolution, and month-length proportional allocation. Distribution tests build ten-day snapshots with bucket counters and assert each daily point receives scaled bucket counts from both snapshots.

State/persistence behavior: all snapshots are in-memory. Tests document proportional allocation semantics and integer truncation outcomes for calendar months.

Dependencies/integration: uses `testlogging.Context` even though time-series creation currently ignores context. Relies on UTC helper timestamps for deterministic expectations.

Risks/test signals: tests do not cover zero-duration snapshots or min/max/sum scaling for distributions. They strongly protect counter splitting and sorted point output.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_timeseries_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_timeseries_timeres.go -->
# sources/sync-backup/kopia/internal/metrics/metrics_timeseries_timeres.go

Purpose: defines time-bucket resolution functions used by metrics time-series aggregation.

Important APIs/types/functions: `TimeResolutionFunc`, `TimeResolutionByHour`, `TimeResolutionByDay`, `TimeResolutionByQuarter`, `TimeResolutionByWeekStartingSunday`, `TimeResolutionByWeekStartingMonday`, `TimeResolutionByMonth`, `TimeResolutionByYear`, `startOfSundayBasedWeek`, `startOfMondayBasedWeek`, and `startOfQuarter`.

Control flow: each resolution function returns the start of the containing period and the start of the next period in the timestamp's location. Hour uses `Truncate(time.Hour)`; day/month/year use calendar construction; week helpers subtract weekday offsets; quarter rounds month to the first month of its quarter.

State/persistence behavior: no state is stored. Returned boundaries determine how historical snapshots are bucketed and therefore affect time-series output.

Dependencies/integration: consumed by `CreateTimeSeries` and tests. Uses `time.Location` from the input timestamp, so local-time snapshots retain local calendar boundaries.

Risks/test signals: `TimeResolutionByWeekStartingMonday` comment says Sunday even though implementation starts Monday. DST transitions can make calendar periods non-24-hour; this is likely desired for local calendar aggregation but important for proportional ratios.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_timeseries_timeres.go -->
