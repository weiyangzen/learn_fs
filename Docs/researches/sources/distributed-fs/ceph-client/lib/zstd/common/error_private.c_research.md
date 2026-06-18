# sources/distributed-fs/ceph-client/lib/zstd/common/error_private.c

Purpose: Provides the central mapping from zstd internal error enum values to human-readable strings.

Important APIs/functions:
- `ERR_getErrorString(ERR_enum code)`.

Control flow:
- If `ZSTD_STRIP_ERROR_STRINGS` is defined, all codes return a stripped-message placeholder.
- Otherwise a switch maps stable and selected unstable `ZSTD_error_*` codes to string literals, with a default unspecified-code string.

State and persistence:
- No mutable state. Uses static const string pointer for the default not-error case.

Dependencies and integration:
- Includes `error_private.h`.
- Public wrappers in zstd/FSE/HUF use this through `ERR_getErrorName()` or `ZSTD_getErrorString()`.

Risks:
- Error enum changes in `<linux/zstd_errors.h>` must be reflected here, or callers get generic names.
- String stripping changes diagnostics but not error codes; tests should not require exact messages when stripped.

Test signals:
- Iterate all known error enum values and verify non-NULL strings.
- Build with and without `ZSTD_STRIP_ERROR_STRINGS`.
