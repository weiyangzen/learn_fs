# subset-b-009622 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/imap.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/imap.py

Purpose: implements the IMAP SOCKS plugin used by ntlmrelayx to let a local SOCKS client reuse an already-relayed IMAP session without reauthenticating to the real server. `PLUGIN_CLASS`, `IMAPSocksRelay.PLUGIN_NAME`, and `PLUGIN_SCHEME` are consumed by the socks plugin loader in `socksserver.py`; `getProtocolPort()` binds the plugin to port 143.

Important APIs and control flow: `skipAuthentication()` fakes the server greeting, expects `CAPABILITY`, mirrors the upstream server capabilities while removing GSSAPI/NTLM/login-disabled options, adds PLAIN/LOGIN, extracts the username from `AUTHENTICATE PLAIN` or `LOGIN`, finds `activeRelays[username]`, and attaches `session.sock` plus `session.file`. `tunnelConnection()` reads client commands and delegates to `processTunnelData()`, which forwards commands, tracks tags, handles continuations, blocks `LOGOUT`, supports `IDLE`/`DONE`, and streams IMAP `APPEND` literals.

State and persistence: state is in-memory only: `username`, `session`, `relaySocket`, `relaySocketFile`, `idleState`, `shouldClose`, and the shared `activeRelays` structure. On client disconnect it may send `DONE` and `CLOSE`, then stores the next IMAP tag in `session.tagnum` so the relayed session can remain usable.

Dependencies and integration: depends on `base64`, `impacket.LOG`, and the `SocksRelay` base class. It assumes the protocol client session exposes `capabilities`, `sock`, `file`, and `tagnum`.

Risks and test signals: Python 3 byte/string handling is fragile (`recv()` bytes compared to `''`, `split('\x00')` on decoded bytes assumptions). APPEND parsing assumes a specific argument position. Tests should cover capability rewriting, PLAIN/LOGIN username normalization, in-use relay rejection, LOGOUT suppression, IDLE cleanup, CLOSE behavior, and literal APPEND streaming.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/imap.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/imaps.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/imaps.py

Purpose: implements the TLS-wrapped IMAPS variant of the IMAP SOCKS plugin. It reuses `IMAPSocksRelay` logic but exposes `PLUGIN_CLASS = "IMAPSSocksRelay"`, scheme `IMAPS`, and port 993.

Important APIs and control flow: `IMAPSSocksRelay` inherits `SSLServerMixin` before `IMAPSocksRelay`, so `skipAuthentication()` first wraps the local client-side SOCKS socket in TLS using `wrapClientConnection()`, then calls the parent IMAP authentication bypass. If the parent fails, the TLS socket is shut down. On success it changes `relaySocket` to `session.sslobj`, matching the upstream `imaplib.IMAP4_SSL`-style session object.

State and persistence: it inherits IMAP state (`idleState`, `shouldClose`, session tag tracking, username, relay sockets) and adds no persistent storage. The TLS wrapper replaces `self.socksSocket`, so all later reads and writes operate on a pyOpenSSL `SSL.Connection`.

Dependencies and integration: integrates with `SSLServerMixin`, pyOpenSSL `SSL`, and the base IMAP plugin. It depends on active relay sessions exposing both `file` and `sslobj` fields.

Risks and test signals: the tunnel loop catches only `SSL.ZeroReturnError`; other TLS exceptions propagate to the SOCKS server handler. It duplicates IMAP cleanup logic, so changes to base IMAP tunnel cleanup can diverge. Tests should exercise TLS handshake, failed parent authentication shutdown, use of `session.sslobj`, IDLE/CLOSE cleanup under TLS, and client close behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/imaps.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/ldap.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/ldap.py

Purpose: implements LDAP SOCKS relay reuse for ntlmrelayx. It fakes the client-side LDAP NTLM bind sequence, maps the authenticating identity to a stored relayed LDAP session, and then passes allowed LDAP traffic between the SOCKS client and the real server.

