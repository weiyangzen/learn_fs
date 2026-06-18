# Research Report: subset-b-009616

Grouped research for Impacket DCERPC v5 bindings and runtime modules. Each section preserves the original source path and is bounded for deterministic splitting into per-file research reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/nspi.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/nspi.py

## Purpose

`nspi.py` implements Impacket's client-side NDR model for the Name Service Provider Interface protocols [MS-NSPI] and [MS-OXNSPI], primarily for Exchange address book access. It defines NSPI constants, MAPI property wire types, entry ID packet structures, request/response classes, opnum mappings, and helper functions for binding to an NSPI server, browsing rows, resolving names, converting distinguished names to minimal entry IDs, querying property columns, and simplifying returned MAPI property rows into Python values.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_NSPI`, `DCERPCSessionError`, many NSPI constants, and the `handle_t` context handle. Its property model is centered on `PropertyTagArray_r`, `Binary_r`, scalar and multivalue array structures, `PROP_VAL_UNION`, `PropertyValue_r`, `PropertyRow_r`, and `PropertyRowSet_r`. Restriction support is partly modeled through `Restriction_r`, `AndRestriction_r`, `ContentRestriction_r`, `PropertyRestriction_r`, and `RestrictionUnion_r`, but matching-related RPC calls are commented out.

Entry identifiers are represented by packet `Structure` classes `EphemeralEntryID` and `PermanentEntryID`, with `GUID_NSPI` used to identify permanent NSPI entry IDs. `STAT` carries cursor and sorting state for table operations. RPC call classes cover opnums 0, 1, 2, 3, 4, 7, 8, 9, 10, 12, 13, 14, 16, 17, 18, 19, and 20. Implemented helpers include `hNspiBind`, `hNspiUnbind`, `hNspiUpdateStat`, `hNspiQueryRows`, `hNspiSeekEntries`, `hNspiDNToMId`, `hNspiGetPropList`, `hNspiGetProps`, `hNspiGetSpecialTable`, `hNspiGetTemplateInfo`, `hNspiModLinkAtt`, `hNspiQueryColumns`, `hNspiGetNamesFromIDs`, `hNspiResolveNames`, and `hNspiResolveNamesW`.

Conversion helpers include `get_guid_from_dn`, `get_dn_from_guid`, `getUnixTime`, `simplifyPropertyRow`, and `simplifyPropertyRowSet`. `EXCH_SID` wraps `LDAP_SID` string formatting, and `ExchBinaryObject` marks opaque Exchange binary values.

## Control Flow

Most protocol behavior is declarative NDR layout. Request helpers allocate an `NDRCALL`, populate a context handle, flags, `STAT` state, arrays, and property tag counts, then call `dce.request()`. Bind sets a default Teletex code page when the caller does not provide a `STAT`. Unbind and update-stat call `dce.request(..., checkError=False)` because NSPI may return useful state alongside non-zero status codes.

Table helpers build optional property tag and entry-table arrays manually. `hNspiQueryRows`, `hNspiSeekEntries`, `hNspiGetProps`, `hNspiGetNamesFromIDs`, and the resolve-name helpers append `DWORD` or string wrapper instances and then adjust `cValues`, `Count`, and sometimes nested `MaximumCount` fields to satisfy conformant varying array encoding. `hNspiSeekEntries` forces `SortTypeDisplayName` and a Unicode display-name target because MS-OXNSPI rejects other combinations in that code path. `hNspiModLinkAtt` converts caller-supplied entry IDs into `Binary_r` values by calling `getData()`.

`simplifyPropertyRow` is the main response post-processor. It inspects the active union arm, converts integer NDR wrappers to Python ints, removes null terminators from strings, turns selected binary property tags into SIDs, GUID strings, permanent or ephemeral entry ID structures, UTF-8 strings, or signed integers, maps file times into `datetime.fromtimestamp()`, and leaves unknown values as raw wrapper objects or `ExchBinaryObject`.

## State And Persistence Behavior

There is no disk persistence. Runtime state lives in server-side NSPI context handles returned by `NspiBind`, client-maintained `STAT` cursor fields, request arrays, and returned row sets. The caller is responsible for retaining the context handle and passing it to later operations, then releasing it with `hNspiUnbind`. Some helpers use mutable default arguments such as `pPropTags=[]`, `lpETable=[]`, and `paStr=[]`; they do not mutate those defaults directly in normal paths, but this pattern is still risky for future changes.

