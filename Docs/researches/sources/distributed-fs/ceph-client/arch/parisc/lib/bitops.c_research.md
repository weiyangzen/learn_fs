<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/bitops.c -->
## sources/distributed-fs/ceph-client/arch/parisc/lib/bitops.c

### Purpose
`bitops.c` implements out-of-line atomic exchange and compare-exchange helpers for PA-RISC.

### Important APIs, Types, And Functions
On SMP it defines aligned `__atomic_hash`. It implements `__xchg64()` on 64-bit builds, `__xchg32()`, `__xchg8()`, and macro-generated `__cmpxchg_u64/u32/u16/u8()`.

### Control Flow
Each helper hashes/locks through `_atomic_spin_lock_irqsave(ptr, flags)`, reads the previous value, optionally writes the new value, unlocks with IRQ restore, and returns the previous value.

### State, Persistence, And Dependencies
The SMP hash lock table persists globally. Dependencies include PA-RISC atomic spinlock helpers, IRQ flag save/restore, and architecture inline atomic APIs that call these out-of-line functions.

### Integration Points
Used by generic atomics and synchronization primitives when operations are too large to inline or require hashed locking.

### Risks
`__xchg32()` and `__xchg8()` sign-extend through `long temp`, noted in comments. Hash-lock granularity can serialize unrelated addresses. Correct 16-byte lock alignment is required by PA-RISC locking instructions.

### Test Signals
Atomic exchange/cmpxchg tests for all widths, SMP contention, IRQ-disabled callers, and sign/zero extension expectations should be run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/bitops.c -->
