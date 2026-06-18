<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/static_call.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/static_call.h

Purpose: Defines PowerPC static-call trampoline assembly layout.

Important APIs/types/functions: `ARCH_DEFINE_STATIC_CALL_TRAMP()`, null and ret0 trampolines, trampoline offsets, and call instruction size. Source-visible declarations include: #define _ASM_POWERPC_STATIC_CALL_H; #define __PPC_SCT(name, inst) \; #define PPC_SCT_RET0 20 /* Offset of label 1 */; #define PPC_SCT_DATA 28 /* Offset of label 2 */; #define ARCH_DEFINE_STATIC_CALL_TRAMP(name, func) __PPC_SCT(name, "b " #func); #define ARCH_DEFINE_STATIC_CALL_NULL_TRAMP(name) __PPC_SCT(name, "blr"); #define ARCH_DEFINE_STATIC_CALL_RET0_TRAMP(name) __PPC_SCT(name, "b .+20"); #define CALL_INSN_SIZE 4.

Control flow: static-call core emits or patches trampoline text using fixed offset labels. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: state is generated executable trampoline text. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with kernel static call core and PowerPC text patching.

Risks: hard-coded offsets must match emitted assembly exactly or runtime patching edits the wrong instruction. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 31 lines, 1090 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/static_call.h -->