Remote effects are mostly read-oriented except `hNspiModLinkAtt`, which can modify a link attribute on an address book object when the caller has permission. Name resolution and row queries disclose Exchange address book data.

## Dependencies And Integration Points

The module depends on Impacket NDR primitives, common Windows types from `dtypes.py`, `Structure`, UUID helpers, `mapi_constants`, HRESULT errors, `LDAP_SID`, `six.PY2`, and Python `datetime`, `struct`, and `binascii`. It integrates with `rpcrt.DCERPC.request()` and is typically used over normal DCE/RPC transports or through `rpch.py` RPC-over-HTTP connections to Exchange ports. `oxabref.py` complements this module by finding an address book referral target.

## Risks And Edge Cases

The module has broad protocol coverage but explicitly leaves some calls commented out, including `NspiGetMatches`, `NspiResortRestriction`, `NspiModProps`, and an undocumented delete call. The restriction model is therefore structurally present but not fully exercised by helpers. Manual nested count manipulation is fragile; wrong `MaximumCount` or `cValues` values can produce malformed NDR. `hNspiSeekEntries` accepts a `SortType` argument but ignores it and always uses `SortTypeDisplayName`.

`simplifyPropertyRow` relies on property-tag-specific heuristics and can misclassify unknown binary values. Its file-time conversion uses local timezone semantics via `datetime.fromtimestamp()`. `checkNullString` indexes `string[-1:]`, so empty strings work by Python slicing behavior but non-string byte/text mismatches can still matter. `get_guid_from_dn` trusts the last `=` component of a DN and does not validate the result before UUID conversion.

## Test Signals

Unit tests should serialize each helper with a fake DCE object and verify opnum, handle assignment, array counts, null termination, and `checkError` behavior. Property simplification tests should cover scalar, string, binary, SID, GUID, permanent entry ID, ephemeral entry ID, multivalue, and file-time cases. Parser tests need captured Exchange row sets with null pointers and uncommon property tags. Integration tests require an Exchange or NSPI-compatible endpoint and should verify bind, query columns, special table, resolve names, DN-to-MID, get props, and unbind workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/nspi.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/oxabref.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/oxabref.py

## Purpose

`oxabref.py` implements the Address Book Name Service Provider Interface Referral Protocol [MS-OXABREF]. It is a small Exchange address book referral binding that asks an RPC endpoint for a suitable NSPI server or converts a mailbox server distinguished name into a server FQDN.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_OXABREF`, `DCERPCSessionError`, pointer wrappers `PUCHAR_ARRAY` and `PPUCHAR_ARRAY`, and two RPC calls: `RfrGetNewDSA` at opnum 0 and `RfrGetFQDNFromServerDN` at opnum 1. `OPNUMS` maps both calls to their response classes.

Helper functions are `hRfrGetNewDSA(dce, pUserDN='')` and `hRfrGetFQDNFromServerDN(dce, szMailboxServerDN)`. `checkNullString` is the shared local helper that preserves `NULL` and appends a C-style null terminator to non-null strings.

## Control Flow

`hRfrGetNewDSA` builds an opnum 0 request with flags set to zero, a null-terminated user DN, `ppszUnused` set to `NULL`, and an initialized `ppszServer` output pointer. It sends the request and strips the trailing null from `ppszServer`; it attempts the same for `ppszUnused` when the original request field was not `NULL`.

`hRfrGetFQDNFromServerDN` null-terminates the mailbox server DN, sets `cbMailboxServerDN` to the resulting string length, sends opnum 1, and strips the returned FQDN terminator. Error rendering first checks MAPI constants and then generic HRESULT messages.

## State And Persistence Behavior

There is no local persistence and no durable module state. Calls are stateless client requests over a bound DCE connection. Remote state is read-only from this client's perspective: the server chooses or reports address book referral information.

## Dependencies And Integration Points

The module depends on `hresult_errors`, `mapi_constants`, `STR`, `ULONG`, `NULL`, NDR call/pointer classes, `rpcrt.DCERPCException`, and UUID helpers. It integrates with Exchange address book workflows by supplying server names used by `nspi.py` over regular DCE/RPC or RPC-over-HTTP.

## Risks And Edge Cases

String and pointer handling are the main risks. `PUCHAR_ARRAY` uses `STR`, so callers need to provide byte/string values compatible with Impacket's `STR` encoding rules. `hRfrGetNewDSA` tests `request['ppszUnused']` rather than the response before trimming `resp['ppszUnused']`, so it will not trim a non-null server-filled unused pointer when the request passed `NULL`. `checkNullString` assumes sliceable string-like input. Response trimming assumes returned strings are non-empty and null-terminated.

## Test Signals

Tests should verify that both helpers set flags, byte counts, and null terminators correctly, and that response strings are trimmed. A fake DCE object can assert opnum selection and request field layout. Error tests should cover MAPI errors, HRESULT errors, and unknown status values. Integration tests should pair `hRfrGetNewDSA` with `nspi.hNspiBind` against an Exchange endpoint.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/oxabref.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/par.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/par.py

## Purpose

`par.py` implements a client-side subset of the Print System Asynchronous Remote Protocol [MS-PAR]. It mirrors much of the synchronous printer binding shape from `rprn.py`, but uses async spooler opnums and usually sends requests with the WINSPOOL object UUID. The implemented surface opens and closes printer handles, enumerates printers and printer drivers, retrieves driver directories, and installs printer drivers.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_PAR`, `MSRPC_UUID_WINSPOOL`, `DCERPCSessionError`, printer access constants, change notification flags, enumeration flags, notification categories, and driver-copy flags. It defines shared print structures such as `PRINTER_HANDLE`, `DEVMODE_CONTAINER`, `SPLCLIENT_INFO_1/2/3`, `DRIVER_INFO_1/2`, `DRIVER_INFO_UNION`, `DRIVER_CONTAINER`, `CLIENT_INFO_UNION`, `SPLCLIENT_CONTAINER`, and async notify option structures.

