# subset-b-008260 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/filemeta/version.rs -->
# sources/object-store/rustfs/crates/filemeta/src/filemeta/version.rs

## Purpose

This module owns version-level XL metadata parsing, encoding, conversion to `FileInfo`, and compatibility with older RustFS/MinIO metadata layouts. It is the main bridge between raw msgpack bytes stored in `xl.meta`, shallow version headers used for list/merge operations, full object/delete-marker metadata, legacy v1/v2 metadata, replication transition metadata, inline-data flags, and high-level object information returned to storage callers.

The file starts with an explicit rule: callers must parse version bytes through `FileMetaShallowVersion::parse_version_meta`, `FileMetaShallowVersion::into_fileinfo`, or `FileMetaVersion::try_from(&[u8])`. Direct `default()` plus `unmarshal_msg()` is intentionally discouraged because it skips the legacy `rmp_serde` fallback path.

## Important APIs, Types, and Functions

- `FileMetaShallowVersion` stores a `FileMetaVersionHeader` plus serialized full version bytes. `parse_version_meta()` delegates to `FileMetaVersion::try_from`, `into_fileinfo()` parses then converts, and `TryFrom<FileMetaVersion>` builds shallow entries by deriving a header and marshaling the full version.
- `FileMetaVersion` represents one version. It carries `version_type`, optional `MetaObjectV1`, optional current `MetaObject`, optional `MetaDeleteMarker`, `write_version`, and `uses_legacy_checksum`.
- `FileMetaVersion::try_from(&[u8])` is the central decoder. It first tries handwritten msgpack decoding and validates the result. If that fails, it tries the explicit `LegacyMetaV2Version` serde shape, then falls back to serde-decoding `FileMetaVersion` itself, marking legacy checksum behavior.
- `FileMetaVersion::decode_data_dir_from_meta()` optimizes extraction of `DDir` from a V2 object by scanning only enough msgpack to find `Type` and `V2Obj`, then falls back to full decode.
- `FileMetaVersionHeader` is the sortable, compact version identity. It stores version id, mod time, signature, version type, flags, and erasure data/parity counts. It has legacy header readers `unmarshal_v1`, `unmarshal_v2`, current `unmarshal_msg`, and `matches_not_strict`/`matches_ec` helpers for quorum merge.
- `MetaObject` is the current object metadata shape with custom msgpack field names such as `ID`, `DDir`, `EcAlgo`, `PartNums`, `MTime`, `MetaSys`, and `MetaUsr`.
- `MetaObjectV1` plus nested `MetaObjectV1Stat`, `MetaObjectV1Erasure`, `MetaObjectV1ChecksumInfo`, and `MetaObjectV1Part` model the older V1 object body and convert it to modern `FileInfo`, `ErasureInfo`, `ChecksumInfo`, and `ObjectPartInfo`.
- `MetaDeleteMarker` represents delete markers and tier free-version delete entries, including free-version transition metadata.
- `VersionType`, `ChecksumAlgo`, and `Flags` encode stored enum values and header flags.
- `merge_file_meta_versions()` merges per-disk shallow-version streams under quorum, strict/non-strict matching, requested version limits, version id de-duplication, and free-version accounting.
- `file_info_from_raw()` and `get_file_info()` are public raw-buffer entry points that load `FileMeta`, select a version, and return `FileInfo`.
- `read_xl_meta_no_data()` asynchronously reads only the metadata portion of an XL file, accounting for metadata header versions and CRC trailer sizing.

## Control Flow

Decode flow starts with msgpack helper functions for strings, binary blobs, and timestamp ext types. Current-format `FileMetaVersion::decode_from()` reads a msgpack map, resets to default, dispatches on keys, instantiates nested `MetaObject` or `MetaDeleteMarker` through `PrependByteReader` when a non-nil marker was already consumed, and skips unknown fields for forward compatibility.

If current decode is invalid, the `TryFrom<&[u8]>` path tries legacy serde shapes. `LegacyMetaV2Version` is normalized into current `FileMetaVersion` by converting object/delete-marker UUID byte fields, erasure/checksum algorithm strings, vectors, mod times, and metadata maps. A final serde fallback supports older named-field layouts.

Encoding flow is custom and intentionally not generic serde: `FileMetaVersion::encode_to()` writes a compact variable-size map, `MetaObject::encode_to()` writes Go-compatible names and omits/nils specific optional arrays/maps, and `MetaDeleteMarker::encode_to()` writes its fixed three-field map. Header encoding uses a seven-element array.

