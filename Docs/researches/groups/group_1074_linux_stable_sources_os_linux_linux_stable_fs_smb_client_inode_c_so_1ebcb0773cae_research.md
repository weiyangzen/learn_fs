# Group Research: group_1074_linux_stable_sources_os_linux_linux_stable_fs_smb_client_inode_c_so_1ebcb0773cae

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/inode.c

Read status: complete.

## Purpose

Implements CIFS/SMB inode lifecycle, metadata conversion, attribute revalidation, VFS mutation operations, and setattr/truncate handling. This is the SMB client’s main bridge between server metadata and Linux VFS inode state.

## Main Responsibilities

- Convert SMB1 Unix, SMB2/SMB3 all-info, and SMB3.1.1 POSIX metadata into `struct cifs_fattr`.
- Instantiate and refresh Linux inodes from `cifs_fattr`, including inode operations, file operations, address-space operations, size, timestamps, ownership, mode, reparse tags, and symlink targets.
- Decide when cached inode data and pagecache mappings must be invalidated.
- Fetch inode metadata by path or by open file handle, with dialect-specific paths for legacy Unix extensions, SMB2/3, POSIX extensions, ACL-derived modes, SFU emulation, MF symlinks, DFS junctions, and reparse points.
- Implement VFS operations for unlink, mkdir, rmdir, rename, getattr, fiemap, truncate, chmod/chown/chgrp/time updates, and root inode lookup.
- Handle server inode-number collisions and automatically disable `serverino` when the server provides unstable or unusable inode numbers.

## Important Functions

- `cifs_set_netfs_context()` / `cifs_set_ops()`
  - Initialize netfs state and choose inode/file/address-space operations based on file type and mount flags.
  - Regular files select direct, strict, no-BRL, or normal CIFS file ops; directories select namespace ops when automounting; symlinks select symlink ops.

- `cifs_revalidate_cache()`
  - Compares new metadata with cached mtime and remote size.
  - Marks the mapping invalid and invalidates fscache when data may have changed and no read oplock protects the cache.

- `cifs_fattr_to_inode()`
  - Central conversion from SMB client metadata to Linux inode fields.
  - Rejects type changes with `-ESTALE`, preserves local mode under `dynperm`, updates delete-pending state, handles safe size updates, transfers symlink targets, and initializes new inodes.

- `cifs_unix_basic_to_fattr()`
  - Converts legacy `FILE_UNIX_BASIC_INFO` into Linux mode, dtype, device numbers, uid/gid, size, timestamps, unique id, and link count.

- `cifs_sfu_type()` / `cifs_sfu_mode()`
  - Interpret SFU/Services-for-Unix emulated special files and SETFILEBITS xattrs.
  - Recognize block/char devices, sockets, FIFOs, and SFU symlink payloads.

- `smb311_posix_info_to_fattr()` / `cifs_open_info_to_fattr()`
  - Convert SMB3 POSIX query data or standard SMB open/query information into `cifs_fattr`.
  - Account for timezone adjustment, readonly mode masking, reparse-point conversion, symlink targets, link counts, and POSIX SID-to-id mapping.

- `cifs_get_fattr()` / `smb311_posix_get_fattr()`
  - Fetch path metadata, handle DFS/junction cases, reparse points, backup-credential fallback, server inode numbers, ACL mode/ownership extraction, SFU/MF symlink tweaks, and readonly permission masking.

- `cifs_get_inode_info()` / `smb311_posix_get_inode_info()` / `cifs_get_inode_info_unix()`
  - Public inode metadata refresh paths for non-POSIX SMB, SMB3 POSIX extensions, and legacy Unix extensions.

- `cifs_iget()` / `cifs_root_iget()`
  - Find or allocate inodes with `iget5_locked()`, using unique id plus create time as identity.
  - Handle directory inode collisions, root prepaths, DFS junction root metadata, and IPC fake roots.

- `__cifs_unlink()` / `cifs_unlink()`
  - Implements file deletion with dentry unhashing, deferred-close flushing, POSIX delete fallback, standard unlink, SMB2 sillyrename behavior, pending-delete rename fallback, readonly attribute clearing, and parent/child cache invalidation.

- `cifs_mkdir()` / `cifs_mkdir_qinfo()` / `cifs_posix_mkdir()`
  - Create directories through SMB3 POSIX, legacy POSIX, or generic mkdir.
  - Query new inode information afterward and apply mode, setgid, dynperm, and setuid/setgid mount behavior.

