# subset-b-009696 Research

Grouped source research for NFS-Ganesha VFS/XFS FSAL support and MDCACHE stackable FSAL cache/export/handle primitives. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/subfsal_vfs.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/subfsal_vfs.c

## Purpose

This file supplies the generic VFS sub-FSAL export hooks used by the common FSAL_VFS implementation. It defines the VFS export configuration block, including `fsid_type` parsing and `async_hsm_restore`, and allocates VFS object handles with inline storage for a `vfs_file_handle_t`. The source was read as a complete 113-line file.

## Important APIs, Types, and Functions

Important exported symbols are `vfs_sub_export_param`, `vfs_sub_fini`, `vfs_sub_init_export_ops`, `vfs_sub_init_export`, `vfs_sub_alloc_handle`, `vfs_obj_subops`, and `vfs_sub_init_handle`. `fsid_types` maps text tokens such as `One64`, `Two64`, `Dev`, and `Device` to `enum fsid_type` values. `vfs_obj_subops` installs `vfs_sub_getattrs` and `vfs_sub_setattrs` from the VFS attributes layer.

## Control Flow

Configuration parsing uses `export_param_block` to populate `vfs_fsal_export` fields. Export initialization optionally initializes debug ACL support, then returns success. Handle allocation zeroes one object allocation large enough for `struct vfs_fsal_obj_handle` plus file-handle storage and points `hdl->handle` at the tail. Handle initialization attaches the sub-FSAL attribute ops.

## State and Persistence Behavior

Persistent state is limited to process memory: export config fields, object handle allocations, and optional debug ACL process state. No on-disk state is written here.

## Dependencies and Integration Points

The file integrates with FSAL config parsing, `vfs_methods.h`, `subfsal.h`, and `attrs.h`. It is compiled into the VFS FSAL path and is the generic counterpart to XFS-specific `subfsal_xfs.c`.

## Risks and Edge Cases

The handle allocation assumes `vfs_file_handle_t` tail storage is sufficient for default VFS handles. Config token drift would change exported FSID behavior. Empty fini/export-op hooks are intentional but can hide future sub-FSAL cleanup requirements.

## Test Signals

Useful tests are config parsing for each `fsid_type` token, export creation with `async_hsm_restore` true/false, handle allocation under leak checking, and getattr/setattr smoke tests through the installed sub-ops.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/subfsal_vfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs_methods.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs_methods.h

## Purpose

This header is the central internal contract for FSAL_VFS. It defines VFS module/export/object structures, inline helpers, and prototypes for export, handle, state, I/O, xattr, credential, and filesystem-handle operations. The source was read as a complete 402-line file.

## Important APIs, Types, and Functions

Core types are `struct vfs_fsal_module`, `struct vfs_fsal_export`, `struct vfs_subfsal_obj_ops`, `struct vfs_fd`, `struct vfs_state_fd`, `struct vfs_fsal_obj_handle`, and `struct closefd`. Conversion macros include `EXPORT_VFS_FROM_FSAL` and `OBJ_VFS_FROM_FSAL`. Important APIs include `vfs_create_export`, `vfs_update_export`, `vfs_lookup_path`, `vfs_create_handle`, `vfs_fd_to_handle`, `vfs_name_to_handle`, `vfs_open_by_handle`, `vfs_check_handle`, `vfs_get_root_handle`, `vfs_fsal_open`, `alloc_handle`, `free_vfs_fsal_obj_handle`, `vfs_open2/read2/write2/setattr2/close2`, xattr operations, HSM and FS_LOCATIONS helpers, and `find_fd`.

## Control Flow

The header does not execute by itself, but it shapes runtime dispatch. Module registration installs FSAL ops; export methods create VFS handles; handle methods use the syscall helpers to convert file descriptors, path names, wire handles, and root filesystem state into FSAL object handles; I/O/state paths use `vfs_fd` or `vfs_state_fd`; xattr and credential helpers are called by object methods.

## State and Persistence Behavior

The state model is in-memory. `vfs_fsal_export` stores FSID and async HSM options. `vfs_fsal_obj_handle` stores the FSAL object, device id, handle bytes, sub-FSAL ops, upcall vector, and a union for file descriptors/share state, symlink contents, or unopenable socket/device names. Persistence on disk is delegated to kernel filesystems.

## Dependencies and Integration Points

Includes connect this header to `fsal_handle_syscalls.h`, `fsal_api.h`, FSAL commonlib/localfs, and access checks. It is consumed by generic VFS files, the XFS specialization, xattr code, state handling, and export creation.

## Risks and Edge Cases

`root_fd` stores an integer fd through `fs->private_data`, so ownership and lifetime must match filesystem claim/unclaim rules. `vfs_unopenable_type` must stay aligned with handle allocation for sockets and devices. Credential helpers branch on `only_one_user`; missed restore calls can leak effective credentials.

## Test Signals

