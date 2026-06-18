# subset-b-009846 research

This grouped report covers the Samba source3 RPC client files assigned to `subset-b-009846`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_pipe.c -->
# sources/user-network-fs/samba/source3/rpc_client/cli_pipe.c research

## Purpose

`cli_pipe.c` is the central source3 DCE/RPC client transport and binding implementation. It creates `rpc_pipe_client` objects over named pipes, local ncalrpc sockets, and TCP; negotiates DCE/RPC bind and alter-context state; fragments outgoing requests; reassembles and verifies incoming fragments; and exposes a `dcerpc_binding_handle` implementation used by generated NDR client stubs. Higher-level files such as SAMR, SPOOLSS, WINREG, NETLOGON, and endpoint mapper clients depend on this layer to turn generated `dcerpc_*` calls into authenticated transport I/O.

## Important APIs, types, and functions

The file defines private state containers `struct rpc_client_association` and `struct rpc_client_connection`. An association owns the DCE/RPC binding, target address, negotiated bind-time features, and monotonically increasing call id. A connection owns the concrete `rpc_cli_transport`, transport session key, local address, maximum fragment sizes, bind completion state, header-signing state, and next auth/presentation context ids. These are moved into `struct rpc_pipe_client` by `rpc_pipe_wrap_create()`.

Core transport helpers are `rpc_read_send/recv()`, `rpc_write_send/recv()`, `cli_api_pipe_send/recv()`, `get_complete_frag_send/recv()`, and `rpc_api_pipe_send/recv()`. They provide tevent-based asynchronous read/write loops, optional transport-level transceive, full-fragment reads, packet unmarshalling, authentication verification, multi-fragment response assembly, and auth3 write-only handling.

Binding helpers include `rpc_pipe_bind_send()`, `rpc_pipe_bind_recv()`, synchronous `rpc_pipe_bind()`, `create_rpc_bind_req()`, `create_rpc_bind_auth3()`, `create_rpc_alter_context()`, `create_bind_or_alt_ctx_internal()`, `check_bind_response()`, `rpc_bind_next_send()`, and `rpc_bind_finish_send()`. These drive anonymous and authenticated bind handshakes, including GENSEC token exchange, alter-context legs, auth3 finalization, bind-time feature negotiation, and header-signing negotiation.

The `dcerpc_binding_handle` integration is implemented through `rpccli_bh_ops`. Key callbacks are `rpccli_bh_raw_call_send/recv()`, `rpccli_bh_disconnect_send/recv()`, `rpccli_bh_is_connected()`, `rpccli_bh_set_timeout()`, `rpccli_bh_transport_session_key()`, `rpccli_bh_auth_session_key()`, `rpccli_bh_auth_info()`, and `rpccli_bh_do_ndr_print()`. `rpccli_bh_create()` builds a handle whose advertised binding flags reflect the selected authentication type, auth level, header signing, and local address.

Public open/auth helpers include `rpccli_anon_bind_data()`, `rpccli_ncalrpc_bind_data()`, `rpc_pipe_open_ncalrpc()`, `rpc_pipe_open_local_np()`, `rpc_pipe_open_np_send/recv()`, `cli_rpc_pipe_open_noauth_transport()`, `cli_rpc_pipe_open_noauth()`, `cli_rpc_pipe_reopen_np_noauth()`, `cli_rpc_pipe_open_with_creds()`, `cli_rpc_pipe_client_prepare_alter()`, `cli_rpc_pipe_client_auth_schannel()`, `cli_rpc_pipe_open_bind_schannel()`, and `cli_rpc_pipe_open_schannel_with_creds()`.

## Control flow

Opening starts by selecting a transport endpoint. `cli_rpc_pipe_open()` resolves a remote name when needed, uses default endpoints when available, maps TCP interfaces through the endpoint mapper when no default port exists, creates an association, opens a connection through `rpc_pipe_open_tcp_port()` or `rpc_client_connection_np()`, and wraps the result into `rpc_pipe_client`. Named-pipe opens attach the client to the owning `cli_state->pipe_list`; the destructor removes it.

Binding begins in `rpc_pipe_bind_send()`. The function moves `pipe_auth_data` onto the client, assigns auth and presentation context ids when they are still sentinel values, creates a binding handle, captures the GENSEC username into `printer_username`, builds the initial bind or alter PDU, and sends it through `rpc_api_pipe_send()`. The response path validates packet type, call id, auth trailers, negotiated transfer syntax, fragment sizes, association group id, and bind result. If GENSEC returns more processing, it sends an alter-context PDU; if GENSEC returns a final token, it sends an auth3 PDU; otherwise the bind completes.

Request calls enter through generated NDR stubs via `rpccli_bh_raw_call_send()`. `rpc_api_pipe_req_send()` assigns a new call id, prepares a security verification trailer when packet-level auth is active, then calls `prepare_next_frag()` repeatedly. Non-final request fragments are written directly; the final fragment is sent through `rpc_api_pipe_send()` so the response is read. Replies are accumulated in `rpc_api_pipe_got_pdu()`, which validates each fragment, checks response auth with `dcerpc_check_auth()`, enforces stable endianness, caps total data with `MAX_RPC_DATA_SIZE`, and returns the assembled stub blob.

Endpoint mapping uses a nested anonymous bind to the endpoint mapper. `rpc_pipe_get_tcp_port()` opens and binds an EPM pipe, then calls `rpccli_epm_map_interface()` and `rpccli_epm_map_binding()` to resolve a TCP endpoint. `rpc_pipe_get_ncalrpc_name()` performs the analogous ncalrpc lookup unless the requested interface is EPM itself.

