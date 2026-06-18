<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/loaded_blobs/guard.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/loaded_blobs/guard.rs

Purpose: Defines `LoadedBlobGuard`, the RAII handle returned for one loaded `FsBlob` entry in the concurrent blob cache.

Important APIs/types/functions: `LoadedBlobGuard::new` wraps a `cryfs_concurrent_store::LoadedEntryGuard<BlobId, AsyncDropTokioMutex<FsBlob<B>>, Arc<anyhow::Error>>`. `blob_id` exposes the cache key. `with_lock` serializes mutable access to the underlying typed `FsBlob`. `remove` asks the concurrent store for an immediate drop and removes the blob from persistent storage through `FsBlob::remove`.

Control flow: callers get a guard from `LoadedBlobs`; operations run inside the per-blob async mutex. Removal loops because another task may already be dropping the same entry. When removal is accepted, this guard is async-dropped first so it no longer prevents exclusive removal, then the returned drop future is awaited.

State and persistence behavior: the guard itself owns no persistent data; it protects a cached `FsBlob` whose final removal deletes the backing blob. Async drop releases the loaded-entry guard and uses `InfallibleUnwrap` because the lower-level guard is expected not to fail.

Dependencies and integration points: integrates `cryfs_concurrent_store`, `AsyncDropTokioMutex`, `FsBlob`, `BlobId`, and `RemoveResult`. `ConcurrentFsBlob::remove` delegates to this type.

Risks: removal contains a panic for the logically impossible unloaded case while a guard is held. If the returned removal future is not driven, removal can stall. Errors are wrapped in `Arc<anyhow::Error>`, which preserves sharing but makes typed recovery harder.

Test signals: no local tests are present. Useful coverage would include concurrent readers plus removal, retry after `AlreadyDropping`, and ensuring `with_lock` excludes simultaneous mutation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/loaded_blobs/guard.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/loaded_blobs/mod.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/loaded_blobs/mod.rs

Purpose: Module facade for the loaded-blob cache internals.

Important APIs/types/functions: declares private `guard` and `store` modules, re-exporting `LoadedBlobGuard`, `LoadedBlobs`, and `RequestRemovalResult`.

Control flow: no runtime flow lives here. Its role is to narrow the public surface that `concurrentfsblobstore` exposes.

State and persistence behavior: no state. State lives in `LoadedBlobs` and `LoadedBlobGuard`.

Dependencies and integration points: imported by `concurrentfsblobstore/mod.rs`, `concurrentfsblobstore/blob.rs`, and `concurrentfsblobstore/store.rs`.

Risks: facade drift is the main risk; hiding internals is useful because removal/load coordination must stay centralized.

Test signals: build coverage is the signal. Any re-export change affects the concurrent blob store public API.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/loaded_blobs/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/loaded_blobs/store.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/loaded_blobs/store.rs

Purpose: Implements `LoadedBlobs`, the process-local cache and synchronization table for typed `FsBlob` instances.

Important APIs/types/functions: `new` creates a `ConcurrentStore<BlobId, AsyncDropTokioMutex<FsBlob<B>>, Arc<anyhow::Error>>`. `try_insert_loading` registers an in-flight load/create future. `try_insert_loaded` inserts a newly created blob. `get_loaded_or_insert_loading` deduplicates concurrent loads. `get_if_loading_or_loaded` probes the cache. `request_removal` coordinates safe removal and returns `RequestRemovalResult`.

Control flow: loading functions transform `FsBlob` into `AsyncDropTokioMutex<FsBlob>` so all users share one mutable instance. A caller that wins a load waits until the insertion completes. Removal uses `request_immediate_drop`; if the blob is loaded it unwraps the mutex and calls `FsBlob::remove`, otherwise it removes directly from `FsBlobStore` while the concurrent-store drop slot blocks new loads.

State and persistence behavior: cache state is in memory; persistent effects are delegated to `FsBlobStore::remove_by_id` or `FsBlob::remove`. Async drop drops all cached entries, which can trigger directory writeback through `FsBlob` async drop.

Dependencies and integration points: depends on `cryfs_concurrent_store`, `AsyncDropArc`, `AsyncDropTokioMutex`, `FsBlobStore`, and `RemoveResult`. `ConcurrentFsBlobStore` owns one `LoadedBlobs`.

Risks: the caller must poll `RequestRemovalResult::RemovalRequested.on_removed` to completion or the entry can remain blocked. The comments note `Arc<anyhow::Error>` as a coarse error channel and possible hash-performance concerns for random blob ids.

Test signals: targeted tests should assert load deduplication, direct removal of unloaded blobs, loaded removal waiting for guards, and retry behavior when an entry is already dropping.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/loaded_blobs/store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/mod.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/mod.rs

Purpose: Public module root for concurrent fsblobstore support.

Important APIs/types/functions: declares `blob`, `loaded_blobs`, and `store`, and re-exports `ConcurrentFsBlob`, `LoadedBlobGuard`, `RequestRemovalResult`, and `ConcurrentFsBlobStore`.

Control flow: no runtime behavior; it shapes the crate API.

State and persistence behavior: no state here. The exported store coordinates loaded blob state and delegates persistence to `fsblobstore`.

Dependencies and integration points: consumed by crate root `lib.rs` and higher-level filesystem code needing concurrent blob access.

Risks: re-exporting `LoadedBlobGuard` exposes a low-level cache concept; misuse can bypass higher-level invariants if used outside intended store paths.

Test signals: compile/API tests and downstream usage of `ConcurrentFsBlobStore` cover this module.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/store.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/store.rs

Purpose: Defines `ConcurrentFsBlobStore`, a concurrency-safe wrapper around `FsBlobStore`.

Important APIs/types/functions: `new` wraps the base store and loaded-blob table in `AsyncDropArc`. Creation APIs create root, file, directory, and symlink blobs and insert them into `LoadedBlobs`. `load` deduplicates concurrent loads. `remove_by_id` coordinates cache-aware removal. `flush_if_cached`, `num_blocks`, space-estimation, and logical-block-size methods delegate to the underlying store.

