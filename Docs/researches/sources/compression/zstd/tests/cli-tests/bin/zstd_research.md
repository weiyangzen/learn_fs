# sources/compression/zstd/tests/cli-tests/bin/zstd

## Purpose

This wrapper invokes the configured `zstd` binary or symlink for CLI tests, optionally through an execution prefix.

## Important APIs, Types, and Functions

It derives its basename and dispatches to `$ZSTD_SYMLINK_DIR/$zstdname`, with `$EXEC_PREFIX` prepended when set.

## Control Flow, State, and Persistence

The script is stateless and returns the underlying command status.

## Dependencies and Integration Points

It depends on `ZSTD_SYMLINK_DIR` and optional `EXEC_PREFIX`. It is the primary command used by CLI shell tests.

## Risks and Test Signals

Unquoted forwarding can mishandle arguments with whitespace. Test signals are that `zstd` options reach the intended binary and emulator-prefixed runs work.
