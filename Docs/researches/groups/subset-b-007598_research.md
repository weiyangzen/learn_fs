# Grouped Research: subset-b-007598

This grouped report covers Kubo node construction, libp2p wiring, provider/reprovide behavior, shutdown helpers, coverage wrappers, and Docker Compose defaults. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/core.go -->
# sources/distributed-fs/ipfs-kubo/core/node/core.go

Purpose: builds core IPLD, block, pinning, fetcher, resolver, and MFS services for an fx-managed Kubo node. Important APIs are `BlockService`, `Pinning`, `FetcherConfig`, `PathResolverConfig`, `Dag`, `Files`, `FetchersOut/In`, `PathResolversOut`, and `syncDagService`.

Control flow: `BlockService` wraps a blockstore and exchange, then registers bounded shutdown. `Pinning` parses `Provide.Strategy`, wraps the DAG service in `syncDagService`, chooses pinned or root DHT provider hooks, and closes before the repo. `FetcherConfig` creates online and offline IPLD/UnixFS fetchers, adding dag-pb support and UnixFS reification. `Files` loads `/local/filesroot`, creates an empty UnixFS root when absent, validates protobuf roots when present, configures MFS import options, and optionally wires the DHT provider only for `mfs` strategies.

State and persistence: MFS root CID is persisted at `FilesRootDatastoreKey`; pinner syncs block and filestore prefixes; `syncDagService.Sync` persists data before pinner operations. Dependencies include boxo blockservice, merkledag, MFS, dspinner, path resolver, repo datastore, and `core/shutdown`.

Integration points: consumed by grouped `Core`, `Storage`, `IPFS`, and online/offline service graphs. Risks are shutdown ordering with datastore-backed pinner operations, invalid persisted MFS CIDs, and strategy bits causing duplicate advertisements if roots and pinned are both enabled. Test signals are mostly integration-level; the comments document shutdown and provide-strategy invariants that downstream tests should preserve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/core.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/dns.go -->
# sources/distributed-fs/ipfs-kubo/core/node/dns.go

Purpose: constructs the multiaddr DNS resolver used by node networking and gateway-style DNS resolution. The central API is `DNSResolver(cfg *config.Config)`.

Control flow: it builds optional DoH settings from `DNS.MaxCacheTTL`, resolves `auto` placeholders through `DNSResolversWithAutoConf`, and asks `gateway.NewDNSResolver` for the base resolver. If `AutoTLS.SkipDNSLookup` is false, the base resolver is returned. Otherwise it builds a local `p2pForgeResolver` for `libp2p.direct` plus any custom AutoTLS suffix and registers it as a domain resolver while retaining the base resolver as fallback.

State and persistence: no durable state is written. Runtime behavior depends on config values and the in-memory resolver chain.

Dependencies and integration: depends on boxo gateway DNS, libp2p DoH resolver, multiformats multiaddr-dns, and `NewP2PForgeResolver`. It integrates with `Online` and `Offline` node graphs via `fx.Provide(DNSResolver)`, feeding namesys and multiaddr resolution.

Risks: incorrect `MaxCacheTTL` changes cache lifetime; local p2p-forge short-circuiting must still delegate TXT lookups for ACME; custom suffix handling must include trailing-dot domain registration. Test signal comes from the compile-time `madns.BasicResolver` assertion and dedicated p2p-forge resolver tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/dns.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/groups.go -->
# sources/distributed-fs/ipfs-kubo/core/node/groups.go

Purpose: defines the high-level fx option groups that assemble storage, identity, libp2p, IPNS, online/offline routing, and the full IPFS node. Important exports are `BaseLibP2P`, `LibP2P`, `Storage`, `Identity`, `IPNS`, `Online`, `Offline`, `Core`, `Networked`, and `IPFS`.

Control flow: `LibP2P` interprets connection manager, pubsub, AutoNAT, relay, AutoTLS, transport, discovery, routing, resource-manager, and NAT-check settings into fx providers/invokes. AutoTLS may append wildcard WSS listeners when TCP and WebSocket transports are enabled. `Storage` configures blockstore cache options and chooses filestore support. `Identity` validates peer ID/private key and adds self keys to the peerstore. `Online` validates IPNS republish durations, enables bitswap, DNS, namesys, peering, p2p service, libp2p, and providers. `Offline` supplies offline exchange/routing/provider variants. `IPFS` pulls config from `BuildCfg`, validates import/provide config, migrates old sharding settings, writes UnixFS HAMT globals, and returns the final graph.

State and persistence: mutates `cfg.Addresses.Swarm` for AutoWSS, sets global UnixFS sharding knobs, and reads repo resource overrides. Dependencies span almost every node package plus libp2p pubsub, resource-manager, and Kubo config.

Risks: fatal logging is used for incompatible relay/AutoTLS/sharding settings; config migration modifies in-memory config; provider strategy influences multiple subsystems. Tests are indirect through libp2p option tests, routing tests, provider tests, and startup integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/groups.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/helpers.go -->
# sources/distributed-fs/ipfs-kubo/core/node/helpers.go

Purpose: provides small fx helpers for lifecycle hooks and conditional option assembly. Important APIs are `lcStartStop.Append`, `maybeProvide`, and `maybeInvoke`.

Control flow: `lcStartStop.Append` accepts a function that starts work and returns a stop function. It installs fx `OnStart` and `OnStop` hooks, skips work when the passed context is already done, stores the stop closure, and errors if stop is unexpectedly nil. `maybeProvide` and `maybeInvoke` return the corresponding fx option only when enabled.

State and persistence: stores only one in-memory `stopFunc` closure per appended hook. No datastore or filesystem state is touched.

Dependencies and integration: depends on `context`, `errors`, and `go.uber.org/fx`. It is used by IPNS republisher and conditional graph composition across `groups.go`.

Risks: the stop function is unbounded and context is not passed to it; callers must make their own shutdown behavior safe. The typo in error text (`lcStatStop`) is harmless but could make logs less searchable. There are no direct tests in this subset; integration tests that start/stop fx apps are the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/helpers/helpers.go -->
# sources/distributed-fs/ipfs-kubo/core/node/helpers/helpers.go

Purpose: defines lifecycle-aware context utilities for node services. Important APIs are `type MetricsCtx context.Context` and `LifecycleCtx`.

Control flow: `LifecycleCtx` derives a cancelable context from the metrics/root context and appends an fx `OnStop` hook that cancels it. Long-running services use this context to stop when the node lifecycle stops.

State and persistence: only in-memory context cancellation state is held. No external persistence.

Dependencies and integration: depends on Go `context` and fx. It is used across blockstore cache setup, host/routing construction, discovery, pubsub, provider resource-manager logging, and other background services.

