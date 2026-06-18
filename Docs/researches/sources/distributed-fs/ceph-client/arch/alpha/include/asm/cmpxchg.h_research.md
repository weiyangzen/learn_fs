# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/cmpxchg.h

This header implements Alpha exchange and compare-exchange primitives. It supports 1, 2, 4, and 8 byte objects using LL/SC loops; byte and halfword operations operate inside an aligned quadword with insert/mask/extract instructions.

Important helpers are `____xchg_u8/u16/u32/u64`, `____cmpxchg_u8/u16/u32/u64`, dispatcher functions `____xchg` and `____cmpxchg`, local macros `xchg_local`, `arch_cmpxchg_local`, `arch_cmpxchg64_local`, and fully ordered `arch_xchg`, `arch_cmpxchg`, and `arch_cmpxchg64`. Invalid sizes deliberately reference undefined bad-pointer functions to cause link errors.

State is the target memory word. Full arch operations wrap local LL/SC with `smp_mb()` before and after, because they may implement critical sections. Risks are memory ordering, unaligned or unexpected object sizes, inline assembly constraints, and 8/16-bit updates contending on the same aligned quadword. Tests should cover cmpxchg loops, try-cmpxchg users, byte/word atomicity, and lock/refcount code.
