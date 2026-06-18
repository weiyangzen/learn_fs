# Research: subset-b-007943

Grouped research for XRootD macaroon issuance and XrdNet core networking files. Each section preserves the source path and is wrapped in reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroonsHandler.cc -->
## sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroonsHandler.cc

Purpose: Implements the HTTP extension handler that issues XRootD macaroons through the legacy `application/macaroon-request` JSON endpoint and OAuth2-style `/.oauth2/token` endpoint, plus OAuth authorization-server discovery.

Important APIs and functions: `MatchesPath` selects POST requests and well-known OAuth paths. `ProcessReq`, `ProcessOAuthConfig`, and `ProcessTokenRequest` parse inbound requests. `GenerateMacaroonResponse` creates the macaroon, adds first-party caveats, serializes it, and sends JSON. `GenerateActivities` maps `XrdAccPrivs` from the authorization chain to WLCG-style activity caveats. `GenerateID`, `NormalizeSlashes`, `unquote`, `determine_validity`, `is_reserved_caveat`, and `is_supported_caveat` are helper routines.

Control flow: The handler branches between OAuth discovery, OAuth token request, and JSON macaroon request. OAuth form data is split on `&`, percent-decoded only for `scope`, converted into one resource path plus an `activity:` caveat, and forwarded to `GenerateMacaroonResponse`. JSON requests require a string `validity`, optional supported caveats, and reject reserved caveat prefixes before generation. Generation clamps validity to `m_max_duration`, creates a `before:` caveat, derives default activities from authorization, lets a caller-supplied `activity:` caveat override defaults, adds `name:`, `activity:`, `path:`, and `before:` caveats, serializes with libmacaroons, and returns either `macaroon` or `access_token`.

State and persistence: The class stores `m_max_duration`, `m_chain`, `m_log`, `m_location`, and `m_secret`; no on-disk state is written. Macaroon IDs are random UUIDs. Debug logging may emit ID, resource, entity fields, user caveats, and expiry when the debug mask is enabled.

Dependencies and integration points: Integrates with `XrdHttpExtReq`, `XrdSecEntity`, `XrdAccAuthorize`, `XrdAccPrivs`, `XrdOucTUtils`, `XrdSysError`, json-c, libmacaroons, and libuuid. Static configuration helpers are declared in the header and implemented in the adjacent macaroon configuration module.

Risks: `NormalizeSlashes` uses a separate `output_idx` and may append the wrong character when duplicate slashes are skipped. Form parsing only decodes `scope`, not keys or other values, and exact content-type matching rejects normal parameters such as charset. OAuth error text mentions the wrong content type. Generated OAuth `activity:` strings leave policy entirely to caller-provided scope when present. Several JSON allocation failure paths leak earlier json-c objects. `macaroon_serialize` failure prints to stdout instead of the configured logger. `strlen` on serialized macaroon assumes null-terminated serialization. `gmtime` returns static storage and can be thread-sensitive on some platforms.

Test signals: Exercise JSON and OAuth endpoints, invalid methods, missing host/content-type/content-length/body, oversized bodies, malformed JSON/form encoding, invalid ISO-8601 durations, `expire_in` clamping, reserved and unsupported caveats, multiple scope paths, authorization-chain privilege mapping, no-security-entity-name behavior, serialization failure injection, and response shape for OAuth versus macaroon JSON.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroonsHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroonsHandler.hh -->
## sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroonsHandler.hh

Purpose: Declares the `Macaroons::Handler` HTTP extension class and shared macaroon configuration surface used by both request handling and authorization code.

Important APIs and types: Defines `LogMask`, `NormalizeSlashes`, and `Handler`. `Handler` derives from `XrdHttpExtHandler`, exposes `MatchesPath`, `ProcessReq`, `Init`, destructor, and static `Config`. `AuthzBehavior` communicates pass-through, allow, or deny behavior to configuration consumers.

Control flow: The constructor initializes defaults, stores the authorization chain and logger, invokes `Config`, and throws `std::runtime_error` on failure. Private methods separate ID generation, activity derivation, OAuth discovery, OAuth token parsing, response generation, and individual config directive parsing.

State and persistence: Per-instance state is `m_max_duration`, `m_chain`, `m_log`, `m_location`, and `m_secret`. The header itself defines no persistence; secret and location are loaded from configuration by implementation files.

Dependencies and integration points: Depends on `XrdHttp/XrdHttpExtHandler.hh`, forward declarations for authorization, stream, environment, security entity, and standard C++ string/vector. It forms the ABI between XRootD HTTP plugin registration, macaroon authorization, and the configuration parser.

Risks: `m_chain` and `m_log` are raw non-owning pointers with no lifetime enforcement. Throwing from the constructor makes plugin load behavior dependent on callers catching exceptions. Static `Config` is shared by multiple modules, so changes to directive behavior affect issuance and authorization.

Test signals: Compile against plugin registration code; construct with valid and invalid config; verify `AuthzBehavior` values match configuration expectations; ensure `Init` being a no-op is acceptable for the HTTP extension lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroonsHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/CMakeLists.txt -->
## sources/distributed-fs/xrootd/src/XrdNet/CMakeLists.txt

