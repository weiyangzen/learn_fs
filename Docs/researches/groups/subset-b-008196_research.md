# subset-b-008196 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-set.go -->
# sources/object-store/minio/cmd/metacache-set.go

Purpose: This file connects S3 listing requests to MinIO's metacache machinery. It defines `listPathOptions`, builds and updates `metacache` records, filters cached streams for list semantics, scans erasure-set disks when a cache must be created, persists the resulting listing into `.metacache` objects, and exposes lower-level quorum listing through `listPathRaw`.

Important APIs and types: `listPathOptions` carries bucket, base directory, prefix, marker, limit, separator, version/deleted-directory flags, disk quorum policy, transient/cache-create flags, and runtime-only bucket metadata (`Versioning`, `Lifecycle`, retention, replication). Key methods are `setBucketMeta`, `newMetacache`, `shouldSkip`, `gatherResults`, `findFirstPart`, `SetFilter`, and `(*metacacheReader).filter`. The erasure paths are `streamMetadataParts`, `listPath`, `saveMetaCacheStream`, and `listPathRaw`; `metaCacheRPC` coordinates remote status/error updates.

Control flow: A list request normalizes options and may read existing cache parts through `streamMetadataParts`. Block metadata is inspected with `findFirstPart` and `getMetacacheBlockInfo` so the reader can jump near the marker/prefix and stop when a block is past the requested range. When creating a cache, `listPath` selects disks according to `AskDisks`, shuffles/falls back when possible, configures `metadataResolutionParams`, and delegates disk walking to `listPathRaw`. `listPathRaw` starts one `WalkDir` stream per disk, peeks sorted entries, returns unanimously agreed entries directly, and calls the resolver on partial disagreements. `saveMetaCacheStream` consumes resolved entries, writes compressed block objects, periodically updates metacache status, and cancels if clients stop refreshing `lastHandout`.

State and persistence behavior: Persistent cache data is stored under `minioMetaBucket` at `bucketMetaPrefix/<bucket>/.metacache/<id>/block-N.s2`. Each block object contains an s2/msgp stream and carries JSON metadata named `x-minio-internal-metacache-part-N` with first/last object names and `EOS`; later blocks also update block 0 metadata so readers can discover them. Runtime state includes `metaCacheRPC.meta`, context cancellation, quorum disk selections, fallback disk state, and in-memory result buffers. Transient caches avoid saving an empty first block. Errors are propagated into the metacache status so readers waiting on remote listings can abort.

Dependencies and integration points: The file depends on bucket lifecycle/versioning/object-lock/replication subsystems, erasure-object disk APIs, `StorageAPI.WalkDir`, `FileInfo`, `DiskInfo` metrics, metadata resolution from `metaCacheEntry`, object IO helpers (`putMetacacheObject`, `updateObjectMetaWithOpts`, `getObjectWithFileInfo`), peer REST updates, and global notification hashing for remote cache ownership.

Risks: Correctness depends on all disk streams being sorted, stable string ordering for object names, and block metadata accurately tracking first/last/EOS. `findFirstPart` returns retry-oriented errors while a cache is still being written, so stale or missing metadata can create latency. Quorum relaxation with `AskDisks=auto` improves speed but can hide disagreement until metadata resolution. Client-liveness cancellation means slow consumers can turn a running listing into `scanStateError`. Lifecycle/replication filtering is request-local and deliberately not serialized.

Test signals: There is no direct unit test file for most of this implementation in this subset. Indirect signals come from metacache stream tests, generated `listPathOptions` msgp tests, metacache lifecycle tests, and broader MinIO listing/erasure tests that should cover cache-part discovery, quorum fallback, marker/prefix pagination, transient-cache behavior, and `.metacache` cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-set_gen.go -->
# sources/object-store/minio/cmd/metacache-set_gen.go

Purpose: This generated file implements the `tinylib/msgp` serialization contract for `listPathOptions`, the transport/persistence shape used when listing options are sent across storage RPCs or encoded for metacache coordination.

