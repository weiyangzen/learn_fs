# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/futex.h

This header implements futex atomic operations in user memory for Alpha. The central `__futex_atomic_op` macro emits optional SMP `mb`, a 32-bit `ldl_l/stl_c` loop, operation-specific arithmetic/logic, retry on failed store-conditional, and exception-table fixups for user faults.

`arch_futex_atomic_op_inuser` validates `access_ok`, supports `FUTEX_OP_SET`, `ADD`, `OR`, `ANDN`, and `XOR`, writes the old value to `oval` on success, and returns `-ENOSYS` for unknown operations. `futex_atomic_cmpxchg_inatomic` performs an in-user compare-exchange with exception fixups and returns the observed value through `uval`.

State is user memory, output old-value storage, and exception fixup registers. Dependencies include futex constants, uaccess, Alpha errno, barriers, and `EXC` exception-table machinery. Risks include weak memory ordering, user fault recovery, access_ok coverage, signed/unsigned operation arguments, and live-lock under contention. Tests are futex selftests, robust mutexes, and fault-injection around invalid user addresses.
