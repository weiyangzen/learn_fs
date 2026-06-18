# sources/distributed-fs/ceph-client/arch/sh/include/asm/atomic-llsc.h



Source read size: 97 lines, 2554 bytes.



Purpose: SH4A LL/SC atomic backend.

Important APIs/types/functions: `movli.l`/`movco.l` loops for arithmetic and bitwise atomics.

Control flow: retry loop until conditional store succeeds, with `synco` on return/fetch variants.

State and persistence: mutates caller atomic_t only.

Dependencies and integration points: SH4A SMP/atomic users.

Risks and test signals: inline asm constraints and missing barriers are high risk. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
