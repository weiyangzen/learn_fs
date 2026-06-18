# sources/distributed-fs/ceph-client/arch/sh/include/asm/cachetype.h



Source read size: 9 lines, 170 bytes.



Purpose: cache type predicate.

Important APIs/types/functions: `cpu_dcache_is_aliasing()` returns true.

Control flow: compile-time inline decision.

State and persistence: none.

Dependencies and integration points: generic cache alias handling.

Risks and test signals: over-conservative but safe; wrong false would be dangerous. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
