# sources/distributed-fs/ceph-client/include/linux/zstd_errors.h

## Purpose
Defines the exported Zstandard error-code enum and symbol-visibility macros used by the kernel zstd wrapper. It is the stable error taxonomy consumed by `zstd_is_error()`, `zstd_get_error_code()`, and error-name helpers.

## Important APIs, Types, and Functions
Visibility macros are `ZSTDERRORLIB_VISIBLE`, `ZSTDERRORLIB_HIDDEN`, and `ZSTDERRORLIB_API`. `typedef enum ZSTD_ErrorCode` lists stable and unstable zstd errors, including no error, generic failure, unknown prefix, unsupported version/frame parameters, window too large, corruption, checksum failure, literal and dictionary errors, unsupported or out-of-bound parameters, table/symbol limits, wrong stage or missing init, allocation/workspace failures, destination/source size issues, null destination, and no-forward-progress conditions. `ZSTD_getErrorString()` maps an enum code to a string.

## Control Flow
No runtime control flow is implemented in the header. Callers receive size-like return values from zstd APIs, test them with the wrapper error predicate, translate to `ZSTD_ErrorCode`, and optionally format the code through `ZSTD_getErrorString()` or higher-level name helpers.

## State and Persistence
No state is owned. The enum values are part of the static API contract. Values below 100 are documented as stable; later values are explicitly not stable and may change.

## Dependencies and Integration Points
Used by `linux/zstd.h` and upstream-derived zstd library internals. Integrates with kernel error reporting, compression/decompression callers, and any tests comparing zstd error categories.

## Risks
Code must prefer enum names and `ZSTD_isError()`-style predicates over hard-coded numeric values, especially for library versions before stable value pinning or for codes at 100 and above. The header notes static-linking assumptions and no official dynamic-linking support, so it should not be treated as a cross-library ABI independent of the bundled zstd version.

## Test Signals
Signals include error-code mapping tests, corrupt frame and bad-parameter tests that produce expected enum names, build coverage for visibility macros, and checks that callers do not persist unstable numeric error values.
