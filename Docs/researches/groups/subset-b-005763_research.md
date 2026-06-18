# Research: subset-b-005763

Grouped research for SMB server management, miscellaneous helpers, NDR xattr encoding, NTLMSSP message layout, oplock/lease handling, server lifecycle, and SMB2 dialect/validation glue.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/user_session.h -->
# sources/distributed-fs/ceph-client/fs/smb/server/mgmt/user_session.h

## Purpose
Declares the in-kernel SMB session-management contract for ksmbd. The header defines the per-session state container, preauthentication session records, multichannel state, and public helpers used by SMB2 session setup, tree connect management, RPC pipe tracking, procfs reporting, and connection teardown.

## Important APIs, Types, and Functions
- `struct channel` binds an SMB3 signing key to a `struct ksmbd_conn`, supporting multichannel sessions where each channel can have connection-specific signing material.
- `struct preauth_session` stores SMB 3.1.1 preauthentication hash material, the preauth session id, and list linkage on the connection preauth table.
- `struct ksmbd_session` is the core authenticated session object. It tracks `id`, negotiated `dialect`, `ClientGUID`, authenticated `ksmbd_user`, sequence number, feature flags, signing/encryption booleans, authentication state, preauth hash, session key, channel/tree/rpc xarrays, tree id allocator, SMB3 signing/encryption keys, file table, activity timestamp, locks, optional procfs entry, and atomic reference count.
- Inline flag helpers `test_session_flag()`, `set_session_flag()`, and `clear_session_flag()` manipulate `sess->flags`; currently `CIFDS_SESSION_FLAG_SMB2` marks SMB2-family sessions.
- Lifecycle and lookup APIs include `ksmbd_smb2_session_create()`, `ksmbd_session_destroy()`, `ksmbd_session_lookup()`, `ksmbd_session_lookup_slowpath()`, `ksmbd_session_lookup_all()`, `is_ksmbd_session_in_connection()`, `ksmbd_session_register()`, `ksmbd_sessions_deregister()`, `__session_lookup()`, `destroy_previous_session()`, and refcount helpers `ksmbd_user_session_get()/put()`.
- Preauth APIs `ksmbd_preauth_session_alloc()` and `ksmbd_preauth_session_lookup()` serve SMB 3.1.1 negotiation/session setup.
- Tree connection id APIs `ksmbd_acquire_tree_conn_id()` and `ksmbd_release_tree_conn_id()` wrap the per-session `ida`.
- RPC helpers `ksmbd_session_rpc_open()`, `ksmbd_session_rpc_close()`, and `ksmbd_session_rpc_method()` manage session-scoped named-pipe/RPC handles.
- `create_proc_sessions()` is exposed for procfs session reporting initialization.

## Control Flow
Session setup code creates a `ksmbd_session`, registers it with a connection, fills user/security/key fields, and later tree connect code attaches tree connections through `tree_conns` under `tree_conns_lock`. Request dispatch paths look up and reference sessions before processing commands, then release references after response handling. Connection teardown calls deregistration, which ultimately destroys sessions, file tables, tree connections, RPC handles, and procfs entries. SMB 3.1.1 paths allocate preauth sessions before authentication is complete and promote or discard them during final session setup.

## State and Persistence
All state is in memory and scoped to the kernel module lifetime. `xarray` maps store channels, tree connections, and RPC handles; `ida` generates tree connect ids; `file_table` owns open files for the session. Cryptographic state includes the raw session key and SMB3 derived signing/encryption/decryption keys. `last_active` supports timeout/scavenging logic. Reference counting with `atomic_t refcnt` is the lifetime guard, while `rw_semaphore` locks protect channels, tree connections, and RPC handles. No durable on-disk persistence is declared here.

## Dependencies and Integration Points
The header depends on Linux `hashtable`, `xarray`, `ida`, list, semaphore, procfs, and atomic primitives. It imports SMB constants from `smb_common.h` and NTLMSSP key-size constants from `ntlmssp.h`. It integrates with `connection`, `tree_connect`, `auth`, `smb2pdu`, `server`, and procfs code. `server.c` calls `ksmbd_sessions_deregister()` on connection termination and `create_proc_sessions()` at module init; request handling calls session lookup and `ksmbd_user_session_put()` when done.

## Risks and Edge Cases
- Lifetime safety depends on every lookup taking a reference and every request path dropping it exactly once.
- Multichannel and tree connection maps require correct lock ordering against connection and session locks.
- Session key and SMB3 key buffers are long-lived secrets in kernel memory; cleanup must clear/free them carefully in the implementation.
- Preauth hash length is fixed at 64 bytes; dialect-specific hash algorithms must match this contract.
- `char ClientGUID[]` and key arrays are binary, not C strings, so call sites must use explicit lengths.

## Test Signals
Useful tests exercise SMB2/3 session setup and logoff, reconnect/destroy of previous sessions, multichannel association, tree connect/disconnect id reuse, SMB 3.1.1 preauth hash behavior, RPC open/close/method lookup, timeout/session teardown with open files, and procfs session output when `CONFIG_PROC_FS` is enabled. KASAN/KCSAN stress around disconnect while requests are in flight is especially relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/mgmt/user_session.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/misc.c -->
# sources/distributed-fs/ceph-client/fs/smb/server/misc.c

## Purpose
Implements general ksmbd helper routines for wildcard matching, filename and stream validation, share/path conversion, share name casefolding, directory entry name conversion, and NTFS/Unix time conversion. These helpers are used throughout request handling and VFS integration.

