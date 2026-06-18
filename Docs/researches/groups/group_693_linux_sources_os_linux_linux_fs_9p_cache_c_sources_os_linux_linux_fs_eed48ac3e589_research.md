# Group Research: group_693_linux_sources_os_linux_linux_fs_9p_cache_c_sources_os_linux_linux_fs_eed48ac3e589

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`. This grouped report covers the listed Linux VFS/filesystem files for 9p, top-level `fs/` configuration, ADFS, and the requested AFFS support files.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/cache.c -->
# File Research: sources/os/linux/linux/fs/9p/cache.c

Implements the 9p client’s FS-Cache integration when `CONFIG_9P_FSCACHE` is enabled.

Key behavior:
- `v9fs_cache_session_get_cookie()` creates a per-session FS-Cache volume key from the mount source plus `cachetag` or `aname`.
- It rewrites `/` characters in the generated volume name to `;` so the key is usable by FS-Cache.
- Handles `fscache_acquire_volume()` errors, treating `-EBUSY` as a nonfatal duplicate-key condition with caching disabled for that session.
- `v9fs_cache_inode_get_cookie()` creates per-regular-file cookies keyed by the inode’s 9p `qid.path`, with coherency data from `qid.version`.
- Only regular files receive inode cookies.
- If a cookie is acquired, the mapping is marked with `mapping_set_release_always()` so FS-Cache release is reliably triggered.

Important interactions:
- Uses `struct v9fs_session_info::fscache` and `struct v9fs_inode::netfs`.
- Tied to 9p cache modes from `v9fs.h`, especially `CACHE_FSCACHE`.
- The cookie coherency model depends on server-provided `qid.version`, unless the mount ignores QID version elsewhere.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/cache.h -->
# File Research: sources/os/linux/linux/fs/9p/cache.h

Declares the 9p FS-Cache helper interface.

Key behavior:
- Under `CONFIG_9P_FSCACHE`, includes `<linux/fscache.h>` and declares:
  - `v9fs_cache_session_get_cookie()`
  - `v9fs_cache_inode_get_cookie()`
- Without FS-Cache support, provides a no-op inline `v9fs_cache_inode_get_cookie()`.

Important interactions:
- Allows the rest of 9p to call inode cache setup unconditionally while compiling out FS-Cache behavior when disabled.
- The session cookie acquisition helper is only available when FS-Cache is configured.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/fid.c -->
# File Research: sources/os/linux/linux/fs/9p/fid.c

Implements 9p FID lookup, attachment, cloning, and tracking on dentries and inodes.

Key behavior:
- Stores per-dentry FIDs in `dentry->d_fsdata` and open inode FIDs in `inode->i_private`, both as hlist heads.
- `v9fs_fid_add()` attaches a FID to a dentry and NULLs the caller’s pointer to transfer ownership.
- `v9fs_open_fid_add()` attaches an open FID to an inode and NULLs the caller’s pointer.
- `v9fs_fid_find_inode()` searches open inode FIDs by uid and optional writability.
- `v9fs_fid_find()` searches dentry FIDs first, then falls back to open inode FIDs.
- `build_path_from_dentry()` builds a root-relative component array while rename protection is held.
- `v9fs_fid_lookup_with_uid()` is the core lookup path:
  - Reuses a matching dentry/inode FID if present.
  - Walks from a parent FID when possible.
  - Attaches the user to the root if needed.
  - Walks from root in chunks capped by `P9_MAXWELEM`.
  - Adds the resulting FID back to the dentry if the dentry is still hashed.
- `v9fs_fid_lookup()` chooses uid matching policy based on access mode:
  - `access=single`, `user`, and `client` use `current_fsuid()`.
  - `access=any` permits any dentry FID and uses session uid.

Important interactions:
- Uses `v9ses->rename_sem` to stabilize path component names during walks.
- 9p mount access mode controls whether FIDs are per-user or shared.
- Dentry release in `vfs_dentry.c` is responsible for dropping dentry-held FIDs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/fid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/fid.h -->
# File Research: sources/os/linux/linux/fs/9p/fid.h

Defines the internal 9p FID management API and cache-mode helper.

Key behavior:
- Declares FID lookup/add helpers for dentries and inodes.
- `v9fs_parent_fid()` retrieves a parent dentry FID.
- `clone_fid()` clones a FID with a zero-component `p9_client_walk()`.
- `v9fs_fid_clone()` looks up a dentry FID, clones it, and drops the original reference.
- `v9fs_fid_add_modes()` annotates a FID’s mode with client-side cache restrictions:
  - Sets `P9L_DIRECT` if caching is disabled, QID version is zero without `ignoreqv`, direct I/O is requested, or `O_DIRECT` is used.
  - Sets `P9L_NOWRITECACHE` if writeback caching is unavailable, `O_DSYNC` is used, or the mount is synchronous.

Important interactions:
- The mode bits set here drive `vfs_file.c` read/write path selection between cached and unbuffered netfs I/O.
- QID version handling is part of the cache coherency policy.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/fid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/v9fs.c -->
# File Research: sources/os/linux/linux/fs/9p/v9fs.c

Implements 9p filesystem module setup, mount option parsing, session creation/destruction, and sysfs integration.

Key behavior:
- Defines the full `fs_parameter_spec` table for 9p core, client, fd transport, and RDMA transport options.
- Parses options including `debug`, `dfltuid`, `dfltgid`, `afid`, `uname`, `aname`, `nodevmap`, `noxattr`, `directio`, `ignoreqv`, `cache`, `cachetag`, `access`, `posixacl`, `locktimeout`, `msize`, `trans`, and protocol `version`.
- `get_cache_mode()` maps named cache modes: `none`, `readahead`, `mmap`, `loose`, and `fscache`.
- `v9fs_show_options()` emits active session options for mount display.
- `v9fs_session_init()`:
  - Creates the 9p client.
  - Sets protocol flags for legacy, 9P2000.u, or 9P2000.L.
  - Applies parsed options.
  - Computes `maxdata`.
  - Normalizes unsupported access/ACL combinations.
  - Attaches the initial root FID.
  - Optionally registers the FS-Cache session volume.
  - Adds the session to a global list.
- `v9fs_session_close()`, `v9fs_session_cancel()`, and `v9fs_session_begin_cancel()` close, disconnect, or begin disconnecting active sessions.
- Creates a `/sys/fs/9p` kobject and, when FS-Cache is enabled, exposes cache tags through a read-only `caches` attribute.
- Creates/destroys the `v9fs_inode_cache` slab.
- Module init registers the `9p` filesystem; exit unregisters it and cleans caches/sysfs.

Important interactions:
- Supplies shared option parsing to `vfs_super.c`.
- Session flags in `v9fs.h` are the central policy inputs for FID lookup, ACL support, xattrs, and caching.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/v9fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/v9fs.h -->
# File Research: sources/os/linux/linux/fs/9p/v9fs.h

Defines the core 9p session, inode, protocol, and cache-mode data structures.

Key behavior:
- Defines session flags for:
  - Protocol variants: `V9FS_PROTO_2000U`, `V9FS_PROTO_2000L`.
  - Access modes: `single`, `user`, `client`, `any`.
  - POSIX ACLs, xattr disabling, QID-version ignoring, direct I/O, and sync mode.
- Defines cache shortcuts and underlying cache bits:
  - `CACHE_FILE`, `CACHE_META`, `CACHE_WRITEBACK`, `CACHE_LOOSE`, `CACHE_FSCACHE`.
- `struct v9fs_session_info` holds mount/session state, user defaults, selected cache policy, 9p client, rename semaphore, lock timeout, and optional FS-Cache data.
- `struct v9fs_inode` wraps `struct netfs_inode`, a 9p `qid`, cache-validity flags, and a mutex.
- Provides helpers for converting between VFS inode/dentry and session state.
- Provides protocol helpers `v9fs_proto_dotu()` and `v9fs_proto_dotl()`.
- Provides `v9fs_get_inode_from_fid()` and `v9fs_get_new_inode_from_fid()` dispatchers that choose legacy/u vs dotl inode creation.

Important interactions:
- This header is the shared contract across all 9p source files.
- The inode embeds netfs state, which lets `vfs_addr.c` and `vfs_file.c` use netfs helpers for cache and I/O behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/v9fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/v9fs_vfs.h -->
# File Research: sources/os/linux/linux/fs/9p/v9fs_vfs.h

Declares 9p VFS operation tables and VFS helper functions.

Key behavior:
- Documents 9p create semantics: Plan 9 creates return an opened FID, while Linux separates create and open, so the client tracks the create FID for later open handling.
- Defines `P9_LOCK_TIMEOUT`.
- Defines `V9FS_STAT2INODE_KEEP_ISIZE` for refresh paths that should not overwrite cached file size.
- Declares file, directory, dentry, address-space, superblock, inode, stat conversion, open-mode conversion, refresh, and setattr/fsync helpers.
- Defines `QID2INO()` conversion:
  - On 32-bit, combines high and low QID path bits.
  - On 64-bit, uses `qid.path + 2`.
- `v9fs_invalidate_inode_attr()` marks inode attributes stale through `V9FS_INO_INVALID_ATTR`.

Important interactions:
- Shared by legacy and dotl inode implementations.
- Dentry revalidation uses `V9FS_INO_INVALID_ATTR` to decide whether to refetch attributes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/v9fs_vfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/vfs_addr.c -->
# File Research: sources/os/linux/linux/fs/9p/vfs_addr.c

Implements 9p address-space operations through the kernel netfs library.

Key behavior:
- `v9fs_init_request()` selects a FID for netfs read/write requests:
  - Uses `file->private_data` when a file is present.
  - Otherwise searches open inode FIDs, requiring writability for write-style origins.
  - Computes request `wsize` from client `msize`, limited by FID `iounit`.
- Writeback delays choosing a write FID until dirty data actually needs upload.
- `v9fs_begin_writeback()` finds a writable open FID for writeback and attaches it to the netfs request.
- `v9fs_issue_read()` issues `p9_client_read()`, marks clear-tail for buffered reads, notes EOF, and completes the netfs subrequest.
- `v9fs_issue_write()` issues `p9_client_write()` and completes the netfs subrequest.
- `v9fs_free_request()` drops the FID reference stored in `netfs_priv`.
- `v9fs_addr_operations` wires folio read, readahead, dirtying, release, invalidation, direct I/O placeholder, writepages, and migration to netfs/filemap helpers.

Important interactions:
- The address-space operations are installed by `v9fs_init_inode()`.
- FID mode decisions from `fid.h` determine when file operations enter these cached netfs paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/vfs_addr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/vfs_dentry.c -->
# File Research: sources/os/linux/linux/fs/9p/vfs_dentry.c

Implements 9p dentry lifecycle and cached dentry revalidation.

Key behavior:
- `v9fs_cached_dentry_delete()` prevents caching of negative dentries.
- `v9fs_dentry_release()` detaches and drops all FIDs stored on a dentry.
- `__v9fs_lookup_revalidate()`:
  - Rejects RCU lookup.
  - Treats negative dentries as valid.
  - If inode attributes are invalid, looks up a FID and refreshes inode attributes through legacy or dotl refresh.
  - Invalidates the dentry on `-ENOENT` or type-change persistence.
- Provides dentry unalias lock/unlock callbacks using the session `rename_sem`.
- Defines cached dentry operations with revalidate/delete/release/unalias hooks.
- Defines uncached dentry operations with release/unalias hooks only.

Important interactions:
- Cached modes in `vfs_super.c` select `v9fs_cached_dentry_operations`; uncached modes select `v9fs_dentry_operations` and `DCACHE_DONTCACHE`.
- Dentry release is also called after successful remove to invalidate dentry-held FIDs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/vfs_dentry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/vfs_dir.c -->
# File Research: sources/os/linux/linux/fs/9p/vfs_dir.c

Implements 9p directory file operations and directory FID release.

Key behavior:
- Defines `struct p9_rdir`, an on-demand per-FID directory read buffer.
- Legacy `v9fs_dir_readdir()` reads raw stat records with `p9_client_read()`, decodes them with `p9stat_read()`, and emits entries using QID-derived inode numbers.
- Dotl `v9fs_dir_readdir_dotl()` calls `p9_client_readdir()`, decodes `p9_dirent` records, and uses server-provided offsets and dtypes.
- `dt_type()` maps legacy 9p mode bits to `DT_REG`, `DT_DIR`, or `DT_LNK`.
- `v9fs_dir_release()`:
  - Flushes dirty regular-file mapping data on writable close.
  - Removes open FIDs from the inode FID list.
  - Drops the FID.
  - Unuses the FS-Cache cookie, updating coherency version and size for writable handles.
- Defines directory operations for legacy/u and dotl protocol variants.

Important interactions:
- Directory open is shared with regular files via `v9fs_file_open()`.
- Release is also used by regular file operations in `vfs_file.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/vfs_dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/vfs_file.c -->
# File Research: sources/os/linux/linux/fs/9p/vfs_file.c

