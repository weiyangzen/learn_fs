
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/x86-stub.h

Purpose: declares x86 EFI stub interfaces shared between the main x86 stub and 5-level paging support.

Important APIs/types/functions: declares trampoline symbols, `efi_adjust_memory_range_protection()`, and `efi_setup_5level_paging()`/`efi_5level_switch()` with no-op stubs on non-64-bit builds.

Control flow: no direct flow. It provides compile-time selection between real LA57 support on x86_64 and no-op behavior elsewhere.

State and persistence behavior: no state in the header.

Dependencies and integration points: depends on EFI and x86 boot headers. It connects `x86-stub.c` to `x86-5lvl.c`.

Risks and test signals: incorrect conditional prototypes would break 32-bit or 64-bit EFI builds. Test signals are successful x86_32, x86_64, `CONFIG_EFI_MIXED`, and non-LA57 configurations.
