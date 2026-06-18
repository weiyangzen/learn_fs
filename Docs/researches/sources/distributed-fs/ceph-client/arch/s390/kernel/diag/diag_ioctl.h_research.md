# sources/distributed-fs/ceph-client/arch/s390/kernel/diag/diag_ioctl.h

## Purpose
Declares internal ioctl handler prototypes shared by the s390 `/dev/diag` dispatcher and its DIAG 310/324 implementation files.

## Important APIs, Types, And Functions
The header declares `diag324_pibbuf()`, `diag324_piblen()`, `diag310_memtop_stride()`, `diag310_memtop_len()`, and `diag310_memtop_buf()`.

## Control Flow
No control flow exists. `diag_misc.c` includes this header and calls the declared functions from its ioctl switch.

## State And Persistence
No state is defined. Runtime state is owned by `diag310.c` and `diag324.c`.

## Dependencies And Integration Points
Depends only on Linux integer types. It integrates the private diag subdirectory modules without exposing these functions as public UAPI.

## Risks And Edge Cases
Prototype drift between dispatcher and implementation would cause build failures or, if types changed incorrectly, ioctl argument handling bugs. The use of `unsigned long arg` matches ioctl dispatch conventions.

## Test Signals
Signals are compile/link success and `/dev/diag` ioctl dispatch tests covering every declared handler.
