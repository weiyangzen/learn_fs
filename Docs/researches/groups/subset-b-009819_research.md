# Research: subset-b-009819

Grouped source-tree-aligned research for Samba `source3/libsmb` SMB2 fnum wrappers and client connection/session setup code. Each source file has a bounded section for reconciliation into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/cli_smb2_fnum.c -->
# sources/user-network-fs/samba/source3/libsmb/cli_smb2_fnum.c

## Purpose
`cli_smb2_fnum.c` is the source3 compatibility layer that makes SMB2/SMB3 file handles usable through the older `libsmb` `uint16_t fnum` API. The underlying SMB2 protocol identifies open objects with persistent and volatile 64-bit FIDs; this file stores those FIDs in a `cli_state`-owned id tree and exposes SMB1-style fnums to callers such as `smbclient`, `libsmbclient`, and higher source3 wrappers.

Beyond handle mapping, the file implements the SMB2 versions of common client operations: create/open, close, delete-on-close, mkdir/rmdir/unlink, directory enumeration, query/set path or handle information, filesystem attributes, maximum access, rename, extended attributes, quotas, read/write/write-all, server-side copy, shadow copy enumeration, truncate, change notify, generic FSCTL, and POSIX filesystem information. Most operations are thin tevent wrappers around `smb2cli_*` routines from `libcli/smb`, with synchronous adapters layered on top where the historical `libsmb` API is synchronous.

## Important APIs, Types, And Functions
The central private type is `struct smb2_hnd`, which records `fid_persistent`, `fid_volatile`, and a `posix` boolean indicating whether the open used the SMB 3.1.1 POSIX create context. `map_smb2_handle_to_fnum()`, `map_fnum_to_smb2_handle()`, and `delete_smb2_handle_mapping()` manage the `cli->smb2.open_handles` idr namespace. Fnums are allocated from `1` through `0xFFFE`, avoiding `0` and `0xFFFF` sentinel values used elsewhere.

Open and close are exported through `cli_smb2_create_fnum_send/recv()`, synchronous `cli_smb2_create_fnum()`, `cli_smb2_close_fnum_send/recv()`, and `cli_smb2_close_fnum()`. `cli_smb2_create_fnum_send()` normalizes path strings, applies backup intent, adds POSIX and snapshot/TWrp create blobs, expands DFS share paths when needed, maps oplock flags with `flags_to_smb2_oplock()`, calls `smb2cli_create_send()`, handles reparse fallback, then maps the returned SMB2 FID pair to an fnum. `cli_smb2_fnum_is_posix()` exposes the saved POSIX-open flag.

Information operations are centered on `cli_smb2_query_info_fnum_send/recv()`, `cli_smb2_query_info_fnum()`, `cli_smb2_set_info_fnum_send/recv()`, and `cli_smb2_set_info_fnum()`. Path operations use the private `get_fnum_from_path_send/recv()` helper, which tries file opens, reparse-point opens, and directory opens as needed. Higher-level APIs such as `cli_smb2_qpathinfo_send/recv()`, `cli_smb2_setpathinfo()`, `cli_smb2_setatr()`, `cli_smb2_setattrE()`, and `cli_smb2_qpathinfo_basic()` build on those primitives.

Directory and namespace APIs include `cli_smb2_mkdir_send/recv()`, `cli_smb2_rmdir_send/recv()`, `cli_smb2_unlink_send/recv()`, `cli_smb2_list_send/recv()`, and `cli_smb2_rename_send/recv()`. Directory listing parses either `SMB2_FIND_ID_BOTH_DIRECTORY_INFO` through `parse_finfo_id_both_directory_info()` or `SMB2_FIND_POSIX_INFORMATION` through `parse_finfo_posix_info()`. `windows_parent_dirname()` splits a search pathname into parent directory and mask.

Filesystem metadata APIs include `cli_smb2_dskattr()`, `cli_smb2_get_fs_full_size_info()`, `cli_smb2_get_fs_attr_info()`, `cli_smb2_get_fs_volume_info()`, `cli_smb2_query_mxac_send/recv()`, and `cli_smb2_get_posix_fs_info_send/recv()`. Quota functions use NDR helpers around `smb2_query_quota_info`, `file_get_quota_info`, and Samba quota parsing/building helpers.

