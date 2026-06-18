# Research: subset-b-008210

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-v2.go -->
# sources/object-store/minio/cmd/xl-storage-format-v2.go

## Purpose
This is the core MinIO XL metadata v2 implementation. It defines the persisted `xl.meta` v2 wire layout, object/delete/legacy version records, shallow indexed headers, conversion from old JSON/legacy msgp metadata, version mutation operations, conversion to `FileInfo`, and quorum merging across erasure-set disks. The file is central to object state persistence for erasure-backed storage: object data parts live in per-version data directories, while this file records the version stack, erasure layout, tiering state, replication purge state, inline small data, and delete markers.

## Important APIs, Types, and Functions
`VersionType`, `ErasureAlgo`, and `ChecksumAlgo` encode persisted enum values for journal entries and erasure/checksum algorithms. `xlMetaV2Object` stores an object version: version/data-dir UUIDs, erasure M/N/index/distribution, part numbers/sizes/ETags/compression indexes, user metadata, internal metadata, size, and modtime. `xlMetaV2DeleteMarker` stores delete-marker identity, modtime, and internal metadata. `xlMetaV2Version` wraps one of object v2, delete marker, or legacy v1 object and records `WrittenByVersion`.

`xlMetaV2VersionHeader` is the indexed shallow header. It stores version ID, modtime, signature, type, flags, and EC M/N so list/merge paths can inspect metadata without full version unmarshalling. Header helpers (`sortsBefore`, `matchesNotStrict`, `matchesEC`, `FreeVersion`, `UsesDataDir`, `InlineData`) drive stable ordering, quorum matching, and hidden/free-version behavior.

`checkXL2V1`, `isIndexedMetaV2`, `decodeXLHeaders`, and `decodeVersions` parse the header and indexed metadata envelope. `LoadOrConvert`, `Load`, `loadIndexed`, and `loadLegacy` populate `xlMetaV2`, repairing inline data and converting older formats when needed. `AppendTo` writes current v1.3 indexed metadata: XL header/version, msgp metadata blob, CRC, and inline data tail. `AddVersion`, `UpdateObjectVersion`, `DeleteVersion`, `AddLegacy`, `ToFileInfo`, `ListVersions`, `SharedDataDirCount`, and `getDataDirs` are the primary mutation/query APIs. `xlMetaBuf` provides zero-copy-ish read-only `ToFileInfo`, `ListVersions`, `IsLatestDeleteMarker`, and `AllHidden` over indexed metadata.

## Control Flow
Loading first checks the `XL2 ` header and major/minor version. v1.3 indexed metadata is parsed into shallow version headers plus raw per-version `meta` slices; inline data is retained as `xlMetaInlineData`. Older v1.0-v1.2 metadata is decoded from the legacy full `Versions` map, converted into shallow entries, then sorted by modtime. Indexed load also contains targeted compatibility repair paths: older delete-marker replication timestamps are normalized by full unmarshal/remarshal, and compressed small-part indexes produced by a known historical bug are removed and reindexed for affected writer versions.

Mutation APIs generally parse the caller's `FileInfo` UUIDs, locate the matching shallow entry by version ID, unmarshal only that entry when needed, modify the specific fields, then `setIdx` remarshal/reheader the entry. `AddVersion` converts `FileInfo` into object or delete-marker metadata and either replaces an existing version ID or inserts by descending modtime. `DeleteVersion` handles multiple cases: adding delete markers, updating replication purge state, deleting object or legacy entries, recording tier free-versions, clearing restore headers, marking transitions complete, and returning the data directory that is safe to remove only when no surviving on-disk version shares it.

Read/list flows skip free-versions unless explicitly requested or unless no non-free versions remain and the caller asked to include them. `mergeXLV2Versions` combines per-disk version streams by repeatedly selecting the latest quorum-satisfying header, using strict header equality or non-strict matching that tolerates signature differences when version/type/EC match, then advances each stream past selected or superseded entries.

