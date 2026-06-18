# Research Group subset-b-009621

This grouped report covers ntlmrelayx relay clients, relay listener servers, and HTTP/HTTPS SOCKS plugins under `sources/user-network-fs/impacket/impacket/examples/ntlmrelayx`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/dcsyncclient.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/dcsyncclient.py

## Purpose
`dcsyncclient.py` implements the `DCSYNC` relay target client. It relays a captured NTLM exchange directly into DRSUAPI, then uses Netlogon/Zerologon-style validation to derive the DCE/RPC signing and sealing key needed for directory replication calls and `secretsdump`-style NTDS extraction.

## Important APIs, Types, and Functions
`MYDCERPC_v5` extends `DCERPC_v5` with `sendBindType1()` and `sendBindType3()` so the relay can inject NTLM type 1 and type 3 blobs into RPC bind/auth3 packets at packet privacy level. `PatchedRemoteOperations` bypasses SAMR setup when no SMB credentials are supplied. `DCSYNCRelayClient` exposes the ntlmrelayx client contract: `initConnection()`, `sendNegotiate()`, `sendAuth()`, `netlogonSessionKey()`, `killConnection()`, and `keepAlive()`.

## Control Flow
Construction resolves the DRSUAPI string binding through endpoint mapper. `initConnection()` builds a DCE/RPC transport, optionally authenticating its transport over SMB with configured RPC SMB credentials. `sendNegotiate()` parses the incoming NTLM negotiate, forces seal support, sends an RPC bind with NTLM type 1, and returns the target challenge. `sendAuth()` unwraps SPNEGO when needed, obtains the sign/seal key through `netlogonSessionKey()`, recalculates the NTLM MIC, sends auth3, performs `DRSBind`, initializes `RemoteOperations`, discovers the NTDS DSA object GUID, and invokes `NTDSHashes.dump()` for all users or selected high-value accounts.

## State and Persistence Behavior
The client mutates `self.session` private signing/sealing fields and RC4 handles directly after Netlogon validation. It stores the negotiated message and challenge for MIC recalculation. Dump output is written through `NTDSHashes` using the hard-coded output prefix `hashes`; `RemoteOperations.finish()` is called in `finally`.

## Dependencies and Integration Points
It depends on Impacket NTLM/SPNEGO, DCE/RPC endpoint mapper, DRSUAPI, NRPC, SMBConnection, and `examples.secretsdump`. It integrates with ntlmrelayx protocol registration through `PROTOCOL_CLIENT_CLASS` and with RPC options such as `rpc_mode`, `rpc_use_smb`, and SMB credential fields on `serverConfig`.

## Risks and Edge Cases
This client is tightly coupled to vulnerable or specially configured Netlogon behavior, NTLMv2 AV pairs, DCE/RPC private attributes, and target DRS permissions. It prints tracebacks on exceptions and may leave partial hash output. NTLMv1 is rejected, patched Zerologon targets fail after many attempts, and DRS extension epoch mismatch requires a second bind.

## Test Signals
Use controlled lab DCs to test successful type1/type3 DRS bind, NTLM MIC recalculation, Netlogon failure paths, NTLMv1 rejection, SMB-credential and no-SMB modes, and `RemoteOperations.finish()` cleanup after exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/dcsyncclient.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/httprelayclient.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/httprelayclient.py

## Purpose
`httprelayclient.py` provides HTTP and HTTPS relay target clients. It turns an incoming NTLM negotiate/authenticate exchange into `Authorization: NTLM` or `Authorization: Negotiate` requests against a web server and treats any non-401 final response as successful authentication.

## Important APIs, Types, and Functions
`HTTPRelayClient` implements `initConnection()`, `sendNegotiate()`, `sendAuth()`, `killConnection()`, and `keepAlive()`. `HTTPSRelayClient` reuses all behavior but creates an `HTTPSConnection` with an SSL context. `PROTOCOL_CLIENT_CLASSES` registers both `HTTPRelayClient` and `HTTPSRelayClient`.

## Control Flow
`initConnection()` creates an HTTP connection and normalizes path/query. `sendNegotiate()` first probes the URL to obtain `WWW-Authenticate`, selects NTLM over Negotiate when both are offered, sends the base64 type 1 token, extracts a challenge from the response header, and returns `NTLMAuthChallenge`. `sendAuth()` unwraps SPNEGO responses, base64 encodes the NTLM token, sends another GET, and returns access denied only on HTTP 401. `keepAlive()` sends a HEAD request for `/favicon.ico`.

## State and Persistence Behavior
State lives in the connection object, `path`, `query`, `authenticationMethod`, and cached `lastresult` response body after a successful relay. No filesystem writes occur in this client.

## Dependencies and Integration Points
It uses Python `http.client`/`httplib`, `ssl`, `base64`, regex header parsing, Impacket NTLM/SPNEGO, and ntlmrelayx `ProtocolClient`. The HTTP relay server and SOCKS HTTP plugin can reuse the authenticated `HTTPConnection` session.

