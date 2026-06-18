# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/ptrace.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/ptrace.h` defines ARM ptrace requests,
CPSR/PSR bits, register aliases, and user-visible pt_regs layout. It is part of the vendored Linux
ARM code under the Ceph client source tree and has 154 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: PTRACE_GET/SET* constants, mode bits, PSR masks, PT_* magic
offsets, struct pt_regs, ARM_* register macros, and ARM_VFPREGS_SIZE.
Visible dependencies include: `asm/hwcap.h`.
Important macros/constants include: `_UAPI__ASM_ARM_PTRACE_H`, `PTRACE_GETREGS`, `PTRACE_SETREGS`,
`PTRACE_GETFPREGS`, `PTRACE_SETFPREGS`, `PTRACE_GETWMMXREGS`, `PTRACE_SETWMMXREGS`,
`PTRACE_OLDSETOPTIONS`, `PTRACE_GET_THREAD_AREA`, `PTRACE_SET_SYSCALL`, `PTRACE_GETCRUNCHREGS`,
`PTRACE_SETCRUNCHREGS`, `PTRACE_GETVFPREGS`, `PTRACE_SETVFPREGS`, `PTRACE_GETHBPREGS`,
`PTRACE_SETHBPREGS`, `PTRACE_GETFDPIC`, `PTRACE_GETFDPIC_EXEC`, ... (77 total).

## Control Flow
debuggers and core dump code use these definitions to inspect or modify task register state.

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: any layout or numeric change breaks gdb, strace, crash dump readers, and old tracing
tools. Changes should preserve register layouts, numeric constants, early-boot calling conventions,
and userspace/module ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.