## State and Persistence Behavior
The persisted format is versioned independently at the outer XL major/minor level and the inner header/meta versions. Current writes use major 1 minor 3, header version 3, and meta version 3. The metadata blob includes a fixed-size CRC of the indexed section; inline data follows outside that CRC and is separately msgp-validated/repaired. Signatures are deterministic xxhash-derived summaries that intentionally ignore disk-local fields such as erasure index and normalize nil/empty optional slices so replicas can compare logical equality.

Object state is split between local filesystem data directories and metadata. Transitioned objects may not use a local data directory unless restored on disk. Inline objects store payload bytes in `xlMetaInlineData`, indexed by version ID/null version ID, and set an internal inline-data metadata marker. Free-versions are delete-marker-shaped records marked by flags/internal metadata and are hidden from normal version counts.

## Dependencies and Integration Points
The file integrates with `FileInfo`, `ObjectPartInfo`, `ErasureInfo`, replication state helpers, lifecycle transition constants, storage class filtering, HTTP/S3 metadata constants, MinIO globals (`globalAPIConfig`, `globalVersionUnix`, `GlobalContext`), `xlMetaV1Object` legacy conversion, and `metaCacheEntry` listing/merge paths. It depends on `msgp` for wire encoding, `xxhash` for signatures/CRC, `uuid` for version/data-dir IDs, `jsoniter` for v1 JSON metadata conversion, and MinIO buffer pools for allocation control.

## Risks and Edge Cases
The file is high-risk because it owns durable object metadata compatibility. Changes to enum values, msgp tags, header tuple shape, signature normalization, or version sorting can make existing objects unreadable or cause erasure-set quorum disagreement. `AddVersion` and `ToFileInfo` assume part slice lengths are mutually consistent when `allParts` is true; malformed metadata could panic if `PartActualSizes` is shorter than part numbers. The free-version and transition branches are subtle: failing to set/clear inline-data, tier metadata, or restore headers can leak tiered content or prematurely remove local data. `mergeXLV2Versions` has complex stream advancement and duplicate suppression, so modifications need tests across strict/non-strict quorum, identical version IDs with differing signatures, and requested-version limits.

## Test Signals
Covered by `xl-storage-format-v2_test.go` for corrupt read trimming, inline data round-trip/removal/rename/trim, `UsesDataDir`, shared data-dir delete safety, legacy-to-indexed load, timestamp/signature normalization, quorum merge behavior, metacache merge ordering, healing metadata filtering, and fast `xlMetaBuf.ToFileInfo` benchmarks. `xl-storage-free-version_test.go` covers free-version visibility and skip semantics. `xl-storage-format_test.go` benchmarks add/update/delete/list flows over many versions and validates old v1 parsing. Generated codec tests cover msgp round-trip/skip behavior for the persisted structs.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-v2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-v2_gen.go -->
# sources/object-store/minio/cmd/xl-storage-format-v2_gen.go

## Purpose
This generated file supplies `tinylib/msgp` encoders, decoders, marshalers, unmarshalers, and `Msgsize` estimates for the XL metadata v2 enum and record types defined in `xl-storage-format-v2.go`. It is part of the durable on-disk wire contract for MinIO object metadata and should be regenerated from source annotations rather than hand-edited.

## Important APIs, Types, and Functions
The scalar enum codecs cover `ChecksumAlgo`, `ErasureAlgo`, `VersionType`, and `xlFlags` as single `uint8` values. `xlMetaBuf` is encoded as raw bytes. `xlMetaDataDirDecoder` is a shallow map decoder for only `V2Obj.DDir`; `SharedDataDirCount` uses it to avoid full object unmarshalling when checking data-dir sharing.

