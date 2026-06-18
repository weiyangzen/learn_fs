# subset-b-005756 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/inode.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/inode.c

## Purpose
`inode.c` is the CIFS/SMB client's core VFS inode implementation. It translates SMB1 Unix extensions, SMB2/3 file information, SMB 3.1.1 POSIX information, reparse-point data, SFU emulation files, and mount options into Linux `struct inode` state. It also implements the high-risk inode-facing operations for lookup-derived metadata, root inode creation, unlink, mkdir, rmdir, rename, setattr, getattr, fiemap, truncation, cache revalidation, and page-cache invalidation.

## Important APIs, types, and functions
The central data carrier is `struct cifs_fattr`, which is filled by `cifs_unix_basic_to_fattr()`, `cifs_open_info_to_fattr()`, `smb311_posix_info_to_fattr()`, `cifs_get_fattr()`, and `smb311_posix_get_fattr()`, then committed by `cifs_fattr_to_inode()`. `cifs_set_ops()` selects inode/file/address-space operations from file type and mount flags, including direct I/O, strict cache, no byte-range lock variants, directory automount operations, and symlink operations. `cifs_iget()` uses `iget5_locked()` with `cifs_find_inode()` and `cifs_init_inode()` to map server IDs plus create time to Linux inodes and disables server inode numbers on problematic directory alias collisions. `cifs_root_iget()` builds the root path, handles prefix paths, and falls back among Unix, POSIX, and standard metadata paths.

Mutation entry points include `cifs_unlink()`, `cifs_mkdir()`, `cifs_rmdir()`, `cifs_rename2()`, `cifs_setattr()`, and `cifs_file_set_size()`. Revalidation entry points include `cifs_revalidate_file_attr()`, `cifs_revalidate_dentry_attr()`, `cifs_revalidate_file()`, `cifs_revalidate_dentry()`, `cifs_getattr()`, `cifs_revalidate_mapping()`, and `cifs_zap_mapping()`. Server behavior is abstracted through `struct TCP_Server_Info->ops` calls such as `query_path_info`, `query_file_info`, `get_srv_inum`, `open`, `unlink`, `mkdir`, `rmdir`, `rename`, `set_file_info`, `set_file_size`, `set_path_size`, `fiemap`, and reparse/symlink helpers.

## Control flow
The metadata path starts with a query against the active tree connection, converts wire metadata into `cifs_fattr`, adjusts it for mount options and server quirks, resolves or generates a unique inode number, then updates or instantiates the inode. Reparse points branch through `reparse_info_to_fattr()`, which may query a reparse buffer, parse special file types, convert unsupported name-surrogate directory reparses to junction fattrs, and defer unsupported tags to server-side open handling. Legacy Unix and SMB 3.1.1 POSIX paths bypass parts of the non-Unix mode/ACL synthesis.

Unlink unhashes the target dentry before network deletion, waits for outstanding netfs I/O, cancels deferred closes under the dentry, optionally performs POSIX delete, then uses dialect unlink or a silly-rename/delete-on-close fallback for busy files. Rename first tries server rename, retries after closing deferred files on access denial, optionally unlinks an existing target for POSIX replacement semantics, and repairs dcache state with `d_move()` or `d_rehash()`. Setattr flushes dirty data for size/time-sensitive changes, uses handle-based operations when possible to avoid oplock disruption, falls back to path-based size and metadata setting, and updates local inode/netfs/fscache state after success.

## State and persistence behavior
Persistent state is remote: file metadata, DOS attributes, reparse tags, object identity, link count, allocation size, and ACL-derived mode are stored on the SMB server. Local state lives in `struct cifsInodeInfo`: server `uniqueid`, `createtime`, `cifsAttrs`, `reparse_tag`, cached symlink target, oplock flags, attribute-cache timestamp `time`, delete-pending/tmpfile flags, netfs remote size, and invalid-mapping bits. The file toggles `CIFS_INO_INVALID_MAPPING`, `CIFS_INO_DELETE_PENDING`, `CIFS_MOUNT_SERVER_INUM`, and related state to preserve coherency. Attribute caching is governed by `acregmax`, `acdirmax`, lookup-cache enablement, oplocks, cached directory leases, hardlink status, and explicit forced-sync stat requests.

