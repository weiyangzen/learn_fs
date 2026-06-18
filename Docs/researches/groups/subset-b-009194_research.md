# subset-b-009194 research

Grouped research for Syncthing connection, dialer, discovery, events, and basic filesystem files. Each section title preserves the source path and is wrapped in the required markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/limiter_test.go -->
## sources/sync-backup/syncthing/lib/connections/limiter_test.go

Purpose: Tests the connection bandwidth limiter behavior around per-device receive/send limits, dynamic config updates, LAN bypass behavior, and aggregate waiter limit selection.

Important APIs/types/functions: `initConfig` constructs a `config.Wrapper` with four devices and starts its service loop; `newDeviceConfiguration` creates device configs from wrapper defaults; tests exercise `newLimiter`, limiter internal maps, `limitedWriter.Write`, `totalWaiter.Limit`, and helper `checkActualAndExpected`. `countingWriter` measures write fragmentation.

Control flow: The tests initialize fixed `protocol.DeviceID` values, mutate device `MaxRecvKbps` and `MaxSendKbps`, wait for config change propagation, then compare limiter maps against expected `rate.Limiter` limits. Writer tests copy random bytes through `limitedWriter` in limited, LAN-bypassed, fully-unlimited, and mixed-limiter modes to verify chunking and fast paths.

State and persistence: State is in-memory test config, limiter maps, and atomic LAN-limit flags. No filesystem persistence is involved beyond using `/dev/null` as config path.

Dependencies and integration points: Uses `config.Wrapper` subscription delivery, `events.NoopLogger`, `protocol.DeviceID`, and `golang.org/x/time/rate`. It indirectly validates assumptions used by `service.handleHellos`, which wraps accepted connections with limiter readers/writers.

Risks: Random rate values can make failures harder to reproduce, though assertions compare only limits and write-count ranges. The tests inspect unexported limiter internals, so internal refactors need test updates.

Test signals: Strong coverage for limiter initialization, add/remove/update propagation, writer fast path, LAN exemption, and combined waiter minimum-rate semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/limiter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/metrics.go -->
## sources/sync-backup/syncthing/lib/connections/metrics.go

Purpose: Defines the Prometheus gauge for active connections per remote device.

Important APIs/types/functions: `metricDeviceActiveConnections` is a `promauto.NewGaugeVec` under namespace `syncthing`, subsystem `connections`, name `active`, labelled by `device`. `registerDeviceMetrics` pre-creates a label series for a device.

Control flow: Registration is passive at package initialization. Runtime call sites in `service.CommitConfiguration` register new devices and delete removed-device labels; `deviceConnectionTracker.accountAddedConnection` increments and `accountRemovedConnection` decrements.

State and persistence: Metrics live in the process-global Prometheus registry. No durable state is written.

Dependencies and integration points: Depends on `prometheus` and `promauto`. Integrates with connection tracking and config device lifecycle.

Risks: Incorrect add/remove accounting can leave negative or stale gauges. Label cardinality is bounded by configured devices but still depends on config churn.

Test signals: No direct tests in this file; behavior is indirectly exercised by connection tracking tests elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/mocks/service.go -->
## sources/sync-backup/syncthing/lib/connections/mocks/service.go

Purpose: Counterfeiter-generated fake for the `connections.Service` interface.

Important APIs/types/functions: `Service` fake implements `AllAddresses`, `ExternalAddresses`, `ListenerStatus`, `ConnectionStatus`, `NATType`, and `Serve`, plus call counters, argument capture, default returns, per-call returns, stubs, and `Invocations`.

Control flow: Each fake method locks its method mutex, records invocation metadata, snapshots the stub/default return, unlocks, then either invokes the stub or returns configured values.

State and persistence: Maintains in-memory call slices, return structs, per-call maps, and invocation maps protected by mutexes. No persistence.

Dependencies and integration points: Imports `connections` for status entry types and satisfies `connections.Service`; imports `context` for `Serve`.

Risks: Generated fakes can drift if the source interface changes and `go generate` is not rerun. `Invocations` shallow-copies slices and interface values, so tests should avoid mutating captured mutable return data.

Test signals: Compile-time assertion `var _ connections.Service = new(Service)` detects interface drift at build time.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/mocks/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/quic_dial.go -->
## sources/sync-backup/syncthing/lib/connections/quic_dial.go

Purpose: Implements QUIC outbound dialing when QUIC support is enabled.

Important APIs/types/functions: Registers `quic`, `quic4`, and `quic6` schemes in `init`. `quicDialer.Dial` resolves UDP addresses, chooses a reusable listener `*quic.Transport` from the registry when available, dials QUIC with TLS, opens a stream, computes LAN/WAN priority, and returns an `internalConn`. `quicDialerFactory` builds dialers from config priorities and reconnect interval.

Control flow: `Dial` default-fills missing ports, maps URL scheme to UDP network, resolves remote address, reuses a registered unspecified transport if possible, otherwise creates an ephemeral UDP packet conn, applies a 10-second operation timeout, dials, opens the first stream, and wraps the session/stream in `quicTlsConn`.

State and persistence: Uses transient QUIC sessions and optional ephemeral packet conns. Reused transports are held in the shared registry by listeners.

Dependencies and integration points: Depends on `quic-go`, `config`, `registry`, `protocol`, and common connection service dialer interfaces. Integrated through the package `dialers` map.

Risks: Resource cleanup is critical when dialing or opening the stream fails, especially for ephemeral packet conns. Reuse selection depends on registry predicate `transportConnUnspecified`.

Test signals: No direct tests in this file; coverage depends on connection integration tests and QUIC-enabled builds.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/quic_dial.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/quic_listen.go -->
## sources/sync-backup/syncthing/lib/connections/quic_listen.go

Purpose: Implements QUIC listeners, address advertisement, STUN/NAT detection, and accepted QUIC stream handoff.

Important APIs/types/functions: `quicListener` implements `genericListener` and STUN callbacks. `serve` binds UDP, creates a `quic.Transport`, starts STUN service over non-QUIC packets, registers the transport, listens for sessions, accepts a stream, and sends an `internalConn`. `WANAddresses`, `LANAddresses`, `NATType`, and callbacks expose dynamic addresses.

Control flow: Startup resolves and binds the listen address, starts STUN, registers transport for outbound reuse, starts QUIC listener, creates NAT mapping, records local address, then loops accepting sessions. Each accepted session must provide a stream within `quicOperationTimeout`; failures close the session and continue. Repeated accept errors restart via supervisor after threshold.

State and persistence: Holds current external STUN address, NAT type in `atomic.Uint64`, NAT mapping, local address, and mutex-protected address state. No durable state.

Dependencies and integration points: Integrates `quic-go`, `stun`, `nat.Service`, registry, `lanChecker`, event address notifier, and service listener supervision.

Risks: Concurrent address callbacks and listener teardown require careful locking. QUIC/STUN share one UDP socket through `transportPacketConn`; incorrect packet handling can break discovery or connectivity. NAT address changes must trigger notifications or discovery announcements become stale.

Test signals: No direct file tests; risks are covered indirectly by listener integration and platform network tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/quic_listen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/quic_misc.go -->
## sources/sync-backup/syncthing/lib/connections/quic_misc.go

Purpose: Provides shared QUIC configuration, URL-scheme network mapping, QUIC-to-TLS connection adapter, and packet-conn adapter for STUN over QUIC transport.