Important APIs and control flow: `skipAuthentication()` loops over BER-decoded LDAP messages from `recv_ldap_msg()`. It answers anonymous/empty bind with success and matched DN `NTLM`, answers `sicilyNegotiate` with the saved `CHALLENGE_MESSAGE` after clearing NTLM sign/seal, and handles `sicilyResponse` by parsing `NTLMAuthChallengeResponse`, normalizing `DOMAIN/user`, looking up `activeRelays`, marking it in use, and sending a success `BindResponse`. Pre-auth `SearchRequest` for `supportedCapabilities` and `supportedSASLMechanisms` receives handcrafted AD-like results. `send_ldap_msg()` wraps ASN.1 protocol operations in `LDAPMessage`.

State and persistence: in-memory state includes `username`, `session`, and `activeRelays[username]['inUse']`. `tunnelConnection()` releases `inUse` after `passthrough_sockets()` returns. No disk persistence is used.

Dependencies and integration: depends heavily on pyasn1, `impacket.ldap.ldapasn1`, `impacket.ntlm`, and the `SocksRelay` contract. It integrates with LDAP protocol clients that store `session.socket` and NTLM challenge data in session data.

Risks and test signals: `recv_ldap_msg()` uses packet-size-short-read as a message boundary heuristic, which can mishandle exact-size or delayed frames. Shared `activeRelays` mutation is unsynchronized. `is_allowed_request()` blocks StartTLS, and `is_forwardable_request()` drops Unbind to preserve the relay. Tests should cover multi-message BER decoding, supportedCapabilities/SASL preauth searches, domain normalization fallback, in-use rejection, StartTLS closure, Unbind suppression, and relay release on tunnel exit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/ldap.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/ldaps.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/ldaps.py

Purpose: provides the LDAPS SOCKS plugin, exposing LDAP relay reuse over a TLS-wrapped client-side SOCKS connection. It inherits LDAP behavior and registers scheme `LDAPS` on port 636.

Important APIs and control flow: `skipAuthentication()` wraps `self.socksSocket` through `SSLServerMixin.wrapClientConnection()`, then delegates to `LDAPSocksRelay.skipAuthentication()` for the LDAP NTLM bind spoofing. On failure it shuts down the TLS socket; on `SSL.SysCallError` it logs and rejects the SOCKS connection. `wait_for_data()` overrides LDAP polling to first check pyOpenSSL pending buffers on both sockets before falling back to `select.select()`.

State and persistence: no disk persistence. It inherits LDAP in-memory state: username, selected relay session, and `activeRelays` in-use flags. TLS state is embedded in pyOpenSSL connection objects replacing the plain socket.

Dependencies and integration: depends on `select`, pyOpenSSL, `SSLServerMixin`, and `LDAPSocksRelay`. The class integrates with `socksserver.py` through the `PLUGIN_CLASS` and `PLUGIN_SCHEME` metadata and with LDAPS protocol clients that have already established a relayed authenticated LDAP socket.

Risks and test signals: `wait_for_data()` assumes both socket objects expose `pending()`, which is true for pyOpenSSL but not normal sockets. Error handling covers only a narrow TLS exception. Tests should verify TLS wrapping, LDAP parent bind behavior, pending-buffer forwarding, StartTLS blocking still effective through LDAPS, and cleanup of `inUse` when the tunnel exits or the TLS peer closes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/ldaps.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/mssql.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/mssql.py

Purpose: implements MSSQL/TDS SOCKS relay reuse on port 1433. It accepts a local SQL client, fakes enough prelogin/login/NTLM flow to bind the client identity to an existing relayed MSSQL session, then forwards TDS packets.

Important APIs and control flow: `skipAuthentication()` optionally detects TDS 8.0 TLS, receives a prelogin packet, returns a `TDS_PRELOGIN` response with encryption based on backend requirements, receives `TDS_LOGIN7`, parses integrated security or SQL username, maps the username into `activeRelays`, loads per-user session data, and sends the saved auth answer. `_backend_requires_tds8()`, `_get_prelogin_encryption()`, `_wrap_client_connection_for_tds8()`, and `_should_wrap_sql_batch_for_backend()` handle strict encryption and SQL batch header adaptation. `tunnelConnection()` loops client `recvTDS()`, sends via the relayed session, receives response, and sends it back.

