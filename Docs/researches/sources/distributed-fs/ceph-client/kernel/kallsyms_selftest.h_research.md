# sources/distributed-fs/ceph-client/kernel/kallsyms_selftest.h

## Purpose
Provides external declarations for kallsyms selftest symbols so generated kallsyms and test code can reference stable function/data names.

## Important APIs, Types, and Functions
Declares `kallsyms_test_var_bss`, `kallsyms_test_var_data`, `kallsyms_test_func`, and `kallsyms_test_func_weak`.

## Control Flow
No control flow; it is a declaration-only header.

## State and Persistence
The declared variables/functions are defined in `kallsyms_selftest.c` and linked into the kernel when the selftest is enabled.

## Dependencies and Integration Points
Includes `linux/types.h` and is consumed by `kallsyms_selftest.c`.

## Risks
If declarations diverge from definitions, selftest build or lookup validation breaks. Weak function semantics are part of the tested symbol set.

## Test Signals
Build success and selftest address comparisons validate this header.
