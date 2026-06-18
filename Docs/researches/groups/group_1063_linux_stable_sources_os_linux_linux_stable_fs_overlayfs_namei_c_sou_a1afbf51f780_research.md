# Group Research: group_1063_linux_stable_sources_os_linux_linux_stable_fs_overlayfs_namei_c_sou_a1afbf51f780

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/overlayfs/namei.c

## Purpose

`namei.c` implements overlayfs lookup, origin/index file-handle verification, redirect following, metacopy lower-data discovery, and helper traversal over overlay path layers. It is the main name-resolution path that turns an overlay dentry name into an overlay inode backed by an optional upper dentry and one or more lower dentries.

## Main Responsibilities

- Validate and decode overlay file-handle xattrs used for origin/index identity.
- Lookup names in upper and lower layers while respecting whiteouts, opaque dirs, redirects, xwhiteouts, metacopy, casefold state, and trap inodes.
- Resolve data-only lower layers through absolute lowerdata redirects, with lazy lowerdata lookup on first access.
- Verify origin/index consistency for `index=on` and `nfs_export=on`.
- Instantiate overlay inodes with `ovl_get_inode()` and initialize dentry revalidation flags.
- Provide layer iteration through `ovl_path_next()` and lower existence probing through `ovl_lower_positive()`.

## Key Types And State

- `struct ovl_lookup_data`: per-lookup mutable state, including current layer, name, type flags, opaque/stop state, redirect buffers, metacopy state, and whether the active redirect is absolute.
- `struct ovl_lookup_ctx`: lifetime container for lookup outputs: upper dentry, lower stack, origin path, index dentry, overlay entry, inode, and lower count.
- `struct ovl_fh` / `struct ovl_fb`: overlay file-handle formats defined in `overlayfs.h` and validated here.
- Lower stack entries use `struct ovl_path` from `ovl_entry.h`.

## Important Functions

- `ovl_check_fb_len()` validates origin/index file-handle buffers, treating unknown versions, unknown flags, and endian mismatch as "origin unknown" (`-ENODATA`) rather than fatal corruption.
- `ovl_uuid_match()` checks whether a stored file-handle UUID matches a candidate layer superblock, or requires null UUID when origin UUID storage is disabled.
- `ovl_decode_real_fh()` decodes a real lower/upper dentry from a file handle using exportfs and rejects weird dentries.
- `ovl_check_origin_fh()` scans lower layers for a decodable origin and fills a one-entry `ovl_path`.
- `ovl_verify_set_fh()` and `ovl_verify_origin_xattr()` compare xattr file handles against encoded real dentries, optionally setting missing xattrs.
- `ovl_index_upper()`, `ovl_verify_index()`, `ovl_get_index_name*()`, `ovl_get_index_fh()`, and `ovl_lookup_index()` implement index directory validation and lookup.
- `ovl_lookup_layer()` and `ovl_lookup_single()` perform path lookup within one real layer, including redirect, whiteout, opacity, metacopy, and trap checks.
- `ovl_lookup_layers()` coordinates complete upper/lower lookup and builds the overlay inode inputs.
- `ovl_lookup()` is the exported inode operation lookup entry.
- `ovl_verify_lowerdata()` performs lazy lowerdata lookup and fs-verity digest validation.
- `ovl_lower_positive()` checks whether a dentry has a positive lower entry despite upper state.

## Lookup Flow

`ovl_lookup()` rejects names longer than `ofs->namelen`, enters overlay credentials, and calls `ovl_lookup_layers()`.

`ovl_lookup_layers()` first searches the upper parent if present. A found upper dentry may provide an origin xattr and may carry redirect or metacopy state. If the upper lookup finds an absolute redirect, lookup restarts against the root lower stack.

The lower-stack pass walks each lower layer from top to bottom. Each layer lookup rejects unsupported objects, validates casefold consistency, handles whiteouts, treats `overlay.opaque=y` as a stop marker, treats `overlay.opaque=x` as an xwhiteout directory marker, and follows valid redirects when allowed. Metacopy entries are kept only when they are meaningful for the topmost metadata object; lower data is required before lookup succeeds.

When data-only lower layers are configured, an absolute lowerdata redirect can defer final data lookup. The inode stores the redirect and later `ovl_verify_lowerdata()` resolves it with `ovl_lookup_data_layers()`.

If an origin is known and indexing is enabled, `ovl_lookup_index()` validates the index entry against the current upper/origin pair. The final inode parameters include upper dentry, lower stack, index flag, redirect, and optional lazy lowerdata redirect. Dentry flags are initialized after inode creation.

## Index And Origin Invariants

Index entry names are hex-encoded lower origin file handles. Directory index entries carry an upper file-handle xattr pointing at the associated upper dir, while non-directory index entries are hardlinks to upper inodes. `ovl_verify_index()` rejects malformed names, stale origins, incompatible types, bad whiteouts, and orphan entries; NFS export tightens verification.

Origin verification is deliberately nuanced: stale lower handles can be treated as unknown in non-fatal cases, but explicit mismatches during index or NFS export paths become stale/error outcomes to avoid aliasing corruption.

## Dependencies And Integration

This file depends heavily on:

- `util.c` for xattr helpers, whiteout checks, redirect/metacopy helpers, lowerdata setters, copy-up state, and fs-verity validation.
- `super.c` mount-time feature choices such as `index`, `metacopy`, `redirect_mode`, `nfs_export`, `uuid`, `xino`, and data-only layer layout.
- `inode.c` for `ovl_get_inode()`, origin trap checks, inode initialization, and nlink helpers.
- `readdir.c` indirectly through xwhiteout and whiteout semantics.
- VFS/exportfs/namei APIs such as `lookup_one_unlocked()`, `vfs_path_lookup()`, `exportfs_decode_fh()`, and dentry revalidation flags.

## Risk Notes

- Redirect following is security-sensitive because it can expose lower paths without normal path permission checks; `ovl_check_follow_redirect()` enforces mount-feature gating.
- Index/origin xattrs are consistency-critical for NFS export and hardlink identity.
- Lazy lowerdata lookup uses memory ordering through `ovl_dentry_set_lowerdata()` in `util.c`; consumers must respect those helpers.
- Casefold consistency is enforced during lookup, but offline lower modifications can still invalidate assumptions.
- Stale lower file handles are sometimes tolerated to preserve compatibility, so feature combinations that require strong identity rely on mount-time checks and index verification.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/overlayfs.h -->
# File Research: sources/os/linux/linux-stable/fs/overlayfs/overlayfs.h

## Purpose

`overlayfs.h` is the central private overlayfs interface. It defines overlay path/xattr/file-handle constants, small VFS wrapper helpers, feature-mode enums, and cross-file function declarations used by overlayfs implementation files.

## Main Contents

- Overlay path-type bits: upper, merge, and origin.
- Overlay private xattr namespace definitions for `trusted.overlay.*` and `user.overlay.*`.
- Overlay xattr IDs such as opaque, redirect, origin, impure, nlink, upper, uuid, metacopy, protattr, and xwhiteout.
- Inode and dentry flag enums for overlay-private state.
- Mount option mode enums for redirect, UUID, xino, verity, and fsync behavior.
- Overlay file-handle wire formats: `struct ovl_fb` and `struct ovl_fh`.
- Metacopy xattr format: `struct ovl_metacopy`.
- Inline wrappers around upper-layer VFS operations with proper mount idmapping.
- Prototypes for utility, lookup, readdir, inode, directory, file, copy-up, export, super, and xattr operations.

## Key Definitions

`struct ovl_fb` is the packed file-handle body stored in xattrs or index names. It includes version, magic, length, flags, fid type, UUID, and a flexible fid array.

`struct ovl_fh` wraps `ovl_fb` with padding so the fid is aligned in memory. Macros such as `OVL_FH_LEN()` and `OVL_FH_FID_OFFSET` describe its in-memory/wire layout.

`struct ovl_metacopy` stores optional fs-verity digest metadata for metadata-only copy-up files. `ovl_metadata_digest_size()` derives digest length from the encoded xattr size.

## VFS Wrapper Helpers

The `ovl_do_*` helpers wrap real upper VFS operations:

- `ovl_do_notify_change()`
- `ovl_do_rmdir()`
- `ovl_do_unlink()`
- `ovl_do_link()`
- `ovl_do_create()`
- `ovl_do_mkdir()`
- `ovl_do_mknod()`
- `ovl_do_symlink()`
- `ovl_do_setxattr()`
- `ovl_do_removexattr()`
- `ovl_do_rename()`
- `ovl_do_whiteout()`
- `ovl_do_tmpfile()`

These consistently use `ovl_upper_mnt_idmap(ofs)` and emit debug traces. This is important for idmapped upper mounts: ownership/mode changes must be interpreted through the upper mount mapping.

## Feature Helpers

Inline helpers encode common feature predicates:

- `ovl_redirect_follow()` and `ovl_redirect_dir()`
- `ovl_origin_uuid()` and `ovl_has_fsid()`
- `ovl_xino_warn()`, `ovl_same_fs()`, `ovl_same_dev()`, `ovl_xino_bits()`
- `ovl_should_sync()`, `ovl_should_sync_metadata()`, `ovl_is_volatile()`
- `ovl_allow_offline_changes()`
- `ovl_force_readonly()`

These are used across lookup, mount setup, copy-up, readdir, export, and sync paths.

## Cross-Module API Surface

This header is the contract between overlayfs compilation units. Notable exported-internal areas:

- `util.c`: stack allocation, path selection, flags, xattrs, whiteouts, metacopy, verity, sync, credential override, and inode attribute copying.
- `namei.c`: file-handle validation, origin/index lookup, lowerdata verification, lookup entry point.
- `readdir.c`: directory operations, merged dir cache, cleanup helpers.
- `inode.c`: permissions, ACLs, inode initialization, fileattr/protattr handling.
- `dir.c`: creation, cleanup, temp names, whiteout cleanup.
- `file.c`: regular file operations and fileattr get/set.
- `copy_up.c`: copy-up and origin encoding.
- `export.c`: export operations.
- `super.c`: `ovl_fill_super()`.
- `xattrs.c`: xattr handlers and overlay get/set/list operations.

## Risk Notes

- This header centralizes subtle idmap and credential semantics; bypassing the wrappers can create ownership or permission bugs.
- File-handle and metacopy layout constants are on-disk/on-wire ABI details.
- The many feature predicates must remain consistent with `params.c` verification and `super.c` fallback behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/overlayfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/ovl_entry.h -->
# File Research: sources/os/linux/linux-stable/fs/overlayfs/ovl_entry.h

