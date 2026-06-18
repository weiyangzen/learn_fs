# sources/compression/zstd/tests/cli-tests/compression/format.sh

## Purpose

This CLI test verifies compression and test-mode behavior for zstd and optional alternate formats.

## Important APIs, Types, and Functions

It sources `common/format.sh`, compresses `file` with `--format=zstd`, tests `file.zst`, then loops through `gzip`, `lz4`, `xz`, and `lzma` when advertised by help output. For each supported format it writes a file with the expected extension, tests it, and tests stdout compression using `zstd -t --format=<format>`.

## Control Flow, State, and Persistence

`set -e` stops on errors. It creates format-specific compressed files in the working directory.

## Dependencies and Integration Points

It targets format selection in `zstdcli.c`, extension mapping in `fileio`, and optional compression backend support.

## Risks and Test Signals

Feature detection depends on help text. Signals are successful encode/decode/test for every compiled-in format and correct file extensions.
