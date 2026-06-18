# subset-b-009943 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/python/pyxattr_native.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/python/pyxattr_native.c

Purpose: `pyxattr_native.c` exposes a small Python extension module, `samba.xattr_native`, for direct filesystem extended attribute access. It is used by Samba Python tooling that needs to probe or manipulate native xattrs without going through the POSIX EADB emulation layer.

Important APIs, types, and functions: The module exports `wrap_getxattr(filename, attribute)`, `wrap_setxattr(filename, attribute, value)`, and `is_xattr_supported()`. Internally it uses Python argument parsing, `DATA_BLOB`, `getxattr`, `setxattr`, talloc temporary allocation, and the Samba Python module init macro.

Control flow: `is_xattr_supported` is a compile-time feature check around `HAVE_XATTR_SUPPORT`. `wrap_setxattr` parses two strings and a Python bytes buffer, then calls `setxattr` with flags 0. `wrap_getxattr` first calls `getxattr` with a NULL buffer to discover length, allocates a talloc buffer, calls `getxattr` again, and returns bytes.

State and persistence behavior: The module does not keep process state. Persistence is delegated to the host filesystem xattr implementation. Temporary buffers are freed before returning.

Dependencies and integration points: It depends on Python C API compatibility wrappers, Samba `DATA_BLOB`, talloc, `system/filesys.h`, and platform xattr functions. It is built as `samba/xattr_native.so` from the POSIX NTVFS build file.

Risks: The two-step get path has a normal race if the xattr changes between length discovery and read. It maps `ENOTSUP` to `IOError` and other failures to `OSError` with filename, so callers must handle platform-specific xattr errors. Zero-length xattrs allocate a zero-length talloc array and should be considered by tests.

Test signals: Useful tests import `samba.xattr_native`, check `is_xattr_supported`, set and get binary values, and validate expected exceptions on unsupported filesystems, missing files, and missing attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/python/pyxattr_native.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/python/pyxattr_tdb.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/python/pyxattr_tdb.c

Purpose: `pyxattr_tdb.c` implements the `samba.xattr_tdb` Python extension, providing xattr-like access backed by Samba's TDB/dbwrap storage instead of native filesystem xattrs. It supports filesystems without suitable xattr support and aligns with source3 `xattr_tdb`.

Important APIs, types, and functions: The exported Python methods are `wrap_setxattr(tdbname, filename, attribute, value)`, `wrap_getxattr(tdbname, filename, attribute)`, and `is_xattr_supported()`. The implementation uses `py_default_loadparm_context`, `db_open_tdb`, `xattr_tdb_setattr`, `xattr_tdb_getattr`, `struct file_id`, and `stat`.

Control flow: Each get or set opens the named TDB with Samba loadparm-derived TDB flags, stats the target file, builds a `file_id` from device and inode, and stores or retrieves the attribute value from the database. Errors are converted into Python exceptions before the temporary talloc context is freed.

State and persistence behavior: Attribute data persists in the external TDB keyed by the file's device and inode. No module-level handle is cached; every call opens the database anew. File renames preserve lookup identity through inode/device, while replacement creates a new identity.

Dependencies and integration points: It depends on Samba dbwrap, tdb, `xattr_tdb`, Python/talloc bridge code, and the `pyparam_util` loadparm helper. The POSIX build file installs it as `samba/xattr_tdb.so`.

Risks: Per-call database open cost and lock ordering matter for callers doing many xattr operations. Device/inode identity can become stale if files are deleted and inodes reused. Several failures are reported as generic `IOError` or `TypeError`, which can obscure storage corruption versus missing attributes.

Test signals: Tests should cover binary round trips, missing files, missing attributes, persistence across process/module reloads, replacement of a file at the same path, and interaction with Samba TDB lock flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/python/pyxattr_tdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/vfs_posix.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/vfs_posix.c

Purpose: `vfs_posix.c` is the entry point and tree-connect setup for Samba4's POSIX NTVFS disk backend. It registers the backend as both `default` and `posix`, constructs per-share `pvfs_state`, initializes locking/notify/search helpers, and wires the NTVFS operation table to the POSIX implementation files.

Important APIs, types, and functions: Key functions are `pvfs_setup_options`, `pvfs_state_destructor`, `pvfs_connect`, `pvfs_disconnect`, `pvfs_chkpath`, `pvfs_copy`, `pvfs_lpq`, `pvfs_trans`, and `ntvfs_posix_init`. The operation table references many integration functions such as `pvfs_open`, `pvfs_read`, `pvfs_write`, `pvfs_lock`, `pvfs_notify`, and `pvfs_async_setup`.

Control flow: On connect, the module normalizes the share name, initializes ACL backends, allocates `pvfs_state`, trims the share path, verifies it is an existing directory, sets reported filesystem/device strings, creates byte-range locking and open database contexts, initializes change notify and search id tracking, initializes name mangling, reads share options, installs a destructor, and blocks `SIGXFSZ` when available. Registration fills `struct ntvfs_ops` and calls `ntvfs_register`.

State and persistence behavior: Per-tree state includes base directory, flags, share name, TDB-backed EADB handle, open file list, open search id tree, oplock/write-delay settings, locking contexts, notify context, SID cache, and ACL backend. Durable state lives in underlying files, optional external EADB, open database, brlock database, and xattrs.

Dependencies and integration points: It depends on `share_config` options, loadparm TDB flags, tdb-wrap, idtree, ntvfs common code, brlock, opendb, notify, ACL modules, and the rest of the `pvfs_*` implementation files.

Risks: Share options directly change security and compatibility behavior, especially xattrs, permission override, case sensitivity, ACL backend selection, fake oplocks, and read-only handling. A failed EADB open disables xattr support. The backend reports NTFS-like capabilities over POSIX filesystems, so metadata emulation must stay consistent across files.

Test signals: Integration tests should tree-connect to POSIX-backed shares under varied share options, verify xattr/EADB fallback, read-only rejection, path checking, locking/notify behavior, ACL backend selection, and registration under both `default` and `posix`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/vfs_posix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/vfs_posix.h -->
# sources/user-network-fs/samba/source4/ntvfs/posix/vfs_posix.h

Purpose: `vfs_posix.h` defines the shared private data model for the POSIX NTVFS backend. It is the contract consumed by the many `pvfs_*` files that implement path resolution, open/close, locking, xattrs, ACLs, notify, searches, and metadata mapping.

Important APIs, types, and functions: Major structs include `pvfs_state`, `pvfs_dos_fileinfo`, `pvfs_filename`, `pvfs_file_handle`, `pvfs_file`, `pvfs_search_state`, `pvfs_odb_retry`, and `pvfs_acl_ops`. It defines `PVFS_RESOLVE_*`, `PVFS_FLAG_*`, share option names such as `PVFS_EADB` and `PVFS_XATTR`, and default timing/allocation constants.

Control flow: The header has no execution flow, but it shapes backend flow by separating per-tree state, per-open-handle state, per-client-file state, and search state. `pvfs_file_handle` deliberately differs from `pvfs_file` to support DOS deny semantics where multiple logical opens can share one low-level fd.

State and persistence behavior: `pvfs_state` owns connection-wide open file/search lists, locking contexts, notify context, mangle context, optional EADB handle, flags, timing options, and ACL state. `pvfs_file_handle` tracks fd, opendb locking key, oplock, seek offsets, write-time delay state, and create options. Persistent effects are in files, xattrs/EADB, and Samba lock/open databases.

