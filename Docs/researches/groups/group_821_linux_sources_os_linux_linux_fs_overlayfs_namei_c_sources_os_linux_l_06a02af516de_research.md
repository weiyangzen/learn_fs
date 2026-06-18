# Group Research: group_821_linux_sources_os_linux_linux_fs_overlayfs_namei_c_sources_os_linux_l_06a02af516de

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/namei.c -->
# File Research: sources/os/linux/linux/fs/overlayfs/namei.c

## Purpose

`namei.c` implements overlayfs name lookup and identity verification. It resolves overlay dentries to upper and lower real dentries, follows overlay redirects when allowed, handles whiteouts/opaque directories/metacopy, verifies origin and index file handles, and creates overlay inodes from the resolved backing stack.

## Main Responsibilities

- Validate overlay file-handle buffers stored in `overlay.origin`, `overlay.upper`, and index names.
- Decode origin/index file handles back to real lower or upper dentries.
- Lookup a child in the upper layer and in the ordered lower layer stack.
- Follow relative and absolute overlay redirects, including redirects into data-only lower layers.
- Interpret whiteouts, opaque directories, xwhiteout markers, metacopy files, and overlapping-layer traps.
- Verify lower origin consistency for `index=on`, `nfs_export=on`, and `verify_lower` paths.
- Lookup and verify index-directory entries for copied-up objects and export support.
- Build `struct ovl_entry` lower stacks and pass `struct ovl_inode_params` to `ovl_get_inode()`.
- Lazily resolve lowerdata for metacopy files with absolute data-layer redirects.

## Key Types And State

- `struct ovl_lookup_data`: per-lookup mutable state, including the current layer, name, directory/metacopy/opaque state, redirect buffers, and whether the current redirect is absolute.
- `struct ovl_lookup_ctx`: owns lookup outputs such as upper dentry, lower stack, origin path, index dentry, allocated overlay entry, inode, and stack count.
- `struct ovl_fh` / `struct ovl_fb`: overlay file-handle wire format from `overlayfs.h`.
- `struct ovl_path`: pairs a resolved real dentry with its overlay layer.
- `d->stop`, `d->opaque`, `d->xwhiteouts`, and `d->metacopy`: lookup controls that determine whether lower-layer traversal continues.

## Important Functions

- `ovl_check_fb_len()` validates overlay file-handle body length, magic, version, flags, and endian compatibility.
- `ovl_uuid_match()` checks stored file-handle UUIDs against real layer superblock UUIDs, or requires null UUID when origin UUID storage is disabled.
- `ovl_decode_real_fh()` uses exportfs to decode a stored file handle and rejects unsupported or weird dentries.
- `ovl_lookup_positive_unlocked()` wraps `lookup_one_unlocked()` and converts negative dentries to `-ENOENT`, optionally dropping disposable negative dentries.
- `ovl_lookup_single()` handles one path element in one real layer, applying casefold checks, whiteout detection, metacopy detection, opaque/xwhiteout handling, redirect extraction, and trap checks.
- `ovl_lookup_layer()` resolves either a simple name or an absolute redirected path component by component.
- `ovl_lookup_data_layers()` searches data-only lower layers for a regular-file lowerdata target.
- `ovl_check_origin_fh()` scans lower layers for a decodable origin file handle.
- `ovl_verify_origin_xattr()` and `ovl_verify_set_fh()` compare or set stored origin/upper file-handle xattrs.
- `ovl_verify_index()`, `ovl_lookup_index()`, `ovl_get_index_name*()`, and `ovl_get_index_fh()` implement index-directory lookup and validation.
- `ovl_lookup_layers()` is the core overlay lookup algorithm.
- `ovl_lookup()` is the VFS inode operation entry point.
- `ovl_verify_lowerdata()` performs lazy lowerdata lookup and optional fs-verity validation.
- `ovl_lower_positive()` checks whether an overlay dentry has a positive lower-layer object.

## Lookup Flow

`ovl_lookup()` rejects names longer than the effective maximum component length, initializes lookup state, enters overlay creator credentials, and calls `ovl_lookup_layers()`.

`ovl_lookup_layers()` first searches the upper parent if an upper exists. A positive upper may provide origin metadata, metacopy state, and redirects. If an absolute upper redirect is found, lower lookup restarts from the root lower stack.

The lower traversal walks layer-by-layer from top to bottom. Each candidate lookup rejects unsupported dentries, casefold inconsistencies, whiteouts, trap inodes, and invalid metacopy states. `overlay.opaque=y` stops further lower lookup; `overlay.opaque=x` marks a directory that may contain xwhiteout files. Redirects can rewrite the lookup name and may restart lookup from the root stack.

For metacopy files, only the top metadata object is kept in the lower stack; lookup must eventually find a real data-bearing lower file. When data-only layers are configured and the metacopy redirect is absolute, the lowerdata lookup can be deferred by appending an empty lowerdata slot and storing the redirect string in the overlay inode.

After upper/lower discovery, the code verifies origins when needed, looks up index entries when indexing is enabled, allocates an `ovl_entry`, initializes dentry flags, and calls `ovl_get_inode()`.

## Index And Origin Invariants

Index names are hex-encoded lower origin file handles. Directory index entries carry `overlay.upper` pointing to the real upper directory; non-directory index entries are hardlinks to upper inodes. Index verification rejects malformed names, stale origins, wrong file types, bad whiteouts, orphan entries, and mismatched upper/origin relationships.

Origin mismatch handling is intentionally nuanced. Stale lower handles can be treated as unknown in compatibility paths, but index and NFS export paths require stronger verification to avoid aliasing distinct lower objects into the same overlay inode identity.

## Dependencies And Integration

This file depends on:

- `overlayfs.h` and `ovl_entry.h` for feature predicates, private structures, xattr IDs, and file-handle formats.
- `util.c` for xattr helpers, path accessors, whiteout checks, metacopy helpers, lowerdata publication, fs-verity validation, and credential override.
- `super.c` for mount-time feature choices and layer construction.
- `inode.c` for overlay inode lookup/creation, trap inodes, and nlink helpers.
- `readdir.c` through shared whiteout/xwhiteout and index cleanup semantics.
- VFS/exportfs APIs such as `lookup_one_unlocked()`, `vfs_path_lookup()`, `exportfs_decode_fh()`, and dentry revalidation flags.

