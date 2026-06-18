# sources/compression/zstd/lib/common/error_private.c

Purpose: embeds the canonical string mapping for zstd internal/public error enum values.

Important function: `ERR_getErrorString(ERR_enum code)`. It returns either a stripped generic message when `ZSTD_STRIP_ERROR_STRINGS` is defined or a switch-based message for each `PREFIX(...)` error code.

Control flow: a switch maps known error codes such as `no_error`, `prefix_unknown`, `corruption_detected`, `checksum_wrong`, parameter errors, allocation errors, dictionary errors, destination/source size errors, seekable errors, and sequence producer errors. Unknown or `maxCode` values return `"Unspecified error code"`.

State and persistence: stateless; returns pointers to string literals.

Dependencies/integration: includes `error_private.h`, which defines `ERR_enum`, `PREFIX`, and error code layout. Public wrappers such as zstd/FSE/HUF error-name APIs ultimately rely on this mapping.

Risks: adding a new error enum without updating this switch yields the generic fallback. Stripping error strings reduces binary detail and can affect diagnostics/tests expecting exact messages. Messages are user-visible enough that wording changes can break brittle tests.

Test signals: iterate every known `ERR_enum` value through `ERR_getErrorString`, verify stripped-string builds, confirm `ZSTD_getErrorName`/FSE/HUF wrappers surface expected text, and check unknown codes return fallback.
