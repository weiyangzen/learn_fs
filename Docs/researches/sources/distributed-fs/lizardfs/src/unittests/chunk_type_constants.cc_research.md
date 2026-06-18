# sources/distributed-fs/lizardfs/src/unittests/chunk_type_constants.cc

Purpose: Defines reusable `ChunkPartType` constants for standard and XOR chunk layouts used in protocol and read-plan tests.

Important APIs/types/functions: Constants `standard`, `xor_1_of_2` through `xor_p_of_9`, built from `slice_traits::standard::ChunkPartType` and `slice_traits::xors::ChunkPartType`.

Control flow: Static constant initialization only.

State and persistence: Process-static test constants; no persistence.

Dependencies and integration: Implements declarations from `chunk_type_constants.h`; used by protocol serialization tests and other unit tests requiring stable chunk part fixtures.

Risks and test signals: Constants must match production `slice_traits` encoding. Only XOR levels listed here are available to tests; EC constants are not provided in this file.
