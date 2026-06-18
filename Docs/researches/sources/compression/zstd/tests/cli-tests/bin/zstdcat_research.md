# sources/compression/zstd/tests/cli-tests/bin/zstdcat

## Purpose

This wrapper invokes the configured `zstdcat` alias for CLI tests.

## Important APIs, Types, and Functions

It uses its basename to choose `$ZSTD_SYMLINK_DIR/zstdcat`, optionally prefixed by `$EXEC_PREFIX`, forwarding all arguments.

## Control Flow, State, and Persistence

It is stateless and returns the wrapped command status.

## Dependencies and Integration Points

It depends on alias symlink setup and is used where decompression-to-stdout behavior must be tested.

## Risks and Test Signals

The same unquoted argument-forwarding risk applies. Tests should verify alias-selected pass-through/stdout defaults and emulator execution.
