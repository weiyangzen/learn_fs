<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/synch.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/synch.h

Purpose: Defines PowerPC memory synchronization instructions and barrier string macros.

Important APIs/types/functions: `eieio()`, `isync()`, `ppc_after_tlbiel_barrier()`, lwsync fixups, acquire/release barrier strings, and atomic entry/exit barriers. Source-visible declarations include: #define _ASM_POWERPC_SYNCH_H; extern unsigned int __start___lwsync_fixup, __stop___lwsync_fixup;; extern void do_lwsync_fixups(unsigned long value, void *fixup_start,; static inline void eieio(void); static inline void isync(void); static inline void ppc_after_tlbiel_barrier(void); #define __PPC_ACQUIRE_BARRIER \; #define PPC_ACQUIRE_BARRIER "\n" stringify_in_c(__PPC_ACQUIRE_BARRIER).

Control flow: atomic/locking/TLB code emits the selected barrier sequence, with boot-time fixups replacing unsupported lwsync forms. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: patchable barrier sites are linker/runtime state; no per-call state. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/cputable.h>, #include <asm/feature-fixups.h>, #include <asm/ppc-opcode.h>. Integrated with atomic primitives, spinlocks, TLB invalidation, feature fixups, and assembly code.

Risks: barrier weakening can create rare memory-order bugs; CPU feature fixups must match hardware support. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 73 lines, 2159 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/synch.h -->