The main codecs are for `xlMetaV2DeleteMarker`, `xlMetaV2Object`, `xlMetaV2Version`, and tuple-style `xlMetaV2VersionHeader`. Delete markers encode fields `ID`, `MTime`, and optional `MetaSys`. Object versions encode all erasure fields, part arrays, size/modtime, optional `PartIdx`, and allownil `PartETags`, `PartASizes`, `MetaSys`, and `MetaUsr`. `xlMetaV2Version` encodes `Type`, optional `V1Obj`, optional `V2Obj`, optional `DelObj`, and writer version `v`. The header is encoded as a fixed array of seven values, making the tuple arity a compatibility boundary.

## Control Flow
Each decode path reads a map or array header, switches on msgp field names, fills the target struct, skips unknown fields, and clears omitted pointer/slice/map fields according to the generated clear-omitted behavior. Encode/marshal paths compute omitted-field masks, write map headers sized to the emitted fields, then serialize fields in generated order. Unmarshal paths return the unused suffix so callers can verify no trailing bytes remain or compose decoders. `Msgsize` functions provide upper-bound allocation sizing for `msgp.Require` and benchmark allocation control.

## State and Persistence Behavior
The field names in this file are the persisted schema names used in `xl.meta`: short tags like `ID`, `DDir`, `EcM`, `EcN`, `PartIdx`, `MetaSys`, `MetaUsr`, `DelObj`, and `v`. Unknown fields are skipped, supporting forward compatibility, while missing omitted fields are cleared to avoid stale data when reusing structs. The tuple header requires exactly seven elements, so any header shape change requires coordinated version handling in `xl-storage-format-v2-legacy.go` and `decodeXLHeaders`.

## Dependencies and Integration Points
The file depends on `github.com/tinylib/msgp/msgp` and the hand-written types from the same package. It is invoked by `xlMetaV2.AppendTo`, `loadIndexed`, `loadLegacy`, `getIdx`, `setIdx`, signature generation, compatibility repairs, `xlMetaBuf` readers, and tests. It also delegates legacy object codec work to `xlMetaV1Object` methods generated elsewhere.

## Risks and Edge Cases
The biggest risk is drift between source struct tags and generated output. Manual edits would be overwritten and can silently change disk encoding. Changing allownil/omitempty tags affects nil-vs-empty normalization and signatures. `xlMetaV2VersionHeader` has strict array-size validation, so adding fields without versioned unmarshal support will reject existing/new metadata. Map iteration order is not deterministic, but higher-level signature code hashes maps separately and removes maps before marshaling when deterministic signatures are required.

## Test Signals
`xl-storage-format-v2_gen_test.go` verifies generated marshal/unmarshal and encode/decode/skip paths for the main metadata structs and provides allocation/throughput benchmarks. Broader integration is exercised by v2 metadata load/append/merge tests, which would fail if generated codecs stopped preserving fields or changed tuple/map behavior unexpectedly.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-v2_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-v2_gen_test.go -->
# sources/object-store/minio/cmd/xl-storage-format-v2_gen_test.go

## Purpose
This generated test file validates the `msgp` code generated for the XL metadata v2 types. It is mechanical coverage for serialization plumbing rather than business-logic coverage, but it protects an important on-disk wire format.

## Important APIs, Types, and Functions
For each generated type (`xlMetaDataDirDecoder`, `xlMetaV2DeleteMarker`, `xlMetaV2Object`, `xlMetaV2Version`, and `xlMetaV2VersionHeader`), the file defines a `TestMarshalUnmarshal...` test, a `TestEncodeDecode...` test, and marshal/append/unmarshal/encode/decode benchmarks. The tests call `MarshalMsg`, `UnmarshalMsg`, `msgp.Skip`, `msgp.Encode`, `msgp.Decode`, and `msgp.NewReader(...).Skip`.

## Control Flow
The marshal/unmarshal tests create zero-valued structs, marshal them, unmarshal the bytes back, and fail if any bytes remain after unmarshal or after `msgp.Skip`. Encode/decode tests serialize through a `bytes.Buffer`, optionally warn when `Msgsize` underestimates actual encoded length, decode into a fresh value, and verify the stream can be skipped. Benchmarks measure allocation and byte throughput for marshal-to-new-buffer, marshal-append-into-reused-buffer, unmarshal from bytes, encode to a `msgp.Writer`, and decode from an endless reader.

