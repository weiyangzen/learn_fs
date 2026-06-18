# sources/distributed-fs/ceph-client/arch/csky/kernel/module.c

Purpose: ELF module relocation and C-SKY branch/call fixups for loadable modules.

Important APIs/types/functions: functions: `jsri_2_lrw_jsr`, `apply_relocate_add`; macros: `IS_BSR32(hi16,`, `IS_JSRI32(hi16,`, `CHANGE_JSRI_TO_LRW(addr)`, `SET_JSR32_R26(addr)`

Control flow: Runtime flow is organized around `jsri_2_lrw_jsr`, `apply_relocate_add`, called by generic kernel subsystems through architecture hooks.

State and persistence: Persistent effect is executable text or relocation patching; cache synchronization is required so all CPUs execute the updated instruction stream.

Dependencies and integration: Depends on `linux/moduleloader.h`, `linux/elf.h`, `linux/mm.h`, `linux/vmalloc.h`, `linux/slab.h`, `linux/fs.h`, `linux/string.h`, `linux/kernel.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Instruction encoding, alignment, text patching, simulated control flow, and cache coherency are high-risk and can misdirect execution or crash CPUs.

Test signals: C-SKY cross-build.
