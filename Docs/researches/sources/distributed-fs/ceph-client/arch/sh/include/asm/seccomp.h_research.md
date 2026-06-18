<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/seccomp.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/seccomp.h

## Purpose
Provides the SH architecture hook for the generic Linux `seccomp` subsystem, mostly by defining small constants or forwarding to generic helpers.

## Important APIs, Types, And Functions
Includes `linux/unistd.h`. Key macros/constants include `__NR_seccomp_read`, `__NR_seccomp_write`, `__NR_seccomp_exit`, `__NR_seccomp_sigreturn`, `__SECCOMP_ARCH_LE`, `SECCOMP_ARCH_NATIVE`, `SECCOMP_ARCH_NATIVE_NR`, `SECCOMP_ARCH_NATIVE_NAME`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `linux/unistd.h`. Kconfig-sensitive paths mention `CONFIG_CPU_LITTLE_ENDIAN`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 21 lines, 546 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/seccomp.h -->
