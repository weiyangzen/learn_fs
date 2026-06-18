<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/seccomp.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/seccomp.h

Purpose: Defines PowerPC seccomp audit architecture variants and sigreturn syscall names.

Important APIs/types/functions: native and compat seccomp syscall numbers, little-endian audit suffix fields, and generic seccomp inclusion. Source-visible declarations include: #define _ASM_POWERPC_SECCOMP_H; #define __NR_seccomp_sigreturn_32 __NR_sigreturn; #define __SECCOMP_ARCH_LE __AUDIT_ARCH_LE; #define __SECCOMP_ARCH_LE_NAME "le"; #define __SECCOMP_ARCH_LE 0; #define __SECCOMP_ARCH_LE_NAME.

Control flow: seccomp validation compares filter architecture values with task ABI and endian mode. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: no persistent state; policy state lives in generic seccomp filters. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/unistd.h>, #include <asm-generic/seccomp.h>. Integrated with audit, ptrace, seccomp, and syscall ABI code.

Risks: audit constants must distinguish 32/64-bit and LE/BE ABIs or filters can match the wrong syscall table. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 34 lines, 1043 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/seccomp.h -->