## Risks and Edge Cases
Header parsing assumes a single recognizable challenge in `WWW-Authenticate`. Non-401 status codes are considered success even if the target application denies access later. Anonymous ADCS/IIS handling can force NTLM despite missing auth headers. Keepalive ignores response state and may fail if a previous response body was not consumed.

## Test Signals
Exercise NTLM and Negotiate headers, query preservation, HTTPS context creation, 401 failure, 200/403/500 success semantics, missing headers, ADCS anonymous fallback, and SOCKS reuse of `lastresult`/socket state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/httprelayclient.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/imaprelayclient.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/imaprelayclient.py

## Purpose
`imaprelayclient.py` implements IMAP and IMAPS NTLM relay target clients for mail servers such as Exchange. It drives IMAP `AUTHENTICATE NTLM` manually enough to relay NTLM type 1 and type 3 tokens.

## Important APIs, Types, and Functions
`IMAPRelayClient` provides the ntlmrelayx client interface. It stores an IMAP tag in `authTag`, sends raw IMAP lines with `imaplib`, and marks successful sessions authenticated. `IMAPSRelayClient` changes only the default port and connection class. `PROTOCOL_CLIENT_CLASSES` registers both variants.

## Control Flow
`initConnection()` connects, allocates a tag with `_new_tag()`, logs capabilities, and requires `AUTH=NTLM`. `sendNegotiate()` sends `AUTHENTICATE NTLM`, waits for the continuation prompt, sends the base64 type 1 blob, decodes the server continuation challenge, and returns `NTLMAuthChallenge`. `sendAuth()` unwraps SPNEGO if present, sends the base64 type 3 blob, and waits for the tagged response to decide between `STATUS_SUCCESS` and `STATUS_ACCESS_DENIED`.

## State and Persistence Behavior
The active `imaplib` session, `authTag`, and IMAP state are the only retained state. A successful relay sets `self.session.state = 'AUTH'`. There is no local persistence.

## Dependencies and Integration Points
It depends on Python `imaplib`, Impacket NTLM/SPNEGO, and the common `ProtocolClient`. SOCKS IMAP plugins can later proxy through the authenticated IMAP session.

## Risks and Edge Cases
The code uses `imaplib` private methods and raw `send()`/`readline()` flows, so Python version or server response formatting differences can break parsing. It compares capabilities against a string literal, and failures may raise after logging instead of returning a relay status.

## Test Signals
Test IMAP and IMAPS servers that advertise or omit `AUTH=NTLM`, continuation prompt mismatch, SPNEGO-wrapped auth, tagged OK/NO/BAD responses, logout cleanup, and NOOP keepalive.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/imaprelayclient.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/ldaprelayclient.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/ldaprelayclient.py

## Purpose
`ldaprelayclient.py` implements LDAP and LDAPS relay target clients using ldap3's Sicily NTLM bind path. It supports normal relays and flag-stripping modes used by ntlmrelayx options for MIC/sign/seal removal.

## Important APIs, Types, and Functions
`LDAPRelayClient` exposes `initConnection()`, `sendNegotiate()`, `sendAuth()`, fake ldap3 callbacks `create_negotiate_message()` and `create_authenticate_message()`, `parse_challenge_message()`, and `keepAlive()`. `LDAPSRelayClient` changes the server URI and default port. `MODIFY_ADD` is re-exported for LDAP attack modules.

## Control Flow
`initConnection()` opens an unauthenticated ldap3 `Connection`. `sendNegotiate()` parses the incoming NTLM type 1, optionally removes SIGN, ALWAYS_SIGN, and SEAL flags, performs Sicily package discovery, sends `SICILY_NEGOTIATE_NTLM`, and stores the challenge in `sessionData`. `sendAuth()` unwraps SPNEGO, optionally strips MIC, key exchange, version, sign, always-sign, and seal fields from the type 3 message, then sends `SICILY_RESPONSE_NTLM`. Successful bind marks the ldap3 connection as bound and refreshes server info.

## State and Persistence Behavior
The ldap3 connection lock and `sasl_in_progress` flag guard bind state. `negotiateMessage`, `authenticateMessageBlob`, and `sessionData['CHALLENGE_MESSAGE']` are retained for ldap3 callbacks and SOCKS/attack reuse. No filesystem persistence occurs.

## Dependencies and Integration Points
It depends on ldap3 `Server`, `Connection`, Sicily bind operations, Impacket NTLM structures, SPNEGO, nt status constants, and ntlmrelayx config flags `remove_mic` and `remove_sign_seal`.

## Risks and Edge Cases
This is intentionally "hacky" ldap3 integration. LDAP signing requirements produce stronger-auth errors unless LDAPS is used. Flag stripping can invalidate standard NTLM semantics except for specific vulnerabilities or nonstandard clients. Missing ldap3 versions exit the process.

## Test Signals
Cover LDAP and LDAPS binds, NTLM package discovery failure, signing-required rejection, MIC removal, sign/seal removal, SPNEGO unwrap, server-info refresh, and keepalive base search.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/ldaprelayclient.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/mssqlrelayclient.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/mssqlrelayclient.py

