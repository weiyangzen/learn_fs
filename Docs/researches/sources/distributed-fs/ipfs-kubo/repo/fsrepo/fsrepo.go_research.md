# sources/distributed-fs/ipfs-kubo/repo/fsrepo/fsrepo.go

Purpose: implements Kubo's filesystem-backed `repo.Repo`, including initialization, opening, locking, config persistence, datastore/keystore creation, API/gateway address files, resource overrides, filestore integration, and close semantics.

Important APIs and control flow: `Init` writes config, datastore spec, and repo version under `packageLock`. `Open` and `OpenWithUserConfig` delegate through `repo.OnlyOne`, call `open`, acquire `repo.lock` or wait based on `IPFS_WAIT_REPO_LOCK`, validate repo version through migrations, check writability, load config/resource overrides, open datastore, open keystore, and optionally create a filestore manager. `Close` removes `api` and `gateway`, closes datastore, marks closed, and releases the lock.

State and persistence: owns files `config`, `datastore_spec`, `version`, `repo.lock`, `api`, `gateway`, `swarm.key`, `keystore`, and datastore contents. `SetAPIAddr` and `SetGatewayAddr` use temp files plus rename. `SetConfig` merges typed config into raw JSON to preserve unknown keys; `SetConfigKey` protects the private key selector.

Dependencies and integration: integrates with config serialization, fs locks, datastore handlers, metrics wrapping, migrations, libp2p resource overrides, multiaddr, and the `repo.Repo` interface.

Risks and test signals: global `packageLock` serializes broad operations and can bottleneck. `BackupConfig` returns the original name rather than the temp backup name, which is surprising. `Datastore()` after close returns a closed datastore. Version mismatch blocks open. Tests cover init idempotence, independent repos, persistence, close behavior, and same-process reference sharing.
