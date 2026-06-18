<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/moduleloader.h -->
# sources/distributed-fs/ceph-client/include/linux/moduleloader.h

## Purpose
`moduleloader.h` declares architecture hooks used by the generic module loader for ELF validation, section adjustment, relocation, finalization, and cleanup.

## Important APIs, Types, and Functions
The header declares `module_elf_check_arch()`, `module_frob_arch_sections()`, `arch_mod_section_prepend()`, `module_init_section()`, `module_exit_section()`, `module_init_layout_section()`, `apply_relocate()`, `apply_relocate_add()`, optional livepatch `clear_relocate_add()`, `module_finalize()`, `flush_module_init_free_work()`, `module_arch_cleanup()`, and `module_arch_freeing_init()`.

## Control Flow and State
During load, the module loader validates ELF headers, lets architecture code adjust sections, applies REL or RELA relocations, finalizes architecture-specific state, and later frees init memory. On unload or failure, architecture cleanup hooks release any arch-owned state. Unsupported relocation formats return `-ENOEXEC` via stubs.

## State and Persistence Behavior
The header does not own persistent state, but its hooks mutate `struct module` memory, architecture-specific fields, relocation targets, and livepatch relocation cleanup state.

## Dependencies and Integration Points
It depends on `linux/module.h` and ELF definitions, and integrates with architecture module backends, livepatch, init/exit section classification, and module memory freeing.

## Risks
Relocation bugs corrupt executable module memory. Section classification affects whether memory is kept, freed, or considered init/core by address lookups. Livepatch relocation cleanup is architecture-sensitive. Stubs must only be used when the corresponding relocation format is genuinely unsupported.

## Test Signals
Load modules with REL and RELA relocations on supported architectures, test module unload/reload, run livepatch reload scenarios, verify init memory freeing, and build architectures with only one relocation format enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/moduleloader.h -->
