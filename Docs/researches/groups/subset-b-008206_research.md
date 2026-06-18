# Research: subset-b-008206

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/storage-datatypes_gen.go -->
# sources/object-store/minio/cmd/storage-datatypes_gen.go

## Purpose

`storage-datatypes_gen.go` is generated `tinylib/msgp` serialization code for MinIO storage datatypes and storage REST/grid request and response envelopes. It gives the storage layer zero-reflection MessagePack encoders, decoders, byte marshalers, byte unmarshalers, and size estimators for the wire-facing types declared primarily in `storage-datatypes.go`.

The file is on the critical storage compatibility path. Types such as `DiskInfo`, `FileInfo`, `FileInfoVersions`, `VolInfo`, and `VolsInfo` carry disk metadata, object metadata, erasure metadata, inline object data, version listings, and volume information across internode RPC boundaries and sometimes represent persisted metadata formats. Handler parameter structs such as `DeleteVersionHandlerParams`, `ReadMultipleReq`, `RenameDataHandlerParams`, and `WriteAllHandlerParams` encode storage REST/grid calls compactly.

## Important APIs, Types, And Functions

Every generated type implements the same five-method msgp surface: `DecodeMsg(*msgp.Reader) error`, `EncodeMsg(*msgp.Writer) error`, `MarshalMsg([]byte) ([]byte, error)`, `UnmarshalMsg([]byte) ([]byte, error)`, and `Msgsize() int`.

The generated surface covers `BaseOptions`, `CheckPartsHandlerParams`, `CheckPartsResp`, `DeleteBulkReq`, `DeleteFileHandlerParams`, `DeleteOptions`, `DeleteVersionHandlerParams`, `DeleteVersionsErrsResp`, `DiskInfo`, `DiskInfoOptions`, `DiskMetrics`, `FileInfo`, `FileInfoVersions`, `FilesInfo`, `ListDirResult`, `LocalDiskIDs`, `MetadataHandlerParams`, `RawFileInfo`, `ReadAllHandlerParams`, `ReadMultipleReq`, `ReadMultipleResp`, `ReadPartsReq`, `ReadPartsResp`, `RenameDataHandlerParams`, `RenameDataInlineHandlerParams`, `RenameDataResp`, `RenameFileHandlerParams`, `RenameOptions`, `RenamePartHandlerParams`, `UpdateMetadataOpts`, `VolInfo`, `VolsInfo`, and `WriteAllHandlerParams`.

Tuple-encoded types use fixed arrays and strict arity checks. `DiskInfo` requires an 18-element array, `FileInfo` requires a 28-element array, `FileInfoVersions` requires a 5-element array, `VolInfo` requires a 3-element array, and each `VolsInfo` element is a 3-element `VolInfo` tuple. These checks make field additions, removals, or reordering wire-incompatible unless coordinated with an internode/storage metadata version bump.

Map-encoded request/response envelopes use compact `msg` tags and skip unknown fields. Examples include `ReadMultipleReq` keys `bk`, `pr`, `fl`, `ms`, `mo`, `ab`, and `mr`; `ReadMultipleResp` keys `bk`, `pr`, `fl`, `ex`, `er`, `d`, and `m`; `RenameDataHandlerParams` keys `id`, `sv`, `sp`, `dv`, `dp`, `fi`, and `ro`; and `MetadataHandlerParams` keys `id`, `v`, `ov`, `fp`, `uo`, and `fi`.

## Control Flow

Each decoder reads a map or array header, loops fields or tuple positions, decodes typed values, and wraps failures with field/index context via `msgp.WrapError`. Unknown map keys are consumed with `Skip`, which permits forward-compatible request maps where absent fields fall back to zero values. Tuple decoders instead reject arity mismatches with `msgp.ArrayError`, intentionally preventing silent compatibility drift for storage metadata objects.

