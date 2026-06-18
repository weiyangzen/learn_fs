<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/text-patching.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/text-patching.h

Purpose: Declares and partially implements PowerPC runtime instruction patching helpers.

Important APIs/types/functions: branch creation/validation, `patch_instruction*`, `patch_instructions()`, site-address helpers, data patch helpers, feature-section patching, and instruction comparison helpers. Source-visible declarations include: #define _ASM_POWERPC_CODE_PATCHING_H; #define BRANCH_SET_LINK 0x1; #define BRANCH_ABSOLUTE 0x2; static inline bool is_offset_in_branch_range(long offset); static inline bool is_offset_in_cond_branch_range(long offset); static inline int create_branch(ppc_inst_t *instr, const u32 *addr,; #define patch_u64 patch_ulong; static inline int patch_uint(void *addr, unsigned int val).

Control flow: callers compute patch-site addresses, synthesize PowerPC instructions, patch text, and rely on cache/TLB synchronization in the implementation. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: patched kernel text and patch metadata persist after boot/runtime modification. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/types.h>, #include <asm/ppc-opcode.h>, #include <linux/string.h>, #include <linux/kallsyms.h>, #include <asm/asm-compat.h>, #include <asm/inst.h>. Integrated with ftrace, jump labels, static calls, alternatives, security mitigations, modules, BPF JIT, and feature fixups.

Risks: branch range checks, endianness, prefixed instructions, and cache synchronization are critical to avoid executing torn text. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 275 lines, 7542 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/text-patching.h -->
