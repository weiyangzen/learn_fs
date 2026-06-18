# sources/distributed-fs/ceph-client/arch/arm64/kernel/module.c

Purpose: Implements AArch64 module relocation application, alternative patching, dynamic SCS patching, and ftrace PLT initialization.

Important APIs and state: relocation helpers include `do_reloc()`, `reloc_data()`, `reloc_insn_movw()`, `reloc_insn_imm()`, and `reloc_insn_adrp()`. Public entry points are `apply_relocate_add()` and `module_finalize()`. `WRITE_PLACE()` writes directly for unformed modules and uses `aarch64_insn_copy()` for already formed text.

Control flow: `apply_relocate_add()` iterates ELF RELA entries, resolves `S + A`, switches on relocation type, patches data or instruction immediates, emits PLTs for out-of-range CALL/JUMP26, and emits veneers or ADR substitutions for vulnerable ADRP locations. `module_finalize()` applies `.altinstructions`, optionally patches `.init.eh_frame` for dynamic shadow call stack, and initializes ftrace PLTs.

Dependencies and integration: integrates with module loader, `module-plts.c`, alternative patching, shadow call stack PI patcher, ftrace, KASAN/module memory, and arm64 instruction encoding.

Risks and test signals: risks include relocation overflow, unsupported RELA types, incorrect signed vs unsigned handling, writing executable memory without text patching, missing PLTs, and malformed SCS frame data. Test by loading modules with broad relocation coverage, far branch targets, alternatives, dynamic SCS, ftrace, and negative tests for unsupported/overflow relocations.