## Dependencies and integration points
This file depends on VFS inode/dentry APIs, netfs, fscache, address-space operations, CIFS mount context, DFS/reparse helpers, ACL SID mapping, SMB dialect operations, cached directory support, and legacy SMB1 Unix extension functions when enabled. It is directly consumed by CIFS inode/file/dir operation tables and indirectly by readdir, link, ioctl, and namespace paths that expect coherent inode attributes and cache invalidation.

## Risks
Key risks are stale inode aliases when server inode numbers collide, incorrect file type conversion for reparse/SFU/MF symlink cases, data loss or stale reads if page-cache invalidation is skipped incorrectly, races between unlink/rename and deferred open handles, improper restoration of DOS readonly/hidden attributes after fallback deletion, and subtle behavior differences among SMB1 Unix extensions, SMB3 POSIX extensions, Windows servers, Samba, ksmbd, DFS targets, and multiuser mounts.

## Test signals
Exercise lookup/stat across Unix, SMB3 POSIX, and non-Unix mounts; root mounts with prefix paths; reparse-point symlink, junction, WSL/LX, NFS, and unsupported tags; MF and SFU symlink/special file detection; unlink of open files, readonly files, hardlinked files, and delete-pending files; rename with existing file/dir targets and `RENAME_NOREPLACE`; setattr size/mode/uid/gid/time through open handles and path fallback; statx force/dont sync; fiemap with and without readable handles; DFS referrals that force fake junction fattrs; and cache invalidation after external server-side changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/ioctl.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/ioctl.c

## Purpose
`ioctl.c` implements the CIFS/SMB VFS ioctl dispatcher. It exposes file and mount controls to userspace: Linux file flags, server-side copy, metadata query passthrough, compression and integrity toggles, mount/share information, snapshot enumeration, SMB3 encryption-key debug dumps, directory change notification, and forced mount shutdown.

## Important APIs, types, and functions
The exported entry point is `cifs_ioctl()`. Helpers include `cifs_ioctl_query_info()` for `CIFS_QUERY_INFO`, `cifs_ioctl_copychunk()` for `CIFS_IOC_COPYCHUNK_FILE`, `smb_mnt_get_tcon_info()`, `smb_mnt_get_fsinfo()`, `cifs_shutdown()`, and `cifs_dump_full_key()`. It uses user ABI structures from `cifs_ioctl.h`, including `smb_mnt_tcon_info`, `smb_mnt_fs_info`, `smb3_key_debug_info`, and `smb3_full_key_debug_info`.

## Control flow
`cifs_ioctl()` allocates an xid, traces the command, branches by ioctl number, derives `cifs_tcon` either from `filep->private_data` or from `cifs_sb_tlink()`, calls the appropriate dialect operation in `server->ops`, copies data to or from userspace, then releases tlinks and xid. Copychunk validates that the destination is writable, obtains mount write access, resolves the source fd, verifies it is also a CIFS file, rejects directory sources, and calls `cifs_file_copychunk_range()`. Query-info builds the dentry path, converts it to UTF-16 for non-root paths, and delegates to `ioctl_query_info`. Shutdown requires `CAP_SYS_ADMIN`, accepts only XFS-style logflush/nologflush flags that CIFS can honor, and marks the superblock with `CIFS_MOUNT_SHUTDOWN`.

## State and persistence behavior
Most commands mutate server state or expose mounted share state. `FS_IOC_SETFLAGS` currently only sets compression when requested and supported. `CIFS_IOC_SET_INTEGRITY` delegates integrity state to the server. `CIFS_IOC_SHUTDOWN` persists locally in the mount flags and blocks later operations through the forced-shutdown checks used elsewhere. Key-dump ioctls copy sensitive session/encryption keys from `struct cifs_ses`; no server state is changed, but the userspace ABI receives raw key material.