Marshal paths preallocate with `msgp.Require(b, z.Msgsize())`, append a header, then append scalar fields and nested messages in deterministic struct order. Stream encoders write directly to `msgp.Writer`; byte unmarshalers return the remaining unconsumed bytes so callers and tests can detect trailing data. Slice decoders reuse existing capacity when possible; map decoders allocate on nil and call `clear` before repopulating an existing map, preventing stale keys when an instance is reused.

The generated `msgp:clearomitted` behavior is visible in omitted fields such as `ReadMultipleReq.Prefix` and `ReadMultipleResp.Prefix`/`Error`: decode paths track whether the field was present and explicitly reset omitted values to `""`. This matters when reusing structs from pools or across repeated decode calls.

## State And Persistence Behavior

The file does not perform disk I/O itself, but it defines the serialized shape of storage state and requests. `FileInfo` carries object metadata, erasure layout, replication state, inline data, checksum, version counters, and deletion flags. `RawFileInfo.Buf`, `FileInfo.Data`, and `FileInfo.Checksum` preserve nil-vs-empty byte-slice semantics where the original type requested `allownil`; decoders set nil for encoded nil and normalize non-nil byte reads to empty slices when needed.

`DiskMetrics` encodes maps of API latency accumulators and call counts plus aggregate availability, timeout, write, and delete counters. `RenameDataResp` carries a signature and an old data directory for the storage layer's two-phase rename cleanup. `CheckPartsResp` serializes integer status codes whose order is documented in `storage-datatypes.go` as data-loss-sensitive for mixed-version clusters.

## Dependencies And Integration Points

The only direct dependency is `github.com/tinylib/msgp/msgp`; nested generated calls integrate with msgp implementations on related MinIO types including `AccElem`, `ObjectPartInfo`, `ErasureInfo`, and `ReplicationState`. The generated handlers are consumed by storage REST/grid code around `StorageAPI` operations such as delete, rename, read, write, metadata update, disk info, read-multiple, and part verification.

The file is regenerated from `storage-datatypes.go` via `go:generate msgp -file=$GOFILE`; manual edits should not be made. Compatibility changes must be coordinated with comments in the hand-written datatype file that call out internode version bumps for metadata-bearing structures.

## Risks

The largest risk is wire incompatibility. Tuple arity changes fail hard, while map field tag changes silently change the protocol. `Msgsize()` is an upper-bound estimate; if it becomes too small, msgp will still grow buffers, but benchmarks and allocation assumptions can degrade. Reuse of slices and maps improves performance but means omitted-field clearing and nil handling are important for correctness.

Large encoded payloads can be carried in `FileInfo.Data`, `RawFileInfo.Buf`, `ReadMultipleResp.Data`, and `WriteAllHandlerParams.Buf`; callers must enforce size limits outside this file. Unknown fields are skipped in maps, so new optional fields are easier to roll out than tuple fields, but old nodes will discard them.

## Test Signals

`storage-datatypes_gen_test.go` exercises generated marshal/unmarshal and encode/decode paths for every generated type, verifies no trailing bytes remain, checks that `msgp.Skip` can skip encoded objects, warns on inaccurate `Msgsize`, and provides encode/decode/marshal benchmarks. `storage-datatypes_test.go` adds performance comparisons between msgp and gob for representative `VolInfo`, `DiskInfo`, and metadata-heavy `FileInfo` values.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/storage-datatypes_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/storage-datatypes_gen_test.go -->
# sources/object-store/minio/cmd/storage-datatypes_gen_test.go

## Purpose

`storage-datatypes_gen_test.go` is generated by `tinylib/msgp` alongside the storage datatype codecs. It provides smoke tests and microbenchmarks for the MessagePack serialization methods in `storage-datatypes_gen.go`.

The file confirms that each generated type can be marshaled to bytes, unmarshaled from bytes, streamed through `msgp.Encode`/`msgp.Decode`, skipped by a `msgp.Reader`, and benchmarked across marshal, append-marshal, unmarshal, encode, and decode paths.

## Important APIs, Types, And Functions