## Important APIs, Types, and Functions
- `match_pattern()` performs case-insensitive matching with `*` and `?` wildcards. It is a compact backtracking matcher and explicitly does not implement DOS wildcard semantics for `DOS_DOT`, `DOS_QM`, or `DOS_STAR`.
- `ksmbd_validate_filename()` rejects ASCII control characters and reserved wildcard/device-like characters through `is_char_allowed()`, returning `-ENOENT` on failure.
- `parse_stream_name()` splits an NTFS alternate data stream suffix from `filename`, validates the stream name, and classifies `$DATA` as `DATA_STREAM` or `$INDEX_ALLOCATION` as `DIR_STREAM`.
- `convert_to_nt_pathname()` converts a kernel `struct path` into a share-relative Windows pathname. It uses `d_path()`, verifies the absolute path has the configured share path prefix, allocates a returned buffer, and converts `/` to `\`.
- `get_nlink()` reports `st->nlink`, subtracting one for directories.
- `ksmbd_conv_path_to_unix()`, `ksmbd_conv_path_to_windows()`, and `ksmbd_strip_last_slash()` mutate path strings in place.
- `ksmbd_casefold_sharename()` lower/casefolds a share name using `utf8_casefold()` when Unicode support and a map are available, falling back to ASCII lowercasing.
- `ksmbd_extract_sharename()` returns the final backslash component of a UNC tree name, casefolded through `ksmbd_casefold_sharename()`.
- `convert_to_unix_name()` joins a share root path with a share-relative SMB path.
- `ksmbd_convert_dir_info_name()` converts directory entry names to UTF-16 using `smbConvertToUTF16()` and returns byte length via `conv_len`.
- `ksmbd_NTtimeToUnix()`, `ksmbd_UnixTimeToNT()`, and `ksmbd_systime()` convert between NT 100ns timestamps since 1601 and Unix `timespec64`.

## Control Flow
Path handling generally normalizes inbound SMB/Windows names to Unix separators, validates illegal characters, joins with a share root, and later converts kernel paths back to NT pathnames for responses. Stream parsing mutates the caller's filename by `strsep()` at the first colon and optionally parses a second colon-delimited stream type. Share lookup extracts and casefolds the UNC share component before configuration lookup. Time conversion uses the constant `NTFS_TIME_OFFSET` and handles negative NT-to-Unix deltas by avoiding signed division on 32-bit architectures.

## State and Persistence
This file keeps no global state. It allocates transient buffers with `KSMBD_DEFAULT_GFP`; callers own returned buffers from conversion and casefold helpers. Path strings passed to separator/strip/stream functions may be modified in place. `ksmbd_systime()` reads wall-clock time but does not persist it.

## Dependencies and Integration Points
The file depends on Linux VFS path APIs, xattrs, Unicode support, NLS conversion, and generic string helpers. It uses `ksmbd_share_config` for share roots and `ksmbd_dir_info`/NLS data for directory enumeration output. It integrates with VFS open/query paths, tree connect share lookup, directory listing, stream handling, and file information responses.

## Risks and Edge Cases
- `parse_stream_name()` calls `strchr(s_name, ':')` after `strsep()` without guarding `s_name` against `NULL`; callers must only invoke it when a colon-delimited stream component exists.
- `convert_to_nt_pathname()` uses simple prefix matching against `share->path`; a share path that is a prefix of another directory name requires upstream path containment guarantees.
- `ksmbd_casefold_sharename()` advances `cf_name` during ASCII lowercasing and returns `cf_name - cf_len`; this relies on `strscpy()` returning copied length and is easy to break if refactored.
- `ksmbd_convert_dir_info_name()` allocates `min(4 * name_len, PATH_MAX)` bytes and then writes two trailing NUL bytes at `conv_len` and `conv_len + 1`; conversion length must remain within allocation.
- Wildcard matching is not full SMB/DOS-compatible, so directory query semantics can diverge from Windows clients.

## Test Signals
Tests should cover wildcard cases with mixed case, trailing `*`, failed backtracking, and unsupported DOS wildcard forms; filenames containing control/reserved characters; alternate stream parsing for valid `$DATA`, `$INDEX_ALLOCATION`, invalid stream types, and missing stream names; share names with Unicode and ASCII casefolding; path conversions at share root and nested files; UTF-16 directory name conversion with long and non-ASCII names; and timestamp round trips before/after 1970 on 32-bit and 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/misc.h -->
# sources/distributed-fs/ceph-client/fs/smb/server/misc.h

## Purpose
Declares the shared utility API implemented by `misc.c` and the procfs helper API used by ksmbd diagnostics. It also exposes constants for directory information alignment and NTFS timestamp conversion.

## Important APIs, Types, and Functions
- Path/name helpers: `match_pattern()`, `ksmbd_validate_filename()`, `parse_stream_name()`, `convert_to_nt_pathname()`, `ksmbd_conv_path_to_unix()`, `ksmbd_strip_last_slash()`, `ksmbd_conv_path_to_windows()`, `ksmbd_casefold_sharename()`, `ksmbd_extract_sharename()`, and `convert_to_unix_name()`.
- Directory info conversion: `KSMBD_DIR_INFO_ALIGNMENT`, forward-declared `struct ksmbd_dir_info`, and `ksmbd_convert_dir_info_name()`.
- Time conversion: `NTFS_TIME_OFFSET`, `ksmbd_NTtimeToUnix()`, `ksmbd_UnixTimeToNT()`, and `ksmbd_systime()`.
- Procfs support under `CONFIG_PROC_FS`: `struct ksmbd_const_name`, initialization/cleanup/reset helpers, `ksmbd_proc_create()`, and formatting helpers `ksmbd_proc_show_flag_names()` and `ksmbd_proc_show_const_name()`.
- No-op inline procfs stubs are provided when procfs is disabled.

## Control Flow
Callers include this header to access path, name, time, and procfs helpers without coupling to implementation files. Conditional compilation keeps procfs users source-compatible even when procfs support is absent.

## State and Persistence
The header declares no state directly. The procfs declarations refer to runtime proc entries and counters maintained elsewhere. Path/time helpers return caller-owned buffers or values and do not persist data.

## Dependencies and Integration Points
The header depends on procfs declarations only when configured and forward declares most ksmbd/VFS structures to avoid heavy includes. It integrates with share management, VFS operations, directory enumeration, server/proc initialization, and session reporting.

## Risks and Edge Cases
- Callers must honor ownership of returned allocated strings and must not pass immutable strings to in-place path mutators.
- Procfs formatting helpers are declared here but implemented outside `misc.c` in this tree, so build linkage depends on the procfs/session implementation being present when `CONFIG_PROC_FS` is enabled.
- `NTFS_TIME_OFFSET` is a raw arithmetic macro; changes to timestamp units must be kept synchronized with both conversion functions.

## Test Signals
Build both with and without `CONFIG_PROC_FS`; compile users of all forward-declared types; run path/name/time tests described for `misc.c`; and verify procfs helpers link and emit expected names in session/cache/server diagnostic files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/ndr.c -->
# sources/distributed-fs/ceph-client/fs/smb/server/ndr.c

## Purpose
Implements a small Network Data Representation encoder/decoder for ksmbd extended attributes, especially DOS attributes, POSIX ACL snapshots, and v4 NT ACL blobs stored in xattrs. It serializes primitive little-endian values and byte/string fields into dynamically grown `struct ndr` buffers and parses those buffers back with bounds checks.

## Important APIs, Types, and Functions
- Internal helpers `ndr_get_field()`, `try_to_realloc_ndr_blob()`, `ndr_write_int16/32/64()`, `ndr_write_bytes()`, `ndr_write_string()`, `ndr_read_string()`, `ndr_read_bytes()`, and `ndr_read_int16/32/64()` maintain `n->offset`, `n->length`, and `n->data`.
- `ndr_encode_dos_attr()` encodes `struct xattr_dos_attrib` version 3 or 4 fields, including hex attr string, duplicated version, flags, attrs, optional EA/size/allocation/change-time fields, and timestamps.
- `ndr_decode_dos_attr()` validates version 3 or 4, validates duplicate version, skips unsupported/unused fields, and extracts attributes plus creation/itime fields.
- `ndr_encode_posix_acl()` serializes optional access/default SMB ACL references, inode owner/group/mode translated through `mnt_idmap`, and ACL entries via `ndr_encode_posix_acl_entry()`.
- `ndr_encode_v4_ntacl()` serializes version, level/ref id, hash metadata, descriptor string, current time, POSIX ACL hash, and security descriptor bytes from `struct xattr_ntacl`.
- `ndr_decode_v4_ntacl()` validates version 4 and duplicate version, reads hash metadata, requires descriptor text beginning with `posix_acl`, allocates `acl->sd_buf`, and copies the remaining security descriptor bytes.

## Control Flow
Each public encoder initializes the supplied `struct ndr` to offset zero, allocates an initial zeroed buffer, then emits fields in the Samba-compatible xattr order. Primitive write helpers grow the blob by 1024 bytes when the next field would exceed the current allocation. Decoders reset offset to zero and advance sequentially, returning `-EINVAL` on truncation or malformed version data and `-ENOMEM` on allocation failure. POSIX ACL encoding writes reference ids for present ACLs, then owner/group/mode, then one or two ACL entry arrays.

## State and Persistence
The only mutable state is the caller-provided `struct ndr` buffer. Encoded blobs are intended for xattr persistence by VFS/xattr code outside this file. Decoding `v4_ntacl` allocates `acl->sd_buf`; callers must free it. On encode failure after allocation, this file does not free `n->data`; ownership remains with caller/error path.

## Dependencies and Integration Points
This file depends on ksmbd xattr structures from `glob.h`, Linux inode/idmap helpers, endianness helpers, and memory allocation. It integrates with VFS xattr get/set code for DOS attributes and ACL/security descriptors, and with SMB ACL conversion code that prepares `xattr_smb_acl` and `xattr_ntacl` structures.

## Risks and Edge Cases
- `try_to_realloc_ndr_blob()` always adds 1024 to `n->length` rather than setting it to the true allocation size `offset + sz + 1024`; when `sz` is much larger than 1024, subsequent bounds accounting can understate allocated space and force repeated reallocations or confuse callers.
- Encoders leak the already allocated `n->data` unless caller cleanup handles every error return.
- Several casts write directly to potentially unaligned `char *` offsets; architectures requiring aligned access rely on compiler/architecture tolerance or need unaligned helpers.
- `ndr_read_string()` copies `len` bytes without appending a NUL to `value`; local fixed buffers are safe only if initialized or if the consumed string already fits with terminator semantics.
- `ndr_decode_v4_ntacl()` ignores the return value from reading the 10-byte descriptor before `strncmp()`, so a truncated blob could leave stale descriptor contents unless the caller zeroed the structure.
- `ndr.h` declares `ndr_encode_v3_ntacl()` but this file does not define it, so another object or dead declaration must satisfy builds.

## Test Signals
Test round trips for DOS attr versions 3 and 4, malformed versions, duplicate-version mismatch, and truncated blobs at every field boundary. Exercise POSIX ACL encoding with no ACLs, access only, access plus default, user/group entries, high uid/gid idmapped values, and large ACL counts that trigger realloc. Validate v4 NTACL encode/decode with expected `posix_acl` descriptor, bad descriptor, truncated hash/descriptor/security descriptor, and caller cleanup under fault-injected `kzalloc`/`krealloc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/ndr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/ndr.h -->
# sources/distributed-fs/ceph-client/fs/smb/server/ndr.h