Important APIs/types/functions: `quicConfig` sets idle timeout and keepalive. `quicNetwork` maps `quic4`/`quic6` to UDP networks. `quicTlsConn` embeds `*quic.Conn` and `*quic.Stream` and implements `Close` and `ConnectionState`. `transportConnUnspecified` selects reusable unspecified transports. `transportPacketConn` adapts `quic.Transport` to `net.PacketConn`.

Control flow: `quicTlsConn.Close` closes stream, QUIC connection, and optional created packet conn, returning the first error. `transportPacketConn.ReadFrom` uses an optional stored read deadline to create a context and calls `ReadNonQUICPacket`; `WriteTo` forwards via transport.

State and persistence: Keeps optional created packet connection and atomic-value read deadline. No persistence.

Dependencies and integration points: Used by QUIC dial/listen, registry preferred transport selection, and STUN service.

Risks: Deadline handling is read-only and write deadline is ignored. Close ordering may surface only the first error. The adapter must remain compatible with `quic-go` non-QUIC packet APIs.

Test signals: No direct tests; exercised by QUIC listener/dialer runtime paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/quic_misc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/quic_unsupported.go -->
## sources/sync-backup/syncthing/lib/connections/quic_unsupported.go

Purpose: Registers QUIC schemes as unsupported when built with `noquic`.

Important APIs/types/functions: `errNotInBuild` wraps `errUnsupported`; `init` registers `invalidListener` and `invalidDialer` for `quic`, `quic4`, and `quic6`.

Control flow: At package initialization, QUIC schemes remain recognized but their factories return an unsupported-build error.

State and persistence: Mutates package-global dialer/listener maps. No persistence.

Dependencies and integration points: Depends on build tag `noquic` and invalid factory types elsewhere in the connections package. Integrates with `getDialerFactory` and `getListenerFactory` so config can contain QUIC addresses without panicking.

Risks: Build-tag divergence can hide QUIC regressions from noquic builds and vice versa.

Test signals: Compile-time build coverage only unless noquic tests exercise factory validity paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/quic_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/registry/registry.go -->
## sources/sync-backup/syncthing/lib/connections/registry/registry.go

Purpose: Tracks listener-owned reusable connection objects by scheme so outbound dials can reuse local listen ports/transports for better NAT traversal.

Important APIs/types/functions: `Registry` holds `available map[string][]interface{}` guarded by `sync.Mutex`. `New`, `Register`, `Unregister`, and `Get` are the public API.

Control flow: `Register` appends items under a scheme. `Unregister` removes the first matching item by interface equality. `Get` scans registered schemes whose key is a prefix of the requested scheme, evaluates a caller-supplied preferred predicate, and picks the first available or a preferred item, breaking preferred ties toward shorter scheme names.

State and persistence: Process-local mutable registry only.

Dependencies and integration points: Uses `sliceutil.RemoveAndZero`. TCP listeners register `*net.TCPAddr`; QUIC listeners register `*quic.Transport`; TCP/QUIC dialers query the registry.

Risks: Uses `interface{}` and equality, so only comparable values can be unregistered safely. Prefix matching is intentional but broad; new schemes need care to avoid accidental compatibility.

Test signals: `registry_test.go` covers empty lookup, prefix compatibility, unregister semantics, duplicates, short-scheme preference, and a benchmark.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/registry/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/registry/registry_test.go -->
## sources/sync-backup/syncthing/lib/connections/registry/registry_test.go

Purpose: Verifies registry matching, preferred selection, unregister behavior, duplicate handling, and lookup cost.

Important APIs/types/functions: `TestRegistry`, `TestShortSchemeFirst`, and `BenchmarkGet`. Helper `want` returns preferred predicates over integer test items.

Control flow: Tests register several schemes and values, query compatible schemes, unregister entries, check nil after removal, verify duplicate removal removes only one entry, and ensure shorter scheme wins when preference does not matter.

State and persistence: In-memory test registry only.

Dependencies and integration points: Uses `net.TCPAddr` in benchmark to match real TCP listener registry use.

Risks: Tests model items as ints, so they do not cover non-comparable item misuse or concurrent access.

Test signals: Direct unit tests provide strong signals for intended prefix and tie-breaking behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/registry/registry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/relay_dial.go -->
## sources/sync-backup/syncthing/lib/connections/relay_dial.go

Purpose: Implements outbound connections through Syncthing relay servers.

Important APIs/types/functions: `relayDialer.Dial` obtains relay invitations and joins relay sessions. `relayDialerFactory` registers scheme `relay`, sets relay reconnect interval, and validates `RelaysEnabled`.

Control flow: Dial asks the relay for an invitation for the target device, joins the session, applies TCP options and traffic class, chooses TLS client/server mode based on invitation `ServerSocket`, performs timed TLS handshake, and returns a WAN relay `internalConn`.

State and persistence: No persistent state. Relay session and TLS connection are transient.

Dependencies and integration points: Uses relay `client`, dialer TCP helpers, config relay options, TLS certificates, and the common connection service dialer path.

Risks: Relay direction determines TLS role; wrong handling breaks handshakes. Relay is always WAN and does not allow separate LAN priority. Failure to set TCP options is fatal here while traffic class errors are debug-only.

Test signals: No direct tests; relay integration tests elsewhere must cover invitation/session paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/relay_dial.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/relay_listen.go -->
## sources/sync-backup/syncthing/lib/connections/relay_listen.go

Purpose: Implements relay listener clients that maintain relay-server connections and accept relay invitations as incoming Syncthing connections.

Important APIs/types/functions: Registers `relay`, `dynamic+http`, and `dynamic+https` listener schemes. `relayListener.serve` creates relay client and runs it. `handleInvitations` joins sessions, performs TLS, and emits `internalConn`. `WANAddresses`, `LANAddresses`, and `Error` expose relay client status.

Control flow: Listener creates a relay client, stores it under lock, starts invitation handling, and blocks in `clnt.Serve`. Invitation handling receives relay invitations, joins sessions, sets TCP options/traffic class, chooses TLS role from `ServerSocket`, handshakes, then sends a relay-server connection to the service. Every 10 seconds it detects dynamic relay URI changes and notifies address listeners.

State and persistence: Keeps current relay client behind a mutex and uses service error state. No durable state.

Dependencies and integration points: Integrates relay client library, service address-change notifications, config relay enablement, TLS config, and connection handoff channel.

Risks: Dynamic relay URI polling is coarse and pointer comparison can miss equal-value object changes unless client returns a distinct pointer. Relay client errors are surfaced through `Error`, so UI/API consumers depend on correct delegation.

Test signals: No direct tests in this file.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/relay_listen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/service.go -->
## sources/sync-backup/syncthing/lib/connections/service.go

Purpose: Central connection manager that supervises listeners, dials configured devices, performs TLS/device identity validation and Hello exchange, tracks active connections, updates metrics, emits address-change events, and exposes connection/listener status.

Important APIs/types/functions: Public `Service` interface; `NewService`; status structs; `handleConns`, `handleHellos`, `connect`, `dialDevices`, `resolveDialTargets`, `CommitConfiguration`, `AllAddresses`, `ExternalAddresses`, `ListenerStatus`, `ConnectionStatus`, `NATType`; helpers `getDialerFactory`, `getListenerFactory`, `tlsTimedHandshake`, `IsAllowedNetwork`, `dialParallel`, `validateIdentity`; `nextDialRegistry`; `deviceConnectionTracker`; `newConnectionID`.