Conversion to `FileInfo` branches by version type. Object conversion optionally expands parts, filters user metadata, converts internal byte metadata to strings, extracts CRC/transition fields by suffix, reconstructs erasure info, builds replication state from internal metadata, and marks objects deleted when purge status is present. Delete marker conversion marks `deleted`, preserves metadata, reconstructs replication state, and for free-version markers populates transition tier/object/version id fields.

`merge_file_meta_versions()` repeatedly compares the top entry of each input stream, accepts identical tops, otherwise chooses the newest/preferred header according to strictness and non-strict matching, requires quorum, removes consumed/duplicate entries across streams, and appends remaining entries from the first stream when a requested non-free version count is reached.

`read_xl_meta_no_data()` reads an initial prefix, checks XL2 version, and for minor versions reads either the whole file, the declared metadata payload, or metadata plus enough CRC bytes to return only the no-data metadata prefix.

## State and Persistence Behavior

The persisted representation is msgpack-based and path-critical: object metadata is stored in `FileMetaShallowVersion.meta`, while a compact `FileMetaVersionHeader` is stored alongside it for indexing, sorting, and quorum decisions. Header versions 1, 2, and 3 are all read; current header v3 includes erasure counts and inline/data-dir/free-version flags. Object/delete metadata stores UUIDs as 16-byte binary values, nil UUIDs become `None` on decode in most full-object paths, and Unix epoch timestamps are normalized to absent mod times.

`MetaObject` separates `meta_user` from `meta_sys`. Internal metadata suffixes persist transition status, transitioned object name, transitioned version id, transition tier, CRC, inline data, tier free-version ids/markers, and replication/purge/reset status. `init_free_version()` can synthesize a persisted delete-marker entry with the free-version suffix and copied transition fields for tiered objects.

The module never writes external storage directly; persistence is through serialized byte buffers returned by `marshal_msg()` or by loading buffers into `FileMeta`.

## Dependencies and Integration Points

The module depends on the parent `filemeta` module for constants and `FileMeta`, on `fileinfo` types for `FileInfo`, erasure, part, and metadata constants, on `msgp_decode` for value skipping and nil-aware array/map readers, on `replication.rs` for replication state/status parsing, and on `rustfs_utils::http` for internal metadata suffix helpers. It also uses `rmp`, `rmp_serde`, `serde`, `uuid`, `time`, `bytes`, `tokio::io::AsyncRead`, `xxhash_rust`, and `tracing`.

External callers include raw metadata readers, metacache reconciliation, object listing/get-file-info paths, healing and erasure-store code that need data-dir/inline/free-version decisions, and tests/fixtures in `test_data.rs`.

## Risks and Edge Cases

- Parsing correctness is high risk because a bad decoder can make older `xl.meta` files unreadable. The fallback contract in `TryFrom<&[u8]>` is therefore critical.
- Several decode paths cast signed integers to `usize`/`u8` after reading `i64`; malformed negative values could wrap unless guarded by the specific field code. `write_version` explicitly rejects negative values, but many erasure/part fields do not.
- `MetaObject::into_fileinfo(all_parts=true)` indexes `part_sizes` and `part_actual_sizes` by `part_numbers.len()` without checking all vectors have the same length. Corrupt or legacy metadata with mismatched vectors could panic.
- `MetaDeleteMarker::decode_from()` errors on unknown fields, unlike object/version decode paths that skip unknowns. That is less forward-compatible for delete marker evolution.
- `init_free_version()` panics on invalid tier free-version id instead of returning an error.
- Header signatures derived by `From<FileMetaVersion> for FileMetaVersionHeader` are initialized to zero, while separate `get_signature` helpers compute content signatures. Callers relying on nonzero signatures need to update or derive them explicitly.
- The fast `decode_data_dir_from_v2_object()` depends on map field order enough to see `Type` before interpreting `V2Obj`; it falls back to full parsing on failure, which protects correctness but can cost work.
- `read_xl_meta_no_data()` has subtle length arithmetic around CRC sizing and partial reads; off-by-one or malformed length handling could lead to `FileCorrupt` or unexpected EOF.

## Test Signals

This file contains substantial unit tests. They verify v1/v2/v3 header decoding, legacy v1 object body conversion to `FileInfo`, legacy meta v2 delete marker decoding, invalid legacy UUID rejection, nil legacy UUID acceptance for object/delete marker paths, fast data-dir extraction, transition version id nil filtering, and free-version delete marker transition id handling. Fixture helpers in `test_data.rs` provide real/corrupt/legacy XL metadata used by other tests.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/filemeta/version.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/filemeta_inline.rs -->
# sources/object-store/rustfs/crates/filemeta/src/filemeta_inline.rs

