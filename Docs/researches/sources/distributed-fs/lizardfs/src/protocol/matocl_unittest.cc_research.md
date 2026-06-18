# sources/distributed-fs/lizardfs/src/protocol/matocl_unittest.cc

Purpose: Unit tests for selected master-to-client packet helpers, mainly chunk read/write responses, chunk health state, and ACL-related responses.

Important APIs/types/functions: Tests `FuseReadChunkData`, `FuseReadChunkStatus`, `FuseWriteChunkData`, `FuseWriteChunkStatus`, `FuseWriteChunkEnd`, `XorChunksHealth`, `FuseDeleteAcl`, `FuseGetAclStatus`, `FuseGetAclResponse`, and `FuseSetAcl`.

Control flow: Each packet test constructs a payload, verifies the header type, removes the header, verifies the packet version when meaningful, deserializes fields, and asserts round-trip equality. `XorChunksHealth` populates availability and replication state across goals and part counts, serializes it, and compares per-goal/per-part counters after deserialization.

State and persistence: Test-only in-memory state. No socket, filesystem, or metadata persistence.

Dependencies and integration: Depends on chunk address/type structures, ACL classes, replication/availability state classes, GTest, and shared packet test helpers. It protects critical client-side decoding of master responses.

Risks and test signals: Good positive coverage for EC chunk server lists and ACL serialization. It does not cover most of the large `matocl.h` packet surface, wrong-version rejection, or malformed responses. There is a minor copy/paste signal in the write-status version check using the read chunk status constant, currently equal in value.
