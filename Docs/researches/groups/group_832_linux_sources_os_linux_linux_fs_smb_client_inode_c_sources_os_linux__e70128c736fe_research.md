# Group Research: Linux SMB client inode, ioctl, link, misc, namespace, netlink, error, auth-schema, and readdir files

This group covers CIFS/SMB client VFS inode mutation and attribute handling, ioctl plumbing, symlink/hardlink creation, shared session/tcon/buffer helpers, DFS automounts, generic netlink witness notifications, SMB/NT time and address helpers, NTSTATUS and NTLMSSP wire definitions, and directory enumeration.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/inode.c -->
# File Research: sources/os/linux/linux/fs/smb/client/inode.c

## Purpose
Implements CIFS/SMB inode construction, attribute conversion, metadata revalidation, create/delete/rename directory operations, setattr/truncate, getattr, fiemap, cache invalidation, and inode operation selection.

## Main Interfaces
- Inode setup and lookup: `cifs_fattr_to_inode()`, `cifs_fill_uniqueid()`, `cifs_iget()`, `cifs_root_iget()`.
- Metadata fetch: `cifs_get_inode_info()`, `smb311_posix_get_inode_info()`, `cifs_get_inode_info_unix()`.
- Attribute conversion: `cifs_unix_basic_to_fattr()`, `wire_mode_to_posix()`, SMB3 POSIX and non-POSIX open-info converters.
- Namespace mutations: `cifs_unlink()`, `cifs_mkdir()`, `cifs_rmdir()`, `cifs_rename2()`.
- Revalidation/stat: `cifs_revalidate_file_attr()`, `cifs_revalidate_dentry_attr()`, `cifs_revalidate_mapping()`, `cifs_getattr()`.
- Size/attribute mutation: `cifs_file_set_size()`, `cifs_set_file_info()`, `cifs_setattr()`.

## Control Flow
Attribute lookup chooses among SMB3 POSIX info, legacy Unix extensions, and regular SMB file-all-info. Reparse points are routed through `reparse_info_to_fattr()` so symlinks, name-surrogate junctions, and unsupported reparse points are either translated locally or left for server-side open handling. The resulting `cifs_fattr` is normalized for mount options such as server inode numbers, ACL-derived modes, SFU emulation, Minshall+French symlinks, readonly DOS attributes, and fake DFS junction attributes before updating or instantiating the inode.

Mutating operations build a full dentry path, acquire a tcon link, call dialect operations, then invalidate parent/child timestamps and dcache state as needed. Delete and rename paths handle busy/open files by closing deferred handles, doing SMB2+ silly-rename behavior, retrying after clearing readonly attributes, and marking open handles as delete-pending.

## State And Synchronization
The file updates CIFS inode fields under `inode->i_lock`, uses CIFS inode flags such as `CIFS_INO_INVALID_MAPPING`, `CIFS_INO_DELETE_PENDING`, and `CIFS_INO_TMPFILE`, and coordinates mapping invalidation with `wait_on_bit_lock_action()` on `CIFS_INO_LOCK`. Size updates are coordinated with netfs remote size, pagecache truncation, fscache resize/invalidation, and outstanding netfs IO waits.

## Integration Points
Uses dialect callbacks in `server->ops` for query path/file info, open, close, unlink, mkdir, rmdir, rename, set size, set info, ACL, symlink, fiemap, and reparse operations. It depends on `reparse.c`, `link.c`, `cached_dir.c`, ACL helpers, DFS mount handling, fscache/netfs, and VFS inode/dentry operation tables from `cifsfs.c`.

## Notable Behaviors
- Auto-disables server inode numbers when collisions or bad root inode numbers are detected.
- Treats DFS referrals and name-surrogate directory reparse points as automount junction directories.
- Avoids path-based size updates when a writable handle can be used.
- Suppresses explicit timestamp setting for `O_TRUNC`/`ftruncate` cases to preserve server automatic timestamp behavior.
- Forces revalidation for ACL-derived modes, SFU special files, MF symlinks, some reparse points, hardlinked `noserverino` files, and stale cached attributes.

