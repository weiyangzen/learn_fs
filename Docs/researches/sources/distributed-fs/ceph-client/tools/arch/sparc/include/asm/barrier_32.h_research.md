# sources/distributed-fs/ceph-client/tools/arch/sparc/include/asm/barrier_32.h

## Purpose
sparc32 tools barrier fallback.

## Important APIs, Types, and Functions
Includes `asm-generic/barrier.h` and defines only an include guard.

## Control Flow, State, and Persistence
No architecture-specific state or instructions are added.

## Dependencies and Integration Points
Used through `asm/barrier.h` for 32-bit SPARC tools builds.

## Risks and Test Signals
Risk is relying on generic compiler barriers where hardware ordering would be needed. Test signals are sparc32 tools builds and any lock-free primitive tests.
