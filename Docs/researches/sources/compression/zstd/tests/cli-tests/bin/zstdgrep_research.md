# sources/compression/zstd/tests/cli-tests/bin/zstdgrep

## Purpose

This wrapper exposes the configured `zstdgrep` script to CLI tests.

## Important APIs, Types, and Functions

It executes `"$ZSTDGREP_BIN" $@`.

## Control Flow, State, and Persistence

The wrapper is stateless and returns `zstdgrep`'s status.

## Dependencies and Integration Points

It depends on `ZSTDGREP_BIN` being set by the CLI test harness and delegates to `programs/zstdgrep`.

## Risks and Test Signals

Unquoted `$@` can mishandle whitespace arguments. Tests should cover good and bad compressed paths through the wrapper.