## Purpose
Defines the minimal NDR buffer abstraction and declares the xattr encode/decode functions used by ksmbd ACL and DOS attribute persistence.

## Important APIs, Types, and Functions
- `struct ndr` contains `char *data`, current `offset`, and current `length`.
- `NDR_NTSD_OFFSETOF` defines an offset constant for NT security descriptor-related encoding.
- Declared public functions: `ndr_encode_dos_attr()`, `ndr_decode_dos_attr()`, `ndr_encode_posix_acl()`, `ndr_encode_v4_ntacl()`, `ndr_encode_v3_ntacl()`, and `ndr_decode_v4_ntacl()`.

## Control Flow
Callers allocate a `struct ndr` on the stack or in another object, pass it to an encoder or decoder with domain-specific xattr structures, then consume or free `n->data` according to the operation. Encoders initialize and allocate the backing buffer; decoders expect `data` and `length` to describe an existing blob.

## State and Persistence
The header carries no global state. It defines the in-memory buffer that becomes the serialized xattr payload. Ownership and freeing of `data` are external to the header.

## Dependencies and Integration Points
The prototypes reference `struct xattr_dos_attrib`, `struct xattr_smb_acl`, `struct xattr_ntacl`, `struct mnt_idmap`, and `struct inode`, supplied by ksmbd and Linux VFS headers included by translation units. It is consumed by xattr/ACL VFS code.

## Risks and Edge Cases
- There is no include guard in the visible header, so multiple inclusion relies on source discipline or surrounding includes.
- `offset` and `length` are `int`, while buffer sizes are often `size_t`; very large blobs risk signed overflow if ever permitted upstream.
- `ndr_encode_v3_ntacl()` is declared but not implemented in the adjacent `ndr.c`; link coverage should verify whether another file provides it or the declaration is stale.
- Callers must know whether a function allocates `data` or expects it to be pre-populated.

