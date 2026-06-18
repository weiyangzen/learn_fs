# subset-b-009618 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/srvs.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/srvs.py

## Purpose

`srvs.py` implements Impacket's [MS-SRVS] Server Service RPC interface binding metadata. It is a protocol-schema module: it defines the SRVS UUID, constants, NDR structure/union/pointer classes for server/share/session/file/transport/DFS data, NDR call classes for supported opnums, the `OPNUMS` dispatch table, and helper functions that populate request objects and send them through an existing DCE/RPC connection.

The file does not open sockets or authenticate by itself. Callers are expected to build a DCE/RPC transport elsewhere, bind to `MSRPC_UUID_SRVS`, and then call helpers such as `hNetrShareEnum`, `hNetrServerGetInfo`, or `hNetrpGetFileSecurity`.

## Important APIs, types, and functions

- `MSRPC_UUID_SRVS` identifies the Server Service interface version 3.0.
- `DCERPCSessionError` renders SRVS RPC failures using `impacket.system_errors.ERROR_MESSAGES`.
- Constants cover share types (`STYPE_*`), session flags, platform/server type flags, path and name validation types, DFS flags, parameter-error codes, and `MAX_PREFERRED_LENGTH`.
- Core NDR data families include `CONNECTION_INFO_*`, `FILE_INFO_*`, `SESSION_INFO_*`, `SHARE_INFO_*`, `SERVER_INFO_*`, `DISK_INFO`, `SERVER_TRANSPORT_INFO_*`, `SERVER_ALIAS_INFO_*`, `TIME_OF_DAY_INFO`, security descriptor wrappers, and DFS entry/site structs.
- Union/container classes are the important level selectors: `CONNECT_ENUM_UNION`, `FILE_ENUM_UNION`, `SESSION_ENUM_UNION`, `SHARE_ENUM_UNION`, `SERVER_INFO`, `TRANSPORT_INFO`, and `SERVER_ALIAS_INFO`.
- RPC call classes model opnums 8 through 57, including connection/file/session enumeration, share add/enum/get/set/delete, server get/set/disk/statistics/time, transport add/enum/delete, path/name canonicalization and comparison, DFS management, server alias management, and extended share deletion.
- `OPNUMS` maps each supported opnum to request/response classes for `rpcrt` unmarshalling.
- Helper functions prefixed `h` create requests and call `dce.request()`. Notable helpers include `hNetrShareEnum`, `hNetrShareAdd`, `hNetrShareSetInfo`, `hNetrServerTransportEnum`, `hNetrpGetFileSecurity`, `hNetrpSetFileSecurity`, and path/name validation helpers.

## Control flow

Import-time execution defines constants and classes only. Runtime flow is thin:

1. A caller creates or receives a bound DCE/RPC object.
2. A helper allocates the corresponding `NDRCALL` request.
3. The helper fills `ServerName`, level fields, union tags, buffers, resume handles, and payload structures.
4. `dce.request(request)` serializes the NDR request, invokes the remote opnum, and unmarshals the response through `OPNUMS`.

The main control-flow risk is correct union tagging. Enumeration helpers explicitly set both the outer `Level` and inner union `tag`, and set returned array buffers to `NULL` before the call. Add/set helpers assign the correct `ShareInfo%d`, `ServerAliasInfo%d`, or related level-specific arm.

## State and persistence behavior

The module is stateless aside from class definitions and constants. Persistent effects happen on the remote server, not locally:

- Share helpers can add, update, delete, or perform staged deletion of server shares.
- Server-set and transport add/delete calls can alter server configuration.
- DFS helpers can create/delete partitions, change local volume state, and create/delete exit points.
- File-security helpers read or write remote share-relative security descriptors.

Local helper state is limited to request objects and resume handles. The caller owns pagination loops via `ResumeHandle` and `PreferedMaximumLength`.

## Dependencies and integration points

- Depends on `impacket.dcerpc.v5.ndr` for NDR base classes, arrays, unions, and pointers.
- Depends on `impacket.dcerpc.v5.dtypes` for common Windows/RPC scalar and string types.
- Uses `impacket.dcerpc.v5.rpcrt.DCERPCException` for session errors.
- Uses `impacket.uuid.uuidtup_to_bin` for UUID encoding.
- Integrates with transport and RPC binding code outside this file; common use is over SMB named pipe transports against `\pipe\srvsvc`.
- The header points users to Impacket SMB_RPC tests as usage examples.

