# sources/distributed-fs/ceph-client/scripts/kconfig/tests/pytest.ini

## Purpose
`pytest.ini` configures pytest discovery for Kconfig unit tests.

## Important APIs, Types, and Functions
It sets `addopts = --verbose` and `python_files = __init__.py`.

## Control Flow
Pytest imports each test package's `__init__.py` as the test module, avoiding duplicate test module basenames across directories.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Applies to the entire `scripts/kconfig/tests` pytest suite.

## Risks and Edge Cases
Because every test file is named `__init__.py`, changing this setting would make pytest miss the suite or collide imports.

## Test Signals
Running pytest from this directory should discover all package-level test modules.
