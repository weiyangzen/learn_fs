<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/task_size_64.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/task_size_64.h

Purpose: Computes 64-bit PowerPC user address-space windows for hash/radix MMUs.

Important APIs/types/functions: 64TB through 4PB constants, `TASK_SIZE_USER64`, default map windows, context size, and 32-bit compatibility window. Source-visible declarations include: #define _ASM_POWERPC_TASK_SIZE_64_H; #define TASK_SIZE_64TB (0x0000400000000000UL); #define TASK_SIZE_128TB (0x0000800000000000UL); #define TASK_SIZE_512TB (0x0002000000000000UL); #define TASK_SIZE_1PB (0x0004000000000000UL); #define TASK_SIZE_2PB (0x0008000000000000UL); #define TASK_SIZE_4PB (0x0010000000000000UL); #define TASK_SIZE_USER64 TASK_SIZE_4PB.

Control flow: MM code chooses effective user/task size from MMU mode, CPU features, and process ABI. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: virtual address limits persist per process/mm context. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with 64-bit MM, mmap layout, radix/hash MMU, compat tasks, and user access checks.

Risks: expanding windows affects userspace ABI, pointer tagging assumptions, and context-ID sizing. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 83 lines, 2630 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/task_size_64.h -->
