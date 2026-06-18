# sources/compression/zstd/tests/cli-tests/progress/no-progress.sh

## Purpose
This test validates cases where progress information must not be printed, even when stderr is faked as a console or verbosity/progress flags interact.

## APIs, control flow, and integration
It sources platform helpers, creates `hello` and `world`, precompresses them, and loops over argument sets including empty, quiet, explicit no-progress, and verbose no-progress combinations. For each set it exercises compression and decompression across file-to-file, pipe-to-pipe, pipe-to-file, file-to-pipe, and multi-file cases. Output descriptions are printed to stderr for exact/glob matching by the harness.

## State, dependencies, risks, and test signals
State includes raw and compressed `hello`/`world` files. Dependencies are `$INTOVOID`, helper `println`, and expected stderr output files. Risks are progress-rendering policy changes and terminal simulation differences. Pass means no progress lines appear in the negative matrix while operations still succeed.
