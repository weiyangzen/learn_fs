## sources/cloud-native/moby/daemon/libnetwork/store_test.go

Purpose: Shared helper test logic for validating local libnetwork datastore persistence and restore.

Important APIs and functions: `testLocalBackend` configures `OptionDataDir` and `DatastoreBucket`, creates a controller, creates a host network and endpoint, directly checks network and endpoint KV entries with `GetObject`, stops the controller, then constructs a second controller and resolves the network by ID.

Control flow and state: The test verifies both immediate store writes (`Exists()` on network and endpoint KV objects) and restart restore via `NetworkByID`. It intentionally closes and reopens the controller to prove the configured local store path and bucket are durable.

Dependencies and integration points: Exercises controller initialization, Bolt/local datastore configuration, network and endpoint creation paths, and network lookup after restore. It is called by platform-specific tests such as `TestBoltdbBackend`.

Risks covered: Prevents regressions where objects are only present in memory, the wrong bucket/data-dir is used, endpoint persistence is skipped, or restored networks fail to reattach enough controller state for lookup.

Test signals: Integration-level persistence coverage but limited to happy path; detailed stale-key/retry behavior in `store.go` is not directly exercised here.
