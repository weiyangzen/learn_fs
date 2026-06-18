# Research: subset-b-007964

Grouped research for XRootD `XrdSec` security interface, protocol loading, request protection, server configuration, transport-layer authentication wrappers, legacy test tools, and the `XrdSecgsi` build target. Each section preserves the source path and is wrapped in reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecInterface.hh -->
## sources/distributed-fs/xrootd/src/XrdSec/XrdSecInterface.hh

Purpose: Defines the public ABI for XRootD security plug-ins and the core authentication/service objects used by clients and servers.

Important APIs and types: `XrdSecBuffer` owns malloc-backed buffers; `XrdSecCredentials` and `XrdSecParameters` alias that buffer type. `XrdSecProtocol` is the per-connection authentication interface, with `Authenticate`, `getCredentials`, optional `Encrypt`/`Decrypt`/`Sign`/`Verify`, session-key methods, `needTLS`, and `Delete`. `XrdSecService` is the server-side factory and policy interface, with `getParms`, `getProtocol`, `PostProcess`, and `protTLS`. Function typedefs `XrdSecGetProt_t` and `XrdSecGetServ_t` describe dynamically loaded factories.

Control flow: Clients consume a server security token with `XrdSecGetProtocol`, generate initial credentials, and loop on `authmore` parameters until authentication completes or fails. Servers send `getParms` output during login, instantiate a protocol from client credentials, call `Authenticate`, and may then run service-level post-processing.

State and persistence: The interface itself has no durable persistence. Protocol objects own per-connection authentication state in `Entity` and optional session keys. Service objects are process-long server singletons in the default loader contract.

Dependencies and integration points: Depends on `XrdSecEntity`, `XrdOucErrInfo`, `XrdNetAddrInfo`, versioned plug-in conventions, and shared libraries named `libXrdSec<p>.so`. It is consumed by protocol plug-ins, `XrdSecServer`, client-side security selection, and request protection.

Risks: The ABI relies on raw pointers, manual `Delete`, malloc/free ownership, and exact exported symbol names. `XrdSecBuffer` frees only the original constructor pointer, so later mutation of `buffer` does not affect ownership. Default crypto methods return `-ENOTSUP`, so protection silently depends on protocol overrides. TLS requirements are split between initializer tokens and `needTLS`.

Test signals: Compile a minimal protocol plug-in with `XrdVERSIONINFO`; exercise multi-step `authmore`, null `einfo`, unsupported crypto, `Delete` lifecycle, TLS-required tokens, and server `PostProcess` rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecInterface.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecLoadSecurity.cc -->
## sources/distributed-fs/xrootd/src/XrdSec/XrdSecLoadSecurity.cc

Purpose: Implements dynamic loading for the default security framework and request-protection framework, plus the client helper that creates `XrdSecProtect` objects from protocol responses.

Important APIs and functions: `XrdSecLoadSecFactory` loads `XrdSecGetProtocol`. `XrdSecLoadSecService` loads `XrdSecgetService` and optionally returns the protection singleton. `XrdSecGetProtection` validates a `kXR_protocol` response and creates client protection. `XrdSecLoadProtection` is the server-side one-time protection loader. Internal `Plug` and overloaded `Load` helpers wrap `XrdOucPinLoader`.

Control flow: The security loader defaults to `libXrdSec.so`, resolves the client factory and service factory, optionally instantiates the service with the logger/config path, and unloads on failure. The protection loader defaults to `libXrdSecProt.so` and resolves `XrdSecProtObjectP`. Client protection first validates response lengths and vector sizes, skips no-protection responses, lazily loads the protection library under `protMutex`, and calls `New4Client`.

State and persistence: Process globals in `XrdSecProtection` cache `theProtector` and `protRC`. `protMutex` serializes lazy client loading. Loaded service/protector objects are process-resident; no disk state is written.

Dependencies and integration points: Uses `XrdOucPinLoader`, `XrdVersion`, `XProtocol` response structs, `XrdSecProtector`, `XrdSysError`, and `XrdSysMutex`. It is the bridge from public ABI symbols to actual shared libraries.

