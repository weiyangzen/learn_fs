<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/watchdog.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/watchdog.h

## Purpose
Defines SH platform hooks for `watchdog` memory, power, reset, or timekeeping integration.

## Important APIs, Types, And Functions
Includes `linux/types.h`, `linux/io.h`, `cpu/watchdog.h`. Key macros/constants include `__ASM_SH_WATCHDOG_H`, `WTCNT_HIGH`, `WTCSR_HIGH`, `WTCSR_CKS2`, `WTCSR_CKS1`, `WTCSR_CKS0`, `WTCNT_R`, `WTCSR_R`, `WTCSR_CKS_32`, `WTCSR_CKS_64`, `WTCSR_CKS_128`, `WTCSR_CKS_256`, `WTCSR_CKS_512`, `WTCSR_CKS_1024`, `WTCSR_CKS_2048`, `WTCSR_CKS_4096`. Register or hardware-address constants include `WTCNT_HIGH`, `WTCSR_HIGH`, `WTCSR_CKS2`, `WTCSR_CKS1`, `WTCSR_CKS0`, `WTCNT_R`, `WTCSR_R`, `WTCSR_CKS_32`, `WTCSR_CKS_64`, `WTCSR_CKS_128`, `WTCSR_CKS_256`, `WTCSR_CKS_512`, plus 3 more.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `linux/types.h`, `linux/io.h`, `cpu/watchdog.h`. Kconfig-sensitive paths mention `CONFIG_CPU_SUBTYPE_SH7785`, `CONFIG_CPU_SUBTYPE_SH7780`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 159 lines, 3981 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/watchdog.h -->
