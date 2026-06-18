# sources/distributed-fs/ceph-client/lib/cmpdi2.c

## Purpose

`sources/distributed-fs/ceph-client/lib/cmpdi2.c` implements the libgcc `__cmpdi2` helper for signed 64-bit comparisons on architectures that need compiler runtime support.

## Important APIs, Types, and Functions

The exported symbol is `word_type notrace __cmpdi2(long long a, long long b)`. It uses `DWunion` from `<linux/libgcc.h>` to access high and low words.

## Control Flow

The function compares signed high words first, returning 0 when `a < b` and 2 when `a > b`. If high words are equal, it compares low words as unsigned and returns the same ordering codes or 1 for equality.

## State and Persistence Behavior

There is no state. It is a pure comparison helper.

## Dependencies and Integration Points

It integrates with compiler-generated calls for 64-bit comparison on targets lacking native support and exports the symbol for kernel linkage.

## Risks and Edge Cases

Return values follow libgcc convention rather than normal `strcmp` convention. Correct signedness split is critical: high word signed, low word unsigned. `notrace` prevents instrumentation recursion in low-level runtime paths.

## Test Signals

Tests should compare equal, less, greater, negative vs positive, high-word differences, low-word-only differences, and compiler-emitted helper linkage on 32-bit builds.

## Read Coverage

Source read size: 30 lines, 501 bytes.
