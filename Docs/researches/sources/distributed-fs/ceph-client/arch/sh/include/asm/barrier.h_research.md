# sources/distributed-fs/ceph-client/arch/sh/include/asm/barrier.h



Source read size: 45 lines, 1503 bytes.



Purpose: SH memory/control barrier definitions.

Important APIs/types/functions: `mb/rmb/wmb`, `ctrl_barrier`, `__smp_*`, `__smp_store_mb`.

Control flow: maps barriers to `synco`, `icbi`, CAS trick, or nop sequence depending on CPU.

State and persistence: no storage; orders CPU/register effects.

Dependencies and integration points: MMU/CCR writes, SMP locking, atomics.

Risks and test signals: weak barrier selection causes ordering bugs. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
