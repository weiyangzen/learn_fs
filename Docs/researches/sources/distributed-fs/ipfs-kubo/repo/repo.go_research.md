# sources/distributed-fs/ipfs-kubo/repo/repo.go

Purpose: defines the core repository abstraction for persistent Kubo node state.

Important APIs and control flow: `Repo` includes config read/write and key-level config mutation, path, user resource overrides, config backup, datastore, storage usage, keystore, filestore manager, API/gateway address writers, swarm key reading, and `io.Closer`. `Datastore` is `go-datastore.Batching` and must be thread-safe. `ErrApiNotRunning` standardizes missing API address behavior.

State and persistence: the interface represents persistent config, datastore, keystore, network address files, swarm key, and resource override data, but does not dictate backing storage.

Dependencies and integration: implemented by `fsrepo.FSRepo`, `repo.Mock`, and `repo.OnlyOne` refs; consumed by node construction and CLI components.

Risks and test signals: `Config` returns a mutable pointer with a warning that callers must clone before changes. Thread-safety expectations are implicit for datastore and implementation-specific for config mutation.