State and persistence: stores `isSSL`, `tlsSocket`, `client_tds8`, `_recv_buffer`, selected `session`, and inherited username/session data. It generates or reuses a temporary PEM for local TLS but maintains no long-term application state.

Dependencies and integration: depends on `impacket.tds`, `NTLMAuthChallengeResponse`, Python `ssl`, pyOpenSSL, and `generateImpacketCert()`. It integrates with MSSQL protocol clients exposing `session`, `sendTDS()`, `recvTDS()`, `tds8`, and `_wrap_sql_batch_data()`.

Risks and test signals: packet fragmentation logic is central; off-by-one packet length errors would corrupt TDS streams. TLS code has legacy `tlsSocket` paths plus newer `ssl.SSLContext` wrapping. Tests should cover prelogin encryption choices, integrated and SQL auth username parsing, active relay selection, fragmented send/receive, EOF handling, TDS8 TLS detection, and SQL batch wrapping for strict backends.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/mssql.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/smb.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/smb.py

Purpose: implements SMB SOCKS relay reuse for both SMB1 and SMB2+. It performs a fake negotiation and NTLM session setup with the local SOCKS client, then binds traffic to an existing relayed SMB session while suppressing logoff.

Important APIs and control flow: `initConnection()` wraps the accepted SOCKS socket in `NetBIOSTCPSession`. `skipAuthentication()` reads SMB1/SMB2 negotiate and session setup packets. `getNegoAnswer()` fabricates SMB1 or SMB2 negotiate responses with NTLMSSP SPNEGO support and dialect details inferred from existing relays. `processSessionSetup()` performs the two-step NTLM challenge/authenticate exchange, parses SPNEGO or raw NTLM tokens, maps `DOMAIN/user` into `activeRelays`, and returns the relayed SMB client plus username. `tunnelConnection()` forwards packets, strips SMB2 signing, ensures fake tree-connect state exists, preserves original SMB2 message IDs, and returns local success for logoff via `getLogOffAnswer()`.

State and persistence: in-memory only: NetBIOS session, `isSMB2`, `serverDialect`, `clientConnection`, and inherited username/session data. It uses the relayed SMB client's internal server/session fields directly.

Dependencies and integration: integrates with `socksserver.py`, `NetBIOSTCPSession`, many `impacket.smb`/`smb3` structures, SPNEGO helpers, NT status codes, and NTLM parsing.

Risks and test signals: this file reaches into private SMB server fields (`_sess`, `_Session`) and mutates packet signing flags, making it sensitive to Impacket internals. SMB1 transaction draining relies on a timeout heuristic. Tests should cover SMB1 extended security, SMB2 negotiate/session setup with SPNEGO and raw NTLM, unsupported mech response, relay miss/access denied, logoff suppression, signing flag stripping, message ID preservation, and SMB1 transaction multi-response handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/smb.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/smtp.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/smtp.py

Purpose: implements SMTP SOCKS relay reuse on port 25. It presents a local SMTP service to a SOCKS client, steers the client toward PLAIN/LOGIN auth to learn the username, then tunnels commands through an existing relayed SMTP session.

Important APIs and control flow: `skipAuthentication()` sends a Microsoft-style `220` banner, expects `EHLO`, mirrors upstream EHLO capabilities from `getServerEhlo()` while removing NTLM/GSSAPI/STARTTLS, adds `AUTH PLAIN` and `AUTH LOGIN`, and extracts the username from `AUTH LOGIN` or `AUTH PLAIN`. It then checks `activeRelays`, rejects in-use sessions, attaches `session.sock` and `session.file`, and returns SMTP `235`. `tunnelConnection()` forwards commands/responses, locally handles `QUIT`, and has a DATA mode loop that forwards message content until CRLF-dot-CRLF.

State and persistence: no persistent storage. State consists of `packetSize`, selected `username`, selected upstream `session`, and relay socket/file handles. `activeRelays` is shared with the SOCKS server and keepalive path.

