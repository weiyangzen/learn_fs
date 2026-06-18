# sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/sigcontext.h

## Purpose

defines the signal-frame machine context saved and restored by sigreturn

## Important APIs, Types, and Functions

Source read size: 13 lines, 271 bytes. Includes: `asm/ptrace.h`. Key macros/defines:
`__ASM_CSKY_SIGCONTEXT_H`. Local structs: `sigcontext`, `pt_regs`, `user_fp`.

## Control Flow and Behavior

the file is consumed by userspace-visible kernel headers and must preserve numeric constants,
structure layout, and include order

## State and Persistence

there is no kernel runtime state, but compiled userspace and kernel UAPI copies persist these
definitions as ABI

## Dependencies and Integration Points

integrates with asm-generic UAPI headers, libc, perf/ptrace/signal tooling, and syscall wrappers

## Risks and Test Signals

renumbering constants or changing layouts breaks existing binaries; headers_install, libc builds,
perf/ptrace, and signal tests are signals
