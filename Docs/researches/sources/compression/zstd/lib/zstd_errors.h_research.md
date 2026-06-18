# sources/compression/zstd/lib/zstd_errors.h

## Purpose
`zstd_errors.h` is the public error-code declaration header shared by `zstd.h` and applications that need to inspect typed zstd failures. It defines the `ZSTD_ErrorCode` enum and a string conversion API, while leaving normal error detection to `ZSTD_isError()` from the main API.

## Important APIs, types, and constants
- Visibility macros `ZSTDERRORLIB_VISIBLE`, `ZSTDERRORLIB_HIDDEN`, and `ZSTDERRORLIB_API` mirror the main library's export/import controls, including backward compatibility for `ZSTDERRORLIB_VISIBILITY` and DLL import/export handling.
- `ZSTD_ErrorCode` enumerates stable errors below `100`, including generic failure, unknown prefix, unsupported version/frame parameters, window too large, corruption/checksum/literals header problems, dictionary errors, unsupported/out-of-bound parameters, table and symbol limits, wrong stage/init/memory/workspace/destination/source-buffer errors, and no-forward-progress cases.
- Values at and above `100` are explicitly marked unstable: frame index, seekable I/O, wrong source/destination buffers, sequence producer failure, invalid external sequences, and `ZSTD_error_maxCode`.
- `ZSTD_getErrorString(ZSTD_ErrorCode code)` maps a typed enum value to a readable string and is documented as equivalent in meaning to `ZSTD_getErrorName()` but taking an enum rather than an encoded function result.

## Control flow and state behavior
This header has no runtime state or control flow beyond declaration-time C/C++ linkage and visibility selection. Its design enforces an error-handling flow in users of libzstd: functions generally return a `size_t` value, callers first detect failure with `ZSTD_isError()`, then may convert to `ZSTD_ErrorCode` using `ZSTD_getErrorCode()` or render the enum with `ZSTD_getErrorString()`.

The comments specify version stability rules. Numeric enum values are pinned down only since v1.3.1, and only values below `100` should be treated as stable. Older or dynamically linked scenarios should prefer enum names and `ZSTD_isError()` rather than numeric constants.

## Dependencies and integration points
The file is self-contained and uses only language linkage/visibility macros. It is included by `zstd.h` and is also useful to embedders that want the enum declarations without relying on internal headers. It integrates with the implementation that encodes errors into `size_t` results and with public conversion helpers declared in `zstd.h`.

## Risks and edge cases
- Code must not persist or compare unstable values at or above `100` as a compatibility promise.
- `ZSTD_error_maxCode` is a sentinel and explicitly should not be used directly.
- `ZSTD_getErrorString()` accepts an enum code; callers with raw function results should first convert through `ZSTD_getErrorCode()` instead of casting arbitrary `size_t` values.
- Dynamic-linking support for the error-list API is called out as not officially supported in the comments, so binary compatibility assumptions should stay conservative.

## Test signals
Test coverage should include mapping representative stable errors to non-null strings, verifying successful operations report `ZSTD_error_no_error` through the normal conversion path, confirming `ZSTD_isError()` remains the primary detector for encoded results, and compiling C++ consumers to validate the `extern "C"` boundary. Compatibility tests should avoid depending on unstable enum values.