## State and Persistence Behavior
The tests mostly use zero values, so they verify that omitted fields, nil pointers, and nil maps/slices are representable and skippable. They do not assert semantic equality for populated metadata or version compatibility. Their primary persistence signal is that the generated codecs produce syntactically valid msgp and consume exactly the bytes they emit.

## Dependencies and Integration Points
The file depends on Go `testing`, `bytes`, and `tinylib/msgp`. It integrates directly with generated methods from `xl-storage-format-v2_gen.go` and is regenerated alongside those methods. It complements the hand-written v2 tests that use populated metadata, real fixture metadata, and load/append round-trips.

## Risks and Edge Cases
Because values are zero-valued, these tests can miss populated-field regressions, map/slice reuse mistakes, allownil differences, and compatibility issues in non-default metadata. The `Msgsize` check logs a warning rather than failing, which avoids brittle generated tests but means size-estimate inaccuracies can persist. Since the file is generated, hand edits are not durable.

## Test Signals
A pass indicates generated codecs are internally self-consistent for zero values and support skip semantics. Failures usually indicate stale generated code, changed struct tags, msgp generator drift, or tuple/map encoding breakage. Performance benchmarks provide useful baselines for hot metadata paths but are not correctness assertions.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-v2_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-v2_string.go -->
# sources/object-store/minio/cmd/xl-storage-format-v2_string.go

## Purpose
This generated `stringer` file provides human-readable `String()` methods for `VersionType` and `ErasureAlgo`. It supports logging, diagnostics, `FileInfo.Erasure.Algorithm` population, and header formatting without hand-maintained switch statements.

## Important APIs, Types, and Functions
`VersionType.String()` maps persisted enum values to `invalidVersionType`, `ObjectType`, `DeleteType`, `LegacyType`, and `lastVersionType`. `ErasureAlgo.String()` maps to `invalidErasureAlgo`, `ReedSolomon`, and `lastErasureAlgo`. The generated `_()` compile-time checks intentionally fail compilation if the source constants change without regenerating the file.

## Control Flow
Each `String()` method bounds-checks the enum value against a generated index table. Known values slice the concatenated name string using generated offsets. Unknown values return `VersionType(<n>)` or `ErasureAlgo(<n>)` through `strconv.FormatInt`, preserving useful diagnostics for corrupt or future enum values.

## State and Persistence Behavior
This file does not write metadata directly, but its output is exposed in `xlMetaV2Object.ToFileInfo` and `xlMetaV2VersionHeader.String()`. Since enum numeric values are persisted by msgp codecs, the string names must be regenerated whenever enum definitions change to keep diagnostics and tests aligned with the wire values.

## Dependencies and Integration Points
It depends only on `strconv` and the enum constants from `xl-storage-format-v2.go`. The generation command is declared next to the enum definitions with `go:generate stringer -type VersionType,ErasureAlgo`.

## Risks and Edge Cases
The risk is stale generated output after enum changes. Compile-time index checks catch changed numeric assignments, but they do not decide whether changing a persisted enum value is safe. Unknown values are tolerated for string formatting but are rejected by `valid()` in the main implementation.

## Test Signals
There is no dedicated test file for these methods. Indirect coverage comes from metadata conversion and `ToFileInfo` tests/benchmarks that set `Erasure.Algorithm` to `ReedSolomon.String()` and from header diagnostic paths used in failures.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-v2_string.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-v2_test.go -->
# sources/object-store/minio/cmd/xl-storage-format-v2_test.go

## Purpose
This hand-written test file validates core XL metadata v2 behavior: partial metadata reads, inline data persistence, transition/restoration data-dir semantics, shared data-dir delete safety, legacy/indexed load compatibility, signature/timestamp repair, quorum version merging, metacache merge integration, healing metadata filtering, and fast `xlMetaBuf` read performance.

