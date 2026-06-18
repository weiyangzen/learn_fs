# sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg.h



Source read size: 86 lines, 2142 bytes.



Purpose: top-level SH xchg/cmpxchg selector and typed wrappers.

Important APIs/types/functions: `arch_xchg`, `arch_cmpxchg`, `__cmpxchg`, backend includes, generic local cmpxchg.

Control flow: selects GRB, LL/SC, CAS, or IRQ backend; dispatches xchg by operand size and cmpxchg for 1/4 bytes.

State and persistence: mutates caller memory atomically.

Dependencies and integration points: atomics, locks, barriers, bitops.

Risks and test signals: unsupported sizes link to bad-pointer sentinels. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
