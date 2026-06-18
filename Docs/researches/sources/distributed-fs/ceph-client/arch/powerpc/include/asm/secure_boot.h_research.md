<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/secure_boot.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/secure_boot.h

Purpose: Exposes simple predicates for PowerPC secure boot and trusted boot support.

Important APIs/types/functions: `is_ppc_secureboot_enabled()` and `is_ppc_trustedboot_enabled()`. Source-visible declarations include: #define _ASM_POWER_SECURE_BOOT_H; static inline bool is_ppc_secureboot_enabled(void); static inline bool is_ppc_trustedboot_enabled(void).

Control flow: security and keyring code call these helpers and receive platform-specific answers only in secure-boot builds. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: boot trust state is platform state queried elsewhere; this wrapper stores none. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with platform security, module signature policy, and key-loading paths.

Risks: stubbed false values on unsupported builds must not be mistaken for a runtime disabled policy. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 29 lines, 476 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/secure_boot.h -->
