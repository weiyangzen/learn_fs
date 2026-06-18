# sources/distributed-fs/lizardfs/src/unittests/chunk_type_constants.h

Purpose: Declares shared chunk part constants for tests.

Important APIs/types/functions: `extern const ChunkPartType` declarations for standard and XOR data/parity parts across levels 2, 3, 4, 6, 7, and 9.

Control flow: No runtime control flow.

State and persistence: Declares process-static constants defined in the `.cc`.

Dependencies and integration: Included by packet serialization tests to avoid repeated chunk type construction.

Risks and test signals: Header and implementation must stay synchronized. Missing declarations limit test coverage for newer chunk layouts.
