# Research: subset-b-009939

Grouped research for Samba source4 librpc DCERPC transport/Python binding files and the source4 NBT server files. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_roh_channel_out.c -->
# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_roh_channel_out.c

## Purpose

`dcerpc_roh_channel_out.c` implements the RPC-over-HTTP outgoing channel pieces for Samba's DCE/RPC client. It sends the HTTP `RPC_OUT_DATA` request, sends the RTS `CONN/A1` PDU, reads the HTTP response, and parses RTS responses such as `CONN/A3` and `CONN/C2`.

## Important APIs, Types, and Functions

Important state structs are `roh_request_state`, `roh_send_pdu_state`, `roh_recv_response_state`, and `roh_recv_pdu_state`. Exported async pairs include `roh_send_RPC_DATA_OUT_send/recv()`, `roh_send_CONN_A1_send/recv()`, `roh_recv_out_channel_response_send/recv()`, `roh_recv_CONN_A3_send/recv()`, and `roh_recv_CONN_C2_send/recv()`.

## Control Flow

The send path builds an HTTP/1.0 RPC_OUT_DATA request to `/rpc/rpcproxy.dll?<server>:<port>`, adds RPC proxy headers, and submits it through `http_send_auth_request_send()`. `CONN/A1` constructs a DCERPC RTS packet with version, virtual connection cookie, out-channel cookie, and receive window size, marshals it with NDR, and writes it to the HTTP connection tstream queue. The receive paths call `http_read_response_send()` or `dcerpc_read_ncacn_packet_send()`, then validate RTS command counts and command types before returning timeout/window/version values.

## State and Persistence Behavior

No disk state is written. Runtime state lives under tevent request allocations and references `roh->default_channel_out`, `roh->connection_cookie`, and channel cookies. The channel's HTTP connection stream and send queue carry persistent transport state outside this file.

## Dependencies and Integration Points

This file depends on tevent, talloc, tstream, Samba HTTP helpers, NDR DCERPC marshalling, credentials/loadparm for authenticated HTTP, and `struct roh_connection` from `dcerpc_roh.h`. It is built into the `dcerpc` library and integrates with the complementary RPC-over-HTTP channel-in and high-level ROH connection code.

## Risks and Test Signals

Risks include hard-coded content length/frag length assumptions, incomplete HTTP status mapping, TODO certificate path handling, and strict RTS command ordering. Tests should cover authenticated proxy setup, 401/503 response handling, malformed RTS packets, short writes, command-count validation, and full ROH handshakes through a proxy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_roh_channel_out.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_schannel.c -->
# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_schannel.c

## Purpose

`dcerpc_schannel.c` establishes Netlogon secure-channel credentials and then binds a DCE/RPC pipe using schannel or Kerberos Netlogon authentication. It is security-critical code for machine-account authentication, secure channel negotiation, and downgrade detection.

## Important APIs, Types, and Functions

`struct schannel_key_state` tracks the secondary netlogon pipe, negotiated flags, challenges, credential material, and Kerberos authenticate request state. `struct auth_schannel_state` tracks the final bind and LogonGetCapabilities verification. The public entry points are `dcerpc_bind_auth_schannel_send()` and `dcerpc_bind_auth_schannel_recv()`. Internal stages include `dcerpc_schannel_key_send/recv()`, `continue_epm_map_binding()`, `continue_secondary_connection()`, `continue_bind_auth_krb5()`, `start_srv_challenge()`, `continue_srv_auth2()`, `continue_get_negotiated_capabilities()`, `continue_get_client_capabilities()`, and `continue_logon_control_do()`.

## Control Flow

The key setup path derives required/local negotiate flags from binding flags and loadparm policy, endpoint-maps the Netlogon interface, opens a secondary pipe, and binds either with Kerberos or no auth. Kerberos-capable paths call `netr_ServerAuthenticateKerberos`; fallback paths call `netr_ServerReqChallenge` followed by `netr_ServerAuthenticate2`. After a successful key exchange, the outer schannel bind stores the netlogon creds on `cli_credentials`, binds the requested interface, and for Netlogon pipes verifies server and client capabilities with `netr_LogonGetCapabilities`, using `netr_LogonControl` as a fallback consistency check for older or patched/unpatched behavior.

## State and Persistence Behavior

The file mutates in-memory `cli_credentials` by installing `netlogon_creds_CredentialState`. It adjusts connection flags such as `DCERPC_SEAL` and schannel/Kerberos flags. It does not persist secrets to disk; machine password material is read from credentials and used to derive credential state. Capability and authenticator state is copied and advanced carefully to keep sequence numbers synchronized.

## Dependencies and Integration Points

Dependencies include generated Netlogon client stubs, libcli auth netlogon credential helpers, credentials, GENSEC settings, loadparm crypto policy, endpoint mapper helpers, secondary connection helpers, and DCE/RPC bind-auth functions. `dcerpc_util.c` invokes this file when `DCERPC_SCHANNEL` is requested and no netlogon creds are already cached.

## Risks and Test Signals

Risks are downgrade acceptance, policy drift around AES/MD5/strong-key requirements, Kerberos Netlogon feature availability, secondary-pipe lifecycle errors, and sequence-number desynchronization in fallback probes. Test signals include schannel with AES, strong-key-only, MD5-rejected, Kerberos Netlogon enabled/disabled, RODC channel type, legacy NT/Samba servers, tampered capability replies, and authentication retry after server `ACCESS_DENIED`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_schannel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_secondary.c -->
# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_secondary.c

## Purpose

`dcerpc_secondary.c` creates secondary DCE/RPC connections or authenticated secondary pipes from an existing primary pipe. It is used for authentication fallbacks, basis connections in Python bindings, and multi-context/multi-pipe workflows that must reuse transport context.

## Important APIs, Types, and Functions

`struct sec_conn_state` carries primary pipe, new pipe, and duplicated binding. `struct sec_auth_conn_state` wraps secondary connection plus bind/auth state. Public APIs are `dcerpc_secondary_connection_send/recv()`, `dcerpc_secondary_auth_connection_send/recv()`, and synchronous `dcerpc_secondary_auth_connection()`. Transport callbacks include `continue_open_smb()`, `continue_open_tcp()`, `continue_open_ncalrpc()`, `continue_open_ncacn_unix()`, and `continue_pipe_open()`.

## Control Flow

The send path duplicates the supplied binding, initializes a second pipe on the same event context, fills missing host, target hostname, endpoint, local address, or ncalrpc directory from the primary binding, and dispatches by the primary connection transport. SMB named pipes reuse the SMB connection/session/tcon, TCP requires an IP host and endpoint port, ncalrpc builds a Unix-socket path from the ncalrpc directory and endpoint, and Unix stream opens the endpoint path directly. Successful opens copy flags and binding to the new pipe.