Compile coverage across all VFS sub-FSALs is essential. Behavioral tests should exercise file, directory, symlink, socket/device handles, root-handle extraction, multi-state open/read/write/close, credential switching, xattr dispatch, and stale handle validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs_methods.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xattrs.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xattrs.c

## Purpose

This file implements VFS FSAL extended attribute operations. It combines a small built-in virtual xattr namespace with native Linux xattr syscalls over file descriptors opened from VFS object handles. The source was read as a complete 641-line file.

## Important APIs, Types, and Functions

Local types are `xattr_getfunc_t`, `xattr_setfunc_t`, and `struct fsal_xattr_def`. The built-in table contains read-only `vfshandle`, implemented by `print_vfshandle`. Helpers include `do_match_type`, `attr_is_read_only`, `xattr_id_to_name`, and `xattr_name_to_id`. Public FSAL methods are `vfs_list_ext_attrs`, `vfs_getextattr_id_by_name`, `vfs_getextattr_value_by_id`, `vfs_getextattr_value`, `vfs_getextattr_value_by_name`, `vfs_setextattr_value`, `vfs_setextattr_value_by_id`, `vfs_remove_extattr_by_id`, and `vfs_remove_extattr_by_name`.

## Control Flow

Listing first emits built-in entries allowed for the object type, then opens the object and appends `flistxattr` names after the cookie. Name-to-id opens the object except for built-ins and searches the native name list; `system.posix_acl_access` is treated as a special synthetic id. Get-by-id dispatches to the built-in getter or resolves a native name then calls `fgetxattr`. Set/remove paths resolve names as needed and call `fsetxattr`/`fremovexattr`.

## State and Persistence Behavior

Built-in `vfshandle` is generated on demand. Native xattrs are persistent filesystem metadata changed by `fsetxattr` and `fremovexattr`. File descriptors are short-lived and closed in each operation unless a caller-supplied fd is used by `vfs_getextattr_value`.

## Dependencies and Integration Points

The code depends on `os/xattr.h`, VFS handle opening, FSAL error conversion, and FSAL xattr cookies. It is wired through `vfs_methods.h` object ops and may be wrapped by MDCACHE xattr methods.

## Risks and Edge Cases

`MAXPATHLEN` fixed buffers can truncate very large xattr lists. Symlinks are mostly not supported because opening by handle is object-type dependent. `vfs_getextattr_value` closes only `local_fd > 0`, so fd zero would not be closed if ever returned. Empty values are stored as one empty byte on set.

## Test Signals

Test listing cookies, small and full result arrays, built-in `vfshandle`, native create/replace/remove, `system.posix_acl_access`, unsupported symlink behavior, ERANGE on short buffers, and error mapping for missing attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xattrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/CMakeLists.txt

## Purpose

This CMake file builds the XFS FSAL module as a loadable module using the common FSAL_VFS sources plus XFS-specific syscall and sub-FSAL glue. The source was read as a complete 56-line file.

## Important APIs, Types, and Functions

Build targets are `fsalxfs` and optional imported `handle`. `fsalxfs_LIB_SRCS` includes `main.c`, shared VFS `export.c`, `handle.c`, `file.c`, `xattrs.c`, `state.c`, `empty_check_hsm.c`, `vfs_methods.h`, and XFS `handle_syscalls.c`/`subfsal_xfs.c`. It adds `-D__USE_GNU`, sanitizer integration, version `4.2.0`, SOVERSION `4`, and installation to `${FSAL_DESTINATION}`.

## Control Flow

At configure/generate time CMake defines the source list, creates a module library, optionally imports libhandle from `PATH_LIBHANDLE`, links `ganesha_nfsd`, system libraries, undefined-symbol protection, and `handle`, then emits install rules.

## State and Persistence Behavior

No runtime state is owned by this file. It controls build artifacts and install layout for the XFS FSAL shared object.

## Dependencies and Integration Points

The important external dependency is XFS libhandle, exposed as `handle` and used by `handle_syscalls.c`. The module integrates common FSAL_VFS implementation with XFS-specific handle support.

## Risks and Edge Cases

`target_link_libraries(fsalxfs handle)` is unconditional even though the imported target is only created under `PATH_LIBHANDLE`; builds rely on a system `handle` library or CMake target resolution. Source-list drift can silently omit common VFS behavior from the module.

## Test Signals

Build with and without explicit `PATH_LIBHANDLE`, run link-time undefined-symbol checks, verify installed module naming/version, and run FSAL_XFS smoke tests that require libhandle symbols.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/handle_syscalls.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/handle_syscalls.c

## Purpose

This file implements the FSAL_VFS handle syscall layer for XFS using libhandle and XFS ioctls. It converts between file descriptors, names, XFS file handles, FSAL FSIDs, dummy export handles, and root mount handles. The source was read as a complete 416-line file.

## Important APIs, Types, and Functions