Control flow: creating a non-root blob first creates through `FsBlobStore`, then inserts the new id as loaded. Loading calls `LoadedBlobs::get_loaded_or_insert_loading` with a cloned base store. Removing loops while another task is dropping the id. Flush checks the loaded cache first and locks the blob for direct flush; if absent, it asks lower layers to flush cached blocks.

State and persistence behavior: in-memory state is two shared async-drop arcs: the base store and loaded cache. Persistent state lives in the underlying blobstore. Async drop first drops loaded blobs, allowing dirty directory entries to write back, then drops the base store.

Dependencies and integration points: central bridge between `fsblobstore` and callers that need shared mutable access. Uses `FlushBehavior`, `ConcurrentFsBlob`, `LoadedBlobs`, and `cryfs_utils` async-drop helpers.

Risks: `expect("blob id is new")` assumes the base store always generates fresh ids. All blob operations are per-blob serialized, so a long operation under `with_lock` blocks other users of that blob. Root creation uses a loading slot to avoid races but returns only success/failure, not the root handle.

Test signals: useful tests should cover concurrent load deduplication, remove-vs-load races, flush of loaded and unloaded blobs, and drop ordering with dirty directory blobs.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/concurrentfsblobstore/store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/base_blob.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/base_blob.rs

Purpose: `BaseBlob` is the common typed-header wrapper over a raw `BlobStore::ConcreteBlob`.

Important APIs/types/functions: `parse` reads and validates the fsblob header. `try_create_with_id` and `create` build a new header plus payload. Accessors expose blob id, type, parent, data length, data read/write/resize, flush, removal, and block enumeration. Test-only helpers expose node counts and raw blobs.

Control flow: parsing reads exactly the header, checks `FORMAT_VERSION_HEADER`, caches the header view, then typed wrappers inspect `blob_type`. Creation writes a fully formed `fsblob` layout and caches only the header. Data operations offset all reads/writes past the header.

State and persistence behavior: persistent layout is `format_version_header`, `blob_type`, `parent`, then type-specific data. `set_parent` updates both storage and cache. `read_all_data` rejects blobs too small for a header.

Dependencies and integration points: used by `FileBlob`, `DirBlob`, and `SymlinkBlob`; depends on `binary_layout`, `cryfs_blobstore`, `cryfs_blockstore`, and `cryfs_utils::Data`.

Risks: error paths call `async_drop().await.unwrap()` in several places. Header validation does not verify parent consistency beyond storing the pointer. `num_data_bytes` subtracts header size and would underflow only if lower layers reported an invalid smaller blob.

Test signals: important tests are format-version rejection, data offset correctness, parent update persistence, and remove/flush delegation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/base_blob.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_blob.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_blob.rs

Purpose: `DirBlob` represents a directory blob with cached serialized directory entries.

Important APIs/types/functions: creation APIs build normal and root directory blobs. Lookup/mutation APIs expose entries by id/name, rename, add, add-or-overwrite, remove, attribute/timestamp updates, parent updates, `writeback`, `flush`, `lstat_size`, removal, and block enumeration.

Control flow: `new` deserializes `DirEntryList` from the base blob. Mutations update the in-memory list and mark it dirty. `writeback` serializes only if dirty; `flush` writes back then flushes the base blob only when serialization occurred. Removal skips async drop because serializing a directory that is about to be deleted is unnecessary.

State and persistence behavior: directory entries are cached in memory and persisted as the base blob data. Root creation uses a caller-provided id and parent `BlobId::zero()`, then flushes immediately to fail early if storage is inaccessible. Directory `lstat_size` is a fixed 4096.

Dependencies and integration points: wraps `BaseBlob` and `DirEntryList`; exports `MODE_NEW_SYMLINK` and uses fs uid/gid/mode types. Higher filesystem code uses it for namespace mutations.

Risks: dirty directory changes are not durable until writeback/drop/flush. Parent pointers are stored but not validated on load. Rename/overwrite correctness depends on the callback removing overwritten child blobs when needed.

Test signals: tests should cover add/remove/rename serialization, overwrite callback ordering, root creation conflict, and crash-window behavior when `DontFlush` is used.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_blob.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_entries/atime_update_behavior.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_entries/atime_update_behavior.rs

Purpose: Defines the policy trait for deciding whether read access should update atime.

Important APIs/types/functions: `AtimeUpdateBehavior` has `should_update_atime_on_file_or_symlink_read` and `should_update_atime_on_directory_read`, both receiving previous atime, mtime, and current time.

Control flow: no implementation lives here. `DirEntryList::maybe_update_access_timestamp` dispatches to the appropriate method based on entry type.

State and persistence behavior: no state. Implementors influence whether a directory entry becomes dirty and later serialized.

Dependencies and integration points: used by `DirBlob::maybe_update_access_timestamp_of_entry` and policy implementations elsewhere in CryFS.

Risks: policy decisions affect write amplification and POSIX timestamp semantics. Implementors must handle clock skew or equal timestamps consistently.

Test signals: policy-specific tests should verify relatime/noatime/strict-atime behavior for file, symlink, and directory reads.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_entries/atime_update_behavior.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_entries/entry.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_entries/entry.rs

Purpose: Defines the serialized directory entry record and validation rules.

Important APIs/types/functions: `EntryType` maps dir/file/symlink to one byte. `DirEntryImpl` is the binrw-serialized layout. `DirEntry` wraps it to enforce validation through `new`, `deserialize`, and `serialize`. Getters/setters expose type, mode, uid/gid, access/modification/metadata-change times, name, and blob id. `ValidationFailed` reports mismatched mode type bits.

Control flow: construction normalizes mode by setting the type bit for the entry type, then validates that exactly the matching file/dir/symlink bit is present. `set_mode` rolls back if validation fails. Path components are serialized as null-terminated nonzero bytes and parsed back through UTF-8 plus `PathComponentBuf` validation.

State and persistence behavior: persisted fields include type, mode, uid, gid, atime, mtime, ctime, name, and blob id. Changing metadata updates ctime; changing atime does not. The code comments question whether mtime should update ctime.

Dependencies and integration points: used exclusively through `DirEntryList` and exported by `dir_entries/mod.rs`. Depends on `binrw`, `BlobId`, fs types, binary timestamp helpers, and CryFS path validation.