I/O and control APIs include `cli_smb2_read_send/recv()`, `cli_smb2_write_send/recv()`, `cli_smb2_writeall_send/recv()`, `cli_smb2_splice_send/recv()` using `FSCTL_SRV_REQUEST_RESUME_KEY` and `FSCTL_SRV_COPYCHUNK_WRITE`, `cli_smb2_shadow_copy_data()`, `cli_smb2_ftruncate()`, `cli_smb2_notify_send/recv()`, and `cli_smb2_fsctl_send/recv()`.

## Control Flow
Most exported async routines follow the same tevent pattern: allocate a state struct, translate the public fnum or path into an SMB2 FID pair, issue an `smb2cli_*_send()` subrequest, install a callback, and finish the parent request with either `tevent_req_done()` or `tevent_req_nterror()`. Synchronous wrappers create a temporary tevent context, reject use while `smbXcli_conn_has_async_calls()` is true, poll the async request, receive the result, and free the stack frame.

Create flow is the most important. The send path duplicates and rewrites the incoming name, optionally prepends DFS server/share components, strips leading and trailing backslashes that SMB2 rejects, attaches POSIX/TWrp/user create blobs, and submits `smb2cli_create_send()`. The completion path retries with `FILE_OPEN_REPARSE_POINT` if the server reports an unhandled reparse tag and the caller did not already request reparse-point opens. On success it records the returned FIDs in the idr and returns only the short fnum to callers.

Path-level set/query/rename/delete operations are implemented as open-operate-close state machines. For example, `cli_smb2_qpathinfo_send()` opens a path with `FILE_READ_ATTRIBUTES`, queries file info, checks the minimum response size, closes the handle, and only then completes. Rename opens the source with `DELETE_ACCESS`, builds a `FILE_RENAME_INFORMATION` buffer for the destination, sets info on the source handle, closes, and returns the rename status if close succeeded. Rmdir and unlink set delete-on-close and deliberately close handles even when the disposition step failed.

Directory enumeration is deliberately incremental. `cli_smb2_list_send()` opens the parent directory, then `cli_smb2_list_recv()` either parses one entry from the cached response blob or sends another `smb2cli_query_directory_send()` and returns `NT_STATUS_RETRY`. This avoids leaving an outstanding async request after returning an entry, preserving compatibility with callers that interleave synchronous operations while walking a directory.

Read and write wrappers are direct fnum-to-FID translations. `cli_smb2_writeall_send()` chunks writes according to `smb2cli_conn_max_write_size()` and currently available request credit limits. Server-side copy first fetches a resume key from the source, then sends one or more copychunk requests to the destination. If the server returns `NT_STATUS_INVALID_PARAMETER` with copychunk limits, the wrapper shrinks the cached connection copychunk size/count and retries once.

Notify and FSCTL wrappers expose long-running SMB2 operations. `cli_smb2_notify_send()` stores the subrequest so cancellation propagates to `smb2cli_notify_send()`. A notify timeout is treated as a successful request with zero changes. FSCTL output is copied out because `smb2cli_ioctl_recv()` returns slices into receive buffers rather than standalone talloc allocations.

## State And Persistence
The durable-in-process state is the fnum mapping under `cli->smb2.open_handles`. Each open maps one fnum to a talloc-owned `struct smb2_hnd`; close removes the idr entry and frees the handle. The mapping is scoped to the `cli_state`, so it is not persistent across reconnects or new `cli_state` instances. A leaked fnum corresponds to a leaked SMB2 server handle until the session/tree/connection is torn down or the server closes it.

Per-request state is talloc-owned by tevent request structures. Many receive functions move or duplicate data into caller-provided memory contexts because lower layers often return pointers into receive buffers. Examples include create output blobs, symlink reparse data, query-info blobs, directory `file_info` names, shadow copy names, notify changes, and FSCTL output.

Filesystem persistence is delegated to server operations: create, delete-on-close, rename, set basic info, EA writes, quota writes, file truncation, and copychunk mutate remote filesystem state. The wrappers often preserve SMB1-facing ABI behavior even when SMB2 semantics differ, notably `cli_smb2_setatr()` reversing the `attr == 0` and `FILE_ATTRIBUTE_NORMAL` meanings to match historical `cli_setatr()` behavior.

