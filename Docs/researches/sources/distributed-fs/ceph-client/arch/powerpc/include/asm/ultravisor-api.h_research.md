<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ultravisor-api.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ultravisor-api.h

Purpose: Defines PowerPC Ultravisor return codes and call numbers.

Important APIs/types/functions: UV return-code aliases to hypervisor codes and call IDs such as write PATE, share/unshare page, page-in/out, mem-slot registration, invalidation, and SVM terminate. Source-visible declarations include: #define _ASM_POWERPC_ULTRAVISOR_API_H; #define U_BUSY H_BUSY; #define U_FUNCTION H_FUNCTION; #define U_NOT_AVAILABLE H_NOT_AVAILABLE; #define U_P2 H_P2; #define U_P3 H_P3; #define U_P4 H_P4; #define U_P5 H_P5.

Control flow: ultravisor wrappers pass these call IDs to low-level UV call assembly. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: state resides in ultravisor-managed secure memory and partition tables. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/hvcall.h>. Integrated with secure VM, protected KVM, ultravisor firmware, and page sharing/migration code.

Risks: call numbers and return code meanings are firmware ABI and must match the ultravisor specification. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 39 lines, 941 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ultravisor-api.h -->
