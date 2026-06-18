# sources/compression/zstd/tests/check_size.py

## Purpose

This Python helper checks that a file exists and does not exceed a byte-size limit.

## Important APIs, Types, and Functions

It reads exactly two arguments, `FILE` and `SIZE_LIMIT`, converts the limit with `int()`, checks `os.path.exists`, computes `os.path.getsize`, and exits 1 with a diagnostic if the file is missing or too large.

## Control Flow, State, and Persistence

The script has no persistent state and performs a single validation per invocation.

## Dependencies and Integration Points

It depends on Python 3 and the stdlib. It is suitable for Makefile or CI size gates.

## Risks and Test Signals

It accepts directories as existing paths, for which `getsize` reports directory metadata size on some platforms. It imports `subprocess` unused. Tests should cover usage errors, non-integer limits, missing files, exact limit equality, over-limit files, and platform behavior for directories if used in CI.