## Dependencies and integration points
The file integrates with VFS ioctl dispatch, fd lookup helpers, mount write protection, tracepoints, CIFS tlink/session/server state, SMB2/3 encryption constants, user-copy APIs, and dialect-specific `server->ops` methods for query info, compression, integrity, snapshots, notify, and key sizes. It also imports `<linux/btrfs.h>` for ioctl flag definitions.

## Risks
The highest security-sensitive area is key dumping. The legacy dump and full-key dump both require `CAP_SYS_ADMIN`, and the full-key path verifies encryption is required and validates user buffer length, but any ABI or bounds mistake would expose secrets or corrupt userspace. Other risks are use of stale `filep->private_data`, incorrectly accepting a non-CIFS source fd for copychunk, partial user copies, unsupported server operations returning ambiguous errors, and shutdown semantics that intentionally do not flush cached data for the default flag.

## Test signals
Test each ioctl with null private data where allowed, unsupported server ops, invalid userspace pointers, short key buffers, admin and non-admin callers, encrypted and unencrypted sessions, AES-128 and AES-256 ciphers, copychunk across same/different filesystems, directory notify on files versus directories, snapshot enumeration with null arg, and shutdown flags `DEFAULT`, `LOGFLUSH`, `NOLOGFLUSH`, and invalid values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/link.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/link.c

## Purpose
`link.c` implements hardlink creation and symbolic-link support for the SMB client. It handles Minshall+French symlink files, SMB1 Unix symlinks, SFU emulated symlinks, native/NFS/WSL reparse symlinks, and dialect-specific query/create routines for MF symlink payloads.

## Important APIs, types, and functions
MF symlink helpers are `parse_mf_symlink()`, `format_mf_symlink()`, `couldbe_mf_symlink()`, `create_mf_symlink()`, `check_mf_symlink()`, `cifs_query_mf_symlink()`, `cifs_create_mf_symlink()`, `smb3_query_mf_symlink()`, and `smb3_create_mf_symlink()`. VFS operations are `cifs_hardlink()` and `cifs_symlink()`. MF symlinks use a fixed 1067-byte regular-file format with an `XSym` header, decimal link length, MD5 digest, target string, newline, and padding.

## Control flow
MF parsing first verifies exact file size, scans link length, rejects overlong targets, recomputes the MD5 over the target bytes, compares the formatted digest, and optionally duplicates the target. MF creation builds the fixed payload and delegates to `server->ops->create_mf_symlink()`, validating a full-size write. SMB1 and SMB2/3 MF query/create wrappers open the file, check `EndOfFile`, read or write the fixed payload, and close the handle. Hardlink creation builds source and destination paths, chooses Unix hardlink when legacy Unix extensions are active, otherwise calls `server->ops->create_hardlink()`, drops the target dentry for relookup, and locally increments source nlink if successful. Symlink creation selects the strategy from `cifs_symlink_type()`, then instantiates the new inode by querying POSIX, Unix, or standard metadata.

## State and persistence behavior
Hardlinks and symlinks persist on the SMB server. Local inode state is adjusted only after successful server operations: hardlink clears tmpfile state, increments local nlink under `i_lock`, and invalidates source attribute time; symlink queries the server-created object before `d_instantiate()`. MF symlink detection modifies `cifs_fattr` by converting a regular 1067-byte file into a Linux symlink with target length and target string.

## Dependencies and integration points
This file depends on CIFS path construction, server operation vectors, SMB1/SMB2 open/read/write/close helpers, MD5 crypto, reparse symlink creation, SFU node creation, inode metadata routines in `inode.c`, local NLS/remapping, and mount flags such as `CIFS_MOUNT_MF_SYMLINKS` and `CIFS_MOUNT_UNX_EMUL`.

## Risks
MF symlink handling relies on exact wire-format validation; weak MD5 is used only for legacy format integrity, but malformed payloads must not be accepted as symlinks. Symlink behavior varies sharply by mount option and server capability. Hardlink local nlink updates can be stale when servers mis-handle ctime/nlink or when cached oplocks hide server-side changes. Reparse symlink creation must preserve target type and path escaping semantics.