Risks: comments acknowledge this is a workaround for services using contexts imperfectly. If callers ignore the returned context, shutdown still depends on explicit close hooks. No direct tests here; shutdown behavior is covered indirectly by service tests and `core/shutdown`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/helpers/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/identity.go -->
# sources/distributed-fs/ipfs-kubo/core/node/identity.go

Purpose: supplies identity providers for fx injection. Important APIs are `PeerID` and `PrivateKey`.

Control flow: `PeerID` returns a closure that injects a fixed `peer.ID`. `PrivateKey` returns a closure that derives the peer ID from the configured private key, verifies it matches the expected ID, and returns the key or an error.

State and persistence: no writes. The functions validate already-loaded config identity material.

Dependencies and integration: depends on libp2p crypto and peer packages. `groups.go` uses these providers in the `Identity` graph, and libp2p host construction later retrieves the private key from the peerstore.

Risks: a mismatched private key causes startup failure, which is correct for identity integrity. Tests are indirect through identity startup paths; no direct unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/identity.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/ipns.go -->
# sources/distributed-fs/ipfs-kubo/core/node/ipns.go

Purpose: configures IPNS validation, resolution, and republishing. Important APIs are `DefaultIpnsCacheSize`, `RecordValidator`, `Namesys`, and `IpnsRepublisher`.

Control flow: `RecordValidator` returns a namespaced validator for public keys and IPNS records backed by the peerstore key book. `Namesys` builds a boxo namesystem using repo datastore, DNS resolver, max cache TTL, and optional cache size. `IpnsRepublisher` constructs a republisher with the namesystem, repo datastore, private key, and keystore, applies configured interval/lifetime, checks lifetime is not shorter than interval, and starts it through `lcStartStop`.

State and persistence: IPNS data uses the repo datastore and keystore. Republisher state is runtime only, but it republishes persisted local records.

Dependencies and integration: boxo IPNS/namesys/republisher, libp2p record validation, peerstore, repo, and DNS resolver. Used by `IPNS`, `Online`, and `Offline` groups.

Risks: bad duration strings or unsafe intervals abort startup; too-short record lifetime would cause expiring records and is rejected. Test coverage is indirect via config and namesys tests outside this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/ipns.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/addrs.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/addrs.go

Purpose: handles address filtering, advertised-address construction, dead-listener diagnostics, listener options, and AutoTLS p2p-forge certificate manager setup. Important APIs include `AddrFilters`, `findDeadListeners`, `listenEndpoint`, `explicitListens`, `MonitorDeadListeners`, `makeAddrsFactory`, `AddrsFactory`, `ListenOn`, `P2PForgeCertMgr`, and `StartP2PAutoTLS`.

Control flow: `AddrFilters` converts configured masks to a `ma.Filters` connection gater. Dead-listener detection compares resolved interface listen addrs against `Swarm.AddrFilters` and `Addresses.NoAnnounce`, classifying explicit specific-IP listeners by IP/transport/port rather than full multiaddr text. `MonitorDeadListeners` runs at startup and on `EvtLocalAddressesUpdated`, deduplicating findings. `makeAddrsFactory` applies Announce override, AppendAnnounce dedupe, NoAnnounce exact/CIDR filtering, and drops empty multiaddrs. `AddrsFactory` composes p2p-forge address processing before announce filtering when AutoTLS is active. AutoTLS setup creates certificate storage under the repo and starts/stops the forge manager.

State and persistence: p2p-forge certificates live in `<repo>/p2p-forge-certs`. Runtime monitors keep in-memory seen findings.

Dependencies/integration: libp2p options, event bus, basic host addrs factory, multiaddr filters, certmagic, p2p-forge, Kubo config. Risks include silently skipped malformed diagnostic masks, fatal listener misconfiguration hiding behind debug logs, and cert storage/registration failures. Tests cover dead-listener classification and empty multiaddr filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/addrs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/addrs_test.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/addrs_test.go

Purpose: validates address filtering and diagnostic helper behavior from `addrs.go`. Important test helpers are `mustMultiaddrs`, `TestFindDeadListeners`, and `TestMakeAddrsFactoryDropsEmptyMultiaddrs`.

Control flow: table tests construct resolved listener addrs, raw `Addresses.Swarm`, filters, and NoAnnounce rules, then compare `findDeadListeners` output with `require.ElementsMatch`. Cases cover empty configs, explicit loopback reverse-proxy gotchas, wildcard expansions, IPv6 ULA filtering, Docker bridge addresses, DNS listeners, exact NoAnnounce entries, malformed rules, WebTransport certhashes, TCP/QUIC port sharing, WSS to `/tls/ws` rewrites, uppercase IPv6, and `/tcp/0` assigned ports. The factory test ensures nil/zero multiaddrs are removed while valid duplicates remain.

State and persistence: no external state; all tests are pure in-memory.

Dependencies/integration: uses multiaddr parsing and testify assertions. It directly protects the log-level routing semantics in `addrs.go` and guards signed peer records from receiving empty multiaddrs.

Risks signaled: explicit-vs-wildcard misclassification can produce noisy errors or hide unreachable listeners; full-string multiaddr comparisons are brittle across transport rewrites. This file is strong unit coverage for recent address edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/addrs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/cgnat.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/cgnat.go

Purpose: detects and warns when a node appears behind carrier-grade NAT or double NAT. Important APIs are `DetectNAT`, `detectNATKind`, `classifyNAT`, `MonitorCGNAT`, `latchNotice`, `logCGNATNotice`, and `logDoubleNATNotice`.

Control flow: detection requires a host implementing `AllAddrs` and `Reachability`. `classifyNAT` ignores public reachability, ignores IPv6 and local-interface IPv4 addresses, classifies foreign RFC6598 addresses as CGNAT, and classifies foreign private addresses as double NAT unless CGNAT is found. `MonitorCGNAT` subscribes to `EvtLocalAddressesUpdated`, runs an initial check in a goroutine, and emits only first/upgrade notices through `latchNotice`.

State and persistence: no durable state. Runtime state is the single `reported` NAT kind in the monitor goroutine. Notices write directly to `cgnatNoticeOut` (default stderr) so they are visible even when go-log filters warn/info.

Dependencies/integration: libp2p host/network/event APIs, multiaddr, fx lifecycle. Wired conditionally by `groups.go` through `Internal.CGNATCheck`.

Risks: best-effort detection misses routers that do not expose mapped WAN addresses; direct stderr output bypasses normal logging controls except the config flag. Tests cover classification, notice latching, and notice content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/cgnat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/cgnat_test.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/cgnat_test.go

Purpose: unit-tests NAT classification, notice latching, and warning text. Important tests are `TestClassifyNAT`, `TestLatchNotice`, and `TestCGNATNoticeOutput`.