## Purpose

`ovl_entry.h` defines overlayfs private mount, layer, dentry, and inode state structures. It is the data model used by the rest of overlayfs.

## Key Structures

`struct ovl_config` stores user-visible and effective mount configuration:

- `upperdir`, `workdir`, and `lowerdirs`
- `default_permissions`
- redirect, verity, index, UUID, NFS export, xino, metacopy, userxattr, and fsync modes

`struct ovl_sb` tracks each unique underlying superblock, its pseudo device number, UUID conflict state, and whether it is used as a lower layer.

`struct ovl_layer` represents one overlay layer. Layer index 0 is reserved for upper. Each layer stores a private mount, trap inode, underlying `ovl_sb`, stack index, fsid, and xwhiteout marker state.

`struct ovl_path` pairs a layer with a real dentry.

`struct ovl_entry` is attached to overlay inodes and contains the counted lower stack.

`struct ovl_fs` is overlay superblock private state. It owns layer arrays, unique fs records, work/index dirs, config strings, creator credentials, feature fallbacks, in-use locks, xino mode, whiteout cache, volatile errseq, and casefold state.

`struct ovl_inode` wraps a VFS inode and stores directory cache or lowerdata redirect, redirect string, version, overlay flags, upper dentry, lower entry, and a mutex for copy-up and related transitions.

## Important Inline Helpers

- `ovl_numlowerlayer()` excludes upper and data-only layers.
- `ovl_upper_mnt()` and `ovl_upper_mnt_idmap()` access upper layer mount/idmap.
- `OVL_FS()`, `OVL_I()`, `OVL_E()`, and `OVL_I_E()` cast VFS objects to overlay-private state.
- `ovl_lowerstack()`, `ovl_lowerpath()`, and `ovl_lowerdata()` access lower stack entries.
- `ovl_lowerdata_dentry()` allows lazy lowerdata entries to be absent.
- `OVL_E_FLAGS()` stores dentry-private flags in `d_fsdata`.
- `ovl_upperdentry_dereference()` reads the upper dentry through `READ_ONCE()`.

## Invariants

- `ofs->layers[0]` is upper when present; lower layers start at index 1.
- Data-only lower layers are part of `numlayer` but excluded from normal merged lower count.
- `struct ovl_entry` lowerstack order is top-to-bottom for merge lookup; its last entry can represent lowerdata.
- Directory inodes use `ovl_inode.cache`; regular files may use `ovl_inode.lowerdata_redirect`.
- Dentry flags live in `d_fsdata`, while inode flags live in `OVL_I(inode)->flags`.

## Integration

Every file in this group relies on these structures. `params.c` fills config and fs-context state; `super.c` builds `ovl_fs`, layers, and root `ovl_entry`; `namei.c` creates per-dentry lower stacks; `readdir.c` caches merged directory entries in `ovl_inode.cache`; `util.c` reads and mutates most of the private state.

## Risk Notes

- The union in `ovl_inode` is type-dependent; directory and regular-file paths must not use the wrong member.
- Lazy lowerdata uses memory-ordering assumptions around the lowerdata `ovl_path`.
- Layer numbering and data-only layer accounting are easy sources of off-by-one errors.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/ovl_entry.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/params.c -->
# File Research: sources/os/linux/linux-stable/fs/overlayfs/params.c

## Purpose

`params.c` implements overlayfs mount parameter parsing, fs-context setup/freeing, remount behavior, option verification, and `/proc/mounts` option rendering.

## Main Responsibilities

- Define module defaults for redirect, xino, index, NFS export, and metacopy.
- Define fs parameter specs for legacy and new mount APIs.
- Parse `lowerdir`, `lowerdir+`, `datadir+`, `upperdir`, `workdir`, and feature options.
- Resolve file/string layer inputs into paths and store display names.
- Enforce layer ordering and casefold consistency while parsing.
- Verify cross-option constraints after parsing.
- Free fs-context and overlayfs mount state on failure.
- Render effective mount options with `ovl_show_options()`.

## Parsing Details

`ovl_parameter_spec[]` accepts:

- `lowerdir`
- `lowerdir+`
- `datadir+`
- `upperdir`
- `workdir`
- `default_permissions`
- `redirect_dir`
- `index`
- `uuid`
- `nfs_export`
- `userxattr`
- `xino`
- `metacopy`
- `verity`
- `fsync`
- `volatile`
- `override_creds`

Legacy monolithic parsing uses `ovl_next_opt()` to split comma-separated options while honoring escaped commas.

`ovl_parse_param_lowerdir()` handles colon-separated legacy `lowerdir=`. Single `:` separates merged lower layers; double `::` transitions into data-only layers. It rejects malformed colon sequences, trailing colons, too many layers, regular lower layers after data layers, and appending via a leading colon.

`ovl_parse_layer()` supports both string paths and file parameters. New `lowerdir+` and `datadir+` use unescaped path lookup, while legacy `lowerdir` supports backslash unescaping.

## Layer Validation