## Purpose

This module defines `InlineData`, the compact persisted container for object data embedded inside metadata rather than stored as separate part files. It wraps a versioned byte buffer containing a msgpack map from string keys to binary values. Keys are typically version UUID strings, and values are inline object payloads.

## Important APIs, Types, and Functions

- `InlineData(Vec<u8>)` is cloneable, serializable, deserializable, and defaults to an empty buffer.
- `INLINE_DATA_VER` is the only supported on-buffer version, currently `1`.
- `new()`, `update()`, and `as_slice()` construct, replace, and expose raw bytes.
- `version_ok()` accepts empty data and versions in `1..=INLINE_DATA_VER`.
- `after_version()` returns the msgpack map bytes after the leading version byte.
- `entries()` returns the msgpack map length, or zero for empty/unsupported version buffers.
- `find(key)` scans the map and returns the matching binary value.
- `validate()` ensures the stored map can be decoded and that keys are non-empty.
- `replace(key, value)` updates or appends a key and rewrites the full buffer.
- `remove_key(key)`, `remove(Vec<Uuid>)`, and `remove_two(first, second)` remove entries by literal string key or UUID-hyphenated keys.
- Internal helpers `contains_key_by`, `remove_keys_by`, `remove_two_keys_by_bytes`, and `serialize` implement efficient scanning and whole-map rewrite.

## Control Flow

Read operations skip the first byte, decode the msgpack map length, iterate key/value pairs, and skip values by advancing the cursor by their binary length. `find()` materializes the key as UTF-8 only when comparing to the requested string; `contains_key_by()` compares raw key bytes and avoids allocation for misses.

Write operations are rebuild-based. `replace()` reads all existing entries into key/value vectors, substitutes the first matching key or appends a new entry, then calls `serialize()`. Removal paths first scan for a hit to avoid rewriting on misses, then rebuild all non-removed entries. If all entries are removed, the raw buffer is set to empty rather than an encoded empty map.

`serialize()` asserts key/value vector length equality, writes the version byte, writes a msgpack map length, then emits each string key and binary value.

## State and Persistence Behavior

The persisted bytes are `version-byte || msgpack-map<string, bin>`. Empty inline data is represented by an empty vector, not by a versioned zero-length map. The code preserves entry order during replacements/removals except when appending new keys at the end. UUID removal canonicalizes keys using lower-case hyphenated UUID strings, so stored keys must match that textual form.

## Dependencies and Integration Points

The module uses crate-local `Error`/`Result`, `rmp` decode/encode primitives, `serde` derives for outer struct serialization, `std::io::Cursor/Read`, and `uuid::Uuid`. It is exported by `lib.rs` and used by `FileMeta` and test fixtures to store/retrieve inline data and by version headers through the inline-data flag stored in `MetaObject.meta_sys`.

## Risks and Edge Cases

- `validate()` does not call `version_ok()`, so a non-empty buffer with an unsupported version byte will still be decoded from byte 1 as msgpack.
- Cursor advancement trusts declared msgpack string/bin lengths; malformed buffers return decode/read errors, but extreme lengths could allocate large key buffers in `replace`, `remove_keys_by`, and `find`.
- `serialize()` uses an `assert_eq!`, so internal misuse with mismatched vectors panics instead of returning an error.
- `remove(Vec<Uuid>)` does a linear scan over encoded removal keys for every stored key; large maps or large removal sets may be quadratic.
- Duplicate keys are not collapsed except that `replace()` updates every matching key's value while leaving duplicates present.

## Test Signals

The module has unit tests for a missing `remove_key()` preserving the raw buffer and for `remove_two()` removing exactly two UUID-keyed entries while keeping an unrelated entry findable.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/filemeta_inline.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/lib.rs -->
# sources/object-store/rustfs/crates/filemeta/src/lib.rs

## Purpose

This is the crate root for `rustfs-filemeta`. It defines the module structure and re-export surface for file metadata, file info, inline data, metacache, replication, errors, and test fixtures.

## Important APIs, Types, and Functions

The file declares private modules `error`, `fileinfo`, `filemeta`, `filemeta_inline`, `metacache`, and `replication`; `headers` is present but commented out. It exposes `test_data` publicly as a module and then publicly re-exports all items from `error`, `fileinfo`, `filemeta`, `filemeta_inline`, `metacache`, and `replication`.