Control flow: `TestClassifyNAT` feeds synthetic multiaddrs, local interface IP sets, and libp2p reachability values into `classifyNAT`. It asserts CGNAT wins over double NAT, local Tailscale-style 100.64/10 addresses are ignored, public reachability suppresses warnings, IPv6 is ignored, and own private interface addrs are not flagged. `TestLatchNotice` proves double-NAT can upgrade to CGNAT but cannot downgrade or repeat. Output tests replace `cgnatNoticeOut` with a buffer and assert key strings.

State and persistence: pure in-memory; `captureNotice` restores the global writer with `t.Cleanup`.

Dependencies/integration: uses multiaddr, libp2p network reachability, testing, and bytes/string checks. The tests directly encode expected operational semantics for user-facing NAT warnings.

Risks signaled: false positives for overlay networks and repeated notices would be user-visible; this suite specifically guards both.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/cgnat_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/discovery.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/discovery.go

Purpose: wires local peer discovery, currently mDNS, into the libp2p host. Important APIs are `discoveryHandler`, `HandlePeerFound`, `DiscoveryHandler`, and `SetupDiscovery`.

Control flow: `DiscoveryHandler` captures a lifecycle context and host. On peer discovery, `HandlePeerFound` attempts `host.Connect` with a 30-second timeout and logs failures. `SetupDiscovery` starts an mDNS service only when enabled; start errors are logged and swallowed so node startup continues.

State and persistence: no durable state. Runtime state is the lifecycle context held by the handler and the mdns service instance.

Dependencies/integration: libp2p host/peer/mdns, fx, and Kubo lifecycle helpers. `BaseLibP2P` provides the handler and `LibP2P` invokes setup based on `Discovery.MDNS.Enabled`.

Risks: mDNS startup failure only logs, which is desirable for noncritical discovery but can hide local-discovery regressions. No direct tests here; integration behavior is observable through host discovery tests elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/discovery.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/dns.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/dns.go

Purpose: adapts Kubo's multiaddr DNS resolver into a libp2p option. Important API is `MultiaddrResolver`.

Control flow: it appends `libp2p.MultiaddrResolver(swarm.ResolverFromMaDNS{Resolver: rslv})` to the grouped libp2p options and returns no error.

State and persistence: no state beyond injecting the resolver into host construction.

Dependencies/integration: depends on libp2p, libp2p swarm resolver adapter, and `go-multiaddr-dns`. Provided by `BaseLibP2P` so host dialing/listening can resolve DNS multiaddrs consistently with Kubo DNS configuration.

Risks: correctness depends on the resolver injected from `core/node/dns.go`; this file is thin and has no direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/dns.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/fd/sys_not_unix.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/fd/sys_not_unix.go

Purpose: platform fallback for file descriptor limit detection on systems that are not Linux, Darwin, or Windows. Important API is `GetNumFDs`.

Control flow: under build tag `!linux && !darwin && !windows`, `GetNumFDs` returns `0`.

State and persistence: none.

Dependencies/integration: consumed by resource-manager default limit calculation in `rcmgr_defaults.go`. A return value of zero means the computed `MaxFileDescriptors` default may become zero/half-zero unless config overrides it.

Risks: on unsupported platforms the resource manager cannot infer FD limits and may need explicit config. Test signal is build coverage across platforms rather than unit tests in this repo.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/fd/sys_not_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/fd/sys_unix.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/fd/sys_unix.go

Purpose: returns the process file descriptor limit on Linux and Darwin. Important API is `GetNumFDs`.

Control flow: under build tag `linux || darwin`, it calls `unix.Getrlimit(unix.RLIMIT_NOFILE, &l)` and returns the current soft limit, or `0` on error.

State and persistence: reads kernel process limits only.

Dependencies/integration: depends on `golang.org/x/sys/unix` and feeds resource-manager default `MaxFileDescriptors` in `rcmgr_defaults.go`.

Risks: returning zero on `Getrlimit` failure may produce overly strict defaults; normal Unix platforms should provide a valid soft limit. No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/fd/sys_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/fd/sys_windows.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/fd/sys_windows.go

Purpose: Windows-specific file descriptor/handle limit placeholder. Important API is `GetNumFDs`.

Control flow: under build tag `windows`, returns `math.MaxInt`.

State and persistence: none.

Dependencies/integration: feeds resource-manager FD limit defaults. The high value avoids Unix-style FD limiting on Windows where the same rlimit mechanism is not available.

Risks: can make FD-derived resource limits effectively unbounded on Windows unless other limits constrain behavior. No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/fd/sys_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/filters.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/filters.go

Purpose: adapts multiaddr filters into libp2p's `connmgr.ConnectionGater`. Important type is `filtersConnectionGater`.

Control flow: `InterceptAddrDial`, `InterceptAccept`, and `InterceptSecured` deny addresses blocked by the filter. `InterceptPeerDial` and `InterceptUpgraded` always allow, because filtering is address-level rather than peer-level after upgrade.

State and persistence: no persistence; the gater is an in-memory wrapper over `ma.Filters`.

Dependencies/integration: depends on libp2p connmgr/control/network/peer and multiaddr filters. Created by `AddrFilters` in `addrs.go` and passed to libp2p as `ConnectionGater`.

Risks: filtering at multiple phases can reject inbound and outbound connections; peer-level allowance means bad peers are not blocked absent address matches. No direct tests for the adapter, but address behavior is covered through `addrs_test.go`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/filters.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/host.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/host.go

Purpose: constructs the libp2p host and exposes the initial routing object. Important types/APIs are `P2PHostIn`, `P2PHostOut`, and `Host`.

Control flow: `Host` starts with `NoListenAddrs`, flattens grouped libp2p options, loads config, resolves bootstrap peers through autoconf, and builds `RoutingOptionArgs`. It sets optimistic provide when either the experimental flag or DHT sweep is enabled. It injects a libp2p routing constructor that captures the resulting routing in `out.Routing`, then calls the selected `HostOption`. For mock/test hosts that ignore libp2p options, it constructs routing manually and wraps the host with `routedhost`.

State and persistence: reads repo config and datastore; no direct writes. Registers bounded host close on fx stop.

Dependencies/integration: repo, record validator, peerstore, routing option, lifecycle helper, and shutdown helper. It is the join point between configured libp2p options and Kubo routing/provider behavior.

Risks: route construction side effects depend on libp2p applying the routing option; the fallback handles tests but production failures still abort startup. Shutdown can time out through `CloseWithCtx`. No direct test here, but many routing tests depend on its contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/host.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/hostopt.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/hostopt.go

Purpose: isolates actual libp2p host construction behind a testable function type. Important APIs are `HostOption`, `DefaultHostOption`, and `constructPeerHost`.

