# sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops-grb.h



Source read size: 173 lines, 6364 bytes.



Purpose: GUSA restartable-block atomic bitops.

Important APIs/types/functions: set/clear/change/test-and operations.

Control flow: uses r15 restartable block login/logout around word updates.

State and persistence: caller bitmap plus transient register state.

Dependencies and integration points: GUSA_RB systems.

Risks and test signals: signal/restart and inline asm fragility. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
