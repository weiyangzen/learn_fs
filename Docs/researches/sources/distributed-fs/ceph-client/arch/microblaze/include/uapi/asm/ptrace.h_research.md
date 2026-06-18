# sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/ptrace.h

## Purpose

defines user-visible pt_regs/register structures and ptrace constants

## Important APIs, Types, and Functions

Source read size: 73 lines, 1827 bytes. Key macros/defines: `_UAPI_ASM_MICROBLAZE_PTRACE_H`,
`PT_GPR(n)`, `PT_PC`, `PT_MSR`, `PT_EAR`, `PT_ESR`, `PT_FSR`, `PT_KERNEL_MODE`. Types visible in
this file: `pt_regs`, `microblaze_reg_t`.

## Control Flow and Behavior

the file is consumed by headers_install and userspace libc/tooling, so constants and structures must
remain ABI-compatible

## State and Persistence

there is no mutable kernel runtime state, but compiled userspace and trace/debug tools persist the
ABI definitions

## Dependencies and Integration Points

integrates with asm-generic UAPI headers, ELF loaders, signal delivery, ptrace, seccomp, libc, and
perf/debuggers depending on the declarations

## Risks and Test Signals

renumbering or changing struct layout breaks existing binaries; headers_install, libc build, ptrace,
signal, and syscall tests are signals
