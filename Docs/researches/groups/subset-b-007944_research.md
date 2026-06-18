# subset-b-007944 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMark.hh -->
# sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMark.hh

## Purpose
`XrdNetPMark.hh` defines the abstract packet-marking interface used by XRootD protocols to attach SciTags/Firefly metadata to TCP flows. It separates mark discovery (`Begin()` from an authenticated `XrdSecEntity`) from mark propagation (`Begin()` from a peer address plus an existing handle) and exposes shared experiment/activity ID validation rules.

## Important APIs, Types, and Functions
`XrdNetPMark` is a non-owning service interface whose destructor notes that the service object cannot be deleted by callers. The nested `Handle` owns an application name string plus experiment and activity codes; `getEA(int&, int&)` returns valid codes, while `Valid()` accepts either the special HTTP-TPC zero/zero value or encoded values derived from the SciTags total ID range. Static `getEA(const char*, int&, int&)` parses CGI strings in the implementation file.

## Control Flow and State
Protocol code creates handles through `Begin()`, stores them for the lifetime of a marked transfer, and deletes the handle to end reporting. `Handle` state is simple heap-owned C string plus two integers. Copy construction duplicates `appName`, allowing derived handles such as `XrdNetPMarkFF` to preserve the base code values.

## Dependencies and Integration Points
The header forward-declares `XrdNetAddrInfo` and `XrdSecEntity`. `XrdNetPMarkCfg` implements the interface, xrootd/http/TPC modules consume it, and `XrdNetPMarkFF` derives from `Handle`.

## Risks and Test Signals
Risk centers on lifetime ownership and validity semantics: callers must delete returned handles but not the service object, and zero/zero is deliberately valid. Tests should cover CGI parsing, boundary values 65 and 65535, invalid total IDs that intentionally map to zero/zero when parsed, copy/destructor ownership, and protocol paths that pass handles between streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMark.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMarkCfg.cc -->
# sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMarkCfg.cc

## Purpose
`XrdNetPMarkCfg.cc` implements packet-marking configuration, runtime mark selection, and Firefly backend construction. It parses `pmark` directives, optionally loads SciTags JSON definitions, maps paths/VOs/users/roles to experiment and activity IDs, and creates `XrdNetPMarkFF` handles for marked sessions.

## Important APIs, Types, and Functions
The file defines internal `MapInfo`, `ExpInfo`, and `CfgInfo` types plus many static configuration globals under `XrdNetPMarkConfig`. Public entry points are `XrdNetPMarkCfg::Parse()`, `Config()`, and both `Begin()` overloads. Private helpers include `ConfigDefs()`, `ConfigPV2E()`, `ConfigRU2A()`, `FetchFile()`, `LoadFile()`, `LoadJson()`, `Extract()`, `Display()`, and `getCodes()`.

## Control Flow
`Parse()` accumulates directive state: definitions file or fetch command, failure policy, domain filtering, Firefly destination/origin ports, echo interval, path/VO-to-experiment mappings, user/role/default activity mappings, tracing, and enablement flags. `Config()` finalizes that state, validates Firefly configuration, loads definitions when mappings require them, opens `XrdNetMsg` UDP tunnels for collector/origin reporting, determines the local host/domain, and returns a new `XrdNetPMarkCfg` service only when marking remains enabled. `Begin(XrdSecEntity...)` filters by local/remote domain, obtains experiment/activity codes from `scitag.flow` or configured maps, allows a CGI `pmark.appname` override, then delegates to the address-based `Begin()`, which creates and starts an `XrdNetPMarkFF` handle.

## State and Persistence
Most runtime state is process-global and intentionally survives for server lifetime: experiment maps, path/VO maps, UDP message objects, scheduler/trace/error pointers, host/domain strings, and flags. Fetched defs files are temporarily written under `/tmp/XrdPMark-<pid>.json` and unlinked after load. `Cfg` exists only during configuration and is deleted by a local RAII guard in `Config()`.

## Dependencies and Integration Points
The implementation depends on `XrdNetMsg`, `XrdNetPMarkFF`, `XrdNetUtils`, `XrdOucJson`/nlohmann JSON, `XrdOucMapP2X`, `XrdOucProg`, `XrdOucStream`, `XrdSecEntity`, scheduler and tracing utilities. `XrdXrootdConfig` calls `Parse()` and `Config()`, then publishes the resulting `XrdNetPMark*` into environments used by xrootd, HTTP, and HTTP-TPC protocol code.

