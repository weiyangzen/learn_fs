# Group Research: group_473_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_h_1b39c2fbfcb5

Scope verified against `Docs/research_subset_a.md`. All eight listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_vnops.c

## Role

Implements vnode operations for illumos HSFS, the High Sierra / ISO-9660 read-only filesystem. The file covers ordinary vnode entry points, directory reading, symlink handling, memory mapping/page-cache integration, and a custom read scheduler for slow optical media.

## Major Responsibilities

- Exposes the `hsfs_vnodeops_template` vnode operation table.
- Implements read-only file access through `hsfs_read`, `hsfs_getpage`, `hsfs_getapage`, and `hsfs_putpage`.
- Implements metadata and namespace VOPs: getattr, lookup, readdir, readlink, fid, access, seek, fsync, close, inactive.
- Supports mmap of regular files while rejecting shared writable mappings.
- Maintains hsnode lifecycle, vnode inactive cleanup, and page-cache invalidation behavior.
- Contains HSFS-specific physical I/O scheduling and readahead for CD/DVD-style media.

## Key Functions

- `hsfs_read()`: Performs regular and directory file reads through `segmap_getmapflt()`, carefully clipping reads to EOF and `MAXBSIZE`-aligned windows.
- `hsfs_getattr()`: Converts `hs_dirent` metadata into `vattr`, including timestamps, device numbers for special nodes, block counts, and sequence number.
- `hsfs_lookup()`: Handles empty name and `"."`, then delegates actual directory search to `hs_dirlook()`.
- `hsfs_readdir()`: Reads raw HSFS directory blocks, validates directory entry lengths, parses entries with `hs_parsedir()`, translates names and inode choices into `dirent64`, and handles Rock Ridge symlink/inode cases.
- `hsfs_readlink()`: Returns the symlink target stored in the hsnode directory entry.
- `hsfs_inactive()`: Releases the vnode reference and either frees the hsnode immediately or moves it through HSFS free-node handling depending on cached pages.
- `hsfs_getpage()` and `hsfs_getapage()`: Provide VM/page-cache page-in support, reject writes, compute sequential readahead, handle ISO-9660 interleaving and extended attribute record offsets, and issue block reads.
- `hsfs_getpage_ra()` and `hsfs_ra_task()`: Implement semi-asynchronous readahead using the HSFS scheduler and taskq cleanup.
- `hsfs_putpage()` and `hsfs_putapage()`: Handle page invalidation/freeing for a read-only filesystem; dirty HSFS pages are treated as impossible and forced to error/invalidate.
- `hsfs_map()`, `hsfs_addmap()`, `hsfs_delmap()`: Support read-only mmap and track mapping counts for mandatory locking checks.
- `hsfs_frlock()`: Delegates to generic file locking but disallows mandatory locking if mapped.
- `hsched_init()`, `hsched_fini()`, `hsched_invoke_strategy()`, `hsched_enqueue_io()`: Implement the custom HSFS read scheduler.

## HSFS I/O Scheduler

The scheduler is designed around slow optical media. It stores queued read requests in two AVL trees:

- `read_tree`: ordered by logical block number for C-LOOK/elevator behavior.
- `deadline_tree`: ordered by request timestamp, then block, to avoid starvation.

`hsched_invoke_strategy()` picks either the next C-LOOK request or an expired-deadline request, coalesces adjacent I/O where worthwhile, and dispatches to `bdev_strategy()`. Coalesced reads use a synthetic buffer and copy completed bytes into the original page-backed buffers before signaling their semaphores.

Important scheduler state:

- `hio_cache` and `hio_info_cache` avoid frequent small allocation overhead.
- `hsfs_taskq_nthreads` controls per-mount readahead taskq thread limit.
- `hsched_coalesce_min` avoids coalescing very small adjacent chains.
- `dev_maxtransfer` is discovered via LDI/DKIOCINFO and limits coalesced transfer size.
- `max_ra_bytes` bounds sequential readahead.

## Data and State

- `struct hsnode`: per-file HSFS vnode private data, including parsed directory entry, page-map count, readahead state, and node identity.
- `struct hsfs`: per-mount state including volume geometry, device vnode, hash lock, scheduler queue, and read/readahead counters.
- `struct hio`: one queued low-level I/O request.
- `struct hio_info`: readahead batch state released by taskq.
- Global tunables include `seq_contig_requests`, `hsfs_taskq_nthreads`, `hsched_coalesce_min`, and `use_rrip_inodes`.

## Edge Cases and Semantics