Risks: The protection `Load` has an early `return 1` before the later diagnostic/unload block, so some failure diagnostics are unreachable. Cached `protRC` makes a failed protection load sticky. Client-side errors go to `std::cerr` when no `XrdSysError` is available. ABI symbol names must match exactly.

Test signals: Missing library, bad symbol, version mismatch, service constructor failure, malformed short and oversized `kXR_protocol` responses, repeated concurrent `XrdSecGetProtection`, and successful lazy reuse of a loaded protector.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecLoadSecurity.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecLoadSecurity.hh -->
## sources/distributed-fs/xrootd/src/XrdSec/XrdSecLoadSecurity.hh

Purpose: Declares ABI-stable loader utilities for client security factories, server security services, and client request-protection objects.

Important APIs and types: Exposes `XrdSecLoadSecFactory`, `XrdSecGetProtection`, and `XrdSecLoadSecService`. Forward declares `XrdSecProtect`, `XrdSecProtector`, `ServerResponseBody_Protocol`, and `XrdSysError`.

Control flow: Callers use `XrdSecLoadSecFactory` client-side to obtain `XrdSecGetProtocol`, use `XrdSecLoadSecService` server-side to instantiate `XrdSecService`, and use `XrdSecGetProtection` after authentication when the server's protocol response requests signed requests.

State and persistence: The header declares no state. Implementations cache loaded plug-ins process-wide and return long-lived service/protector pointers.

Dependencies and integration points: Includes `XrdSecInterface.hh` for protocol and service ABI types and references protocol response structures from `XProtocol`.

Risks: Comments document ABI stability, so signature or ownership changes are high impact. Error handling is split: factory loading returns text in a caller buffer, while service loading logs through `XrdSysError`.

Test signals: Compile client and server users against the header, verify default arguments, and check that callers interpret positive, zero, and negative `XrdSecGetProtection` results correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecLoadSecurity.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecMonitor.hh -->
## sources/distributed-fs/xrootd/src/XrdSec/XrdSecMonitor.hh

Purpose: Provides a tiny extension interface for attaching security-related metadata to monitoring streams through `XrdSecEntity::secMon`.

Important APIs and types: `XrdSecMonitor::WhatInfo` currently defines `TokenInfo`. `Report(WhatInfo, const char *)` is pure virtual and expects CGI-formatted null-terminated strings.

Control flow: Security or authorization code calls `Report` on the monitor object associated with the current mapped user. Implementations decide whether the info type is enabled and whether to emit it.

State and persistence: The interface has no state. Persistence depends entirely on the concrete monitor implementation and downstream monitoring pipeline.

Dependencies and integration points: Forward-linked from `XrdSecEntity` users; no includes are required. It is intended for optional observability rather than authentication decisions.

Risks: CGI-format strings are unvalidated at the interface boundary. Unknown enum values must be rejected by implementations. Raw `const char *` lifetime must cover the call.

Test signals: Implement a fake monitor and verify `TokenInfo` is accepted, invalid enum values are ignored, disabled monitoring returns false, and callers tolerate a null monitor pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecMonitor.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecPManager.cc -->
## sources/distributed-fs/xrootd/src/XrdSec/XrdSecPManager.cc

Purpose: Implements protocol discovery, loading, caching, and client/server protocol object creation for XRootD security protocols.

Important APIs and functions: `Find` returns a protocol bitmask and optional initializer arguments. `Get(host, endpoint, pname, err)` creates a server-side protocol. `Get(host, endpoint, XrdSecParameters&, err)` scans a server token for client-side candidates. Private `Add`, `Lookup`, and `ldPO` manage loaded protocol list entries and dynamic library resolution.

Control flow: Server configuration calls `Load`, which invokes `ldPO` to resolve `XrdSecProtocol<p>Object` and `XrdSecProtocol<p>Init`, run one-time initialization, and append the protocol. Client selection scans `&P=<name>[,<args>]` entries, honors `xrd.wantprot` or `XrdSecPROTOCOL`, lazily loads matching protocols, and advances `secparm.buffer/size` past failed candidates so callers can retry later.