## State and Persistence Behavior

No persistent storage is used. The new pipe is allocated under the composite context, then stolen under the primary pipe or caller memory on receive. TCP open updates the duplicated binding's `localaddress` and `host` to the actual local and remote addresses.

## Dependencies and Integration Points

This code depends on `dcerpc_smb.c`, `dcerpc_sock.c`, binding helpers, resolve context setup, composite async contexts, and `dcerpc_pipe_auth_send()` from `dcerpc_util.c`. It is directly used by schannel setup, auth fallback from SPNEGO to NTLMSSP, Python basis connections, and other callers needing a second pipe.

## Risks and Test Signals

Risks include missing endpoint/host fallback, rejecting non-IP TCP hostnames in secondary paths, talloc ownership mistakes when auth fallback replaces the original pipe, and transport-specific option propagation. Tests should cover secondary pipes for `ncacn_np`, `ncacn_ip_tcp`, `ncalrpc`, and `ncacn_unix_stream`, plus authenticated secondary binds with and without credentials.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_secondary.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_smb.c -->
# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_smb.c

## Purpose

`dcerpc_smb.c` implements DCE/RPC over SMB named pipes (`ncacn_np`). It opens a named pipe over an existing SMB1 or SMB2 tree/session and configures the generic DCE/RPC connection around the resulting `tstream_smbXcli_np` stream.

## Important APIs, Types, and Functions

`struct smb_private` stores the SMB session key, connection, session, tree connect, and timeout used for secondary named-pipe opens. Public APIs include `dcerpc_pipe_open_smb_send/recv()`, synchronous `dcerpc_pipe_open_smb()` for SMB1, `dcerpc_pipe_open_smb2()` for SMB2, and `dcerpc_secondary_smb_send/recv()`. `smb_session_key()` exposes the stored SMB application session key to RPC security code.

## Control Flow

The async open path normalizes pipe names by stripping `/pipe/`, `\\pipe\\`, and leading slash/backslash prefixes, captures SMB transport handles, records the remote server name, fetches the SMB application session key, and opens the named pipe with `tstream_smbXcli_np_open_send()`. Completion installs the stream, write queue, `NCACN_NP` transport type, Windows-compatible 4280 fragment limits, session-key callback, and transport encryption flag based on the SMB2 encryption cipher.

## State and Persistence Behavior

The file stores transport private state on `c->transport.private_data` and keeps the SMB session key in memory. It does not own or persist SMB sessions; it references caller-provided SMB handles. If no RPC binding exists, the synchronous helpers create an `ncacn_np:<remote>` binding.

## Dependencies and Integration Points

Dependencies include SMB raw and SMB2 client structures, `smbXcli` base/session helpers, `tstream_smbXcli_np`, tevent queues, and DCE/RPC connection internals. Secondary connection creation reuses this state through `dcerpc_secondary_smb_send()`.

## Risks and Test Signals

Risks include pipe-name normalization edge cases, absent user session keys, mismatched SMB encryption detection, lifetime coupling to SMB session/tree objects, and fragment-size assumptions. Tests should open RPC pipes over SMB1 and SMB2, with encrypted and unencrypted SMB3 sessions, missing session key behavior, secondary pipe reuse, and pipe names in all accepted slash forms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_smb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_sock.c -->
# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_sock.c

## Purpose

`dcerpc_sock.c` implements socket-backed DCE/RPC transports for TCP, Unix stream sockets, and local ncalrpc-style pipe paths. It converts connected sockets into DCE/RPC `tstream` transports and handles asynchronous name resolution and address retry for TCP.

## Important APIs, Types, and Functions

Key state structs are `pipe_open_socket_state`, `pipe_tcp_state`, and `pipe_unix_state`. Important APIs are `dcerpc_pipe_open_tcp_send/recv()`, `dcerpc_pipe_open_unix_stream_send/recv()`, `dcerpc_pipe_open_pipe_send/recv()`, and synchronous `dcerpc_pipe_open_pipe()`. Shared helpers include `dcerpc_pipe_open_socket_send/recv()` and `continue_socket_connect()`.

## Control Flow

The generic socket open creates a stream socket, connects it, captures the local address and file descriptor, marks the socket no-close, wraps it in `tstream_bsd_existing_socket()`, installs the write queue, sets transport type and 5840 fragment sizes, and blocks SIGPIPE. TCP first resolves a NetBIOS name with `resolve_name_send()`, tries each resolved address until one connects, and returns actual local/remote addresses. Unix stream and ncalrpc construct Unix socket addresses; ncalrpc canonicalizes slash separators and combines an ncalrpc directory with the identifier.

## State and Persistence Behavior

Transport state is held on `struct dcecli_connection` and in talloc-owned state objects. No disk state is created. TCP stores actual local and remote address strings for binding update by secondary connection logic.

## Dependencies and Integration Points

Dependencies include Samba socket and tsocket/tstream layers, composite async contexts, resolve APIs, DCE/RPC connection internals, and transport enum values from RPC common headers. This file is called by generic connection setup and secondary connection code.

## Risks and Test Signals

Risks include address-list retry correctness, local bind failures, target-hostname null handling for local transports, Unix path canonicalization, descriptor ownership after `SOCKET_FLAG_NOCLOSE`, and SIGPIPE process-wide side effects. Test signals include DNS/NetBIOS multi-address failover, localaddress binding, IPv4/IPv6 reachability where supported, Unix/ncalrpc path opens, and simulated connect failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_sock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_util.c -->
# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_util.c

## Purpose

`dcerpc_util.c` provides utility operations around DCE/RPC interface lookup, endpoint mapper resolution, authentication policy selection, authentication fallback, session-key defaults, and secondary presentation contexts.

## Important APIs, Types, and Functions

Public functions include `dcerpc_iface_find_call()`, `dcerpc_epm_map_binding_send/recv()`, synchronous `dcerpc_epm_map_binding()`, `dcerpc_pipe_auth_send/recv()`, synchronous `dcerpc_pipe_auth()`, `dcecli_generic_session_key()`, and `dcerpc_secondary_context()`. Main state structs are `epm_map_binding_state` and `pipe_auth_state`.

## Control Flow

Endpoint mapping first sets the abstract syntax, scans IDL default endpoints for a matching transport, and otherwise connects anonymously to epmapper, builds an EPM tower, calls `epm_Map`, validates one returned tower, extracts floor 3 RHS endpoint data, and writes it into the binding. Authentication chooses no-auth for anonymous credentials, special ncalrpc-as-system auth for configured local bindings, schannel setup when requested and missing netlogon creds, implicit no-auth over unsigned named pipes, or authenticated bind with SPNEGO/KRB5/schannel/NTLM. Auto auth starts with SPNEGO and can retry with NTLMSSP or a better password on a secondary connection.

