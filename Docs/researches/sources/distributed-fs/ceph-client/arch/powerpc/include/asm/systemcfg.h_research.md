<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/systemcfg.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/systemcfg.h

Purpose: Defines the ppc64 system configuration page exported to userspace.

Important APIs/types/functions: `SYSTEMCFG_MAJOR/MINOR`, `struct systemcfg`, and global `systemcfg` pointer. Source-visible declarations include: #define _SYSTEMCFG_H; #define SYSTEMCFG_MAJOR 1; #define SYSTEMCFG_MINOR 1; struct systemcfg {; struct { /* Systemcfg version numbers */; extern struct systemcfg *systemcfg;.

Control flow: kernel populates the page with processor, cache, TB, platform, and feature data for userspace/vDSO consumers. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: the mapped systemcfg page persists as read-mostly kernel/userspace ABI state. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/types.h>. Integrated with ppc64 vDSO, glibc, timebase calibration, and platform feature discovery.

Risks: layout changes require versioning and userspace compatibility care. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 52 lines, 1726 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/systemcfg.h -->
