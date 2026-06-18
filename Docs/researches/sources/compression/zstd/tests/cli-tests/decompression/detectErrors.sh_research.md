# sources/compression/zstd/tests/cli-tests/decompression/detectErrors.sh

## Purpose
This decompression test verifies that known malformed golden samples are rejected.

## APIs, control flow, and integration
It sets `GOLDEN_DIR` to `$ZSTD_REPO_DIR/tests/golden-decompression-errors/`, iterates every file, and runs `zstd -t`. If any invalid sample tests successfully, it calls `die`. The runner supplies `ZSTD_REPO_DIR` and the shell helper `die`.

## State, dependencies, risks, and test signals
No files are modified. The test depends on the repository golden corpus existing and containing only invalid samples. Risks are shell glob behavior if the directory is missing and changes to error tolerance. Pass means every corpus member produced a decompression error.
