# Group Research: group_935_linux_stable_sources_os_linux_linux_stable_fs_9p_Kconfig_sources_os__6e58c5cce5f6

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/9p/Kconfig
- Purpose: Defines kernel configuration switches for the Linux 9P filesystem client.
- Main options: `9P_FS` enables the filesystem; `9P_FSCACHE` enables FS-Cache integration; `9P_FS_POSIX_ACL` enables POSIX ACL support; `9P_FS_SECURITY` enables security xattr support.
- Integration: Ties the filesystem to the network 9P client stack and optional VFS features such as ACLs, xattrs, and caching.
- Build impact: These symbols drive object selection in `fs/9p/Makefile` and conditional code in `acl.h`, `cache.h`, and xattr/security handlers.
- Research notes: Configuration combinations are important because many 9P helper headers provide inline no-op fallbacks when optional ACL/cache support is disabled.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/9p/Makefile
- Purpose: Builds the 9P filesystem module/object set.
- Main object: `9p.o` is built when `CONFIG_9P_FS` is enabled.
- Core objects: Includes session/superblock/VFS/inode/dentry/dir/file/fid/address-space/xattr support.
- Conditional objects: Adds `cache.o` under `CONFIG_9P_FSCACHE` and `acl.o` under `CONFIG_9P_FS_POSIX_ACL`.
- Integration: Encodes the module boundary for the whole `fs/9p` subtree.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/acl.c -->
# File Research: sources/os/linux/linux-stable/fs/9p/acl.c
- Purpose: Implements POSIX ACL support for 9P by translating between VFS ACL objects and 9P xattr operations.
- Main functions: `v9fs_get_acl`, `v9fs_iop_get_inode_acl`, `v9fs_iop_get_acl`, `v9fs_iop_set_acl`, `v9fs_acl_chmod`, `v9fs_set_create_acl`, `v9fs_acl_mode`.
- Data flow: Reads ACL xattrs through `v9fs_fid_xattr_get`, converts via `posix_acl_from_xattr`, caches ACLs on inodes, and writes ACLs with `v9fs_fid_xattr_set` or `v9fs_xattr_set`.
- Protocol behavior: Dotl and non-dotl paths differ for ACL setting and chmod interactions; dotl can use VFS setattr support for mode updates.
- Integration: Called during inode creation, chmod/setattr, and inode/dentry ACL inode operations declared in `acl.h`.
- Risks: ACL caching assumes inode instantiation populates cached ACL state; code uses `BUG_ON(is_uncached_acl())` for violated expectations. Error handling around xattr absence versus malformed ACL data is central to correct behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/acl.h -->
# File Research: sources/os/linux/linux-stable/fs/9p/acl.h
- Purpose: Declares 9P ACL interfaces and provides disabled-config fallbacks.
- Main exports: ACL get/set inode operations, `v9fs_get_acl`, `v9fs_acl_chmod`, `v9fs_set_create_acl`, `v9fs_put_acl`, and `v9fs_acl_mode`.
- Conditional behavior: Under `CONFIG_9P_FS_POSIX_ACL`, real functions are declared. Without it, inode operation pointers are `NULL` and helpers return success/no ACL work.
- Integration: Used by inode creation, chmod, superblock xattr setup, and dotl/non-dotl inode operation tables.
- Research notes: This header is the compile-time compatibility layer that keeps 9P buildable without ACL support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/cache.c -->
# File Research: sources/os/linux/linux-stable/fs/9p/cache.c
- Purpose: Implements FS-Cache cookie acquisition for 9P sessions and inodes.
- Main functions: `v9fs_cache_session_get_cookie` and `v9fs_cache_inode_get_cookie`.
- Session flow: Builds a volume name from device/cache tag/aname data and calls `fscache_acquire_volume`, storing the result in `v9ses->fscache`.
- Inode flow: Uses the 9P qid version/path as coherency keys and calls `fscache_acquire_cookie` for regular-file cache state.
- Integration: Used by mount/session setup and inode instantiation/open paths when `CACHE_FSCACHE` is active.
- Risks: Cache identity depends on qid metadata and selected mount cache tag; incorrect tag sharing could affect coherency assumptions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/cache.h -->
# File Research: sources/os/linux/linux-stable/fs/9p/cache.h
- Purpose: Declares 9P FS-Cache helpers and disabled-cache fallback behavior.
- Main exports: `v9fs_cache_session_get_cookie` and `v9fs_cache_inode_get_cookie`.
- Conditional behavior: With `CONFIG_9P_FSCACHE`, real helpers are used. Without it, inode cookie acquisition is an inline no-op.
- Integration: Included by session, inode, file, and address-space code that needs cache-aware behavior.
- Research notes: The header hides most compile-time differences from the rest of the 9P code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/fid.c -->
# File Research: sources/os/linux/linux-stable/fs/9p/fid.c
- Purpose: Manages 9P FID lookup, cloning, attachment to dentries/inodes, and path walking.
- Main functions: `v9fs_fid_add`, `v9fs_fid_find_inode`, `v9fs_open_fid_add`, `build_path_from_dentry`, `v9fs_fid_lookup`.
- Dentry model: Stores FIDs in `d_fsdata` hlist entries, releases them from dentry operations, and reuses/duplicates them for parent/child walks.
- Inode model: Tracks open FIDs in `v9fs_inode->writeback_fid` and open fid lists so cached writeback and netfs operations can find suitable readable/writeable handles.
- Lookup flow: Builds path components up to a usable ancestor/root FID, performs 9P walk, and handles clone/retry logic.
- Risks: Correct fid reference counting is critical; lookup must balance dentry aliasing, disconnected dentries, open-file writeback requirements, and uid-specific access.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/fid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/fid.h -->
# File Research: sources/os/linux/linux-stable/fs/9p/fid.h
- Purpose: Declares FID lookup helpers and small inline wrappers.
- Main APIs: `v9fs_fid_find_inode`, `v9fs_fid_lookup`, `v9fs_parent_fid`, `clone_fid`, `v9fs_fid_clone`, `v9fs_fid_add_modes`.
- Integration: Used by nearly every VFS operation to obtain a protocol handle before issuing 9P requests.
- Behavior: `v9fs_fid_add_modes` annotates a FID with open mode/access/caching information derived from mount flags and file flags.
- Research notes: This header is the bridge between VFS objects and 9P client state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/fid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/v9fs.c -->
# File Research: sources/os/linux/linux-stable/fs/9p/v9fs.c
- Purpose: Implements 9P module/session lifecycle, mount option parsing, sysfs cache reporting, and inode-cache setup.
- Main functions: `v9fs_parse_param`, `v9fs_apply_options`, `v9fs_session_init`, `v9fs_session_close`, `v9fs_session_cancel`, `v9fs_session_begin_cancel`, `init_v9fs`, `exit_v9fs`.
- Mount parsing: Uses `fs_context` parameter specs to parse access mode, cache mode, protocol version, debug, uid/gid, dfltuid/dfltgid, aname, cache tag, transport options, and client options.
- Session setup: Allocates/initializes `v9fs_session_info`, creates a 9P client, attaches the root fid, sets cache policy, initializes rename serialization, and registers session state.
- Cache modes: Converts textual cache options into bit flags such as metadata, loose, mmap, fscache, and writeback-related behavior.
- Integration: Provides module init/exit, sysfs session cache visibility, and exports session helpers consumed by superblock setup.
- Risks: Option combinations affect data coherency and writeback semantics; protocol version selection controls whether dotl or legacy operation tables are used.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/v9fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/v9fs.h -->
# File Research: sources/os/linux/linux-stable/fs/9p/v9fs.h
- Purpose: Central private header for the 9P filesystem.
- Main types: `v9fs_session_info`, `v9fs_inode`, session flag enums, cache shortcut/bit enums.
- Session state: Holds the 9P client, mount options, cache mode, protocol version, uid/gid defaults, rename semaphore, fscache volume, and session list linkage.
- Inode state: Embeds `netfs_inode`, stores qid, cache validity flags, mutex, open fid list, and optional writeback fid.
- Main helpers: `V9FS_I`, `v9fs_inode_cookie`, `v9fs_session_cache`, `v9fs_inode2v9ses`, `v9fs_dentry2v9ses`, `v9fs_proto_dotu`, `v9fs_proto_dotl`.
- Integration: Declares VFS operation tables and inode-from-fid helpers used across superblock, inode, file, dentry, and address-space code.
- Risks: Session and inode structs encode coherency, protocol, and cache invariants shared across all 9P operations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/v9fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/v9fs_vfs.h -->
# File Research: sources/os/linux/linux-stable/fs/9p/v9fs_vfs.h
- Purpose: Declares VFS-facing 9P operations and common VFS helpers.
- Main declarations: Filesystem type, address-space ops, file ops, dir ops, dentry ops, inode cache, inode allocation/init, stat conversion, refresh, setattr, and invalidate helpers.
- Constants: Defines lock timeout, stat-to-inode flags, and `QID2INO` conversion for deriving inode numbers from 9P qids.
- Integration: Shared by superblock, inode, dentry, file, dir, xattr, and ACL implementation files.
- Research notes: This is the VFS contract header for the 9P subtree.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/v9fs_vfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/vfs_addr.c -->
# File Research: sources/os/linux/linux-stable/fs/9p/vfs_addr.c
- Purpose: Implements 9P address-space operations through the kernel netfs library.
- Main functions: `v9fs_begin_writeback`, `v9fs_issue_write`, `v9fs_issue_read`, `v9fs_init_request`, `v9fs_free_request`.
- Netfs integration: Provides `v9fs_req_ops` callbacks and `v9fs_addr_operations` using `netfs_read_folio`, `netfs_readahead`, `netfs_dirty_folio`, `netfs_writepages`, and related helpers.
- FID handling: Finds or references a suitable FID for reads/writes, stores it in `rreq->netfs_priv`, and releases it when the request completes.
- I/O behavior: Uses `p9_client_read` and `p9_client_write`, sizing requests by `msize`, protocol header size, and optional fid iounit.
- Risks: Read-for-write and writeback require a FID with correct access mode; missing open FIDs trigger warnings and I/O errors.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/vfs_addr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/vfs_dentry.c -->
# File Research: sources/os/linux/linux-stable/fs/9p/vfs_dentry.c
- Purpose: Implements 9P dentry lifecycle and validation operations.
- Main functions: `v9fs_cached_dentry_delete`, `v9fs_dentry_release`, `__v9fs_lookup_revalidate`, `v9fs_lookup_revalidate`, dentry unalias lock helpers.
- Dentry release: Walks FIDs stored in `d_fsdata`, removes them, and drops references.
- Revalidation: Refreshes inode attributes when `V9FS_INO_INVALID_ATTR` is set, using dotl or legacy refresh paths based on session protocol.
- Operation tables: Provides cached and uncached dentry operation sets; cached mode adds revalidation and negative-dentry deletion.
- Risks: Dentry aliasing is serialized through the session `rename_sem`; incorrect FID cleanup would leak protocol handles.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/vfs_dentry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/vfs_dir.c -->
# File Research: sources/os/linux/linux-stable/fs/9p/vfs_dir.c
- Purpose: Implements 9P directory file operations.
- Main functions: `v9fs_dir_readdir`, `v9fs_dir_readdir_dotl`, `v9fs_dir_release`.
- Legacy readdir: Reads raw 9P stat records with `p9_client_read`, decodes them, maps 9P mode bits to `DT_*`, and emits VFS dirents.
- Dotl readdir: Uses `p9_client_readdir` and `p9_dirent` data for Linux 9P2000.L directory entries.
- Release behavior: Clunks/drops the directory FID and frees readdir buffer state.
- Operation tables: Exports `v9fs_dir_operations` and `v9fs_dir_operations_dotl`.
- Risks: Directory offsets and partial record handling must remain consistent across repeated `iterate_shared` calls.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/vfs_dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/vfs_file.c -->
# File Research: sources/os/linux/linux-stable/fs/9p/vfs_file.c
- Purpose: Implements 9P regular-file open/read/write/mmap/fsync/locking operations.
- Main functions: `v9fs_file_open`, lock helpers, `v9fs_file_read_iter`, `v9fs_file_write_iter`, `v9fs_file_fsync`, `v9fs_file_fsync_dotl`, `v9fs_file_mmap_prepare`, `v9fs_vm_page_mkwrite`.
- Open flow: Clones or looks up a FID, opens it with the right 9P mode, stores it in `file->private_data`, initializes cache usage, and records open FIDs for writeback.
- I/O flow: Cached modes use generic/netfs paths; direct behavior issues 9P client reads/writes through the open FID.
- Locking: Supports legacy 9P lock protocol and dotl `getlock`/`lock`/`flock` behavior with VFS lock structures.
- Mmap behavior: Prepares cached mappings and handles page write faults for writeback-capable mappings.
- Risks: File flag to protocol-mode mapping, fscache cookie use/unuse, and FID lifetime around open/writeback are correctness-sensitive.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/vfs_file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/vfs_inode.c -->
# File Research: sources/os/linux/linux-stable/fs/9p/vfs_inode.c
- Purpose: Implements legacy/dotu 9P inode operations and common inode conversion logic.
- Main functions: mode conversion helpers, `v9fs_alloc_inode`, `v9fs_init_inode`, `v9fs_evict_inode`, `v9fs_inode_from_fid`, `v9fs_create`, `v9fs_vfs_lookup`, `v9fs_vfs_atomic_open`, unlink/rmdir/rename/getattr/setattr/symlink/link/mknod helpers, `v9fs_stat2inode`, `v9fs_refresh_inode`.
- Protocol conversion: Maps Unix modes/open flags to 9P modes and maps 9P stat metadata back into Linux inode state.
- Create/open path: Uses parent FIDs and `p9_client_create`/walk operations, instantiates or reuses inodes based on cache policy, and attaches FIDs to dentries/files.
- Metadata path: Uses `p9_client_stat`/`p9_client_wstat`; invalidates cached inode attributes after modifications.
- Operation tables: Provides legacy and dotu directory/file/symlink inode operations with dotu-only symlink/link handling.
- Risks: Rename serializes through `rename_sem`; cached versus uncached inode instantiation changes alias behavior; writeback/fscache resizing must stay synchronized with remote size changes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/vfs_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/vfs_inode_dotl.c -->
# File Research: sources/os/linux/linux-stable/fs/9p/vfs_inode_dotl.c
- Purpose: Implements Linux 9P2000.L inode operations with dotl-specific protocol calls and metadata formats.
- Main functions: `v9fs_inode_from_fid_dotl`, `v9fs_open_to_dotl_flags`, `v9fs_vfs_create_dotl`, `v9fs_vfs_atomic_open_dotl`, `v9fs_vfs_getattr_dotl`, `v9fs_vfs_setattr_dotl`, `v9fs_stat2inode_dotl`, symlink/link/mknod/get_link/refresh helpers.
- Dotl protocol: Uses `p9_client_getattr_dotl`, `p9_client_setattr`, `p9_client_create_dotl`, `p9_client_mkdir_dotl`, `p9_client_symlink`, `p9_client_link`, `p9_client_mknod_dotl`, and `p9_client_readlink`.
- Attribute mapping: Converts Linux open flags and iattr valid bits to dotl flags/masks; maps `p9_stat_dotl` into inode fields.
- ACL integration: Creation helpers prepare inherited POSIX ACLs and write them after successful remote object creation.
- Operation tables: Exports dotl directory, file, and symlink inode operations.
- Risks: Dotl mode/flag mapping must match server expectations; ACL and gid inheritance during create affect POSIX compatibility.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/vfs_inode_dotl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/vfs_super.c -->
# File Research: sources/os/linux/linux-stable/fs/9p/vfs_super.c
- Purpose: Implements 9P superblock, mount, unmount, statfs, writeback, and fs_context behavior.
- Main functions: `v9fs_fill_super`, `v9fs_get_tree`, `v9fs_kill_super`, `v9fs_umount_begin`, `v9fs_statfs`, `v9fs_write_inode`, `v9fs_write_inode_dotl`, `v9fs_init_fs_context`.
- Mount flow: Initializes session, attaches root FID, instantiates root inode, selects operation tables based on protocol/cache/ACL/xattr options, and creates root dentry.
- Super operations: Provide statfs, drop_inode, write_inode, and show-options behavior.
- Fs context: Allocates mount context, wires parse/get_tree/free operations, and stores client/session options before mount.
- Integration: Registers `v9fs_fs_type`; coordinates with `v9fs.c` session setup and inode creation helpers.
- Risks: Mount failure paths must clunk FIDs and close sessions; dotl versus legacy write_inode behavior differs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/vfs_super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/9p/xattr.c
- Purpose: Implements extended attribute get/set/list and VFS xattr handlers for 9P.
- Main functions: `v9fs_fid_xattr_get`, `v9fs_xattr_get`, `v9fs_xattr_set`, `v9fs_fid_xattr_set`, `v9fs_listxattr`, xattr handler get/set callbacks.
- Protocol flow: Uses xattr walk/open/read and create/write/clunk style 9P operations through FIDs.
- VFS integration: Exports `v9fs_xattr_handlers` for generic xattr namespaces and conditional security xattrs.
- ACL integration: ACL code uses the FID xattr helpers to fetch and write POSIX ACL xattr payloads.
- Risks: Buffer sizing and two-phase get operations must distinguish required size from actual read errors.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/xattr.h -->
# File Research: sources/os/linux/linux-stable/fs/9p/xattr.h
- Purpose: Declares xattr support shared by 9P xattr and ACL code.
- Main exports: `v9fs_fid_xattr_get`, `v9fs_xattr_get`, `v9fs_xattr_set`, `v9fs_fid_xattr_set`, `v9fs_listxattr`, and `v9fs_xattr_handlers`.
- Integration: Included by inode/super/ACL code to wire VFS xattr handlers and POSIX ACL persistence.
- Research notes: This header carries the public internal xattr contract for the 9P subtree.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/9p/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/Kconfig
- Purpose: Top-level Linux filesystem Kconfig menu.
- Main role: Defines global filesystem infrastructure options and sources per-filesystem Kconfig files.
- Infrastructure options: Includes dcache word access, fs parser validation, iomap, stacking, buffer heads, direct I/O, DAX, POSIX ACLs, exportfs, file locking, crypto, verity, notify, quota, caches, pseudo filesystems, and network filesystems.
- Local filesystem integration: Sources ext, jfs, xfs, gfs2, ocfs2, btrfs, nilfs2, f2fs, zonefs, ADFS, AFFS, and many other filesystem menus.
- Network integration: Sources NFS/NFSD, SUNRPC, Ceph, SMB, Coda, AFS, and 9P.
- Research notes: This file determines menu hierarchy and shared config symbols that lower-level filesystem code depends on.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/Makefile
- Purpose: Top-level build manifest for Linux filesystem and VFS code.
- Core build: Always builds VFS core objects such as open/read-write/file-table/super/inode/dcache/namei/stat/namespace/splice/sync/attr and related infrastructure.
- Conditional build: Adds filesystems and subsystems according to `CONFIG_*` symbols, including `9p/`, `adfs/`, and `affs/`.
- Integration: Maps top-level Kconfig selections to compiled directories and object files.
- Research notes: Ordering matters for some entries, such as hfsplus before hfs; this file is the build-level counterpart to `fs/Kconfig`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/adfs/Kconfig
- Purpose: Defines configuration options for Acorn Disc Filing System support.
- Main options: `ADFS_FS` enables read support; `ADFS_FS_RW` enables experimental write support.
- Integration: Appears under miscellaneous filesystems and controls `fs/adfs/Makefile`.
- Behavior: Write support is separately gated because the driver primarily targets reading ADFS media and has narrower write guarantees.
- Research notes: The split config matches code paths where update/writeback functions exist but are optional.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/adfs/Makefile
- Purpose: Builds the ADFS filesystem module/object.
- Main object: `adfs.o` is built under `CONFIG_ADFS_FS`.
- Component objects: `dir.o`, `dir_f.o`, `dir_fplus.o`, `file.o`, `inode.o`, `map.o`, and `super.o`.
- Integration: Encodes the complete ADFS implementation units: directory formats, VFS operations, block map lookup, inode handling, and mount logic.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/adfs.h -->
# File Research: sources/os/linux/linux-stable/fs/adfs/adfs.h
- Purpose: Central private header for the ADFS filesystem.
- Main types: `adfs_inode_info`, `adfs_sb_info`, `adfs_dir`, `object_info`, `adfs_dir_ops`, and `adfs_discmap`.
- Constants: Defines special fragment IDs, ADFS filetype handling, directory attribute bits, maximum exported name length, and mount-derived masks.
- Inline helpers: Provide inode/superblock container access, filetype extraction, signed shifts, block mapping via `adfs_map_lookup`, disc record mapping, and disc size calculation.
- Integration: Declares cross-file functions for inode lookup/setattr/writeback, directory operations, map reading/freeing, statfs, and error reporting.
- Risks: Many values are stored in compact historical on-disk formats; helpers centralize endian, bit-shift, and address conversion assumptions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/adfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/adfs/dir.c
- Purpose: Implements common ADFS directory reading, updating, lookup, iteration, and dentry comparison.
- Main functions: `adfs_dir_read_buffers`, `adfs_dir_read_inode`, `adfs_dir_update`, `adfs_object_fixup`, `adfs_iterate`, `adfs_dir_lookup_byname`, `adfs_lookup`.
- Directory abstraction: Uses `adfs_dir_ops` so old F-format and F+ directory implementations share VFS-level logic.
- Name handling: Converts special ADFS names, optionally appends filetype suffixes, and performs case-insensitive dentry hashing/comparison.
- Concurrency: Uses a directory read/write semaphore around iteration and update operations.
- Operation tables: Exports `adfs_dir_operations`, `adfs_dentry_operations`, and `adfs_dir_inode_operations`.
- Risks: Directory buffer read/update paths depend on correct indirect address mapping and validation by the selected directory format implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/dir_f.c -->
# File Research: sources/os/linux/linux-stable/fs/adfs/dir_f.c
- Purpose: Implements classic ADFS F-format directory operations.
- Main functions: `adfs_f_validate`, `adfs_f_read`, `adfs_f_setpos`, `adfs_f_getnext`, `adfs_f_iterate`, `adfs_f_update`, `adfs_f_commit`.
- Format handling: Reads/writes packed little multi-byte fields with helper functions and uses fixed-size directory entries.
- Validation: Checks directory start/end metadata and directory check bytes.
- Object conversion: Converts between `adfs_direntry` and generic `object_info`.
- Integration: Exports `adfs_f_dir_ops` for use by common directory and mount code.
- Risks: Fixed name length and check-byte recomputation make boundary and corruption handling important.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/dir_f.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/dir_f.h -->
# File Research: sources/os/linux/linux-stable/fs/adfs/dir_f.h
- Purpose: Defines on-disk structures for classic ADFS F-format directories.
- Main structures: `adfs_dirheader`, `adfs_direntry`, `adfs_olddirtail`, and `adfs_newdirtail`.
- Constants: Defines directory size, entry count, and short F-format filename limit.
- Integration: Consumed by `dir_f.c`, `dir.c`, and mount code that creates root object metadata.
- Research notes: Structures are direct on-disk layouts and should be treated as format contracts.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/dir_f.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/dir_fplus.c -->
# File Research: sources/os/linux/linux-stable/fs/adfs/dir_fplus.c
- Purpose: Implements ADFS F+ large-directory operations.
- Main functions: `adfs_fplus_validate_header`, `adfs_fplus_validate_tail`, `adfs_fplus_checkbyte`, `adfs_fplus_read`, `adfs_fplus_getnext`, `adfs_fplus_iterate`, `adfs_fplus_update`, `adfs_fplus_commit`.
- Format handling: Supports variable-sized directory storage with a header, entry array, name area, and tail.
- Validation: Checks magic values, size/entry bounds, tail metadata, and check byte.
- Object conversion: Reads little-endian big directory entries into `object_info` and copies names from the directory name area.
- Integration: Exports `adfs_fplus_dir_ops` and is selected by mount code when the disc record indicates F+ directories.
- Risks: Size calculations guard against malformed directories; update logic must locate entries by indirect address.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/dir_fplus.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/dir_fplus.h -->
# File Research: sources/os/linux/linux-stable/fs/adfs/dir_fplus.h
- Purpose: Defines on-disk structures and constants for ADFS F+ directories.
- Main structures: `adfs_bigdirheader`, `adfs_bigdirentry`, and `adfs_bigdirtail`.
- Constants: Defines maximum F+ name length and header/tail magic values.
- Integration: Used by `dir_fplus.c` and included by mount/super code for root directory sizing decisions.
- Research notes: This file captures the large-directory disk format contract.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/dir_fplus.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/adfs/file.c
- Purpose: Defines ADFS regular-file VFS operation tables.
- Main exports: `adfs_file_operations` and `adfs_file_inode_operations`.
- File ops: Uses generic read/write/mmap/splice/llseek helpers appropriate for buffered filesystem files.
- Inode ops: Wires `adfs_setattr` for metadata changes.
- Integration: Actual block mapping and writeback are implemented in `inode.c`; this file supplies the VFS table glue.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/adfs/inode.c
- Purpose: Implements ADFS inode instantiation, block mapping, address-space operations, attribute conversion, and inode writeback.
- Main functions: `adfs_get_block`, `adfs_writepages`, `adfs_read_folio`, `adfs_write_begin`, `_adfs_bmap`, `adfs_atts2mode`, `adfs_mode2atts`, time conversion helpers, `adfs_iget`, `adfs_setattr`, `adfs_write_inode`.
- Block mapping: Resolves file fragment/offset pairs through `__adfs_block_map` and `adfs_map_lookup`.
- Metadata conversion: Maps ADFS directory attributes and load/exec timestamps to Linux mode, uid/gid, size, and timestamps.
- VFS integration: Supplies buffered address-space operations and inode update/writeback hooks.
- Risks: Timestamp encoding and ADFS filetype bits share load/exec fields; writeback must update parent directory entries through `adfs_dir_update`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/map.c -->
# File Research: sources/os/linux/linux-stable/fs/adfs/map.c
- Purpose: Implements ADFS free-space/fragment map reading, validation, lookup, and statfs accounting.
- Main functions: `lookup_zone`, `scan_free_map`, `scan_map`, `adfs_map_statfs`, `adfs_map_lookup`, `adfs_checkmap`, `adfs_map_read`, `adfs_read_map`, `adfs_free_map`.
- Format model: Treats the map as zones containing variable-sized fragment bitstreams with fragment IDs and free-space records.
- Lookup flow: Converts fragment ID and file offset into a zone/map offset, scans map entries, and returns a physical sector/block address.
- Validation: Recomputes zone check and cross-check bytes before accepting the map.
- Integration: Used by inode block mapping and superblock mount/statfs logic.
- Risks: Bit-level parsing, signed shifts, zone wrapping, and corrupt-map handling are central to safe reads.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/adfs/super.c
- Purpose: Implements ADFS mount, superblock operations, option parsing, disc record validation, inode cache, and module lifecycle.
- Main functions: `adfs_checkdiscrecord`, `adfs_parse_param`, `adfs_reconfigure`, `adfs_statfs`, `adfs_probe`, `adfs_validate_bblk`, `adfs_validate_dr0`, `adfs_fill_super`, `adfs_init_fs_context`, module init/exit.
- Mount flow: Parses owner/group/mask/filetype suffix options, probes for disc records, reads and validates the map, selects F or F+ directory ops, creates the root inode/dentry, and sets default dentry operations.
- Super operations: Allocate/free/drop inodes, write inodes, put super, statfs, and show mount options.
- Integration: Registers the `adfs` filesystem type and uses block-device mount support through `get_tree_bdev`.
- Risks: Disc record validation protects against invalid geometry and oversized media; mount cleanup must release maps and buffers on partial failure.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/adfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/affs/Kconfig
- Purpose: Defines configuration for Amiga Fast File System support.
- Main option: `AFFS_FS` enables AFFS filesystem support.
- User-facing role: Supports mounting Amiga FFS/OFS variants and related disk-file use cases.
- Integration: Controls build of `fs/affs/` through the top-level filesystem Kconfig and Makefile.
- Research notes: Feature variants are largely runtime mount/format choices rather than separate Kconfig switches.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/affs/Makefile
- Purpose: Builds the AFFS filesystem module/object.
- Main object: `affs.o` is built under `CONFIG_AFFS_FS`.
- Component objects: `super.o`, `namei.o`, `inode.o`, `file.o`, `dir.o`, `amigaffs.o`, `bitmap.o`, and `symlink.o`.
- Integration: This file shows `amigaffs.c` is a shared helper unit rather than the whole filesystem implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/affs.h -->
# File Research: sources/os/linux/linux-stable/fs/affs/affs.h
- Purpose: Central private header for AFFS.
- Main types: `affs_inode_info`, `affs_bm_info`, `affs_sb_info`, and extension/cache structures for file block metadata.
- On-disk helpers: Defines macros for AFFS block headers, tails, root blocks, data blocks, hash table slots, and data payloads.
- Mount state: Stores partition geometry, root block, hash size, uid/gid/mode overrides, bitmap state, root buffer, symlink prefix state, delayed superblock work, and mount flags.
- Declarations: Exposes hash/link helpers, checksum helpers, protection conversion, bitmap allocation/freeing, namei operations, inode/file/dir/symlink operation tables, and address-space ops.
- Inline helpers: Validate block numbers, read/get/zero buffers, adjust checksums, and lock/unlock inode link/hash/extension mutexes.
- Risks: Many helpers directly manipulate buffer_head-backed on-disk structures; locking discipline around link/hash/ext state is important.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/affs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/amigaffs.c -->
# File Research: sources/os/linux/linux-stable/fs/affs/amigaffs.c
- Purpose: Implements AFFS shared on-disk helper operations for directory hash chains, hardlink chains, checksums, protection bits, errors, and names.
- Main functions: `affs_insert_hash`, `affs_remove_hash`, `affs_remove_link`, `affs_empty_dir`, `affs_remove_header`, `affs_checksum_block`, `affs_fix_checksum`, `affs_secs_to_datestamp`, `affs_prot_to_mode`, `affs_mode_to_prot`, `affs_error`, `affs_warning`, `affs_check_name`, `affs_copy_name`.
- Hash behavior: Inserts/removes header blocks in AFFS directory hash chains and updates checksums as links change.
- Link removal: Handles AFFS hardlink chain semantics, including replacing a primary header with link metadata when necessary and fixing dcache references.
- Removal flow: Checks directory emptiness, removes hash entries, updates link counts, frees link blocks, and coordinates link/hash locks.
- Metadata conversion: Converts Amiga protection bits to Linux modes and back; converts Unix seconds to Amiga datestamps.
- Error handling: Logs filesystem errors and remounts read-only when appropriate.
- Risks: Link-chain manipulation is complex and buffer/checksum updates must remain atomic enough with the surrounding inode locks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/amigaffs.c -->