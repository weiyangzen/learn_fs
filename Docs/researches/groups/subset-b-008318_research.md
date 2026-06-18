# subset-b-008318 research

This grouped report covers the listed `cryfs/crates/rustfs` source files. Each section is source-tree aligned and bounded by reconciliation markers so it can be split into the required per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/backend/running_filesystem.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/backend/running_filesystem.rs

Purpose: wraps a mounted FUSE background session in an RAII object that can unmount explicitly, on process exit signals, on a cancellation trigger, or during drop. It abstracts over both supported backend session types via `BackgroundSession`.

Important APIs: `BackgroundSession::join` and `is_finished`; `RunningFilesystem::new`, `unmount_join`, `unmount_on_trigger`, `block_until_unmounted`, and `Drop`. Feature-gated impls adapt `fuser_fusemt::BackgroundSession` and `fuser::BackgroundSession`; the latter uses `umount_and_join`.

Control flow and state: the session is stored as `Arc<Mutex<Option<BS>>>`. Every unmount path takes the option, making unmount idempotent and preventing double joins. `AtExitHandler` owns a closure that joins during SIGTERM/SIGINT/SIGQUIT handling. `unmount_on_trigger` spawns a Tokio task waiting on `CancellationToken`. `block_until_unmounted` polls `is_finished` every 100 ms.

Dependencies and integration: used by backend mount/spawn paths and tests. It depends on `cryfs_utils::at_exit`, `tokio_util`, logging, and fuser session APIs.

Risks and tests: busy polling is noted as a TODO. Drop logs unmount errors instead of panicking, while tests use explicit `unmount_join` to fail loudly. The mutex unwraps assume no poisoning.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/backend/running_filesystem.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/atime_update_behavior.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/atime_update_behavior.rs

Purpose: models mount-style access-time policies for files, symlinks, and directories. It is serializable and can be used by filesystems to decide whether a read should update atime.

Important APIs: `AtimeUpdateBehavior` variants are `Noatime`, `Strictatime`, `Relatime`, `NodiratimeRelatime`, and `NodiratimeStrictatime`. The public decision methods are `should_update_atime_on_file_or_symlink_read` and `should_update_atime_on_directory_read`.

Control flow and state: the type is stateless. Both decision functions match on the enum and optionally call private `relatime`, which updates when old atime is older than mtime or older than 24 hours relative to the candidate new atime.

Dependencies and integration: uses `serde` for config persistence and `SystemTime`/`Duration`. It is exported through `common/mod.rs` and `lib.rs`.

Risks and tests: there is a TODO for tests. The comment mentions ctime, but the implementation only receives and compares mtime, so ctime-driven relatime behavior is absent. Subtracting 24 hours from `new_atime` assumes the timestamp is representable.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/atime_update_behavior.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/callback.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/callback.rs

Purpose: provides a generic callback pattern used by read-like FUSE APIs to force implementations to call back with borrowed data while returning the callback's result.

Important APIs: `Callback<T, R>::call(self, T) -> R` is the trait. `CallbackImpl<T, F>` wraps a `FnOnce(T)` and implements `Callback<T, ()>`.

Control flow and state: `CallbackImpl::new` stores the closure and a `PhantomData<T>`. `call` consumes the callback, preserving one-shot behavior and avoiding lifetime escape for borrowed buffers. The generic return type makes trait implementors unable to synthesize `R` without calling the callback.

Dependencies and integration: used in high-level and low-level `read` and `readlink` signatures so adapters can hand temporary byte or string slices to backend-specific reply objects. Re-exported from `lib.rs`.

Risks and tests: no runtime state and little failure surface. The pattern relies on type discipline; callers needing non-unit return values must implement their own callback type because `CallbackImpl` only covers `()`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/callback.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/dir_entry.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/dir_entry.rs

Purpose: defines directory listing values shared by object and path adapters.

Important APIs: `DirEntry { name: PathComponentBuf, kind: NodeKind }` describes a real child. `DirEntryOrReference` wraps either `Entry`, `SelfReference`, or `ParentReference`.

Control flow and state: these are plain data structures. The high-level adapter synthesizes `.` and `..` as `SelfReference` and `ParentReference`; the low-level adapter writes those directly into reply buffers before ordinary entries.

Dependencies and integration: depends on `cryfs_utils::path::PathComponentBuf` and local `NodeKind`. `Dir::entries` returns `Vec<DirEntry>`, high-level `readdir` returns an iterator of `DirEntryOrReference`, and low-level `readdir` converts `DirEntry` into FUSE reply entries.

Risks and tests: correctness depends on `NodeKind` being accurate for each child. `DirEntryOrReference` avoids representing `.` and `..` as names, which reduces path-component validation risk.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/dir_entry.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/error.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/error.rs

Purpose: central error taxonomy for filesystem operations, plus the `FsResult<T>` alias.

Important APIs: `FsError` covers custom errno values, not implemented, internal/corruption errors, descriptor misuse, node existence/type errors, overwrite errors, invalid path/operation, xattr buffer issues, and unsupported file type. `error_code` maps each error to libc errno. `From<Never>` converts unreachable lockable errors.

Control flow and state: errors are cloneable. Internal errors are stored in `Arc<anyhow::Error>` to preserve clone behavior. The adapters return `FsError` and backend adapters map to OS errors for FUSE replies.

Dependencies and integration: depends on `thiserror`, `libc`, `lockable::Never`, and `FileHandle`. Used by every trait and utility in the crate, including async drop bounds.

Risks and tests: mapping is security relevant because it controls user-visible POSIX behavior. `UnknownError` and `Custom` are broad escape hatches. TODOs call out the need for function-specific errors and richer context. `mkdir` tests verify several mappings such as ENOSYS, EEXIST, ENOENT, ENOTDIR, and EINVAL through the mounted backend.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/file_handle.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/file_handle.rs

