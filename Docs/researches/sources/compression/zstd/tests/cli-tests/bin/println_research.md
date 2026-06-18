# sources/compression/zstd/tests/cli-tests/bin/println

## Purpose

This helper prints a newline-terminated message for CLI tests.

## Important APIs, Types, and Functions

It runs `printf '%b\n' "${*}"`, interpreting backslash escapes in the joined argument string.

## Control Flow, State, and Persistence

There is no state. Exit status is `printf`'s status.

## Dependencies and Integration Points

It depends on POSIX `sh` and `printf`. Many CLI tests use it for stable command labels and diagnostics.

## Risks and Test Signals

Because `%b` interprets escapes, test messages containing backslashes can be transformed. Tests rely on deterministic output from this helper.
