# sources/distributed-fs/eos/namespace/utils/DataHelper.hh

## Purpose
`DataHelper.hh` declares static utility methods for CRC calculation and copying POSIX file ownership metadata.

## Important APIs, Types, and Functions
`DataHelper` exposes `computeCRC32()`, `updateCRC32()`, `computeCRC32C()`, `updateCRC32C()`, `finalizeCRC32C()`, and `copyOwnership(const std::string& target, const std::string& source, bool ignoreNoPerm = true)`.

## Control Flow
The header contains declarations only. The intended call flow is direct static invocation without object construction.

## State and Persistence Behavior
CRC functions are stateless by contract. `copyOwnership()` is the only API with persistent side effects, changing target file ownership in the implementation when permissions allow.

## Dependencies and Integration Points
The header includes only integer and string types, keeping the interface light. It is suitable for inclusion by namespace code that needs checksums or ownership preservation without pulling in POSIX and zlib implementation details.

## Risks and Edge Cases
Raw `void*` buffers provide no length safety beyond the explicit `len` argument. The `ignoreNoPerm` default means callers must opt in to strict permission failure when ownership copying is required for correctness.

## Test Signals
Header-level tests are not applicable. Implementation tests should verify known checksums and ownership-copy permission behavior.
