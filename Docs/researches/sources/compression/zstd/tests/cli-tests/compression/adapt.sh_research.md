# sources/compression/zstd/tests/cli-tests/compression/adapt.sh

## Purpose

This CLI test verifies adaptive compression mode and that adaptation still occurs when progress output is disabled.

## Important APIs, Types, and Functions

It pipes `zstd -f file --adapt -c` to `zstd -t`, generates a 100 MB file with `datagen`, then runs high-verbosity adaptive compression at level 19 with `--zstd=wlog=10` and greps for the "faster speed , lighter compression" adaptation message, both with and without `--no-progress`.

## Control Flow, State, and Persistence

`set -e` aborts on any failed command or missing grep match. It creates `file100M` in the test directory.

## Dependencies and Integration Points

It targets adaptive settings in `zstdcli.c` and downstream file I/O/compression adaptation logic. It depends on `datagen`, `zstd`, and `grep`.

## Risks and Test Signals

The test is large and message-string sensitive. Slow or resource-limited systems may make it expensive. Signals are valid compressed output and explicit adaptation diagnostics.
