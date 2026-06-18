## sources/distributed-fs/beegfs/meta/tests/TestSerialization.h

Purpose: Declares the metadata serialization test fixture and generic round-trip helper.

Important APIs/types/functions: `TestSerialization` derives from `::testing::Test`, declares session-store initialization and random-fill helpers, and defines templated `testObjectRoundTrip(Obj&)`.

Control flow: `testObjectRoundTrip()` computes serialized size, writes to a buffer, deserializes to a default object, verifies consumption, serializes the result again, and asserts byte-for-byte equivalence.

State and persistence: All state is in-memory test data.

Dependencies and integration: Includes `NetMessage.h`, GoogleTest, and `SessionStore.h`. The helper works for BeeGFS types that support default construction and `%` serialization.

Risks and test signals: The helper checks self-consistency, not compatibility with previous releases. Types without meaningful default constructors or equality need separate tests.
