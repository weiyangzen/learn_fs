# sources/distributed-fs/ceph-client/tools/arch/arc/include/uapi/asm/mman.h

## Purpose
Provides ARC tools mman compatibility by including generic mman constants and defining missing `MAP_32BIT`.

## Important APIs, Types, And Functions
- Includes `<uapi/asm-generic/mman.h>`.
- Defines `MAP_32BIT` as `0` for ARC.

## Control Flow
No runtime flow.

## State And Persistence
No state. Compile-time constants only.

## Dependencies And Integration Points
Used by tools builds that expect `MAP_32BIT` to exist across architectures.

## Risks
Code that tests `MAP_32BIT` must tolerate zero meaning unsupported/no-op on ARC.

## Test Signals
Cross-compile tools for ARC and ensure mman users build without architecture-specific ifdefs.