## Risks and Test Signals
Key risks are global mutable state, incomplete cleanup of `ffDest`/message objects, JSON schema assumptions that can throw, off-by-one ID boundary handling, and map lookup bugs around extracted VO/role tokens versus original strings. Domain filtering depends on reverse names and private-address detection. Tests should cover directive parse variants, missing or malformed defs files under `fail` and `nofail`, local/remote/any domains, CGI scitag precedence, default experiment/activity fallback, role/user mappings, fetched defs cleanup, Firefly collector/origin failure modes, and emitted diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMarkCfg.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMarkCfg.hh -->
# sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMarkCfg.hh

## Purpose
`XrdNetPMarkCfg.hh` declares the concrete configuration-backed implementation of `XrdNetPMark`. It is the public bridge between server configuration parsing and runtime packet-marking handles.

## Important APIs, Types, and Functions
The class overrides both `Begin()` overloads from `XrdNetPMark`, exposes static `Config()` for final service construction, and static `Parse()` for `pmark` directive parsing. Private static helpers mirror the implementation phases: definition loading, mapping setup, JSON processing, display, and code lookup.

## Control Flow and State
The header makes the lifecycle explicit: `Parse()` is called while reading configuration, `Config()` resolves and validates accumulated static state, and runtime callers use `Begin()` to obtain per-flow handles. The constructor is public and trivial, while the destructor is private, reinforcing that service instances are not meant to be deleted through ordinary callers.

## Dependencies and Integration Points
It includes `XrdNetPMark.hh` and forward-declares logging, scheduler, stream, map, and trace classes. It is included by xrootd configuration code and by its own implementation.

## Risks and Test Signals
The private destructor and static mutable configuration make ownership and reconfiguration behavior important. Tests should verify that parsing can happen before construction, that disabled configurations return null without leaks or fatal state, and that `Begin()` behavior matches the configured maps and flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMarkCfg.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMarkFF.cc -->
# sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMarkFF.cc

## Purpose
`XrdNetPMarkFF.cc` implements the Firefly packet-marking handle. It builds RFC5424-like syslog JSON messages for flow lifecycle start/end events, gathers TCP usage/RTT statistics, and sends messages to configured collector and/or origin UDP destinations.

## Important APIs, Types, and Functions
`Start()` initializes flow identity, UDP destinations, JSON header/tail fragments, and sends the start message. `Emit()` collects socket statistics, formats the lifecycle message, and sends through `netMsg` and/or `netOrg`. `SockStats()` uses Linux `TCP_INFO` when available. `getUTC()` formats UTC timestamps with microseconds. The destructor emits the end message and releases allocated state.

## Control Flow
`XrdNetPMarkCfg::Begin()` constructs the handle and calls `Start()`. `Start()` reads the socket FD from `XrdNetAddrInfo`, obtains peer and local addresses with `XrdNetUtils::GetSokInfo()`, prepares collector/origin routing, formats static JSON context, chooses source/destination orientation based on `http-put`, sets `fdOK`/`odOK`, and emits `"start"`. Destruction emits `"end"` only for still-valid reporting paths.

## State and Persistence
Per-flow state includes copied peer address for origin reporting, optional chained extra handle, tident, destination strings, JSON fragments, socket FD, and booleans tracking collector/origin viability. There is no disk persistence. The file references process-global PMark configuration objects owned by `XrdNetPMarkCfg.cc`.

## Dependencies and Integration Points
It depends on scheduler/error/trace globals, `XrdNetMsg`, `XrdNetAddrInfo`, `XrdNetUtils`, Linux TCP headers, and socket APIs. It is instantiated only by the PMark configuration implementation and consumed indirectly by xrootd/http/TPC callers through the base `Handle`.

## Risks and Test Signals
Important risks are JSON truncation, unescaped application names, platform-specific missing TCP counters, negative errno reporting mixups, use of `tcpi_bytes_acked` as sent bytes, and correctness of source/destination inversion for PUT-like traffic. Tests should use UDP capture or a fake `XrdNetMsg`, exercise IPv4/IPv6 sockets, collector-only/origin-only/both destinations, long application names, non-Linux behavior, and destructor end-message emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMarkFF.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMarkFF.hh -->
# sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMarkFF.hh

