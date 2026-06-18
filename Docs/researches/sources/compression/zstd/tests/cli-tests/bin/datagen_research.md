# sources/compression/zstd/tests/cli-tests/bin/datagen

## Purpose

This wrapper exposes the configured datagen binary to CLI shell tests.

## Important APIs, Types, and Functions

It executes `"$DATAGEN_BIN" $@`, forwarding all arguments.

## Control Flow, State, and Persistence

There is no state or cleanup. Exit status is the wrapped datagen exit status.

## Dependencies and Integration Points

It depends on `DATAGEN_BIN` being set by the CLI test harness.

## Risks and Test Signals

Unquoted `$@` can split arguments containing whitespace. Tests should verify harness setup exports a valid executable and that common datagen options work through the wrapper.