## Purpose
`mssqlrelayclient.py` provides an MSSQL/TDS relay target client. It wraps Impacket's `MSSQL` class to send NTLMSSP data inside TDS login and SSPI packets, enabling relay to SQL Server integrated authentication.

## Important APIs, Types, and Functions
`MYMSSQL` extends `MSSQL` with `initConnection()`, `sendNegotiate()`, `sendAuth()`, and `close()`. `MSSQLRelayClient` delegates relay calls to `MYMSSQL` and exposes helper methods `sql_query()`, `printReplies()`, and `printRows()` for attack modules.

## Control Flow
`MYMSSQL.initConnection()` connects and negotiates encryption. `sendNegotiate()` builds a TDS LOGIN7 packet with random host/app names, integrated-security flags, and the NTLM type 1 blob in `SSPI`, then reads the target's TDS SSPI response and parses the NTLM challenge from `Data[3:]`. `sendAuth()` unwraps SPNEGO, sends a TDS SSPI packet with type 3 data, parses replies, and treats `TDS_LOGINACK_TOKEN` as success.

## State and Persistence Behavior
`MYMSSQL` records `resp`, `sessionData['NTLM_CHALLENGE']`, and `sessionData['AUTH_ANSWER']`. `MSSQLRelayClient.sendAuth()` exposes that sessionData to the server/attack layer. SQL connection state remains in the underlying socket/TDS session.

## Dependencies and Integration Points
It depends on Impacket TDS constants and `MSSQL`, NTLM challenge parsing, SPNEGO, and ntlmrelayx `ProtocolClient`. Attack modules can execute SQL through `sql_query()`.

## Risks and Edge Cases
TDS encryption behavior is nuanced: when encryption is off, only the first login packet should remain TLS-wrapped, while TDS 8.0 keeps TLS. Failure detection depends on login-ack tokens and may miss useful error state. SQL authentication is explicitly not handled.

## Test Signals
Test SQL Server versions with encryption off/on/required, TDS 8.0, NTLM challenge parsing, SPNEGO type 3 unwrap, login failure token paths, and post-auth batch query execution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/mssqlrelayclient.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/rpcrelayclient.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/rpcrelayclient.py

## Purpose
`rpcrelayclient.py` relays NTLM authentication to selected DCE/RPC endpoints, currently TSCH and ICPR. It builds custom RPC bind/auth3 packets so ntlmrelayx can validate a relayed identity against RPC services.

## Important APIs, Types, and Functions
`MYDCERPC_v5` provides `sendBindType1()` and `sendBindType3()` with `RPC_C_AUTHN_LEVEL_CONNECT`. `DummyOp` is an `NDRCALL` with opnum 255 used to probe post-auth behavior. `RPCRelayClient` implements endpoint selection, connection setup, NTLM negotiate/auth, keepalive, and disconnect.

## Control Flow
The constructor maps `serverConfig.rpc_mode` to TSCH or ICPR UUID and chooses SMB named pipes or endpoint mapper string bindings. `initConnection()` creates transport, optionally authenticates SMB transport credentials, and connects with the appropriate auth level. `sendNegotiate()` sends NTLM type 1 in an RPC bind and parses the bind-ack challenge. `sendAuth()` sends auth3 with the type 3 token, then issues `DummyOp`; expected operation-range or invalid-header exceptions mean authentication worked, while access denied means failure.

## State and Persistence Behavior
State is the `MYDCERPC_v5` session and selected string binding/UUID. No data is persisted. Keepalive repeats `DummyOp` and expects the same benign exception pattern.

## Dependencies and Integration Points
It depends on Impacket DCE/RPC transport, endpoint mapper, TSCH, ICPR, RPC packet classes, NTLM/SPNEGO parsing, and ntlmrelayx RPC config fields.

## Risks and Edge Cases
Endpoint support is deliberately narrow. The file imports `transport`, `rpcrt`, `epm`, and `tsch` twice and imports `icpr` only in the first duplicated import. `keepAlive()` uses `or` where `and` was likely intended, so exception filtering is suspicious. Success inference relies on service-specific error strings.

## Test Signals
Cover TCP and SMB transports, TSCH and ICPR UUIDs, bind nak/fault paths, SPNEGO unwrap, dummy-op success inference, access denied, and keepalive exception filtering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/rpcrelayclient.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/smbrelayclient.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/smbrelayclient.py

## Purpose
`smbrelayclient.py` is the SMB relay target client. It negotiates SMB1 or SMB2/3 with a target, relays NTLMSSP session setup messages, supports standard security for reflection, and can derive signing keys through Netlogon for remove-target/MIC scenarios.

## Important APIs, Types, and Functions
`MYSMB` and `MYSMB3` customize negotiation to respect extended security and avoid signing. `SMBRelayClient` implements `initConnection()`, `sendNegotiate()`, SMB1/SMB2 negotiate/auth variants, `sendStandardSecurityAuth()`, `netlogonSessionKey()`, `getStandardSecurityChallenge()`, `isAdmin()`, and keepalive.