Control flow: Construction subscribes to config, starts listeners/NAT service, and adds three service loops. Listener/dialer paths feed `internalConn` into `handleConns`, which verifies TLS protocol/certificate count, rejects self/ignored/paused/over-limit/disallowed/low-priority connections, then exchanges BEP Hello asynchronously. `handleHellos` processes the exchange, calls model `OnHello`, validates configured certificate name, wraps traffic limiters, creates a protocol connection, tracks it, schedules redial on close, and hands it to the model. The connect loop repeatedly resolves configured device addresses, consults discovery for `dynamic`, filters by allowed networks and priority cutoffs, schedules backoff in `nextDialRegistry`, sorts dial queues, and dials targets in parallel with global and per-device semaphores.

State and persistence: Process state includes listener maps/tokens, status maps, dial-now channel and per-device set, next-dial cooldown registry, limiter, NAT service, and tracked protocol connections/wanted counts. No direct disk persistence; config wrapper is external.

Dependencies and integration points: Integrates config subscriptions, discovery lookups, NAT/UPnP/PMP providers, relay/TCP/QUIC factories, protocol connection/model interfaces, Prometheus metrics, event logger, TLS, semaphores, and suture supervision.

Risks: This is highly concurrent: listener map locks, connection tracker locks, dial cancellation, Hello goroutines, and config callbacks must stay ordered. Identity validation is security-sensitive. Priority/upgrade logic can churn connections if thresholds or desired connection negotiation are wrong. `IsAllowedNetwork` only supports resolvable IP/CIDR rules and ignores malformed CIDRs. Timer handling in connection loop must avoid leaks and rapid loops.

Test signals: Existing tests outside this item cover fixup/allowed networks/dialer selection/connection status/registry cleanup/connection establishment. Files in this item add limiter and registry unit coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/structs.go -->
## sources/sync-backup/syncthing/lib/connections/structs.go

Purpose: Defines shared connection abstractions, transport metadata, listener/dialer interfaces, model interface, address-change notification, and dial target wrapper.

Important APIs/types/functions: `tlsConn`, `internalConn`, `connType`, `newInternalConn`, `internalConn` methods (`Close`, `Type`, `IsLocal`, `Priority`, `Crypto`, `Transport`, `EstablishedAt`, `ConnectionID`, `String`, `LogValue`), `dialerFactory`, `commonDialer`, `genericDialer`, `listenerFactory`, `ListenerAddresses`, `genericListener`, `Model`, `onAddressesChangedNotifier`, and `dialTarget`.

Control flow: Dialers/listeners wrap raw TLS-like connections in `internalConn`. `Close` sets a short write deadline before closing to avoid blocking on TLS close alerts. `Transport` enriches transport with IPv4/IPv6 suffix when the remote address can be parsed. `commonDialer.Priority` uses `lanChecker` to choose LAN/WAN priorities. Notifier invokes registered callbacks with listener addresses or clears them on shutdown.

State and persistence: `internalConn` carries per-connection metadata and a post-Hello connection ID. Notifier stores callback slices. No persistence.

Dependencies and integration points: Used throughout all transport adapters and the central service; imports config, registry, NAT, protocol, stats, suture, and osutil.

Risks: `Crypto` assumes TLS suite/version maps contain the negotiated values; unknown values format empty names. Callback list is not mutex-protected, so registration is expected before concurrent notifications.

Test signals: Indirectly tested by connection establishment, status, and logging behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/structs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/tcp_dial.go -->
## sources/sync-backup/syncthing/lib/connections/tcp_dial.go

Purpose: Implements outbound TCP BEP dialing.

Important APIs/types/functions: Registers `tcp`, `tcp4`, and `tcp6` dialers. `tcpDialer.Dial` performs port fixup, registry-aware dialing, TCP option setup, traffic class setup, TLS client handshake, LAN/WAN priority calculation, and `internalConn` construction. `tcpDialerFactory` builds config-derived dialers.

Control flow: Dial wraps the context in a 10-second timeout, dials with `dialer.DialContextReusePortFunc`, applies socket options, wraps as TLS client, performs timed handshake, checks locality from the actual remote address, and returns a TCP client connection.

State and persistence: Transient socket/TLS state only. Registry may supply local listen address reuse.

Dependencies and integration points: Depends on dialer package, registry, config options, TLS config, and service dial loop.

Risks: Setting TCP options failure is logged but not fatal; TLS handshake failure closes the TLS connection. Reuse-port behavior varies by platform.

Test signals: Covered indirectly by TCP connection integration tests and dialer helper behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/tcp_dial.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/tcp_listen.go -->
## sources/sync-backup/syncthing/lib/connections/tcp_listen.go

Purpose: Implements TCP BEP listeners, NAT port mapping, LAN/WAN address advertisement, and accepted connection handoff.

Important APIs/types/functions: `tcpListener` implements `genericListener`; `serve` binds with reuse-port control, registers local address, creates NAT mapping, accepts TCP, performs TLS server handshake, computes priority, and sends `internalConn`. `WANAddresses` and `LANAddresses` expose mapped and local addresses. `tcpListenerFactory` creates listeners.

Control flow: Listener resolves and binds the configured address, replaces port zero with actual port for notifications, registers the listen address for outbound reuse, starts NAT mapping, and loops with one-second accept deadlines for cancellation responsiveness. Non-timeout accept failures back off and restart after a threshold. Accepted sockets get TCP options, optional traffic class, TLS handshake, and LAN/WAN priority before handoff.

State and persistence: Holds NAT mapping and actual local address behind mutex; registry entries live while serving. No persistent state.

Dependencies and integration points: Uses net listeners, dialer socket controls, NAT service, registry, config, `lanChecker`, and service listener supervisor.

Risks: Address advertisement must account for `:0`, unspecified binds, NAT mappings, and reuse-port punch-through zero-port announcements. Accept failure threshold controls listener restart behavior.

Test signals: Indirect connection establishment tests cover basic listener/dialer behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/tcp_listen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/util.go -->
## sources/sync-backup/syncthing/lib/connections/util.go

Purpose: Shared URL/address helpers for connection transports and discovery advertisement.

Important APIs/types/functions: `fixupPort`, `getURLsForAllAdaptersIfUnspecified`, `getHostPortsForAllAdapters`, `resolve`, `maybeReplacePort`, and `portMappingURIs`.

Control flow: `fixupPort` fills default ports for missing or empty URL ports. Adapter expansion resolves a listen URI, checks for unspecified address and nonzero port, enumerates interface networks, and builds host:port URLs for private/link-local addresses. `maybeReplacePort` substitutes actual bound port for configured zero port. `portMappingURIs` converts NAT external addresses into listener URLs and adds zero-IP variants for DMZ-like cases.

State and persistence: Stateless helpers, except for current interface address lookup.

Dependencies and integration points: Used by TCP/QUIC listeners and dialers; depends on `nat` and `osutil`.

Risks: URL parsing and IPv6 bracket handling are subtle. Interface enumeration failures silently suppress LAN address expansion. Mutating `addr.IP` while building zero-IP NAT variants relies on value semantics of loop variables.

Test signals: Connection tests cover `fixupPort`; listener behavior indirectly covers advertisement helpers.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/dialer/control_unix.go -->
## sources/sync-backup/syncthing/lib/dialer/control_unix.go

Purpose: Detects and applies `SO_REUSEPORT` on Unix-like systems excluding Solaris and Windows.

Important APIs/types/functions: Package variable `SupportsReusePort`; `init` probes socket option support; `ReusePortControl` is a `net.ListenConfig`/`net.Dialer` control hook.

