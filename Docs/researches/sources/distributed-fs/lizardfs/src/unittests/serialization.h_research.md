# sources/distributed-fs/lizardfs/src/unittests/serialization.h

Purpose: Provides small test helpers for serialization/deserialization round trips.

Important APIs/types/functions: Generic serialization test templates/macros for comparing serialized and deserialized values; integration with `common/serialization`.

Control flow: Helpers serialize input values into a buffer, deserialize into output values, and assert equality or expected serialized shape depending on the helper used.

State and persistence: Test local buffers only. No persistence.

Dependencies and integration: Used by unit tests for serializable classes and protocol payloads. Depends on common serialization APIs and GTest-style equality.

Risks and test signals: Generic helpers assume equality operators and deterministic serialization. They are useful for positive tests but do not replace malformed-buffer testing.
