# sources/distributed-fs/ceph-client/arch/sh/include/asm/bug.h



Source read size: 121 lines, 2871 bytes.



Purpose: SH BUG/WARN trap encoding.

Important APIs/types/functions: `BUG`, `WARN_ON`, `UNWINDER_BUG`, bug-table emission, trap opcode `trapa #0x3e`, `die*()` declarations.

Control flow: inline asm emits trap and metadata into `__bug_table`.

State and persistence: bug table metadata persists in kernel image.

Dependencies and integration points: generic bug framework, unwinder, trap handling.

Risks and test signals: bad metadata breaks diagnostics/unwinding. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
