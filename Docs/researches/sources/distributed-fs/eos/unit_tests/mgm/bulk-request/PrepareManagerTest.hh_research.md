# sources/distributed-fs/eos/unit_tests/mgm/bulk-request/PrepareManagerTest.hh

## sources/distributed-fs/eos/unit_tests/mgm/bulk-request/PrepareManagerTest.hh

Purpose: provides shared fixtures and RAII helpers for prepare-manager unit tests.

Important APIs and types: `ClientWrapper` builds and owns an `XrdSecEntity` from protobuf helpers. `ErrorWrapper` builds and owns an `XrdOucErrInfo`. `PrepareManagerTest` initializes and resets `eos::common::Mapping`, exposes `getDefaultClient()`, `getDefaultError()`, `generateDefaultPaths()`, and `generateEmptyOinfos()`. `BulkRequestPrepareManagerTest` derives from `PrepareManagerTest`.

Control flow: setup initializes global mapping before each test; teardown resets it. Path generation returns reverse-numbered `pathN` strings. Opaque-info generation returns empty strings matching the path count.

State and persistence: manages heap allocations for XRootD client/error objects to avoid leaks. It also touches process-global mapping state, so teardown is essential for isolation.

Dependencies and integration: includes `XrdMgmOfs`, XRootD version headers, gtest/gmock, `PrepareUtils`, auth proto utilities, and `PrepareArgumentsWrapper`.

Risks and test signals: the helper returns wrappers by value; callers rely on RAII lifetimes lasting through the prepare call. Any change in auth proto conversion or mapping initialization can affect all prepare tests.
