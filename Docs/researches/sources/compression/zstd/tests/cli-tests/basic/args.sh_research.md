# sources/compression/zstd/tests/cli-tests/basic/args.sh

## Purpose

This CLI test exercises invalid zstd arguments and expects the harness to capture failures/output for exact-output comparison.

## Important APIs, Types, and Functions

It invokes `zstd --blah`, `zstd -xz`, malformed `--adapt=min=1,maxx=2 file.txt`, and malformed `--train-cover=k=48,d=8,steps32 file.txt`, printing each command first with `println`.

## Control Flow, State, and Persistence

There is no setup or cleanup. Each command is run sequentially without `set -e`, so failures do not stop the script.

## Dependencies and Integration Points

It depends on CLI test wrappers `zstd` and `println`. It targets parser branches in `zstdcli.c`.

## Risks and Test Signals

The useful signal is stable rejection of unknown short/long options and malformed parameter lists. If a command unexpectedly succeeds or changes diagnostics, the CLI exact-output tests should fail.
