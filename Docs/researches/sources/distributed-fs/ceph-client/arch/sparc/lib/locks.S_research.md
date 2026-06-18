# sources/distributed-fs/ceph-client/arch/sparc/lib/locks.S

Purpose: SPARC32 low-level read/write lock primitives.

Important APIs/functions: Exports `___rw_read_enter`, `___rw_read_exit`, `___rw_read_try`, and `___rw_write_enter`.

Control flow: Implements spinning paths for entering/exiting read locks and acquiring write locks. It checks lock word state, spins when writer bits are set, updates counters atomically with architecture primitives, and returns success/failure for try-lock.

State and persistence: Mutates lock words supplied by callers.

Dependencies/integration: Includes `asm/ptrace.h`, `asm/psr.h`, `asm/smp.h`, and `asm/spinlock.h`; used by SPARC32 locking code.

Risks/test signals: Reader count, writer bit, and SMP interrupt interactions are critical. Test lock torture, try-lock semantics, and contention on SMP SPARC32.