For each generated type, the file follows a fixed pattern:

- `TestMarshalUnmarshal<Type>` creates a zero-value `v`, calls `v.MarshalMsg(nil)`, calls `v.UnmarshalMsg(bts)`, asserts no error and no leftover bytes, and then verifies `msgp.Skip(bts)` consumes the full object.
- `TestEncodeDecode<Type>` encodes `v` to a `bytes.Buffer`, logs a warning if `buf.Len() > v.Msgsize()`, decodes into `vn`, and verifies a `msgp.NewReader(&buf).Skip()` path.
- `BenchmarkMarshalMsg<Type>`, `BenchmarkAppendMsg<Type>`, `BenchmarkUnmarshal<Type>`, `BenchmarkEncode<Type>`, and `BenchmarkDecode<Type>` measure the generated methods using `b.ReportAllocs()`.

The covered types match the generated implementation: `BaseOptions`, all storage handler parameter envelopes, `DiskInfo`, `DiskInfoOptions`, `DiskMetrics`, `FileInfo`, `FileInfoVersions`, `FilesInfo`, volume/listing/read-part/read-multiple types, rename types, `RawFileInfo`, and `UpdateMetadataOpts`.

## Control Flow

The tests are deliberately simple and mechanical. They rely on zero values for most types, so the flow validates codec shape, nil handling, skip support, and method availability more than semantic equality of populated objects. The encode/decode tests compare encoded length against `Msgsize()` only as a warning, not as a failure, because `Msgsize()` is documented as an upper-bound estimate.

Benchmarks pre-encode test values where needed, use `msgp.NewEndlessReader` for decode loops, and write encode benchmarks to `msgp.Nowhere` or a reusable buffer path. The append benchmark allocates a byte slice with capacity `v.Msgsize()` and repeatedly remarshal into `bts[0:0]`.

## State And Persistence Behavior

This file does not persist state. Its main state behavior is exercising zero-value encoded forms, including nil maps/slices/byte slices and empty embedded option structs. Because the generated implementation reuses buffers and clears omitted fields, the tests provide basic regression signals that zero values remain decodable and skippable.

The benchmarks help detect allocation regressions in storage metadata serialization, which is important because these datatypes are used in hot paths for internode storage calls and object metadata exchange.

## Dependencies And Integration Points

The file depends on Go `bytes`, `testing`, and `github.com/tinylib/msgp/msgp`. It integrates only through the generated methods on package `cmd` types. It is normally run as part of MinIO's package tests and regenerated when `storage-datatypes.go` changes.

## Risks

The main coverage gap is that the generated tests mostly use zero-value instances and do not assert deep equality after round trips. They will catch malformed code generation, trailing-byte handling, skip failures, and hard decode errors, but they are weak at catching semantic issues in populated maps, nested `FileInfo` values, optional omitted fields, `allownil` byte slices, or tuple compatibility changes.

Because this is generated code, local manual edits are brittle and can be overwritten. A broken `Msgsize()` only logs a warning in encode/decode tests, so allocation or sizing regressions may not fail CI unless accompanied by a hard serialization error.

## Test Signals

The file itself is the direct test signal for `storage-datatypes_gen.go`. Stronger complementary signals come from `storage-datatypes_test.go`, which benchmarks realistic `DiskInfo` and metadata-heavy `FileInfo` values, and from higher-level storage REST/grid tests that populate these envelopes in real calls.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/storage-datatypes_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/storage-datatypes_test.go -->
# sources/object-store/minio/cmd/storage-datatypes_test.go

## Purpose

`storage-datatypes_test.go` contains hand-written benchmarks for selected storage datatype serialization paths. Unlike the generated test file, this file compares msgp performance with Go gob for representative values and includes a populated `FileInfo` with realistic object metadata, erasure layout, encryption-related metadata keys, part metadata, checksums, and timestamps.

## Important APIs, Types, And Functions

The benchmark set covers:

- `BenchmarkDecodeVolInfoMsgp`, which decodes a msgp-encoded `VolInfo`.
- `BenchmarkDecodeDiskInfoMsgp` and `BenchmarkEncodeDiskInfoMsgp`, which measure msgp on a populated `DiskInfo`.
- `BenchmarkDecodeDiskInfoGOB` and `BenchmarkEncodeDiskInfoGOB`, which provide gob baselines for the same `DiskInfo`.
- `BenchmarkDecodeFileInfoMsgp` and `BenchmarkEncodeFileInfoMsgp`, which measure msgp on a complex `FileInfo`.
- `BenchmarkDecodeFileInfoGOB` and `BenchmarkEncodeFileInfoGOB`, which provide gob baselines for that complex `FileInfo`.

The benchmarks use `msgp.Encode`, `msgp.NewEndlessReader`, `msgp.NewReader`, `gob.NewEncoder`, `gob.NewDecoder`, `io.Discard`, `bytes.Buffer`, `time.Now`, and MinIO's `UTCNow()`.

## Control Flow

Each decode benchmark builds a value, encodes it once into a `bytes.Buffer`, logs the encoded size, configures allocation reporting and byte accounting, then repeatedly decodes from a reusable endless reader. Gob decode benchmarks keep the encoded byte slice and create a new `bytes.Buffer` and decoder each iteration. Encode benchmarks write to `io.Discard`, using either `msgp.Encode` or a reusable gob encoder.

The file uses `b.Loop()` loops, so benchmark execution depends on a Go toolchain that supports that testing API. There are no assertions outside fataling on encode/decode errors.

## State And Persistence Behavior

No persistent state is created. The benchmark values model storage-layer state: `DiskInfo` contains capacity and endpoint data; `FileInfo` models object version metadata, encryption metadata, part information, erasure coding parameters, distribution, and checksum records. The realistic `FileInfo` payload is important because metadata maps and nested slices dominate object metadata serialization cost.

## Dependencies And Integration Points

This file depends on standard-library `bytes`, `encoding/gob`, `io`, `testing`, and `time`, plus `github.com/tinylib/msgp/msgp`. It integrates with storage datatype definitions and generated msgp methods from the same package.

The practical integration signal is performance rather than correctness. These benchmarks justify and monitor the generated msgp path used by storage REST/grid calls and metadata movement.

## Risks

The benchmarks are not unit tests and will not fail on performance regressions unless a separate benchmark comparison process is used. They cover only a few representative values, so they do not exercise all generated datatypes, nil edge cases, omitted fields, tuple arity failures, or decode compatibility with older wire formats.

The gob comparison may not match production behavior, because production storage RPCs use msgp. It is useful as a relative baseline but should not be interpreted as a protocol compatibility test.

## Test Signals

Running these benchmarks provides allocation and throughput signals for `VolInfo`, `DiskInfo`, and `FileInfo` serialization. The generated test file remains the broader smoke-test signal for every generated codec.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/storage-datatypes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/storage-errors.go -->
# sources/object-store/minio/cmd/storage-errors.go

## Purpose

`storage-errors.go` centralizes storage-layer sentinel errors and maps low-level operating-system errors into MinIO storage errors. It gives disk, volume, file, bitrot, versioning, and backend failure paths stable error values that higher layers can classify and translate into object-layer or S3 API behavior.

## Important APIs, Types, And Functions

The file defines many package-level sentinels as `StorageErr`, including disk state errors (`errDiskNotFound`, `errFaultyDisk`, `errFaultyRemoteDisk`, `errDiskFull`, `errDiskAccessDenied`, `errUnsupportedDisk`, `errDriveIsRoot`), format/backend errors (`errCorruptedFormat`, `errCorruptedBackend`, `errUnformattedDisk`, `errInconsistentDisk`, `errXLBackend`), file and volume errors (`errFileNotFound`, `errFileVersionNotFound`, `errFileAccessDenied`, `errFileCorrupt`, `errPathNotFound`, `errVolumeNotFound`, `errVolumeExists`, `errVolumeNotEmpty`, `errVolumeAccessDenied`), and protocol/data errors (`errLessData`, `errMoreData`, `errBitrotHashAlgoInvalid`, `errMaxVersionsExceeded`).