Control flow: `constructPeerHost` fetches the node private key from the peerstore for the expected peer ID, errors if missing, prepends identity and peerstore options, and calls `libp2p.New`.

State and persistence: no writes; depends on peerstore contents populated by identity setup.

Dependencies/integration: libp2p, host, peer, peerstore. `Host` receives a `HostOption`, allowing tests or alternate construction to substitute behavior.

Risks: missing private key causes startup failure; this is expected for encrypted libp2p operation. No direct tests in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/hostopt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/libp2p.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/libp2p.go

Purpose: defines common libp2p option providers and option prioritization. Important APIs are `Libp2pOpts`, `ConnectionManager`, `PstoreAddSelfKeys`, `UserAgent`, `simpleOpt`, `priorityOption`, `prioritizeOptions`, and `ForceReachability`.

Control flow: provider functions append libp2p options into the fx group `libp2p`. `ConnectionManager` builds a basic connection manager with watermarks, grace, and silence period. `PstoreAddSelfKeys` stores local public/private keys. `prioritizeOptions` filters disabled priority settings, sorts ascending by priority, and chains resulting options. `ForceReachability` maps config strings to libp2p public/private reachability options.

State and persistence: peer keys are stored in the in-memory peerstore. No datastore writes.

Dependencies/integration: Kubo version/config, libp2p options, crypto/peerstore, connmgr, fx. Used widely by `groups.go` transport/security/resource setup.

Risks: lower priority numbers win, so config mistakes can reorder security/transports; unrecognized forced reachability aborts startup. Tests cover priority ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/libp2p.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/libp2p_test.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/libp2p_test.go

Purpose: tests option priority sorting. Important test is `TestPrioritize`.

Control flow: the test creates libp2p options that encode their identity as TCP listen ports, applies `prioritizeOptions`, extracts port numbers from the resulting config, and checks ordering with default priorities and custom priorities.

State and persistence: no external state.

Dependencies/integration: libp2p config application, multiaddr parsing, testify. It protects the shared priority mechanism used by security and other configurable libp2p option groups.

Risks signaled: a sorting regression would silently change protocol preference order; this test makes the behavior explicit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/libp2p_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/nat.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/nat.go

Purpose: provides NAT port mapping and AutoNAT service options. Important APIs are `NatPortMap` and `AutoNATService`.

Control flow: `NatPortMap` is a simple option wrapping `libp2p.NATPortMap`. `AutoNATService` enables the AutoNAT service, applies optional throttle limits, and enables AutoNAT v2 unless `v1only` is true.

State and persistence: no persistence; options affect runtime host services.

Dependencies/integration: Kubo AutoNAT throttle config and libp2p options. Wired by `groups.go` based on `Swarm.DisableNatPortMap` and `AutoNAT.ServiceMode`.

Risks: enabling NAT services broadly affects resource use and network behavior; throttle config must be sane. No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/nat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/peerstore.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/peerstore.go

Purpose: provides the libp2p peerstore and closes it with the node lifecycle. Important API is `Peerstore`.

Control flow: constructs an in-memory peerstore with `pstoremem.NewPeerstore`, registers an fx `OnStop` hook, and closes it through `shutdown.CloseWithCtx`.

State and persistence: peerstore is memory-backed; no durable peer metadata is written by this provider.

Dependencies/integration: pstoremem, fx, shutdown helper. Used by identity setup, host construction, and IPNS record validation.

Risks: peerstore close can block, so bounded shutdown is important. No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/peerstore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/pnet.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/pnet.go

Purpose: configures private libp2p networks from a repo swarm key and warns when isolated. Important APIs are `PNetFingerprint`, `PNet`, `PNetChecker`, and `pnetFingerprint`.

Control flow: `PNet` reads `repo.SwarmKey`, decodes a V1 PSK, adds `libp2p.PrivateNetwork`, and returns a fingerprint. `PNetChecker` starts a ticker after node start and warns every 30 seconds after the first tick if the private-network host has no peers. `pnetFingerprint` runs Salsa20 over zero bytes with the PSK and then SHAKE-128 to produce a 16-byte non-reversible fingerprint.

State and persistence: reads swarm key from repo; no writes. Runtime checker uses a done channel.

Dependencies/integration: repo, libp2p pnet, host, fx, Salsa20, SHA3. Base libp2p provides and invokes this logic.

Risks: invalid swarm keys abort startup; private networks cannot use some transports, enforced elsewhere. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/pnet.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/pubsub.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/pubsub.go

Purpose: creates FloodSub/GossipSub services and a datastore-backed seqno validator to reduce replay/cycle risk. Important APIs are `FloodSub`, `GossipSub`, `newSeqnoValidator`, `SeqnoStorePrefix`, and `seqnoStore.Get/Put`.

Control flow: both pubsub constructors use a lifecycle context, host, topic discovery, and default validator. GossipSub additionally enables flood publishing for local publications to improve IPNS delivery. `newSeqnoValidator` wraps `seqnoStore` in libp2p pubsub's basic seqno validator. `seqnoStore.Get` maps datastore-not-found to `(nil, nil)` so first messages from unknown peers are accepted; `Put` stores bytes under `/pubsub/seqno/<peer>`.

State and persistence: seqno metadata persists in the repo datastore, allowing validator state to survive restarts. Pubsub service itself is runtime.

Dependencies/integration: libp2p pubsub/discovery/host/peer, repo datastore, Kubo helpers. Wired when `pubsub` or `ipnsps` build options are enabled.

Risks: persistent seqno state can reject old messages after restart by design; datastore errors bubble to validation. Tests cover `seqnoStore`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/pubsub.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/pubsub_test.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/pubsub_test.go

Purpose: validates the datastore-backed pubsub sequence-number store. Important test is `TestSeqnoStore`.

Control flow: tests create a synchronized in-memory datastore and a `seqnoStore`, decode two peers, then assert unknown peers return nil without error, seqnos store/retrieve as big-endian uint64, peer entries are isolated, updates replace older values, keys use `/pubsub/seqno/<peer>`, and data persists across store instances sharing the datastore.

State and persistence: uses in-memory datastore to model repo persistence.

Dependencies/integration: go-datastore, sync datastore wrapper, libp2p peer IDs, testify. The test directly protects the validator contract needed by `pubsub.NewBasicSeqnoValidator`.

Risks signaled: returning datastore-not-found as an error would reject first messages; peer key collision or non-persistence would weaken replay prevention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/pubsub_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/rcmgr.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/rcmgr.go

Purpose: constructs and exposes libp2p resource manager limits, runtime usage views, and safety checks. Important APIs include `ResourceManager`, `LimitConfig`, `ResourceLimitsAndUsage`, `LimitsConfigAndUsage`, `MergeLimitsAndStatsIntoLimitsConfigAndUsage`, `LimitConfigsToInfo`, and `ensureConnMgrMakeSenseVsResourceMgr`.

