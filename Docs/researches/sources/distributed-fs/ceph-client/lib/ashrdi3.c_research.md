<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ashrdi3.c -->
# sources/distributed-fs/ceph-client/lib/ashrdi3.c

## Purpose
Provides the generic libgcc-style 64-bit arithmetic right shift helper `__ashrdi3()` for targets that need a kernel-local implementation.

## APIs, Types, and Functions
Exports `long long notrace __ashrdi3(long long u, word_type b)`. It uses `DWunion` to manipulate signed high and unsigned low 32-bit halves.

## Control Flow, State, and Persistence
Shift by zero returns the input. For shifts of 32 or more, the high half is sign-filled from the old high sign bit and the low half receives the old high half shifted by `b - 32`. For smaller shifts, the high half is arithmetically shifted right and carries from high bits are ORed into the low half. There is no mutable state.

## Dependencies and Integration
Depends on `linux/libgcc.h` and export support. Built when `CONFIG_GENERIC_LIB_ASHRDI3` is selected, typically for 32-bit architectures without the helper supplied elsewhere.

## Risks and Test Signals
Risks include sign-extension mistakes, shift-count assumptions, and mismatch with compiler expectations for helper calling convention. Test signals include positive and negative 64-bit values shifted by 0, 1, 31, 32, 33, and 63, cross-compiler builds, and comparing results against native C arithmetic on test platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ashrdi3.c -->