- HSFS is read-only: write page faults return `EROFS`; shared writable mmap returns `ENOSYS`.
- Reads past EOF return short reads or zero.
- Directory reads skip invalid/trailing junk entries and can log bogus disk warnings.
- ISO-9660 interleaving is handled when mapping file offsets to physical device blocks.
- Extended attribute records (`xar_len`) are skipped before data.
- Files with zero size or symlink data may use `HS_DUMMY_INO` unless Rock Ridge inode data is trusted.
- `hsfs_putpage()` accepts invalidation/freeing requests even though the filesystem cannot write dirty data.
- `hsfs_pathconf()` reports name maximum, 33 file size bits, and 1/100 second timestamp resolution.

## Dependencies

Uses VM and segmap primitives (`pvn_read_kluster`, `page_lookup`, `segmap_getmapflt`), buffer I/O (`bdev_strategy`, `biowait`, `bioinit`), vnode/VFS helpers, AVL trees, taskqs, LDI device queries, DTrace probes, HSFS parser helpers (`hs_parsedir`, `hs_dirlook`, `hs_filldirent`), and Rock Ridge/SUSP metadata.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/lofs/lofs_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/lofs/lofs_subr.c

## Role

Provides the core support routines for LOFS, illumos’s loopback filesystem. This file manages the mapping from real vnodes to LOFS shadow vnodes, plus the mapping from real VFS instances to LOFS wrapper VFS instances.

## Major Responsibilities

- Maintains a dynamically growing per-mount hash table of `lnode_t` objects.
- Creates and reuses loopback shadow vnodes through `makelonode()`.
- Creates wrapper `vfs_t` structures for real filesystems encountered under a LOFS tree.
- Handles lnode and lfsnode lifetime, reference accounting, and cleanup.
- Provides support for lock-safe hash-table growth without freeing old tables prematurely.

## Key Functions

- `lofs_subrinit()` / `lofs_subrfini()`: Create and destroy the `lnode_cache`.
- `lsetup()`: Initializes a `struct loinfo`, including the hash table, lfs list, and locks.
- `ldestroy()`: Destroys locks, current hash table, and retired hash tables at unmount time.
- `makelonode()`: Returns the LOFS vnode corresponding to a real vnode. It reuses an existing `lnode` unless `LOF_FORCE` is requested, otherwise allocates a new vnode/lnode pair, sets vnode ops, records the real vnode, and inserts into the table.
- `makelfsnode()`: Finds or creates a LOFS wrapper VFS for a real VFS. It propagates mount flags, mountpoint refstr, block size, dev/fsid, root vnode, and VFS features.
- `freelfsnode()`: Removes and destroys an idle wrapper VFS.
- `lfsfind()`: Finds an existing wrapper VFS for a real VFS, skipping stale/forced-unmounted roots.
- `lo_realvfs()`: Maps a LOFS VFS back to its real VFS and optionally returns the corresponding real root vnode.
- `lgrow()`: Resizes and rehashes the lnode table while preserving safe concurrent bucket locking.
- `lretire()`: Stores old hash tables on a retired list so concurrent stale readers never touch freed memory.
- `lsave()`: Inserts an `lnode` into its bucket and triggers growth if total refs exceed the threshold.
- `freelonode()`: Removes an lnode from the hash, releases the real vnode, frees the LOFS vnode/lnode, and reclaims idle wrapper VFS instances.
- `lfind()`: Finds and holds an existing shadow vnode for a real vnode.

## Data Structures

- `struct loinfo`: Per-mount LOFS state. Holds real/mount VFS pointers, root vnode, refcount, hash table, retired hash tables, and lfs wrapper list.
- `struct lobucket`: Hash bucket containing chain, count, and mutex.
- `lnode_t`: Maps one LOFS vnode to one real vnode.
- `struct lfsnode`: Wrapper VFS for a real VFS below the LOFS mount.
- `struct lo_retired_ht`: Retired hash table kept until unmount.

## Concurrency Model

The hash table intentionally avoids a single global lock for normal lookup. Bucket locking uses `table_lock_enter()`:

- Reads current table size and pointer.
- Locks the computed bucket.
- Verifies the table pointer and size are still current.
- Retries if a resize raced.

Growth uses `li_htlock`, then locks every old bucket and the corresponding new buckets before publishing `li_hashtable` and `li_htsize` with memory barriers. Old tables are not freed immediately; they are retired and freed only by `ldestroy()`.

The lfs wrapper list is protected separately by `li_lfslock`.

## Edge Cases and Semantics

- `LOF_FORCE` bypasses reuse and creates a distinct lnode. This is used by LOFS loop termination logic in vnode lookup.
- `makelonode()` performs non-sleeping allocation first while holding the bucket lock, then retries with sleeping allocation if needed.
- If a racing thread creates the lnode while allocation is retried, the newly allocated objects are freed and the existing lnode is used.
- Wrapper VFS reference counts intentionally stop at 1 so LOFS can free `struct lfsnode` itself rather than allowing generic VFS release to free the wrong allocation size.
- `lfsfind()` guards against real VFS pointer reuse after forced unmounts by checking the cached real root vnode.

