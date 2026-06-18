# sources/distributed-fs/openafs/src/rx/xdr_float.c

## Purpose
`xdr_float.c` implements floating-point XDR primitives for non-Windows platforms.

## Important APIs, Types, and Functions
- `xdr_float()` serializes a `float` by treating its bits as one 32-bit unit.
- `xdr_double()` serializes a `double` as two 32-bit units with word ordering chosen for the supported non-NT environments.

## Control Flow
Each function switches on `x_op`: encode writes raw integer words, decode reads them, free succeeds without action. On `AFS_NT40_ENV`, both return `FALSE`.

## State and Persistence
No persistent state or allocation.

## Dependencies and Integration Points
Used by generated XDR routines for IDL `float` and `double` types. Depends on backend `XDR_GETINT32` and `XDR_PUTINT32`.

## Risks and Edge Cases
The file explicitly warns the implementation is non-portable. It assumes local floating-point representation and word ordering compatible with the chosen XDR layout; Windows is unsupported here.

## Test Signals
Round-trip representative floats/doubles on supported platforms and compile-time exclusion or expected failure on NT builds. Cross-endian interoperability is the key risk signal.