Important functions are `display_xfs_handle`, `xfs_fsal_bulkstat_inode`, `xfs_fsal_inode2handle`, `vfs_open_by_handle`, `vfs_fd_to_handle`, `vfs_name_to_handle`, `vfs_readlink`, `vfs_extract_fsid`, `vfs_encode_dummy_handle`, `vfs_is_dummy_handle`, `vfs_valid_handle`, and `vfs_get_root_handle`. It uses `xfs_handle_t`, `xfs_bstat`, `XFS_IOC_FSBULKSTAT_SINGLE`, `fd_to_handle`, `open_by_handle`, `readlink_by_handle`, `path_to_fshandle`, and FSAL `encode_fsid`/`decode_fsid`.

## Control Flow

Regular files and directories get handles from an opened fd through libhandle. Other object types use `fstatat` and XFS bulkstat to synthesize handle contents from inode/generation while copying FSID from a reference fd. Open-by-handle maps `ENOENT` to stale. Root setup opens the mount point, obtains the root handle, extracts its FSID, and re-indexes the FSAL filesystem by that XFS FSID.

## State and Persistence Behavior

No persistent state is written. File-handle bytes encode XFS FSID, inode, generation, and a dummy marker in `fid_pad` for synthetic FSID-only handles. `vfs_get_root_handle` temporarily opens the root directory and updates in-memory FSAL filesystem indexing.

## Dependencies and Integration Points

This is XFS-specific glue for prototypes in `vfs_methods.h`. It depends on libhandle headers/runtime and FSAL localfs indexing. It is called by generic VFS export/handle code.

## Risks and Edge Cases

Handle size checks use caller-provided `handle_len`; undersized buffers fail with `E2BIG`. Dummy handles overload `fid_pad`, so validation must reject unsupported FSID types and nonzero generations. `vfs_get_root_handle` closes and resets `root_fd`, so callers should not expect it to keep an fd open.

## Test Signals

Run on real XFS with libhandle support: fd/name/open-by-handle round trips, symlink `readlink_by_handle`, socket/device lookup via bulkstat, dummy handle encode/extract/validate, stale-handle mapping, and export root re-indexing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/handle_syscalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/handle_syscalls.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/handle_syscalls.h

## Purpose

This header supplies the missing libhandle prototype for `fd_to_handle`, which the XFS syscall implementation needs but `xfs/handle.h` does not declare in this source version. The source was read as a complete 31-line file.

## Important APIs, Types, and Functions

It declares `int fd_to_handle(int fd, void **hanp, size_t *hlen);`.

## Control Flow

There is no runtime control flow. Including this header allows `handle_syscalls.c` to call `fd_to_handle` without relying on an implicit declaration.

## State and Persistence Behavior

No state is owned. The declared libhandle function allocates or returns handle storage through `hanp`/`hlen`, and callers free that storage with `free_handle`.

## Dependencies and Integration Points

The header belongs to the XFS FSAL build and complements `<xfs/handle.h>`. It is consumed by `handle_syscalls.c`.

## Risks and Edge Cases

Prototype drift against the installed libhandle ABI would cause compile or runtime linkage problems. The caller must preserve the allocation/free contract.

## Test Signals

Compile on distributions where `<xfs/handle.h>` lacks the prototype, link against libhandle, and exercise `vfs_fd_to_handle` so the declaration is validated at build and runtime.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/handle_syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/main.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/main.c

## Purpose

This is the FSAL_XFS module entry point. It declares static module capabilities, parses XFS FSAL configuration, probes OFD lock support, registers the FSAL, and initializes object operation vectors. The source was read as a complete 226-line file.

## Important APIs, Types, and Functions

Key symbols are `XFS_SUPPORTED_ATTRIBUTES`, `myname`, static `struct vfs_fsal_module XFS`, `xfs_params`, `xfs_param`, `init_config`, `xfs_init`, and `xfs_unload`. Configurable parameters include link/symlink support, `cansettime`, `maxread`, `maxwrite`, `umask`, `auth_xdev_export`, and `only_one_user`.

## Control Flow

Module load calls `xfs_init`, which registers FSAL name `XFS`, installs module ops (`vfs_create_export`, `vfs_update_export`, `init_config`), and initializes VFS handle ops. Configuration loading optionally creates a temporary file and uses `F_OFD_GETLK` to decide lock support, then loads `xfs_param` into the module and displays final fsinfo. Module unload unregisters the FSAL.

## State and Persistence Behavior

Runtime state is held in the static `XFS` module object: fsinfo capabilities, object ops, and `only_one_user`. The temporary OFD-lock test file is created under `/tmp` and unlinked immediately. No durable FSAL state is written.

## Dependencies and Integration Points

It integrates with FSAL registration, config parsing, VFS export/update functions, and `vfs_handle_ops_init`. Capabilities are consumed by upper NFS protocol code and export creation.

## Risks and Edge Cases

`CONFIG_UNIQUE` prevents multiple XFS module config blocks. OFD-lock probing depends on kernel headers/runtime and silently disables lock support when unavailable. ACL support depends on compile-time `ENABLE_VFS_ACL`.

