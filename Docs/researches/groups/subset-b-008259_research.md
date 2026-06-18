# subset-b-008259 grouped source research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/tests/minio_generated_read_test.rs -->
# sources/object-store/rustfs/crates/ecstore/tests/minio_generated_read_test.rs

Purpose: feature-gated integration coverage for reading MinIO-generated encrypted multipart fixtures through RustFS. It is compiled only with `rio-v2` and ignored by default because it needs fixture data plus a local static KMS key.

Important APIs and flow: fixture discovery uses `RUSTFS_MINIO_FIXTURE_ROOT` or `../rio-v2/tests/fixtures/minio-generated`; `ManifestRecord` supplies bucket, object, and backend file paths. `load_file_info` reads object `xl.meta` and calls `rustfs_filemeta::get_file_info` with data and free-version inclusion. `encrypted_fixture_bytes` opens the fixture disk via `Endpoint` and `new_disk`, creates part readers with `create_bitrot_reader`, reads each part shard with checksum metadata, and concatenates encrypted object bytes. `assert_fixture_round_trip` then creates `ObjectInfo`, injects `__RUSTFS_SSE_SIMPLE_CMK`, constructs `GetObjectReader`, reads plaintext, and verifies offset, length, object size, byte count, and SHA-256.

State and persistence: this test reads fixture files under a MinIO disk layout and temporarily mutates process environment through `temp_env::async_with_vars`. It does not write repository state. Disk readers are explicitly closed.

Dependencies and integration: ties `ecstore` disk, bitrot, object read/decryption, `rustfs_filemeta`, `sha2`, `hex_simd`, `tokio`, `serde_json`, and the fixture-lab manifest contract together. It is a high-value cross-project compatibility guard for SSE-S3 and SSE-KMS MinIO data.

Risks: ignored tests can drift if fixtures are not regenerated in CI. Environment-variable KMS setup is brittle. The reader loop stops on a short read, so any future reader that returns short non-EOF reads could truncate test input. Fixture path assumptions depend on object names not requiring escaping beyond the manifest entries.

Test signals: two ignored Tokio tests cover `sse-s3-multipart-8m` and `sse-kms-multipart-8m`; success proves xl.meta decoding, bitrot reads, encrypted-object reader construction, and plaintext hash compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/tests/minio_generated_read_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/tests/protobuf_bytes_regression_test.rs -->
# sources/object-store/rustfs/crates/ecstore/tests/protobuf_bytes_regression_test.rs

Purpose: compile-time regression test that protobuf binary payload fields remain `bytes::Bytes` rather than `Vec<u8>` or another buffer type.

Important APIs and flow: `expect_bytes(_: &Bytes)` is a type assertion helper. The single test constructs default node-service messages and passes `file_info_bin`, `opts_bin`, `raw_file_info_bin`, `read_multiple_req_bin`, and an element of `read_multiple_resps_bin` to the helper.

State and persistence: no runtime state or persistence. The important behavior is at compilation: generated prost field types must match the storage/node API zero-copy contract.

Dependencies and integration: depends on `bytes::Bytes` and `rustfs_protos::proto_gen::node_service` generated types. It protects storage RPC integration points that pass metadata blobs between disks or nodes.

Risks: this cannot validate wire compatibility or message contents; it only guards Rust field types. The repeated response case uses `first().cloned().unwrap_or_default()`, so it asserts the vector element type when present, not response population semantics.

Test signals: the test fails to compile if the generated protobuf configuration stops mapping the selected `bytes` fields to `Bytes`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/tests/protobuf_bytes_regression_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/tests/storage_api_compat_test.rs -->
# sources/object-store/rustfs/crates/ecstore/tests/storage_api_compat_test.rs

Purpose: compile-time contract test proving `ECStore` implements public storage traits with expected associated types.

Important APIs and flow: `storage_admin_api_type_name<T>` constrains `T` to `StorageAdminApi<BackendInfo = rustfs_madmin::BackendInfo, StorageInfo = rustfs_madmin::StorageInfo, Disk = DiskStore, Error = Error>`. `storage_api_with_namespace_locking_type_name<T>` constrains `T` to `StorageAPI + NamespaceLocking`. The tests instantiate both helpers with `ECStore` and assert the returned type name ends in `::ECStore`.