## Risks And Review Focus
- Inode number collision handling is correctness-sensitive for hardlinks and dcache aliasing.
- Delete/rename fallback behavior touches deferred close, silly rename, readonly attributes, and dentry hashing.
- Reparse point classification must not misrepresent unsupported server-side objects.
- Setattr paths mix local permission checks, ACL updates, DOS attributes, truncation, fscache, and netfs state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/ioctl.c -->
# File Research: sources/os/linux/linux/fs/smb/client/ioctl.c

## Purpose
Implements CIFS/SMB VFS ioctl dispatch for filesystem flags, server-side copy, query info, mount/session information, snapshots, encryption-key debug dumping, notifications, integrity/compression controls, and forced shutdown.

## Main Interfaces
- `cifs_ioctl()` is the exported ioctl dispatcher.
- `cifs_ioctl_query_info()` converts a dentry path to UTF-16 and calls dialect query-info ioctl support.
- `cifs_ioctl_copychunk()` copies an entire source file to the destination through server-side copychunk.
- `smb_mnt_get_fsinfo()` and `smb_mnt_get_tcon_info()` copy mount/tcon data to userspace.
- `cifs_shutdown()` sets mount forced-shutdown state.
- `cifs_dump_full_key()` exports SMB3 encryption keys for privileged debugging.

## Control Flow
`cifs_ioctl()` obtains an XID, traces the command, checks whether a file handle is required, and dispatches by ioctl command. Most commands call server dialect operations when present and otherwise return `-EOPNOTSUPP`, `-ENOTTY`, or validation errors. Copychunk validates write access and source filesystem identity, shutdown validates `CAP_SYS_ADMIN` and supported flags, and key dump validates encryption state plus key-buffer sizing.

## State And Synchronization
Uses tcon links and session references while copying mount data or key material. `cifs_dump_full_key()` can search all TCP sessions under `cifs_tcp_ses_lock`, protects session status with `ses_lock`, increments the session refcount while using a found session, and releases it afterward.

## Integration Points
Dispatches to dialect callbacks including `ioctl_query_info`, `set_compression`, `set_integrity`, `enum_snapshots`, and `notify`. Uses mount write accounting for copychunk and tracepoints for ioctl/shutdown observability.

## Notable Behaviors
- `FS_IOC_GETFLAGS` can expose legacy Unix extension flags or compression status.
- `FS_IOC_SETFLAGS` only attempts compression today.
- `CIFS_DUMP_KEY` handles older AES-128 debug format; `CIFS_DUMP_FULL_KEY` handles variable key sizes.
- `CIFS_IOC_SHUTDOWN` supports logflush/nologflush-style shutdown by setting `CIFS_MOUNT_SHUTDOWN`.

## Risks And Review Focus
- Key dumping is intentionally privileged but exposes sensitive session keys; any expansion should preserve capability checks and buffer validation.
- User-copy paths must keep structure sizing and `copy_to_user()`/`copy_from_user()` failures exact.
- Copychunk assumes both files are CIFS by comparing ioctl operation tables.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/link.c -->
# File Research: sources/os/linux/linux/fs/smb/client/link.c

## Purpose
Implements SMB client hardlink and symlink creation plus Minshall+French symlink detection, parsing, creation, and protocol-specific read/write helpers.

## Main Interfaces
- MF symlink helpers: `couldbe_mf_symlink()`, `check_mf_symlink()`, `cifs_query_mf_symlink()`, `cifs_create_mf_symlink()`, `smb3_query_mf_symlink()`, `smb3_create_mf_symlink()`.
- VFS link operations: `cifs_hardlink()` and `cifs_symlink()`.

## Control Flow
MF symlinks are represented as fixed-size regular files containing an `XSym` header, a length, an MD5 of the target, and the target string padded to `CIFS_MF_SYMLINK_FILE_SIZE`. Detection first checks regular-file type and size, then reads and validates the header/hash before changing the fattr to a symlink with the decoded target.

Hardlink creation builds source and destination paths, uses legacy Unix extensions when available, otherwise calls the dialect `create_hardlink()` operation. Symlink creation chooses the configured symlink strategy: Unix extension symlink, MF symlink, SFU node, or native/NFS/WSL reparse symlink when reparse support is available.

