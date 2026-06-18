# sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/errno.h

## Purpose
PowerPC errno compatibility wrapper.

## Important APIs, Types, and Functions
Includes generic errno definitions and aliases `EDEADLOCK` to `EDEADLK`.

## Control Flow, State, and Persistence
No state or flow.

## Dependencies and Integration Points
Used by PowerPC tools that expect the architecture's UAPI errno alias.

## Risks and Test Signals
Risk is minimal; test signals are errno preprocessing and source compatibility checks.
