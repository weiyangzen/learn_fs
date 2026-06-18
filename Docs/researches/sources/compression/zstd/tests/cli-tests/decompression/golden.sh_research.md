# sources/compression/zstd/tests/cli-tests/decompression/golden.sh

## Purpose
This test validates that all known-good golden decompression samples are accepted by the CLI.

## APIs, control flow, and integration
It sets `GOLDEN_DIR` to `$ZSTD_REPO_DIR/tests/golden-decompression/` and invokes `zstd -r -t "$GOLDEN_DIR"` to recursively test every compressed sample. `set -e` turns any failed test into a script failure.

## State, dependencies, risks, and test signals
The test is read-only. It depends on golden assets and recursive CLI traversal. Risks are missing corpus files or support changes for old/edge frames. Pass confirms compatibility with the golden decompression suite.
