# subset-b-009866 Research

Grouped research for the Samba smbd open, Linux kernel oplock, and password/session helper sources. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/open.c -->
# sources/user-network-fs/samba/source3/smbd/open.c

## Purpose
`open.c` is the central Samba `smbd` implementation for SMB file and directory create/open semantics. It translates SMB1/SMB2 create parameters into VFS opens, validates NT access masks and share modes, enforces delete-on-close and stream rules, coordinates oplocks and SMB2 leases, handles deferred/retried opens, and installs inherited DOS/NT ACL metadata for newly created objects.

The exported surface includes `fd_openat()`, `fd_close()`, `reopen_from_fsp()`, `smbd_check_access_rights_fsp()`, `check_parent_access_fsp()`, `smbd_calculate_access_mask_fsp()`, `send_break_message()`, `defer_smb1_sharing_violation()`, `is_deferred_open_async()`, `smbd_is_tmpname()`, `create_directory()`, `msg_file_was_renamed()`, and `create_file_default()`. The main public VFS entry point is `create_file_default()`, which backs `vfs_default.c` and dispatches to the deeper create/open machinery.

## Important APIs, Types, And Helpers
Important local state structs are `deferred_open_record` for open retry bookkeeping, `open_ntcreate_lock_state` for share-mode lock preparation/cleanup, `delay_for_oplock_state` and `blocker_debug_state` for lease/oplock delay decisions, and several iterator states for share-mode and lease DB traversal.

Access checking is layered. `smbd_check_access_rights_fname()` first applies share access, root override, DELETE exceptions, symlink delete behavior, and `do_not_check_mask`. `smbd_check_access_rights_sd()` runs `se_file_access_check()`, then applies compatibility overrides for DOS attribute writes and parent `DELETE_CHILD` rights. `smbd_check_access_rights_fsp()` obtains NT ACLs via `SMB_VFS_FGET_NT_ACL()` on `metadata_fsp(fsp)`. `smbd_calculate_access_mask_fsp()` maps generic rights, resolves `MAXIMUM_ALLOWED_ACCESS`, clamps by share permissions, and respects readonly attributes unless computing an ignore-readonly maximum-access response.

Open primitives are split to reduce races. `fd_openat()` opens via `SMB_VFS_OPENAT()`, prefers direct `O_NOFOLLOW` opens when possible, falls back through `filename_convert_dirfsp_rel()` for symlink/path conversion, and fills `fsp` stat and directory flags. `fd_open_atomic()` avoids ambiguous `O_CREAT` results by trying create-exclusive or non-create variants and retrying once on expected races. `reopen_from_fsp()` reopens an existing pathref either through `/proc/self/fd` style paths (`reopen_from_fsp_pathref_based()`) or a name-based reopen, with automount detection through `fstatfs()`, `AUTOFS_SUPER_MAGIC`, configured `automount fs types`, and optional `VFS_OPEN_HOW_RESOLVE_NO_XDEV`.

Share and lease APIs center on `share_mode_lock`, `share_mode_entry_prepare_lock_add()`, `set_share_mode()`, `del_share_mode()`, `remove_share_oplock()`, `share_mode_watch_send()`, and `share_mode_forall_entries()`. Lease persistence is through `leases_db_get()`, `leases_db_set()`, `leases_db_add()`, and `leases_db_parse()`.

## Control Flow
The high-level flow starts in `create_file_default()`. It records the original request time for deferred opens, handles fake NTFS stream files, validates named-stream support and default stream directory cases, processes SMB2 POSIX create blobs through `check_posix_create_context()`, and then calls `create_file_unixpath()`.

`create_file_unixpath()` rejects unsupported create options such as `FILE_OPEN_BY_FILE_ID`, validates reparse/symlink cases, normalizes internal opens to `INTERNAL_OPEN_ONLY`, performs SMB2 lease-key matching with `lease_match()`, opens streams for delete checks when a base file is opened with `DELETE_ACCESS`, enforces `SEC_FLAG_SYSTEM_SECURITY`, validates delete-on-close access, optionally opens or creates a base file for alternate streams, binds or allocates a `files_struct`, obtains a parent `dirfsp`, and dispatches to either `open_directory()` or `open_file_ntcreate()`. If a normal file path returns `NT_STATUS_FILE_IS_A_DIRECTORY`, it retries through `open_directory()` unless the open was a stream or explicitly non-directory.