## Risks and implementation notes

- Several helpers do not normalize trailing NULs consistently. `hNetrShareEnum` enforces a final NUL for `serverName`, while many other `WSTR`/`LPWSTR` inputs are passed through as provided.
- Level/tag mismatches in caller-provided `infoStruct` or `shareInfo` objects can produce malformed NDR requests or server-side `ERROR_INVALID_LEVEL`/parameter errors.
- `SHARE_INFO_1005_ARRAY.item` is set to `SHARE_INFO_1004`, which looks like a likely copy/paste defect for level 1005 array handling.
- Security descriptor helpers manually convert buffers: `hNetrpGetFileSecurity` joins returned descriptor bytes, and `hNetrpSetFileSecurity` sets length plus byte-list buffer. Tests should cover binary descriptor round trips.
- Destructive administrative calls are exposed without guardrails. Higher-level tools must enforce authorization checks, dry-run behavior, and user confirmation if needed.
- Many NDR schemas mirror protocol documents and are not locally validated beyond Impacket serialization.

## Test signals

Useful tests should bind to an SRVS-capable endpoint and cover:

- Share enumeration at levels 0, 1, 2, 501, 502, and 503, including resume-handle pagination.
- Share add/get/set/delete for level-specific structures and `ParmErr` behavior.
- Session, file, connection, disk, transport, server alias, path/name, and remote time helpers.
- Security descriptor get/set byte preservation.
- Error formatting through `DCERPCSessionError` for known and unknown system error codes.
- Regression tests for union tag setup and the suspicious `SHARE_INFO_1005_ARRAY` item type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/srvs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/transport.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/transport.py

## Purpose

`transport.py` provides Impacket's transport abstraction for DCE/RPC v5/v4 traffic. It parses DCE/RPC string bindings, composes bindings, chooses the correct transport implementation, stores authentication and connection options, and implements concrete transports for UDP, TCP, HTTP/RPC proxy, SMB named pipes, and local named pipes.

This module is the bridge between high-level RPC interface modules and lower-level sockets, SMB sessions, and RPC over HTTP clients.

## Important APIs, types, and functions

- `DCERPCStringBinding` parses strings of the form `uuid@protocol_sequence:network_address[endpoint,options]` and exposes UUID, protocol sequence, network address, endpoint, and options.
- `DCERPCStringBindingCompose()` serializes binding components back into a string.
- `DCERPCTransportFactory()` maps protocol sequences to transport classes: `ncadg_ip_udp`, `ncacn_ip_tcp`, `ncacn_http`, `ncacn_np`, and `ncalocal`.
- `DCERPCTransport` is the base class. It stores remote name/host/port, string binding, max send/receive fragments, credentials, Kerberos options, timeout, and optional strict hostname validation.
- `UDPTransport` implements datagram RPC over UDP and switches `DCERPC_class` to `DCERPC_v4`.
- `TCPTransport` implements stream RPC over TCP, including optional send fragmentation and exact-length receive support.
- `HTTPTransport` supports direct `ncacn_http` and RPC proxy mode through `RPCProxyClient`.
- `SMBTransport` implements RPC over SMB named pipes, can create its own `SMBConnection` or reuse an existing one, and exposes SMB connection/server accessors.
- `LOCALTransport` opens a local Windows named pipe path for local RPC access.

## Control flow

Typical usage:

1. A caller passes a string binding to `DCERPCTransportFactory`.
2. The factory parses it with `DCERPCStringBinding`, instantiates the matching transport, and stores the parsed binding on the transport.
3. The caller sets credentials, Kerberos, timeout, SMB connection, hostname validation, or fragmentation options.
4. `transport.get_dce_rpc()` returns a `DCERPC_v5` wrapper, except UDP advertises `DCERPC_v4` through `DCERPC_class`.
5. `dce.connect()` delegates to the selected transport's `connect()`, then the RPC layer binds and sends requests through `send()`/`recv()`.

