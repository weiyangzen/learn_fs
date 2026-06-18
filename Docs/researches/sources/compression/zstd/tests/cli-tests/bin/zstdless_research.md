# sources/compression/zstd/tests/cli-tests/bin/zstdless

## Purpose

This wrapper exposes the configured `zstdless` script to CLI tests.

## Important APIs, Types, and Functions

It executes `"$ZSTDLESS_BIN" $@`.

## Control Flow, State, and Persistence

The wrapper is stateless and returns the wrapped command status.

## Dependencies and Integration Points

It depends on `ZSTDLESS_BIN` and delegates to `programs/zstdless`.

## Risks and Test Signals

Unquoted `$@` can mishandle whitespace arguments. Tests should confirm less options and file arguments pass through as intended.