Control flow: Init creates an IPv4 TCP socket, attempts `unix.SetsockoptInt(SO_REUSEPORT)`, logs support, and flips `SupportsReusePort`. Control hook no-ops if unsupported; otherwise calls `RawConn.Control` to set the option.

State and persistence: Process-global boolean only.

Dependencies and integration points: Used by TCP listener and registry-aware TCP dialer to improve NAT punch-through and stable ports.

Risks: Probe behavior varies by OS/kernel. Control hook must not fail on unsupported systems because listener startup depends on it.

Test signals: No direct tests; platform-specific build and runtime networking exercise this path.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/dialer/control_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/dialer/control_unsupported.go -->
## sources/sync-backup/syncthing/lib/dialer/control_unsupported.go

Purpose: Solaris fallback for reuse-port support.

Important APIs/types/functions: `SupportsReusePort = false`; `ReusePortControl` returns nil.

Control flow: Always disables port reuse and allows callers to proceed without special socket options.

State and persistence: Constant package-level state.

Dependencies and integration points: Satisfies the same API used by TCP listener/dialer on unsupported platforms.

Risks: NAT punch-through quality may be lower on this platform, but correctness is maintained.

Test signals: Build-tag compile coverage only.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/dialer/control_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/dialer/control_windows.go -->
## sources/sync-backup/syncthing/lib/dialer/control_windows.go

Purpose: Windows implementation of reuse-port semantics using `SO_REUSEADDR`.

Important APIs/types/functions: `SupportsReusePort = true`; `ReusePortControl` sets `syscall.SO_REUSEADDR` via `RawConn.Control`.

Control flow: Control hook applies socket option and logs control or socket-option errors before returning them.

State and persistence: Package-level support flag only.

Dependencies and integration points: Used by TCP listener/dialer for port reuse on Windows.

Risks: Windows `SO_REUSEADDR` semantics differ from Unix `SO_REUSEPORT`; behavior is accepted intentionally but can affect binding conflicts.

Test signals: Build-tag compile coverage and Windows network tests elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/dialer/control_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/dialer/debug.go -->
## sources/sync-backup/syncthing/lib/dialer/debug.go

Purpose: Defines the dialer package debug logger adapter.

Important APIs/types/functions: Package variable `l = slogutil.NewAdapter("Dialing connections")`.

Control flow: None beyond package initialization.

State and persistence: Process-global logger adapter only.

Dependencies and integration points: Used throughout dialer internals for proxy/fallback/socket diagnostic logging.

Risks: None beyond consistent logger naming.

Test signals: No tests needed; compile-time use validates symbol.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/dialer/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/dialer/empty_test.go -->
## sources/sync-backup/syncthing/lib/dialer/empty_test.go

Purpose: Placeholder test file to make Go report 0% coverage instead of no coverage for the dialer package.

Important APIs/types/functions: No executable tests or APIs.

Control flow: None.

State and persistence: None.

Dependencies and integration points: Keeps package `dialer` test target present.

Risks: Can mask absence of meaningful unit tests for proxy/fallback/reuse-port logic.

Test signals: Explicitly indicates missing dialer tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/dialer/empty_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/dialer/internal.go -->
## sources/sync-backup/syncthing/lib/dialer/internal.go

Purpose: Initializes proxy support and implements SOCKS/HTTP/HTTPS proxy dialing internals while preserving intended remote address semantics.

Important APIs/types/functions: Package init registers `socks`, `http`, and `https` proxy dialers and may replace `http.DefaultTransport`. `socksDialerFunction`, `httpDialerFunction`, `httpProxyDialer.DialContext`, `bufferedConn`, `dialerConn`, `newDialerAddr`, and `fallbackAddr` are key internals.

Control flow: Init reads proxy environment and `ALL_PROXY_NO_FALLBACK`, registers proxy dialer types, configures default HTTP transport through this package when a proxy is detected, and logs proxy state asynchronously. HTTP proxy dialing connects to proxy, optionally TLS-wraps HTTPS proxy, sends CONNECT with optional Basic auth, validates 200 OK, and returns a buffered connection preserving any bytes already read. Proxy connections are wrapped in `dialerConn` so `RemoteAddr` reports the target rather than the proxy.

State and persistence: Process-global proxy registration/default transport changes and `warnCleartextProxyAuthOnce`. No durable state.

Dependencies and integration points: Used by public dial functions and global discovery HTTP clients. Integrates with `golang.org/x/net/proxy` and `net/http`.

Risks: Global `http.DefaultTransport` mutation affects other package users. Cleartext proxy auth is security-sensitive but warns once. The target address fudge is required for LAN checks and relay logic; removing it would alter connection classification.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/dialer/internal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/dialer/public.go -->
## sources/sync-backup/syncthing/lib/dialer/public.go

Purpose: Public dialer helpers for TCP socket options, traffic class, proxy-aware dialing, reuse-port dialing, and racing fallback strategies.

Important APIs/types/functions: `SetTCPOptions`, `SetTrafficClass`, `DialContext`, `DialContextReusePortFunc`, and `dialTwicePreferFirst`; error `errUnexpectedInterfaceType`.

Control flow: TCP options set linger, Nagle/NoDelay, keepalive period, and keepalive. Traffic class sets IPv4 TOS and IPv6 traffic class. Proxy dialing chooses proxy direct/no-fallback/fallback paths. Reuse-port dialing skips local-address reuse when a proxy is configured, otherwise queries the connection registry for an unspecified TCP listen address and races reuse vs non-reuse dialing. `dialTwicePreferFirst` starts the preferred dial immediately and the fallback after a delay, returning first success preference and closing late fallback success.

State and persistence: Stateless except registry reads and proxy environment.

Dependencies and integration points: Core dependency for TCP transport and global announce client; uses `registry.Registry`, `ipv4`, `ipv6`, and `proxy`.

Risks: Racing dials must close losing connections to avoid leaks. Traffic class returns IPv4 error before IPv6 error, which may matter on dual-stack sockets. `SetTCPOptions` accepts only raw TCP or `dialerConn`.

Test signals: Only placeholder coverage in this package; behavior is mainly integration-tested through connections.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/dialer/public.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/cache.go -->
## sources/sync-backup/syncthing/lib/discover/cache.go

Purpose: Provides cache primitives and metadata for discovery finders.

Important APIs/types/functions: `cachedFinder` wraps a `Finder` with positive/negative cache durations, per-finder `cache`, and optional suture token. `cachedError` can override negative cache time. `cache` exposes `Set`, `Get`, and `Cache`.

Control flow: Methods lock a mutex for map access; `Cache` returns a shallow copy of the map for safe iteration by callers.

State and persistence: In-memory map keyed by `protocol.DeviceID` to `CacheEntry`. No disk persistence.

Dependencies and integration points: Used by discovery manager to cache global lookup successes/failures and to aggregate local finder caches.

Risks: `Cache` returns `CacheEntry` values whose `Addresses` slices are not deep-copied. Callers should not mutate returned slices.

Test signals: `cache_test.go` exercises manager lookup cache aggregation and nonblocking child error access during slow lookups.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/cache_test.go -->
## sources/sync-backup/syncthing/lib/discover/cache_test.go

Purpose: Tests discovery manager cache aggregation, address uniqueness/sorting, and lookup concurrency behavior.

Important APIs/types/functions: `setupCache`, `TestCacheUnique`, `TestCacheSlowLookup`, `fakeDiscovery`, and `slowDiscovery`.

