<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/task_size_32.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/task_size_32.h

Purpose: Computes 32-bit PowerPC user, module, vmalloc, and IO mapping address windows.

Important APIs/types/functions: `MODULES_*`, `USER_TOP`, `TASK_SIZE`, `VMALLOC_START/END`, `IOREMAP_TOP`, and config-dependent layout constants. Source-visible declarations include: #define _ASM_POWERPC_TASK_SIZE_32_H; #define MODULES_END ASM_CONST(CONFIG_PAGE_OFFSET); #define MODULES_SIZE (CONFIG_MODULES_SIZE * SZ_1M); #define MODULES_VADDR (MODULES_END - MODULES_SIZE); #define MODULES_BASE (MODULES_VADDR & ~(UL(SZ_4M) - 1)); #define USER_TOP (MODULES_BASE - SZ_4M); #define MODULES_END (ASM_CONST(CONFIG_PAGE_OFFSET) & ~(UL(SZ_256M) - 1)); #define MODULES_SIZE (CONFIG_MODULES_SIZE * SZ_1M).

Control flow: MM setup and address validation use these constants to split user, module, vmalloc, and ioremap spaces. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: layout persists as the process/kernel virtual address ABI for the booted config. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/sizes.h>. Integrated with 32-bit MMU setup, modules, vmalloc, ioremap, and `access_ok()`.

Risks: small layout changes can overlap user space, modules, or vmalloc and break ABI assumptions. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 47 lines, 1345 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/task_size_32.h -->