State and persistence: `XrdSecProtList` entries are intentionally never freed and hold protocol id, arguments, bitmask, TLS-required flag, and factory pointer. `tlsProt` accumulates protocol names requiring TLS. `protnum` assigns shifting bitmasks until overflow. State is process-local.

Dependencies and integration points: Uses `XrdOucPinLoader`, `XrdOucErrInfo`, `XrdOucEnv`, `XrdVersionPlugin`, `XrdNetAddrInfo`, the builtin `host` protocol, and `XrdSecInterface` plug-in symbols.

Risks: Dynamic libraries are pinned by retaining function pointers after deleting the loader object. The constructor stores `protargs` as a string literal when no args are supplied, while the destructor never frees entries. `secparm.buffer` is mutated during scan, surprising callers that reuse it. Protocol-id and token parsing are bounded but still legacy C-string heavy. The debug export branch appears contradictory (`if (DebugON && ... && !DebugON)`).

Test signals: Load builtin `host`, load a valid shared protocol, fail missing `Init`/`Object`, parse multiple `&P=` candidates, filter with `XrdSecPROTOCOL`, verify `secparm` advancement, detect TLS prefixes, and enforce protocol bitmask overflow behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecPManager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecPManager.hh -->
## sources/distributed-fs/xrootd/src/XrdSec/XrdSecPManager.hh

Purpose: Declares the protocol manager used by both client and server security code to find, load, and instantiate authentication protocols.

Important APIs and types: Defines `XrdSecPMask_t`, the `PROTPARMS` function signature macro, and class `XrdSecPManager`. Public methods include `Find`, two `Get` overload groups, `Load`, `setDebug`, `setErrP`, and `protTLS`.

Control flow: Server startup loads configured protocols with `Load`; runtime server authentication calls `Get` by protocol name; clients call `Get` with server parameters to select a supported candidate.

State and persistence: Maintains a linked list of loaded protocols, next bitmask, logger pointer, TLS protocol string, and proxy/forwarded-credential policy flags. All state is in memory and effectively process-long.

Dependencies and integration points: Includes `XrdSecInterface.hh` and `XrdSysPthread.hh`; forward declares network, error, protocol, and logging classes. It is embedded statically in `XrdSecServer`.

Risks: Thread-safety depends on internal mutex use and the invariant that protocols are added but not removed. The API returns raw protocol pointers whose `Delete` method must be used. Proxy behavior changes client protocol selection by suppressing `xrd.wantprot`.

Test signals: Header consumers should compile in client and server contexts, exercise constructor proxy flags, and verify returned masks drive `protbind only` enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecPManager.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtect.cc -->
## sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtect.cc

Purpose: Implements XRootD request stream protection by deciding which requests require signatures, creating `kXR_sigver` requests, and verifying received signatures.

Important APIs and functions: `Screen` evaluates request codes against `secTable` and conditional rules for `open`, `query`, and `set`. `Secure` hashes sequence number, request header, and optional payload, encrypts or sends the SHA-256 digest, and builds a `SecurityRequest`. `Verify` checks anti-replay sequence order, stream id, request id, signature version, hash/key flags, decrypts if needed, recomputes the digest, and compares. `SetProtection` maps protocol response levels and overrides into an active security vector.

Control flow: Callers first use `NEED2SECURE(protP)(request)` to avoid unnecessary signing. When signing, `Secure` increments the local sequence, signs the header and, depending on request/data policy, payload bytes. On the server side, `Verify` validates metadata before digest comparison and records the accepted sequence.

State and persistence: Each `XrdSecProtect` holds the auth protocol pointer, selected security vector, protocol response copy, sequence number union, data-signing flag, and encryption-permitted flag. No durable state exists.

Dependencies and integration points: Uses `XProtocol` request structs, OpenSSL EVP SHA-256 or CommonCrypto headers, `XrdSecProtocol::Encrypt/Decrypt/getKey`, `XrdSecProtector`, atomics/platform helpers, and errno-to-text conversion.

