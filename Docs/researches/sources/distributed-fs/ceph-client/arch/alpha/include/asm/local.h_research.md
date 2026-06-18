# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/local.h

This header defines `local_t` counters backed by `atomic_long_t` and optimized local operations. Simple read/set/inc/dec/add/sub delegate to atomic_long operations; `local_add_return` and `local_sub_return` use `ldq_l/stq_c` loops without full SMP barriers; cmpxchg/xchg use local cmpxchg primitives.

Important APIs include `LOCAL_INIT`, `local_read`, `local_set`, arithmetic helpers, `local_cmpxchg`, `local_try_cmpxchg`, `local_xchg`, `local_add_unless`, `local_inc_not_zero`, and test/return variants. It also defines non-atomic `__local_*` helpers, though `__local_dec` appears to increment in this source, a notable risk signal if used.

State is the local counter. Integration is per-CPU counters and generic local API users. Risks include memory-order differences from full atomics, the suspicious `__local_dec` macro, and casting in `local_try_cmpxchg`. Tests are local_t API compile/runtime tests and any users of `__local_dec`.
