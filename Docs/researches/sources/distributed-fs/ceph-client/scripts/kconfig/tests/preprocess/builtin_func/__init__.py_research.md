# sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/builtin_func/__init__.py

## Purpose
This pytest module validates built-in preprocessor output.

## Important APIs, Types, and Functions
It runs `conf.oldaskconfig()`, checks stdout containment, and matches stderr with `expected_stderr`.

## Control Flow
The Kconfig parse completes successfully because the only `error-if` condition is false.

## State and Persistence
Only stdout/stderr are inspected.

## Dependencies and Integration Points
Depends on the built-in function fixture and expected output files.

## Risks and Edge Cases
Line-number expectations can change if the Kconfig fixture is edited.

## Test Signals
Pass means built-in function expansion and diagnostics remain stable.