## State and Persistence Behavior

The code mutates connection flags from binding flags and can replace the caller's pipe during authentication fallback. It stores endpoint and abstract-syntax data in the binding and creates secondary context IDs via `dcerpc_alter_context()`. It does not write persistent data.

## Dependencies and Integration Points

Dependencies include epmapper generated stubs, NDR tower helpers, credentials, GENSEC settings, schannel helpers, secondary connection helpers, bind/auth functions in core DCE/RPC, and loadparm. It is central glue used by connection code, Python bindings, schannel, and callers that need endpoint lookup.

## Risks and Test Signals

Risks include incorrect default endpoint selection, tower floor assumptions, auth fallback ownership changes, implicit sign defaulting, anonymous/no-auth over SMB named pipes relying on SMB-layer auth, and handling of wrong-password retries. Tests should cover default endpoints, EPM lookup, SPNEGO success, SPNEGO-to-NTLM fallback, Kerberos wrong-password retry, schannel, ncalrpc-as-system, and `alter_context` secondary context creation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/pyrpc.c -->
# sources/user-network-fs/samba/source4/librpc/rpc/pyrpc.c

## Purpose

`pyrpc.c` implements the `samba.dcerpc.base` Python extension module. It exposes a generic `ClientConnection`, transfer syntax helper types, bind-time feature syntax construction, and a Python wrapper type for NDR pointers.

## Important APIs, Types, and Functions

The main Python type is `dcerpc_InterfaceType` backed by `dcerpc_InterfaceObject` from `pyrpc.h`. Getters expose `server_name`, `abstract_syntax`, `transfer_syntax`, `session_key`, `user_session_key`, and mutable `request_timeout`. Methods are `request()`, `transport_encrypted()`, and `auth_info()`. Helper type constructors include `py_transfer_syntax_ndr_new()`, `py_transfer_syntax_ndr64_new()`, `py_bind_time_features_syntax_new()`, and `py_dcerpc_ndr_pointer_new()`.

## Control Flow

Module init imports `talloc.BaseObject` and `samba.dcerpc.misc.ndr_syntax_id`, sets Python type bases, readies types, and registers module objects. `ClientConnection.__new__` parses a binding string plus syntax UUID/version, rejects direct `irpc:` from the generic constructor, builds a dummy interface table, and delegates connection setup to `py_dcerpc_interface_init_helper()`. Raw `request()` copies Python bytes into a talloc blob, optionally parses an object GUID, calls `dcerpc_binding_handle_raw_call()`, and returns response bytes.

## State and Persistence Behavior

Connection state is the talloc memory context, DCE/RPC pipe, binding handle, event context, and result-exception flag stored on the Python object. Deallocation reparents the event context so it is freed last. Session keys are exposed as Python bytes but not persisted.

## Dependencies and Integration Points

Dependencies include Python C API, Samba py3 compatibility helpers, pytalloc, DCE/RPC core, credentials/GENSEC indirectly through util code, and generated NDR syntax types. Generated Python RPC modules use the base connection and method registration helpers from `pyrpc_util.c`.

## Risks and Test Signals

Risks include Python reference-count mistakes, static dummy interface table reuse, raw request object GUID validation, lifetime ordering between pipe and event context, and exposing sensitive session keys. Test signals include constructing `ClientConnection` with string and tuple syntax IDs, raw request success/failure, timeout get/set, session key access failure/success, module import, and pointer wrapper get/set reference behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/pyrpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/pyrpc.h -->
# sources/user-network-fs/samba/source4/librpc/rpc/pyrpc.h

## Purpose

`pyrpc.h` is the shared header for Python DCE/RPC binding code. It defines the concrete Python object layout for client connections and a reusable type-check macro used by generated or hand-written Python RPC bindings.

## Important APIs, Types, and Functions

`PY_CHECK_TYPE(type, var, fail)` validates Python object types and emits contextual `TypeError` messages. `dcerpc_InterfaceObject` embeds `PyObject_HEAD`, a talloc memory context, `struct dcerpc_pipe *`, `struct dcerpc_binding_handle *`, `struct tevent_context *`, and a `raise_result_exceptions` boolean. The header also aliases several domain SID generated type/check names and defines `NDR_DCERPC_REQUEST_OBJECT_PRESENT` when absent.

## Control Flow

There is no runtime flow in this file. It controls compile-time structure sharing between `pyrpc.c`, `pyrpc_util.c`, and generated Python NDR/RPC modules.

## State and Persistence Behavior

The object layout defines how Python connection objects persist live RPC state across method calls. The state is memory-only and released through the deallocator in `pyrpc.c`.

## Dependencies and Integration Points

It includes Python error helpers and depends on DCE/RPC, talloc, and tevent types being visible through including translation units. Generated code relies on this exact ABI, so field changes affect Python extension compatibility.

## Risks and Test Signals

Risks include ABI breakage if the struct layout changes, macro misuse with expressions that have side effects, and type aliases drifting from generated NDR type names. Test signals are successful compilation of generated Python RPC modules, type-check failures with useful messages, and runtime connection object behavior through `samba.dcerpc.base`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/pyrpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/pyrpc_util.c -->
# sources/user-network-fs/samba/source4/librpc/rpc/pyrpc_util.c

## Purpose

`pyrpc_util.c` provides reusable Python binding helpers for generated Samba DCE/RPC modules. It initializes DCE/RPC interface objects, connects IRPC or network pipes, creates secondary contexts, dispatches generated RPC methods, maps errors, and converts NDR/talloc objects to Python.

## Important APIs, Types, and Functions

Important exports are `py_check_dcerpc_type()`, `py_dcerpc_interface_init_helper()`, `PyInterface_AddNdrRpcMethods()`, `py_dcerpc_syntax_init_helper()`, `PyErr_SetDCERPCStatus()`, `py_return_ndr_struct()`, `PyString_FromStringOrNULL()`, `PyBytes_FromUtf16StringOrNULL()`, `PyUtf16String_FromBytes()`, `pyrpc_import_union()`, `pyrpc_export_union()`, `py_dcerpc_ndr_pointer_deref()`, and `py_dcerpc_ndr_pointer_wrap()`. The local `pyrpc_irpc_connect()` creates an IRPC binding handle from a messaging context.

## Control Flow

Interface initialization parses Python arguments for binding, loadparm, credentials, timeout, basis connection, and exception behavior. It initializes DCE/RPC, allocates the Python object, then chooses IRPC binding, secondary connection/context from a basis `ClientConnection`, or a fresh `dcerpc_pipe_connect()`. Generated method calls use `PyNdrRpcMethodDef`: pack Python args into an NDR request struct, call the generated C client function against the binding handle, and unpack the output into Python.