Risks: Sequence numbers are per object and must not be shared across independent streams. The anti-replay compare relies on network byte order preserving monotonic comparison. If `force` permits unencrypted hashes, signatures provide integrity only against parties without stream write access assumptions. Payload signing is skipped for write/pgwrite unless `secVerData` is enabled. `EVP_get_digestbyname("sha256")` is not checked for null.

Test signals: Sign/verify every level, conditional open/query/set cases, payload and `kXR_nodata` behavior, replayed and out-of-order sequence numbers, stream/request mismatch, unsupported crypto flags, protocols with and without session keys, and malformed signature lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtect.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtect.hh -->
## sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtect.hh

Purpose: Declares the per-connection request protection object and the `NEED2SECURE` fast path macro.

Important APIs and types: `XrdSecProtect` exposes `Delete`, member-function pointer `Need2Secure`, `Secure`, and `Verify`. Protected constructors distinguish client initialization from server cloning. `SetProtection` is used by `XrdSecProtector` to configure levels and vectors.

Control flow: Callers check `NEED2SECURE(protP)(ClientRequest&)`, then call `Secure` before sending or `Verify` when receiving the companion `kXR_sigver` request.

State and persistence: Holds non-owning `XrdSecProtocol *authProt`, active vector pointers, local vector storage, request settings, sequence counters, and option flags. State is in-memory and tied to a connection.

Dependencies and integration points: Includes `XProtocol.hh`, forward declares `XrdSecProtocol`, and friends `XrdSecProtector` for controlled construction/configuration.

Risks: `Need2Secure` is public and must be invoked through the macro to avoid null-pointer misuse. The auth protocol lifetime must exceed the protection object. `Secure` returns malloc-backed request storage that callers must free.

Test signals: Compile macro call sites, verify no signing when `protP` is null, confirm `Delete` cleanup, and test ownership of returned `SecurityRequest` buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtect.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtector.cc -->
## sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtector.cc

Purpose: Provides the default request-protection factory exported as `XrdSecProtObjectP` and manages server/client creation of `XrdSecProtect` instances.

Important APIs and functions: `Config` converts local/remote `XrdSecProtectParms` into `ServerResponseReqs_Protocol` templates. `LName` maps levels to strings. `New4Client` creates a client object from server response requirements. `New4Server` selects local versus remote policy and clones a configured template. `ProtResp` returns the correct response payload for a client address.

Control flow: Server startup configures local and remote policies, creates template `XrdSecProtect` objects when levels are non-none, and sets shortcut globals. Runtime server creation chooses local/remote by `XrdNetIF::InDomain`, honors relaxed old-client behavior, checks whether the authentication protocol has an encryption key, and either disables, warns, or forces unencrypted digest behavior. Client creation validates response length and requires either encryption support or forced mode.

State and persistence: Namespace globals `lrTab`, `lrSame`, and `noProt` hold process-wide protection policy. Template protection objects are heap allocated and persist. No disk persistence.

Dependencies and integration points: Links with `XrdNetIF`, `XrdSecProtect`, `XrdSecInterface`, `XrdSysError`, and XRootD protocol structs. It is loaded by `XrdSecLoadProtection`.

Risks: Policy is global and not guarded for reconfiguration; it assumes startup-only configuration. `ProtResp` ignores the `pver` argument, so compatibility relies on `New4Server` relaxed checks. Lack of encryption downgrades protection unless `force` is set. Local/remote split depends on correct `Entity.addrInfo`.

Test signals: Configure all levels, local-only and remote-only policies, relaxed old-client protocol levels, forced and non-forced no-key protocols, local-domain detection, `ProtResp` sizes, and client validation of vector lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtector.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtector.hh -->
## sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtector.hh

Purpose: Declares the protection policy parameters and factory interface that manages `XrdSecProtect` objects.

Important APIs and types: `XrdSecProtectParms` defines levels `secNone` through `secPedantic` and options `doData`, `relax`, and `force`. `XrdSecProtector` exposes `Config`, `LName`, `New4Client`, `New4Server`, and `ProtResp`, plus `lrType` for local/remote slots.

