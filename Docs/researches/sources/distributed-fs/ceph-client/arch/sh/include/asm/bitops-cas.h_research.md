# sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops-cas.h



Source read size: 94 lines, 1770 bytes.



Purpose: CAS-loop atomic bitops for J2 SMP.

Important APIs/types/functions: `set_bit`, `clear_bit`, `change_bit`, test-and variants, `__bo_cas()`.

Control flow: uses `cas.l` retry loops on 32-bit words.

State and persistence: mutates caller bitmaps.

Dependencies and integration points: J2 SMP bitops and generic non-atomic helpers.

Risks and test signals: alignment/endian and CAS constraints. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
