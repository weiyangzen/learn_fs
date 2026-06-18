# sources/distributed-fs/openafs/src/rx/xdr.h

## Purpose
`xdr.h` declares the OpenAFS XDR public interface, core data types, operation enum, stream handle layout, ops macros, inline encode/decode macros, and namespace-remapping macros.

## Important APIs, Types, and Functions
- `enum xdr_op` defines `XDR_ENCODE`, `XDR_DECODE`, and `XDR_FREE`.
- `XDR` contains `x_op`, an `xdr_ops` vector, public/private pointers, base pointer, and `x_handy` scratch integer.
- `xdrproc_t` adapts to platforms needing fixed parameters instead of variadic calls.
- `struct xdr_discrim` describes discriminated-union arms.
- `XDR_GETINT32`, `XDR_PUTINT32`, `XDR_GETBYTES`, `XDR_PUTBYTES`, `XDR_GETPOS`, `XDR_SETPOS`, `XDR_INLINE`, and `XDR_DESTROY` dispatch into the active backend.
- `IXDR_*` macros optimize inline network-order 32-bit primitive access.

## Control Flow
The header defines dispatch macros rather than runtime logic. All XDR implementation files install an `xdr_ops` vector, and generic marshalling routines call back through this vector.

## State and Persistence
`XDR` instances own backend-specific stream state through `x_private`, `x_base`, and `x_handy`; ownership and persistence depend on the backend. The header also maps common `xdr_*` names to `afs_xdr_*` for non-NT builds to avoid namespace collisions.

## Dependencies and Integration Points
Included by RX, rxgen-generated code, tests, and all XDR backends. It bridges platform headers, kernel/user allocation hooks, OpenAFS integer types, and `xdr_prototypes.h`.

## Risks and Edge Cases
Backend implementations must fully populate ops entries used by callers; some backends intentionally set unsupported operations to `NULL`, so generic callers must avoid unsupported operations. Inline macros assume alignment and network-order 32-bit units. The `xdrproc_t` signature variations are sensitive to ABI/calling-convention mismatches.

## Test Signals
Compile coverage across kernel/user and platform targets is important. Runtime signals include successful generic type round-trips over every backend and safe failure when unsupported operations are not invoked.
