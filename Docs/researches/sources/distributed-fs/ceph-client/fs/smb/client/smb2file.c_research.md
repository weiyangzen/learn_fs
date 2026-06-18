# sources/distributed-fs/ceph-client/fs/smb/client/smb2file.c

## Purpose

This file contains SMB2/SMB3 file-open helpers that handle symlink error payloads, resilient-handle setup, server inode-number completion, and byte-range lock replay/unlock batching. It provides higher-level file operations with a cleaner `smb2_open_file()` API around `SMB2_open()` while preserving CIFS-specific behavior for symlinks, leases, resiliency, and local lock bookkeeping.

## Important APIs, types, and functions

- `symlink_data()` extracts and validates `struct smb2_symlink_err_rsp` from either SMB2 error contexts or legacy error data, checking byte counts, context lengths, `SYMLINK_ERROR_TAG`, and `IO_REPARSE_TAG_SYMLINK`.
- `smb2_fix_symlink_target_type()` normalizes parsed symlink targets for non-POSIX mounts by appending a slash for directory symlinks and rejecting file symlinks ending in slash.
- `smb2_parse_symlink_response()` validates the symlink path buffers and delegates native target conversion to `smb2_parse_native_symlink()`.
- `smb2_open_file()` converts paths to UTF-16, adjusts access masks, calls `SMB2_open()`, handles `STATUS_STOPPED_ON_SYMLINK`, optionally reopens with `OPEN_REPARSE_POINT`, applies network resiliency through `FSCTL_LMR_REQUEST_RESILIENCY`, and fills `cifs_open_info_data`.
- `smb2_unlock_range()` removes or batches unlocks for local `cifsLockInfo` entries covered by a VFS lock range.
- `smb2_push_mandatory_locks()` and `smb2_push_mand_fdlocks()` replay cached mandatory byte-range locks to the server with `smb2_lockv()`.

## Control flow

The open path first converts the mount-relative path to UTF-16. If the requested access lacks `FILE_READ_ATTRIBUTES` and does not already imply it, the helper adds that bit to retrieve metadata, with a retry path that removes it on `-EACCES`. On symlink-stop errors, the function parses the symlink target from the error response, reopens the object as a reparse point to collect metadata, and adjusts the target based on directory/file type. After a successful open, it may issue a resiliency ioctl and may fetch a server inode number if the create response omitted `IndexNumber`.

Lock removal scans `cfile->llist->locks` under `cinode->lock_sem`. If byte-range locks are locally cacheable, matching entries are deleted without network I/O. Otherwise matching locks are moved to a temporary list, batched into SMB2 unlock elements up to the negotiated buffer/page limit, sent to the server, and restored to the original list if the network unlock fails.

## State and persistence behavior

This file mutates open parameters, `cifs_fid` metadata, `cifs_open_info_data`, `tcon->use_resilient`, symlink target ownership, and in-memory CIFS lock lists. There is no durable local persistence. Remote persistence occurs through SMB2 create/open, ioctl resiliency requests, and lock/unlock requests on the server. Error-buffer ownership is carefully tracked with `err_buftype` and released via `free_rsp_buf()`.

## Dependencies and integration points

The file depends on CIFS mount/session structures, UTF-16 conversion, SMB2 PDU helpers, status constants, and SMB FSCTL constants. `smb2_open_file()` is part of the SMB2 operation surface declared in `smb2proto.h` and used by file create/open flows. Symlink parsing is reused by `smb2inode.c` for compound path queries and reparse handling.

## Risks and edge cases

Symlink error parsing is length-sensitive and must reject malformed contexts before dereferencing nested payloads. Access-mask retry changes `oparms->desired_access` in place, so callers see the final adjusted value. Resiliency failures are intentionally suppressed except for disabling unsupported resiliency, which can hide server-side configuration issues. Lock batching must preserve local lock state on partial failures; restoring the temporary list on failed unlock is essential for consistency. Range matching uses start/end arithmetic, so overflow-sensitive lock ranges should be covered by tests.

## Test signals

Relevant signals include symlink traversal tests for absolute and relative targets, directory symlink slash behavior, open without read-attributes permissions, resilient-handle mounts, and byte-range lock stress tests across reconnects. No direct KUnit file is present here; behavior is mostly integration-tested through SMB2 file operations.
