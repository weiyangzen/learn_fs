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