State and persistence: no runtime storage state is touched. Trait bounds are the persistent contract.

Dependencies and integration: joins `rustfs_ecstore::{store::ECStore, disk::DiskStore, error::Error, store_api::*}`, `rustfs_storage_api::StorageAdminApi`, and madmin response types. It protects admin/storage trait compatibility used by higher-level object store orchestration.

Risks: type-name string assertions are incidental; the real value is compile-time trait checking. The test does not exercise behavior, associated method semantics, or namespace lock correctness.

Test signals: any trait implementation removal or associated type drift breaks compilation before runtime assertions.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/tests/storage_api_compat_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/extension-schema/Cargo.toml -->
# sources/object-store/rustfs/crates/extension-schema/Cargo.toml

Purpose: crate manifest for `rustfs-extension-schema`, the shared RustFS extension contract/schema package.

Important declarations: package metadata inherits workspace version, edition, license, repository, rust-version, and homepage. It disables doctests for the library. Runtime dependencies are intentionally minimal: `serde` for stable wire/schema serialization and `thiserror` for typed validation errors. `serde_json` is dev-only for JSON shape tests. Lints are workspace-governed.

State and persistence: no runtime state, but the manifest controls published crate identity, dependency surface, and documentation/test behavior.

Dependencies and integration: this crate is a small boundary contract for extension systems. The manifest keeps it independent of object-store internals, which helps plugins, ops diagnostics, and S3 hook contracts share schemas without pulling storage dependencies.

Risks: disabling doctests can hide stale documentation examples. Any workspace dependency feature changes to `serde` or `thiserror` affect this crate. The manifest has no feature gates, so future optional contract families would need careful dependency discipline.

Test signals: `serde_json` dev dependency supports the stable JSON serialization tests in `src/lib.rs`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/extension-schema/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/extension-schema/src/lib.rs -->
# sources/object-store/rustfs/crates/extension-schema/src/lib.rs

Purpose: defines serializable extension schema contracts and validators for RustFS extension kinds, runtime boundaries, S3 post-auth hooks, and ops diagnostics.

Important APIs/types/functions: constants `EXTENSION_SCHEMA_VERSION`, `OPS_DIAGNOSTICS_CAPABILITY`, and `S3_POST_AUTH_HOOK_CAPABILITY` anchor stable identifiers. `ExtensionKind`, `ExtensionRuntimeBoundary`, `ExtensionRuntimeContract`, `ExtensionCapabilityRef`, and `ExtensionSchema` define the top-level extension document. `S3HookPoint` and `S3HookContract` describe read-only post-auth S3 hook capabilities. `OpsDiagnosticSurface` and `OpsDiagnosticsContract` describe admin-gated operational diagnostic surfaces. Validation entry points are `validate_extension_schemas`, `validate_s3_hook_contract`, and `validate_ops_diagnostics_contract`; failures are typed as `ExtensionSchemaError` and `ExtensionContractError`.

Control flow: schema validation iterates all schemas, trims mandatory strings, checks the exact schema version, rejects empty or duplicate capabilities with `BTreeSet`, requires external `Sidecar`/`Wasm` boundaries to be disabled by default, and rejects duplicate extension IDs. S3 hook validation rejects empty/duplicate hook points, object data mutation, and IAM bypass. Ops diagnostics validation rejects empty/duplicate surfaces, object mutation, and missing admin-action requirement.

State and persistence: all contracts are `Serialize`/`Deserialize`; persistence is the JSON/config representation of extension declarations. There is no mutable global state. `#[serde(rename_all = "snake_case")]`, transparent capability refs, and `deny_unknown_fields` on contract bodies are important wire-shape controls.

Dependencies and integration: uses `serde`, `thiserror`, and `BTreeSet`. It integrates with extension discovery/config systems that need deterministic validation before enabling plugins or diagnostic surfaces.

Risks: `S3HookPoint::is_post_auth` currently always returns true, so adding non-post-auth variants would require updating this method. `ExtensionCapabilityRef::new` does not trim or validate until schema validation, so callers must run the validator. `ExtensionKind` is not cross-checked against declared capabilities/contracts in this file.

