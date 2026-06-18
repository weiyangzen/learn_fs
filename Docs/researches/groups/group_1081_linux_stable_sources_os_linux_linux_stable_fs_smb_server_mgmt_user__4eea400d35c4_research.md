# Group Research: group_1081_linux_stable_sources_os_linux_linux_stable_fs_smb_server_mgmt_user__4eea400d35c4

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/user_session.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/mgmt/user_session.h

This header defines ksmbd’s per-user SMB session state and declares the session-management API used by SMB2/SMB3 authentication, tree-connect handling, multichannel, RPC handles, and `/proc` session reporting.

Key definitions:
- `CIFDS_SESSION_FLAG_SMB2`: session flag bit for SMB2-family sessions.
- `PREAUTH_HASHVALUE_SIZE`: SMB 3.1.1 preauthentication hash size, 64 bytes.
- `struct channel`: per-channel signing key and associated `ksmbd_conn`, used for SMB3 multichannel.
- `struct preauth_session`: preauthentication hash value, session id, and list node.
- `struct ksmbd_session`: central session object containing:
  - session id, dialect, client GUID, user pointer, sequence number, flags
  - signing/encryption booleans and session state
  - preauth hash pointer and NTLM/CIFS session key
  - hash/list linkage, channel xarray, tree connection xarray/IDA, RPC handle xarray
  - SMB3 encryption/decryption/signing keys
  - per-session file table, last activity timestamp, locks, optional proc entry, refcount

Inline helpers:
- `test_session_flag()`
- `set_session_flag()`
- `clear_session_flag()`

Declared APIs:
- Session lifecycle: `ksmbd_smb2_session_create()`, `ksmbd_session_destroy()`.
- Session lookup and registration: `ksmbd_session_lookup*()`, `__session_lookup()`, `ksmbd_session_register()`, `ksmbd_sessions_deregister()`.
- Session replacement: `destroy_previous_session()`.
- SMB 3.1.1 preauth sessions: `ksmbd_preauth_session_alloc()`, `ksmbd_preauth_session_lookup()`.
- Tree connection ID allocation: `ksmbd_acquire_tree_conn_id()`, `ksmbd_release_tree_conn_id()`.
- Named-pipe/RPC tracking: `ksmbd_session_rpc_open()`, `ksmbd_session_rpc_close()`, `ksmbd_session_rpc_method()`.
- Refcounting: `ksmbd_user_session_get()`, `ksmbd_user_session_put()`.
- Proc integration: `create_proc_sessions()`.

Concurrency and ownership:
- `ksmbd_session` uses `rw_semaphore` locks for channel, tree connection, and RPC state.
- `xarray` containers hold channels, tree connections, and RPC handles.
- `atomic_t refcnt` protects lifetime across request processing and async paths.

Risk areas:
- Session refcounting is security-critical; premature put or missing get can turn request/session lookup paths into use-after-free risks.
- Multichannel state depends on `ClientGUID`, channel xarray contents, and per-channel signing keys staying consistent.
- Preauth hash state is part of SMB 3.1.1 authentication integrity; changes affect downgrade and session setup behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/mgmt/user_session.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/misc.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/misc.c

This file implements general ksmbd utility routines for wildcard matching, path/name conversion, filename validation, share-name extraction, directory-entry name conversion, and NT time conversion.

Functions:
- `match_pattern()`
  - Case-insensitive wildcard matcher supporting `*` and `?`.
  - Returns true/false style values despite the comment saying zero means matched.
  - TODO notes missing DOS wildcard semantics for `DOS_DOT`, `DOS_QM`, and `DOS_STAR`.

- `is_char_allowed()`
  - Rejects ASCII control characters and Windows-disallowed wildcard/path characters: `?`, `"`, `<`, `>`, `|`, `*`.

- `ksmbd_validate_filename()`
  - Walks a filename and rejects disallowed characters with `-ENOENT`.

