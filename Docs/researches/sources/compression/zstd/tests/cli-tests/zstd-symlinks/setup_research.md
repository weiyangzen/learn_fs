# sources/compression/zstd/tests/cli-tests/zstd-symlinks/setup

## Purpose
Per-test setup for zstd symlink behavior tests. It prepares both raw and compressed fixtures.

## APIs, control flow, and integration
The script writes `hello` and `world` using `println`, then runs `zstd hello world`, which creates `hello.zst` and `world.zst`. It is run inside the per-test scratch directory by `run.py`.

## State, dependencies, risks, and test signals
State includes two raw files and two compressed outputs. Dependencies are the platform helper `println` and zstd default output naming. Downstream symlink tests rely on this setup to cover mixed compressed/raw operands.
