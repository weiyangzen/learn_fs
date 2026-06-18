# sources/distributed-fs/ipfs-kubo/repo/fsrepo/config_test.go

Purpose: validates datastore config parsing and creation for default mount, LevelDB, flatfs, and measurement wrapper specs.

Important APIs and control flow: the tests unmarshal JSON snippets into `config.Datastore` or generic spec maps, call `fsrepo.AnyDatastoreConfig`, compare `DiskSpec().String()` to expected minimal JSON, then call `Create` in a temp dir and assert the concrete datastore type. The default config test initializes and injects plugins so external datastore handlers are registered.

State and persistence: creates datastore directories under `t.TempDir`; the disk spec checks represent persistent layout identity and are used by `FSRepo.openDatastore` to reject mismatched repos.

Dependencies and integration: depends on plugin loader injection, `config`, `reflect`, and `fsrepo` datastore handlers.

Risks and test signals: strong signal that runtime-only wrapper fields such as measurement prefixes are excluded from disk specs and mount ordering is deterministic. It does not test invalid specs, duplicate handler registration, or datastore close behavior.
