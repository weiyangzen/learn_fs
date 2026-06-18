<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/Makefile

## Purpose
This Makefile selects architecture-specific RISC-V library routines for the kernel build.

## Important APIs, Types, And Functions
It includes delay, memcpy, memset, memmove, checksum, uaccess, 128-bit shift helpers, Zicboz clear-page, vector helper, and optional error-injection objects. String routines are excluded under generic/software-tag KASAN so instrumented generic implementations can be used.

## Control Flow
Kbuild conditionals add objects based on `CONFIG_MMU`, `CONFIG_64BIT`, `CONFIG_RISCV_ISA_V`, `CONFIG_RISCV_ISA_ZICBOZ`, `CONFIG_FUNCTION_ERROR_INJECTION`, and KASAN modes.

## State And Persistence
No runtime state is defined. Build configuration determines which symbols exist in the final kernel.

## Dependencies And Integration Points
It integrates assembly/C helper objects with core kernel library symbols such as `memcpy`, `clear_user`, checksums, and string APIs.

## Risks
Changing object conditions can break early boot, user access, KASAN compatibility, or missing compiler helper symbols on 64-bit builds.

## Test Signals
Build matrix coverage across MMU/no-MMU, 32/64-bit, KASAN, vector, Zicboz, and error-injection configs is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/Makefile -->
