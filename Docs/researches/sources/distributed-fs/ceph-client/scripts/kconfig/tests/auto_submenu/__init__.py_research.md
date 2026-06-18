# sources/distributed-fs/ceph-client/scripts/kconfig/tests/auto_submenu/__init__.py

## Purpose
This pytest module validates the auto-submenu fixture.

## Important APIs, Types, and Functions
The only test function calls `conf.oldaskconfig()` and `conf.stdout_contains('expected_stdout')`.

## Control Flow
Pytest injects the `conf` fixture from `conftest.py`; the test runs the interactive frontend with automatic enter input and compares stdout against the expected output file.

## State and Persistence
Temporary output is managed by the `Conf` helper. No module-level mutable state is used.

## Dependencies and Integration Points
Depends on `scripts/kconfig/conf`, the local `Kconfig`, and expected-output files in the same test directory.

## Risks and Edge Cases
The test is output-format sensitive, so harmless UI text changes can require expected fixture updates.

## Test Signals
Pass means automatic submenu rendering still matches expectations.