Risks: corrupt UTF-8 or invalid path components fail deserialization. `serialize` uses `expect` if an invariant is broken. The separate `EntryType` and `BlobType` enums must remain semantically aligned.

Test signals: TODO comments call out missing tests for path component read/write. Additional coverage should validate mode-bit rejection, ctime update semantics, and malformed serialized entries.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_entries/entry.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_entries/entry_list.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_entries/entry_list.rs

Purpose: Implements the mutable in-memory directory entry collection and its serialization.

Important APIs/types/functions: `DirEntryList` stores a sorted `Vec<DirEntry>` plus a dirty flag. APIs include lookup by name/id, deserialize, serialize-if-dirty, iteration, add, add-or-overwrite, rename, set attributes, maybe update atime, update mtime, remove by name, and remove by id. Error enums model add, overwrite, set-attr, timestamp, remove, and rename failures.

Control flow: id lookups use a hinted linear lower/upper-bound search based on random blob-id bytes. Name lookups are linear. Adds insert by blob-id order. Overwrite removes and re-adds if the blob id changes. Rename can invoke an overwrite callback before deleting the target name, then mutates the source name in place.

State and persistence behavior: dirty is set on mutable access and all structural mutations. Serialization rewrites the complete directory data payload after resizing the base blob; after success dirty is cleared. Deserialization reads the whole directory payload into a cursor.

Dependencies and integration points: owned by `DirBlob`; uses `DirEntry`, `EntryType`, `BaseBlob`, fs uid/gid/mode types, and `AtimeUpdateBehavior`.

Risks: comments document a no-hardlink invariant: at most one entry per blob id. `get_by_name_mut` marks dirty before the caller actually changes anything. Deserialization does not explicitly sort or deduplicate entries, so corrupted ordering could break id lookup assumptions. Full rewrite can be costly for large directories.

Test signals: key tests should include sorted insertion, corrupted unsorted input behavior, overwrite callback failures, rename-over-existing, dirty flag serialization, and atime policy branches.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_entries/entry_list.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_entries/mod.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_entries/mod.rs

Purpose: Facade for directory entry submodules.

Important APIs/types/functions: declares `atime_update_behavior`, `entry`, and `entry_list`; re-exports `AtimeUpdateBehavior`, `DirEntry`, `EntryType`, `DirEntryList`, serialization result, and directory mutation error enums.

Control flow: none. It preserves a clean API boundary around serialized entry internals.

State and persistence behavior: no state; the re-exported types define directory persistence through `DirEntryList`.

Dependencies and integration points: used by `dir_blob.rs` and re-exported by `fsblob/mod.rs` for higher layers.

Risks: exposing `DirEntryList` along with error enums means downstream code can rely on low-level behavior, so facade changes are API-sensitive.

Test signals: compile coverage plus all `DirBlob`/`DirEntryList` tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_entries/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/file_blob.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/file_blob.rs

Purpose: Represents regular file blobs.

Important APIs/types/functions: `new`, `create_blob`, `blob_id`, `num_bytes`, `resize`, `try_read`, `write`, `flush`, `parent`, `set_parent`, `remove`, `lstat_size`, and `all_blocks`. Test-only helpers expose node count and raw blob extraction.

Control flow: all file data operations delegate to `BaseBlob` data APIs, which offset past the fsblob header. Creation stores `BlobType::File` with empty data. Removal consumes the wrapper and removes the base blob directly.

State and persistence behavior: no extra file metadata lives here beyond the base header and raw data payload. Size is the base data length. Flush delegates to the underlying blob flush.

Dependencies and integration points: constructed by `FsBlobStore` and `FsBlob::parse`; used through `FsBlob::File` and `ConcurrentFsBlob`.

Risks: file-level timestamps and ownership are not stored here; they live in parent directory entries. Callers must update parent directory metadata when file content changes. `try_read` semantics depend on lower-layer blob behavior.

Test signals: useful tests include read/write offset handling, resize truncation/extension, lstat size, parent updates, and remove not attempting a writeback.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/file_blob.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/layout.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/layout.rs

Purpose: Defines the on-disk/in-blob binary layout for fsblob headers.

Important APIs/types/functions: constants map blob type magic bytes and `FORMAT_VERSION_HEADER`. `BlobType` implements `binary_layout::LayoutAs<u8>`. `binary_layout!` declares `fsblob_header` with version, blob type, and parent id, plus `fsblob` as header plus variable data.

Control flow: `try_read` rejects unknown blob type magic values; `try_write` maps enum variants to bytes. Other modules use generated views to read/write header fields.

State and persistence behavior: this is the compatibility contract for every typed blob. Version is currently `1`; parent is persisted as raw `BLOBID_LEN` bytes.

Dependencies and integration points: used by `BaseBlob` for all parsing/creation and by typed blob wrappers through `BlobType`.

Risks: comments note parent pointers are not validated when traversing. Any layout change requires a format-version migration path. `BlobType` is distinct from `EntryType`, so duplicated type mapping must stay synchronized.

Test signals: tests should assert exact header size/field offsets, invalid magic rejection, and round-trip creation/parsing for each blob type.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/layout.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/mod.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/mod.rs

Purpose: Typed blob enum and facade for file, directory, and symlink blobs.

Important APIs/types/functions: re-exports typed blobs, directory entry types, and errors. `FsBlob` variants hold async-drop guards for `FileBlob`, `DirBlob`, and `SymlinkBlob`. APIs include `parse`, `blob_id`, type-specific `as_*` accessors, `lstat_size`, `all_blocks`, `flush`, test-only `into_raw`, and async-drop dispatch.

Control flow: parsing first creates a `BaseBlob`, then switches on the header `BlobType`. If blob type decoding fails, it async-drops the base blob before returning the error. Callers must request the correct variant through `as_file`, `as_dir`, or `as_symlink`.

State and persistence behavior: `FsBlob` is an in-memory typed owner. Persistence is delegated to the contained typed blob. Async drop flushes directory dirty state through `DirBlob` but file/symlink drops mostly delegate base drop.

Dependencies and integration points: central type returned by `FsBlobStore` and stored inside `ConcurrentFsBlobStore` cache.

