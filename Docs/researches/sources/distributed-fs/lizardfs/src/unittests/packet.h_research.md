# sources/distributed-fs/lizardfs/src/unittests/packet.h

Purpose: Provides packet assertion helpers for protocol unit tests.

Important APIs/types/functions: `verifyHeader`; `removeHeaderInPlace`; `verifyVersion`; overloads using `std::vector<uint8_t>` and packet constants.

Control flow: Helpers deserialize packet headers/versions, assert expected type or version, and erase header bytes from buffers so tests can feed payloads to deserializers.

State and persistence: Mutates test buffers in-place when removing headers. No persistence.

Dependencies and integration: Included by protocol unit tests in this subset. Depends on GTest assertions and `protocol/packet.h`.

Risks and test signals: Header removal changes buffer indexing, so tests must call helpers in the correct order. These helpers centralize common packet test idioms.