## Test signals
Create and read symlinks under Unix extensions, MF symlink mode, SFU emulation, native reparse, NFS, and WSL modes. Verify malformed MF size, length, digest, overlong target, and short read are rejected. Test hardlink creation with cached source inode, unsupported server hardlink op, Unix and non-Unix servers, DFS paths, tmpfile source flags, and target dentry relookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/misc.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/misc.c

## Purpose
`misc.c` is a broad utility module for CIFS client lifetime, buffer, oplock, deferred-close, DFS, superblock, path, and reconnect support. It supplies small but central helpers used by almost every SMB client subsystem.

## Important APIs, types, and functions
Request accounting is handled by `_get_xid()` and `_free_xid()`. Session and tree-connect lifetime helpers are `sesInfoAlloc()`, `sesInfoFree()`, `tcon_info_alloc()`, and `tconInfoFree()`. Buffer helpers include `cifs_buf_get()`, `cifs_buf_release()`, `cifs_small_buf_get()`, `cifs_small_buf_release()`, and `free_rsp_buf()`. Cache/coherency helpers include `cifs_autodisable_serverino()`, `cifs_set_oplock_level()`, `cifs_get_writer()`, `cifs_put_writer()`, `cifs_queue_oplock_break()`, and `cifs_done_oplock_break()`. Deferred-close helpers include `cifs_add_deferred_close()`, `cifs_del_deferred_close()`, `cifs_close_deferred_file()`, `cifs_close_all_deferred_files()`, `cifs_close_all_deferred_files_sb()`, `cifs_close_deferred_file_under_dentry()`, and `cifs_mark_open_handles_for_deleted_file()`. DFS and path helpers include `parse_dfs_referrals()`, `extract_unc_hostname()`, `copy_path_name()`, `cifs_get_dfs_tcon_super()`, `cifs_update_super_prepath()`, `cifs_inval_name_dfs_link_error()`, and `cifs_wait_for_server_reconnect()`.

## Control flow
Allocation helpers initialize locks, lists, counters, delayed work, cached directory state, DFS work, and trace references. Deferred-close cancellation scans open-file lists under the relevant spinlocks, removes pending deferred-close records under inode deferred locks, collects file references in temporary lists, then drops references outside the spinlocked scan. DFS referral parsing validates response size, referral count, version 3 entries, and UTF-16 string bounds before allocating `dfs_info3_param` nodes and duplicating path/target strings. Reconnect waiting checks `tcpStatus`, scales timeout by target count, waits on `response_q`, and either returns once reconnect ends or fails on signal/soft timeout.

## State and persistence behavior
Most state is local kernel state: global xid counters, allocation counters, session/tcon reference counts, cached directory pools, open/deferred file lists, oplock flags, pending open lists, superblock activity references, DFS prepath, and server reconnect status. DFS referrals describe remote namespace state but are parsed into caller-owned temporary arrays. `cifs_autodisable_serverino()` permanently clears `CIFS_MOUNT_SERVER_INUM` for the mount when server IDs prove unsafe.

## Dependencies and integration points
The file integrates with mempools, workqueues, spinlocks, mutexes, tracepoints, NLS conversion, DFS cache/upcall code, DNS resolution, cached directory support, SMB1/SMB2 protocol helpers, tlink/superblock iteration, and CIFS mount contexts. Many inode, readdir, rename, unlink, reconnect, failover, and oplock paths call these helpers.

## Risks
The riskiest areas are lock ordering around open-file and deferred-close lists, correct refcounting while dropping deferred files, buffer lifetime with SMB response buffers, DFS referral bounds validation, server-inode autodisable changing hardlink semantics for a whole mount, and reconnect waits that must not hang soft mounts or ignore fatal signals. Secret fields such as passwords and auth keys are freed with sensitive-free helpers and must remain that way.

## Test signals
Stress open/close with deferred close enabled, unlink/rename during deferred close, oplock break while writers are pending, allocation/free counter balance, DFS referral parsing with malformed sizes/offsets/versions/Unicode lengths, DFS failover superblock matching, prepath updates, reconnect waiting on hard and soft mounts, backup credential detection, and deletion marking for hardlinked open files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/namespace.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/namespace.c