Important APIs and types: It provides `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` for `*listPathOptions`. Encoded fields are `ID`, `Bucket`, `BaseDir`, `Prefix`, `FilterPrefix`, `Marker`, `Limit`, `AskDisks`, `InclDeleted`, `Recursive`, `Separator`, `Create`, `IncludeDirectories`, `Transient`, `Versioned`, `V1`, `StopDiskAtLimit`, and the unexported `pool` and `set` integers.

Control flow: Decode reads a msgpack map header, switches on string keys, assigns known fields, and skips unknown keys for forward compatibility. Encode writes a fixed map of 19 fields. Marshal appends the same map into a caller-provided byte slice using `msgp.Require`; Unmarshal reads from a byte slice and returns the unconsumed tail. `Msgsize` computes an upper-bound allocation estimate.

State and persistence behavior: This file does not own storage state, but it defines which `listPathOptions` fields survive serialization. Runtime-only fields marked `msg:"-"` in the source type, such as lifecycle, versioning, retention, and replication config pointers, are intentionally absent and must be rehydrated on the receiving side if needed.

Dependencies and integration points: The generated code depends only on `github.com/tinylib/msgp/msgp` and the source `listPathOptions` type. It is used by grid/peer/listing code paths that need compact binary option transport and by generated tests that guard marshal/unmarshal behavior.

Risks: Manual edits would be overwritten by `go generate`. Adding a field to `listPathOptions` requires regenerating this file and considering whether that field should be serialized. Including unexported `pool` and `set` is intentional for local routing but creates a compatibility surface across mixed-version nodes.

Test signals: `metacache-set_gen_test.go` checks zero-value marshal/unmarshal, `msgp.Skip`, encode/decode, `Msgsize` sanity, and benchmark paths. Those tests do not populate all fields, so non-zero field round-trip coverage depends on broader integration tests or msgp generator correctness.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-set_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-set_gen_test.go -->
# sources/object-store/minio/cmd/metacache-set_gen_test.go

Purpose: This generated test file validates the generated msgp implementation for `listPathOptions` and provides serialization benchmarks.

Important APIs and types: It exercises `listPathOptions.MarshalMsg`, `UnmarshalMsg`, `EncodeMsg`, `DecodeMsg`, `Msgsize`, `msgp.Skip`, `msgp.Encode`, `msgp.Decode`, `msgp.NewReader`, `msgp.NewWriter`, and `msgp.NewEndlessReader`.

Control flow: `TestMarshalUnmarshallistPathOptions` marshals a zero-value `listPathOptions`, unmarshals it, and asserts no bytes remain; it then verifies `msgp.Skip` consumes the full payload. `TestEncodeDecodelistPathOptions` encodes to a `bytes.Buffer`, warns if `Msgsize` underestimates the encoded length, decodes back into a new value, and checks the stream can be skipped. Benchmarks measure marshal, append-style marshal, unmarshal, encode, and decode loops.

State and persistence behavior: The tests use only in-memory buffers and zero-value structs. No metacache object, disk, bucket metadata, or remote state is touched.

Dependencies and integration points: These tests are tied to `tinylib/msgp` generated code and protect the binary option contract used by listing and storage RPC paths. They complement production paths that populate real options with bucket names, prefixes, limits, and flags.

Risks: Coverage is mostly structural. Because the value under test is empty, the tests do not assert that every non-zero field round-trips correctly, that unknown fields are skipped in realistic payloads, or that runtime-only fields remain absent. Failures usually indicate generator/runtime incompatibility rather than listing logic regressions.

Test signals: Passing signals are no marshal/unmarshal errors, no leftover bytes, successful skip, successful stream encode/decode, and benchmark allocation/throughput data for the generated methods.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-set_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-stream.go -->
# sources/object-store/minio/cmd/metacache-stream.go

Purpose: This file defines the compressed metacache stream format and the reader/writer utilities used to serialize sorted `metaCacheEntry` values. It also implements block splitting metadata used when large listings are persisted as multiple `.s2` objects.

