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
