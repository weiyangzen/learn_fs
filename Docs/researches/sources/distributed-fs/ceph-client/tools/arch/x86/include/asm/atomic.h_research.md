# sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/atomic.h

## Purpose
x86 tools atomic primitive header.

## Important APIs, Types, and Functions
Defines `LOCK_PREFIX`, `ATOMIC_INIT`, `atomic_read()`, `atomic_set()`, `atomic_inc()`, `atomic_dec_and_test()`, `atomic_cmpxchg()`, `test_and_set_bit()`, and `test_and_clear_bit()` using x86 locked instructions and rmwcc helpers.

## Control Flow, State, and Persistence
Atomic operations act on caller-owned `atomic_t` or bit memory. `atomic_read()`/`atomic_set()` use READ/WRITE semantics, increments and bit ops emit locked instructions, and cmpxchg delegates to `cmpxchg.h`.

## Dependencies and Integration Points
Depends on `linux/compiler.h`, `linux/types.h`, `rmwcc.h`, `asm/asm.h`, and `asm/cmpxchg.h`. Integrated with tools libraries needing kernel-style atomic operations on x86.

## Risks and Test Signals
Risks include only implementing the subset used by tools, inline asm constraint mistakes, and architecture-size interactions for bit operations. Test signals are x86 tools builds and atomic/bit operation unit tests.
