# sources/compression/zstd/tests/cli-tests/basic/version.sh

## Purpose

This CLI test verifies version-reporting commands.

## Important APIs, Types, and Functions

It runs `zstd -V` and `zstd --version`.

## Control Flow, State, and Persistence

`set -e` fails the script on either nonzero status. No files are created.

## Dependencies and Integration Points

It targets `printVersion()` in `zstdcli.c` through the test wrapper `zstd`.

## Risks and Test Signals

Signals include successful exit status and stable version text, including verbosity-dependent or feature-dependent details controlled by the harness.