## Dependencies

Used directly by `lofs_vfsops.c` and `lofs_vnops.c`. Depends on vnode/VFS allocation, reference counting, feature propagation, mountpoint refstr handling, atomics, mutexes, and LOFS private headers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/lofs/lofs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/lofs/lofs_vfsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/lofs/lofs_vfsops.c

## Role

Implements module linkage and VFS operations for LOFS. This file handles mounting, unmounting, root/stat/sync/vget operations, and registration of LOFS VFS and vnode operation tables.

## Major Responsibilities

- Defines the LOFS module wrapper and filesystem definition.
- Defines LOFS mount options: xattr/noxattr and sub/nosub.
- Implements `lo_mount()` to create a loopback mount over an existing path.
- Enforces mount permissions, overlay rules, zone/MAC policy, and inherited mount flags.
- Initializes per-mount `struct loinfo` and root lnode.
- Exposes VFS operations through `lofsinit()`.

## Key Functions

- `_init()`: Initializes LOFS subroutines and installs the module.
- `_fini()`: Returns `EBUSY`; LOFS is not unloadable.
- `_info()`: Module information.
- `lo_mount()`: Main mount implementation.
- `lo_unmount()`: Rejects forced unmount, requires only root lnode reference to remain, then releases it.
- `lo_root()`: Returns the LOFS root vnode, using `specvp()` for device special roots.
- `lo_statvfs()`: Delegates statvfs to the real root’s current VFS, which matters after forced unmount behavior in underlying filesystems.
- `lo_sync()`: No-op for general sync because LOFS has no own data.
- `lo_syncfs()`: Directed syncfs passes through to the real VFS.
- `lo_vget()`: Passes fid-to-vnode lookup to the underlying real VFS.
- `lo_freevfs()`: Destroys and frees `struct loinfo`.
- `lofsinit()`: Registers VFS ops and vnode ops, stores filesystem type.

## Mount Path Details

`lo_mount()` performs:

- Privilege check with `secpolicy_fs_mount()`.
- Overlay/busy checks on the mount point.
- Path lookup of `uap->spec` to get the real root vnode.
- Labeled-system policy for global-zone mounts, including read-only enforcement for read-down cases and special allowances for scratch zones and `NET_MAC_AWARE`.
- `VOP_ACCESS(realrootvp, 0, ...)` to trigger autofs if the source path is an autofs trigger.
- `traverse()` to mount the topmost filesystem after autofs resolution.
- `struct loinfo` allocation and setup.
- Inheritance of restrictive flags such as readonly, nosuid, nodevices, and nosetuid.
- Handling of permissive flags such as xattr and NBMAND using explicit deny flags.
- VFS feature propagation from real VFS to LOFS VFS.
- Hash-table initialization through `lsetup()`.
- Root vnode creation through `makelonode()`.

## Mount Options

- `MNTOPT_XATTR` / `MNTOPT_NOXATTR`: Controls extended attribute exposure.
- `MNTOPT_LOFS_SUB` / `MNTOPT_LOFS_NOSUB`: Controls whether LOFS traverses subordinate mounted filesystems during lookup.
- Standard mount options such as ro, nosuid, nodevices, nosetuid, nbmand/nonbmand are interpreted into LOFS inherited/denied VFS flags.

## Edge Cases and Semantics

- LOFS forbids forced unmount.
- A loopback mount over autofs performs access and traversal so the mounted target is the filesystem autofs resolves to, not the trigger node.
- Global-zone labeled mounts can be forced read-only to prevent write-up.
- `lo_root()` returns `specvp()` for device roots because the lnode table stores only LOFS nodes, not their specfs wrappers.
- `lo_statvfs()` intentionally avoids relying only on cached real VFS state so it can reflect forced-unmount dummy ops.
- Non-directory loopback roots use a one-bucket lnode hash table because they do not require broad directory traversal caching.

## Dependencies

Depends on `lofs_subr.c` for `lsetup()`, `ldestroy()`, `makelonode()`, and `lo_realvfs()`. It also uses common VFS registration APIs, `lookupname()`, `traverse()`, zone/label APIs, privilege policy, mount option helpers, and `lofs_vnops.c` vnode template.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/lofs/lofs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/lofs/lofs_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/lofs/lofs_vnops.c

## Role

Implements LOFS vnode operations. Most operations unwrap the LOFS vnode to its real vnode and delegate, while lookup, create, link, rename, realvp, and inactive contain the core stacking semantics.

## Major Responsibilities