## Dependencies And Integration Points
This file sits between source3 client APIs and lower-level SMB2 client primitives. It depends on `client.h`/`cli_state`, `smbXcli_base`, `smb2cli_*` create/close/query/set/read/write/ioctl/notify APIs, tevent NTSTATUS helpers, talloc, idr allocation, DFS helpers, path/string conversion helpers, NDR-generated structures for security, ioctl, quota, and SMB3 POSIX data, EA/quota utilities, and POSIX SMB2 create-context helpers.

Integration points include `libsmb/proto.h` callers that dispatch SMB1 versus SMB2 behavior, `libsmbclient` public ABI expectations, `smbclient` command implementations using fnums, DFS path handling, snapshot token support for `@GMT-` paths, SMB3 POSIX extensions, quota tooling, copy acceleration, change notification, and test code that expects SMB1-like fnum behavior even on SMB2/SMB3 sessions.

## Risks And Test Signals
Handle lifetime is the primary risk. Every successful `cli_smb2_create_fnum_recv()` must eventually reach `cli_smb2_close_fnum()` or another cleanup path that deletes the idr mapping. Tests should cover close-after-failed-intermediate operations, double close, invalid fnum lookup, maximum fnum allocation pressure, and session teardown with open mappings.

Network-response parsing is another high-risk area. Directory parsers validate `NextEntryOffset`, name lengths, short-name lengths, POSIX NDR consumption, and UTF-16 conversions; fuzzing malformed directory blobs is valuable. Filesystem volume parsing checks several length and integer-wrap conditions. Notify parsing checks buffer bounds before conversion. Copychunk handles offset overflow and server-advertised limits. These paths need malformed-response regression tests, not only happy-path interop tests.

The SMB2/SMB1 ABI translation carries subtle compatibility risk. `cli_smb2_setatr()` intentionally inverts normal-vs-clear attribute semantics. Rename strips leading/trailing backslashes and pads short rename buffers for Windows 10 behavior. Create retries reparse points in a simplified way that assumes the last component was the symlink/reparse object. DFS path expansion and `@GMT-` token extraction alter the path before create.

Specific suspicious test targets are `cli_smb2_fsctl_recv()`, which sets `status = NT_STATUS_NO_MEMORY` on copy failure but returns success at the end, and `cli_smb2_get_posix_fs_info_queried()`, which silently closes and later returns success with zeroed fields when the POSIX FS info response length is not exactly 56. Both deserve focused regression tests or code review. Server-side copy should be tested against servers with smaller copychunk limits and with progress callbacks that cancel. Notify should be tested for cancellation, timeout-as-success, multi-entry changes, and malformed `NextEntryOffset`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/cli_smb2_fnum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/cli_smb2_fnum.h -->
# sources/user-network-fs/samba/source3/libsmb/cli_smb2_fnum.h

## Purpose
`cli_smb2_fnum.h` declares the source3 SMB2/SMB3 fnum compatibility API implemented by `cli_smb2_fnum.c`. It lets callers that were written around SMB1-style `uint16_t` fnums perform SMB2 operations without directly handling SMB2 persistent/volatile FIDs, create contexts, or lower-level `smb2cli_*` request objects.

## Important APIs, Types, And Functions
The only concrete public type in this header is `struct cli_smb2_create_flags`, with `batch_oplock` and `exclusive_oplock` bitfields. The header forward-declares `smbXcli_conn`, `smbXcli_session`, `cli_state`, `file_info`, and `symlink_reparse_struct`, keeping the public surface narrow while relying on other Samba headers for full definitions of `DATA_BLOB`, `NTSTATUS`, `SMB_NTQUOTA_STRUCT`, `SMB_NTQUOTA_LIST`, `smb2_create_blobs`, `smb_create_returns`, and notify structures.

The create/open API is `cli_smb2_create_fnum_send/recv()` and synchronous `cli_smb2_create_fnum()`. It accepts SMB2 create parameters, optional input create blobs, and returns an fnum plus optional create returns, output blobs, and symlink information. `cli_smb2_fnum_is_posix()` exposes whether an fnum originated from a POSIX-context open.