`ovl_mount_dir_check()` ensures parsed paths are directories, are not weird/unsupported dentries, and have consistent casefold state across all layers. For upper/work paths, it rejects read-only mounts and unsupported `DCACHE_OP_REAL` upper filesystems. For lower additions, it enforces `OVL_MAX_STACK`, prevents mixing legacy `lowerdir` with new add options, and prevents regular lowers after data lowers.

## Option Verification

`ovl_fs_params_verify()` normalizes and rejects incompatible feature combinations:

- `workdir` and `index=on` are ignored without upperdir.
- `volatile` is meaningless without upperdir.
- `uuid=on` without upperdir falls back to `uuid=null`.
- `metacopy=on` requires `redirect_dir=on`, unless explicit conflicting options require disabling or erroring.
- `nfs_export=on` requires index and conflicts with metacopy/verity.
- `userxattr` disables default redirect/metacopy behavior and rejects explicit incompatible options.
- Without trusted-xattr privileges, explicit redirect/metacopy/verity/data-only lower requests are rejected unless `userxattr` is used.

## Context Lifecycle

`ovl_init_fs_context()` allocates `struct ovl_fs_context`, default lower capacity, and `struct ovl_fs`, installs default feature modes, sets fs-context operations, and initializes the whiteout mutex.

`ovl_free()` frees untransferred overlay state and fs-context layer paths/names. `ovl_free_fs()` releases traps, dentries, locks, mounts, pseudo devices, config strings, creator credentials, and the overlay fs object.

`ovl_reconfigure()` largely preserves historical remount behavior, allowing old API options to be ignored but rejecting new mount API changes. It forces read-only consistency and syncs upper fs when transitioning to read-only if required.

## Option Display

`ovl_show_options()` prints the effective lower/upper/work options and only prints feature options when they differ from defaults or are explicitly relevant. It distinguishes legacy `lowerdir` from `lowerdir+`/`datadir+`.

## Dependencies And Integration

`params.c` feeds `super.c` through `struct ovl_fs_context` and `struct ovl_config`. It relies on `overlayfs.h` feature helpers, `ovl_dentry_casefolded()`, `ovl_dentry_weird()`, and `ovl_free_fs()`.

## Risk Notes