Control flow: `ResourceManager` honors config and `LIBP2P_RCMGR`, computes limits plus user overrides, logs defaults, checks connection-manager compatibility, sets trace reporters, subnet limits, allowlisted multiaddrs, optional debug trace file, wraps the manager in `loggingResourceManager`, injects it into libp2p, and closes it on stop. If disabled, it injects `NullResourceManager`. Merge helpers combine concrete limits with runtime stats and render filtered resource info entries.

State and persistence: optional trace file `rcmgr.json.gz` is written in the repo when `LIBP2P_DEBUG_RCMGR` is set. Runtime error counts live in the logging wrapper. No datastore state.

Dependencies/integration: Kubo config/repo/helpers/shutdown, libp2p network/resource-manager, multiaddr, fx. Used by `LibP2P` and swarm resource commands.

Risks: conflicting resource limits vs connection manager high-water abort startup; invalid allowlist entries are skipped with logs; disabling manager removes protection. Tests cover logging wrapper; default calculations are in `rcmgr_defaults.go`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/rcmgr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/rcmgr_defaults.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/rcmgr_defaults.go

Purpose: computes default libp2p resource-manager limits from memory, file descriptors, and connection-manager settings. Important API is `createDefaultLimitConfig`.

Control flow: it defaults max memory to half total memory and max FDs to half the detected descriptor limit. It builds partial limits for system, transient, allowlisted, service/protocol/conn/stream, and per-peer scopes. It scales libp2p defaults, sets service limits, then increases inbound connection and stream limits to be at least twice ConnMgr high-water and a configured minimum when applicable. It returns a concrete config and startup message.

State and persistence: no writes; reads process/system memory and FD limits.

Dependencies/integration: `pbnjay/memory`, Kubo config, fd helper, go-libp2p resource-manager defaults. Called by `LimitConfig` before user overrides are applied.

Risks: memory and FD detection errors directly affect resource limits; comments note memory accounting gaps in libp2p, so inbound connection limits are a defensive proxy. Test coverage is indirect through resource-manager startup and command behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/rcmgr_defaults.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/rcmgr_logging.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/rcmgr_logging.go

Purpose: wraps a libp2p resource manager to aggregate and periodically log resource-limit-exceeded errors. Important types are `loggingResourceManager` and `loggingScope`.

Control flow: `start` launches a ticker, drains `limitExceededErrs` every interval, logs counts by unwrapped error message, and emits a documentation hint when any occurred. `countErrs` records only `network.ErrResourceLimitExceeded`. The wrapper forwards resource-manager methods and wraps transient/service/protocol/peer scopes so memory reservations and scope assignments are counted. It also implements state APIs such as `ListServices`, `Stat`, and `VerifySourceAddress` when the delegate supports them.

State and persistence: in-memory mutex-protected error-count map; no persistence.

Dependencies/integration: libp2p network/resource-manager interfaces, zap logging, multiaddr. Constructed by `ResourceManager` in `rcmgr.go`.

Risks: many type assertions in `loggingScope` assume the delegate scope implements the requested interface; misuse on the wrong scope type would panic. The wrapper intentionally aggregates logs to avoid noisy per-error output. Tests cover aggregated connection-limit logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/rcmgr_logging.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/rcmgr_logging_test.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/rcmgr_logging_test.go

Purpose: verifies aggregated resource-manager warning behavior. Important test is `TestLoggingResourceManager`.

Control flow: under `synctest`, the test builds a resource manager with system connection limits of one, wraps it with `loggingResourceManager` using a one-second interval and observed zap logger, opens three inbound connections, starts logging, advances fake time, and waits until a warning is observed. It asserts the warning reports two protected limit exceedances with the expected libp2p message.

State and persistence: all in-memory; the delegate resource manager is closed with defer.

Dependencies/integration: testing/synctest, libp2p resource-manager/network, multiaddr, zap observer, testify. It guards the operator-facing aggregated log contract and confirms `OpenConnection` errors are counted.

Risks signaled: without aggregation, limit-exceeded logs could be either missing or too noisy; this test ensures a bounded periodic summary appears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/rcmgr_logging_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/relay.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/relay.go

Purpose: configures circuit relay transport, relay service, AutoRelay client, and hole punching. Important APIs are `RelayTransport`, `RelayService`, `MaybeAutoRelay`, and `HolePunching`.

Control flow: relay transport enables or disables circuit relay. Relay service applies user overrides onto libp2p default relay resources. `MaybeAutoRelay` either configures static relays or creates a peer source fed by trusted peering peers, DHT closest peers, and currently connected swarm peers through `autoRelayFeeder`. `HolePunching` enables hole punching only when the relay client is active; explicit incompatible enablement is fatal.

State and persistence: runtime channels and goroutines only. Relay reservations are libp2p runtime state.

Dependencies/integration: Kubo relay/peering config, libp2p autorelay and circuitv2 relay, fx. `groups.go` validates relay dependency flags before wiring these options.

Risks: peer source goroutine must respect shutdown; static relay strings must parse; disabling relay client disables hole punching. Tests are indirect through networking integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/relay.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/routing.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/routing.go

Purpose: composes DHT, delegated HTTP, pubsub, offline, content routing, content discovery, accelerated DHT, and AutoRelay feeder behavior. Important APIs include `Router`, `BaseRouting`, `ContentRouting`, `ContentDiscovery`, `Routing`, `OfflineRouting`, `PubsubRouter`, and `autoRelayFeeder`.

Control flow: `BaseRouting` captures the initial routing from host construction, locates a dual DHT, registers DHT shutdown, and optionally replaces the content router with FullRT plus default HTTP routers when accelerated DHT client is enabled. `Routing` sorts grouped routers by priority and builds a composable parallel router. `ContentRouting` tiers content-capable routers. `PubsubRouter` adds a high-priority IPNS-only value store. `autoRelayFeeder` periodically feeds trusted peers, DHT closest peers, and connected swarm peers to an AutoRelay channel with exponential backoff and bounded shutdown.

State and persistence: DHTs and FullRT clients use repo datastore through their constructors; this file manages lifecycle but does not write directly. AutoRelay feeder holds runtime channels.

Dependencies/integration: go-libp2p-kad-dht, fullrt, pubsub-router, routing-helpers, repo/config, shutdown. Risks include duplicate close hooks if composable router detection changes, FullRT readiness delays, and feeder goroutine stalls; shutdown uses context bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/routing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/routingopt.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/routingopt.go

