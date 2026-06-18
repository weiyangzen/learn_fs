# sources/distributed-fs/ceph-client/arch/s390/include/asm/futex.h

Purpose: This header implements s390 user-memory atomic futex operations used by the generic futex subsystem.

Important APIs/types/functions: `FUTEX_OP_FUNC` generates `__futex_atomic_set/add/or/and/xor`; `arch_futex_atomic_op_inuser()` dispatches generic futex op codes; `futex_atomic_cmpxchg_inatomic()` performs user-space compare-and-swap. The assembly uses `sacf`, load, arithmetic/logical instructions, `cs`, and user-access exception-table fixups.

Control flow: A futex operation instruments the user read, enables SACF user access, loads the old value, computes the new value, loops on failed compare-and-swap, restores access mode, and reports either the old value or a user-access fault. The cmpxchg helper follows the same access-mode and exception-table pattern.

State and persistence: The only persistent state is the user futex word modified atomically; kernel local variables hold old/new values and fault status. Instrumentation hooks feed KMSAN/usercopy accounting but do not persist futex state.

Dependencies and integration points: It depends on Linux futex op codes, uaccess instrumentation, s390 SACF access helpers from `mmu_context.h`, errno values, and `EX_TABLE_UA_FAULT` exception fixups.

Risks and test signals: The access-mode restore path is critical on all fault exits, and the compare-and-swap loop must preserve user atomicity. Tests should cover each futex op, bad user addresses, concurrent waiter/waker stress, KMSAN builds, and 31/64-bit user access edge cases.
