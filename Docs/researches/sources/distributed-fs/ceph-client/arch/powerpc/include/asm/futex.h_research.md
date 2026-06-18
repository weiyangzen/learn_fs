# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/futex.h

Purpose: Implements PowerPC futex atomic operations and compare-exchange in user memory using load-reserve/store-conditional sequences with exception-table recovery.

Important APIs, types, and functions: `__futex_atomic_op()` emits the atomic inline assembly for set/add/or/andn/xor operations. `arch_futex_atomic_op_inuser()` dispatches `FUTEX_OP_*` operations and returns the old value. `futex_atomic_cmpxchg_inatomic()` performs atomic compare-exchange on a user pointer.

Control flow: Callers enter with pagefaults disabled by the futex core. The assembly attempts user access, performs the atomic update with `lwarx/stwcx.`, retries on reservation failure, and uses exception fixups to return `-EFAULT`. Successful operations report the old user value.

State and persistence: The only state changed is the user futex word. No kernel state is persisted by the header.

Dependencies and integration points: Depends on Linux futex core, `uaccess`, PowerPC synchronization primitives, errno, and exception tables. It is part of the arch futex contract used by locking primitives in userspace.

Risks: Memory ordering and exception fixups are correctness-critical. Operation decoding must match generic futex op encodings. Misaligned or unmapped user addresses must fail without corrupting state. Reservation loops can spin under contention.

Test signals: Futex atomic op tests for all supported ops, compare-exchange success/failure, invalid user pointers, high contention, 32-bit and 64-bit builds, and memory-ordering litmus tests around wake/wait paths.
