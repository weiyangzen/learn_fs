<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/unistd.h

Purpose: Wraps PowerPC syscall-number UAPI and declares generic syscall implementation wants.

Important APIs/types/functions: `NR_syscalls`, many `__ARCH_WANT_*` feature macros, and 32-bit syscall entry declarations. Source-visible declarations include: #define _ASM_POWERPC_UNISTD_H_; #define NR_syscalls __NR_syscalls; #define __ARCH_WANT_NEW_STAT; #define __ARCH_WANT_OLD_READDIR; #define __ARCH_WANT_STAT64; #define __ARCH_WANT_SYS_ALARM; #define __ARCH_WANT_SYS_GETHOSTNAME; #define __ARCH_WANT_SYS_IPC.

Control flow: generic syscall code uses the want macros to include legacy implementations and syscall tables use `NR_syscalls`. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: syscall ABI is generated and immutable for the running kernel. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <uapi/asm/unistd.h>, #include <linux/types.h>, #include <linux/compiler.h>, #include <linux/linkage.h>. Integrated with syscall tables, compat syscalls, generic syscall selection, and userspace ABI headers.

Risks: want macro changes can remove legacy syscalls still required by PowerPC ABI. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 56 lines, 1485 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/unistd.h -->