Dependencies and integration: depends on `base64`, `impacket.LOG`, and `SocksRelay`. It assumes SMTP protocol clients expose `session.ehlo_resp`, `sock`, and `file`.

Risks and test signals: Python 3 byte/string assumptions are visible in socket `send()` calls and base64 split handling. DATA termination tracking compares trailing bytes/strings and may be confused by fragmentation or binary content. Tests should cover EHLO capability rewriting, AUTH LOGIN and PLAIN extraction, relay miss/in-use paths, QUIT suppression, DATA fragmentation around the terminator, and STARTTLS omission.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/smtp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksserver.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksserver.py

Purpose: provides the ntlmrelayx SOCKS server and plugin host. It accepts SOCKS4/SOCKS5 client connections, routes them to protocol-specific relay plugins backed by active relayed sessions, keeps idle relays alive, and exposes a small Flask API listing available relays.

Important APIs and control flow: `SocksRelay` is the abstract plugin base. `SOCKS` registers classes from `socksplugins.SOCKS_RELAYS`, starts `RepeatedTimer(keepAliveTimer)`, a REST API thread, and `activeConnectionsWatcher`. `activeConnectionsWatcher()` consumes `(target, port, scheme, user, client, data)` tuples from the global queue and populates `activeRelays[target][port]` with protocol clients, session data, scheme, `inUse`, and optional `isAdmin`. `SocksRequestHandler.handle()` parses SOCKS greeting/request, validates an active relay for target/port, directly proxies DNS port 53, instantiates the right plugin, sends a success reply, calls `initConnection()`, `skipAuthentication()`, sets `inUse`, tunnels, and releases `inUse` in `finally`.

State and persistence: all runtime state is in memory: `activeRelays`, plugin registry, global `activeConnections` queue, timer, REST thread, and watcher thread. No durable storage exists.

Dependencies and integration: depends on `socketserver`, `impacket.structure.Structure`, enum support, protocol plugins, Flask for the API, and relay servers that enqueue successful sessions.

Risks and test signals: `activeRelays` is mutated across handler, timer, and watcher threads without locks. Some SOCKS4 byte/string comparisons appear Python-version-sensitive. REST route duplication defines two identical relay routes. Tests should cover SOCKS4/5 parsing, domain/IPv4 requests, relay missing errors, plugin dispatch, DNS passthrough, in-use release after exceptions, keepalive removal on broken sessions, active connection registration, and REST relay listing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksserver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/wcfrelayserver.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/wcfrelayserver.py

Purpose: implements a WCF/ADWS NetTcpBinding relay frontend. It parses .NET Message Framing and NegotiateStream records, relays NTLM negotiate/authenticate messages to a selected target protocol client, then either enqueues the resulting session for SOCKS or launches a configured attack.

Important APIs and control flow: `WCFRelayServer.WCFServer` is a threaded TCP server with IPv4/IPv6 binding via `get_address()`. `WCFHandler.handle()` validates Version, Mode, Via, KnownEncoding, and Upgrade records, requires `net.tcp://` and `application/negotiate`, then reads NegotiateStream handshake records. It unwraps SPNEGO or raw NTLM, calls `do_ntlm_negotiate()` to initialize the target protocol client and get a challenge, sends the challenge back, receives NTLM authenticate, calls `do_ntlm_auth()`, logs and writes John hash material, registers target outcome, and calls `do_attack()`.

State and persistence: per-connection handler state includes selected target, protocol client, challenge message, auth user, and machine-account fields. Persistent side effects are optional hash output via `writeJohnOutputToFile()` and target progress stored in `TargetsProcessor`.

Dependencies and integration: integrates with `TargetsProcessor`, protocol client classes in config, `activeConnections` for SOCKS, configured attack classes, NTLM/SPNEGO helpers, and SMB server hash formatting utilities.

Risks and test signals: `recvall()` can loop forever if the peer closes before enough bytes arrive because it does not break on empty reads. The parser supports only NetTcpBinding Negotiate. Tests should cover framing validation failures, SPNEGO unsupported mech negotiation, raw NTLM path, target exhaustion, remove-target AV pair handling, successful SOCKS enqueue, classic attack dispatch, hash output, and failed negotiate/auth target registration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/wcfrelayserver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/winrmrelayserver.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/winrmrelayserver.py