`open_file_ntcreate()` handles file-specific semantics: printer opens go to `print_spool_open()`, existing directories are rejected early, POSIX and DOS attributes are converted to Unix modes, create dispositions are validated, readonly/timewarp restrictions are applied, access masks are recalculated, open flags are built, and the lower `open_file()` performs the actual file descriptor work. After the fd is open, it verifies dev/inode stability, determines `FILE_WAS_CREATED`, `FILE_WAS_OPENED`, or `FILE_WAS_OVERWRITTEN`, enters the share-mode lock path, possibly obtains kernel oplocks, truncates under lock, clears alternate data streams for overwrite/supersede, takes kernel share modes, sets delete-on-close, sets archive/sparse/mode bits, and releases the prepared share lock with cleanup callbacks on failure.

`open_directory()` separately implements directory create/open. It creates missing directories through `mkdir_internal()`, validates directory identity, reopens directories with a usable fd when needed for listing/add/flush cases, applies access checks on existing directories, masks non-lease oplock requests, stores a directory share-mode entry, and applies delete-on-close semantics. `mkdir_internal()` may create via a temporary `SMBD_TMPDIR_PREFIX` name and rename into place to hide partially initialized directories while ACLs, DOS attributes, inherited owner, and mode bits are applied.

## State And Persistence
Persistent cross-process state is primarily the share-mode database and leases database. Open state is stored in `share_mode_entry` records keyed by `file_id` and includes access masks, share access, oplock type, lease key, server id, and name hash. Lease state persists in `leases_db`, including client GUID, lease key, file IDs, current state, breaking state, version, epoch, service path, base name, and stream name.

Per-connection state is held on `files_struct`: fd/pathref state, file id, vuid, SMB pid, access mask, oplock type, lease pointer/refcount, base stream fsp, flags for directory, pathref, POSIX open, append, sparse, delete-on-close, kernel share modes, and AIO write-behind. Deferred open state is persisted in the SMB deferred message queue by `push_deferred_open_message_smb()` and later reactivated by `schedule_deferred_open_message_smb()`.

Filesystem persistence includes created files/directories, chmod/chown changes, POSIX ACL inheritance, NT ACL writes through `SMB_VFS_FSET_NT_ACL()`, DOS attributes through `file_set_dosmode()`, xattrs/streams through stream VFS modules, allocation via `vfs_allocate_file_space()`, and compression changes via `SMB_VFS_SET_COMPRESSION()`.

## Dependencies And Integration Points
This file integrates with the Samba VFS layer (`SMB_VFS_OPENAT`, `FGET_NT_ACL`, `FSET_NT_ACL`, `FTRUNCATE`, `FILESYSTEM_SHAREMODE`, `MKDIRAT`, `RENAMEAT`, `UNLINKAT`, compression and stream APIs), the security subsystem (`security_descriptor`, `security_token`, `se_file_access_check`, SID/idmap helpers), loadparm configuration (`lp_*`), messaging (`messaging_send`, `MSG_SMB_BREAK_REQUEST`, rename messages), tevent timers/watchers, the share-mode and leases databases, SMB1/SMB2 request/session structures, and notification delivery via `notify_fname()`.

Direct call sites in the surrounding tree include `vfs_default.c` calling `create_file_default()`, durable handle restore and directory code using `fd_openat()`/`reopen_from_fsp()`, SMB2 oplock code using `send_break_message()`, and session/open close paths relying on the share-mode entries this file creates.

## Risks And Edge Cases
The risk profile is high because this code is the concurrency boundary between SMB semantics and POSIX/VFS behavior. Key risks include TOCTOU races around path resolution, symlink replacement, automount handling, dev/inode mismatch after path walk, and create/open races. The code mitigates many of these with pathrefs, `O_NOFOLLOW`, `O_CREAT|O_EXCL`, post-open stat checks, and locked share-mode updates, but changes in this area can easily reopen races.

Lease/oplock risks include stale share entries, hung clients, server-id death, Windows lease-client quirks, kernel oplock blocking with `O_NONBLOCK`, and inconsistent lease epochs. Deferred opens must preserve original request timeout and avoid retry storms. Share access calculations are subtle because cached aggregate flags may need recalculation when stale entries are discovered.

Security risks include incorrect `MAXIMUM_ALLOWED_ACCESS`, owner/group inheritance, parent delete override, SACL privilege handling, readonly/share write interactions, named stream deletion checks, and delete-on-close without delete rights. Directory temporary-name creation reduces partial-object visibility but adds rollback and rename portability risks.

