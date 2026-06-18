# sources/compression/zstd/tests/cli-tests/dictionaries/setup

## Purpose
Per-test setup for dictionary CLI tests. It copies suite-generated files and dictionaries into each test scratch directory.

## APIs, control flow, and integration
The script runs `cp -r ../files .` and `cp -r ../dicts .` under `set -e`. It is invoked by `run.py` before each test in the dictionaries suite.

## State, dependencies, risks, and test signals
The copied `files/` and `dicts/` directories isolate tests from one another. The script depends on `setup_once` having completed. Risks are hidden fixture coupling and stale generated dictionaries. Setup failure prevents the test body from running.
