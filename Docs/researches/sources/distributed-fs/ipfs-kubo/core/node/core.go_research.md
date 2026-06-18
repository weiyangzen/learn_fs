# sources/distributed-fs/ipfs-kubo/core/node/core.go

Purpose: builds core IPLD, block, pinning, fetcher, resolver, and MFS services for an fx-managed Kubo node. Important APIs are `BlockService`, `Pinning`, `FetcherConfig`, `PathResolverConfig`, `Dag`, `Files`, `FetchersOut/In`, `PathResolversOut`, and `syncDagService`.

Control flow: `BlockService` wraps a blockstore and exchange, then registers bounded shutdown. `Pinning` parses `Provide.Strategy`, wraps the DAG service in `syncDagService`, chooses pinned or root DHT provider hooks, and closes before the repo. `FetcherConfig` creates online and offline IPLD/UnixFS fetchers, adding dag-pb support and UnixFS reification. `Files` loads `/local/filesroot`, creates an empty UnixFS root when absent, validates protobuf roots when present, configures MFS import options, and optionally wires the DHT provider only for `mfs` strategies.

State and persistence: MFS root CID is persisted at `FilesRootDatastoreKey`; pinner syncs block and filestore prefixes; `syncDagService.Sync` persists data before pinner operations. Dependencies include boxo blockservice, merkledag, MFS, dspinner, path resolver, repo datastore, and `core/shutdown`.

Integration points: consumed by grouped `Core`, `Storage`, `IPFS`, and online/offline service graphs. Risks are shutdown ordering with datastore-backed pinner operations, invalid persisted MFS CIDs, and strategy bits causing duplicate advertisements if roots and pinned are both enabled. Test signals are mostly integration-level; the comments document shutdown and provide-strategy invariants that downstream tests should preserve.