## Risk Notes

- Redirect following is security-sensitive because it resembles symlink traversal into lower layers without normal path permission checks; `ovl_check_follow_redirect()` enforces feature gating.
- Index/origin file handles are consistency-critical for hardlinks, NFS export, and stable inode identity.
- Lazy lowerdata publication relies on memory barriers in `ovl_dentry_set_lowerdata()` and `ovl_path_lowerdata()`.
- Casefold consistency is checked during lookup, but offline lower-layer changes can still invalidate assumptions.
- Data-only layer redirects require absolute paths and only accept regular files as lowerdata.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/overlayfs.h -->
# File Research: sources/os/linux/linux/fs/overlayfs/overlayfs.h

## Purpose

`overlayfs.h` is the central private overlayfs header. It defines overlay path-type bits, xattr namespace constants, on-disk metadata formats, feature-mode enums, idmapped upper-layer VFS wrappers, and cross-file function declarations for the overlayfs implementation.

## Main Contents

- Overlay path type bits: upper, merge, and origin.
- Private xattr namespace definitions for `trusted.overlay.*`, `user.overlay.*`, and escaped overlay xattrs.
- Overlay xattr IDs for opaque, redirect, origin, impure, nlink, upper, uuid, metacopy, protattr, and xwhiteout.
- Overlay inode and dentry flag enums.
- Mount option mode enums for redirect, UUID, xino, verity, and fsync behavior.
- File-handle ABI structures `struct ovl_fb` and `struct ovl_fh`.
- Metacopy xattr ABI structure `struct ovl_metacopy`.
- Inline wrappers around upper-layer VFS operations.
- Prototypes for util, lookup, readdir, inode, dir, file, copy-up, export, super, and xattr modules.

## Key Definitions

`struct ovl_fb` is the packed file-handle body stored in xattrs and encoded index names. It includes version, magic, length, flags, fid type, filesystem UUID, and the flexible file identifier array.

`struct ovl_fh` wraps `struct ovl_fb` with padding so the fid area is 32-bit aligned in memory. `OVL_FH_WIRE_OFFSET`, `OVL_FH_LEN()`, and `OVL_FH_FID_OFFSET` describe the in-memory and wire layout.

`struct ovl_metacopy` stores optional fs-verity digest metadata for metadata-only copy-up files. `OVL_METACOPY_MIN_SIZE`, `OVL_METACOPY_MAX_SIZE`, and `ovl_metadata_digest_size()` define its ABI sizing rules.

## VFS Wrapper Helpers

The `ovl_do_*` inline helpers route upper-layer operations through the upper mount idmap and emit debug tracing. They cover:

- metadata changes: `ovl_do_notify_change()`
- directory and file creation/removal: `ovl_do_create()`, `ovl_do_mkdir()`, `ovl_do_mknod()`, `ovl_do_symlink()`, `ovl_do_rmdir()`, `ovl_do_unlink()`
- linking and renaming: `ovl_do_link()`, `ovl_do_rename()`, `ovl_do_rename_rd()`
- xattrs and ACLs: `ovl_do_getxattr()`, `ovl_do_setxattr()`, `ovl_do_removexattr()`, `ovl_do_set_acl()`, `ovl_do_remove_acl()`
- whiteouts and temporary files: `ovl_do_whiteout()`, `ovl_do_tmpfile()`
- upper lookup/create/remove helpers: `ovl_lookup_upper_unlocked()`, `ovl_start_creating_upper()`, `ovl_start_removing_upper()`

The idmap usage is important: upper-layer ownership and mode changes must be interpreted through the upper mount mapping, not the overlay mount.

## Feature Helpers

Inline predicates encode common feature decisions:

- `ovl_redirect_follow()` and `ovl_redirect_dir()`
- `ovl_origin_uuid()` and `ovl_has_fsid()`
- `ovl_xino_warn()`, `ovl_same_fs()`, `ovl_same_dev()`, `ovl_xino_bits()`
- `ovl_should_sync()`, `ovl_should_sync_metadata()`, `ovl_is_volatile()`
- `ovl_allow_offline_changes()`
- `ovl_force_readonly()`

These helpers keep feature checks consistent across lookup, copy-up, readdir, export, mount setup, and sync paths.

## Cross-Module API Surface

The header exposes overlayfs-internal APIs from:

- `util.c`: credential override, write accounting, stack allocation, path resolution, dentry flags, xattrs, copy-up synchronization, metacopy, verity, volatile sync, and attribute copying.
- `namei.c`: file-handle validation, origin/index lookup, lowerdata verification, and lookup operations.
- `readdir.c`: directory operations, merged cache handling, whiteout cleanup, d_type checks, and index/workdir cleanup.
- `inode.c`: permissions, ACLs, inode initialization, nlink accounting, fileattr/protattr support, trap inodes, and attribute updates.
- `dir.c`: create/remove/rename support, temp names, whiteouts, and cleanup.
- `file.c`: regular file operations and fileattr access.
- `copy_up.c`: copy-up flow, xattr copying, origin encoding, and upper attribute setup.
- `export.c`: export operations.
- `super.c`: `ovl_fill_super()`.
- `xattrs.c`: overlay xattr handlers and public xattr operations.

## Risk Notes

- The file-handle and metacopy structures are persistent ABI details; layout changes must preserve compatibility.
- Upper VFS wrapper bypasses can create idmapped mount bugs or permission inconsistencies.
- Private xattr namespace rules must match `xattrs.c` filtering and escaping.
- Feature predicates must stay aligned with `params.c` verification and `super.c` fallback behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/overlayfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/ovl_entry.h -->
# File Research: sources/os/linux/linux/fs/overlayfs/ovl_entry.h

## Purpose

`ovl_entry.h` defines overlayfs private mount, layer, dentry, and inode state. It is the core data model used by lookup, readdir, copy-up, inode operations, xattrs, export, and superblock setup.

## Key Structures

`struct ovl_config` stores effective mount configuration: `upperdir`, `workdir`, lower directory strings, default permissions, redirect mode, verity mode, index, UUID mode, NFS export, xino, metacopy, userxattr, and fsync mode.

`struct ovl_sb` represents a unique underlying superblock. It tracks the real superblock, overlay pseudo device number, whether UUID identity is unusable due to conflicts, and whether the filesystem is used as a lower layer.