## Purpose
`XrdNetPMarkFF.hh` declares the Firefly-specific packet-marking handle type that extends `XrdNetPMark::Handle` with socket state, UDP reporting destinations, and lifecycle emission helpers.

## Important APIs, Types, and Functions
The public API is `Start(XrdNetAddrInfo&)`, `addHandle()` for optional chained ownership, the copy-from-handle constructor, and a virtual destructor. Private `sockStats` captures bytes received, bytes sent, and RTT split into milliseconds and microsecond remainder. Private helpers emit messages, format UTC timestamps, and query socket stats.

## Control Flow and State
The object is constructed with base experiment/activity/app state and a trace identity, started once against a connected socket, then destroyed to emit flow closure. It owns `mySad`, `xtraFH`, `oDest`, `ffHdr`, and `ffTail`.

## Dependencies and Integration Points
It includes `XrdNetPMark.hh` and forward-declares address and socket-address types. Only the PMark config backend should construct it, while protocols see it as a base `Handle`.

## Risks and Test Signals
Ownership is the main header-level risk: `addHandle()` transfers a raw pointer that the destructor deletes. Tests should verify start-before-destroy behavior, chained handle deletion, and safe cleanup when start partially fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMarkFF.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetPeer.hh -->
# sources/distributed-fs/xrootd/src/XrdNet/XrdNetPeer.hh

## Purpose
`XrdNetPeer.hh` defines the small peer descriptor used by `XrdNet` accept/connect paths and UDP message infrastructure to carry a file descriptor, network address, optional peer hostname, and optional datagram buffer.

## Important APIs, Types, and Functions
`XrdNetPeer` has public data members: `fd`, `Inet`, `InetName`, and `InetBuff`. The constructor initializes nullable pointers. The destructor frees `InetName` and recycles `InetBuff`.

## Control Flow and State
The type is a plain transfer container. Producers fill it during accepts or UDP setup, and consumers inspect it or pass it to helpers such as `XrdNetRefresh::Register()`. It owns only the hostname string and buffer pointer, not necessarily the socket descriptor.

## Dependencies and Integration Points
It includes `XrdNetBuffer.hh` and `XrdNetSockAddr.hh`. `XrdNet.cc` fills `XrdNetPeer` for accepts/connects; `XrdNetMsg.cc` uses it when registering refreshable UDP endpoints.

## Risks and Test Signals
Because members are public, ownership conventions must be respected. Tests should check destructor recycling, hostname duplication by producers, and no double-free when peers are copied or reused by higher layers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetPeer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetRefresh.cc -->
# sources/distributed-fs/xrootd/src/XrdNet/XrdNetRefresh.cc

## Purpose
`XrdNetRefresh.cc` maintains connected UDP sockets whose destination hostnames may resolve to new addresses over time. It periodically re-resolves registered peers and reconnects or replaces sockets when their destination IP changes.

## Important APIs, Types, and Functions
The file defines global `XrdNetSocketCFG::NetRefresh` and `udpRefr`, private `RefInfo`, `fd2Info`, `refMTX`, and scheduler/error pointers. Public methods are `Start()`, `Register()`, `UnRegister()`, and job `DoIt()`. Private helpers are `RegFail()`, `SetDest()`, and `Update()`.

## Control Flow
`Start()` installs logger/scheduler pointers, allocates the never-deleted job object, and schedules it. `Register()` validates hostname, FD, socket-ness, and `SOCK_DGRAM`, records `hostname:port` with a monotonically increasing instance ID, and rejects duplicate FDs. `Update()` copies the registry under lock, performs DNS resolution without holding the lock, then reacquires the lock and applies still-current updates. Same-family changes use `connect()` on the original FD; family changes create a new socket, connect it, and atomically replace the original FD with `dup2`. `DoIt()` calls `Update()` and reschedules.

## State and Persistence
All state is in memory: FD-to-host mapping, instance IDs to prevent stale updates, and scheduler registration. There is no disk persistence. Registered sockets outlive the refresh service and are unregistered explicitly.

## Dependencies and Integration Points
It depends on `XrdScheduler`, `XrdNetPeer`, `XrdNetAddr`, `XrdNetUtils::Compare()`, `XrdSysFD` wrappers, and pthread mutex helpers. `XrdNetMsg` registers UDP peers, and `XrdConfig` starts the service with configured refresh intervals.