Test signals: unit tests lock JSON shape, valid ops diagnostics schemas, disabled-by-default external extensions, duplicate capability and extension ID rejection, schema-version rejection, empty capability rejection, S3 hook safety, duplicate hook rejection, and ops diagnostics admin/read-only requirements.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/extension-schema/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/Cargo.toml -->
# sources/object-store/rustfs/crates/filemeta/Cargo.toml

Purpose: crate manifest for `rustfs-filemeta`, the metadata encoding/decoding and object-version model used by RustFS object storage.

Important declarations: library doctests are disabled. Dependencies include MessagePack (`rmp`, `rmp-serde`), `serde`, `bytes`, `time`, `uuid`, `tokio` IO, `xxhash-rust`, `crc-fast`, `byteorder`, `rustfs-utils` with hash/http features, `s3s`, `regex`, `arc-swap`, `tracing`, and `thiserror`. Criterion and tempfile are dev-only. The `xl_meta_bench` benchmark is registered with `harness = false`.

State and persistence: the manifest defines the persistence-format stack: MessagePack encoding, xxhash CRCs, UUID/time handling, byte buffers, S3 headers, and async reading. It also exposes the crate for docs.rs.

Dependencies and integration: this crate sits below ecstore and object APIs, sharing metadata types via `pub use` in `src/lib.rs`. `rustfs-utils` and `s3s` link metadata with HTTP/S3 headers and restore/tiering semantics.

Risks: broad dependency surface means workspace feature changes can affect serialization or HTTP metadata behavior. Disabling doctests leaves examples uncompiled. Benchmark availability depends on dev dependency alignment with workspace Criterion.

Test signals: manifest declares Criterion bench coverage for XL metadata creation, parsing, serialization, round-trip, stats, and integrity.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/benches/xl_meta_bench.rs -->
# sources/object-store/rustfs/crates/filemeta/benches/xl_meta_bench.rs

Purpose: Criterion benchmark suite for the XL metadata hot path in `rustfs-filemeta`.

Important APIs and flow: benchmarks call `test_data::{create_real_xlmeta, create_complex_xlmeta}`, parse with `FileMeta::load`, serialize with `marshal_msg`, run load/serialize/load round trips, compute `get_version_stats`, and call `validate_integrity`. `black_box` prevents compiler elimination.

State and persistence: all data is generated in memory from test fixtures. Benchmarks measure the same serialized XL metadata bytes persisted on disk but do not write files.

Dependencies and integration: depends on Criterion and public `rustfs_filemeta` APIs. It provides performance signals for storage paths that repeatedly parse or rewrite `xl.meta`.

Risks: generated fixture realism controls benchmark value. No explicit throughput thresholds are enforced, so regressions require comparing Criterion history. The suite benchmarks synchronous parse/serialize, not async disk read or object-store end-to-end behavior.

Test signals: named benchmark functions cover real and complex metadata creation, parsing, serialization, round-trip, stats, and integrity validation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/benches/xl_meta_bench.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/examples/dump_fileinfo.rs -->
# sources/object-store/rustfs/crates/filemeta/examples/dump_fileinfo.rs

Purpose: debug CLI for inspecting a single `xl.meta` file as `FileInfo`, including object parts, user/system metadata, transition fields, and compression index bytes.

Important APIs and flow: `main` reads a path argument, loads bytes, calls `get_file_info` with placeholder bucket/object names and `include_free_versions = true`, then prints size, ETag, part fields, transition fields, and sorted metadata. Part index bytes are passed to `decode_compression_index`.

Compression-index control flow: `index_candidates` tries full MinIO S2 or legacy RustFS frames when a known chunk type is present, otherwise reconstructs headerless candidates. `parse_index` validates the skippable-frame header, S2 header/trailer, length fields, signed or unsigned varints, entry limits, uncompressed-offset flag, and compressed/uncompressed offset delta coding. `restore_index_headers` rebuilds a complete skippable frame around headerless payloads. `read_varint` handles signed zig-zag decoding when requested.

State and persistence: read-only CLI over an existing xl.meta file. It reconstructs temporary candidate buffers but does not persist changes.

Dependencies and integration: uses the public `rustfs_filemeta::{get_file_info, FileInfoOpts}` path and mirrors MinIO S2 compression index formats. It is useful when investigating compatibility bugs with compressed object parts or transition metadata.