- `cifs_rmdir()`
  - Removes directories, marks deleted inodes pending-delete, clears size/link count, and invalidates parent and child metadata.

- `cifs_rename2()` / `cifs_do_rename()`
  - Implements VFS rename with path-based SMB rename, legacy open-file rename fallback, target dentry unhashing, deferred-close handling, no-replace support, target unlink/rmdir fallback, and directory delete-pending updates.

- `cifs_dentry_needs_reval()`
  - Decides whether inode attributes must be refreshed based on delete-pending/tmpfile state, oplocks, lookup cache state, cached directory freshness, `acdirmax`/`acregmax`, and noserverino hardlinks.

- `cifs_revalidate_mapping()` / `cifs_zap_mapping()`
  - Serializes pagecache invalidation with `CIFS_INO_LOCK`.
  - Skips invalidation for swapfiles and `cache=singleclient`.

- `cifs_getattr()`
  - Implements stat/statx behavior, waits for dirty pages when size/times/blocks are requested, optionally forces sync, fills birth time and compressed/encrypted statx attributes, and adjusts ownership for multiuser mounts without Unix/ACL ownership.

- `cifs_fiemap()`
  - Flush-waits dirty data, finds a readable handle, and dispatches to dialect-specific fiemap support.

- `cifs_file_set_size()` / `cifs_setsize()`
  - Prefer handle-based EOF setting, fall back to path-based size setting, resize netfs/fscache/pagecache, and update local inode block estimates.

- `cifs_setattr_unix()` / `cifs_setattr_nounix()` / `cifs_setattr()`
  - Implement chmod/chown/chgrp/truncate/timestamp updates through legacy Unix info, ACL security descriptors, SMB3 POSIX ACL path, DOS readonly attributes, or generic file-info setting.
  - Avoids setting ctime/mtime on `ATTR_OPEN` and after ftruncate paths that would disable server automatic timestamp updates.

## Dependencies

- Uses CIFS core structures from `cifsglob.h`, mount state from `cifs_fs_sb.h` and `fs_context.h`, dialect operations from `cifsproto.h` and `smb2proto.h`, cached directory helpers, ACL helpers, reparse helpers, fscache, and netfs APIs.
- Relies heavily on `server->ops` indirection for dialect-specific open/query/setinfo/delete/rename/ACL/reparse/fiemap behavior.

## Notable Behaviors

- Inode identity is not just server file id; create time is also compared to reduce stale aliasing.
- Reparse points are treated conservatively. Unsupported name-surrogate directory reparse points can become junction automount placeholders.
- If a server returns unusable inode numbers, the mount can automatically switch away from `serverino`.
- Many paths mark `CIFS_I(inode)->time = 0` rather than immediately querying, forcing later revalidation.
- Delete and rename paths actively close deferred handles to avoid server-side sharing conflicts.
- ACL-enabled mounts may intentionally re-query after readdir so mode and ownership visible to `ls -l` are not stale or placeholder values.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/ioctl.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/ioctl.c

Read status: complete.

## Purpose

Implements CIFS/SMB file ioctl handling for filesystem flags, server-side copy, query-info passthrough, integrity/compression controls, snapshot enumeration, mount information, encryption key debug export, notifications, and forced shutdown.

## Main Responsibilities

- Dispatch `cifs_ioctl()` commands from VFS to CIFS/SMB-specific operations.
- Convert pathnames for query-info ioctl use.
- Support server-side copychunk from another CIFS file descriptor.
- Report mount, tree-connect, share, filesystem, and protocol information to userspace.
- Implement XFS-style going-down shutdown semantics for CIFS mounts.
- Export SMB3 encryption key material to privileged callers for debugging.
- Wire directory change-notification ioctls to dialect-specific notify operations.

## Important Functions

- `cifs_ioctl_query_info()`
  - Builds the dentry path, converts it to UTF-16, handles root path specially, and calls `server->ops->ioctl_query_info`.

- `cifs_ioctl_copychunk()`
  - Validates destination write mode and mount writability.
  - Validates that the source fd is also a CIFS file and not a directory.
  - Copies the full source size through `cifs_file_copychunk_range()`.

- `smb_mnt_get_tcon_info()`
  - Copies tree id and session id to userspace.

- `smb_mnt_get_fsinfo()`
  - Reports protocol id, tcon flags, device characteristics, filesystem attributes, volume serial/create time, share flags/capabilities, sector flags, optimal sector size, maximal access, chunk size, and CIFS POSIX capability bits.