## Test Signals
Relevant selftest and torture signals include `raw.open`, `raw.mkdir`, `raw.unlink`, `raw.streams`, `raw.oplock`, `smb2.oplock`, `smb2.lease`, `smb2.dirlease`, `smb2.streams`, `smb2.create_no_streams`, POSIX tests such as `POSIX`, `POSIX-APPEND`, `POSIX-SYMLINK-*`, `POSIX-MKDIR`, `POSIX-DIR-DEFAULT-ACL`, and SMB1 sharing-violation/deferred behavior. `source3/selftest/tests.py` also gates `smb2.kernel-oplocks` when Linux kernel oplocks are available. Focused regression signals should cover readonly files/shares, DELETE_ON_CLOSE, alternate streams, ACL inheritance, SMB2 maximum-allowed behavior, lease break/ack ordering, directory leases, temporary directory create rollback, and kernel share-mode failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/oplock_linux.c -->
# sources/user-network-fs/samba/source3/smbd/oplock_linux.c

## Purpose
`oplock_linux.c` provides Samba `smbd` support for Linux kernel oplocks, implemented with Linux file leases. When compiled with `HAVE_KERNEL_OPLOCKS_LINUX`, it sets lease signal delivery, requests and releases kernel leases through the VFS `linux_setlease` hook, and wires Linux lease-break signals back into Samba’s oplock break path.

When kernel oplocks are not available at build time, the file only provides an empty dummy symbol so the compilation unit remains valid.

## Important APIs, Types, And Functions
`linux_set_lease_sighandler(int fd)` sets `F_SETSIG` to `RT_SIGNAL_LEASE` for a file descriptor. `linux_setlease(int fd, int leasetype)` temporarily becomes root, installs the signal target, calls `fcntl(fd, F_SETLEASE, leasetype)`, preserves `errno`, and then drops root privileges.

`linux_oplock_signal_handler()` is a tevent signal callback for `RT_SIGNAL_LEASE`. It extracts `si_fd`, finds the matching `files_struct` with `file_find_fd()`, and calls `break_kernel_oplock()` through the server connection messaging context.

`linux_set_kernel_oplock()` requests `F_WRLCK` through `SMB_VFS_LINUX_SETLEASE()` and logs the file id/gen id. `linux_release_kernel_oplock()` optionally logs current `F_GETLEASE` state and releases the lease with `F_UNLCK`. `linux_oplocks_available()` probes `/dev/null` with `F_GETLEASE`. `linux_init_kernel_oplocks()` allocates `struct kernel_oplocks`, assigns `linux_koplocks`, stores the `smbd_server_connection`, registers the tevent signal handler, and returns the context.

## Control Flow
Initialization starts when `init_kernel_oplocks()` in `smb2_oplock.c` calls `linux_init_kernel_oplocks()` if configuration and platform checks allow it. The initializer probes support, allocates context, and registers a realtime signal handler with `SA_SIGINFO`.

On granting an oplock, higher-level oplock code calls the `kernel_oplocks_ops.set_oplock` function, which maps to `linux_set_kernel_oplock()`. That path goes through the VFS macro `SMB_VFS_LINUX_SETLEASE()`, so VFS modules can audit, replace, or reject lease operations before the default wrapper reaches `linux_setlease()`.

When another local process conflicts with a kernel lease, Linux sends `RT_SIGNAL_LEASE`. The tevent signal callback maps the fd back to Samba’s open file and invokes `break_kernel_oplock()`, which lets the normal SMB oplock break logic notify the client. Release uses the matching `release_oplock` op and clears the Linux lease.

## State And Persistence
The persistent kernel state is the Linux file lease attached to the open fd. Samba-side state is held in `sconn->oplocks.kernel_ops`, `files_struct` records, and the usual share-mode/oplock records managed elsewhere. `linux_setlease()` briefly changes effective privileges with `become_root()`/`unbecome_root()` but restores `errno` and does not persist process identity changes.

The signal handler depends on fd identity remaining findable through `file_find_fd()`. If the fd was already closed, it logs and drops the signal.

## Dependencies And Integration Points
The file depends on Linux `fcntl()` lease operations (`F_SETSIG`, `F_SETLEASE`, `F_GETLEASE`, `F_WRLCK`, `F_UNLCK`), realtime signals, tevent signal integration, Samba file lookup, `break_kernel_oplock()`, VFS lease wrappers, loadparm-controlled kernel oplock initialization, and `struct kernel_oplocks_ops` from Samba headers.