Implements 9p regular file operations, locking, mmap behavior, cached/unbuffered I/O selection, and fsync.

Key behavior:
- `v9fs_file_open()`:
  - Converts Linux open flags to legacy/u or dotl open modes.
  - Clones a dentry FID if `file->private_data` is not already set by atomic create.
  - With writeback caching and write-only opens, tries to open as read/write to support read-modify-write cache paths; if that fails, disables caching for that FID.
  - Uses FS-Cache cookies when enabled.
  - Applies FID cache mode flags and stores the open FID on the inode.
- Legacy `v9fs_file_lock()` only flushes/invalidates pages before local lock changes.
- Dotl locking maps POSIX and flock locks to 9p lock/getlock RPCs:
  - `v9fs_file_do_lock()` sends blocking/nonblocking `TLOCK` requests and maps server status to Linux errors.
  - `v9fs_file_getlock()` combines local conflict testing with server `TGETLOCK`.
  - Failed remote locks roll back local lock state.
- `v9fs_file_read_iter()` chooses unbuffered netfs read for `P9L_DIRECT`, otherwise cached netfs read.
- `v9fs_file_write_iter()` chooses unbuffered write for direct/no-write-cache FIDs, otherwise cached netfs write.
- `v9fs_file_splice_read()` selects copy-based splice for direct mode and filemap splice otherwise.
- Legacy fsync sends a blank `wstat`; dotl fsync sends `p9_client_fsync()`.
- mmap:
  - Non-writeback mounts only allow read-only mmap preparation.
  - Writeback mounts install vm ops that use filemap faults and `netfs_page_mkwrite()`.
  - Shared VMA close flushes the mapped byte range.

