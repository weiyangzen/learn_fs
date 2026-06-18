# sources/distributed-fs/ceph-client/tools/arch/arm/include/uapi/asm/mman.h

## Purpose
Provides ARM tools mman compatibility by including generic mman constants and defining missing `MAP_32BIT`.

## Important APIs, Types, And Functions
- Includes `<uapi/asm-generic/mman.h>`.
- Defines `MAP_32BIT` as `0` for ARM.

## Control Flow
No runtime flow.

## State And Persistence
No state; compile-time constants only.

## Dependencies And Integration Points
Used by tool code that references `MAP_32BIT` across architectures.

## Risks
`MAP_32BIT` is a no-op/unsupported marker on ARM, so callers must not expect x86 behavior.

## Test Signals
Cross-compile tools for ARM and verify mman users build.