## Test Signals

Load/unload the module, parse each config item, verify fsinfo values, run with and without OFD lock support, validate `only_one_user` credential behavior through VFS helpers, and run ACL-enabled and ACL-disabled builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/subfsal_xfs.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/subfsal_xfs.c

## Purpose

This file supplies the XFS-specific sub-FSAL hooks for FSAL_VFS. Compared with the generic VFS sub-FSAL, it only accepts a no-op export name parameter and allocates standard VFS object handles. The source was read as a complete 85-line file.

## Important APIs, Types, and Functions

Important symbols are `vfs_sub_export_param`, `vfs_sub_fini`, `vfs_sub_init_export_ops`, `vfs_sub_init_export`, `vfs_sub_alloc_handle`, and `vfs_sub_init_handle`.

## Control Flow

Config parsing uses `export_param_block`. Init/fini/export-op hooks are no-ops that return success. Handle allocation mirrors the generic VFS path by allocating `struct vfs_fsal_obj_handle` plus `vfs_file_handle_t` storage and pointing `hdl->handle` at the tail.

## State and Persistence Behavior

Only in-memory object handle allocations and the static config block are owned. XFS persistent behavior is handled by the common VFS code and XFS handle syscall layer.

## Dependencies and Integration Points

It includes FSAL types/API, `vfs_methods.h`, and `subfsal.h`, and is compiled into the `fsalxfs` module. XFS-specific handle behavior lives in `handle_syscalls.c`; this file just supplies sub-FSAL lifecycle glue.

## Risks and Edge Cases

The no-op hooks mean XFS-specific export initialization/cleanup cannot be performed here unless implemented later. Unlike generic VFS, this file does not attach `vfs_subfsal_obj_ops`, so behavior relies on common VFS defaults and XFS syscall functions.

## Test Signals

XFS export creation, handle allocation/free leak tests, and regression coverage that verifies XFS object methods still receive valid `vfs_fsal_obj_handle` storage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/subfsal_xfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/CMakeLists.txt

## Purpose

This CMake file selects stackable FSAL subdirectories. It conditionally includes FSAL_NULL and always includes FSAL_MDCACHE. The source was read as a complete 25-line file.

## Important APIs, Types, and Functions

The relevant CMake commands are `if(USE_FSAL_NULL)`, `add_subdirectory(FSAL_NULL)`, `endif`, and `add_subdirectory(FSAL_MDCACHE)`.

## Control Flow

During configuration, CMake adds the NULL stackable FSAL only when enabled, then adds MDCACHE unconditionally so the metadata cache object library is built.

## State and Persistence Behavior

No runtime state exists here. It controls generated build graph state.

## Dependencies and Integration Points

It is the parent build entry for stackable FSAL implementations under `src/FSAL/Stackable_FSALs`, integrating MDCACHE into the wider NFS-Ganesha build.

## Risks and Edge Cases

Making MDCACHE unconditional means missing dependencies in FSAL_MDCACHE break stackable FSAL builds. Conditional flags must stay aligned with top-level build options.

## Test Signals

Configure builds with `USE_FSAL_NULL` on/off and verify `FSAL_MDCACHE` is always entered and produces the expected object target.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/CMakeLists.txt

## Purpose

This CMake file builds the MDCACHE stackable FSAL object library. MDCACHE wraps a sub-FSAL and caches metadata, handles, dirents, and related state for NFS-Ganesha. The source was read as a complete 64-line file.

## Important APIs, Types, and Functions

The target is `fsalmdcache` as an `OBJECT` library. `fsalmdcache_LIB_SRCS` includes core headers and implementation files such as `mdcache_handle.c`, `mdcache_file.c`, `mdcache_xattrs.c`, `mdcache_main.c`, `mdcache_export.c`, `mdcache_helpers.c`, `mdcache_lru.c`, `mdcache_hash.c`, `mdcache_avl.c`, `mdcache_read_conf.c`, and `mdcache_up.c`. It adds `-D__USE_GNU`, optional DBus includes, sanitizer instrumentation, `-fPIC`, and optional LTTng trace dependencies/properties.

## Control Flow

At configure time it collects sources, creates the object library, applies sanitizer and PIC flags, and wires LTTng generation if enabled. No executable control flow is present.

## State and Persistence Behavior

No runtime state is directly owned, but the selected sources implement MDCACHE global parameters, LRU/hash partitions, export maps, dirent chunks, upcalls, and object operations.

## Dependencies and Integration Points

It depends on global build options `USE_DBUS` and `USE_LTTNG`, DBus include variables, generated trace property files, and the wider FSAL build that links this object library into NFS-Ganesha.

## Risks and Edge Cases

Object-library source-list drift can omit a cache component while still compiling other FSAL code. LTTng generation ordering must be correct or trace headers will be missing. `LIB_PREFIX` is set but not used locally.

## Test Signals