Concrete flow details:

- UDP uses `socket.getaddrinfo`, creates a datagram socket, and uses `sendto`/`recvfrom`.
- TCP opens a stream socket and either sends all data at once or chunks by `_max_send_frag`.
- HTTP direct mode connects over TCP, expects the legacy `ncacn_http/1.0` banner, and uses RPC over HTTP v1 semantics. RPC proxy mode parses `RpcProxy` binding options and delegates connect/send/recv/disconnect to `RPCProxyClient`.
- SMB creates or reuses an `SMBConnection`, logs in with NTLM or Kerberos, connects to `IPC$`, opens the named pipe, writes request bytes, and reads response bytes.
- Local transport prefixes `\PIPE\` if needed and uses `os.open/read/write/close`.

## State and persistence behavior

The transport objects maintain connection state:

- Credentials and hashes are stored on the transport; hash strings are normalized to bytes when possible.
- SMB transport tracks tree ID, open file handle, socket, pending forced receives, whether the SMB connection is caller-owned, and preferred dialect.
- HTTP transport tracks whether RPC proxy mode is enabled, the proxy URL, and the active implementation class.
- TCP/UDP hold socket objects and timeout.

Remote persistent changes are not performed by this module directly; it only carries RPC traffic. It can, however, authenticate to SMB, open named pipes, and keep remote SMB sessions alive until `disconnect()`.

## Dependencies and integration points

- Uses Python `socket`, `os`, `re`, `binascii`, and URL parsing.
- Integrates with `impacket.dcerpc.v5.rpcrt.DCERPC_v5` and `DCERPC_v4`.
- Integrates with `impacket.dcerpc.v5.rpch.RPCProxyClient` for RPC over HTTP proxy support.
- Integrates with `impacket.smbconnection.SMBConnection` for named pipe transport.
- Uses `impacket.ntlm.USE_NTLMv2` as the default NTLMv2 support signal.
- Consumed by interface modules and tools throughout Impacket through string bindings such as `ncacn_np:host[\pipe\srvsvc]`.

## Risks and implementation notes

- `DCERPCStringBinding.__init__` assumes the regex matches; malformed bindings can produce an attribute error rather than a clean parse exception.
- `DCERPCStringBindingCompose` uses a mutable default `options={}`. It does not mutate the object internally, but the signature is still a Python footgun.
- `HTTPTransport.connect()` references private base fields as `self.__remoteName` and `self.__dstport` in an exception path. Because those are name-mangled in `DCERPCTransport`, that error path can itself fail.
- SMB named-pipe handling strips a leading `\pipe` endpoint prefix by slicing; unusual endpoint casing or shape may not normalize correctly.
- `disconnect()` on `SMBTransport` assumes tree/file/session state was established. Failed partial connects may need defensive cleanup by callers.
- `SMBTransport.recv(count=...)` ignores `count` and relies on SMB read semantics except when max fragmentation or pending forced receives are active.
- Credentials are kept in object fields as plaintext/password/hash material for the life of the transport.

## Test signals

Useful tests should cover:

- Parsing and composing bindings with UUIDs, empty endpoints, `endpoint=` syntax, options without values, and `RpcProxy`.
- Factory selection for each supported protocol sequence and failure on unknown sequences.
- Credential hash normalization for odd-length and already-binary LM/NT hashes.
- TCP send fragmentation and exact-count reads, including remote close behavior.
- SMB reuse of an existing connection versus internally-created login/logoff lifecycle.
- Kerberos and hostname-validation propagation into SMB connections.
- HTTP direct mode banner validation and RPC proxy URL construction for port 80/443 plus rejection of other proxy ports.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/transport.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/tsch.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/tsch.py

## Purpose

`tsch.py` implements Impacket's [MS-TSCH] Task Scheduler Service RPC interface. It defines the scheduler UUID, scheduler constants, NDR request/response classes for opnums 0 through 19, helper functions for common calls, and a few binary `Structure` classes for legacy `.job` data and trigger records.

The module is a client-side RPC schema and helper layer. It does not schedule work locally; it marshals Task Scheduler requests to a bound remote `ITaskSchedulerService` endpoint.

## Important APIs, types, and functions

- `MSRPC_UUID_TSCHS` identifies `86D35949-83C9-4044-B424-DB363231FD0C` version 1.0.
- `DCERPCSessionError` renders HRESULTs through `hresult_errors` and low-word system errors through `system_errors`.
- Constants cover task flags, logon types, task states, registration flags, security flags, enumeration flags, run flags, and trigger enums.
- NDR array/pointer types include `TASK_NAMES_ARRAY`, `WSTR_ARRAY`, `GUID_ARRAY`, `SYSTEMTIME_ARRAY`, and `TASK_USER_CRED_ARRAY`.
- Scheduler structures include `TASK_USER_CRED`, `TASK_XML_ERROR_INFO`, plus binary `FIXDLEN_DATA`, `TRIGGERS`, `WEEKLY`, `MONTHLYDATE`, `MONTHLYDOW`, and `JOB_SIGNATURE`.
- RPC calls cover highest-version query, task registration/retrieval, folder creation, security get/set, folder/task/instance enumeration, instance info, stop/run/delete/rename, scheduled runtimes, last run info, task info, missed run count, and enable/disable.
- `OPNUMS` maps opnums 0 to 19 to request and response classes.
- Helper functions `hSchRpc*` create requests, normalize strings, handle optional arrays, and call `dce.request()`.

## Control flow

Runtime flow is linear:

1. A caller binds a DCE/RPC connection to `MSRPC_UUID_TSCHS`.
2. A helper creates the relevant `SchRpc*` request.
3. The helper applies `checkNullString()` to most scheduler path/XML/SDDL strings.
4. For array parameters, helpers append wrapped values: `hSchRpcRegisterTask` appends credentials when present, and `hSchRpcRun` appends each argument as an `LPWSTR`.
5. `dce.request()` sends the request and returns the response object.

`checkNullString()` is central. It returns `NULL` unchanged and appends `\x00` to non-null strings lacking a terminator.

## State and persistence behavior

The module keeps no local persistent state. Remote persistent effects include:

- `hSchRpcRegisterTask` can create, update, disable, or validate scheduled tasks depending on flags.
- `hSchRpcCreateFolder`, `hSchRpcDelete`, and `hSchRpcRename` mutate scheduler folder/task namespace state.
- `hSchRpcSetSecurity` mutates SDDL security descriptors.
- `hSchRpcRun`, stop helpers, and enable helpers mutate runtime state.

Task XML, credentials, paths, and SDDL are transmitted to the remote scheduler service. Callers are responsible for protecting credential material and avoiding accidental persistent task creation.

## Dependencies and integration points

- Depends on `impacket.dcerpc.v5.ndr` and `impacket.dcerpc.v5.dtypes` for NDR schema.
- Uses `impacket.structure.Structure` for fixed binary legacy task/job records.
- Uses `hresult_errors` and `system_errors` for error display.
- Integrates with the rest of Impacket through DCE/RPC transport and binding code. Typical transport is SMB named pipe or RPC endpoint mapper resolution to Task Scheduler.
- Test guidance in the header points to Impacket SMB_RPC tests.

## Risks and implementation notes

- `SCHED_S_TASK_RUNNING` and `SCHED_S_TASK_NOT_SCHEDULED` are both assigned `0x00041301`; that looks suspicious because these scheduler success codes are normally distinct.
- XML and SDDL are caller-provided and only NUL-normalized; semantic validation is left to the remote service.
- `hSchRpcRegisterTask` sets `pCreds` to `NULL` when empty but otherwise appends directly into `request['pCreds']`; tests should verify pointer/array initialization works for non-empty credentials.
- Many helpers default to broad values such as `0xffffffff` for security information, counts, or enumeration size; callers should restrict where needed.
- The binary `.job` structures are independent from the RPC calls and need separate binary fixture coverage.

## Test signals

Useful tests should cover:

- `checkNullString()` behavior for `NULL`, already-terminated strings, and unterminated strings.
- Opnum map coverage for all nineteen calls.
- Register/retrieve/delete task round trips with minimal XML.
- Credential-array registration behavior.
- Folder/task enumeration pagination through `startIndex` and `cRequested`.
- `hSchRpcRun` argument array marshalling.
- Error formatting for HRESULTs, low-word Win32 errors, and unknown values.
- Binary layout parsing for `FIXDLEN_DATA`, trigger variants, and `JOB_SIGNATURE`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/tsch.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/tsts.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/tsts.py

## Purpose

`tsts.py` implements a large portion of the [MS-TSTS] Terminal Services Terminal Server Runtime Interface Protocol for Impacket. It defines UUIDs for several Terminal Services RPC interfaces, NDR helpers for Terminal Services strings, handles, enums, session/client/config/process structures, many RPC call classes, standalone helper functions, and endpoint wrapper classes that bind to the proper named pipe and expose those helpers as methods.

The file is intentionally mixed-maturity. Header comments define tags such as `#NOT_IMPLEMENTED`, `#DOES_NOT_WORK`, and `#OLD`, and the body contains many partially implemented or deprecated calls alongside working helpers.

