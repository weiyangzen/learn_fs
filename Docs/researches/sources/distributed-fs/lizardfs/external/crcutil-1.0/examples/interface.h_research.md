<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/examples/interface.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/examples/interface.h

## Purpose
This header declares a clean virtual CRC interface for projects that want to use crcutil without including crcutil's implementation templates and macros throughout their codebase. It is intentionally small and opaque: users create a `CRC` object through a factory, operate through virtual methods, and destroy through `Delete`.

## Important APIs and types
- `crcutil_interface::UINT64` is an unsigned long long alias used for the public low/high CRC representation.
- `CRC::Create` constructs an implementation from a reversed-bit polynomial split into low/high words, polynomial degree, canonical mode, rolling CRC start value, rolling window length, optional SSE4.2 preference, and optional allocated-memory output.
- `Delete` destroys an instance created by `Create`.
- `IsSSE42Available` reports hardware support for SSE4.2 CRC instructions where compiled.
- Property methods are `GeneratingPolynomial`, `Degree`, `CanonizeValue`, `RollStartValue`, `RollWindowBytes`, and `SelfCheckValue`.
- Computation methods are `Compute`, `RollStart`, `Roll`, `CrcOfZeroes`, `ChangeStartValue`, `Concatenate`, `StoreComplementaryCrc`, `StoreCrc`, and `CrcOfCrc`.
- The constructor and destructor are protected, enforcing factory allocation and custom deletion.

## Control flow and usage contract
Callers first invoke `CRC::Create`. If arguments are illegal, it returns `NULL`; otherwise it returns a polymorphic object. The caller initializes CRC values in `lo` and optionally `hi`, then passes pointers into computation methods. For CRC degrees 64 or less, `hi` is optional and not touched according to the interface comments. For rolling CRC, callers should call `RollStart` before `Roll`, and should avoid rolling operations when the configured rolling window length is zero.

## State and persistence behavior
The interface exposes no mutable member fields. Concrete implementations are intended to be immutable constants with precomputed tables, so applications should create a small number of instances and reuse them. Persistence is limited to process memory. The `allocated_memory` output can be used by callers to inspect or track the raw allocation returned by the aligned allocator in the implementation.

## Dependencies and integration points
The header includes `std_headers.h` for `size_t` and is implemented by `examples/interface.cc`. It integrates with crcutil's generic, rolling, and hardware-accelerated CRC implementations while keeping those dependencies out of downstream translation units. `examples/usage.cc` demonstrates the public contract.

## Risks and edge cases
The API uses raw pointers, nullable output parameters, and a custom lifecycle; misuse can leak memory or dereference null pointers. The comments say `RollStart` and `Roll` should not be called when rolling CRC is disabled, but enforcement is implementation-dependent. For CRC widths above 64 bits, callers must provide the high-word pointers even though many methods default `hi` to `NULL`; that default is only safe for 64-bit-or-smaller CRCs. `Create` returns `NULL` instead of an error object, so callers need explicit validation.

## Test signals
Compile a downstream file including only `interface.h` to ensure implementation details remain hidden. Exercise every public method with a known CRC32C configuration and verify full-message CRC equals incremental CRC, rolling results match direct computation, `Concatenate` matches direct concatenation, and stored CRC/complementary CRC properties hold. Add negative tests for illegal `Create` arguments and null pointer handling at the application boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/examples/interface.h -->
