# sources/object-store/rustfs/crates/ecstore/src/set_disk.rs lines 6889-6987

## Scope And Purpose

This chunk is the tail of the `set_disk.rs` unit-test module. It does not add production runtime behavior directly; instead, it pins down three narrow but important contracts in the erasure set implementation:

- small object and multipart part write-path classification for non-inline, single-block payloads;
- S3-compatible storage-class categorization helpers for cold and infrequent-access classes;
- a regression path for same-bucket/same-key copy of a transitioned, tiered object where `ObjectInfo.metadata_only` is false.

The surrounding production code is in the same file. `classify_small_write_path` and its helpers are used by both `put_object` and `copy_object_part` encoding paths. `is_cold_storage_class` and `is_infrequent_access_class` are exported predicates used to distinguish lifecycle/tiering classes. `SetDisks::copy_object` is the lower erasure-set implementation used by higher-level store and set routing code for self-copy metadata updates, version-only copies, and tiered-object de-tiering.

## Important APIs, Types, And Functions

`should_use_single_block_non_inline_fast_path(is_inline_buffer, object_size, block_size)` returns true only when the input is not inline-buffered and `object_size` is positive and no larger than the erasure block size. The test in this chunk asserts the exact boundary behavior: sizes equal to and below the block size are fast-path candidates, one byte above the block size is not, and zero is not.

`SmallWritePath` is the internal classifier result with `Inline`, `SingleBlockNonInline`, and `Pipeline` variants. `classify_small_write_path` prefers the inline fast path when `is_inline_buffer` is true and the object fits a single block, otherwise uses `SingleBlockNonInline` for non-inline single-block data, and falls back to `Pipeline`.

`is_cold_storage_class(storage_class)` recognizes `DEEP_ARCHIVE`, `GLACIER`, and `GLACIER_IR`. The test also asserts that standard, reduced redundancy, standard infrequent access, and express one-zone classes are not cold classes.

`is_infrequent_access_class(storage_class)` recognizes `ONEZONE_IA`, `STANDARD_IA`, and `INTELLIGENT_TIERING`. The test asserts that standard, reduced redundancy, deep archive, and express one-zone are not infrequent-access classes.

`SetDisks::copy_object` is the lower-level copy entry point under test for the tiered self-copy regression. Relevant inputs are `src_bucket`, `src_object`, `dst_bucket`, `dst_object`, mutable `ObjectInfo`, source options, and destination options. The chunk constructs `ObjectInfo { metadata_only: false, transitioned_object.tier: "NEXTCLOUD", .. }` and calls `copy_object` with identical source and destination keys and `dst_opts.no_lock = true`.

The test uses `SetupTypeGuard::switch_to(SetupType::Erasure)`, `make_test_set_disks`, `LocalClient`, and `GlobalLockManager` to build a minimal erasure-set test environment while avoiding nested lock waits through `no_lock`.

## Control Flow

The small-write test exercises a pure decision path. The helper first rejects inline buffers for the non-inline fast path, then delegates size validation to `object_fits_single_block`, which rejects zero, negative, and `usize` conversion overflow cases and accepts `1..=block_size`. The classifier uses that result to select `SmallWritePath::SingleBlockNonInline` for multipart and non-inline small object writes.

In production, `put_object` calls `classify_small_write_path(is_inline_buffer, data.size(), fi.erasure.block_size)` before choosing among `encode_inline_small`, `encode_single_block_non_inline`, and the normal streaming `encode` pipeline. `copy_object_part` calls the same classifier with `is_inline_buffer = false`; only `SingleBlockNonInline` receives the special single-block encoding path, while `Inline` and `Pipeline` both use normal streaming encode for multipart data.

The storage-class tests are direct predicate checks. They serve as a concise executable mapping from the constants in `config::storageclass` to the semantic categories used by lifecycle/tiering code.

The tiered self-copy regression follows `SetDisks::copy_object`'s initial guard. If `metadata_only` is false, cross-key copies are still rejected with `StorageError::NotImplemented`, but same-key copies are allowed to continue. If `src_info.put_object_reader` is present, the method de-tiers by calling `put_object` for the destination. If no reader is present, same-key copy falls through to the metadata path so callers receive a normal disk, missing-file, or quorum error instead of an early `NotImplemented`.

After the initial same-key check, `copy_object` optionally acquires a write lock unless `dst_opts.no_lock` is true, checks HTTP write preconditions, reads all xl/file metadata from disks, computes read/write quorum, picks a valid `FileInfo`, rejects delete markers, updates metadata, version ID, versioning flags, mod time, and etag, and persists either with `write_unique_file_info` for version-only copies or `update_object_meta_with_opts` for normal metadata replacement.