Purpose: typed nonzero FUSE file-handle wrapper used for open files and directory handles.

Important APIs: `FileHandle { handle: NonZeroU64 }`, `from_const`, derived `From`/`Into`, display, ordering, hashing, and `HandleTrait` implementation. `MIN` is 1 and `MAX` is `u64::MAX`.

Control flow and state: `incremented` constructs the next nonzero value. `range` iterates the numeric range and unwraps `NonZeroU64`; the range starts from valid nonzero handles.

Dependencies and integration: used by `OpenFileList`, `DirCache` through `OpenDirHandle`, high/low API response structs, and descriptor-related errors. Re-exported as a public common type.

Risks and tests: the type prevents zero handles, but several call sites unwrap numeric conversions and assume no overflow. `HandlePool` asserts before incrementing past `MAX`, so exhaustion panics rather than returning an error.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/file_handle.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/gid.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/gid.rs

Purpose: lightweight typed group identifier wrapper.

Important APIs: `Gid(u32)` with `Display`, `From`, and `Into`.

Control flow and state: no behavior beyond conversion and formatting. It preserves type distinction between group IDs and raw integers.

Dependencies and integration: used in `RequestInfo`, `NodeAttrs`, object trait creation/setattr methods, and `MaybeInitializedFs` initialization. Publicly re-exported.

Risks and tests: no validation of platform-specific gid ranges beyond `u32`. Test helpers assert request gid values when checking FUSE request propagation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/gid.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/handles/handle_map.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/handles/handle_map.rs

Purpose: stores async-droppable objects by generated handles, coupling a `HandlePool` with an async-drop hash map.

Important APIs: `HandleMap::new`, `add`, `remove`, `get`, feature-gated `iter`, and `AsyncDrop`.

Control flow and state: `add` acquires a handle with generation, inserts the object by bare handle, and returns `HandleWithGeneration`. `remove` deletes the object and releases the handle for future reuse with incremented generation. `get` returns an optional guard reference. `AsyncDrop` delegates to the inner `AsyncDropHashMap`.

Dependencies and integration: used by `OpenFileList` and `DirCache`. Depends on `HandlePool`, `HandleWithGeneration`, `HandleTrait`, `AsyncDropGuard`, and `FsError`.

Risks and tests: duplicate insert and missing remove panic. The map keys only by handle, not generation, so callers must not use stale handles after release; generation is returned for diagnostics and inode replies but not validated here. TODO suggests a slab/vector optimization and tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/handles/handle_map.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/handles/handle_pool.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/handles/handle_pool.rs

Purpose: allocates, releases, and optionally reserves typed handles with generation counters.

Important APIs: `HandlePool::new`, `acquire`, `acquire_specific`, `try_acquire_specific`, `release`, `undo_acquire`, and `lookup`.

Control flow and state: it tracks `in_use_handles: HashMap<Handle, u64>`, `released_handles: Vec<HandleWithGeneration<Handle>>`, and `next_handle`. `acquire` prefers recycled handles, otherwise returns `next_handle` and advances it. `try_acquire_specific` can jump forward, releasing skipped handles into the free list. `release` increments generation; `undo_acquire` returns a handle without incrementing generation for failed transactional inserts.

Dependencies and integration: generic over `HandleTrait`. Used by `HandleMap` and `HandleForest`, making it foundational for file handles and inode numbers.

Risks and tests: several invariant violations panic: releasing unused handles, exhausting handle range, generation overflow. Released handles are LIFO, which is fine but may make reuse patterns surprising. TODO calls for tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/handles/handle_pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/handles/handle_trait.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/handles/handle_trait.rs

Purpose: common interface for handle-like numeric wrapper types usable by the handle pool, map, and forest.

Important APIs: associated constants `MIN` and `MAX`, plus `incremented` and `range(begin, end)`.

Control flow and state: the trait is behavior-only and requires clone, equality, ordering, hashing, and debug. Concrete implementations are `FileHandle`, `InodeNumber`, and `OpenDirHandle`.

Dependencies and integration: keeps handle utilities generic without relying on unstable `std::iter::Step`.

Risks and tests: correctness of allocation depends on each implementation providing monotonic `incremented` and exclusive-end `range`. The parameter name typo `end_exclusve` is cosmetic.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/handles/handle_trait.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/handles/handle_with_generation.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/handles/handle_with_generation.rs

Purpose: couples a handle value with a generation counter.

Important APIs: `HandleWithGeneration<Handle> { handle, generation }`, clone/copy/equality/hash/debug/display.

Control flow and state: plain data. Display formats as `handle.generation`, useful in logs and FUSE reply debugging.

Dependencies and integration: returned by `HandlePool`, `HandleMap`, `InodeList`, and reply structs. Generation increases when a handle is released and later reused.

Risks and tests: generation does not enforce stale-handle rejection by itself because maps generally key by bare handle. It is most useful where the kernel or tests track inode lookup generations.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/handles/handle_with_generation.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/handles/mod.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/handles/mod.rs

Purpose: module facade for generic handle utilities.

Important APIs: conditionally declares `handle_pool` and `handle_map` for FUSE-enabled builds, always declares `handle_with_generation` and `handle_trait`, and re-exports `HandlePool`, `HandleMap`, `HandleWithGeneration`, and `HandleTrait`.

Control flow and state: no runtime behavior. Feature gating keeps handle map/pool out when neither backend is built.

Dependencies and integration: imported by `common/mod.rs`, then re-exported through the crate root.

Risks and tests: public surface varies by feature flags, so downstream code must enable `fuser` or `fuse_mt` when using pool/map types.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/handles/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/inode_number.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/inode_number.rs

Purpose: typed nonzero inode number wrapper.

Important APIs: `InodeNumber { inode: NonZeroU64 }`, `from_const`, conversions, display, ordering, hashing, and `HandleTrait`.

