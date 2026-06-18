<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/unistd32.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/unistd32.h

Purpose: Includes the generated 32-bit PowerPC syscall-number table.

Important APIs/types/functions: `asm/unistd_32.h` include. Source-visible declarations include: #define _ASM_POWERPC_UNISTD32_H_.

Control flow: compat and 32-bit builds include this wrapper for syscall numbers. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: no state; generated numbers define ABI. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/unistd_32.h>. Integrated with 32-bit syscall tables and UAPI export.

Risks: must track generated syscall list exactly. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 7 lines, 181 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/unistd32.h -->
