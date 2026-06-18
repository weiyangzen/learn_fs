# sources/compression/zstd/lib/common/zstd_common.c

## Purpose
`zstd_common.c` provides the small public/common ABI surface that must exist even when most zstd logic is compiled into other translation units. It exports version metadata, error-result classification, error-name conversion, enum-to-string conversion, and a deterministic-build probe. The file is intentionally narrow: it bridges public `zstd.h` users to internal `error_private.h` helpers without exposing private macros as the only callable interface.

## Important APIs, Types, and Functions
The exported functions are `ZSTD_versionNumber()`, `ZSTD_versionString()`, `ZSTD_isError()`, `ZSTD_getErrorName()`, `ZSTD_getErrorCode()`, `ZSTD_getErrorString()`, and `ZSTD_isDeterministicBuild()`. `ZSTD_ErrorCode` comes from the public zstd API, while the actual error mechanics come from `ERR_isError()`, `ERR_getErrorName()`, `ERR_getErrorCode()`, and `ERR_getErrorString()`. The file undefines the inline/macro `ZSTD_isError` from `zstd_internal.h` so a real external symbol is emitted.

## Control Flow, State, and Persistence
There is no mutable state, allocation, or persistence. Each function is a direct constant return or one-hop wrapper. `ZSTD_isDeterministicBuild()` is compile-time controlled by `ZSTD_IS_DETERMINISTIC_BUILD`, returning `1` or `0` based on preprocessor configuration.

## Dependencies and Integration Points
The file defines `ZSTD_DEPS_NEED_MALLOC` before including `zstd_internal.h`, so the dependency shim exposes malloc/free/calloc macros for downstream common internals. It integrates with public callers that need stable symbols for version and error handling, and with test/packaging code that needs to verify deterministic build settings.

## Risks and Test Signals
Risk is mainly ABI and macro drift: removing the `#undef ZSTD_isError` would leave external callers without the intended function symbol. Error-code wrappers must stay consistent with `error_private.h`. Test signals include checking version string/number against public macros, verifying `ZSTD_isError()` recognizes all `ERROR(...)` results, and building with deterministic mode both enabled and disabled.