Dependencies and integration points: It includes generated `vfs_posix_proto.h` and `vfs_acl_proto.h`, NDR xattr definitions, NTVFS common types, wbclient, tevent, and system filesys declarations. The ACL ops table is the extension point for xattr and NFSv4 ACL modules.

Risks: This header is central ABI glue inside the backend; layout changes can ripple widely. The flags combine compatibility and security-sensitive behavior, and ambiguous fields such as `mode` or probabilistic `stream_id` need careful handling by callers.

Test signals: Build coverage should catch prototype and struct use regressions. Functional tests should indirectly exercise each state family: open handle sharing, write-time delayed updates, search cleanup, xattr/ACL toggles, stream handling, and permission override paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/vfs_posix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/wscript_build -->
# sources/user-network-fs/samba/source4/ntvfs/posix/wscript_build

Purpose: This Waf build script declares the POSIX NTVFS backend, POSIX ACL modules, EADB helper library, and Python xattr/EADB extension modules.

Important APIs, types, and functions: It uses `bld.SAMBA_SUBSYSTEM`, `bld.SAMBA_MODULE`, `bld.SAMBA_LIBRARY`, `bld.SAMBA_PYTHON`, `bld.CONFIG_SET`, and `bld.pyembed_libname`. Targets include `pvfs_acl`, `pvfs_acl_xattr`, `pvfs_acl_nfs4`, `ntvfs_posix`, `posix_eadb`, `python_xattr_native`, `python_posix_eadb`, and `python_xattr_tdb`.

Control flow: When `WITH_NTVFS_FILESERVER` is enabled, it builds ACL backends and the internal `ntvfs_posix` module from the large set of `pvfs_*` sources plus `xattr_system.c`. Independently, it builds `posix_eadb` and the Python modules, wiring their runtime names under `samba/*.so`.

State and persistence behavior: The script itself has no runtime state. It determines whether POSIX backend code is present, whether generated prototypes are produced, and which private libraries/modules are linked into the installed Samba build.

Dependencies and integration points: Build dependencies include `NDR_XATTR`, `NDR_NFS4ACL`, `samdb`, `events`, `MESSAGING`, `LIBWBCLIENT_OLD`, `ntvfs_common`, `posix_eadb`, `tdb`, `tdb-wrap`, `attr`, Python embedding helpers, and `xattr_tdb`.

Risks: Feature gating means code can compile in one configuration but disappear in another. Missing `attr` or Python embed dependencies break the xattr modules. The long `ntvfs_posix` source list is easy to desynchronize from generated prototypes.

Test signals: Configure/build matrix tests should include `WITH_NTVFS_FILESERVER` on and off, Python enabled and disabled, native attr availability, and module load checks for `ntvfs_posix` and the three Python extension realnames.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/xattr_system.c -->
# sources/user-network-fs/samba/source4/ntvfs/posix/xattr_system.c

Purpose: `xattr_system.c` is the POSIX backend adapter for storing and retrieving Samba metadata in native filesystem extended attributes.

Important APIs, types, and functions: It exports `pull_xattr_blob_system`, `push_xattr_blob_system`, `delete_xattr_system`, and `unlink_xattr_system`. These operate on either a pathname or fd and translate Unix errors through `pvfs_map_errno`.

Control flow: Pull allocates an estimated-size blob, reads with `fgetxattr` or `getxattr`, doubles the allocation on `ERANGE`, and returns a sized `DATA_BLOB`. A special `EPERM` path stats the target and treats sticky directories as not found, matching expected semantics for inaccessible directory xattrs. Push and delete call the fd or path xattr variants and map errors.

State and persistence behavior: Metadata persists in filesystem xattrs. The code holds no global state. `unlink_xattr_system` is a no-op because native xattrs are removed with the file by the filesystem.

Dependencies and integration points: It depends on `pvfs_state`, Samba `DATA_BLOB`, talloc allocation, system xattr APIs, and POSIX stat mode checks. Higher-level `pvfs_xattr` code selects this backend when native xattrs are enabled.

Risks: Estimated-size growth must avoid repeated realloc failures and races with concurrent xattr changes. Filesystem-specific xattr namespaces and permission behavior affect SMB metadata correctness. The sticky-directory EPERM exception is subtle and should not mask real permission bugs outside that case.

Test signals: Tests should force small initial estimates, read changed-size xattrs, use fd and path variants, delete missing attributes, run on sticky directories, and verify error translation for unsupported xattr filesystems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/posix/xattr_system.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/simple/svfs.h -->
# sources/user-network-fs/samba/source4/ntvfs/simple/svfs.h

Purpose: `svfs.h` defines private structs for the simple NTVFS backend, a deliberately minimal disk backend used for basic file serving and tests.

Important APIs, types, and functions: It defines `svfs_private`, `svfs_dir`, nested `svfs_dirfile`, `svfs_file`, and `search_state`. These track connection path, open files, directory listings, and search handles.

Control flow: The header has no executable flow. `vfs_simple.c` allocates `svfs_private` on tree connect, adds/removes `svfs_file` nodes as files open and close, and creates `search_state` entries for TRANS2 directory searches.

State and persistence behavior: Runtime state is per-tree-connect and in memory: base path, next search handle, open file list, and open search list. Persistent state is only the underlying filesystem files accessed by fd/path.

Dependencies and integration points: It is consumed by `vfs_simple.c` and `svfs_util.c` and relies on NTVFS handles, `struct stat`, and Samba dlinklist conventions.

Risks: The structures are intentionally sparse and lack locking, share mode, ACL, xattr, oplock, and full metadata state. Search handles are simple 16-bit counters and can wrap on long-lived sessions.

Test signals: Simple backend tests should cover open/close list maintenance, search state lifecycle, directory listing allocation, and behavior when unsupported SMB features are requested.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/simple/svfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/simple/svfs_util.c -->
# sources/user-network-fs/samba/source4/ntvfs/simple/svfs_util.c

Purpose: `svfs_util.c` provides utility functions for the simple NTVFS backend: path conversion, directory wildcard listing, fd-based utime support, and Unix-to-DOS attribute mapping.

Important APIs, types, and functions: Functions are `svfs_unix_path`, `svfs_list_unix`, `svfs_list`, `svfs_file_utime`, and `svfs_unix_to_dos_attrib`.

Control flow: `svfs_unix_path` lowercases the incoming SMB path, prepends the share connect path, and converts backslashes to slashes. `svfs_list_unix` splits the requested pattern into directory and mask, opens the directory, lowercases names, filters with `ms_fnmatch_protocol`, skips stream-like names unless requested, stats matches, and grows a talloc array. `svfs_file_utime` updates times through a `/proc/self/<fd>` path.

State and persistence behavior: Directory listings are snapshots allocated under the caller's talloc context. `svfs_file_utime` persists access/write timestamps. Other functions only map or inspect filesystem state.

Dependencies and integration points: It depends on Samba wildcard matching, `system/dir.h`, `system/time.h`, POSIX `opendir/readdir/stat/utime`, and the simple backend structs. `vfs_simple.c` uses it for query info and searches.

Risks: Lowercasing every path is not a correct general SMB case policy. `/proc/self/<fd>` is nonportable and likely wrong on platforms without procfs or with different fd path syntax. Directory listing allocation growth uses integer math and should be watched for large directories.

