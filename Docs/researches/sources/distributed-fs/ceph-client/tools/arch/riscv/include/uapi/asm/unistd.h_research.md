# sources/distributed-fs/ceph-client/tools/arch/riscv/include/uapi/asm/unistd.h

## Purpose
RISC-V syscall UAPI selector and architecture-specific syscall declaration.

## Important APIs, Types, and Functions
Requests `__ARCH_WANT_NEW_STAT` and `__ARCH_WANT_SET_GET_RLIMIT`, includes generic unistd, defines `__NR_riscv_flush_icache`, and registers it with `__SYSCALL()`.

## Control Flow, State, and Persistence
Include-time flow expands generic syscall definitions, then appends the RISC-V flush-icache syscall used because userspace cannot portably synchronize remote instruction caches itself.

## Dependencies and Integration Points
Integrated with syscall tracing and generated syscall tables for RISC-V.

## Risks and Test Signals
Risk is wrong arch-specific syscall offset or missing syscall registration. Test signals are syscall table generation and trace/decode of `riscv_flush_icache`.