Risks: type mismatch accessors return generic anyhow errors. Directory async drop can fail because it performs writeback, so cache drop paths must handle errors. Comments suggest possible ownership refactoring.

Test signals: parse dispatch tests, wrong-type accessor tests, directory writeback-on-drop tests, and invalid header tests are important.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/symlink_blob.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/symlink_blob.rs

Purpose: Represents symlink blobs whose data payload is the target string.

Important APIs/types/functions: `create_blob` writes a `BlobType::Symlink` blob with target bytes. `target` reads all data and decodes UTF-8. Other APIs expose blob id, parent, parent update, removal, `lstat_size`, `flush`, block enumeration, and test helpers.

Control flow: reading the target loads the full base data payload every time and converts it to `String`. Size is recomputed from the decoded target string length. Removal delegates directly to `BaseBlob::remove`.

State and persistence behavior: symlink target is persisted as UTF-8 bytes after the common header; ownership/timestamps live in parent directory entries. There is no target cache.

Dependencies and integration points: constructed by `FsBlobStore`, parsed by `FsBlob`, and referenced by directory entries with `EntryType::Symlink`.

Risks: invalid UTF-8 in the blob fails target reads and lstat size. Very large symlink data is read entirely; a TODO notes the lack of max-size enforcement. `lstat_size` rereads the target.

Test signals: tests should cover UTF-8 failure, target round-trip, lstat size, parent update, and remove behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/symlink_blob.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/mod.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/mod.rs

Purpose: `FsBlobStore` wraps a raw `BlobStore` and exposes typed filesystem blobs.

Important APIs/types/functions: `new`, create root/file/dir/symlink blob, `load`, `num_blocks`, space and logical-block-size queries, `remove_by_id`, `into_inner_blobstore`, test-only cache clearing, `flush_if_cached`, and `FlushBehavior`.

Control flow: create methods call the typed blob constructors and optionally flush immediately. `load` asks the raw blobstore for a blob and parses it into `FsBlob`. `remove_by_id` and flush/cache methods delegate to the underlying store.

State and persistence behavior: owns an `AsyncDropGuard<B>` raw store. Typed creation writes fsblob headers and data into the raw store. `FlushBehavior::DontFlush` allows batching but creates durability windows.

Dependencies and integration points: used directly by non-concurrent callers and wrapped by `ConcurrentFsBlobStore` for shared access. Re-exports most typed blob API.

Risks: `num_blocks` calls `blobstore.num_nodes()`, so naming may be confusing depending on lower-store semantics. Root creation errors if the id exists. No parent-chain validation occurs on load.

Test signals: important tests include create/load/remove for all blob types, flush behavior, invalid blob parse, root id collision, and cache flushing.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/lib.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/lib.rs

Purpose: Crate root for CryFS fsblobstore.

Important APIs/types/functions: declares `concurrentfsblobstore`, `fsblobstore`, and `utils`; re-exports `ConcurrentFsBlob`, `ConcurrentFsBlobStore`, `LoadedBlobGuard`, `RequestRemovalResult`, `BlobType`, directory/file/symlink blob types, errors, `FlushBehavior`, and fs uid/gid/mode types.

Control flow: no runtime control flow. It defines the public API surface for typed blob storage.

State and persistence behavior: no state here. Exported modules implement the fsblob binary format and concurrent cache.

Dependencies and integration points: downstream CryFS filesystem layers import this crate instead of reaching into private module trees.

Risks: broad re-exports make internal error and guard types part of the public contract. Future refactors need compatibility care.

Test signals: public API compile tests and downstream crate builds are the primary signal for this file.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/utils/fs_types.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/utils/fs_types.rs

Purpose: Defines local filesystem scalar types used by fsblobstore without depending on `cryfs-rustfs`.

Important APIs/types/functions: `Uid` and `Gid` are `u32` newtypes with binary read/write and conversions. `Mode` is a `u32` bitmask newtype with derive-more bit operators, constructors, node-kind flag checks, and const helpers for setting file/dir/symlink and permission bits.

Control flow: no complex flow. Methods create modified copies or query bit flags.

State and persistence behavior: these values serialize via `binrw` inside directory entries. Mode bit constants include POSIX type bits and basic user/group/other rwx permissions.

Dependencies and integration points: used by `DirEntry`, `DirBlob`, and typed blob APIs. A TODO notes possible unification with rustfs types while avoiding unwanted crate dependencies.

Risks: only add/with helpers are present, not remove helpers for all bits. Incorrect mode construction can fail `DirEntry` validation. Duplicating rustfs types risks semantic drift.

Test signals: tests should cover bit operations, binary round trips, and compatibility with rustfs `Mode` values used at integration boundaries.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/utils/fs_types.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/utils/mod.rs -->
# sources/security-integrity/cryfs/crates/fsblobstore/src/utils/mod.rs

Purpose: Utility module root for fsblobstore.

Important APIs/types/functions: exposes `fs_types`.

Control flow: none.

State and persistence behavior: none directly; `fs_types` values are serialized in directory entries.

Dependencies and integration points: imported by crate root and fsblob modules for uid/gid/mode support.

Risks: minimal. Re-export changes can affect downstream code paths that import utility types through this module.

Test signals: compile coverage plus `fs_types` tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/fsblobstore/src/utils/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/Cargo.toml -->
# sources/security-integrity/cryfs/crates/rustfs/Cargo.toml

Purpose: Cargo manifest for the `cryfs-rustfs` crate.

Important APIs/types/functions: declares crate metadata, dependencies for async FUSE integration, local CryFS utility/concurrent-store crates, `fuser` 0.17, a renamed `fuser_fusemt` 0.16 for `fuse_mt`, `fuse_mt`, `tokio`, `tokio-util`, `nix`, and examples `inmemory` and `passthrough`.

Control flow: feature flags select backend support: default enables `fuser`, optional `fuse_mt`, and `testutils` forwards test features to dependencies. macOS adds fuser ABI compatibility features.

State and persistence behavior: no runtime state. Dependency versions and features control compiled backend behavior and platform capabilities.

Dependencies and integration points: coordinates high-level, low-level, object-based APIs, tests, and example binaries. Comments explain the dual-fuser dependency caused by `fuse_mt` still using fuser 0.16.