Control flow: Tests create a manager with local/global announcement disabled, manually add fake finders under lock, call `Lookup`, and compare sorted unique results. Slow lookup test starts a lookup that holds the read lock path and asserts `ChildErrors` returns quickly.

State and persistence: In-memory fake manager and fake finders only.

Dependencies and integration points: Uses config wrapper, events noop logger, registry, and manager internals.

Risks: Tests call unexported `addLocked`, so they are coupled to manager internals.

Test signals: Good coverage for multi-finder deduplication and avoiding lock contention between lookup and child error reporting.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/debug.go -->
## sources/sync-backup/syncthing/lib/discover/debug.go

Purpose: Defines discovery package debug logger adapter.

Important APIs/types/functions: Package variable `l = slogutil.NewAdapter("Remote device discovery")`.

Control flow: None beyond initialization.

State and persistence: Process-global logger adapter only.

Dependencies and integration points: Used by local/global/manager discovery files for debug diagnostics.

Risks: None beyond logger naming.

Test signals: Compile-time use validates symbol.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/discover.go -->
## sources/sync-backup/syncthing/lib/discover/discover.go

Purpose: Declares discovery interfaces and shared cache entry structure.

Important APIs/types/functions: `Finder`, `CacheEntry`, `FinderService`, and `AddressLister`.

Control flow: No implementation logic; these contracts define lookup, error reporting, string identity, cache exposure, service lifecycle, and address-list sources.

State and persistence: `CacheEntry` includes exported addresses and unexported timing/found/instance metadata used by package internals.

Dependencies and integration points: Used by connection service for `discover.Finder`, discovery manager/finder implementations, and address listers such as the connection service.

Risks: Unexported fields in `CacheEntry` mean external packages can see addresses but not reconstruct fully valid cache entries.

Test signals: Interface conformance is exercised by manager, local, global, and generated mocks.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/discover.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/doc.go -->
## sources/sync-backup/syncthing/lib/discover/doc.go

Purpose: Package documentation for local and global Syncthing device discovery protocols.

Important APIs/types/functions: No code APIs; documents announcement JSON, direct/relay address semantics, certificate-authenticated identity, response status codes, reannounce/retry headers, GET lookup query format, and rate-limit behavior.

Control flow: Describes protocol flows for HTTPS POST announcements and HTTPS GET queries.

State and persistence: Documentation only; describes server-side registry behavior conceptually.

Dependencies and integration points: Serves as the protocol reference for `global.go` and `local.go` implementations.

Risks: Documentation can drift from implementation or protocol server behavior.

Test signals: No executable tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/global.go -->
## sources/sync-backup/syncthing/lib/discover/global.go

Purpose: Implements global discovery client for announcing local addresses to HTTPS discovery servers and querying remote device addresses.

Important APIs/types/functions: `globalClient`, `httpClient`, `announcement`, `serverOptions`, `lookupError`, `NewGlobal`, `Lookup`, `Serve`, `sendAnnouncement`, `parseOptions`, `queryBool`, `idCheckingHTTPClient`, `errorHolder`, `contextClient`, identity helpers, and `http2EnabledTransport`.

Control flow: `NewGlobal` parses server options, builds separate announce and query HTTP clients, optionally wraps them with discovery-server device ID verification, and sets initial error when announcement is required. `Lookup` adds `device` query parameter, performs GET, handles non-200 and `Retry-After`, and decodes addresses. `Serve` debounces listen-address-change events and calls `sendAnnouncement`; repeated flip-flopping suppresses endless resets. `sendAnnouncement` marshals sanitized external addresses, POSTs them, follows `Retry-After` or `Reannounce-After`, and updates error state.

State and persistence: Holds server URL, address lister, clients, no-announce/no-lookup flags, and mutex-protected current error. No persistent cache; manager wraps it with cache.

Dependencies and integration points: Uses TLS cert identity, dialer proxy/reuse-port dialing, events `ListenAddressesChanged`, registry, HTTP/2 transport, and relay address sanitization from local discovery.

Risks: TLS `InsecureSkipVerify` is enabled for `?insecure` or explicit ID mode, with manual device ID verification only when `id` is supplied. HTTP is allowed only for insecure no-announce lookups. Timer reset/debounce logic must avoid missed announcements and permanent flip-flop suppression.

Test signals: `global_test.go` covers option parsing, HTTP restrictions/lookups, HTTPS certificate modes, ID verification, lookup timeout, and successful announcement.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/global.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/global_test.go -->
## sources/sync-backup/syncthing/lib/discover/global_test.go

Purpose: Tests global discovery URL option parsing, HTTP/HTTPS security behavior, lookup, timeout, server identity validation, and announcements.

Important APIs/types/functions: `TestParseOptions`, `TestGlobalOverHTTP`, `TestGlobalOverHTTPS`, `TestGlobalAnnounce`, `testLookup`, `fakeDiscoveryServer`, and `fakeAddressLister`.

Control flow: Tests construct local HTTP/TLS servers, exercise `NewGlobal` with different query options, perform lookups, validate error/success modes, start discovery service for announcement, and wait for error state to clear.

State and persistence: In-memory fake server captures POST body. No disk persistence.

Dependencies and integration points: Uses `tlsutil.NewCertificateInMemory`, registry, events noop logger, and real HTTP servers.

Risks: Timeout test is skipped in short mode and depends on request timeout behavior. Fake server returns an intentionally odd address string, so assertions are tightly coupled to current parser permissiveness.

Test signals: Strong security and protocol behavior coverage for global discovery client.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/global_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/local.go -->
## sources/sync-backup/syncthing/lib/discover/local.go

Purpose: Implements LAN-local device discovery using IPv4 broadcast or IPv6 multicast beacons.

Important APIs/types/functions: `localClient`, constants `BroadcastInterval`, `CacheLifeTime`, `Magic`, `v13Magic`; `NewLocal`, `Lookup`, `announcementPkt`, `sendLocalAnnouncements`, `recvAnnouncements`, `registerDevice`, `filterUndialableLocal`, and `sanitizeRelayAddresses`.

Control flow: `NewLocal` chooses broadcast for empty host or multicast otherwise, adds beacon, receive, and send services to a supervisor. Sender builds protobuf announcement packets with instance ID and sanitized dialable addresses, then sends on periodic or forced ticks. Receiver validates magic, rejects old/invalid packets, unmarshals announcements, skips self, registers devices, and forces an announcement when a new device appears. Registration reconstructs unspecified advertised addresses from packet source and records cache entries.

State and persistence: Holds local cache, beacon service, per-run random instance ID in sender, broadcast tick channels, and event logger. Cache entries expire after three broadcast intervals.

Dependencies and integration points: Uses generated `discoproto`, beacon package, event `DeviceDiscovered`, address lister from connection service, and protocol device IDs.

Risks: Address filtering/reconstruction must handle IPv4/IPv6 scheme compatibility and avoid leaking relay tokens. `filterUndialableLocal` mutates the input slice in place. Forced broadcast channel is unbuffered and best-effort.

Test signals: `local_test.go` covers instance ID packet changes/new-device detection and undialable address filtering.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/local.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/local_test.go -->
## sources/sync-backup/syncthing/lib/discover/local_test.go

Purpose: Tests local discovery instance ID semantics and local address filtering.

Important APIs/types/functions: `TestLocalInstanceID`, `TestLocalInstanceIDShouldTriggerNew`, `padDeviceID`, and `TestFilterUndialable`.

