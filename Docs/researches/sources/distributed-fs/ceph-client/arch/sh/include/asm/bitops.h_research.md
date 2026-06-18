# sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops.h



Source read size: 72 lines, 1656 bytes.



Purpose: top-level SH bit operations selector.

Important APIs/types/functions: backend includes, `ffz()`, `__ffs()`, generic ffs/hweight/lock/le helpers.

Control flow: selects atomic bitop implementation by CPU/config and provides inline bit scanning.

State and persistence: caller-owned bitmaps only.

Dependencies and integration points: scheduler, locks, filesystems, memory management.

Risks and test signals: backend mismatch breaks bitmap atomicity or endian semantics. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