Test signals: Tests should validate wildcard matching, stream name filtering, mixed slash input, case behavior, large directories, missing directories, and timestamp setting through open fds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/simple/svfs_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/simple/vfs_simple.c -->
# sources/user-network-fs/samba/source4/ntvfs/simple/vfs_simple.c

Purpose: `vfs_simple.c` implements Samba4's `simple` NTVFS disk backend. It is a minimal file server backend that maps a small subset of SMB operations directly to POSIX file calls and intentionally omits much of the correct CIFS/NTFS compatibility behavior.

Important APIs, types, and functions: Key functions include `svfs_connect`, `find_fd`, `svfs_unlink`, `svfs_chkpath`, `svfs_map_fileinfo`, `svfs_qpathinfo`, `svfs_qfileinfo`, `svfs_open`, `svfs_mkdir`, `svfs_rmdir`, `svfs_rename`, `svfs_read`, `svfs_write`, `svfs_flush`, `svfs_close`, `svfs_setfileinfo`, `svfs_fsinfo`, search first/next/close handlers, and `ntvfs_simple_init`.

Control flow: Tree connect verifies the configured share path and records it in `svfs_private`. Open maps generic create dispositions to `open` flags, optionally creates directories, creates an NTVFS handle, and links an `svfs_file`. Query operations stat paths/fds and fill generic fileinfo. Search first snapshots a directory into `svfs_dir`, emits entries through the callback, and either stores or frees search state depending on client flags. Close fsync/close paths operate directly on tracked fds.

State and persistence behavior: Runtime state is an open-file linked list and search linked list under the connection. Persistent effects are direct filesystem changes: create, mkdir, unlink, rename, write, truncate, fsync, and timestamp updates. It does not persist Samba-specific xattrs, locks, ACLs, or oplocks.

Dependencies and integration points: It integrates with the NTVFS operation table, generic NTVFS mapping helpers for unsupported levels, Samba share options, statvfs helpers, POSIX file APIs, and `svfs_util.c`.

Risks: It ignores wildcards for unlink/rename, does not implement byte-range locks, returns placeholder errors such as `NT_STATUS_FOOBAR`, has weak metadata mapping, and defaults read-only checks through share options. It should not be treated as a production NTFS-compatible backend.

Test signals: Tests should exercise supported generic open/read/write/query/search/fsinfo flows and verify unsupported operations return stable errors. Regression coverage should include read-only shares, directory opens, search resume flags, flush-all behavior, truncate/time set, and handle invalidation after close.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/simple/vfs_simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/sysdep/inotify.c -->
# sources/user-network-fs/samba/source4/ntvfs/sysdep/inotify.c

Purpose: `inotify.c` implements the Linux inotify backend for Samba's abstract system change notify layer. It maps SMB change-notify filters onto inotify watches and callbacks.

Important APIs, types, and functions: It defines `inotify_private`, `inotify_watch_context`, `filter_match`, `inotify_dispatch`, `inotify_handler`, `inotify_setup`, `inotify_map`, `watch_destructor`, `inotify_watch`, and `sys_notify_inotify_init`.

Control flow: The first watch lazily initializes an inotify fd and registers it with tevent. `inotify_watch` maps and removes handled bits from the caller's `notify_entry`, adds an `IN_ONLYDIR|IN_MASK_ADD` watch, stores callback state, and returns a talloc handle. When the fd is readable, `inotify_handler` reads all queued events, walks variable-length records, and dispatches actions. Rename cookies are used to emit old/new names, and file renames generate an extra modified event to match SMB expectations.

State and persistence behavior: Runtime state is the inotify fd plus a linked list of watch contexts. Watch removal is controlled by freeing the returned talloc handle; the destructor removes the kernel watch only when no other context uses the same watch descriptor. No durable state is stored.

Dependencies and integration points: It depends on Linux `<sys/inotify.h>`, tevent fd handling, Samba notify NDR types, `sys_notify_register`, and SMB file notify filter constants.

Risks: Inotify coalesces watches, so filtering must be correct per watcher. Not all SMB filters are representable; remaining filter bits are left for generic handling. Event buffer parsing is sensitive to record lengths, and rename pairing is best-effort using adjacent events/cookies.

Test signals: Tests should cover multiple watches on one path, free-handle cleanup, create/delete/rename/attribute events, directory versus file filters, unhandled filter bits, and configure-time gating by `HAVE_LINUX_INOTIFY`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/sysdep/inotify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_lease.c -->
# sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_lease.c

Purpose: `sys_lease.c` provides a generic registry and dispatch layer for kernel lease/oplock backends used by NTVFS.

Important APIs, types, and functions: Public functions are `sys_lease_context_create`, `sys_lease_register`, `sys_lease_init`, `sys_lease_setup`, `sys_lease_update`, and `sys_lease_remove`. It stores registered `struct sys_lease_ops` backends in a global array.

Control flow: Initialization runs statically linked lease backend init functions once. Context creation reads the share option `lease:backend`, matches it case-insensitively against registered backends, stores event/messaging contexts and the break-send callback, and calls the backend `init`. Setup/update/remove simply dispatch through `ctx->ops`.

State and persistence behavior: The registry is process-global and grows as modules register. A lease context is per caller/share and holds only pointers and backend private data. Durable lease semantics are backend/kernel state, not file storage.

Dependencies and integration points: It depends on Samba module initialization, `share_config` option lookup, tevent, messaging, and opendb entries. `sys_lease_linux.c` is the Linux backend when available.

Risks: No backend is selected unless `lease:backend` is explicitly configured; context creation returns NULL otherwise. Dispatch functions assume a valid context and ops table. Duplicate backend registration is not guarded here.

Test signals: Tests should verify module init idempotence, backend selection, missing backend behavior, propagation of backend init failure, and that setup/update/remove calls reach the selected backend.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_lease.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_lease.h -->
# sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_lease.h

Purpose: `sys_lease.h` declares Samba's abstract interface for kernel lease/oplock support.

Important APIs, types, and functions: It declares `sys_lease_send_break_fn`, `struct sys_lease_ops`, `struct sys_lease_context`, and public registration/context/operation functions. The ops table has `init`, `setup`, `update`, and `remove`.

Control flow: The header defines the callback contract: a backend receives opendb entries and can send break notifications through `break_send` using the supplied messaging context. `sys_lease.c` owns selection and dispatch.

State and persistence behavior: `sys_lease_context` holds tevent context, messaging context, break callback, backend private data, and the selected ops table. Backends own any persistent kernel lease state.

Dependencies and integration points: It forward declares opendb, messaging, and tevent types and includes `param/share.h` for share configuration. Backend files include this header to register themselves.

Risks: The `opendb_entry->fd` member is treated by backends as a pointer to an int, so callers must preserve that convention. Missing const protection on some pointers leaves backend misuse possible.

Test signals: Compile tests cover ABI shape; behavioral tests should use a fake backend to verify context creation and setup/update/remove dispatch without Linux-specific fcntl behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_lease.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_lease_linux.c -->
# sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_lease_linux.c

Purpose: `sys_lease_linux.c` implements the lease backend using Linux `fcntl(F_SETLEASE)` and realtime signal delivery to support Samba oplock breaks.

Important APIs, types, and functions: It defines `linux_lease_pending`, global `leases`, `linux_lease_signal_handler`, `linux_lease_pending_destructor`, `linux_lease_init`, `linux_lease_setup`, `linux_lease_update`, `linux_lease_remove`, `linux_lease_ops`, and `sys_lease_linux_init`.

