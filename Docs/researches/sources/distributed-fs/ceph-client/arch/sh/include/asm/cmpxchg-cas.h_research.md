# sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg-cas.h



Source read size: 25 lines, 549 bytes.



Purpose: J2 CAS backend for cmpxchg/xchg.

Important APIs/types/functions: `__cmpxchg_u32`, `xchg_u32`, subword xchg include.

Control flow: uses `cas.l` loop for 32-bit exchange/compare-exchange.

State and persistence: caller memory only.

Dependencies and integration points: J2 SMP atomic primitives.

Risks and test signals: CAS inline asm constraints and alignment. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
