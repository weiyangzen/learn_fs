# sources/compression/zstd/tests/checkTag.c

## Purpose

This small C tool validates that a release tag is compatible with the compiled `ZSTD_VERSION_STRING`.

## Important APIs, Types, and Functions

`validate(tag)` requires a tag beginning with `v`, longer than the version string plus prefix, and whose characters after `v` start with `ZSTD_VERSION_STRING`. `main()` expects exactly one tag argument, prints version and tag, then returns 0 for compatible, 1 for mismatch, or 2 for incorrect usage.

## Control Flow, State, and Persistence

There is no persistent state. Runtime flow is argument validation, diagnostic printing, version prefix comparison, and exit code selection.

## Dependencies and Integration Points

It includes `zstd.h` and is built by the tests Makefile. It is intended for automated release/tag checks.

## Risks and Test Signals

The compatibility rule allows arbitrary suffixes after the exact version prefix. Tests should cover missing args, no `v` prefix, too-short tags, exact version with no suffix, compatible suffixes, and mismatched major/minor/patch values.