Control flow: Backend init registers a tevent signal handler for `SIGRTMIN+1`. Setup ignores no oplocks, downgrades level-II oplocks to none because Linux leases do not support them, allocates a pending lease record for exclusive oplocks, sets the fd's signal with `F_SETSIG`, then sets a write lease with `F_SETLEASE`. On signal, the handler finds the pending entry by `si_fd` and calls `break_send(..., OPLOCK_BREAK_TO_NONE)`. Update/remove free the pending record, whose destructor unlocks the lease.

State and persistence behavior: Pending lease records are kept in a process-global linked list. Kernel lease state is tied to the fd and removed when the pending talloc object is freed or fd is invalid. No disk persistence is involved.

Dependencies and integration points: It depends on Linux fcntl lease support, tevent signal handling, opendb entries, cluster server IDs, and the generic `sys_lease` registry.

Risks: Global state plus signal-driven callbacks make lifecycle ordering important. The code compares `opendb_entry.fd` pointer identity in update/remove but compares actual fd value in the signal handler. Level-II oplocks are silently denied. Signal availability and `SA_SIGINFO` configure checks are platform-sensitive.

Test signals: Tests should cover setup failure paths for invalid fds, signal-triggered break callback with a real leased fd, cleanup on remove/update, level-II downgrade, and configure gating on `HAVE_F_SETLEASE_DECL`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_lease_linux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_notify.c -->
# sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_notify.c

Purpose: `sys_notify.c` is the generic registry and selector for system-specific change notify backends.

Important APIs, types, and functions: It exports `sys_notify_context_create`, `sys_notify_watch`, `sys_notify_register`, and `sys_notify_init`. Registered backends are stored in a global array of `struct sys_notify_backend`.

Control flow: Initialization runs static notify backend initializers once. Context creation chooses `notify:backend` from share options or falls back to the first registered backend, checks per-backend `notify:<name>` enable flags, and stores the selected watch callback. `sys_notify_watch` dispatches a watch request or returns `NT_STATUS_INVALID_SYSTEM_SERVICE`.

State and persistence behavior: Backend registration is global process state. Each notify context stores the event context, backend private data, selected backend name, and watch function. Durable filesystem state is not modified.

Dependencies and integration points: It uses Samba module initialization, share option helpers, talloc, tevent, and `sys_notify.h`. The inotify backend registers through this layer.

Risks: If no event context or backend exists, creation returns NULL. Backend selection is simple and can silently create a context with no watch callback if the named backend is disabled or absent. Backends mutate `notify_entry` filter bits to indicate handled parts.

Test signals: Tests should validate backend registration, default selection, explicit backend selection, per-backend disable flags, NULL event context behavior, and watch dispatch/error behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_notify.h -->
# sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_notify.h

Purpose: `sys_notify.h` declares the abstract interface between Samba change notify code and OS-specific notification backends.

Important APIs, types, and functions: It defines `sys_notify_callback_t`, `notify_watch_t`, `struct sys_notify_context`, `struct sys_notify_backend`, and prototypes for backend registration, context creation, watch setup, and initialization.

Control flow: Backends implement `notify_watch_t`, receive a `notify_entry`, callback, private data, and output handle pointer, then remove handled filter bits from the entry. The callback reports `struct notify_event` back to the higher layer.

State and persistence behavior: `sys_notify_context` stores tevent context, backend private data, name, and selected watch function. Watch handle lifetimes are backend-defined, usually talloc-owned.

Dependencies and integration points: It includes NDR notify types and share configuration declarations. It is consumed by generic notify code and backend modules such as inotify.

Risks: The `void *handle` parameter is really a pointer-to-handle convention, so callers and backends must agree on casting. Mutation of `notify_entry` filters is part of the API and can surprise new backend authors.

Test signals: Fake-backend tests should assert callback signature, handle return behavior, filter-bit mutation, and error propagation through `sys_notify_watch`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_notify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/sysdep/wscript_build -->
# sources/user-network-fs/samba/source4/ntvfs/sysdep/wscript_build

Purpose: This Waf script builds the system-dependent notify and lease abstraction layers and their Linux-specific modules.

Important APIs, types, and functions: It declares `sys_notify_inotify`, `sys_notify`, `sys_lease_linux`, and `sys_lease` using `bld.SAMBA_MODULE` and `bld.SAMBA_SUBSYSTEM`.

Control flow: The inotify module is enabled only when `HAVE_LINUX_INOTIFY` is configured. The Linux lease module is enabled only when `HAVE_F_SETLEASE_DECL` is configured. Generic subsystems always list their C files and dependencies.

State and persistence behavior: The build file has no runtime state. It controls which runtime backends can register with `sys_notify_init` and `sys_lease_init`.

Dependencies and integration points: It links notify code with `events`, `inotify`, `talloc`, and `tevent`; lease code with `tevent` and `talloc`. It is recursed from `source4/ntvfs/wscript_build` when the NTVFS file server is enabled.

Risks: Platform detection controls feature availability, so runtime behavior varies by host. Misconfigured feature tests can expose backend names without working OS support or omit useful modules.

Test signals: Build tests should cover Linux with inotify/F_SETLEASE, non-Linux without them, and module registration lists in generated static module tables.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/sysdep/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/sysdep/wscript_configure -->
# sources/user-network-fs/samba/source4/ntvfs/sysdep/wscript_configure

Purpose: This configure fragment detects platform capabilities needed by NTVFS system-dependent notify and lease code.

Important APIs, types, and functions: It uses Python `sys.platform`, `conf.CHECK_HEADERS`, `conf.CONFIG_SET`, `conf.DEFINE`, and `conf.CHECK_DECLS`.

Control flow: It skips Linux inotify detection on SunOS/illumos even if headers exist because illumos inotify is not an exact Linux match. Otherwise it checks for `sys/inotify.h` and defines `HAVE_LINUX_INOTIFY` if present. It also checks declaration availability for `SA_SIGINFO`.

State and persistence behavior: It writes configure symbols that drive later build decisions. It does not affect runtime state directly.

Dependencies and integration points: The symbols are consumed by `sysdep/wscript_build`, `inotify.c`, and signal/lease code. The fragment depends on Waf configure context APIs.

Risks: Header presence is a weak proxy for full Linux-compatible inotify semantics. `SA_SIGINFO` detection affects signal-driven lease support and must match libc/kernel behavior.

Test signals: Configure tests on Linux, SunOS/illumos, and BSD-like hosts should confirm `HAVE_LINUX_INOTIFY` and `SA_SIGINFO` outcomes match expected backend build availability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/sysdep/wscript_configure -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/unixuid/vfs_unixuid.c -->
# sources/user-network-fs/samba/source4/ntvfs/unixuid/vfs_unixuid.c

Purpose: `vfs_unixuid.c` implements the `unixuid` NTVFS pass-through module. It wraps downstream NTVFS operations with effective Unix UID/GID/group changes derived from the authenticated SMB session token.

Important APIs, types, and functions: Key pieces are `unixuid_private`, `save_unix_security`, `set_unix_security`, `unixuid_event_nesting_hook`, `nt_token_to_unix_security`, `unixuid_setup_security`, the `PASS_THRU_REQ` macro, wrapper functions for most NTVFS operations, and `ntvfs_unixuid_init`.