- Presents a full vnode operation table for LOFS shadow vnodes.
- Delegates ordinary file operations to underlying vnodes.
- Wraps newly discovered underlying vnodes in LOFS lnodes.
- Maintains correct behavior across nested LOFS mounts, autofs, mount loops, and special device vnodes.
- Enforces readonly semantics for operations where generic code might only check one side of a stacked operation.
- Frees lnodes through `lo_inactive()`.

## Key Functions

- `lo_open()`: Opens the real vnode. If the underlying VOP substitutes a different vnode, wraps it in a new lnode, propagates loop flags for directories, handles device `specvp()`, and releases the old LOFS vnode.
- `lo_close()`, `lo_read()`, `lo_write()`, `lo_ioctl()`, `lo_setfl()`, `lo_getattr()`, `lo_setattr()`, `lo_fsync()`: Pass through to the real vnode.
- `lo_access()`: Rejects writes to regular files on readonly LOFS mounts before delegating.
- `lo_inactive()`: Calls `freelonode()` for lnode cleanup.
- `lo_lookup()`: Central path lookup logic with dot/dotdot handling, subordinate mount traversal, loop detection, autofs loop termination, and wrapping of returned vnodes.
- `lo_create()`: Delegates create and wraps result. Special-cases single regular-file LOFS roots where some underlying filesystems return `ENOSYS` for create-on-root.
- `lo_link()`: Resolves lofs and realvp layers on source/target, rejects source readonly, and enforces same real VFS.
- `lo_rename()`: Rejects readonly source LOFS, protects mounted-on directories hidden by LOFS layers, and recurses through stacked LOFS layers as needed.
- `lo_mkdir()`, `lo_rmdir()`, `lo_symlink()`, `lo_readlink()`, `lo_readdir()`: Mostly pass-through with wrapping where needed.
- `lo_realvp()`: Unwraps all LOFS layers and asks lower filesystems for their real vnode if available.
- `lo_cmp()`: Compares real underlying vnodes.
- VM and page operations (`lo_getpage`, `lo_putpage`, `lo_map`, `lo_addmap`, `lo_delmap`, `lo_pageio`, `lo_dispose`) delegate to the real vnode.

## Lookup and Loop Handling

`lo_lookup()` is the most complex function. It handles:

- Empty component as `"."` unless xattr lookup/create flags require underlying lookup.
- `".."` crossing out of real mounted filesystems.
- Returning `dvp` for `"."` to avoid stale file handles.
- `LO_NOSUB` to suppress traversal into subordinate mounts.
- Device-special wrapping via `specvp()`.
- Direct loops where lookup returns the current LOFS root.
- Indirect loops through multiple LOFS layers.
- Autofs/LOFS loops where returning the covered vnode once is insufficient; `LO_AUTOLOOP` forces directory children to resolve to covered vnodes to terminate traversal.
- Forced lnode creation with `LOF_FORCE` for loop-termination identities.

## Edge Cases and Semantics

- `lo_access()` protects readonly LOFS regular files independently of underlying filesystem writability.
- `lo_link()` prevents hard-linking from a readonly LOFS source into a writable LOFS target over the same real filesystem.
- `lo_rename()` prevents renames from readonly LOFS mounts even if the underlying filesystem is writable.
- `lo_rename()` checks hidden mountpoints when target directory is not itself a LOFS vnode.
- `lo_create()` handles a single regular file mounted as the LOFS root as an existing-file create/truncate operation.
- `lo_dispose()` avoids calling dispose on `VN_ISKAS()` vnodes.
- Security attribute setting checks LOFS readonly state before delegation.

## Operation Table

`lo_vnodeops_template` registers broad vnode coverage: open, close, read/write, ioctl, getattr/setattr, access, lookup/create/remove/link/rename, directory ops, symlink ops, locking, space, realvp, page/mmap operations, poll, dump, pathconf, dispose, security attributes, and share locks.

## Dependencies

Depends on `lofs_subr.c` for `makelonode()`, `realvp()`, `vtoli()`, `vtol()`, and `freelonode()`. Interacts heavily with generic VFS lookup/traversal, specfs, autofs behavior, vnode readonly checks, and lower filesystem vnode operations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/lofs/lofs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/lookup.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/lookup.c

## Role

Implements central illumos pathname lookup and vnode-to-path reverse lookup helpers. This file is VFS infrastructure rather than a specific filesystem.

## Major Responsibilities

- Converts user or kernel path strings into vnodes through `lookupname*()` and `lookuppn*()` APIs.
- Implements component-by-component pathname traversal in `lookuppnvp()`.
- Handles root/chroot/zone roots, `"."`, `".."`, mount crossing, symlinks, trailing slashes, and case-preserving lookup.
- Provides `traverse()` for crossing mounted-on vnodes to mounted filesystem roots.
- Implements reverse path discovery for `vnodetopath()` and `dogetcwd()`.
- Maintains and validates cached vnode paths (`v_path`) when enabled by `vfs_vnode_path`.

