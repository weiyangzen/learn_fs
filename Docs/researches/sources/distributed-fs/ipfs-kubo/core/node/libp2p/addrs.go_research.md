# sources/distributed-fs/ipfs-kubo/core/node/libp2p/addrs.go

Purpose: handles address filtering, advertised-address construction, dead-listener diagnostics, listener options, and AutoTLS p2p-forge certificate manager setup. Important APIs include `AddrFilters`, `findDeadListeners`, `listenEndpoint`, `explicitListens`, `MonitorDeadListeners`, `makeAddrsFactory`, `AddrsFactory`, `ListenOn`, `P2PForgeCertMgr`, and `StartP2PAutoTLS`.

Control flow: `AddrFilters` converts configured masks to a `ma.Filters` connection gater. Dead-listener detection compares resolved interface listen addrs against `Swarm.AddrFilters` and `Addresses.NoAnnounce`, classifying explicit specific-IP listeners by IP/transport/port rather than full multiaddr text. `MonitorDeadListeners` runs at startup and on `EvtLocalAddressesUpdated`, deduplicating findings. `makeAddrsFactory` applies Announce override, AppendAnnounce dedupe, NoAnnounce exact/CIDR filtering, and drops empty multiaddrs. `AddrsFactory` composes p2p-forge address processing before announce filtering when AutoTLS is active. AutoTLS setup creates certificate storage under the repo and starts/stops the forge manager.

State and persistence: p2p-forge certificates live in `<repo>/p2p-forge-certs`. Runtime monitors keep in-memory seen findings.

Dependencies/integration: libp2p options, event bus, basic host addrs factory, multiaddr filters, certmagic, p2p-forge, Kubo config. Risks include silently skipped malformed diagnostic masks, fatal listener misconfiguration hiding behind debug logs, and cert storage/registration failures. Tests cover dead-listener classification and empty multiaddr filtering.