Purpose: implements the HTTP WinRM relay frontend on port 5985 by default. It handles `/wsman` NTLM/Negotiate authentication, WebDAV-style methods used for coercion, multirelay redirects, optional WPAD/image responses, and dispatches successful relays to SOCKS or attack modules.

Important APIs and control flow: `WinRMRelayServer.HTTPServer` is a threaded TCP server. `HTTPHandler` overrides HTTP verbs. `do_GETPOST()` only relays POSTs to `/wsman`; other paths get 404 plus Negotiate. `strip_blob()` extracts NTLM tokens from `Authorization` or `Proxy-Authorization`. `do_local_auth()` performs the multirelay capture step with a local challenge, stores `authUser`, chooses a target for that identity, and redirects. `do_relay()` handles NTLM type 1 by selecting/initializing a protocol client and returning the real challenge, and type 3 by sending auth to the target, writing John-format hashes, then calling `do_attack()` and either redirecting to another target or returning terminal responses.

State and persistence: per-handler state tracks challenge, target, client, auth user, relay mode, and negotiation count. Server-level state has WPAD counters. Persistent side effects are optional output-file hash writes and target processor bookkeeping.

Dependencies and integration: depends on Python `http.server`, Impacket NTLM, `TargetsProcessor`, `activeConnections`, configured protocol clients, configured attacks, and `get_address()`.

Risks and test signals: `send_error()` uses `message.find('RPC_IN')` truthily, likely matching unexpectedly when `find()` returns `-1`. Token parsing assumes NTLMSSP layout once a header is present. Tests should cover unauthenticated WSMANIDENTIFY, `/wsman` POST body drain, proxy CONNECT, multirelay local auth and redirect, disableMulti behavior, negotiation count rejection, failed target rotation, SOCKS enqueue, hash output, PROPFIND multi-status, and serve-image fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/winrmrelayserver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/winrmsrelayserver.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/winrmsrelayserver.py

Purpose: implements the HTTPS WinRM relay frontend on port 5986 by default. It mirrors the HTTP WinRM relay behavior but wraps the listening server socket in a generated self-signed TLS certificate.

Important APIs and control flow: `WinRMSRelayServer.HTTPServer` creates an RSA key/certificate with CN `localhost`, writes them to temporary files, builds an `ssl.SSLContext`, and wraps the server socket. `HTTPHandler` is structurally parallel to the HTTP version: it handles `/wsman` POSTs, `PROPFIND`, `CONNECT`, auth header parsing, local multirelay auth, real target negotiate/auth, John hash output, SOCKS enqueue or attack dispatch, and target rotation through redirects.

State and persistence: server state includes the SSL context and WPAD counters. Temporary certificate and key files are created with `delete=False` and are not cleaned up by this module. Per-connection relay state includes challenge, target, protocol client, auth user, relay mode, and negotiation count. Optional persistent hash output uses the configured output file.

Dependencies and integration: depends on Python `ssl`, pyOpenSSL `crypto` for cert generation, `http.server`, Impacket NTLM and hash helpers, `TargetsProcessor`, `activeConnections`, protocol clients, and configured attacks.

Risks and test signals: temporary cert/key file leakage is likely over repeated starts. HTTPS version differs subtly from HTTP in auth headers (`NTLM` challenge returned for real negotiate while local auth may use `Negotiate`). `send_error()` shares the truthiness issue around `.find('RPC_IN')`. Tests should cover TLS server startup, certificate generation, `/wsman` routing, auth token parsing, multirelay redirect, disableMulti terminal responses, failed auth target cycling, SOCKS enqueue, classic attack dispatch, hash output, and temp file lifecycle expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/winrmsrelayserver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/__init__.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/__init__.py

Purpose: package marker for `impacket.examples.ntlmrelayx.utils`. It contains only the project header and `pass`, so it exposes no runtime APIs beyond making the directory importable as a Python package.

Important APIs and control flow: no functions, classes, constants, imports, or side effects are defined. Importing this module is a no-op.

