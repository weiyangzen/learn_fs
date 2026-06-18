## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_standalone_libraries/lib_float_math.h

### Purpose
This header exposes the standalone float/double math helper API used by DML2 calculations.

### Important APIs, Types, And Functions
It declares modulo, min/max, floor/ceil, max-of-N, power, absolute value, logarithm, approximate log2, and round helpers.

### Control Flow
The header has no runtime flow. Its declarations allow DML2 code to use the local helper implementation instead of depending directly on platform math libraries.

### State, Persistence, And Dependencies
There is no state and no includes beyond the include guard. Implementations are in `lib_float_math.c`.

### Integration Points
Included by DCN4 FAMS2 PMO and SOC15 top mcache/scheduling code.

### Risks
The names resemble standard math functions but semantics differ from libc in precision and edge cases, so new callers should confirm inputs match the restricted behavior.

### Test Signals
Build tests should verify all declared functions are linked, and unit tests should pin edge-case semantics before using these helpers in new formulas.
