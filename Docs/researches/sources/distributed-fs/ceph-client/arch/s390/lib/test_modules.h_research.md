# sources/distributed-fs/ceph-client/arch/s390/lib/test_modules.h

## Purpose
Macro generator and declarations for the s390 module relocation KUnit test.

## Important APIs, Types, And Functions
Defines nested repetition macros `__REPEAT_10000_1/2/3` and `REPEAT_10000(f)` to expand a macro over numeric suffixes `0000` through `9999`. `DECLARE_RETURN(i)` declares `int test_modules_return_i(void)`, and `REPEAT_10000(DECLARE_RETURN)` emits 10,000 declarations.

## Control Flow And State
No runtime control flow. It creates compile-time repetition to generate a large symbol surface for relocation stress.

## Dependencies And Integration
Used by both `test_modules.c` and `test_modules_helpers.c`. The macro shape must match helper definitions and expected summation in the C test.

## Risks And Test Signals
Risks include accidental numeric token changes, excessive compiler memory/time, or declaration/definition mismatch. Signals are successful compilation/linkage and the KUnit relocation test sum.