RPC calls include `RpcAsyncOpenPrinter` opnum 0, `RpcAsyncClosePrinter` opnum 20, `RpcAsyncEnumPrinters` opnum 38, `RpcAsyncAddPrinterDriver` opnum 39, `RpcAsyncEnumPrinterDrivers` opnum 40, and `RpcAsyncGetPrinterDriverDirectory` opnum 41. Helpers include `hRpcAsyncOpenPrinter`, `hRpcAsyncClosePrinter`, `hRpcAsyncEnumPrinters`, `hRpcAsyncAddPrinterDriver`, `hRpcAsyncEnumPrinterDrivers`, and `hRpcAsyncGetPrinterDriverDirectory`.

## Control Flow

Open and close helpers create a request, populate handles and optional containers, and call `dce.request(request, MSRPC_UUID_WINSPOOL)`. `hRpcAsyncOpenPrinter` requires a non-null client info container and initializes `pDevModeContainer.pDevMode` to `NULL` when no devmode is supplied.

Enumeration helpers follow the common Windows RPC two-call buffer pattern. They first send a request with a null output buffer and zero buffer size. If the server returns `ERROR_INSUFFICIENT_BUFFER`, they read `pcbNeeded` from the decoded error packet, allocate a placeholder byte buffer of that size, and send the request again. Driver enumeration and driver directory lookup use the same pattern. `hRpcAsyncAddPrinterDriver` sends a filled `DRIVER_CONTAINER` and file-copy flags directly.

## State And Persistence Behavior

There is no disk persistence. Runtime state is in printer context handles, caller-supplied driver/client containers, and temporary byte buffers. Remote side effects can be significant: `RpcAsyncAddPrinterDriver` installs printer driver files on the remote spooler, and open/close helpers create and release server-side handles. Enumeration helpers are read-oriented but can disclose printer and driver inventory.

## Dependencies And Integration Points

The module depends on common dtypes, NDR classes, `system_errors`, `rpcrt.DCERPCException`, and UUID helpers. It integrates with the DCE runtime through `dce.request` and object UUID routing. Its structures and helper patterns are intentionally close to `rprn.py`, so tests and callers often compare the async and sync spooler implementations.

## Risks And Edge Cases

There are correctness hazards in the IDL model. `SPLCLIENT_INFO_3` declares `dwFlags` twice, which can overwrite or obscure the first value in Impacket field access. `OPNUMS` maps opnum 39 to `(RpcAsyncAddPrinterDriver, RpcAsyncAddPrinterDriver)` instead of the response class, which can break generic dispatch or server-side use of the table. Error text says `RPRN SessionError`, which is confusing for PAR failures.