## Control Flow
`initConnection()` manually negotiates dialects, chooses SMB1 vs SMB2/3, and wraps the low-level connection in `SMBConnection`. `sendNegotiate()` optionally strips MIC-related flags, relays type 1 through SMB1 SessionSetupAndX or SMB2 SESSION_SETUP, stores the challenge in `sessionData`, and records the server challenge. `sendAuth()` optionally strips MIC fields, handles `remove_target` by validating over Netlogon and recalculating the MIC, then sends SMB1 or SMB2 type 3 auth. Standard-security auth sends ANSI/Unicode password fields directly.

## State and Persistence Behavior
The client retains `sessionData`, negotiate/challenge bytes, server challenge, keepalive hit count, machine account settings, and an active SMBConnection. Successful remove-target mode installs a signing key on the underlying SMB connection. No local files are written by this client.

## Dependencies and Integration Points
It integrates deeply with Impacket SMB, SMB3, SMBConnection, SPNEGO, NRPC, SCMR, DCERPC transport, ntlmrelayx SOCKS keepalive timing, and config flags for SMB2 support, remove_mic, remove_target, machineAccount, machineHashes, and domainIp.

## Risks and Edge Cases
Signing-required targets stop the attack unless a compatible bypass is enabled. Manual packet construction touches private SMB internals and dialect-specific status handling. Netlogon-derived signing relies on configured machine credentials. `isAdmin()` opens SCMR and treats failures broadly.

## Test Signals
Test SMB1, SMB2.002, SMB2.1, SMB3 negotiation, signing-required rejection, remove_mic and remove_target modes, standard-security reflection, Netlogon signing key installation, IPC$ keepalive, and SCMR admin detection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/smbrelayclient.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/smtprelayclient.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/smtprelayclient.py

## Purpose
`smtprelayclient.py` implements an SMTP NTLM relay target client for mail servers. It drives the `AUTH NTLM` command sequence using Python `smtplib`.

## Important APIs, Types, and Functions
`SMTPRelayClient` provides `initConnection()`, `sendNegotiate()`, `sendAuth()`, `killConnection()`, and `keepAlive()`. `PROTOCOL_CLIENT_CLASSES` registers the SMTP client.

## Control Flow
`initConnection()` opens an SMTP connection, sends EHLO, and verifies the EHLO response advertises `AUTH NTLM`. `sendNegotiate()` sends `AUTH NTLM`, expects reply code 334, sends the base64 type 1 token, decodes the returned challenge, and returns `NTLMAuthChallenge`. `sendAuth()` unwraps SPNEGO if needed, sends base64 type 3 data, and treats SMTP 235 as success.

## State and Persistence Behavior
Only the `smtplib.SMTP` session is retained. A successful relay sets `self.session.state = 'AUTH'`. No output files or external persistence are touched.

## Dependencies and Integration Points
It depends on Python `smtplib`, `base64`, Impacket NTLM/SPNEGO, and `ProtocolClient`. Authenticated sessions can be consumed by SMTP attack or SOCKS layers if configured elsewhere.

## Risks and Edge Cases
EHLO response handling assumes string containment for `AUTH NTLM`, which may vary by Python version and server formatting. The code logs `''.join(data)` on failure even though `data` may be bytes, and STARTTLS is not handled here.

## Test Signals
Cover servers with and without `AUTH NTLM`, 334 prompt failure, challenge decoding, SPNEGO auth unwrap, 235 success, non-235 denial, SMTP close, and NOOP keepalive.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/smtprelayclient.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/winrmrelayclient.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/winrmrelayclient.py

## Purpose
`winrmrelayclient.py` implements a WinRM-over-HTTPS relay target client named `WINRMS`. It sends SOAP POST requests to `/wsman` and relays NTLM through HTTP authorization headers.

## Important APIs, Types, and Functions
`WinRMSRelayClient` implements connection setup, `sendNegotiate()`, `sendAuth()`, `killConnection()`, placeholder `isAdmin()`, and SOAP `keepAlive()`. It parses and can modify NTLM negotiate/auth flags for remove-MIC behavior.

## Control Flow
`initConnection()` opens `HTTPSConnection` and defaults the path to `/wsman`. `sendNegotiate()` parses the incoming type 1 token, optionally removes SIGN and ALWAYS_SIGN, probes with a SOAP POST, selects NTLM or Negotiate from `WWW-Authenticate`, sends base64 type 1 auth, and parses the returned challenge. `sendAuth()` unwraps SPNEGO, logs NTLMv2/channel-binding risk heuristics, sends base64 type 3 auth, and treats any non-401 response as success. `keepAlive()` sends a shell-create SOAP envelope.

## State and Persistence Behavior
The client stores `path`, HTTPS connection, `authenticationMethod`, `negotiateMessage`, `lastresult`, and constant XML payloads. It does not write files.

## Dependencies and Integration Points
It uses `HTTPSConnection`, `ssl`, regex header parsing, Impacket NTLM/SPNEGO, ntlmrelayx config flags, and WinRM SOAP conventions. It mirrors HTTP relay behavior but with POST/SOAP semantics.