Important interactions:
- FID mode bits from `v9fs_fid_add_modes()` are the central switch for cached vs direct behavior.
- The dotl operations table includes remote lock/flock and writeback-aware mmap; legacy table has local lock behavior and read-only mmap preparation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/vfs_file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/vfs_inode.c -->
# File Research: sources/os/linux/linux/fs/9p/vfs_inode.c

Implements inode and inode-operation handling for legacy 9P2000 and 9P2000.u.

Key behavior:
- Converts between Unix modes and 9p mode bits:
  - `unixmode2p9mode()` maps directories, devices, sockets, FIFOs, suid/sgid/sticky when dotu extensions allow them.
  - `p9mode2unixmode()` maps 9p stat mode and extension strings back to Linux file type, permissions, and device numbers.
- `v9fs_uflags2omode()` maps Linux open flags to legacy 9p open modes.
- `v9fs_blank_wstat()` prepares a “do not change” wstat structure.
- Allocates/frees 9p inodes from `v9fs_inode_cache`, initializes netfs state, address-space ops, inode ops, and file ops based on file type and protocol.
- `v9fs_evict_inode()` waits for netfs I/O, truncates pages, clears writeback, releases FS-Cache cookies, and clears the inode.
- Inode cache lookup uses QID version/type/path matching and rejects mismatched file types.
- `v9fs_inode_from_fid()` stats a FID and instantiates or reuses an inode.
- Remove path:
  - Prefer dotl `unlinkat` when available.
  - Fall back to path-based `p9_client_remove()`.
  - Updates nlink counts, invalidates attributes, and releases dentry FIDs.
- Create path:
  - Clones parent FID, sends `fcreate`, walks back to an unopened FID, creates the inode, attaches the dentry FID, and returns the opened create FID.
- Lookup walks from the parent FID, creates cached or always-new inodes depending on cache mode, and uses `d_splice_alias()`.
- Atomic open preserves Plan 9 create-open atomicity by passing the opened create FID directly to the file.
- Rename:
  - Rejects nonzero Linux rename flags.
  - Uses dotl renameat/rename if available.
  - Legacy/u path only supports same-directory rename through `wstat.name`.
  - Uses `rename_sem`, updates link counts, invalidates affected attributes, and performs `d_move()`.
- Getattr:
  - Uses cached inode attributes for meta/loose cache.
  - Flushes dirty writeback data before stat in writeback mode.
  - Otherwise fetches server stat and refreshes inode.
- Setattr:
  - Builds wstat fields for mode, times, size, uid/gid where supported.
  - Flushes dirty data first.
  - Resizes page/netfs/FS-Cache state on size changes.
  - Invalidates inode attrs and marks inode dirty.
- Supports dotu symlink, hardlink, and special-file creation through extension strings.
- `v9fs_refresh_inode()` refetches legacy stat data, preserving size in loose cache mode.

Important interactions:
- Dotl-specific inode operations are in `vfs_inode_dotl.c`.
- This file provides shared helpers used by dotl code too, including `v9fs_vfs_lookup()`, remove, rename, and open flag conversion for non-dotl.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/vfs_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/vfs_inode_dotl.c -->
# File Research: sources/os/linux/linux/fs/9p/vfs_inode_dotl.c