- Mount option interactions are feature-critical; a permissive fallback can silently disable index/NFS/xino semantics.
- Escaping and `:` parsing in `lowerdir=` is compatibility-sensitive.
- `override_creds` changes creator credentials and must remain aligned with user namespace checks in `super.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/params.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/params.h -->
# File Research: sources/os/linux/linux-stable/fs/overlayfs/params.h

## Purpose

`params.h` declares overlayfs fs-context parsing structures and mount-parameter APIs shared between `params.c` and `super.c`.

## Main Definitions

- `ovl_parameter_spec[]`: parameter spec table consumed by VFS fs-parser.
- `ovl_parameter_redirect_dir[]`: redirect mode constant table exposed for parsing.
- `struct ovl_opt_set`: tracks whether selected options were explicitly set by the user, allowing `params.c` to distinguish automatic fallback from explicit conflicts.
- `OVL_MAX_STACK`: maximum total lower layer count, set to 500.
- `struct ovl_fs_context_layer`: stores a parsed layer name and resolved `struct path`.
- `struct ovl_fs_context`: stores parsed upper/work paths, lower layer array/capacity/counts, explicit option set, raw legacy lowerdir string, and casefold initialization state.

## Declared Functions

- `ovl_init_fs_context()`
- `ovl_free_fs()`
- `ovl_fs_params_verify()`
- `ovl_show_options()`
- `ovl_xino_mode()`

## Integration Notes

`super.c` consumes `struct ovl_fs_context` to allocate layers, clone mounts, build root lower stacks, and set up work/index dirs. `params.c` owns allocation, parsing, verification, and cleanup of this context.

## Risk Notes

The `nr` and `nr_data` fields are central to regular lower vs data-only lower semantics. Any user must preserve the invariant that data-only layers are counted in `nr` and also in the suffix count `nr_data`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/params.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/readdir.c -->
# File Research: sources/os/linux/linux-stable/fs/overlayfs/readdir.c

## Purpose

`readdir.c` implements overlayfs directory iteration. It builds merged directory views from upper/lower layers, suppresses hidden entries via whiteouts, handles xwhiteouts, maintains per-directory read caches, adjusts exposed inode numbers, supports direct real-dir iteration when possible, and cleans work/index directories.

## Main Types

- `struct ovl_cache_entry`: one directory entry in a merged cache, with original and casefolded names, real and exposed inode numbers, d_type, upper/whiteout/xwhiteout flags, list node, and rb-tree node.
- `struct ovl_dir_cache`: cached merged entries plus version and refcount.
- `struct ovl_readdir_data`: temporary state for reading real dirs into overlay cache structures.
- `struct ovl_dir_file`: per-open directory file state, including whether iteration can use a real dir directly, cached upperfile, merged cache, and cursor.

## Directory Cache Flow

For merged directories, `ovl_cache_get()` returns a valid cache if the inode version matches. Otherwise it allocates a cache and calls `ovl_dir_read_merged()`.

`ovl_dir_read_merged()` iterates overlay paths from upper through lower layers using `ovl_path_next()`. Upper and intermediate layers insert into an rb-tree to suppress duplicates. The lowest layer is inserted ahead of upper entries to keep offsets more stable.

Whiteouts are filtered through two mechanisms:

- Character-device whiteouts are tracked as possible whiteouts and later checked with `ovl_check_whiteouts()`.
- xwhiteouts are checked lazily for regular zero-sized files in directories marked by `overlay.opaque=x`.

Casefold-enabled overlays use `utf8_casefold()` and compare casefolded names in the rb-tree.

## Iteration Paths

`ovl_iterate()` chooses among three paths:

- `ovl_iterate_merged()` for merge dirs or dirs with whiteouts.
- `ovl_iterate_real()` for direct real-dir iteration with inode-number translation where needed.
- Direct `iterate_dir()` on the real file when no adjustment is needed.

`ovl_dir_is_real()` allows direct iteration only when the overlay inode does not have `OVL_WHITEOUTS`.

`ovl_dir_reset()` invalidates a per-open cache if the overlay inode version changed, and transitions from real to merged iteration if a directory was copied up.

## Inode Number Handling

`ovl_cache_update()` resolves deferred inode numbers for upper entries, xwhiteout checks, and xino remapping. It can call overlay lookup and `vfs_getattr()` to keep `d_ino` consistent with `st_ino` for origin-backed entries.

`ovl_remap_lower_ino()` maps lower inode numbers into fsid-specific high-bit ranges when xino is active. It warns on overflow if `xino=on`.

`ovl_iterate_real()` uses `struct ovl_readdir_translate` to adjust `..`, impure upper entries, and lower xino mappings during direct real iteration.

## File Operations

`ovl_dir_operations` provides:

- `open`: opens the current real dir backing the overlay dir.
- `iterate_shared`: wrapped `ovl_iterate()`.
- `llseek`: delegates to real dir if possible, otherwise seeks within the merged cache.
- `fsync`: syncs the upper real dir when one exists and sync is not skipped.
- `release`: drops cache, real files, and per-open state.
- `read`: `generic_read_dir`.
- `setlease`: `generic_setlease`.

`ovl_dir_real_file()` returns the real dir file and lazily opens/caches the upper file if a lower dir was copied up after open.

## Cleanup Helpers

`ovl_check_empty_dir()` builds a merged view to determine whether a directory is empty, preserving upper whiteouts for later cleanup.

`ovl_cleanup_whiteouts()` removes selected upper whiteouts.

`ovl_workdir_cleanup()` and `ovl_workdir_cleanup_recurse()` clean stale workdir entries, with special handling for `work/incompat` feature markers.

`ovl_indexdir_cleanup()` scans indexdir entries, verifies each index entry, removes stale entries, and whiteouts orphan entries when NFS export requires stale handle blocking.

## Dependencies And Integration

This file depends on lookup/path helpers from `namei.c`, state helpers from `util.c`, cleanup/create helpers from `dir.c`, and mount feature state from `super.c`/`params.c`.

## Risk Notes

- Directory offsets are cache-position based for merged dirs, so cache invalidation through inode versioning is essential.
- Whiteout and xwhiteout filtering must be correct to avoid exposing hidden lower files.
- xino overflow handling affects user-visible inode identity.
- Work/index cleanup runs during mount setup and can determine whether a mount is allowed to proceed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/readdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/overlayfs/super.c

## Purpose

`super.c` implements overlayfs filesystem registration, superblock setup, layer construction, work/index directory setup, mount-time feature probing, dentry/inode/super operations, and teardown.

## Main Responsibilities

- Register the `overlay` filesystem and allocate overlay inode cache.
- Implement overlay superblock operations.
- Define overlay dentry operations, including `d_real()` and revalidation.
- Validate and clone upper/lower mounts into private overlay mounts.
- Create and validate workdir/indexdir.
- Probe upper/lower filesystem capabilities.
- Build layer arrays, fsid mapping, xino mode, and root overlay inode.
- Select export operations for NFS/exportfs support.
- Enforce stacking-depth and overlapping-layer constraints.

## Dentry And Inode Operations

`ovl_d_real()` returns the real dentry for regular-file data or metadata, using lazy lowerdata verification for metacopy data paths. It recurses through stacked lower filesystems with `d_real()`.

`ovl_dentry_revalidate_common()` delegates revalidation/weak revalidation to all real upper/lower dentries attached to an overlay dentry.

`ovl_alloc_inode()`, `ovl_destroy_inode()`, and `ovl_free_inode()` manage `struct ovl_inode` state, including upper dentry refs, lower stacks, directory caches, redirect strings, and mutexes.

`ovl_super_operations` includes inode allocation/free/destruction, `inode_just_drop`, `put_super`, `sync_fs`, `statfs`, and `show_options`.

## Workdir And Upper Setup

`ovl_get_upper()` validates upperdir, checks namelen, creates a trap inode, clones a private upper mount, strips atime mount flags, inherits `SB_NOSEC`, and takes the in-use lock.

`ovl_get_workdir()` requires workdir and upperdir to be on the same mount and separate subtrees. It locks workbasedir, sets a trap, and calls `ovl_make_workdir()`.

`ovl_make_workdir()` creates/cleans `work/`, validates d_type, tmpfile support, `RENAME_WHITEOUT`, overlay xattr support, file-handle support, and volatile dirty markers. It downgrades features such as redirect, metacopy, index, UUID, and xino when upper capabilities are insufficient.

`ovl_get_indexdir()` turns `index/` into the active workdir when indexing is enabled, verifies root origin/upper xattrs, and invokes `ovl_indexdir_cleanup()`.

## Lower Layer And Fsid Setup

`ovl_lower_dir()` probes namelen, stack depth, file-handle support, and inode encoding. It can disable index/NFS/xino when lower filesystems cannot support required file-handle behavior.

`ovl_get_fsid()` assigns unique fsids to underlying superblocks, checks UUID conflicts, allocates pseudo devices, and marks UUID conflicts that disable file-handle decoding features.

`ovl_get_layers()` allocates fs records, reserves fsid 0 for upper, clones private lower mounts as read-only/noatime, assigns traps, assigns fsid/layer indexes, preserves lowerdir display strings, and validates encoding consistency.

`ovl_get_lowerstack()` validates lower counts, checks all lowers, enforces stack-depth limit, builds root lowerstack excluding data-only layers, and records `numdatalayer`.

## Root And Superblock Setup

`ovl_fill_super()` ensures the current user namespace matches the fs-context namespace, sets dentry operations, prepares creator credentials if needed, enters overlay credentials, and calls `ovl_fill_super_creds()`.

`ovl_fill_super_creds()` verifies options, allocates layers/config lowerdir array, initializes xino mode, sets super operations early for traps, sets up upper/work/lower/index state, checks overlapping layers, chooses export operations, lowers `CAP_SYS_RESOURCE`, sets superblock flags and xattr handlers, and creates the root dentry with `ovl_get_root()`.

`ovl_get_root()` creates a directory inode, chooses root ino/fsid from upper or top lower, marks root merge/whiteout/connected/upperdata flags, detects xwhiteout markers in lower roots, initializes inode state, and installs dentry flags.

## Export And Sync Behavior

If `nfs_export=on`, `sb->s_export_op` is `ovl_export_operations`. If all layers support file handles but NFS export is off, `ovl_export_fid_operations` is used for non-decodable handle support.

`ovl_sync_fs()` skips real sync on volatile clean mounts, otherwise syncs upper fs during wait phase.

## Risk Notes

- Mount setup contains many feature downgrades; reports in `/proc/mounts` reflect effective behavior, not necessarily requested behavior.
- Workdir cleanup and indexdir cleanup can delete stale internal entries and must never target user data outside validated work/index dirs.
- Overlapping layer traps prevent recursive/self-overlay corruption.
- UUID/fsid and xino decisions affect persistent inode identity and export correctness.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/util.c -->
# File Research: sources/os/linux/linux-stable/fs/overlayfs/util.c

## Purpose

`util.c` provides shared overlayfs helpers for write access, credential override, file-handle capability probing, lower-stack allocation, path selection, dentry/inode flags, whiteout/xattr checks, copy-up synchronization, nlink/index cleanup, metacopy and fs-verity support, volatile sync state, and inode attribute copying.

## Main Functional Areas

### Write And Credential Helpers

`ovl_get_write_access()`, `ovl_put_write_access()`, `ovl_start_write()`, `ovl_end_write()`, `ovl_want_write()`, and `ovl_drop_write()` wrap upper mount/superblock write access.

`ovl_override_creds()` switches to the overlay creator credentials for underlying filesystem access.

### File Handle And Index Feature Helpers

`ovl_can_decode_fh()` checks whether a filesystem supports exportfs decode and whether it uses generic 32-bit inode file handles.

`ovl_indexdir()`, `ovl_index_all()`, and `ovl_verify_lower()` expose index/NFS feature decisions to lookup and copy-up paths.

### Stack And Entry Helpers

`ovl_stack_alloc()`, `ovl_stack_cpy()`, `ovl_stack_put()`, `ovl_stack_free()`, `ovl_alloc_entry()`, and `ovl_free_entry()` manage lower path arrays and references.

### Dentry And Path Helpers

`ovl_path_type()` classifies an overlay dentry as upper, merge, and/or origin. `ovl_path_upper()`, `ovl_path_lower()`, `ovl_path_lowerdata()`, `ovl_path_real()`, and `ovl_path_realdata()` choose the real backing path.

`ovl_dentry_upper()`, `ovl_dentry_lower()`, `ovl_dentry_lowerdata()`, `ovl_dentry_real()`, and inode equivalents expose upper/lower/real backing objects.

`ovl_dentry_set_lowerdata()` installs lazily resolved lowerdata with memory barriers so readers see layer and dentry consistently.

### Flags And Cache State

The file implements dentry flags for opacity, xwhiteouts, and upper alias state, and inode flags for upperdata, impure dirs, index, verity digest state, and related features.

`ovl_dir_modified()` copies attributes and increments directory version when needed. `ovl_inode_version_get()` supports readdir cache invalidation.

### Whiteout, Xattr, UUID, And Protattr Helpers

`ovl_is_whiteout()` and `ovl_path_is_whiteout()` detect device whiteouts and xattr whiteouts.

`ovl_init_uuid_xattr()` loads or creates the persistent overlay UUID xattr when configured, with fallback to `uuid=null`.

`ovl_xattr_table` maps overlay-private xattr IDs to trusted or user namespaces.

`ovl_check_setxattr()` centralizes xattr feature fallback behavior.

`ovl_set_impure()` marks upper dirs that may contain non-pure entries.

`ovl_check_protattr()` and `ovl_set_protattr()` preserve append/immutable semantics through `overlay.protattr` instead of applying those flags directly to upper inodes during copy-up.

### Copy-Up And Nlink Synchronization

`ovl_already_copied_up()` and locked variant check whether copy-up/data copy-up is still needed.

`ovl_copy_up_start()` locks the overlay inode and takes upper write access unless the object is already copied up. `ovl_copy_up_end()` releases both.

`ovl_need_index()` decides whether copy-up should create/use an index entry.

`ovl_nlink_start()` and `ovl_nlink_end()` synchronize link/unlink/rename operations with copy-up and persistent union nlink accounting. `ovl_cleanup_index()` removes or whiteouts orphaned index entries when overlay nlink reaches zero.

### Metacopy And Verity

`ovl_check_metacopy_xattr()` reads and validates metacopy xattrs, accepting empty xattrs as a valid minimal metacopy marker.

`ovl_set_metacopy_xattr()` writes metacopy metadata, optimizing empty digest/flag state to a zero-length xattr.

`ovl_is_metacopy_dentry()` identifies metadata-only copy-up files.

`ovl_get_redirect_xattr()` validates redirect xattrs, allowing absolute redirect paths with sane components and relative redirects without slashes.

`ovl_ensure_verity_loaded()`, `ovl_validate_verity()`, and `ovl_get_verity_digest()` integrate fs-verity digest validation for metacopy lowerdata.

### Sync And Attribute Copying

`ovl_sync_status()` returns whether sync should proceed, be skipped for clean volatile mounts, or fail due to upper writeback errors.

`ovl_copyattr()` mirrors ownership, mode, times, and size from the selected real inode into the overlay inode, applying the real mount idmap.

## Risk Notes

- Memory barriers around `OVL_UPPERDATA`, upper dentry publication, and lowerdata publication are important for lockless readers.
- `ovl_get_redirect_xattr()` is security-sensitive because redirects influence lower path traversal.
- Index cleanup manipulates persistent identity state and must stay synchronized with copy-up/nlink updates.
- `ovl_copyattr()` must remain idmap-aware to avoid incorrect ownership reporting.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/xattrs.c -->
# File Research: sources/os/linux/linux-stable/fs/overlayfs/xattrs.c

## Purpose

`xattrs.c` implements overlayfs xattr handlers. It filters overlay-private xattrs from users, supports escaped access to private-looking xattrs, triggers copy-up for xattr mutation, and selects trusted vs user overlay xattr namespaces.

## Main Behavior

Overlayfs private xattrs use either `trusted.overlay.*` or `user.overlay.*` depending on `ofs->config.userxattr`. These are internal metadata and should not normally be exposed as ordinary xattrs.

The file distinguishes:

- Own/private overlay xattrs: current overlay namespace prefix.
- Escaped xattrs: names with an extra `overlay.` escape segment that represent user-visible xattrs whose names would otherwise collide with overlay private metadata.

`ovl_is_private_xattr()` returns true for own overlay xattrs that are not escaped.

## Get/Set Flow

`ovl_xattr_get()` resolves the real backing path for an overlay inode and calls `vfs_getxattr()` under overlay credentials.

`ovl_xattr_set()` selects upper if present or lower otherwise. Removing an xattr from a lower-only object first checks that the xattr exists, then copies up before mutating. All set/remove operations target the upper real dentry and use `ovl_want_write()`/`ovl_drop_write()`. After mutation it calls `ovl_copyattr()` to refresh ctime/mtime and other copied attributes.

## Listing Flow

`ovl_listxattr()` lists real xattrs, then edits the returned list in place:

- Private overlay xattrs are removed.
- Non-trusted xattrs are listed normally.
- Trusted non-overlay xattrs are listed only for `CAP_SYS_ADMIN`.
- Escaped overlay xattrs are unescaped by removing the escape segment from the listed name.

The implementation validates xattr list entry lengths and returns `-EIO` on malformed underlying xattr lists.

## Xattr Handler Sets

The file defines two handler arrays:

- Trusted mode: own trusted overlay handler plus catch-all other handler.
- User mode: own user overlay handler plus catch-all other handler.

`ovl_xattr_handlers(ofs)` returns the active handler set based on `userxattr`.

Own overlay handler get/set operations escape names before delegating, so users can intentionally access xattrs that would otherwise conflict with overlay metadata.

## Dependencies

This file relies on:

- `ovl_i_dentry_upper()`, `ovl_dentry_lower()`, `ovl_i_path_real()`, and `ovl_dentry_real()` from shared overlay state helpers.
- `ovl_copy_up()` to ensure mutations happen on upper.
- `ovl_do_setxattr()`, `ovl_do_removexattr()`, `ovl_want_write()`, and `ovl_copyattr()`.

## Risk Notes

- Incorrect private-xattr filtering can expose or corrupt overlay metadata.
- Copy-up before xattr mutation is required to avoid modifying lower layers.
- Escaping rules must stay consistent with namespace prefix constants in `overlayfs.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/overlayfs/xattrs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/pidfs.c -->
# File Research: sources/os/linux/linux-stable/fs/pidfs.c