## Risks and Edge Cases
The negotiate path computes a modified `self.negotiateMessage` but base64 encodes the original `negotiateMessage` variable, so remove-MIC behavior may be ineffective. Success uses non-401 status only. `isAdmin()` is a stub, and the keepalive SOAP target is hard-coded to `windows-host:5986`.

## Test Signals
Test `/wsman` default path, NTLM and Negotiate header parsing, connection failures, remove-MIC behavior, NTLMv2 logging, 401 denial, non-401 success, response caching, and keepalive SOAP handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/winrmrelayclient.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/__init__.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/__init__.py

## Purpose
`servers/__init__.py` exposes ntlmrelayx relay listener server classes from the package namespace. Importing it makes the configured server types available to the main ntlmrelayx orchestration code.

## Important APIs, Types, and Functions
The file imports `HTTPRelayServer`, `SMBRelayServer`, `WCFRelayServer`, `RAWRelayServer`, `RPCRelayServer`, `WinRMRelayServer`, `WinRMSRelayServer`, `RDPRelayServer`, and `MSSQLRelayServer`. It defines no classes or functions itself.

## Control Flow
Control flow is import-time only. Python resolves each server module and binds the class names into `impacket.examples.ntlmrelayx.servers`.

## State and Persistence Behavior
There is no runtime state beyond module imports and no persistence. Import failures in any listed server module can prevent the package from loading.

## Dependencies and Integration Points
This file couples the package namespace to all listed server implementations. It is an integration point for command-line server startup code that imports from `servers` rather than individual modules.

## Risks and Edge Cases
Eager imports mean optional dependencies of less common listeners, such as RDP TLS or MSSQL certificate generation dependencies, can affect package import if not handled in their modules. There is no `__all__`, so exported names are implicit.

## Test Signals
Test importing the package in environments with all server dependencies installed and with common listener selections. Static checks should catch stale class names when adding or removing server modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/httprelayserver.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/httprelayserver.py

## Purpose
`httprelayserver.py` implements the HTTP listener side of ntlmrelayx. It accepts browser/WebDAV/proxy NTLM authentication, relays it to configured protocol clients, supports multirelay redirection, serves WPAD/image responses, and dispatches attacks or SOCKS sessions after success.

## Important APIs, Types, and Functions
`HTTPRelayServer` is a thread wrapper around nested `HTTPServer` and `HTTPHandler`. The handler implements HTTP verbs, `strip_blob()`, `do_local_auth()`, `do_relay()`, `do_ntlm_negotiate()`, `do_ntlm_auth()`, `do_attack()`, WPAD/image helpers, redirects, and error responses.

## Control Flow
Requests flow through `do_GET()`, `do_POST()`, `do_CONNECT()`, or WebDAV `do_PROPFIND()`. The handler extracts NTLM from Authorization or Proxy-Authorization headers. In multirelay mode it first performs local auth to identify the user, selects a target for that identity, and redirects the client to force a new auth. Relay mode initializes the protocol client, forwards type 1, sends the target challenge to the HTTP client, forwards type 3, records John-the-Ripper hash material, registers target status, then starts an attack thread or queues a SOCKS connection.

## State and Persistence Behavior
Per-request state includes `target`, `client`, `challengeMessage`, `authUser`, and `relayToHost`. Server state includes config and `wpad_counters`. It may write hash output through `writeJohnOutputToFile`; otherwise it queues live sessions into `activeConnections`.

## Dependencies and Integration Points
It depends on `http.server`, `socketserver`, Impacket NTLM, SMB hash-output helpers, `TargetsProcessor`, `activeConnections`, configured protocol clients, attacks, and SOCKS server capabilities.

## Risks and Edge Cases
Header parsing is NTLM-only and assumes base64 tokens. Multirelay relies on browser redirect/retry behavior. `send_error()` checks `message.find('RPC_IN')` without comparing to `>= 0`, which is always truthy for `-1`. WPAD counters control when PAC files are served and can be sensitive to client retry behavior.

## Test Signals
Test direct, proxy, CONNECT, WebDAV PROPFIND, WPAD, redirect mode, disableMulti mode, target exhaustion, remove_target AV-pair stripping, hash dump output, SOCKS queuing, and attack fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/httprelayserver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/mssqlrelayserver.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/mssqlrelayserver.py

## Purpose
`mssqlrelayserver.py` implements a fake MSSQL/TDS listener that captures SQL Server integrated-auth NTLM and relays it to configured ntlmrelayx targets. It supports classic TDS pre-login/login flows and TDS 8.0 TLS-from-start detection.

## Important APIs, Types, and Functions
`MSSQLRelayServer` wraps nested `MSSQLServer` and `MSSQLHandler`. The server builds a self-signed TLS context for TDS 8.0. The handler provides packet reassembly helpers, `sendNegotiate()`, `sendLoginFailed()`, `handle()`, and `do_attack()`.

## Control Flow
The handler chooses a target at connection start and parses target netloc. `handle()` peeks for TLS, wraps the socket when needed, then reassembles TDS messages. On pre-login it initializes the relay client and responds with encryption settings. On LOGIN7 it parses client login fields, rejects non-SSPI SQL auth, optionally overrides MSSQL target negotiation to preserve login/database semantics, relays type 1, and returns a TDS SSPI challenge token. On TDS SSPI it sends a local login failure to the client, relays type 3, logs success/failure, saves hash output, registers the target, and dispatches attack/SOCKS.