## Important APIs, types, and functions

- Interface UUIDs include `TermSrvSession_UUID`, `TermSrvNotification_UUID`, `TermSrvEnumeration_UUID`, `RCMPublic_UUID`, `RcmListener_UUID`, `SessEnvPublicRpc_UUID`, and `LegacyAPI_UUID`.
- `DCERPCSessionError` displays TSTS errors using the low 16 bits against `system_errors`.
- Scalar/string helpers include custom `NDRENUM.dump`, `TS_WCHAR`, `TS_LPWCHAR`, `TS_CHAR`, `SYSTEM_TIMESTAMP`, stripped string subclasses, `ZEROPAD`, `getUnixTime`, `enum2value`, `binary_sid_to_string`, and `SID`.
- Handle abstractions include `context_handle`, `handle_t`, `ENUM_HANDLE`, `HLISTENER`, `SERVER_HANDLE`, `NOTIFY_HANDLE`, and `SESSION_HANDLE`.
- Enums cover message-box results, shutdown flags, hotkey modifiers, event flags, address families, information/state/security/shadow classes, reconnect/session/shadow request types, notification IDs, callback class, session flags, and result statuses.
- Data models cover session enumeration levels, execution environment data, listener enumeration, `LSMSESSIONINFORMATION`, `WINSTATIONCLIENT`, counters, extended session info, notification changes, user config, WinStation config, remote address union, all-process information, and SID conversion helpers.
- RPC call classes span TermSrvSession, TermSrvNotification, TermSrvEnumeration, RCMPublic, RCMListener, SessEnv public shadowing, and Legacy WinStation APIs.
- Helper functions prefixed `hRpc*` build requests and often normalize strings or interpret unusual success behavior.
- Endpoint wrapper classes `TermSrvSession`, `TermSrvNotification`, `TermSrvEnumeration`, `RCMPublic`, `RcmListener`, `SessEnvPublicRpc`, and `LegacyAPI` inherit `TSTSEndpoint`, bind to a named pipe/interface UUID, set packet privacy, and expose matching helper functions as bound methods.