## State and Persistence Behavior

The helper owns each Python object's talloc context and event context references. It may create messaging clients for IRPC and install synchronous event handling on IRPC binding handles. Basis connections share underlying event/pipe references or open secondary pipes. No disk state is written.

## Dependencies and Integration Points

Dependencies include Python C API, pytalloc, pyparam, pycredentials, DCE/RPC core, messaging/IRPC, generated NDR interface tables, and generated Python marshalling code. `wscript_build` builds this as the `pyrpc_util` Python embedding subsystem used by many generated modules.

## Risks and Test Signals

Risks include Python/talloc lifetime coupling, accepting credentials without loadparm for basis connections, IRPC nested event loops, unchecked `PyDict_SetItemString()` failure in method injection, and UTF-16 byte validation edge cases. Tests should import generated modules, connect fresh and via basis connections, exercise IRPC bindings, call generated methods with result-exception behavior on/off, convert NULL strings, validate UTF-16 odd/embedded-null rejection, and import/export discriminated unions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/pyrpc_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/pyrpc_util.h -->
# sources/user-network-fs/samba/source4/librpc/rpc/pyrpc_util.h

## Purpose

`pyrpc_util.h` declares the helper API used by hand-written and generated Python DCE/RPC extension modules.

## Important APIs, Types, and Functions

It defines `PyErr_FromNdrError` and `PyErr_SetNdrError` macros, function pointer typedefs `py_dcerpc_call_fn`, `py_data_pack_fn`, and `py_data_unpack_fn`, and `struct PyNdrRpcMethodDef`, which maps a Python method name/docstring to a generated C RPC call, packer, unpacker, opnum, and interface table. It declares all conversion, connection, method-registration, union, pointer, and error helpers implemented in `pyrpc_util.c`.

## Control Flow

There is no runtime flow. The header is consumed at compile time by generated `py_*.c` modules so they can register RPC methods and delegate common connection/call behavior.

## State and Persistence Behavior

The header itself stores no state, but it defines contracts around talloc-backed Python objects and DCE/RPC binding handles. `PyNdrRpcMethodDef` entries are generally static tables in generated modules.

## Dependencies and Integration Points

It includes `pyrpc.h` and references `struct ndr_interface_table`, `struct ndr_syntax_id`, Python object types, and DCE/RPC binding handles. It is integrated through the `pyrpc_util` build subsystem and many generated Python RPC modules.

## Risks and Test Signals

Risks include generated-code ABI drift if typedefs or struct fields change, macro error objects not setting exceptions unless used correctly, and mismatched opnums/table entries causing wrong request struct sizes. Test signals are clean generated-module compilation and runtime calls for multiple generated interfaces using the shared method table path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/pyrpc_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/scripts/build_idl.sh -->
# sources/user-network-fs/samba/source4/librpc/scripts/build_idl.sh

## Purpose

`build_idl.sh` is a small shell wrapper that runs Samba's PIDL generator for source4 librpc IDL files. It supports full regeneration and incremental regeneration based on whether an `.idl` file is newer than its generated `ndr_*.c` output.

## Important APIs, Types, and Functions

The script accepts `FULLBUILD`, `OUTDIR`, and a list of IDL files. It constructs the `PIDL` command with output directory, header, NDR parser, server/client, Python, DCOM proxy, COM header, and include-directory flags.

## Control Flow

The script ensures the output directory exists, builds a PIDL command string, and if `FULLBUILD` equals `FULL`, invokes PIDL on all given IDL files. Otherwise it loops over IDL files, derives `OUTDIR/ndr_<basename>.c`, and adds files to a regeneration list when the generated file is missing or older than the IDL. If the list is non-empty, PIDL runs only on that list.

## State and Persistence Behavior

It writes generated files through PIDL under `OUTDIR`. It does not maintain a manifest; freshness is inferred from filesystem timestamps and generated C file presence.

## Dependencies and Integration Points

Dependencies are POSIX shell utilities, `basename`, `find -newer`, the environment's `PIDL` command, and IDL include path `../librpc/idl`. It is part of the librpc build/generation workflow consumed by Waf build rules.

## Risks and Test Signals

Risks include unquoted variable expansion for paths with spaces, reliance on generated C timestamp rather than all generated outputs, unclear `IDLDIR` use in the full-build log, and command-string construction via shell words. Tests should run full and incremental builds, missing-output regeneration, older/newer timestamp cases, and paths or file names with unusual shell characters if supported by the build system.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/scripts/build_idl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/tests/binding_string.c -->
# sources/user-network-fs/samba/source4/librpc/tests/binding_string.c

## Purpose

`binding_string.c` is a local torture test suite for DCE/RPC binding string parsing, formatting, protocol tower conversion, options, flags, object UUIDs, and IPv6/address-only forms.

## Important APIs, Types, and Functions

The suite registers through `torture_local_binding_string()`. `test_BindingString()` performs parse/stringify/tower round trips for `test_strings[]`. `test_parse_check_results()` validates specific parsed fields, flags, host/target/principal/localaddress options, object UUID behavior, and association group IDs. `test_no_transport()` validates address strings parsed with `NCA_UNKNOWN` transport using `test_no_strings[]`.

## Control Flow

For each binding string, the test parses with `dcerpc_parse_binding()`, regenerates with `dcerpc_binding_string()`, builds an EPM tower, reconstructs a binding from that tower, restores the object UUID lost by tower conversion, strips non-endpoint options for tower comparison, and compares expected strings. The focused parse test runs targeted assertions for transport, endpoint, flags, object, abstract syntax, and string output.

## State and Persistence Behavior

The tests are memory-only and use the torture context as talloc parent. They do not require network I/O or persistent state.

## Dependencies and Integration Points

Dependencies include DCE/RPC binding/tower helpers, EPM tower structures, torture local framework, and IP address utilities. The suite is an important regression guard for the binding parser used by transport connection, endpoint mapping, auth, and Python connection paths.

## Risks and Test Signals

Risks include brittle string ordering expectations, partial tower comparison only for IPv4 host cases, and parser behavior around IPv6 colons, scope IDs, empty endpoints, and options. Test signals are failures in local torture `binding` tests after parser/formatter changes, especially for `target_hostname`, `target_principal`, `assoc_group_id`, no-transport address parsing, and sign/seal/connect/packet flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/tests/binding_string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/wscript_build -->
# sources/user-network-fs/samba/source4/librpc/wscript_build

## Purpose

`wscript_build` defines the source4 librpc Waf build graph: Samba-specific NDR subsystems, grouping libraries, the core `dcerpc` client library, Python DCE/RPC extension modules, generated NDR table construction, and selected generated RPC client subsystems.