Control flow: On connect, the module stores private cache state, installs a tevent nesting hook, and calls the next backend as root so it can initialize databases. For normal requests, `PASS_THRU_REQ` saves the current Unix credentials, converts or reuses the session security token's Unix token, sets effective groups/gid/uid, calls `ntvfs_next_*`, then restores the saved context. The nesting hook temporarily returns to root when nested event loops begin and restores caller credentials afterward.

State and persistence behavior: Runtime state caches the last NT security token and corresponding Unix token per module instance. A global nesting counter tracks whether the event nesting hook must act. Persistent file effects are performed by downstream modules under the switched Unix credentials.

Dependencies and integration points: It depends on auth token conversion, wbclient, NTVFS pass-through APIs, tevent nesting hooks, and Samba setid wrappers. It registers for disk, print, and IPC backend types.

Risks: Credential switching is security-critical; any missed restore can leave the server in the wrong effective identity. The global nesting counter interacts with per-connection state and nested async processing. The cache compares token pointers, so token lifetime and reuse matter.

Test signals: Tests should verify operations execute as the session Unix identity, credentials restore on success and failure, nested tevent callbacks restore correctly, logoff clears cached token, and all registered backend types pass through as expected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/unixuid/vfs_unixuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/unixuid/wscript_build -->
# sources/user-network-fs/samba/source4/ntvfs/unixuid/wscript_build

Purpose: This Waf script builds the `ntvfs_unixuid` pass-through module.

Important APIs, types, and functions: It declares `bld.SAMBA_MODULE('ntvfs_unixuid', source='vfs_unixuid.c', subsystem='ntvfs', init_function='ntvfs_unixuid_init', deps='auth_unix_token talloc')`.

Control flow: The script has a single module declaration. It is reached from the parent NTVFS build only when `WITH_NTVFS_FILESERVER` is enabled.

State and persistence behavior: No runtime state is in the script. It determines whether the credential-switching wrapper can be loaded as an NTVFS module.

Dependencies and integration points: It links with Unix token conversion and talloc. The module registers with the NTVFS subsystem under `unixuid`.

Risks: Missing `auth_unix_token` support prevents the module from building, which changes the server's ability to enforce filesystem access using Unix credentials.

Test signals: Build and module-load tests should ensure `ntvfs_unixuid_init` is present and the module appears in NTVFS registration when file server support is enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/unixuid/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/wscript_build -->
# sources/user-network-fs/samba/source4/ntvfs/wscript_build

Purpose: This parent Waf script builds the NTVFS core library and recurses into backend/module subdirectories.

Important APIs, types, and functions: It declares private library `ntvfs`, recurses into `posix`, `common`, `unixuid`, and `sysdep`, and declares modules `ntvfs_cifs`, `ntvfs_simple`, and `ntvfs_ipc`.

Control flow: The core `ntvfs` library is enabled only with `WITH_NTVFS_FILESERVER`. The POSIX directory is always recursed, but most POSIX targets are internally gated. When file server support is enabled, common/unixuid/sysdep are recursed and CIFS/simple/IPC modules are built.

State and persistence behavior: The script has no runtime state, but build gating controls the installed module set and therefore available server backend behavior.

Dependencies and integration points: The core library depends on tevent and Samba module support. CIFS depends on raw SMB client libraries, simple depends on talloc, and IPC depends on named-pipe auth, GSSAPI, credentials, and DCERPC share code.

Risks: Inconsistent gating can build submodules without core support or omit required generated prototypes. The simple backend is built from only `vfs_simple.c` and `svfs_util.c`, matching its intentionally limited behavior.

Test signals: Build matrix tests should cover file server on/off and check that registered NTVFS modules match configured targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/ntvfs/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/loadparm.c -->
# sources/user-network-fs/samba/source4/param/loadparm.c

Purpose: `loadparm.c` provides helper functions that translate Samba loadparm settings into SMB client option structures.

Important APIs, types, and functions: It exports `lpcfg_smbcli_options` and `lpcfg_smbcli_session_options`. These fill `struct smbcli_options` and `struct smbcli_session_options`.

Control flow: `lpcfg_smbcli_options` reads a parametric `libsmb:client_guid`; if absent, it generates a random GUID. It then fills max transmit/mux, SPNEGO, signing, protocol bounds, Unicode, oplocks, SMB2/3 capabilities, credit request, transports, and SMB3 algorithm capabilities from loadparm. `lpcfg_smbcli_session_options` fills LANMAN, NTLMv2, and plaintext auth booleans.

State and persistence behavior: No state is stored by these helpers. The generated client GUID may differ per call unless configured, affecting client identity in negotiation.

Dependencies and integration points: It depends on loadparm getters, raw SMB client structures, SMB2 negotiate context helpers, GUID utilities, and transport/capability parsers. It is built as the `param_options` subsystem.

Risks: Defaults here affect all clients using these helpers. Random GUID fallback can complicate reproducibility. Capability parsing must remain aligned with loadparm option syntax.

Test signals: Tests should verify configured and random client GUID paths, protocol min/max propagation, signing/auth option mapping, transport parsing, and SMB3 capability parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/loadparm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/provision.c -->
# sources/user-network-fs/samba/source4/param/provision.c

Purpose: `provision.c` is C glue that calls Samba Python provisioning/schema code from C callers and bridges Python objects back to C `loadparm_context` and `ldb_context` pointers.

Important APIs, types, and functions: Key functions are `dict_insert`, `provision_module`, `schema_module`, `ldb_module`, `PyLdb_FromLdbContext`, `call_wrapper`, `provision_bare`, `py_dom_sid_FromSid`, `provision_store_self_join`, and `provision_get_schema`.

Control flow: Each public function initializes Python, updates `sys.path`, imports the target module, builds a kwargs dict, calls the Python function with no positional arguments, and extracts result attributes. `provision_bare` calls `samba.provision.provision_become_dc`. `provision_store_self_join` opens `secrets.ldb`, starts a transaction, passes an LDB wrapper to `secretsdb_self_join`, then commits. `provision_get_schema` calls `samba.schema.ldb_with_schema` and returns the embedded LDB.

State and persistence behavior: Provisioning changes are performed by Python code and LDB/secrets transactions. The C layer persists self-join changes only if the LDB transaction commits. Returned `samdb`, schema LDB, and loadparm contexts are talloc-referenced into the caller's memory context.

Dependencies and integration points: It depends on Python C API, pyldb, pytalloc, Samba Python modules, dynconfig path setup, secrets database helpers, NDR SID wrappers, and loadparm bridge utilities.

Risks: Reference ownership is delicate around borrowed module dictionaries and Python attributes. Error handling often returns generic `NT_STATUS_UNSUCCESSFUL` after printing Python errors. A failed path after starting a transaction must cancel or free correctly. Python module availability is runtime-critical.

Test signals: Tests should cover successful bare provision and self-join, Python import failure, transaction commit failure, schema override prefixmap, returned LDB/loadparm lifetime, and error string propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/provision.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/provision.h -->
# sources/user-network-fs/samba/source4/param/provision.h

Purpose: `provision.h` declares C structures and entry points for Samba provisioning helpers.

Important APIs, types, and functions: It defines `struct provision_settings`, `struct provision_result`, `struct provision_store_self_join_settings`, and prototypes for `provision_bare`, `provision_store_self_join`, and `provision_get_schema`.