`struct ovl_layer` represents one layer. Layer index 0 is reserved for upper. Each layer stores its private mount, trap inode, underlying `ovl_sb`, stack index, fsid, and xwhiteout marker state.

`struct ovl_path` pairs a layer with a real dentry.

`struct ovl_entry` is attached to overlay inodes and contains the counted lower stack.

`struct ovl_fs` is the overlay superblock-private state. It owns layer arrays, unique filesystem records, work/index directories, config strings, creator credentials, feature fallback flags, in-use locks, xino mode, whiteout cache, volatile errseq state, and casefold state.

`struct ovl_inode` wraps a VFS inode. It stores a directory cache or lowerdata redirect, redirect string, version counter, overlay flags, upper dentry, lower entry, and a mutex for copy-up and related transitions.

## Important Inline Helpers

- `ovl_numlowerlayer()` excludes upper and data-only lower layers from the normal lower-layer count.
- `ovl_upper_mnt()` and `ovl_upper_mnt_idmap()` access the upper mount and idmap.
- `OVL_FS()`, `OVL_I()`, `OVL_E()`, and `OVL_I_E()` cast VFS objects to overlay-private state.
- `ovl_numlower()`, `ovl_lowerstack()`, `ovl_lowerpath()`, and `ovl_lowerdata()` access lower-stack entries.
- `ovl_lowerdata_dentry()` reads lazy lowerdata dentries with `READ_ONCE()`.
- `OVL_E_FLAGS()` stores dentry-private flags in `d_fsdata`.
- `ovl_upperdentry_dereference()` reads the upper dentry with `READ_ONCE()`.

## Invariants

- `ofs->layers[0]` is the upper layer slot, even for lower-only overlays.
- Normal lower layers start at index 1.
- Data-only lower layers are included in `numlayer` but excluded from the normal merged lower count.
- `struct ovl_entry` lowerstack entries are ordered from top to bottom.
- The last lowerstack entry may represent lowerdata, and may initially have no dentry when lazy lookup is needed.
- Directory inodes use `ovl_inode.cache`; regular files may use `ovl_inode.lowerdata_redirect`.
- Dentry flags live in `d_fsdata`; inode flags live in `OVL_I(inode)->flags`.

## Integration

`params.c` fills `ovl_config` and `ovl_fs_context`. `super.c` converts parsed paths into `ovl_layer`, `ovl_sb`, and root `ovl_entry` state. `namei.c` builds per-dentry lower stacks. `readdir.c` stores merged directory caches in `ovl_inode.cache`. `util.c` reads and mutates most of the state defined here.

## Risk Notes

- The `ovl_inode` union is mode-dependent; directory and regular-file paths must use the correct member.
- Lazy lowerdata publication depends on memory ordering with `READ_ONCE()` and barriers in `util.c`.
- Layer numbering, fsid numbering, and data-only layer exclusion are easy sources of off-by-one errors.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/ovl_entry.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/params.c -->
# File Research: sources/os/linux/linux/fs/overlayfs/params.c

## Purpose

`params.c` implements overlayfs mount parameter parsing, fs-context initialization/freeing, option dependency verification, reconfigure behavior, and mount option rendering for `/proc/mounts`.

## Main Responsibilities

- Define overlayfs module parameters and default mount-option modes.
- Declare the `fs_parameter_spec` table for old and new mount APIs.
- Parse legacy comma-separated mount data with overlay-specific escaping.
- Parse `lowerdir=`, `lowerdir+`, `datadir+`, `upperdir=`, and `workdir=` layer options.
- Validate layer paths as directories and reject unsupported dentries.
- Enforce consistent casefold state across all layers.
- Maintain `struct ovl_fs_context` lower-layer arrays and path ownership.
- Resolve feature dependencies among redirect, metacopy, index, NFS export, verity, userxattr, UUID, and volatile mode.
- Allocate and initialize `struct ovl_fs` and fs-context private state.
- Free untransferred mount context state on failure.
- Render effective mount options.

## Parameter Model

The file supports these major options:

- layer paths: `lowerdir`, `lowerdir+`, `datadir+`, `upperdir`, `workdir`
- behavior flags: `default_permissions`, `userxattr`, `volatile`, `override_creds`
- mode options: `redirect_dir`, `index`, `uuid`, `nfs_export`, `xino`, `metacopy`, `verity`, `fsync`

`lowerdir=` supports colon-separated lower layers and double-colon-separated data-only layers, for example `lower1:lower2::data1::data2`. `lowerdir+` and `datadir+` are new API forms that can accept file descriptors as well as strings.

## Important Functions

- `ovl_next_opt()` parses old mount option strings while respecting backslash-escaped commas.
- `ovl_parse_param_split_lowerdirs()` splits legacy `lowerdir=` strings and validates colon sequencing.
- `ovl_mount_dir()` and `ovl_mount_dir_noesc()` resolve path strings.
- `ovl_mount_dir_check()` validates directory-ness, casefold consistency, weird dentry rejection, read-only upper rejection, and lower/data ordering constraints.
- `ovl_ctx_realloc_lower()` grows the parsed lower-layer array up to `OVL_MAX_STACK`.
- `ovl_add_layer()` transfers parsed path/name ownership into config or lower-layer context slots.
- `ovl_parse_layer()` handles both string and file-descriptor layer options.
- `ovl_parse_param_lowerdir()` replaces existing lower layers and parses legacy lower/data lower syntax.
- `ovl_parse_param()` handles all fs parameters and stores explicit-option bits in `ctx->set`.
- `ovl_init_fs_context()` allocates context state and sets defaults from module parameters and Kconfig.
- `ovl_free_fs()` releases overlayfs superblock-private resources when mount setup fails or the superblock is destroyed.
- `ovl_fs_params_verify()` resolves cross-option dependencies and permission constraints.
- `ovl_show_options()` prints the effective option set.

## Option Dependency Rules

`ovl_fs_params_verify()` applies several important rules:

- `workdir` and `index=on` are ignored without an upperdir.
- `volatile` is meaningless without an upperdir and is reset to the default.
- `uuid=on` without upperdir falls back to `uuid=null`.
- `metacopy=on` requires `redirect_dir=on`; explicit conflicts fail, while implicit defaults may be adjusted.
- `nfs_export=on` requires index support except in lower-only conditions that require `redirect_dir=nofollow`.
- `nfs_export=on` conflicts with metacopy and verity combinations.
- `userxattr` forces redirect and metacopy off unless explicitly requested in conflicting ways.
- Without `userxattr`, unprivileged callers cannot explicitly request trusted-xattr-dependent redirect, metacopy, verity, or data-only lower layers.

## Mount Context Lifetime

`ovl_init_fs_context()` allocates `struct ovl_fs_context`, preallocates three lower slots, allocates `struct ovl_fs`, sets defaults, installs fs-context operations, and initializes the whiteout mutex.

`ovl_free()` frees the overlayfs private state if it has not been transferred to the superblock and frees parsed path context state. `ovl_free_fs()` releases traps, dentries, in-use locks, cloned mounts, anonymous devices, config strings, credentials, and layer arrays.

## Reconfigure Behavior

`ovl_reconfigure()` preserves old mount API behavior by ignoring remount options. For the new mount API, it rejects option changes. It also prevents remounting read-write when the overlay is forced read-only, and syncs the upper filesystem when transitioning to read-only if needed.

## Risk Notes

- Legacy `lowerdir=` parsing has subtle escaping and colon semantics; incorrect parsing can reorder data-only layers.
- Dependency resolution changes effective options, so `/proc/mounts` must show final config rather than raw user input.
- `override_creds` changes the creator credential used for overlay operations and is restricted to the fsopen user namespace.
- Casefold consistency is enforced at mount parsing and later rechecked during lookup.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/params.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/params.h -->
# File Research: sources/os/linux/linux/fs/overlayfs/params.h

## Purpose

`params.h` declares the overlayfs fs-context and mount-parameter interface shared between `params.c` and `super.c`.

## Main Contents

- Includes fs-context and fs-parser declarations.
- Forward declares `struct ovl_fs` and `struct ovl_config`.
- Exposes `ovl_parameter_spec[]` for filesystem type registration.
- Exposes `ovl_parameter_redirect_dir[]` for redirect option parsing.
- Defines `struct ovl_opt_set`, which records which dependency-sensitive options were explicitly set by the user.
- Defines `OVL_MAX_STACK` as the maximum number of overlay lower/data layers.
- Defines `struct ovl_fs_context_layer`, pairing a user path name with a resolved `struct path`.
- Defines `struct ovl_fs_context`, the mount-parse staging area.

## Key Structures

`struct ovl_opt_set` tracks explicit user requests for `metacopy`, `redirect`, `nfs_export`, and `index`. This lets verification distinguish explicit conflicts from defaults that can be adjusted automatically.

`struct ovl_fs_context` stores parsed upper and work paths, dynamic lower-layer capacity/counts, data-only lower count, explicit-option flags, an array of lower layers, the original legacy `lowerdir` string, and whether casefold state has been established.

## Exported Functions

- `ovl_init_fs_context()` initializes overlayfs fs-context state.
- `ovl_free_fs()` releases `struct ovl_fs`.
- `ovl_fs_params_verify()` validates and resolves mount config dependencies.
- `ovl_show_options()` renders effective mount options.
- `ovl_xino_mode()` returns the string form of the configured xino mode.

## Integration Notes

`params.c` owns parsing and verification. `super.c` consumes the resulting `struct ovl_fs_context` to construct layers, clone mounts, set fsids, configure root state, and register superblock operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/params.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/readdir.c -->
# File Research: sources/os/linux/linux/fs/overlayfs/readdir.c

## Purpose

`readdir.c` implements overlayfs directory iteration, merged directory caching, whiteout filtering, xwhiteout handling, inode-number translation for directory entries, directory fsync/release/open operations, emptiness checks, and work/index directory cleanup.

## Main Responsibilities

- Read directory entries from real upper/lower directories under overlay credentials.
- Merge entries from multiple layers while hiding lower names shadowed by upper names.
- Filter whiteouts and xwhiteout entries from visible results.
- Maintain a per-directory cache for merged directory iteration.
- Translate `d_ino` values so readdir output stays consistent with overlay `stat(2)` behavior where possible.
- Handle casefolded comparison names when the overlay stack is casefolded.
- Support direct iteration of real directories when no merge cache is needed.
- Track and invalidate caches using overlay inode version counters.
- Check whether a merged directory is empty before removal.
- Clean up upper whiteouts, workdir leftovers, and stale/orphan index entries.

## Key Types

- `struct ovl_cache_entry`: one cached directory entry, with visible name, comparison name, real inode, translated inode, type, upper/whiteout/xwhiteout state, and RB-tree/list links.
- `struct ovl_dir_cache`: refcounted merged directory cache with version, list order, and name RB-tree.
- `struct ovl_readdir_data`: callback state used while reading real directories into caches.
- `struct ovl_dir_file`: per-open directory file state, including whether direct real iteration is possible, cached upperfile, realfile, and cursor.
- `struct ovl_readdir_translate`: state for translating real directory iteration into overlay-visible inode numbers.

## Important Functions

- `ovl_casefold()` creates normalized comparison names for casefolded layers.
- `ovl_cache_entry_find*()` manage RB-tree name lookup.
- `ovl_cache_entry_new()` allocates entries and marks candidates needing later inode or xwhiteout checks.
- `ovl_fill_merge()` adds entries during merged directory reads.
- `ovl_fill_lowest()` preserves reasonably stable offsets by inserting lowest-layer entries before upper ones.
- `ovl_check_whiteouts()` performs full lookup of character-device whiteout candidates.
- `ovl_dir_read()` opens and iterates one real directory.
- `ovl_dir_read_merged()` walks all real paths from `ovl_path_next()` and builds a merged cache.
- `ovl_cache_get()` obtains or rebuilds the merged cache if the inode version changed.
- `ovl_cache_update()` resolves delayed inode-number updates and xwhiteout checks.
- `ovl_dir_read_impure()` and `ovl_cache_get_impure()` build a special cache for impure real upper directories.
- `ovl_iterate_real()` directly iterates real dirs while translating `d_ino` when needed.
- `ovl_iterate_merged()` emits entries from the merged cache.
- `ovl_dir_open()`, `ovl_dir_llseek()`, `ovl_dir_fsync()`, and `ovl_dir_release()` implement directory file operations.
- `ovl_check_empty_dir()` verifies merged directory emptiness and collects upper whiteouts for cleanup.
- `ovl_cleanup_whiteouts()` removes selected upper whiteouts.
- `ovl_check_d_type_supported()` probes whether the upper/work filesystem supplies useful `d_type`.
- `ovl_workdir_cleanup()` recursively removes workdir leftovers.
- `ovl_indexdir_cleanup()` validates, removes, or whiteouts index entries during mount.