Risks: TODOs note `fuser` should become optional for the feature, and `env_logger`/`nix` are mostly example dependencies. Version skew between fuser 0.17 and fuser 0.16 bridge must be handled carefully.

Test signals: `cargo test -p cryfs-rustfs --features testutils` and building both examples/backends are the main signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/device.rs -->
# sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/device.rs

Purpose: Implements an in-memory object-based filesystem device and root traversal.

Important APIs/types/functions: `RootDir::new`, `_node`, and `load_node` maintain and traverse the root directory. `InMemoryDevice::new` constructs the root. The `Device` impl supplies associated node types, `rootdir`, path-level `rename`, and placeholder `statfs`.

Control flow: `load_node` walks an absolute path component by component, requiring every intermediate node to be a directory. Rename splits old/new paths, loads parents, and either renames within one directory or locks source and target directories in pointer order to avoid deadlock.

State and persistence behavior: all state is process memory under `Arc<Mutex<DirInode>>`. There is no persistence and async drop is a no-op.

Dependencies and integration points: used by `examples/inmemory/main.rs` through `ObjectBasedFsAdapterLL`. Integrates dir/file/symlink node refs and `cryfs_utils::lock_in_ptr_order`.

Risks: rename blocks all overwrites even though POSIX allows some cases. `statfs` is `todo!()` and will panic if called. Many error semantics are TODO-level approximations.

Test signals: useful example tests should exercise lookup traversal, cross-directory rename deadlock avoidance, invalid root rename, and statfs behavior once implemented.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/device.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/dir.rs -->
# sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/dir.rs

Purpose: Implements in-memory directory inode state and the object-based `Dir` trait.

Important APIs/types/functions: private `DirInode` stores `NodeAttrs` and `HashMap<PathComponentBuf, InMemoryNodeRef>`. `InMemoryDirRef` wraps it in `Arc<Mutex<_>>` and exposes metadata, child lookup, setattr, rename, cloning, and inode access. The `Dir` impl handles lookup, rename/move, entries, create/remove directory, symlink, and file operations.

Control flow: directory mutations lock the inode mutex. Cross-directory moves lock two directories in pointer order. Entry creation checks occupied names before inserting. Directory listing maps stored node enum variants to `NodeKind`.

State and persistence behavior: entries and attributes are memory-only. Metadata size/link counts are simplistic; comments warn that exposing `entries_mut` could violate future invariants.

Dependencies and integration points: used by `InMemoryDevice`, `InMemoryNodeRef`, and file/symlink refs. It mirrors the object-based API contracts used by adapters.

Risks: POSIX overwrite behavior is incomplete. Mutex poisoning uses `unwrap`, so panics can cascade. Metadata timestamps and directory sizes are approximate.

Test signals: cover create/list/remove, duplicate names, same-dir and cross-dir rename, move overwrite rejection, and metadata updates.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/dir.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/file.rs -->
# sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/file.rs

Purpose: Implements in-memory file inode and open-file behavior.

Important APIs/types/functions: private `FileInode` stores metadata plus `Vec<u8>` data and maintains `metadata.num_bytes == data.len()`. `InMemoryFileRef` creates/clones/opens files and handles metadata changes. `InMemoryOpenFileRef` implements getattr, setattr, read, write, flush, and fsync.

Control flow: opening captures `OpenInFlags`. Reads reject write-only handles; writes and size-changing setattr reject read-only handles. Writes extend the vector with zeros when offset+data exceeds current length, then copies bytes into place.

State and persistence behavior: data and metadata live in memory under `Arc<Mutex<FileInode>>`; flush and fsync are no-ops.

Dependencies and integration points: used by in-memory dirs and nodes; exercises `object_based_api::File` and `OpenFile` contracts for backend tests/examples.

Risks: read computes `data.len() - offset` and can underflow/panic if offset exceeds file length. Several integer conversions unwrap. Timestamp maintenance is incomplete.

Test signals: tests should include read beyond EOF, sparse writes, read/write permission errors, truncate through setattr, and metadata size invariant checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/inode_metadata.rs -->
# sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/inode_metadata.rs

Purpose: Shared helper for mutating in-memory inode metadata.

Important APIs/types/functions: `setattr` updates optional mode, uid, gid, atime, mtime, and ctime fields on a mutable `NodeAttrs` and returns the new attrs.

Control flow: applies each optional argument independently; absent fields keep previous values.

State and persistence behavior: memory-only metadata mutation. Size changes are handled by callers before this helper.

Dependencies and integration points: called by in-memory dir, file, and symlink inode implementations.

Risks: callers decide ctime semantics; comments elsewhere note ctime/atime/mtime updates are incomplete.

Test signals: simple unit tests should verify every optional field and no-op behavior with all `None`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/inode_metadata.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/main.rs -->
# sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/main.rs

Purpose: Example binary that mounts the in-memory filesystem through the fuser backend.

Important APIs/types/functions: declares example modules, parses one mountdir argument, builds a Tokio runtime, constructs `InMemoryDevice` from request uid/gid, wraps it in `ObjectBasedFsAdapterLL`, and calls `backend::fuser::mount`.

Control flow: synchronous `main` initializes logging, validates arguments with `expect`/`assert`, then blocks on async mount until unmounted.

State and persistence behavior: filesystem contents are volatile and recreated at process start.

Dependencies and integration points: demonstrates object-based API to low-level adapter to fuser backend flow.

Risks: argument parsing is minimal, runtime `unwrap`s panic on failures, and no cancellation token is provided. Calls to unimplemented filesystem operations such as `statfs` may panic.

Test signals: build the example and smoke mount/unmount in an environment with FUSE support.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/node.rs -->
# sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/node.rs

Purpose: Implements the in-memory sum type for file, directory, and symlink nodes.

Important APIs/types/functions: `InMemoryNodeRef` variants wrap the concrete refs. `clone_ref` preserves shared inode ownership. The `Node` impl provides `as_file`, `as_dir`, `as_symlink`, `getattr`, and `setattr` dispatch.

Control flow: type conversions return type-specific errors where implemented. Metadata operations dispatch to the underlying ref and pass through optional size and timestamp changes.