## Purpose

`pidfs.c` implements the kernel pidfs pseudo filesystem used to back pidfds with real inodes, stable inode/file-handle identity, pidfd polling, pidfd info ioctls, namespace-opening ioctls, pidfd xattrs, and lifecycle hooks for process exit/coredump metadata.

## Main State

- `pidfs_root_path`: root path of the kernel-mounted pidfs instance.
- `pidfs_attr_cachep`: cache for per-pid pidfs attributes.
- `pidfs_ino_ht`: rhashtable mapping 64-bit pidfs inode numbers to `struct pid`.
- `struct pidfs_attr`: per-pid state containing simple xattrs and anonymous pidfd metadata.
- `struct pidfs_anon_attr`: exit and coredump fields exposed by `PIDFD_GET_INFO`.

`PIDFS_PID_DEAD` marks a `struct pid` that was reaped before pidfs registration could provide exit metadata.

## Inode Number Model

On 64-bit systems, pidfs inode numbers are generated as 64-bit cookies and exposed directly.

On 32-bit systems, the lower 32 bits become `i_ino` and upper 32 bits become `i_generation`; zero lower bits are skipped on wraparound. This lets users reconstruct a wider identity using inode plus generation or file handles.

`pidfs_add_pid()` allocates an inode number and inserts the pid into the rhashtable. `pidfs_remove_pid()` removes it.