Risks: placeholder bucket/object names can affect fields derived from path context. The custom index decoder has its own bounds and varint logic, so it can diverge from production decompression code. It prints only first five and last offsets for long indexes.

Test signals: no direct tests in the example, but its helpers are deterministic and fail with explicit strings for malformed index buffers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/examples/dump_fileinfo.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/examples/dump_versions.rs -->
# sources/object-store/rustfs/crates/filemeta/examples/dump_versions.rs

Purpose: small debug CLI for listing all versions in an `xl.meta` file.

Important APIs and flow: `main` reads the file path argument, loads bytes, parses with `FileMeta::load`, converts with `into_file_info_versions("debug-bucket", "debug-object", true)`, and prints path, version count, and per-version ID/delete/latest/size/mod-time fields.

State and persistence: read-only over an existing xl.meta file. It uses placeholder volume/object labels for display and conversion context.

Dependencies and integration: depends on public `rustfs_filemeta::FileMeta`. It exercises the same version conversion path object-store listing/debugging uses.

Risks: it does not expose all metadata, erasure, tiering, or replication fields; pair with `dump_fileinfo` for deeper object inspection. Placeholder names may hide path-sensitive issues.

Test signals: no direct tests; success depends on `FileMeta::load` and `into_file_info_versions` compatibility tests in the library.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/examples/dump_versions.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/error.rs -->
# sources/object-store/rustfs/crates/filemeta/src/error.rs

Purpose: central error type and `Result` alias for file metadata operations.

Important APIs/types/functions: `pub type Result<T> = core::result::Result<T, Error>`. `Error` covers storage-style states (`FileNotFound`, `FileVersionNotFound`, `VolumeNotFound`, `FileCorrupt`, `DoneForNow`, `MethodNotAllowed`, `Unexpected`) and wrapped codec/runtime failures (`Io`, rmp serde encode/decode, raw rmp read/write errors, UTF-8, time range, UUID parse). `Error::other` wraps arbitrary errors through `std::io::Error::other`. `is_io_eof` detects `Error::Io(UnexpectedEof)`.

Control flow and conversions: `From<std::io::Error>` maps `UnexpectedEof` to the sentinel `Unexpected`; other IO errors stay in `Io`. `From<Error> for std::io::Error` converts `Unexpected` back to `UnexpectedEof`, preserves `Io`, and wraps other variants as `Other`. MessagePack, UTF-8, time, UUID, and marker errors are stringified into stable enum variants. Manual `PartialEq` and `Clone` preserve comparability for IO errors by kind/message.

State and persistence: no persistent state. The enum is part of the public API and shapes how metadata parse failures propagate through storage callers.

Dependencies and integration: integrates `thiserror`, `std::io`, `rmp`, `rmp-serde`, `time`, and `uuid`. `DoneForNow` is used internally as a controlled early-stop sentinel in metadata scanning.

Risks: mapping raw `UnexpectedEof` into `Unexpected` means `is_io_eof` does not detect EOFs after conversion through `From<std::io::Error>`. Stringifying third-party errors loses structured details but makes clone/equality simpler. `Error::other` wraps source errors as IO `Other`, which can blur domain boundaries.

Test signals: unit tests cover conversion, `other`, clone, equality, display strings, rmp/time/uuid/marker conversion, EOF helper behavior, IO round-trip preservation, error-kind handling, and wrapped message retention.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/fileinfo.rs -->
# sources/object-store/rustfs/crates/filemeta/src/fileinfo.rs

Purpose: public object metadata model used after decoding `xl.meta` and before storage/object APIs consume metadata.

Important APIs/types/functions: constants include `ERASURE_ALGORITHM`, `BLOCK_SIZE_V2`, `NULL_VERSION_ID`, and tier-free metadata keys. `ObjectPartInfo` models part number, sizes, ETag, optional compression index, checksums, and errors. `ChecksumInfo`, `ErasureAlgo`, and `ErasureInfo` model erasure coding and bitrot checksums, with `calc_shard_size`, `shard_size`, `shard_file_size`, `get_checksum_info`, and `equals`. `FileInfo` contains volume/object identity, version/delete status, transition/restore fields, data dir, mod time, size, metadata map, parts, erasure info, replication state, inline data, checksum, and legacy checksum marker. `FileInfoVersions`, `RawFileInfo`, and `FilesInfo` are aggregate DTOs. `RestoreStatusOps`, `parse_restore_obj_status`, and `is_restored_object_on_disk` handle S3 restore headers.

