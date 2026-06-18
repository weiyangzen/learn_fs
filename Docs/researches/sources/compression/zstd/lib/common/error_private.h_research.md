# sources/compression/zstd/lib/common/error_private.h

## Purpose
`error_private.h` is zstd's private error-code adapter. It maps public `ZSTD_ErrorCode` values into the internal convention where functions returning `size_t` encode errors as negative enum values cast to `size_t`, and it supplies the return/forward macros used throughout the common, compression, and decompression code.

## Important APIs, Types, and Functions
The header aliases `ERR_enum` to `ZSTD_ErrorCode`, defines `ERROR(name)` and `ZSTD_ERROR(name)`, and provides inline helpers `ERR_isError()`, `ERR_getErrorCode()`, and `ERR_getErrorName()`. `CHECK_V_F()` and `CHECK_F()` evaluate a call, return early on error, and preserve the original `size_t` error. `RETURN_ERROR_IF()`, `RETURN_ERROR()`, and `FORWARD_IF_ERROR()` add debug logging via `RAWLOG()` and enforce a non-empty format string through `_FORCE_HAS_FORMAT_STRING()`.

## Control Flow, State, and Persistence
The header has no persistent state. Its control flow is macro-driven: callees return normal sizes below or equal to `ERROR(maxCode)`, while failures are returned immediately. In debug builds the macros log file, line, failed condition or expression, symbolic error, and optional formatted details before returning.

## Dependencies and Integration Points
It depends on `../zstd_errors.h` for the enum namespace, `compiler.h` for inline attributes, `debug.h` for logging, and `zstd_deps.h` for `size_t`. It is included by low-level modules such as FSE, Huffman, bitstream, and zstd frame/block code so they can expose public-compatible error names without exposing this private header as API.

## Risks and Test Signals
The main risk is misuse of the `size_t` error convention: arithmetic on returned sizes before `ERR_isError()` checks can turn failures into bogus capacities or offsets. The variadic logging macros also require call sites to pass a format string that is syntactically valid even when debug logging is disabled. Useful test signals include expected propagation through `CHECK_F()`/`FORWARD_IF_ERROR()`, correct `ZSTD_getErrorName()` strings for failures, and clean strict-C99 builds that reject empty variadic macro payloads.