## State and Persistence Behavior
State includes selected target, `login` data, `tds8_mode`, `challengeMessage`, relay client, auth user, generated TLS context, and optional hash output file writes. Temporary cert/key material is written to a temp file then unlinked after loading.

## Dependencies and Integration Points
It depends on Impacket `tds`, NTLM, target parsing, active SOCKS connections, configured protocol clients/attacks, and `cryptography` for certificate creation.

## Risks and Edge Cases
TDS packet reassembly and TLS boundaries are easy to mishandle. Self-signed cert generation requires `cryptography`. SQL password logins are logged and rejected rather than relayed. The code sends login failed before processing relay success, which is intentional for capture flow but visible to clients.

## Test Signals
Cover TDS 7.x pre-login, TDS 8.0 TLS, fragmented packets, LOGIN7 with and without SSPI, database override, MSSQL-to-MSSQL relay, auth success/failure, hash output, and SOCKS/attack dispatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/mssqlrelayserver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/rawrelayserver.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/rawrelayserver.py

## Purpose
`rawrelayserver.py` provides a minimal length-prefixed NTLM relay listener for third-party integrations. It accepts raw NTLM type 1/type 3 blobs over TCP and bridges them into ntlmrelayx protocol clients and attacks.

## Important APIs, Types, and Functions
`RAWRelayServer` wraps nested `RAWServer` and `RAWHandler`. The handler implements `handle()`, `do_ntlm_negotiate()`, `do_ntlm_auth()`, and `do_attack()`.

## Control Flow
On connection, the handler creates a reflection target if none is configured, selects a target, then reads a two-byte signed length and NTLM negotiate blob. It initializes the target protocol client, forwards type 1, optionally removes target NetBIOS AV pair, sends the raw challenge back with a length prefix, reads type 3, relays auth, sends a one-byte boolean success result, records John hash output, registers target success, and starts SOCKS or attack handling.

## State and Persistence Behavior
Per-connection state includes selected target, relay client, challenge, and auth user. Successful relays may write hash output and enqueue `activeConnections`. There is no protocol-level session persistence beyond the live socket/client.

## Dependencies and Integration Points
It depends on `socketserver`, Impacket NTLM, SMB hash-output helpers, `TargetsProcessor`, configured protocol clients/attacks, and SOCKS active connection queue.

## Risks and Edge Cases
The two-byte signed length limits token size and lacks robust partial-read handling. There is no authentication or framing beyond simple lengths, so callers must be trusted. Anonymous auth is rejected except localhost-target special handling.

## Test Signals
Test valid type1/type3 exchanges, fragmented raw reads, target exhaustion, reflection target creation, remove_target AV stripping, anonymous rejection, hash output, and SOCKS/attack dispatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/rawrelayserver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/rdprelayserver.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/rdprelayserver.py

## Purpose
`rdprelayserver.py` implements an RDP listener that relays CredSSP/NLA NTLM authentication to ntlmrelayx targets. It emulates enough X.224/RDP negotiation, TLS, and TSRequest wrapping to extract and respond to NTLMSSP tokens.

## Important APIs, Types, and Functions
`RDPRelayServer` defines TPKT/TPDU/RDP negotiation structures and constants. Nested `RDPHandler` implements `handle()`, `handle_credssp()`, `find_ntlmssp_in_data()`, `build_rdp_neg_response()`, `build_tsrequest_challenge()`, and `do_attack()`.

## Control Flow
`handle()` validates the initial TPKT connection request, strips optional cookie data, requires PROTOCOL_HYBRID, sends a hybrid negotiation response, and calls `handle_credssp()`. That method generates a self-signed certificate, completes TLS with the client, scans received TLS data for `NTLMSSP\0`, relays type 1 to a selected target, wraps the target challenge in a minimal ASN.1 TSRequest, then relays type 3. Success registers the target and dispatches SOCKS or attack modules.

## State and Persistence Behavior
Per-connection state includes target, auth user, TLS connection, relay client, and challenge bytes. Certificate/key files are generated by `generate_self_signed_cert()`. Hash output is written only when `outputFile` is configured.

## Dependencies and Integration Points
It depends on PyOpenSSL, Impacket NTLM, `Structure`, RDP SSL utilities, SOCKS active connections, target processing, and configured protocol clients/attacks.

## Risks and Edge Cases
CredSSP ASN.1 handling is minimal and searches raw TLS payloads for NTLM rather than fully parsing TSRequest. TLS handshake timeout is long. Generated certificate cleanup depends on helper behavior. Only NLA-capable clients are supported.

## Test Signals
Test RDP negotiation with and without PROTOCOL_HYBRID, cookie stripping, TLS handshake, type1/type3 extraction, ASN.1 TSRequest challenge format, target exhaustion/reload, hash output, and attack/SOCKS dispatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/rdprelayserver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/rpcrelayserver.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/rpcrelayserver.py

