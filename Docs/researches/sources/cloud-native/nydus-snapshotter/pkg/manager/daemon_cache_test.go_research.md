# Research: sources/cloud-native/nydus-snapshotter/pkg/manager/daemon_cache_test.go

This test file validates the basic semantics of `DaemonCache`. It creates two daemon objects with explicit IDs, adds them, retrieves them by ID, verifies list membership and size, removes by pointer, removes by ID, updates a daemon back into the cache, and removes it again.

The test signals confirm that the cache stores pointers, returns expected daemon objects, tracks size, and supports both removal styles. It also verifies `Update` can repopulate the cache, which matters during manager recovery from persisted daemon records.

Coverage is intentionally narrow. It does not test replacing an existing daemon via `Add`, callback behavior in `GetByDaemonID`, concurrent access, list nil behavior for empty caches, or interactions with the persistent store. There is no filesystem or process state. Because the cache is a shared lookup path for manager, filesystem, and metrics code, concurrency behavior remains a residual risk despite mutex use.