## Key Functions

- `lookupname()`: Convenience wrapper using current credentials.
- `lookupnameatcred()`: Copies a pathname from user/kernel space into a `pathname`, using a stack-sized buffer first and falling back to dynamic allocation for long paths.
- `lookupnameat()`: Lookup with a supplied start vnode and current credentials.
- `lookuppn()` / `lookuppnat()` / `lookuppnatcred()`: `pathname_t`-based wrappers.
- `lookuppnvp()`: Central path resolution engine.
- `traverse()`: Follows `v_vfsmountedhere` chains to mounted filesystem roots with VFS read locks.
- `vn_under()`: For reverse lookup, descends from a mounted filesystem root to the vnode covered by the mount.
- `vnode_match()`: Compares vnodes by special device clone semantics or real attributes.
- `dirfindvp()`: Scans a parent directory to find the name corresponding to a target vnode.
- `localpath()`: Converts a global resolved path into the portion visible below a current root.
- `vnode_valid_pn()`: Validates that a cached path still resolves to the expected vnode.
- `dirtopath()`: Reconstructs an absolute path to a directory by repeatedly looking up `".."` and scanning parents.
- `vnodetopath_common()`: Shared implementation for `vnodetopath()` and `dogetcwd()`.
- `vnodetopath()`: Public vnode-to-path helper.
- `dogetcwd()`: Implements current working directory resolution and caches process cwd strings.

## Path Lookup Semantics

`lookuppnvp()` performs the main namei loop:

- Requires an initial held vnode and optionally a held non-global root vnode.
- Rejects empty paths with `ENOENT`.
- Skips leading slashes in higher-level wrappers.
- Strips trailing slashes with `pn_fixslash()`, forcing final symlink following and final-directory validation.
- Handles `".."` specially at process root, zone root, and filesystem root.
- Crosses out of mounted filesystems by following `vfs_vnodecovered`.
- Uses `VOP_LOOKUP()` for each component.
- Retries lookup with `zone_kcred()` for mountpoint-crossing `".."` cases that fail with `EACCES`.
- Calls `traverse()` after successful lookup if the result has a mounted filesystem on it.
- Expands symlinks into the remaining pathname and enforces `MAXSYMLINKS`.
- Builds resolved path output in `rpnp` if requested.
- Returns parent vnode in `dirvpp` and/or final vnode in `compvpp`.

## Reverse Lookup Semantics

The reverse path logic prioritizes cached `v_path` but validates it before use:

- `vnode_valid_pn()` forward-lookups the cached path and compares the result with the expected vnode.
- For zone/chroot roots, it may resolve globally with `kcred` and then derive a local path.
- Stale cached paths are cleared through `vn_clearpath()`.
- `dirtopath()` reconstructs directory paths by walking to parents and scanning directory entries with `dirfindvp()`.
- Successfully reconstructed intermediate names are fed back through `vn_setpath()` so later lookups can use cache.
- `dogetcwd()` also maintains a process-level `u_cwd` refstr cache, validating it before returning.

## Edge Cases and Semantics

- Root escape is prevented by treating `".."` at `rootvp` or zone root as `"."`.
- Forced-unmounted filesystem roots return `EIO` when crossing covered vnode state is invalid.
- `ESTALE` at lookup roots, mounted roots, or the start vnode is translated to `ENOENT`.
- Trailing slash means final component must be a directory and symlinks must be followed.
- Case-insensitive lookup can return case-preserved names in resolved paths.
- `LOOKUP_CHECKREAD` is private to getcwd-style behavior and requires read permission on each directory, matching historical/standards expectations.
- `dirfindvp()` tolerates entries that disappear after `readdir()` by ignoring `ENOENT`.
- `dirfindvp()` has a special `.zfs` fallback because some ZFS pseudo-directories may not appear normally.

## Dependencies

Uses pathname helpers, vnode/VFS operations, mount traversal locks, zone state, auditing hooks, DNLC-related vnode path cache APIs, proc/user current directory/root fields, specfs clone helpers, and generic directory entry structures.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/mntfs/mntvfsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/mntfs/mntvfsops.c

## Role

Implements module linkage and VFS operations for mntfs, the synthetic filesystem that exposes kernel mount-table information as `/etc/mnttab`.

## Major Responsibilities

- Registers the `mntfs` filesystem type and vnode operations.
- Creates the root synthetic vnode for a mntfs mount.
- Mounts mntfs only into the appropriate zone.
- Assigns unique synthetic device numbers for `stat(2)`.
- Handles unmount, root lookup, and statvfs for the synthetic one-file filesystem.

