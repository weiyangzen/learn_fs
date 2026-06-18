# sources/distributed-fs/ceph-client/arch/sh/include/asm/atomic.h



Source read size: 35 lines, 693 bytes.



Purpose: top-level SH atomic operation selector.

Important APIs/types/functions: `arch_atomic_read/set` plus GRB, SH4A LL/SC, IRQ, or generic J2 implementation.

Control flow: preprocessor selects the atomic backend for the CPU/config.

State and persistence: atomic variables are caller-owned.

Dependencies and integration points: refcounting, locks, bitops/cmpxchg.

Risks and test signals: wrong backend breaks SMP atomicity. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
