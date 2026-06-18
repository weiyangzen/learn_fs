# sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/posix_types.h

## Purpose

selects exported POSIX type definitions for MicroBlaze

## Important APIs, Types, and Functions

Source read size: 10 lines, 302 bytes. Includes: `asm-generic/posix_types.h`. Key macros/defines:
`_ASM_MICROBLAZE_POSIX_TYPES_H`, `__kernel_mode_t`. Types visible in this file: `__kernel_mode_t`.

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