## Control Flow

There is no runtime control flow. Compilation wires the crate modules and glob re-exports so downstream crates can import public types from the crate root rather than deep module paths.

## State and Persistence Behavior

No state is stored here. Persistence behavior is delegated to the re-exported modules, especially `filemeta`, `filemeta_inline`, `metacache`, and `replication`.

## Dependencies and Integration Points

This root controls integration for all crate consumers. The broad glob re-exports mean changes to any exported public type in the child modules immediately affect the crate-level API. `pub mod test_data` also exposes fixture builders to downstream test code.

## Risks and Edge Cases

- Glob re-exports can create API ambiguity if child modules introduce same-named public items.
- Because `test_data` is public in all builds, fixture helpers and fixture include paths become part of the visible crate surface unless gated elsewhere.
- The commented `headers` module hints at either removed or pending API; consumers cannot access it through this crate root.

## Test Signals

There are no tests in this file. Its behavior is implicitly covered by any crate compilation or downstream imports using the root exports.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/metacache.rs -->
# sources/object-store/rustfs/crates/filemeta/src/metacache.rs

## Purpose

This module provides two related capabilities. First, it models and streams metacache entries used for object listing and metadata reconciliation across disks. Second, it implements a generic asynchronous TTL cache with stale-value and background-refresh options.

Metacache entries carry an object or prefix name plus raw XL metadata bytes and optional decoded `FileMeta`. Reconciliation logic chooses or synthesizes a usable entry under directory/object quorum constraints.

## Important APIs, Types, and Functions

- `MetadataResolutionParams` carries directory quorum, object quorum, requested version count, bucket name, strict flag, and candidate version streams.
- `MetaCacheEntry` stores `name`, raw `metadata`, optional decoded `cached: FileMeta`, and `reusable`. Key methods include `marshal_msg`, `is_dir`, `is_in_dir`, `is_object`, `is_object_dir`, `is_latest_delete_marker`, `to_fileinfo`, `file_info_versions`, `matches`, and `xl_meta`.
- `MetaCacheEntries(Vec<Option<MetaCacheEntry>>)` provides `resolve()` for quorum reconciliation and `first_found()`.
- `MetaCacheEntriesSorted` wraps entries with list id/reuse/last skipped state, exposes flattened entries, and supports `forward_past(marker)`.
- `MetacacheWriter<W>` writes a stream with `METACACHE_STREAM_VERSION`, then repeated bool/name/bin records, ending with a false bool.
- `MetacacheReader<R>` reads the stream incrementally from an `AsyncRead`, with `peek()`, `skip(size)`, and `read_all()`.
- `Cache<T>` is a generic async cache using `UpdateFn<T>`, `ttl`, `Opts`, `ArcSwapOption`, an atomic last-update timestamp, and an async mutex to coalesce refreshes.
- `Opts` controls `return_last_good` and `no_wait` behavior.

## Control Flow

`MetaCacheEntry::to_fileinfo()` special-cases directory placeholders, uses cached metadata when available, and otherwise calls `get_file_info()` on raw bytes. `is_latest_delete_marker()` prefers cached versions, then fast indexed metadata checks, then full `xl_meta()` parsing, treating parse errors as delete markers in some paths.

`MetaCacheEntry::matches()` compares two entries. It first orders by name, handles directory placeholders, decodes both `FileMeta` values, compares version counts and latest mod times, then compares version headers. In non-strict mode it can ignore signature differences for otherwise matching headers and prefers the newest sortable header.

`MetaCacheEntries::resolve()` scans candidates, counts directory hits and valid object metadata, populates candidate version streams, chooses an initial or preferred selected entry, and returns directory entries if directory quorum is met. For objects, it rejects if valid object count is below quorum. If all valid objects agree, it reuses the selected entry. If they disagree, it calls `merge_file_meta_versions()`, marshals a new `FileMeta`, and returns a reusable synthetic `MetaCacheEntry`.

The stream writer lazily writes the version in `init()`, flushes after each object, and emits an end marker in `close()`. The reader lazily checks version, reads msgpack markers manually, buffers exact bytes as needed, and resets its buffer after each entry.

`Cache::get_shared()` returns fresh cached values when TTL has not expired. In `no_wait` mode, if the value is stale but less than twice TTL old, it returns the stale value and tries to spawn one background update. Otherwise it waits on the update mutex, rechecks freshness, runs `update()`, and returns the stored value. `return_last_good` suppresses update errors when a cached value exists.