- `cifs_shutdown()`
  - Requires `CAP_SYS_ADMIN`.
  - Accepts logflush/nologflush style shutdown flags and sets `CIFS_MOUNT_SHUTDOWN`.
  - Rejects unsupported default flush semantics.

- `cifs_dump_full_key()`
  - Validates encryption state and optional session id.
  - Finds a matching session when requested, sizes key output for AES-128 or AES-256 variants, and copies session, encryption, and decryption keys to userspace.

- `cifs_ioctl()`
  - Main command dispatcher.
  - Handles `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`, `CIFS_IOC_COPYCHUNK_FILE`, `CIFS_QUERY_INFO`, `CIFS_IOC_SET_INTEGRITY`, mount info ioctls, snapshot enumeration, key dumps, notifications, and shutdown.

## Dependencies

- Uses `cifs_ioctl.h` ioctl structures, dialect operations from `server->ops`, CIFS session/tcon state, SMB2/SMB3 encryption metadata, Linux fd helpers, mount write accounting, and userspace copy helpers.

## Notable Behaviors

- Compression is the only generic file flag set path currently implemented through `FS_IOC_SETFLAGS`.
- Legacy `CIFS_DUMP_KEY` only handles fixed AES-128-era key sizes; `CIFS_DUMP_FULL_KEY` handles variable key sizes.
- Key-dump ioctls are gated by `CAP_SYS_ADMIN`; shutdown is also privileged.
- Unsupported ioctls return `-ENOTTY`, matching existing ioctl precedent.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/link.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/link.c

Read status: complete.

## Purpose

Implements CIFS/SMB hardlink and symlink creation plus Minshall+French symlink parsing, formatting, querying, and creation helpers.

## Main Responsibilities

- Recognize MF symlink placeholder files by size and payload format.
- Parse MF symlink files and expose them as Linux symlinks.
- Create MF symlink placeholder files when that symlink mode is selected.
- Provide SMB1 and SMB2/3 MF symlink query/create operations.
- Implement hardlink creation through legacy Unix extensions or dialect-specific SMB operations.
- Implement symlink creation through legacy Unix symlinks, MF symlinks, SFU emulation, or native/NFS/WSL reparse symlinks.

## Important Functions

- `parse_mf_symlink()`
  - Validates fixed MF symlink file size.
  - Parses `XSym` length, validates target length, recomputes MD5 over the target, compares encoded digest, and optionally returns a copied target string.

- `format_mf_symlink()`
  - Builds the fixed-size MF symlink payload with length header, MD5 digest, target string, newline, and padding.

- `couldbe_mf_symlink()`
  - Fast screen for regular files whose EOF exactly matches MF symlink file size.

- `create_mf_symlink()`
  - Formats an MF symlink buffer and calls `server->ops->create_mf_symlink`.
  - Verifies the server wrote the full fixed-size payload.

- `check_mf_symlink()`
  - Reads and parses a possible MF symlink.
  - On success, rewrites `fattr` as a symlink with `0777`-style permission bits and transfers the target into `cf_symlink_target`.

- `cifs_query_mf_symlink()` / `cifs_create_mf_symlink()`
  - SMB1-specific open/read/write helpers for MF symlink files.

- `smb3_query_mf_symlink()` / `smb3_create_mf_symlink()`
  - SMB2/SMB3 variants using UTF-16 paths, `SMB2_open`, `SMB2_read`, `SMB2_write`, and `SMB2_close`.

- `cifs_hardlink()`
  - Creates hardlinks via legacy Unix extension or `server->ops->create_hardlink`.
  - Drops the target dentry to force fresh lookup.
  - Locally increments source nlink when creation succeeds and clears tmpfile state.

- `cifs_symlink()`
  - Selects symlink strategy from mount/server state.
  - Supports legacy Unix, MF symlink files, SFU node creation, and reparse-point symlinks.
  - Queries and instantiates the new inode after successful non-reparse symlink creation.

## Dependencies

- Uses crypto MD5 helper, CIFS path building, dialect open/read/write/close operations, SMB2 protocol helpers, reparse symlink creation, SFU node creation, and inode metadata refresh helpers from `inode.c`.

## Notable Behaviors

- Invalid MF payloads are treated as “not a symlink” rather than hard errors.
- MF symlink detection is intentionally size-gated before issuing expensive reads.
- SMB2/3 MF creation checks for short writes and maps them to traceable `-EIO`.
- Hardlink creation updates local nlink only for the source inode and still forces future revalidation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/link.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/misc.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/misc.c

