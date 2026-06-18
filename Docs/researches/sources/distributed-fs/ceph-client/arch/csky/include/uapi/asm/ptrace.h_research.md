# sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/ptrace.h

## Purpose

defines user-visible register structures and ptrace constants

## Important APIs, Types, and Functions

Source read size: 51 lines, 839 bytes. Key macros/defines: `_CSKY_PTRACE_H`. Local structs:
`pt_regs`, `user_fp`.

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