## Purpose
`namespace.c` implements CIFS automount support for SMB junctions and DFS referrals. It converts a dentry that represents a remote namespace transition into a new submount with an updated device name and filesystem context, then schedules mount expiry for idle automounts.

## Important APIs, types, and functions
The exported helpers are `cifs_build_devname()`, `cifs_release_automount_timer()`, `cifs_d_automount()`, and the `cifs_namespace_inode_operations` table used by automount inodes. Internal helpers include `cifs_expire_automounts()`, `is_dfs_mount()`, `automount_fullpath()`, `fs_context_set_ids()`, and `cifs_do_automount()`.

## Control flow
`cifs_d_automount()` delegates to `cifs_do_automount()`, then attaches the resulting mount to `cifs_automount_list` and schedules delayed expiry. `cifs_do_automount()` rejects root automounts, synchronizes passwords from the root session into the mountpoint superblock context, creates a submount fs context, computes the full automount path either from the dentry path or `tcon->origin_fullpath`, duplicates the current SMB3 context with current user IDs for multiuser cases, parses the new device name, builds the final `source`, marks DFS automount/connection flags, and calls `fc_mount()`.

## State and persistence behavior
Automounts are VFS mounts stored locally and marked for expiry through `cifs_automount_list`; they are not persistent server-side state. The generated fs context carries UNC, prepath, credentials, source, DFS state, and mount options into the submount. Password synchronization prevents redundant retry/password swapping during DFS automounts.

## Dependencies and integration points
This file depends on VFS mount/fs-context APIs, CIFS mount contexts, dentry path building, DFS origin tracking via `tcon->origin_fullpath`, session password synchronization, and the inode operations chosen in `inode.c` for `S_AUTOMOUNT` directories.

## Risks
Risks include malformed referral UNC/prepath handling, buffer underflow/overflow when prefixing `origin_fullpath` into a raw dentry path, stale password context during multiuser automounts, failure to cancel the expiry work while automounts remain, and incorrect DFS flags causing either missed failover behavior or unnecessary DFS connection handling.

## Test signals
Test DFS and non-DFS junction automounts, root dentry rejection, trailing and leading delimiter normalization in `cifs_build_devname()`, prefix-path mounts, `origin_fullpath` automount paths, multiuser uid/gid/cruid inheritance, password rotation before automount, failed `smb3_parse_devname()`, and expiry scheduling/release with active and empty automount lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/namespace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/netlink.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/netlink.c

## Purpose
`netlink.c` registers the CIFS generic netlink family used for server witness notification (SWN) integration. It defines accepted attributes, the command dispatcher, multicast groups, and module init/exit hooks for netlink registration.

## Important APIs, types, and functions
The core object is the global `struct genl_family cifs_genl_family`. `cifs_genl_policy` validates attributes such as registration id, network/share/resource names, IP sockaddr storage, notification flags, Kerberos auth flag, username/password/domain, notification type, and resource state. `cifs_genl_ops` maps `CIFS_GENL_CMD_SWN_NOTIFY` to `cifs_swn_notify()`. `cifs_genl_mcgrps` defines the SWN multicast group. Exported lifecycle functions are `cifs_genl_init()` and `cifs_genl_exit()`.

## Control flow
Module initialization calls `genl_register_family()`, logs on failure, and returns the kernel error code. Exit calls `genl_unregister_family()` and logs failures. At runtime, generic netlink validates incoming SWN notify messages against the policy and invokes `cifs_swn_notify()`.

## State and persistence behavior
The persistent local state is generic netlink registration in the kernel and multicast group membership managed by netlink. The file itself stores no per-message state. SWN registration state is maintained by the witness subsystem reached through `cifs_swn_notify()`.

## Dependencies and integration points
It depends on `<net/genetlink.h>`, UAPI definitions in `uapi/linux/cifs/cifs_netlink.h`, `cifs_swn.h`, and CIFS debug logging. It integrates with module load/unload and the witness notification subsystem.

