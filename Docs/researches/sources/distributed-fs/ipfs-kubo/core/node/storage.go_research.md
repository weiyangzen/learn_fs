# sources/distributed-fs/ipfs-kubo/core/node/storage.go

Purpose: constructs repo config/datastore providers and blockstore layers. Important APIs are `RepoConfig`, `Datastore`, `BaseBlocks`, `BaseBlockstoreCtor`, `GcBlockstoreCtor`, and `FilestoreBlockstoreCtor`.

Control flow: `RepoConfig` and `Datastore` expose repo values. `BaseBlockstoreCtor` creates a write-through blockstore, optionally adds a provider when `Provide.Strategy` includes `all`, wraps with hash-verifying `VerifBS`, cache, ID store, and optional hash-on-read validation. `GcBlockstoreCtor` adds a GC locker and GC blockstore. `FilestoreBlockstoreCtor` adds filestore support and optional provider integration before wrapping with GC and verification.

State and persistence: block data is persisted in the repo datastore and optional filestore references via the file manager. Provider callbacks may enqueue provides during Put operations when strategy includes `all`.

Dependencies/integration: boxo blockstore/filestore/provider, go-datastore, Kubo config/helpers/repo, third-party verifying blockstores, fx. Used by `Storage` group before blockservice, pinning, MFS, and provider wiring.

Risks: provider calls from blockstore are intentionally blocking, so provider queuing must be efficient; hash-on-read adds cost; filestore/urlstore changes persistence semantics. Tests are mostly integration-level outside this file.