Configure and build with DBus/LTTng toggled, verify all listed MDCACHE sources compile as PIC, and run link tests that consume the object library from the final daemon/module target.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_avl.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_avl.c

## Purpose

This file implements AVL indexes for MDCACHE directory entries. It supports lookup by name, lookup by FSAL cookie for chunked readdir, sorted-order indexing, deletion marking, chunk detachment, duplicate handling, and cleanup of a directory's cached dirents. The source was read as a complete 609-line file.

## Important APIs, Types, and Functions

Public functions are `mdcache_avl_init`, `avl_dirent_set_deleted`, `unchunk_dirent`, `mdcache_avl_remove`, `mdcache_avl_insert_ck`, `mdcache_avl_insert`, `mdcache_avl_lookup_ck`, `mdcache_avl_lookup`, and `mdcache_avl_clean_trees`. It uses `mdcache_entry_t`, `mdcache_dir_entry_t`, `struct dir_chunk`, AVL nodes `node_name`, `node_ck`, `node_sorted`, CityHash or Murmur3 name hashes, and MDCACHE LRU chunk/entry references.

## Control Flow

Initialization creates three AVL trees per directory. Insert computes a name hash, inserts into the name tree, optionally inserts into the cookie tree for chunked dirents, and handles duplicate names by comparing cache keys, replacing stale entries, or returning duplicate/cookie-collision errors. Delete marking removes active names, marks dirents deleted, deletes their key, and adjusts `first_ck` across chunks. Removal frees entry refs, unchunks when needed, removes detached dirents, deletes keys, and frees memory.

## State and Persistence Behavior

All state is in memory under the parent directory's `fsobj.fsdir.avl` trees and chunk lists. Cookie and name indexes persist only while the cache entry/chunk remains alive. Dirent deletion may keep chunked entries in the cookie tree so readdir can restart at old positions and skip deleted entries.

## Dependencies and Integration Points

This file integrates with `mdcache_int.h`, `mdcache_lru.h`, `mdcache_avl.h`, hash libraries, dirent chunk logic, and readdir helpers. Callers are expected to hold the parent `content_lock` for write on mutation.

## Risks and Edge Cases

Duplicate file names with different cookies and FSAL cookie collisions make READDIR unreliable and return negative codes. Chunk lifetime is subtle because `mdcache_avl_lookup_ck` returns a dirent while taking a chunk ref. Deleted chunk entries remaining in cookie lookup require all enumeration paths to skip deletion flags.

## Test Signals

Test insert/lookup/remove by name, chunked cookie lookup and unref, duplicate names with same/different keys, duplicate cookies, deletion of first chunk entry updating `first_ck`, full tree cleanup, and debug builds that assert `content_lock` ownership.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_avl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_avl.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_avl.h

## Purpose

This header defines comparison functions and prototypes for MDCACHE directory-entry AVL indexes. It documents the hash-plus-string ordering model for name lookups and exposes cookie and sorted comparison functions. The source was read as a complete 132-line file.

## Important APIs, Types, and Functions

Inline comparators are `avl_dirent_name_cmpf`, `avl_dirent_ck_cmpf`, and `avl_dirent_sorted_cmpf`. Public prototypes cover the functions implemented in `mdcache_avl.c`: init, insert, cookie insert/lookup, name lookup, deletion, removal, cleanup, and `unchunk_dirent`.

## Control Flow

The name comparator orders first by precomputed `namehash`, then by `strcmp`. The cookie comparator orders by `ck`. The sorted comparator delegates to the sub-FSAL's `dirent_cmp` through the parent sub-handle; it handles the create-time case where one side has not yet been placed into a chunk.

## State and Persistence Behavior

No storage is owned by the header. It defines how existing `mdcache_dir_entry_t` AVL node fields are interpreted while cached directories are alive.

## Dependencies and Integration Points

It includes `mdcache_int.h` and `avltree.h` and is used by readdir, dirent cache, and AVL implementation code. The sorted comparator integrates directly with lower FSAL directory ordering semantics.

## Risks and Edge Cases

Comparator correctness is critical: inconsistent ordering corrupts AVL trees. `avl_dirent_sorted_cmpf` assumes access to a valid parent through at least one chunk and relies on sub-FSAL `dirent_cmp` behavior.

## Test Signals

Unit-style comparator tests for equal hashes with different names, cookie ordering, sorted ordering via a test sub-FSAL, and compile coverage for all callers using the exported prototypes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_avl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_debug.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_debug.h

## Purpose

This header exposes a debug-only helper for white-box tests or diagnostics that need the sub-FSAL object handle under an MDCACHE object. It explicitly warns against production use. The source was read as a complete 59-line file.

## Important APIs, Types, and Functions

It defines `mdcdb_get_sub_handle(struct fsal_obj_handle *obj_hdl)`, which uses `container_of` to convert the MDCACHE object handle to `mdcache_entry_t` and returns `entry->sub_handle`.

## Control Flow