## Important APIs, Types, and Functions
The tests directly exercise `readXLMetaNoData`, `xlMetaV2.AddVersion`, `AppendTo`, `Load`, `xlMetaInlineData` operations, `xlMetaV2TrimData`, `xlMetaV2Object.UsesDataDir`, `SharedDataDirCount`, `DeleteVersion`, `mergeXLV2Versions`, `mergeEntryChannels`, `ToFileInfo`, `isIndexedMetaV2`, and `xlMetaBuf.ToFileInfo`. They use `FileInfo`, `ErasureInfo`, lifecycle transition constants, restore header helpers, zstd/zip fixtures, and fixture files under `testdata`.

## Control Flow
`TestXLV2FormatData` builds two inline object versions, serializes/deserializes metadata, checks find/list/remove/replace/rename behavior, trims inline data from the serialized buffer, and confirms metadata CRC corruption is detected. `TestUsesDataDir` checks transitioned, restore-in-progress, restored, expired restore, and normal object cases. `TestDeleteVersionWithSharedDataDir` creates multiple versions sharing or not sharing data dirs and verifies deletion only returns a data dir when no remaining version uses it.

The shallow load tests read a large v1.2 fixture, load legacy metadata, append it as indexed metadata, reload it, and assert header/full-version consistency and sort order. Additional subtests verify historical timestamp/signature repair and compressed index cleanup. Merge tests load multiple fixture metadata copies, mutate headers in controlled ways, and check strict/non-strict quorum behavior. `Test_mergeXLV2Versions2` constructs small synthetic streams and shuffles input order to verify deterministic quorum output. `Test_mergeEntryChannels` verifies higher-level listing merge produces three sorted versions. Benchmarks compare legacy/indexed load, merge, and `ToFileInfo` with/without part details.

## State and Persistence Behavior
The tests encode expected persistence invariants: current metadata can be appended and loaded without losing inline data, inline data can be stripped while retaining readable metadata, indexed headers must match full unmarshaled versions, old metadata must remain readable, and known historical encodings are normalized on load. They also encode lifecycle semantics: transitioned but not restored versions do not require local data-dir deletion; restored versions may use local data; free/hidden markers and delete markers affect listing and merge visibility.

## Dependencies and Integration Points
The file integrates with fixtures (`xl.meta-corrupt.gz`, `xl.meta-v1.2.zst`, `xl-meta-consist.zip`, `xl-meta-merge.zip`, `xl-many-parts.meta`), `metaCacheEntry`, restore header helpers, lifecycle constants, UUID generation, zstd/zip/gzip readers, and the object metadata conversion APIs. This makes it a broad regression suite for storage metadata and list healing behavior.

## Risks and Edge Cases
Several tests use embedded binary/base64 fixtures that are hard to update safely; they are valuable compatibility anchors but can obscure intent. Some coverage is benchmark-only, so performance paths like large-version `UpdateObjectVersion` and many-part `ToFileInfo` are not hard correctness gates unless benchmarks are run. The merge tests cover many header mutations but should be extended whenever `xlMetaV2VersionHeader` fields or non-strict matching rules change.

## Test Signals
Passing tests strongly signal compatibility for v1.2-to-v1.3 load, indexed metadata round-trip, CRC detection, quorum merge selection, data-dir preservation, and inline data operations. Failures in this file usually indicate a real storage compatibility or lifecycle regression and should be treated as high priority.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format-v2_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format_test.go -->
# sources/object-store/minio/cmd/xl-storage-format_test.go

## Purpose
This test file covers legacy XL metadata v1 validation/parsing helpers, part-size calculation, and broad v2 metadata operation benchmarks. It anchors compatibility for JSON-based v1 metadata while also benchmarking the v2 shallow metadata API under many-version workloads.

