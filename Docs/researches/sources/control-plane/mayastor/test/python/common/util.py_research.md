# sources/control-plane/mayastor/test/python/common/util.py

## Purpose
Small utility for resolving the Mayastor build output directory used by CLI/protobuf tests.

## Important APIs, Types, And Functions
Exports `mayastor_target_dir()`, which requires `SRCDIR` and returns `${SRCDIR}/${IO_ENGINE_DIR}`.

## Control Flow
The function checks the environment and raises an exception if `SRCDIR` is missing.

## State And Persistence
No persistent state.

## Dependencies And Integration Points
Used by `msclient.py` to locate `io-engine-client` and indirectly by CLI tests. Depends on `SRCDIR` and `IO_ENGINE_DIR` environment conventions.

## Risks
The docstring has a typo, and the function assumes the target directory naming scheme without validating `IO_ENGINE_DIR`.

## Test Signals
Correct path resolution allows setup and CLI tests to find generated binaries.
