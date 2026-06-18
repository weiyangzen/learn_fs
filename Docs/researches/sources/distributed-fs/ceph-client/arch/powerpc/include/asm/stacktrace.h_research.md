<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/stacktrace.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/stacktrace.h

Purpose: Provides the PowerPC stacktrace include point.

Important APIs/types/functions: include guard only in this snapshot. Source-visible declarations include: #define _ASM_POWERPC_STACKTRACE_H.

Control flow: generic stacktrace code includes it for architecture hooks. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: no state. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with unwinder and generic stacktrace infrastructure.

Risks: minimal wrapper; future hooks must align with PowerPC frame layout. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 13 lines, 297 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/stacktrace.h -->