Purpose: Registers XrdNet source and header files as private sources of the `XrdUtils` target.

Important APIs and functions: Uses CMake `target_sources(XrdUtils PRIVATE ...)` to list network core, address, buffer, cache, notification, connect, identity, interface, messaging, PMark, refresh, registry, security, socket, and utility compilation units.

Control flow: No runtime control flow. Build configuration simply feeds the listed files into the `XrdUtils` target.

State and persistence: No runtime state or persistence. The file persists build membership and therefore controls whether implementation files are compiled into the utility library.

Dependencies and integration points: Integrates XrdNet into the broader XRootD CMake build through `XrdUtils`. Headers are included in the source list for IDE visibility and dependency tracking; implementations rely on system socket APIs and XRootD support libraries.

Risks: Missing a `.cc` file here can produce unresolved symbols; listing headers as private sources does not export include paths by itself. PMark is split across adjacent files, so partial build-list changes can silently break optional packet marking features.

Test signals: Configure and build `XrdUtils`; verify every listed implementation compiles on Linux and Windows-gated code paths; check incremental builds notice header changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNet.cc -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNet.cc

Purpose: Implements the high-level XRootD network wrapper for binding TCP/UDP or Unix sockets, accepting inbound peers, creating outbound connections, UDP relay sockets, domain trimming, socket defaults, and optional network security authorization.

Important APIs and functions: `Accept(XrdNetAddr&)`, `Accept(XrdNetPeer&)`, `Bind(int)`, `Bind(char*)`, `Connect(XrdNetAddr&)`, `Connect(XrdNetPeer&)`, `Relay`, `Secure`, `Trim`, `unBind`, and `WSize` are public behavior. Private `do_Accept_TCP` overloads and `do_Accept_UDP` perform actual accept/receive work.

Control flow: Binding closes any previous socket, chooses stream versus datagram mode, opens through `XrdNetSocket`, detaches the fd, records the bound port, and creates a UDP `XrdNetBufferQ` when needed. Accept optionally polls for readiness, then dispatches to TCP accept or UDP receive. TCP accept builds an `XrdNetAddr`, sets socket options, authorizes through `XrdNetSecurity`, optionally reverse-resolves, and either returns the modern address or converts to legacy `XrdNetPeer`. UDP accept allocates a queue buffer, reads a datagram with `recvfrom`, rejects loopback/spoofed or unauthorized senders, optionally duplicates the fd, and attaches the buffer to the peer.

State and persistence: Instance state includes logger, security policy pointer, domain suffix, listening fd, bound port, port type, window/buffer sizes, default options, and UDP buffer queue. No durable persistence; sockets and heap buffers are process-local.

Dependencies and integration points: Depends on `XrdNetAddr`, `XrdNetPeer`, `XrdNetSecurity`, `XrdNetSocket`, `XrdNetUtils`, `XrdSysFD`, `poll`, `accept`, `recvfrom`, and socket option helpers. It is a compatibility bridge between newer address APIs and older peer-based code.

Risks: `Secure` merges ownership semantics into raw pointers and can be misused by callers retaining a pointer. `setDomain` assumes non-null input. `do_Accept_TCP` throttles `EMFILE` messages with a static counter shared across all instances. UDP accept stores received data as a null-terminated string and drops binary datagrams containing embedded nulls for string consumers. `XrdNetBufferQ` allocation is mandatory for UDP, so null allocation would crash if `Bind` succeeds but queue creation fails.

Test signals: Bind TCP/UDP to fixed and ephemeral ports; bind Unix stream/datagram paths; accept with timeout and no timeout; exercise authorization allow/deny; verify reverse lookup and no-lookup modes; test UDP buffer recycle and `XRDNET_NEWFD`; inspect socket options for keepalive, nodelay, linger, close-on-exec, and window size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNet.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNet.hh -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNet.hh

Purpose: Declares the high-level XrdNet networking façade for TCP, UDP, and Unix-domain accept/connect operations.

Important APIs and types: Public methods include two `Accept` overloads, two `Bind` overloads, two `Connect` overloads, `Port`, `Relay`, `Secure`, `setDefaults`, `setDomain`, `Trim`, `unBind`, and `WSize`. Protected members expose fd, port, domain, defaults, security, and UDP buffer queue to derived classes.

Control flow: The header documents option semantics for accept, bind, and connect operations and defines the private helper split between TCP and UDP accepts.

State and persistence: The class owns an active socket fd and UDP buffer queue for its lifetime and frees the domain string in the destructor. It does not persist configuration outside process memory.

Dependencies and integration points: Includes platform socket headers and `XrdNetOpts.hh`; forward declares `XrdNetAddr`, `XrdNetPeer`, `XrdNetSecurity`, `XrdNetBufferQ`, and `XrdSysError`. This header is included by server code and message helpers that need network setup.