Surrounding integration points include `vfs_default.c` calling `linux_setlease()` from `vfswrap_linux_setlease()`, VFS modules such as GPFS/gluster/audit wrappers overriding `linux_setlease_fn`, and `smb2_service.c` enabling kernel oplocks per share.

## Risks And Edge Cases
Kernel oplocks are platform- and configuration-sensitive. Risks include realtime signal setup failure, support probes that pass on `/dev/null` but fail on a real backing filesystem, fd reuse races if a signal arrives late, lease release failures, and VFS modules returning errors or not implementing the hook. Because `linux_setlease()` becomes root to ensure lease-break signal delivery, privilege bracketing and `errno` preservation are important correctness points.

The handler logs and ignores missing fds; that is safe for late signals but can hide bugs if file tracking is inconsistent. The implementation requests write leases only (`F_WRLCK`), so semantic mapping to SMB oplock types is handled in the higher-level oplock code.

## Test Signals
Build configuration should define `HAVE_KERNEL_OPLOCKS_LINUX` only when `F_SETLEASE` support is detected. Runtime selftest coverage is represented by `source3/selftest/tests.py`, which detects Linux kernel oplock support and schedules `OPLOCK5` and `smb2.kernel-oplocks` when available. Manual or automated tests should verify lease grant/release logging, conflict-triggered signal delivery, interaction with VFS wrappers, and graceful behavior when the kernel or filesystem refuses leases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/oplock_linux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/password.c -->
# sources/user-network-fs/samba/source3/smbd/password.c

## Purpose
`password.c` contains small `smbd` session and homes-share helpers. It invalidates authenticated virtual user IDs and dynamically registers `[homes]` shares for users whose Unix account has a valid home directory.

## Important APIs, Types, And Functions
`invalidate_vuid(struct smbd_server_connection *sconn, uint64_t vuid)` looks up a live `smbXsrv_session` with `get_valid_smbXsrv_session()`. If found, it calls `session_yield()`, decrements `sconn->num_users`, and clears connection/session vuid caches with `conn_clear_vuid_caches()`.

`register_homes_share(const char *username)` checks whether a static or previously created service already exists with `lp_servicenumber()`. If so, it returns that service number. Otherwise it resolves the Unix account with `Get_Pwnam_alloc()`, rejects missing/empty home directories and `/`, and calls `add_home_service(username, username, pwd->pw_dir)`.

## Control Flow
Session invalidation is intentionally short. Invalid or already-gone vuids return without side effects. Valid sessions are yielded first, then the server connection user count is decremented under an assertion that it was positive, then all cached references to the vuid are cleared from connection state.

Homes registration first prefers existing loadparm services, which avoids recreating a dynamic share. If no service exists, it queries passwd data on the current talloc stack, validates the directory field, creates the home service, frees the passwd record, and returns the resulting service index or `-1`.

## State And Persistence
`invalidate_vuid()` mutates in-memory server state: the `smbXsrv_session`, `sconn->num_users`, and vuid caches on connections. Durable session database effects are delegated to `session_yield()`.

`register_homes_share()` mutates Samba service configuration through `add_home_service()`, creating an in-process dynamic service for the username. It reads but does not modify system passwd data. Allocations use `talloc_tos()` and are freed before return.

## Dependencies And Integration Points
The file depends on `smbXsrv_session` lookup/yielding, connection cache management, loadparm service lookup and substitution, passwd lookup, and service creation. Call sites include SMB1 and SMB2 session setup paths that register homes for authenticated Unix users, `srvsvc` service lookup for homes, and `smbXsrv_session.c` invalidation on session shutdown.

## Risks And Edge Cases
The main session risk is counter/cache consistency: `sconn->num_users` must only be decremented when a valid session was found, and all connection caches must be cleared after yielding. For homes, the safety checks prevent creating a share rooted at `/` or at an empty/missing path. Remaining risks are stale passwd/home data, username-to-service naming conflicts, and dynamic homes behavior differing across SMB1, SMB2, and RPC service enumeration paths.

## Test Signals
Relevant signals include SMB1/SMB2 session setup and logoff tests, dynamic `[homes]` blackbox coverage (`samba3.blackbox.homes` in `source3/selftest/tests.py`), and session teardown paths that exercise `invalidate_vuid()`. Focused tests should verify that repeated homes registration reuses the service, invalid home directories return `-1`, root home `/` is rejected, and vuid invalidation clears per-connection caches without underflowing `num_users`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/password.c -->
