# sources/distributed-fs/ipfs-kubo/repo/mock.go

Purpose: provides a lightweight, non-thread-safe in-memory-ish implementation of `repo.Repo` for tests and components that do not need full fsrepo behavior.

Important APIs and control flow: `Mock` stores config, datastore, keystore, and file manager fields. It returns pointers or values directly for `Config`, `SetConfig`, `Datastore`, `Keystore`, `FileManager`, and nil swarm key. Unsupported methods return `errTODO`.

State and persistence: no disk persistence; delegates datastore close to the configured datastore and mutates the embedded config field directly.

Dependencies and integration: implements the `Repo` interface and integrates with components expecting a repo but not API/gateway/config-key operations.

Risks and test signals: not thread-safe, returns direct config pointer, and `Close` panics if datastore is nil. Unsupported methods are explicit TODO errors. No direct tests in this subset.
