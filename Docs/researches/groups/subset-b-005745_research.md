# subset-b-005745 research

Grouped research for the requested source files. Each section preserves the source path in its title and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/namei.c -->
# sources/distributed-fs/ceph-client/fs/overlayfs/namei.c

## Purpose
`namei.c` implements OverlayFS pathname lookup, origin-file-handle validation, redirect following, metacopy lower-data resolution, index lookup, and lower-positive checks. It is the bridge between VFS dentry lookup and OverlayFS' multi-layer model: for each overlay dentry it discovers the upper dentry, lower stack, optional data-only lower path, redirect metadata, index entry, and final overlay inode.

## Important APIs, types, and functions
The local `struct ovl_lookup_data` carries lookup state such as current layer, name, directory/opaque status, redirect strings, metacopy state, and stop/last flags. `struct ovl_lookup_ctx` owns the objects assembled for the final dentry: upper dentry, lower stack, origin path, index dentry, `ovl_entry`, and inode.

Public entry points include `ovl_lookup()`, `ovl_lower_positive()`, `ovl_path_next()`, `ovl_verify_lowerdata()`, file-handle helpers such as `ovl_check_fb_len()`, `ovl_uuid_match()`, `ovl_decode_real_fh()`, `ovl_check_origin_fh()`, `ovl_verify_origin_xattr()`, and index helpers such as `ovl_get_index_name()`, `ovl_get_index_fh()`, `ovl_lookup_index()`, `ovl_index_upper()`, and `ovl_verify_index()`.

## Control flow
`ovl_lookup()` validates name length, switches to mounter credentials with `with_ovl_creds()`, and delegates to `ovl_lookup_layers()`. Lookup starts in the parent's upper dentry when present, checks upper redirects/origin/metacopy, then walks lower layers from top to bottom unless a whiteout, opaque directory, non-directory conflict, or final usable result stops the search. `ovl_lookup_layer()` handles absolute redirect paths element by element; `ovl_lookup_single()` performs the actual `lookup_one_unlocked()` call, filters whiteouts, validates casefold consistency, detects opaque/xwhiteout directories, rejects weird dentries, and rewrites `d->name` when a redirect xattr is followed.

After layer walking, the code enforces redirect/metacopy policy in `ovl_check_follow_redirect()`, rejects metacopy files without data, optionally installs origin-path lookups, verifies lower origins for indexed/NFS-export cases, looks up an index entry, allocates an `ovl_entry`, and calls `ovl_get_inode()`. `d_splice_alias()` attaches the resulting inode. Lazy lower-data lookup for data-only layers is deferred to `ovl_verify_lowerdata()`, which resolves the absolute redirect with `LOOKUP_BENEATH | LOOKUP_NO_SYMLINKS | LOOKUP_NO_XDEV` and then validates fs-verity digest when configured.

## State and persistence
Persistent state is carried in OverlayFS xattrs: `overlay.origin`, `overlay.redirect`, `overlay.upper`, `overlay.metacopy`, and whiteout/opaque markers. `ovl_fix_origin()` can add a missing origin xattr and mark the upper parent impure. Index entries are named by hex-encoded lower file handles and may be whiteouted to represent stale exported handles. In-memory state is stored in dentry flags, `ovl_entry` lower stacks, inode flags such as `OVL_UPPERDATA`, `OVL_HAS_DIGEST`, and `OVL_VERIFIED_DIGEST`, and redirect strings owned by `ovl_inode`.

## Dependencies and integration points
The file depends on VFS lookup, exportfs encode/decode, xattrs, mount idmaps, fs-verity helpers via `util.c`, index/workdir setup from `super.c`, inode creation from `inode.c`, and constants/types from `overlayfs.h` and `ovl_entry.h`. It is called by the overlay directory inode operations and supports export operations by resolving file handles and index entries.

## Risks
The main risks are stale or malicious xattrs, conflicting lower UUIDs, redirect traversal security, metacopy files without accessible lower data, casefold mismatch after offline changes, and index corruption. The code mitigates with strict lookup flags for data-only redirects, capability checks for file-handle decode, trap inode checks for overlapping layers, type validation, rate-limited warnings, and policy gates for redirect/metacopy following.