Read status: complete.

## Purpose

Provides shared CIFS client utility routines for xid accounting, session/tcon allocation, SMB buffer pools, oplock and writer coordination, deferred close handling, delete-handle marking, DFS referral parsing, DFS superblock lookup, DFS helper checks, and reconnect waiting.

## Main Responsibilities

- Allocate/free core session and tree-connect objects.
- Allocate/release CIFS large and small SMB buffers from mempools.
- Maintain xid active counters used for tracing VFS requests.
- Set oplock/cache flags and coordinate writers with pending oplock breaks.
- Queue and complete oplock break work.
- Track backup-credential eligibility.
- Manage pending opens and deferred closes.
- Force-close deferred files globally, per-superblock, per-inode, or under a dentry.
- Mark open handles as deleted so close deferral is not used after unlink/rename.
- Parse DFS referral V3 responses into internal target arrays.
- Find CIFS superblocks associated with DFS tcons.
- Resolve and compare DFS target host IPs.
- Update DFS prepaths and detect special DFS-link error cases.
- Wait for reconnect completion under hard/soft mount semantics.

## Important Functions

- `_get_xid()` / `_free_xid()`
  - Increment/decrement global active xid counters and allocate monotonically increasing xid values.

- `sesInfoAlloc()` / `sesInfoFree()`
  - Initialize or release `struct cifs_ses`, including locks, lists, iface refs, NLS table, passwords, names, domain fields, and auth key material.

- `tcon_info_alloc()` / `tconInfoFree()`
  - Initialize or release `struct cifs_tcon`, including cached directory state, counters, locks, lists, stats timestamps, fscache lock, pending opens, query interface work, and DFS cache work.

- `cifs_buf_get()` / `cifs_buf_release()` / `cifs_small_buf_get()` / `cifs_small_buf_release()` / `free_rsp_buf()`
  - Manage large and small SMB request/response buffers and allocation counters.

- `cifs_autodisable_serverino()`
  - Clears `CIFS_MOUNT_SERVER_INUM`, records autodisable state, and emits warnings when server inode numbers are unreliable.

- `cifs_set_oplock_level()`
  - Maps protocol oplock level into CIFS read/write cache flags.

- `cifs_get_writer()` / `cifs_put_writer()`
  - Block writers while an oplock break is pending and wake oplock-break waiters when writers drain.

- `cifs_queue_oplock_break()` / `cifs_done_oplock_break()`
  - Reference the open file, queue break work, and clear/wake pending break state.

- `backup_cred()`
  - Checks backup uid/gid mount options against current credentials.

- `cifs_add_pending_open*()` / `cifs_del_pending_open()`
  - Track pending opens by lease key under tcon open-file locking.

- `cifs_is_deferred_close()` / `cifs_add_deferred_close()` / `cifs_del_deferred_close()`
  - Manage per-inode deferred close records under `deferred_lock`.

- `cifs_close_deferred_file()` / `cifs_close_all_deferred_files()` / `cifs_close_all_deferred_files_sb()` / `cifs_close_deferred_file_under_dentry()`
  - Cancel delayed close work and drop file refs immediately in several scopes.

- `cifs_mark_open_handles_for_deleted_file()`
  - Marks matching open handles deleted, comparing paths only when hardlinks require precision.

- `parse_dfs_referrals()`
  - Validates DFS referral response bounds, requires referral version 3, converts paths from UTF-16 or byte form, and fills `dfs_info3_param` entries.

- `extract_unc_hostname()` / `copy_path_name()`
  - Small path utility helpers for UNC host extraction and bounded path copying.

- `cifs_get_dfs_tcon_super()` / `cifs_put_tcp_super()`
  - Locate and hold/release an active superblock matching a DFS tcon’s origin path.

- `match_target_ip()` / `cifs_update_super_prepath()` / `cifs_inval_name_dfs_link_error()`
  - DFS upcall helpers for DNS target matching, prepath replacement, and probing whether `STATUS_OBJECT_NAME_INVALID` is actually a DFS link case.

- `cifs_wait_for_server_reconnect()`
  - Waits for reconnect state to clear, scaling timeout by target count and retrying only for hard-style behavior.

## Dependencies