## Control flow

There are two main calling styles:

1. Low-level style: caller binds a DCE/RPC connection manually and calls helper functions with `dce` plus request parameters.
2. Endpoint style: caller passes an existing SMB connection, target IP, and Kerberos flag to an endpoint wrapper. `TSTSEndpoint` builds an `ncacn_np` string binding, reuses the SMB connection, creates a DCE/RPC object, sets GSS negotiate when Kerberos is requested, sets packet privacy, connects, binds to the endpoint UUID, and aliases `self.request` to `self._dce.request`.

Helper control flow is mostly request-fill-send-return. A few helpers add special handling:

- `hRpcConnect` treats `DCERPCSessionError` code `0x1` as success.
- `hRpcLogoff` treats `0x10000000` as success.
- Legacy API helpers use `dce.request(..., checkError=False)` because those responses encode success as a trailing one-byte boolean rather than normal `rpcrt` error status.
- `hRpcWinStationGetProcessSid` retries with a larger SID buffer when the first call reports `ERROR_STATUS_BUFFER_TOO_SMALL`.
- Some RCMPublic helpers catch all exceptions and return `None`, trading detailed failure signals for best-effort querying.

## State and persistence behavior

Local state is kept in endpoint wrapper instances:

- The SMB connection, target IP, string binding, endpoint UUID, transport, and DCE/RPC object are stored for the endpoint lifetime.
- Context handles returned by open/register calls represent server-side state and must be closed/unregistered with the corresponding helper.
- `TSTSEndpoint` is a context manager; `__exit__` disconnects the DCE/RPC connection.

