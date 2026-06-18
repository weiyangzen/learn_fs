# sources/compression/zstd/tests/cli-tests/cltools/zstdgrep.sh

## Purpose

This CLI test checks basic `zstdgrep` behavior on good and bad paths.

## Important APIs, Types, and Functions

It runs `zstdgrep "1234" file file.zst` and then `zstdgrep "1234" bad.zst`, with labels emitted by `println`.

## Control Flow, State, and Persistence

`set -e` means the second command is expected by the harness exact-output/status model; if it returns nonzero directly under `set -e`, the script exits there. It does not create files itself and depends on setup.

## Dependencies and Integration Points

It depends on `cltools/setup`, `zstdgrep`, and `println`.

## Risks and Test Signals

Signals are successful matching across plain/compressed inputs and appropriate failure/diagnostics for missing compressed input.