Control flow and state: like `FileHandle`, it provides monotonic increment and range iteration over nonzero values.

Dependencies and integration: used by low-level API replies, inode list, handle forest, tests, and mock helpers. Constants such as `FUSE_ROOT_ID` and `DUMMY_INO` are built from it.

Risks and tests: invalid zero values are unrepresentable. Overflow and conversion assumptions are handled by assertions/unwraps in callers. Stable inode behavior depends on `InodeList`, not this wrapper alone.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/inode_number.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/mod.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/mod.rs

Purpose: central export module for shared RustFS types.

Important APIs: declares and re-exports typed IDs, errors, mode, attributes, byte counts, flags, stats, callbacks, request info, directory entries, atime behavior, and handle utilities. Feature gates expose handle pools and file handles only when FUSE backends are active.

Control flow and state: no runtime behavior. It determines which common types are visible to `lib.rs` and internal modules.

Dependencies and integration: every API layer imports from this module. `lib.rs` publicly re-exports most of these types for users implementing filesystems.

Risks and tests: feature-gated exports can produce API differences across builds. The module is source-tree alignment glue; mistakes here become public API breakage.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/mode.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/mode.rs

Purpose: typed POSIX mode wrapper combining file-type bits and permission bits.

Important APIs: `Mode(u32)` with constants for file types and rwx permissions, `default_const`, `as_u32`, node-kind predicates/conversion, flag add/remove methods, `BitAnd`, `BitOr`, `Not`, `Display`, and custom `Debug`.

Control flow and state: immutable value object. File-type helpers clear previous type bits before adding dir/file/symlink flags, preventing mixed type flags when using provided methods. Permission methods OR or AND bits.

Dependencies and integration: used in `NodeAttrs`, create/mkdir/mknod/setattr/open APIs, tests, and backend adapters. `mkdir` tests verify directory flag behavior and umask interaction.

Risks and tests: direct `From<u32>` can construct inconsistent modes; callers need to use helpers or validate. Debug formatting can aid tests. Several TODOs ask for broader mode semantics.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/mode.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/node_attrs.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/node_attrs.rs

Purpose: shared file metadata struct.

Important APIs: `NodeAttrs` fields include `mode`, `uid`, `gid`, `num_bytes`, optional `num_blocks`, `atime`, `mtime`, `ctime`, and `nlink`. A helper formats timestamps for custom `Debug`.

Control flow and state: plain copyable metadata. The debug derive hides raw `SystemTime` formatting behind human-readable `OffsetDateTime`.

Dependencies and integration: returned by object nodes, high-level `AttrResponse`, low-level `ReplyEntry`/`ReplyAttr`/`ReplyCreate`, and tests.

Risks and tests: no validation ensures mode and node kind agree. Optional block count lets backends omit block accounting. Test helpers construct deterministic-like metadata around `SystemTime::now`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/node_attrs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/node_kind.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/node_kind.rs

Purpose: compact enum for directory entry kind.

Important APIs: `NodeKind::{Dir, File, Symlink}`.

Control flow and state: stateless enum used for listing and mode classification.

Dependencies and integration: `Mode::node_kind` returns this value; `DirEntry` stores it; tests parameterize over it.

Risks and tests: special files/devices are not represented here despite object API having `Device` and high-level `mknod`; this constrains directory listing expressiveness.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/node_kind.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/num_bytes.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/num_bytes.rs

Purpose: typed byte-count and offset wrapper.

Important APIs: `NumBytes(u64)` with display/from/into, `ZERO`, conversions to `usize`, `as_usize`, `checked_add`, and `Sub`.

Control flow and state: immutable numeric wrapper. `as_usize` and `TryFrom<NumBytes> for usize` return `FsError::InvalidOperation` when the value does not fit.

Dependencies and integration: used for file size, offsets, read/write lengths, xattr sizes, block sizes, and stat structures.

Risks and tests: `Sub` directly subtracts and will panic on underflow in debug builds or wrap depending on compilation settings if unchecked. Several callers unwrap conversions from `usize` to `u64`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/num_bytes.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/open_in_flags.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/open_in_flags.rs

Purpose: typed wrapper for incoming open flags.

Important APIs: `OpenInFlags { flags: i32 }`, derived `From`/`Into`, and `Debug`.

Control flow and state: no behavior; it preserves the raw FUSE/POSIX flags for filesystem implementations.

Dependencies and integration: used by high-level `open`, `create`, `opendir`, release methods, object `File::into_open`, and directory creation APIs.

Risks and tests: no bit-level helpers or validation, so callers must interpret flags manually. TODOs in adapters note missing wrappers for many raw flag parameters.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/open_in_flags.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/open_out_flags.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/open_out_flags.rs

Purpose: placeholder for outgoing open flags returned to FUSE.

Important APIs: empty `OpenOutFlags` struct with clone/copy/equality/hash/debug.

Control flow and state: carries no fields today. Adapters return `OpenOutFlags {}` for open/create/opendir.

Dependencies and integration: part of high-level and low-level reply structs.

Risks and tests: missing fields means direct I/O, keep-cache, nonseekable, and similar FUSE open response controls are not modeled yet.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/open_out_flags.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/request_info.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/request_info.rs

Purpose: captures caller identity for a filesystem request.

Important APIs: `RequestInfo { uid: Uid, gid: Gid, pid: u32 }`.

Control flow and state: copyable data passed through all high-level and low-level trait methods.

Dependencies and integration: initialized by backend adapters from FUSE request metadata and used by object adapters when creating nodes with caller ownership. Test helper `assert_request_info_is_correct` verifies propagation in mkdir tests.

Risks and tests: only uid/gid/pid are represented; groups, capabilities, and security labels are out of scope.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/request_info.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/statfs.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/statfs.rs

Purpose: filesystem capacity and capability statistics.