## Merge And Cache Flow

For merge directories, `ovl_iterate_merged()` obtains a cache via `ovl_cache_get()`. Cache construction reads each real directory in stack order. Upper and higher lower layers populate an RB-tree keyed by visible or casefolded name; lower duplicates are ignored. The lowest layer is inserted through a middle list so offsets are more stable across rebuilds.

Entries marked as whiteouts are skipped during emission. Character device whiteouts are checked after reading, while xwhiteout regular files are checked lazily with `ovl_cache_update()` because detecting them requires a real lookup and xattr check.

The cache is versioned with `ovl_inode_version_get()`. Directory mutations in `util.c` increment the version, causing existing open directory state to drop and rebuild stale caches.

## Inode Number Handling

The file tries to keep `readdir()` `d_ino` consistent with overlay `stat(2)`:

- Lower inode numbers can be remapped with xino bits and fsid.
- Upper entries in impure directories may need lookup/stat to match overlay inode identity.
- `.` and `..` can require recalculation.
- Origin-backed entries may require `vfs_getattr()` on the overlay path.
- If xino overflows, the real inode is used and a warning can be emitted for `xino=on`.

## Real Directory Fast Path

If a directory is real and does not require whiteout filtering or merge behavior, overlayfs can iterate the real file directly. It still may use `ovl_iterate_real()` for inode-number translation when xino is active, the parent is merged, or the directory is impure.

`ovl_dir_real_file()` handles directories that were opened as lower but later copied up, lazily opening and caching the upper real file.

## Workdir And Index Cleanup

`ovl_workdir_cleanup()` removes temporary workdir entries, recursing one level for directories. The special `work/incompat` path aborts mount with a clearer incompatibility error if non-empty.

`ovl_indexdir_cleanup()` scans the index directory at mount, verifies each index entry with `ovl_verify_index()`, removes stale entries, and whiteouts orphan index entries when NFS export needs stale file handles to remain blocked.

## Risk Notes

- Directory offsets are cache-derived for merged dirs and only best-effort stable.
- Casefolded comparison names must be used consistently or duplicate hiding can break.
- Whiteout and xwhiteout detection requires care because some checks are deferred until emission.
- Impure directory caches are not refcounted like merge caches and are rebuilt separately.
- Index cleanup is consistency-critical; aborting mount is preferred over continuing with incompatible index state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/readdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/super.c -->
# File Research: sources/os/linux/linux/fs/overlayfs/super.c

## Purpose

`super.c` implements overlayfs superblock operations, filesystem registration, inode cache management, dentry revalidation, mount setup, upper/work/index directory preparation, layer/fsid construction, xino setup, overlap detection, and root dentry creation.

## Main Responsibilities

- Register the `overlay` filesystem type and inode slab cache.
- Provide superblock operations for inode allocation/free/destruction, sync, statfs, option display, and teardown.
- Implement dentry operations including `d_real()`, strong revalidation, weak revalidation, and case-insensitive hashing/comparison when needed.
- Validate and clone upper, work, lower, and data-only layer mounts.
- Probe upper/work filesystem capabilities such as xattrs, `d_type`, `O_TMPFILE`, `RENAME_WHITEOUT`, and file handles.
- Create or clean the workdir and indexdir.
- Allocate unique fsids and pseudo devices for underlying filesystems.
- Configure xino and persistent UUID behavior.
- Detect overlapping layers and in-use upper/work/lower paths.
- Construct the root overlay inode and dentry.
- Choose export operations depending on NFS export and file-handle availability.

## Important Functions

- `ovl_d_real()` returns the real backing dentry for data or metadata users, including lazy lowerdata lookup for metacopy data.
- `ovl_revalidate_real()` and `ovl_dentry_revalidate_common()` forward revalidation to upper and lower real dentries.
- `ovl_alloc_inode()`, `ovl_destroy_inode()`, and `ovl_free_inode()` manage `struct ovl_inode` lifetime.
- `ovl_sync_fs()` syncs the upper filesystem unless volatile sync status allows skipping.
- `ovl_statfs()` delegates statfs to the real root path and adjusts overlay type/name length/fsid.
- `ovl_workdir_create()` creates or cleans `work`/`index` directories under workbasedir.
- `ovl_lower_dir()` checks lower namelen, stack depth, file-handle support, and xino implications.
- `ovl_get_upper()` validates and clones upperdir, sets traps, inherits `SB_NOSEC`, and applies in-use locking.
- `ovl_check_rename_whiteout()` probes `RENAME_WHITEOUT` support.
- `ovl_make_workdir()` creates workdir and probes upper/work features, applying feature fallbacks.
- `ovl_get_workdir()` enforces upper/work same-mount and separate-subtree constraints.
- `ovl_get_indexdir()` verifies upper root origin, creates/opens indexdir, verifies index ownership xattrs, and invokes index cleanup.
- `ovl_get_fsid()` assigns per-underlying-filesystem fsids and detects conflicting/null UUID risks.
- `ovl_get_layers()` clones lower mounts, marks them read-only/noatime, assigns fsids, and sets casefold encoding.
- `ovl_get_lowerstack()` validates lower/data layer counts and builds the root lower stack.
- `ovl_check_overlapping_layers()` detects overlap with traps and in-use markers.
- `ovl_get_root()` creates and initializes the root overlay inode/dentry.
- `ovl_fill_super_creds()` performs the main mount construction under overlay credentials.
- `ovl_fill_super()` verifies user namespace, prepares credentials, and calls the credentialed setup.

## Mount Setup Flow

`ovl_fill_super()` sets dentry operations, prepares creator credentials if absent, and runs `ovl_fill_super_creds()` under those credentials.