Control flow: Tests create local clients, generate announcements with different instance IDs, register synthetic device announcements from a UDP source, and compare new-device boolean outcomes. Filtering test feeds valid and invalid TCP/QUIC URLs and compares retained list.

State and persistence: In-memory local client/cache only.

Dependencies and integration points: Uses generated discovery proto, protocol IDs, fake address lister, and events noop logger.

Risks: Tests do not fully exercise beacon send/receive network I/O. Filtering assertions depend on current `net.ResolveTCPAddr` behavior.

Test signals: Good coverage for cache newness trigger and address safety filtering.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/local_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/manager.go -->
## sources/sync-backup/syncthing/lib/discover/manager.go

Purpose: Aggregates multiple discovery mechanisms, manages their lifecycle from configuration, caches lookup results, and exposes combined cache/error state.

Important APIs/types/functions: Public `Manager` interface; `manager` struct; `NewManager`; `serve`; `addLocked`; `removeLocked`; `Lookup`; `ChildErrors`; `Cache`; and `CommitConfiguration`.

Control flow: Manager subscribes to config in `serve` and reconciles finders in `CommitConfiguration`. Global servers are added with five-minute positive and one-minute negative caches; local IPv4/IPv6 discovery is added without manager-level caching. `Lookup` scans finders under read lock, uses valid positive/negative cache entries, performs finder lookups when needed, caches success/failure, deduplicates and sorts addresses, and returns nil error. `Cache` merges positive manager cache entries with child finder caches.

State and persistence: Holds a supervised map of finder identities to `cachedFinder` entries under RW mutex. No durable state.

Dependencies and integration points: Integrates config options, global/local discovery constructors, event logger, registry, address lister, TLS cert, and suture supervisor.

Risks: `Lookup` holds `m.mut.RLock` while calling finder `Lookup`, so config updates requiring write lock can wait on slow discovery; tests only check `ChildErrors` read path. Negative-cache errors are swallowed from the public return, so callers see empty addresses/nil error.

Test signals: Cache tests cover aggregation and ChildErrors during slow lookups; global/local tests cover child implementations.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/mocks/manager.go -->
## sources/sync-backup/syncthing/lib/discover/mocks/manager.go

Purpose: Counterfeiter-generated fake for `discover.Manager`.

Important APIs/types/functions: Fake `Manager` implements `Cache`, `ChildErrors`, `Error`, `Lookup`, `Serve`, and `String`, with stubs, call counters, argument accessors, default/per-call returns, and `Invocations`.

Control flow: Each method records invocation under locks, copies mutable slice args where needed, calls a stub when configured, otherwise returns configured values.

State and persistence: In-memory fake state protected by per-method mutexes. No persistence.

Dependencies and integration points: Imports `discover` and `protocol`; compile-time assertion satisfies `discover.Manager`.

Risks: Generated code can drift from interface changes. Return maps/slices are not deep-copied, so tests can accidentally share mutable state.

Test signals: Compile-time conformance assertion is the main guard.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/discover/mocks/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/events/debug.go -->
## sources/sync-backup/syncthing/lib/events/debug.go

Purpose: Defines event package debug logger adapter.

Important APIs/types/functions: Package variable `dl = slogutil.NewAdapter("Event generation and logging")`.

Control flow: None beyond package initialization.

State and persistence: Process-global logger adapter only.

Dependencies and integration points: Used by event logger and subscription methods for diagnostics.

Risks: None beyond logger naming.

Test signals: Compile-time use validates symbol.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/events/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/events/events.go -->
## sources/sync-backup/syncthing/lib/events/events.go

Purpose: Provides process-wide event logging, subscription, polling, buffering, event type string/JSON handling, and noop logger implementations.

Important APIs/types/functions: `EventType` constants and `AllEvents`; `String`, `MarshalText`, `UnmarshalJSON`, `UnmarshalEventType`; interfaces `Logger`, `Subscription`, `BufferedSubscription`; structs `logger`, `Event`, `subscription`, `bufferedSubscription`; `NewLogger`, `Serve`, `Log`, `sendEvent`, `Subscribe`, `unsubscribe`, `Poll`, `NewBufferedSubscription`, `Since`, `Error`, `NoopLogger`.

Control flow: `Logger.Serve` serializes all event delivery, subscription creation, and unsubscription through channels. `Log` enqueues an event. `sendEvent` assigns global IDs, checks subscription masks, assigns per-subscription IDs, delivers with a 15 ms timeout, and records created/delivered/dropped metrics. `Subscribe` schedules subscription creation on the logger goroutine. `Poll` resets a per-subscription timer and waits for event or timeout. Buffered subscriptions continuously drain an underlying subscription into a ring buffer and `Since` waits until newer subscription IDs are available.

State and persistence: In-memory subscription slices, per-subscription next IDs, global ID counter, event channels, timers, ring buffers, condition variable, and metrics. No durable persistence.

Dependencies and integration points: Used throughout Syncthing for API events; discovery and connection services log `DeviceDiscovered` and `ListenAddressesChanged`. Uses suture service interface, `syncutil.TimeoutCond`, Prometheus metrics.

Risks: `Log` blocks when the logger service is not running and event channel fills. Slow subscribers can drop events after timeout by design. `Poll` is not safe for concurrent calls on the same subscription. Buffered ring buffers overwrite old events, so clients must poll often enough.

Test signals: `events_test.go` covers subscription masks, timeouts, IDs, buffering, JSON unmarshal, unsubscribe behavior, contention, and benchmarks.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/events/events.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/events/events_test.go -->
## sources/sync-backup/syncthing/lib/events/events_test.go

Purpose: Tests event logger lifecycle, delivery semantics, buffering, IDs, JSON unmarshalling, and unsubscribe contention.

Important APIs/types/functions: `setupLogger`; tests `TestNewLogger`, `TestSubscriber`, `TestTimeout`, `TestEventBeforeSubscribe`, `TestEventAfterSubscribe`, `TestEventAfterSubscribeIgnoreMask`, `TestBufferOverflow`, `TestUnsubscribe`, `TestGlobalIDs`, `TestSubscriptionIDs`, `TestBufferedSub`, `TestSinceUsesSubscriptionId`, `TestUnmarshalEvent`, `TestUnsubscribeContention`; benchmarks `BenchmarkBufferedSub`, `BenchmarkLogEvent`.

Control flow: Tests run a logger service under context, create subscriptions, log events, poll or read channels, and assert event type/data/ID/error behavior. Contention test runs many listener and sender goroutines, then ensures listener unsubscribe completes in reasonable time.

State and persistence: In-memory logger/subscriptions only. `runningTests` is set to stabilize timer branches.

Dependencies and integration points: Exercises Prometheus metric side effects implicitly but does not assert metrics.

Risks: Timing-sensitive tests use one-second/minute thresholds and may be affected by heavily loaded CI, though stabilization hooks reduce flakiness.

Test signals: Strong direct coverage of public event bus behavior and concurrency stress.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/events/events_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/events/metrics.go -->
## sources/sync-backup/syncthing/lib/events/metrics.go

Purpose: Defines Prometheus counters for event creation, delivery, and drops.

Important APIs/types/functions: `metricEvents` is a `CounterVec` under namespace `syncthing`, subsystem `events`, name `total`, labelled by event type and state. State constants are `created`, `delivered`, and `dropped`.

Control flow: Counter is registered at package init. `events.go` increments created when processing logged events, delivered when sent to a subscriber, and dropped on subscriber timeout.

State and persistence: Process metrics only.

Dependencies and integration points: Depends on Prometheus client and event logger delivery path.