The two-call helpers depend on string matching `ERROR_INSUFFICIENT_BUFFER` in exception text and on `e.get_packet()['pcbNeeded']` being available. If the server returns success with no data, a different error, or an undecodable error packet, `bytesNeeded` may remain zero or unbound in some paths. `checkNullString` assumes string-like input, and helpers use placeholder `b'a'` buffers rather than typed result structures.

## Test Signals

Unit tests should verify opnum mappings, especially opnum 39, and serialize every helper with a fake DCE object. Buffer-sizing tests should simulate `ERROR_INSUFFICIENT_BUFFER` packets and successful second calls. Structure tests should cover `DRIVER_CONTAINER` union tags, `SPLCLIENT_CONTAINER` union tags, `NULL` devmode behavior, and the duplicate `dwFlags` field. Integration tests need a Windows spooler and should validate open, enum printers, enum drivers, get driver directory, close, and guarded driver-install scenarios.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/par.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/raa.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/raa.py

## Purpose

`raa.py` implements the client-side Remote Authorization API Protocol [MS-RAA]. It lets callers create authorization contexts from SIDs, combine user and device contexts, run remote access checks against one or more security descriptors, query context information, modify claims, modify SIDs, and free context handles.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_RAA`, default object UUID constants, `AUTHZ_COMPUTE_PRIVILEGES`, security attribute flags and value type constants, and three NDR enum classes: `AUTHZ_CONTEXT_INFORMATION_CLASS`, `AUTHZ_SECURITY_ATTRIBUTE_OPERATION`, and `AUTHZ_SID_OPERATION`.

Core structures include `AUTHZR_HANDLE`, `SR_SD`, `AUTHZR_ACCESS_REQUEST`, `AUTHZR_ACCESS_REPLY`, `AUTHZR_SID_AND_ATTRIBUTES`, `AUTHZR_TOKEN_USER`, custom `AUTHZR_TOKEN_GROUPS`, security attribute string/union/value arrays, `AUTHZR_SECURITY_ATTRIBUTES_INFORMATION`, and `AUTHZR_CONTEXT_INFORMATION`. RPC calls cover opnums 0 through 6: `AuthzrFreeContext`, `AuthzrInitializeContextFromSid`, `AuthzrInitializeCompoundContext`, `AuthzrAccessCheck`, `AuthzGetInformationFromContext`, `AuthzrModifyClaims`, and `AuthzrModifySids`.

Helpers mirror those calls: `hAuthzrFreeContext`, `hAuthzrInitializeContextFromSid`, `hAuthzrInitializeCompoundContext`, `hAuthzrAccessCheck`, `hAuthzGetInformationFromContext`, `hAuthzrModifyClaims`, and `hAuthzrModifySids`. `_enum_operation` coerces raw integer operations into the expected NDR enum wrapper.

## Control Flow

Initialization from SID converts a canonical SID string into `RPC_SID`, clears expiration time with `NULL`, zeros the `LUID`, and requests a context handle using the selected object UUID. Access checks construct an `AUTHZR_ACCESS_REQUEST`, optionally attach an object type list, normalize a single security descriptor into a list, wrap each descriptor as `SR_SD`, initialize reply arrays with the requested result length, and call `dce.request(..., uuid=objectUuid)`.

The modify helpers set operation counts from the caller's operation list, append coerced enum values, and attach optional claims or SID/group arrays. `AUTHZR_TOKEN_GROUPS` has custom parser and serializer flow because observed NDR32 replies omit the conformant-array max count while NDR64 replies include it. Its methods manually handle alignment, group counts, entry serialization, and referent parsing.

## State And Persistence Behavior

There is no local persistence. Server-side authorization contexts are represented by `AUTHZR_HANDLE` values and must be freed by the caller. `hAuthzrModifyClaims` and `hAuthzrModifySids` mutate remote authorization context state for the lifetime of that context. `AuthzrAccessCheck` is read/evaluation-oriented but can reveal effective access and policy behavior for supplied descriptors.

The object UUID argument changes server behavior. `RAA_OBJECT_UUID_NO_SCOPED_POLICY_BIN` disables server-side stripping of `SYSTEM_SCOPED_POLICY_ID_ACE` entries during access checks, so callers must choose the object UUID intentionally.

## Dependencies And Integration Points

Dependencies include `struct.pack`, `struct.unpack_from`, Impacket NDR classes, dtypes such as `RPC_SID`, `OBJECT_TYPE_LIST`, `LUID`, and `ACCESS_MASK`, the local compatibility `Enum`, `system_errors`, `rpcrt.DCERPCException`, and UUID helpers. The module integrates with security descriptor builders/parsers elsewhere in Impacket and with `rpcrt` object UUID request support.

## Risks And Edge Cases

The security impact is medium to high because the module can model hypothetical group, SID, and claim changes and ask a remote host for resulting access. Callers can misuse it for reconnaissance of authorization boundaries. Context handles are server resources; failing to call `hAuthzrFreeContext` can leak server-side state until timeout.

Parsing risk is concentrated in `AUTHZR_TOKEN_GROUPS`, whose custom NDR32/NDR64 behavior is based on observed Windows replies. Malformed or alternate server encodings can desynchronize offsets. The boolean security attribute maps to a `ULONGLONG` field named `Uint64`, which may surprise callers. `DCERPCSessionError` is defined at the end of the file after helpers, which works at runtime but is easy to miss during review.

## Test Signals

Tests should cover canonical SID conversion, context initialization request layout, compound context handle assignment, access checks with one and multiple security descriptors, object type lists, result lengths greater than one, and both object UUID modes. Parser tests should round-trip `AUTHZR_TOKEN_GROUPS` in NDR32 and NDR64 with zero, one, and multiple groups. Modify tests should verify enum coercion from both raw integers and enum instances. Integration tests should run against a Windows host and compare granted masks with local AuthZ expectations for known descriptors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/raa.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/rpch.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/rpch.py

## Purpose

`rpch.py` implements Impacket's RPC over HTTP v2 client support, including RTS PDU structures and a transport-like `RPCProxyClient` built on `HTTPClientSecurityProvider`. It establishes paired `RPC_IN_DATA` and `RPC_OUT_DATA` HTTP channels, performs RPC proxy authentication, creates the virtual connection tunnel, reads RPC and RTS packets from the outbound channel, sends RPC data on the inbound channel, and maintains flow-control acknowledgments.

## Important APIs, Types, And Functions

The module exports RPC-over-HTTP version constants, proxy error strings, forward destination constants, RTS flags, RTS command constants, `RPCProxyClientException`, RTS command structures, helper packet builders, and `RPCProxyClient`.

RTS structures include `RTSCookie`, `EncodedClientAddress`, `Ack`, command wrappers such as `ReceiveWindowSize`, `FlowControlAck`, `ConnectionTimeout`, `Cookie`, `ChannelLifetime`, `ClientKeepalive`, `Version`, `Empty`, `Padding`, `NegativeANCE`, `ANCE`, `ClientAddress`, `AssociationGroupId`, `Destination`, and `PingTrafficSentNotify`, plus `RTSHeader`. Higher-level RTS PDUs include `CONN_A1_RTS_PDU`, `CONN_B1_RTS_PDU`, `CONN_A3_RTS_PDU`, `CONN_C2_RTS_PDU`, and `FlowControlAckWithDestination_RTS_PDU`.

Helpers `hCONN_A1`, `hCONN_B1`, `hFlowControlAckWithDestination`, and `hPing` return serialized RTS packets. `RPCProxyClient` exposes `connect`, `disconnect`, `send`, `recv`, channel creation/closing methods, `rpc_out_read_pkt`, `rpc_out_recv1`, `flow_control`, and `handle_out_of_sequence_rts`.

## Control Flow

`RPCProxyClient.connect()` creates the inbound and outbound HTTP channels, then calls `create_tunnel()`. Channel creation prepares RPC proxy headers, obtains authentication headers from `HTTPClientSecurityProvider`, derives or validates the remote RPC server name, adds `?RemoteName:Port` to the RPC proxy URL when needed, sends the HTTP method request, and waits for an HTTP 100 Continue response.

Tunnel creation sends CONN/A1 on the out channel and CONN/B1 on the in channel, reads the outbound HTTP 200 response, detects chunked transfer encoding, preserves any body bytes already received, then parses CONN/A3 and CONN/C2 RTS PDUs to capture server timeout and receive-window values.

Outbound reads use `rpc_out_read_pkt()`: read the common RPC header, read exactly `frag_len`, apply flow control to non-RTS packets, and either handle out-of-sequence RTS packets or return the packet. `rpc_out_recv1()` abstracts normal and chunked HTTP body reads while preserving over-read bytes. `flow_control()` sends a `FlowControlAckWithDestination` packet when the advertised receive window drops below half. `handle_out_of_sequence_rts()` replies to ping RTS packets and rejects channel recycle requests.

## State And Persistence Behavior

There is no disk persistence. Runtime state includes HTTP channel objects, generated cookies, association group ID, virtual connection cookie, server timeout/window values, advertised and remaining receive windows, bytes received, chunked transfer state, read buffer leftovers, and an `rts_ping_received` flag. `disconnect()` closes both channels and resets state via `init_state()`.

The class mutates the transport string binding when it learns the RPC proxy NetBIOS name from NTLMSSP. It also caches the remote name for later channel creation.

## Dependencies And Integration Points

The module depends on `re`, `binascii`, `struct.unpack`, Impacket `uuid`, `ntlm`, system and NT error tables, `LOG`, `EMPTY_UUID`, `HTTPClientSecurityProvider`, `AUTH_BASIC`, `Structure`, and constants/classes from `rpcrt.py`. It is an integration layer between Impacket's HTTP authentication stack and `rpcrt.DCERPC_v5`, which can use this object as an RPC transport provider. Exchange NSPI and OXABREF workflows are important consumers.

## Risks And Edge Cases

HTTP parsing is intentionally narrow and stream-oriented. The code reads until CRLFCRLF for response headers, checks fixed byte offsets in status lines, and handles localized errors only in the first line. Chunked decoding tracks one chunk at a time and assumes well-formed chunk-size lines and trailing CRLF; malformed proxies can desynchronize the read buffer. HTTP 503 RPC errors are detected by a fixed prefix.

RPC proxy behavior differs across Exchange and RD Gateway deployments, and the code contains assumptions about valid ports, remote names, and NTLM-derived host names. Basic auth requires an explicit remote name. Long-lived idle tunnels are not fully supported: a ping RTS packet is treated as a sign of likely server-side trouble, though the client sends pings back. Channel recycle requests are explicitly unsupported.

## Test Signals

Unit tests should serialize all RTS helper packets and validate flags, command counts, cookies, and window values. Stream tests should cover non-chunked reads, chunked reads with split chunk headers, over-read buffering, HTTP error injection, and RTS packet interleaving. Authentication/channel tests can mock `HTTPClientSecurityProvider` to verify Basic-auth remote-name failure, NTLM-derived remote names, RPC proxy query construction, and 100 Continue handling. Integration tests need an RPC proxy or Exchange endpoint and should verify bind and request flow through `rpcrt.DCERPC_v5`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/rpch.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/rpcrt.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/rpcrt.py

## Purpose

`rpcrt.py` is Impacket's core partial implementation of connection-oriented DCE/RPC v5 runtime behavior. It defines PDU constants, status-code tables, packet structures, bind and alter-context negotiation, authenticated send/receive handling for NTLM, Netlogon, and Kerberos/SPNEGO, request/response dispatch, fragmentation/reassembly, object UUID calls, type serialization headers, and a minimal DCE/RPC server used by SMB server and relay scenarios.

## Important APIs, Types, And Functions

The public surface includes PDU type constants, packet flags, authentication provider and level constants, `rpc_status_codes`, many named `MSRPC_STATUS_CODE_*` constants, bind-time feature negotiation constants, and `MSRPC_STANDARD_NDR_SYNTAX`. `DCERPCException` is the common runtime exception for transports and protocol modules.

Packet and bind structures include `CtxItem`, `CtxItemResult`, `SEC_TRAILER`, `MSRPCHeader`, `MSRPCRequestHeader`, `MSRPCRespHeader`, `MSRPCBind`, `MSRPCRelayBind`, `MSRPCBindAck`, `MSRPCRelayBindAck`, and `MSRPCBindNak`. Runtime classes are `DCERPC`, `DCERPC_v4`, `DCERPC_v5`, `DCERPC_RawCall`, and `DCERPCServer`. Type serialization helpers are `CommonHeader`, `PrivateHeader`, and `TypeSerialization1`.

Important `DCERPC_v5` APIs include `set_credentials`, `get_credentials`, `set_auth_level`, `set_auth_type`, `get_auth_type`, `set_aes`, `set_session_key`, `get_session_key`, `set_max_tfrag`, `bind`, `send`, `recv`, and `alter_ctx`. `DCERPC.request()` implements the common NDR call pattern used by almost every protocol binding in `impacket.dcerpc.v5`.

## Control Flow

`DCERPC.request()` adapts the request for NDR64 when needed, calls the request opnum, receives bytes, imports the request module, locates the matching `*Response` class, and either returns a decoded response or raises a module-specific `DCERPCSessionError`/runtime exception based on the final four-byte error code.

`DCERPC_v5.bind()` builds one or more presentation context items, optionally prepending bogus contexts, then sends a bind or alter-context PDU. If authentication is enabled, it obtains credentials, builds a Type 1 token for NTLM, Netlogon, or Kerberos, appends a security trailer, and sends the bind. It parses bind acknowledgments or faults, validates accepted context results, stores the selected transfer syntax and negotiated max transmit size, completes authentication with NTLM Type 3, Netlogon, or Kerberos continuation tokens, initializes signing/sealing keys and sequence state, and sends AUTH3 or Kerberos alter-context continuation when required.

`send()` wraps raw calls, sets call ID, context ID, object UUID flags, and allocation hint, decides whether fragmentation is needed based on negotiated and user fragment sizes, emits first/middle/last fragments, and signs or seals each fragment through `_transport_send()`. `_transport_send()` adds security trailers, computes padding, signs or encrypts payloads for packet integrity or privacy, increments sequence numbers, and delegates to the underlying transport. `recv()` reads full response fragments, handles faults, strips and verifies/decrypts authentication trailers when configured, removes auth padding, reassembles fragments, and returns stub data.

`DCERPCServer` accepts sockets, parses bind requests, validates transfer syntax and registered interface UUIDs, returns bind acks, dispatches request opnums to registered callbacks, returns faults for unsupported opnums, and fragments server responses when needed.

## State And Persistence Behavior

There is no disk persistence. Client runtime state includes transport, context ID, call ID, negotiated transfer syntax, max transmit size, credentials, authentication type and level, session key, signing/sealing keys and ARC4 handles, Netlogon confounder, Kerberos GSS wrapper, sequence number, and max user fragment setting. `alter_ctx()` creates a new runtime object sharing the same underlying transport and credentials but with a new context.

Server state includes listening socket, bound UUID, callback registry, current client socket, call ID, listen address/port, and fragmentation settings. Registered callbacks persist in memory until the server object is discarded.

## Dependencies And Integration Points

The module depends on sockets, logging, threading, `Cryptodome.Cipher.ARC4`, Impacket NTLM, Kerberos, GSSAPI, UUID helpers, `Structure` packing/unpacking, `dtypes`, NDR structures, HRESULT errors, and `LOG`. Every DCE/RPC protocol binding in this directory depends on `DCERPCException` and `DCERPC_v5.request()` semantics. Transports from `impacket.dcerpc.v5.transport` supply the actual SMB, TCP, HTTP, or local communication layer.

## Risks And Edge Cases

This file is security-critical because authentication, signing, sealing, fault handling, and fragmentation all converge here. Several comments flag incomplete behavior: receive-side NTLM packet privacy with extended session security says signature calculation needs fixing, and fragmentation sizing uses a broad 128-byte trailer estimate. Kerberos and Netlogon sequence handling has provider-specific branches that are easy to regress. `DCERPC.request()` assumes non-error NDR responses end with four zero bytes, which can be brittle for unusual stubs.

Parsing and compatibility risks include manual PDU length calculations, object UUID header-size adjustments, auth trailer padding, and fixed assumptions about connection-oriented NDR32/NDR64 syntax. `MSRPCBind.getData()` and related structures append to `ctx_items` without clearing it, so repeated serialization of the same object can duplicate context bytes. The minimal server ignores authentication and only supports NDR32 in bind acceptance. Some server paths set padding as text strings instead of bytes, which can be problematic under strict Python 3 byte handling.

## Test Signals

Unit tests should cover PDU structure round trips, bind context item construction, bind ack parsing, bind rejection messages, request response class lookup, module-specific error raising, object UUID calls, fragmentation boundaries, and repeated `getData()` calls on bind structures. Auth tests should use known NTLM, Netlogon, and Kerberos fixtures for connect, integrity, and privacy levels. Transport tests should simulate multi-fragment responses, faults with RPC and HRESULT codes, auth padding, and short reads. Server tests should bind supported and unsupported interfaces, dispatch known and unknown opnums, and verify response fragmentation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/rpcrt.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/rprn.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/rprn.py

## Purpose

`rprn.py` implements a client-side subset of the Print System Remote Protocol [MS-RPRN]. It models print spooler RPC structures and helpers for enumerating printers and drivers, opening and closing printer handles, registering for change notifications, retrieving driver directories, and installing printer drivers.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_RPRN`, `DCERPCSessionError`, printer/job/server access constants, change notification flags, printer enumeration flags, notification category constants, and AddPrinterDriverEx file-copy flags. Shared structures include `PRINTER_HANDLE`, `DEVMODE_CONTAINER`, `SPLCLIENT_INFO_1/2/3`, `DRIVER_INFO_1/2`, `DRIVER_INFO_UNION`, `DRIVER_CONTAINER`, `CLIENT_INFO_UNION`, `SPLCLIENT_CONTAINER`, `RPC_V2_NOTIFY_OPTIONS_TYPE`, and `RPC_V2_NOTIFY_OPTIONS`.

