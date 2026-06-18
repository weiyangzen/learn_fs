<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/platform_early.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/platform_early.h

## Purpose
Defines SH architecture declarations and macros for `platform_early` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `linux/types.h`, `linux/platform_device.h`, `linux/pm_runtime.h`, `linux/slab.h`. Key macros/constants include `__PLATFORM_EARLY__`, `EARLY_PLATFORM_ID_UNSET`, `EARLY_PLATFORM_ID_ERROR`, `sh_early_platform_init(class_string, platdrv)`, `sh_early_platform_init_buffer(class_string, platdrv, buf, bufsiz)`. Structures include `sh_early_platform_driver`, `platform_driver`, `list_head`. Functions or extern declarations include `sh_early_platform_driver_register`, `sh_early_platform_add_devices`, `sh_early_platform_driver_register_all`, `sh_early_platform_driver_probe`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `linux/types.h`, `linux/platform_device.h`, `linux/pm_runtime.h`, `linux/slab.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 61 lines, 1849 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/platform_early.h -->
