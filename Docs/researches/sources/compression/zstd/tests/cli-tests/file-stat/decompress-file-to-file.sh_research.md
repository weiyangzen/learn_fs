# sources/compression/zstd/tests/cli-tests/file-stat/decompress-file-to-file.sh

## Purpose
This test covers traced decompression from a named compressed file to the default output file.

## APIs, control flow, and integration
It creates `file.zst` from `datagen | zstd -q`, sets mode `642`, then runs `zstd -dq --trace-file-stat file.zst`. The default output path is derived by stripping `.zst`.

## State, dependencies, risks, and test signals
State includes `file.zst` and decompressed `file`. The test depends on permission/stat handling for compressed inputs. Pass confirms traced file-to-file decompression succeeds and output naming remains intact.