Important APIs: `Statfs` fields include total/free/available blocks and files, block size, max filename length, and fragment size.

Control flow and state: plain data returned by `statfs`.

Dependencies and integration: object `Device::statfs`, high-level `AsyncFilesystem::statfs`, and low-level `AsyncFilesystemLL::statfs` use this shared struct.

Risks and tests: no validation of consistency between block counts and sizes. Backends must map it correctly to FUSE statfs replies.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/statfs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/uid.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/common/uid.rs

Purpose: lightweight typed user identifier wrapper.

Important APIs: `Uid(u32)` with `Display`, `From`, and `Into`.

Control flow and state: no behavior beyond conversion and formatting.

Dependencies and integration: used in `RequestInfo`, `NodeAttrs`, object creation and setattr methods, and filesystem initialization. Re-exported publicly.

State and persistence behavior: the wrapper itself is not persisted, but values flow into persistent metadata through `NodeAttrs` and into newly created nodes through directory creation APIs. `MaybeInitializedFs` also uses the first request uid to construct the backend filesystem, so this tiny type participates in initialization identity.

Risks and tests: no platform-specific validation. Tests assert request uid propagation through the FUSE path. Because the wrapper is a transparent newtype over `u32`, backend code still needs to enforce any platform or filesystem ownership policy outside this file.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/common/uid.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/high_level_api/interface.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/high_level_api/interface.rs

Purpose: path-oriented asynchronous filesystem trait roughly matching FUSE operations while addressing nodes by absolute path and optional file handle.

Important APIs: response structs `AttrResponse`, `OpenResponse`, `OpendirResponse`, and `CreateResponse`; trait `AsyncFilesystem` with lifecycle, metadata, creation/deletion, rename/link, file I/O, directory I/O, statfs, xattr, access, and create operations.

Control flow and state: the trait has no implementation state. Methods receive `RequestInfo` by value, path references, typed handles, typed sizes/modes, and callbacks for borrowed read buffers. `read` returns the callback result to enforce callback invocation.

Dependencies and integration: implemented by `ObjectBasedFsAdapter` for `Device` implementations and consumed by the `fuse_mt` backend adapter. Uses common types and `cryfs_utils::path::AbsolutePath`.

Risks and tests: many raw parameters remain unwrapped (`flags`, lock owners, xattr flags). Some operations are expected to return `FsError::NotImplemented`. Tests currently focus on low-level mounted mkdir behavior rather than this trait directly.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/high_level_api/interface.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/high_level_api/mod.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/high_level_api/mod.rs

Purpose: module facade for the high-level path API.

Important APIs: declares `interface` and re-exports `AsyncFilesystem`, `AttrResponse`, `CreateResponse`, `OpenResponse`, and `OpendirResponse`.

Control flow and state: no runtime behavior.

Dependencies and integration: used by `lib.rs`, `object_based_api/high_level_adapter.rs`, and backend glue.

State and persistence behavior: this module does not own data, but it defines which path-oriented operation results are available to downstream filesystem implementations and backend adapters. The response types carry TTLs, attributes, and handles that control cache and persistence behavior at the FUSE boundary.

Risks and tests: public API stability depends on the re-export list matching intended surface. If a response type or trait method is added in `interface.rs` but not re-exported here, users may have to reach through private module paths or lose access entirely. Coverage is indirect through adapters and mounted tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/high_level_api/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/lib.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/lib.rs

Purpose: crate root and public API assembly for RustFS.

Important APIs: public modules `object_based_api`, `high_level_api`, `low_level_api`, and feature-gated `backend`; public re-exports of common types, `Data`, and callback helpers. Test module is enabled under `cfg(test)`.

Control flow and state: no runtime behavior. Feature flags determine whether backend and handle-related public items are available.

Dependencies and integration: users implement object or high/low-level traits through the exported types. `cryfs_utils::data::Data` is exposed for open-file data transfer.

Risks and tests: crate surface is feature-sensitive. Public re-exports make internal common type changes semver relevant.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/low_level_api/interface.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/low_level_api/interface.rs

Purpose: inode-oriented asynchronous filesystem trait aligned closely with FUSE low-level operations.

Important APIs: reply structs for entry, attr, open, write, create, lock, bmap, lseek, xtimes, and ioctl; `ReplyDirectory` and `ReplyDirectoryPlus` buffer traits; `ReplyDirectoryAddResult`; trait `AsyncFilesystemLL` with init/destroy, lookup/forget, metadata, readlink, mknod/mkdir/unlink/rmdir/symlink/rename/link, open/read/write/flush/release/fsync, opendir/readdir/readdirplus/releasedir/fsyncdir, statfs, xattrs, access, create, locks, bmap, ioctl, fallocate, lseek, copy range, and macOS operations.

Control flow and state: implementations control inode lifetime through lookup and forget. Directory reply traits let adapters stop when buffers are full. Callback-based read and readlink keep borrowed data lifetimes local.

Dependencies and integration: implemented by `ObjectBasedFsAdapterLL`; backend adapters translate fuser calls to this trait. Uses common typed wrappers and `PathComponent`.

Risks and tests: the trait includes many operations that the object adapter returns as `NotImplemented`. Numerous TODOs flag raw integer parameters and platform-specific semantics. `mkdir` tests exercise lookup, creation, errno mapping, and mounted fuser integration.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/low_level_api/interface.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/low_level_api/mod.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/low_level_api/mod.rs

Purpose: module facade for the low-level inode API.

Important APIs: declares `interface`, re-exports `ReplyXTimes` and the main reply structs, directory reply traits, add-result enum, and `AsyncFilesystemLL`.

Control flow and state: no runtime behavior.

Dependencies and integration: imported by object low-level adapter, backend adapters, and tests/mocks.

Risks and tests: re-export list defines the crate's low-level public API. Platform-gated `ReplyXTimes` use in implementations must match this module's public surface.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/low_level_api/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/backends.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/backends.rs