RPC calls include `RpcEnumPrinters` opnum 0, `RpcOpenPrinter` opnum 1, `RpcEnumPrinterDrivers` opnum 10, `RpcGetPrinterDriverDirectory` opnum 12, `RpcClosePrinter` opnum 29, `RpcRemoteFindFirstPrinterChangeNotificationEx` opnum 65, `RpcOpenPrinterEx` opnum 69, and `RpcAddPrinterDriverEx` opnum 89. Helpers include `hRpcOpenPrinter`, `hRpcClosePrinter`, `hRpcOpenPrinterEx`, `hRpcRemoteFindFirstPrinterChangeNotificationEx`, `hRpcEnumPrinters`, `hRpcAddPrinterDriverEx`, `hRpcEnumPrinterDrivers`, and `hRpcGetPrinterDriverDirectory`.

## Control Flow

Open helpers null-terminate printer names, attach optional datatype and devmode containers, set access masks, and send requests through `dce.request()`. `hRpcOpenPrinterEx` additionally requires a non-null `SPLCLIENT_CONTAINER`. `hRpcRemoteFindFirstPrinterChangeNotificationEx` requires `pszLocalMachine`, null-terminates it, sets flags/options/local IDs, and sends the notification registration request.

Enumeration and directory helpers use a two-call buffer sizing pattern. The first request sends a null output buffer and zero size. On `ERROR_INSUFFICIENT_BUFFER`, the helper extracts `pcbNeeded` from the decoded exception packet, creates a byte buffer of that size, and retries. `hRpcAddPrinterDriverEx` sends a `DRIVER_CONTAINER` and copy flags directly, which can trigger server-side driver installation.

