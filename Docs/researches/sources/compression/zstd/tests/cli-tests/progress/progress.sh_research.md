# sources/compression/zstd/tests/cli-tests/progress/progress.sh

## Purpose
This test validates cases where progress information should be printed.

## APIs, control flow, and integration
It sources platform helpers, creates `hello`/`world`, precompresses them, and loops over `--progress`, `--fake-stderr-is-console`, and `--progress --fake-stderr-is-console -q`. For each argument set it runs the same compression/decompression matrix as `no-progress.sh`: file/file, pipe/pipe, pipe/file, file/pipe, and multi-file in both directions.

## State, dependencies, risks, and test signals
State is local raw/compressed fixtures. Dependencies are terminal/progress simulation flags and harness expectation files. Risks are progress output formatting changes. Pass confirms expected progress diagnostics appear without breaking data paths.
