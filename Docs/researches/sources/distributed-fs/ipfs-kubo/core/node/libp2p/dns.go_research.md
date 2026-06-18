# sources/distributed-fs/ipfs-kubo/core/node/libp2p/dns.go

Purpose: adapts Kubo's multiaddr DNS resolver into a libp2p option. Important API is `MultiaddrResolver`.

Control flow: it appends `libp2p.MultiaddrResolver(swarm.ResolverFromMaDNS{Resolver: rslv})` to the grouped libp2p options and returns no error.

State and persistence: no state beyond injecting the resolver into host construction.

Dependencies/integration: depends on libp2p, libp2p swarm resolver adapter, and `go-multiaddr-dns`. Provided by `BaseLibP2P` so host dialing/listening can resolve DNS multiaddrs consistently with Kubo DNS configuration.

Risks: correctness depends on the resolver injected from `core/node/dns.go`; this file is thin and has no direct tests.
