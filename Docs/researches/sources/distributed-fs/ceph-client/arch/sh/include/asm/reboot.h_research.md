<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/reboot.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/reboot.h

## Purpose
Defines SH platform hooks for `reboot` memory, power, reset, or timekeeping integration.

## Important APIs, Types, And Functions
Includes `linux/kdebug.h`. Key macros/constants include `__ASM_SH_REBOOT_H`. Structures include `pt_regs`, `machine_ops`. Functions or extern declarations include `native_machine_crash_shutdown`, `machine_ops`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `linux/kdebug.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 22 lines, 472 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/reboot.h -->