Implements inode operations specific to the 9P2000.L protocol.

Key behavior:
- Uses dotl stat data including generation number for inode matching.
- `v9fs_inode_from_fid_dotl()` fetches `P9_STATS_BASIC | P9_STATS_GEN` and instantiates/reuses inodes.
- Converts Linux open flags to dotl flags with `v9fs_open_to_dotl_flags()`.
- Creation paths use POSIX-like dotl RPCs:
  - `p9_client_create_dotl()`
  - `p9_client_mkdir_dotl()`
  - `p9_client_mknod_dotl()`
  - `p9_client_symlink()`
  - `p9_client_link()`
- New object gid honors parent `S_ISGID` through `v9fs_get_fsgid_for_create()`.
- Creation and mkdir/mknod adjust mode through ACL helpers and set inherited create ACLs after inode instantiation.
- Dotl atomic open mirrors legacy atomic behavior while using dotl open flags and ACL-aware mode creation.
- Dotl getattr fetches `P9_STATS_ALL`, refreshes inode, fills `kstat`, and uses server block size.
- Dotl setattr maps Linux `ATTR_*` bits to 9p dotl attribute flags, flushes dirty data, sends `p9_client_setattr()`, resizes cache/page state on truncate, invalidates attributes, and updates ACLs on chmod.
- `v9fs_stat2inode_dotl()` handles both full basic stat and partial result masks for atime, mtime, ctime, uid, gid, nlink, mode, size, blocks, and generation.
- Dotl symlink following uses `p9_client_readlink()`.
- Dotl hardlink instantiates the new dentry with the existing inode and refreshes link metadata in cached modes.
- Exposes inode operations with xattr and ACL hooks for directories/files; symlinks expose listxattr but no ACL hooks.

Important interactions:
- Reuses common lookup, unlink, rmdir, rename, cache, dentry, and netfs machinery from other 9p files.
- Dotl is the only path where POSIX ACL enforcement is enabled by mount/session logic.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/vfs_inode_dotl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/vfs_super.c -->
# File Research: sources/os/linux/linux/fs/9p/vfs_super.c

Implements 9p superblock, fs_context, mount, statfs, and unmount behavior.

Key behavior:
- `v9fs_fill_super()` initializes superblock size limits, block size based on `maxdata`, magic, super operations, xattr handlers for dotl, time limits, backing device info, readahead/io page settings, and POSIX ACL flag.
- `v9fs_get_tree()`:
  - Allocates a session.
  - Initializes 9p session and root FID.
  - Allocates an anonymous superblock.
  - Selects cached or uncached dentry operations based on cache mode.
  - Creates root inode from the root FID.
  - Fetches ACLs and attaches the root FID to the root dentry.
- `v9fs_kill_super()` kills the anonymous superblock, cancels/closes the 9p session, frees session state, and clears `s_fs_info`.
- `v9fs_umount_begin()` begins client disconnect on forced/unmount paths.
- Dotl `v9fs_statfs()` uses server `statfs` when supported, otherwise falls back to `simple_statfs()`.
- `v9fs_drop_inode()` keeps cached-mode inode retention generic, but always drops inodes for uncached mode to force server attribute freshness.
- Write-inode hooks call `netfs_unpin_writeback()`.
- Defines `fs_context_operations` for parse/get_tree/free.
- `v9fs_init_fs_context()` sets default session/client/fd/RDMA options, including protocol default 9P2000.L and default `msize`.
- Registers the `file_system_type` named `9p`.

Important interactions:
- The cache mode selected in `v9fs.c` controls dentry caching, inode dropping, readahead, and xattr/ACL behavior here.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/vfs_super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/xattr.c -->
# File Research: sources/os/linux/linux/fs/9p/xattr.c

Implements extended attribute get/set/list support for 9P2000.L.

Key behavior:
- `v9fs_fid_xattr_get()`:
  - Uses `p9_client_xattrwalk()` to open an xattr FID and learn attribute size.
  - Returns size for zero-length probe buffers.
  - Returns `-ERANGE` if the provided buffer is too small.
  - Reads the xattr contents through `p9_client_read()`.
- `v9fs_xattr_get()` looks up a dentry FID and delegates to FID-based get.
- `v9fs_fid_xattr_set()`:
  - Clones the input FID.
  - Uses `p9_client_xattrcreate()` to create/replace/remove the attribute stream.
  - Writes the value through `p9_client_write()`.
  - Returns clunk errors if the write path succeeded.
- `v9fs_xattr_set()` looks up a dentry FID and delegates to FID-based set.
- `v9fs_listxattr()` uses xattrwalk with an empty string.
- Defines generic xattr handlers for `user.*` and `trusted.*`.
- Adds `security.*` handler when `CONFIG_9P_FS_SECURITY` is enabled.

Important interactions:
- `vfs_super.c` installs these handlers only for dotl mounts when xattrs are not disabled.
- ACL code uses the same xattr-capable dotl infrastructure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/9p/xattr.h -->
# File Research: sources/os/linux/linux/fs/9p/xattr.h

Declares 9p extended attribute interfaces.

Key behavior:
- Exposes `v9fs_xattr_handlers` for superblock installation.
- Declares FID-based and dentry-based xattr get/set helpers.
- Declares `v9fs_listxattr()`.

Important interactions:
- Used by dotl inode operations and superblock setup.
- Depends on 9p client xattr RPC support.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/9p/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/Kconfig -->
# File Research: sources/os/linux/linux/fs/Kconfig

Defines the top-level Linux filesystem Kconfig menu and sources filesystem subsystem Kconfig files.