## Important APIs, Types, and Functions

The file uses Waf/Samba build declarations such as `bld.RECURSE()`, `bld.SAMBA_SUBSYSTEM()`, `bld.SAMBA_LIBRARY()`, `bld.SAMBA_PIDL_TABLES()`, `bld.SAMBA_PYTHON()`, `bld.SAMBA_SCRIPT()`, and `bld.INSTALL_FILES()`. Major targets include `NDR_IRPC`, `NDR_WINSIF`, `NDR_WINSREPL`, `ndr-samba4`, `dcerpc-samba4`, `ndr-table`, `RPC_NDR_IRPC`, `dcerpc-samr`, `dcerpc`, `pyrpc_util`, `python_dcerpc`, and many `python_*` generated modules.

## Control Flow

Waf evaluates this Python-like build script to recurse into IDL/tool directories, create generated NDR tables, define grouping libraries, build the core `dcerpc` library from the transport/auth/connect files, select warning-suppression flags for generated code, derive embedded Python utility library names, and declare generated Python modules with install names under `samba/dcerpc`.

## State and Persistence Behavior

It does not run application logic. Build state is represented in Waf's task graph and outputs generated/compiled artifacts. Installed Python module names and public headers are controlled here.

## Dependencies and Integration Points

This file binds together core libraries (`dcerpc`, `ndr`, `gensec`, SMB client libs, HTTP, credentials, tevent/talloc), generated NDR code, source3-generated SMBXSRV RPC code, and Python extension install layout. It is the integration point that ensures files in this work item are compiled into the expected libraries/modules.

## Risks and Test Signals

Risks include missing dependencies when a source starts using a new subsystem, generated module install-name drift, public header path conflicts, Python-build conditional mistakes, and grouping-library dependency omissions. Test signals are clean configure/build with Python enabled and disabled, generated NDR table freshness, import of every installed `samba.dcerpc.*` module, pkg-config/public header checks for `dcerpc`, and rebuilds after IDL changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/defense.c -->
# sources/user-network-fs/samba/source4/nbt_server/defense.c

## Purpose

`defense.c` defends locally registered NetBIOS names against incoming name registration or refresh requests. It decides whether to answer with an active-name conflict or forward the request to the WINS server handling path.

## Important APIs, Types, and Functions

The file exports `nbtd_request_defense()`. It uses `nbtd_self_packet()`, `nbtd_find_iname()`, `nbtd_name_registration_reply()`, `nbtd_winsserver_request()`, and the `NBTD_ASSERT_PACKET` validation macro from `nbt_server.h`.

## Control Flow

If the request originates from one of Samba's own interfaces, it is treated as WINS-client-to-WINS-server traffic and forwarded to `nbtd_winsserver_request()`. Otherwise the function validates query/additional counts, question type/class, additional record type/class, and NetBIOS rdata length. It then looks for an active local name. Non-group, non-logon active names are defended by sending a registration reply with `NBT_RCODE_ACT`; other cases are delegated to WINS server logic.

## State and Persistence Behavior

The file does not create or persist state. It reads the interface's in-memory registered name list and increments no counters directly; dispatch counters are updated by the caller in `interfaces.c`.

## Dependencies and Integration Points

Dependencies include NBT packet structures, interface name state from `nbt_server.h`, WINS server request handling, socket address data, and generated NBT constants. `nbtd_request_handler()` dispatches register/refresh opcodes here.

## Risks and Test Signals

Risks include overly strict packet assertions dropping unusual but tolerated clients, not defending group/logon names, self-packet classification errors, and WINS forwarding loops. Tests should send registration/refresh packets for active unique names, group names, logon names, malformed records, and self-originated requests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/defense.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/dgram/browse.c -->
# sources/user-network-fs/samba/source4/nbt_server/dgram/browse.c

## Purpose

`dgram/browse.c` handles browser-service mailslot datagrams received by the NBT datagram server. In this source4 implementation it parses and logs browse packets rather than acting as a full browser election/announcement engine.

## Important APIs, Types, and Functions

`nbtd_mailslot_browse_handler()` is the mailslot callback. `nbt_browse_opcode_string()` maps `enum nbt_browse_opcode` values to readable names for debug logs. The handler uses `dgram_mailslot_browse_parse()` and optional `NDR_PRINT_DEBUG()`.

## Control Flow

The handler allocates a `struct nbt_browse_packet`, parses the incoming datagram into it, logs opcode, destination NetBIOS name, mailslot, and source address, prints full NDR detail at high debug levels, and frees the parsed packet. Parse or allocation failures go to a common debug failure path.

## State and Persistence Behavior

No state is persisted or mutated beyond temporary talloc allocations and debug logging. The datagram socket and mailslot handler registration are managed by `dgram/request.c`.

## Dependencies and Integration Points

Dependencies include libdgram mailslot parsing, generated NBT browse structures, socket addresses, and the NBT server datagram setup. The browse handler is registered for `NBT_MAILSLOT_BROWSE`.

## Risks and Test Signals

Risks include accepting but ignoring browse semantics, null opcode strings for unrecognized opcodes, and failure logging that calls `nbt_name_string()` with a possibly failed allocation context. Tests should cover each known browse opcode, malformed browse datagrams, unknown opcodes, and high-debug NDR printing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/dgram/browse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/dgram/netlogon.c -->
# sources/user-network-fs/samba/source4/nbt_server/dgram/netlogon.c

## Purpose

`dgram/netlogon.c` handles Netlogon mailslot datagrams for DC discovery. It answers legacy GETDC and ADS-style SAM_LOGON requests when the NBT server is listening on the requested NetBIOS name and the local server role/domain conditions are satisfied.

## Important APIs, Types, and Functions

Main helpers are `nbtd_netlogon_getdc()`, `nbtd_netlogon_samlogon()`, `nbtd_mailslot_netlogon_reply()`, and exported callback `nbtd_mailslot_netlogon_handler()`. It uses `fill_netlogon_samlogon_response()`, `samdb_is_pdc()`, `nbtd_find_iname()`, `nbtd_find_reply_iface()`, `dgram_mailslot_netlogon_parse_request()`, and `dgram_mailslot_netlogon_reply()`.

## Control Flow

Incoming mailslot packets are checked against local registered names, parsed as Netlogon requests, and dispatched by command. `LOGON_PRIMARY_QUERY` is answered only for PDC/LOGON destination names, only when Samba is an AD DC and PDC for the local workgroup. `LOGON_SAM_LOGON_REQUEST` builds a richer SAM_LOGON response using the SAM database, optional domain SID, requested username/account control, source address, and requested Netlogon version. Successful responses are sent from the best reply interface to the caller's requested mailslot.

