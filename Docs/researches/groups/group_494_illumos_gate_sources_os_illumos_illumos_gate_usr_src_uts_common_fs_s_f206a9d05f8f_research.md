# Group Research: group_494_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_s_f206a9d05f8f

Scope: `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`, so all listed files are in scope. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_subr.c

## Purpose
Core SMBFS client helper routines for wire/path marshalling and decoding SMB directory, file, and filesystem attribute responses.

## Main Responsibilities
- Builds full remote SMB paths from cached `smbnode::n_rpath` values.
- Converts Unicode directory names to local UTF-8 form.
- Decodes directory enumeration records for normal directory listings and named-stream listings.
- Decodes `FileAllInformation` and `FileFsAttributeInformation` responses into SMBFS internal attributes.

## Key Functions
- `smbfs_fullpath(...)`
  - Marshals the directory path plus optional child name into an `mbchain`.
  - SMB2 paths omit the leading backslash.
  - SMB1 Unicode paths may need an alignment pad and are null terminated.
  - At share root, avoids adding a duplicate separator.
  - For XATTR fake directories (`N_XATTR`), suppresses the separator so named streams use the existing colon convention.
- `smbfs_fname_tolocal(...)`
  - Converts UCS-2 little-endian names in `smbfs_fctx` to UTF-8 using `uconv_u16tou8`.
  - On conversion failure, replaces the name with `"?"` because callers do not handle conversion errors.
- `smbfs_decode_dirent(...)`
  - Decodes one directory entry from `ctx->f_mdchain`.
  - Uses `NextEntryOffset` to isolate one entry safely instead of hand-adding structure sizes.
  - Supports `FileFullDirectoryInformation`, `SMB_FIND_FULL_DIRECTORY_INFO`, and `FileStreamInformation`.
  - For stream information, skips the leading colon in stream names when present.
  - Populates `ctx->f_attr`, `ctx->f_name`, `ctx->f_nmlen`, `ctx->f_rkey`, and advances `ctx->f_eofs`.
- `smbfs_decode_file_all_info(...)`
  - Decodes the `FileBasicInformation` and `FileStandardInformation` portions of `FileAllInformation`.
  - Sets create/access/modify/change times, DOS attributes, allocation size, and file size.
- `smbfs_decode_fs_attr_info(...)`
  - Decodes filesystem capability flags, maximum component length, and filesystem type name.
  - Converts the filesystem name from UCS-2 when the VC uses Unicode strings.

## Important Interactions
- Relies on `netsmb` mchain helpers (`mb_put_*`, `md_get_*`, `smb_put_dmem`, `smb_get_dstring`).
- Path logic must stay consistent with `smbfs_getino` and `smbfs_node_findcreate` identity rules.
- XATTR path behavior is coordinated with `smbfs_xattr.c`.

## Notes
- The file deliberately keeps every node’s full remote path instead of walking parent links.
- Directory-entry parsing is defensive around short buffers and treats failures as exhaustion of the current response.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_subr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_subr.h

## Purpose
Shared internal SMBFS client declarations for find contexts, protocol helper entry points, VFS/node lifecycle helpers, cache helpers, XATTR helpers, ACL helpers, and SMBFS reader/writer lock wrappers.

## Main Definitions
- Debug/logging macros:
  - `SMBFSERR(...)`
  - `SMBVDEBUG(...)`
- Lock command constants:
  - `SMB_LOCK_EXCL`
  - `SMB_LOCK_SHARED`
  - `SMB_LOCK_RELEASE`
- Find context type enum:
  - `ft_LM1`
  - `ft_LM2`
  - `ft_SMB2`
  - `ft_XA`
- Find/read-directory flags:
  - `SMBFS_RDD_FINDFIRST`
  - `SMBFS_RDD_EOF`
  - `SMBFS_RDD_FINDSINGLE`
  - `SMBFS_RDD_NOCLOSE`
- `struct smbfs_fctx`
  - Carries find-first/find-next state, output attributes/name, SMB1/SMB2 request state, current response mdchain, resume keys, stream/XATTR scan state, and wildcard/filter data.
- `struct smb_fs_size_info`
  - Internal form of `FileFsFullSizeInformation`.

## Declared Functional Areas
- Common SMB operations:
  - Locks, get/set file attributes, statfs, open/create/rename/mkdir, findopen/findnext/findclose, security descriptor get/set.