## Test Signals
Compile all consumers with warnings enabled to catch missing declarations and duplicate inclusion problems. Link tests should verify every declared symbol is provided. Runtime tests should confirm encoder allocation ownership and decoder behavior on caller-provided buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/ndr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/ntlmssp.h -->
# sources/distributed-fs/ceph-client/fs/smb/server/ntlmssp.h

## Purpose
Defines NTLMSSP constants and packed wire structures used by ksmbd authentication. It describes negotiate, challenge, authenticate, AV pair, NTLMv2 response, and per-session NTLMSSP state layouts.

## Important APIs, Types, and Functions
- Constants define the NTLMSSP signature, server target name (`KSMBD`), crypto/session key sizes, encrypted password sizes, message type values, and all major NTLMSSP negotiate flags.
- `enum av_field_type` lists target-info AV pair ids such as NetBIOS/DNS names, flags, timestamp, target name, and channel bindings.
- `struct security_buffer` is the packed length/maximum/offset triple used throughout NTLMSSP messages.
- `struct target_info` represents variable-length AV pair entries.
- `struct negotiate_message`, `struct challenge_message`, and `struct authenticate_message` model NTLMSSP type 1, type 2, and type 3 packets, with flexible trailing string buffers where appropriate.
- `struct ntlmv2_resp` models the fixed prefix of an NTLMv2 response blob.
- `struct ntlmssp_auth` stores per-authentication/session state: whether the session key is per SMB session, client/server flags, challenge ciphertext, and server challenge key.

## Control Flow
Authentication code parses a type 1 negotiate message, records client flags, creates a type 2 challenge with target information and random challenge bytes, then validates a type 3 authenticate message. The negotiated flags select Unicode/OEM strings, signing/sealing, key exchange, NTLM version behavior, and target info handling. `ntlmssp_auth` carries the challenge and flags across the multi-step session setup exchange.

## State and Persistence
This header defines only packet and transient authentication state. `ntlmssp_auth` is per connection/session setup and is not persistent. Challenge material and ciphertext are sensitive and should be cleared by implementation cleanup paths.

## Dependencies and Integration Points
The structures are consumed by auth/session setup code and inform key sizes in `user_session.h`. Endianness is explicit with `__le16`/`__le32`/`__le64`, and `__packed` preserves wire layout. The resulting session key feeds SMB signing/encryption key derivation in SMB2/SMB3 code.

## Risks and Edge Cases
- Flexible trailing fields require strict bounds checking by parsers; this header only defines layout.
- `sizeof(NTLMSSP_SIGNATURE)` includes the NUL terminator, so message signature arrays are one byte longer than the visible string; parser/generator code must match existing convention.
- Security buffer offsets are client-controlled on inbound messages and must be validated against total blob length.
- Negotiate flag combinations can request unsupported signing/sealing/key exchange behavior; auth code must reject or downgrade consistently with SMB dialect policy.

## Test Signals
Tests should parse valid and malformed NTLMSSP type 1/2/3 blobs, out-of-range security buffers, Unicode and OEM names, NTLMv2 responses with AV pairs, anonymous/identify flags, signing/sealing negotiation, key exchange, and channel binding AV pairs. Fuzzing session setup security blobs is high value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/ntlmssp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/oplock.c -->
# sources/distributed-fs/ceph-client/fs/smb/server/oplock.c

## Purpose
Implements ksmbd SMB2 oplock and lease management. It grants requested oplocks/leases during create/open, tracks per-inode and per-client lease state, sends server-initiated oplock/lease break notifications, waits for acknowledgements, handles parent directory lease breaks, emits create-context response buffers, and validates durable handle reconnect oplock/lease requirements.

## Important APIs, Types, and Functions
- Global state: `lease_table_list` groups active leases by client GUID; `lease_list_lock` protects that list. Per-inode lists live in `ksmbd_inode::m_op_list` and are protected by `m_lock`.
- Allocation/lifetime helpers: `alloc_opinfo()`, `alloc_lease()`, `alloc_lease_table()`, `opinfo_get()`, `opinfo_get_list()`, `opinfo_put()`, `opinfo_add()`, `opinfo_del()`, `free_opinfo()` and RCU callback cleanup manage `struct oplock_info` references and publication through `fp->f_opinfo`.
- State transition APIs exported through the header: `opinfo_write_to_read()`, `opinfo_read_handle_to_read()`, `opinfo_write_to_none()`, `opinfo_read_to_none()`, and `lease_read_to_write()`.
- Grant helpers `grant_write_oplock()`, `grant_read_oplock()`, `grant_none_oplock()`, `set_oplock_level()`, and the public `smb_grant_oplock()` implement open-time policy.
- Break helpers `oplock_break_pending()`, `oplock_break()`, `smb2_oplock_break_noti()`, `smb2_lease_break_noti()`, `smb_break_all_write_oplock()`, `smb_break_all_levII_oplock()`, and `smb_break_all_oplock()` coordinate notifications and wait states.
- Lease table helpers `same_client_has_lease()`, `find_same_lease_key()`, `lookup_lease_in_table()`, `destroy_lease_table()`, `copy_lease()`, and `add_lease_global_list()` handle lease identity and global lookup by client GUID/lease key.
- Parent lease helpers `smb_send_parent_lease_break_noti()` and `smb_lazy_parent_lease_break_close()` implement SMB2.1/3 directory lease invalidation.
- Create-context helpers `create_lease_buf()`, `parse_lease_state()`, `smb2_find_context_vals()`, `create_durable_rsp_buf()`, `create_durable_v2_rsp_buf()`, `create_mxac_rsp_buf()`, `create_disk_id_rsp_buf()`, and `create_posix_rsp_buf()` parse request contexts and build response contexts.
- `smb2_map_lease_to_oplock()` maps SMB2 lease state bits to legacy oplock levels.
- `smb2_check_durable_oplock()` validates durable reconnect owner, GUID, lease key, handle caching state, lease version, and reconnect name.