- `ksmbd_validate_stream_name()`
  - Rejects `/`, `:`, and `\` inside alternate data stream names.

- `parse_stream_name()`
  - Splits `filename` on `:` using `strsep`.
  - Extracts stream name and optional stream type.
  - Recognizes `$DATA` as `DATA_STREAM` and `$INDEX_ALLOCATION` as `DIR_STREAM`.
  - Mutates the input filename buffer.

- `convert_to_nt_pathname()`
  - Converts a kernel `struct path` into a share-relative Windows path.
  - Uses `d_path()`, verifies the absolute path has the configured share path prefix, strips that prefix, ensures share root reports as `/`, then converts `/` to `\`.
  - Returns allocated string or `ERR_PTR()`.

- `get_nlink()`
  - Returns `st->nlink`, subtracting one for directories.

- `ksmbd_conv_path_to_unix()`, `ksmbd_conv_path_to_windows()`
  - Replace `\` with `/`, or `/` with `\`.

- `ksmbd_strip_last_slash()`
  - Removes trailing `/` characters in place.

- `ksmbd_casefold_sharename()`
  - Allocates a `KSMBD_REQ_MAX_SHARE_NAME` buffer.
  - Uses Unicode casefolding when `CONFIG_UNICODE` and a unicode map are available.
  - Falls back to ASCII lowercasing and returns `ERR_PTR(-E2BIG)` on truncation.

- `ksmbd_extract_sharename()`
  - Extracts final component after the last `\` and casefolds it.

- `convert_to_unix_name()`
  - Allocates and returns `share->path` joined with the share-relative name.
  - Handles a leading slash in the requested name.

- `ksmbd_convert_dir_info_name()`
  - Converts a directory entry name to UTF-16 using `smbConvertToUTF16()`.
  - Allocates up to `min(4 * name_len, PATH_MAX)` bytes and appends a UTF-16 NUL.

- `ksmbd_NTtimeToUnix()`
  - Converts NT time, based on 1601-01-01 in 100 ns units, to `timespec64`.
  - Handles negative values separately for 32-bit division constraints.

- `ksmbd_UnixTimeToNT()`
  - Converts `timespec64` to NT time.

- `ksmbd_systime()`
  - Returns current wall-clock time in NT format.

Dependencies:
- Share configuration from `mgmt/share_config.h`.
- SMB charset conversion from `smb_common.h`.
- VFS path handling through `d_path()` and `struct path`.

Risk areas:
- `parse_stream_name()` assumes `strsep(&s_name, ":")` leaves a usable `s_name`; callers must only use it when a stream separator exists.
- `convert_to_nt_pathname()` uses a simple prefix comparison against `share->path`; correctness depends on canonical path handling before this helper is called.
- `ksmbd_convert_dir_info_name()` allocates `sz` bytes but writes two trailing NUL bytes at `conv[*conv_len]` and `conv[*conv_len + 1]`; callers depend on conversion length staying within the overallocated buffer.
- Wildcard matching intentionally does not implement full DOS wildcard semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/misc.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/misc.h

This header declares common ksmbd helper APIs implemented by `misc.c` and, under `CONFIG_PROC_FS`, proc helper APIs implemented by `proc.c`.

Declared utility APIs:
- Pattern and filename parsing:
  - `match_pattern()`
  - `ksmbd_validate_filename()`
  - `parse_stream_name()`
- Path conversion:
  - `convert_to_nt_pathname()`
  - `ksmbd_conv_path_to_unix()`
  - `ksmbd_strip_last_slash()`
  - `ksmbd_conv_path_to_windows()`
  - `ksmbd_casefold_sharename()`
  - `ksmbd_extract_sharename()`
  - `convert_to_unix_name()`
- Metadata formatting:
  - `get_nlink()`
  - `ksmbd_convert_dir_info_name()`
- Time conversion:
  - `NTFS_TIME_OFFSET`
  - `ksmbd_NTtimeToUnix()`
  - `ksmbd_UnixTimeToNT()`
  - `ksmbd_systime()`

Proc-related definitions under `CONFIG_PROC_FS`:
- `struct ksmbd_const_name`
- `ksmbd_proc_init()`
- `ksmbd_proc_cleanup()`
- `ksmbd_proc_reset()`
- `ksmbd_proc_create()`
- `ksmbd_proc_show_flag_names()`
- `ksmbd_proc_show_const_name()`

No-proc stubs:
- If `CONFIG_PROC_FS` is disabled, init/cleanup/reset become no-op inline functions.

Role:
- Shared interface for protocol handlers, VFS helpers, share handling, and optional proc reporting.

Risk areas:
- The proc helper declarations are only available under `CONFIG_PROC_FS`; code using `ksmbd_proc_create()` or proc format helpers must be similarly guarded or conditionally compiled.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/misc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/ndr.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/ndr.c

This file implements a small NDR-like encoder/decoder used for ksmbd extended attribute blobs, including DOS attributes, POSIX ACL metadata, and v4 NT ACL blobs.

Internal helpers:
- `ndr_get_field()`: returns `n->data + n->offset`.
- `try_to_realloc_ndr_blob()`: grows `n->data` by 1024 bytes beyond the requested write area using `krealloc()`, then zeros 1024 bytes from the current offset.
- Write helpers:
  - `ndr_write_int16()`
  - `ndr_write_int32()`
  - `ndr_write_int64()`
  - `ndr_write_bytes()`
  - `ndr_write_string()`
- Read helpers:
  - `ndr_read_string()`
  - `ndr_read_bytes()`
  - `ndr_read_int16()`
  - `ndr_read_int32()`
  - `ndr_read_int64()`

Encoding/decoding:
- `ndr_encode_dos_attr()`
  - Allocates a 1024-byte blob.
  - Encodes DOS attribute xattr formats for version 3 and version 4.
  - Version 3 includes hex string, version fields, flags, attributes, EA size, size, allocation size, create time, and change time.
  - Version 4 encodes empty string, version fields, flags, attributes, inode time, and create time.

- `ndr_decode_dos_attr()`
  - Parses the encoded string and version fields.
  - Supports versions 3 and 4.
  - Verifies the duplicate version field matches.
  - Extracts attributes and relevant timestamps while skipping unused fields.

- `ndr_encode_posix_acl_entry()`
  - Encodes ACL entry count and entry records.
  - Aligns entry payloads to 8 bytes.
  - Writes type twice, optional uid/gid for user/group entries, and permission bits.

- `ndr_encode_posix_acl()`
  - Allocates a 1024-byte blob.
  - Writes reference IDs for access/default ACLs.
  - Encodes mapped inode uid/gid and mode.
  - Appends access ACL and default ACL entries when present.

- `ndr_encode_v4_ntacl()`
  - Allocates a 2048-byte blob.
  - Encodes version, level, reference id, hash type, 64-byte security descriptor hash, description, timestamp, POSIX ACL hash, and raw security descriptor buffer.

- `ndr_decode_v4_ntacl()`
  - Validates version 4 and duplicate version field.
  - Reads level/ref id/hash fields.
  - Reads and validates a 10-byte description prefix against `posix_acl`.
  - Allocates and copies remaining data as the security descriptor buffer.

Declared but absent here:
- `ndr.h` declares `ndr_encode_v3_ntacl()`, but this file does not implement it. In the searched server tree, only `ndr_encode_v4_ntacl()` was found as an implementation.

Dependencies:
- Uses `xattr_dos_attrib`, `xattr_smb_acl`, and `xattr_ntacl` structures from ksmbd xattr/ACL definitions.
- Uses idmapped mount helpers for UID/GID encoding in POSIX ACL blobs.

Risk areas:
- Write helpers reallocate when `n->length <= n->offset + size`; exact-boundary writes trigger growth, which is conservative.
- `try_to_realloc_ndr_blob()` increases `n->length` by exactly 1024 regardless of `sz`, while `krealloc()` requests `offset + sz + 1024`; length accounting can understate the allocated size for large writes.
- Encoder error paths return without freeing `n->data`; callers must free partial blobs after failures.
- Decoder inputs are xattr blobs and must be treated as untrusted; bounds checks are present in primitive readers, but higher-level validation is minimal.
- `ndr_decode_v4_ntacl()` calls `ndr_read_bytes(n, acl->desc, 10)` without checking that return value before `strncmp()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/ndr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/ndr.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/ndr.h

