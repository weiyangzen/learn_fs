# sources/distributed-fs/ipfs-kubo/repo/fsrepo/fsrepo_test.go

Purpose: tests core filesystem repo lifecycle properties.

Important APIs and control flow: `TestInitIdempotence` calls `Init` repeatedly. `TestCanManageReposIndependently` initializes two repos, opens both, closes/removes one while the other remains open, then closes/removes the other. `TestDatastoreGetNotAllowedAfterClose` checks datastore operations fail after repo close. `TestDatastorePersistsFromRepoToRepo` writes through one open, closes, reopens, and reads. `TestOpenMoreThanOnceInSameProcess` asserts `Open` returns the same reference through `OnlyOne` and reference-counted close releases after both closes.

State and persistence: uses temp repos, version/config/datastore files, and actual datastore writes.

Dependencies and integration: exercises `config.DefaultDatastoreConfig`, fsrepo locking, datastore persistence, and `repo.OnlyOne`.

Risks and test signals: covers major lifecycle invariants but not migration mismatch, user config files, API/gateway file writes, resource override parsing, swarm key reads, or lock wait environment behavior.
