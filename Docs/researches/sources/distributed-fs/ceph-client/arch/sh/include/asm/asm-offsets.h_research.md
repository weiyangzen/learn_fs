# sources/distributed-fs/ceph-client/arch/sh/include/asm/asm-offsets.h



Source read size: 2 lines, 74 bytes.



Purpose: wrapper for generated assembly offsets.

Important APIs/types/functions: `<generated/asm-offsets.h>`.

Control flow: assembly includes generated C structure offsets.

State and persistence: generated build artifact only.

Dependencies and integration points: low-level assembly entry/context code.

Risks and test signals: stale offsets corrupt register frames. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
