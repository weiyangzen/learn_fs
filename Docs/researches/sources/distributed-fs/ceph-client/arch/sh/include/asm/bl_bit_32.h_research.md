# sources/distributed-fs/ceph-client/arch/sh/include/asm/bl_bit_32.h



Source read size: 34 lines, 639 bytes.



Purpose: 32-bit SH status-register BL bit helpers.

Important APIs/types/functions: `set_bl_bit()` and `clear_bl_bit()`.

Control flow: reads SR, sets or clears BL and interrupt-mask bits, writes SR.

State and persistence: mutates CPU SR.

Dependencies and integration points: trap/interrupt critical sections.

Risks and test signals: incorrect SR masks can block interrupts or exceptions. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
