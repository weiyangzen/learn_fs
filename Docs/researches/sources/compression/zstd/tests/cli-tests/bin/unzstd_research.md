# sources/compression/zstd/tests/cli-tests/bin/unzstd

## Purpose

This wrapper invokes the configured `unzstd` symlink/binary under the optional execution prefix used by CLI tests.

## Important APIs, Types, and Functions

It derives `zstdname=$(basename $0)`, then runs either `"$ZSTD_SYMLINK_DIR/$zstdname" $@` or `$EXEC_PREFIX "$ZSTD_SYMLINK_DIR/$zstdname" $@`.

## Control Flow, State, and Persistence

There is no state. Exit status is the wrapped executable status.

## Dependencies and Integration Points

It depends on `ZSTD_SYMLINK_DIR` and optional `EXEC_PREFIX`, supporting QEMU or other emulator prefixes in `tests/Makefile`.

## Risks and Test Signals

Unquoted `$@` and `$EXEC_PREFIX` can split arguments. Tests should verify alias behavior is preserved because zstd mode is selected from executable basename.
