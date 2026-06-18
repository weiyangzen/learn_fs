# sources/distributed-fs/ceph-client/arch/sh/include/asm/bl_bit.h



Source read size: 2 lines, 66 bytes.



Purpose: BL-bit helper include wrapper.

Important APIs/types/functions: `<asm/bl_bit_32.h>`.

Control flow: delegates to 32-bit status-register helpers.

State and persistence: CPU status register state.

Dependencies and integration points: exception/interrupt masking code.

Risks and test signals: wrong include affects BL manipulation. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