## Pidfd File Operations

`pidfs_file_operations` provides:

- `poll`: `pidfd_poll()` wakes for process exit, avoiding premature thread-group leader notifications.
- `show_fdinfo`: `pidfd_show_fdinfo()` under procfs, printing `Pid` and `NSpid`.
- `unlocked_ioctl`: `pidfd_ioctl()`.
- `compat_ioctl`: `compat_ptr_ioctl`.
- `release`: `pidfs_file_release()`, which optionally sends `SIGKILL` for `PIDFD_AUTOKILL`.

`pidfd_pid()` validates that a file is a pidfs pidfd and returns its `struct pid`.

## PIDFD_GET_INFO

`pidfd_info()` implements the extensible `PIDFD_GET_INFO` ioctl. It validates structure size, copies the requested mask, restricts information to the caller's pid namespace hierarchy, and returns supported subsets:

- pid/tgid/ppid
- credentials mapped into current user namespace
- cgroup id
- exit code
- coredump mask/signal/code
- supported mask

Exit and coredump info are read from `pidfs_attr` with memory barriers so users see complete records or no record.

## Namespace Ioctls

`pidfd_ioctl()` validates pidfd ioctl commands and supports namespace-opening ioctls for cgroup, IPC, mount, network, pid-for-children, time, UTS, user, and pid namespaces. It gets the target task, checks ptrace read access with filesystem credentials, takes namespace references, and returns namespace file descriptors via `open_namespace()`.