The helper performs a direct field lookup with no locking, no ref acquisition, and no validation.

## State and Persistence Behavior

No state is created. It exposes an existing sub-FSAL handle pointer whose lifetime is tied to the MDCACHE entry.

## Dependencies and Integration Points

It includes `mdcache_int.h` and `mdcache_lru.h`. Integration is intended for debug and white-box testing code that already holds a reference on the MDCACHE object.

## Risks and Edge Cases

The returned sub-handle can be freed if the caller does not hold an MDCACHE ref for the full use duration. Using this helper in production paths bypasses MDCACHE coherency, accounting, and lock expectations.

## Test Signals

White-box tests can assert that a wrapped object maps to the expected lower FSAL handle while holding a ref. Static analysis should ensure production code does not depend on this header.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_export.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_export.c

## Purpose

This file implements MDCACHE export operations. Most filesystem capability and quota/pNFS queries pass through to the sub-FSAL, while unexport/unmount/release perform MDCACHE-specific export-map cleanup and LRU drain synchronization. The source was read as a complete 1051-line file.

## Important APIs, Types, and Functions

Important functions include `mdcache_get_name`, `mdcache_unexport`, `mdcache_unmount`, `mdcache_drain_export_cleanup`, `mdcache_exp_release`, `mdcache_get_dynamic_info`, many `mdcache_fs_*` wrappers, quota wrappers, pNFS device/layout wrappers, `mdcache_wire_to_host`, `mdcache_host_to_key`, `mdcache_alloc_state`, `mdcache_is_superuser`, `mdcache_prepare_unexport`, and `mdcache_export_ops_init`.

## Control Flow

Unexport marks the export with `MDC_UNEXPORT`, walks `entry_list`, takes active refs, removes `entry_export_map` links under the documented `attr_lock` then `mdc_exp_lock` order, closes stale global FDs, clears `first_export_id`, and schedules export-less entries for LRU cleanup. Unmount performs the same map removal for junction entries. Release waits until `cleanup_pending` drains, stops dirmap LRU, releases the sub-export, detaches export ops, destroys locks, and frees memory. Other operations call the corresponding sub-export op through `subcall_raw`.

## State and Persistence Behavior

State includes export flags, export-entry maps, cleanup counters, dirmap state, name strings, mutexes, and sub-export references. Persistence is not on disk; cleanup protects against dangling in-memory FDs/export pointers after export teardown.

## Dependencies and Integration Points

The file depends on FSAL export ops, export manager state, MDCACHE LRU/hash helpers, config parsing, quota/mount helpers, and the lower FSAL export vector. `mdcache_export_ops_init` is the integration point that publishes the wrapper export vector.

## Risks and Edge Cases

Lock ordering is critical. Cleanup intentionally cannot hold `attr_lock` across LRU cleanup queue push. Multi-export entries must update `first_export_id` and close global FDs without evicting sibling exports. `mdcache_drain_export_cleanup` can wait indefinitely if cleanup counters are leaked.

## Test Signals

Test single and nested export unexport, junction unmount, active NFSv3 FD cleanup, entries shared by multiple exports, sub-FSAL pass-through capability queries, pNFS/quota wrappers, and release waiting for LRU cleanup completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_ext.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_ext.h

## Purpose

This header exposes MDCACHE configuration and a small external helper for code outside the private MDCACHE implementation. It primarily defines `struct mdcache_parameter`, the global cache tuning structure. The source was read as a complete 178-line file.

## Important APIs, Types, and Functions

Important symbols are `MDCACHE_AVL_CHUNK_DEFAULT`, `struct mdcache_parameter`, `extern struct mdcache_parameter mdcache_param`, and `get_readdir_mode`. Parameters cover partition counts, cache sizes, directory invalidation, AVL chunking, entry/chunk high-water marks, LRU intervals, FD caching/reaper thresholds, dirmap limits, delegation scaling, and cached-owner override behavior.

## Control Flow

`get_readdir_mode` asks the active export for `fs_readdir_mode`. If the sub-FSAL returns `FSAL_RDDIR_CHUNK_USE_CONFIG`, it converts configuration and export options into either `FSAL_RDDIR_CHUNK_NEVER` or `FSAL_RDDIR_CHUNK_ALWAYS`.

## State and Persistence Behavior

`mdcache_param` is process-global configuration loaded elsewhere. It governs in-memory cache sizing, reaper behavior, FD caching, and directory chunking. It does not itself persist state.

## Dependencies and Integration Points

It includes `nfs_exports.h` and uses `op_ctx`, export ops, and export options. Many MDCACHE files consult these parameters to decide readdir, LRU, and FD behavior.

## Risks and Edge Cases

The header labels these external hooks as hacks to remove, so callers should not expand the public surface casually. `get_readdir_mode` depends on `op_ctx` and a valid active export. Misconfigured chunk sizes or FD thresholds can cause memory pressure or poor performance.

## Test Signals