It also defines plain `errors.New` control-flow sentinels: `errDoneForNow`, `errSkipFile`, and `errIgnoreFileContrib`. `baseErrs` contains common disk-unavailable errors, and `baseIgnoredErrs` currently aliases that slice.

`type StorageErr string` implements `Error() string`, making the sentinel value itself the message and keeping comparisons simple when callers hold the exact package variable.

`osErrToFileErr(err error) error` is the main function. It returns nil for nil input, maps not-exist, permission, not-directory/is-directory, path-not-found, too-many-files, invalid-handle, I/O, invalid-argument, and no-space conditions to storage sentinels, and returns unknown errors unchanged.

## Control Flow

`osErrToFileErr` is a prioritized classification chain. It first handles nil, then common object/file lookup failures, permission failures, path shape errors, file descriptor exhaustion, invalid handles, disk I/O failures, invalid arguments, and disk-full conditions. Invalid-argument errors are logged through `storageLogIf(context.Background(), err)` before returning `errFileNotFound`; the comment explains this is intended for odd `O_DIRECT` read behavior on some filesystems.

## State And Persistence Behavior

The file does not mutate storage state. Its sentinels shape persistence behavior indirectly by guiding callers: disk full prevents writes, not-found drives read/list/delete responses, faulty disk errors affect erasure set availability, and cross-device rename errors point to backend misconfiguration that can break atomic rename assumptions.

Because `StorageErr` values are strings, error text is part of the observable behavior. Changing messages can affect logs, tests, admin tooling, and any code comparing error strings instead of sentinel identity.

## Dependencies And Integration Points

The file imports `context` and `errors`. It depends on OS helper predicates declared elsewhere in the package, including `osIsNotExist`, `osIsPermission`, `isSysErrNotDir`, `isSysErrIsDir`, `isSysErrPathNotFound`, `isSysErrTooManyFiles`, `isSysErrHandleInvalid`, `isSysErrIO`, `isSysErrInvalidArg`, and `isSysErrNoSpace`. It also integrates with `storageLogIf` for unexpected invalid-argument logging.

Storage implementations, erasure code, REST handlers, healing, scanners, and object-layer translation code consume these sentinels to decide whether an operation is retryable, ignorable, fatal, or user-visible.

## Risks

Misclassification can cause serious behavior changes. Mapping an I/O error to not-found would hide disk corruption; mapping not-found to faulty disk would reduce availability; changing `errCrossDeviceLink` behavior could mask non-atomic backend renames. The alias `baseIgnoredErrs = baseErrs` means in-place mutation of either slice would affect the other.

The invalid-argument path deliberately maps to `errFileNotFound`, which is pragmatic for `O_DIRECT` edge cases but can hide other EINVAL causes after logging. Callers that wrap errors without preserving sentinel identity may also weaken classification.

## Test Signals

This file has no direct tests in the requested set. Useful coverage should include table tests for `osErrToFileErr` using representative `os.PathError` and platform-specific syscall errors, plus integration tests that ensure storage REST and object-layer code translate these sentinels to expected API errors.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/storage-errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/storage-interface.go -->
# sources/object-store/minio/cmd/storage-interface.go

## Purpose

`storage-interface.go` defines `StorageAPI`, the central abstraction for a MinIO storage disk or remote disk endpoint. It is the contract implemented by local XL storage and remote storage clients and consumed by erasure/object-layer code, healing, scanners, and storage REST/grid handlers.

The interface groups disk identity/lifecycle, disk health, namespace scanning, volume operations, metadata operations, file operations, bulk reads, verification, cleanup, and disk location access behind a single contract.

## Important APIs, Types, And Functions