## Key Functions

- `_init()`: Installs the mntfs module.
- `_info()`: Returns module info.
- `mntinitrootnode()`: Initializes the root `mntnode_t` and its vnode. The vnode is marked root, no-cache, no-map, no-swap, and no-mount, and is a regular file.
- `mntinit()`: Registers VFS ops and vnode ops, stores `mntfstype`, allocates a unique major device number, and initializes the minor lock.
- `mntmount()`: Performs privilege and zone checks, sets resource to `"mnttab"`, allocates per-mount `mntdata_t`, checks mountpoint busy state, initializes zone reference, assigns unique minor, initializes root node, and attaches state to `vfsp`.
- `mntunmount()`: Requires unmount privilege, rejects unmount while root/open vnodes are active, releases zone reference, invalidates/frees the root vnode, and frees `mntdata_t`.
- `mntroot()`: Holds and returns the root synthetic vnode.
- `mntstatvfs()`: Returns synthetic statvfs data for `/mnttab`.

## Mount Semantics

`mntmount()` enforces:

- `secpolicy_fs_mount()`.
- In the global zone, the mountpoint path must resolve to the global zone itself; mntfs may not be mounted into another zone from outside.
- Non-overlay mounts require the mountpoint vnode to have no extra references and not already be a root.
- The VFS resource name is forced to `"mnttab"`.

The mounted filesystem consists of a single regular-file root vnode representing the mount table.

## Data and State

- `mntdata_t`: Per-mount data, including root node, zone reference, open count, cached size/mtime fields used by vnode ops.
- `mntnode_t`: Per-vnode state used by mntfs vnode operations.
- `mnt_major`, `mnt_minor`, `mnt_minor_lock`: Synthetic device number allocation.
- `mntfstype`: Filesystem type number assigned at registration.

## Edge Cases and Semantics

- There is no `_fini()` routine; comments state the module cannot be unloaded once loaded.
- `mntunmount()` checks both vnode count and `mnt_nopen`, because mntfs creates per-open vnodes in `mntvnops.c`.
- `mntstatvfs()` reports zero blocks, one file, no free files, `DEV_BSIZE`, arbitrary name max 64, and `/mnttab` strings.
- Root vnode is `VREG`, not `VDIR`, because `/etc/mnttab` behaves as a file.

## Dependencies

Pairs with `mntvnops.c` for actual file read/ioctl behavior. Uses zone refs, VFS registration, vnode allocation, synthetic device helpers, mount policy checks, and mntfs private data structures.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/mntfs/mntvfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/mntfs/mntvnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/mntfs/mntvnops.c

## Role

Implements vnode operations and snapshot machinery for mntfs. This is the main implementation of reading `/etc/mnttab` and servicing mount-table ioctls.

## Major Responsibilities

- Generates textual `/etc/mnttab` entries from in-kernel `vfs_t` state.
- Provides per-open stable snapshots for `read(2)` and mnttab ioctls.
- Maintains a zone-local database of mount entries with birth/death times and refcounts.
- Supports public and private `mntio` ioctls used by mnttab consumers.
- Implements vnode open/close/read/getattr/access/seek/poll/cmp behavior.

## Snapshot Design

The large block comment describes the core model:

- Each zone has a mount database at `zone_mntfs_db`, protected by `zone_mntfs_db_lock`.
- Each database element (`mntelem_t`) stores one rendered mount-table line plus an `extmnttab` offset table.
- Elements have birth/death times so a snapshot can see the database as it existed at snapshot creation.
- A snapshot (`mntsnap_t`) holds references to all matching elements.
- Elements are freed only when no active snapshot references them.
- Each open mntfs vnode has separate snapshots for read and ioctl use, because `getmntent(3C)` and `read(2)` have independent stream positions on the same fd.

## Key Functions