## Purpose
`rpcrelayserver.py` implements a DCE/RPC listener that relays incoming RPC NTLM authentication to ntlmrelayx target clients. It also responds to endpoint mapper and IObjectExporter calls enough to keep RPC clients moving through authentication.

## Important APIs, Types, and Functions
`RPCRelayServer` wraps `RPCSocketServer` and `RPCHandler`. The handler uses `DCERPCServer`, callback handlers `handle_epmap()` and `send_ServerAlive2Response()`, request dispatch `handle_single_request()`, NTLM state machine `negotiate_ntlm_session()`, `bind()`, `send_error()`, `do_ntlm_negotiate()`, `do_ntlm_auth()`, and `do_attack()`.

## Control Flow
`setup()` registers EPM and IObjectExporter callbacks and creates reflection targets when needed. `handle()` receives RPC PDUs and delegates. BIND/ALTERCTX with WINNT auth enters NTLM negotiation: type 1 selects a target, initializes a protocol client, forwards negotiate, and returns a bind ack with challenge auth data; type 3 authenticates to the target, records hash material, registers target success, runs attack/SOCKS, and returns access denied to the RPC caller.

## State and Persistence Behavior
Per-connection fields cache request headers, PDU data, security trailers, challenge, target, client, and authenticated user. Successful relays may write hash output and queue active SOCKS sessions.

## Dependencies and Integration Points
It depends on Impacket DCE/RPC runtime, EPM/DCOM structures, NTLM constants, target processor, active SOCKS queue, configured protocol clients, and attack classes.

## Risks and Edge Cases
Only WINNT/default auth is implemented; SPNEGO, Kerberos, Schannel, Netlogon, and challenge-message handling are not. Bind accepts most context items to force authentication and rejects NDR64. It returns access denied after successful relay, which is expected but may affect client retry behavior.

## Test Signals
Test BIND without auth, WINNT type1/type3, unsupported auth types, endpoint mapper reflection, feature-negotiation context items, target reload, successful relay dispatch, and outputFile hash writing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/rpcrelayserver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/smbrelayserver.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/smbrelayserver.py

## Purpose
`smbrelayserver.py` implements the SMB listener side of ntlmrelayx. It hooks Impacket's SMB server to capture SMB1/SMB2 NTLM authentication, relay it to configured targets, and use tree-connect reconnect semantics for multirelay.

## Important APIs, Types, and Functions
`SMBRelayServer` configures an `SMBSERVER` with IPC$, hooks SMB1 and SMB2 negotiate/session-setup/tree-connect commands, and implements `init_client()`, `do_ntlm_negotiate()`, `do_ntlm_auth()`, `do_attack()`, `_start()`, and `run()`. `auth_callback()` logs pre-relay identities in multirelay mode.

## Control Flow
Initialization builds an SMB server config, installs command hooks, and stores a relay connection. In disableMulti mode negotiate immediately selects and initializes a target client. In multirelay mode the original SMB server first authenticates locally; tree connect then selects a target, stores `SMBClient`, clears previous auth state, and returns `STATUS_NETWORK_SESSION_EXPIRED` so the client reauthenticates. Session setup unwraps SPNEGO/raw NTLM, forwards type 1 to the target, returns the challenge, forwards type 3, logs success/failure, records hash output, registers target status, then dispatches SOCKS or an attack thread.

## State and Persistence Behavior
State is stored both on the server object (`target`, `targetprocessor`, `authUser`) and Impacket connection data (`SMBClient`, `NEGOTIATE_MESSAGE`, `CHALLENGE_MESSAGE`, `AUTHENTICATE_MESSAGE`, `relayToHost`, `Authenticated`, `EncryptionKey`, `Uid`). Hash output may be written through SMB server config.

## Dependencies and Integration Points
It depends on Impacket SMB/SMB3/SMBSERVER, SPNEGO, target processing, SOCKS active connections, configured protocol clients/attacks, and ntlmrelayx options for SMB2, reflection, disableMulti, keepRelaying, ADCS, dump hashes, and output files.

## Risks and Edge Cases
This file is highly stateful and mutates per-connection dictionaries. Fixed SMB1 UID `10`, reconnect loops, SPNEGO/raw token differences, signing, reflection downgrades, and target exhaustion are fragile areas. Exceptions inside hooks can terminate client sessions abruptly.

## Test Signals
Cover SMB1 extended and standard security, SMB2 negotiation/session setup/tree connect, disableMulti vs multirelay, reflection mode, target reload, raw NTLM and SPNEGO, STATUS_NETWORK_SESSION_EXPIRED loops, hash output, SOCKS queuing, and attack dispatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/smbrelayserver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/__init__.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/__init__.py

## Purpose
`socksplugins/__init__.py` dynamically discovers and registers SOCKS relay plugins for ntlmrelayx. It imports each plugin module in the package and collects its declared plugin class in `SOCKS_RELAYS`.

