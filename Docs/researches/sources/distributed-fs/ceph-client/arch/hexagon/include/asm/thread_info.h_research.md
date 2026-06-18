# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/thread_info.h

Purpose: Hexagon thread_info layout, fixed register lookup, and thread flags.

Important APIs/types/functions: types: `thread_info`, `task_struct`, `pt_regs`; macros: `_ASM_THREAD_INFO_H`, `THREAD_SHIFT`, `THREAD_SIZE`, `THREAD_SIZE_ORDER`, `INIT_THREAD_INFO(tsk)`, `qqstr(s)`, `qstr(s)`, `QUOTED_THREADINFO_REG`, `current_thread_info()`, `TIF_SYSCALL_TRACE`, `TIF_NOTIFY_RESUME`, `TIF_SIGPENDING`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/processor.h`, `asm/registers.h`, `asm/page.h`, `asm/asm-offsets.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.
