<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uic.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uic.h

Purpose: Declares IBM 4xx Universal Interrupt Controller setup hooks.

Important APIs/types/functions: `uic_init_tree()` and `uic_get_irq()`. Source-visible declarations include: #define _ASM_POWERPC_UIC_H; extern void __init uic_init_tree(void);; extern unsigned int uic_get_irq(void);.

Control flow: platform IRQ initialization builds the UIC tree and runtime interrupt entry asks it for the pending IRQ. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: UIC mask/status hardware state is owned by the implementation. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with PowerPC 4xx interrupt controller and device-tree IRQ setup.

Risks: tree setup must match cascaded UIC topology or interrupt dispatch loses lines. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 17 lines, 403 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uic.h -->