Config parsing tests for every field, readdir mode tests for sub-FSAL return values plus `EXPORT_OPTION_NO_DIR_CACHING`, and stress tests around LRU/FD high-water behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_ext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_file.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_file.c

## Purpose

This file implements MDCACHE file I/O object operations. It delegates actual data I/O and locking to the sub-FSAL while keeping MDCACHE metadata validity, async callback context, and created/opened handle wrapping coherent. The source was read as a complete 868-line file.

## Important APIs, Types, and Functions

Important types/functions include `struct mdc_async_arg`, `mdc_set_time_current`, `mdcache_io_advise`, `mdcache_close`, `mdc_open2_by_name`, `mdcache_open2`, `mdcache_check_verifier`, `mdcache_status2`, `mdcache_reopen2`, read/write callback wrappers, `mdcache_read2`, `mdcache_write2`, `mdcache_seek2`, `mdcache_io_advise2`, `mdcache_commit2`, `mdcache_lock_op2`, `mdcache_lease_op2`, `mdcache_close2`, and `mdcache_fallocate`.

## Control Flow

`mdcache_open2` first tries a cached lookup by name and, when possible, opens the existing sub-handle. If not found, it calls parent sub-FSAL `open2`, requests attributes, then wraps the returned sub-handle through `mdcache_alloc_and_check_handle` under the parent content lock. Reads/writes allocate callback wrapper state, call the sub-FSAL async method, then re-enter MDCACHE context through `supercall`. Write-like operations clear `MDCACHE_TRUST_ATTRS` or increment `attr_generation`.

## State and Persistence Behavior

MDCACHE stores no file data. It caches attributes, atime updates after reads, and invalidation flags after write/truncate/commit/fallocate/layout changes. Open/create can create new in-memory MDCACHE entries and dirents.

## Dependencies and Integration Points

The file depends on `mdcache_int.h`, `mdcache_lru.h`, sub-FSAL object ops, FSAL access/state contracts, and handle allocation in `mdcache_handle.c`. Async callbacks integrate lower FSAL completion with upper-layer callback expectations.

## Risks and Edge Cases

Ref handling in async callbacks is subtle: callbacks may drop initial refs, so wrappers take active refs around user callbacks. Stale sub-FSAL results must kill entries. Open-by-name must handle verifier semantics, non-regular targets, and `FSAL_O_TRUNC` invalidation. `Close_Fast` and FD caching behavior is configured elsewhere but affects these paths.

## Test Signals

Test open existing/missing/create guarded/exclusive/unchecked cases, verifier matching, truncation invalidation, async read/write callback ordering and ref safety, stale errors on I/O, commit/fallocate invalidation, close of unreachable last-state entries, and lock/lease pass-through.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_handle.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_handle.c

## Purpose

This file implements MDCACHE object-handle operations for namespace, attributes, references, wire/key conversion, pNFS layouts, and export-level handle creation. It is the main bridge between upper FSAL object ops and lower sub-FSAL handles. The source was read as a complete 1711-line file.

## Important APIs, Types, and Functions

Key functions include `mdcache_alloc_and_check_handle`, `mdcache_lookup`, `mdcache_mkdir`, `mdcache_mknode`, `mdcache_symlink`, `mdcache_readlink`, `mdcache_link`, `mdcache_readdir`, `mdcache_test_access`, `mdcache_rename`, `mdcache_refresh_attrs`, `mdcache_getattrs`, `mdcache_setattr2`, `mdcache_unlink`, handle digest/key/cmp wrappers, pNFS layout wrappers, ref/release methods, `mdcache_merge`, `mdcache_is_referral`, `mdcache_handle_ops_init`, `mdcache_lookup_path`, and `mdcache_create_handle`.

## Control Flow

Create operations call the sub-FSAL, request non-ACL attributes, then under parent content lock allocate/check an MDCACHE entry and optionally add a chunked dirent. Lookup delegates to `mdc_lookup`. Readdir either passes through uncached or uses chunked MDCACHE readdir based on `get_readdir_mode`. Rename checks destination cache/delegations, locks source and destination in stable order, performs sub-FSAL rename, invalidates affected attrs/dirents, handles FSALs whose rename changes keys, and marks overwritten entries unreachable. Getattr uses cache validity under `attr_lock`, refreshes from the sub-FSAL on misses, and may invalidate directory dirents when mtime changes.

## State and Persistence Behavior

The file manages in-memory MDCACHE entries, attr caches, content trust, parent pointers, dirents, export references, LRU refs, and unreachable/stale markers. Backing filesystem persistence is always performed by the sub-FSAL.

## Dependencies and Integration Points

It depends on MDCACHE LRU/hash/AVL helpers, FSAL default ops, NFS ACL/export/state helpers, dynamic metrics, sub-FSAL object and export ops, and xattr wrappers registered in `mdcache_handle_ops_init`.

## Risks and Edge Cases

