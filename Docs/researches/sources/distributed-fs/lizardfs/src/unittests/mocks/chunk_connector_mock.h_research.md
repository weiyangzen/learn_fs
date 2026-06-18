# sources/distributed-fs/lizardfs/src/unittests/mocks/chunk_connector_mock.h

Purpose: Declares `ChunkConnectorMock`, a test connector that redirects chunkserver connection attempts to `ModuleMock` instances.

Important APIs/types/functions: Class `ChunkConnectorMock`; typedef `Modules`; constructor accepting an initializer list of logical address/mock pairs; override `startUsingConnection`.

Control flow: The header defines a mapping-based connector interface; the `.cc` starts each module and delegates mapped connections to the base connector using the mock's actual localhost port.

State and persistence: Stores the address-to-module map. No persistence; real sockets are opened by the modules and base connector during tests.

Dependencies and integration: Depends on production chunk connector types and network/chunk identifiers. Used by unit tests that need to inject a connector.

Risks and test signals: The mock is realistic enough for socket framing tests but only models configured servers. Unmapped addresses throw, which is useful test signal for missing fixtures.
