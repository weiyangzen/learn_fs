# File Research: sources/cow-pools/bcachefs-tools/fs/errcode.c

## Purpose

Implements bcachefs custom error-code naming, hierarchy matching, class reduction, and conversions from block and zstd errors.

## Main Interfaces

- `const char *bch2_err_str(int err)`.
- `bool __bch2_err_matches(int err, int class)`.
- `int __bch2_err_class(int bch_err)`.
- `const char *bch2_blk_status_to_str(blk_status_t status)`.
- `enum bch_errcode blk_status_to_bch_err(blk_status_t err)`.
- `enum bch_errcode zstd_err_to_bch_err(ZSTD_ErrorCode err)`.
- `int __bch2_err_throw(struct bch_fs *c, int err)`.

## Behavior

`BCH_ERRCODES()` generates string and parent-class tables. `bch2_err_str()` returns custom names for bcachefs errors, Linux `errname()` for standard errno values, and explicit invalid/no-error strings. Matching walks parent classes until the requested class or a root is found. Class reduction maps a custom error back to its top-level standard errno-like class.

Block status and zstd errors are converted through generated switch statements. `__bch2_err_throw()` increments the persistent `error_throw` counter and emits `trace_error_throw()` before returning the negative error.

## Dependencies

Depends on `errcode.h`, Linux `errname`, block status strings, zstd error enums, persistent counters, and tracepoints.

## Notes

The hierarchy lets code test broad classes like `ENOENT` or bcachefs-specific classes while preserving detailed leaf errors for diagnostics.
