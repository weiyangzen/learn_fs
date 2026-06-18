# sources/compression/zstd/tests/cli-tests/determinism/setup

## Purpose
Per-test setup for determinism cases. It provides each test with a local copy of the shared deterministic fixture corpus.

## APIs, control flow, and integration
Under `run.py`, this script runs before each determinism test and executes `cp -r ../files .`. The source `../files` directory is produced by `setup_once` in the suite scratch root.

## State, dependencies, risks, and test signals
The state is a copied `files` directory inside each test scratch directory. The dependency on `setup_once` is strong; if the fixture corpus is missing, every determinism test fails before its body. Copying rather than sharing isolates tests from each other's `.zst` side effects.