- SMB1-specific operations:
  - Trans2 query, statfs, set EOF/disposition/attributes, rename variants, stream info, security descriptor operations.
- SMB2-specific operations:
  - Path/file attribute queries, statfs, set EOF/disposition/attributes, rename, directory enumeration, stream info, security descriptor operations.
- `smbfs_subr.c` helpers:
  - `smbfs_fullpath`
  - `smbfs_decode_dirent`
  - `smbfs_decode_file_all_info`
  - `smbfs_decode_fs_attr_info`
- VFS/module lifecycle:
  - `smbfs_vfsinit`, `smbfs_vfsfini`, `smbfs_subrinit`, `smbfs_subrfini`, `smbfs_clntinit`, `smbfs_clntfini`
- Mount/node/cache helpers:
  - zone list management, node table checks/destruction, flush paths, direct I/O, temporary name generation, AVL setup, node creation/lookup, cache validation/purge.
- Page and vnode helpers:
  - `smbfs_readvnode`, `smbfs_writevnode`, `smbfsgetattr`, `smbfs_invalidate_pages`.
- ACL helpers:
  - ID fetch/set, VSA get/set, raw SD ioctls.
- XATTR helpers:
  - fake xattr directory creation, xattr parent lookup, existence check, xattr attribute lookup, xattr find operations.
- Interruptible SMBFS rwlock wrappers:
  - `smbfs_rw_enter_sig`, `smbfs_rw_tryenter`, `smbfs_rw_exit`, `smbfs_rw_lock_held`, init/destroy.

## Important Interactions
- This header is the primary coupling point among SMBFS vnode ops, VFS ops, protocol-specific SMB1/SMB2 implementations, ACL handling, and XATTR/named-stream support.
- `smbfs_fctx` is shared by normal directory listings and XATTR stream listings.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_subr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_subr2.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_subr2.c

## Purpose
SMBFS client vnode/node cache implementation and supporting utilities. It manages `smbnode` lifecycle, per-mount AVL lookup by remote path, free-list recycling, node destruction, cache pruning, flushing, direct I/O state, and module-level node-cache initialization.

## Core Design
- Uses a per-mount AVL tree keyed by full remote path (`n_rpath`, `n_rplen`).
- Replaces older global hash-chain style while retaining some “hash” naming in fields/functions.
- Maintains a global smbnode free list for reusable inactive nodes.
- Keeps vnode reference counts from dropping below one while nodes are cached/free-listed.
- Lock ordering is documented as:
  - AVL tree lock -> vnode lock
  - AVL tree lock -> freelist lock

## Key Functions
- `smbfs_node_findcreate(...)`
  - Builds a remote path from directory path, optional separator, and name.
  - Looks up or creates an `smbnode`.
  - Applies attributes when real `smbfattr` is provided.
  - Uses `smbfs_fattr0` as a sentinel to force creation without real attributes.
- `make_smbnode(...)`
  - Allocates or recycles an smbnode.
  - Drops/reacquires the AVL lock around allocation.
  - Rechecks for races before inserting into the AVL tree.
  - Initializes vnode ops, mount reference, locks, owner/group defaults, path string, and inode hash.
- `smbfs_addfree(...)`
  - Either places an inactive node on the free list or destroys it.
  - Destroys immediately when unhashable, errored, unmounted, or over node limit if no references remain.
- `sn_hashfind(...)`
  - Finds a node by path in the mount AVL tree.
  - Removes it from the free list or takes a vnode hold before returning.
