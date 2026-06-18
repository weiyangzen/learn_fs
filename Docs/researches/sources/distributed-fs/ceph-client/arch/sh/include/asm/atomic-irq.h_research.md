# sources/distributed-fs/ceph-client/arch/sh/include/asm/atomic-irq.h



Source read size: 81 lines, 2055 bytes.



Purpose: IRQ-masked atomic backend.

Important APIs/types/functions: `arch_atomic_add/sub/and/or/xor` and fetch/return variants.

Control flow: saves local IRQs, updates `counter`, restores IRQs.

State and persistence: mutates caller atomic_t only.

Dependencies and integration points: UP or older SH cores lacking LL/SC.

Risks and test signals: not SMP-safe without stronger exclusion. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
