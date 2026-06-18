# sources/distributed-fs/ceph-client/arch/x86/kernel/module.c

Purpose: Implements x86-specific module relocation, runtime relocation clearing for livepatch, and final module text fixups such as alternatives, retpolines, returns, call thunks, FineIBT/CFI, ENDBR sealing, SMP locks, and ORC unwind registration.

Important APIs/types/functions: defines `apply_relocate()` on 32-bit, `apply_relocate_add()` on 64-bit, optional `clear_relocate_add()`, `module_finalize()`, and `module_arch_cleanup()`. Internal helper `__write_relocate_add()` applies or clears ELF64 RELA relocations with either `memcpy` or `text_poke`.

Control flow: 32-bit relocation applies `R_386_32`, `R_386_PC32`, and `R_386_PLT32`. 64-bit relocation computes symbol plus addend, validates relocation type and overflow, verifies the target is zero before applying or matches expected value before clearing, then writes through normal memory for unformed modules or `text_poke` under `text_mutex` for live modules. Finalization scans section names, initializes IBT sealing state, applies FineIBT/CFI and retpolines, finalizes IBT state, applies return-site and call-thunk patches, alternatives, ENDBR sealing, SMP lock alternatives, and ORC unwind metadata.

State and persistence: relocation writes modify loaded module memory. Runtime relocation patching for already formed modules uses synchronized text patching. Module cleanup removes SMP alternatives and frees IBT sealing metadata.

Dependencies and integration points: depends on ELF relocation definitions, module loader state, x86 text patching, alternatives, jump labels/static calls indirectly through module text, retpoline/return thunk/fineibt/callthunk machinery, objtool-generated sections, ORC unwinder, stack protector special clang relocation workaround, and livepatch clearing.

Risks: relocation targets are required to be zero before apply to detect corrupt or reused module text. PC-relative and 32-bit relocations check overflow. Finalization order matters: FineIBT, retpolines, return sites, alternatives, and sealing all mutate code. Runtime patching must hold `text_mutex` and sync CPUs.

Test signals: module load tests should cover 32-bit and 64-bit relocation types, overflow rejection, nonzero relocation target rejection, livepatch clear/apply paths, modules with alternatives, ORC unwind, retpolines, return sites, call thunks, CFI/FineIBT, ENDBR sealing, and module unload cleanup.