Control flow: Server code configures the protector once, sends `ProtResp` in protocol negotiation, and creates server-side protectors after authentication. Client code creates a protector from the negotiated response.

State and persistence: The abstract class declares no fields. The default implementation stores global configured templates and flags.

Dependencies and integration points: Uses `XPtypes.hh`, protocol response structs, `XrdNetAddrInfo`, `XrdSecProtocol`, and `XrdSysLogger`. The exported singleton is resolved by the loader as `XrdSecProtObjectP`.

Risks: `force` explicitly allows operation without encrypted hashes, which should be treated as a compatibility/testing downgrade. `relax` permits unsigned old clients. The ABI is virtual and plug-in-facing.

Test signals: Validate enum-to-wire mappings, options-to-response flags, client and server object construction, and plug-in replacement compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtector.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtocolhost.cc -->
## sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtocolhost.cc

Purpose: Implements the builtin `host` authentication protocol, a minimal protocol that identifies the peer by host/address rather than cryptographic credentials.

Important APIs and functions: `Authenticate` fills `Entity.prot`, `Entity.host`, and `Entity.addrInfo` and succeeds. `getCredentials` returns a credential buffer containing `host`. `XrdSecProtocolhostObject` constructs `XrdSecProtocolhost`.

Control flow: The protocol manager special-cases `host` and binds this factory directly. On client credential generation it sends the protocol name. On server authentication it accepts and populates entity host/address.

State and persistence: Each object owns a duplicated host string and a copied `XrdNetAddrInfo`. No persistent state or session key exists.

Dependencies and integration points: Depends on `XrdSecProtocolhost.hh` and `XrdSecInterface`. It is loaded through `XrdSecPManager` without a dynamic initializer.

Risks: Provides no cryptographic authentication and can negate other default protocols when enabled. `getCredentials` returns a string literal through `XrdSecCredentials`, relying on constructor ownership behavior to avoid freeing it. `Authenticate` ignores credential contents.

Test signals: Enable implicit host auth, generate credentials, authenticate null/host credentials through server code, verify entity fields, and ensure request protection is not enabled without a session key unless forced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtocolhost.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtocolhost.hh -->
## sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtocolhost.hh

Purpose: Declares the builtin host-based `XrdSecProtocol` implementation and factory.

Important APIs and types: `XrdSecProtocolhost` overrides `Authenticate`, `getCredentials`, and `Delete`, and provides `getParms` returning `"host"`. Private state stores `XrdNetAddrInfo epAddr` and `char *theHost`.

Control flow: Constructed with a host string and endpoint, then used like any other protocol through the base `XrdSecProtocol` methods.

State and persistence: Owns duplicated host memory and endpoint copy until `Delete`. No durable state and no cryptographic key state.

Dependencies and integration points: Includes `XrdNetAddrInfo` and `XrdSecInterface`. The non-extern factory `XrdSecProtocolhostObject` is referenced directly by `XrdSecPManager`.

Risks: Header-level `getParms` returns size 5 for a four-character string plus terminator, while other token sizes typically exclude terminators. Authentication strength is host-trust only.