## Control Flow
During open, SMB2 create handling parses lease context with `parse_lease_state()`, checks lease-key reuse with `find_same_lease_key()`, then calls `smb_grant_oplock()`. `smb_grant_oplock()` rejects unsupported directory lease cases, allocates an `oplock_info`, optionally attaches a `lease`, handles same-client lease upgrade/copy, finds existing inode oplocks, breaks conflicting batch/exclusive holders to level II when needed, downgrades the new request for stacked lease/oplock cases, sets final level, preallocates a lease table if required, publishes `o_fp`, increments inode oplock count, links the opinfo to inode and global lease lists, and RCU-publishes it in the file.

Break flow uses `pending_break` as a bit lock, sets `op_state` to `OPLOCK_ACK_WAIT` for ack-required transitions, sends an async SMB2 OPLOCK_BREAK response through a temporary `ksmbd_work`, optionally sends interim `STATUS_PENDING` on the triggering request, waits up to `OPLOCK_WAIT_TIME`, and force-downgrades to none on timeout. Lease break state chooses new state based on write/handle/read bits and truncation. Close flow calls `close_id_del_oplock()`, unlinks lease/inode list entries, clears `fp->f_opinfo`, wakes waiters if an ack was pending, decrements counts, and drops references.

Create-context parsing walks the SMB2 create context chain validated earlier by `ksmbd_smb2_check_message()`, enforcing alignment, name offset, data offset, and bounds. Response helpers fill SMB2 create context structures with offsets, lengths, names, and data for leases, durable handles, maximal access, disk id, and POSIX metadata.

## State and Persistence
Oplock and lease state is in memory, tied to open files, inodes, connections, sessions, and client GUIDs. `struct lease` persists requested/current/new lease states, flags, duration, parent key, version, and epoch while the file is open. Durable handles can outlive a transient connection elsewhere, but this file only validates reconnect state and emits durable response contexts; it does not persist handles itself. Synchronization uses inode rwsems, global rwlock, per-table spinlocks, RCU, wait queues, atomics, and bit waits.

## Dependencies and Integration Points
The file depends on SMB2 PDU structures/status constants, connection/session/share/tree management, global file lookup, VFS durable owner/name checks, inode cache objects, workqueue response writing, and SID/id conversion for POSIX create contexts. It is called heavily from `smb2pdu.c` create/open, write/truncate, close, lease break ack, and durable reconnect paths. Share flag `KSMBD_SHARE_FLAG_OPLOCKS` controls whether breaks are sent.

## Risks and Edge Cases
- This is concurrency-sensitive code: RCU publication, list traversal, atomic refcounts, wait queues, and lock nesting must remain consistent to avoid use-after-free, missed wakeups, or deadlocks.
- `oplock_break()` increments `breaking_cnt` before `oplock_break_pending()`; early error paths must ensure the counter is decremented or waiters can stall.
- Break notification work uses `work->request_buf` to carry allocated break info; cleanup depends on `ksmbd_free_work_struct()` freeing request buffers correctly.
- `smb2_find_context_vals()` assumes `CreateContextsOffset/Length` were validated by `ksmbd_smb2_check_message()`; direct callers on unchecked buffers would be unsafe.
- `create_durable_v2_rsp_buf()` casts to `create_durable_rsp_v2` but zeros only `sizeof(struct create_durable_rsp)`, which may leave v2 fields uninitialized if the v2 structure is larger.
- Lease/oplock level comparisons mix SMB2 lease bitfields and oplock constants in some conditions; tests must catch incorrect downgrade decisions.
- Timeout-driven forced downgrade can preserve server progress but risks client cache incoherency if a client later sends a stale ack.

## Test Signals
Exercise single open grants for none/II/exclusive/batch and lease R/RH/RWH; conflicting opens requiring batch/exclusive break to II; write/truncate break to none; same-client lease upgrades and break-in-progress flags; duplicate lease key on different files; parent directory lease breaks; close during pending break; break timeout; durable reconnect success/failure for owner, GUID, lease key, handle caching, version, and renamed/deleted files; malformed create contexts with bad alignment/offset/length; and KASAN/KCSAN stress with concurrent open/close/break/disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/oplock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/oplock.h -->
# sources/distributed-fs/ceph-client/fs/smb/server/oplock.h

## Purpose
Declares ksmbd oplock, lease, durable handle, and create-context helpers. It defines the shared state structures used by `oplock.c` and consumers in SMB2 create/open, close, write/truncate, lease break, and durable reconnect handling.

## Important APIs, Types, and Functions
- Constants define `OPLOCK_WAIT_TIME`, internal opinfo states (`OPLOCK_STATE_NONE`, `OPLOCK_ACK_WAIT`, `OPLOCK_CLOSING`), and transition reason bits.
- `struct lease_ctx_info` captures parsed request lease context, including lease key, requested state, flags, duration, parent key, epoch, version, and directory indicator.
- `struct lease_table` groups leases by client GUID and owns an RCU traversed `lease_list` plus spinlock.
- `struct lease` stores active lease key/state/new_state/flags/duration/parent key/version/epoch/dir flag/table pointer.
- `struct oplock_info` is the central open-file cache state: connection, session, triggering work, file pointer, level, state, pending break bit, FID/TID, break counters/refcount, lease flag, truncation flag, lease pointer, inode/global list entries, wait queues, and RCU head.
- Break message structs `lease_break_info` and `oplock_break_info` carry notification payload state.
- Public functions cover grant/break/close/refcount, lease parsing/mapping/buffer creation, durable response buffers, create context lookup, lease lookup, parent lease breaks, and durable oplock reconnect validation.

## Control Flow
SMB2 create/open code parses lease contexts into `lease_ctx_info`, calls `smb_grant_oplock()`, and uses response buffer creators to include granted lease/durable/POSIX/max-access/disk-id contexts. Write/truncate paths call break helpers. Close paths call `close_id_del_oplock()`. Lease break ack paths use `lookup_lease_in_table()` and transition helpers. Durable reconnect code calls `smb2_check_durable_oplock()`.

## State and Persistence
The structures describe in-memory cache-coherency state for open files. State is tied to kernel objects and protected with locks/RCU/atomics initialized in `oplock.c`. Durable handle metadata is represented indirectly through `ksmbd_file`; this header only exposes helper functions for response creation and validation.

## Dependencies and Integration Points
The header depends on `smb_common.h` for SMB2 constants and forward declarations from other ksmbd headers included by implementation files. It is part of the contract among `smb2pdu.c`, VFS file objects, connection/session management, and create-context response assembly.