- `mntfs_devsize()` / `mntfs_devprint()`: Size and print legacy `dev=xxx` option.
- `mntfs_newest()`: Compares two `timespec_t` values.
- `mntfs_optsize()` / `mntfs_optprint()`: Size and print visible mount options, zone option, and legacy device option.
- `mntfs_populate_text()`: Builds the tab-delimited textual mount entry and fills `struct extmnttab` offsets/major/minor/hidden metadata.
- `mntfs_text_len()`: Computes required text size for one VFS entry.
- `mntfs_destroy_elem()`: Frees an element.
- `mntfs_elem_in_range()`: Tests whether an element belongs to a snapshot.
- `mntfs_get_next_elem()`: Iterates visible elements for a snapshot.
- `mntfs_freesnap()`: Releases snapshot holds and removes unreferenced elements.
- `mntfs_snapshot()`: Synchronizes the zone database with current kernel VFS list and initializes a snapshot.
- `mntfs_getmntopts()`: Public helper to stringify a VFS mount option set.
- `mntopen()`: Rejects write opens and creates a fresh per-open mntnode/vnode.
- `mntclose()`: On final close, frees read/ioctl snapshots and decrements open count.
- `mntread()`: Reads a stable snapshot into user space with per-snapshot offset caching.
- `mntgetattr()`: Computes attributes for `/etc/mnttab`, including consistent size/mtime.
- `mntaccess()`: Rejects write/exec and delegates read checks to the underlying mountpoint vnode.
- `mntgetnode()` / `mntfreenode()`: Allocate/free per-open synthetic vnode state.
- `mntseek()`: Marks ioctl snapshot rewind when lseek rewinds to offset 0.
- `mntpoll()`: Reports readable status and supports `POLLRDBAND` notification on mnttab changes.
- `mntfs_same_word()`: Compares user preference fields against tab-delimited entry fields.
- `mntfs_special_info_string()` / `mntfs_special_info_element()`: Resolve special device resource paths to type/major/minor for robust matching.
- `mntfs_import_addr()`: Converts user pointers inside an imported user buffer to kernel-buffer pointers.
- `mntfs_copyout_elem()`: Copies an entry and its pointer fields to userland for mnttab ioctls.
- `mntioctl()`: Implements mntfs ioctl command set.
- `mntcmp()`: Treats two per-open vnodes as the same mnttab instance when they share the same VFS.

## Ioctl Support

`mntioctl()` supports:

- `MNTIOC_NMNTS`: Return number of mounted resources in the ioctl snapshot.
- `MNTIOC_GETDEVLIST`: Return major/minor pairs for snapshot entries.
- `MNTIOC_SETTAG` / `MNTIOC_CLRTAG`: Set or clear mount tags after zone-aware path translation.
- `MNTIOC_SHOWHIDDEN`: Enable hidden mount entries for this open vnode.
- `MNTIOC_GETMNTANY`: Find next entry matching user-provided preferences, including special-device major/minor matching.
- `MNTIOC_GETMNTENT` / `MNTIOC_GETEXTMNTENT`: Return next mount entry.

It also handles 32-bit data model structure layouts under `_SYSCALL32_IMPL`.

## Database Update Semantics

`mntfs_snapshot()` walks the relevant VFS list:

- Global zone uses the global circular VFS list.
- Non-global zones use `zone_vfslist`.
- If a non-global zone lacks an explicit root VFS entry, a dummy VFS entry is cloned from the zone root vnode’s VFS.
- Existing elements are matched by high-resolution VFS creation time.
- Stale elements are killed by setting death time.
- Remounted or changed VFS entries cause old elements to die and new elements to be inserted.
- Hidden entries are included only if `MNT_SHOWHIDDEN` is active.

## Edge Cases and Semantics

- Read snapshots are refreshed on first read or when read offset is zero.
- Ioctl snapshots are refreshed on first ioctl use or after rewind marker.
- `mntgetattr()` goes to extra effort to keep reported size and mtime consistent around mount-table changes.
- `mntfs_enabledev` preserves the historical `dev=xxx` option.
- Zone path visibility and translation are applied to resource and mountpoint fields.
- The synthetic file is read-only and non-executable.
- `mntpoll()` uses the newer of read/ioctl snapshot mtimes.
- `MNTIOC_GETMNTANY` may temporarily drop the database lock to inspect special-device type through filesystem lookup.

## Dependencies

Depends on VFS list locking, zone mount databases, mount option structures, vnode lookup/getattr, copyin/copyout, poll hooks, DTrace probes, mntfs private structures, and public/private mnttab ioctl ABI definitions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/mntfs/mntvnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/namefs/namevfs.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/namefs/namevfs.c

## Role

Implements the VFS side of NAMEFS, the filesystem behind descriptor-to-path attachment such as `fattach()`. It mounts an open file descriptor onto a filesystem node and presents the descriptor’s vnode through a synthetic namefs vnode.

## Major Responsibilities

- Registers NAMEFS VFS and vnode operations.
- Allocates unique namenode inode numbers.
- Maintains a global hash from mounted file vnode to `struct namenode`.
- Supports walking all namefs mounts for a file vnode.
- Forces unmounts of all namefs mounts for a vnode, used for stream/pipe close cases.
- Implements mount, unmount, root, statvfs, sync, and syncfs.
- Maintains stream `STRMOUNT` state while streams are attached.

## Key Functions