## State and Persistence Behavior

The file reads `nbtsrv->sam_ctx`, loadparm role/workgroup/netbios name, and interface registration state. It does not persist data; replies are transient allocations under the mailslot handler context.

## Dependencies and Integration Points

Dependencies include libdgram Netlogon parse/reply helpers, DSDB/SAMDB, auth/security helpers, loadparm, server role helpers, and NBT interface selection. It is registered for both NETLOGON and NTLOGON mailslot names in `dgram/request.c`.

## Risks and Test Signals

Risks include responding to the wrong domain/name, mismatched PDC role detection, SAMDB response construction failures, reply-interface selection problems, and broad handling of NTLOGON through the Netlogon parser. Tests should cover PDC and non-PDC roles, wrong domain names, unknown commands, malformed packets, SID and no-SID SAM_LOGON, and reply source address correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/dgram/netlogon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/dgram/ntlogon.c -->
# sources/user-network-fs/samba/source4/nbt_server/dgram/ntlogon.c

## Purpose

`dgram/ntlogon.c` is a legacy NTLOGON mailslot handler that parses NTLOGON packets and can answer simple SAM logon requests with an NT4-style reply.

## Important APIs, Types, and Functions

The exported callback is `nbtd_mailslot_ntlogon_handler()`. The internal responder `nbtd_ntlogon_sam_logon()` builds `struct nbt_ntlogon_packet` replies. It uses `dgram_mailslot_ntlogon_parse()`, `dgram_mailslot_ntlogon_reply()`, `nbtd_find_iname()`, and `nbtd_find_reply_iface()`.

## Control Flow

The handler verifies the destination NetBIOS name is locally registered, parses the NTLOGON packet, logs it, and dispatches on command. For `NTLOGON_SAM_LOGON`, the responder only answers PDC or LOGON destination names, fills server/user/domain/version/token fields, clears destination name type to zero, and sends the reply to the request's mailslot.

## State and Persistence Behavior

No persistent state is written. The function reads the registered-name list and loadparm NetBIOS/workgroup settings. Reply packet fields borrow some strings from the incoming packet context.

## Dependencies and Integration Points

Dependencies include NBT datagram mailslot helpers, generated NBT NTLOGON structs, service task loadparm access, and interface selection. Note that `dgram/request.c` currently maps `NBT_MAILSLOT_NTLOGON` to the Netlogon handler, so this file may be legacy or used by other registrations outside this snippet.

## Risks and Test Signals

Risks include bitrot if the handler is not registered, lack of server-role/domain checks in the legacy reply path, and clearing destination name type in the input packet before reply. Tests should confirm whether this handler is reachable, parse valid/invalid NTLOGON packets, and verify SAM_LOGON replies only for PDC/LOGON names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/dgram/ntlogon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/dgram/request.c -->
# sources/user-network-fs/samba/source4/nbt_server/dgram/request.c

## Purpose

`dgram/request.c` sets up NetBIOS datagram sockets on port 138, registers static mailslot handlers, and forwards otherwise unexpected direct-unique datagrams to the source3 unexpected-packet compatibility server.

## Important APIs, Types, and Functions

The static `mailslot_handlers[]` table maps `NBT_MAILSLOT_NETLOGON`, `NBT_MAILSLOT_NTLOGON`, and `NBT_MAILSLOT_BROWSE` to callbacks. Exported functions are `dgram_request_handler()` and `nbtd_dgram_setup()`.

## Control Flow

`nbtd_dgram_setup()` optionally creates a broadcast datagram socket for non-wildcard interfaces, always creates a unicast datagram socket, binds them to the configured datagram port, installs `dgram_request_handler()`, and registers mailslot listeners on both sockets. `dgram_request_handler()` logs unexpected mailslots/general datagrams, prints packet detail at debug level, and only forwards `DGRAM_DIRECT_UNIQUE` packets by NDR-pushing them, converting to source3 `packet_struct`, dispatching to `nb_packet_server`, and freeing the packet.

## State and Persistence Behavior

The function stores the unicast datagram socket on `iface->dgmsock`; broadcast socket ownership is held by talloc and mailslot callbacks. It does not persist data. Unexpected packet forwarding is transient.

## Dependencies and Integration Points

Dependencies include libdgram sockets/mailslots, socket binding, loadparm datagram port, NDR NBT marshalling, source3 `parse_packet()`/`nb_packet_dispatch()`, and server interface state. `interfaces.c` calls this for every listening NBT interface.

## Risks and Test Signals

Risks include binding failures on broadcast addresses, only forwarding direct-unique datagrams, registering NTLOGON to the Netlogon handler rather than `ntlogon.c`, and lifetime assumptions for unnamed broadcast sockets. Tests should cover wildcard and per-interface setup, broadcast/unicast mailslots, unexpected direct-unique forwarding, non-direct datagram drop, and bind failure cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/dgram/request.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/interfaces.c -->
# sources/user-network-fs/samba/source4/nbt_server/interfaces.c

## Purpose

`interfaces.c` manages NBT server listening interfaces, name and datagram sockets, request dispatch, unexpected response redirection, address-list construction, and interface selection for outgoing requests/replies.

## Important APIs, Types, and Functions

Important functions are `nbtd_request_handler()`, `nbtd_unexpected_handler()`, `nbtd_find_iname()`, `nbtd_add_socket()`, `nbtd_add_wins_socket()`, `nbtd_startup_interfaces()`, `nbtd_address_list()`, `nbtd_find_request_iface()`, and `nbtd_find_reply_iface()`.

## Control Flow

Startup optionally creates a wildcard broadcast-style interface when `bind interfaces only` is disabled, then creates per-IPv4-interface sockets for each broadcast-capable interface, and optionally creates a WINS client interface. Each real interface gets a broadcast name socket, unicast name socket, unexpected handler, and datagram setup. Incoming NBT name packets increment stats, ignore self broadcast packets, and dispatch by opcode to query, defense, release/multihome WINS handling, or bad-packet logging. Unexpected replies are matched against request IDRs on broadcast, WINS, or other sockets; unmatched replies are serialized and sent to the unexpected packet server.

## State and Persistence Behavior

This file builds and links `struct nbtd_interface` objects into `nbtsrv->interfaces`, `bcast_interface`, and `wins_interface`. It owns socket pointers and per-interface names lists, but persistent name state is only memory-resident.

## Dependencies and Integration Points

Dependencies include network interface enumeration, socket/listen APIs, libnbt name sockets, libdgram setup, WINS server hooks, ID tree request tracking, source3 unexpected packet compatibility, and loadparm options. It is called during NBT task initialization.

## Risks and Test Signals

