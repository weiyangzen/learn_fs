# sources/distributed-fs/lizardfs/src/protocol/matocs_unittest.cc

Purpose: Tests representative master-to-chunkserver packet serialization in `matocs.h`.

Important APIs/types/functions: Tests `SetVersion`, `DeleteChunk`, and `Replicate`; `matocs::setVersion`, `matocs::deleteChunk`, `matocs::replicateChunk`; `ChunkTypeWithAddress` vectors for replication sources.

Control flow: Tests serialize EC chunk commands, verify headers and versions where checked, remove headers, deserialize, and compare inputs to outputs. The replicate test includes multiple server addresses and chunk part types.

State and persistence: No persistence; local packet fixtures only.

Dependencies and integration: Uses GTest, packet helpers, and chunk type constants. Validates commands that master scheduling sends to chunkservers.

Risks and test signals: Positive coverage catches basic field-order regressions for critical commands. It does not cover all lifecycle command families, legacy overloads, partial replicate decoding, or error cases.
