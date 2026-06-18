<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/examples/interface.cc -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/examples/interface.cc

## Purpose
This C++ file implements the clean `crcutil_interface::CRC` facade declared in `examples/interface.h`. It hides crcutil's template-heavy, macro-heavy implementation headers behind a stable virtual interface, centralizes CRC table allocation/alignment, and selects between generic, 128-bit SSE2-backed, and SSE4.2 CRC32C implementations.

## Important types and functions
- `kAlign` is a 4 KiB alignment boundary used for CRC tables and instances.
- Template class `Implementation<CrcImplementation, RollingCrcImplementation>` derives from `CRC` and adapts concrete crcutil implementations to the virtual facade.
- `Implementation::Create` uses `AlignedAlloc(sizeof(Self), offsetof(Self, crc_), kAlign, allocated_memory)` followed by placement new, ensuring internal CRC tables are aligned.
- `Delete` calls `AlignedFree(this)` rather than plain `delete`.
- Property methods expose generating polynomial, degree, canonical XOR value, rolling start value, rolling window size, and self-check CRC.
- Data methods implement `Compute`, `RollStart`, `Roll`, `CrcOfZeroes`, `ChangeStartValue`, `Concatenate`, `StoreComplementaryCrc`, `StoreCrc`, and `CrcOfCrc`.
- Static helper overloads `GetValue` and `SetValue` convert between the public `UINT64 lo/hi` representation and concrete crcutil CRC types.
- `CRC::IsSSE42Available` delegates to `Crc32cSSE4::IsSSE42Available()` on x86/x86_64 builds and returns false otherwise.
- `CRC::Create` validates arguments and chooses the implementation type.

## Control flow
The template adapter constructs `crc_` from polynomial, degree, and canonical mode, then constructs `rolling_crc_` from the CRC object, rolling window length, and rolling start value. Every virtual operation converts public `lo`/`hi` inputs to the concrete CRC type, delegates to crcutil's base or rolling implementation, and writes the result back through `SetValue`.

`CRC::Create` first rejects degree 0. For degrees above 64, it requires `HAVE_SSE2`, rejects degrees above 128, validates that polynomial and rolling start values fit the selected degree, chooses a `GenericCrc<uint128_sse2,...>` specialization based on architecture and GCC version, and returns an `Implementation<Crc128, RollingCrc<Crc128>>`. For 64-bit-or-smaller CRCs, it optionally selects `Crc32cSSE4` plus `RollingCrc32cSSE4` when `CRCUTIL_USE_MM_CRC32`, x86/x86_64, `use_sse4_2`, degree, polynomial, and high words match CRC32C constraints. Otherwise it validates that high words and out-of-degree bits are zero and returns a generic 64-bit implementation.

## State and persistence behavior
Instances are effectively immutable after construction: `crc_` and `rolling_crc_` are `const`, and no persistent global mutable state is modified besides the file-scope `kAlign`. Runtime state lives in allocated aligned memory owned by the returned `CRC*`. The caller must destroy it with `CRC::Delete`; the destructor is protected and not intended for direct deletion. `SelfCheckValue` computes a CRC over the in-memory `crc_` and `rolling_crc_` objects, providing a runtime integrity signal for generated tables.

## Dependencies and integration points
The implementation includes `aligned_alloc.h`, `crc32c_sse4.h`, `generic_crc.h`, `protected_crc.h`, and `rolling_crc.h` from crcutil, and `interface.h` for the public contract. It depends on configuration/architecture macros such as `HAVE_AMD64`, `HAVE_I386`, `HAVE_SSE2`, `CRCUTIL_USE_MM_CRC32`, and `GCC_VERSION_AVAILABLE`. It is demonstrated by `examples/usage.cc` and is a recommended pattern for projects that want to use crcutil without exposing internal template headers and macros across the whole codebase.

## Risks and edge cases
Memory management is nonstandard: callers must use `Delete`, and failed allocation is not explicitly checked before placement new. Public methods generally assume non-null `lo` and, for CRC widths above 64 bits, non-null `hi`; passing null `hi` for a 128-bit instance can dereference null in `GetValue`/`SetValue`. `offsetof` is locally redefined for GCC to avoid a warning, which is brittle. Degree validation uses shifts and has special cases for degree 64 and 128 to avoid undefined or meaningless checks. SSE4.2 selection is only correct for CRC32C and only after hardware availability is checked.

## Test signals
Build and run `examples/usage.cc`, which exercises both generic CRC32 and CRC32C paths, rolling CRC, zero CRC, start-value changes, concatenation, complementary CRC storage, CRC storage, and `CrcOfCrc`. Add tests for invalid `Create` arguments: degree 0, degree above 128, out-of-range polynomial bits, out-of-range rolling start bits, and SSE4.2 requested for non-CRC32C polynomials. On machines with and without SSE4.2, verify `IsSSE42Available` and output self-check values are stable for the same build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/examples/interface.cc -->