Handle operations include close, delete-on-close, generic query-info and set-info by fnum, read/write/writeall, splice/copychunk, truncate, notify, and FSCTL. Path operations include mkdir, rmdir, unlink, list, qpathinfo, setpathinfo, set attributes, query filesystem size/attributes/volume data, maximum access, rename, and EA get/set helpers. Quota functions operate on a quota fnum and marshal user or filesystem quota data.

The header consistently exposes async send/recv pairs for operations that can naturally fit tevent workflows, plus synchronous convenience wrappers for legacy callers. Synchronous functions all take `struct cli_state *cli` and typically return `NTSTATUS`; async send functions take `TALLOC_CTX *mem_ctx`, `struct tevent_context *ev`, and `struct cli_state *cli`.

## Control Flow
The header encodes a layered control-flow contract. Callers can either use send/recv pairs and drive them through a tevent loop, or call synchronous wrappers that internally create and poll a tevent request. For path operations that have no direct SMB2 path-level primitive, the implementation opens a temporary fnum, performs a handle-level operation, and closes it before returning.

Create, list, notify, fsctl, read, write, writeall, splice, and POSIX filesystem info are explicitly asynchronous in the interface. Directory listing has a special receive contract: `cli_smb2_list_recv()` can return one `file_info`, report `NT_STATUS_RETRY` while another query-directory request is outstanding, or terminate with no-more-files/error semantics.

## State And Persistence
The header does not declare state storage, but its API implies fnum lifetime state inside `cli_state`. Any fnum returned by create or opened internally by path helpers maps to an SMB2 server handle until closed. Functions that mutate remote persistence include create, mkdir, rmdir, unlink, set-info, set attributes, rename, EA writes, quota writes, copychunk, truncate, and delete-on-close.

Memory ownership is part of the API contract. Receive functions use caller-provided memory contexts for output blobs, symlink data, `file_info` arrays, EA arrays, shadow copy names, notify changes, and FSCTL output. Callers must keep the request alive long enough for direct receive buffers documented by the implementation, especially read buffers returned from `cli_smb2_read_recv()`.

## Dependencies And Integration Points
This header is included by source3 client code that dispatches SMB2 behavior from generic `libsmb` APIs. It depends on Samba-wide NTSTATUS, tevent, talloc, SMB2 create context, quota, EA, file-info, and notify type definitions being visible through surrounding includes. It integrates with the lower-level `smb2cli_*` layer indirectly through the implementation, and with legacy SMB1-facing caller code by preserving fnum-shaped handles and historical behavior.

## Risks And Test Signals
The broad API surface means signature drift can break many consumers. Build tests should include source3 clients, `libsmbclient`, quota tools, and SMB2 POSIX feature paths. Async contract tests should verify each send/recv pair handles posted errors, cancellation where supported, memory-context transfer, and request cleanup.

The header exposes several nuanced contracts that need tests: POSIX fnum detection, directory-list retry iteration, read buffer lifetime, set attribute SMB1-compatible semantics, quota-fnum usage, notify timeout behavior, and FSCTL output ownership. Because many synchronous wrappers reject operation while another async request is in flight, mixed async/sync caller tests should assert `NT_STATUS_INVALID_PARAMETER` rather than deadlock or protocol corruption.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/cli_smb2_fnum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/cliconnect.c -->
# sources/user-network-fs/samba/source3/libsmb/cliconnect.c

## Purpose
`cliconnect.c` implements source3 client connection setup and teardown for SMB clients. It covers credential object construction, SMB1 and SMB2 session setup, SPNEGO/GENSEC negotiation, guest and anonymous setup, tree connect/disconnect, transport socket creation, protocol negotiation, SMB1 Unix-extension encryption setup, full connection orchestration through tree connect, raw legacy tree connect, and helper IPC/master-browser connection routines.

The file is the bridge between high-level `libsmb` connection APIs and lower layers such as name resolution, socket transport, `smbXcli` negotiation, SMB1 request builders, SMB2 session/tree connect functions, GENSEC authentication, signing, and encryption policy.