Purpose: abstracts mounting an object-based filesystem through either supported backend.

Important APIs: `RustfsBackend` trait with associated `BackgroundSession`, `mount`, and `spawn_mount`; feature-gated `RustfsFuserBackend` and `RustfsFusemtBackend`; public re-exports of `fuser::{Config, MountOption, SessionACL}`.

Control flow and state: backend impls wrap a `Device` constructor in the appropriate adapter. Fuser uses `ObjectBasedFsAdapterLL`; fuse-mt uses the path-based `ObjectBasedFsAdapter`. Both delegate to backend-specific mount/spawn functions and return `RunningFilesystem` for spawned mounts.

Dependencies and integration: connects object API, backend module, `RunningFilesystem`, Tokio runtime handles, and cancellation triggers.

Risks and tests: behavior diverges by backend because fuser and fuse-mt use different adapter layers. Generic bounds are broad (`Send`, `Sync`, `Debug`, `'static`) and TODOs question whether all are necessary.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/backends.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/high_level_adapter.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/high_level_adapter.rs

Purpose: adapts object-based `Device`, `Dir`, `File`, `OpenFile`, `Node`, and `Symlink` traits into the high-level path-based filesystem API.

Important APIs: `ObjectBasedFsAdapter::new`, `trigger_on_operation`, test-only `reset_cache_after_setup`, `Debug`, `AsyncFilesystem` impl, and `AsyncDrop` impl.

Control flow and state: stores delayed filesystem initialization in `Arc<RwLock<AsyncDropGuard<MaybeInitializedFs<Fs>>>>` and open files in `OpenFileList`. `init` constructs the device using request uid/gid. Most operations call `trigger_on_operation`, then either operate on an open file handle or resolve a path through `Device::lookup`. Path-splitting operations locate the parent directory and call child creation/removal methods. `read` uses the callback after fetching `Data`; `release` removes and async-drops the open file. `readdir` synthesizes self and parent references.

Dependencies and integration: used by the fuse-mt object backend. It relies on `with_async_drop_2` for deterministic guard release and common high-level response types.

Risks and tests: many operations are unimplemented: macOS utimens, mknod, link, xattrs, fsyncdir. `opendir` uses `FileHandle::MAX` as a dummy. Several TODOs mention missing path precondition checks, unwraps, and rename overwrite semantics.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/high_level_adapter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/device.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/device.rs

Purpose: root trait for object-based filesystem implementations.

Important APIs: associated types `Node`, `Dir<'a>`, `Symlink<'a>`, `File<'a>`, and `OpenFile`; optional `on_operation`; required `rootdir`, `rename`, and `statfs`; default path-based `lookup`.

Control flow and state: default `lookup` starts from `rootdir`, converts to node, walks intermediate path components as directories, calls `lookup_child`, and async-drops each previous node before continuing. Root path returns root node directly.

Dependencies and integration: object adapters consume this trait. It depends on `AsyncDrop`, `AsyncDropGuard`, `AbsolutePath`, and `with_async_drop_2`.

Risks and tests: `lookup` performs repeated directory conversions and has TODOs for avoiding extra drops/lookups. The `rename` method is retained mainly for fuse-mt and may be removed once low-level-style dir operations cover that backend.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/device.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/dir.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/dir.rs

Purpose: object interface for directories.

Important APIs: `Dir::into_node`, `entries`, `lookup_child`, `rename_child`, `move_child_to`, `create_child_dir`, `create_child_symlink`, `create_and_open_file`, `remove_child_file_or_symlink`, `remove_child_dir`, and `fsync`.

Control flow and state: trait implementors own directory persistence. Adapters call create methods, often immediately converting returned child objects into nodes or dropping them after collecting attrs. `lookup_child` must return `NodeDoesNotExist` immediately for missing names.

Dependencies and integration: used by device lookup, high-level adapter, low-level adapter, and inode loading. It uses typed path components, modes, uid/gid, open flags, attrs, and `DirEntry`.

Risks and tests: semantics of overwrite, move, and fsync are delegated to implementations. Low-level adapter assumes successful unlink/rmdir means inode forest can be orphaned.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/dir.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/file.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/file.rs

Purpose: object interface for closed regular files.

Important APIs: `File::into_node` and async `File::into_open(this, flags) -> OpenFile`.

Control flow and state: consumes an async-drop file guard to create an open-file object. This transfers future I/O to the `OpenFile` trait and lets adapters register a file handle.

Dependencies and integration: used by both object adapters for `open` and by directory `create_and_open_file`.

Risks and tests: access mode validation is up to implementations. Failure must preserve async-drop correctness for the consumed guard.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/mod.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/mod.rs

Purpose: module facade for object-based filesystem traits.

Important APIs: declares `device`, `dir`, `file`, `node`, `open_file`, and `symlink`; re-exports `Device`, `Dir`, `File`, `Node`, `OpenFile`, and `Symlink`.

Control flow and state: no runtime behavior.

Dependencies and integration: consumed by `object_based_api/mod.rs`, adapters, utilities, and filesystem implementations.

Risks and tests: this is the public object API boundary; changes alter implementation requirements for downstream filesystems.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/node.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/node.rs

Purpose: common object interface for any filesystem node.

Important APIs: associated `Device`; conversions `as_dir`, `as_file`, `as_symlink`; `getattr`, `setattr`, and `fsync`.

Control flow and state: adapters first load nodes, then downcast to a concrete object kind via async methods. `setattr` accepts optional mode, uid, gid, size, atime, mtime, and ctime.

Dependencies and integration: used by both adapters, inode list, and test cache flush. Depends on `AsyncDropGuard`, typed attrs, ids, mode, and sizes.

Risks and tests: type mismatch errors must be reported by implementors. Optional setters require careful partial-update semantics and persistence ordering.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/open_file.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/open_file.rs