Control flow: The header is a contract only. Callers fill provision settings, call the C glue, and receive LDB/loadparm outputs or error strings.

State and persistence behavior: `provision_settings` carries target DNs, server identity, realm/domain, machine password, target directory, and `use_ntvfs`. `provision_result` returns domain DN, SAM database, and loadparm context. Self-join settings carry secrets database material including SID, password, secure channel type, and key version.

Dependencies and integration points: It references LDB, loadparm, tevent, domain SID, and Netlogon secure channel types. `provision.c` implements the declared calls using Samba Python.

Risks: Most fields are raw pointers with no ownership annotation, so caller lifetime must be clear. Missing or NULL settings propagate into Python calls and may fail late.

Test signals: Compile coverage plus integration tests for all three public calls are needed; boundary tests should omit optional DN fields and validate required field failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/provision.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/pyparam.c -->
# sources/user-network-fs/samba/source4/param/pyparam.c

Purpose: `pyparam.c` implements the `samba.param` Python extension exposing Samba loadparm configuration objects and compiled path helpers.

Important APIs, types, and functions: It defines Python types `param.LoadParm` and `param.LoadparmService`, helpers `py_lp_ctx_get_helper`, load/set/dump/path/server-role methods, mapping access by service name, `py_lp_ctx_new`, and module functions `data_dir`, `default_path`, `setup_dir`, `modules_dir`, `bin_dir`, and `sbin_dir`.

Control flow: `LoadParm()` returns a reference to the global loadparm context by default, or loads a non-global config when `filename_for_non_global_lp` is supplied. Methods call loadparm getters/setters and convert parameter types to Python bool/int/string/list. Parametric options are parsed by `type:option` syntax for global or service scope. Dump methods write to stdout or opened files.

State and persistence behavior: The default Python object references Samba's global loadparm context, so changes can be process-wide. Non-global construction creates a separate context. Dump methods persist config text to requested files; path helpers return configured filesystem paths.

Dependencies and integration points: It depends on Python C API, pytalloc, Samba hostconfig/loadparm APIs, dynconfig constants, debug level access, and server role helpers. `pyparam_util.c` consumes the exposed `LoadParm` type.

Risks: Shared global context behavior can surprise Python callers. File dump methods open arbitrary paths/modes supplied by Python. Parameter conversion must stay in sync with loadparm enum/type definitions. Some error paths return NULL without setting a detailed Python exception.

Test signals: Python tests should cover global versus non-global construction, parametric get/set, service mapping, dump file output, compiled directory functions, weak_crypto property, server-role reporting, and unknown parameter/service errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/pyparam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/pyparam.h -->
# sources/user-network-fs/samba/source4/param/pyparam.h

Purpose: `pyparam.h` declares helper functions for converting Python loadparm-related inputs into C `struct loadparm_context` pointers.

Important APIs, types, and functions: It declares `_PUBLIC_ struct loadparm_context *lpcfg_from_py_object(TALLOC_CTX *, PyObject *)` and `_PUBLIC_ struct loadparm_context *py_default_loadparm_context(TALLOC_CTX *)`.

Control flow: Implementations in `pyparam_util.c` accept a Python string path, `None`, or a `samba.param.LoadParm` object and return a C loadparm context.

State and persistence behavior: Returned contexts may be global or talloc references to Python-backed contexts. The header itself has no state.

Dependencies and integration points: It includes `param/param.h` and uses Python object types. It is used by provisioning and Python xattr TDB helpers.

Risks: Callers need to know whether they receive a global context, a new loaded context, or a referenced Python object. Python headers must be included before or through compatible wrappers in translation units.

Test signals: Compile tests and Python/C bridge tests should verify conversions for string, `None`, valid LoadParm, and invalid object inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/pyparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/pyparam_util.c -->
# sources/user-network-fs/samba/source4/param/pyparam_util.c

Purpose: `pyparam_util.c` implements C utility functions for converting Python loadparm inputs into C loadparm contexts.

Important APIs, types, and functions: It implements `lpcfg_from_py_object` and `py_default_loadparm_context`. It uses the `samba.param.LoadParm` Python type and pytalloc extraction.

Control flow: If the Python object is a Unicode string, it initializes the global loadparm context and loads the named file. If it is `None`, it returns the default global context. Otherwise it imports `samba.param`, fetches the `LoadParm` type, checks the object type, and returns a talloc reference to its underlying context. Invalid inputs set `TypeError`.

State and persistence behavior: String and `None` paths use global loadparm initialization, potentially sharing process-wide configuration. A Python LoadParm object path returns a talloc reference tied to the caller's memory context.

Dependencies and integration points: It depends on Python C API compatibility headers, pytalloc, `samba.param`, loadparm APIs, and `param/pyparam.h`. It is used by provisioning and xattr TDB code that need loadparm flags.

Risks: Importing `samba.param` at conversion time can fail in embedded contexts without Python path setup. Loading a filename mutates or initializes global state. Error handling after failed `lpcfg_load` leaves the allocated context unfreed.

Test signals: Tests should cover object conversion under initialized/uninitialized Python paths, invalid types, failed file load, and lifetime of returned references after Python object deletion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/pyparam_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/secrets.c -->
# sources/user-network-fs/samba/source4/param/secrets.c

Purpose: `secrets.c` provides helpers for opening Samba's secrets LDB and extracting domain SID/keytab-related data.

Important APIs, types, and functions: It implements `secrets_db_create`, `secrets_db_connect`, `secrets_get_domain_sid`, and `keytab_name_from_msg`.

Control flow: Database helpers call `ldb_wrap_connect` for `secrets.ldb`, with or without `LDB_FLG_DONT_CREATE_DB`. `secrets_get_domain_sid` opens the database, searches under `cn=Primary Domains` for the flatname, fetches `objectSid` and optionally `secureChannelType`, pulls the SID with NDR, and returns an allocated `dom_sid`. `keytab_name_from_msg` prefers `krb5Keytab`; otherwise it converts `privateKeytab` to an LDB-relative file path and prefixes `FILE:`.

State and persistence behavior: The helpers open persistent `secrets.ldb` but only read in this file. Returned SIDs and strings are talloc-owned by the caller.

Dependencies and integration points: It depends on loadparm private paths through ldbwrap, DSDB search helpers, NDR security parsing, and LDB message APIs. Provisioning and authentication code use these helpers.

Risks: Search failures and missing attributes return NULL with error strings; callers must not conflate missing domain with parse corruption. The function does not free the LDB context on all success paths because it is talloc-parented under the caller context.

Test signals: Tests should cover create/connect flags, missing database, absent domain, malformed SID blob, missing secureChannelType when requested, and keytab selection precedence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/secrets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/secrets.h -->
# sources/user-network-fs/samba/source4/param/secrets.h

Purpose: `secrets.h` declares constants and helpers for Samba's secrets database layout.

Important APIs, types, and functions: It defines DN/filter macros such as `SECRETS_PRIMARY_DOMAIN_DN`, `SECRETS_PRINCIPALS_DN`, `SECRETS_PRIMARY_DOMAIN_FILTER`, `SECRETS_PRIMARY_REALM_FILTER`, `SECRETS_KRBTGT_SEARCH`, `SECRETS_PRINCIPAL_SEARCH`, and `SECRETS_LDAP_FILTER`. It declares `randseed_init`, secrets DB open functions, `secrets_get_domain_sid`, and `keytab_name_from_msg`.

