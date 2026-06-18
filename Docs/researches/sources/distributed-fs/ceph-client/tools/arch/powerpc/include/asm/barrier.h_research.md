# sources/distributed-fs/ceph-client/tools/arch/powerpc/include/asm/barrier.h

## Purpose
PowerPC tools memory-barrier header.

## Important APIs, Types, and Functions
Defines `mb()`, `rmb()`, `wmb()` using `sync`, `smp_lwsync()` using `lwsync`, plus release/acquire helpers implemented with compiler barriers and `WRITE_ONCE`/`READ_ONCE`.

## Control Flow, State, and Persistence
No persistent state. Expanded macros emit ordering instructions or compiler barriers at call sites.

## Dependencies and Integration Points
Used by perf/tools code that needs Linux-style barriers on PowerPC.

## Risks and Test Signals
Risks include using light-weight barriers where full ordering is required and divergence from kernel Kconfig-specific barrier behavior. Test signals are PowerPC tools builds and lock-free primitive tests.