Key behavior:
- Declares foundational filesystem config symbols such as `DCACHE_WORD_ACCESS`, `VALIDATE_FS_PARSER`, `FS_IOMAP`, `FS_STACK`, `BUFFER_HEAD`, and `LEGACY_DIRECT_IO`.
- Under `BLOCK`, includes major local/block filesystems such as ext2/ext4, JBD2, JFS, XFS, GFS2, OCFS2, Btrfs, NILFS2, F2FS, and zonefs.
- Defines DAX support options and POSIX ACL helper config.
- Includes filesystem crypto, verity, notify, quota, autofs, fuse, and overlayfs configuration.
- Defines the “Caches” submenu for netfs and cachefiles.
- Defines CD/DVD, DOS/FAT/EXFAT/NT, pseudo filesystems, tmpfs, hugetlbfs, configfs, and efivarfs menus.
- Defines `MISC_FILESYSTEMS` and sources ADFS, AFFS, and other miscellaneous filesystem Kconfigs.
- Defines `NETWORK_FILESYSTEMS` and sources NFS, NFSD, SunRPC, Ceph, SMB, Coda, AFS, and 9p Kconfigs.
- Includes NLS, DLM, Unicode, and `IO_WQ`.

Important interactions:
- `fs/adfs/Kconfig` and `fs/affs/Kconfig` are included under `MISC_FILESYSTEMS`.
- `fs/9p/Kconfig` is included under `NETWORK_FILESYSTEMS`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/Makefile -->
# File Research: sources/os/linux/linux/fs/Makefile

Defines build composition for Linux VFS core and filesystem directories.

Key behavior:
- Builds core VFS objects unconditionally, including open/read/write paths, superblocks, dentries, inodes, namespace, fs context/parser, xattrs, sync, splice, mount idmapping, and related helpers.
- Adds optional core objects based on config, such as buffer heads, proc namespace, legacy direct I/O, epoll, signalfd, eventfd, aio, DAX, file locking, binfmt handlers, POSIX ACLs, and NFS common code.
- Adds core subdirectories including notify, iomap, quota, proc, kernfs, sysfs, configfs, devpts, dlm, netfs, ramfs, unicode, and many filesystems.
- Maps specific filesystem config symbols to directories:
  - `CONFIG_ADFS_FS` -> `adfs/`
  - `CONFIG_AFFS_FS` -> `affs/`
  - `CONFIG_9P_FS` -> `9p/`
- Preserves ordering notes, such as ext4 before ext2.

Important interactions:
- This is the build-side counterpart of `fs/Kconfig`.
- The requested ADFS, AFFS, and 9p trees are all pulled into the kernel build through this file.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/adfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/adfs/Kconfig

Defines configuration for the Acorn Disc Filing System driver.

Key behavior:
- `ADFS_FS` is a tristate option depending on `BLOCK` and selecting `BUFFER_HEAD`.
- Help text describes read support for Acorn/RISC OS ADFS hard-drive partitions and floppy images.
- `ADFS_FS_RW` enables experimental write support and depends on `ADFS_FS`.
- Write support is explicitly labeled dangerous/experimental.

Important interactions:
- `ADFS_FS` controls whether `fs/adfs/` is built by the top-level `fs/Makefile`.
- Runtime write behavior in ADFS checks `CONFIG_ADFS_FS_RW`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/adfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/adfs/Makefile -->
# File Research: sources/os/linux/linux/fs/adfs/Makefile

Defines the ADFS module object composition.

Key behavior:
- Builds `adfs.o` when `CONFIG_ADFS_FS` is enabled.
- Combines:
  - `dir.o`
  - `dir_f.o`
  - `dir_fplus.o`
  - `file.o`
  - `inode.o`
  - `map.o`
  - `super.o`

Important interactions:
- Separates common directory handling from F and F+ format-specific directory implementations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/adfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/adfs/adfs.h -->
# File Research: sources/os/linux/linux/fs/adfs/adfs.h

Defines ADFS internal structures, constants, helper macros, and cross-file prototypes.

Key behavior:
- Defines fragment constants for free, bad, and root fragments.
- Defines RISC OS filetype extraction from stamped load addresses.
- Defines ADFS attribute bits for owner/public read/write, locked, directory, and execute state.
- `struct adfs_inode_info` stores parent object id, indirect disk address, RISC OS load/exec addresses, attributes, mmu-private size, and embedded VFS inode.
- `struct adfs_sb_info` stores map state, selected directory operations, uid/gid/masks, filetype suffix option, map geometry, share size, and name length.
- `struct adfs_dir` abstracts a loaded directory across up to inline or allocated buffer-head arrays and format-specific headers/tails.
- `struct object_info` is the common in-memory representation of a directory entry.
- `struct adfs_dir_ops` defines format-specific directory operations.
- Declares inode, map, directory, file, and logging helpers.
- `__adfs_block_map()` maps an object’s block offset through the fragment map, accounting for embedded offset bits in indirect addresses.
- `adfs_map_discrecord()` returns the disk record stored in the map.
- `adfs_disc_size()` builds the 64-bit filesystem size from low/high fields.

Important interactions:
- Shared by every ADFS source file.
- The selected `adfs_dir_ops` implementation is chosen at mount based on disk format version.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/adfs/adfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/adfs/dir.c -->
# File Research: sources/os/linux/linux/fs/adfs/dir.c

Implements common ADFS directory loading, iteration, lookup, dentry comparison, and metadata update support.

Key behavior:
- Uses a global `adfs_dir_rwsem` to serialize directory reads and updates.
- Provides buffer-spanning copy helpers `adfs_dir_copyfrom()` and `adfs_dir_copyto()`.
- Reads directory buffer heads through `adfs_dir_read_buffers()`, using `__adfs_block_map()` for logical-to-physical mapping.
- Releases or forgets loaded directory buffers depending on whether dirty state should be preserved.
- `adfs_dir_read_inode()` validates that the loaded directory parent id matches the inode’s stored parent id.
- `adfs_object_fixup()`:
  - Converts RISC OS `/` characters in names to Linux `.`.
  - Avoids generated `.` and `..` names by changing the first character to `^`.
  - Optionally appends `,xyz` filetype suffixes.