## State and Persistence Behavior

Metacache entry persistence is a simple msgpack stream: version byte, then repeated records containing a boolean continuation marker, a string name, and binary metadata. The stream version currently written is `2`; the reader accepts versions `1` and `2`.

`MetaCacheEntry.cached` is an in-memory decode cache skipped by serde. `xl_meta()` populates it lazily. Reconciled entries may have `reusable=true` and newly marshaled metadata bytes reflecting merged versions.

The generic `Cache<T>` stores an `Arc<T>` in `ArcSwapOption`, records update time as Unix seconds, and uses a mutex only for update coordination. It does not persist across process restarts.

## Dependencies and Integration Points

Metacache integrates with `FileMeta`, `FileMetaShallowVersion`, `VersionType`, `get_file_info`, `FileInfoVersions`, `FileInfoOpts`, and `merge_file_meta_versions` from the filemeta crate. It uses `tokio` async IO/spawn/mutex, `rmp` marker decoding, `arc_swap` for lock-free cached reads, `time::OffsetDateTime`, and `tracing`.

It is likely used by object listing, quorum reads, healing/reconciliation, and cache-heavy metadata paths where repeatedly loading XL metadata would be expensive.

## Risks and Edge Cases

- `MetacacheReader::check_init()` reads two bytes and then decodes a `u8`; this may consume more than a single version byte depending on the stream and should be treated carefully if stream layout changes.
- `MetacacheReader::skip()` subtracts one when `current.is_some()`; calling it with `size == 0` while current is set would underflow `usize`.
- `read_more()` grows buffers based on caller-provided lengths from msgpack markers; malformed streams can request large allocations.
- `resolve()` clones entries and metadata extensively. Large listings or many versions can be allocation-heavy.
- `matches()` returns `(None, false)` on decode failures, which may cause reconciliation to drop candidates without surfacing detailed corruption signals.
- In the generic cache, future last-update timestamps intentionally force refresh via checked subtraction returning `u64::MAX`. System clock jumps can therefore trigger refreshes.
- `no_wait` returns stale values for up to `2 * ttl`; callers must opt in only where stale data is acceptable.

## Test Signals

Tests cover writer/reader round-tripping, rebuilding resolved metadata from merged versions, concurrent cache access, fresh `get_shared()` pointer reuse, future timestamp refresh behavior, `no_wait` background refresh behavior, background refresh coalescing, and `return_last_good` error handling both enabled and disabled.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/metacache.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/replication.rs -->
# sources/object-store/rustfs/crates/filemeta/src/replication.rs

## Purpose

This module defines replication status, purge status, replication decisions, MRF replay entries, worker-operation abstraction, and helpers for converting per-target state into internal metadata strings and composite object status. It is the metadata-side model used by object replication, delete replication, heal replication, resync, and recovery queues.

## Important APIs, Types, and Functions

- Constants such as `REPLICATE_QUEUED`, `REPLICATE_EXISTING`, `REPLICATE_MRF`, `REPLICATE_INCOMING`, and heal/delete variants name replication audit/event origins.
- `ReplicationStatusType` models S3-style `PENDING`, `COMPLETED`, legacy `COMPLETE`, `FAILED`, `REPLICA`, and empty states, with string conversion and conversion from `VersionPurgeStatusType`.
- `VersionPurgeStatusType` models `PENDING`, `COMPLETE`, `FAILED`, and empty purge states.
- `ReplicationType` models object/delete/metadata/heal/existing/resync/all operation kinds and has validity/data-replication helpers.
- `ReplicationState` stores timestamps, replica status, internal replication/purge status strings, parsed target maps, reset status map, and replicate-decision string. It provides `equal`, composite status helpers, and `target_state`.
- `get_composite_replication_status()` and `get_composite_version_purge_status()` reduce target maps to overall status.
- `ReplicationAction`, `ReplicatedTargetInfo`, and `ReplicatedInfos` describe per-target results and aggregate completed size, resync occurrence, internal status strings, aggregate status, purge status, and action.
- `MrfOpKind` and `MrfReplicateEntry` define persisted Most Recent Failures queue entries, with serde defaults for backward compatibility.
- `ReplicationWorkerOperation` is a trait abstraction for queued replication work.
- `ReplicateTargetDecision` and `ReplicateDecision` model per-target replication decisions and can render pending status or parse string decisions with `parse_replicate_decision`.
- `ReplicateObjectInfo` is the concrete object/delete replication work item and implements `ReplicationWorkerOperation`.
- `replication_statuses_map()`, `version_purge_statuses_map()`, `get_replication_state()`, and `target_reset_header()` convert between strings, maps, and persisted state.
- `ResyncDecision` and `ResyncTargetDecision` model target-specific resync requirements.

