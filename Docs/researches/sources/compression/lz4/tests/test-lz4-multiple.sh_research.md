# sources/compression/lz4/tests/test-lz4-multiple.sh

## Purpose
This shell test validates standard multi-file mode for compression, decompression, test mode, stdout concatenation, and missing-file failure behavior.

## Important Control Flow
It generates three inputs, compresses with `lz4 -f -m`, verifies per-file artifacts, deletes originals, decompresses back, and compares. It then verifies `-m ... -c` emits concatenated compressed output without creating artifacts, and `-d -m ... -c` emits concatenated plaintext. Test mode `lz4 -tm` is checked for one or multiple compressed files and must not create decompressed outputs. Missing input cases are expected to fail.

## State, Dependencies, and Integration
State is `tmp-tml*`. The test depends on `datagen`, `lz4`, `cmp`, `cat`, and glob expansion. It exercises command-line multi-file control flow rather than library APIs.

## Risks and Test Signals
It gives strong signals for artifact creation policy and test-mode non-mutating behavior. It assumes deterministic glob matches and does not inspect exit codes beyond shell `set -e` plus explicit `&& exit 1` failure expectations.
