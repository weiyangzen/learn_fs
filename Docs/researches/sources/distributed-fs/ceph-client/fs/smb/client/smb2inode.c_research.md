# sources/distributed-fs/ceph-client/fs/smb/client/smb2inode.c

## Purpose

This file implements SMB2/SMB3 inode and path operations using compound open-operation-close request chains. It covers path metadata queries, mkdir/rmdir/unlink, rename, hardlink creation, file-size and attribute updates, reparse-point creation/query, POSIX metadata, WSL EA handling, and pending-delete rename flows. It is one of the main bridges between Linux VFS inode operations and SMB2 protocol primitives.

## Important APIs, types, and functions

- `smb2_compound_op()` is the central helper. It builds optional `CREATE`, one or more operation requests selected by `enum smb2_compound_ops`, and optional `CLOSE`, sends them with `compound_send_recv()`, maps each response, parses output data, frees request buffers, and handles replayable errors.
- `smb2_query_path_info()` obtains file metadata through cached-root handles, normal query-info, POSIX query-info, open-query fallback for access-denied cases, reparse-point probing, WSL EA fetches, and DFS invalid-name handling.
- `smb2_mkdir()`, `smb2_mkdir_setinfo()`, `smb2_rmdir()`, `smb2_unlink()`, `smb2_rename_path()`, `smb2_create_hardlink()`, `smb2_set_path_size()`, and `smb2_set_file_info()` wrap common VFS operations.
- `smb2_create_reparse_inode()` creates a file/directory with `OPEN_REPARSE_POINT`, sets reparse data, queries metadata, builds an inode, and deletes the intermediate object if setting the reparse point fails.
- `smb2_query_reparse_point()` returns reparse data and tag ownership to the caller.
- `smb2_rename_pending_delete()` implements a silly-rename style pending-delete sequence: clear attributes, rename to a generated hidden name, then mark delete pending.
- Helper validators include `reparse_buf_ptr()`, `parse_posix_sids()`, `check_wsl_eas()`, `parse_create_response()`, and `ea_unsupported()`.

## Control flow

Most exported functions prepare `CIFS_OPARMS`, optional input `kvec`s, and an array of `SMB2_OP_*` commands, then call `smb2_compound_op()`. The compound helper chooses a channel, allocates `smb2_compound_vars`, optionally converts the path to UTF-16, may reuse a lease key from the inode, appends request initializers, marks related/next commands, sends the compound, parses per-command responses, and frees or transfers output buffers. If `cfile` is provided, the helper skips explicit open/close and uses the existing FID.

Replay control is built into both `smb2_compound_op()` and the specialized `smb2_unlink()` path: replayable errors trigger `smb2_should_replay()`, optional backoff, and `smb2_set_replay()` on each request. Lease-key hardlink/rename/truncate failures with `-EINVAL` are retried without the inode lease key.

## State and persistence behavior

Local state mutations include inode CIFS attributes, cached directory invalidation, `tcon->need_reconnect`, transferred reparse IO buffers in `cifs_open_info_data`, symlink targets, WSL EA buffers, `CIFS_INO_DELETE_PENDING`, and open-handle deletion marking. Remote persistence is significant: create, delete-on-close, rename, hardlink, EOF update, basic-info update, FSCTL reparse point set/get, and query operations all change or observe server-side namespace and metadata. Buffer ownership is subtle when reparse query succeeds: response ownership is moved to `data.reparse.io` and removed from the normal free path.

## Dependencies and integration points

The file depends on CIFS superblock/tcon/session state, UTF-16 conversion, cached directory handles, SMB2 PDU initializers/free routines, compound transport, status mapping, POSIX SID helpers, WSL EA constants, tracepoints, and inode population functions (`cifs_get_inode_info()` and `smb311_posix_get_inode_info()`). It shares symlink handling with `smb2file.c` and operation IDs with `smb2glob.h`.

## Risks and edge cases

The compound path is high-risk because request count, response index, and free index must remain aligned across optional open/close, explicit open-query, existing `cfile`, and retry cases. Adding a new `SMB2_OP_*` requires construction, response parsing, trace, free, and output ownership handling. Reparse and WSL EA parsing are length-sensitive. Access-denied metadata fallback intentionally relies on create responses instead of query-info and may return reduced metadata. Lease reuse with hardlinks can provoke `STATUS_INVALID_PARAMETER`, so retry without lease is required. Failed reparse creation must clean up the server object to avoid leaving unusable empty files.

## Test signals

Strong test signals include VFS stat/open on normal files, roots, DFS links, symlinks, and unsupported reparse points; POSIX extension stat including owner/group SID parsing; WSL special-file EA queries; mkdir/rmdir/unlink/rename/hardlink/truncate integration tests; replay/reconnect tests for compound operations; and negative tests for malformed reparse or EA response lengths. No direct KUnit file is present in this subset.