Test signals: Verify constructor/destructor ownership, returned parameter size expectations, and factory compatibility with `PROTPARMS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtocolhost.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecServer.cc -->
## sources/distributed-fs/xrootd/src/XrdSec/XrdSecServer.cc

Purpose: Implements the default server-side `XrdSecService`: parses `sec.*` configuration, loads protocols and entity post-processors, builds security tokens, enforces protocol bindings, and initializes request protection.

Important APIs and functions: `XrdSecgetService` constructs/configures the service. `Configure` runs authentication then protection initialization. `getParms`, `getProtocol`, and `PostProcess` implement the public service contract. Directive handlers include `xenlib`, `xlevel`, `xpbind`, `xprot`, `xpparm`, and `xtrace`. Helpers `XrdSecProtBind`, `XrdSecProtParm`, `add2token`, and `ProtBind_Complete` manage host bindings and accumulated protocol arguments.

Control flow: Startup opens the config file, scans only `sec.` directives, loads configured protocols, accumulates default `&P=` token entries, resolves `protbind` host templates, optionally loads `SecEntityPin`, exports `XRDSECPROTOCOLS`, then configures local/remote protection. At login, `getParms` picks a host-specific or default token. `getProtocol` defaults null credentials to `host`, validates bindings when `only` enforcement is enabled, and delegates to `PManager`.

State and persistence: The service stores binding lists, default token buffers, config path, trace object, entity plugin handle, and flags. Static `PManager` caches loaded protocols across the process. No files are written, but environment variables are exported.

Dependencies and integration points: Uses `XrdOucStream`, `XrdOucPinKing`, `XrdSecEntityPin`, `XrdSecProtector`, `XrdNetAddr`, `XrdSysError`, `XrdOucTrace`, and the protocol manager. It is the implementation loaded by `XrdSecLoadSecService`.

Risks: Heavy use of raw allocation and linked lists makes startup error paths leak-tolerant but hard to unwind. `host` authentication can negate other default protocols. `protbind only` enforcement depends on protocol bitmasks and host template matching. `XrdSecProtParm` buffers are fixed at 4096 bytes. Constructor allocates `STBuff` without checking. `getParms` uses hostname matching and may return no auth for `none` bindings.

Test signals: Config files with no protocols, duplicate protocols, invalid protocol ids, missing libraries, `protparm` before/after protocol, wildcard and exact `protbind`, `only` enforcement, `entitylib ++`, trace toggles, protection levels/options, local/remote split, and `PostProcess` accept/reject.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecServer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecServer.hh -->
## sources/distributed-fs/xrootd/src/XrdSec/XrdSecServer.hh

Purpose: Declares the default server-side security service implementation used by the `XrdSecgetService` plug-in entrypoint.

Important APIs and types: `XrdSecServer` privately inherits `XrdSecService` and implements `getParms`, `getProtocol`, `PostProcess`, `Configure`, and `protTLS`. Private helpers correspond to configuration directives and token/binding completion.

Control flow: Construction sets defaults and logger/trace state; `Configure` must succeed before the object is returned as an `XrdSecService`.

State and persistence: Holds static `PManager`, a union for pre-load versus loaded entity post-processing plugin state, binding list pointers, security token buffers, trace pointer, and policy flags. State is process-local and not deleted during normal server lifetime.

Dependencies and integration points: Includes `XrdSysError`, `XrdSysLogger`, `XrdOucStream`, `XrdSecInterface`, and `XrdSecPManager`; forward declares entity pinning and binding helpers.

Risks: Private inheritance still casts to `XrdSecService *` at the factory boundary. The union requires correct phase discipline between `pinInfo` and `secEntityPin`. The destructor is intentionally empty because the server is never deleted.

Test signals: Compile the factory cast, verify `protTLS` forwards manager state, and run lifecycle tests that call `Configure` once then service methods concurrently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecServer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecTLayer.cc -->
## sources/distributed-fs/xrootd/src/XrdSec/XrdSecTLayer.cc

Purpose: Implements a transport-layer shim for security protocols that need socket-style handshakes over the XRootD authentication exchange.

Important APIs and functions: `getCredentials` drives the client side; `Authenticate` drives the server side; `bootUp` creates a socketpair and starts the protocol thread; `Read` self-paces socket reads; `secDone`, `secDrain`, `secError`, and `secXeq` handle completion, thread/socket cleanup, and error propagation.

Control flow: On first use, the wrapper creates a UNIX socketpair, starts a thread running derived `secClient` or `secServer`, and exchanges framed `TLayerRR` records as credentials/parameters. Each frame carries protocol name, `xfrData` or `endData`, and optional bytes. Reads poll in short slices and switch to `endData` after repeated no-progress slices. Final completion drains the socket, waits for the thread semaphore, and returns success or error.

State and persistence: Per object state includes thread id, semaphore, initiator/responder roles, socket fds, time-slice counters, error code/text, and reusable header. No durable state exists.

Dependencies and integration points: Uses `XrdSecProtocol`, `XrdOucErrInfo`, `XrdSysThread`, `XrdSysSemaphore`, `XrdSysFD_Socketpair`, `poll`, `read`, `write`, and derived protocol implementations such as TLS-like mechanisms.

Risks: Derived `Delete` must join `secTid`; otherwise thread lifecycle is unsafe. The framing header carries only an eight-byte protocol name and minimal validation. Timeouts are CPU/poll-slice based rather than wall-clock RTT. `write` does not handle partial writes. `eDest` is a raw pointer set from the current call.

Test signals: Derived fake client/server that exchange multiple frames, server-initiated and client-initiated starts, partial/no-progress reads, invalid frame sizes/codes, socketpair/thread creation failure injection, error propagation, and deletion while a thread is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecTLayer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecTLayer.hh -->
## sources/distributed-fs/xrootd/src/XrdSec/XrdSecTLayer.hh

Purpose: Declares `XrdSecTLayer`, an abstract `XrdSecProtocol` wrapper that virtualizes a transport socket for protocols that require stream-socket handshakes.

Important APIs and types: `Initiator` selects client- or server-first flow. Derived classes implement `secClient`, `secServer`, and `Delete`. The class overrides `Authenticate` and `getCredentials`, exposes `secXeq`, and defines internal `TLayerRR` frame constants.

Control flow: Client and server call the normal security protocol methods, while derived implementations communicate on a supplied file descriptor in a helper thread.

State and persistence: Stores thread, semaphore, socket descriptors, timeout counters, error state, and frame header. State is transient per authentication object.

Dependencies and integration points: Includes `XrdSecInterface` and `XrdSysPthread`; forward declares `XrdOucErrInfo`. It is intended as a base for SSL/TLS-like protocols integrated into XRootD auth handshakes.

Risks: Documentation requires derived `Delete` to join the thread, but the base cannot enforce it. Protocols must tolerate a local 127.0.0.1-style virtual socket identity. `Tmax` is fixed internally.

Test signals: Compile a mock derived class, verify both initiator modes, ensure destructor closes `myFD`, and check derived `Delete` joins active threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecTLayer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecTrace.hh -->
## sources/distributed-fs/xrootd/src/XrdSec/XrdSecTrace.hh

Purpose: Defines trace bit masks for the XrdSec subsystem.

Important APIs and types: Includes `XrdOucTrace.hh` and defines `TRACE_Authenxx`, `TRACE_Authen`, and `TRACE_Debug`.

Control flow: Server configuration uses these masks in `sec.trace` parsing; runtime code checks `QTRACE(Debug)` and authentication trace categories.

State and persistence: No state. Values are compile-time constants.

Dependencies and integration points: Integrated with `XrdOucTrace` and `XrdSecServer` tracing setup.

Risks: Mask values must remain compatible with existing trace usage. The `TRACE_Authenxx` aggregate masks both auth and debug bits, so changes can affect clearing behavior.

Test signals: Parse `sec.trace all`, `debug`, `auth`, `authentication`, `off`, and negative options; verify `PManager` debug toggling follows trace state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSecTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSectestClient.cc -->
## sources/distributed-fs/xrootd/src/XrdSec/XrdSectestClient.cc

Purpose: Legacy command-line utility that converts a security token into client credentials for manual or scripted protocol testing.

Important APIs and functions: `main` parses `-b`, `-d`, `-l`, and `-h`, obtains `XrdSecGetProtocol`, calls `getCredentials`, and prints binary or hex output. `tohex` converts bytes to lowercase hex. `help` prints usage.

Control flow: The tool reads the sectoken from argv or `XrdSecSECTOKEN`, resolves the target host or defaults to localhost, optionally sets `XrdSecDEBUG`, gets a protocol object, generates credentials, optionally prefixes length, writes credentials, and calls `Delete`.

State and persistence: No persistent state. It uses environment variables for input and debug behavior and writes credentials to stdout.

Dependencies and integration points: Links to the client-side `XrdSecGetProtocol` symbol, `XrdNetAddr`, and security interface types. It pairs with `XrdSectestServer.cc`.

Risks: The source references `eText` and `pp->addrInfo` in ways that appear stale relative to the shown interfaces, so build coverage is important. Binary `fwrite` checks compare item count against byte size, which is incorrect for a one-item write. Credentials are printed to stdout and may expose secrets.

Test signals: Build the utility, run host and real protocol tokens, binary and hex output, length prefix, invalid host, missing token, debug mode, and pipe output into the test server.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSectestClient.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSectestServer.cc -->
## sources/distributed-fs/xrootd/src/XrdSec/XrdSectestServer.cc

Purpose: Legacy command-line utility that feeds credentials into the server security service and prints the authenticated entity.

Important APIs and functions: `main` creates `XrdSecgetService`, prints the service token, reads credentials in binary or hex, calls `getProtocol` and `Authenticate`, and prints `name@host prot=...`. Helpers parse arguments, read binary credentials, convert hex with `unhex`/`cvtx`, read lines, and print errors/help.

Control flow: Command-line options set config path, host, input source, binary mode, and debug flag. The server service is configured from `-c`, host defaults to localhost, credentials come from inline argument, file/stdin, or binary stream, then normal server authentication APIs are exercised.

State and persistence: Uses global `opts`, `errbuff`, and `hexbuff`. No durable writes; output goes to stdout/stderr.

Dependencies and integration points: Links directly to `XrdSecgetService`, `XrdSysLogger`, `XrdOucErrInfo`, `XrdNetAddr`, and XrdSec interfaces. Intended for manual interoperability with test client and real protocol plug-ins.

Risks: Several parsed options in the usage string are legacy or unimplemented. `opts.xtra` and `opts.debug` are parsed but not materially used. Credential buffer size is fixed at 8192 bytes for binary input and 4096 bytes for hex conversion in `main`. The call to `getParms` passes `opts.host` where the interface expects `XrdNetAddrInfo *`, suggesting this file may be excluded or stale in current builds.

Test signals: Build test target, run with valid/invalid config, inline hex credentials, stdin/file input, binary input, malformed hex, oversized credentials, missing config, host auth, and multi-step protocols returning continuation parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSec/XrdSectestServer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/CMakeLists.txt -->
## sources/distributed-fs/xrootd/src/XrdSecgsi/CMakeLists.txt

Purpose: Defines build targets for the GSI security protocol plug-in, its authorization mapping helper plug-ins, and optional GSI command-line utilities.

Important APIs and targets: Creates module libraries `${XrdSecgsi}`, `${XrdSecgsi_AUTHZVO}`, and `${XrdSecgsi_GMAPDN}`. Links the main GSI module to `XrdCrypto` and `XrdUtils`, and mapping modules to `XrdUtils`. Adds all three to the aggregate `plugins` target. Optionally builds `xrdgsiproxy` and `xrdgsitest` when `XRDCL_LIB_ONLY` is false.

Control flow: CMake evaluates target names with `${PLUGIN_VERSION}`, registers sources, links dependencies, installs module libraries to `${CMAKE_INSTALL_LIBDIR}`, and installs optional executables to `${CMAKE_INSTALL_BINDIR}`.

State and persistence: No runtime state. The file persists build graph membership and install layout.

Dependencies and integration points: Depends on `XrdSecProtocolgsi`, GSI option/trace headers, `XrdSecgsiAuthzFunVO`, `XrdSecgsiGMAPFunDN`, `XrdCrypto`, `XrdUtils`, and `OpenSSL::Crypto` for tools.

Risks: Source additions must be reflected here or the plug-in will miss symbols. Module names include `PLUGIN_VERSION`, so loader expectations and install names must stay aligned. Optional tools disappear in client-library-only builds.

Test signals: Configure with and without `XRDCL_LIB_ONLY`, build `plugins`, inspect installed module names, verify OpenSSL crypto linkage, and load the GSI protocol through the security protocol manager.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/CMakeLists.txt -->
