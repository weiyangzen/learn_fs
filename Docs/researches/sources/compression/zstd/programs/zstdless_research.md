# sources/compression/zstd/programs/zstdless

## Purpose

This shell script implements `zstdless` by configuring `less` to transparently decompress zstd files through `zstd -cdfq`.

## Important APIs, Types, and Functions

Environment variable `ZSTD` overrides the zstd executable. The script exports `LESSOPEN="|-${zstd} -cdfq %s"` and then `exec`s `less "$@"`.

## Control Flow, State, and Persistence

It has no persistent state beyond the exported `LESSOPEN` environment for the `less` process. All user arguments are passed directly to `less`, not zstd.

## Dependencies and Integration Points

It depends on POSIX `sh`, `less`, and zstd. CLI tests wrap it through `tests/cli-tests/bin/zstdless`.

## Risks and Test Signals

Behavior depends on `less` supporting `LESSOPEN` and on shell/environment quoting. Tests should cover valid compressed input, pass-through of less flags, missing files, and custom `ZSTD` paths.