## State And Synchronization
Hardlink success updates the source inode link count locally and clears `CIFS_INO_TMPFILE`. Source inode attribute cache time is invalidated so later stat can reconcile with server state.

## Integration Points
Calls SMB1 open/read/write/close helpers for legacy MF symlink access and SMB2 open/read/write/close helpers for SMB2/3. Uses inode metadata lookup from `inode.c` after successful symlink creation and reparse symlink creation from `reparse.c`.

## Notable Behaviors
- MF symlink writes require the full fixed-size payload or return an SMB EIO trace error.
- MF symlink parsing treats malformed fixed-size files as ordinary regular files.
- Native reparse symlink creation exits early because it handles dentry instantiation in the reparse helper path.
- Hardlink target dentry is dropped to force a fresh lookup.

## Risks And Review Focus
- MF symlink validation relies on fixed offsets and MD5 string formatting.
- Symlink behavior varies substantially by mount option and server capability.
- Hardlink metadata is partly updated locally under oplock/cache assumptions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/link.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/misc.c -->
# File Research: sources/os/linux/linux/fs/smb/client/misc.c

## Purpose
Provides shared CIFS/SMB client utility code: XID accounting, session/tcon allocation and freeing, request-buffer pools, oplock writer coordination, pending/deferred open handling, DFS referral parsing, DFS superblock lookup helpers, UNC/path helpers, target IP matching, DFS prefix updates, DFS link error probing, and reconnect waiting.

## Main Interfaces
- Request tracking: `_get_xid()`, `_free_xid()`.
- Session/tcon lifecycle: `sesInfoAlloc()`, `sesInfoFree()`, `tcon_info_alloc()`, `tconInfoFree()`.
- Buffer pools: `cifs_buf_get()`, `cifs_buf_release()`, `cifs_small_buf_get()`, `cifs_small_buf_release()`, `free_rsp_buf()`.
- Oplocks/writers: `cifs_set_oplock_level()`, `cifs_get_writer()`, `cifs_put_writer()`, `cifs_queue_oplock_break()`, `cifs_done_oplock_break()`.
- Deferred handles: `cifs_add_deferred_close()`, `cifs_del_deferred_close()`, `cifs_close_deferred_file()`, `cifs_close_all_deferred_files()`, `cifs_close_all_deferred_files_sb()`, `cifs_close_deferred_file_under_dentry()`.
- DFS/reconnect: `parse_dfs_referrals()`, `cifs_get_dfs_tcon_super()`, `match_target_ip()`, `cifs_update_super_prepath()`, `cifs_inval_name_dfs_link_error()`, `cifs_wait_for_server_reconnect()`.

## Control Flow
Allocation helpers initialize locks, lists, counters, delayed work, fscache state, cached-dir state, DFS state, and reference counters. Free helpers unload NLS tables, free interface refs, free cached directories, and use sensitive frees for passwords and auth keys.

Deferred-close helpers cancel delayed close work under open-file locks, remove deferred-close records under inode deferred locks, collect handles into temporary lists, and then put file references outside the primary lock. DFS referral parsing validates the referral response header, referral count, version, buffer bounds, UTF-16 offsets, target names, TTLs, and path-consumed values.

## State And Synchronization
Uses global `GlobalMid_Lock` for XID counters, session/tcon spinlocks for status and refs, tcon/inode open-file locks for open handle lists, inode `deferred_lock` for deferred-close lists, superblock tlink-tree locking for per-superblock tcon walks, and active superblock refs during DFS failover lookup.

## Integration Points
Shared across mount/session setup, demultiplex callbacks, oplock break workers, inode delete/rename paths, DFS cache/referral code, and reconnect logic. Calls DNS resolution and DFS cache helpers only under `CONFIG_CIFS_DFS_UPCALL`.

