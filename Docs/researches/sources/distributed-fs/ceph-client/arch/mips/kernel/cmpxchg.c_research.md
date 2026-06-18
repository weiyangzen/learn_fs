<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cmpxchg.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cmpxchg.c

### Purpose
`cmpxchg.c` implements sub-word exchange and compare-exchange helpers for MIPS by operating on the containing aligned 32-bit word.

### Important APIs, Types, And Functions
It provides `__xchg_small()` and exported `__cmpxchg_small()`, both using `arch_cmpxchg()` on aligned `u32` storage with masks and shifts.

### Control Flow
Each helper verifies natural alignment with `WARN_ON`, masks inputs to the requested byte/halfword size, computes endian-aware bit position within the containing word, loads the word, then loops with `arch_cmpxchg()` until the exchange succeeds or the compare value does not match.

### State, Persistence, And Dependencies
State is the target memory word. The helpers depend on atomic LL/SC or equivalent `arch_cmpxchg`, Linux bitops, and compile-time endianness.

### Integration Points
Generic atomic/xchg APIs call these when exchanging 1- or 2-byte values on architectures whose native atomics are word-sized.

### Risks
Concurrent updates to different bytes in the same word serialize through full-word compare-exchange and can still cause contention. Misaligned callers get only a warning, so correctness depends on API discipline.

### Test Signals
Atomic tests should cover byte and halfword exchange/cmpxchg, big- and little-endian positions, failure return values, concurrent updates to adjacent bytes, and misalignment warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cmpxchg.c -->