`ovl_fill_super_creds()` verifies parsed parameters, allocates layer and lowerdir arrays, initializes superblock basics, and configures xino defaults. If an upperdir is present, it validates upperdir, checks volatile upper writeback error state, prepares workdir, and uses the upper superblock stack depth/time granularity.

The lower stack is then validated and converted into cloned private mounts. If persistent UUID/fsid support is enabled, the upper root UUID xattr may be initialized. If indexing is enabled and the mount is writable, the indexdir is created and cleaned. Overlapping layers are checked before final feature fallbacks and export operation selection.

Finally the function installs superblock flags and xattr handlers, creates the root dentry with `ovl_get_root()`, and leaves `ofs` attached to `sb->s_fs_info`.

## Upper/Work Feature Fallbacks

`ovl_make_workdir()` probes required and optional upper/work capabilities. Missing xattr support disables or downgrades redirect, metacopy, index, UUID, and xino where needed. Missing `d_type`, `O_TMPFILE`, or `RENAME_WHITEOUT` is warned for local filesystems, but remote upper filesystems must satisfy stricter requirements. File-handle absence disables index if required and contributes to `nofh`.

Volatile mounts create `work/incompat/volatile/dirty` so future mounts can detect incompatible dirty volatile state.

## Layer And Identity Model

Layer index 0 is upper. Lower layers are cloned private mounts and forced read-only/noatime. Regular lower layers receive fsids tied to unique underlying superblocks. Data-only layers share a special null fsid after normal lower fsids and are excluded from the merged root lower stack.

`ovl_get_fsid()` rejects or marks bad UUID situations that would make origin file-handle decoding ambiguous. This can force fallback from xino/index/NFS export to safer modes.

## Root Initialization

`ovl_get_root()` creates a directory inode, chooses the root inode number/fsid from upper or top lower, marks root as a merge directory with whiteout support, sets connected and upperdata flags, detects xwhiteout markers on lower roots, initializes inode state, installs dentry revalidation flags, and takes an upper dentry reference.

## Risk Notes

- Mount setup intentionally falls back for some feature failures but aborts for unsafe combinations such as remote upper missing required features.
- In-use and trap checks protect against overlapping layers and concurrent upper/work reuse; disabling index weakens exclusive protection.
- UUID conflicts can break origin decoding, so the code disables dependent features when ambiguity is detected.
- `d_real(D_REAL_DATA)` can trigger lazy lowerdata lookup and warns if no real data dentry can be found.
- Workdir/indexdir cleanup occurs during mount and must avoid corrupting valid index state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/util.c -->
# File Research: sources/os/linux/linux/fs/overlayfs/util.c

## Purpose

`util.c` provides shared overlayfs helper logic for write access, credential override, file-handle capability probing, stack allocation, real path selection, dentry/inode flags, copy-up synchronization, xattr naming, metacopy and fs-verity validation, volatile sync status, in-use locks, nlink/index cleanup, and idmapped attribute copying.

## Main Responsibilities

- Wrap upper mount write access and freeze protection helpers.
- Override credentials with the overlay creator credentials.
- Detect whether underlying filesystems can decode file handles.
- Allocate, copy, free, and release lower stacks and overlay entries.
- Propagate real dentry revalidation flags to overlay dentries.
- Reject unsupported backing dentries.
- Compute overlay path type and select real upper/lower/lowerdata paths.
- Publish lazy lowerdata dentries with correct memory ordering.
- Manage overlay dentry and inode flags.
- Track upperdata state for metacopy/data-copy-up decisions.
- Synchronize copy-up transactions and nlink-sensitive operations.
- Implement private overlay xattr names and xattr fallback behavior.
- Handle impure directories, protection attributes, xwhiteouts, metacopy xattrs, redirects, and fs-verity digests.
- Check volatile sync status and copy real inode attributes into overlay inodes with idmap translation.

## Important Functions

- `ovl_get_write_access()`, `ovl_want_write()`, `ovl_start_write()`, and matching put/drop/end helpers manage upper write access.
- `ovl_override_creds()` applies creator credentials to overlayfs real filesystem operations.
- `ovl_can_decode_fh()` checks exportfs file-handle decode support and detects generic 32-bit inode encoding.
- `ovl_indexdir()`, `ovl_index_all()`, and `ovl_verify_lower()` expose feature predicates.
- `ovl_stack_alloc()`, `ovl_stack_cpy()`, `ovl_stack_put()`, `ovl_stack_free()`, `ovl_alloc_entry()`, and `ovl_free_entry()` manage lower stack storage.
- `ovl_dentry_init_flags()` propagates revalidation requirements from real dentries.
- `ovl_dentry_weird()` rejects backing dentries that overlayfs cannot safely stack.
- `ovl_path_type()`, `ovl_path_upper()`, `ovl_path_lower()`, `ovl_path_lowerdata()`, `ovl_path_real()`, and `ovl_path_realdata()` select backing paths.
- `ovl_dentry_set_lowerdata()` publishes lazy lowerdata after data-layer lookup.
- `ovl_inode_update()` installs an upper dentry after copy-up and hashes the overlay inode if needed.
- `ovl_dir_modified()` copies attributes and increments directory version counters.
- `ovl_path_is_whiteout()` detects both native whiteouts and xattr whiteouts.
- `ovl_path_open()` performs permission checks before opening real paths.
- `ovl_copy_up_start()` and `ovl_copy_up_end()` serialize copy-up and hold upper write access.
- `ovl_init_uuid_xattr()` loads or creates persistent overlay UUID xattrs.
- `ovl_set_impure()` marks upper directories that may contain copied-up entries.
- `ovl_check_protattr()` and `ovl_set_protattr()` translate immutable/append-only protection state through overlay xattrs.
- `ovl_inuse_trylock()`, `ovl_inuse_unlock()`, and `ovl_is_inuse()` manage `I_OVL_INUSE`.
- `ovl_nlink_start()` and `ovl_nlink_end()` synchronize persistent nlink/index updates.
- `ovl_check_metacopy_xattr()` and `ovl_set_metacopy_xattr()` parse and store metacopy metadata.
- `ovl_get_redirect_xattr()` validates redirect xattr syntax.
- `ovl_validate_verity()` and `ovl_get_verity_digest()` compare/store fs-verity digests for metacopy files.
- `ovl_sync_status()` reports whether sync is required or a volatile mount has observed upper writeback errors.
- `ovl_copyattr()` copies mode, ownership, timestamps, and size from the real inode with mount idmap conversion.

