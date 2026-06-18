# sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/circular_expansion/Kconfig

## Purpose
This fixture verifies recursive variable expansion is detected and rejected.

## Important APIs, Types, and Functions
It defines `X = $(Y)`, `Y = $(X)`, then expands `$(X)` through `$(info $(X))`.

## Control Flow
Because both variables are recursive, expansion enters a cycle and `variable_expand()` should raise a fatal preprocessor error.

## State and Persistence
No config state; failure is observable via stderr and exit status.

## Dependencies and Integration Points
Targets `preprocess.c` recursion tracking.

## Risks and Edge Cases
If recursion detection only catches direct self-reference, this indirect cycle would hang or hit depth limits.

## Test Signals
The paired test expects nonzero exit and matching stderr.
