# sources/compression/zstd/tests/cli-tests/common/format.sh

## Purpose

This shared shell helper provides format-detection utilities for CLI compression-format tests.

## Important APIs, Types, and Functions

It sources `common/platform.sh`, defines `zstd_supports_format()` by grepping `zstd -h` for `--format=<name>`, and defines `format_extension()` mapping `zstd` to `zst`, `gzip` to `gz`, and all other names to themselves.

## Control Flow, State, and Persistence

The file defines functions only and has no persistent state beyond variables imported from `platform.sh`.

## Dependencies and Integration Points

It is used by `compression/format.sh` and depends on the test `zstd` wrapper plus `$INTOVOID`.

## Risks and Test Signals

Feature detection depends on help text remaining stable. Tests should cover each optional format build and correct extension mapping.