## Path And Data Selection

`ovl_path_type()` classifies an overlay dentry as upper-backed, merged, and/or origin-backed. Directory and metacopy cases determine whether reads should use upper, lower metadata, or lowerdata.

`ovl_path_lowerdata()` reads the lowerdata dentry and layer with explicit memory barriers paired with `ovl_dentry_set_lowerdata()`. This supports lazy lowerdata lookup for data-only layers without exposing a dentry before its layer pointer is visible.

## Copy-Up And Upperdata State

`ovl_has_upperdata()` and `ovl_set_upperdata()` use memory barriers so consumers see data-copy effects before the upperdata flag. `ovl_dentry_needs_data_copy_up()` decides whether write/truncate opens require data copy-up. `ovl_already_copied_up()` provides a lockless fast path with documented false-negative tolerance.

`ovl_copy_up_start()` locks the overlay inode and obtains upper write access unless another path already completed copy-up. `ovl_copy_up_end()` releases both.

## Xattrs And Metadata

`ovl_xattr_table` maps internal xattr IDs to either `trusted.overlay.*` or `user.overlay.*` names depending on mount configuration. `ovl_check_setxattr()` records missing xattr support and returns caller-selected fallback errors.

Metacopy helpers treat an empty metacopy xattr as a valid minimal marker and validate non-empty format versions and sizes. Redirect helpers require absolute redirects to have non-empty path components and relative redirects to contain no slashes.

## Index And Nlink Handling

`ovl_need_index()` requests indexing for lower hardlinks, directories under index-all behavior, and NFS-export consistency. `ovl_nlink_start()` may copy up indexed lower objects before whiteout/rename operations so persistent nlink state can be stored. `ovl_cleanup_index()` removes or whiteouts orphan index entries when overlay nlink drops to zero.

## Risk Notes

- Memory ordering around upperdata and lowerdata state is subtle and required for lockless readers.
- `ovl_dentry_weird()` defines what backing dentries are safe; relaxing it could expose automount or custom hash/compare issues.
- Persistent nlink/index cleanup is consistency-critical for hardlinks and NFS export.
- Volatile mounts rely on errseq sampling; missed writeback errors would violate sync semantics.
- Protection attributes intentionally avoid setting immutable/append-only on upper inodes directly.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/xattrs.c -->
# File Research: sources/os/linux/linux/fs/overlayfs/xattrs.c

## Purpose

`xattrs.c` implements overlayfs xattr get/set/list handling. It forwards public xattrs to real backing dentries, copies up lower-only objects before mutation, filters private overlay xattrs from user-visible lists, and supports escaped overlay xattr names so users can store names that would otherwise collide with overlayfs private metadata.

## Main Responsibilities

- Distinguish overlay-private xattrs from user-visible escaped xattrs.
- Forward xattr get operations to the current real backing path.
- Copy up lower-only objects before setting or removing xattrs.
- Require existing lower xattr presence before removing xattrs from lower-only objects.
- Filter private overlay xattrs from `listxattr()`.
- Expose escaped private-prefix xattrs as ordinary names by stripping the escape marker.
- Provide handler sets for `trusted.overlay.*` mode and `user.overlay.*` mode.

## Important Functions

- `ovl_is_escaped_xattr()` detects xattrs using the doubled overlay escape prefix.
- `ovl_is_own_xattr()` detects xattrs in overlayfs' configured private namespace.
- `ovl_is_private_xattr()` returns true for overlay-private metadata xattrs, excluding escaped names.
- `ovl_xattr_get()` selects the real path with `ovl_i_path_real()` and calls `vfs_getxattr()` under overlay credentials.
- `ovl_xattr_set()` copies up if needed, obtains upper write access, and sets or removes the xattr on the upper real dentry.
- `ovl_can_list()` filters private xattrs and restricts trusted xattr visibility to capable callers.
- `ovl_listxattr()` lists real xattrs, removes private overlay names, and unescapes escaped overlay names in place.
- `ovl_xattr_escape_name()` builds an escaped private-prefix xattr name.
- `ovl_own_xattr_get()` and `ovl_own_xattr_set()` access escaped names for overlay-owned prefixes.
- `ovl_other_xattr_get()` and `ovl_other_xattr_set()` pass through all other xattrs.
- `ovl_xattr_handlers()` selects trusted or user handler arrays based on `ofs->config.userxattr`.

## Xattr Escaping Model

Overlayfs reserves `trusted.overlay.*` or `user.overlay.*` for its own metadata. To let users access an xattr with the same apparent prefix, the handler maps it to an escaped name by inserting another `overlay.` segment after the namespace prefix. Listing reverses this by removing `OVL_XATTR_ESCAPE_PREFIX` from escaped entries while hiding true private entries.

## Copy-Up Behavior

When setting an xattr on a lower-only object, overlayfs copies the object up first and then mutates the upper dentry. When removing an xattr from a lower-only object, it first checks whether the lower real xattr exists; if not, the remove fails without copying up. After a successful mutation, overlay inode attributes are refreshed with `ovl_copyattr()`.

## Risk Notes

- Private xattr filtering must exactly match the namespace rules used by `util.c`.
- Escaped-name length can exceed `XATTR_NAME_MAX`, in which case operations return `-EOPNOTSUPP`.
- Removing xattrs from lower-only objects has intentionally different behavior from setting because it avoids unnecessary copy-up if the xattr is absent.
- Trusted xattr listing is gated by `CAP_SYS_ADMIN` in the initial user namespace.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/overlayfs/xattrs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/pidfs.c -->
# File Research: sources/os/linux/linux/fs/pidfs.c

## Purpose

`pidfs.c` implements the kernel pseudo filesystem backing pidfds. It gives pidfds stable inode/file identity, poll and ioctl behavior, namespace-fd access, pidfd information retrieval, export-by-file-handle support, trusted xattrs, and lifecycle integration with `struct pid` allocation, task exit, coredump reporting, and pid cleanup.

## Main Responsibilities