State and persistence: no state, no persistence, and no I/O.

Dependencies and integration: its integration role is structural: modules such as `config`, `targetsutils`, `ssl`, `rdp_ssl`, `shadow_credentials`, `identity_log`, `enum`, and `tcpshell` live under this package and are imported directly by relay servers and attacks.

Risks and test signals: risk is minimal. Tests only need package import coverage if packaging or namespace behavior changes. A useful signal is that `import impacket.examples.ntlmrelayx.utils` succeeds without side effects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/config.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/config.py

Purpose: central mutable configuration object for ntlmrelayx servers, clients, and attacks. `NTLMRelayxConfig` stores command-line-derived options and exposes setter methods used by the main tool setup code. `parse_listening_ports()` parses comma-separated ports and ranges.

Important APIs and control flow: `__init__()` initializes defaults for interface/listening settings, target handling, SOCKS, SMB/RPC/LDAP/MSSQL/HTTP/WebDAV/AD CS/Shadow Credentials/SCCM attack options, protocol client registry, and attack registry. Most setters directly assign corresponding attributes. `setDomainAccount()` enforces that machine account, hashes, and domain IP are supplied together and only applies when `remove_target` is enabled. `setRPCOptions()` parses SMB credentials and LM/NT hashes. `setLDAPOptions()` and other attack setters store multiple related knobs at once. `parse_listening_ports()` accepts entries like `80,443,8000-8010` and returns a set of integers.

State and persistence: all state is in-memory and intentionally mutable. No disk I/O occurs. The config object is passed by reference to servers, protocol clients, and attacks.

Dependencies and integration: imports `parse_credentials` from Impacket examples utilities. It is the integration hub between CLI parsing, relay servers, protocol client factories, attack factories, SOCKS server, and target processors.

Risks and test signals: many attributes are created only by setters, so consumers can hit missing attributes if setup paths diverge. `parse_listening_ports()` does not enforce numeric range 1-65535 or reject duplicates beyond set collapse. Tests should cover default values, each multi-option setter, domain account validation, hash splitting, WPAD enablement, exploit flags, and valid/invalid port lists including reversed ranges.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/config.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/enum.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/enum.py

Purpose: provides `EnumLocalAdmins`, a helper for enumerating local Administrators group membership over an existing SMB connection after relay.

Important APIs and control flow: the constructor stores the SMB connection and fixed named-pipe bindings for SAMR and LSARPC. `getLocalAdmins()` calls private `__getLocalAdminSids()` and `__resolveSids()`. `__getDceBinding()` builds a DCE/RPC transport and attaches the existing SMB connection. `__getLocalAdminSids()` binds SAMR, opens the Builtin domain, opens alias RID 544, and returns member SIDs. `__resolveSids()` binds LSAT/LSAD, opens policy, looks up SIDs, and formats `DOMAIN\Name` strings.

State and persistence: only stores the supplied SMB connection and binding strings. No persistent storage; network RPC calls are the side effect.

Dependencies and integration: depends on Impacket DCE/RPC transport, SAMR, LSAT, LSAD, and `MAXIMUM_ALLOWED`. It integrates with relay attack logic that wants to determine whether the relayed identity has local admin rights.

Risks and test signals: private methods do not use `try/finally`, so exceptions can leave DCE connections open. Alias RID 544 assumes the standard Administrators alias. SID resolution assumes all returned names have valid domain indexes. Tests should mock DCE transports to verify bind/open call order, returned SID formatting, name formatting, disconnect behavior on success, and exception behavior for access denied or unknown SIDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/enum.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/identity_log.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/identity_log.py

Purpose: provides thread-local identity tagging for log records. It lets ntlmrelayx code add an identity prefix to log formatting without passing identity through every logging call.

Important APIs and control flow: `_get_identity()` reads `_tlocal.identity` if set. `set_identity(identity)` updates the current thread's identity. `identity_context(identity)` is a context manager that saves the previous identity, sets a new one for the block, and restores the previous value in `finally`, supporting nested usage. `IdentityFilter.filter()` injects `record.identity` as either `"<identity> -> "` or an empty string and always returns `True`.

