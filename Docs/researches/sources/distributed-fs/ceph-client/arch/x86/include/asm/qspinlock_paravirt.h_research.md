<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/qspinlock_paravirt.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/qspinlock_paravirt.h

Purpose: defines optimized paravirtual queued spinlock unlock glue for x86. Important APIs are `__pv_queued_spin_unlock_slowpath()`, callee-save thunks, `__pv_queued_spin_unlock`, and the 64-bit `PV_UNLOCK_ASM` implementation.

Control flow: the fast path attempts a locked byte `cmpxchg` from locked to zero; if it fails, it preserves required registers and calls the slowpath with the observed lock byte. On 32-bit, the implementation is an external callee-save function instead of inline hand-coded assembly.

State and persistence: operates only on `struct qspinlock` lock bytes. Dependencies include IBT/ENDBR-compatible thunk machinery, qspinlock constants, and paravirt slowpath code. Risks include calling convention drift, register save/restore errors, section placement, and IBT annotation issues. Test signals include paravirt guest locktorture, unlock fast/slow path tracing, objtool validation, and 32/64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/qspinlock_paravirt.h -->