## Test signals
Useful tests include lookups across upper/lower/merged directories, whiteout and opaque behavior, absolute and relative redirects, metacopy with and without data-only layers, fs-verity require/on/off modes, NFS export/index stale-handle behavior, lower UUID conflicts, casefold consistency, negative dentry handling, and `ovl_lower_positive()` results after copy-up and whiteout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/namei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/overlayfs.h -->
# sources/distributed-fs/ceph-client/fs/overlayfs/overlayfs.h

## Purpose
`overlayfs.h` is the central internal interface for OverlayFS. It defines feature enums, on-disk xattr/file-handle formats, wrapper helpers around VFS operations, mount option constants, inode/dentry flag helpers, and prototypes shared across lookup, readdir, copy-up, inode, dir, file, export, superblock, and xattr code.

## Important APIs, types, and functions
Key enums include `ovl_path_type`, `ovl_xattr`, `ovl_inode_flag`, `ovl_entry_flag`, redirect modes, UUID modes, xino modes, verity modes, and fsync modes. Persistent formats are `struct ovl_fb`, `struct ovl_fh`, and `struct ovl_metacopy`. The header declares the global `ovl_fs_type`, `ovl_xattr_table`, and many internal entry points including `ovl_lookup()`, `ovl_dir_operations`, `ovl_fill_super()`, `ovl_xattr_handlers()`, copy-up helpers, fileattr helpers, index helpers, export operations, and inode allocation/lookup helpers.

Inline wrappers such as `ovl_do_create()`, `ovl_do_unlink()`, `ovl_do_rename()`, `ovl_do_setxattr()`, `ovl_do_tmpfile()`, `ovl_lookup_upper_unlocked()`, and `ovl_start_creating_upper()` ensure upper-layer operations consistently use `ovl_upper_mnt_idmap(ofs)` and emit debug traces. Convenience helpers expose feature policy, including `ovl_redirect_follow()`, `ovl_redirect_dir()`, `ovl_origin_uuid()`, `ovl_has_fsid()`, `ovl_should_sync()`, `ovl_should_sync_metadata()`, `ovl_is_volatile()`, `ovl_allow_offline_changes()`, `ovl_same_fs()`, `ovl_same_dev()`, and `ovl_xino_bits()`.

## Control flow
This header does not own a standalone algorithm; it standardizes cross-file control flow. Upper mutations go through `ovl_do_*` wrappers; xattrs go through `ovl_xattr(ofs, enum)` to select `trusted.overlay.*` versus `user.overlay.*`; lookup and readdir code use `ovl_path_type()` and path accessor prototypes; copy-up uses `ovl_copy_up_start()`/`ovl_copy_up_end()` and `ovl_open_flags_need_copy_up()`.

## State and persistence
The file documents and encodes the persistent xattr namespace and file-handle layouts. `struct ovl_fb` stores a magic/versioned exported file handle plus filesystem UUID and endian/path flags; `struct ovl_fh` aligns that payload; `struct ovl_metacopy` stores optional fs-verity digest metadata. In-memory state is represented by inode and entry flags plus `struct ovl_inode_params`, which transfers lookup/copy-up results into inode construction.

## Dependencies and integration points
It includes kernel VFS, UUID, fs-verity, namei, and ACL headers, then includes `ovl_entry.h` for core OverlayFS state objects. Almost every OverlayFS implementation file includes this header, so changes here have a broad ABI-like effect inside the filesystem.

## Risks
Risks include changing packed persistent formats, misusing idmapped upper helpers, adding xattrs without updating `ovl_xattr_table`, and weakening feature policy helpers in ways that break export, redirect, metacopy, or volatile semantics. Since many helpers are inline, subtle semantic changes propagate widely.

## Test signals
Compile coverage with all relevant config combinations is important: POSIX ACL on/off, Unicode/casefold on/off, fs-verity on/off, NFS export, userxattr, metacopy, xino, and redirect modes. Runtime tests should exercise idmapped upper operations, xattr namespace selection, file-handle validation, volatile sync behavior, and copy-up decisions for write/truncate opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/overlayfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/ovl_entry.h -->
# sources/distributed-fs/ceph-client/fs/overlayfs/ovl_entry.h

## Purpose
`ovl_entry.h` defines the core in-memory objects that represent an OverlayFS mount, layer, path, dentry entry, and inode. These are the private data structures used across superblock setup, lookup, readdir, copy-up, xattrs, and inode operations.