## Risks and Test Signals
There is a likely logic issue: `Update()` treats anything other than `IPDiff` as a family exception before computing `newFam`, so `IPDFam` changes cannot reach `SetDest()` even though `SetDest()` supports them. Other risks include duplicate scheduling from both `DoIt()` and `Update()`, races with FD close/reuse, DNS failures causing noisy logs, and the typo-laden diagnostics. Tests should simulate DNS changes, same-family reconnects, family changes, unregister while update is pending, duplicate FD registration, invalid hostnames, and UDP-only validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetRefresh.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetRefresh.hh -->
# sources/distributed-fs/xrootd/src/XrdNet/XrdNetRefresh.hh

## Purpose
`XrdNetRefresh.hh` declares `XrdNetRefresh`, an `XrdJob` used to periodically refresh connected UDP destination addresses.

## Important APIs, Types, and Functions
`DoIt()` overrides the scheduler job callback. Static `Register()` and `UnRegister()` manage refreshable peer FDs. Static `Start()` initializes the singleton job. Private helpers validate registration failures, replace destinations, and run updates.

## Control Flow and State
The header presents the class as a singleton-style service with only static management methods plus a scheduler job instance. The constructor names the job `"NetRefresh"`.

## Dependencies and Integration Points
It forward-declares peer, scheduler, and error classes and inherits from `XrdJob`. It is started by core configuration and used by UDP message code.