Risks include IPv4-only filtering, broadcast address binding portability, wildcard-interface selection semantics, unexpected reply misrouting by transaction ID collision, loopback address filtering in replies, and null-interface fallback assumptions. Tests should cover bind-interfaces-only on/off, multiple interfaces, loopback plus non-loopback, WINS client interface, broadcast self-packet suppression, unmatched unexpected response forwarding, and reply interface selection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/interfaces.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/irpc.c -->
# sources/user-network-fs/samba/source4/nbt_server/irpc.c

## Purpose

`irpc.c` exposes internal RPC services from the NBT server. It provides statistics and a get-DC helper used by other Samba components that need port-138 Netlogon replies to be received by the NBT server process.

## Important APIs, Types, and Functions

`nbtd_information()` returns `NBTD_INFO_STATISTICS`. `struct getdc_state` tracks deferred get-DC replies. `nbtd_getdcname()` sends a Netlogon SAM_LOGON request and defers the IRPC response. `getdc_recv_netlogon_reply()` parses the mailslot response and completes the IRPC call. `nbtd_register_irpc()` registers NBTD information, getdcname, and WINS proxy handlers.

## Control Flow

For getdc, the handler selects an outgoing interface for the requested IP, creates a temporary mailslot, builds a version-1 `LOGON_SAM_LOGON_REQUEST`, sends it to `<domain>[0x1c]` at UDP port 138, marks the IRPC message deferred, and returns. The temporary mailslot callback parses the Netlogon response, validates version, strips leading backslashes from the PDC name, stores `out.dcname`, and sends the deferred IRPC reply.

## State and Persistence Behavior

The server statistics pointer is returned directly from `nbtd_server`. Getdc state is temporary and talloc-owned by the IRPC message. The function does not persist data but relies on the NBT server's live datagram socket.

## Dependencies and Integration Points

Dependencies include Samba messaging/IRPC, generated `ndr_irpc` definitions, libdgram Netlogon helpers, NBT name construction, socket address creation, and WINS proxy functions. Winbind is the motivating consumer mentioned in comments.

## Risks and Test Signals

Risks include no explicit timeout handling shown for deferred getdc, temporary mailslot lifetime coupling, accepting only Netlogon NT version 1, source interface selection errors, and debug message wording referring to ntlogon parse. Tests should query statistics, perform getdc against responsive and non-responsive DCs, validate malformed replies, verify deferred reply completion, and exercise WINS proxy registration failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/irpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/nbt_server.c -->
# sources/user-network-fs/samba/source4/nbt_server/nbt_server.c

## Purpose

`nbt_server.c` is the service-task entry point for Samba's source4 NBT server. It initializes interfaces, unexpected packet compatibility support, SAMDB, WINS server support, IRPC services, message handlers, NetBIOS name registration, process naming, and pidfile lifecycle.

## Important APIs, Types, and Functions

The service entry point is `server_service_nbtd_init()`, which registers service name `nbt`. `nbtd_task_init()` performs startup. `nbtd_server_msg_send_packet()` handles source3-style `MSG_SEND_PACKET` messages. `nbtd_server_destructor()` removes the `nmbd` pidfile.

## Control Flow

Startup loads configured interfaces, rejects empty interface lists and `disable netbios = yes`, allocates `nbtd_server`, starts NBT interfaces, creates the unexpected packet server under the configured or dynamic nmbd socket directory, opens SAMDB as system, initializes the WINS server, registers IRPC and `MSG_SEND_PACKET`, starts local name registration, adds messaging name `nbt_server`, and creates the nmbd pidfile. `MSG_SEND_PACKET` validates a `packet_struct`, resolves the outgoing interface, adjusts datagram source fields, builds a raw packet into a fixed buffer, and sends it via name or datagram socket.

## State and Persistence Behavior

The service stores all live server state in `struct nbtd_server`. Persistent side effects are the `nmbd` pidfile and any WINS/SAMDB effects delegated to other components. Name registrations and stats are memory-resident.

## Dependencies and Integration Points

Dependencies include Samba service task registration, interface loading, pidfile utilities, SAMDB/system session, WINS server init, messaging, source3 packet compatibility, socket utilities, dynamic config, and NBT interface/registration modules.

## Risks and Test Signals

Risks include fixed 1024-byte raw packet build buffer, strict `packet_struct` length validation across ABI changes, source address rewrite for datagrams, startup termination on optional component failures, and pidfile cleanup ordering. Tests should start with NetBIOS disabled/enabled, no interfaces, WINS enabled, MSG_SEND_PACKET name and datagram sends, invalid packet inputs, SAMDB failure, and pidfile create/unlink behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/nbt_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/nbt_server.h -->
# sources/user-network-fs/samba/source4/nbt_server/nbt_server.h

## Purpose

`nbt_server.h` defines the central in-memory data model for the source4 NBT server and includes the generated NBT server prototypes. It is the coordination header shared by name service, datagram, WINS, IRPC, and startup modules.

## Important APIs, Types, and Functions

`struct nbtd_iface_name` represents one registered NetBIOS name on an interface, including flags, registration time, TTL, and WINS server. `struct nbtd_interface` represents a listening interface with addresses, name socket, datagram socket, name list, and WINS WACK queue. `struct nbtd_server` holds task context, interface lists, WINS server, stats, SAMDB, and unexpected packet server. `NBTD_ASSERT_PACKET()` validates incoming packets and calls `nbtd_bad_packet()`.

## Control Flow

The header has no runtime flow, but it shapes dispatch: handlers recover `nbtd_interface` from socket private data, then reach `nbtd_server` for stats, loadparm, SAMDB, and global interface lists.

## State and Persistence Behavior

All defined structures are runtime-only talloc-managed state. Registered names track TTL and registration time for refresh timers, but persistence is handled elsewhere if at all. The server struct points to SAMDB and WINS contexts rather than storing their data inline.

## Dependencies and Integration Points

It includes libnbt, WINS replication, datagram, IRPC, and messaging headers, then includes `nbt_server_proto.h`. Every C file in this NBT server subset depends on these definitions.

## Risks and Test Signals

Risks include broad coupling through a single header, ABI sensitivity of shared structs, and assertion macro behavior that returns from `void` handlers only. Tests are compile-time coverage across all NBT server modules plus runtime validation that each socket private_data really points to a populated `nbtd_interface`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/nbt_server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/nodestatus.c -->
# sources/user-network-fs/samba/source4/nbt_server/nodestatus.c

## Purpose

`nodestatus.c` answers NetBIOS node status queries by returning the active local names registered on the addressed interface.

## Important APIs, Types, and Functions