Risks: The interface returns `int` booleans for many operations and negative errno for bind failures, so callers must interpret results per method. `Secure` documentation transfers ownership but the type is a raw pointer. `setDefaults` applies options that cannot be disabled on individual calls.

Test signals: Compile consumers using both modern and legacy APIs; verify documented option bits match `XrdNetSocket` behavior; run leak/fd-close tests around constructor/destructor and repeated `Bind`/`unBind`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNet.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetAddr.cc -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetAddr.cc

Purpose: Implements mutable address construction and process-wide DNS/IP mode controls for `XrdNetAddr`, the write-enabled subclass of `XrdNetAddrInfo`.

Important APIs and functions: Constructors, `Hints`, `OnlyIPV4`, `Map64`, `Port`, `Register`, multiple `Set` overloads, `SetCache`, `SetDynDNS`, `SetIPV4`, `SetIPV6`, `SetLocation`, and `SetTLS` are implemented here.

Control flow: Static initialization builds `addrinfo` hints and probes IPv6 support. `Set(const char*, int)` clears prior state, handles wildcard, Unix paths, bracketed IPv6, IPv4, hostnames, and embedded ports, then writes the port. The multi-address `Set` parses host/port, calls `getaddrinfo`, and fills an array while suppressing adjacent duplicates. Sockaddr and fd overloads copy addresses from system calls. Global mode setters mutate shared hint structures and inform `XrdNetUtils`.

State and persistence: Per-object state inherited from `XrdNetAddrInfo` is reset and rewritten on each `Set`. Static state includes hint structures, `useIPV4`, `dynDNS`, and the shared DNS cache pointer. No disk persistence.

Dependencies and integration points: Uses `getaddrinfo`, `inet_pton`, `getsockname`, `getpeername`, `XrdNetIdentity`, `XrdNetUtils`, `XrdNetCache`, and `XrdSysE2T`. It underpins socket bind/connect, interface routing, address comparison, and security checks.

Risks: Static hint mutation is not synchronized and should only happen during initialization. `Set(const sockaddr*)` assumes non-null valid sockaddr. Hostnames containing colon are treated as host:port and may not support all IPv6-literal edge cases unless bracketed. `Register` trusts DNS resolution to validate a supplied hostname and is explicitly not MT-safe. `OnlyIPV4` changes global behavior at static initialization based on one socket probe.

Test signals: Parse wildcard, IPv4, bracketed IPv6, mapped IPv4, Unix paths, hostnames with numeric/service ports, missing ports, invalid ports, and too-long names. Verify IPv4-only and IPv6 mode behavior, dynamic DNS error text, fd peer/local address extraction, hostname registration, and multi-address duplicate suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetAddr.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetAddr.hh -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetAddr.hh

Purpose: Declares `XrdNetAddr`, the mutable address manipulation layer over read-only `XrdNetAddrInfo`.

Important APIs and types: Static `DynDNS`, `IPV4Set`, `SetCache`, `SetDynDNS`, `SetIPV4`, and `SetIPV6` expose process-wide controls. Instance APIs include `Port`, `Register`, multiple `Set` overloads, `SetDialect`, `SetLocation`, `SetTLS`, and convenience constructors from sockets and sockaddrs.

Control flow: The header establishes accepted address formats and the `PortInSpec` sentinel semantics for parsing ports from host specifications.

State and persistence: Mutable address data, hostname, socket fd association, location, TLS flag, and dialect are inherited. Static hints and DNS behavior are private global state implemented in the `.cc` file.

Dependencies and integration points: Includes `XrdNetAddrInfo.hh` and forwards `addrinfo`. It is the common address type passed to `XrdNet`, `XrdNetSocket`, `XrdNetSecurity`, `XrdNetIF`, cache, and utility modules.

Risks: Callers can associate fd values with address objects without ownership transfer, so fd lifetime is external. Static IP mode controls are effectively global and irreversible during normal runtime. `SetDialect` stores a pointer that must remain stable.

Test signals: Header/API tests should compile all constructors and overloads; behavioral tests should assert documented port sentinel behavior and global IPv4/IPv6 mode transitions before network initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetAddr.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetAddrInfo.cc -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetAddrInfo.cc

Purpose: Implements read-only address formatting, classification, reverse DNS naming, and address equality for `XrdNetAddrInfo`.

Important APIs and functions: `Format`, `isLocal`, `isLoopback`, `isPrivate`, `isRegistered`, `isUsingTLS`, `isHostName`, `Name`, `Port`, `Resolve`, and `Same` are implemented. Private helpers include `LowCase` and `QFill`.

Control flow: `Format` handles Unix, cached hostname, auto/name/address modes, IPv4, IPv6, mapped IPv4, deprecated mapped forms, bracket insertion, and optional port omission. `Name` returns cached or DNS-cache names before calling `Resolve`. `Resolve` uses `getnameinfo`, falls back to numeric formatting, normalizes IPv6 bracket form, and stores successful results in the cache. Classification methods branch on address family and mapped IPv4 handling. `Same` optionally checks port and compares cross-family mapped IPv4 addresses.

