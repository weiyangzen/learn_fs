# sources/distributed-fs/ceph-client/include/linux/atomic.h

## Purpose
Defines machine-independent atomic operation wrappers, conditional atomic reads, and generic acquire/release/full-fence construction around architecture relaxed atomics.

## Important APIs, Types, And Functions
Includes architecture `asm/atomic.h` and barrier definitions. `atomic_cond_read_acquire()`, `atomic_cond_read_relaxed()`, and 64-bit equivalents use conditional load primitives. Fence hook macros default to `smp_mb__after_atomic` or `smp_mb__before_atomic` unless the architecture overrides them. `__atomic_op_acquire()`, `__atomic_op_release()`, and `__atomic_op_fence()` wrap relaxed operations with acquire, release, or full ordering. It then includes generated/fallback, atomic-long, and instrumented atomic headers.

## Control Flow, State, And Persistence
The header layers memory-order semantics over architecture operations. Atomic state lives in `atomic_t`/`atomic64_t` objects supplied by callers. Acquire wrappers fence after relaxed load-modify operations; release wrappers fence before; full wrappers fence before and after.

## Dependencies And Integration Points
Depends on `linux/types.h`, architecture atomic/barrier headers, and Linux generated atomic fallback/instrumentation headers. Integrated everywhere kernel code uses atomics, refcounts, locks, wait loops, and memory-order-sensitive synchronization.

## Risks And Test Signals
Memory-ordering mistakes can be architecture-specific and intermittent. Tests should include LKMM litmus coverage, KCSAN/race detection, build coverage for architectures with and without overrides, atomic64 availability, instrumented atomic behavior, and users of conditional reads waiting for state transitions.