Control flow: The header is a contract for callers constructing LDB searches or opening secrets databases.

State and persistence behavior: It describes persistent records in `secrets.ldb` but stores no state itself.

Dependencies and integration points: It forward declares loadparm, tevent, LDB message/context types, and includes NDR misc types for `enum netr_SchannelType`.

Risks: Filter macros contain `%s` placeholders and must be used with proper LDB escaping. Layout constants are shared assumptions across provisioning, authentication, and RPC code.

Test signals: Compile tests and LDB integration tests should confirm filters match created secrets records and that callers escape user/domain input correctly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/secrets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/share.c -->
# sources/user-network-fs/samba/source4/param/share.c

Purpose: `share.c` implements the generic share configuration backend registry and forwarding API.

Important APIs, types, and functions: It exports option accessors `share_string_option`, `share_int_option`, `share_bool_option`, `share_string_list_option`; lifecycle APIs `share_list_all`, `share_get_config`, `share_create`, `share_set`, `share_remove`; registry APIs `share_register`, `share_get_context`, and `share_init`.

Control flow: Option and CRUD functions dispatch through the selected `share_ops`. Optional create/set/remove return `NT_STATUS_NOT_IMPLEMENTED` when absent. Registration rejects duplicate names, reallocates the global backend vector, copies the ops table, and stores a duplicated backend name. `share_get_context` currently selects the `classic` backend.

State and persistence behavior: Registered backends are process-global heap state. Actual share persistence depends on backend implementation; the classic backend reads loadparm and does not implement mutations.

Dependencies and integration points: It depends on `param/share.h`, loadparm types, Samba module initialization, and static share module tables. NTVFS backends use share option accessors heavily.

Risks: The backend list uses manual allocation outside talloc and panics on OOM. `share_get_context` is hard-wired to `classic`, limiting backend configurability. No synchronization is visible around backend registration.

Test signals: Existing local share tests exercise context creation and unsupported mutation paths. Additional tests should cover duplicate backend registration, missing classic backend, and option dispatch through a fake backend.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/share.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/share.h -->
# sources/user-network-fs/samba/source4/param/share.h

Purpose: `share.h` defines the share configuration abstraction used by Samba4 NTVFS and related services.

Important APIs, types, and functions: It declares `struct share_context`, `struct share_config`, `enum share_info_type`, `struct share_info`, `struct share_ops`, public share APIs, option name macros, and default values.

Control flow: Backends implement `share_ops` to initialize contexts, retrieve typed options, list shares, fetch configs, and optionally create/set/remove shares. Generic callers use wrapper functions from `share.c`.

State and persistence behavior: `share_context` stores selected ops and backend private data. `share_config` names a share and carries backend opaque service data. Persistent state is backend-defined.

Dependencies and integration points: It forward declares `loadparm_context` and `tevent_context`; the classic backend maps these options to loadparm service parameters. POSIX/simple NTVFS backends use macros such as `SHARE_PATH`, `SHARE_READONLY`, and mask defaults.

Risks: Defaults are security-sensitive: `SHARE_READONLY_DEFAULT` is true, create mask is 0744, and directory mask is 0755. Option names must remain stable because backend code and smb.conf compatibility rely on them.

Test signals: Tests should verify each typed accessor, option defaults, classic mapping, and behavior for optional mutation functions on read-only backends.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/share.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/share_classic.c -->
# sources/user-network-fs/samba/source4/param/share_classic.c

Purpose: `share_classic.c` implements the `classic` share backend by adapting Samba loadparm services to the generic share API.

Important APIs, types, and functions: Key functions are `sclassic_init`, `sclassic_string_option`, `sclassic_int_option`, `sclassic_bool_option`, `sclassic_string_list_option`, `sclassic_list_all`, `sclassic_get_config`, static `ops`, and `share_classic_init`.

Control flow: Initialization stores the loadparm context as backend private data. Option getters check for parametric `type:option` names first, then map generic share option names to loadparm service getters and defaults. Listing iterates all configured services. `get_config` looks up a service by name and returns a `share_config` with opaque service pointer. The ops table omits create/set/remove, making mutations unsupported.

State and persistence behavior: The backend references the existing loadparm context; it does not write configuration. Returned share configs are talloc objects that point back to loadparm service structures.

Dependencies and integration points: It depends on loadparm service APIs and `share_register`. NTVFS connect code consumes `SHARE_PATH`, read-only, mask, oplock, case, and parametric options through this backend.

Risks: Unknown options log and return defaults, which can hide configuration mistakes. Parametric integer options treat zero as missing and replace it with the default. The case-insensitive filesystem mapping is intentionally nuanced and easy to misread.

Test signals: Local share tests cover context setup and unsupported create/remove paths. Additional tests should cover every mapped option, parametric strings/ints/bools/lists, unknown share lookup, and zero-valued parametric integer behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/share_classic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/tests/loadparm.c -->
# sources/user-network-fs/samba/source4/param/tests/loadparm.c

Purpose: `param/tests/loadparm.c` defines local torture tests for loadparm context creation, option parsing, parametric options, service lookup, and server role derivation.

Important APIs, types, and functions: It contains test functions for `loadparm_init`, `lpcfg_set_option`, `lpcfg_set_cmdline`, `lpcfg_do_global_parameter`, `lpcfg_do_global_parameter_var`, parametric double/bool/int/bytes accessors, service parameter setting, service lookup, and server role/security combinations. `torture_local_loadparm` registers the suite.

Control flow: Each test creates a fresh loadparm context, applies one or more configuration changes, then asserts getter results. Server role tests cover standalone, AD DC, member, PDC/BDC inference, and security-driven member inference.

State and persistence behavior: Tests use in-memory loadparm contexts only; no config files are written. They validate state transitions inside the context.

Dependencies and integration points: It depends on Samba torture framework, loadparm APIs, share declarations, and server role constants.

Risks: Coverage is focused on core parsing and role inference, not Python bindings or file loading. It assumes default role/security values that can change with global defaults.

Test signals: This file is itself a signal for `param/loadparm` behavior. New option parsing logic should add simple tests here for invalid syntax, defaults, and parametric value conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/tests/loadparm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/tests/share.c -->
# sources/user-network-fs/samba/source4/param/tests/share.c

Purpose: `param/tests/share.c` defines local torture tests for the generic share API using the classic backend fixture.

Important APIs, types, and functions: Tests include `test_list_empty`, `test_create`, `test_create_invalid`, `test_share_remove_invalid`, `test_share_remove`, `test_double_create`, fixture functions `setup_classic` and `teardown`, and suite factory `torture_local_share`.

Control flow: The suite calls `share_init`, creates a `classic` test case, and obtains a share context from the torture loadparm context. Mutation tests call `share_create`/`share_remove`; if the backend returns `NT_STATUS_NOT_IMPLEMENTED`, the test is skipped. Otherwise they assert creation, invalid parameter, collision, and removal behavior.

State and persistence behavior: For the classic backend, no share mutations persist because create/remove are unsupported and skipped. The fixture context is talloc-freed on teardown.

Dependencies and integration points: It depends on the torture framework, generic share APIs, and loadparm-backed classic context setup.

Risks: Because classic skips mutation tests, the suite does not currently validate a writable backend unless one is added. `test_list_empty` does not assert count, only successful listing.