## Notable Behaviors
- `cifs_autodisable_serverino()` clears server inode use and warns when server inode numbers are unreliable.
- `backup_cred()` checks backup uid/gid mount options against current credentials.
- `cifs_mark_open_handles_for_deleted_file()` marks all or matching hardlink handles as deleted so close deferral is avoided.
- DFS invalid-name handling probes referrals without filling the DFS cache to avoid evicting useful failover targets.

## Risks And Review Focus
- Deferred-close cancellation and file ref ownership are lock-order sensitive.
- Session/tcon free paths contain sensitive credentials and must keep zeroing semantics.
- DFS referral parsing depends on strict buffer bounds and offset validation.
- Reconnect waits differ between soft one-shot and hard retry behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/namespace.c -->
# File Research: sources/os/linux/linux/fs/smb/client/namespace.c

## Purpose
Implements CIFS automount handling for DFS referrals and SMB junctions, including device-name construction, automount expiry, submount fs-context creation, and namespace inode operations.

## Main Interfaces
- `cifs_build_devname()` builds a `//server/share[/prepath]` source string from a referral target.
- `cifs_d_automount()` is the dentry automount entry point.
- `cifs_release_automount_timer()` cancels the delayed automount expiry worker at module teardown.
- `cifs_namespace_inode_operations` exposes namespace inode operations for automount directories.

## Control Flow
`cifs_d_automount()` calls `cifs_do_automount()`, then adds the new mount to `cifs_automount_list` and schedules expiry. `cifs_do_automount()` rejects root automounts, synchronizes current fs-context passwords from the root session, creates a submount fs context, constructs the automount full path, duplicates the current SMB3 context with current uid/gid/credential ids, parses the new devname, builds `ctx->source`, marks DFS automount state, and calls `fc_mount()`.

## State And Synchronization
Automount expiry is driven by `cifs_automount_task` and `mark_mounts_for_expiry()`. DFS origin paths are read under `tcon->tc_lock`. The session password sync is protected by `ses->session_mutex`.

## Integration Points
Depends on path builders from `dir.c`, SMB3 fs-context parsing/duplication, `cifs_sb_master_tcon()`, DFS origin path state from tcons, and VFS automount/submount APIs.

## Notable Behaviors
- DFS-origin automount paths are reconstructed from `tcon->origin_fullpath` plus the raw dentry path.
- Multiuser automount contexts default uid/gid and cruid to the current caller when unspecified.
- Device names are normalized to slash delimiters and trailing UNC separators are trimmed.

## Risks And Review Focus
- Automount full-path construction must avoid underrunning the allocated path page when prepending origin paths.
- Password synchronization affects retry behavior for DFS submounts.
- Expiry list must be empty before final timer cancellation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/namespace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/netlink.c -->
# File Research: sources/os/linux/linux/fs/smb/client/netlink.c

## Purpose
Registers the CIFS generic netlink family used for server witness notification messages from userspace to the kernel SMB client.

## Main Interfaces
- `cifs_genl_family` defines the generic netlink family, attributes, operations, and multicast groups.
- `cifs_genl_init()` registers the family.
- `cifs_genl_exit()` unregisters the family.

## Main Contents
The file defines `cifs_genl_policy` for witness registration, names, share names, IP sockaddr payloads, notify flags, Kerberos auth flag, credentials, domain name, notification type, resource state, and resource name. It defines one admin-permission operation, `CIFS_GENL_CMD_SWN_NOTIFY`, dispatched to `cifs_swn_notify()`, and one net-admin multicast group.

## Integration Points
Depends on UAPI definitions in `linux/cifs/cifs_netlink.h`, local `netlink.h`, CIFS globals/debug, and server witness notification logic in `cifs_swn.h`.

## Risks And Review Focus
- Attribute policy must stay synchronized with the UAPI enum.
- The notification command is privileged through generic netlink admin permission and multicast group capability flags.
- Registration/unregistration errors are logged but otherwise simple lifecycle events.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/netlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/netlink.h -->
# File Research: sources/os/linux/linux/fs/smb/client/netlink.h

## Purpose
Declares the CIFS generic netlink family and registration lifecycle functions.

## Main Contents
- Header guard `_CIFS_NETLINK_H`.
- `extern struct genl_family cifs_genl_family`.
- Prototypes for `cifs_genl_init()` and `cifs_genl_exit()`.