## Important APIs, Types, and Functions
`TestIsXLMetaFormatValid` covers `isXLMetaFormatValid`; `TestIsXLMetaErasureInfoValid` covers `isXLMetaErasureInfoValid`. Helpers `newTestXLMetaV1`, `AddTestObjectCheckSum`, `AddTestObjectPart`, `getXLMetaBytes`, `getSampleXLMeta`, and `compareXLMetaV1` construct and compare legacy `xlMetaV1Object` values. `TestGetXLMetaV1Jsoniter1` and `TestGetXLMetaV1Jsoniter10` compare standard JSON and jsoniter behavior. `TestGetPartSizeFromIdx` validates `calculatePartSizeFromIdx`. `BenchmarkXlMetaV2Shallow` measures `Load`, `UpdateObjectVersion`, `DeleteVersion`, `AddVersion`, `ToFileInfo`, `ListVersions`, and `xlMetaBuf` fast read paths for up to 100,000 versions.

## Control Flow
The legacy tests create representative v1 metadata with erasure info, checksums, parts, stat info, and user metadata. The same JSON bytes are unmarshaled with both `encoding/json` and jsoniter, then every meaningful field is compared. Part-size tests cover zero total size, exact multiples, partial final parts, out-of-range part indexes, zero part size, invalid part index, and negative total size.

The benchmark constructs a baseline `FileInfo`, repeatedly adds many versions to an `xlMetaV2`, serializes it, then measures load-modify-save and load-list/query loops. It also extracts indexed metadata with `isIndexedMetaV2` and compares the newer shallow `xlMetaBuf` list/query paths against full `xlMetaV2` loading.

## State and Persistence Behavior
The file is mostly test-only, but it describes expected legacy persisted metadata shape: v1 object metadata includes version/format strings, erasure checksums/distribution, object parts, stat modtime/size, release, and user metadata. The benchmark confirms v2 persistence can scale to very large version stacks and that indexed metadata supports efficient read-only access without fully materializing every version.

## Dependencies and Integration Points
It depends on `xl-storage-format.go` legacy helpers and structures, v2 metadata APIs from `xl-storage-format-v2.go`, `jsoniter`, standard JSON, MinIO HTTP metadata constants, humanize constants, and random UUID helpers. It bridges the legacy JSON world and the msgp v2 metadata implementation.

## Risks and Edge Cases
The legacy JSON comparison tests are precise but only cover synthetic metadata with fixed checksums/parts. The large v2 workload is benchmark-only; regressions may be missed in normal unit-test runs unless correctness tests elsewhere fail. Because this file uses `rand` during benchmarks, benchmark access patterns are repeatable only where seeded.

## Test Signals
Passing unit tests signal that legacy format/version validation, erasure M/N validation, jsoniter compatibility, and part-size math remain correct. Benchmark trends signal whether v2 shallow metadata changes affect large-version operational costs.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-format_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-free-version.go -->
# sources/object-store/minio/cmd/xl-storage-free-version.go

## Purpose
This file implements XL metadata "free-version" support. A free-version is represented as a delete marker with special internal metadata and is used to track tiered remote content that must be deleted asynchronously after an object version is overwritten or removed.

## Important APIs, Types, and Functions
`freeVersion` is the internal metadata marker key suffix. `xlMetaV2Object.InitFreeVersion(fi FileInfo)` creates a delete-marker-shaped `xlMetaV2Version` when the object has completed transition metadata and the caller did not request `SkipTierFreeVersion`. `xlMetaV2DeleteMarker.FreeVersion()` and `xlMetaV2Version.FreeVersion()` identify free-version records. `xlMetaV2.AddFreeVersion(fi FileInfo)` finds the target object version and appends the generated free-version if the version has tiered content.

## Control Flow
`InitFreeVersion` first checks the caller skip flag. It then verifies the object has `x-minio-internal-transition-status` equal to lifecycle `TransitionComplete`. If so, it parses the free-version ID stored in the `FileInfo`; invalid IDs panic because the caller has already committed to a generated internal ID. The new version is type `DeleteType`, uses the original object's modtime, records the current writer version, stores the free-version marker, and copies only tier name/object/version metadata needed by the scanner to delete remote tier content. `AddFreeVersion` parses the target version ID, scans the shallow version list for an object entry with that ID, loads it, and delegates to `InitFreeVersion`.