This header declares the ksmbd NDR blob cursor and encoder/decoder APIs for filesystem xattrs.

Definitions:
- `struct ndr`
  - `data`: backing byte buffer.
  - `offset`: current read/write offset.
  - `length`: tracked buffer/input length.
- `NDR_NTSD_OFFSETOF`: constant `0xA0`.

Declared APIs:
- DOS attributes:
  - `ndr_encode_dos_attr()`
  - `ndr_decode_dos_attr()`
- POSIX ACL metadata:
  - `ndr_encode_posix_acl()`
- NT ACL blobs:
  - `ndr_encode_v4_ntacl()`
  - `ndr_encode_v3_ntacl()`
  - `ndr_decode_v4_ntacl()`

Role:
- Shared contract between ksmbd VFS/xattr code and `ndr.c`.

Risk areas:
- The header declares `ndr_encode_v3_ntacl()`, but the implementation is not present in `ndr.c` or the searched SMB server tree. If referenced by future code, this would become a link-time issue unless implemented elsewhere.
- `struct ndr` exposes mutable cursor fields directly; callers must initialize `data`, `offset`, and `length` according to encode/decode mode.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/ndr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/ntlmssp.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/ntlmssp.h

This header defines NTLMSSP constants, flags, wire-format message structures, AV pair identifiers, and per-session NTLMSSP authentication state used by ksmbd authentication code.

Constants:
- `NTLMSSP_SIGNATURE`: `"NTLMSSP"`.
- `TGT_Name`: `"KSMBD"`.
- Key and ciphertext sizes:
  - `CIFS_CRYPTO_KEY_SIZE`: 8
  - `CIFS_KEY_SIZE`: 40
  - `CIFS_ENCPWD_SIZE`: 16
  - `CIFS_CPHTXT_SIZE`: 16
- Message types:
  - `NtLmNegotiate`
  - `NtLmChallenge`
  - `NtLmAuthenticate`
  - `UnknownMessage`

Negotiate flags:
- Defines NTLMSSP flags for Unicode/OEM strings, target request/type, signing/sealing, LM/NTLM choices, anonymous auth, domain/workstation supplied, always-sign, extended security, target info, version, 128-bit, key exchange, and 56-bit support.

Enums:
- `enum av_field_type`
  - AV pair IDs from `NTLMSSP_AV_EOL` through `NTLMSSP_AV_CHANNEL_BINDINGS`.

Wire structures:
- `struct security_buffer`
  - Length, maximum length, and buffer offset.
- `struct target_info`
  - Type, length, and variable content.
