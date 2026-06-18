# sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_recursive_dep/__init__.py

## Purpose
This pytest module asserts recursive dependency errors are fatal.

## Important APIs, Types, and Functions
The test calls `conf.oldaskconfig()` and checks for return code 1 plus expected stderr.

## Control Flow
The run should fail during parse/finalization before normal configuration output.

## State and Persistence
Only captured stderr/return code are used.

## Dependencies and Integration Points
Depends on recursive dependency diagnostics from `symbol.c`.

## Risks and Edge Cases
Error text is precise, so formatting changes require fixture updates.

## Test Signals
Pass indicates recursive dependencies remain hard errors.