## State And Persistence Behavior

There is no local disk persistence. Runtime state is carried in remote spooler handles, request/response NDR objects, and temporary output buffers. Remote state can change: `RpcAddPrinterDriverEx` installs or updates printer driver files, `RpcRemoteFindFirstPrinterChangeNotificationEx` registers a server-side notification object, and open/close calls allocate and release handles. Enumeration helpers are read-only from the client perspective.

## Dependencies And Integration Points

The module depends on common dtypes, NDR classes, `system_errors`, `rpcrt.DCERPCException`, and UUID helpers. It integrates with Impacket transports over named pipes such as `\pipe\spoolss` and with `rpcrt.DCERPC.request()` for response decoding and module-specific error handling. `par.py` duplicates much of this module's model for asynchronous print operations.

## Risks And Edge Cases

The print spooler attack surface is historically sensitive. Driver installation and notification registration helpers can be used in offensive workflows when credentials permit. Callers should treat `hRpcAddPrinterDriverEx` as a remote state-changing operation, not as a harmless enumeration helper.

Structure correctness risks mirror `par.py`: `SPLCLIENT_INFO_3` declares `dwFlags` twice, and union tags must be set correctly by callers for driver and client containers. The two-call buffer helpers rely on matching `ERROR_INSUFFICIENT_BUFFER` in exception text and on decoded packets containing `pcbNeeded`; alternate server errors can leave `bytesNeeded` at zero or uninitialized. `checkNullString` assumes string-like input. Placeholder byte buffers are sufficient for NDR output buffers but do not parse returned printer information into typed records.

## Test Signals

Unit tests should verify opnum mappings, helper request layouts, null handling, required parameter exceptions, and two-call retry behavior with fake DCE responses. Structure tests should cover `PRINTER_HANDLE` alignment in NDR32/NDR64, devmode null pointers, driver container union tags, client info union tags, and notification option pointers. Integration tests against a Windows spooler should cover enum printers, open/close, enum drivers, driver directory lookup, notification registration, and a tightly controlled AddPrinterDriverEx path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/rprn.py -->