Lock ordering is central: parent content locks, source/destination directory locks, and attr locks must not conflict with LRU cleanup. Attribute cache generation can change during refresh and must clear trust. Rename over junctions is blocked; rename-changing-key FSALs require invalidation and unreachable marking. Owner-skip access can use cached owner by configuration, trading correctness risk for speed.

## Test Signals

Exercise lookup/create/link/rename/unlink with chunked and uncached readdir modes, stale sub-FSAL responses, directory parent changes, delegation conflicts, attr cache hit/miss metrics, ACL/FS_LOCATIONS/security-label refresh, referral cache updates, pNFS layout pass-through, ref/put/release behavior, and create-handle lookup from host handles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_hash.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_hash.c

## Purpose

This file owns initialization and destruction of MDCACHE's file-handle lookup table. The table maps hashed lower-FSAL handle keys to `mdcache_entry_t` objects using partitioned AVL trees plus a direct cache slot array. The source was read as a complete 114-line file.

## Important APIs, Types, and Functions

Important symbols are global `struct cih_lookup_table cih_fhcache`, static `initialized`, `cih_pkginit`, and `cih_pkgdestroy`.

## Control Flow

Initialization reads `mdcache_param.nparts` and `mdcache_param.cache_size`, allocates the partition array, initializes each partition mutex and AVL tree with `cih_fh_cmpf`, and allocates the per-partition cache slot array. Destroy iterates partitions, logs if any AVL tree is not empty, destroys mutexes, frees cache arrays and the partition table, and clears the initialized flag.

## State and Persistence Behavior

All state is process memory. Partitions contain locks, AVL trees, and cache slots. No file-backed persistence exists; cache contents must be empty or intentionally torn down before package destruction.

## Dependencies and Integration Points

It depends on `mdcache_param`, `mdcache_hash.h`, `mdcache_int.h`, AVL support, and Ganesha allocation/logging. Inline lookup/insert/remove functions in `mdcache_hash.h` operate on the global table initialized here.

## Risks and Edge Cases

Destroy only logs non-empty trees, so callers must ensure cache cleanup happens before package shutdown. A zero or poor `nparts`/`cache_size` configuration would break partition/cache modulo assumptions. Partition lock destruction while entries remain can race if shutdown order is wrong.

## Test Signals

Initialize/destroy with representative partition/cache sizes, check mutex and allocation cleanup under leak tools, verify warnings for non-empty trees in controlled tests, and run concurrent locate/insert/remove stress after init.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_hash.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_hash.h

## Purpose

This header defines MDCACHE's hashed file-handle index. It provides partition types, key hashing, latch locking, fast lookup through cache slots, AVL comparison, insertion, and removal helpers for `mdcache_entry_t`. The source was read as a complete 461-line file.

## Important APIs, Types, and Functions

Core types are `cih_partition_t`, `struct cih_lookup_table`, and `cih_latch_t`. Important APIs/macros include `cih_partition_of_scalar`, `cih_cache_offsetof`, `cih_fh_cmpf`, `cih_fhcache_inline_lookup`, `cih_hash_key`, `cih_hash_release`, `cih_latch_entry`, `cih_get_by_key_latch`, `cih_set_latched`, `cih_remove_checked`, and `cih_remove_latched`. Flags include `CIH_HASH_KEY_PROTOTYPE`, `CIH_GET_UNLOCK_ON_MISS`, `CIH_SET_HASHED`, `CIH_SET_UNLOCK`, and `CIH_REMOVE_UNLOCK`.

## Control Flow

Callers hash a key using CityHash, select a partition by hash modulo partition count, and latch that partition mutex. Lookup first probes the cache slot indexed by hash modulo cache size, validates with `mdcache_key_cmp`, then falls back to the AVL tree and updates the slot on hit. Insert places the entry into the latched partition AVL and sets `inavl`. Removal clears AVL membership and the cache slot, then drops the sentinel LRU ref outside or as part of the locked path depending on helper used.

## State and Persistence Behavior

The header manipulates in-memory hash keys, AVL nodes, `inavl` flags, partition cache slots, and LRU sentinel refs. It intentionally refuses to return entries whose LRU refcount is already zero.

## Dependencies and Integration Points

It integrates with `mdcache_int.h`, `mdcache_lru.h`, `abstract_atomic`, CityHash, AVL trees, lock tracing, and optional LTTng tracepoints. `mdcache_hash.c` provides the global table storage and lifecycle.

## Risks and Edge Cases

Partition locks must not be held while dropping the last LRU ref in paths that can recurse into hash removal. Cache slots are optimistic and must always be validated. Key prototype usage borrows caller buffer storage, so lifetime must cover lookup. Incorrect hash/key duplication leaks or corrupts cache lookup.

## Test Signals

Concurrent lookup/insert/remove stress, cache-slot hit/miss correctness, duplicate key comparison, zero-ref entry rejection, locktrace builds, LTTng trace compile coverage, and sentinel-ref release behavior under final unref.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_hash.h -->