Purpose: builds routing option implementations for DHT, delegated HTTP, custom routers, nil routing, and HTTP provider address resolution. Important APIs are `RoutingOptionArgs`, `RoutingOption`, `EndpointSource`, `determineCapabilities`, `collectAllEndpoints`, `constructDefaultHTTPRouters`, `ConstructDelegatedOnlyRouting`, `ConstructDefaultRouting`, `constructDHTRouting`, `ConstructDelegatedRouting`, `httpRouterAddrFunc`, and `parseMultiaddrs`.

Control flow: endpoint collection merges delegated routers and publishers, with `IPFS_HTTP_ROUTERS` overriding read endpoints. Capabilities are inferred per endpoint and merged by origin so one HTTP router/composer is built per base URL. Default routing combines DHT and HTTP routers in parallel; delegated-only requires at least one HTTP router; custom routing delegates to `irouting.Parse`; DHT routing configures dual WAN/LAN DHT and test stubs when `TEST_DHT_STUB` is set. `httpRouterAddrFunc` prefers explicit Announce, then AutoNAT V2 confirmed addrs, then `host.Addrs`, always appending AppendAnnounce.

State and persistence: DHT routing receives datastore; HTTP routing may sign with identity private key but this file stores nothing.

Dependencies/integration: autoconf, Kubo routing/config, libp2p DHT/host/multiaddr. Risks include endpoint capability misclassification, env override surprises, and reliance on experimental `BasicHost.ConfirmedAddrs`. Tests cover capability logic and address selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/routingopt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/routingopt_test.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/routingopt_test.go

Purpose: unit-tests delegated endpoint capability parsing and HTTP router address selection. Important tests are `TestDetermineCapabilities`, `TestEndpointCapabilitiesReadWriteLogic`, and `TestHttpRouterAddrFunc`.

Control flow: capability tests feed read/write endpoint sources with no path, trailing slash, IPNS path, providers path, peers path, write-only endpoint, and unsupported path, asserting base URL and capability booleans. The stub host implements `ConfirmedAddrs` and minimal `host.Host` methods. Address tests verify AutoNAT confirmed addresses win over `host.Addrs`, fallback works, Announce overrides both, AppendAnnounce is appended in all modes, and NoAnnounce filtering is assumed to happen upstream in `host.Addrs`.

State and persistence: no external state; all multiaddrs are parsed in-memory.

Dependencies/integration: autoconf capabilities, Kubo config, libp2p host interfaces, testify. It protects HTTP routing's read/write split and provider-address selection used for delegated routing records.

Risks signaled: publishing private/wildcard addresses to HTTP routers or enabling unsupported endpoint capabilities would harm retrieval and IPNS behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/routingopt_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/sec.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/sec.go

Purpose: configures libp2p security transports. Important API is `Security`.

Control flow: if encryption is disabled, it logs a prominent error and appends `libp2p.NoSecurity`. Otherwise it chains TLS and Noise security options using the shared priority mechanism, with default priorities TLS=100 and Noise=200 and config overrides from `Swarm.Transports.Security`.

State and persistence: no persistence.

Dependencies/integration: Kubo transport config, libp2p security options, Noise, TLS. Wired by `LibP2P` based on `BuildCfg.DisableEncryptedConnections`.

Risks: disabling encryption prevents connections to encrypted nodes and is operator-dangerous; priority changes alter protocol negotiation preference. Priority behavior is covered by `libp2p_test.go`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/sec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/smux.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/smux.go

Purpose: configures stream multiplexing. Important APIs are `makeSmuxTransportOption` and `SmuxTransport`.

Control flow: rejects the legacy `LIBP2P_MUX_PREFS` environment variable, rejects disabled Yamux config, and returns the Yamux default muxer option. `SmuxTransport` wraps this into the grouped libp2p option provider.

State and persistence: reads environment only; no writes.

Dependencies/integration: Kubo transport config, libp2p muxer option, Yamux. Wired by `LibP2P`.

Risks: unsupported env/config aborts startup; currently Yamux is mandatory. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/smux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/topicdiscovery.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/topicdiscovery.go

Purpose: creates routing-backed topic discovery with exponential backoff. Important API is `TopicDiscovery`.

Control flow: it builds a `routingdiscovery.RoutingDiscovery` from content routing, then wraps it in `backoff.NewBackoffDiscovery` with 60-second minimum, one-hour maximum, full jitter, factor 5, and a random source.

State and persistence: runtime-only backoff state.

Dependencies/integration: libp2p discovery/backoff/routing and content routing. Provided when pubsub or IPNS-over-pubsub is enabled.

Risks: random seed uses `rand.Int63` from the package-level source; discovery delays affect pubsub mesh formation. No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/topicdiscovery.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/transport.go -->
# sources/distributed-fs/ipfs-kubo/core/node/libp2p/transport.go

Purpose: configures libp2p network transports and bandwidth metrics. Important APIs are `Transports` and `BandwidthCounter`.

Control flow: `Transports` checks whether a private network fingerprint exists, enables TCP with metrics, WebSocket with optional p2p-forge TLS config, shared TCP listener when TCP+WebSocket are enabled and allowed, and QUIC/WebTransport/WebRTC Direct unless disabled or private networking is active. Private networks explicitly error for transports that do not support pnet. `BandwidthCounter` creates and injects a metrics reporter.

State and persistence: runtime options only; no persistent state.

Dependencies/integration: Kubo transport config, p2p-forge cert manager, libp2p tcp/quic/websocket/webtransport/webrtc, metrics, fx. Wired by `LibP2P`.

Risks: pnet incompatibilities abort startup; `LIBP2P_TCP_MUX=false` changes listener sharing; AutoTLS requires WebSocket TLS config. No direct tests here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/libp2p/transport.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/p2pforge_resolver.go -->
# sources/distributed-fs/ipfs-kubo/core/node/p2pforge_resolver.go

Purpose: implements local DNS resolution for p2p-forge hostnames that encode IP addresses, avoiding network DNS for AutoTLS A/AAAA lookups. Important APIs are `p2pForgeResolver`, `NewP2PForgeResolver`, `LookupIPAddr`, and `LookupTXT`.

Control flow: suffixes are normalized. `LookupIPAddr` lowercases/trims the hostname, matches configured suffixes, requires `<encoded-ip>.<peerID>.<suffix>`, validates the peer ID, rejects labels starting/ending with hyphen, parses IPv4 by replacing hyphens with dots, parses IPv6 by replacing hyphens with colons, and falls back to the underlying resolver on any mismatch. `LookupTXT` always delegates to fallback for ACME DNS-01 compatibility.

State and persistence: no persistent state; stores suffix list and fallback resolver.

Dependencies/integration: libp2p peer ID validation, net/netip, multiaddr-dns. Used by `DNSResolver` when AutoTLS DNS lookup skipping is enabled.