## Integration Points
Included by the netlink implementation and module initialization code that registers/unregisters CIFS generic netlink support.

## Risks And Review Focus
- This header is intentionally minimal; changes should remain aligned with `netlink.c` and generic netlink lifecycle call sites.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/netlink.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/netmisc.c -->
# File Research: sources/os/linux/linux/fs/smb/client/netmisc.c

## Purpose
Provides network and time conversion helpers for the CIFS/SMB client, including textual IP parsing, socket port assignment, NT time conversion, Unix-to-NT time conversion, and DOS date/time conversion.

## Main Interfaces
- `cifs_convert_address()` parses IPv4 and IPv6 literals, including IPv6 numeric scope IDs.
- `cifs_set_port()` writes a TCP/UDP port into IPv4 or IPv6 sockaddr structures.
- `cifs_NTtimeToUnix()` converts NT 1601-based 100ns timestamps to `timespec64`.
- `cifs_UnixTimeToNT()` converts Unix `timespec64` to NT time.
- `cnvrtDosUnixTm()` converts SMB/DOS date and time fields to Unix time.

## Control Flow
Address parsing first attempts IPv4, then IPv6, optionally splitting an IPv6 `%scope` suffix and parsing the scope as an integer. NT time conversion subtracts the NTFS epoch offset and handles negative values specially so 32-bit `do_div()` does not receive a negative dividend. DOS time conversion decodes bitfields, clamps invalid month/day values, adjusts for the 1980 epoch and leap years through 2107, then applies the supplied server time offset.

## Integration Points
Used by metadata conversion in inode and readdir paths, connection address parsing, and SMB1/SMB2 protocol helpers.

## Notable Behaviors
- `cifs_inet_pton()` treats backslash as the parsing terminator for UNC-style addresses.
- DOS conversion logs invalid ranges but still clamps and returns a time.
- NT timestamp conversion leaves timezone adjustment to callers.

## Risks And Review Focus
- Time conversion must preserve pre-1970 NT timestamps and 32-bit architecture behavior.
- IPv6 scope parsing accepts only numeric scope IDs up to 12 characters.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/netmisc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/nterr.h -->
# File Research: sources/os/linux/linux/fs/smb/client/nterr.h

## Purpose
Defines NTSTATUS constants and the `ntstatus_to_dos_err` mapping record used by SMB error translation code.

## Main Contents
- `struct ntstatus_to_dos_err` with DOS class, DOS code, NTSTATUS value, and string name.
- Win32-style error constants used in SMB status handling.
- A large list of `NT_STATUS_*` definitions covering success, pending, informational statuses, filesystem errors, object/path errors, network errors, auth/account errors, pipe errors, DFS errors, encryption errors, reparse statuses, and SMB3 preauth negotiation errors.
- Comments beside most constants encode the DOS class/code mapping used to generate SMB1 mapping tables.

## Integration Points
Included by SMB error mapping and helper code such as `netmisc.c`, `misc.c`, and SMB1/SMB2 error translation units.

## Notable Behaviors
This is a schema/header file rather than executable logic. It centralizes numeric NTSTATUS definitions so protocol parsers and error mappers can use symbolic names consistently.

## Risks And Review Focus
- Numeric constants must match Windows/SMB protocol definitions.
- Mapping comments are data for generated tables, so comment format changes can affect generation.
- Adding new statuses should preserve endian and integer-width expectations at use sites.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/nterr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/ntlmssp.h -->
# File Research: sources/os/linux/linux/fs/smb/client/ntlmssp.h

## Purpose
Defines NTLMSSP wire constants, flags, AV-pair identifiers, packed message structures, and prototypes for NTLMSSP negotiate/challenge/authentication blob helpers.