State and persistence behavior: no state beyond cloned `Arc` refs to memory-only inodes.

Dependencies and integration points: central node type for `InMemoryDevice` and directory entries.

Risks: symlink-to-file conversion returns `UnknownError` instead of a precise error. Timestamp semantics are marked TODO. Size setattr validity depends on the target type implementation.

Test signals: type-dispatch tests should assert correct errors for wrong node kind and metadata propagation for each variant.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/symlink.rs -->
# sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/symlink.rs

Purpose: Implements in-memory symlink nodes.

Important APIs/types/functions: `SymlinkInode` stores metadata and target string. `InMemorySymlinkRef` supports creation, cloning, metadata, setattr, and target access. The `Symlink` trait impl returns the target.

Control flow: symlink read simply clones the stored target. Setattr rejects size changes and mutates metadata fields through the shared helper.

State and persistence behavior: target and attrs are held in an `Arc<Mutex<_>>` and never persisted.

Dependencies and integration points: used by in-memory directories and node dispatch; complements file and dir implementations.

Risks: size changes assert rather than returning an error. Metadata timestamps are approximate. Target is not validated beyond being a Rust string.

Test signals: cover target round-trip, wrong size setattr, clone sharing, and metadata updates.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/inmemory/symlink.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/device.rs -->
# sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/device.rs

Purpose: Implements an object-based device that maps filesystem operations onto a real base directory.

Important APIs/types/functions: `PassthroughDevice::new` stores `basedir`; `apply_basedir` joins requested absolute paths. `Device` impl provides rootdir, optimized lookup, rename, and statfs.

Control flow: lookup and rename translate CryFS absolute paths into host paths. `statfs` runs blocking `nix::sys::statfs::statfs` on a blocking thread and converts platform-specific values to `Statfs`.

State and persistence behavior: persistent state is the host filesystem under `basedir`; this object stores only the base path.

Dependencies and integration points: used by the passthrough example main with `ObjectBasedFsAdapterLL`; integrates `tokio::fs`, `nix`, and path wrappers.

Risks: base-path joining must prevent escaping through invalid path components; safety relies on CryFS path types. Platform-specific statfs conversion uses unwraps and a macOS filename-length guess.

Test signals: smoke tests should check root lookup, rename, statfs, and path containment under the base directory.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/device.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/dir.rs -->
# sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/dir.rs

Purpose: Implements passthrough directory operations against the host filesystem.

Important APIs/types/functions: `PassthroughDir` stores an absolute path and implements `Dir`: lookup, rename/move, entries, mkdir, rmdir, symlink, unlink, create-and-open file, and fsync. `convert_mode` adapts `Mode` to Unix `mode_t`.

Control flow: most operations clone the directory path and append a component. Unix-specific ownership and creation operations run in `spawn_blocking` when using `nix` or `std::fs`. Directory listing reads `tokio::fs::read_dir`, converts names to `PathComponent`, and maps file types.

State and persistence behavior: changes are immediate host filesystem mutations. `fsync` opens the directory and calls `sync_all` or `sync_data`.

Dependencies and integration points: integrates `PassthroughNode`, `PassthroughOpenFile`, `PassthroughSymlink`, error conversion helpers, and metadata conversion.

Risks: unknown file types panic. Some unwraps are present in mode conversion. TODOs question directory fsync correctness, dot-entry filtering, and platform portability.

Test signals: tests should cover entry listing of files/dirs/symlinks, create/remove operations, duplicate errors, fsync, and behavior with special files.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/dir.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/errors.rs -->
# sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/errors.rs

Purpose: Provides adapters from `std::io::Result` and `nix::Result` to rustfs `FsResult`.

Important APIs/types/functions: `IoResultExt<T>::map_error` maps IO errors through `FsError::from_io_error`; `NixResultExt<T>::map_error` maps nix errno through `FsError::from_nix_error`.

Control flow: no complex flow; both traits transform the error side of `Result`.

State and persistence behavior: none.

Dependencies and integration points: used throughout passthrough device, dir, file, node, symlink, openfile, and utils modules.

Risks: conversion fidelity depends on `FsError` mappings. Call sites that need context lose the original path unless they wrap errors separately.

Test signals: unit tests should verify representative errno mappings such as ENOENT, EEXIST, EACCES, ENOTDIR, and EISDIR.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/file.rs -->
# sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/file.rs

Purpose: Implements passthrough file node opening.

Important APIs/types/functions: `PassthroughFile::new` stores a path. The `File` impl consumes the async-drop guard, opens the host file with read/write options derived from `OpenInFlags`, and returns `PassthroughOpenFile`.

Control flow: `into_open` unwraps the guard without dropping, builds `tokio::fs::OpenOptions`, maps read/write/readwrite flags, opens the path, and wraps the file handle.

State and persistence behavior: no in-memory file data; persistence is the host file. Async drop is a no-op.

Dependencies and integration points: used by `PassthroughNode::as_file` and directory create/open paths.

Risks: opening does not pass through every kernel open flag such as append/truncate; it only models access mode. `unsafe_into_inner_dont_drop` is deliberate but must remain paired with no resource cleanup in the wrapper.

Test signals: cover open modes, permission errors, and read/write attempts through `PassthroughOpenFile`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/main.rs -->
# sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/main.rs

Purpose: Example binary that mounts a host-directory passthrough filesystem.

Important APIs/types/functions: parses `basedir` and `mountdir`, constructs `PassthroughDevice`, wraps it in `ObjectBasedFsAdapterLL`, and mounts through `backend::fuser::mount`.

Control flow: synchronous `main` initializes logging, validates two arguments, builds a multi-thread Tokio runtime, and blocks on mount until unmounted.

State and persistence behavior: all changes persist in the provided base directory.

Dependencies and integration points: demonstrates passthrough object API over the low-level fuser backend.

Risks: argument parsing and path conversion use `expect`/`unwrap`; malformed paths panic. No cancellation token is supplied. Running this example can modify/delete real files under `basedir`.

Test signals: build plus controlled temporary-directory mount tests are appropriate.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/node.rs -->
# sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/node.rs

Purpose: Implements passthrough node metadata and type conversion operations.