- Uses CIFS core global counters, mempools, cached directory subsystem, DFS cache/upcall code when enabled, DNS resolution, SMB1/SMB2 protocol helpers, Linux superblock iteration, wait queues, delayed work, spinlocks, mutexes, and krefs.

## Notable Behaviors

- Deferred close cancellation builds a temporary list under locks, then drops file refs outside the main open-file lock.
- DFS referral parsing includes explicit response-size and offset-bound checks before string extraction.
- `cifs_close_all_deferred_files_sb()` takes temporary tcon references while walking the superblock tlink tree.
- Reconnect wait returns `-ERESTARTSYS` on signal and `-EHOSTDOWN` when a soft wait gives up.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/namespace.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/namespace.c

Read status: complete.

## Purpose

Implements CIFS namespace automount support for DFS referrals and SMB junction traversal.

## Main Responsibilities

- Maintain a list of CIFS automounts eligible for expiry.
- Build CIFS device names from referral UNC paths and optional prepaths.
- Construct full automount paths for ordinary and DFS-origin mounts.
- Duplicate and adjust filesystem context for submounts.
- Mount referred targets through `fc_mount()`.
- Register new automounts for expiry scheduling.

## Important Functions

- `cifs_expire_automounts()`
  - Marks CIFS automounts for expiry and reschedules delayed expiry work while the list is nonempty.

- `cifs_release_automount_timer()`
  - Cancels delayed expiry work, warning if automounts still remain.

- `cifs_build_devname()`
  - Normalizes a referral UNC into `//server/share[/prepath]`.
  - Trims leading/trailing delimiters, appends prepath when present, converts delimiters to `/`, and returns an allocated string.

- `is_dfs_mount()`
  - Checks whether the master tcon has an `origin_fullpath`, indicating a DFS-origin mount.

- `automount_fullpath()`
  - Builds the full automount source path from a dentry.
  - For DFS-origin mounts, prepends `tcon->origin_fullpath` to the raw dentry path.

- `fs_context_set_ids()`
  - Sets uid/gid/credential uid defaults from current credentials for multiuser automount contexts.

- `cifs_do_automount()`
  - Synchronizes session passwords, creates a submount fs context, builds the full path, duplicates current context, parses the new devname, derives source, sets DFS automount flags, and mounts.

- `cifs_d_automount()`
  - Public automount entry point.
  - Calls `cifs_do_automount()`, registers expiry, schedules expiry work, and returns the new mount.

- `cifs_namespace_inode_operations`
  - Empty inode operations table used for automount-marked namespace inodes.

## Dependencies

- Uses VFS fs context and submount APIs, CIFS mount context parsing/duplication helpers, session password synchronization, tcon origin paths, dentry path utilities, and mount expiry APIs.

## Notable Behaviors

- Root dentries are rejected as stale automount points.
- Automount context clears pointer-owned fields before duplication to avoid sharing mutable strings from the parent context.
- DFS automount state is propagated through `ctx->dfs_automount` and `ctx->dfs_conn`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/namespace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/netlink.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/netlink.c

Read status: complete.

## Purpose

Defines and registers the CIFS generic netlink family used for server witness notification support.

## Main Responsibilities

- Define generic netlink attribute validation policy for CIFS witness registration and notification data.
- Register the witness notification command.
- Define the witness multicast group.
- Provide module init/exit helpers for generic netlink family registration.

## Important Contents

- `cifs_genl_policy`
  - Attribute policy for SWN registration id, net/share names, IP sockaddr storage, notify flags, Kerberos auth flag, username/password/domain, notification type, resource state, and resource name.

- `cifs_genl_ops`
  - Registers `CIFS_GENL_CMD_SWN_NOTIFY` with admin permission and dispatches to `cifs_swn_notify`.

- `cifs_genl_mcgrps`
  - Defines the `CIFS_GENL_MCGRP_SWN` multicast group with `GENL_MCAST_CAP_NET_ADMIN`.

- `cifs_genl_family`
  - Generic netlink family object using `CIFS_GENL_NAME`, `CIFS_GENL_VERSION`, policy, ops, and multicast group.

- `cifs_genl_init()` / `cifs_genl_exit()`
  - Register and unregister the family, logging VFS errors on failure.

## Dependencies

- Uses Linux generic netlink, UAPI CIFS netlink definitions, CIFS debug logging, CIFS global state, and witness notification code from `cifs_swn.h`.

## Notable Behaviors

- Notification command requires administrative permission.
- String attributes use netlink string policy; IP uses fixed `sockaddr_storage` length.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/netlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/netlink.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/netlink.h

