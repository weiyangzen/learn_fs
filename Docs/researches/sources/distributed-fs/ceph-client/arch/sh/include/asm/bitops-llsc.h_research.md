# sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops-llsc.h



Source read size: 147 lines, 2858 bytes.



Purpose: SH4A LL/SC atomic bitops.

Important APIs/types/functions: set/clear/change/test-and operations using `movli.l`/`movco.l`.

Control flow: retry loop until conditional store succeeds.

State and persistence: caller bitmap only.

Dependencies and integration points: SH4A atomic bitmap users.

Risks and test signals: barrier placement and r0 constraints. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