Purpose: object interface for an opened regular file.

Important APIs: `read`, `write`, `flush`, `fsync`, `getattr`, and `setattr`.

Control flow and state: adapters store open-file instances in `OpenFileList` keyed by `FileHandle`. `read` returns owned `Data`, then adapters pass a borrowed slice to callbacks. `write` receives `Data` and adapters report the input length as written after success.

Dependencies and integration: used by high and low-level adapters for handle-based I/O and metadata changes.

Risks and tests: open mode enforcement and short-write semantics are implementation-dependent. Returning the input length after `write` assumes success means all bytes were written.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/open_file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/symlink.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/symlink.rs

Purpose: object interface for symbolic links.

Important APIs: `Symlink::into_node` and async `target`.

Control flow and state: adapters downcast a node with `as_symlink`, call `target`, and return the string to readlink callers.

Dependencies and integration: used by high-level and low-level readlink handling and symlink creation paths.

Risks and tests: target is an unconstrained string; comments elsewhere note the lack of a relative-or-absolute path type. Implementations must preserve target bytes/encoding semantics.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/symlink.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/low_level_adapter.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/low_level_adapter.rs

Purpose: adapts object-based filesystems to the low-level inode-based API used by the `fuser` backend.

Important APIs: `ObjectBasedFsAdapterLL::new`, test-only cache reset/flush helpers, `trigger_on_operation`, inode access helpers, `_orphan_inode`, `_move_inode`, full `AsyncFilesystemLL` implementation, `Debug`, and `AsyncDrop`.

Control flow and state: holds delayed filesystem initialization, `InodeList`, `OpenFileList`, and `DirCache`. `init` constructs the filesystem, loads rootdir, and registers the root inode. `lookup` uses `InodeList::add_or_increment_refcount`, loading children through parent directories and returning attrs. `forget` decrements inode references. Create/mkdir/symlink add loaded children. Unlink/rmdir remove the underlying child, then orphan any loaded inode. Rename updates underlying dirs, then moves the inode forest if the child was loaded. Open/read/write/flush/release/fsync use file handles. Opendir/readdir/releasedir use directory handles and cached entries with careful offsets for `.` and `..`.

Dependencies and integration: core bridge for `RustfsFuserBackend`. Depends on `MaybeInitializedFs`, `InodeList`, `DirCache`, `OpenFileList`, `flatten_async_drop`, and low-level reply traits.

Risks and tests: many advanced operations return `NotImplemented`. Several unwraps and panics enforce invariants. Readdirplus, xattrs, locks, fallocate, ioctl, lseek, and copy range are incomplete. Existing `mkdir` tests exercise lookup and creation paths through this adapter and fuser.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/low_level_adapter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/mod.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/mod.rs

Purpose: public module facade for object-based RustFS support.

Important APIs: re-exports object traits, `FUSE_ROOT_ID`, high-level and low-level adapters, backend wrappers, and backend config/mount types.

Control flow and state: no runtime behavior. Feature gates control adapter and backend availability.

Dependencies and integration: this is the main entry point for users implementing `Device` and mounting it through RustFS.

Risks and tests: feature-specific exports can alter public API. It exposes low-level root inode only when fuser utilities are built.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/dir_cache.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/dir_cache.rs

Purpose: manages per-open-directory handles and cached directory entries for low-level readdir.

Important APIs: `OpenDirHandle(FileHandle)` implements `HandleTrait`; `DirCache::new/add/remove/get`; `DirCacheEntry::new`, `dir_ino`, and `get_or_query_entries`.

Control flow and state: `DirCache` wraps a mutex-protected `HandleMap<OpenDirHandle, AsyncDropArc<DirCacheEntry>>`. `add` creates an entry for an inode and returns a handle. `get` clones the async-drop arc. `DirCacheEntry` stores `Option<Vec<DirEntry>>` behind a Tokio mutex; first query fills the cache and all later calls reuse it.

Dependencies and integration: low-level `opendir`, `readdir`, and `releasedir` use it to ensure repeated offset reads see a consistent directory snapshot.

Risks and tests: cache lives until `releasedir`, so changes after open are intentionally hidden. `remove` panics through `HandleMap` if the handle is invalid. Readdir offset behavior has TODO tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/dir_cache.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/handle_forest/delayed_handle_release.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/handle_forest/delayed_handle_release.rs

Purpose: RAII guard ensuring removed handles are intentionally released back to a `HandleForest` only after associated async drops complete.

Important APIs: `DelayedHandleRelease::new`, `release`, and `Drop`.

Control flow and state: stores `Option<Handle>`. `release` consumes the guard and calls `forest.release_removed_handle`. If dropped without release, `safe_panic!` reports an invariant violation.

Dependencies and integration: returned by `HandleForest::try_remove` and used by `InodeList` to delay inode-number reuse until `ConcurrentStore` entries are absent.

Risks and tests: forgetting to call `release` causes a panic-like safe failure, preventing silent handle leaks or unsafe reuse. It assumes release is always paired with the original forest.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/handle_forest/delayed_handle_release.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/handle_forest/handle_forest.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/handle_forest/handle_forest.rs

Purpose: generic forest of handle-addressed nodes with parent/child edge tracking and handle allocation.

Important APIs: `HandleForest::new`, `block_handle`, `get`, `get_mut`, `try_insert_root_with_specific_handle`, `get_child_of_mut`, async `try_insert`, `try_remove`, `make_node_into_orphan`, `move_node`, test-only `drain`, and error/result enums.

Control flow and state: combines `HandlePool` and `AsyncDropHashMap<Handle, Node<...>>`. Insert transactionally acquires a handle, inserts into the parent child map, constructs node value only on success, and undoes acquisition on duplicate edge. Remove refuses nodes with children, removes the child pointer from the parent if present, returns the node value and a delayed handle release. Move removes an edge from the old parent, reinserts into new parent, updates the child's parent pointer, and restores the old edge if the new parent is missing.

