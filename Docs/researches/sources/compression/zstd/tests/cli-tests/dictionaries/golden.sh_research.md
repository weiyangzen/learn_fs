# sources/compression/zstd/tests/cli-tests/dictionaries/golden.sh

## Purpose
This test validates dictionary compression/decompression behavior with golden dictionary assets, specifically a dictionary missing symbols.

## APIs, control flow, and integration
It locates `$ZSTD_REPO_DIR/tests/golden-compression/` and `$ZSTD_REPO_DIR/tests/golden-dictionaries/`, compresses the golden `http` input with `http-dict-missing-symbols`, writes `http.zst`, and tests the frame using the same dictionary.

## State, dependencies, risks, and test signals
Scratch state is `http.zst`. Dependencies are golden input/dictionary assets and stable dictionary handling in the CLI. The test is narrow but targets an edge case in dictionary entropy tables. Pass means the compressor can emit and the decompressor can read a frame for that golden dictionary case.