## Important APIs, types, and functions
`struct ovl_config` stores resolved mount options: upper/work/lower path strings, permission mode, redirect/verity/uuid/xino/fsync modes, and feature booleans such as `index`, `nfs_export`, `metacopy`, and `userxattr`. `struct ovl_sb` tracks each unique underlying superblock, its pseudo device, UUID conflict status, and whether it is used as a lower. `struct ovl_layer` maps a layer to a cloned mount, trap inode, fs entry, layer index, fsid, and xwhiteout state. `struct ovl_path` pairs a layer with a real dentry.

`struct ovl_entry` is a flex-array object holding a lower stack for an overlay inode/dentry. `struct ovl_fs` is the mount-private superblock state: layer arrays, work/index directories, namelen, config, creator credentials, capability probe results, in-use locks, trap inodes, xino mode, whiteout cache, volatile error sequence, and casefold state. `struct ovl_inode` embeds `struct inode` and stores per-inode cache/redirect data, version, flags, upper dentry, lower entry, and a mutex.

Inline accessors include `OVL_FS()`, `ovl_numlowerlayer()`, `ovl_upper_mnt()`, `ovl_upper_mnt_idmap()`, `ovl_numlower()`, `ovl_lowerstack()`, `ovl_lowerdata()`, `ovl_lowerdata_dentry()`, `OVL_E_FLAGS()`, `OVL_I()`, `OVL_I_E()`, `OVL_E()`, and `ovl_upperdentry_dereference()`.

## Control flow
These structures are allocated during mount (`ovl_fs`, layers, root `ovl_entry`) and lookup (`ovl_entry`, `ovl_inode`). Runtime helpers select upper/lower/data paths by reading these objects. Lookup may populate lowerdata lazily, while copy-up updates the upper dentry and flags under `ovl_inode.lock`.

## State and persistence
The file itself contains no on-disk format, but its fields mirror persistent OverlayFS concepts: lower/upper/work paths, stable fsid/xino policy, index/work directories, origin/lowerdata references, and volatile mount error tracking. References are owned carefully: layer mounts are unmounted by `ovl_free_fs()`, lower dentries are refcounted in `ovl_entry`, upper dentries are held by `ovl_inode`, and trap inodes prevent overlap cycles.

## Dependencies and integration points
The header is included by `overlayfs.h`, making these definitions globally available to the OverlayFS implementation. It assumes VFS objects such as `super_block`, `vfsmount`, `dentry`, `inode`, credentials, mutexes, and atomics.

## Risks
The first member of `struct ovl_layer` must remain `mnt` because `ovl_free_fs()` reuses layout assumptions while unmounting. Flexible-array sizing and reference ownership are safety-sensitive. Memory ordering around `__upperdentry` and lowerdata requires the accessors in `util.c` to be used consistently.

## Test signals
Tests should stress mount/unmount cleanup, copy-up races, lazy lowerdata lookup, multiple lower/data layers, overlapping-layer rejection, xino/fsid behavior, and directory cache lifetime. Debug builds should watch for `WARN_ON_ONCE()` checks in `OVL_FS()` and lowerdata accessors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/ovl_entry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/params.c -->
# sources/distributed-fs/ceph-client/fs/overlayfs/params.c

## Purpose
`params.c` implements OverlayFS mount option parsing, default option selection, fs-context lifecycle, option compatibility verification, reconfigure handling, option display, and teardown of mount-private state on failed mounts or unmount.

## Important APIs, types, and functions
It exports `ovl_parameter_spec[]`, `ovl_parameter_redirect_dir[]`, `ovl_xino_mode()`, `ovl_init_fs_context()`, `ovl_free_fs()`, `ovl_fs_params_verify()`, and `ovl_show_options()`. Module parameters define defaults for redirect_dir, redirect_always_follow, xino_auto, index, nfs_export, and metacopy. `enum ovl_opt` maps parser tokens to mount features. Constant tables translate string values for bool, uuid, xino, redirect, verity, and fsync modes.

Parsing helpers include `ovl_next_opt()` for escaped comma splitting, `ovl_parse_monolithic()`, `ovl_parse_param_split_lowerdirs()` for single-colon regular lower and double-colon data layers, path lookup helpers `ovl_mount_dir*()`, consistency checks in `ovl_mount_dir_check()`, lower array growth via `ovl_ctx_realloc_lower()`, layer storage in `ovl_add_layer()`, and reset/free helpers.