Test signals: This suite verifies that the share subsystem initializes and that unsupported operations are reported consistently. Writable backend work should extend these tests to avoid skip-only coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/tests/share.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/wscript_build -->
# sources/user-network-fs/samba/source4/param/wscript_build

Purpose: This Waf script builds Samba4 parameter/provision/share/secrets components and Python bindings.

Important APIs, types, and functions: It declares subsystems for embedded `PROVISION`, `share`, `SECRETS`, `pyparam_util`, and `param_options`; modules/libraries `share_classic`, Python extension `pyparam`, and grouping library `shares`.

Control flow: Python-enabled targets use `bld.pyembed_libname` for embedded Python, pytalloc, pyldb, and pyparam utility dependencies. The provision subsystem is enabled only when Python build support is enabled. Share and secrets subsystems are normal C targets, while `pyparam` installs as `samba/param.so`.

State and persistence behavior: The script has no runtime state. Build outcomes determine whether provisioning from C, Python loadparm bindings, share backend registration, secrets database helpers, and client option helpers are available.

Dependencies and integration points: It links to `samba-hostconfig`, `server-role`, `samba-debug`, `ldb`, `tdb-wrap`, `util_tdb`, `NDR_SECURITY`, `tevent`, and `ldbwrap`.

Risks: Python target names use embedded-library helper names, so Python-disabled builds omit provisioning glue. Dependency drift can break extension import at runtime despite successful C compilation.

Test signals: Build tests should cover Python enabled/disabled, import of `samba.param`, module registration of `share_classic`, and linkage of `SECRETS` and `param_options`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/param/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/backupkey/dcesrv_backupkey.c -->
# sources/user-network-fs/samba/source4/rpc_server/backupkey/dcesrv_backupkey.c

Purpose: `dcesrv_backupkey.c` implements Samba's DCERPC server for the MS-BKRP BackupKey protocol. It returns domain backup certificates, decrypts client-wrapped secrets, and encrypts/decrypts server-wrapped secrets for domain users on writable Active Directory DCs.

Important APIs, types, and functions: Major helpers include `dcesrv_interface_backupkey_bind`, `set_lsa_secret`, `get_lsa_secret`, RSA key conversion helpers, `get_and_verify_access_check`, `bkrp_client_wrap_decrypt_data`, certificate/key generation helpers, `bkrp_retrieve_client_wrap_key`, server-wrap key retrieval/generation helpers, `bkrp_server_wrap_decrypt_data`, `bkrp_generic_decrypt_data`, `bkrp_server_wrap_encrypt_data`, and `dcesrv_bkrp_BackupKey`.

Control flow: Binding requires DCERPC privacy. The main `BackupKey` handler rejects non-AD-DC roles, opens samdb as system, skips service on RODCs, then dispatches by action GUID. Certificate retrieval lazily generates an RSA keypair and self-signed certificate, stores the keypair as `BCKUPKEY_<guid>` and preferred GUID as `BCKUPKEY_PREFERRED`, then returns the DER certificate. Client-wrap decrypt parses NDR, loads the private keypair secret, decrypts the reversed RSA secret, validates magic/hash/access-check SID, and returns plaintext. Server-wrap encrypt/retrieve uses `BCKUPKEY_P` and `BCKUPKEY_<guid>` symmetric keys, derives RC4/HMAC keys from random values with SHA1 HMAC, binds ciphertext to caller SID, and validates MAC/SID on decrypt.

State and persistence behavior: Persistent protocol secrets are stored as LSA secret objects in samdb's system container. Client-wrap RSA keypairs/certs and server-wrap symmetric keys are generated on demand and persist under BackupKey secret names. Per-call cryptographic buffers are talloc or GnuTLS-owned and freed/deinitialized along error paths where implemented.

Dependencies and integration points: It depends on generated BackupKey NDR server stubs, samdb/DSDB secret manipulation, auth session info, DC role/loadparm checks, GnuTLS x509/private key/cipher/HMAC APIs, NDR security SID encoding, and DCERPC privacy enforcement from common server code.

Risks: This file is security-critical. Secret storage, RODC handling, SID access checks, constant-time hash comparisons, RSA bignum endian conversion, and legacy RC4/SHA1 compatibility must be preserved exactly. Some paths return client-expected generic errors, complicating diagnostics. Debug dumps use password-aware logging helpers but still require care. Generated key insertion uses create-only semantics and may race on first use.

Test signals: Required coverage includes privacy-required bind, non-DC and RODC rejection, first-use key generation, certificate retrieval, client-wrap v2/v3 decrypt success and bad hash/SID/magic failures, server-wrap encrypt/decrypt round trips, missing/corrupt LSA secrets, and interoperability vectors from MS-BKRP or Windows clients.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/backupkey/dcesrv_backupkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/browser/dcesrv_browser.c -->
# sources/user-network-fs/samba/source4/rpc_server/browser/dcesrv_browser.c

Purpose: `dcesrv_browser.c` provides a mostly stubbed DCERPC endpoint server for the legacy Browser service pipe.

Important APIs, types, and functions: It implements handlers for Browser RPC operations including `BrowserrServerEnum`, `BrowserrDebugCall`, `BrowserrQueryOtherDomains`, reset/debug/statistics calls, `BrowserrSetNetlogonState`, `BrowserrQueryEmulatedDomains`, and `BrowserrServerEnumEx`.

Control flow: Nearly all operations immediately raise `DCERPC_FAULT_OP_RNG_ERROR`, indicating unsupported operation range. `BrowserrQueryOtherDomains` is partially implemented for info level 100: it validates the input union, allocates an empty `BrowserrSrvInfo100Ctr`, assigns zero entries, sets total entries to zero, and returns `WERR_OK`. Other levels return `WERR_INVALID_LEVEL`.

State and persistence behavior: No server state is stored or mutated. The one implemented path returns an allocated empty result under the call memory context.

Dependencies and integration points: It depends on DCERPC server declarations and generated browser NDR stubs (`ndr_browser_s.c`). It is part of Samba's RPC endpoint set for compatibility with clients that probe the browser pipe.

Risks: Clients expecting real Browser service enumeration/statistics will receive faults or empty domain data. The stub must still marshal level-100 output correctly to avoid client crashes.

Test signals: RPC tests should assert unsupported methods fault consistently, `BrowserrQueryOtherDomains` level 100 returns an empty success response, invalid levels fail, and NULL info100 input returns `WERR_INVALID_PARAMETER`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/browser/dcesrv_browser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/common/common.h -->
# sources/user-network-fs/samba/source4/rpc_server/common/common.h

Purpose: `common.h` defines small shared declarations for Samba4 DCERPC server interface implementations.

Important APIs, types, and functions: It forward declares share, DCERPC, NDR packet, and auth session types; defines `struct dcerpc_server_info` with domain name and version fields; and includes generated/common RPC server prototypes through `rpc_server/common/proto.h`.

Control flow: The header has no executable flow. RPC server C files include it for shared prototypes and server info type declarations.

State and persistence behavior: `dcerpc_server_info` is a data carrier only. The header stores no state.

Dependencies and integration points: It is used by RPC server implementations such as BackupKey and depends on generated/common prototype headers.

Risks: Duplicate forward declaration of `struct dcesrv_context` is harmless but untidy. Changes to this header affect many RPC server build units.

Test signals: Compile coverage is the main signal. Runtime server info behavior should be tested wherever `dcerpc_server_info` is populated and returned by common RPC helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/common/common.h -->