## Control Flow

Status conversion is mostly enum/string mapping. Composite status reduction returns failed if any target failed, completed/complete only if all targets completed, pending otherwise, and empty when there are no targets.

`ReplicationState::composite_replication_status()` first honors a simple internal status string if it is one of the known direct statuses. Otherwise it reduces parsed target statuses. If a replica timestamp is newer than the replication timestamp and all targets look completed, it can return the replica status instead. Purge status follows the same direct-string-first, map-reduction-second pattern.

`ReplicatedInfos` builds internal status strings in `arn=status;` form, skipping empty targets and empty purge statuses. `action()` returns the replication action from the first target that was not already completed.

`parse_replicate_decision()` parses comma-delimited `key=replicate;synchronous;arn;id` items. It rejects malformed pairs or target strings with `InvalidInput`.

`ReplicateObjectInfo::target_replication_status()` applies a lazily compiled regex to `replication_status_internal` and returns the matching ARN status. `to_mrf_entry()` serializes core replay fields; both the trait implementation and inherent method currently set `op` to `MrfOpKind::Object`.

`get_replication_state()` merges new `ReplicatedInfos` into previous state by preserving previous replica fields and decision string, adding reset timestamps, rebuilding parsed target maps from generated internal strings, and setting replication/purge timestamps/status strings.

## State and Persistence Behavior

Replication state is persisted mainly as strings in internal metadata. Target statuses use `arn=status;` format parsed by a global regex. Reset status keys are persisted with `internal_key_rustfs("replication-reset-{arn}")`. `MrfReplicateEntry` is serde-serializable and intentionally backward-compatible: missing `versionID`, `op`, `deleteMarkerVersionID`, `deleteMarker`, and `size` fields default safely for old queue entries.

Timestamps are `OffsetDateTime`; durations are stored in `ReplicatedTargetInfo` for runtime result reporting. Decision and resync maps are normal Rust maps and are rendered only where needed.

## Dependencies and Integration Points

The module uses `bytes::Bytes`, `regex::Regex`, `LazyLock`, `serde`, `time`, `uuid`, `Duration`, and `rustfs_utils::http::internal_key_rustfs`. It integrates with `version.rs` through `get_internal_replication_state()`, which parses internal metadata into `ReplicationState`, and with replication workers/managers through `ReplicationWorkerOperation`, `ReplicateObjectInfo`, and MRF entries.

## Risks and Edge Cases

- `REPL_STATUS_REGEX` is `([^=].*?)=([^,].*?);`; it is permissive and can match broad substrings. ARNs or malformed status strings containing delimiters may parse unexpectedly.
- `parse_replicate_decision()` splits on every `=` and requires exactly two parts, so ARNs/ids containing `=` would break parsing.
- `ReplicateObjectInfo::to_mrf_entry()` always writes `MrfOpKind::Object`, even when `op_type` or `delete_marker` indicates delete work. Delete-specific MRF fields are therefore not populated by this method.
- `ReplicationStatusType::CompletedLegacy` exists but composite map reduction counts only `Completed` as complete. Legacy `COMPLETE` parsed from per-target maps will not count as completed.
- `ReplicationState::equal()` compares only status fields, not timestamps, target maps, purge maps, reset maps, or decisions. This is intentional if equality means "status-equivalent", but risky if used as full-state equality.
- Display/string serialization iterates hash maps, so output ordering is nondeterministic.

## Test Signals

This file has no local test module. It is indirectly exercised by `version.rs` object/delete conversion tests that parse internal replication/purge metadata and by higher-level replication/heal code that consumes these exported types.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/replication.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/test_data.rs -->
# sources/object-store/rustfs/crates/filemeta/src/test_data.rs

## Purpose

This module builds deterministic and fixture-backed `xl.meta` byte buffers for tests. It covers current metadata, complex multi-version metadata, inline-data metadata, corrupted metadata, empty metadata, hand-built legacy v1 metadata, and real legacy hex fixtures captured from RustFS issues.

## Important APIs, Types, and Functions