## Important APIs, Types, And Functions
`cli_session_creds_init()` builds a `cli_credentials` object from username/domain/realm/password options. It handles empty-password anonymous logic, `DOMAIN\user`, `DOMAIN/user`, and winbind-separator username forms, principal-to-account conversion, Kerberos required/disabled policy, NTLM ccache features, plaintext password setting, and NT-hash password parsing.

Session setup helpers include `cli_session_setup_guest_create/send/recv()` for NT1 guest setup, `cli_sesssetup_blob_send/recv()` for chunked SPNEGO token exchange over SMB1 extended security or SMB2 session setup, `cli_session_setup_gensec_send/recv()` for the local/remote GENSEC handshake, `cli_session_setup_spnego_send/recv()` as a SPNEGO wrapper, and `cli_session_setup_creds_send/recv()` plus synchronous `cli_session_setup_creds()` as the main credential-based session setup API. `cli_session_setup_anon()` constructs anonymous credentials and delegates to the main session setup path.

Connection teardown and tree APIs include `cli_ulogoff()`, `cli_tcon_andx_create/send/recv()`, `cli_tcon_andx()`, `cli_tree_connect()`, `cli_tree_connect_creds()`, `cli_tdis()`, and `cli_raw_tcon()`. These select SMB2 logoff/tree disconnect, SMB1 `ulogoffX`, SMB1 `tconX`, or old raw `SMBtcon` based on negotiated protocol and server capabilities.

Transport and negotiation APIs include `cli_connect_nb()`, private `cli_connect_sock_send/recv()`, private `cli_connect_nb_send/recv()`, `cli_start_connection()`, and private `cli_start_connection_send/recv()`. They resolve names when needed, connect through configured SMB transports, create `cli_state`, choose min/max protocol from client settings and flags, optionally add SMB2 POSIX negotiate contexts, call `smbXcli_negprot_send()`, and raise SMB2 credits after successful negotiation.

Encryption/full-connect APIs include `cli_smb1_setup_encryption()`, private `cli_smb1_setup_encryption_blob_send/recv()`, private `cli_smb1_setup_encryption_send/recv()`, `cli_full_connection_creds_send/recv()`, and synchronous `cli_full_connection_creds()`. Full connect performs transport connection, negotiation, session setup, optional anonymous fallback, encryption activation, optional IPC$ setup for SMB1 Unix encryption, and final tree connect.

Browser/IPC helpers include private `get_ipc_connect()` and public `get_ipc_connect_master_ip()`, which force SMB1 IPC connections for legacy browsing/master-browser discovery and fall back from IP address to NetBIOS name status when needed.

## Control Flow
Credential initialization starts by creating a `cli_credentials` object, loading source3 parameters, normalizing username/domain/principal fields, applying Kerberos policy, optionally enabling NTLM ccache, then setting password, NT hash, or Kerberos ccache. Failure releases the partially built credential object.

The main session setup decision in `cli_session_setup_creds_send()` is protocol and capability driven. SMB2 and SMB1 extended-security connections use SPNEGO/GENSEC. Older SMB1 paths choose anonymous, plaintext, LM/NTLM, or NTLMv2 response construction depending on security mode, protocol, and configured client authentication policy. NT1 session setup activates signing and validates the signed response when a session key is available. LM21 setup only updates server strings.

The GENSEC session setup state machine alternates local token generation (`gensec_update_send/recv()`) and remote token submission (`cli_sesssetup_blob_send/recv()`). It tracks `local_ready` and `remote_ready`, detects invalid extra blobs, special-cases guest sessions that cannot complete a session-key handshake, extracts the session key, and installs it in SMB2 or SMB1 session state. For SMB2/SMB3, it can also dump signing/application/encryption/decryption keys when debug encryption is enabled.

Tree connect control flow selects by negotiated protocol. SMB2 builds a UNC string and calls `smb2cli_tcon_send()`. LANMAN1 and newer SMB1 uses `tconX`, including share-level password handling and optional extended-signature support. Very old SMB uses raw `SMBtcon`. Tree disconnect and logoff similarly split SMB2 direct helpers from SMB1 request/response state machines.