`FS_IOC_GETVERSION` returns inode generation, which matters especially on 32-bit inode identity.

## Exit And Coredump Hooks

`pidfs_exit()` runs during task release. If no pidfd ever registered the pid, it marks the pid dead so future pidfs registration fails. Otherwise it records cgroup id and exit code, then sets the exit bit after a write memory barrier.

`pidfs_coredump()` records coredump disposition, signal, and code, then sets the coredump bit after a write memory barrier.

`pidfs_free_pid()` frees or defers freeing pidfs attributes. If xattrs exist, freeing is queued through an llist and work item so simple xattrs can be released safely.

## Pseudo Filesystem And Export

Pidfs is initialized as a pseudo filesystem with `init_pseudo()`, `PID_FS_MAGIC`, noexec/nodev flags, non-cached dentries, pidfs super ops, export ops, dentry ops, and trusted xattr handlers.

Export support includes:

- `pidfs_encode_fh()`: encodes the 64-bit pidfs inode number.
- `pidfs_fh_to_dentry()`: resolves a handle through the inode rhashtable and stashed dentry mechanism.
- `pidfs_export_permission()`: validates open flags for `open_by_handle_at()`.
- `pidfs_export_open()`: opens pidfd handles as pidfd files.

`pidfs_ino_get_pid()` rejects missing, unregistered, exited, or namespace-invisible pids.

## Dentry And Inode Handling

Pidfs uses stashed dentries to give pidfds stable dentries/inodes. `pidfs_stash_dentry()` ensures pidfs registration before stashing.

`pidfs_init_inode()` initializes inode private data, flags, operations, file operations, inode number, and generation.

`pidfs_evict_inode()` clears the inode and drops the pid reference.

Dentry names are reported as `anon_inode:[pidfd]` to preserve existing userspace expectations such as `lsof`.

## Xattr Support

Pidfs allows trusted xattrs through simple xattr storage. `pidfs_xattr_set()` lazily allocates the xattr container under inode lock, and `pidfs_xattr_get()` / `pidfs_listxattr()` read it. This is intentionally narrow and paired with anon-inode-style setattr/getattr behavior.

## Initialization

`pidfs_init()` initializes the inode rhashtable, creates the pidfs attribute slab cache, kernel-mounts pidfs, and records the root path.

## Risk Notes

- Exit/coredump info publication relies on memory ordering around attr bits.
- Namespace ioctl access control depends on pid namespace visibility plus ptrace filesystem-credential checks.
- File-handle reopen must reject stale/exited pids to avoid resurrecting invalid pidfds.
- `PIDFD_AUTOKILL` release behavior is powerful and intentionally excludes kernel threads/user workers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/pidfs.c -->