Dependencies and integration: used by `InodeList` to model kernel-visible inode parentage. Depends on `Node`, `HandlePool`, async drop containers, and `DelayedHandleRelease`.

Risks and tests: many invariants are enforced by panics. Overwriting an existing child during move orphans that child. Comments document cases where parent pointers may remain on orphaned nodes.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/handle_forest/handle_forest.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/handle_forest/mod.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/handle_forest/mod.rs

Purpose: module facade for inode-list forest internals.

Important APIs: declares `delayed_handle_release`, `handle_forest`, and `node`; re-exports `DelayedHandleRelease`, `GetChildOfError`, `HandleForest`, `MakeOrphanError`, `MoveInodeError`, `MoveInodeSuccess`, `TryInsertError`, and `TryRemoveResult`.

Control flow and state: no runtime behavior.

Dependencies and integration: consumed by `inode_list/mod.rs`.

State and persistence behavior: no state is stored here, but the exported types are the state-management vocabulary used by `InodeList` for parent/child topology, orphan handling, move handling, and delayed handle reuse. Keeping `node` private forces mutations through `HandleForest`, preserving invariants around bidirectional edges and async-drop ownership.

Risks and tests: intentionally exposes selected internals within the utility layer while keeping `node` private. A re-export mistake could either leak low-level mutable internals or hide error types needed by `InodeList` to translate forest failures into filesystem errors and panics.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/handle_forest/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/handle_forest/node.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/handle_forest/node.rs

Purpose: node record used inside `HandleForest`.

Important APIs: constructors `new_root` and `new`; parent accessors and `set_parent`; child lookup/insert/remove methods; `num_children`, `has_children`, `into_value`, `value`, `value_mut`; async drop; `RemoveResult`; `TryRemoveChildByHandleError`.

Control flow and state: stores optional `(parent_handle, edge_key)`, a child map from edge to handle, and an async-drop node value. Removal by handle verifies that the named edge points to the expected child and restores the mapping if it does not.

Dependencies and integration: generic over `HandleTrait`, edge key, and async-drop node value. Used only by `HandleForest`.

Risks and tests: `into_value` uses `unsafe_into_inner_dont_drop`, so callers must preserve drop responsibility. Parent and child bidirectional invariants are maintained by `HandleForest`, not this type alone.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/handle_forest/node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/inode_tree_node.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/inode_tree_node.rs

Purpose: value stored in the inode handle forest, combining kernel lookup reference count with a shared loading/loaded inode guard.

Important APIs: `InodeTreeNode::new`, `increment_refcount`, `decrease_refcount`, `inode_future`, `RefcountInfo`, and `AsyncDrop`.

Control flow and state: `kernel_refcount` starts at 1. Decrease asserts no underflow and reports whether it reached zero. The inode payload is an `AsyncDropShared` future resolving to a `LoadedEntryGuard`; this allows multiple lookup waiters to share a pending load.

Dependencies and integration: used by `InodeList` to enforce FUSE lookup/forget semantics and keep concurrent store entries alive.

Risks and tests: refcount overflow and underflow panic. The nested async-drop/future type is complex and marked with TODOs suggesting improvements to `ConcurrentStore`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/inode_tree_node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/mod.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/mod.rs

Purpose: tracks all inode numbers handed to the FUSE kernel and ties them to object nodes, parent relationships, lookup refcounts, and async-drop lifecycle.

Important APIs: constants `FUSE_ROOT_ID` and `DUMMY_INO`; `InodeList::new`, `insert_rootdir`, `get_node_and_parent_ino`, `get_node`, `add`, `add_or_increment_refcount`, `forget`, `make_into_orphan`, `move_inode`, test-only `clear_all_slow` and `fsync_all`; error enums.

Control flow and state: inner state holds a `ConcurrentStore<InodeNumber, Fs::Node>` and `HandleForest<InodeNumber, PathComponentBuf, InodeTreeNode<Fs>>` under a Tokio mutex. Root insertion establishes invariants. Lookup either increments an existing child refcount or inserts a loading child, waits outside the lock, then cleans up forest and parent refcount on load failure. Forget decrements refcount and removes zero-refcount leaf nodes, cascading to parents when child references were the last references. Removed handles are released only after async drops confirm store absence. Orphaning removes a parent child edge without dropping a loaded inode; moving updates parent edges and parent refcounts.

Dependencies and integration: central to `ObjectBasedFsAdapterLL` lookup, forget, create, unlink, rmdir, rename, getattr, and readdir parent references.

Risks and tests: invariants are extensive and many violations panic. Shutdown drops remaining inodes because the kernel may omit forgets. TODOs note deadlock/performance risks, cloned refs, and missing assertions. Test utilities can clear and fsync caches.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/maybe_initialized_fs.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/maybe_initialized_fs.rs

Purpose: stores a filesystem constructor until FUSE init supplies uid/gid, then exposes the initialized filesystem.

Important APIs: `MaybeInitializedFs::new_uninitialized`, `initialize`, `get`, custom debug, and `AsyncDrop`.

Control flow and state: enum state is either `Uninitialized(Some(Box<FnOnce(Uid, Gid) -> Fs>))` or `Initialized(AsyncDropGuard<Fs>)`. `initialize` consumes the constructor and changes state. `get` panics if called before init. Async drop drops the initialized filesystem, or if still uninitialized, calls the constructor with uid/gid zero and drops the result.

Dependencies and integration: used by high and low object adapters to delay device creation until request identity is known.

Risks and tests: calling the constructor on drop with dummy ids may have side effects even if init never occurred. Double init and pre-init get panic. TODOs question whether initialization storage can be simplified.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/maybe_initialized_fs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/mod.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/mod.rs

