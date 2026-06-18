# Research: sources/distributed-fs/ipfs-kubo/config/init.go

Purpose: Builds initial Kubo config defaults and creates new peer identities.

Important APIs/types/functions: `Init`, `InitWithIdentity`, connection manager/resource manager defaults, `addressesConfig`, `DefaultDatastoreConfig`, datastore spec helpers (`pebbleSpec`, `badgerSpec`, `flatfsSpec` and measure variants), and `CreateIdentity`.

Control flow, state, and persistence: `Init` generates an identity then delegates to `InitWithIdentity`. Initial config sets API/gateway headers, default swarm/API/gateway addresses, flatfs datastore, Bootstrap/DNS/delegated routing/IPNS publishers to `"auto"`, MDNS on, mount paths, gateway defaults, and empty remote pinning services. `CreateIdentity` validates key options, generates RSA or Ed25519 keys, stores the private key as base64, derives PeerID, and writes progress messages to the supplied writer.

Dependencies and integration points: Uses libp2p crypto/peer, Kubo options, Cockroach Pebble version constants, and config profiles. fsrepo init persists the returned config.

Risks and test signals: Identity private keys are stored unencrypted. Default `"auto"` values require AutoConf to remain enabled or replaced. Datastore specs are untyped maps and plugin-dependent. `init_test.go` covers RSA/Ed25519 identity generation and rejects Ed25519 size options; `autoconf_test.go` covers init auto placeholders.