## Control flow
`ovl_init_fs_context()` allocates `struct ovl_fs_context` and `struct ovl_fs`, initializes default config from module/build options, installs `ovl_context_ops`, and initializes the whiteout mutex. `ovl_parse_param()` rejects new-api reconfigure changes, parses each parameter, and updates config or layer arrays. `lowerdir=` replaces existing lower layers; `lowerdir+`/`datadir+` append file-or-string paths and are rejected after legacy `lowerdir=`. `override_creds` can replace creator credentials only when current is in the fsopen user namespace.

Before superblock fill proceeds, `ovl_fs_params_verify()` resolves feature dependencies: workdir/index without upper are disabled, volatile without upper is ignored, uuid=on without upper becomes uuid=null, metacopy may force redirect_dir=on, nfs_export may force index=on, nfs_export conflicts with metacopy/verity, userxattr disables default redirect/metacopy unless explicitly allowed, and unprivileged trusted-xattr-dependent features are rejected.

## State and persistence
Mount strings are preserved in `config.upperdir`, `config.workdir`, and `config.lowerdirs` for `/proc/mounts`. `ovl_fs_context` temporarily owns resolved `struct path` objects and user strings until `super.c` consumes them. `ovl_free_fs()` releases traps, work/index dirs, in-use locks, layer mounts, anon bdevs, config strings, credentials, and the `ovl_fs`.

## Dependencies and integration points
The file integrates with the new mount API (`fs_context`), VFS path lookup, parser helpers, capability checks, and `ovl_fill_super()` via `get_tree_nodev()`. It depends on `super.c` to probe actual filesystem capabilities after parsing.

## Risks
Option interaction is complex. Regressions may come from accepting inconsistent lower/data ordering, losing escaped path semantics, mishandling user namespace credentials, or silently enabling features that require trusted xattrs. Freeing paths/strings during parse reset must preserve ownership exactly.

## Test signals
Test legacy mount strings, new API `lowerdir+`/`datadir+`, escaped commas/colons, empty lowerdir, too many layers, casefold mismatch, read-only upper rejection, userxattr conflicts, unprivileged mounts, reconfigure behavior, and `/proc/mounts` rendering of defaults versus explicit options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/params.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/params.h -->
# sources/distributed-fs/ceph-client/fs/overlayfs/params.h

## Purpose
`params.h` is the small shared interface between OverlayFS mount parsing and superblock setup. It declares parser tables, the fs-context data structures, and the option verification/display/free entry points used by `params.c`, `super.c`, and the filesystem type registration.

## Important APIs, types, and functions
`struct ovl_opt_set` records whether the user explicitly requested `metacopy`, `redirect`, `nfs_export`, or `index`; this matters because `ovl_fs_params_verify()` distinguishes explicit conflicts from defaults that can be adjusted. `OVL_MAX_STACK` caps lower layers at 500. `struct ovl_fs_context_layer` stores one user-provided layer name plus its resolved `struct path`. `struct ovl_fs_context` stores upper/work paths, dynamic lower capacity/counts, count of data-only layers, explicit-option set, the lower array, preserved legacy `lowerdir=` string, and casefold consistency state.

The file declares `ovl_parameter_spec[]`, `ovl_parameter_redirect_dir[]`, `ovl_init_fs_context()`, `ovl_free_fs()`, `ovl_fs_params_verify()`, `ovl_show_options()`, and `ovl_xino_mode()`.

## Control flow
During `fsopen()`/mount setup, `ovl_init_fs_context()` allocates and attaches `struct ovl_fs_context` to `fc->fs_private`. `params.c` mutates this context while parsing mount options. `super.c` consumes it during `ovl_fill_super()`, transferring lowerdir strings and path references into `struct ovl_fs` layers. On failure or context release, `ovl_free()` calls the context free helper and `ovl_free_fs()`.

## State and persistence
The context is temporary mount-construction state, not persistent state. It preserves user-visible mount strings for later `show_options` and owns path references until superblock setup clones mounts or drops the context. `casefold_set` and the mount-private `ofs->casefold` jointly ensure all layer directories are consistently casefolded or not.

## Dependencies and integration points
It depends on `linux/fs_context.h` and `linux/fs_parser.h`, and forward declares `struct ovl_fs` and `struct ovl_config` to avoid pulling all OverlayFS internals into users. `super.c` relies on the lower ordering contract: regular lower layers first, data-only lower layers last, and `nr` includes `nr_data`.

## Risks
Changing `OVL_MAX_STACK`, lower ordering fields, or explicit-option tracking affects mount validation and feature downgrade behavior. Incorrect ownership expectations for `lowerdir_all`, layer `name`, or `path` can cause leaks, double frees, or wrong `/proc/mounts` output.