- `struct negotiate_message`
  - Type 1 client negotiate message.
- `struct challenge_message`
  - Type 2 server challenge message.
- `struct authenticate_message`
  - Type 3 client authenticate message.
- `struct ntlmv2_resp`
  - NTLMv2 response blob prefix.

Session state:
- `struct ntlmssp_auth`
  - Whether session key is per SMB session.
  - Client and connection flags.
  - Challenge ciphertext.
  - NTLMSSP crypto key.

Role:
- Protocol wire-format header for authentication exchange; included by session management and auth implementation.

Risk areas:
- All wire structures are `__packed`; code must use little-endian helpers and avoid assuming natural alignment.
- Security buffer offsets and lengths are client-controlled in incoming messages and require strict validation in parser code.
- `sizeof(NTLMSSP_SIGNATURE)` includes the trailing NUL, matching the structures here; parser code must be consistent with that convention.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/ntlmssp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/oplock.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/oplock.c

This file implements ksmbd oplock and SMB2/SMB3 lease handling: allocation, reference management, lease tables, break notification, grant decisions on open, parent lease breaks, create-context parsing, durable-handle validation, and response context construction.

Global state:
- `lease_table_list`: global list of lease tables keyed by client GUID.
- `lease_list_lock`: rwlock protecting the global lease table list.

Object lifecycle:
- `alloc_opinfo()`
  - Allocates `struct oplock_info`, records session, gets a connection reference, initializes wait queues, list nodes, refcount, breaking counter, fid, tree id, and default level/state.
- `alloc_lease()`, `free_lease()`
  - Allocate and copy lease state from `lease_ctx_info`.
- `free_opinfo()` / `free_opinfo_rcu()`
  - Free oplock info via RCU and release the connection reference.
- `opinfo_get()`
  - RCU-safe lookup from `ksmbd_file->f_opinfo`.
- `opinfo_get_list()`
  - Gets first oplock info from an inode’s `m_op_list` under `ci->m_lock`.
- `opinfo_put()`
  - Atomic refcount release.
- `opinfo_add()`, `opinfo_del()`
  - Add/remove oplock info from inode list; lease entries are also removed from lease tables.
- `opinfo_count()`, `opinfo_count_inc()`, `opinfo_count_dec()`
  - Track ordinary oplocks versus stream oplocks through inode counters.

Lease-table management:
- `alloc_lease_table()`
  - Allocates a table for a connection client GUID.
- `lease_add_list()`, `lease_del_list()`
  - Add/remove opinfo from a lease table’s RCU list.
- `add_lease_global_list()`
  - Reuses an existing client-GUID lease table or publishes a new one.
- `destroy_lease_table()`
  - Destroys all lease tables, or only tables matching a connection’s client GUID.

State transitions:
- `opinfo_write_to_read()`: batch/exclusive to level II.
- `opinfo_read_handle_to_read()`: read+handle lease to read.
- `opinfo_write_to_none()`: batch/exclusive to none.
- `opinfo_read_to_none()`: level II to none.
- `lease_read_to_write()`: upgrade read lease to include write caching and set oplock level accordingly.
- `lease_none_upgrade()`: upgrade a none lease to a requested lease state and derive oplock level.
- `set_oplock_level()` dispatches grant to write/read/none helpers.

Break handling:
- `wait_for_break_ack()`
  - Waits up to `OPLOCK_WAIT_TIME` for state to become none or closing; timeout forces lease/oplock to none.
- `oplock_break_pending()`
  - Serializes concurrent breaks with `pending_break` bit wait/wake.
- `smb2_oplock_break_noti()` and `__smb2_oplock_break_noti()`
  - Build and send SMB2 oplock break notifications.
- `smb2_lease_break_noti()` and `__smb2_lease_break_noti()`
  - Build and send SMB2 lease break notifications.
- `wait_lease_breaking()`
  - Waits briefly for lease break counter to drain.
- `oplock_break()`
  - Core break state machine. Determines lease new state, optionally sends interim response, marks ACK wait, sends notification, wakes pending breakers, and waits for lease-breaking completion.

Open/grant path:
- `same_client_has_lease()`
  - Finds an existing lease with the same client GUID and lease key on the same inode; may upgrade the existing lease state.
- `find_same_lease_key()`
  - Rejects reuse of the same lease key by the same client on another file.
- `smb_grant_oplock()`
  - Main grant decision on file open.
  - Handles directory lease restrictions, lease allocation, no-existing-oplock fast path, attribute-only/truncate cases, same-client lease reuse, previous oplock breaking, share-mode failures, mixed lease/oplock cases, lease-table preallocation, inode-list publication, global lease-list publication, and `fp->f_opinfo` RCU assignment.

Break-all helpers:
- `smb_break_all_write_oplock()`
  - Breaks a batch/exclusive oplock to level II.
- `smb_break_all_levII_oplock()`
  - Breaks level II oplocks/read leases to none, with same-lease-owner skip logic.
- `smb_break_all_oplock()`
  - Breaks both write and level II oplocks.