Connection startup is layered. `cli_connect_sock_send()` resolves or accepts a socket address and calls `smbsock_any_connect_send()`. `cli_connect_nb_send()` parses optional `host#type`, creates `cli_state` around the connected transport, and returns it. `cli_start_connection_send()` selects protocol bounds from global client settings and flags, optionally requests SMB2 POSIX extensions, connects, negotiates, and configures SMB2 credits.

Full connection orchestration is a linear tevent chain with cleanup ownership. It starts transport/protocol negotiation, performs session setup, optionally retries with anonymous credentials if requested, activates encryption according to credential policy, optionally probes SMB1 Unix extension encryption through temporary IPC$, then performs the requested share tree connect. The state destructor shuts down partial `cli_state` objects unless ownership is moved out by the receive function.

## State And Persistence
Persistent-in-process state is concentrated in `cli_state`: server OS/type/domain strings, UID/session state, SMB1 or SMB2 session objects, tree connect objects, share/device strings, signing/encryption state, negotiated protocol/capabilities, and transport references. This file mutates that state after session setup, tree connect, tree disconnect, logoff, encryption setup, and negotiation.

Secrets are handled through `cli_credentials` and transient `DATA_BLOB`s. `cli_session_setup_creds_cleanup()` clears password/session-key blobs when the request is received. GENSEC state destructors free auth state and clear session keys. SMB1 encryption setup moves a `smb_trans_enc_state` into the connection and marks encryption on. SMB2 session setup installs session keys in the SMB2 session object.

Network persistence is limited to remote session and tree state. Session setup authenticates and allocates a server session; logoff invalidates it. Tree connect allocates a server tree id; tree disconnect releases it. Full connection may temporarily connect to IPC$ to negotiate SMB1 Unix transport encryption, then disconnect it before connecting the target share.

## Dependencies And Integration Points
The file depends on source3 client state (`client.h`), generated and hand-written `libsmb` prototypes, ADS status mapping, NetBIOS namequery/nmblib, socket transport connection helpers, `smbXcli_base`, SMB1/SMB2 session and tree connect primitives, GENSEC/auth_generic/NTLMSSP credentials, source3 loadparm settings, SMB sealing/encryption helpers, tevent NTSTATUS helpers, and SMB2 negotiate context support.

It integrates high-level public connection APIs with authentication policy (`client plaintext auth`, `client lanman auth`, `client ntlmv2 auth`, `client use spnego`, Kerberos state), signing/encryption settings from credentials, configured SMB transports, min/max protocol settings, IPC-specific protocol settings, POSIX negotiate-context requests, legacy browser code, and SMB1 Unix extension encryption.

## Risks And Test Signals
Authentication downgrade and policy handling are the main security risks. Tests should cover Kerberos-required against non-SPNEGO servers, plaintext/LM auth disabled paths, NTLMv2 without SPNEGO policy rejection, anonymous fallback with encryption desired versus required, guest sessions with signing required, and ccache/no-password handling.

State-machine correctness is critical. SPNEGO/GENSEC should be tested with multi-leg Kerberos and NTLMSSP, guest success, malformed extra blobs, failed final signatures, SMB2 session allocation cleanup on failure, and session key installation. SMB1 encryption uses heuristics because the server may return OK before it is actually ready; tests should include Unix-extension encryption supported, unsupported, desired, and required cases.

Connection and tree tests should cover name resolution versus pre-supplied addresses, `host#type` parsing, NetBIOS/IP fallback, transport list ordering, protocol min/max flags forcing or disabling SMB1, POSIX negotiate-context request, SMB2 credit initialization, share-level password behavior, raw legacy tree connect, and cleanup of partially connected `cli_state` objects on every failure edge.

Parsing and memory ownership also need regression coverage. Session setup server strings are pulled from SMB byte areas and defaulted to empty strings. `cli_state_update_after_sesssetup()` only fills empty fields, so tests should confirm server metadata is not overwritten unintentionally. Blob cleanup should be checked with leak and secret-zeroing tools. Tcon paths should verify `cli->share`, `cli->dev`, SMB1 tcon IDs, optional support flags, and SMB2 tcon ownership after success and failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/cliconnect.c -->