State and persistence: Each object owns `hostName` and sockaddr/unix-path storage; `dnsCache` is a static optional process cache. Reverse-lookup results are cached per object and optionally globally.

Dependencies and integration points: Uses system socket/address functions, `XrdNetCache`, and `XrdNetSockAddr`. Consumers use this class when deciding security, routing, logging, message destinations, and local/private/registered status.

Risks: `Format` mutates `hostName` by triggering DNS lookup in name mode, so a read-looking operation can allocate and cache. DNS cache use is global. `isLoopback` uses a compact byte comparison for mapped loopback that depends on structure representation. `Same` may consider differing families equal by hostname if both names exist, which depends on prior resolution. Formatting failure writes question marks and returns zero, so callers must check lengths.

Test signals: Format IPv4, IPv6, mapped IPv4, raw no-port, old mapped form, Unix sockets, small buffers, and hostname modes. Test private/local/loopback classes for RFC1918, link-local, ULA, mapped, and Unix addresses. Validate DNS success/failure cache behavior and `Same` with and without ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetAddrInfo.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetAddrInfo.hh -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetAddrInfo.hh

Purpose: Declares the read-only network address information object used across XrdNet APIs.

Important APIs and types: Defines formatting modes `fmtAuto`, `fmtName`, `fmtAddr`, `fmtAdv6`; options `noPort`, `noPortRaw`, `old6Map4`, `prefipv4`; address type enum `IPType`; `LocInfo`; and accessors/classifiers for family, protocol, socket address, sock size, fd, port, name, TLS, locality, privacy, mapped IPv4, registration, and equality.

Control flow: The header provides inline accessors and an assignment operator that deep-copies hostname and Unix sockaddr state while preserving value semantics for the socket address union.

State and persistence: Owns `XrdNetSockAddr IP`, optional `hostName`, optional Unix-path sockaddr, location metadata, address size, protocol type/flags, associated fd number, and protocol dialect pointer. Static `dnsCache` is shared by all instances.

Dependencies and integration points: Includes socket headers, `XrdNetSockAddr.hh`, and platform definitions. It is the base type for mutable `XrdNetAddr` and is passed to interface, security, PMark, and messaging code when mutation should not be allowed.

Risks: Copy assignment sets `sockAddr` only in some branches; value semantics depend on careful union pointer relocation. `SockFD` maps zero to no fd, so fd 0 cannot be represented as an associated socket. `Dialect` and location fields are not synchronized. `Longtitude` is misspelled in the public struct and must remain ABI-compatible.

Test signals: Copy/assign IPv4, IPv6, Unix, hostname-bearing, and TLS/dialect/location-bearing objects; verify destructors free exactly owned memory; assert fd 0 behavior if callers can pass it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetAddrInfo.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetBuffer.cc -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetBuffer.cc

Purpose: Implements aligned reusable network buffers and a locked freelist queue used mainly by UDP receive handling.

Important APIs and functions: `XrdNetBufferQ` constructor/destructor, `Alloc`, `Recycle`, `Set`, and `XrdNetBuffer` constructor are implemented.

Control flow: `Alloc` locks the queue, pops a recycled buffer if available, otherwise creates a new `XrdNetBuffer` and allocates aligned data with `posix_memalign`, then unlocks. `Recycle` deletes buffers when the freelist is at capacity or resets `dlen` and pushes the buffer back. Destructor drains the freelist.

State and persistence: Queue state includes buffer size, alignment, maximum retained buffers, current retained count, mutex, and stack. Each buffer owns an allocated `data` pointer and a back-pointer to its queue. No persistent state.

Dependencies and integration points: Uses `XrdOucStack`, `XrdOucQSItem`, `XrdSysMutex`, `sysconf(_SC_PAGESIZE)`, and `posix_memalign`. `XrdNet` UDP accept attaches these buffers to legacy peers.

Risks: `maxbuff` checks occur before locking in `Recycle`, allowing small races in retained count decisions. `Alloc` decrements `numbuff` when popping under lock, but allocation is also under lock and may block other users. `posix_memalign` is POSIX-specific; Windows support depends on platform abstraction elsewhere.

