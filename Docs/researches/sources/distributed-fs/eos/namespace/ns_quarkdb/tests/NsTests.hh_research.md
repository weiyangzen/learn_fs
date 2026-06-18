# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/NsTests.hh

Purpose: Declares the shared QuarkDB namespace test fixture and QDB reset guard.
Important APIs/types/functions: `FlushAllOnConstruction`, `SizeMapper`, `NsTests`, lazy service/view accessors, flusher/qclient helpers, `setSizeMapper`, `populateDummyData1`, `cleanNSCache`, and protected `initServices`.
Control flow: tests derive from `NsTestsFixture` in `TestUtils.hh`, then call fixture accessors; initialization is deferred until first use.
State/persistence: holds `RWMutex`, config map, flush guard, `unique_ptr<QuarkNamespaceGroup>`, and optional quota size mapper.
Dependencies/integration: forward-declares service/view/flusher types, includes `NamespaceGroup.hh`, `Members.hh`, and namespace test macros.
Risks: shared fixture API can encourage tests to depend on deterministic allocator state after `FLUSHALL`; no copying controls are explicit, though ownership fields make copying unavailable.
Test signals: this header is the public contract for all integration tests.