Read status: complete.

## Purpose

Declares the CIFS generic netlink family and its lifecycle functions.

## Main Contents

- Include guard `_CIFS_NETLINK_H`.
- `extern struct genl_family cifs_genl_family`.
- `int cifs_genl_init(void);`
- `void cifs_genl_exit(void);`

## Dependencies

- Intended for CIFS client code that needs access to the generic netlink family or registration helpers.

## Role in the Subsystem

This is the small public internal header for `netlink.c`, separating CIFS netlink registration declarations from the implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/netlink.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/netmisc.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/netmisc.c

Read status: complete.

## Purpose

Provides small network and time-conversion helpers used by CIFS/SMB protocol code.

## Main Responsibilities

- Parse textual IPv4 and IPv6 addresses into socket address structures.
- Set network ports in IPv4 or IPv6 socket addresses.
- Convert between NT time and Unix `timespec64`.
- Convert DOS date/time fields into Unix `timespec64`.

## Important Functions

- `cifs_inet_pton()`
  - Internal wrapper around `in4_pton()` and `in6_pton()`.
  - Stops parsing on `\` to support UNC-style address substrings.

- `cifs_convert_address()`
  - Tries IPv4 first, then IPv6.
  - Handles IPv6 `%scope_id` suffixes when numeric.
  - Sets the socket family on success and returns 1/0 for success/failure.

- `cifs_set_port()`
  - Sets `sin_port` or `sin6_port` depending on address family.

- `cifs_NTtimeToUnix()`
  - Converts NT UTC time, based on 1601-01-01 in 100 ns units, to Unix seconds/nanoseconds.
  - Handles negative converted times without relying on signed 64-bit division on 32-bit architectures.

- `cifs_UnixTimeToNT()`
  - Converts Unix `timespec64` to NT UTC 100 ns units.

- `cnvrtDosUnixTm()`
  - Converts SMB/DOS packed date and time fields to Unix time with a supplied offset.
  - Validates/clamps basic date fields and accounts for DOS date range leap-year behavior.

## Dependencies

- Uses kernel IP parsing helpers, endian helpers, CIFS debug logging, SMB date/time wire structures, and NT status/error headers.

## Notable Behaviors

- IPv6 scope ids longer than 12 bytes or nonnumeric scope ids are rejected.
- DOS conversion treats invalid day/month values as log-worthy but clamps them rather than failing.
- NT time conversion leaves timezone adjustment to callers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/netmisc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/nterr.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/nterr.h

Read status: complete.

## Purpose

Defines NTSTATUS and selected Win32 error constants used by CIFS/SMB error mapping and protocol handling.

## Main Contents

- Include guard `_NTERR_H`.
- `struct ntstatus_to_dos_err`
  - Maps an NT status to DOS error class/code and a string name.
- Win32 error constants:
  - `NT_ERROR_INVALID_PARAMETER`
  - `NT_ERROR_INSUFFICIENT_BUFFER`
  - `NT_ERROR_INVALID_DATATYPE`
- Large `NT_STATUS_*` constant set.
  - Includes success/pending statuses, informational statuses, warnings, and many `0xC0000000` failure statuses.
  - Covers object/path errors, access errors, pipe errors, network errors, domain/logon errors, DFS/path-not-covered errors, reparse/encryption statuses, and SMB/auth-related statuses.
- Per-constant comments encode DOS error class/code mapping data used to generate `smb1_mapping_table.c`.

## Important Groups

- General operation:
  - `NT_STATUS_OK`, `NT_STATUS_PENDING`, `NT_STATUS_MORE_ENTRIES`, `NT_STATUS_BUFFER_OVERFLOW`, `NT_STATUS_NO_MORE_ENTRIES`.

- File/path/object:
  - `NT_STATUS_NO_SUCH_FILE`, `NT_STATUS_OBJECT_NAME_NOT_FOUND`, `NT_STATUS_OBJECT_NAME_COLLISION`, `NT_STATUS_OBJECT_PATH_NOT_FOUND`, `NT_STATUS_DELETE_PENDING`, `NT_STATUS_DIRECTORY_NOT_EMPTY`, `NT_STATUS_NOT_A_DIRECTORY`, `NT_STATUS_NAME_TOO_LONG`.

- Access/security:
  - `NT_STATUS_ACCESS_DENIED`, `NT_STATUS_PRIVILEGE_NOT_HELD`, `NT_STATUS_INVALID_OWNER`, `NT_STATUS_INVALID_SID`, `NT_STATUS_INVALID_SECURITY_DESCR`, `NT_STATUS_LOGON_FAILURE`, `NT_STATUS_ACCOUNT_DISABLED`, `NT_STATUS_ACCOUNT_LOCKED_OUT`.

- Locking/sharing/oplocks:
  - `NT_STATUS_SHARING_VIOLATION`, `NT_STATUS_FILE_LOCK_CONFLICT`, `NT_STATUS_LOCK_NOT_GRANTED`, `NT_STATUS_OPLOCK_NOT_GRANTED`, `NT_STATUS_INVALID_OPLOCK_PROTOCOL`.

- Network/share/session:
  - `NT_STATUS_BAD_NETWORK_PATH`, `NT_STATUS_NETWORK_BUSY`, `NT_STATUS_BAD_NETWORK_NAME`, `NT_STATUS_NETWORK_NAME_DELETED`, `NT_STATUS_CONNECTION_DISCONNECTED`, `NT_STATUS_NETWORK_SESSION_EXPIRED`.

- DFS/reparse/encryption:
  - `NT_STATUS_PATH_NOT_COVERED`, `NT_STATUS_NOT_A_REPARSE_POINT`, `NT_STATUS_DIRECTORY_IS_A_REPARSE_POINT`, `NT_STATUS_ENCRYPTION_FAILED`, `NT_STATUS_DECRYPTION_FAILED`.

- SMB/auth negotiation:
  - `NT_STATUS_MORE_PROCESSING_REQUIRED`, `NT_STATUS_NO_USER_SESSION_KEY`, `NT_STATUS_NO_PREAUTH_INTEGRITY_HASH_OVERLAP`.

## Dependencies

- Uses fixed-width kernel integer types.
- Consumed by CIFS error mapping code and protocol handlers that compare raw NTSTATUS values.

## Notable Behaviors

- This header is data definition only; it contains no executable logic.
- Comments are part of the build/data-generation contract for SMB1 NTSTATUS-to-DOS mapping.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/nterr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/ntlmssp.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/ntlmssp.h

Read status: complete.

## Purpose

Defines NTLMSSP constants, wire-format message structures, AV-pair identifiers, version layout, and authentication blob helper prototypes for CIFS NTLM/NTLMSSP authentication.

## Main Contents

- NTLMSSP signature and message type constants:
  - Negotiate, Challenge, Authenticate, and Unknown.
- NTLMSSP negotiate flag definitions:
  - Unicode/OEM, target request/type, signing/sealing, NTLM, anonymous, supplied domain/workstation, extended security, target info, version, 128-bit, key exchange, and 56-bit support.
- `enum av_field_type`
  - Defines NTLMSSP target-info AV pair ids such as NetBIOS names, DNS names, flags, timestamp, target name, and channel bindings.
- `SECURITY_BUFFER`
  - Packed length/maximum-length/offset descriptor used in NTLMSSP messages.
- `NEGOTIATE_MESSAGE`
  - Legacy negotiate layout without version block.
- `struct ntlmssp_version`
  - MS-NLMP version field with product version, module build, reserved bytes, and NTLM revision.
- `struct negotiate_message`
  - SMB2+ negotiate layout including version.
- `CHALLENGE_MESSAGE`
  - Server challenge layout with target name, negotiate flags, challenge bytes, reserved field, and target-info array.
- `AUTHENTICATE_MESSAGE`
  - Client authenticate layout with LM/NT challenge responses, domain, user, workstation, session key, flags, version, and trailing payload.
- Function prototypes:
  - `decode_ntlmssp_challenge()`
  - `build_ntlmssp_negotiate_blob()`
  - `build_ntlmssp_smb3_negotiate_blob()`
  - `build_ntlmssp_auth_blob()`

## Dependencies

- Uses CIFS crypto key size constants and CIFS session/server structures from surrounding CIFS headers.
- Implemented by NTLMSSP authentication code elsewhere in the SMB client.

## Notable Behaviors

- Structures are packed to match wire format.
- Typedefs are intentionally used here to mirror NTLMSSP standards terminology.
- SMB2+ negotiate messages can include the NTLMSSP version block while the legacy negotiate typedef omits it.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/ntlmssp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/readdir.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/readdir.c

Read status: complete.

## Purpose

Implements CIFS/SMB directory enumeration, find-first/find-next search state, directory-entry metadata conversion, dcache priming, resume positioning, and cached directory entry emission.

## Main Responsibilities

- Start and continue directory searches at the right SMB information level for Unix extensions, SMB3 POSIX extensions, legacy standard info, server inode mode, or full directory info.
- Convert directory search entries into Linux names, inode numbers, dtypes, and `cifs_fattr`.
- Skip `.` and `..` entries returned by servers after VFS dot emission.
- Maintain resume keys/names for find-next operations.
- Restart directory searches when seeking backward or when directory metadata changed.
- Prime the dcache from readdir results when safe.
- Support cached directory handles and cached dirent replay.
- Mark entries needing full revalidation when readdir data is incomplete for ACLs, reparse points, MF symlinks, or special files.

## Important Functions

- `cifs_prime_dcache()`
  - Looks up or allocates child dentries from readdir results.
  - Updates matching inodes in place when unique id and type are stable.
  - Avoids priming entries that immediately need revalidation.
  - Handles reparse-point metadata carefully to avoid clobbering known symlink/device/ownership data with incomplete query-dir data.

- `cifs_fill_common_info()`
  - Applies mount uid/gid, directory/file mode defaults, dtype, readonly masking, unknown-nlink marking, ACL revalidation flags, SFU FIFO handling, and reparse-point conversion.

- `cifs_posix_to_fattr()`
  - Converts `SMB_FIND_FILE_POSIX_INFO` entries to `cifs_fattr`.
  - Parses POSIX owner/group SIDs, mode, inode, size, allocation, nlink, DOS attrs, reparse tag, and special-file revalidation needs.

- `cifs_dir_info_to_fattr()` / `cifs_fulldir_info_to_fattr()` / `cifs_std_info_to_fattr()`
  - Convert the different SMB directory info response formats into common `cifs_fattr`.

- `_initiate_cifs_search()` / `initiate_cifs_search()`
  - Allocate `struct cifsFileInfo` for directory state when needed.
  - Choose info level and search flags.
  - Call `server->ops->query_dir_first`.
  - Retry briefly on `-EDEADLK` credit shortage and disable `serverino` if unsupported.

- `cifs_unicode_bytelen()` / `nxt_dir_entry()`
  - Determine Unicode filename byte length and advance between variable-sized search entries with bounds checks.

- `cifs_fill_dirent*()` / `cifs_fill_dirent()`
  - Extract name pointer, name length, resume key, and inode number from each supported directory info format.

- `cifs_entry_is_dot()`
  - Detects `.` and `..` in Unicode or byte names.

- `is_dir_changed()` / `cifs_save_resume_key()`
  - Detect directory invalidation and store resume state from the current entry.

- `find_cifs_entry()`
  - Locates the directory entry corresponding to `ctx->pos`.
  - Rewinds and restarts searches when necessary, issues find-next calls until the target buffer is reached, and scans within the current SMB response.

- `emit_cached_dirents()` / `add_cached_dirent()` / `cifs_dir_emit()`
  - Replay or populate cached dirent lists for cached directory handles.
  - Track entry count and byte accounting per tcon and globally.

- `cifs_filldir()`
  - Converts a single network entry to a VFS dirent.
  - Handles UTF-16 conversion, fattr conversion, inode-number selection, MF symlink revalidation marking, dcache priming, and dirent emission.

- `cifs_readdir()`
  - Main VFS readdir implementation.
  - Builds path, attempts cached directory replay, starts search when needed, emits dots, finds current entry, opens cache for population, loops through entries, updates `ctx->pos`, resume key, and cache accounting.

## Dependencies

- Uses CIFS search state in `struct cifsFileInfo`, dialect `query_dir_first/query_dir_next/close_dir/calc_smb_size` operations, cached directory subsystem, inode/fattr helpers from `inode.c`, SID-to-id and POSIX info parsing helpers, Unicode conversion, reparse helpers, and VFS `dir_context`.

## Notable Behaviors

- Readdir deliberately marks some entries for later stat revalidation because query-dir responses do not carry enough ACL, special-file, symlink, or reparse detail.
- Dot entries from the server are suppressed because VFS emits dots first.
- Search buffer traversal has explicit overflow and end-of-SMB checks.
- Cached dirents preserve original logical positions so lseek/readdir replay can maintain expected `ctx->pos` behavior even when skipped dot entries create holes.
- If a returned inode number is absent while `serverino` is requested, the code generates one and may autodisable server inode numbers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/readdir.c -->