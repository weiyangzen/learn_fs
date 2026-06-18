# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/ContainerMDSvcTest.cc

Purpose: Integration tests for QuarkDB-backed container metadata service behavior.
Important APIs/types/functions: `ContainerMDSvcF` derives from `NsTestsFixture`; tests use `containerSvc()`, `mdFlusher()`, and `view()`.
Control flow: `BasicSanity` creates root/child containers, manipulates access mode, hierarchy links, attributes, updates stores, synchronizes flushers, removes a subtree member, restarts services with `shut_down_everything()`, verifies persisted state, then cleans up. `getContainerMDWhenContIsLockedShouldNotLock` locks a container and ensures ID retrieval in another thread does not block on that metadata lock.
State/persistence: validates QDB persistence of container count, names, hierarchy, access metadata, and extended attributes across service restart.
Dependencies/integration: depends on container/file services, metadata flusher, hierarchical view, and the shared QDB fixture.
Risks: fixed ID assumptions during cleanup can couple tests to allocator state; concurrency test only checks join completion, not timing.
Test signals: strong coverage for container CRUD, attribute replacement, permission checks, flush/reload, and non-locking retrieval semantics.