## Test signals
Compile-time coverage should catch prototype drift. Runtime signals include correct handling of legacy and new lower options, data-layer counts, explicit conflict diagnostics, casefold validation, and cleanup after parse failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/readdir.c -->
# sources/distributed-fs/ceph-client/fs/overlayfs/readdir.c

## Purpose
`readdir.c` implements directory iteration for OverlayFS. It merges upper and lower directory entries, handles whiteouts and xwhiteouts, maintains a per-inode merged directory cache, translates inode numbers for xino and impure dirs, supports direct real-dir iteration when safe, and cleans work/index directories during mount and unlink paths.

## Important APIs, types, and functions
Core types are `struct ovl_cache_entry`, `struct ovl_dir_cache`, `struct ovl_readdir_data`, and `struct ovl_dir_file`. Exported functions include `ovl_cache_free()`, `ovl_dir_cache_free()`, `ovl_dir_real_file()`, `ovl_check_empty_dir()`, `ovl_cleanup_whiteouts()`, `ovl_check_d_type_supported()`, `ovl_workdir_cleanup()`, `ovl_indexdir_cleanup()`, and `ovl_dir_operations`.

Important internals include rb-tree lookup/add helpers, `ovl_fill_merge()`, `ovl_dir_read()`, `ovl_dir_read_merged()`, `ovl_cache_get()`, `ovl_cache_update()`, `ovl_cache_get_impure()`, `ovl_iterate_real()`, `ovl_iterate_merged()`, `ovl_iterate()`, `ovl_dir_llseek()`, and `ovl_dir_open()`.

## Control flow
Opening a directory stores an `ovl_dir_file` with the initial real file, whether the inode can be iterated directly, and whether the real file is upper. Iteration resets stale state when position is zero. Non-merge/real dirs can pass through to the real filesystem unless xino, parent merge, or impure state requires translation. Merged dirs build or reuse `ovl_dir_cache`: entries are read layer by layer using `iterate_dir()`, deduplicated by name (or casefolded name), and ordered so lowest-layer offsets remain relatively stable.

Whiteout detection is two-phase: character-device whiteout candidates are checked after reading, while xwhiteout regular files in marked directories can be deferred until emit time. `ovl_iterate_merged()` updates missing `d_ino` values and xwhiteout state lazily before `dir_emit()`. `llseek` proxies to the real file for real dirs and manipulates the cache cursor for merged dirs.

## State and persistence
The per-inode `ovl_dir_cache` stores entries, an rb-tree, refcount, and version. `OVL_I(inode)->version` is incremented by mutations in `util.c`, invalidating old caches. Impure directory caches are not refcounted the same way and may trigger best-effort removal of the `overlay.impure` xattr when no translated entries remain. Workdir/index cleanup mutates upper work directories and index entries using VFS unlink/rmdir/whiteout helpers.

## Dependencies and integration points
The file depends on lookup/path helpers from `namei.c`, flags and xattr helpers from `util.c`, upper operation wrappers from `overlayfs.h`, and copy-up/dir cleanup helpers from `dir.c`. `super.c` uses `ovl_check_d_type_supported()` and index/workdir cleanup during mount.

## Risks
Directory cache consistency depends on correct version increments and locking. Whiteout and xwhiteout handling must avoid exposing hidden lower entries. Inode-number translation can break user expectations if xino overflows or impure cache lookup fails. Cleanup helpers operate on persistent work/index directories and must avoid deleting valid index state.

## Test signals
Exercise merged readdir ordering, duplicate names across layers, whiteouts, xwhiteouts, casefolded names, `seekdir/telldir`, concurrent copy-up while iterating, impure dirs, xino remapping, `d_type` probing, empty-dir checks before rmdir, stale index cleanup, and workdir incompat feature handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/readdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/super.c -->
# sources/distributed-fs/ceph-client/fs/overlayfs/super.c

## Purpose
`super.c` registers the OverlayFS filesystem type and builds an overlay superblock from a parsed fs context. It probes upper/work/lower capabilities, creates work/index directories, assigns fsids and xino policy, checks overlapping layers, initializes root inode/dentry state, and defines superblock/dentry/inode operations.

