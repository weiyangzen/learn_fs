# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/plugins/__init__.py

## Purpose
Marks the `plugins` directory as a Python package for tc-testing plugin imports.

## Important APIs, Types, And Functions
The file is intentionally empty and exports no names.

## Control Flow
No runtime control flow beyond Python package initialization.

## State And Persistence
No state.

## Dependencies And Integration Points
Allows plugin modules under `plugins` to be imported by package path if present. The assigned plugin implementations live under `plugin-lib`, but the runner may also use this package directory.

## Risks
Because it is empty, all behavior depends on external plugin discovery logic. Removing it could break package-based imports on older Python tooling.

## Test Signals
Python can import the `plugins` package without error.