Control flow: `FileInfo::new` computes deterministic erasure distribution from a CRC32 of the object name. `is_valid` allows delete markers and validates data/parity/index/distribution for object entries. Part insertion replaces matching part numbers and sorts. Offset lookup walks parts cumulatively. Metadata helper methods set/read internal healing, inline-data, data-moved, tier-free, skip-tier-free, compression, and remote/tiering flags. Quorum helpers distinguish deleted objects from erasure-coded objects. Equality helpers compare compression, transition, mod time, erasure, metadata, and replication fields. Restore parsing validates `ongoing-request` and RFC3339 expiry syntax.

State and persistence: this module represents persisted object metadata after decoding and before encoding. Inline data and part indexes use `bytes::Bytes`; metadata flags use HTTP/internal suffix helpers. Restore on-disk state is derived from `x-amz-restore` expiry compared to current UTC time.

Dependencies and integration: uses `serde`, `rmp-serde`, `bytes`, `time`, `uuid`, `s3s` restore headers, `rustfs_utils` HTTP/hash helpers, and replication types from the crate. It is consumed by `FileMeta`, ecstore tests, object info conversion, tiering, healing, and replication flows.

Risks: restore header parser accepts a narrow format and only RFC3339 expiry, while `to_string2` emits RFC1123. `is_remote` depends on current time through restore status, making behavior time-sensitive. `FileInfo::new` distribution must remain compatible with MinIO/RustFS erasure layout. Metadata keys are plain strings; suffix helper behavior is critical to avoid persisting transient flags.

Test signals: direct tests are not in this file, but `filemeta.rs`, examples, and MinIO fixture tests exercise FileInfo construction, erasure layout, inline data, restore/tiering behavior, parts, and metadata extraction.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/fileinfo.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/filemeta.rs -->
# sources/object-store/rustfs/crates/filemeta/src/filemeta.rs

Purpose: core XL metadata container implementation for RustFS object versions, inline data, serialization, deletion, version listing, and compatibility with current and legacy `xl.meta` formats.

Important APIs/types/functions: constants define `XL_FILE_HEADER`, `XL_META_VERSION`, transition keys, and free-version labels. `FileMeta` stores ordered `FileMetaShallowVersion` entries, `InlineData`, and `meta_ver`. Public methods include `new`, `find_version`, `update_object_version(_with_opts)`, `add_version`, `add_version_filemata`, `delete_version`, `into_fileinfo`, `get_file_info_versions`, `get_all_file_info_versions`, `into_file_info_versions`, `latest_mod_time`, `load_or_convert`, `list_versions`, `all_hidden`, `append_to`, and `find_version_str`. The module re-exports version and validation types including `VersionStats` and `DetailedVersionStats`.

Control flow: versions are kept newest-first by modification time with additional deterministic tie-breakers. Adding a version normalizes missing version IDs to nil UUID for null versions, updates inline data atomically through a cloned `InlineData`, replaces existing matching versions, and enforces a 10,000-version limit. Updating object metadata splits user metadata from internal system metadata, skips transient healing/data-moved flags, optionally clears user metadata, updates mod time, and persists resolved checksum bytes. Deletion handles delete markers, purge replication metadata, free-version creation, transition-to-remote updates, restore expiry cleanup, inline-data reset, and data-dir reclamation only when no other version shares the directory. Conversion to `FileInfo` tracks latest/successor mod times, free versions, inline data lookup, and version-not-found distinction.

State and persistence: this is the persistence root for object metadata. It owns the in-memory representation of `xl.meta`, delegates wire encoding to `codec.rs`, inline data lookup to `inline_data.rs`, version structs to `version.rs`, and integrity/statistics to `validation.rs`. It must preserve legacy null-version inline keys and legacy meta v1/v2 parse paths.