Identity and lifecycle methods include `String`, `IsOnline`, `LastConn`, `IsLocal`, `Hostname`, `Endpoint`, `Close`, `GetDiskID`, `SetDiskID`, `Healing`, `DiskInfo`, `NSScanner`, and `GetDiskLoc`.

Volume methods include `MakeVol`, `MakeVolBulk`, `ListVols`, `StatVol`, and `DeleteVol`.

Metadata/object-version methods include `DeleteVersion`, `DeleteVersions`, `DeleteBulk`, `WriteMetadata`, `UpdateMetadata`, `ReadVersion`, `ReadXL`, and `RenameData`.

File and data-plane methods include `WalkDir`, `ListDir`, `ReadFile`, `AppendFile`, `CreateFile`, `ReadFileStream`, `RenameFile`, `RenamePart`, `CheckParts`, `Delete`, `VerifyFile`, `StatInfoFile`, `ReadParts`, `ReadMultiple`, `CleanAbandonedData`, `WriteAll`, and `ReadAll`.

The interface references important storage datatypes from nearby files: `DiskInfoOptions`, `DiskInfo`, `VolInfo`, `WalkDirOptions`, `FileInfo`, `FileInfoVersions`, `DeleteOptions`, `UpdateMetadataOpts`, `ReadOptions`, `RawFileInfo`, `RenameOptions`, `RenameDataResp`, `BitrotVerifier`, `CheckPartsResp`, `StatInfo`, `ReadMultipleReq`, and `ReadMultipleResp`.

## Control Flow

This file declares no implementation, but it shapes caller control flow. Object-layer code can treat local and remote disks uniformly: inspect online state and disk identity, perform volume setup, read or mutate metadata, stream or bulk-read files, check parts, and clean abandoned data. `context.Context` appears on every potentially blocking operation, making cancellation and request scoping part of the contract.

`ReadMultiple` is asynchronous from the caller's perspective: it accepts a request and sends `ReadMultipleResp` values on a caller-provided channel. `WalkDir` streams a metacache representation to an `io.Writer`. `ReadFileStream` returns an `io.ReadCloser`, pushing resource management to the caller.

## State And Persistence Behavior

Implementations of this interface own persistent storage behavior: creating/deleting volumes, writing metadata, updating `xl.meta`, appending and creating files, renaming data directories, deleting object versions, and cleaning abandoned data. The interface distinguishes metadata writes from data writes and has explicit options for delete, rename, read, and metadata persistence.

`RenameData` returns `RenameDataResp`, which includes old data directory information for two-phase cleanup. `UpdateMetadataOpts.NoPersistence` can alter sync behavior for metadata updates. `DiskInfo` and `NSScanner` expose disk state and data-usage scanning to higher layers.

## Dependencies And Integration Points

The file imports `context`, `io`, `time`, and `github.com/minio/madmin-go/v3`. It integrates with MinIO's endpoint model, healing tracker, data-usage cache, metacache walking, bitrot verification, object part metadata, and storage REST/grid serialization. The generated msgp datatypes in `storage-datatypes_gen.go` support the wire representation for many of these interface methods when the implementation is remote.

## Risks

Because `StorageAPI` is broad, adding or changing a method affects every local and remote implementation, mocks, tests, and wrapper types. Method semantics must stay aligned across local disks and remote clients; otherwise erasure sets can behave differently depending on disk locality. The `CreateFile` signature contains an `olume` parameter name typo, harmless for callers but a readability hazard.

Concurrency, cancellation, stream closure, and partial-write semantics are implementation-sensitive and not enforced by the interface. Any method returning storage sentinel errors from `storage-errors.go` must preserve enough identity for higher layers to make availability and API decisions.

## Test Signals

The requested files do not include direct interface conformance tests. Signals should come from compile-time implementation checks elsewhere, storage REST/grid tests, erasure integration tests, healing/scanner tests, and tests that exercise local and remote disks through the same `StorageAPI` contract.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/storage-interface.go -->