- `namenodeno_alloc()`, `namenodeno_init()`, `namenodeno_free()`: Allocate/free unique node IDs from a vmem arena, extending the arena in `NM_INOQUANT` chunks.
- `nameinsert()`: Adds a namenode to `nm_filevp_hash`.
- `nameremove()`: Removes a namenode from the hash.
- `namefind()`: Finds a namenode by mounted file vnode and optionally mountpoint vnode.
- `nm_walk_mounts()`: Calls a callback for every namenode mounted from a given file vnode.
- `nm_umountall()` / `nm_unmountall()`: Force-unmount every namefs mount associated with a vnode, retrying on `EBUSY`.
- `nm_mount()`: Main file-descriptor mount implementation.
- `nm_unmount()`: Removes the namenode, drops the root reference, frees or de-roots the synthetic vnode, clears stream mount state if this was the last mount, and closes the held file.
- `nm_root()`: Holds and returns the mounted descriptor root vnode.
- `nm_statvfs()`: Returns simple synthetic statvfs data.
- `nm_sync()`: On `SYNC_CLOSE`, force-unmounts all mounts for the file vnode; otherwise fsyncs the mounted file vnode.
- `nm_syncfs()`: Directed syncfs, accepting only zero flags, fsyncs the mounted file vnode.
- `nameinit()`: Registers VFS ops, dummy VFS ops, vnode ops, initializes device number, hash table, locks, and the dummy `namevfs`.
- `_init()`, `_fini()`, `_info()`: Module lifecycle; `_fini()` returns `EBUSY`.

## Mount Semantics

`nm_mount()` performs:

- Validates `struct namefd` size and copies it from user space.
- Resolves the file descriptor to a `struct file` and vnode.
- Rejects busy/namefs mountpoints and roots.
- Rejects attaching inside `/dev/pts` or `/dev/vt` via specfs realvp checks.
- Rejects directory and event port file descriptors.
- Requires mount privilege if the descriptor is neither a door nor a stream.
- Rejects descriptors that are themselves filesystem roots.
- Reads attributes from both mountpoint and descriptor vnode.
- Requires caller ownership or privilege over the mountpoint.
- Requires write access on the mountpoint.
- Rejects descriptor vnodes with file/record locks.
- Sets `STRMOUNT` on streams.
- Holds the file structure and stores it in the namenode.
- Builds synthetic vnode attributes: descriptor type/size/rdev/block info, synthetic fsid/nodeid, one link.
- Allocates and initializes the namefs root vnode.
- Marks VFS as `VFS_UNLINKABLE`, assigns synthetic fsid/dev/data, and sets a generated resource string like `unspecified_<fstype>_<nodetype>`.
- Inserts the namenode into the global hash table.

## Data Structures and Globals

- `namedev`: Synthetic device number for namefs.
- `namefstype`: Registered filesystem type.
- `nm_filevp_hash[]`: Hash table keyed by `nm_filevp`.
- `namevfs`: Dummy VFS used for temporary namefs nodes.
- `ntable_lock`: Global hash lock.
- `nm_inoarena` and `nm_inolock`: Unique inode allocator state.
- `struct namenode`: Holds mounted file vnode/file pointer, mountpoint vnode, synthetic vnode, attributes, flags, and hash linkage.

## Unmount and Lifetime Semantics

`nm_unmount()`:

- Rejects forced unmount with `ENOTSUP`.
- Requires owner/privilege according to stored mountpoint uid.
- Removes the namenode from the global hash.
- Drops the mounted root vnode count under vnode lock.
- If count reaches zero, invalidates/frees vnode, releases VFS, frees node ID and namenode, and later closes the held file.
- If still referenced, clears `VROOT` so inactive cleanup can finish later.
- Clears stream `STRMOUNT` only when no more namefs mounts reference the same file vnode.

`nm_unmountall()` loops until `nm_umountall()` stops returning `EBUSY`, yielding briefly between attempts.

## Edge Cases and Semantics

- Multiple mountpoints may attach the same file descriptor vnode; hash entries are unique per mountpoint.
- `nm_walk_mounts()` supports callers that need to act on every namefs attachment for a vnode.
- There is a race window in forced unmount-all because `ntable_lock` must be dropped around `dounmount()`. The code documents that new mounts may appear during the window.
- NAMEFS does not support forced unmount for normal unmount.
- `nm_sync()` with `SYNC_CLOSE` is a cleanup trigger for all mounts of the underlying vnode.
- The mounted descriptor’s own VFS is used to derive the generated resource string, but failure falls back to a generic nodetype resource.

## Dependencies

Pairs with NAMEFS vnode operations from `nm_vnodeops_template` in another source file. Uses file descriptor APIs (`getf`, `releasef`, `closef`), vnode/VFS allocation and registration, stream locks, specfs/devpts/devvt checks, privilege policy, vmem, statvfs, and generic mount/unmount infrastructure.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/namefs/namevfs.c -->