## Main Contents
- NTLMSSP signature and message type constants for negotiate, challenge, authenticate, and unknown messages.
- Negotiate flags for Unicode/OEM strings, signing, sealing, NTLM, target info, version, 128-bit, key exchange, and 56-bit support.
- `enum av_field_type` for target-info AV pairs such as NetBIOS/DNS names, flags, timestamp, target name, restrictions, and channel bindings.
- Packed `SECURITY_BUFFER`, negotiate-message, challenge-message, and authenticate-message layouts.
- `struct ntlmssp_version` for MS-NLMP version fields.
- Prototypes for challenge decoding and negotiate/auth blob construction.

## Integration Points
Used by NTLMSSP authentication implementation and CIFS encryption/auth helpers. The structures match MS-NLMP/NTLMSSP wire format and are consumed when building SMB session setup security blobs.

## Notable Behaviors
- Older typedef-style structures are retained to mirror NTLMSSP standards.
- SMB3 negotiate blob construction can include version information while the older negotiate layout omits it.
- All wire structures are packed and use little-endian fields.

## Risks And Review Focus
- Wire layout and packing are security-sensitive because auth blobs are parsed by servers and local crypto code.
- Flag definitions must stay compatible with NTLMSSP negotiation behavior and FIPS/auth policy in implementation files.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/ntlmssp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/readdir.c -->
# File Research: sources/os/linux/linux/fs/smb/client/readdir.c

## Purpose
Implements CIFS/SMB directory enumeration, FIND_FIRST/FIND_NEXT search state management, directory entry parsing across SMB info levels, dcache priming, cached directory entry serving, and VFS `iterate_shared`-style emission through `cifs_readdir()`.

## Main Interfaces
- Directory read entry point: `cifs_readdir()`.
- Search setup: `initiate_cifs_search()` and `_initiate_cifs_search()`.
- Search positioning: `find_cifs_entry()`, `nxt_dir_entry()`, `cifs_save_resume_key()`.
- Entry conversion: `cifs_fill_dirent()`, `cifs_dir_info_to_fattr()`, POSIX/Unix/full/std info converters.
- Dcache/cache helpers: `cifs_prime_dcache()`, `cifs_dir_emit()`, cached dirent add/emit/count helpers.

## Control Flow
`cifs_readdir()` builds the directory path, tries to open and serve a cached directory, emits dot entries, initiates a network search if needed, seeks to the requested logical position, fetches more buffers with `query_dir_next()` as needed, converts each returned record to a VFS name and `cifs_fattr`, primes the dcache, emits to the VFS dir context, and optionally stores entries in the cached-dir structure.

Search setup chooses the info level based on legacy Unix extensions, SMB3 POSIX extensions, NT find capability, and server inode mount options. If server inode support fails with `-EOPNOTSUPP`, it disables server inode use and retries.

## State And Synchronization
Per-open directory state lives in `struct cifsFileInfo` and its `srch_inf`, including the network buffer, last entry, resume key/name, index of last entry, entries-in-buffer, unicode flag, empty/end-of-search flags, and invalid handle state. Cached directory entries are protected by `cfid->dirents.de_mutex` and accounted per tcon and globally with atomic counters.

## Integration Points
Calls dialect `query_dir_first`, `query_dir_next`, `close_dir`, `dir_needs_close`, and `calc_smb_size` callbacks. Uses inode conversion helpers from `inode.c`, reparse parsing, idmap/ACL helpers, cached-dir open/close APIs, and VFS `dir_emit()`/dcache aliasing APIs.

## Notable Behaviors
- Suppresses server-returned `.` and `..` because VFS dot entries are emitted first.
- Validates next-entry offsets and entry bounds against the SMB buffer end.
- Rewinds and restarts search when the caller seeks backward or cached directory metadata indicates change.
- Marks ACL-derived, MF symlink, SFU, reparse, symlink, block, and char entries for later revalidation when readdir metadata is insufficient.
- Auto-disables server inode numbers when directory entries lack usable inode IDs.

## Risks And Review Focus
- Directory parsing is buffer-boundary sensitive across many SMB info levels.
- Cached directory serving must preserve `ctx->pos` holes caused by suppressed dot entries.
- Dcache priming must avoid clobbering mounted dentries and must handle inode type/uniqueid changes.
- Search rewind and network-buffer cleanup must avoid stale pointers in `srch_inf`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/readdir.c -->