Remote effects can be significant:

- Session helpers can connect, disconnect, log off, display message boxes, query state, and inspect users/times/counters.
- Notification helpers can wait for state changes and register async notifications.
- Listener helpers can start/stop Terminal Services listeners.
- Legacy helpers can disconnect/reset sessions, shut down/reboot/log off systems via `RpcWinStationShutdownSystem`, terminate processes, shadow sessions, and alter security/configuration where calls work.
- Process helpers can enumerate processes and resolve SIDs.

## Dependencies and integration points

- Uses `impacket.dcerpc.v5.transport` to build named-pipe transports.
- Depends on many NDR/dtype primitives from `impacket.dcerpc.v5.ndr` and `impacket.dcerpc.v5.dtypes`.
- Uses `impacket.uuid` conversions for endpoint UUIDs and context handles.
- Uses `impacket.dcerpc.v5.rpcrt` authentication constants, especially `RPC_C_AUTHN_GSS_NEGOTIATE` and `RPC_C_AUTHN_LEVEL_PKT_PRIVACY`.
- Uses `impacket.dcerpc.v5.enum.Enum` and `impacket.system_errors`.
- Expected named pipes are `\pipe\LSM_API_service`, `\pipe\TermSrv_API_service`, `\pipe\SessEnvPublicRpc`, and `\pipe\Ctx_WinStation_API_service`.

## Risks and implementation notes

- The file contains explicit incomplete and non-working sections. `EXECENVDATAEX_LEVEL1`, `PROTOCOLCOUNTERS`, `CACHE_STATISTICS`, `PROTOCOLSTATUS`, `WINSTATIONCONFIG2`, and `CLIENT_STACK_ADDRESS` are pass-through placeholders; multiple RPC classes use `UNKNOWNDATA` or commented protocol signatures.
- Several helper implementations appear to instantiate the wrong request class: `hRpcWinStationCloseServerEx`, `hRpcWinStationIsHelpAssistantSession`, and `hRpcWinStationOpenSessionDirectory` create `RpcWinStationShadowStop()` instead of their matching request classes.
- `RpcConnectCallback` is commented as opnum 66 but sets `opnum = 61`, conflicting with `RpcWinStationIsHelpAssistantSession`.
- Broad `except:` blocks in `hRpcGetClientData` and `hRpcGetRemoteAddress` suppress all failure detail.
- Custom string/array classes and fixed-size padding functions rely on exact byte/character sizing; off-by-one errors can corrupt request marshalling.
- Legacy response handling bypasses normal RPC error checking and must inspect boolean/result fields carefully.
- Some helpers can perform disruptive administrative actions, including logoff, reset, process termination, and system shutdown.
- Endpoint wrappers always request packet privacy and require a valid SMB connection; callers need to manage authentication and SMB lifetime consistently.

## Test signals

Useful tests should cover:

- Unit tests for custom string decoding, stripped NUL behavior, `ZEROPAD`, timestamp conversion, enum rendering, SID conversion, and context handle tuple/null behavior.
- Binding tests for each endpoint wrapper, verifying named pipe, UUID, auth level, Kerberos auth type, and context-manager disconnect behavior.
- Session open/query/close and notification register/wait/unregister against a test Windows host.
- Enumeration helpers at levels 1, 2, and 3, including union tags and returned array parsing.
- RCMPublic client/config/last-input/remote-address/listener parsing, especially IPv4/IPv6 remote address unions.
- Legacy API tests with `checkError=False`, including open/close server, message, name/logon lookup, disconnect/reset, process enumeration, SID retry behavior, and error boolean interpretation.
- Regression tests for the wrong-request-class helpers and the `RpcConnectCallback` opnum mismatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/tsts.py -->