- `create_real_xlmeta()` builds a `FileMeta` with one object version, one delete marker, and one manually adjusted legacy shallow version, then sorts by newest mod time and marshals it.
- `create_issue_2288_legacy_xlmeta()`, `create_issue_2265_legacy_meta_v2_object_xlmeta()`, `create_issue_2265_legacy_meta_v2_config_xlmeta()`, and `create_issue_2434_legacy_meta_v2_pool_xlmeta()` decode included hex fixtures.
- `create_legacy_v1_object_xlmeta()` hand-builds an XL2 file with legacy v1 header/body layout and CRC.
- `create_complex_xlmeta()` creates ten object versions plus periodic delete markers with varying UUIDs, data dirs, sizes, etags, and times.
- `create_corrupted_xlmeta()` returns a deliberately truncated XL2 payload.
- `create_empty_xlmeta()` marshals an empty `FileMeta`.
- `verify_parsed_metadata()` asserts version count, metadata version, and descending mod-time ordering.
- `create_xlmeta_with_inline_data()` stores inline payload bytes in `FileMeta.data` and adds one object version referencing the inline version id.

## Control Flow

The builder functions construct `MetaObject`, `MetaDeleteMarker`, and `FileMetaVersion` values, convert them to `FileMetaShallowVersion`, push them into `FileMeta.versions`, sort when needed, and call `FileMeta::marshal_msg()`. Legacy helpers manually encode msgpack headers and bodies with `rmp`, write the XL2 magic/version bytes, patch the data length into the header, and append an xxh64 CRC trailer.

The fixture helpers call `decode_hex_fixture()`, which trims the included fixture string, validates even length, converts each hex pair with `to_digit(16)`, and returns bytes or a crate error naming the invalid index.

## State and Persistence Behavior

All state produced is in-memory byte vectors, but those vectors are intended to match persisted `xl.meta` layouts. The real fixture functions use `include_str!("../tests/fixtures/...")`, tying the compiled crate to fixture files under `crates/filemeta/tests/fixtures`. Legacy hand-built data writes `"XL2 "`, little-endian header/meta versions, a msgpack bin32 length marker, msgpack metadata body, and a big-endian CRC marker/value.

## Dependencies and Integration Points

This module depends on crate-local metadata types, `time::OffsetDateTime`, `uuid`, `xxhash_rust`, `rmp`, and fixture files. It is exported as `pub mod test_data` by `lib.rs` and is used by unit tests in `metacache.rs`, likely by `filemeta` tests, and by downstream crates that need realistic metadata bytes.

## Risks and Edge Cases

- Several helpers use `Uuid::new_v4()` and `OffsetDateTime::now_utc()`, so some generated metadata is nondeterministic. Tests should assert structural properties rather than exact bytes for those helpers.
- The public `verify_parsed_metadata()` uses assertions rather than returning normal validation errors for mismatches; it can panic in callers.
- `create_real_xlmeta()` includes a `VersionType::Legacy` shallow version with no `legacy_object` body and manually adjusted header fields. It is useful for ordering/header tests but not a fully valid legacy object body.
- The hand-built legacy XL2 writer has low-level length/CRC logic; changes to `FileMeta` wire format can silently stale this fixture builder.
- Fixture include paths must remain valid for crate compilation.

## Test Signals

Local tests verify that real, complex, inline-data, corrupted, and empty metadata helpers produce parseable or intentionally failing buffers. They assert XL2 magic, version counts, inline data presence, and corrupted-load failure.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/filemeta/src/test_data.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/Cargo.toml -->
# sources/object-store/rustfs/crates/heal/Cargo.toml

## Purpose

This manifest defines the `rustfs-heal` crate, described as RustFS erasure set and object healing. It declares package metadata, workspace inheritance, dependencies, development dependencies, and disables doctests for the library target.

## Important APIs, Types, and Functions

As a Cargo manifest, it does not define Rust APIs directly. Its important interface is the crate package:

- Package name: `rustfs-heal`.
- Workspace-managed version, edition, license, rust-version, repository, homepage, and dependency versions.
- Description: `RustFS erasure set and object healing`.
- Library target with `doctest = false`.

## Control Flow

Cargo uses this file during dependency resolution and compilation. The selected dependencies enable async healing logic, storage access, admin/common/config integration, serialization, errors, metrics, and tests. Tokio is built with `sync`, `io-util`, `time`, and `macros` for normal use, and with `test-util` and `fs` in dev-dependencies.

## State and Persistence Behavior

No runtime state is stored here. The manifest controls build-time state: feature selection, dependency graph, package metadata, and documentation/test behavior. Disabling doctests means examples in crate docs, if any, will not be executed by `cargo test --doc`.

