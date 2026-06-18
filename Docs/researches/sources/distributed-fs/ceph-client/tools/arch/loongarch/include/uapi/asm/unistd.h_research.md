# sources/distributed-fs/ceph-client/tools/arch/loongarch/include/uapi/asm/unistd.h

## Purpose
LoongArch syscall UAPI selector for tools.

## Important APIs, Types, and Functions
Requests `__ARCH_WANT_SYS_CLONE` and includes `asm-generic/unistd.h`.

## Control Flow, State, and Persistence
No runtime flow; generic syscall generation handles expansion.

## Dependencies and Integration Points
Integrated by syscall-number and trace tooling for LoongArch.

## Risks and Test Signals
Risk is missing architecture wants as LoongArch syscall ABI evolves. Test signals are syscall table generation and clone syscall trace coverage.