Important APIs/types/functions: `PassthroughNode::new`, private `chmod`, `chown`, `truncate`, and `utimens`, and the `Node` impl for type conversions, `getattr`, `setattr`, and test-only fsync.

Control flow: `getattr` uses `symlink_metadata` to avoid following symlinks. `setattr` applies chmod, chown, truncate, and utimens in sequence, then returns fresh attrs. Unix metadata operations that can block use `spawn_blocking`.

State and persistence behavior: mutates host filesystem metadata and file size. No additional state is stored.

Dependencies and integration points: type conversion returns passthrough dir/file/symlink wrappers. Uses error extensions and metadata/time conversion utilities.

Risks: `chmod` builds `self.path.clone().push_all(&self.path)`, which appears to duplicate the path and is likely a bug. `as_file/as_dir/as_symlink` TODOs note they do not validate actual node type. ctime setting asserts.

Test signals: tests should catch chmod path handling, wrong-type conversions, symlink-no-follow metadata behavior, truncate, chown, and utimens.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/openfile.rs -->
# sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/openfile.rs

Purpose: Implements operations on an opened passthrough file handle.

Important APIs/types/functions: `PassthroughOpenFile::new` wraps `tokio::fs::File`. Helpers implement chmod, fchown, truncate, and futimens-style timestamp updates. `OpenFile` methods provide getattr, setattr, read, write, flush, and fsync.

Control flow: metadata operations act on the open file descriptor where possible. Reads and writes seek/read/write the host file through Tokio APIs. Flush and fsync delegate to file sync methods based on datasync.

State and persistence behavior: persistent state is the host file content and metadata. The wrapper owns only the open file handle.

Dependencies and integration points: returned by `PassthroughFile::into_open` and directory create/open. Uses `nix`, fd traits, and utility conversions.

Risks: descriptor cloning for fchown has overhead. Offset conversion and seek behavior need careful EOF/error handling. Host filesystem semantics may differ from object API expectations.

Test signals: cover read/write offsets, truncate through open handle, sync modes, setattr ownership/mode changes, and permission errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/openfile.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/symlink.rs -->
# sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/symlink.rs

Purpose: Implements passthrough symlink reads.

Important APIs/types/functions: `PassthroughSymlink::new` stores a path. The `Symlink` impl reads the host symlink target and converts it to UTF-8 string.

Control flow: `target` calls `tokio::fs::read_link`, then `into_os_string().into_string()`; invalid Unicode becomes `FsError::CorruptedFilesystem`.

State and persistence behavior: no state beyond path. Target is stored by the host filesystem.

Dependencies and integration points: returned by `PassthroughNode::as_symlink` and symlink creation in `PassthroughDir`.

Risks: non-UTF-8 symlink targets are rejected even though Unix permits them. No validation in `as_symlink` means callers can construct this for non-symlinks until read fails.

Test signals: cover relative and absolute targets, non-UTF-8 targets on Unix, and wrong-node-type behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/symlink.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/utils.rs -->
# sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/utils.rs

Purpose: Shared conversion helpers for passthrough metadata and timestamps.

Important APIs/types/functions: `convert_metadata` maps `std::fs::Metadata` to `NodeAttrs`, deriving mode, uid/gid, size, block count, and times. `convert_timespec` maps `SystemTime` to nix `TimeSpec`.

Control flow: metadata conversion inspects Unix metadata extensions and file type bits. Time conversion handles `SystemTime` relative to Unix epoch.

State and persistence behavior: no state; converts host filesystem state into rustfs common structs.

Dependencies and integration points: used by passthrough dir, node, symlink, and openfile code.

Risks: platform assumptions are Unix-heavy. Time before epoch and nanosecond conversion need careful error handling depending on implementation. Mode mapping must preserve node-kind bits expected by rustfs.

Test signals: tests should cover regular file, dir, symlink metadata, block counts, permissions, uid/gid, and pre/post-epoch timestamps.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/backend/fuse_mt/backend_adapter.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/backend/fuse_mt/backend_adapter.rs

Purpose: Adapts the high-level path-based `AsyncFilesystem` API to the synchronous `fuse_mt::FilesystemMT` trait.

Important APIs/types/functions: `BackendAdapter` stores `Arc<RwLock<AsyncDropGuard<Fs>>>` plus a Tokio runtime handle. `run_async` synchronously drives async filesystem methods and maps `FsError` to libc errno. The `FilesystemMT` impl covers init/destroy, metadata, node creation/removal, rename/link, open/read/write, flush/release/fsync, directory operations, statfs, xattrs, access, and create. Helpers convert attrs, node kinds, flags, paths, file handles, request info, statfs, and read callbacks.

Control flow: each FUSE call parses kernel inputs into CryFS path and scalar types, acquires a read guard for normal operations or write guard for destroy, awaits the high-level API, then converts replies. `read` uses a callback adapter because fuse_mt expects borrowed data through `ResultSlice`.

State and persistence behavior: adapter state is just the guarded filesystem object. `destroy` calls filesystem destroy and async drop. `Drop` safe-panics if destroy was not called first.

Dependencies and integration points: used by `backend/fuse_mt/mount.rs`; bridges `fuse_mt`, `fuser_fusemt`, `AsyncFilesystem`, and common rustfs types.

Risks: TODOs question concurrent `runtime.block_on`, FUSE precondition checking, symlink behavior, and incomplete flag support. Several conversions unwrap on size/handle assumptions. Invalid xattr UTF-8 maps to broad errors.

Test signals: backend integration tests should exercise all operations through a mounted filesystem, especially destroy-after-open, xattrs, read callback behavior, and flag parsing.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/backend/fuse_mt/backend_adapter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/backend/fuse_mt/mod.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/backend/fuse_mt/mod.rs

Purpose: Public facade for the legacy `fuse_mt` backend.

Important APIs/types/functions: declares private `backend_adapter` and `mount`, re-exports `mount` and `spawn_mount`, re-exports shared fuser config/mount option/session ACL types, and defines backend-specific `RunningFilesystem`.

Control flow: none directly.

State and persistence behavior: no state; mounted sessions are returned by `mount.rs`.

