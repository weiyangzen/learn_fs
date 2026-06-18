# sources/compression/zstd/tests/cli-tests/compression/setup

## Purpose
Per-test setup for the compression CLI suite. It creates reusable scratch input files for compression tests.

## APIs, control flow, and integration
Under `run.py`, this script runs before each test case in the `compression` suite. It uses `datagen` three times to create `file`, `file0`, and `file1` in the per-test scratch directory. `set -e` makes data generation failures abort setup before the test body starts.

## State, dependencies, risks, and test signals
The persistent state is exactly the generated input files. Tests in this folder assume these names exist. Risks are hidden coupling: changes in generated file size or compressibility can affect size-order tests and long-window tests. A setup failure is surfaced by the harness as a suite setup exception.
