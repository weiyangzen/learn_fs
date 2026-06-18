# sources/distributed-fs/ceph-client/fs/smb/client/reparse.c

## Purpose
`reparse.c` implements CIFS/SMB reparse point support for Linux special-file semantics. It creates and parses native Windows symlinks, NFS-style reparse special files, WSL/LX reparse points, and AF_UNIX socket tags, then converts parsed reparse metadata into `struct cifs_fattr` file type, device, uid/gid, and symlink target state.

## Important APIs, types, and functions
The exported entry points are `create_reparse_symlink`, `mknod_reparse`, `parse_reparse_point`, `smb2_parse_native_symlink`, `smb2_get_reparse_point_buffer`, and `cifs_reparse_point_to_fattr`. Creation helpers include `create_native_symlink`, `create_native_socket`, `mknod_nfs`, `mknod_wsl`, `nfs_set_reparse_buf`, `wsl_set_reparse_buf`, `wsl_set_xattrs`, and `ea_create_context`. Parsing helpers include `parse_reparse_nfs`, `parse_reparse_native_symlink`, `parse_reparse_wsl_symlink`, `wsl_to_fattr`, and `posix_reparse_to_fattr`.

## Control flow
Symlink creation dispatches by mount symlink type: native Windows symlink, NFS reparse point, or WSL reparse point. Native symlink creation converts Linux paths to SMB/NT representation, optionally maps absolute `/symlinkroot/<drive>/...` paths into `\??\X:\...`, probes relative targets to decide file-vs-directory symlink type, builds a `reparse_symlink_data_buffer`, and calls the dialect operation `create_reparse_inode`. `mknod_reparse` prefers native AF_UNIX sockets unless disabled, then dispatches to NFS or WSL creation based on `ctx->reparse_type`.

Parsing starts with `parse_reparse_point`, which switches on `ReparseTag`. NFS parsing validates data lengths and UTF-16 symlink target content. Native symlink parsing validates substitute-name bounds, then `smb2_parse_native_symlink` translates NT absolute, share-root-relative, and ordinary relative/POSIX-style targets into Linux paths. WSL symlink parsing accepts only version 2 UTF-8 targets and rejects embedded NUL bytes.

## State and persistence
The durable state is the reparse buffer and, for WSL files, create-time EAs such as `$LXUID`, `$LXGID`, `$LXMOD`, and `$LXDEV` stored on the server. Runtime state is held in transient `cifs_open_info_data`, `kvec` buffers, allocated target strings, and `cifs_fattr`. `cifs_reparse_point_to_fattr` is the main bridge from persisted server tag/data back into Linux inode mode and device metadata.

## Dependencies and integration points
This file depends on CIFS mount context, path conversion helpers, SMB2 create contexts, common reparse tag definitions, NLS conversion, server dialect ops, and `cifs_open_info_data`. It is called from common inode creation and lookup/open paths through `server->ops->create_reparse_inode`, `query_reparse_point`, and `get_reparse_point_buffer`. SMB1 also integrates with these routines through `smb1ops.c`.

## Risks and test signals
Risks include malformed server buffers, UTF-16/UTF-8 length mistakes, embedded NUL targets, absolute NT path conversion gaps, symlinkroot misconfiguration, target type misdetection for unresolved relative symlinks, WSL EA alignment/length errors, and mismatches between reparse tag type and `$LXMOD` file type. Test signals should cover native absolute and relative symlinks, share-root-relative symlink conversion, NFS char/block/fifo/socket/link buffers, WSL symlink/device metadata, missing `$LXDEV` for devices, invalid lengths, unsupported tags, and permission-denied target probes.