Risks: fallback is essential for future DNS record formats and invalid hostnames; TXT delegation must remain for certificate issuance. Tests cover IPv4, IPv6, multiple suffixes, fallback, errors, and TXT delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/p2pforge_resolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/p2pforge_resolver_test.go -->
# sources/distributed-fs/ipfs-kubo/core/node/p2pforge_resolver_test.go

Purpose: verifies deterministic p2p-forge DNS parsing and fallback behavior. Important helpers are `mockResolver`, `newTestResolver`, `assertLookupIP`, and tests for `LookupIPAddr` and `LookupTXT`.

Control flow: IP tests cover IPv4 ranges, trailing dot, uppercase suffix, full/compressed IPv6, loopback, and all-zero IPv6. Multiple suffix tests verify custom domains. Fallback tests ensure peerID-only, invalid peer ID, invalid IP encoding, leading hyphen, too many labels, and wrong suffix delegate to the fallback resolver. Error propagation is checked for fallback failure. TXT tests assert ACME challenge records are delegated and empty fallback records produce empty results.

State and persistence: pure in-memory mock resolver maps.

Dependencies/integration: Kubo config default domain suffix, Go net, testify. The tests protect AutoTLS DNS behavior and ACME compatibility.

Risks signaled: local parsing must not hijack unsupported names; otherwise future p2p-forge DNS formats or certificate validation could break.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/p2pforge_resolver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/peering.go -->
# sources/distributed-fs/ipfs-kubo/core/node/peering.go

Purpose: constructs and configures the peering service. Important APIs are `Peering` and `PeerWith`.

Control flow: `Peering` creates a boxo `PeeringService`, starts it on fx start, and stops it on fx stop through `shutdown.CloseWithCtx`. `PeerWith` returns an invoke option that adds configured peers to the service.

State and persistence: runtime peering state only; configured peers come from config and are not written here.

Dependencies/integration: boxo peering, libp2p host/peer, fx, shutdown helper. Wired by `Online` in `groups.go` and feeds trusted peers into AutoRelay elsewhere.

Risks: stop is bounded but `PeeringService.Stop` itself has no context; startup failure from `Start` propagates. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/peering.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/provider.go -->
# sources/distributed-fs/ipfs-kubo/core/node/provider.go

Purpose: owns content providing and reprovide orchestration for DHT and routing systems. Important APIs/types include `DHTProvider`, `NoopProvider`, `LegacyProvider`, `LegacyProviderOpt`, `SweepingProviderOpt`, `OnlineProviders`, `OfflineProviders`, strategy key-provider helpers, keystore migration helpers, unique-count persistence, and DHT availability checks.

Control flow: online provider setup validates strategy, creates a key provider, then chooses sweeping provider when DHT sweep and DHT routing are available, otherwise legacy provider. Legacy mode wraps boxo `provider.System`, defers key-provider injection until lifecycle start to break dependency cycles, and reports slow reprovide throughput. Sweeping mode builds resettable provider keystores, optionally purges unused on-disk keystores when interval is zero, migrates old inline keystore data, creates dual/single/fullrt providers with buffered queues, initializes and periodically syncs keystores from the selected strategy, closes provider before keystore, and monitors slow periodic queues.

State and persistence: repo datastore keys include `/provider`, `/provider/keystore`, `/reprovideStrategy`, and `/reprovideLastUniqueCount`; separate provider keystore datastores live under `<repo>/provider-keystore/{0,1}`. Unique strategies persist bloom counts. Queue clearing occurs when strategy changes.

Dependencies/integration: boxo blockstore/walker/mfs/pinner/provider, go-datastore/mount/namespace/query, Kubo config/repo/fsrepo/routing, libp2p DHT/fullrt/keystore/buffered providers, fx, shutdown. Risks include datastore migration interruption, path deletion guarded by suffix validation, long DAG walks, fullrt readiness delaying provides, HTTP-only routing falling back to legacy, and shutdown races. Tests cover unique-count persistence; other behavior is integration-heavy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/provider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/provider_test.go -->
# sources/distributed-fs/ipfs-kubo/core/node/provider_test.go

Purpose: tests persistence helpers for unique reprovide cycle counts. Important tests cover `readLastUniqueCount` and `persistUniqueCount`.

Control flow: tests create a fresh in-memory datastore, assert missing counts read as zero, round-trip several counts including `math.MaxUint64`, verify overwrites replace previous values, and assert corrupt byte lengths return zero rather than panicking.

State and persistence: models repo datastore writes under `reprovideLastUniqueCountKey` using an in-memory datastore.

Dependencies/integration: go-datastore, context, math, testify. It protects the bloom sizing feedback loop used by `+unique` and `+entities` provide strategies.

Risks signaled: corrupt or truncated persisted counts must not crash startup/reprovide; stale counts must be overwritten every successful cycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/provider_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/storage.go -->
# sources/distributed-fs/ipfs-kubo/core/node/storage.go

Purpose: constructs repo config/datastore providers and blockstore layers. Important APIs are `RepoConfig`, `Datastore`, `BaseBlocks`, `BaseBlockstoreCtor`, `GcBlockstoreCtor`, and `FilestoreBlockstoreCtor`.

Control flow: `RepoConfig` and `Datastore` expose repo values. `BaseBlockstoreCtor` creates a write-through blockstore, optionally adds a provider when `Provide.Strategy` includes `all`, wraps with hash-verifying `VerifBS`, cache, ID store, and optional hash-on-read validation. `GcBlockstoreCtor` adds a GC locker and GC blockstore. `FilestoreBlockstoreCtor` adds filestore support and optional provider integration before wrapping with GC and verification.

State and persistence: block data is persisted in the repo datastore and optional filestore references via the file manager. Provider callbacks may enqueue provides during Put operations when strategy includes `all`.

Dependencies/integration: boxo blockstore/filestore/provider, go-datastore, Kubo config/helpers/repo, third-party verifying blockstores, fx. Used by `Storage` group before blockservice, pinning, MFS, and provider wiring.

Risks: provider calls from blockstore are intentionally blocking, so provider queuing must be efficient; hash-on-read adds cost; filestore/urlstore changes persistence semantics. Tests are mostly integration-level outside this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/node/storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/shutdown/close.go -->
# sources/distributed-fs/ipfs-kubo/core/shutdown/close.go

Purpose: provides a bounded close helper for subsystems whose `Close` method lacks context. Important API is `CloseWithCtx`.

Control flow: starts the close function in a goroutine, waits for either its result or `ctx.Done`, returns the close error when completed, or logs an error and returns a wrapped context error when the deadline/cancel wins.

State and persistence: no persistence. It may intentionally leave the close goroutine running after timeout because process shutdown is imminent.

Dependencies/integration: context, time, go-log. Used throughout node services: blockservice, pinner, MFS, host, peerstore, resource manager, providers, peering, and routing.

