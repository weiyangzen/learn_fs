# sources/compression/zstd/tests/cli-tests/compression/gzip-compat.sh

## Purpose

This CLI test verifies gzip-compatible alias behavior when a gzip symlink is available.

## Important APIs, Types, and Functions

Inside a command-existence guard, it tests `gzip --fast`, `gzip --best`, `gzip -n`, `gzip --no-name`, and stdout `gzip -c --no-name`. It decompresses generated `file.gz` with the gzip alias and uses `grep -qv file` to assert `-n`/`--no-name` do not embed the original filename.

## Control Flow, State, and Persistence

`set -e` fails on unexpected command errors. It creates and removes `file.gz` through compression/decompression cycles.

## Dependencies and Integration Points

It depends on `$ZSTD_SYMLINK_DIR/gzip` and targets executable-name routing plus gzip-specific option handling in `zstdcli.c`.

## Risks and Test Signals

The guard uses `command -v` through command substitution in an `if`, which depends on shell behavior but is typical in this harness. Signals are gzip alias level mapping, decompression compatibility, source restoration, and filename suppression.