## State And Persistence Behavior

The small-write and storage-class tests are pure and have no persistent state. Their importance is indirect: changing these helpers changes which erasure encoder path writes object shards and part shards. A misclassification can alter inline data placement, bitrot writer usage, memory behavior, or quorum write behavior.

The tiered self-copy test builds in-memory/minimal local lock state and does not create object shard data. Its expected outcome deliberately allows success or any ordinary storage error except `StorageError::NotImplemented`. That makes the test a guard for routing and validation behavior, not a full persistence test for de-tiering bytes.

The production `copy_object` path is stateful. It reads existing object metadata from the erasure disks, derives quorum from available metadata, mutates `FileInfo` metadata and version fields, and writes metadata back to online disks. For version-only copy it preserves inline-data flags carefully across valid metadata entries before calling `write_unique_file_info`; for ordinary metadata updates it calls `update_object_meta_with_opts` with `replace_user_metadata = true`.

For tiered objects with an available `put_object_reader`, same-key `metadata_only = false` can write remote tier data back to local erasure storage through `put_object`. For tiered objects without a reader, the current lower-level behavior is intentionally to fall through and surface a disk/quorum style error rather than a feature-not-implemented error.

## Dependencies And Integration Points

The small-write path integrates with the erasure coding module and bitrot writer setup in `put_object` and `copy_object_part`. It depends on `HashReader`, erasure block sizing from `FileInfo.erasure.block_size`, write quorum checks, and writer construction for each target disk.

The storage-class predicates depend on `crate::config::storageclass` constants. They are likely consumed by lifecycle, restore, transition, and object classification paths that need different behavior for archive-like classes versus infrequent-access classes.

The tiered copy regression sits at the boundary between higher-level object copy routing and lower-level set operations. `store/object.rs` decides when a self-copy should be metadata-only, version-only, or restored from a tier through `put_object_reader`; `sets.rs` routes between source and destination sets; `SetDisks::copy_object` enforces the final same-key-only lower-copy contract. The test imports `TransitionedObject` from lifecycle operations because tier metadata is represented on `ObjectInfo.transitioned_object`.

Locking is also an integration point. Earlier nearby tests assert `copy_object` honors `dst_opts.no_lock` when an outer write lock is already held and rejects metadata-only cross-key lower copies. This chunk's regression uses the same `no_lock` option to focus on the NotImplemented guard rather than lock acquisition.

## Risks And Edge Cases

The single-block fast path is boundary-sensitive. Treating zero-length payloads as single-block writes, accepting payloads larger than the block size, or failing to distinguish inline from non-inline buffers would send data through the wrong encoder and could affect shard layout or read compatibility.

Storage-class classification can drift as new classes are added. The predicates are explicit allowlists, so adding a new archive or infrequent-access class elsewhere without updating these helpers would silently route that class as a normal/frequent class.

The tiered self-copy test documents a historical regression, but the embedded comment is stale relative to the current implementation: it says the test currently fails because an old guard unconditionally rejected `!metadata_only`, while the current `copy_object` implementation already allows same-key `metadata_only = false` and only rejects cross-key copies. Keeping that comment stale could confuse future debugging even though the test assertion remains useful.

The regression test is intentionally weak on persistence. It only rejects `StorageError::NotImplemented`; it does not verify that tier data is fetched, written locally, metadata transitions are cleared or preserved correctly, or storage-class headers are applied. Those behaviors need broader integration tests with a real `put_object_reader` and readable object metadata.

Because same-key path checks use `path_join_buf(&[bucket, object])`, correctness depends on consistent path normalization. Any change in bucket/object path joining semantics could alter whether a copy is considered self-copy or cross-key.

## Test Signals

The chunk provides direct unit-test signals:

- `put_object_part_fast_path_selection_matches_single_block_non_inline_rules` guards exact size and inline-buffer boundaries for multipart part fast-path selection.
- `test_is_cold_storage_class` guards the cold-storage allowlist and several explicit non-cold classes.
- `test_is_infrequent_access_class` guards the infrequent-access allowlist and several explicit frequent or archive classes.
- `copy_object_tiered_self_copy_does_not_return_not_implemented` guards same-key tiered self-copy routing by failing only if `copy_object` returns `StorageError::NotImplemented`.

Useful follow-up test coverage would include an end-to-end tiered self-copy with `put_object_reader = Some(...)` that verifies bytes and metadata after `put_object`, plus storage-class predicate tests updated whenever new S3-compatible storage-class constants are introduced.