Dependencies and integration points: only compiled with the `fuse_mt` feature; lets users mount a high-level `AsyncFilesystem`.

Risks: the backend depends on a compatibility bridge to fuser 0.16. API users should prefer the newer fuser backend where possible, matching comments in the adapter.

Test signals: feature-gated build and mount smoke tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/backend/fuse_mt/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/backend/fuse_mt/mount.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/backend/fuse_mt/mount.rs

Purpose: Mount orchestration for the `fuse_mt` backend.

Important APIs/types/functions: `mount` spawns the backend, invokes the success callback, optionally installs unmount trigger, and blocks until unmounted. `spawn_mount` builds `BackendAdapter`, wraps it in `FuseMT`, translates fuser 0.17 `Config` to fuser 0.16 options, and calls `fuser_fusemt::spawn_mount2`. Helpers choose thread count and convert mount options.

Control flow: on spawn failure it manually calls `destroy` and async-drops the backend because fuser will not call destroy. On success it drops the internal arc and returns `RunningFilesystem`.

State and persistence behavior: state is the background FUSE session and guarded filesystem. No persistence beyond delegated filesystem.

Dependencies and integration points: used by `backend/fuse_mt/mod.rs`; depends on `RunningFilesystem`, `BackendAdapter`, `FuseMT`, and cancellation tokens.

Risks: manual cleanup path uses `unwrap` during async drop. Thread count defaults to available parallelism or 2. Config translation must stay aligned with fuser versions.

Test signals: mount failure cleanup tests, option translation tests, and cancellation-trigger unmount tests are valuable.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/backend/fuse_mt/mount.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/backend/fuser/backend_adapter.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/backend/fuser/backend_adapter.rs

Purpose: Adapts the low-level inode-based `AsyncFilesystemLL` API to `fuser::Filesystem`.

Important APIs/types/functions: `BackendAdapter` stores a guarded filesystem and runtime. It provides many `run_async_reply_*` helpers for spawning async operations and replying with fuser reply types. The `Filesystem` impl covers init/destroy, lookup, forget, getattr/setattr, readlink, mknod/mkdir/unlink/rmdir/symlink/rename/link, open/read/write, flush/release/fsync, opendir/readdir/readdirplus/releasedir/fsyncdir, statfs, xattrs, access, create, locks, bmap, ioctl, fallocate, lseek, copy_file_range, and macOS extensions.

Control flow: most kernel callbacks clone request info and owned names/data, parse inode/file-handle/path-component inputs, spawn an async task on the provided runtime, call the low-level API, and complete the provided reply. Init/destroy use `run_blocking`, which runs on a short-lived thread if already inside a Tokio runtime to avoid nested `block_on` panics.

State and persistence behavior: adapter state is the async-drop guarded filesystem. Destroy invokes fs destroy and async drop; later operations detect dropped state and return `FilesystemDestroyed`.

Dependencies and integration points: used by `backend/fuser/mount.rs`; integrates fuser 0.17 with rustfs low-level API and directory reply traits.

Risks: many conversions use unwrap for size and signed/unsigned offsets. `OpenOutFlags` conversion is not implemented. Comments note inode generation uniqueness requirements for NFS, FUSE API drift, and copy minimization. All reply paths must reply exactly once.

Test signals: rustfs tests include fuser runner utilities. High-value tests cover every reply helper, dropped-filesystem operations, xattr size/data branches, directory full replies, lock/ioctl/fallocate paths, and init/destroy inside Tokio.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/backend/fuser/backend_adapter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/backend/fuser/mod.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/backend/fuser/mod.rs

Purpose: Public facade for the fuser backend.

Important APIs/types/functions: declares private `backend_adapter` and `mount`, re-exports `mount` and `spawn_mount`, re-exports `fuser::{Config, MountOption, SessionACL}`, and defines backend-specific `RunningFilesystem`.

Control flow: none directly.

State and persistence behavior: no state; runtime session state is in `RunningFilesystem` returned by mount functions.

Dependencies and integration points: primary backend used by examples and tests for low-level rustfs filesystems.

Risks: re-exporting fuser config types couples public API to fuser 0.17. Backend behavior depends on feature selection in Cargo.

Test signals: default-feature build and fuser mount tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/backend/fuser/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/backend/fuser/mount.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/backend/fuser/mount.rs

Purpose: Mount orchestration for the primary fuser backend.

Important APIs/types/functions: `mount` wraps `spawn_mount`, invokes a success callback, optionally wires a `CancellationToken` unmount trigger, and blocks until unmount. `spawn_mount` creates `BackendAdapter`, calls `fuser::spawn_mount2`, and returns `RunningFilesystem`.

Control flow: as in fuse_mt, the code keeps an internal arc so failed mount setup can manually destroy and async-drop the filesystem. Successful spawn transfers lifecycle to fuser destroy/drop handling.

State and persistence behavior: session state is held by fuser's background session; filesystem persistence is delegated to `AsyncFilesystemLL`.

Dependencies and integration points: used by examples and backend facade; depends on `RunningFilesystem`, `BackendAdapter`, fuser config, and cancellation tokens.

Risks: mount failure cleanup has to mirror normal destroy exactly. Async drop failure handling uses unwrap in the failure path. `mount` blocks the caller after success until unmounted.

Test signals: mount failure cleanup, success callback ordering, cancellation-trigger unmount, and smoke operations through a mounted filesystem.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/backend/fuser/mount.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/backend/mod.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/backend/mod.rs

Purpose: Backend module root for rustfs.

Important APIs/types/functions: declares `running_filesystem`, re-exports `BackgroundSession` and generic `RunningFilesystem`, and conditionally exposes `fuse_mt` and `fuser` backend modules according to features.

Control flow: none directly; feature gates determine compiled backend surface.

State and persistence behavior: no state here. `RunningFilesystem` owns background sessions and unmount behavior in its own module.

Dependencies and integration points: central import point for example binaries and downstream users selecting a backend.

Risks: feature-gated exports mean downstream code must align Cargo features with imports. Both backends share type names, so callers should import through the chosen submodule.

Test signals: build matrix for default, `--no-default-features`, `--features fuser`, and `--features fuse_mt`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/backend/mod.rs -->