- Mount and initialize the internal `pidfs` pseudo filesystem.
- Allocate stable pidfs inode numbers for `struct pid`.
- Maintain an inode-number-to-`struct pid` rhashtable for file-handle decode.
- Create pidfd files from stashed pidfs dentries.
- Provide pidfd file operations: poll, ioctl, release, and proc fdinfo display.
- Expose process namespace file descriptors via pidfd ioctls.
- Expose structured pidfd information through `PIDFD_GET_INFO`.
- Record exit and coredump information in pidfs attributes.
- Support exportfs file handles for live pidfds.
- Provide simple trusted xattr storage tied to pidfs attributes.
- Handle delayed freeing of xattrs after `struct pid` teardown.

## Key Types And Globals

- `pidfs_root_path`: root path of the internal pidfs mount.
- `pidfs_attr_cachep`: slab cache for `struct pidfs_attr`.
- `pidfs_xa_cache`: cache for simple xattr objects.
- `pidfs_ino_ht`: rhashtable keyed by `struct pid.ino`.
- `PIDFS_PID_DEAD`: sentinel used when a pid can no longer be registered with pidfs.
- `struct pidfs_anon_attr`: stores exit and coredump information exposed by pidfd info APIs.
- `struct pidfs_attr`: owns simple xattrs plus anonymous pidfd attributes, or an llist node while queued for deferred free.

## Inode Number Handling

On 64-bit systems, `pidfs_alloc_ino()` uses a cookie generator and the full 64-bit value is the inode number. The generation number is zero.

On 32-bit systems, the 64-bit pidfs identifier is split: lower 32 bits become `i_ino` and upper 32 bits become `i_generation`. If the lower 32 bits wrap to zero, allocation skips forward so inode numbering restarts at one. Userspace can reconstruct stronger identity from inode plus generation or file handles.

`pidfs_add_pid()` assigns an inode number and inserts the pid into `pidfs_ino_ht`; `pidfs_remove_pid()` removes it.

## Pidfd File Operations

`pidfs_file_operations` provides:

- `pidfd_poll()`: waits on `pid->wait_pidfd` and reports readable/hangup state after process exit, avoiding premature notification for delayed group leaders.
- `pidfd_ioctl()`: handles pidfd ioctls.
- `pidfs_file_release()`: implements `PIDFD_AUTOKILL` by sending `SIGKILL` to the target thread group when the pidfd is closed.
- `pidfd_show_fdinfo()`: under procfs, prints `Pid:` and `NSpid:` from the procfs instance pid namespace perspective.

`pidfd_pid()` verifies that a file really uses pidfs file operations before returning its `struct pid`.

## PIDFD_GET_INFO

`pidfd_info()` implements the extensible `PIDFD_GET_INFO` ioctl. It validates userspace struct size, copies the requested mask, rejects tasks outside the caller's pid namespace hierarchy, and returns requested or unconditional fields.

It can report:

- pid/tgid/ppid identifiers
- real/effective/saved/fs uid/gid values mapped into the caller's user namespace
- cgroup id
- exit code and exit cgroup id when exit info is available
- coredump policy/result, signal, and code
- supported mask for feature discovery

If the task has already been reaped, only stored exit information may be available. Memory barriers pair with exit/coredump writers so users see complete stored records.

## Namespace Ioctls

`pidfd_ioctl()` supports namespace accessors for cgroup, IPC, mount, network, pid-for-children, time, time-for-children, UTS, user, and pid namespaces when the corresponding kernel config exists. It obtains the target task, snapshots or references the namespace, checks `ptrace_may_access()` with filesystem credentials, and returns an opened namespace fd via `open_namespace()`.

It also handles `FS_IOC_GETVERSION` by returning the pidfs inode generation number.

## Exit And Coredump State

`pidfs_exit()` runs during task exit. If no pidfd ever registered the pid, it marks `pid->attr` as `PIDFS_PID_DEAD` so later pidfs registration fails instead of creating pidfds for a reaped task without exit info. If attributes exist, it records cgroup id and exit code, issues a write barrier, and sets the exit bit.

`pidfs_coredump()` records coredump mask, signal, and code, then sets the coredump bit after a write barrier.

`pidfs_free_pid()` frees pidfs attributes when the pid is freed. If xattrs are present, it queues the attribute object onto a lockless list and schedules work to free simple xattrs safely.

## Pseudo Filesystem And Dentries

`pidfs_init_fs_context()` initializes a pseudo filesystem with `PID_FS_MAGIC`, `DCACHE_DONTCACHE`, pidfs super operations, export operations, dentry operations, xattr handlers, and stashed-dentry operations.

`pidfs_dname()` returns `anon_inode:[pidfd]` for compatibility with userspace tools that historically saw pidfds as anonymous inodes.

`pidfs_stash_dentry()` ensures the pid is registered before stashing a dentry in `pid->stashed`. `pidfs_alloc_file()` obtains the stashed path, opens it as `O_RDWR`, preserves pidfd-specific internal flags that normal open handling strips, and returns the pidfd file.

## Exportfs Support

`pidfs_encode_fh()` encodes the 64-bit pidfs inode number into a two-word file handle. `pidfs_fh_to_dentry()` decodes live pids by looking up the inode number in `pidfs_ino_ht`, rejecting dead/exited/out-of-namespace pids, and recreating the stashed dentry path.

`pidfs_export_permission()` validates `open_by_handle_at()` flags and relies on pid namespace hierarchy checks in pid lookup. `pidfs_export_open()` normalizes flags and opens pidfds as read-write.

## Xattrs

Pidfs supports trusted xattrs using `simple_xattr_*()` helpers. `pidfs_xattr_get()` and `pidfs_xattr_set()` access xattrs stored in `pid->attr->xattrs`; setting expects the inode lock to serialize list mutation. `pidfs_listxattr()` lists xattrs through the inode operations.

## Initialization

`pidfs_init()` initializes the inode rhashtable, creates the `pidfs_attr_cache`, mounts the internal pseudo filesystem with `kern_mount()`, and stores its root path for later use by pidfs callers.

## Risk Notes

- `pid->attr` has sentinel, NULL, and allocated states; races with exit are synchronized with `pid->wait_pidfd.lock`.
- Exit and coredump information uses memory barriers so readers observe complete records.
- File-handle decode must not resurrect exited or namespace-invisible pids.
- Namespace ioctls require ptrace-style access checks before exposing namespace fds.
- `PIDFD_AUTOKILL` close behavior is intentionally restricted away from kthreads and user workers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/pidfs.c -->