- `adfs_iterate()` emits `.` and `..`, then delegates entry iteration to the selected directory format ops.
- `adfs_dir_update()` updates an object’s on-disk directory entry when write support is enabled, commits directory checksums/sequence fields, marks buffers dirty, and optionally syncs.
- Lookup is case-insensitive using an ASCII-only lowercase helper.
- Dentry operations provide case-insensitive hash/compare and enforce maximum name length.
- `adfs_lookup()` reads object info by name and instantiates an inode with `adfs_iget()`.

Important interactions:
- Format-specific callbacks come from `dir_f.c` or `dir_fplus.c`.
- Writeback from `inode.c` uses `adfs_dir_update()` to persist changed metadata.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/adfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/adfs/dir_f.c -->
# File Research: sources/os/linux/linux/fs/adfs/dir_f.c

Implements ADFS E/F fixed-size directory format handling.

Key behavior:
- Provides unaligned little-endian read/write helpers for 1-4 byte fields.
- Computes the F-format directory check byte by rotating/xoring directory words and tail data.
- Validates directory header/tail sequence fields, magic names (`Nick` or `Hugo`), reserved fields, and check byte.
- Reads fixed 2048-byte directories and sets header/tail pointers.
- Converts disk directory entries to `object_info`:
  - Name up to 10 visible characters.
  - 3-byte indirect disk address.
  - 4-byte load/exec/length.
  - Attribute byte.
- Converts `object_info` back to disk entry metadata for updates.
- Supports fixed-position scanning of up to 77 entries.
- Iteration emits entries until an empty name or the fixed entry limit.
- Update locates an entry by indirect address and rewrites its mutable fields.
- Commit increments directory sequence numbers, recomputes check byte, and revalidates.

