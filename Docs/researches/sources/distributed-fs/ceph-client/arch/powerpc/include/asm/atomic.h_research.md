# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/atomic.h

Purpose: implements PowerPC atomic integer operations using load-reserve/store-conditional loops and architecture-specific acquire/release barriers.

Important APIs/types/functions: provides `arch_atomic_read`, `arch_atomic_set`, generated add/sub/and/or/xor operations, relaxed return and fetch variants, `arch_atomic_fetch_add_unless`, `arch_atomic_dec_if_positive`, and 64-bit variants such as `arch_atomic64_read`, `arch_atomic64_set`, `arch_atomic64_inc_not_zero`, and `arch_atomic64_fetch_add_unless` under `__powerpc64__`.

Control flow: each modifying operation loops on `lwarx/stwcx.` or `ldarx/stdcx.` until the conditional store succeeds. Return/fetch variants preserve either new or old values. Specialized functions branch out when comparison predicates fail.

State and persistence: state is the caller-provided `atomic_t` or `atomic64_t` counter. The header itself stores nothing.

Dependencies and integration points: depends on `<asm/cmpxchg.h>`, barriers, asm constants, and asm compatibility macros. It is foundational for kernel refcounts, locks, scheduler state, memory management, and driver synchronization.

Risks: barrier placement is subtle and tied to `PPC_ATOMIC_ENTRY_BARRIER`, `PPC_ATOMIC_EXIT_BARRIER`, acquire, and release definitions. Prefixed instruction handling uses base-register fallbacks to avoid out-of-range generated offsets. Inline asm clobbers such as `xer` must stay correct for add/sub carry forms.

Test signals: build 32/64-bit configs, run LKDTM/refcount/atomic tests, lock and refcount stress workloads, KCSAN-oriented concurrency tests, and inspect generated code for prefixed-kernel configurations.
