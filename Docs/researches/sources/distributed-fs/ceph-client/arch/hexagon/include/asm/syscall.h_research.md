# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/syscall.h

Purpose: Hexagon syscall register access helpers for tracing and seccomp.

Important APIs/types/functions: functions: `syscall_get_nr`, `syscall_set_nr`, `syscall_get_arguments`, `syscall_set_arguments`, `syscall_get_error`, `syscall_get_return_value`, `syscall_set_return_value`, `syscall_get_arch`; types: `pt_regs`; macros: `_ASM_HEXAGON_SYSCALL_H`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `uapi/linux/audit.h`, `linux/err.h`, `asm/ptrace.h`, `asm-generic/syscalls.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.