State and persistence: state is thread-local memory only. No disk or network side effects. Context restoration is explicit and exception-safe.

Dependencies and integration: depends on `logging`, `threading.local`, and `contextlib.contextmanager`. It integrates with logging configuration that includes `%(identity)s` in format strings and installs `IdentityFilter` on handlers or loggers.

Risks and test signals: identity is thread-local, so async tasks or worker pools that change threads will not inherit it automatically. Any formatter expecting `identity` needs the filter installed on all relevant records. Tests should cover default empty identity, set/read behavior, nested `identity_context()` restoration after normal return and exception, per-thread isolation, and `LogRecord` enrichment.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/identity_log.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/rdp_ssl.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/rdp_ssl.py

Purpose: supplies TLS helpers for the RDP relay server: loading a server TLS context from PEM files and generating temporary self-signed certificate/key pairs.

Important APIs and control flow: `ServerTLSContext.__init__()` stores private key and certificate paths. `getContext()` creates a pyOpenSSL `SSL.Context` with `SSLv23_METHOD`, sets RDP compatibility and protocol-disable options, loads certificate and private key from disk, and installs them into the context. `generate_self_signed_cert()` creates a 2048-bit RSA key, a self-signed X.509 certificate with configurable CN, one-year validity, SHA256 signature, writes cert and key to `NamedTemporaryFile(delete=False)` paths, and returns `(key_file.name, cert_file.name)`.

State and persistence: `ServerTLSContext` stores file names. `generate_self_signed_cert()` persists temporary certificate and key files and leaves cleanup to callers.

Dependencies and integration: depends on pyOpenSSL `SSL`/`crypto`, `random`, and `tempfile`. It is intended for RDP relay code that needs a pyOpenSSL server context compatible with RDP TLS negotiation.

Risks and test signals: temporary file leakage is possible. `SSLv23_METHOD` is a compatibility method with security controlled by options; future pyOpenSSL changes may alter behavior. Tests should verify generated files exist and load, CN assignment, context options, certificate/key matching, and caller cleanup policy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/rdp_ssl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/shadow_credentials.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/shadow_credentials.py

Purpose: builds certificates and `msDS-KeyCredentialLink` binary values used by Shadow Credentials attacks, and exports generated credentials in PFX or PEM format.

Important APIs and control flow: `getTicksNow()` returns Windows/.NET ticks since 1601 UTC. `getDeviceId()` returns UUID bytes. `createSelfSignedX509Certificate()` creates a 2048-bit RSA key and ten-year self-signed CA certificate for a subject. `KeyCredential.raw_public_key()` serializes RSA public key material in the expected `RSA1` layout. `KeyCredential.__init__()` prepares key material, usage/source/device/custom info/creation fields and the key identifier. `dumpBinary()` packs version, key identifier, key hash over binary properties, and binary properties. `toDNWithBinary2String()` formats the binary blob as an AD DN-Binary string. `exportPFX()` and `exportPEM()` create output directories and write credential files.

State and persistence: `KeyCredential` keeps private serialized fields in memory. `exportPFX()` writes `.pfx`; `exportPEM()` writes `_cert.pem` and `_priv.pem`. Directory creation is persistent.

Dependencies and integration: uses `cryptography`, PyCryptodome number conversion, hashing/base64/UUID/date utilities, and AD attack code that writes the generated DN-Binary string to LDAP attributes.

Risks and test signals: PFX export requires a non-empty password because it calls `password.encode()`. PEM private keys are unencrypted. Field packing must match Windows expectations exactly. Tests should validate deterministic field structure lengths, ticks range, DN-Binary formatting, exported file names/content, directory creation, and compatibility with LDAP shadow credential consumers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/shadow_credentials.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/ssl.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/ssl.py

Purpose: provides generic SSL helpers for SOCKS plugins that need to present a local TLS server, such as IMAPS and LDAPS, plus certificate generation for those local-only sessions.

