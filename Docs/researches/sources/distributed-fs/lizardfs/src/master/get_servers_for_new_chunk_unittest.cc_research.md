# sources/distributed-fs/lizardfs/src/master/get_servers_for_new_chunk_unittest.cc

Purpose: validates chunkserver selection for label satisfaction and long-run weighted distribution across many goal definitions.

Important APIs/types/functions: `createProxy()` builds a `Goal::Slice::ConstPartProxy`; `GetServersForNewChunkTests` maps string server names to labels and reinterprets map entries as fake `matocsserventry *`; `ChooseServers0..5` cover shortages and label constraints; `testScenario()` parses goal definitions, simulates many chunk placements, and verifies per-weight usage spread; `ChunkDistribution` enumerates standard, XOR, and erasure-code scenarios.

Control flow: each scenario repeatedly constructs a selector, adds servers with labels/weights, prepares shared history, chooses servers for every goal slice part with a shared `used` list, accumulates counts, and compares normalized usage.

State and persistence behavior: tests use in-memory `ChunkCreationHistory` to verify balancing over repeated placements; no disk persistence.

Dependencies/integration: depends on GoogleTest, media labels, goal config parser, and the chunk placement API.

Risks and test signals: tests use fake pointer identities and version/load factor zero, so they do not cover min-version or load-factor prioritization. Random shuffle can make distribution tests sensitive, though high iteration counts reduce variance. These tests are the main signal for preserving weighted placement behavior.