Parent lease handling:
- `smb_send_parent_lease_break_noti()`
  - For v2 leases, breaks leases on the parent directory unless the request supplies a matching parent lease key.
- `smb_lazy_parent_lease_break_close()`
  - On close, lazily breaks parent directory leases for v2 lease cases.

Create-context helpers:
- `smb2_map_lease_to_oplock()`
  - Maps lease state bits to SMB2 oplock level.
- `create_lease_buf()`
  - Builds lease response context for v1 or v2 lease.
- `parse_lease_state()`
  - Finds and parses the `RqLs` create context into `lease_ctx_info`.
- `smb2_find_context_vals()`
  - Iterates create contexts, validating alignment, offsets, names, data lengths, and `Next`.
- Response builders:
  - `create_durable_rsp_buf()`
  - `create_durable_v2_rsp_buf()`
  - `create_mxac_rsp_buf()`
  - `create_disk_id_rsp_buf()`
  - `create_posix_rsp_buf()`

Lookup and durable reconnect:
- `lookup_lease_in_table()`
  - Finds a lease by client GUID and lease key while requiring active break-related state and handle/write caching.
- `smb2_check_durable_oplock()`
  - Validates durable reconnect ownership, client GUID, lease key, handle-caching state, lease version, and name reconnect validity.

Concurrency:
- Uses RCU for `fp->f_opinfo` and lease-list traversal.
- Uses `ci->m_lock` for inode oplock lists.
- Uses `lease_list_lock` for global lease table list.
- Uses per-lease-table spinlocks for `lease_list`.
- Uses wait queues and atomic counters for break acknowledgement and lease-breaking coordination.
- Uses connection refcounts to keep notification targets alive.

Risk areas:
- This is one of the most concurrency-sensitive ksmbd files: oplock info is published through both inode lists and RCU file pointers, while lease entries are also globally visible.
- `smb_grant_oplock()` intentionally preallocates lease tables and sets `opinfo->o_fp` before publication; comments indicate this order prevents NULL dereference by concurrent lease-key scans.
- Break state transitions involve timeouts that force state to none; changing timeout or ACK handling can affect client cache coherency and data consistency.
- `create_durable_v2_rsp_buf()` zeroes `sizeof(struct create_durable_rsp)` while using `struct create_durable_rsp_v2`; this may be intentional layout overlap, but it is a notable structure-size dependency.
- `create_disk_id_rsp_buf()` uses `offsetof(struct create_mxac_rsp, Name)` for `create_disk_id_rsp`; this cross-structure offset dependency should remain layout-compatible.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/oplock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/oplock.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/oplock.h

This header defines oplock/lease state structures and declares the public oplock, lease, durable-handle, and create-context helper APIs.

Constants:
- `OPLOCK_WAIT_TIME`: 35 seconds.
- Oplock internal states:
  - `OPLOCK_STATE_NONE`
  - `OPLOCK_ACK_WAIT`
  - `OPLOCK_CLOSING`
- Break transition flags:
  - `OPLOCK_WRITE_TO_READ`
  - `OPLOCK_READ_HANDLE_TO_READ`
  - `OPLOCK_WRITE_TO_NONE`
  - `OPLOCK_READ_TO_NONE`

Structures:
- `struct lease_ctx_info`
  - Parsed create-context lease request: lease key, requested state, flags, duration, parent lease key, epoch, version, directory flag.
- `struct lease_table`
  - Client GUID, list of leases, global-list node, spinlock.
- `struct lease`
  - Granted/current lease state, pending new state, flags, duration, parent key, version, epoch, directory flag, owning lease table.
- `struct oplock_info`
  - Connection/session/work/file references, oplock level/state, pending break bit, fid/tid, breaking count, refcount, lease flag, truncate flag, lease pointer, inode/lease list entries, wait queues, RCU head.
- `struct lease_break_info`
  - Current/new lease state, epoch, lease key for notification.
- `struct oplock_break_info`
  - Oplock level, truncate flag, fid for notification.

Declared APIs:
- Grant/break/lifecycle:
  - `smb_grant_oplock()`
  - `smb_break_all_levII_oplock()`
  - `smb_break_all_oplock()`
  - `close_id_del_oplock()`
  - `opinfo_get()`
  - `opinfo_put()`
- State transition helpers:
  - `opinfo_write_to_read()`
  - `opinfo_read_handle_to_read()`
  - `opinfo_write_to_none()`
  - `opinfo_read_to_none()`
  - `lease_read_to_write()`
- Lease helpers:
  - `create_lease_buf()`
  - `parse_lease_state()`
  - `smb2_map_lease_to_oplock()`
  - `lookup_lease_in_table()`
  - `find_same_lease_key()`
  - `destroy_lease_table()`
  - parent lease break helpers
- Create context response helpers:
  - Durable handle, durable v2, maximal access, disk id, POSIX context builders.
- Durable reconnect:
  - `smb2_check_durable_oplock()`.

