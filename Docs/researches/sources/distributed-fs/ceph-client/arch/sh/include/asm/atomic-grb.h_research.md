# sources/distributed-fs/ceph-client/arch/sh/include/asm/atomic-grb.h



Source read size: 95 lines, 3045 bytes.



Purpose: GUSA restartable-block atomic backend.

Important APIs/types/functions: restartable inline assembly for add/sub/and/or/xor.

Control flow: temporarily encodes block size in r15, updates memory, restores stack pointer.

State and persistence: mutates caller atomic_t and transient r15/r0/r1.

Dependencies and integration points: GUSA_RB CPUs and signal/restart machinery.

Risks and test signals: r15 manipulation and compiler constraints are fragile. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
