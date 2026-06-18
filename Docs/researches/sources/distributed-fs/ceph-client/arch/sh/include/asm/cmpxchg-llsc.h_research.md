# sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg-llsc.h



Source read size: 53 lines, 1085 bytes.



Purpose: SH4A LL/SC xchg/cmpxchg backend.

Important APIs/types/functions: `xchg_u32`, `__cmpxchg_u32`.

Control flow: uses `movli.l`/`movco.l` retry loops with `synco`.

State and persistence: caller memory only.

Dependencies and integration points: SH4A atomic primitives.

Risks and test signals: conditional-store loop and barrier correctness. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
