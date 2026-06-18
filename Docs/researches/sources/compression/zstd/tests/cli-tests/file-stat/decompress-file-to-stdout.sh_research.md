# sources/compression/zstd/tests/cli-tests/file-stat/decompress-file-to-stdout.sh

## Purpose
This test covers traced decompression from a named file to stdout.

## APIs, control flow, and integration
It creates `file.zst`, runs `zstd -dcq --trace-file-stat file.zst > file`, and relies on shell redirection for the decompressed output.

## State, dependencies, risks, and test signals
State is `file.zst` and redirected `file`. The key risk is diagnostics leaking to stdout. Pass confirms the binary stdout stream remains clean and decompression succeeds with trace enabled.
