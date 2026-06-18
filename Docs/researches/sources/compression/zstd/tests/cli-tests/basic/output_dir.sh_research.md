# sources/compression/zstd/tests/cli-tests/basic/output_dir.sh

## Purpose

This CLI test verifies that empty output directory arguments are rejected.

## Important APIs, Types, and Functions

It runs `zstd -r * --output-dir-mirror=""` and `zstd -r * --output-dir-flat=""`, failing with `die` if either succeeds.

## Control Flow, State, and Persistence

No files are intentionally created. The script exits 0 after both negative checks.

## Dependencies and Integration Points

It depends on recursive support and targets `--output-dir-flat` and `--output-dir-mirror` validation in `zstdcli.c`.

## Risks and Test Signals

Signals are nonzero status and diagnostics for empty strings. The glob `*` depends on the harness working directory containing at least one input-like path.
