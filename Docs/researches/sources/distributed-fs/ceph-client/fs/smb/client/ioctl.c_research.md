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
