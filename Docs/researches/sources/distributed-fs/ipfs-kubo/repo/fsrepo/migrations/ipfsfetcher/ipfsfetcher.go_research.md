# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/ipfsfetcher/ipfsfetcher.go

Purpose: implements a migration fetcher that starts a temporary Kubo node and retrieves distribution files over IPFS.

Important APIs and control flow: `NewIpfsFetcher` normalizes dist path, limit, repo root, and user config. `Fetch` lazily initializes once: reads bootstrap/peering config, creates a temp repo with a generated Ed25519 identity and DHT client routing, opens it, starts an online node, then calls CoreAPI UnixFS `Get` on the parsed distribution path. Fetched paths are recorded under a mutex. `Close` stops the node and removes temp repo once.

State and persistence: creates a temp IPFS repo and node, records fetched paths in memory, and removes temp state on close.

Dependencies and integration: uses Kubo core/coreapi, libp2p DHT client, fsrepo init/open, config parsing, Boxo files/path, and migration `Fetcher`.

Risks and test signals: expensive and network-dependent; plugin loading is assumed done before temp repo init. `FetchedPaths` returns the internal slice directly. Config read errors are logged to stderr and ignored. Tests cover fetcher operation in epic mode, path parsing/config reads, and bad config handling.