## Risks and Edge Cases
- Many fields are binary buffers and little-endian values; callers must not treat them as native-endian or NUL-terminated strings.
- Public transition helpers assume the supplied opinfo is referenced and in a compatible current state.
- `oplock_info` exposes many mutable fields, so external code must preserve locking discipline defined by `oplock.c`.
- `oplock_break_info::fid` is `int` while public grant APIs and file ids use `u64`; truncation risk depends on actual FID ranges and implementation casts.

## Test Signals
Compile users for type/endianness correctness; run create/open, break, close, lease ack, durable reconnect, and create-context tests described for `oplock.c`; and use lockdep/KCSAN to verify external callers follow expected lock and lifetime rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/oplock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/proc.c -->
# sources/distributed-fs/ceph-client/fs/smb/server/proc.c

## Purpose
Implements procfs diagnostics and per-CPU counters for ksmbd. It creates `/proc/fs/ksmbd`, a `sessions` subdirectory, a `server` status file, and initializes/destroys/reset counters used by request processing and VFS I/O accounting.

## Important APIs, Types, and Functions
- Global `static struct proc_dir_entry *ksmbd_proc_fs` holds the procfs root.
- Global `struct ksmbd_counters ksmbd_counters` provides storage for percpu counters declared in `stats.h`.
- `ksmbd_proc_create()` wraps `proc_create_single_data()` under the ksmbd proc root.
- `smb2_process_req[]` maps SMB2 command numbers to display names for per-command counters.
- `proc_show_ksmbd_stats()` emits server identity/configuration, session/tree/read/write counters, and SMB2 per-command request counters through `seq_file`.
- `ksmbd_proc_init()` creates the proc root and `sessions` directory, initializes all percpu counters, creates the `server` file, and resets counters.
- `ksmbd_proc_cleanup()` removes the proc tree and destroys counters.
- `ksmbd_proc_reset()` sets all counters to zero.

## Control Flow
Module init calls `ksmbd_proc_init()` before server operation. If any proc or counter setup step fails, `ksmbd_proc_init()` jumps to cleanup. Request dispatch increments per-command counters through `ksmbd_counter_inc_reqs()`, session/tree code updates their counters, and VFS read/write paths add bytes. Reading `/proc/fs/ksmbd/server` calls `proc_show_ksmbd_stats()`. Module shutdown calls `ksmbd_proc_cleanup()`.

## State and Persistence
Proc entries and counters are runtime-only kernel state. Counters are per-CPU and reset at initialization and on server control reset via `ksmbd_proc_reset()`. No values persist across module unload or reset.

## Dependencies and Integration Points
This file depends on procfs, seq_file, Linux module headers, `server.h`, `stats.h`, `smb_common.h`, and `smb2pdu.h`. It reads `server_conf` and server identity helpers from `server.c`, protocol string helpers from SMB common code, and counter helpers from `stats.h`. Session-specific proc entries are created elsewhere under the `sessions` directory.

## Risks and Edge Cases
- If counter initialization fails partway through, `ksmbd_proc_cleanup()` destroys every counter slot, including any not successfully initialized; this depends on percpu counter destroy tolerating zero/uninitialized storage.
- `ksmbd_proc_reset()` assumes counters are initialized; calls before successful init would be unsafe.
- The command-name table must stay aligned with `KSMBD_COUNTER_MAX_REQS` and SMB2 command ordering.
- Proc output reads global configuration without explicit locking, so it is a diagnostic snapshot rather than a strongly consistent view.

## Test Signals
Build with procfs enabled; mount/read `/proc/fs/ksmbd/server`; verify counters increment for representative SMB2 commands and read/write byte paths; reset the server and confirm counters zero; exercise init failure injection for proc creation and percpu counter allocation; unload/reload under KASAN to detect proc/counter lifetime issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/server.c -->
# sources/distributed-fs/ceph-client/fs/smb/server/server.c

## Purpose
Implements the ksmbd kernel module's server lifecycle, global configuration storage, work dispatch loop, sysfs control surface, transport callbacks, and module init/exit ordering. It is the central coordinator between network transport, protocol operations, session/tree validation, signing/encryption, request counters, and subsystem startup/shutdown.

## Important APIs, Types, and Functions
- Globals `int ksmbd_debug_types` and `struct ksmbd_server_config server_conf` hold debug flags and mutable server configuration.
- Config setters/getters `ksmbd_set_netbios_name()`, `ksmbd_set_server_string()`, `ksmbd_set_work_group()`, `ksmbd_netbios_name()`, `ksmbd_server_string()`, and `ksmbd_work_group()` manipulate string slots via `___server_conf_set()`.
- Request path functions: `check_conn_state()`, `__process_request()`, `__handle_ksmbd_work()`, `handle_ksmbd_work()`, `queue_ksmbd_work()`, and `ksmbd_server_process_request()`.
- Transport callbacks are registered by `ksmbd_server_tcp_callbacks_init()`, with termination handled by `ksmbd_server_terminate_conn()` calling session deregistration and lease table cleanup.
- Config lifecycle: `server_conf_init()` sets default state, protocols, auth mechanisms, and credit limit; `server_conf_free()` frees strings.
- Control work: `server_ctrl_struct`, `server_ctrl_handle_init()`, `server_ctrl_handle_reset()`, `server_ctrl_handle_work()`, `__queue_ctrl_work()`, `server_queue_ctrl_init_work()`, and `server_queue_ctrl_reset_work()` perform async start/reset under `ctrl_lock`.
- Sysfs class attributes expose `stats`, `kill_server`, and `debug` through `ksmbd-control`.
- Lifecycle functions `ksmbd_server_shutdown()`, `ksmbd_server_init()`, and `ksmbd_server_exit()` initialize and tear down procfs, work pools, IPC, global file table, inode hash, crypto, workqueues, transport, leases, and caches.

## Control Flow
Transport code receives an SMB request into `conn->request_buf` and calls the registered process callback. `queue_ksmbd_work()` initializes SMB dialect state, allocates `ksmbd_work`, moves the request buffer into it, enqueues it on the connection, increments connection request count, and schedules `handle_ksmbd_work()`. The worker optionally decrypts a transform request, allocates/initializes a response, checks session and tree connection, verifies and dispatches the command through `conn->cmds[command].proc`, handles compounded SMB2 messages, grants credits, signs responses when required, updates preauth hash, optionally encrypts the response, releases tree/session references, writes the response, dequeues and frees work.