Important APIs and types: `metacacheStreamVersion` is the stream version. `metacacheWriter` writes s2-compressed msgpack streams through `write`, `stream`, `Close`, and `Reset`. `metacacheReader` supports lazy initialization, `peek`, `next`, `nextEOF`, `forwardTo`, `readN`, `readAll`, `readFn`, `readNames`, `skip`, and `Close`. `metacacheBlockWriter` groups entry streams into `metacacheBlock` values, and `metacacheBlock` exposes `headerKV`, `pastPrefix`, and `endedPrefix`.

Control flow: Writers lazily create an s2 writer and msgp writer, write a version byte, encode each entry as `true`, name, metadata bytes, then encode `false` on close. The streaming writer path uses a goroutine and channel to consume entries. Readers lazily read and validate version 1 or 2, keep one cached `current` entry for `peek`/`forwardTo`, convert truncated streams into `io.ErrUnexpectedEOF`, and provide fast name-only or prefix-limited scans. Block writing consumes entries from a channel, writes up to the channel capacity per block, finalizes each compressed block into a bytebuffer, and calls the supplied persistence callback.

State and persistence behavior: The stream format is persisted as s2-compressed msgpack in metacache block objects. Reader state is intentionally stateful: once `err` is set, future reads return it, and `current` can hold a prefetched entry. Metadata buffers are recycled through MinIO pools when entries are reusable or empty. Block metadata persists only the block number, first name, last name, and EOS flag, which readers use to skip blocks and determine prefix completion.

Dependencies and integration points: The file depends on `klauspost/compress/s2`, `tinylib/msgp`, MinIO buffer pools, bytebuffer pools, and `metaCacheEntry` helpers such as `isDir`, `isObject`, `isLatestDeletemarker`, `isObjectDir`, `isAllFreeVersions`, and `hasPrefix`. It is used by disk `WalkDir`, cache save/read paths, and raw quorum listing.

Risks: The stream assumes entries are sorted; `forwardTo`, prefix short-circuiting, and block first/last metadata become incorrect if writers send unsorted entries. Reader methods are not interchangeable without understanding state consumption. `readN` skips only a byte when it detects a name outside the prefix after reading the name header, relying on the following metadata skip semantics, so format changes need care. Pool reuse makes ownership of metadata byte slices important. Version handling accepts only 1 and 2.

Test signals: `metacache-stream_test.go` validates reading names, reading N entries, directory filtering, prefix searches, callback reads, channel reads, forward-to semantics, peek/next interaction, writer round-trip, and skip behavior using `testdata/metacache.s2`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-stream.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-stream_test.go -->
# sources/object-store/minio/cmd/metacache-stream_test.go

Purpose: This test suite locks down metacache stream reader/writer behavior against a fixed sample stream containing sorted Go source-style object and directory names.

Important APIs and types: Helpers `loadMetacacheSample` and `loadMetacacheSampleEntries` open `testdata/metacache.s2` and create `metacacheReader` instances. Tests exercise `readNames`, `readN`, `readFn`, `readAll`, `forwardTo`, `next`, `peek`, `newMetacacheWriter.write`, and `skip`.

Control flow: The tests compare reader output to `loadMetacacheSampleNames`. They cover full reads, zero-count reads, limited reads, directory inclusion/exclusion, prefix reads for existing and non-existing ranges, callback traversal, channel traversal with a wait group, forwarding to exact and partial names, sequential `next`, repeated `peek` followed by `next`, writer round-trip into a `bytes.Buffer`, and skipping across stream positions.

State and persistence behavior: Persistent input is the fixture file `testdata/metacache.s2`; output is in-memory only. The suite validates reader state transitions, especially that `peek` preserves the current entry for `next`, `readN(0)` is non-consuming, and `skip` advances through the encoded name/metadata pairs.

Dependencies and integration points: Tests depend on the sample stream remaining sorted and on `metaCacheEntry` directory classification. They indirectly protect disk walking and metacache persistence because those systems consume the same stream format and reader APIs.

Risks: The fixture has mostly names and no emphasis on rich object metadata, delete markers, versioned entries, corrupt streams, or concurrent writer stream errors. Because expected names are hard-coded, legitimate fixture regeneration requires updating the large expected slice.