## Important APIs, types, and functions
Key operations are `ovl_fill_super()`, `ovl_fill_super_creds()`, `ovl_get_upper()`, `ovl_get_workdir()`, `ovl_make_workdir()`, `ovl_get_indexdir()`, `ovl_get_layers()`, `ovl_get_lowerstack()`, `ovl_get_root()`, `ovl_check_overlapping_layers()`, `ovl_sync_fs()`, `ovl_statfs()`, and module init/exit registration. Dentry ops implement `d_real`, strong/weak revalidation, and optional case-insensitive hash/compare. Inode ops allocate, free, destroy, and clean per-inode OverlayFS state.

## Control flow
`ovl_fill_super()` verifies the caller user namespace, sets dentry operations, prepares creator credentials if needed, then runs `ovl_fill_super_creds()` under override creds. The fill path verifies parsed options, allocates layers and lowerdir strings, initializes xino assumptions, sets super operations early for trap inode support, processes upper/workdir if present, builds the lower stack, initializes persistent UUID when requested, creates/validates the index directory if enabled, checks layer overlap, selects export operations, lowers `CAP_SYS_RESOURCE`, sets superblock flags, and builds the root dentry.

Workdir creation probes upper features: directory creation/cleanup, `d_type`, `O_TMPFILE`, `RENAME_WHITEOUT`, OverlayFS xattr support, volatile dirty marker creation, file-handle decode, and NFS-export dependency on index. Missing optional features downgrade config or force read-only; missing required remote-upper features fail the mount.

## State and persistence
Persistent state includes work/index directories under workdir, `work/incompat/volatile/dirty`, index xattrs linking upper root to indexdir, upper root UUID xattr, and root origin verification. In-memory state includes layer cloned mounts, pseudo devices per unique fs, trap inodes, in-use locks, root `ovl_entry`, root flags, export operations, and inode cache objects.

## Dependencies and integration points
It integrates with `params.c` for config and context, `namei.c` for origin/index validation, `readdir.c` for `d_type` and cleanup, `util.c` for xattrs/sync/in-use, and VFS mount/fs_context infrastructure. It registers `ovl_fs_type` with `FS_USERNS_MOUNT` and `kill_anon_super`.

## Risks
Feature downgrades are subtle: xattr/file-handle/d_type/whiteout limitations must not leave config inconsistent. Workdir/index cleanup has persistent data risk. Overlap detection must prevent recursive layer exposure. Volatile mounts must refuse unseen upper writeback errors. Reference ownership during partial mount failures is complex.

## Test signals
Test upperless and upperful mounts, missing workdir, read-only upper, same versus separate upper/work mount, unsupported upper xattrs, remote upper rejection, volatile dirty markers and sync behavior, index creation/cleanup, root origin verification, xino mode decisions, lower UUID conflicts, casefold encoding, export modes, overlap/in-use detection, and unmount cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/util.c -->
# sources/distributed-fs/ceph-client/fs/overlayfs/util.c

## Purpose
`util.c` provides shared OverlayFS utility logic for write access, credential override, stack allocation, dentry/inode path selection, flag management, copy-up synchronization, origin/whiteout/metacopy/redirect/protection xattrs, fs-verity validation, volatile sync status, and copying real inode attributes to overlay inodes.

## Important APIs, types, and functions
Write helpers include `ovl_get_write_access()`, `ovl_start_write()`, `ovl_want_write()`, `ovl_put_write_access()`, `ovl_end_write()`, and `ovl_drop_write()`. Path and state helpers include `ovl_workdir()`, `ovl_override_creds()`, `ovl_can_decode_fh()`, `ovl_indexdir()`, `ovl_index_all()`, `ovl_verify_lower()`, stack alloc/copy/free helpers, `ovl_alloc_entry()`, `ovl_free_entry()`, dentry revalidation helpers, and real path accessors.

Flag and copy-up APIs include `ovl_path_type()`, `ovl_dentry_*`, `ovl_has_upperdata()`, `ovl_set_upperdata()`, `ovl_inode_update()`, `ovl_dir_modified()`, `ovl_copy_up_start()`, `ovl_copy_up_end()`, and `ovl_already_copied_up()`. Xattr/security helpers include `ovl_init_uuid_xattr()`, `ovl_check_setxattr()`, `ovl_set_impure()`, `ovl_check_protattr()`, `ovl_set_protattr()`, in-use locks, `ovl_need_index()`, nlink transaction helpers, metacopy helpers, redirect parsing, fs-verity helpers, `ovl_sync_status()`, and `ovl_copyattr()`.

