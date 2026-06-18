# sources/distributed-fs/ceph-client/arch/parisc/include/asm/alternative.h

Purpose: defines PA-RISC runtime instruction alternative metadata and assembly macros. It lets boot code patch instructions based on CPU/platform conditions such as SMP, cache presence, split TLB availability, I/O cache behavior, or QEMU.

Important APIs/types/functions: `struct alt_instr`, `ALT_COND_*`, `INSN_PxTLB`, `INSN_NOP`, declarations for `set_kernel_text_rw()` and `apply_alternatives_all()`, and the `ALTERNATIVE`/`ALTERNATIVE_CODE` macros.

Control flow: assembly emits original instructions plus entries in `__alt_instructions`; early runtime code makes kernel text writable, evaluates conditions, patches replacement instructions, and restores protection.

State and persistence: patch decisions persist by modifying kernel text. Dependencies and integration: integrates with `sections.h`, cache/TLB setup, text patching, and architecture initialization.

Risks and test signals: wrong instruction counts or section metadata can patch adjacent code. Test with objdump section checks, boot logs for alternative application, and platform coverage for all condition bits.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
