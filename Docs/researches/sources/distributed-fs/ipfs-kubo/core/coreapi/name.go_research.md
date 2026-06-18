# sources/distributed-fs/ipfs-kubo/core/coreapi/name.go

Purpose: implements CoreAPI IPNS publish, search, resolve, and key lookup.

Important APIs/types/functions: `NameAPI` methods `Publish`, `Search`, `Resolve`, and helper `keylookup`.

Control flow: `Publish` checks mount/publish restrictions, parses options, handles delegated publishing mode by requiring configured delegated publishers, otherwise checks online status respecting allow-offline, resolves the private key by name or PeerID, builds EOL/TTL/sequence/v1-compat publish options, calls namesys `Publish`, and returns the IPNS name for the key. `Search` checks online permissively, optionally creates a cache-bypassing namesys resolver, normalizes names to `/ipns/`, starts `ResolveAsync`, and streams results to an output channel. `Resolve` consumes `Search` results until completion or first error and returns the last path.

State and persistence behavior: `Publish` writes IPNS records through the configured namesys/routing stack, which may be local datastore, DHT, or delegated publisher depending on options/config. Search/resolve are read-only but may consult caches and network.

Dependencies and integration points: integrates with CoreAPI key management, repo config `Ipns.DelegatedPublishers`, namesys, routing, DNS resolver, keystore, fusemount publish context, and libp2p peer IDs.

Risks: delegated mode only checks delegated publisher configuration before calling namesys; actual remote publish failures surface later. `Resolve` returns the last successful async result, which is intentional for newer records but depends on namesys stream ordering. Key lookup by PeerID scans the full keystore.

Test signals: covered by CoreAPI interface tests; path/name resolution also indirectly covered by `resolve.go` behavior.