## State and persistence behavior

The file maintains in-memory state only. Association state persists across binds on a client: association group id, bind-time feature results, and call ids are retained. Connection state tracks max fragment sizes, bind completion, header signing, transport, local socket address, and the SMB application key when opened over named pipes. Authentication state is stored in `rpc_pipe_client->auth`; presentation context verification is recorded in `rpc_pipe_client->verified_pcontext`; security trailer verification records `verified_bitmask1` in the auth object.

Secrets include GENSEC credentials, transport session keys, and authentication session keys. Session keys are copied into caller memory and marked with `talloc_keep_secret()`. The code does not write persistent files. `cli_rpc_pipe_reopen_np_noauth()` deliberately resets association group id, negotiated feature bits, call id, auth, connection, presentation context id, and verification state before rebinding anonymously.

## Dependencies and integration points

The implementation depends on Samba's tevent, talloc, generated NDR DCE/RPC structures, `auth_generic`, GENSEC, credentials, endpoint mapper stubs, Netlogon credential helpers, SMB client state, `smbXcli` session APIs, socket helpers, local named-pipe helpers, npa streams, and transport implementations from `rpc_transport_np.c`, `rpc_transport_sock.c`, and `rpc_transport_tstream.c`. Generated NDR client files integrate through `dcerpc_binding_handle` callbacks, not by calling transport helpers directly.

It integrates with SMB named pipes through `rpc_transport_np_init_send/recv()` and captures the SMB application key for transport-session-key queries. It integrates with local server code through `local_np_connect()` and `rpc_transport_tstream_init()`. Schannel-specific helpers integrate with `netlogon_creds_cli_context`, and endpoint discovery integrates with the EPM generated client.

## Risks and edge cases

This file is security-critical. Packet validation must keep packet type, call id, flags, auth trailer length, auth type, auth level, auth context id, and header-signing negotiation aligned or callers could accept spoofed or malformed replies. The code frees `cli->conn` synchronously on several protocol/security failures; callers must treat the binding handle as disconnected afterward. Multi-fragment reply assembly relies on `MAX_RPC_DATA_SIZE` and the 15 MiB allocation-hint guard to resist oversized responses.

Authentication code assumes `cli->auth` exists in paths such as `prepare_next_frag()`; public open helpers always bind first, but future raw uses must preserve that contract. Bind-time feature negotiation consumes an extra presentation context id only when the negotiation result is acknowledged. `cli_rpc_pipe_client_prepare_alter()` can keep an old connection alive when security context multiplexing is unavailable; callers need to understand that association and connection lifetimes are intentionally decoupled.

Transport opening maps UNIX/socket errors into NTSTATUS and usually frees partial state. TCP endpoint mapping has nested RPC dependency on EPM availability. NCALRPC path construction must fit in `sockaddr_un.sun_path`. Named-pipe reconnect depends on a valid original `cli_state`.

## Test signals