## Risks and Test Signals
The API assumes callers register only connected UDP sockets and unregister before FD reuse. Tests should verify registration validation and scheduler invocation through `DoIt()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetRefresh.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetRegistry.cc -->
# sources/distributed-fs/xrootd/src/XrdNet/XrdNetRegistry.cc

## Purpose
`XrdNetRegistry.cc` implements pseudo-host registration for contact lists. Names beginning with `%` can expand into one or more real `host:port` entries, optionally rotating returned order across calls and supporting aliases.

## Important APIs, Types, and Functions
Private `regEntry` stores the pseudo-host name, host vector, parent alias pointer, reference counter, rotate flag, and per-entry RW lock. Public `Register()` overloads accept arrays or comma-separated strings. `GetAddrs()` resolves a registered pseudo-host through `XrdNetUtils`. Private `Resolve()` validates targets and `SetAlias()` creates aliases.

## Control Flow
Registration validates arguments and resolves every target unless resolution reports a dynamic host. String registration splits comma-separated hosts, requires ports, and delegates to array registration or alias creation. `GetAddrs()` finds the entry under a global mutex, increments the rotation counter if needed, takes an entry read lock, releases the global mutex, resolves the list with optional force behavior, then releases the entry lock.

## State and Persistence
Registry entries are process-global linked-list nodes and are never deleted. Updates replace an entry's host vector under its write lock. Aliases point to parent entries.

## Dependencies and Integration Points
It depends on `XrdNetAddr`, `XrdNetUtils`, and XrdSys locks. `XrdNetUtils::GetAddrs(std::string...)` dispatches `%` names here. `XrdSsiClient` registers multi-contact pseudo-hosts.

## Risks and Test Signals
`regEntry::Find()` compares `const char*` to `std::string` via overloaded equality and follows aliases, which should be tested carefully. Rotation uses an 8-bit `refs` counter exposed as unsigned int, so wraparound is expected. Tests should cover invalid names, missing ports, unresolved hosts, dynamic hosts, replacing entries, alias rules, rotation ordering, force resolution, concurrent get/update, and unregistered lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetRegistry.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetRegistry.hh -->
# sources/distributed-fs/xrootd/src/XrdNet/XrdNetRegistry.hh

## Purpose
`XrdNetRegistry.hh` declares the pseudo-host registry interface used to map `%`-prefixed names to concrete network contacts.

## Important APIs, Types, and Functions
`pfx` is the required `%` prefix. `GetAddrs()` expands a registered name into `XrdNetAddr` values and reports ordering partition info. Two `Register()` overloads accept either an array of host strings or a comma-separated string, with optional error text and rotation.

## Control Flow and State
The API is static, process-wide, and stateful. Successful registration makes later `XrdNetUtils::GetAddrs()` calls able to resolve pseudo-hosts.

## Dependencies and Integration Points
It includes `XrdNetUtils.hh` for `AddrOpts` and forward-declares `XrdNetAddr`. It is part of the address-resolution layer, not a standalone service.

## Risks and Test Signals
Callers must include ports in registered targets and must not expect unregister/delete support. Tests should verify error text for invalid arguments and integration through `XrdNetUtils`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetRegistry.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetSecurity.cc -->
# sources/distributed-fs/xrootd/src/XrdNet/XrdNetSecurity.cc

## Purpose
`XrdNetSecurity.cc` implements host/netgroup authorization for network endpoints. It supports exact IP caching, hostname pattern matching, and system netgroups.

## Important APIs, Types, and Functions
`AddHost()` adds exact resolvable hosts directly into the OK IP hash or stores wildcard/pattern hosts in `HostList`. `AddNetGroup()` records allowed netgroups. `Authorize()` resolves a string or evaluates an `XrdNetAddr`. `Merge()` combines another security object and deletes it. Private `addHIP()` resolves host IPs, while `hostOK()` caches and unlocks successful authorization.

## Control Flow
Authorization formats the address as normalized IP text, checks the OK cache under `okHMutex`, resolves a hostname if netgroups or host patterns are configured, checks netgroups with `innetgr()`, then checks the host pattern list. Successful checks add the IP to the OK cache and unlock through `hostOK()`. Failure unlocks and returns false.

## State and Persistence
State is in-memory per `XrdNetSecurity`: pattern list, netgroup linked list, OK IP hash cache, mutex, trace pointer, and booleans indicating whether pattern/netgroup checks are needed. No disk persistence.

## Dependencies and Integration Points
It depends on `XrdNetAddr`, `XrdNetUtils::GetAddrs()`, `XrdOucHash`, `XrdOucNList`, pthread locks, and platform `innetgr()` support. Core `Xrd`, CMS, and PSS configuration create and use these objects for peer authorization.

## Risks and Test Signals
Risks include lock discipline because `hostOK()` unlocks on behalf of callers, platform stubs where `innetgr()` always denies on MUSL/Windows, stale DNS-to-IP cache, and pattern resolution behavior for `+`. Tests should cover exact hosts, wildcard hosts, expanded hosts, netgroups, cache hits, merge duplicate netgroups, unknown host denial, and platform-specific netgroup stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetSecurity.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetSecurity.hh -->
# sources/distributed-fs/xrootd/src/XrdNet/XrdNetSecurity.hh

## Purpose
`XrdNetSecurity.hh` declares a compact authorization helper for host and netgroup based access control.

## Important APIs, Types, and Functions
Public methods add hosts/netgroups, authorize by string or `XrdNetAddr`, merge another instance, and set tracing. Private helpers cache successful hosts and resolve exact host IPs. The class owns an `XrdOucNList` host-pattern anchor, linked netgroup list, OK-host hash, mutex, trace pointer, and check flags.

## Control Flow and State
Instances are mutable policy accumulators. Configuration adds policy, then runtime authorization checks use the cached OK-host hash before slower hostname/netgroup checks.

## Dependencies and Integration Points
It includes XrdOuc hash/list helpers and XrdSys mutexes, and forward-declares address and trace classes. It is used by server and proxy subsystems.

## Risks and Test Signals
`Merge()` deletes its source pointer, so ownership must be explicit. Tests should include policy accumulation, cache behavior, merge ownership, and trace-enabled diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetSecurity.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetSockAddr.hh -->
# sources/distributed-fs/xrootd/src/XrdNet/XrdNetSockAddr.hh

## Purpose
`XrdNetSockAddr.hh` defines `XrdNetSockAddr`, a minimal union for IPv4, IPv6, and generic socket address views.

## Important APIs, Types, and Functions
The union exposes `sockaddr_in6 v6`, `sockaddr_in v4`, and `sockaddr Addr`. There are no functions.

## Control Flow and State
Callers fill one view and read another according to `sa_family`. The union is used to avoid the larger `sockaddr_storage` footprint where only IPv4/IPv6 are needed.

## Dependencies and Integration Points
It includes `<sys/socket.h>` and `<netinet/in.h>`. It is embedded in `XrdNetPeer`, passed through `XrdNetUtils`, and used by socket/refresh/PMark code.

## Risks and Test Signals
Risks are unsupported address families and code assuming `v6.sin6_port` and `v4.sin_port` layout interchangeably. Tests should validate IPv4/IPv6 formatting, comparison, encoding, and port extraction paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetSockAddr.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetSocket.cc -->
# sources/distributed-fs/xrootd/src/XrdNet/XrdNetSocket.cc

## Purpose
`XrdNetSocket.cc` implements a thin socket wrapper for creating, opening, accepting, configuring, and naming TCP/UDP/Unix sockets and local FIFOs.

## Important APIs, Types, and Functions
Core methods are the constructor, `Accept()`, `Close()`, `Create()`, `Detach()`, `Open()`, `Peername()`, `SockData()`, `SockName()`, `socketPath()`, and static `setOpts()`, `setWindow()`, `getWindow()`. Global keepalive tunables live in `XrdNetSocketCFG`.

## Control Flow
`Open()` resolves the endpoint into `SockInfo`, creates the descriptor, sets socket options, optionally sets window sizes, then binds/listens for servers or connects for clients, including timeout support for TCP. `Accept()` optionally polls before accepting and always uses XrdSys FD wrappers. `Create()` builds a filesystem path, creates a FIFO or Unix socket, and returns an owned wrapper. `setOpts()` handles close-on-exec yielding, UDP early return, linger, keepalive, Linux inherited TCP keepalive tunables, and `TCP_NODELAY`.

## State and Persistence
Each wrapper owns at most one FD plus `SockInfo`, an optional error route, and last error code. `Detach()` transfers FD ownership to the caller. Filesystem sockets/FIFOs persist as pathnames outside object lifetime unless unlinked by server setup.

## Dependencies and Integration Points
The implementation depends on `XrdNetAddr`, `XrdNetConnect`, `XrdNetOpts`, `XrdNetUtils::ProtoID()`, `XrdOucUtils::makePath()`, and XrdSys FD/platform helpers. It is used across CMS, XrdInet, XrdOfs eventing, admin sockets, bandwidth logging, and transfer daemons.

## Risks and Test Signals
Risks include platform differences for Unix sockets/FIFOs, close-on-exec semantics, partial option failure being nonfatal in `Open()`, use of `chmod()` after bind, path length handling, and `getWindow()` logging `"set socket RCVBUF"` in a getter. Tests should cover server/client TCP and UDP, Unix sockets, FIFO creation, timeout accept/connect, detach ownership, socket option failures, window sizing, path creation/access errors, and repeated `Open()` on busy wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetSocket.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetSocket.hh -->
# sources/distributed-fs/xrootd/src/XrdNet/XrdNetSocket.hh

## Purpose
`XrdNetSocket.hh` declares the socket wrapper API used throughout XRootD server components.

## Important APIs, Types, and Functions
The class provides construction from an optional error router and optional attached FD, static `Create()` and `socketPath()`, instance `Open()`, `Accept()`, `Close()`, `Detach()`, `LastError()`, `Peername()`, `SockData()`, `SockName()`, `SockNum()`, and static socket tuning helpers.

## Control Flow and State
The wrapper is single-FD: open once, close or detach before reuse. Destruction calls `Close()`. Error reporting is either routed through `XrdSysError` or stored in `ErrCode`.

## Dependencies and Integration Points
It includes `XrdNetAddr.hh` and platform socket headers. Consumers include XrdNet accept/connect logic, CMS admin sockets, XrdOfs event FIFOs, and xrootd admin setup.

## Risks and Test Signals
The API mixes ownership transfer and automatic close, so tests should assert `Detach()` prevents destructor close. Header-level contracts around path/port/flags combinations should be covered by integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetSocket.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetUtils.cc -->
# sources/distributed-fs/xrootd/src/XrdNet/XrdNetUtils.cc

## Purpose
`XrdNetUtils.cc` implements address comparison, encoding/decoding, host resolution, formatting, protocol/service lookup, network-stack detection, host pattern matching, port parsing, and nonblocking connect-with-timeout helpers.

## Important APIs, Types, and Functions
Major APIs include `Compare()`, `Decode()`, `Encode()`, three `GetAddrs()` overloads, `GetSokInfo()`, `Hosts()`, `IPFormat()`, `Match()`, `MyHostName()`, `NetConfig()`, `Parse()`, `Port()`, `ProtoID()`, `ServPort()`, `SetAuto()`, `Singleton()`, and `ConnectWithTimeout()`. Private `hpSpec`, `FillAddr()`, `GetAInfo()`, `GetHints()`, `GetHostPort()`, `setET()`, and `SetSockBlocking()` provide shared implementation.

## Control Flow
Resolution starts by parsing host/port, choosing addrinfo hints from `AddrOpts`, resolving with `getaddrinfo()`, filtering unsupported/link-local entries, partitioning IPv4/IPv6 or mapped addresses, applying optional rotation, and filling `XrdNetAddr` objects. `%`-prefixed string specs are delegated to `XrdNetRegistry`. Formatting wraps `XrdNetAddr`. `ConnectWithTimeout()` flips a socket nonblocking, calls `connect()`, polls for writability, checks `SO_ERROR`, restores blocking mode, and closes the FD on failure.

## State and Persistence
Static `autoFamily` and `autoHints` capture preferred address-family behavior, initialized from interface inspection. Other state is stack/local. There is no disk persistence.

## Dependencies and Integration Points
The file depends on libc networking APIs, `XrdNetAddr`, `XrdNetIdentity`, `XrdNetIF`, `XrdNetRegistry`, `XrdOucTList`, `XrdOucUtils`, and XrdSys platform/error helpers. It is a common dependency for clients, servers, PMark Firefly, refresh, registry, security, and config parsers.

## Risks and Test Signals
Several details deserve tests: `GetSokInfo()` uses `htons()` where `ntohs()` would normally be expected for extracting a network-order port; `ConnectWithTimeout()` closes the caller's FD on failure, which must match caller expectations; multi-host `GetAddrs()` with `force=true` can silently skip bad entries; address-family ordering and mapped IPv4 behavior are subtle; service-name lookup depends on system databases. Tests should cover IPv4/IPv6/mapped round trips, port parsing modes, registry dispatch, ordering flags, rotation, link-local filtering, `prefAuto`, `Match()` wildcard and `+` expansion, `Singleton()`, connect timeout success/failure, and FD blocking restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetUtils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdNet/XrdNetUtils.hh

## Purpose
`XrdNetUtils.hh` declares the central network utility API for address operations, host resolution, formatting, protocol detection, parsing, and timed connects.

## Important APIs, Types, and Functions
It defines `IPComp`, `AddrOpts` with enum operators, port sentinel constants, formatting flags, `NetProt`, and `NetType`. Public static methods cover compare, encode/decode, `GetAddrs()` overloads, socket info, host lists, IP formatting, pattern matching, local FQDN, network configuration, host spec parsing, port/protocol/service lookup, automatic family selection, singleton detection, and `ConnectWithTimeout()`.

## Control Flow and State
All behavior is static. Hidden static fields `autoFamily` and `autoHints` drive `prefAuto` resolution. The header documents port-handling modes, ordering semantics, caller ownership of allocated arrays/lists, and FD sign conventions for local versus peer socket addresses.

## Dependencies and Integration Points
It includes STL types and `XrdOucEnum.hh`, forward-declares `XrdNetAddr`, `XrdOucTList`, and `XrdNetSockAddr`, and is included widely across network, client, server, storage, and config code.

## Risks and Test Signals
The API has many sentinel and ownership contracts. Tests should focus on each documented mode: allocated array deletion, vector clearing on failure, `ordn` semantics, `PortInSpec`/`NoPortRaw`, order flags, onlyUDP service lookup, FD sign behavior, and timeout-connect ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdNet/XrdNetUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdOfs/CMakeLists.txt

## Purpose
This CMake file wires the XrdOfs implementation into the `XrdServer` target and builds the `XrdOfsPrepGPI` module plugin.

## Important APIs, Types, and Functions
The build declarations add many `XrdOfs*.cc` and `XrdOfs*.hh` files to `XrdServer` with `target_sources()`. It sets `XrdOfsPrepGPI` to `XrdOfsPrepGPI-${PLUGIN_VERSION}`, creates a `MODULE` library from `XrdOfsPrepGPI.cc`, links it privately to `XrdUtils`, and installs it to `${CMAKE_INSTALL_LIBDIR}`.

## Control Flow and State
At configure/generate time, CMake attaches source files to an already-defined target and creates the plugin target. There is no runtime control flow or persistent application state in this file, but build output names depend on `PLUGIN_VERSION`.

## Dependencies and Integration Points
The file assumes `XrdServer`, `XrdUtils`, `PLUGIN_VERSION`, and install directory variables have been defined by parent CMake logic. XrdOfs code integrates with filesystem, TPC, events, stats, and security headers listed here.

## Risks and Test Signals
Risks are build-graph omissions and plugin install/link errors. Tests should include full configure/build, verifying `XrdServer` compiles with all listed sources, the module file name includes the plugin version, `XrdOfsPrepGPI` links only required private dependencies, and install rules place the module in the expected library directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOfs/CMakeLists.txt -->