Risks: High-cardinality risk is low because event type/state are bounded. Metrics can reveal dropped event pressure but are only accurate if logger service is running.

Test signals: Event tests exercise increments indirectly, but metrics values are not asserted.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/events/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/events/mocks/buffered_subscription.go -->
## sources/sync-backup/syncthing/lib/events/mocks/buffered_subscription.go

Purpose: Counterfeiter-generated fake for `events.BufferedSubscription`.

Important APIs/types/functions: Fake `BufferedSubscription` implements `Mask` and `Since`, with stubs, counters, argument capture, default/per-call returns, and `Invocations`.

Control flow: Methods lock, record invocation, snapshot stub/returns, unlock, and return stub/default values. `Since` copies the input event slice argument for later inspection.

State and persistence: In-memory fake state protected by mutexes. No persistence.

Dependencies and integration points: Imports `events` and `time`; compile-time assertion satisfies `events.BufferedSubscription`.

Risks: Generated fake drift on interface changes; returned slices are not deep-copied.

Test signals: Compile-time conformance assertion.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/events/mocks/buffered_subscription.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs.go -->
## sources/sync-backup/syncthing/lib/fs/basicfs.go

Purpose: Implements the core `basic` filesystem by rooting relative paths under a configured OS directory and delegating most operations to the Go `os` package.

Important APIs/types/functions: `FilesystemTypeBasic`; filename errors; `OptionJunctionsAsDirs`; `BasicFilesystem`; `newBasicFilesystem`; `rooted`; methods `Chmod`, `Chtimes`, `Mkdir`, `MkdirAll`, `Lstat`, `RemoveAll`, `Rename`, `Stat`, `DirNames`, `Open`, `OpenFile`, `Create`, `Walk`, `Glob`, `Usage`, `Type`, `URI`, `Options`, `SameFile`, `underlying`; `basicFile`; `basicFileInfo`; `longFilenameSupport`; `WatchEventOutsideRootError`.

Control flow: Registration installs a factory for type `basic`. Construction normalizes root, expands tilde, absolutizes when possible, applies Windows long-path prefix, initializes user/group caches, and applies options. Operations call `rooted` to canonicalize and join paths safely before invoking OS calls. `OpenFile` adds platform `alwaysOpenFlags`; `Lstat` delegates to platform-specific `underlyingLstat`; `Glob` unroots matches; `SameFile` only compares basic file info values.

State and persistence: Holds root path, options, junction behavior, and one-hour user/group caches. It manipulates real filesystem state under the root via OS calls.

Dependencies and integration points: Implements Syncthing `Filesystem`; integrates with platform-specific `basicfs_*` files, disk usage via gopsutil, build flags, and higher-level walking/copy/xattr code.

Risks: Root canonicalization is security-sensitive; any bypass could escape the shared folder. `RemoveAll` and `Rename` operate on rooted paths and therefore have high destructive impact if rooting is wrong. `Walk` intentionally returns not implemented because walking is handled elsewhere.

Test signals: Broader `basicfs_test.go` outside this item covers many operations; platform files in this subset add targeted behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_copy_range.go -->
## sources/sync-backup/syncthing/lib/fs/basicfs_copy_range.go

Purpose: Adapts platform copy-range implementations that require `basicFile` and exposes helpers for syscall file descriptor access.

Important APIs/types/functions: `copyRangeImplementationBasicFile`, `copyRangeImplementationForBasicFile`, `withFileDescriptors`, and `unwrap`.

Control flow: The adapter unwraps layered `File` values, type-checks both ends as `basicFile`, returns `ENOTSUP` otherwise, and calls the platform implementation. `withFileDescriptors` obtains `SyscallConn` for both files and nests `Control` callbacks to pass raw descriptors. `unwrap` repeatedly follows local `unwrap() File` interfaces.

State and persistence: Stateless helper logic, but platform implementations mutate destination file contents.

Dependencies and integration points: Used by Linux/Windows copy-range backends registered in sibling files and by the filesystem copy-range registry elsewhere.

Risks: Nested `Control` callbacks must not block in unsafe ways. Only `basicFile` is supported, so wrapped files must expose `unwrap` correctly or optimized copy falls back.

Test signals: Copy-range tests are outside this subset; behavior is indirectly validated by filesystem copy operations.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_copy_range.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_copy_range_copyfilerange.go -->
## sources/sync-backup/syncthing/lib/fs/basicfs_copy_range_copyfilerange.go

Purpose: Linux copy-range backend using `copy_file_range`.

Important APIs/types/functions: `init` registers `CopyRangeMethodCopyFileRange`; `copyRangeCopyFileRange` loops until requested bytes are copied.

Control flow: For each loop, calls `unix.CopyFileRange` with explicit source/destination offsets so file offsets are not changed. Zero bytes with nil error is treated as unexpected EOF. `EAGAIN` is retryable; positive byte counts reduce remaining size.

State and persistence: Mutates destination file content and advances local offset variables only.

Dependencies and integration points: Linux build tag; uses `withFileDescriptors` adapter and copy-range method registry.

Risks: Kernel/filesystem support varies; errors should trigger fallback by higher-level copy-range selection. Large sizes are cast to `int` per syscall call.

Test signals: No direct tests here; copy-range integration tests should cover fallback behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_copy_range_copyfilerange.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_copy_range_duplicateextents.go -->
## sources/sync-backup/syncthing/lib/fs/basicfs_copy_range_duplicateextents.go

Purpose: Windows copy-range backend using `FSCTL_DUPLICATE_EXTENTS_TO_FILE` block cloning.

Important APIs/types/functions: Registers `CopyRangeMethodDuplicateExtents`; constants/vars `availableClusterSize`, `GiB`, `fsctlDuplicateExtentsToFile`; struct `duplicateExtentsData`; functions `copyRangeDuplicateExtents`, `wrapError`, `callDuplicateExtentsToFile`, and `roundUp`.

Control flow: Ensures destination is large enough, verifies source length, validates 4 KiB boundary requirements, clones whole GiB chunks, then tries tail clone rounded to 64 KiB and falls back to 4 KiB. DeviceIoControl performs the actual clone.

State and persistence: May truncate destination to fit target range and clone filesystem extents. No other persistence.

Dependencies and integration points: Windows build tag; uses Windows syscalls and copy-range registry.

Risks: Filesystem constraints are strict; nonaligned offsets and unsupported filesystems return errors/fallback. `wrapError` maps a Windows severity error to `ENOTSUP`; other platform errors pass through.

Test signals: No direct tests in this subset; requires Windows/filesystem-specific integration coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_copy_range_duplicateextents.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_copy_range_ioctl.go -->
## sources/sync-backup/syncthing/lib/fs/basicfs_copy_range_ioctl.go

Purpose: Linux reflink copy-range backend using clone ioctls.

Important APIs/types/functions: Registers `CopyRangeMethodIoctl`; `copyRangeIoctl` performs whole-file or range clone through `unix.IoctlFileClone`/`IoctlFileCloneRange`.

Control flow: Checks source size, converts a range ending exactly at source EOF to length zero per ioctl semantics, optimizes whole-file clone when offsets and length are zero, otherwise fills `unix.FileCloneRange` and invokes ioctl.

State and persistence: Creates copy-on-write clone extents in destination file.

Dependencies and integration points: Linux build tag; uses `withFileDescriptors` and copy-range registry.

Risks: Requires filesystem reflink support. EOF and zero-length semantics must be exact to avoid cloning more than intended.

