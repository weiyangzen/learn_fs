# sources/compression/zstd/tests/cli-tests/file-stat/decompress-stdin-to-stdout.sh

## Purpose
This test covers the fully streamed decompression path with file-stat tracing.

## APIs, control flow, and integration
It creates `file.zst`, runs `zstd -dcq --trace-file-stat < file.zst > file`, and writes decompressed bytes through stdout redirection.

## State, dependencies, risks, and test signals
State is `file.zst` and `file`. Pass confirms trace diagnostics do not corrupt stdout and decompression handles non-file input/output descriptors.
