# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/HierarchicalViewTest.cc

Purpose: Large integration/regression suite for hierarchical namespace behavior, quota accounting, locking, path resolution, symlinks, and concurrent metadata access.
Important APIs/types/functions: uses `IView` create/get/rename/unlink/remove APIs, `IContainerMD`/`IFileMD` locking wrappers, `BulkNsObjectLocker`, `QuotaRecomputer`, `Resolver`, `RmrfHelper`, and helper `mapSize/createFiles`.
Control flow: tests create nested trees, assert path/name validation and conflicts, rename files/containers, reverse-resolve URIs, prevent deletion with replicas, restart and verify persistence, compute quotas, recompute nested quotas, check custom IDs, verify bulk lock ordering/waiting, mutate file size/location state concurrently, propagate mtime, follow symlinks, and stress cache clearing plus ID/path lookups across threads.
State/persistence: validates QDB hierarchy, quota nodes, tree size/file/container counters, location/unlinked-location sets, symlink targets, and metadata after service restart.
Dependencies/integration: integrates nearly all namespace layers: services, accounting views, lock helpers, resolver, quota recomputer, flusher, and qclient-backed fixture.
Risks: timing assertions with sleeps can be slow/flaky; several tests depend on deterministic IDs; one cleanup TODO documents a known problematic lost-container cleanup path.
Test signals: the strongest behavioral suite in this subset, especially for concurrency, locking semantics, quota isolation, rename safety, and cache reload correctness.