## Dependencies and Integration Points

Runtime dependencies include RustFS crates `rustfs-config`, `rustfs-ecstore`, `rustfs-storage-api`, `rustfs-common`, `rustfs-madmin`, and `rustfs-utils`; async/runtime crates `tokio`, `tokio-util`, `async-trait`, and `futures`; diagnostics/ops crates `tracing` and `metrics`; data/error crates `serde`, `serde_json`, `thiserror`, `anyhow`, and `uuid`.

Dev dependencies include `serial_test`, `tracing-subscriber`, `tempfile`, `walkdir`, `http`, `temp-env`, and extra Tokio features. These point to tests that likely exercise filesystem walks, temporary environments, HTTP-ish types, tracing setup, and serialized/isolated heal scenarios.

## Risks and Edge Cases

- `serde_json` appears in both dependencies and dev-dependencies; that is harmless but redundant unless different feature sets are needed.
- The crate uses both `thiserror` and `anyhow`, and `error.rs` has an `Anyhow` variant. Clear boundaries are needed to avoid losing typed error information.
- Healing is storage-critical; dependency changes in `rustfs-ecstore` or `rustfs-storage-api` can have broad impact.
- `doctest = false` reduces documentation test coverage.

## Test Signals

The manifest itself has no tests, but dev-dependencies indicate expected test coverage around temporary files/directories, serialized tests, environment manipulation, tracing, walking directory trees, HTTP types, and Tokio async testing.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/error.rs -->
# sources/object-store/rustfs/crates/heal/src/error.rs

## Purpose

This module defines the typed error surface for the `rustfs-heal` crate. It centralizes storage, disk, configuration, task lifecycle, transient skip, serialization, progress, event, timeout, cancellation, and generic error cases, and exposes the crate-local `Result` alias.

## Important APIs, Types, and Functions

- `Error` is a `thiserror::Error` enum with variants for:
  - wrapped `std::io::Error`;
  - wrapped `rustfs_ecstore::error::Error`;
  - wrapped `rustfs_ecstore::disk::error::DiskError`;
  - string configuration/other/serialization/IO/not-found/checkpoint errors;
  - structured task errors such as `TaskNotFound`, `TaskAlreadyExists`, `TaskExecutionFailed`, `InvalidHealType`, event/progress failures;
  - lifecycle states such as `InvalidClientToken`, `ManagerNotRunning`, `TaskCancelled`, and `TaskTimeout`;
  - `TransientSkip` for retryable background heal checks;
  - transparent `anyhow::Error`.
- `pub type Result<T, E = Error>` is the heal crate result alias.
- `Error::other()` converts any boxed-compatible error into `Error::Other`.
- `Error::transient_skip()` builds a `TransientSkip`.
- `impl From<Error> for std::io::Error` wraps heal errors into `std::io::Error::other`.

## Control Flow

Most control flow is through automatic `From` conversions generated by `thiserror` for I/O, ecstore, disk, and anyhow errors. Callers can use `?` to convert those into heal errors. Explicit constructors support generic "other" errors and retryable transient skips. The reverse conversion to `std::io::Error` lets heal APIs integrate with interfaces that require I/O errors.

## State and Persistence Behavior

The enum itself is transient runtime state and is not serialized. Some variants carry task ids, heal types, and messages that may be logged, returned to admin APIs, or embedded in status/progress reporting. No persistent storage is directly modified here.

## Dependencies and Integration Points

The module depends on `thiserror`, `anyhow`, and error types from `rustfs-ecstore`. It is consumed by heal managers, workers, event processors, progress trackers, and APIs through the crate-local `Result` alias.

## Risks and Edge Cases

- There are both `Io(std::io::Error)` and `IO(String)` variants, which can make matching/reporting inconsistent.
- `Config(String)` and `ConfigurationError { message }` overlap semantically.
- `Other(String)` and transparent `Anyhow` both serve generic-error roles; converting to `Other` loses the original error chain.
- `From<Error> for std::io::Error` wraps every heal error as kind `Other`, so callers that need typed task cancellation/timeout/not-found semantics must inspect the inner error string or avoid this conversion.
- The error type is not `Clone`, which is normal for `std::io::Error` but relevant for retry queues or shared task state.

## Test Signals

There are no local tests in this file. Expected coverage should come from heal crate tests that assert error conversion, task lifecycle failure mapping, transient skip handling, and manager/API responses.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/error.rs -->
