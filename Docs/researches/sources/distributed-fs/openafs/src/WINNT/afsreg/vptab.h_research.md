# sources/distributed-fs/openafs/src/WINNT/afsreg/vptab.h

## Purpose
Declares the vice partition table data structures and registry-backed access functions.

## Important APIs, Types, And Functions
The header defines `VPTABSIZE_NAME` and `VPTABSIZE_DEV`, `struct vptab` with `vp_name` and `vp_dev`, `struct vpt_iter` with multistring iteration pointers, and prototypes for starting/advancing/finishing iteration, adding/removing entries, and validating partition/device names.

## Control Flow
Callers iterate with `vpt_Start`, repeated `vpt_NextEntry`, then `vpt_Finish`; mutations use `vpt_AddEntry` and `vpt_RemoveEntry` after validation.

## State And Persistence
The structures represent registry-backed persistent partition entries, while `vpt_iter` owns transient enumeration memory allocated by the implementation.

## Dependencies And Integration Points
It uses C linkage for C++ callers and pairs with `vptab.c`. It is consumed by server setup/diagnostic utilities such as `regman.c`.

## Risks And Test Signals
The fixed field sizes and validation contract are the main compatibility boundaries. Compile coverage and add/list/remove tests are the expected signals.
