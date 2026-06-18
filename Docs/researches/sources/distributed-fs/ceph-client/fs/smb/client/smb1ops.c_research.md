# sources/distributed-fs/ceph-client/fs/smb/client/smb1ops.c

## Purpose
`smb1ops.c` adapts legacy SMB1/CIFS wire operations to the common CIFS client operation interfaces. It negotiates Unix extensions, controls request cancelation, sizes I/O, queries metadata, wraps open/read/write/close/dir/lock/fs operations, handles reparse-backed special files, and publishes `smb1_operations`/`smb1_values`.

## Important APIs, types, and functions
The public symbol is `reset_cifs_unix_caps`; the main exported data are `smb1_operations` and `smb1_values`. Important internal functions include `send_nt_cancel`, `send_lock_cancel`, `cifs_send_cancel`, `cifs_get_next_mid`, `smb1_negotiate_wsize`, `smb1_negotiate_rsize`, `cifs_query_path_info`, `cifs_query_file_info`, `smb_set_file_info`, `cifs_open_file`, `cifs_query_symlink`, `cifs_get_reparse_point_buffer`, `cifs_make_node`, and `cifs_is_network_name_deleted`.

## Control flow
Mount/reconnect capability negotiation queries server Unix capabilities, masks them according to mount options and saved reconnect behavior, sets POSIX ACL/path flags, and sends the negotiated capability mask back to the server. Request cancelation rewrites an existing request as `SMB_COM_NT_CANCEL` or sends a lock-cancel request for Windows blocking locks. MID allocation walks pending requests to avoid 16-bit MID collisions and forces reconnect under extreme queue pressure.

Metadata query first tries NT `QPathInfo`, falls back to `FindFirst`, then to legacy `SMB_COM_QUERY_INFORMATION`, with wildcard handling for non-Unicode servers. For WSL reparse points it opportunistically fetches `$LXMOD` and `$LXDEV` EAs. File info setting prefers existing writable handles, then path set-info, then open-by-path set-info, then legacy setattr for older servers. Node creation chooses Unix extensions, SFU emulation, or reparse points.

## State and persistence
Runtime state includes negotiated `tcon->fsUnixInfo`, mount flags, credits, request MID counters, tcon statistics, cifs inode attributes/oplock state, open FIDs, search handles, and reconnect flags. Persistent server-side effects include file metadata changes, node creation, EAs for WSL reparse data, compression settings, locks, symlinks, hardlinks, and deletes.

## Dependencies and integration points
This file depends on nearly all SMB1 command helpers declared in `smb1proto.h`, common CIFS inode and transport code, reparse support from `reparse.c`, xattr support, DFS upcalls, ACL helpers, mandatory lock helpers, and common dialect interfaces. `smb1_operations` is the central integration point used by the rest of the CIFS client to dispatch dialect-specific behavior.

## Risks and test signals
Risks include capability drift on reconnect, MID exhaustion or collision, legacy server fallbacks changing semantics, wildcard expansion in non-Unicode query fallbacks, WSL EA length/alignment mistakes, read/write size negotiation over server max buffer limits, lock cancel sequence interactions, file attribute updates on non-NT servers, and share-deleted reconnect marking. Test signals include old LANMAN/non-NT servers, Unix extensions on/off, POSIX paths/ACL options, reparse node creation, WSL special-file lookup, signed sessions, blocking lock cancelation, metadata set fallbacks, directory query close behavior, share deletion errors, and operation-table completeness.