## Risks
Risks are ABI compatibility of policy definitions, accepting unvalidated or underspecified string lengths due to non-strict validation flags, correct sockaddr length handling, registration failure on module init, and multicast group naming/version mismatch with userspace witness clients.

## Test signals
Test family registration/unregistration, duplicate registration failure paths, malformed SWN messages, missing required attributes as interpreted by `cifs_swn_notify()`, oversized strings, invalid sockaddr lengths, multicast group discovery from userspace, and notify behavior across module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/netlink.h -->
# sources/distributed-fs/ceph-client/fs/smb/client/netlink.h

## Purpose
`netlink.h` is the small internal declaration header for CIFS generic netlink support. It exposes the registered family and lifecycle functions to the rest of the SMB client module.

## Important APIs, types, and functions
The header declares `extern struct genl_family cifs_genl_family`, `int cifs_genl_init(void)`, and `void cifs_genl_exit(void)`. It uses a normal `_CIFS_NETLINK_H` include guard.

## Control flow
There is no runtime control flow in the header. It enables other compilation units to call the registration and unregistration functions implemented in `netlink.c` and to refer to the family object when needed.

## State and persistence behavior
No state is stored here. The declared family is defined in `netlink.c` and registered with generic netlink at module lifecycle boundaries.

## Dependencies and integration points
The header assumes `struct genl_family` is visible where included or through prior includes. It is integrated with CIFS module initialization and witness notification code.

## Risks
Risks are limited to declaration drift: if the family object or lifecycle signatures change in `netlink.c`, this header must change in lockstep. Include-order assumptions around `struct genl_family` should be watched if new users include it without generic netlink headers.

## Test signals
Build coverage is the main signal: compile all configurations that enable CIFS netlink/SWN support and ensure module init/exit users link against these declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/netmisc.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/netmisc.c

## Purpose
`netmisc.c` provides low-level network address conversion and SMB/NT time conversion helpers. These routines are shared by mount parsing, network connection setup, directory metadata conversion, and SMB1/SMB2 timestamp handling.

## Important APIs, types, and functions
`cifs_convert_address()` parses IPv4 and IPv6 text into `struct sockaddr`, including numeric IPv6 scope IDs. `cifs_set_port()` sets the port on IPv4 or IPv6 socket addresses. `cifs_NTtimeToUnix()` converts little-endian NT time in 100ns units since 1601 to `struct timespec64`. `cifs_UnixTimeToNT()` converts Unix `timespec64` to NT time. `cnvrtDosUnixTm()` converts legacy DOS date/time fields plus server time adjustment into Unix time.

## Control flow
Address conversion first attempts IPv4 using `in4_pton()` with backslash as terminator, then IPv6 using `in6_pton()`. For IPv6 values containing `%`, it parses a decimal scope id with `kstrtouint()`. Time conversion subtracts or adds the NTFS epoch offset and uses `do_div()` carefully so negative NT times work on 32-bit builds. DOS conversion decodes bitfield date/time structures, logs invalid ranges, clamps invalid day/month, accounts for years since 1980, leap years, and the year-2100 exception, then applies the supplied offset.

## State and persistence behavior
The file holds no persistent state. It mutates caller-provided socket address buffers and returns computed timestamps.

## Dependencies and integration points
It depends on kernel inet parsers, byteorder helpers, `SMB_TIME`/`SMB_DATE` definitions, CIFS debug logging, and is used by metadata converters in `inode.c` and `readdir.c` for SMB1/DOS timestamp formats.

## Risks
Risks include parsing ambiguities for IPv6 scope IDs, accepting partial address strings due to delimiter behavior, arithmetic mistakes for pre-1970 NT times, invalid DOS date clamping hiding corrupt server data, leap-year edge cases around 2100, and port setting on uninitialized address families.

## Test signals
Test IPv4, IPv6, IPv6 scoped addresses, invalid scope strings, backslash-terminated UNC host components, unsupported families in `cifs_set_port()`, NT times before and after 1970, zero NT time, nanosecond precision truncation, DOS timestamps at leap-year boundaries, invalid day/month/hour/minute values, and server time-adjust offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/netmisc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/nterr.h -->
# sources/distributed-fs/ceph-client/fs/smb/client/nterr.h