Server init registers the sysfs class, procfs, session proc support, transport callbacks, then initializes config, work pool, file cache, IPC, global file table, inode hash, crypto, workqueue, and connection workqueue in dependency order. Shutdown reverses most resources, destroys lease tables, and uses `rcu_barrier()` before destroying the connection workqueue so deferred connection releases have drained.

## State and Persistence
`server_conf` stores runtime configuration and server state. Config strings are heap allocated and freed/reset on server reset or shutdown. Work items and request buffers are transient. Sysfs/procfs entries and counters are runtime-only. No persistent on-disk server state is created here; durable handle and share/user configuration state lives in other subsystems.

## Dependencies and Integration Points
This file depends on connection and transport callbacks, SMB dialect ops, authentication, crypto contexts, IPC, stats/procfs, oplock lease cleanup, session management, tree connect references, global file table/inode cache, and Linux module/workqueue/sysfs infrastructure. It calls protocol-specific operations supplied by `smb2ops.c` and validators from SMB common code.

## Risks and Edge Cases
- `__process_request()` aborts on signature failure or missing command handlers; command tables must be complete for negotiated dialects.
- Compound request handling shares response/session/tree state across loop iterations; reference and response-buffer handling must match dialect ops.
- On decrypt failure, `__handle_ksmbd_work()` returns before response allocation and relies on outer cleanup to free work and decrement connection request count.
- `stats_show()` indexes a fixed state string array by `server_conf.state`; invalid state values could read out of bounds.
- `kill_server_store()` performs synchronous reset under `ctrl_lock` and module reference manipulation; reset paths must not sleep in invalid contexts or race async control work.
- Init failure unwinding must mirror successful initialization exactly; missing cleanup can leave proc/sysfs/workqueue state behind.

## Test Signals
Exercise module load/unload, init failure injection at each subsystem step, server start/reset/kill sysfs paths, debug flag toggles, stats output, SMB2 request dispatch including unsupported commands and compounds, signing failure, encrypted request/response paths, disconnect while work is queued, session/tree invalidation, and RCU/KASAN validation during shutdown after active connections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/server.h -->
# sources/distributed-fs/ceph-client/fs/smb/server/server.h

## Purpose
Declares ksmbd global server configuration, server state constants, configuration accessors, control work queue entry points, and inline state predicates.

## Important APIs, Types, and Functions
- Server states: `SERVER_STATE_STARTING_UP`, `SERVER_STATE_RUNNING`, `SERVER_STATE_RESETTING`, and `SERVER_STATE_SHUTTING_DOWN`.
- Config string indices: `SERVER_CONF_NETBIOS_NAME`, `SERVER_CONF_SERVER_STRING`, and `SERVER_CONF_WORK_GROUP`.
- `struct ksmbd_server_config` contains global feature flags, state, signing policy, protocol range, TCP/IPC settings, share faked capabilities, domain SID, auth mechanisms, connection/request limits, config strings, durable scavenger task pointer, and bind-interface policy.
- `extern struct ksmbd_server_config server_conf` exposes the global config.
- Setters/getters manage NetBIOS name, server string, and workgroup.
- Inline predicates `ksmbd_server_running()` and `ksmbd_server_configurable()` use `READ_ONCE()` on `server_conf.state`.
- `server_queue_ctrl_init_work()` and `server_queue_ctrl_reset_work()` schedule server control actions.

## Control Flow
Configuration code updates `server_conf` while the server is configurable. Request/transport code can cheaply check `ksmbd_server_running()`. IPC or management code schedules start/reset work through the declared control functions.

## State and Persistence
`server_conf` is process-global kernel module state and is not persistent across module unload. String fields are heap-owned by `server.c`. State reads are lockless snapshots.

## Dependencies and Integration Points
The header includes `smbacl.h` for `struct smb_sid`. It is included by server implementation, IPC/config management, procfs stats, and protocol negotiation code that reads feature flags and protocol bounds.

## Risks and Edge Cases
- Global mutable configuration requires careful synchronization by writers; the header only provides lockless read predicates.
- Consumers that read multiple fields may observe a mixed snapshot during reset.
- `ksmbd_server_configurable()` treats states numerically, so state enum ordering is part of the ABI between header and implementation.

## Test Signals
Compile and run management/config tests that set names/workgroup, start/reset the server, check state predicates during transitions, and verify procfs/sysfs readers behave under concurrent reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/smb2misc.c -->
# sources/distributed-fs/ceph-client/fs/smb/server/smb2misc.c

## Purpose
Provides SMB2 request validation utilities. It checks SMB2 headers, fixed structure sizes, variable data area offsets/lengths, compound message boundaries, SMB2 credit charge correctness, and dispatches SMB2 negotiate requests into common negotiation handling.

## Important APIs, Types, and Functions
- `check_smb2_hdr()` rejects inbound messages already marked `SMB2_FLAGS_SERVER_TO_REDIR`.
- `smb2_req_struct_sizes[]` maps SMB2 command numbers to expected request `StructureSize2` values.
- `has_smb2_data_area[]` identifies commands with variable-length data areas.
- `smb2_get_data_area_len()` extracts and validates data offsets/lengths for session setup, tree connect, create, query/set info, read/write channel info or data, query directory, lock arrays, and ioctl buffers.
- `smb2_calc_size()` computes the expected PDU length from header, fixed structure, and variable data region, with special lock-array adjustment.
- Request length helpers compute credit-relevant sizes for query info, set info, read, write, query directory, and ioctl request/response maxima.
- `smb2_validate_credit_charge()` validates client `CreditCharge` against payload/expected response size, maximum dialect credits, granted credits, and outstanding credits under `conn->credits_lock`.
- `ksmbd_smb2_check_message()` is the public validator called before command dispatch.
- `smb2_negotiate_request()` forwards SMB2 negotiate handling to `ksmbd_smb_negotiate_common()`.

## Control Flow
`ksmbd_smb2_check_message()` obtains the current SMB2 PDU from the work item, bounds `NextCommand` against RFC1002 message length for compounds, normalizes the current PDU length, rejects server-to-client headers, checks SMB2 header size and command range, validates command-specific fixed structure size including SMB2.1 oplock/lease break exceptions, ensures fixed request size fits, calculates expected total size, accepts known padding variants, then validates credit charge when Large MTU capability is active.

