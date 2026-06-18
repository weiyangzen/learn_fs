# sources/compression/zstd/tests/cli-tests/compression/long-distance-matcher.sh

## Purpose
This short CLI test exercises long-distance matching options in the compressor.

## APIs, control flow, and integration
It assumes `compression/setup` has created `file`. The script runs `zstd -f file --long` and `zstd -f file --long=20`, then validates the produced `file.zst` with `zstd -t` after each command. It uses only CLI entry points and the shell harness `set -e` failure model.

## State, dependencies, risks, and test signals
The only persistent scratch artifact is overwritten `file.zst`. The test depends on the built zstd supporting long-distance mode and on default memory limits being sufficient for `--long=20`. A pass confirms the option parser accepts both forms and the resulting frames decompress successfully.
