# sources/compression/zstd/tests/cli-tests/compression/basic.sh

## Purpose

This CLI test covers core compression flags and verifies resulting frames with `zstd -t`.

## Important APIs, Types, and Functions

It tests default compression, `-f`, `-z`, `-k`, `-C`, `--check`, `--no-check`, `--`, `-o`, compact `-fo`, stdout via `-c` and `--stdout`, stdin pipe compression, gzip stdout keep-source behavior when gzip alias exists, and `--rm` source removal.

## Control Flow, State, and Persistence

`set -e` stops on failures. The script creates or overwrites `file.zst`, `file-out.zst`, and `file-rm.zst`, and ensures `file-rm` is removed after `--rm`.

## Dependencies and Integration Points

It exercises `zstdcli.c` option parsing and `fileio` compress/test paths through the test wrappers, plus optional gzip alias behavior.

## Risks and Test Signals

Signals are valid compressed output, correct stdout behavior, kept source when stdout is used, and successful source deletion for file outputs. It assumes a baseline `file` fixture exists.