Test signals: Strong signals are exact ordered name equality, expected `io.EOF` at natural stream end, zero-length reads returning no error, prefix reads returning the expected slices, successful writer/readback round-trip, and `skip` returning `io.EOF` when asked to skip past the end.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-stream_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-walk.go -->
# sources/object-store/minio/cmd/metacache-walk.go

Purpose: This file implements per-disk directory walking for metacache listings and exposes it over local storage wrappers and remote grid streams. It is the disk-side producer of sorted `metaCacheEntry` streams consumed by `listPathRaw`.

Important APIs and types: `WalkDirOptions` specifies bucket, base directory, recursive mode, not-found reporting, one-level `FilterPrefix`, `ForwardTo`, limit, and disk ID. `(*xlStorage).WalkDir` performs the actual filesystem traversal. Wrappers `(*xlStorageDiskIDCheck).WalkDir`, `(*storageRESTClient).WalkDir`, and `(*storageRESTServer).WalkDirHandler` add disk-health tracking and remote transport.

Control flow: `xlStorage.WalkDir` validates the volume and access, creates a small-block `metacacheWriter`, and streams entries through a channel. It first handles the S3-specific case where a slash-suffixed base path may itself be a directory object. `scanDir` lists directory entries, filters by prefix and forward marker, reads `xl.meta` or legacy `xl.json`, emits object entries immediately, collects possible directory entries, sorts them, emits directory markers in lexical order, and recurses when requested. It stops early on context cancellation or object limit.

State and persistence behavior: The walker reads object metadata from the disk layout but does not mutate storage. Runtime state includes object count for limit enforcement, directory-object tracking, stack of directories to emit, temporary buffers, and optional walk locks. The remote client serializes `WalkDirOptions` with msgp and streams bytes from a grid handler into the caller's writer.

Dependencies and integration points: It depends on `xlStorage` filesystem helpers, metadata files (`xl.meta`, legacy `xl.json`), volume access checks, disk health tracking, `grid.HandlerWalkDir`, `grid.WriterToChannel`, and the metacache stream writer. It integrates directly with `StorageAPI.WalkDir` calls from `listPathRaw`.

Risks: Correct ordering is subtle because object-vs-directory detection requires metadata reads after directory listing. Concurrent object rewrites can produce EOF or unexpected EOF while reading metadata; the code logs and skips these cases. Prefix and forward handling are lexical and conservative. Legacy filesystem support and `isDirEmpty` behavior vary by filesystem type. Disk ID mismatches must be handled to avoid reading from a replaced drive.

Test signals: This file has generated serialization tests for `WalkDirOptions` but no focused unit test for `xlStorage.WalkDir` in this subset. Practical signals come from listing integration tests: sorted output, recursion, directory objects, limit enforcement, not-found behavior, legacy metadata, disk-health accounting, and remote grid streaming.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-walk.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-walk_gen.go -->
# sources/object-store/minio/cmd/metacache-walk_gen.go

Purpose: This generated file implements `tinylib/msgp` serialization for `WalkDirOptions`, the request payload used to invoke disk walking locally and over storage REST/grid streams.

Important APIs and types: It defines `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` for `*WalkDirOptions`. The encoded map contains `Bucket`, `BaseDir`, `Recursive`, `ReportNotFound`, `FilterPrefix`, `ForwardTo`, `Limit`, and `DiskID`.

Control flow: Decode and Unmarshal switch on msgpack map keys, assign known fields, and skip unknown fields. Encode and Marshal write a fixed 8-field map. `Msgsize` estimates the serialized size for preallocation.

State and persistence behavior: No storage is modified. The file defines the binary compatibility boundary for remote disk walks, including the disk identity check value that prevents a client from streaming from the wrong physical disk after replacement.

Dependencies and integration points: It depends on `github.com/tinylib/msgp/msgp` and the `WalkDirOptions` type. `storageRESTClient.WalkDir` calls `MarshalMsg` before opening `grid.HandlerWalkDir`, and `storageRESTServer.WalkDirHandler` calls `UnmarshalMsg` before validating disk ID and invoking `xlStorage.WalkDir`.