## Purpose
`nterr.h` defines NTSTATUS constants and the structure used for NTSTATUS-to-DOS error mapping. It is protocol vocabulary rather than executable logic, used by SMB status decoding and generated SMB1 mapping tables.

## Important APIs, types, and functions
The main type is `struct ntstatus_to_dos_err`, containing DOS error class, DOS code, NTSTATUS value, and string name. The file defines Win32-style helper constants such as `NT_ERROR_INVALID_PARAMETER`, then a large set of `NT_STATUS_*` values including success, pending, buffer overflow, access denied, object/path/file errors, sharing and lock failures, authentication/account failures, network errors, DFS path errors, reparse errors, encryption errors, and SMB negotiation/authentication statuses. Comments encode DOS class/code metadata for mapping generation.

## Control flow
There is no runtime control flow. Preprocessor definitions are consumed by C code and by table generation. The comments are semantically relevant because they document mapping pairs used to generate `smb1_mapping_table.c`.

## State and persistence behavior
The header stores no runtime state. It stabilizes constants that must match the SMB/Windows wire protocol and generated mapping artifacts.

## Dependencies and integration points
It is included by error mapping and network helper code such as `netmisc.c`, SMB1/SMB2 protocol handling, and status-to-errno conversion paths. Any change affects wire-status interpretation and user-visible errno behavior across the SMB client.

## Risks
Risks are incorrect constant values, duplicate or missing status definitions, comment/mapping drift that changes generated DOS mappings, and accidentally changing ABI-visible behavior for server errors. Because many constants are encoded as `0xC0000000 | value`, edits must preserve exact widths and values.

## Test signals
Regenerate and compare SMB1 mapping tables, compile all protocol configurations, verify representative status-to-errno conversions for access denied, object not found, path not covered, sharing violation, delete pending, not a reparse point, too many links, logon failure, and encryption errors, and run interoperability tests against Windows, Samba, and ksmbd servers that return these statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/nterr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/ntlmssp.h -->
# sources/distributed-fs/ceph-client/fs/smb/client/ntlmssp.h

## Purpose
`ntlmssp.h` defines NTLMSSP authentication wire constants, flags, AV pair identifiers, packed message structures, and builder/parser prototypes used by CIFS session setup.

## Important APIs, types, and functions
Constants include `NTLMSSP_SIGNATURE`, message types `NtLmNegotiate`, `NtLmChallenge`, `NtLmAuthenticate`, and negotiate flags for Unicode/OEM strings, signing, sealing, NTLM, anonymous, domain/workstation supplied, extended security, target info, version, 128-bit, key exchange, and 56-bit support. `enum av_field_type` names NTLM target-info AV pairs. Packed wire structures include `SECURITY_BUFFER`, `NEGOTIATE_MESSAGE`, `struct ntlmssp_version`, `struct negotiate_message`, `CHALLENGE_MESSAGE`, and `AUTHENTICATE_MESSAGE`. Prototypes cover `decode_ntlmssp_challenge()`, `build_ntlmssp_negotiate_blob()`, `build_ntlmssp_smb3_negotiate_blob()`, and `build_ntlmssp_auth_blob()`.

## Control flow
The header has no implementation flow, but it defines the layout that the NTLMSSP builder/parser code follows: client sends negotiate, server returns challenge with target info and nonce, client sends authenticate with LM/NT responses, identity strings, optional version, session key, and negotiated flags.

## State and persistence behavior
No local state is stored here. The structures describe transient authentication blobs. Sensitive material referenced by these blobs, such as session keys and challenge responses, lives in session/auth code and must be handled as secret memory there.

## Dependencies and integration points
The header depends on CIFS crypto key sizing and kernel endian types. It integrates with SMB session setup, NTLMv2 response generation, signing/sealing negotiation, and SMB2/3 negotiate blob construction.

## Risks
Risks are packed layout drift from the MS-NLMP wire format, endian mistakes in flags/message types, insufficient validation of `SECURITY_BUFFER` offsets/lengths by parser implementations, downgrade-prone negotiate flag choices, and incorrect handling of version fields between SMB1 and SMB2+ builders.

