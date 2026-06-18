# sources/compression/zstd/tests/cli-tests/basic/help.sh

## Purpose

This CLI test verifies short and advanced help commands.

## Important APIs, Types, and Functions

It runs `zstd -h`, `zstd -H`, and `zstd --help`, printing command labels with `println`.

## Control Flow, State, and Persistence

`set -e` makes any nonzero help command fail the test. No files are created.

## Dependencies and Integration Points

It depends on test wrappers `zstd` and `println`, and targets `usage()` plus `usageAdvanced()` in `zstdcli.c`.

## Risks and Test Signals

Signals are successful exit status and stable help text. Build-feature-dependent help content must be accounted for by the CLI test harness outputs.
