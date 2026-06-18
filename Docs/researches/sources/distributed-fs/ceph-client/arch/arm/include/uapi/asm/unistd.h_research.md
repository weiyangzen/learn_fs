# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/unistd.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/unistd.h` selects ARM EABI or OABI
syscall number headers and defines ARM-private SWIs. It is part of the vendored Linux ARM code under
the Ceph client source tree and has 41 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: __NR_OABI_SYSCALL_BASE, __NR_SYSCALL_MASK, __NR_SYSCALL_BASE,
unistd-eabi.h/unistd-oabi.h includes, __NR_sync_file_range2 alias, and __ARM_NR_*.
Visible dependencies include: `asm/unistd-eabi.h`, `asm/unistd-oabi.h`.
Important macros/constants include: `_UAPI__ASM_ARM_UNISTD_H`, `__NR_OABI_SYSCALL_BASE`,
`__NR_SYSCALL_MASK`, `__NR_SYSCALL_BASE`, `__NR_sync_file_range2`, `__ARM_NR_BASE`,
`__ARM_NR_breakpoint`, `__ARM_NR_cacheflush`, `__ARM_NR_usr26`, `__ARM_NR_usr32`,
`__ARM_NR_set_tls`, `__ARM_NR_get_tls`.

## Control Flow
the syscall entry path and libc agree on the syscall base and private ARM SWI range.

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
Primary risk: wrong base selection breaks every syscall for the affected ABI. Changes should
preserve register layouts, numeric constants, early-boot calling conventions, and userspace/module
ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.