Risks: Any field added to `WalkDirOptions` must be regenerated and reviewed for mixed-version behavior. Because remote walks are performance-sensitive, `Msgsize` and allocation behavior matter. Unknown-field skipping helps forward compatibility, but missing fields default to zero values that can change traversal semantics.

Test signals: `metacache-walk_gen_test.go` covers zero-value marshal/unmarshal, skip, encode/decode, `Msgsize` warning, and serialization benchmarks.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-walk_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-walk_gen_test.go -->
# sources/object-store/minio/cmd/metacache-walk_gen_test.go

Purpose: This generated test file validates the msgp serialization helpers for `WalkDirOptions` and benchmarks their throughput/allocation behavior.

Important APIs and types: It uses `WalkDirOptions`, generated `MarshalMsg`, `UnmarshalMsg`, `EncodeMsg`, `DecodeMsg`, `Msgsize`, and msgp helpers including `Skip`, `Encode`, `Decode`, `NewReader`, `NewWriter`, and `NewEndlessReader`.

Control flow: `TestMarshalUnmarshalWalkDirOptions` marshals a zero-value options struct, unmarshals it, and asserts that no bytes remain; it also checks that `msgp.Skip` consumes the full payload. `TestEncodeDecodeWalkDirOptions` performs stream encode/decode and checks skip behavior through a msgp reader. Benchmarks cover marshal, append marshal, unmarshal, encode, and decode loops.

State and persistence behavior: Tests use in-memory buffers only. They do not touch disks, buckets, grid streams, or metacache output files.

Dependencies and integration points: The test protects the generated transport contract used by `storageRESTClient.WalkDir` and `storageRESTServer.WalkDirHandler`. It is a structural complement to higher-level listing tests.

Risks: Zero-value-only coverage will not catch field-specific mistakes such as a non-empty `DiskID`, `ForwardTo`, or `Limit` failing to round-trip. It also does not exercise unknown-field compatibility beyond the generic skip call.

Test signals: Passing signals are clean marshal/unmarshal, full byte consumption, successful encode/decode, successful reader skip, and benchmark measurements for the generated code.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-walk_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metacache.go -->
# sources/object-store/minio/cmd/metacache.go

Purpose: This file defines the lifecycle state for a metacache listing and the core rules for keeping, refreshing, updating, and deleting cached listing data.

Important APIs and types: `scanStatus` has `scanStateNone`, `scanStateStarted`, `scanStateSuccess`, and `scanStateError`. `metacache` stores timestamps (`started`, `ended`, `lastHandout`, `lastUpdate`), bucket/root/filter/id, status, error text, recursive flag, file-not-found flag, and stream data version. Key methods are `finished`, `worthKeeping`, `keepAlive`, `update`, and `delete`; `baseDirFromPrefix` computes a listing base directory.

Control flow: `worthKeeping` removes stale running listings, old finished listings, and stale failed/none states. `keepAlive` periodically updates `lastHandout` through a local or remote peer while a request context is alive, and stops when the scan leaves `scanStateStarted`. `update` merges another metacache state into the current record, sets success/end timestamps, transitions away from started, marks clients missing after `metacacheMaxClientWait`, captures the first error, and preserves `fileNotFound`. `delete` validates bucket/id and asks the object layer to delete the `.metacache` prefix.

State and persistence behavior: The `metacache` struct is msgp-serializable and is the persisted/cache-manager record for listing state. The actual listing data is stored separately as metacache block objects. Deletion removes all cache data below the derived `.metacache` prefix through a `deleteAllStorager` object layer.

Dependencies and integration points: It interacts with peer REST `UpdateMetacacheListing`, `localMetacacheMgr`, global object-layer creation, `deleteAllStorager`, MinIO metadata bucket paths, and debug logging. It is constructed from `listPathOptions.newMetacache` and serialized by `metacache_gen.go`.