## Important APIs, Types, and Functions
The only public object is `SOCKS_RELAYS`, a set of plugin classes. Import-time code uses `importlib.resources.files()` to enumerate package files, imports each non-dunder `.py` module, reads its `PLUGIN_CLASS` global, resolves that class from the module, and adds it to the set.

## Control Flow
On package import, the directory `impacket.examples.ntlmrelayx.servers.socksplugins` is scanned. Files containing `__` or not ending in `.py` are skipped. The package name is taken from `__spec__.name` with a Python 2 fallback to `__package__`, then modules are imported one by one.

## State and Persistence Behavior
State is limited to the in-memory `SOCKS_RELAYS` set and normal `sys.modules` imports. No files are written.

## Dependencies and Integration Points
It depends on `importlib.resources`, `os`, and `sys`. The SOCKS server uses `SOCKS_RELAYS` to know which protocol plugins are supported.

## Risks and Edge Cases
Discovery is eager: importing one broken plugin can fail the whole package. Plugins must define `PLUGIN_CLASS` and the named class. Set ordering is nondeterministic, so consumers should not depend on registration order.

## Test Signals
Test package import, plugin addition/removal, modules without `PLUGIN_CLASS`, Python packaging from filesystem and zip/importlib resources, and duplicate class handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/http.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/http.py

## Purpose
`socksplugins/http.py` implements the HTTP SOCKS relay plugin. It lets a SOCKS client reuse a previously relayed HTTP session by authenticating to the local proxy with Basic credentials matching an active relay identity.

## Important APIs, Types, and Functions
`HTTPSocksRelay` extends `SocksRelay` and defines `PLUGIN_NAME`, `PLUGIN_SCHEME`, `getProtocolPort()`, `skipAuthentication()`, `getHeaders()`, `prepareRequest()`, `transferResponse()`, `transferChunked()`, and `tunnelConnection()`. `PLUGIN_CLASS` names the exported plugin class.

## Control Flow
`skipAuthentication()` reads the first HTTP request from the SOCKS socket, parses headers, requires `Authorization: Basic`, normalizes usernames including `user@fqdn` into `DOMAIN/user`, locates a matching idle active relay, binds `self.session` and `relaySocket` to the HTTPConnection socket, forwards the sanitized request, and relays the response. `tunnelConnection()` repeats request sanitization and response transfer for subsequent requests.

## State and Persistence Behavior
The plugin tracks `username`, `session`, `relaySocket`, and `packetSize`. It consumes active relay entries supplied by the SOCKS server but does not persist data. It rewrites Authorization and Connection headers in forwarded requests.

## Dependencies and Integration Points
It depends on `SocksRelay`, Impacket logging, and `activeRelays` entries containing `protocolClient.session`. It integrates directly with `HTTPRelayClient` sessions.

## Risks and Edge Cases
HTTP parsing is simple byte splitting and assumes complete headers in one recv. In `prepareRequest()`, comparing `part == ''` mixes bytes and str and may miss header termination. Chunked transfer parsing assumes chunk-size lines arrive cleanly.

## Test Signals
Test Basic auth prompt, username normalization, missing/active/in-use sessions, request body forwarding with Content-Length, connection header rewriting, no-body responses, content-length responses, chunked responses, and repeated tunnel requests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/http.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/https.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/https.py

## Purpose
`socksplugins/https.py` implements HTTPS SOCKS relay support by layering TLS server behavior over the HTTP SOCKS relay plugin. It lets local SOCKS users proxy HTTPS requests through relayed HTTPS target sessions.

## Important APIs, Types, and Functions
`HTTPSSocksRelay` subclasses `SSLServerMixin` and `HTTPSocksRelay`, sets `PLUGIN_NAME` to `HTTPS Socks Plugin`, `PLUGIN_SCHEME` to `HTTPS`, and overrides `getProtocolPort()` to return 443. It inherits authentication, request rewriting, response transfer, and tunneling from `HTTPSocksRelay`.

## Control Flow
Initialization calls `HTTPSocksRelay.__init__()` and creates an OpenSSL context through `SSLServerMixin`. The SOCKS server wraps client-side traffic in TLS, then the inherited HTTP plugin logic processes Basic auth, selects an active HTTPS relay, forwards sanitized HTTP requests over the already-authenticated target session, and relays responses.

## State and Persistence Behavior
State is inherited from `HTTPSocksRelay` plus TLS context/session state from `SSLServerMixin`. No files are written directly in this module; certificate behavior is delegated to the SSL utility mixin.

## Dependencies and Integration Points
It depends on OpenSSL, Impacket logging, `HTTPSocksRelay`, and `impacket.examples.ntlmrelayx.utils.ssl.SSLServerMixin`. Active relay entries are expected to come from HTTPS target clients.

## Risks and Edge Cases
TLS behavior depends entirely on the mixin and client trust of the generated certificate. HTTP parsing risks are inherited from `http.py`. The module imports `LOG` but does not use it, indicating minimal local logic.

## Test Signals
Test plugin discovery, default port 443, TLS handshake with SOCKS clients, Basic auth session selection, inherited content-length/chunked forwarding, certificate generation/trust failure handling, and HTTPS active relay reuse.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/https.py -->
