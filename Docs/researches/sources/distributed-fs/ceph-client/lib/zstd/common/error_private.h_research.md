# sources/distributed-fs/ceph-client/lib/zstd/common/error_private.h

Purpose: Defines internal zstd/FSE/HUF error-code encoding, propagation macros, and debug-aware return helpers.

Important APIs/macros:
- `ERR_enum` aliases `ZSTD_ErrorCode`; `PREFIX(name)` maps names to `ZSTD_error_*`.
- `ERROR(name)` and `ZSTD_ERROR(name)` encode errors as negative `size_t` values.
- `ERR_isError()`, `ERR_getErrorCode()`, and `ERR_getErrorName()` inspect encoded returns.
- `CHECK_V_F()` and `CHECK_F()` forward errors from called functions.
- `RETURN_ERROR_IF()`, `RETURN_ERROR()`, and `FORWARD_IF_ERROR()` return encoded errors and optionally log debug context.
- `_force_has_format_string()` and `_FORCE_HAS_FORMAT_STRING()` enforce valid variadic macro usage.
- Declares `ERR_getErrorString()`.

Control flow:
- Error-return macros check conditions or encoded return values and immediately return `size_t` error codes.
- Debug logging paths use `RAWLOG` with file/line and formatted context when enabled.

State and persistence:
- Stateless. Encoded error values are returned in `size_t`, a common zstd convention.

Dependencies and integration:
- Includes `<linux/zstd_errors.h>`, `compiler.h`, `debug.h`, and `zstd_deps.h`.
- Used throughout zstd common/compress/decompress code.

Risks:
- Error encoding assumes valid non-error sizes are never greater than `ERROR(maxCode)`. This convention must be preserved.
- Macros return from the current function, so they are appropriate only in functions returning `size_t` or compatible encoded errors.
- Debug formatting helpers must avoid evaluating arguments at runtime in disabled paths.

Test signals:
- Unit tests for `ERR_isError`, `ERR_getErrorCode`, and macro forwarding.
- Compile paths using empty and non-empty variadic macro arguments under strict C modes.
