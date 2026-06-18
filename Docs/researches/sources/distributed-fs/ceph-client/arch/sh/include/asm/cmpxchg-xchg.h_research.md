# sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg-xchg.h



Source read size: 50 lines, 1274 bytes.



Purpose: portable subword xchg built on 32-bit cmpxchg.

Important APIs/types/functions: `__xchg_cmpxchg`, `xchg_u16`, `xchg_u8`.

Control flow: aligns to containing u32, masks/shifts by endian, retries cmpxchg until update succeeds.

State and persistence: caller memory word.

Dependencies and integration points: CAS/LLSC backends needing byte/halfword xchg.

Risks and test signals: unaligned pointer and endian bit offset mistakes. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