Test signals: Allocate/recycle under concurrency; verify alignment, size, maximum retained count, deletion beyond cap, destructor cleanup, and UDP datagram buffer lifetime through `XrdNetPeer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetBuffer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetBuffer.hh -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetBuffer.hh

Purpose: Declares `XrdNetBufferQ` and `XrdNetBuffer`, a small pooled buffer API for network datagrams.

Important APIs and types: `XrdNetBufferQ::Alloc`, `BuffSize`, `Recycle`, and `Set` manage queue behavior. `XrdNetBuffer` exposes public `data`, `dlen`, `BuffSize`, and `Recycle`.

Control flow: The header defines friend access so the queue can manipulate a buffer's private link and back-pointer; callers recycle through the buffer or queue.

State and persistence: Queue state is public for historical access and includes mutex, stack, size, alignment, and count fields. Buffer state is transient heap memory only.

Dependencies and integration points: Includes `XrdOucChain.hh` and `XrdSysPthread.hh`. Used by `XrdNet` UDP receive and likely legacy peer consumers.

Risks: Public mutable queue members allow callers to bypass locking. Buffer ownership is manual; using `Recycle` after the queue is destroyed would dereference a stale back-pointer. `data` is public and may be written past `BuffSize` by callers.

Test signals: Compile legacy callers that access public fields; run sanitizer tests around recycle-after-destroy, double recycle, and oversized writes in consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetBuffer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetCache.cc -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetCache.cc

Purpose: Implements a mutex-protected address-to-hostname DNS cache for `XrdNetAddrInfo`.

Important APIs and functions: Constructor, `Add`, `Find`, private `Expand`, `GenKey`, and `Locate` are implemented. Static `keepTime` controls entry expiry.

Control flow: `Add` generates an address key, locks, updates an existing entry or expands the hash table when the load threshold is crossed, then prepends a new entry. `Find` generates the key, locks, locates the item, returns a duplicated hostname if unexpired, or unlinks and deletes expired entries. `Expand` grows table size using a Fibonacci step and rehashes entries.

State and persistence: Process-local heap hash table, item chains, expiration times, and static keep time. The destructor intentionally does not clean the table because the cache is designed as a never-deleted singleton-style object.

Dependencies and integration points: Uses `XrdNetAddrInfo` for socket address access and `XrdSysMutex` for locking. `XrdNetAddr::SetCache` installs this cache for reverse lookups.

Risks: Constructor does not check `malloc` before `memset`. `nashnum` is not decremented when expired items are removed, so load accounting can drift upward. `Find` returns `strdup` memory that callers must own and free. Static `keepTime` changes affect all cache instances.

Test signals: Add/find IPv4 and IPv6 names; reject Unix/invalid families; expire entries; update existing entries; force expansion; run concurrent add/find; validate caller frees returned names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetCache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetCache.hh -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetCache.hh

Purpose: Declares the DNS cache backing optional reverse-name caching for network addresses.

Important APIs and types: Public `Add`, `Find`, and static `SetKT` form the cache interface. Private `anItem` stores IPv4/IPv6 key bytes, hash, hostname, expiry, and chain pointer.

Control flow: Header-defined `anItem` constructors duplicate hostnames and compute expiration from constructor arguments; `operator!=` compares hash, length, and key bytes.

State and persistence: Owns a heap hash table and chained entries for process lifetime. Static `keepTime` defines default TTL. No durable persistence.

Dependencies and integration points: Uses `XrdSysMutex` and is referenced by `XrdNetAddrInfo` through a static pointer. Intended initialization is through `XrdNetAddr::SetCache`.

Risks: Destructor comment states deletion loses memory, so ordinary RAII expectations do not hold. `SetKT` is static and not locked. `Find` ownership convention requires callers to free returned strings.

Test signals: Header compatibility with `XrdNetAddrInfo`; static TTL setting before cache use; leak checks should account for intentional process-lifetime cache behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetCache.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetCmsNotify.cc -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetCmsNotify.cc

Purpose: Sends cache-manager notification datagrams for file availability changes.

Important APIs and functions: Constructor builds destination path and message sender; destructor releases them. `Have`, `Gone`, and private `Send` format and transmit CMS commands.

Control flow: Construction derives an instance-specific `.olb` path and appends `olbd.notes` for server mode or `olbd.seton` otherwise, then creates an `XrdNetMsg`. `Have` emits `have  ` or `newfn `; `Gone` emits `gone  ` or `rmdid `; both append the path and newline. `Send` optionally serializes calls with a static mutex and 10 ms wait before calling `XrdNetMsg::Send`.

State and persistence: Per-object state is logger, `XrdNetMsg`, destination path, and pacing flag. Notifications are transient UDP/Unix socket messages; no persistent state is stored here.

Dependencies and integration points: Uses `XrdNetMsg`, `XrdOucUtils::InstName`, `XrdOucUtils::genPath`, `XrdSysTimer`, and `MAXPATHLEN`. Integrates file-server events with olbd/cms notification sockets.

Risks: Constructor uses fixed `char buff[1024]` with `strcpy`/`strcat` after `genPath`; long admin paths can overflow despite path commands later checking `MAXPATHLEN`. Static pacing mutex serializes all instances. Return mapping treats positive send timeouts as `-ETIMEDOUT`.

Test signals: Build destinations for service and non-service modes, with and without instance names; send `Have`/`Gone` for PFN and logical names; test long paths, send timeouts, noPace mode, and missing notification socket.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetCmsNotify.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetCmsNotify.hh -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetCmsNotify.hh

Purpose: Declares the CMS notification helper that reports file presence/removal events.

Important APIs and types: Public methods `Have` and `Gone`; option bits `isServ` and `noPace`; constructor and destructor. Private `Send` centralizes pacing and transport.

Control flow: Header defines a simple command-oriented API; implementation maps calls to text datagrams.

State and persistence: Holds raw pointers to `XrdSysError`, `XrdNetMsg`, and duplicated destination path plus pacing flag. No persistence beyond process memory.

Dependencies and integration points: Forward declares `XrdNetMsg` and `XrdSysError`. Used by server/cache-manager integration code that needs to notify olbd.

Risks: Raw pointer ownership is split: logger is non-owned, message and path are owned. Copying is not disabled, so accidental copies would double-free.

Test signals: Compile construction in CMS code; avoid copying in callers; verify option bits remain stable for configuration code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetCmsNotify.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetConnect.cc -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetConnect.cc

Purpose: Implements a static connect wrapper that can apply a caller-specified timeout without using process-wide alarms.

Important APIs and functions: `XrdNetConnect::Connect` accepts an fd, sockaddr, address length, and timeout seconds, returning zero or errno.

Control flow: With `tsec == 0`, it calls blocking `connect`. Otherwise it saves flags, sets non-blocking mode, calls `connect`, handles immediate success or non-`EINPROGRESS` error, polls for writability until timeout, reads `SO_ERROR`, restores flags, and returns the result.

State and persistence: No object state and no persistence; all state is local to the call and the socket fd flags.

Dependencies and integration points: Uses `fcntl`, `connect`, `poll`, `getsockopt`, socket headers, and `XrdSysPlatform` for platform errno/data macros. Called by lower-level socket connection setup.

Risks: The final restore call uses `F_SETFD` instead of `F_SETFL`, so file status flags may not be restored as intended. Negative `tsec` still enters timeout path and passes a negative poll timeout, effectively waiting indefinitely after changing to non-blocking. It does not check `fcntl` failures.

Test signals: Immediate connect, refused connect, in-progress success, timeout, interrupted poll, negative timeout, and flag restoration on sockets with preexisting nonblocking/other status flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetConnect.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetConnect.hh -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetConnect.hh

Purpose: Declares the static `XrdNetConnect` utility for timeout-capable socket connects.

Important APIs and types: Public static `Connect(int fd, const sockaddr *name, int namelen, int tsec=-1)` returns zero on success or errno on failure. Constructor/destructor are private to prevent instances.

Control flow: Header documents syscall-compatible semantics plus optional timeout behavior.

State and persistence: Stateless utility class; no persistence.

Dependencies and integration points: Includes platform socket headers and is consumed by `XrdNetSocket` or other low-level connection code.

Risks: Timeout unit is seconds in declaration comments but implementation passes milliseconds to `poll` after multiplying by 1000. Default `-1` means wait indefinitely in implementation, not "no timeout" in the `tsec == 0` branch.

Test signals: Compile on POSIX and Windows-gated builds; verify default timeout semantics match all callers' expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetConnect.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetIF.cc -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetIF.cc

Purpose: Implements interface discovery, advertised interface encoding, public/private IPv4/IPv6 routing selection, and destination construction for XRootD network routing.

Important APIs and functions: `Display`, static `GetIF` overloads, `GetDest`, `InDomain`, `Port`, `PortDefault`, `Routing`, `SetIF`, `SetIFNames`, `SetMsgs`, and `SetRPIPA` are public behavior. Private helpers `GenAddrs`, `GenIF`, `GetDomain`, `IsOkName`, `SetIFPP`, `SetIF64`, and `V4LinkLocal` implement routing tables.

Control flow: `GetIF` enumerates usable non-loopback interfaces with `getifaddrs`, filters configured names, excludes link-local addresses, formats addresses, and tags public/private/interface index metadata. `SetIF` sets the port/routing mode, derives interfaces from source DNS or an explicit list, categorizes each as public/private and v4/v6, then calls `GenIF`. `GenIF` writes compact `ifData` strings into a stack buffer, chooses names versus addresses, fills missing alternate protocol destinations from DNS, copies the compact table to heap storage, and relocates pointers. `SetIF64` fills dual-stack selection slots and mask bits.

State and persistence: Static state includes logger, local domain, configured public/private interface names, global routing mask vector, default routing type, default port, null slot, and private-IP resolution policy. Each instance owns an `ifBuff` heap block plus arrays of pointers into it, a port suffix, selected route, mask, and available interface.

Dependencies and integration points: Uses `XrdNetAddr`, `XrdNetAddrInfo`, `XrdNetIdentity`, `XrdNetUtils`, `XrdOucTList`, `XrdSysError`, `getifaddrs`, and network interface flags. It feeds locate/cms routing and client redirection decisions.

Risks: Static routing and interface-name settings are not thread-safe and are intended for initialization. `GenAddrs(const char*, bool)` contains `if (i > iN)` where `i < iN` was likely intended, so alternate DNS-derived addresses may never be accepted. Compact stack buffer writes rely on size assumptions and macros without explicit bounds checks beyond source formatting. `SetIF` decrements `ifCnt` while filling `netAdr`, making the explicit-list loop hard to reason about. `GetName` inline methods can dereference empty `ifNull` slots if callers skip `HasDest`.

Test signals: Enumerate interfaces with and without `getifaddrs`; filter configured public/private interface names; route under `netLocal`, `netSplit`, and `netCommon`; test public/private IPv4/IPv6 combinations, DNS fallback, explicit interface lists, missing interface warnings, domain membership, port suffix formatting, and small destination buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetIF.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetIF.hh -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetIF.hh

Purpose: Declares the interface-routing object that represents available public/private IPv4/IPv6 endpoints and chooses advertised destinations.

Important APIs and types: Defines `ifType`, interface availability bits, `netType`, `Display`, `GetDest`, `GetName`, static `GetIF` overloads, `GetIFType`, `HasDest`, `InDomain`, `Mask`, `Name`, `Port`, `Privatize`, `PortDefault`, `Routing`, `SetIF`, `SetIFNames`, `SetMsgs`, and `SetRPIPA`.

Control flow: Inline helpers select `ifAvail` when callers request `ifAny`, combine private/public bits, append port suffixes, and expose mask data used by routing clients.

State and persistence: Instances store compact interface data pointers, DNS-name flags, owned backing buffer, port suffix, port, route, mask, and available interface. Static config and routing state are shared process-wide. No durable persistence.

Dependencies and integration points: Forward declares `XrdNetAddrInfo`, `XrdOucTList`, `XrdSysError`, and `sockaddr`. Used by identity discovery, locate routing, and redirect destination construction.

Risks: `ifData` uses a flexible-array-like `char iVal[6]` pattern and depends on implementation allocation layout. Copying an `XrdNetIF` would copy pointers into the same backing buffer, but copy operations are not disabled. Inline `GetName` uses `strcpy` and assumes the caller supplies at least 256 bytes.

Test signals: ABI/compile tests for enum values used externally; copy-prevention or copy-safety tests; destination/name access for empty and fully populated interface tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetIF.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetIdentity.cc -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetIdentity.cc

Purpose: Computes and exposes the process-wide network identity: fully qualified host name and domain suffix.

Important APIs and functions: Static initializer `getMyFQN`, `XrdNetIdentity::Domain`, `FQN`, and `SetFQN` are implemented.

Control flow: Initialization clears static buffers, honors `XRDNET_IDENTITY` if set, otherwise calls `gethostname`, lowercases it, enumerates interfaces, reverse-resolves public/private addresses, prefers names matching the short hostname, falls back to old DNS lookup, then public/private IP address, then bare hostname. `Domain` and `FQN` return static values and optional diagnostic text. `SetFQN` overrides identity and recalculates the domain pointer.

State and persistence: Static `DNS_FQN`, `DNS_Domain` pointer into `DNS_FQN`, `DNS_Error`, and `FQN_DNS` hold identity for the process. No persistence outside environment input.

Dependencies and integration points: Uses `XrdNetIF::GetIF`, `XrdNetAddr`, `XrdNetAddrInfo`, `XrdOucUtils`, `XrdOucTList`, `gethostname`, and `XrdSysE2T`. Used by `XrdNetAddr` default constructor and interface domain checks.

Risks: Static initialization performs network/interface discovery, which can be costly or order-sensitive. `XRDNET_IDENTITY` branch returns `false` even though identity was set, making `FQN_DNS` false by design. `SetFQN` does not lowercase input. Static buffers are not protected against concurrent `SetFQN` and reads.

Test signals: Environment override, lowercase conversion, hostnames with and without domain, matching public/private reverse DNS, DNS failure fallbacks, no usable interfaces, `SetFQN`, and `Domain` pointer correctness after changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetIdentity.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetIdentity.hh -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetIdentity.hh

Purpose: Declares static access to the local network identity.

Important APIs and types: `Domain`, `FQN`, and `SetFQN` expose the domain suffix, fully qualified name, and override hook. Constructor/destructor are trivial.

Control flow: No logic in the header; implementation computes values at static initialization and returns stable pointers.

State and persistence: State is entirely static in the implementation. `SetFQN` changes process-local identity only.

Dependencies and integration points: Used by address and interface code to derive local defaults and domain membership.

Risks: Returned pointers refer to static mutable storage and can change after `SetFQN`. Callers must not free or modify them.

Test signals: Compile and call from early initialization paths; verify users tolerate empty domain string and diagnostic `eText`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetIdentity.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetMsg.cc -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetMsg.cc

Purpose: Implements UDP-style message sending to a default or per-call endpoint, with optional send readiness timeout and address refresh registration.

Important APIs and functions: Constructor, destructor, three `Send` overloads, `OK2Send`, and `retErr` helpers are implemented.

Control flow: Construction creates a UDP relay socket through `XrdNet`; with a default destination, it validates the address, connects the UDP socket, records the default destination string/fd, and optionally registers with `XrdNetRefresh`. `Send` with no destination uses connected `send`; with a destination uses `sendto`; with iovec uses `writev` for connected sockets or `sendmsg` for explicit destinations. `OK2Send` polls for writability when a nonnegative timeout is requested. Errors are logged and mapped to `-1` or positive timeout/block indicators.

State and persistence: Stores logger pointer, duplicated default destination, fd, `destOK`, and `isRefr`. No persistent state; address refresh registration is process-local.

Dependencies and integration points: Uses `XrdNet`, `XrdNetAddr`, `XrdNetPeer`, `XrdNetRefresh`, `XrdSysError`, POSIX `send`, `sendto`, `sendmsg`, `writev`, and `poll`. Used by CMS notification and other local datagram signaling.

Risks: Constructor registers refresh but never sets `isRefr = true`, so destructor will not unregister. If construction with a bad non-null destination returns early, `FD` may remain `-1` and `dfltDest` null; destructor still calls `close(FD)` and logs using possibly null destination. Timeout argument is documented as milliseconds and passed directly to `poll`; other networking APIs use seconds, so caller confusion is possible. `Send` with explicit destination requires same family as socket but only discovers mismatch at send time.

Test signals: Construct with null, valid, invalid, and refresh-enabled destinations; send default, explicit string, sockaddr, and iovec messages; simulate blocked socket, `EAGAIN`, fatal errors, and destructor after constructor failure; verify refresh unregister behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetMsg.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetMsg.hh -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetMsg.hh

Purpose: Declares a UDP message sender abstraction with default-destination and per-call-destination modes.

Important APIs and types: Three `Send` overloads support raw buffers, `XrdNetSockAddr`, and `iovec` payloads. Constructor accepts logger, optional destination, success flag, and refresh flag. Protected helpers manage readiness and error mapping.

Control flow: Header documents return semantics: negative for error, zero for sent, positive for timeout/not sent.

State and persistence: Holds non-owned logger, owned default destination string, socket fd, destination-valid flag, and refresh-registration flag. No persistence.

Dependencies and integration points: Includes socket headers and `XrdNetAddr.hh`; forward declares `XrdNetSockAddr` and `XrdSysError`. Used by notification and control-plane datagram senders.

Risks: Copy operations are not disabled, so copying would duplicate fd/string ownership. `FD` defaults to `-1`, but destructor behavior depends on implementation safeguards. `Send` uses `strlen` when length is zero, unsuitable for binary datagrams.

Test signals: Compile callers using all overloads; sanitizer tests for copy misuse, binary payloads with explicit length, and destructor after failed construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetMsg.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetOpts.hh -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetOpts.hh

Purpose: Defines shared bit flags and constants used by XrdNet and XrdNetSocket option handling.

Important APIs and definitions: Network flags include `XRDNET_NEWFD`, `SENDONLY`, `MULTREAD`, `NODNTRIM`, `DELAY`, `KEEPALIVE`, `NOCLOSEX`, `NOEMSG`, `NOLINGER`, `UDPSOCKET`, `FIFO`, `NORLKUP`, `USETLS`, and `SERVER`. Low-order-byte masks `XRDNET_BKLG` and `XRDNET_TOUT` encode backlog or timeout. Constants define default UDP buffer size, max backlog, and linger seconds.

Control flow: No runtime logic. Flags are ORed into bind, connect, accept, and socket setup calls.

State and persistence: None.

Dependencies and integration points: Included by `XrdNet`, `XrdNetSocket`, `XrdNetMsg`, and clients constructing network options.

Risks: Backlog and timeout share the same low-order byte and are interpreted according to server/client mode. Flags are preprocessor macros rather than scoped enum values, so accidental overlap or misuse is unchecked. Typos in comments can obscure operational meaning.

Test signals: Static assertions or compile checks for non-overlap of flag groups; integration tests for each option in socket setup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetOpts.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMark.cc -->
## sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMark.cc

Purpose: Implements parsing of SciTags packet-marking experiment/activity codes from CGI query strings.

Important APIs and functions: `XrdNetPMark::getEA(const char *cgi, int &ecode, int &acode)` extracts a combined `scitag.flow` value and splits it into experiment and activity IDs.

Control flow: The method initializes outputs to zero, searches for `scitag.flow=`, parses a decimal integer with `strtol`, accepts only values ending at `&` or end-of-string, checks the total ID range, and if valid shifts/masks into experiment and activity codes. It returns true whenever a syntactically present `scitag.flow` parameter was parsed to an integer terminator, even if out of range, preserving the specification that invalid values mark packets with zero.

State and persistence: Stateless; only caller-provided output references are modified.

Dependencies and integration points: Includes `XrdNetPMark.hh` for ID limits and bit masks. Adjacent PMark config and flow-file code use the parsed codes to begin packet marking handles.

Risks: `strstr` matches `scitag.flow=` anywhere, including inside another parameter name. Negative values and overflow rely on `strtol` behavior and range check. Duplicate parameters use the first occurrence only. The return value distinguishes parameter presence/syntax from absence, not validity of the code.

Test signals: Query strings with no parameter, valid min/max codes, out-of-range values, zero, negative, overflow, non-numeric suffix, duplicate parameters, prefix-name collisions, and parameters followed by `&`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMark.cc -->
