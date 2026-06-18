# sources/compression/zstd/tests/cli-tests/zstd-symlinks/zstdcat.sh

## Purpose
This test verifies zstdcat behavior through both installed harness symlinks and a local symlink to the zstd binary.

## APIs, control flow, and integration
Using setup fixtures, it runs `zstdcat` over compressed-only and mixed compressed/raw operands, then creates `./zstdcat` as a symlink to `$(which zstd)` and runs it on `hello.zst`. The behavior relies on program-name dispatch in the zstd CLI.

## State, dependencies, risks, and test signals
State adds a local `zstdcat` symlink. Dependencies are `which`, symlink support, `PATH`, and zstdcat pass-through policy. Risks are platforms without symlinks and changes to argv[0]-based mode selection. Pass confirms symlink invocation decompresses/prints as expected.