Role:
- Shared contract for SMB2 create/open, close, write/truncate, lease break ACK, durable reconnect, and create-context response paths.

Risk areas:
- `struct oplock_info` lifetime depends on RCU plus atomic refcounting; callers must pair `opinfo_get()` with `opinfo_put()`.
- `pending_break`, `breaking_cnt`, `oplock_q`, and `oplock_brk` are tightly coupled with the implementation’s break state machine.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/oplock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/proc.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/proc.c

This file implements `/proc/fs/ksmbd` reporting and percpu counters for ksmbd when proc support is built.

Global state:
- `ksmbd_proc_fs`: root proc directory entry.
- `ksmbd_counters`: global ksmbd percpu counters.

Functions:
- `ksmbd_proc_create()`
  - Creates a read-only single-data proc file under `/proc/fs/ksmbd`.

- `proc_show_ksmbd_stats()`
  - Emits server metadata:
    - server string
    - NetBIOS name
    - workgroup
    - min/max protocol
    - flags
    - fake filesystem capabilities
    - session count
    - tree connect count
    - read bytes
    - written bytes
  - Emits SMB2 command counters for all request slots from negotiate through oplock break.

- `ksmbd_proc_cleanup()`
  - Removes proc tree and destroys all percpu counters.
  - Sets `ksmbd_proc_fs` to NULL.

- `ksmbd_proc_reset()`
  - Resets all counters to zero.

- `ksmbd_proc_init()`
  - Creates `/proc/fs/ksmbd`.
  - Creates `sessions` directory.
  - Initializes all percpu counters.
  - Creates `server` proc file.
  - Resets counters.
  - Cleans up on partial failure.

Data tables:
- `smb2_process_req[]`
  - Maps SMB2 command constants to human-readable names for proc output.

Dependencies:
- `server_conf` and server string accessors from `server.c`.
- Protocol-name helper `ksmbd_get_protocol_string()`.
- Counter helpers from `stats.h`.

Risk areas:
- Counter initialization and cleanup are coupled to proc directory creation; partial initialization failure uses `ksmbd_proc_cleanup()`.
- The command-name table size is `KSMBD_COUNTER_MAX_REQS`; it must stay aligned with counter indices and SMB2 command ordering.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/server.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/server.c

This file is ksmbd’s main module and request-processing hub. It owns global server configuration, sysfs control, module lifecycle, transport callbacks, request dispatch, response signing/encryption, and server reset/init work.

Global state:
- `ksmbd_debug_types`: debug mask.
- `server_conf`: global `struct ksmbd_server_config`.
- `ctrl_lock`: serializes control work and hard reset.

Configuration helpers:
- `___server_conf_set()`
  - Replaces one of the global config strings.
- `ksmbd_set_netbios_name()`, `ksmbd_set_server_string()`, `ksmbd_set_work_group()`.
- `ksmbd_netbios_name()`, `ksmbd_server_string()`, `ksmbd_work_group()`.
- `server_conf_init()`
  - Sets state to starting, initializes protocol bounds, auth mechanisms, signing defaults, and max inflight requests.
- `server_conf_free()`
  - Frees config strings.

Request processing:
- `check_conn_state()`
  - Detects exiting/reconnect-needed connection and sets disconnected status.
- `__process_request()`
  - Verifies SMB message.
  - Extracts command.
  - Bounds-checks command index.
  - Rejects unimplemented commands.
  - Verifies request signature when required.
  - Dispatches command handler.
  - Increments request counters.
  - Handles positive return values as chained/AndX-style follow-up commands.
- `__handle_ksmbd_work()`
  - Handles transform-header decryption.
  - Allocates response buffer.
  - Initializes response header.
  - Checks user session and tree connection.
  - Processes one or more chained SMB2 messages.
  - Grants response credits.
  - Signs response when session/signing rules require it.
  - Releases tree/session references.
  - Updates SMB 3.1.1 preauth response hash.
  - Encrypts response when needed.
  - Writes response.
- `handle_ksmbd_work()`
  - Worker entry: increments request-served stat, handles request, dequeues/frees work, decrements connection request count.
- `queue_ksmbd_work()`
  - Initializes SMB dialect/server state for connection, allocates work, transfers request buffer ownership, queues work.
- `ksmbd_server_process_request()`
  - Transport callback wrapper.
- `ksmbd_server_terminate_conn()`
  - Deregisters sessions and destroys connection lease table.
- `ksmbd_server_tcp_callbacks_init()`
  - Registers process and terminate callbacks with connection layer.

Control work:
- `server_ctrl_handle_init()`
  - Resets proc counters, initializes connection transport, marks server running.
- `server_ctrl_handle_reset()`
  - Soft-resets IPC, destroys transport, stops durable scavenger, frees and reinitializes server config, marks starting.
- `server_ctrl_handle_work()`
  - Executes init/reset work under `ctrl_lock` and drops module reference.
