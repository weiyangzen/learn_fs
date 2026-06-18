<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/stackprotector.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/stackprotector.h

Purpose: Seeds the PowerPC per-task stack canary from early random data.

Important APIs/types/functions: `boot_init_stack_canary()` inline setup using `get_random_canary()`, current task, and paca canary state. Source-visible declarations include: #define _ASM_STACKPROTECTOR_H.

Control flow: boot and fork paths initialize stack canaries before protected C code relies on them. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: canary values persist per task and in PACA on 64-bit. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/reg.h>, #include <asm/current.h>, #include <asm/paca.h>. Integrated with compiler stack protector, task setup, current/PACA accessors, and random canary source.

Risks: must run early enough and update the right per-CPU/task storage or stack protector checks become ineffective. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 30 lines, 604 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/stackprotector.h -->