## Control flow
Copy-up start locks the overlay inode interruptibly, rechecks whether copy-up already happened, and takes upper mount write access; end releases both. Path selection prefers upper where appropriate but can return lower or lowerdata for metacopy/data-only files. Memory barriers pair upperdata/lowerdata publication with readers. Nlink operations may force copy-up for indexed lower aliases, store persistent nlink xattrs before mutation, and clean orphaned index entries when nlink reaches zero.

Xattr helpers use the selected namespace, tolerate missing optional support by downgrading `ofs->noxattr`, and parse strict formats for metacopy, redirect, UUID, and protection attributes. fs-verity validation loads lower verity info if needed and compares stored metacopy digest with actual lower data digest.

## State and persistence
Persistent state includes OverlayFS xattrs for UUID, impure, origin, metacopy, redirect, xwhiteout, nlink, and protattr. In-memory state includes dentry flags stored in `d_fsdata`, inode flags, upper dentry publication, lowerdata publication, directory version, in-use inode state, volatile mount error sequence, and attribute copies.

## Dependencies and integration points
`namei.c`, `readdir.c`, `super.c`, copy-up, dir, inode, fileattr, and export code all use these helpers. External dependencies include VFS write/freeze APIs, exportfs, fs-verity, fileattr, xattrs, idmapped mount helpers, and credentials.

## Risks
Memory ordering mistakes can expose partially initialized upper or lowerdata paths. Xattr format looseness could accept corrupt metadata; overly strict behavior could break upgrades. Copy-up/nlink/index cleanup races can corrupt hardlink accounting. Volatile sync status must preserve data-loss signaling.

## Test signals
Test copy-up races, metacopy data copy-up on write/truncate, lazy lowerdata publication, redirect validation, fs-verity require/on modes, protattr append/immutable preservation, in-use locking, index cleanup after unlink/rename, xattr unsupported upper fallback, idmapped ownership copying, and volatile syncfs error returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/xattrs.c -->
# sources/distributed-fs/ceph-client/fs/overlayfs/xattrs.c

## Purpose
`xattrs.c` implements OverlayFS VFS xattr handlers. It hides private OverlayFS metadata xattrs from users, escapes user-visible names that collide with OverlayFS' own namespace, copies up lower objects before xattr mutation, and selects trusted versus user xattr namespaces based on the `userxattr` mount option.

## Important APIs, types, and functions
Public functions are `ovl_is_private_xattr()`, `ovl_listxattr()`, and `ovl_xattr_handlers()`. Internal helpers classify names with `ovl_is_escaped_xattr()` and `ovl_is_own_xattr()`, perform real get/set/remove through `ovl_xattr_get()` and `ovl_xattr_set()`, filter list results with `ovl_can_list()`, allocate escaped names with `ovl_xattr_escape_name()`, and implement handler callbacks for own namespace and catch-all xattrs.

The handler arrays are `ovl_trusted_xattr_handlers` and `ovl_user_xattr_handlers`; each combines an "own" handler for `trusted.overlay.` or `user.overlay.` and a catch-all handler for all other xattrs.

## Control flow
Getting an xattr resolves the real metadata path via `ovl_i_path_real()` and calls `vfs_getxattr()` under OverlayFS creator credentials. Setting/removing first checks whether removal from a lower-only object is a valid replace by probing the lower xattr. If no upper exists, it copies the dentry up, takes upper write access, then sets or removes the real upper xattr via `ovl_do_setxattr()` or `ovl_do_removexattr()`. After mutation it copies timestamps and size metadata back to the overlay inode.

Listing xattrs reads the real dentry list, removes private OverlayFS metadata xattrs, conditionally exposes non-Overlay trusted xattrs only to init-user-namespace `CAP_SYS_ADMIN`, and unescapes xattrs that were stored as `*.overlay.overlay.<name>` to present the user's original collision name.

## State and persistence
This file mutates persistent xattrs on the upper layer only. Collision escaping protects OverlayFS metadata by storing user requests for `trusted.overlay.*` or `user.overlay.*` under an escaped prefix. It does not own separate in-memory state beyond temporary escaped-name buffers.

## Dependencies and integration points
It relies on namespace constants and upper write helpers from `overlayfs.h`, path helpers from `util.c`, copy-up from `copy_up.c`, and VFS xattr APIs. `super.c` installs the chosen handler array in `sb->s_xattr`.