- `server_queue_ctrl_init_work()`, `server_queue_ctrl_reset_work()`
  - Queue control work on `system_long_wq`.

Sysfs control:
- Class: `ksmbd-control`.
- `stats_show()`
  - Emits stats format version, state string, TCP port, and IPC activity time.
- `kill_server_store()`
  - Accepts `hard`, marks resetting, and performs reset synchronously under `ctrl_lock`.
- `debug_show()` / `debug_store()`
  - Show and toggle debug classes: `smb`, `auth`, `vfs`, `oplock`, `ipc`, `conn`, `rdma`, or all.

Module lifecycle:
- `ksmbd_server_init()`
  - Registers class.
  - Initializes proc and session proc support.
  - Registers TCP callbacks.
  - Initializes server config, work pools, file cache, IPC, global file table, inode hash, crypto, workqueue, connection workqueue.
  - Has staged error unwinding.
- `ksmbd_server_shutdown()`
  - Marks shutting down and destroys proc, sysfs class, workqueue, IPC, transport, crypto, global file table, leases, work pool, file cache, and config.
- `ksmbd_server_exit()`
  - Calls shutdown, waits for RCU callbacks, destroys connection workqueue, releases inode hash.

Risk areas:
- Request processing is reference-sensitive: tree connection and session references are released in the send path after possible encryption/signing.
- Error paths before `send:` must leave enough response state for `ksmbd_conn_write()` or intentionally return without writing.
- `kill_server_store()` directly calls reset handler while holding `ctrl_lock`; it mirrors queued reset logic but executes synchronously.
- Module teardown ordering matters because connection puts can defer release onto `ksmbd_conn_wq` after RCU callbacks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/server.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/server.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/server.h

This header defines global ksmbd server state/configuration and declares server configuration/control APIs.

Enums:
- Server state:
  - `SERVER_STATE_STARTING_UP`
  - `SERVER_STATE_RUNNING`
  - `SERVER_STATE_RESETTING`
  - `SERVER_STATE_SHUTTING_DOWN`
- Config string slots:
  - `SERVER_CONF_NETBIOS_NAME`
  - `SERVER_CONF_SERVER_STRING`
  - `SERVER_CONF_WORK_GROUP`

Structure:
- `struct ksmbd_server_config`
  - Global feature flags and server state.
  - Signing policy.
  - Min/max protocol.
  - TCP port.
  - IPC timeout/activity.
  - Deadtime.
  - Fake filesystem capabilities for shares.
  - Domain SID.
  - Authentication mechanisms.
  - Connection and request limits.
  - Config strings.
  - Durable-handle scavenger task.
  - Bind-interface-only flag.

Global:
- `extern struct ksmbd_server_config server_conf`.

Declared APIs:
- String setters/getters:
  - `ksmbd_set_netbios_name()`
  - `ksmbd_set_server_string()`
  - `ksmbd_set_work_group()`
  - `ksmbd_netbios_name()`
  - `ksmbd_server_string()`
  - `ksmbd_work_group()`
- State helpers:
  - `ksmbd_server_running()`
  - `ksmbd_server_configurable()`
- Control work:
  - `server_queue_ctrl_init_work()`
  - `server_queue_ctrl_reset_work()`

Role:
- Shared server-global contract for transport IPC, request dispatch, proc reporting, sysfs control, and dialect initialization.

Risk areas:
- `server_conf` is global mutable state; users rely on `READ_ONCE()` state checks but most other fields are accessed directly.
- `ksmbd_server_configurable()` allows configuration before resetting or shutdown; callers must respect this gate.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/server.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/smb2misc.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/smb2misc.c

This file validates incoming SMB2-family request framing, fixed structure sizes, variable data areas, compound message lengths, and credit charges. It also routes SMB2 negotiate to the common negotiate handler.

Validation tables:
- `smb2_req_struct_sizes[]`
  - Expected `StructureSize2` per SMB2 command.
  - Includes special handling note for oplock/lease break.
- `has_smb2_data_area[]`
  - Marks which SMB2 commands have variable data areas that need offset/length validation.

Functions:
- `check_smb2_hdr()`
  - Rejects packets marked `SMB2_FLAGS_SERVER_TO_REDIR`, since incoming requests must not be server-to-client responses.

- `smb2_get_data_area_len()`
  - Extracts variable data offset/length by command:
    - session setup security buffer
    - tree connect path
    - create name and create contexts
    - query/set info buffers
    - read/write channel/data buffers
    - query directory filename
    - lock element array
    - ioctl input buffer
  - Caps offsets over 4096 and total offset+length over `MAX_STREAM_PROT_LEN`.

- `smb2_calc_size()`
  - Computes expected SMB2 PDU size from SMB2 header, fixed structure size, and variable data area.
  - Adjusts lock request size because its structure size includes one lock element.
  - Rejects variable data that overlaps the fixed area.