Test signals: No direct tests here; copy-range integration should validate fallback.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_copy_range_ioctl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_copy_range_sendfile.go -->
## sources/sync-backup/syncthing/lib/fs/basicfs_copy_range_sendfile.go

Purpose: Linux/Solaris copy-range backend using `sendfile`.

Important APIs/types/functions: Registers `CopyRangeMethodSendFile`; `copyRangeSendFile` copies bytes from source fd to destination fd with explicit source offset.

Control flow: Ensures destination size, records and restores current destination offset, seeks destination to requested offset, loops `syscall.Sendfile`, treats zero-without-error as EOF, retries `EAGAIN`, and subtracts positive byte counts.

State and persistence: Writes destination bytes and temporarily changes destination file offset, restoring it before return.

Dependencies and integration points: Linux/Solaris build tags; copy-range registry and descriptor helper.

Risks: Offset restoration is important for callers sharing file handles. Sendfile support and behavior differ across filesystems/platforms.

Test signals: No direct tests in subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_copy_range_sendfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_fileinfo_unix.go -->
## sources/sync-backup/syncthing/lib/fs/basicfs_fileinfo_unix.go

Purpose: Unix implementation of `basicFileInfo` mode, owner, group, and same-file conversion.

Important APIs/types/functions: `basicFileInfo.Mode`, `Owner`, `Group`, and `osFileInfo`.

Control flow: Mode directly converts underlying `os.FileMode`; owner/group inspect `*syscall.Stat_t` from `FileInfo.Sys()` and return UID/GID or -1; `osFileInfo` returns underlying info.

State and persistence: Read-only file metadata view.

Dependencies and integration points: Non-Windows build tag; used by `BasicFilesystem.Stat/Lstat`, ownership scan, and `SameFile`.

Risks: `Sys()` type assertion can fail for nonstandard `os.FileInfo`, yielding -1 ownership.

Test signals: Filesystem metadata tests outside this subset cover Unix behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_fileinfo_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_fileinfo_windows.go -->
## sources/sync-backup/syncthing/lib/fs/basicfs_fileinfo_windows.go

Purpose: Windows implementation of `basicFileInfo` mode normalization, executable-bit synthesis, ownership placeholders, and same-file conversion.

Important APIs/types/functions: `execExts` initialized from `PATHEXT`; `isWindowsExecutable`; `basicFileInfo.Mode`, `Owner`, `Group`, and `osFileInfo`.

Control flow: Init lowercases executable extensions from environment. Mode clears symlink bit for nonzero-size dedup/hardlink-like files, adds execute bits for executable extensions, and clears group/other write bits to avoid exporting world-writable permissions. Owner/group return -1. `osFileInfo` unwraps directory junction wrappers.

State and persistence: Reads environment at init; metadata view only.

Dependencies and integration points: Windows filesystem metadata, cross-platform permission synchronization, and directory junction support.

Risks: PATHEXT-dependent executable detection can vary by environment. Permission normalization is intentionally lossy.

Test signals: Windows basic filesystem tests outside this subset cover path and metadata behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_fileinfo_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_lstat_broken.go -->
## sources/sync-backup/syncthing/lib/fs/basicfs_lstat_broken.go

Purpose: Linux/Android `Lstat` workaround for transient `EINTR`.

Important APIs/types/functions: `BasicFilesystem.underlyingLstat`.

Control flow: Calls `os.Lstat` up to ten times, sleeping an increasing number of milliseconds after `PathError` with `EINTR`, and returns on success or non-EINTR error.

State and persistence: Read-only metadata access.

Dependencies and integration points: Used by `BasicFilesystem.Lstat` on Linux/Android.

Risks: Retry loop hides repeated EINTR for up to a small bounded delay; after ten retries it returns the last result.

Test signals: No direct tests in subset; motivated by Android-specific behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_lstat_broken.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_lstat_regular.go -->
## sources/sync-backup/syncthing/lib/fs/basicfs_lstat_regular.go

Purpose: Default non-Linux/non-Android/non-Windows `Lstat` implementation.

Important APIs/types/functions: `BasicFilesystem.underlyingLstat`.

Control flow: Directly returns `os.Lstat(name)`.

State and persistence: Read-only metadata access.

Dependencies and integration points: Used by `BasicFilesystem.Lstat` on supported fallback platforms.

Risks: No platform-specific correction is applied.

Test signals: Build-tag compile and generic filesystem tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_lstat_regular.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_lstat_windows.go -->
## sources/sync-backup/syncthing/lib/fs/basicfs_lstat_windows.go

Purpose: Windows `Lstat` implementation with optional directory junction treatment as directories.

Important APIs/types/functions: `readReparseTag`, `isDirectoryJunction`, `dirJunctFileInfo`, `junctionPointModeMask`, and `BasicFilesystem.underlyingLstat`.

Control flow: `readReparseTag` opens the path with backup semantics and open-reparse-point flags, then queries `FILE_ATTRIBUTE_TAG_INFO`. Init builds a mode mask for junction points based on Go runtime version. `underlyingLstat` calls `os.Lstat`; if junction-as-dirs is enabled and the mode indicates a junction-like reparse point, it reads the tag and wraps mount points as `dirJunctFileInfo`, whose mode and `IsDir` simulate a traversable directory.

State and persistence: Read-only metadata and runtime-version-derived mask.

Dependencies and integration points: Windows build tag; used by `BasicFilesystem.Lstat`, directory walking, and option `OptionJunctionsAsDirs`.

Risks: Windows reparse semantics changed around Go 1.23, so version checks are fragile. Opening reparse points can fail on some filesystems; errors fall back to ordinary `Lstat` result.

Test signals: Windows-specific basic filesystem tests outside this subset should cover junction behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_lstat_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_platformdata_unix.go -->
## sources/sync-backup/syncthing/lib/fs/basicfs_platformdata_unix.go

Purpose: Non-Windows bridge from `BasicFilesystem` to Unix platform metadata collection.

Important APIs/types/functions: `BasicFilesystem.PlatformData`.

Control flow: Delegates to `unixPlatformData` with filesystem root/name, user/group caches, ownership and xattr scan flags, and xattr filter.

State and persistence: Reads metadata/xattrs depending on flags; uses caches owned by `BasicFilesystem`.

Dependencies and integration points: Integrates basic filesystem with protocol `PlatformData` for Unix ownership and xattrs.

Risks: Behavior depends on `unixPlatformData` and xattr support outside this file.

Test signals: Platform data/xattr tests are outside this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_platformdata_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_platformdata_windows.go -->
## sources/sync-backup/syncthing/lib/fs/basicfs_platformdata_windows.go

Purpose: Windows platform metadata collection for file owner names.

Important APIs/types/functions: `BasicFilesystem.PlatformData` and `openReadOnlyWithBackupSemantics`.

Control flow: If ownership scanning is disabled, returns empty platform data. Otherwise roots the path, opens it read-only with backup semantics so directories can be opened, calls `windows.GetSecurityInfo` for owner SID, resolves SID through user then group caches, and returns `protocol.PlatformData{Windows: ...}` with owner name and group flag when known.

State and persistence: Reads Windows security descriptors and uses filesystem user/group caches. No mutation.

Dependencies and integration points: Windows API, protocol WindowsData, BasicFilesystem rooting, value caches.

Risks: Owner lookup failures only debug-log and return empty owner fields. Opening with backup semantics and security APIs can fail due to permissions or filesystem behavior.

Test signals: Windows platform metadata tests are outside this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_platformdata_windows.go -->
