# sources/distributed-fs/ceph-client/arch/s390/kernel/module.c

Purpose: s390 module loader architecture support for GOT/PLT sizing, ELF relocation application, module finalization patching, stack protector setup, alternatives, expoline reversion, and ftrace trampoline allocation.

Important APIs and state: `module_frob_arch_sections()` scans symbols and relocations, initializes `mod->arch.syminfo`, and grows module text memory for GOT/PLT. `apply_relocate_add()` applies relocations with `memcpy` during early unformed state or `s390_kernel_write()` later. `module_finalize()` applies alternatives, nospec reverts, stack-protector locations, and ftrace callsite trampoline allocation. Cleanup frees syminfo and optional ftrace executable memory.

Control flow: `check_rela()` assigns per-symbol GOT/PLT offsets. `apply_rela_bits()` validates alignment, signedness, bit width, and shifted values before writing split/direct fields. `apply_rela()` handles direct, PC-relative, GOT, PLT, GOTOFF, GOTPC, and unsupported dynamic relocations. PLT entries are synthesized with optional expoline tail thunk when speculation mitigation is active.

Dependencies and integration: depends on module core memory classes, s390 ABI relocation constants, executable memory, alternatives, nospec branch state, stack protector, ftrace linker sections, and livepatch module lifetime.

Risks and test signals: relocation range errors, PLT fallback selection, expoline thunk sizing, late text writes, and livepatch cleanup are sensitive. Test modules with far calls, GOT-heavy code, livepatch modules, ftrace-enabled modules, expoline on/off, stack protector, alternatives, and unknown relocation rejection.
