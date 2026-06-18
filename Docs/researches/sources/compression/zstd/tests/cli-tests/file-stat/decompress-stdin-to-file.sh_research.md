# sources/compression/zstd/tests/cli-tests/file-stat/decompress-stdin-to-file.sh

## Purpose
This test covers traced decompression from stdin to a named output file.

## APIs, control flow, and integration
It creates `file.zst`, runs `zstd -dcq --trace-file-stat < file.zst -o file`, and expects a valid decompressed `file`. This combines stdin source handling with explicit output path handling.

## State, dependencies, risks, and test signals
State is `file.zst` and `file`. Risks are stat code assuming file input and stdout/file option interaction. Pass confirms stream input plus named output works under trace instrumentation.