- Request/response length helpers:
  - `smb2_query_info_req_len()`
  - `smb2_set_info_req_len()`
  - `smb2_read_req_len()`
  - `smb2_write_req_len()`
  - `smb2_query_dir_req_len()`
  - `smb2_ioctl_req_len()`
  - `smb2_ioctl_resp_len()`

- `smb2_validate_credit_charge()`
  - Computes required credit charge from the larger of request length and expected response length.
  - Requires at least one credit.
  - Rejects credit charge above connection max credits.
  - Under `credits_lock`, rejects requests exceeding granted or outstanding credits, otherwise increments outstanding credits.

- `ksmbd_smb2_check_message()`
  - Validates compound `NextCommand` bounds.
  - Adjusts current length for compounded or offset SMB2 message.
  - Rejects response-direction messages, bad SMB2 header structure size, invalid command index, and bad command fixed structure size.
  - Handles special oplock break structure sizes.
  - Ensures fixed request structure fits.
  - Compares calculated length against actual length, allowing:
    - one-byte implied BCC variance
    - 8-byte compound padding
    - negotiate validation deferral
    - up to 8 bytes of padding seen from some clients
  - Validates large-MTU credit charge when enabled.

- `smb2_negotiate_request()`
  - Calls `ksmbd_smb_negotiate_common()` for SMB2 negotiate.

Dependencies:
- SMB2 PDU structures and constants.
- Connection credit state.
- Common negotiate path.

Risk areas:
- This is a primary network-input validation boundary; offset, length, and credit rules protect later command handlers.
- Credit accounting increments `outstanding_credits` during validation; downstream response-credit handling must balance this correctly.
- Create-context bounds are only partially checked here; `smb2_find_context_vals()` performs deeper create-context validation later.
- Accepted padding exceptions are compatibility-sensitive; tightening them can break clients, loosening them can expose parser confusion.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/smb2misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/smb2ops.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/smb2ops.c

This file defines SMB2/SMB3 dialect-specific server value tables, operation tables, command dispatch table, and initialization helpers for negotiated SMB dialects.

Dialect value tables:
- `smb21_server_values`
  - SMB 2.1 protocol id, large MTU, SMB2 default I/O sizes, max credits, lock flags, header sizes, response sizes, create-context sizes.
- `smb30_server_values`
  - SMB 3.0 protocol id, SMB3 I/O/trans sizes, SMB3 create lease v2 and durable v2 sizes.
- `smb302_server_values`
  - SMB 3.0.2 values, durable v2 and persistent-handle support size fields.
- `smb311_server_values`
  - SMB 3.1.1 values, same core sizes as SMB3 with SMB 3.1.1 signing/encryption key hooks.

Operation tables:
- `smb2_0_server_ops`
  - SMB2 command extraction, request counter increment, response header/status/allocation/credits, user session/tree connect lookup, SMB2 signing checks and signing response.
- `smb3_0_server_ops`
  - SMB3 signing checks and response signing.
  - SMB 3.0 signing/encryption key generation.
  - Transform header detection, decrypt request, encrypt response.
- `smb3_11_server_ops`
  - SMB 3.1.1 signing/encryption key generation plus transform handling.

Command dispatch table:
- `smb2_0_server_cmds[]`
  - Maps SMB2 command indices to handlers:
    - negotiate
    - session setup
    - tree connect/disconnect
    - logoff
    - create
    - query info
    - query directory
    - close
    - echo
    - set info
    - read/write
    - flush
    - cancel
    - lock
    - ioctl
    - oplock break
    - change notify

Initialization helpers:
- `init_smb2_1_server()`
  - Assigns SMB 2.1 values/ops/commands, HMAC-SHA256 signing, optional leasing capability.
- `init_smb3_0_server()`
  - Assigns SMB 3.0 values/ops/commands, AES-CMAC signing.
  - Enables leasing/directory leasing, encryption, and multichannel based on server flags and client capabilities.
- `init_smb3_02_server()`
  - Similar to SMB3.0, also enables persistent handles when durable-handle flag is set.
- `init_smb3_11_server()`
  - Assigns SMB 3.1.1 values/ops/commands, AES-CMAC signing, leasing, multichannel, durable/persistent handle capability, and initializes preauth session list.
- Runtime tuners:
  - `init_smb2_max_read_size()`
  - `init_smb2_max_write_size()`
  - `init_smb2_max_trans_size()`
  - `init_smb2_max_credits()`

Role:
- Dialect negotiation support: after a client dialect is selected, these helpers attach the correct capabilities, limits, operation hooks, signing/encryption algorithms, and command table to `ksmbd_conn`.

Risk areas:
- The dialect value tables are static globals, and init functions mutate `conn->vals->req_capabilities` by ORing feature bits. Because `conn->vals` points at the shared table, capabilities enabled for one connection can persist for later connections unless reset elsewhere.
- Runtime max-size tuners also mutate shared dialect tables, intentionally affecting subsequent connections globally.
- Command table is shared for SMB2 through SMB3.1.1; dialect-specific behavior is mainly in `conn->ops` and `conn->vals`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/smb2ops.c -->