## Test signals
Test NTLMSSP negotiate/challenge/authenticate against Windows and Samba, validate blob offsets and lengths under short/oversized inputs, exercise Unicode and OEM names, domain/workstation supplied flags, target-info AV parsing, SMB2+ version-bearing negotiate blobs, key-exchange/sign/seal flag combinations, and malformed challenge rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/ntlmssp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/readdir.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/readdir.c

## Purpose
`readdir.c` implements CIFS directory enumeration. It starts and resumes SMB FIND searches, parses multiple directory-information wire formats, converts entries to `cifs_fattr`, primes the dcache, emits VFS dirents, and optionally populates cached directory leases.

## Important APIs, types, and functions
The exported entry point is `cifs_readdir()`. Important helpers are `cifs_prime_dcache()`, `cifs_fill_common_info()`, `cifs_posix_to_fattr()`, `cifs_dir_info_to_fattr()`, `cifs_fulldir_info_to_fattr()`, `cifs_std_info_to_fattr()`, `initiate_cifs_search()`, `find_cifs_entry()`, `nxt_dir_entry()`, `cifs_fill_dirent()`, `cifs_entry_is_dot()`, `cifs_filldir()`, and directory-cache helpers `emit_cached_dirents()`, `add_cached_dirent()`, `update_cached_dirents_count()`, and `finished_cached_dirents_count()`. It supports `SMB_FIND_FILE_POSIX_INFO`, `SMB_FIND_FILE_UNIX`, `SMB_FIND_FILE_DIRECTORY_INFO`, `SMB_FIND_FILE_FULL_DIRECTORY_INFO`, `SMB_FIND_FILE_ID_FULL_DIR_INFO`, `SMB_FIND_FILE_BOTH_DIRECTORY_INFO`, and `SMB_FIND_FILE_INFO_STANDARD`.

## Control flow
`cifs_readdir()` builds the full path, tries `open_cached_dir()` and emits cached dirents when a valid directory lease cache exists. Otherwise it starts `query_dir_first()` if needed, emits dot entries, finds the current entry for `ctx->pos`, optionally performs `query_dir_next()` until the target position is in the current buffer, reopens cached-dir tracking, allocates a Unicode scratch buffer, loops entries, converts names and metadata, primes dcache, emits entries, updates resume keys and cache accounting, and closes cached-dir references before returning.

## State and persistence behavior
Search state is stored in `struct cifsFileInfo->srch_inf`: search handle, info level, Unicode flag, network buffer pointers, entries in buffer, last-entry index, resume name/key, empty/end-of-search flags, and invalid handle state. Directory lease cache state is stored in `struct cached_fid->dirents` with position, validity/failure flags, byte and entry accounting, and copied fattrs. Dcache is updated opportunistically through `cifs_prime_dcache()`, but entries that require immediate revalidation, especially reparse points and POSIX special types, may be skipped or marked stale.

## Dependencies and integration points
This file depends on CIFS path construction, server `query_dir_first/query_dir_next/close_dir/calc_smb_size` operations, cached directory support, Unicode/NLS conversion, `inode.c` fattr conversion and inode instantiation, reparse helpers, backup credential detection, server-inode autodisable, VFS `dir_context`, and dcache lookup/splice APIs.

## Risks
The highest risks are malformed server buffer parsing, invalid `NextEntryOffset`, name length exceeding SMB buffer bounds, Unicode conversion errors, stale dcache priming for reparse points, incorrect resume position after suppressed dot entries, cached-dir accounting mismatches, server inode number collisions, and races when directories change between `seekdir`/`readdir` calls.

## Test signals
Test readdir on empty directories, large directories spanning many FIND buffers, lseek rewind and forward seek, directories changing during enumeration, cached directory lease hits and failures, Unicode and long filenames, malformed or fuzzed FIND buffers, all supported info levels, server-inode enabled/disabled fallback, POSIX special/reparse entries, MF symlink candidates, backup-credential searches, and servers that omit or return late dot entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/readdir.c -->