- `smbfs_attrcache_prune(...)`
  - Walks the AVL tree after a node and invalidates cached attributes for descendants.
  - Handles both normal child separator `\` and XATTR separator `:`.
- `smbfs_check_table(...)`
  - Checks for active/busy vnodes during unmount.
  - Considers non-free-listed nodes, dirty cached pages, and extra `r_count` references.
- `smbfs_destroy_table(...)`
  - Removes inactive nodes from a mount’s AVL tree during unmount.
  - Preserves busy nodes in a temporary AVL tree.
- `smbfs_rflush(...)`
  - Finds vnodes with dirty or mapped pages and issues `VOP_PUTPAGE`.
- `smbfs_directio(...)`
  - Enables/disables direct I/O.
  - Flushes dirty cached pages before enabling direct mode.
- `smbfs_newnum()` / `smbfs_newname(...)`
  - Generate unique temporary unlink/rename names like `~$smbfs%08X`.
- `smbfs_subrinit()` / `smbfs_subrfini()`
  - Create/destroy the smbnode cache and global locks.
  - Allocate a unique major device number and initialize minor counter.
- `smbfs_kmem_reclaim(...)`
  - Frees reusable nodes from the smbnode free list under memory pressure.

## Important Interactions
- `smbfs_vfsops.c` initializes one AVL tree per mount and destroys it during unmount.
- `smbfs_vnops.c` relies on node identity for lookups, creates, renames, removes, and XATTR fake directories.
- Attribute cache pruning is critical after rename/delete so stale descendant nodes are not trusted.

## Notes
- Path identity is central: `n_rpath` is both lookup key and inode-hash input.
- The code is race-aware around node allocation, vnode refs, pageout, and unmount.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_subr2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_vfsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_vfsops.c

## Purpose
SMBFS VFS/module operations: module load/unload, VFS op registration, mount setup, unmount teardown, root lookup, filesystem statistics, sync, and VFS resource cleanup.

## Mount Options and Globals
- `smbfs_default_opt_acl`
  - Controls whether `-o acl` is enabled by default; default is off.
- `smbfs_tq_nthread`
  - Per-mount taskq thread count; default one thread.
- Mount options include:
  - `intr` / `nointr`
  - `acl` / `noacl`
  - `xattr` / `noxattr`
  - fake-kernel-only `noac`
- `smbfs_mountcount`
  - Prevents module unload while mounts or forced-unmount remnants exist.

## Key Functions
- `_init()`
  - Verifies `nsmb` ABI version.
  - Initializes subr, VFS, and client layers.
  - Installs the filesystem module or fake-kernel filesystem.
- `_fini()`
  - Refuses unload while `smbfs_mountcount` is nonzero.
  - Removes module/fake filesystem and tears down SMBFS layers and vnode/VFS ops.
- `smbfsinit(...)`
  - Registers VFS ops and vnode ops.
- `smbfs_mount(...)`
  - Validates mount permissions and mountpoint type.
  - Copies in and validates `smbfs_args`.
  - Rejects remount.
  - Gets `smb_share_t` from the netsmb device fd.
  - Enforces zone and Trusted Extensions label policy in kernel builds.
  - Allocates and initializes `smbmntinfo_t`.
  - Sets attribute cache timers, mount uid/gid/modes, ACL/intr/noac flags.
  - Queries remote filesystem attributes/capabilities.
  - Forces `noxattr` when named streams are unsupported.
  - Forces `noacl` when persistent ACLs are unsupported.
  - Allocates a unique device id/fsid.
  - Registers VFS features `VFSFT_XVATTR` and `VFSFT_SYSATTR_VIEWS`.
  - Creates and holds the root smbnode at remote path `\`.
  - Creates the per-mount taskq for async work such as putpage/delmap.
- `smbfs_unmount(...)`
  - Checks unmount permission.
  - For non-forced unmount, flushes dirty nodes and rejects busy node tables/root refs.
  - Marks `VFS_UNMOUNTED`.
  - Releases the mount-held root vnode.
  - Destroys inactive node-table entries.
  - Kills the SMB share and destroys the per-mount taskq.
  - Deletes mount kstats.
- `smbfs_root(...)`
  - Returns a hold on the root vnode if called from the owning zone and mount is alive.
- `smbfs_statvfs(...)`
  - Serializes remote statfs refresh through `smi_lock` and `smi_statvfs_cv`.
  - Uses cached stats until `smi_statfstime`.
  - Fills local statvfs fields not supplied over the wire.
- `smbfs_sync(...)`
  - Ignores `SYNC_ATTR`.
  - Flushes all SMBFS mounts in zone when `vfsp == NULL`, otherwise flushes one mount.
- `smbfs_freevfs(...)`
  - Removes mount from zone list, frees `smbmntinfo_t`, and decrements mount count.
- `smbfs_mount_label_policy(...)`
  - Kernel-only Trusted Extensions MAC policy.
  - Allows read-write, read-only read-down, or denies based on zone/server labels.

## Important Interactions
- Uses `smb_dev2share`, `smb_share_rele`, and `smb_share_kill` from netsmb.
- Uses node-cache helpers from `smbfs_subr2.c`.
- VFS unmount deliberately keeps the share alive until after node cleanup.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_vnops.c

## Purpose
SMBFS vnode operation implementation. It maps Solaris vnode operations to SMB client operations, VM/page-cache behavior, namespace changes, local access checks, mmap handling, locks, pathconf, and ACL hooks.

## Core Themes
- Enforces owning-zone checks on nearly every operation.
- Treats dead or unmounted mounts as `EIO`.
- Uses local Unix-mode checks based on mount uid/gid/mode, while SMB server enforces remote credentials.
- Reuses SMB FIDs across opens when rights and generation are compatible.
- Supports both direct I/O and VM-backed cached I/O.
- Implements XATTR/named-stream support through fake XATTR directories.
- Many unsupported Unix features return `ENOSYS`: hard links, symlinks, readlink, fid, realvp.

## Open/Close and FID Lifecycle
- `smbfs_open(...)`
  - Allows regular files and directories.
  - Serializes FID/directory-sequence state with `r_lkserlock`.
  - For directories, opens a find context and tracks `n_dirrefs`.
  - For regular files, reuses `n_fid` when rights are sufficient and VC generation matches.
  - Opens with read-control/read-attributes plus requested read/write rights.
  - Saves credentials used for open and records first-open vnode type in `n_ovtype`.
- `smbfs_close(...)`
  - Cleans local locks when mounted with local locking.
  - On last close, writes dirty pages for write opens.
  - Calls `smbfs_rele_fid(...)`.
- `smbfs_rele_fid(...)`
  - Closes directory find contexts or releases file FIDs when reference counts reach zero.
  - Clears cached credentials and invalidates changed attributes.

## Read/Write and Page Cache
- `smbfs_read(...)`
  - Validates open FID, type, offsets, EOF, and caches.
  - Uses direct `smb_rwuio` if `VNOCACHE`, direct I/O, or mount direct I/O conditions apply.
  - Otherwise uses segmap/VPM paths.
- `smbfs_write(...)`
  - Handles append, sync flags, file-size limit enforcement, stale-node errors, direct I/O, and segmap writes.
  - Marks `NFLUSHWIRE`, `NATTRCHANGED`, and `RDIRTY` as appropriate.
- `smbfs_writenp(...)`
  - Kernel-only writer helper that creates/touches pages and updates `r_size`.
  - Uses `RMODINPROGRESS` to coordinate with pageout.
- `smbfs_bio(...)`
  - Performs page I/O via `smb_rwuio`.
  - Handles EOF clipping, zero-fill beyond EOF for reads, sync flush after writes, and error propagation.
- `smbfs_getpage(...)`, `smbfs_getapage(...)`
  - Kernel VM page-in support, including cache validation and EOF/stale retry handling.
- `smbfs_putpage(...)`, `smbfs_putapage(...)`
  - Kernel page writeback support.
  - Handles `ROUTOFSPACE`, forced invalidation, clustering, `RMODINPROGRESS`, and retry/invalidating behavior on out-of-space style errors.
- `smbfs_invalidate_pages(...)`
  - Invalidates cached pages from an offset, coordinating with `RTRUNCATE`.

## Attributes, Access, and ACLs
- `smbfs_getattr(...)`
  - Returns hint-only cached size/fsid/rdev when allowed.
  - Flushes dirty pages before mtime-sensitive getattr.
  - Delegates actual attribute fetch to `smbfsgetattr`.
- `smbfs_setattr(...)` / `smbfssetattr(...)`
  - Performs Solaris policy checks using mount owner semantics.
  - Supports size, atime, mtime, and DOS attributes from extensible attrs.
  - Uses temporary SMB opens when handle-based setting is needed.
  - XATTR directories ignore setattr; XATTR files only allow size changes.
- `xvattr_to_dosattr(...)`
  - Maps archive/system/readonly/hidden extensible attributes to SMB DOS attributes.
- `smbfs_access_rwx(...)`
  - Implements local access checks from mount uid/gid/file mode/dir mode.
- `smbfs_getsecattr(...)` / `smbfs_setsecattr(...)`
  - Use SMB ACL implementation when `SMI_ACL` is enabled.
  - Falls back to fabricated ACLs for get when ACL support is unavailable.

## Namespace Operations
- `smbfs_lookup(...)` / `smbfslookup(...)`
  - Handles `LOOKUP_XATTR`, empty name, `.`, `..`, illegal characters, cache lookup, and over-the-wire lookup.
  - For `..`, trims cached remote paths rather than going over the wire.
  - Prunes caches when remote lookup indicates a directory was removed/renamed.
- `smbfslookup_cache(...)`
  - Reclaims valid nodes from the path-keyed smbnode cache without an OTW lookup.
- `smbfs_create(...)`
  - Handles existing-file open/truncate and new creation via SMB create dispositions.
  - Performs local access checks for both directory write and requested file access.
  - For XATTR directories, passes xattr mode to SMB create.
- `smbfs_remove(...)` / `smbfsremove(...)`
  - Opens target with delete access, optionally renames locally open files to temporary names, sets delete-on-close, and removes node from hash on success.
  - Uses delete-on-close to fit SMB semantics while approximating Unix unlink expectations.
- `smbfs_rename(...)` / `smbfsrename(...)`
  - Locks source and target directories in address order to avoid deadlock.
  - Removes existing file targets before rename when needed.
  - Uses a temporary delete-access handle for SMB rename.
  - Prunes source subtree caches on success.
- `smbfs_mkdir(...)`
  - Creates remote directory, re-looks it up, touches parent attrs, returns vnode.
- `smbfs_rmdir(...)`
  - Validates directory, mountpoint, root/current-dir conditions, then reuses `smbfsremove`.
- `smbfs_readdir(...)` / `smbfs_readvdir(...)`
  - Serializes directory enumeration with `r_lkserlock`.
  - Synthesizes `.` and `..`.
  - Uses SMB findnext, assigns cookie-like offsets, and optionally pre-populates node cache via `smbfs_fastlookup`.
  - Keeps find context open until close so EOF reads remain stable.

## mmap and Locks
- `smbfs_map(...)`
  - Validates open FID, type, offsets, mandatory lock interactions, and cacheability.
  - Uses `as_map` with `segvn_create`.
- `smbfs_addmap(...)`
  - Increments `r_mapcnt` and keeps SMB FID referenced while mapped.
- `smbfs_delmap(...)` / `smbfs_delmap_async(...)`
  - Queues async work to flush mapped dirty ranges and release FID refs when map count reaches zero.
- `smbfs_frlock(...)` / `smbfs_shrlock(...)`
  - Use local filesystem lock helpers only when `SMI_LLOCK` is set; otherwise return `ENOSYS`.

## Miscellaneous Vnode Ops
- `smbfs_ioctl(...)`
  - Supports `_FIOFFS`, direct I/O toggle, and raw SMB security descriptor get/set ioctls.
- `smbfs_fsync(...)`
  - Writes dirty pages and sends SMB flush when needed.
- `smbfs_inactive(...)`
  - Waits for async activity, flushes/invalidates pages, then calls `smbfs_addfree`.
- `smbfs_seek(...)`
  - Permits directory cookie seeks and rejects negative file offsets.
- `smbfs_space(...)`
  - Implements truncate via `F_FREESP` with zero length.
- `smbfs_pathconf(...)`
  - Reports file size bits, link max, ACL mode, symlink max, XATTR existence, system attribute support, and timestamp resolution.

## Vnode Op Table
Registers implementations for open, close, read, write, ioctl, getattr, setattr, access, lookup, create, remove, link, rename, mkdir, rmdir, readdir, symlink, readlink, fsync, inactive, fid, rwlock/rwunlock, seek, frlock, space, realvp, kernel page/mmap ops, pathconf, security attrs, and share locks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_xattr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_xattr.c

## Purpose
Implements Solaris extended attributes for SMBFS by representing SMB named streams as files inside a fake XATTR directory vnode.

## Core Model
- SMB named streams are not real directories, but Solaris expects an xattr directory.
- SMBFS fakes an xattr directory by creating an `smbnode` whose remote path appends `:` to the parent path.
- Children of that fake directory represent named streams.
- Path construction rules:
  - Normal paths use `\`.
  - Entering the fake XATTR directory adds one `:`.
  - Children under the fake XATTR directory add no extra separator, ensuring exactly one colon before the stream name.

## Key Functions
- `smbfs_get_xattrdir(...)`
  - Rejects recursive xattrs under xattrs.
  - Creates/finds the fake xattr directory node with `:` suffix.
  - Marks vnode as `VDIR | V_XATTRDIR` and node as `N_XATTR`.
- `smbfs_xa_parent(...)`
  - For an XATTR directory, trims the trailing colon to find the real parent.
  - For an XATTR file, trims after the first colon to find the fake xattr directory.
- `smbfs_xa_exists(...)`
  - Lists streams and returns true if at least one named stream exists.
- `smbfs_xa_getfattr(...)`
  - Returns fake directory attributes for `V_XATTRDIR`.
  - For stream files, looks up the stream name in the xattr directory and returns its attributes.
- `smbfs_xa_get_streaminfo(...)`
  - Resolves the real parent object and fetches stream information through SMB2 or SMB1.
  - Stores stream info in `ctx->f_mdchain` and marks EOF after one successful stream-info fetch.
- `smbfs_xa_findopen(...)`
  - Initializes an XATTR find context using `FileStreamInformation`.
- `smbfs_xa_findnext(...)`
  - Fetches stream info as needed and decodes entries with `smbfs_decode_dirent`.
  - Strips trailing `:$DATA`.
  - Skips the empty unnamed-data stream entry.
  - Applies case-insensitive filtering for single-name lookup.
- `smbfs_xa_findclose(...)`
  - Frees the find context name buffer.

## Important Interactions
- Depends on `smbfs_fullpath` suppressing separators for `N_XATTR`.
- Depends on SMB1/SMB2 stream info protocol helpers.
- Used by vnode lookup/pathconf/getattr/create logic to expose named streams through Solaris xattr APIs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_aapl.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_aapl.c

## Purpose
SMB server-side support for Apple SMB2 `AAPL` create-context extensions and Mac-specific directory-entry metadata.

## Globals and Capabilities
- `smb2_aapl_extensions`
  - Enables/disables AAPL extension handling.
- `smb2_aapl_server_caps`
  - Currently advertises `kAAPL_SUPPORTS_READ_DIR_ATTR`.
  - `OSX_COPYFILE` and `UNIX_BASED` are intentionally disabled in comments.
- `smb2_aapl_volume_caps`
  - Advertises `kAAPL_SUPPORTS_FULL_SYNC`.
- `smb2_aapl_use_file_ids`
  - Defaults off because file IDs may not be unique under `.zfs` or submounts.
- `smb_aapl_ext_maxlen`
  - Caps response context size.

## Key Functions
- `smb2_aapl_crctx(...)`
  - Decodes AAPL create context command code.
  - Rejects when AAPL extensions are disabled.
  - Builds a response header with command code and dispatches supported commands.
  - Supports `kAAPL_SERVER_QUERY`; returns invalid info class for unsupported commands such as `kAAPL_RESOLVE_ID`.
- `smb2_aapl_srv_query(...)`
  - Decodes client bitmap and capabilities.
  - Marks the session as MacOS and AAPL-capable.
  - Intersects requested bitmap/caps with server-supported capabilities.
  - Enables `SMB_SSN_AAPL_READDIR` if read-dir attributes are negotiated.
  - Returns server and volume capabilities plus padding/null model string.
- `smb2_aapl_get_macinfo(...)`
  - Enriches directory entries for AAPL readdir.
  - Looks up the listed file to compute max access.
  - Reads `AFP_Resource` named stream size into `mi_rforksize`.
  - Reads `AFP_AfpInfo` named stream and copies Finder info bytes.
  - Optionally fills Unix mode when `kAAPL_UNIX_BASED` is enabled.

## Important Interactions
- Uses SMB server filesystem operations (`smb_fsop_lookup`, `smb_fsop_lookup_name`, `smb_fsop_read`, `smb_node_getattr`).
- AAPL state is stored in the SMB session flags and native OS marker.
- Stream names `AFP_Resource` and `AFP_AfpInfo` are queried per directory entry.

## Notes
- The code prefers normal server copy chunk behavior over Apple copyfile extensions.
- UNIX mode reporting is disabled to avoid Mac client misbehavior with nontrivial ACL-derived modes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_aapl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_cancel.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_cancel.c

## Purpose
SMB2 server dispatch and immediate-reader handling for `SMB2_CANCEL`.

## Key Functions
- `smb2_newrq_cancel(...)`
  - Handles cancel requests immediately when seen in the reader path.
  - Rejects compound cancel by returning `EINVAL`.
  - Dispatches to async or sync cancel based on `SMB2_FLAGS_ASYNC_COMMAND`.
  - Sends no response.
- `smb2_cancel(...)`
  - Normal dispatch handler for cancel.
  - Drops the VC for compound cancel protocol violations.
  - Dispatches async or sync cancel.
  - Returns `SDRC_NO_REPLY`.
- `smb2_cancel_sync(...)`
  - Cancels synchronous requests by matching the cancel message ID against request credit ranges.
  - Skips cancelling itself.
  - Calls `smb_request_cancel(req)` on matches.
  - Emits DTrace error probe when match count is not one.
  - Debug builds warn when a cancel misses or races with completion.
- `smb2_cancel_async(...)`
  - Cancels async requests by matching `smb2_async_id`.
  - No response and no normal logging when count is not one because races with notify close/cancel are normal.

## Important Interactions
- Walks `session->s_req_list` under `smb_slist_enter/exit`.
- Uses request-level cancellation via `smb_request_cancel`.
- Sync cancel has inherent race with worker dispatch; async cancel is less racy because async id is known to client only after interim response.

## Notes
- SMB2 cancel never produces a protocol response.
- Compound cancel is treated as a protocol violation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_cancel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_change_notify.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_change_notify.c

## Purpose
SMB2 server dispatch and async completion support for `SMB2_CHANGE_NOTIFY`.

## Key Constants
- `DATA_OFF`
  - Output data offset for the SMB2 change notify response: `SMB2_HDR_SIZE + 8`.

## Key Functions
- `smb2_change_notify(...)`
  - Decodes request fields:
    - structure size
    - flags
    - output buffer length
    - file id
    - completion filter
  - Looks up the SMB2 FID.
  - Requires change notify to be last in a compound because it can block indefinitely.
  - Masks completion filter to valid bits and adds subtree watch when `SMB2_WATCH_TREE` is set.
  - Rejects output buffers larger than `smb2_max_trans`.
  - Calls `smb_notify_act1` for immediate/non-blocking event consumption.
  - If pending, moves request to async indefinite mode and calls `smb_notify_act2`.
  - If still pending, records latency before async wait and returns `SDRC_SR_KEPT`.
  - On completion/error, encodes reply data from `sr->raw_data` or emits SMB2 error.
- `smb2_change_notify_finish(...)`
  - Async completion callback dispatched by notify code.
  - Calls `smb_notify_act3` to finish common notify processing.
  - Encodes success/error response.
  - Records SMB2 stats.
  - Encodes final SMB2 header, signs if needed, sends reply.
  - Marks request completed and frees it.

## Important Interactions
- Uses shared notify state machine:
  - `smb_notify_act1`
  - `smb_notify_act2`
  - `smb_notify_act3`
- Uses SMB2 async machinery:
  - `smb2sr_go_async_indefinite`
  - `smb2_encode_header`
  - `smb2_sign_reply`
  - `smb2_send_reply`
- Handles DTrace start/done across synchronous and async completion paths.

## Notes
- The code explicitly avoids counting long async wait time as ordinary dispatch latency by sampling before going async.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_change_notify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_close.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_close.c

## Purpose
SMB2 server dispatch for `SMB2_CLOSE`.

## Key Function
- `smb2_close(...)`
  - Decodes close request:
    - structure size
    - flags
    - reserved
    - persistent and temporal FID
  - Looks up the FID before firing the DTrace start probe.
  - If `SMB2_CLOSE_FLAG_POSTQUERY_ATTRIB` is set, tries to fetch all attributes through `smb2_ofile_getattr`.
  - If attribute query fails, still closes the file and clears the postquery flag rather than failing close.
  - If durable handle is persistent, records persistent durable-handle close documentation state via `smb2_dh_setdoc_persistent`.
  - Closes the ofile with `smb_ofile_close`.
  - On success, encodes close response with timestamps, allocation size, file size, and DOS attributes.
  - On failure, emits SMB2 error response.

## Important Interactions
- Uses `smb2sr_lookup_fid` to resolve the open file.
- Uses `smb2_ofile_getattr` for optional post-close attributes.
- Uses durable-handle support when `of->dh_persist` is set.
- Close itself is not failed just because postquery attributes cannot be collected.

## Notes
- Response structure size is encoded as `60`, matching SMB2 close response format.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_close.c -->