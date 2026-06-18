# sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_transitional/__init__.py

## Purpose
This pytest module asserts invalid transitional symbol properties are rejected.

## Important APIs, Types, and Functions
The test calls `conf.olddefconfig()` and `conf.stderr_contains('expected_stderr')`.

## Control Flow
The noninteractive config run should terminate with code 1 during parser sanity checks.

## State and Persistence
Only stderr and return code are examined.

## Dependencies and Integration Points
Depends on transitional checks in `parser.y`.

## Risks and Edge Cases
The assertion uses containment, giving some tolerance for additional diagnostics.

## Test Signals
Pass confirms transitional help-only rules are enforced.
