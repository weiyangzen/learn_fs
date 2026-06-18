# sources/distributed-fs/lizardfs/src/protocol/cstocs_unittest.cc

Purpose: Unit tests for chunkserver-to-chunkserver packet serialization in `cstocs.h`. It validates the EC `ChunkPartType` paths for block requests and block-status replies.

Important APIs/types/functions: Test cases `GetChunkBlocks` and `GetChunkBlocksStatus`; `cstocs::getChunkBlocks`; `cstocs::getChunkBlocksStatus`; constants from `unittests/chunk_type_constants.h`; packet helpers `verifyHeader`, `removeHeaderInPlace`.

Control flow: The tests serialize known chunk ids, versions, chunk part types, block counts, and status bytes, then remove packet headers and deserialize into output variables. `LIZARDFS_VERIFY_INOUT_PAIR` asserts round-trip equality.

State and persistence: No persistence; all state is local test data in vectors and scalar pairs.

Dependencies and integration: Depends on GTest, LizardFS packet helpers, and chunk type constants. It supports confidence in peer chunkserver replication/repair messaging.

Risks and test signals: Positive round-trip tests catch field-order and version errors for the EC overloads. They do not exercise the legacy overloads, corrupted buffers, or version rejection paths.