Important APIs and control flow: `generateImpacketCert(certname='/tmp/impacket.crt')` creates a 2048-bit RSA key and five-year self-signed X.509 certificate with CN `impacket`, then writes private key and certificate into the same PEM file. `SSLServerMixin.wrapClientConnection()` creates a pyOpenSSL `SSL.Context(TLS_METHOD)`, lowers cipher restrictions with `ALL:@SECLEVEL=0`, loads the configured combined PEM, generates it if missing/invalid, creates an `SSL.Connection` around `self.socksSocket`, sets accept state, and replaces `self.socksSocket`.

State and persistence: certificate generation writes a combined key/cert file to `/tmp/impacket.crt` by default. Mixin state mutation is the socket replacement on the instance.

Dependencies and integration: depends on pyOpenSSL and `impacket.LOG`. It integrates by multiple inheritance into SOCKS relay plugins that already expose `self.socksSocket`.

Risks and test signals: `/tmp/impacket.crt` is shared, predictable, and contains a private key. No certificate subjectAltName or hostname matching is attempted because it is intended for local use. Tests should cover cert generation, fallback when cert load fails, socket replacement with an accept-state `SSL.Connection`, custom cert path support, and concurrent plugin startup using the same default file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/ssl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/targetsutils.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/targetsutils.py

Purpose: manages ntlmrelayx target selection, target exhaustion, identity-specific matching, target-file reloads, and `all://` expansion across protocol clients.

Important APIs and control flow: `TargetsProcessor.__init__()` loads a single target or file, optionally randomizes, then calls `reloadTargets(full_reload=True)`. `processTarget()` defaults bare hosts to SMB, parses URI targets, and expands `ALL...` into one URL per registered protocol. `readTargets()` ignores blank/comment lines and reloads candidates. `reloadTargets()` rebuilds `generalCandidates` and `namedCandidates` excluding finished/failed attacks. `registerTarget()` records finished or failed attempts, converting general targets into identity-qualified URLs when a username is known. `getTarget()` first tries explicit username matches, then identity-specific general targets not already finished/failed, then one-shot behavior for `multiRelay=False`, then reloads remaining candidates. `TargetsFileWatcher` polls the target file mtime once per second and refreshes.

State and persistence: keeps `originalTargets`, `finishedAttacks`, `failedAttacks`, candidate lists, and file mtime in memory. It reads target files but writes no files.

Dependencies and integration: depends on `urlparse`, `random`, `os`, `time`, `Thread`, and `impacket.LOG`. Relay servers call `getTarget()` and `registerTarget()` to coordinate multirelay progress.

Risks and test signals: candidate state is not locked for concurrent handlers. `getTarget()` contains a stray `print(self.failedAttacks)`. URL username/domain comparison is case-normalized inconsistently across backslash/slash forms. Tests should cover bare host defaulting, URI parsing, ALL expansion, file reload, randomization, named identity matching with and without domain, duplicate finished/failed suppression, multiRelay disabled semantics, and watcher refresh.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/targetsutils.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/tcpshell.py -->
# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/tcpshell.py

Purpose: provides a minimal local TCP shell endpoint used by interactive relay attacks. Each `TcpShell` instance listens on localhost and exposes accepted socket file objects as stdin/stdout.

Important APIs and control flow: module-level `port` starts at 11000. `TcpShell.__init__()` assigns the current global port to the instance and increments the global for the next shell. `listen()` creates an IPv4 TCP socket, binds `127.0.0.1:self.port`, calls `listen(0)`, blocks in `accept()`, then creates text-mode file objects with `makefile("r")` and `makefile("w")`. `close()` closes stdout, stdin, and the accepted connection.

State and persistence: state is process-local only: the global port counter plus per-instance socket connection and file handles. No disk persistence.

Dependencies and integration: depends only on Python `socket`. It integrates with attack modules that need an operator-facing interactive channel after successful relay.

Risks and test signals: the listening socket object is local to `listen()` and is not explicitly closed after accept. The global port increment is not thread-safe, and port collisions are possible across processes. `listen(0)` allows no backlog beyond the active accept. Tests should cover sequential port allocation, bind/listen/accept behavior, stdin/stdout file creation, close idempotency expectations, and failure when the selected port is already in use.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/tcpshell.py -->
