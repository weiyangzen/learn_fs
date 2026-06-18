# sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg-irq.h



Source read size: 54 lines, 1065 bytes.



Purpose: IRQ-masked xchg/cmpxchg backend.

Important APIs/types/functions: `xchg_u32/u16/u8`, `__cmpxchg_u32`.

Control flow: disables local IRQs around load/store or compare/store.

State and persistence: caller memory only.

Dependencies and integration points: UP/legacy CPU atomic users.

Risks and test signals: not sufficient for true SMP without global exclusion. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