Dependencies and integration: integrates `FileInfo`, erasure and replication types, S3 restore/tiering headers, internal HTTP metadata suffix helpers, `bytes`, `uuid`, `time`, `tracing`, MessagePack, xxhash, and async IO through submodules. Public helpers `get_file_info`, `file_info_from_raw`, `merge_file_meta_versions`, and `read_xl_meta_no_data` are provided by the re-exported version module.

Risks: deletion and replication logic is stateful and branch-heavy, with subtle differences between object versions, delete markers, free versions, transitioned objects, and purge metadata. Inline data updates must remain atomic to avoid orphaning data on failed version insertion. `get_idx` checks `idx > len` rather than `idx >= len`, so callers must avoid len indexes. Compatibility with legacy MinIO/RustFS layouts depends on private version decode logic remaining in sync with fixtures.

Test signals: extensive unit tests cover new/marshal round trips, metadata object/delete marker/version/header encoding, real and complex xl.meta compatibility, legacy issue fixtures (#2288, #2265, #2434), legacy v1 object support, inline data including legacy nil UUID keys and stale inline cleanup, corrupted/empty data, version stats, ordering, signatures, performance thresholds, concurrent mutation under a mutex, metadata/part/UUID edge cases, purge deletion behavior, checksum metadata persistence, merge scenarios, flags, special characters, and async `read_xl_meta_no_data`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/filemeta.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/filemeta/codec.rs -->
# sources/object-store/rustfs/crates/filemeta/src/filemeta/codec.rs

Purpose: binary codec for the top-level `FileMeta` XL2 on-disk format.

Important APIs/functions: `is_xl2_v1_format`, `load`, `read_format_versions`, `check_xl2_v1`, `is_indexed_meta`, `read_bytes_header`, `unmarshal_msg`, private `decode_xl_headers`/`decode_versions`, `is_latest_delete_marker`, and `marshal_msg`.

Control flow: decoding validates the `XL2 ` magic, reads little-endian major/minor file version, reads a MessagePack bin length, splits metadata payload, reads a MessagePack u32 CRC, verifies xxhash64-truncated CRC over metadata, validates optional inline data, decodes header/meta version/count, then iterates header and version-meta bin pairs into `FileMetaShallowVersion`. `is_latest_delete_marker` decodes only enough metadata to inspect the first header and uses `Error::DoneForNow` as early exit. Encoding writes magic/version, reserves a bin32 length, writes header version, meta version, version count, each version header/meta as bins, patches the metadata length, appends CRC, then appends inline data bytes.

State and persistence: this module defines persisted byte layout and checksum validation. It mutates `self.data`, `self.meta_ver`, and `self.versions` during unmarshal. The metadata CRC protects only the metadata payload, not trailing inline data, which is validated by `InlineData::validate`.

Dependencies and integration: uses `byteorder`, `rmp`, `xxhash_rust`, `Cursor`, `Read`, `Write`, `FileMetaVersionHeader`, and `InlineData`. `read_format_versions` supports compatibility tests and tooling without full object decode.

Risks: the format assumes the MessagePack bin length prefix is exactly five bytes in several helpers. Major versions greater than the current major are rejected, but minor is not bounded. `is_indexed_meta` returns empty slices for unsupported/short metadata in some cases, so callers must treat empty as "not indexed" rather than valid parse. Inline data integrity relies on its own validator.

Test signals: library tests exercise real/legacy format version reads, round-trip marshal/load, CRC/corruption failures, latest delete marker checks indirectly, and async no-data reads.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/filemeta/codec.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/filemeta/inline_data.rs -->
# sources/object-store/rustfs/crates/filemeta/src/filemeta/inline_data.rs

Purpose: data-directory and inline-data helper methods for `FileMeta`.

Important APIs/functions: `find_unshared_data_dir_for_version`, `shard_data_dir_count`, `get_data_dirs`, and `shared_data_dir_count`.

Control flow: helpers scan shallow object versions whose headers indicate object type and data-dir usage. They decode each data dir from serialized version metadata only when needed. `find_unshared_data_dir_for_version` returns the target version's data dir only if no other version shares it. `shared_data_dir_count` treats existing inline data for the version as not sharing a disk data dir and otherwise counts other object versions with the same decoded directory.

State and persistence: no writes. The functions inspect persisted version metadata and inline-data entries to decide whether disk data directories can be safely reclaimed or are shared by multiple versions.

Dependencies and integration: depends on `VersionType`, `FileMetaVersion::decode_data_dir_from_meta`, `InlineData`, `Uuid`, and `HashSet`. It is called by deletion/transition logic in `filemeta.rs`.

Risks: decode failures are mostly collapsed with `unwrap_or_default`, which can hide malformed metadata and return `None` instead of surfacing corruption. Correct reclamation depends on version headers accurately setting `UsesDataDir`. Inline-data short-circuit means delete logic must keep inline and data-dir states mutually consistent.

Test signals: tests create two versions with restore metadata and erasure info, then assert unique data dirs are returned and shared data dirs return `None`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/filemeta/inline_data.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/filemeta/msgp_decode.rs -->
# sources/object-store/rustfs/crates/filemeta/src/filemeta/msgp_decode.rs

Purpose: low-level MessagePack decoding helpers used by legacy/custom metadata decoders.

Important APIs/types/functions: `PrependByteReader` replays a previously-read byte before delegating to an inner reader. `read_nil_or_array_len` and `read_nil_or_map_len` accept MessagePack nil or array/map length encodings and return `Option<usize>`. `skip_msgp_value` recursively skips a single MessagePack value, including nested arrays/maps and extension/bin/string payloads.

Control flow: nil-or-length helpers read the marker byte and decode fixed, 16-bit, or 32-bit collection lengths; any other marker returns an error. `skip_msgp_value` reads a marker, computes the number of scalar bytes to discard or recursively skips child elements for arrays/maps, then reads the discard buffer. Extension markers include type bytes plus data bytes.

State and persistence: no persistent state. It consumes bytes from a reader and is used to preserve forward compatibility by skipping unknown fields in persisted MessagePack maps.

Dependencies and integration: uses `rmp::Marker`, `std::io::Read`, and crate `Error`/`Result`. It supports `version.rs` decode paths for old or map-based metadata.

Risks: skipping huge `Str32`/`Bin32`/`Ext32` lengths allocates a vector of that length, so corrupt metadata could cause memory pressure before EOF. `Marker::Reserved` is treated as zero-length skip instead of an error. Ext16/Ext32 skip lengths appear to include more than the one type byte required by MessagePack extension payloads, so changes should be validated against fixtures before reuse.

Test signals: no tests in this module; behavior is indirectly covered by legacy metadata fixture decoding in `filemeta.rs` and `version.rs` tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/filemeta/msgp_decode.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/filemeta/validation.rs -->
# sources/object-store/rustfs/crates/filemeta/src/filemeta/validation.rs

Purpose: validation and statistics helpers for `FileMeta` and `FileMetaVersionHeader`.

Important APIs/types/functions: `FileMeta::is_compatible_with_meta`, `validate_integrity`, private `is_sorted_by_mod_time`, `get_version_stats`, `VersionStats`, `FileMetaVersionHeader::is_valid`, `DetailedVersionStats`, and `FileMeta::get_detailed_version_stats`.

Control flow: integrity validation checks newest-first ordering and delegates inline data validation. Basic compatibility currently requires `meta_ver == XL_META_VERSION`. Version stats count object versions, delete markers, invalid/legacy versions, and free versions. Header validation checks valid version type, allows mod times no more than 24 hours in the future, and validates erasure coding only when both erasure fields indicate EC is present. Detailed stats decode object version metadata to aggregate total object size and count data-dir/inline-data usage.

State and persistence: read-only validation over the in-memory representation loaded from persisted `xl.meta`. Future-time validation depends on current UTC time, so results can vary with clock skew.

Dependencies and integration: depends on `FileMetaVersion`, `VersionType`, `OffsetDateTime`, `time::Duration`, and inline-data validation. Benchmarks and unit tests call these helpers as compatibility and performance signals.

Risks: `is_compatible_with_meta` is intentionally minimal and does not validate header version or version body compatibility. Legacy versions are counted as invalid in `VersionStats` but separately in `DetailedVersionStats`, so consumers must choose the right stats type. Header EC validation is skipped if `has_ec` is false, allowing partial zero EC fields.

Test signals: filemeta tests and Criterion benchmarks cover integrity success, sorting expectations, version stats accuracy, detailed stats, header validation edge cases, and validation performance.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/filemeta/validation.rs -->
