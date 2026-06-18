<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/barrier.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/barrier.h

**Purpose:** Defines MIPS memory, IO, SMP, LL/SC, and global-invalidate barriers.

**Important APIs/types/functions:** `__sync`, `rmb`, `wmb`, `fast_mb`, `fast_iob`, `mb`, `iob`, `__smp_mb/rmb/wmb`, `smp_llsc_mb`, `smp_mb__before_llsc`, `nudge_writes`, `__smp_mb__before/after_atomic`, and `sync_ginv`.

**Control flow:** Compile-time configuration selects write-buffer flush versus sync, Octeon and SGI IP28 special paths, weak-ordering SMP barriers, and LL/SC compiler clobber behavior.

**State, dependencies, integration:** Used by atomics, bitops, IO access, locking, and cache code. Depends on `addrspace.h` and `sync.h`.

**Risks and test signals:** Incorrect barriers produce SMP-only data races or IO ordering failures. Test memory-model litmus tests, device IO on weakly ordered CPUs, Octeon/IP28 special cases, and LL/SC ordering configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/barrier.h -->