`nbtd_node_status_reply_packet()` builds a status response packet. `nbtd_query_status()` validates and dispatches incoming status queries. The local `nbtd_node_status_reply()` sends the reply. The code uses `nbtd_find_iname()`, NBT status rdata structures, and `nbt_name_reply_send()`.

## Control Flow

Packet construction counts active, non-`*` interface names, allocates one answer record, duplicates the requested name, fills status rdata, then iterates names again to write padded 15-character names, type, and flags. Query handling validates qdcount, type, and class, finds an active matching name on the interface, and sends the status reply or silently ignores missing names.

## State and Persistence Behavior

No state is persisted. The function reads active flags and names from `iface->names` and increments sent statistics through the server in the send helper.

## Dependencies and Integration Points

Dependencies include generated NBT structures, socket send helpers, interface name registration state, and the query dispatcher in `query.c`.

## Risks and Test Signals

Risks include name padding/truncation behavior, excluding wildcard `*`, silent no-reply for missing names, and memory cleanup on partial allocation failure. Tests should cover status queries for active/inactive/missing names, multiple aliases, wildcard exclusion, flag preservation, and malformed query validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/nodestatus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/packet.c -->
# sources/user-network-fs/samba/source4/nbt_server/packet.c

## Purpose

`packet.c` contains shared packet helpers for the NBT name service: bad-packet logging, self-packet detection, and construction/sending of positive/negative query, registration, release, and WACK replies.

## Important APIs, Types, and Functions

Exports include `nbtd_bad_packet()`, `nbtd_self_packet_and_bcast()`, `nbtd_self_packet()`, `nbtd_name_query_reply_packet()`, `nbtd_name_query_reply()`, `nbtd_negative_name_query_reply()`, `nbtd_name_registration_reply()`, `nbtd_name_release_reply()`, and `nbtd_wack_reply()`.

## Control Flow

Self-packet detection checks broadcast status, whether the packet arrived on a unicast socket, source port, and source address against local interfaces. Query reply construction creates a single answer with NetBIOS rdata entries for each address. Negative replies and registration/release replies mirror the incoming transaction ID and name, set appropriate opcode/rcode flags, and send via `nbt_name_reply_send()`. WACK replies include the original operation in a two-byte data body.

## State and Persistence Behavior

The file only reads interface/server state and increments `stats.total_sent` in send helpers. Packets are allocated under the socket or caller context and freed after send.

## Dependencies and Integration Points

Dependencies include NBT generated NDR structures, service task loadparm for NBT port, socket addresses, and interface private data. Query, defense, release, and WINS paths reuse these helpers for consistent reply formatting.

## Risks and Test Signals

Risks include shallow copying request rdata into registration/release replies, self-packet false positives with spoofed source address/port, address-list length zero behavior, and WACK data encoding. Tests should validate exact packet flags/opcodes/rcodes, multi-address query replies, negative replies, self broadcast suppression, and malformed allocation paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/packet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/query.c -->
# sources/user-network-fs/samba/source4/nbt_server/query.c

## Purpose

`query.c` answers NetBIOS name query requests or forwards them to WINS when recursion is requested and local answers are unavailable or special WINS behavior is needed.

## Important APIs, Types, and Functions

The file exports `nbtd_request_query()`. It uses `nbtd_query_status()` for status queries, `nbtd_find_iname()` for local name lookup, `nbtd_winsserver_request()` for recursive/WINS handling, `nbtd_negative_name_query_reply()`, `nbtd_name_query_reply()`, and `nbtd_address_list()`.

## Control Flow

Status queries with `NBT_QTYPE_STATUS` are delegated immediately. Normal queries validate one NetBIOS/IP question, find a matching local interface name, and if absent either suppress negative replies for broadcasts, forward recursive queries to WINS, or send a negative reply. Existing group names on a WINS server may also be forwarded for non-broadcast recursive queries. Inactive names are ignored for broadcast queries. Otherwise the file replies with the name's TTL, flags, and interface-prioritized address list.

## State and Persistence Behavior

No persistent state is written. The function reads the in-memory name list and loadparm WINS-server role. Sent packets update stats in packet helpers.

## Dependencies and Integration Points

Dependencies include NBT packet structures, WINS server request handling, node status handling, interface address-list construction, and loadparm.

## Risks and Test Signals

Risks include WINS recursion branching for group names, no negative replies to broadcasts, inactive name suppression, and exact matching rules in `nbtd_find_iname()`. Tests should query active unique names, active group names with WINS enabled, missing names with broadcast/recursion/no-recursion combinations, inactive names, and node status queries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/query.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/register.c -->
# sources/user-network-fs/samba/source4/nbt_server/register.c

## Purpose

`register.c` registers and refreshes the Samba NBT server's NetBIOS names on local broadcast interfaces, the wildcard broadcast interface, and configured WINS servers.

## Important APIs, Types, and Functions

Public functions are `nbtd_register_name()` and `nbtd_register_names()`. Internal pieces include `refresh_completion_handler()`, `name_refresh_handler()`, `nbtd_start_refresh_timer()`, `struct nbtd_register_name_state`, `nbtd_register_name_handler()`, and `nbtd_register_name_iface()`.

## Control Flow

`nbtd_register_names()` registers the server NetBIOS name as client/user/server, aliases as client/server, AD DC workgroup PDC/logon names when appropriate, the workgroup group name, and permanent `__SAMBA__`/`*` names. Per-interface registration creates an `nbtd_iface_name`, uppercases name and optional scope, sets TTL and flags, links it into the interface, and either marks permanent names active, delegates WINS-interface names to the WINS client, or sends a broadcast registration request. Successful broadcast registration marks the name active, records registration time, and starts a refresh timer. Refresh uses registration packets rather than refresh packets so peers defend conflicts.

## State and Persistence Behavior

The file maintains the in-memory `iface->names` list, `NBT_NM_ACTIVE`/`NBT_NM_CONFLICT` flags, TTL, registration timestamps, and refresh timers. It does not persist names to disk; WINS registration side effects are delegated to WINS client code.

## Dependencies and Integration Points

Dependencies include tevent timers, libnbt broadcast registration APIs, WINS client registration, SAMDB PDC detection, loadparm NetBIOS/workgroup/alias/TTL/scope settings, and server role helpers. It is called from NBT task startup after interfaces and SAMDB are ready.

## Risks and Test Signals

Risks include conflicts leaving names inactive, refresh timeout treated as success for broadcast refresh, timer lifetime tied to name objects, role-dependent PDC/logon registration, and permanent wildcard names being immediately active. Tests should cover successful registration, conflict replies, refresh conflict/error/timeout paths, WINS-interface registration, aliases, AD DC PDC and non-PDC roles, scope uppercasing, TTL-derived refresh time, and permanent names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/nbt_server/register.c -->
