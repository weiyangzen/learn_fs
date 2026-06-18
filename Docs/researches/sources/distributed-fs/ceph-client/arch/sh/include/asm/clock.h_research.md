# sources/distributed-fs/ceph-client/arch/sh/include/asm/clock.h



Source read size: 17 lines, 436 bytes.



Purpose: SH clock initialization declarations.

Important APIs/types/functions: `arch_init_clk_ops`, `arch_clk_init`, `cpg_clk_init`, `clk_init`.

Control flow: platform/CPU clock init calls these during boot.

State and persistence: clock framework state lives in implementation.

Dependencies and integration points: SH CPG/common clock and board setup.

Risks and test signals: deprecated hooks can hide missing COMMON_CLK migration. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