Risks: Lifecycle decisions are time-sensitive, so clock skew or slow clients can discard useful caches. `update` assigns `m.lastHandout = update.lastUpdate` when `update.lastHandout` is newer, which is subtle and should be reviewed before changing. `delete` depends on the global object layer being available and implementing `deleteAllStorager`.

Test signals: `metacache_test.go` checks `baseDirFromPrefix`, `finished`, and `worthKeeping` across successful, recursive, stale, errored, running, not-found, and week-old cases. Generated tests cover binary serialization.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metacache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metacache_gen.go -->
# sources/object-store/minio/cmd/metacache_gen.go

Purpose: This generated file implements msgp serialization for `metacache` and `scanStatus`, defining the compact persisted/transport representation of listing cache state.

Important APIs and types: It provides `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` for `*metacache`, plus the same methods for `scanStatus`. Encoded metacache keys use short msg tags: `end`, `st`, `lh`, `u`, `b`, `flt`, `id`, `err`, `root`, `fnf`, `stat`, `rec`, and `v`.

Control flow: Decode/Unmarshal read msgpack maps and assign timestamp, string, bool, uint8, and status fields while skipping unknown keys. Encode/Marshal write a fixed 13-field map. `scanStatus` is encoded as a uint8.

State and persistence behavior: This file does not make state transitions itself, but it controls durable metacache field compatibility. It preserves timestamps, status, error, bucket/id/root/filter, recursive mode, file-not-found state, and stream version. Any field not represented here will not survive manager persistence or peer transport.

Dependencies and integration points: It depends on `tinylib/msgp/msgp` and the production `metacache` definitions. Cache managers, peer update calls, and tests rely on this binary contract.

Risks: Manual edits are unsafe because regeneration will overwrite them. Reordering or retagging fields can break mixed-version compatibility. `scanStatus` has no validation in generated decode, so unknown numeric states can enter memory if read from corrupt or future payloads.

Test signals: `metacache_gen_test.go` validates zero-value marshal/unmarshal, skip, stream encode/decode, `Msgsize` sanity, and benchmarks. Behavioral status transitions are tested in `metacache_test.go`, not here.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metacache_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metacache_gen_test.go -->
# sources/object-store/minio/cmd/metacache_gen_test.go

Purpose: This generated test file validates the msgp serialization implementation for the `metacache` struct and benchmarks generated methods.

Important APIs and types: It uses `metacache`, generated `MarshalMsg`, `UnmarshalMsg`, `EncodeMsg`, `DecodeMsg`, `Msgsize`, and msgp utilities for skip, stream encode/decode, writer, reader, and endless reader benchmarking.

Control flow: `TestMarshalUnmarshalmetacache` marshals a zero-value cache, unmarshals it, checks no bytes remain, and verifies `msgp.Skip` consumes the payload. `TestEncodeDecodemetacache` encodes to a buffer, warns if `Msgsize` is too small, decodes into a new value, and verifies reader skip. Benchmarks cover marshal, append marshal, unmarshal, encode, and decode.

State and persistence behavior: The tests operate entirely in memory with zero-value `metacache`. They do not create cache-manager entries, remote updates, or `.metacache` block objects.

Dependencies and integration points: These tests protect the generated binary format used by metacache managers and peer coordination. They are most useful as generator/runtime compatibility checks.

Risks: Like the other generated tests, this suite does not assert populated timestamps, status values, IDs, or error strings round-trip. It also does not cover unknown numeric `scanStatus` values or mixed-version payloads.

Test signals: Passing signals are error-free marshal/unmarshal, no remaining bytes, successful skip, successful stream decode, and stable benchmark behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metacache_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metacache_test.go -->
# sources/object-store/minio/cmd/metacache_test.go

Purpose: This test file validates small but important metacache lifecycle helpers: base-directory derivation, finished-state detection, and cache-retention decisions.

Important APIs and types: It defines `metaCacheTestsetTimestamp` and `metaCacheTestset`, a slice of representative `metacache` values covering normal success, recursive success, older success, error, stale started, not-found success, older recursive success, running, and week-old finished cases. Tests call `baseDirFromPrefix`, `metacache.finished`, and `metacache.worthKeeping`.