Useful tests include anonymous bind to known interfaces, authenticated NTLM/KRB5/SPNEGO/SCHANNEL binds, alter-context with new auth and presentation contexts, SMB1 and SMB2 named-pipe opens, TCP endpoint-mapper resolution, ncalrpc endpoint resolution, connection drop and `cli_rpc_pipe_reopen_np_noauth()`, fragmented request/reply sizes near negotiated fragment limits, malformed packet type/call id/auth trailer cases, and header-signing negotiation with and without server support. Existing generated NDR callers should exercise `rpccli_bh_raw_call_send/recv()` paths; transport tests should assert that disconnect state is visible through `rpccli_is_connected()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_pipe.h -->
# sources/user-network-fs/samba/source3/rpc_client/cli_pipe.h research

## Purpose

`cli_pipe.h` publishes the source3 RPC pipe client API implemented mainly by `cli_pipe.c` and partly by `cli_pipe_schannel.c`. It is the public contract used by higher-level Samba client code to open DCE/RPC pipes over SMB named pipes, TCP, ncalrpc, or local named pipes, bind them anonymously or with credentials, alter authentication/presentation contexts, and create binding handles for generated NDR stubs.

## Important APIs, types, and functions

The header forward-uses `struct rpc_pipe_client`, `struct pipe_auth_data`, `struct cli_state`, `struct cli_credentials`, `struct netlogon_creds_cli_context`, and generated `struct ndr_interface_table`. It includes `rpc_client/rpc_client.h` for RPC client structures and `auth/credentials/credentials.h` for credential ownership.

The bind API is `rpc_pipe_bind_send()`, `rpc_pipe_bind_recv()`, and synchronous `rpc_pipe_bind()`. Open APIs include asynchronous `rpc_pipe_open_np_send/recv()`, local `rpc_pipe_open_ncalrpc()`, local named-pipe `rpc_pipe_open_local_np()`, anonymous `cli_rpc_pipe_open_noauth()` and `cli_rpc_pipe_open_noauth_transport()`, credentialed `cli_rpc_pipe_open_with_creds()`, and reopen `cli_rpc_pipe_reopen_np_noauth()`.

Utility APIs are `rpccli_set_timeout()`, `rpccli_is_connected()`, `rpccli_ncalrpc_bind_data()`, `rpccli_anon_bind_data()`, `rpccli_bh_create()`, and `cli_rpc_pipe_client_prepare_alter()`. Schannel APIs are `cli_rpc_pipe_client_auth_schannel()`, `cli_rpc_pipe_open_bind_schannel()`, `cli_rpc_pipe_open_schannel_with_creds()`, and `cli_rpc_pipe_open_schannel()`.

## Control flow and contracts

Callers typically open a pipe for a generated interface table, obtain or construct `pipe_auth_data`, then bind. Convenience open helpers combine transport open and bind. The async named-pipe open returns an unbound `rpc_pipe_client`; callers then choose anonymous or authenticated bind. `rpccli_bh_create()` is normally called during bind but is exposed for code that needs a binding handle tied to an existing pipe.

The comment on `cli_rpc_pipe_open_with_creds()` says the routine steals or references the passed credentials depending on historical wording, while the implementation passes credentials into `auth_generic_set_creds()` and then moves the GENSEC security context into `pipe_auth_data`. Callers should not assume this header is a standalone ownership specification; the implementation and talloc hierarchy are authoritative.

## State and persistence behavior

The API manages in-memory connection, binding, authentication, and credential state. No persistent storage is exposed here. Functions that take `TALLOC_CTX *mem_ctx` return talloc-owned objects under that context. Several bind-data constructors allocate `pipe_auth_data` whose `auth_context_id` is intentionally left as `UINT32_MAX` so `rpc_pipe_bind_send()` can allocate a unique context id.

## Dependencies and integration points

This header is a hub between source3 SMB client code, auth/gensec credentials, generated NDR interfaces, Netlogon schannel credential state, and the lower transport implementations. Service-specific wrappers such as `cli_samr.c`, `cli_spoolss.c`, and `cli_winreg.c` depend on `rpc_pipe_client->binding_handle` after these APIs complete.

## Risks and test signals

API misuse risks include binding with an auth object whose lifetime is not transferable, calling generated stubs before a successful bind, attempting `cli_rpc_pipe_client_prepare_alter()` without requesting either a new auth or presentation context, and using schannel helpers without valid Netlogon credentials. Tests should compile all callers against this header, exercise async open/recv ownership, verify timeout and connected-state behavior, and cover all convenience open paths advertised here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_pipe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_pipe_schannel.c -->
# sources/user-network-fs/samba/source3/rpc_client/cli_pipe_schannel.c research

## Purpose

`cli_pipe_schannel.c` provides the high-level "open a pipe using schannel if appropriate" helper. It obtains domain trust credentials, establishes or reuses Netlogon credential state, chooses between Kerberos privacy, schannel authenticated RPC, and anonymous RPC based on negotiated Netlogon capabilities, and returns an opened `rpc_pipe_client`.

## Important APIs, types, and functions

The sole exported function is `cli_rpc_pipe_open_schannel()`. It accepts an SMB `cli_state`, messaging context, target interface table, transport, domain, remote name and address, output pipe, and optional output Netlogon credentials context. It uses `pdb_get_trust_credentials()`, `cli_credentials_add_gensec_features()`, `rpccli_create_netlogon_creds_ctx()`, `rpccli_connect_netlogon()`, `rpccli_setup_netlogon_creds()`, `netlogon_creds_cli_get()`, `cli_rpc_pipe_open_with_creds()`, `cli_rpc_pipe_open_schannel_with_creds()`, and `cli_rpc_pipe_open_noauth()`.

## Control flow

The function first loads trust credentials for the requested domain and disables delegation on those credentials. It creates a Netlogon credential context for the remote host. If the requested table is the Netlogon interface itself, it calls `rpccli_connect_netlogon()` and returns that pipe.

For other interfaces it establishes Netlogon credentials with `rpccli_setup_netlogon_creds()`, fetches the negotiated credential state, and inspects `negotiate_flags` and `authenticate_kerberos`. If Kerberos authentication was negotiated, it opens the target pipe with `DCERPC_AUTH_TYPE_KRB5` and privacy level using target service `"netlogon"`. If the server supports `NETLOGON_NEG_AUTHENTICATED_RPC`, it opens with schannel credentials. Otherwise it falls back to an anonymous named-pipe open.

## State and persistence behavior

State is talloc-scoped to a temporary frame until success. On success, the `rpc_pipe_client` is returned through `presult`; if `pcreds` is non-NULL, the Netlogon credentials context is moved to the caller's `mem_ctx`. Trust credentials and Netlogon credential state may internally come from passdb or credential caches, but this function itself writes no persistent data.

## Dependencies and integration points

The file integrates passdb trust account credential retrieval, GENSEC features, source3 Netlogon RPC helpers, Netlogon credential cache/locking code, and the generic pipe open/bind functions from `cli_pipe.c`. It is used by code that wants a secure RPC pipe without manually handling Netlogon negotiation details.

## Risks and test signals

The key risk is selecting the wrong authentication mode after Netlogon setup. Kerberos mode forces privacy and service `"netlogon"`; schannel mode requires valid machine account credentials; the fallback anonymous path may be insecure but preserves compatibility with servers lacking authenticated RPC flags. Tests should cover Netlogon table short-circuit, Kerberos-authenticated credential state, schannel-authenticated state, no-auth fallback, trust credential lookup failure, and propagation of a returned `netlogon_creds_cli_context`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_pipe_schannel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_samr.c -->
# sources/user-network-fs/samba/source3/rpc_client/cli_samr.c research

## Purpose

`cli_samr.c` implements source3 convenience helpers for the SAMR RPC interface. Its main responsibility is password-change preparation: it transforms plaintext old/new passwords or caller-provided blobs into the encrypted structures expected by SAMR change-password operations, invokes generated NDR SAMR calls, returns transport NTSTATUS separately from server result NTSTATUS, and wipes sensitive intermediate material. It also provides display-info pagination parameters and a compatibility sequence for SAMR connect variants.

## Important APIs, types, and functions

Password helpers include `dcerpc_samr_chgpasswd_user()` and `rpccli_samr_chgpasswd_user()` for handle-based `ChangePasswordUser`; `dcerpc_samr_chgpasswd_user2()` and `rpccli_samr_chgpasswd_user2()` for username-based `ChangePasswordUser2`; `dcerpc_samr_chng_pswd_auth_crap()` and its `rpccli_` wrapper for precomputed blobs; `dcerpc_samr_chgpasswd_user3()` and its wrapper for `ChangePasswordUser3` with domain/reject details; and `dcerpc_samr_chgpasswd_user4()` for the AES-based password change path.

Utility helpers are `dcerpc_get_query_dispinfo_params()` and `dcerpc_try_samr_connects()`. The file uses `samr_Password`, `samr_CryptPassword`, `samr_EncryptedPasswordAES`, `lsa_String`, `policy_handle`, `samr_DomInfo1`, and `userPwdChangeFailureInformation`.

## Control flow

The older password-change flows calculate NT hashes with `E_md4hash()` and, if permitted and possible, LM hashes with `E_deshash()`. They derive old-password-encrypted hash fields with `E_old_pw_hash()` and construct `samr_CryptPassword` buffers with `init_samr_CryptPassword()`, using the old NT hash as the session key for the crypt-password encoding. They then call generated SAMR operations such as `dcerpc_samr_ChangePasswordUser`, `ChangePasswordUser2`, or `ChangePasswordUser3`.

The `rpccli_` wrappers call the `dcerpc_` variants using `cli->binding_handle` and `cli->srv_name_slash`, then return the server-side `result` if the transport call succeeded. This preserves the Samba pattern where an RPC transport failure and an application-level SAMR failure are distinguished.

`dcerpc_samr_chgpasswd_user4()` implements the AES/HMAC-SHA512 password-change mechanism. It generates a random salt, derives a content-encryption key from the old NT hash and salt using PBKDF2-SHA512 with a random iteration count between 5000 and 1000000, encodes the new password into a 514-byte Unicode buffer, encrypts it with `samba_gnutls_aead_aes_256_cbc_hmac_sha512_encrypt()`, fills `samr_EncryptedPasswordAES`, and calls `dcerpc_samr_ChangePasswordUser4()`.

`dcerpc_try_samr_connects()` attempts `Connect5`, then `Connect4`, then `Connect2`, returning as soon as both transport status and SAMR result are success. `dcerpc_get_query_dispinfo_params()` returns empirically chosen `max_entries` and `max_size` values for repeated QueryDisplayInfo calls.

## State and persistence behavior

The file maintains no persistent state. It allocates temporary encrypted structures under the caller's talloc context and explicitly zeroes or burns plaintext hashes, LM/NT hash arrays, crypt-password buffers, AES keys, and password buffers before returning where implemented. Returned domain info or reject structures are allocated by the generated NDR call under the caller's `mem_ctx`.

## Dependencies and integration points

Dependencies include generated `ndr_samr_c` stubs, `rpc_client/rpc_client.h`, SAMR/LSA initialization helpers, legacy auth crypto helpers from `libcli_auth`, Samba GnuTLS helpers, and runtime configuration such as `lp_client_lanman_auth()`. The file integrates with `cli_pipe.c` through `struct rpc_pipe_client->binding_handle` and `srv_name_slash`.

## Risks and edge cases

This file handles plaintext passwords and derived hashes. The main risks are incomplete secret wiping on early returns, incorrect LM-hash behavior for long passwords, cryptographic API failures mapped to policy-like NTSTATUS values, and ensuring `presult` is meaningful only when the transport status is OK. The AES path defines `old_nt_key.size` with `sizeof(old_nt_key)`, not the size of the 16-byte key buffer; that is a subtle implementation detail worth targeted review because PBKDF2 input length must be exactly what the protocol expects.

Blob-based `dcerpc_samr_chng_pswd_auth_crap()` silently leaves zeroed fields when blobs are missing or shorter than expected; callers must validate blob provenance. `dcerpc_try_samr_connects()` keeps the final transport status even when earlier server results failed, so callers must inspect `presult`.

## Test signals

Tests should cover password changes with NT-only and LM-enabled configurations, long passwords that disable LM hashes, generated crypto failure paths, wrapper behavior that returns server result after successful transport, `ChangePasswordUser3` reject/domain-info outputs, AES `ChangePasswordUser4` with known test vectors if available, zeroization under failure, and SAMR connect fallback against servers supporting only Connect2 or Connect4.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_samr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_samr.h -->
# sources/user-network-fs/samba/source3/rpc_client/cli_samr.h research

## Purpose

`cli_samr.h` declares source3 SAMR convenience routines implemented in `cli_samr.c`. It provides both `dcerpc_binding_handle`-based APIs and `rpc_pipe_client` wrappers for password changes, plus helper declarations for QueryDisplayInfo sizing and compatible SAMR connect attempts.

## Important APIs, types, and functions

The header exposes `dcerpc_samr_chgpasswd_user()`, `rpccli_samr_chgpasswd_user()`, `dcerpc_samr_chgpasswd_user2()`, `rpccli_samr_chgpasswd_user2()`, `dcerpc_samr_chng_pswd_auth_crap()`, `rpccli_samr_chng_pswd_auth_crap()`, `dcerpc_samr_chgpasswd_user3()`, `rpccli_samr_chgpasswd_user3()`, and `dcerpc_samr_chgpasswd_user4()`. It also exposes `dcerpc_get_query_dispinfo_params()` and `dcerpc_try_samr_connects()`.

The declarations reference generated SAMR types such as `policy_handle`, `samr_DomInfo1`, and `userPwdChangeFailureInformation`, plus Samba `DATA_BLOB`, `NTSTATUS`, `TALLOC_CTX`, and `rpc_pipe_client`.

## Control flow and contracts

The `dcerpc_` functions accept an already-bound `struct dcerpc_binding_handle *h`; they return transport/call NTSTATUS and write the server-side SAMR result to `presult`. The `rpccli_` functions accept an already-bound `struct rpc_pipe_client *cli` and collapse the two-status pattern by returning the server result when transport succeeded.

Password-change variants differ in addressing and encoding: handle-based `ChangePasswordUser`, username/server-name based `ChangePasswordUser2`, blob-based ChangePasswordUser2, `ChangePasswordUser3` with policy feedback outputs, and AES `ChangePasswordUser4`.

## State and persistence behavior

The header exposes no global state. Output structures are caller-owned through `mem_ctx`, and callers are responsible for valid bound handles and policy handles. Server-name strings in `rpccli_` wrappers are supplied from `rpc_pipe_client->srv_name_slash`.

## Dependencies and integration points

This header is consumed by account/password tools and domain code that need SAMR password operations without duplicating crypto marshalling. It sits above generated NDR SAMR stubs and below user-facing utilities.

## Risks and test signals

Because the prototypes expose plaintext password parameters, callers must control lifetimes and logging. Tests should verify both direct `dcerpc_` and `rpccli_` APIs, ensure `presult` is initialized on failures as expected by callers, and compile-check all declared functions against generated SAMR type definitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_samr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_spoolss.c -->
# sources/user-network-fs/samba/source3/rpc_client/cli_spoolss.c research

## Purpose

`cli_spoolss.c` implements convenience wrappers around generated SPOOLSS RPC client stubs. The wrappers hide common SPOOLSS boilerplate: user-level containers, devmode/security descriptor placeholder containers, WERROR versus NTSTATUS conversion, and the common two-call "insufficient buffer/more data, allocate needed size, retry" pattern used by many printer enumeration and query APIs.

## Important APIs, types, and functions

Open/create APIs are `rpccli_spoolss_openprinter_ex()` and `rpccli_spoolss_addprinterex()`. Query APIs include `rpccli_spoolss_getprinterdriver()`, `rpccli_spoolss_getprinterdriver2()`, `rpccli_spoolss_getprinter()`, `rpccli_spoolss_getjob()`, `rpccli_spoolss_getprinterdata()`, `rpccli_spoolss_enumprinterkey()`, and `rpccli_spoolss_enumprinterdataex()`.

Enumeration APIs include `rpccli_spoolss_enumforms()`, `rpccli_spoolss_enumprintprocessors()`, `rpccli_spoolss_enumprintprocessordatatypes()`, `rpccli_spoolss_enumports()`, `rpccli_spoolss_enummonitors()`, `rpccli_spoolss_enumjobs()`, `rpccli_spoolss_enumprinterdrivers()`, and `rpccli_spoolss_enumprinters()`.

The file uses generated unions and structs such as `spoolss_DriverInfo`, `spoolss_PrinterInfo`, `spoolss_JobInfo`, `spoolss_FormInfo`, `spoolss_PrintProcessorInfo`, `spoolss_PortInfo`, `spoolss_MonitorInfo`, `spoolss_PrinterEnumValues`, `spoolss_SetPrinterInfoCtr`, `spoolss_UserLevelCtr`, and `policy_handle`.

## Control flow

Each wrapper obtains `struct dcerpc_binding_handle *b = cli->binding_handle` and calls the corresponding generated `dcerpc_spoolss_*` function. If the generated call returns a non-OK NTSTATUS, the wrapper returns `ntstatus_to_werror(status)`. Otherwise it returns or processes the WERROR result supplied by the server.

Most query/enumeration wrappers accept an `offered` buffer size. If `offered > 0`, the wrapper allocates a zeroed `DATA_BLOB` of that size and passes it to the generated stub. If the server returns `WERR_INSUFFICIENT_BUFFER` or `WERR_MORE_DATA`, the wrapper reallocates with the returned `needed` size and retries once. Results are returned through generated output pointers such as `info`, `count`, `server_major_version`, `server_minor_version`, `type`, and data buffers.

`rpccli_spoolss_openprinter_ex()` initializes a `spoolss_UserLevel1` from `cli->printer_username`, wraps it in a user-level container, and calls `OpenPrinterEx`. `rpccli_spoolss_addprinterex()` similarly supplies user-level, devmode, and security descriptor containers and uses `cli->srv_name_slash` as the server name.

## State and persistence behavior

The file does not maintain state beyond allocations under the caller's `mem_ctx`. It uses state prepared during pipe binding: `cli->binding_handle`, `cli->printer_username`, and `cli->srv_name_slash`. Returned policy handles and information structures represent server-side printer state, but the local wrappers do not persist anything.

## Dependencies and integration points

Dependencies include generated `ndr_spoolss_c` stubs, `rpc_client/rpc_client.h`, `cli_spoolss.h`, GENSEC/credential headers for client structures, and `init_spoolss.h` for `spoolss_init_spoolss_UserLevel1()`. The wrappers are integration points for Samba utilities and management code that need printer RPCs without manually performing SPOOLSS buffer retries.

## Risks and edge cases

The repeated buffer-sizing pattern trusts server-provided `needed`; a malicious or broken server can force large allocations. Most wrappers retry only once, so a changing server-side object can still return buffer errors to the caller. Some local `DATA_BLOB buffer` variables are only initialized when `offered > 0`, but the code only passes `&buffer` in that case. `rpccli_spoolss_getprinterdata()` always allocates `offered` bytes, so an initial zero-size request may produce allocation behavior that depends on `talloc_zero_array()` semantics.

Conversion from NTSTATUS to WERROR loses some transport detail but matches the declared WERROR interface. Callers must distinguish a returned server WERROR from a converted transport failure only by value.

## Test signals

Tests should cover each wrapper with first-call success, first-call insufficient-buffer/more-data followed by success, generated NTSTATUS failure converted to WERROR, server WERROR failure returned unchanged, zero offered size, very large needed size guard behavior at higher layers, and open/add paths with initialized `printer_username` and `srv_name_slash`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_spoolss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_spoolss.h -->
# sources/user-network-fs/samba/source3/rpc_client/cli_spoolss.h research

## Purpose

`cli_spoolss.h` declares source3 convenience wrappers for the SPOOLSS RPC interface. It gives callers WERROR-returning APIs for printer open, add, query, and enumeration operations while hiding generated NDR call details.

## Important APIs, types, and functions

The header declares `rpccli_spoolss_openprinter_ex()`, `rpccli_spoolss_getprinterdriver()`, `rpccli_spoolss_getprinterdriver2()`, `rpccli_spoolss_addprinterex()`, `rpccli_spoolss_getprinter()`, `rpccli_spoolss_getjob()`, `rpccli_spoolss_enumforms()`, `rpccli_spoolss_enumprintprocessors()`, `rpccli_spoolss_enumprintprocessordatatypes()`, `rpccli_spoolss_enumports()`, `rpccli_spoolss_enummonitors()`, `rpccli_spoolss_enumjobs()`, `rpccli_spoolss_enumprinterdrivers()`, `rpccli_spoolss_enumprinters()`, `rpccli_spoolss_getprinterdata()`, `rpccli_spoolss_enumprinterkey()`, and `rpccli_spoolss_enumprinterdataex()`.

The prototypes use `struct rpc_pipe_client`, `policy_handle`, generated SPOOLSS unions, WINREG value type enum, `DATA_BLOB`-style byte outputs, and caller-provided talloc contexts.

## Control flow and contracts

All functions require an already-opened and bound `rpc_pipe_client` for the SPOOLSS interface. Query and enumeration APIs follow a caller-visible `offered` size contract but internally may retry with a server-provided `needed` size. Output arrays and information unions are allocated or filled under `mem_ctx`.

## State and persistence behavior

The header itself exposes no state. The wrappers consume `cli->binding_handle`, and some open/add operations depend on username/server-name fields populated by the bind layer. Server-side state is accessed through policy handles returned by SPOOLSS.

## Dependencies and integration points

This header is included by printer administration and RPC client code. It aligns source3 callers with generated SPOOLSS NDR structures while using WERROR as the public status type.

## Risks and test signals

The main API risks are invalid policy handles, wrong `level` values for output unions, and callers supplying too-small or zero `offered` sizes without handling retry errors. Compile tests should ensure generated SPOOLSS types remain compatible; behavioral tests should validate open, query, enum, and buffer retry contracts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_spoolss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_winreg.c -->
# sources/user-network-fs/samba/source3/rpc_client/cli_winreg.c research

## Purpose

`cli_winreg.c` provides typed helper functions over generated WINREG RPC calls. It queries, sets, enumerates, and recursively deletes registry values/keys while converting between Samba-native data representations and WINREG wire formats such as `REG_DWORD`, `REG_BINARY`, `REG_SZ`, `REG_EXPAND_SZ`, `REG_MULTI_SZ`, and security descriptors.

## Important APIs, types, and functions

Typed query APIs are `dcerpc_winreg_query_dword()`, `dcerpc_winreg_query_binary()`, `dcerpc_winreg_query_multi_sz()`, `dcerpc_winreg_query_sz()`, and `dcerpc_winreg_query_sd()`. Set APIs are `dcerpc_winreg_set_dword()`, `dcerpc_winreg_set_sz()`, `dcerpc_winreg_set_expand_sz()`, `dcerpc_winreg_set_multi_sz()`, `dcerpc_winreg_set_binary()`, and `dcerpc_winreg_set_sd()`. Mutation/enumeration helpers are `dcerpc_winreg_add_multi_sz()`, `dcerpc_winreg_enum_keys()`, `dcerpc_winreg_enumvals()`, and `dcerpc_winreg_delete_subkeys_recursive()`.

The file uses generated `winreg_String`, `winreg_StringBuf`, `winreg_ValNameBuf`, `winreg_Type`, `policy_handle`, `NTTIME`, and generated WINREG RPC calls. It also uses registry utility marshalling functions `pull_reg_multi_sz()`, `pull_reg_sz()`, `push_reg_sz()`, and `push_reg_multi_sz()`, plus NDR security descriptor push/pull functions.

## Control flow

Typed query helpers follow a two-call flow. They first call `dcerpc_winreg_QueryValue()` with no data buffer to obtain type and size. They verify the returned type, allocate a zeroed blob of the reported size, call `QueryValue()` again with a buffer, then decode the result into a typed output. DWORD queries require `REG_DWORD` and exactly four bytes. String and multi-string queries use registry utility pull helpers. Security descriptor queries call the binary query helper and then NDR-decode a `security_descriptor`.

Set helpers marshal typed input into a `DATA_BLOB` and call `dcerpc_winreg_SetValue()` with the matching registry type. `dcerpc_winreg_set_sd()` NDR-encodes the descriptor and delegates to binary set. `dcerpc_winreg_add_multi_sz()` reads the existing multi-string list, appends one pointer plus a NULL terminator, and writes it back.

`dcerpc_winreg_enum_keys()` calls `QueryInfoKey()` to obtain subkey counts and maximum lengths, allocates an array, then loops over `EnumKey()`. It treats `WERR_NO_MORE_ITEMS` as successful termination. `dcerpc_winreg_enumvals()` similarly calls `QueryInfoKey()` for value counts and maximum buffer sizes, loops over `EnumValue()`, and returns parallel arrays of names, types, and `DATA_BLOB`s. `dcerpc_winreg_delete_subkeys_recursive()` opens a key, enumerates its subkeys, recursively deletes children, closes the opened key handle, and deletes the key from its hive handle.

## State and persistence behavior

The file maintains no local persistent state. It directly reads and mutates the remote or internal registry visible through the supplied binding handle and policy handles. Local allocations are under `mem_ctx` or stackframe temporary contexts. Recursive deletion changes server registry state and should be treated as destructive.

## Dependencies and integration points

The helpers sit above generated `ndr_winreg_c` stubs and below registry management callers. They integrate with security descriptor NDR helpers, registry string/multi-string utilities, Samba status conventions (`NTSTATUS` plus output `WERROR`), and policy handles opened elsewhere, including by `cli_winreg_int.c`.

## Risks and edge cases

Type-specific query helpers return `NT_STATUS_OBJECT_TYPE_MISMATCH` when server type differs, while server-side `WERROR` remains in `pwerr`; callers need to check both. `dcerpc_winreg_set_dword()` allocates a blob and writes to it without explicitly checking allocation before `SIVAL()`, unlike several other helpers. `dcerpc_winreg_add_multi_sz()` does not special-case a failed query before iterating over `a`; a failed query can still lead to appending to a NULL list and overwriting the value depending on `pwerr` and caller expectations.

Enumeration relies on maximum lengths reported by `QueryInfoKey()`; changing registry contents during enumeration can produce truncated data, early `NO_MORE_ITEMS`, or mismatched final counts. `dcerpc_winreg_enum_keys()` sets `*pnum_subkeys` to the original queried count even if enumeration breaks early on `NO_MORE_ITEMS`. Recursive deletion uses caller `mem_ctx` for recursive path allocations and can grow memory with deep trees.

## Test signals

Tests should cover each registry type query/set, type mismatch handling, zero-length binary/string values, security descriptor round trip, multi-string append with existing and missing values, enumeration of empty and populated keys, changing values during enumeration, recursive deletion with nested keys, handle close behavior, and dual-status propagation where NTSTATUS succeeds but WERROR fails.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_winreg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_winreg.h -->
# sources/user-network-fs/samba/source3/rpc_client/cli_winreg.h research

## Purpose

`cli_winreg.h` declares typed source3 helper APIs for WINREG RPC operations. It lets callers query and set registry values using Samba-native C types instead of manually marshalling WINREG byte buffers and generated NDR structures.

## Important APIs, types, and functions

The header declares typed query functions for DWORD, binary, multi-string, string, and security descriptor values: `dcerpc_winreg_query_dword()`, `dcerpc_winreg_query_binary()`, `dcerpc_winreg_query_multi_sz()`, `dcerpc_winreg_query_sz()`, and `dcerpc_winreg_query_sd()`.

It declares typed setters `dcerpc_winreg_set_dword()`, `dcerpc_winreg_set_sz()`, `dcerpc_winreg_set_expand_sz()`, `dcerpc_winreg_set_multi_sz()`, `dcerpc_winreg_set_binary()`, and `dcerpc_winreg_set_sd()`. It also declares `dcerpc_winreg_add_multi_sz()`, `dcerpc_winreg_enum_keys()`, `dcerpc_winreg_enumvals()`, and `dcerpc_winreg_delete_subkeys_recursive()`.

## Control flow and contracts

All APIs require an existing WINREG `dcerpc_binding_handle` and an already-opened `policy_handle` for the relevant key or hive. The functions return transport/call NTSTATUS and write server-side registry status to `WERROR *pwerr`. Query outputs and enumeration arrays are talloc-owned under `mem_ctx`.

The header documents value-type expectations, but callers must still check both NTSTATUS and WERROR. Enumeration returns arrays whose shape depends on server-reported counts. Recursive deletion expects a hive handle plus a key path relative to that hive.

## State and persistence behavior

The header exposes mutating APIs that alter registry values and keys on the target server. It has no local state. Output memory ownership is through the supplied talloc context.

## Dependencies and integration points

Consumers include registry tools, print/registry configuration code, and internal WINREG open helpers. The declarations integrate generated WINREG types, security descriptors, and Samba `DATA_BLOB` with higher-level registry workflows.

## Risks and test signals

Misuse risks include ignoring `pwerr`, passing a policy handle opened with insufficient access rights, using setters with data not encoded as expected for Windows registry semantics, and recursively deleting unintended keys. Tests should compile-check generated type compatibility and behaviorally validate dual-status handling, ownership of returned arrays/blobs, and destructive operation safeguards at caller layers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_winreg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_winreg_int.c -->
# sources/user-network-fs/samba/source3/rpc_client/cli_winreg_int.c research

## Purpose

`cli_winreg_int.c` provides helpers for connecting to Samba's internal WINREG server and opening registry keys. It normalizes hive/key paths, creates an internal RPC binding handle using local session information, opens the requested hive, and then opens or creates the requested key.

## Important APIs, types, and functions

The private `_split_hive_key()` normalizes a path into hive name and subkey string. The private `_winreg_int_openkey()` creates the binding and opens a hive/key for a numeric hive type. Public APIs are `dcerpc_winreg_int_openkey()` for paths containing a hive prefix and `dcerpc_winreg_int_hklm_openkey()` for paths relative to HKLM.

The implementation uses `auth_session_info`, `messaging_context`, `tsocket_address`, generated `ndr_table_winreg`, `rpcint_binding_handle()`, generated open-hive calls (`OpenHKLM`, `OpenHKCR`, `OpenHKU`, `OpenHKCU`, `OpenHKPD`), `dcerpc_winreg_OpenKey()`, and `dcerpc_winreg_CreateKey()`.

## Control flow

`_split_hive_key()` rejects NULL or empty paths, converts `/` to `\` when no backslash is present, strips trailing backslashes, splits the first path component as the hive, and returns the remainder as the subkey. `dcerpc_winreg_int_openkey()` maps hive names such as `HKLM`, `HKEY_LOCAL_MACHINE`, `HKCR`, `HKU`, `HKCU`, and `HKPD` to numeric hive constants, then delegates to `_winreg_int_openkey()`.

`_winreg_int_openkey()` creates a loopback `tsocket_address` for `127.0.0.1`, obtains an internal binding handle with the supplied session and messaging context, opens the selected hive with the requested access mask, and then either creates or opens the requested key. On create it logs whether a new or existing key was returned. On any generated NTSTATUS failure or server WERROR failure it frees the binding handle and returns the error. On success it returns the binding handle and policy handles to the caller.

## State and persistence behavior

The function returns live RPC binding and policy handles. If `create_key` is true it can create registry keys in the internal registry server. Otherwise it only opens existing keys. It allocates path pieces and handles under the caller's `mem_ctx` and writes no local files.

## Dependencies and integration points

This file integrates source3 server-side session identity, messaging, internal RPC binding creation (`rpc_server/rpc_ncacn_np.h`), generated WINREG RPC stubs, and registry constants from `include/registry.h`. Higher-level registry code can combine these open helpers with typed value helpers from `cli_winreg.c`.

## Risks and edge cases

There is a notable path-handling risk: `dcerpc_winreg_int_openkey()` computes both `hivename` and `subkey`, but delegates to `_winreg_int_openkey()` with `key` rather than `subkey`. If generated WINREG `OpenKey` expects a path relative to the opened hive, passing the full hive-prefixed path can fail or create/open the wrong path. `dcerpc_winreg_int_hklm_openkey()` intentionally passes the caller's key as HKLM-relative, so the inconsistency deserves focused testing.

`_split_hive_key()` only converts slash separators when the path contains no backslash at all; mixed separators are not normalized. It strips trailing backslashes before splitting. The loopback binding uses port 0 with an internal binding helper, so correctness depends on `rpcint_binding_handle()` interpreting the local address in the expected way. Access masks are reused for both hive and subkey open/create.

## Test signals

Tests should cover hive-only paths, hive plus subkey paths, legacy slash paths, mixed slash/backslash paths, trailing separators, unknown hives, create versus open behavior, each supported hive, insufficient access masks, session identity propagation, and specifically whether `dcerpc_winreg_int_openkey("HKLM\\Software\\...")` opens a key relative to HKLM or incorrectly includes the hive prefix.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_winreg_int.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_winreg_int.h -->
# sources/user-network-fs/samba/source3/rpc_client/cli_winreg_int.h research

## Purpose

`cli_winreg_int.h` declares internal WINREG client helpers used to connect to Samba's local/internal WINREG RPC server and open registry keys. It is narrower than `cli_winreg.h`: it only covers binding and key-open setup, not typed value query/set operations.

## Important APIs, types, and functions

The header forward-declares `struct auth_session_info` and `struct dcerpc_binding_handle`, then declares `dcerpc_winreg_int_openkey()` and `dcerpc_winreg_int_hklm_openkey()`. Both return NTSTATUS and output a binding handle, hive policy handle, key policy handle, and server-side WERROR.

`dcerpc_winreg_int_openkey()` accepts a key path that must begin with a hive name such as HKLM. `dcerpc_winreg_int_hklm_openkey()` accepts a key path intended to be opened under HKEY_LOCAL_MACHINE.

## Control flow and contracts

Callers supply a talloc context, session info, messaging context, requested key, `create_key` flag, and access mask. On success they receive an internal WINREG binding handle and two policy handles. If `create_key` is true, the implementation may create the subkey path if absent. Callers should check both NTSTATUS and `pwerr`.

## State and persistence behavior

The functions can mutate registry state by creating keys. Returned handles keep local RPC resources alive until closed/freed by the caller. The header does not define persistent local state.

## Dependencies and integration points

These declarations are used by server-side or local management code that needs registry access under a specific authenticated session. The resulting binding handle can be passed to typed helpers from `cli_winreg.c`.

## Risks and test signals

Risks include passing a key path in the wrong form, ignoring `pwerr`, leaking policy handles, or creating keys unintentionally. Tests should validate both full-hive and HKLM-relative APIs, success and failure ownership, and compatibility with the typed WINREG helpers after the key is opened.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_winreg_int.h -->
