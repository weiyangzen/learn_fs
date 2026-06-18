# sources/distributed-fs/lizardfs/src/unittests/mocks/chunk_connector_mock.cc

Purpose: Implements a mock chunk connector that maps logical chunkserver addresses to `ModuleMock` localhost servers for tests.

Important APIs/types/functions: `ChunkConnectorMock` constructor; `ChunkConnectorMock::startUsingConnection`; `Modules` map from `NetworkAddress` to `ModuleMock*`; base `ChunkConnector::startUsingConnection`.

Control flow: The constructor stores the provided module map and calls `init()` on each `ModuleMock`. `startUsingConnection` looks up the requested logical server address, translates it to localhost plus the mock's listening port, and delegates to the production `ChunkConnector`; missing mappings throw `ChunkserverConnectionException`.

State and persistence: Maintains an in-memory address-to-mock map and starts mock listener threads. No persistent state.

Dependencies and integration: Used in tests that require a `ChunkConnector`-like object without network side effects.

Risks and test signals: Tests get real TCP connection behavior against mocks, but only for addresses explicitly registered in the map. Lifetime depends on the referenced `ModuleMock` objects staying alive while connections are used.
