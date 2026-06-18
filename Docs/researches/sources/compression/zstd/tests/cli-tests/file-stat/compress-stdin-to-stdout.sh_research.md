# sources/compression/zstd/tests/cli-tests/file-stat/compress-stdin-to-stdout.sh

## Purpose
This test covers the fully streamed compression path with `--trace-file-stat`.

## APIs, control flow, and integration
It generates `file`, runs `zstd < file -cq --trace-file-stat > file.zst`, and tests the output. Both input and output are shell streams from zstd's perspective.

## State, dependencies, risks, and test signals
State is limited to the source fixture and redirected compressed output. The important signal is that trace diagnostics do not contaminate stdout and stream-only stat handling does not fail.
