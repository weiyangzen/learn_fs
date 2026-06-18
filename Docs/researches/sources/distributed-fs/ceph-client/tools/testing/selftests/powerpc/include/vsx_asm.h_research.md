# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/vsx_asm.h

## Purpose
Assembly macros/helpers for loading and storing nonvolatile VSX registers.

## Important APIs, Types, and Functions
Defines `load_vsx` and `store_vsx` style helper sequences for vs20-vs31.

## Control Flow
Generated assembly copies VSX register contents to/from caller-provided buffers.

## State and Persistence
State is VSX register file and memory buffers supplied by callers.

## Dependencies and Integration Points
Depends on `basic_asm.h`; used by VSX-specific math tests.

## Risks and Test Signals
Risk is VSX availability and ABI register mapping. VSX preempt/signal tests provide coverage.
