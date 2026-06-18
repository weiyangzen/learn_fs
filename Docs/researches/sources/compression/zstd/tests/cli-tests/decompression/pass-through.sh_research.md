# sources/compression/zstd/tests/cli-tests/decompression/pass-through.sh

## Purpose
This test covers pass-through semantics for non-zstd data during decompression, including explicit `--pass-through`, cat-style symlinks, legacy `-fc` behavior, and `--no-pass-through` rejection.

## APIs, control flow, and integration
It sources platform helpers, creates short raw files and `file`, compresses `file`, then exercises `zstd -dc --pass-through`, `zstdcat`, symlinked `zcat`/`gzcat`, mixed compressed/uncompressed operands, output-to-file pass-through, and legacy forced stdout cases. It then verifies disabled pass-through paths fail for cat commands and regular `zstd -d`.

## State, dependencies, risks, and test signals
Scratch state includes raw files, `file.zst`, and pass-through output files. Dependencies include `ZSTD_SYMLINK_DIR`, `$DIFF`, and expected stderr behavior. Risks are policy changes around implicit pass-through and symlink mode detection. Pass signals include byte equality for file output and failure of raw input when pass-through is disabled.
