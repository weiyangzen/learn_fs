# sources/distributed-fs/ipfs-kubo/core/node/ipns.go

Purpose: configures IPNS validation, resolution, and republishing. Important APIs are `DefaultIpnsCacheSize`, `RecordValidator`, `Namesys`, and `IpnsRepublisher`.

Control flow: `RecordValidator` returns a namespaced validator for public keys and IPNS records backed by the peerstore key book. `Namesys` builds a boxo namesystem using repo datastore, DNS resolver, max cache TTL, and optional cache size. `IpnsRepublisher` constructs a republisher with the namesystem, repo datastore, private key, and keystore, applies configured interval/lifetime, checks lifetime is not shorter than interval, and starts it through `lcStartStop`.

State and persistence: IPNS data uses the repo datastore and keystore. Republisher state is runtime only, but it republishes persisted local records.

Dependencies and integration: boxo IPNS/namesys/republisher, libp2p record validation, peerstore, repo, and DNS resolver. Used by `IPNS`, `Online`, and `Offline` groups.

Risks: bad duration strings or unsafe intervals abort startup; too-short record lifetime would cause expiring records and is rejected. Test coverage is indirect via config and namesys tests outside this file.