Risks: timed-out close goroutines leak until process exit; this is accepted to honor shutdown deadlines. Tests cover success, error propagation, and timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/shutdown/close.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/shutdown/close_test.go -->
# sources/distributed-fs/ipfs-kubo/core/shutdown/close_test.go

Purpose: validates `CloseWithCtx` behavior. Important tests are `TestCloseWithCtx_finishesBeforeDeadline`, `TestCloseWithCtx_propagatesCloseError`, and `TestCloseWithCtx_timesOut`.

Control flow: first two tests use real timeout contexts and assert nil/error propagation. The timeout test runs under `synctest`, creates a short fake deadline, blocks the close function until after assertions, verifies elapsed fake time equals the deadline, checks `context.DeadlineExceeded`, then releases the goroutine so synctest can finish cleanly.

State and persistence: no external state.

Dependencies/integration: context, errors, testing/synctest, time. It protects bounded shutdown semantics used by many node lifecycle hooks.

Risks signaled: production intentionally leaks close goroutines on timeout, so tests need explicit release to avoid fake-clock blocked-goroutine failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/shutdown/close_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/shutdown/state.go -->
# sources/distributed-fs/ipfs-kubo/core/shutdown/state.go

Purpose: tracks daemon-wide graceful shutdown state for health checks and diagnostics. Important APIs are `MarkStarted`, `StartedAt`, and `InProgress`.

Control flow: `MarkStarted` uses atomic compare-and-swap to record the first shutdown timestamp in Unix nanoseconds and returns whether the caller won. `StartedAt` converts the stored timestamp to `time.Time` or returns zero time. `InProgress` checks whether the timestamp is nonzero.

State and persistence: process-global atomic `startedAt`; no disk persistence.

Dependencies/integration: sync/atomic and time. Used by daemon signal handling and health checks such as Docker `ipfs diag healthy`.

Risks: global state is intentionally monotonic for a process and cannot be reset except in tests. Tests cover initial, repeated, timestamp preservation, and concurrent behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/shutdown/state.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/shutdown/state_test.go -->
# sources/distributed-fs/ipfs-kubo/core/shutdown/state_test.go

Purpose: unit-tests shutdown state tracking. Important helpers/tests are `resetForTest`, `TestInProgressInitiallyFalse`, `TestMarkStartedFirstCallWins`, `TestMarkStartedPreservesFirstTimestamp`, and `TestMarkStartedConcurrent`.

Control flow: tests reset the package atomic, assert initial false/zero state, verify first mark wins, sleep briefly to ensure a later timestamp would differ, and launch 64 goroutines to assert exactly one concurrent winner.

State and persistence: mutates package-global atomic only; tests cannot run in parallel because they share global state.

Dependencies/integration: sync/atomic, testing, time. It protects health-check-visible shutdown semantics.

Risks signaled: replacing CAS with Store would corrupt the first timestamp and concurrent winner count; tests catch that.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/shutdown/state_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/coverage/Rules.mk -->
# sources/distributed-fs/ipfs-kubo/coverage/Rules.mk

Purpose: Makefile fragment for sharness coverage support. Important targets/variables are `coverage_deps`, `$(d)/ipfs`, `IPFS_COVER_DIR`, and `$(d)/sharness_tests.coverprofile`.

Control flow: prepares a `sharnesscover` directory, builds a coverage-enabled `ipfs` wrapper with `testrunmain`, adds dependencies when coverage goals are requested, exports coverage output directory, disables test plugins for the sharness coverage target, runs sharness tests through `ipfs-test-cover`, and merges generated coverage profiles with `gocovmerge`.

State and persistence: creates `coverage/sharnesscover`, `coverage/ipfs`, and `coverage/sharness_tests.coverprofile`; updates `CLEAN` and `COVERAGE` make variables.

Dependencies/integration: Kubo make system (`mk/header.mk`, `mk/footer.mk`), Go build helpers, sharness tests, `cmd/ipfs/ipfs-test-cover`, and `test/bin/gocovmerge`.

Risks: path manipulation prepends coverage wrapper to `PATH`; stale cover files are removed only through target setup/CLEAN. No direct unit tests; make/CI coverage jobs are the signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/coverage/Rules.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/coverage/main/main.go -->
# sources/distributed-fs/ipfs-kubo/coverage/main/main.go

Purpose: coverage-only wrapper binary used when collecting sharness coverage. Important API is `main`, built only with `testrunmain`.

Control flow: reads `IPFS_COVER_DIR`, creates a coverage profile temp file and return-code temp file, executes `ipfs-test-cover` with `-test.run ^TestRunMain$`, coverprofile path, and original CLI args after `--`, forwards stdio/env, sets Linux parent-death signal, forwards SIGHUP/SIGINT/SIGTERM to the child after start, waits for the child, reads the return code file, strips the trailing byte, parses an integer, and exits with that status.

State and persistence: writes temporary coverage and return-code files; coverage dir comes from make. No repo datastore state.

Dependencies/integration: os/exec, signal/syscall, `ipfs-test-cover`, and the `Rules.mk` coverage target.

Risks: assumes return file has at least one byte and a trailing delimiter; signal-forwarding goroutine blocks on signal channel forever until process exit; `Pdeathsig` is Unix-specific. Test signal is build-tagged coverage CI behavior rather than direct unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/coverage/main/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/doc.go -->
# sources/distributed-fs/ipfs-kubo/doc.go

Purpose: package documentation stub for the root `ipfs` package.

Control flow: no executable logic; it contains a package comment stating IPFS is a global, versioned, peer-to-peer filesystem and declares `package ipfs`.

State and persistence: none.

Dependencies/integration: participates in Go package documentation and root package compilation.

Risks and tests: no runtime risk; build/package documentation checks are the only signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/docker-compose.yaml -->
# sources/distributed-fs/ipfs-kubo/docker-compose.yaml

Purpose: provides a default Docker Compose service for running Kubo. Important entries are the `ipfs` service, persistent volumes, `IPFS_PATH`, and port mappings.

Control flow: Compose builds the local Dockerfile, restarts unless stopped, mounts `ipfs_path` at `/data/ipfs`, FUSE volumes at `/ipfs` and `/ipns`, sets `IPFS_PATH=/data/ipfs`, exposes swarm TCP/UDP port 4001 on all interfaces, and binds API 5001 plus gateway 8080 to loopback only.

State and persistence: named volumes persist repo data and FUSE mount content across container restarts.

Dependencies/integration: Docker Compose v3.8, local Dockerfile, Kubo container entrypoint behavior. It aligns with network defaults used by the node/libp2p code in this subset.

Risks: swarm ports are remotely reachable by default; API and gateway are safer on loopback but users extending compose can expose admin API accidentally. No automated tests in this file; validation is Docker Compose parsing and runtime smoke testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/docker-compose.yaml -->
