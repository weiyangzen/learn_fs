# File Research: sources/block-storage/kvdo/vdo/permassert.h

## Purpose
Defines UDS assertion macros and compile-time assertion helpers.

## Key Macros
- `ASSERT_WITH_ERROR_CODE`: checked assertion returning caller-specified error.
- `ASSERT`: checked assertion returning `UDS_ASSERTION_FAILED`.
- `ASSERT_LOG_ONLY`: logs failure without requiring caller to use an error code.
- `ASSERT_FALSE`: convenience wrapper for impossible paths.
- `STATIC_ASSERT`, `STATIC_ASSERT_SIZEOF`: compile-time checks.
- `uds_must_use`: wraps integral expressions with `__must_check`.

## API
- `set_exit_on_assertion_failure`
- `uds_assertion_failed`

## Integration Notes
All assertion macros route through `__UDS_ASSERT`, which includes module name, file, line, and formatted message. The macro design enforces checked handling for assertion-return values where used.
