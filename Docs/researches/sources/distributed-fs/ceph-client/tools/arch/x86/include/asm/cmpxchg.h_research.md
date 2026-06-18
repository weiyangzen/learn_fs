# sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/cmpxchg.h

## Purpose
x86 tools compare-and-exchange helper.

## Important APIs, Types, and Functions
Defines size constants, an error symbol `__cmpxchg_wrong_size()`, `__raw_cmpxchg()` for 1/2/4/8-byte operands using locked `cmpxchg`, `__cmpxchg()`, and public `cmpxchg()`.

## Control Flow, State, and Persistence
The macro evaluates typed old/new values, switches on operand size, emits the correct instruction, and returns the previous memory value. On 32-bit builds the 8-byte case is made impossible with a `-1` size constant.

## Dependencies and Integration Points
Depends on `linux/compiler.h` and `LOCK_PREFIX` supplied by including code. Integrated by x86 tools atomics and lock-free helpers.

## Risks and Test Signals
Risks include unsupported operand sizes surfacing as link/compile errors, 64-bit use on 32-bit builds, and inline asm constraints. Test signals are compile tests for byte/word/long/quad cmpxchg and wrong-size negative tests.