## State and Persistence Behavior
Free-versions persist inside the normal version stack but are hidden from normal object listing and version counts by `xlMetaV2.ToFileInfo` and `xlMetaBuf` readers unless callers explicitly include them or no non-free versions remain. The marker lives in delete-marker `MetaSys` under the reserved metadata prefix. They carry tier routing metadata, not local object data, and exist so lifecycle/scanner paths can eventually purge remote tiered objects after the user-visible version is gone.

## Dependencies and Integration Points
The file depends on `FileInfo` tier/free-version accessors, lifecycle transition constants, UUID parsing, reserved internal metadata names from the v2 metadata implementation, `globalVersionUnix`, and scanner/lifecycle integrations that request `InclFreeVersions` and enqueue free-version deletion. `DeleteVersion` in the main v2 file also calls `InitFreeVersion` when deleting transitioned object versions.

## Risks and Edge Cases
The panic on invalid tier free-version ID assumes internal callers set a valid UUID; externalizing or loosening this path would need error handling. Missing tier metadata would create a free-version with insufficient deletion routing. Creating free-versions when `SkipTierFreeVersion` is set could duplicate work during lifecycle expiry. Failing to hide free-versions from normal reads would expose internal cleanup records as object versions.

## Test Signals
`xl-storage-free-version_test.go` covers creation during overwrite/removal, listing/counting free-versions, `ToFileInfo` behavior with and without `inclFreeVers`, scanner-style deletion of free-versions, no-op behavior for non-tiered versions, and skip-flag behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-free-version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-free-version_test.go -->
# sources/object-store/minio/cmd/xl-storage-free-version_test.go

## Purpose
This test file validates the free-version lifecycle for tiered object content. It confirms that internal cleanup versions are created only for transitioned content, hidden or shown appropriately, and removable by scanner-like flows.

## Important APIs, Types, and Functions
`listFreeVersions` is a test helper that calls `xlMetaV2.ListVersions` and filters `FileInfo.TierFreeVersion()`. `TestFreeVersion` exercises `AddVersion`, `DeleteVersion`, `AddFreeVersion`, `ToFileInfo`, `listFreeVersions`, `SetTierFreeVersionID`, and tier metadata fields. `TestSkipFreeVersion` directly exercises `xlMetaV2Object.InitFreeVersion` and `FileInfo.SetSkipTierFreeVersion`.

## Control Flow
`TestFreeVersion` creates a local version and a null version, marks the null version as transitioned, deletes/overwrites/removes it with specific free-version IDs, and asserts the stack contains two free-versions plus one non-free version. It then checks three read cases: including free versions while a non-free version exists returns the non-free latest version; including free versions after deleting the non-free version returns the latest free-version; excluding free versions when only free-versions remain returns `errFileNotFound`. Finally it deletes each free-version and verifies none remain, and verifies `AddFreeVersion` is a no-op for non-tiered content.

`TestSkipFreeVersion` constructs an object with transition metadata and verifies `InitFreeVersion` creates a free-version by default, then sets the skip flag and verifies no free-version is created.

## State and Persistence Behavior
The tests encode the intended internal-state model: free-versions are persisted as delete-marker versions, have their own UUIDs distinct from user-visible versions, preserve tier metadata, and should not count as normal versions when user data exists. The scanner can later delete free-version records by version ID through the same metadata delete mechanism.

## Dependencies and Integration Points
The tests depend on lifecycle `TransitionComplete`, UUID generation, `FileInfo` tier helper methods, erasure info setup, and v2 metadata mutation/listing APIs. They mirror production flows in erasure object overwrite/delete and lifecycle scanner cleanup.