Control flow: `Test_baseDirFromPrefix` checks root object, dot-slash, slash, folder, folder/object, nested folder/object, and nested folder prefixes. `Test_metacache_finished` compares each fixture against expected end-time-derived booleans. `Test_metacache_worthKeeping` checks which caches should survive according to age, status, and last-handout/update rules.

State and persistence behavior: No persistent state is created. The fixtures model persisted metacache records by setting timestamps and status fields directly. Retention expectations are time-relative to `time.Now()` at package initialization, so the tests simulate stale records by subtracting minutes or days.

Dependencies and integration points: These tests protect logic used by the metacache manager cleanup path and listing request routing. `baseDirFromPrefix` also affects cache sharing and scan roots derived from list prefixes.

Risks: The `worthKeeping` test contains a TODO and uses real current time rather than an injected clock, so it is sensitive to long pauses between fixture initialization and assertions. It does not cover `keepAlive`, `update`, or `delete`, which have more complex interactions with peers and object-layer state.

Test signals: Exact expected base directory strings, `finished` true only when `ended` is non-zero, and retention booleans for stale running, old failed, recent success, and week-old finished caches.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metacache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-realtime.go -->
# sources/object-store/minio/cmd/metrics-realtime.go

Purpose: This file collects on-demand local and remote realtime metrics for disks, scanner, OS, batch jobs, site resync, network, memory, CPU, and RPC subsystems.

Important APIs and types: `collectMetricsOpts` filters hosts, disks, job ID, and deployment ID. `collectLocalMetrics` returns `madmin.RealtimeMetrics`; `collectLocalDisksMetrics` returns per-disk `madmin.DiskMetric`; `collectRemoteMetrics` merges peer metrics from the notification system.

Control flow: `collectLocalMetrics` exits for `MetricsNone`, resolves the reporting host name, and conditionally fills requested metric groups based on `madmin.MetricType.Contains`. Disk collection builds per-disk metrics and an aggregate. Scanner, OS, batch, and site-resync metrics come from global metric reporters. Network stats query the internode interface. Memory uses `madmin.GetMemInfo`. CPU uses gopsutil CPU time/count/load calls. RPC reads grid connection stats if the grid is initialized. The final metrics object stores a shallow `ByHost` map pointing at the aggregate. Remote collection is skipped unless the node is distributed erasure, then all peer responses are merged.

State and persistence behavior: The file does not persist data. It samples global runtime state and OS counters. Disk metrics include lifetime and last-minute API calls, healing/offline markers, and Linux drive stats when available.

Dependencies and integration points: It integrates with madmin metric types, global scanner/OS/batch/site-resync metric providers, object-layer storage info, internal disk and net packages, gopsutil CPU/load, global grid stats, endpoint host resolution, and the notification system's peer metric fan-out.

Risks: Host filtering depends on endpoint naming and can return an empty result for mismatches. OS/stat calls can fail and are recorded as strings in `Errors`. `ByHost` uses a shallow aggregate reference, so callers must avoid mutating shared data. Disk stat availability varies by platform and drive state. Remote merge behavior depends on peer responsiveness and distributed-erasure mode.

Test signals: No direct tests are present in this subset. Signals should come from admin/metrics integration tests that assert selected metric groups appear, errors are surfaced, host/disk filtering works, and distributed peer merges preserve local plus remote values.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-realtime.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-resource.go -->
# sources/object-store/minio/cmd/metrics-resource.go

Purpose: This file implements MinIO's resource metrics collector for Prometheus: periodic local resource sampling, rolling current/average/max values, peer collection, and handler construction for `/v2/metrics/resource`.

Important APIs and types: Constants define collection/cache intervals and resource metric names for drives, network interfaces, memory, and CPU. `PeerResourceMetrics`, `ResourceMetrics`, and `ResourceMetric` model collected values. Key functions are `getResourceKey`, `updateResourceMetrics`, `updateDriveIOStats`, `collectDriveMetrics`, `collectLocalResourceMetrics`, `initLatestValues`, `startResourceMetricsCollection`, `prepareResourceMetrics`, `getResourceMetrics`, and `metricsResourceHandler`. `minioResourceCollector` implements Prometheus `Describe` and `Collect`.