`smb2_get_data_area_len()` is command-specific: for CREATE it considers both name and create-context regions and chooses a covering variable area; for WRITE it prioritizes data when `DataOffset` or `Length` is present, otherwise checks write-channel info; for LOCK it derives the lock array length from `LockCount`.

## State and Persistence
The file mutates only connection credit accounting: `conn->outstanding_credits` is increased when credit validation succeeds. It otherwise performs stateless validation over the request buffer.

## Dependencies and Integration Points
It depends on SMB2 PDU definitions, status/common constants, session and connection structures, and the common negotiate function. `smb_common.c` calls `ksmbd_smb2_check_message()` through dialect verification; `server.c` calls `ksmbd_verify_smb_message()` before dispatch. Correct validation is a prerequisite for `oplock.c` create-context parsing and all SMB2 command handlers.

## Risks and Edge Cases
- Validation accepts some padding mismatches to interoperate with Windows and Linux clients; the tolerance must not mask malicious overlong variable areas.
- `hdr->Command` is little-endian in the wire struct but many switch statements compare against SMB2 constants; this relies on the constants used here matching the field representation.
- Credit validation increments `outstanding_credits` but the corresponding decrement must happen elsewhere; leaks will throttle clients.
- `*off > 4096` and `MAX_STREAM_PROT_LEN` limits protect offsets/lengths, but command handlers still need their own semantic validation.
- Compound `NextCommand` handling must align with subsequent `ksmbd_req_buf_next()` advancement or a later command can be validated against the wrong slice.

## Test Signals
Fuzz SMB2 headers and all command fixed sizes, variable offsets, zero/nonzero lengths, CREATE name/context overlap, LOCK lock counts, IOCTL input/output/max response sizes, compound `NextCommand` offsets, padded PDUs, Large MTU credit charge under/over-reporting, outstanding credit overflow, CANCEL credit exemption, and NEGOTIATE size exceptions. Handler tests should assert malformed create contexts are rejected before `smb2_find_context_vals()` sees them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/smb2misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/smb2ops.c -->
# sources/distributed-fs/ceph-client/fs/smb/server/smb2ops.c

## Purpose
Defines dialect-specific SMB2/SMB3 server value tables, operation vectors, command dispatch table, dialect initialization functions, and runtime tuners for I/O sizes and credits. It connects the generic server dispatch loop to SMB2 command handlers and SMB3 signing/encryption implementations.

## Important APIs, Types, and Functions
- `smb21_server_values`, `smb30_server_values`, `smb302_server_values`, and `smb311_server_values` define dialect strings, protocol ids, capabilities, max read/write/transaction sizes, max credits, lock flags, header sizes, read response size, create-context response sizes, and feature bits.
- `smb2_0_server_ops` provides basic SMB2 operation callbacks: command lookup, request counters, response header/status/buffer/credits, session/tree validation, and SMB2 signing.
- `smb3_0_server_ops` adds SMB3 signing key generation, encryption key generation, transform-header detection, decrypt, and encrypt callbacks.
- `smb3_11_server_ops` switches key derivation to SMB 3.1.1 functions and otherwise mirrors SMB3 encrypted operation support.
- `smb2_0_server_cmds[]` maps SMB2 command indices to handlers such as negotiate, session setup, tree connect/disconnect, logoff, create, query info, query directory, close, echo, set info, read, write, flush, cancel, lock, ioctl, oplock break, and change notify.
- Dialect init functions `init_smb2_1_server()`, `init_smb3_0_server()`, `init_smb3_02_server()`, and `init_smb3_11_server()` attach values/ops/commands to `struct ksmbd_conn`, set signing algorithm, and enable capabilities according to `server_conf.flags` and client capabilities.
- Runtime tuners `init_smb2_max_read_size()`, `init_smb2_max_write_size()`, `init_smb2_max_trans_size()`, and `init_smb2_max_credits()` update all dialect value tables.

## Control Flow
After negotiation selects a dialect, connection initialization calls the matching init function. The generic server path then uses `conn->ops` for verification, response setup, signing/encryption, session/tree lookup, credits, and request counters, and `conn->cmds` for actual command dispatch. SMB3 dialects enable encryption capability only when server policy and client capability allow it, enable leasing/directory leasing and multichannel according to global flags, and enable persistent handles for SMB 3.0.2/3.1.1 when durable handles are configured. SMB 3.1.1 initializes the connection preauth session list.

## State and Persistence
The dialect value tables are static global mutable structures. Runtime tuner functions modify the same tables for future and possibly existing connections referencing them. Per-connection selected pointers in `conn->vals`, `conn->ops`, and `conn->cmds` are not copies. No persistent storage is used.

## Dependencies and Integration Points
This file depends on auth/crypto signing and encryption functions, connection structures, SMB common/PDU constants, server global configuration, and stats counters. It is used by negotiation/common server initialization and by `server.c` request dispatch. Command handlers live primarily in `smb2pdu.c` and related modules.

## Risks and Edge Cases
- Because `conn->vals` points at shared static tables, capability bits ORed during one connection initialization can persist for later connections even when their `server_conf` or `cli_cap` differs. This is particularly sensitive for encryption, leasing, multichannel, and persistent handle capabilities.
- Runtime size/credit tuners mutate shared tables without visible locking; concurrent negotiation/request paths may observe partial changes.
- `init_smb3_0_server()` contains two encryption capability checks, one redundant with slightly different condition; policy interpretation must be tested for `ENCRYPTION` and `ENCRYPTION_OFF` flags.
- Command table holes produce `STATUS_NOT_IMPLEMENTED` in `server.c`; command indices must stay aligned with SMB2 constants and counter ordering.
- SMB 3.1.1 preauth list initialization must happen before any preauth session allocation.

## Test Signals
Negotiate each dialect and verify selected protocol id, signing algorithm, max sizes, command table, create-context sizes, and capabilities under combinations of leasing, encryption, encryption-off, multichannel, durable handle, and client encryption capability. Test runtime max read/write/trans/credit tuners before and during connections. Regression tests should verify one connection's enabled capabilities do not leak incorrectly into later connections with different policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/smb2ops.c -->