## Risks and Edge Cases
The tests focus on a single object stack and do not cover corrupted tier metadata, invalid free-version UUID panic behavior, or concurrent updates across disks. They do, however, cover the most important visibility invariant: internal free cleanup versions must not appear as normal object versions.

## Test Signals
Passing tests indicate free-version creation, hiding, explicit inclusion, no-op non-tiered behavior, and skip semantics are intact. Failures usually point to lifecycle tier cleanup leaks or accidental exposure of internal versions.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-free-version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-meta-inline.go -->
# sources/object-store/minio/cmd/xl-storage-meta-inline.go

## Purpose
This file implements the inline-data tail for XL metadata v2. It stores small object payloads as msgp-encoded string-to-bytes entries after the main metadata blob, allowing zero-byte/small inline object data to be persisted in `xl.meta` rather than a separate data directory.

## Important APIs, Types, and Functions
`xlMetaInlineData` is a raw byte slice with a one-byte format version followed by a msgp map of key/value pairs. `versionOK`, `afterVersion`, `validate`, `repair`, `list`, `entries`, and `find` inspect serialized inline data without a full object abstraction. Mutators `replace`, `rename`, and `remove` rebuild the serialized map with updated entries. `serialize` constructs the versioned payload. `xlMetaV2TrimData` strips the inline data tail from a serialized XL metadata buffer without unmarshalling the metadata.

## Control Flow
Read paths first accept empty data, then validate the leading version byte and read a msgp map header from the payload. Iteration uses zero-copy msgp key/value reads where possible. `find` returns the bytes for a matching key and skips other entries. `validate` fails on unknown versions, malformed msgp, or empty keys. `repair` salvages valid prefix entries into a new serialized payload, or clears the data if the version/map header is invalid.

Mutators parse the existing map, collect key/value slices, calculate an approximate payload size, and call `serialize`. `replace` updates a matching key or appends a new one. `rename` swaps a key only if found. `remove` supports multiple keys and switches to a map lookup for larger remove sets. Removing all entries clears the inline-data slice.

`xlMetaV2TrimData` checks the outer XL header/version, skips the main metadata bytes and CRC where present, computes the end offset before inline data, and returns that prefix. On parse errors it logs and returns the original buffer to avoid destructive truncation.

## State and Persistence Behavior
Inline data is stored outside the main indexed metadata CRC and is keyed by version ID or null-version ID. The current inline data format version is `1`; unknown non-empty versions are rejected or repaired away. `xlMetaV2.AddVersion` inserts data into this structure when `FileInfo.Data` is non-empty or the object size is zero. `xlMetaV2Object.InlineData` separately marks an object version as likely having inline data through internal metadata, while this file owns the actual byte map.

## Dependencies and Integration Points
The file depends on `tinylib/msgp`, `slices`, error/log helpers, and the outer XL v2 header parsing from `xl-storage-format-v2.go`. It is used by `xlMetaV2.Load`, `AppendTo`, `AddVersion`, `SharedDataDirCount`, tests, and metacache merge paths that trim data before comparing/listing metadata.

## Risks and Edge Cases
Because this code works directly on serialized bytes, size accounting and msgp prefix constants must remain correct. `repair` salvages syntactically valid entries but cannot verify payload integrity. Inline data is outside the metadata CRC, so corruption detection relies on msgp validation rather than checksum comparison. `xlMetaV2TrimData` must preserve old v1.0 metadata and handle v1.1/v1.2 variable CRC layouts correctly; otherwise list/merge paths could compare inconsistent bytes.

## Test Signals
`TestXLV2FormatData` covers inline data add/list/find/remove/replace/rename, append/load round-trip, trim behavior, and metadata corruption detection after trimming. `TestDeleteVersionWithSharedDataDir` verifies inline data versions do not count as sharing local data directories. `Test_mergeEntryChannels` trims metadata before merge, indirectly covering trim compatibility with fixture metadata.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/xl-storage-meta-inline.go -->