## Risks
Namespace confusion is the main risk: exposing private xattrs, failing to escape collisions, or choosing the wrong trusted/user prefix could corrupt OverlayFS metadata or leak internals. Copy-up before mutation can fail, and removal semantics must avoid fabricating success for missing lower xattrs.

## Test signals
Test listing hides `overlay.*` metadata, escaped collision round trips, userxattr and trusted modes, unprivileged trusted xattr visibility, set/remove on lower-only files causing copy-up, `XATTR_REPLACE` removal failure when lower xattr is absent, and behavior when upper xattrs are unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/xattrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pidfs.c -->
# sources/distributed-fs/ceph-client/fs/pidfs.c

## Purpose
`pidfs.c` implements the pidfs pseudo filesystem backing pidfds. It gives pidfds real inodes, stable file handles, polling, fdinfo, namespace and info ioctls, optional autokill-on-close, trusted xattrs, and export/open-by-handle support while keeping dentries stashed on `struct pid`.

## Important APIs, types, and functions
Lifecycle APIs include `pidfs_prepare_pid()`, `pidfs_add_pid()`, `pidfs_remove_pid()`, `pidfs_free_pid()`, `pidfs_register_pid()`, `pidfs_alloc_file()`, `pidfs_get_root()`, and `pidfs_init()`. Exit/coredump hooks are `pidfs_exit()` and `pidfs_coredump()`. File operations include `pidfd_poll()`, `pidfd_ioctl()`, `pidfd_show_fdinfo()`, and `pidfs_file_release()`. Export helpers include `pidfs_encode_fh()`, `pidfs_fh_to_dentry()`, `pidfs_export_open()`, and `pidfs_export_permission()`.

`struct pidfs_attr` stores optional simple xattrs and anonymous pidfd attributes: exit cgroup/exit code and coredump mask/signal/code. A global rhashtable maps 64-bit pidfs inode numbers to `struct pid`.

## Control flow
At boot, `pidfs_init()` initializes the rhashtable, creates the attr cache, mounts the pseudo filesystem, and stores the root path. `pidfs_add_pid()` allocates a unique inode number and inserts the pid in the hash; removal deletes it. `pidfs_alloc_file()` creates or reuses a stashed dentry via `path_from_stashed()`, opens it with `O_RDWR`, and preserves internal pidfd flags stripped by `do_dentry_open()`.

Pidfd poll waits on `pid->wait_pidfd` and reports readable/hangup when the task exits without delayed group-leader ambiguity. `PIDFD_GET_INFO` copies requested exit/coredump information from `pidfs_attr`, then live task credentials, cgroup id, ppid/tgid/pid, and supported-mask data when permitted by pid namespace hierarchy. Namespace ioctls fetch task namespace references after ptrace filesystem-credential checks and return namespace fds. File-handle open reconstructs a live pid from inode number, rejects exited or out-of-namespace pids, recreates the stashed path, and opens a pidfd-like file.

## State and persistence
Pidfs is pseudo/in-memory. Persistent-for-lifetime state lives in `struct pid`: `ino`, `pidfs_hash`, `attr`, and stashed dentry. On 64-bit, inode numbers come from a cookie; on 32-bit, the lower 32 bits are `i_ino` and upper 32 bits become `i_generation`. Exit and coredump attributes use write barriers before setting mask bits so readers see all-or-nothing data. Xattrs are stored in `simple_xattrs` under trusted.* and freed synchronously or via llist work when needed.

## Dependencies and integration points
The file integrates with pid allocation/free and task exit, proc fdinfo, cgroups, namespace APIs, ptrace access control, exportfs, pseudo_fs/stashed dentry helpers, anon-inode getattr/setattr behavior, rhashtable, simple xattrs, and pidfd UAPI definitions.

## Risks
Concurrency is central: pid exit races with pidfs registration, file-handle lookup, poll, and info ioctl. Namespace checks must prevent leaking information across pid namespace branches. Exported handles must not resurrect exited tasks. Xattr lazy allocation requires inode locking. `PIDFD_AUTOKILL` release must avoid kthreads/user workers.

## Test signals
Test pidfd inode/generation uniqueness on 32- and 64-bit, poll readiness for thread-group leader cases, fdinfo across pid namespaces, `PIDFD_GET_INFO` before and after exit/coredump, namespace ioctls and ptrace denial, open-by-handle for live/exited/out-of-namespace pids, autokill-on-close, trusted xattr set/list/get/remove, and cleanup after task creation failure with no pidfd.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pidfs.c -->
