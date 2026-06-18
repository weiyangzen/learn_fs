# sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/variable/Kconfig

## Purpose
This fixture tests Kconfig variable flavor semantics and user-defined functions.

## Important APIs, Types, and Functions
It exercises simple `:=`, recursive `=`, append `+=` for defined and undefined variables, variable references on the left-hand side, and user-defined function arguments through `greeting = $(1), my name is $(2).`.

## Control Flow
Warnings emit each expansion result after changing underlying variables, demonstrating when values are captured and when they are deferred.

## State and Persistence
Variable state exists only during parsing and is deleted by `variable_all_del()`.

## Dependencies and Integration Points
Targets parser assignment rules and `preprocess.c` variable expansion.

## Risks and Edge Cases
Undefined `+=` must become recursive, and missing function parameters must expand to empty strings without arity errors.

## Test Signals
The paired test matches stderr warnings to expected output.
