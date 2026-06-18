# sources/distributed-fs/ceph-client/tools/include/nolibc/stdbool.h

## Purpose
Provides C boolean compatibility macros for nolibc.

## APIs, Types, and Functions
Defines `bool` as `_Bool`, `true` as `1`, `false` as `0`, and `__bool_true_false_are_defined`.

## Control Flow, State, and Persistence
There is no control flow or state. It is a compile-time compatibility layer.

## Dependencies and Integration
Depends on C99 `_Bool` support. It integrates with code expecting `<stdbool.h>` in a nolibc include path.

## Risks and Test Signals
Risks are compiling in non-C99 modes or clashing with C++ bool semantics if used incorrectly. Test signals are simple C and C++ preprocessing/compile smoke tests where applicable.
