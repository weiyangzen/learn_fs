<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/arch_data.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/arch_data.h

Purpose: Defines PowerPC architecture-specific data embedded in the generic vDSO data page.

Important APIs/types/functions: `SYSCALL_MAP_SIZE` and `struct vdso_arch_data` variants for 32-bit and 64-bit builds. Source-visible declarations include: #define _ASM_POWERPC_VDSO_ARCH_DATA_H; #define SYSCALL_MAP_SIZE ((NR_syscalls + 31) / 32); struct vdso_arch_data {; struct vdso_arch_data {.

Control flow: kernel populates syscall maps or architecture data that vDSO helpers read without syscalls. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: mapped vDSO data persists read-only or read-mostly for userspace. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/unistd.h>, #include <linux/types.h>. Integrated with generic vDSO data, syscall availability mapping, and libc vDSO consumers.

Risks: structure layout must stay synchronized with vDSO code compiled for user mapping. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 37 lines, 1171 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/arch_data.h -->