Important interactions:
- Exported through `adfs_f_dir_ops`.
- Used for non-F+ ADFS disks selected in `super.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/adfs/dir_f.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/adfs/dir_f.h -->
# File Research: sources/os/linux/linux/fs/adfs/dir_f.h

Defines on-disk structures for ADFS E/F directory format.

Key behavior:
- Defines `struct adfs_dirheader` with start sequence and start name.
- Defines fixed constants:
  - `ADFS_NEWDIR_SIZE` = 2048 bytes.
  - `ADFS_NUM_DIR_ENTRIES` = 77.
  - `ADFS_F_NAME_LEN` = 10.
- Defines packed `struct adfs_direntry` with name, load/exec/length, indirect address, and attributes.
- Defines old and new directory tail layouts with parent id, title/name fields, end sequence/name, and check byte.

Important interactions:
- Consumed by `dir_f.c` and `super.c`.
- `ADFS_NEWDIR_SIZE` is also used for the default root directory object size.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/adfs/dir_f.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/adfs/dir_fplus.c -->
# File Research: sources/os/linux/linux/fs/adfs/dir_fplus.c

Implements ADFS F+ variable-size “big directory” handling.

Key behavior:
- Computes entry offsets after variable directory name storage and aligned header fields.
- Validates F+ headers:
  - Version bytes must be zero.
  - Start magic must match `BIGDIRSTARTNAME`.
  - Directory size must be nonzero, 2048-aligned, and <= 4 MiB.
  - Name, entry, and names-table areas must fit inside the directory.
- Validates tail magic, sequence, and reserved fields.
- Computes check byte across header, entries, name storage, and tail fields.
- Reads the first block to validate header, then reads the full directory size.
- Handles mismatch between inode directory size and header size as a warning.
- `adfs_fplus_getnext()` reads a big directory entry, then fetches its name from the names area.
- Iteration supports large entry counts via `ctx->pos - 2`.
- Update locates an entry by indirect address and rewrites load/exec/length/indaddr/attr fields.
- Commit increments sequence fields, recomputes check byte, and validates header/tail.

Important interactions:
- Exported through `adfs_fplus_dir_ops`.
- Selected in `super.c` when the disk record has a nonzero format version.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/adfs/dir_fplus.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/adfs/dir_fplus.h -->
# File Research: sources/os/linux/linux/fs/adfs/dir_fplus.h

Defines on-disk structures and constants for ADFS F+ big directories.

Key behavior:
- Defines `ADFS_FPLUS_NAME_LEN` as 255.
- Defines big-directory start/end magic constants.
- Defines packed/aligned `struct adfs_bigdirheader` with version, size, entry count, names size, parent id, and variable directory name.
- Defines `struct adfs_bigdirentry` with load/exec/length/indaddr/attr plus name length and name pointer.
- Defines `struct adfs_bigdirtail` with end magic, sequence, reserved bytes, and check byte.

Important interactions:
- Consumed by `dir_fplus.c`.
- F+ support expands maximum exposed name length compared with F directories.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/adfs/dir_fplus.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/adfs/file.c -->
# File Research: sources/os/linux/linux/fs/adfs/file.c

Defines regular-file VFS operation tables for ADFS.

Key behavior:
- `adfs_file_operations` uses generic helpers for:
  - llseek
  - read_iter
  - mmap preparation
  - fsync
  - write_iter
  - splice_read
- `adfs_file_inode_operations` provides `setattr = adfs_setattr`.

Important interactions:
- Actual block mapping and address-space operations are implemented in `inode.c`.
- Write behavior depends on mount/write-support configuration and allocation limitations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/adfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/adfs/inode.c -->
# File Research: sources/os/linux/linux/fs/adfs/inode.c

Implements ADFS inode creation, block mapping, address-space operations, permission/time conversion, setattr, and inode writeback.

Key behavior:
- `adfs_get_block()` maps file logical blocks through `__adfs_block_map()` for reads, but returns `-EIO` for block creation because allocation is not implemented.
- Address-space operations use buffer-head/mpage helpers for folio read, writepages, write_begin/write_end, invalidation, migration, and bmap.
- Converts ADFS/RISC OS attributes to Linux modes:
  - Directory attributes become executable directories with owner-mask read bits.
  - Filetype `0xfc0` becomes symlink.
  - Filetype `0xfe6` gets executable read masks.
  - Owner/public read/write attributes map through mount masks.
- Converts Linux mode changes back to ADFS attributes for writable metadata updates.
- Converts 40-bit RISC OS centisecond timestamps from the 1900 epoch to Unix `timespec64`.
- Converts Unix mtime back to stamped ADFS timestamp when possible.
- `adfs_iget()` creates a new inode from `object_info`, storing parent id, object id, load/exec addresses, attributes, size, uid/gid, timestamps, and operation tables.
- Uses the object indirect disk address as the inode number.
- `adfs_setattr()`:
  - Rejects uid/gid changes that differ from global mount uid/gid.
  - Handles size changes only at page-cache/inode-size level; comments note missing on-disk truncation.
  - Converts mtime and mode into ADFS metadata.
  - Marks inode dirty for size/mtime/mode changes.
- `adfs_write_inode()` reconstructs `object_info` and calls `adfs_dir_update()` to write metadata back to the parent directory entry.

Important interactions:
- Relies on immutable parent-id assumptions: metadata writeback needs the parent directory id, so cross-directory rename is not supported by this design.
- Block allocation is absent despite generic write paths being wired.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/adfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/adfs/map.c -->
# File Research: sources/os/linux/linux/fs/adfs/map.c

Implements ADFS free-space/object map parsing, validation, lookup, and statfs accounting.

Key behavior:
- Describes the ADFS map as zones containing variable-length fragment bitstreams.
- `lookup_zone()` scans a zone for a fragment id and resolves an offset within repeated fragments.
- `scan_free_map()` follows free-fragment links and sums free map bits.
- `scan_map()` searches starting from the fragment’s expected zone and wraps across zones if needed.
- `adfs_map_statfs()` computes total blocks, files, free blocks, and available blocks from map data.
- `adfs_map_lookup()` maps a fragment id plus object offset to a physical sector/block:
  - Root fragment starts at the middle zone.
  - Other fragments start at `frag_id / ids_per_zone`.
  - Converts between sector offsets and map-bit offsets using `s_map2blk`.
- Computes and validates zone checksums and map crosscheck byte.
- Lays out zone metadata, including first-zone disk-record area and last-zone truncation to filesystem size.
- Reads all map zones from disk.
- `adfs_read_map()` initializes map geometry from the disk record, reads map blocks, validates them, and returns an allocated `adfs_discmap`.
- `adfs_free_map()` releases buffer heads and frees the map array.

Important interactions:
- All ADFS file and directory block mapping depends on `adfs_map_lookup()`.
- Mount fails if map validation fails.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/adfs/map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/adfs/super.c -->
# File Research: sources/os/linux/linux/fs/adfs/super.c

Implements ADFS mount, superblock, options, probing, statfs, inode cache, and module registration.

Key behavior:
- Provides ADFS logging helpers.
- Validates ADFS disk records:
  - Sector size must be 256/512/1024 bytes.
  - `idlen` must fit format limits.
  - Filesystem must fit 32-bit sector offsets.
  - Reserved fields must be zero.
- Mount options:
  - `uid`
  - `gid`
  - `ownmask`
  - `othmask`
  - `ftsuffix`
- Reconfigure syncs the filesystem and copies parsed option state.
- `adfs_statfs()` uses map-derived block/free counts and sets magic, max name length, block size, and fsid.
- Creates/destroys a slab cache for ADFS inodes.
- `adfs_drop_inode()` always drops inodes for read-only mounts or builds without write support.
- `adfs_probe()` reads candidate disk-record locations, adjusts block size to the filesystem sector size, and reads the map.
- Supports validation through the boot block disk record or a disk record at block zero.
- `adfs_fill_super()`:
  - Sets superblock flags/magic/time granularity.
  - Probes filesystem metadata.
  - Chooses F or F+ directory ops based on disk format version.
  - Adjusts name length for optional filetype suffix.
  - Installs dentry operations.
  - Synthesizes the root object and creates the root dentry.
- Registers the block-backed `adfs` filesystem requiring a device.

Important interactions:
- `super.c` selects the directory format implementation used by `dir.c`.
- Mount fails if disk record or map validation fails.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/adfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/affs/Kconfig -->
# File Research: sources/os/linux/linux/fs/affs/Kconfig

Defines configuration for Amiga Fast File System support.

Key behavior:
- `AFFS_FS` is a tristate option depending on `BLOCK`.
- Selects `BUFFER_HEAD` and `LEGACY_DIRECT_IO`.
- Help text describes read/write support for Amiga FFS partitions and disk images, excluding native Amiga floppies due to controller incompatibility.
- Module name is `affs`.

Important interactions:
- Controls inclusion of `fs/affs/` through the top-level `fs/Makefile`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/affs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/affs/Makefile -->
# File Research: sources/os/linux/linux/fs/affs/Makefile

Defines AFFS module object composition.

Key behavior:
- Builds `affs.o` when `CONFIG_AFFS_FS` is enabled.
- Combines:
  - `super.o`
  - `namei.o`
  - `inode.o`
  - `file.o`
  - `dir.o`
  - `amigaffs.o`
  - `bitmap.o`
  - `symlink.o`
- Contains a commented debug compiler flag.

Important interactions:
- The files researched in this group are shared support pieces for the complete AFFS module.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/affs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/affs/affs.h -->
# File Research: sources/os/linux/linux/fs/affs/affs.h

Defines AFFS internal structures, macros, mount flags, helper wrappers, and cross-file prototypes.

Key behavior:
- Provides macros for interpreting AFFS block headers/tails, root blocks, and data blocks.
- Defines cache sizing constants for linear and associative extended-block caches.
- `struct affs_inode_info` stores open count, link/ext/hash locks, metadata buffer tracking, block/ext counts, extension caches, last allocation/preallocation state, protection bits, mmu-private size, and embedded VFS inode.
- `struct affs_bm_info` records bitmap block number and free count.
- `struct affs_sb_info` stores partition geometry, data block size, root block, hash size, mount flags, uid/gid/mode overrides, root and bitmap buffers, prefix/volume symlink state, delayed superblock work, and RCU head.
- Defines mount flags for international mode, valid bitmap, immutable protection bits, quiet chmod errors, forced uid/gid/mode, MUFS, OFS, prefix allocation, verbose, and no filename truncation.
- Declares AFFS functions for hash insertion/removal, header removal, checksums, date/protection conversion, errors, names, bitmap allocation/freeing, namei operations, inode operations, file operations, directory operations, symlink operations, and export ops.
- Provides block access wrappers that validate block ranges before calling buffer-head helpers.
- Provides checksum adjustment helpers for header and bitmap blocks.
- Provides lock helpers for link, directory/hash, and extension operations.

Important interactions:
- Shared by all AFFS implementation files.
- Metadata buffer tracking is used so directory/hash changes can be marked dirty against inode metadata.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/affs/affs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/affs/amigaffs.c -->
# File Research: sources/os/linux/linux/fs/affs/amigaffs.c

Implements AFFS on-disk structure helpers: hash chains, link removal, checksums, date/protection conversion, error reporting, and name validation.

Key behavior:
- `affs_insert_hash()` inserts a file header block into a directory hash chain:
  - Hashes the name.
  - Traverses the hash chain to the end.
  - Sets parent/hash-chain fields.
  - Fixes checksums and dirties directory metadata.
  - Updates directory mtime/ctime and inode version.
- `affs_remove_hash()` removes a header block from its directory hash chain and patches either the hash table slot or previous entry’s hash-chain pointer.
- `affs_fix_dcache()` updates alias dentry `d_fsdata` when a hardlink block is replaced by the inode’s main block.
- `affs_remove_link()` removes an AFFS hardlink block:
  - If removing the head entry, promotes the first link by copying its name/hash position.
  - Unlinks the link-chain entry.
  - Frees the removed link block.
  - Adjusts nlink when appropriate.
- `affs_empty_dir()` checks whether a directory hash table contains any children.
- `affs_remove_header()` removes a filesystem object:
  - Locks link and directory state.
  - Verifies directories are empty.
  - Removes from parent hash.
  - Removes a hardlink or clears nlink.
  - Marks inode ctime/dirty.
- `affs_checksum_block()` sums big-endian 32-bit words.
- `affs_fix_checksum()` recomputes the header checksum field.
- `affs_secs_to_datestamp()` converts Unix seconds to Amiga days/minutes/ticks, applying timezone and epoch delta.
- `affs_prot_to_mode()` maps Amiga protection bits to Linux permissions.
- `affs_mode_to_prot()` maps Linux permissions back to Amiga protection bits, handling inverted owner bits and MUFS group/other bits.
- `affs_error()` logs critical errors and remounts the filesystem read-only.
- `affs_warning()` logs nonfatal warnings.
- `affs_check_name()` validates AFFS names, optionally enforcing no truncation beyond 30 bytes.
- `affs_copy_name()` writes a length-prefixed AFFS name.

Important interactions:
- Hash/link logic is called by namei operations.
- Bitmap block freeing is delegated to `bitmap.c`.
- Error handling can force the whole mounted filesystem read-only.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/affs/amigaffs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/affs/amigaffs.h -->
# File Research: sources/os/linux/linux/fs/affs/amigaffs.h

Defines AFFS/Amiga on-disk constants and packed structures.

Key behavior:
- Defines filesystem type constants for OFS/FFS, international variants, directory-cache variants, and MUFS variants.
- Defines primary and secondary block type constants such as `T_SHORT`, `T_LIST`, `T_DATA`, `ST_FILE`, `ST_ROOT`, `ST_USERDIR`, `ST_SOFTLINK`, and link types.
- Defines root bitmap slot count and Amiga epoch delta.
- Defines Amiga date structures.
- Defines on-disk root block header and tail structures, including bitmap pointers, root/disk dates, disk name, and secondary type.
- Defines generic file/directory header and tail structures with hash table, uid/gid, protection, size, comment, date, name, link chain, hash chain, parent, extension, and secondary type.
- Defines symlink and data block layouts.
- Defines Amiga protection bit masks, including inverted classic owner flags and MUFS group/other flags.

Important interactions:
- Used by `affs.h` macros and AFFS implementation files to parse and modify on-disk blocks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/affs/amigaffs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/affs/bitmap.c -->
# File Research: sources/os/linux/linux/fs/affs/bitmap.c

Implements AFFS bitmap-based free-space accounting, allocation, deallocation, initialization, and cleanup.

Key behavior:
- `affs_count_free_blocks()` sums cached per-bitmap free counts under `s_bmlock`; returns zero for read-only mounts.
- `affs_free_block()`:
  - Validates block range.
  - Locates the bitmap block and bit for the block.
  - Reads/caches the active bitmap buffer.
  - Detects double-free attempts.
  - Sets the free bit, adjusts bitmap checksum, marks buffer and superblock dirty, and increments free count.
- `affs_alloc_block()`:
  - Uses inode preallocation first when available.
  - Normalizes invalid goals to the reserved boundary.
  - Searches bitmap blocks with free space, wrapping as needed.
  - Locates a free bit in big-endian bitmap words.
  - Preallocates consecutive free bits within the same word.
  - Clears allocated bits, adjusts checksum, marks bitmap/superblock dirty, and returns the allocated block.
  - Returns zero on full filesystem or bitmap read failure.
- `affs_init_bitmap()`:
  - Skips initialization for read-only mounts.
  - Forces read-only if the root bitmap valid flag is clear.
  - Computes bitmap geometry and allocates `s_bitmap`.
  - Reads bitmap block pointers from the root block and bitmap extension blocks.
  - Validates bitmap checksums, forcing read-only on invalid bitmap.
  - Counts free bits with `memweight()`.
  - Marks unused bits beyond partition end allocated in the last bitmap block and recomputes its checksum.
- `affs_free_bitmap()` releases the cached bitmap buffer and bitmap info array.

Important interactions:
- Allocation/freeing are protected by `s_bmlock`.
- `affs_alloc_block()` maintains per-inode last allocation and preallocation state.
- Invalid bitmap state downgrades the mount to read-only rather than continuing writable operation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/affs/bitmap.c -->