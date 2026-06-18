# sources/distributed-fs/ceph-client/tools/unittests/run.py

## Purpose

`run.py` is the top-level unittest discovery runner for tests under `tools/unittests`.

## Important APIs, Types, and Functions

It computes `TOOLS_DIR`, prepends it to `sys.path`, imports `TestUnits` from `lib.python.unittest_helper`, discovers `test*.py` modules under `tools/unittests`, and runs the resulting suite.

## Control Flow and Data Flow

When executed as `__main__`, it creates a `unittest.TestLoader`, discovers tests, and delegates execution/output formatting to `TestUnits().run("", suite=suite)`.

## State and Persistence Behavior

It mutates only Python import path for the process. It writes no persistent state.

## Dependencies and Integration Points

It depends on the repository's Python helper library and Python unittest discovery. It is the convenient entry point for kernel-doc and tokenizer unit tests.

## Risks and Edge Cases

Discovery depends on file names matching `test*.py`. Import path insertion assumes the script remains one level below `tools`. Missing optional dependencies are handled by individual tests rather than this runner.

## Test Signals

A successful run reports all discovered unit tests passing. Useful smoke tests invoke this file from different working directories to confirm `TOOLS_DIR` resolution.
