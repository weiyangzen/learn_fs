## sources/distributed-fs/ceph-client/arch/arm64/include/asm/futex.h

Purpose: implements arm64 atomic futex operations on user memory.

Important APIs/types/functions: defines `FUTEX_MAX_LOOPS`, LL/SC futex atomic op generators, optional LSUI operation generators, `__llsc_futex_cmpxchg`, `__lsui_cmpxchg32/64`, `arch_futex_atomic_op_inuser`, and `futex_atomic_cmpxchg_inatomic`.

Control flow: validates user access, masks user pointers, enables privileged user access or TTBR0 access, performs atomic LL/SC or LSUI operations with exception-table recovery, applies memory barriers, and returns old values or errors.

State and persistence: mutates a user futex word atomically; no kernel-persistent state.

Dependencies and integration: depends on uaccess, exception tables, LSUI/LLSC dispatch, futex core, and memory ordering.

Risks: user-access windows, retry limits, and barriers are security and correctness critical. Test signals are futex selftests, robust futex tests, fault-injection on user addresses, stress-ng futex workloads, LSUI hardware coverage, and memory-order litmus tests.
