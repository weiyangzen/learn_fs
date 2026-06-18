# sources/compression/zstd/tests/cli-tests/cltools/setup

## Purpose

This setup script prepares shared files for command-line tool tests such as `zstdgrep` and `zstdless`.

## Important APIs, Types, and Functions

It writes `1234` to `file` and compresses it with `zstd file`.

## Control Flow, State, and Persistence

`set -e` aborts on setup failure. It persists `file` and `file.zst` in the test working directory for subsequent test scripts.

## Dependencies and Integration Points

It depends on the CLI test `zstd` wrapper and is associated with `tests/cli-tests/cltools`.

## Risks and Test Signals

The setup assumes default compression keeps the source file. Signals are existence and validity of both plain and compressed files for later tests.
