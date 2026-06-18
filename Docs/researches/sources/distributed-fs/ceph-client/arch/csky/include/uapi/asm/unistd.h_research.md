# sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/unistd.h

## Purpose

selects generic syscall numbering and C-SKY syscall count exports

## Important APIs, Types, and Functions

Source read size: 6 lines, 153 bytes. Includes: `asm/unistd_32.h`. Key macros/defines:
`__NR_sync_file_range2`.

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