Control flow: `init` builds help text, registers the resource metrics group, and creates the collector. `startResourceMetricsCollection` initializes disk baselines, clears the global map, samples once, then samples every minute until `GlobalContext` is done. Sampling calls `collectLocalMetrics` for disk/net/mem/CPU, converts cumulative network counters into deltas, records memory totals and percentages, computes CPU percentage/load values, updates drive IO rates from disk stat deltas, and records drive space/inode gauges. Prometheus collection publishes local cached metrics and remote peer metrics concurrently.

State and persistence behavior: Runtime state is held in `resourceMetricsMap`, protected by `resourceMetricsMapMu`, and drive baselines in `latestDriveStats`, protected by `latestDriveStatsMu`. `ResourceMetric` tracks current, cumulative baseline, max, sum, average, and count. There is no on-disk persistence.

Dependencies and integration points: It depends on `collectLocalMetrics`, `globalNotificationSys.GetResourceMetrics`, Prometheus client APIs, MinIO `MetricsGroupV2`, metric description helpers, local drive maps, and madmin disk IO structures. It feeds the resource metrics HTTP handler registered by `metrics-router.go`.

Risks: `getResourceKey` concatenates map values in iteration order; current callers mostly use zero or one label, but multi-label metrics could become nondeterministic. `updateResourceMetrics` compares `metric.Current` but assigns `metric.Max = val`, which is subtle for cumulative counters. CPU percentage calculation assumes non-zero total time. The collector publishes peer and local metrics concurrently, so slow peers can affect scrape latency.

Test signals: No direct tests are present in this subset. Useful signals would include deterministic metric keys, correct cumulative deltas, drive IO rate math across refresh intervals, average/max behavior, no divide-by-zero CPU failures, and Prometheus output containing local and peer resource metrics with expected labels.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-resource.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-router.go -->
# sources/object-store/minio/cmd/metrics-router.go

Purpose: This file registers MinIO Prometheus metrics HTTP routes and selects whether those routes require JWT authentication or are public.

Important APIs and types: Constants define legacy, v2 cluster/bucket/node/resource, and v3 metrics paths, plus environment variables `MINIO_PROMETHEUS_AUTH_TYPE` and `MINIO_PROMETHEUS_OPEN_METRICS`. `prometheusAuthType` supports `jwt` and `public`. The main API is `registerMetricsRouter`.

Control flow: `registerMetricsRouter` creates a subrouter under the reserved MinIO bucket path, reads `MINIO_PROMETHEUS_AUTH_TYPE` through `env.Get`, lowercases it, and chooses `AuthMiddleware` by default or `NoAuthMiddleware` for `public`. It then registers legacy, v2 cluster, v2 bucket, v2 node, and v2 resource handlers. Finally it creates the v3 metrics server with the same auth middleware and registers `GET /metrics/v3{pathComps:.*}`, including support for query behavior implemented by that server.

State and persistence behavior: No persistent state is written. Runtime state is limited to route registration and environment-based auth choice during server setup.

Dependencies and integration points: It depends on `github.com/minio/mux`, `github.com/minio/pkg/v3/env`, MinIO auth middlewares, v2 metrics handlers, `metricsResourceHandler`, and `newMetricsV3Server`. It is part of the server router initialization path.

Risks: Setting auth type to `public` exposes metrics without JWT, which is operationally intentional but security-sensitive. Unknown auth values silently fall back to JWT. The declared `MINIO_PROMETHEUS_OPEN_METRICS` constant is not used in this file. Route ordering and reserved bucket prefix must remain consistent with other API routers.

Test signals: No direct tests are present in this subset. Integration signals should verify route availability, default JWT protection, public mode behavior, v2 resource handler registration, and v3 wildcard path handling.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-router.go -->