Purpose: utility module facade for object adapters.

Important APIs: exports `MaybeInitializedFs`; feature-gated `OpenFileList` and test callback; feature-gated `DirCache`, `OpenDirHandle`, `InodeList`, `FUSE_ROOT_ID`, `DUMMY_INO`, `MakeOrphanError`, and `MoveInodeError`.

Control flow and state: no runtime behavior.

Dependencies and integration: consumed by object adapters and public object API facade.

Risks and tests: utility availability depends on backend features. This file defines which internals become visible across the object-based module.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/open_file_list.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/open_file_list.rs

Purpose: thread-safe registry of open file objects keyed by `FileHandle`.

Important APIs: `OpenFileList::new`, async `get`, `add`, `remove`, test-only `for_each`, `ForEachCallback`, and `AsyncDrop`.

Control flow and state: wraps `HandleMap<FileHandle, AsyncDropArc<OF>>` in a mutex. `get` clones the open-file arc while holding the mutex, releases the mutex before awaiting the callback, then async-drops the clone. `add` stores a new async-drop arc. `remove` removes by handle and returns the guard for final release.

Dependencies and integration: used by both adapters for file I/O. Test cache flush iterates open files and fsyncs them.

Risks and tests: invalid `get` returns `InvalidFileDescriptor`, but invalid `remove` panics through `HandleMap`. AsyncDrop unwraps the inner drop result, so drop failures can panic.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/open_file_list.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/tests/mkdir.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/tests/mkdir.rs

Purpose: integration-style tests for mkdir through a mounted fuser-backed mock filesystem.

Important APIs: `test_mkdir` fixture helper, `mkdir_return_ok`, path helpers, and nested test modules for arguments and results.

Control flow and state: each test builds a mock low-level filesystem, sets lookup expectations for parent path and target absence/existence, starts a real mounted `Runner`, then uses `FilesystemDriver::mkdir`. The mock expectation checks propagated request info, parent inode, path component name, mode after kernel umask, and returned/error behavior.

Dependencies and integration: uses `rstest`, `mockall`, `nix::Errno`, fuser mount runner, mock helper, and low-level reply types. It exercises backend adapter, FUSE kernel behavior, and low-level API translation.

Risks and tests: coverage is focused on mkdir and path lookup error cases. TODOs note missing umask detail and broader mkdir errno cases. Because it mounts FUSE, test reliability depends on environment support and unmount cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/tests/mkdir.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/tests/mod.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/tests/mod.rs

Purpose: test module root.

Important APIs: declares `utils` and `mkdir`.

Control flow and state: no runtime behavior.

Dependencies and integration: included by `lib.rs` under `cfg(test)`.

State and persistence behavior: this module does not own test state; it wires the helper harness and mkdir tests into the crate test build. The actual persistent side effects happen in mounted temporary filesystems created by `utils::Runner`.

Risks and tests: only listed test suite here is mkdir plus utilities, indicating current test coverage is narrow for the broader filesystem API. The absence of additional module declarations means many adapters, inode-list invariants, xattr paths, readdir offsets, and error mappings are not directly exercised from this test root.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/tests/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/filesystem_driver.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/filesystem_driver.rs

Purpose: small async test driver for invoking filesystem operations against a mounted temporary path.

Important APIs: `FilesystemDriver { mountpoint }`, `new`, and async `mkdir`.

Control flow and state: `mkdir` joins the requested absolute path to the mountpoint, calls blocking `nix::unistd::mkdir` inside `tokio::task::spawn_blocking`, and returns the resulting nix error or success. It converts `Mode` to raw mode bits.

Dependencies and integration: used by `mkdir` tests through `Runner::driver`. Depends on `AbsolutePathBuf`, `nix`, `tokio`, and local `Mode`.

Risks and tests: currently only supports mkdir. Path joining strips the leading slash with `without_root`, so absolute test paths are interpreted under the temp mount.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/filesystem_driver.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/fuser_runner.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/fuser_runner.rs

Purpose: test harness that mounts a mock low-level filesystem with the fuser backend and unmounts it safely.

Important APIs: `Runner::start`, `driver`, `Drop`, static `LOG_INIT`, and two self-tests.

Control flow and state: `start` initializes test logging once, wraps the mock in `AsyncDropArc`, creates a temp mountpoint, spawns the fuser mount on the current Tokio runtime, waits for mock init completion, and returns a driver-capable runner. Drop explicitly calls `unmount_join` and `safe_panic!` on failure, ensuring mock expectations fail on the main thread.

Dependencies and integration: used by mkdir tests. Depends on backend fuser `spawn_mount`, `RunningFilesystem`, tempfile, async-drop utilities, and mock types.

Risks and tests: member order is important so the mount is dropped before mountpoint/mock. Self-tests verify setup and that unmet mock expectations surface as test failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/fuser_runner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/mock_helper.rs -->
# sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/mock_helper.rs

Purpose: helper for setting common mock low-level filesystem expectations and synthetic attrs in tests.

Important APIs: `ROOT_INO`, `TestInodeNumberPool`, `MockHelper::new`, lookup expectation helpers for failure, nonexistence, kind, directory/file paths, and private attr constructors.

Control flow and state: `TestInodeNumberPool` returns increasing arbitrary inodes. Helper methods chain mock `lookup` expectations for each component of a path, returning inode numbers for later expectations. Attribute helpers create directory, file, and symlink `NodeAttrs` with appropriate modes and current timestamps.

Dependencies and integration: used by mkdir tests to establish expected parent and target lookup behavior. Uses `mockall` predicates, path components, common types, and low-level `ReplyEntry`.

Risks and tests: helper-generated attrs use current time and arbitrary sizes, so tests should not depend on exact values unless set. Commented-out helper methods suggest incomplete convenience coverage for direct file/symlink lookup.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/mock_helper.rs -->
