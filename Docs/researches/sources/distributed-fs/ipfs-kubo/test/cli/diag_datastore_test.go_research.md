# sources/distributed-fs/ipfs-kubo/test/cli/diag_datastore_test.go

Purpose: tests `ipfs diag datastore` offline access, counting, JSON output, raw get/put helpers, repo-lock behavior, and provider-keystore namespace visibility.

Important APIs/functions: `TestDiagDatastore`, harness datastore helpers `DatastoreCount`, `DatastorePut`, `DatastoreHasKey`, `DatastoreGet`, and provider config flags.

Control flow: subtests cover missing-key errors, counts after pinning, JSON count format, offline operation without daemon, put/get roundtrip, failure while daemon holds the repo lock, unified provider keystore counts under `/provider/keystore/{0,1}/`, and behavior when provider keystore directories are absent.

State/persistence: creates pins, direct datastore entries, provider-keystore directories, and toggles `Provide.DHT.SweepEnabled`/`Provide.Enabled`.

Dependencies/integration: repo datastore layer, diagnostic CLI, JSON encoder, provider keystore stores, pinning, and daemon lock detection.

Risks/test signals: validates operational tooling and hidden provider datastores. Several subtests only assert counts are nonzero/nonnegative, so they are smoke-level rather than byte-level format checks.
