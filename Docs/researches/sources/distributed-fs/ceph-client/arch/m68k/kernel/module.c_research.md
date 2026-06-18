# sources/distributed-fs/ceph-client/arch/m68k/kernel/module.c

## Purpose

`module.c` provides m68k-specific relocation and fixup support for loadable modules. It applies ELF relocation records for module sections and patches architecture fixup records embedded by m68k assembly/C code.

## Important APIs, Types, and Functions

Under `CONFIG_MODULES`, `apply_relocate()` handles `Elf32_Rel`, `apply_relocate_add()` handles `Elf32_Rela`, and `module_finalize()` calls `module_fixup()`. `module_fixup(struct module *mod, struct m68k_fixup_info *start, struct m68k_fixup_info *end)` handles entries such as `m68k_fixup_memoffset` and `m68k_fixup_vnode_shift` when `CONFIG_MMU` is set.

## Control Flow

For each relocation record, the code computes the target location from the relocated section plus `r_offset`, resolves the symbol through `symindex`, and switches on `ELF32_R_TYPE`. `R_68K_32` adds or assigns the absolute symbol value, while `R_68K_PC32` adds or assigns a PC-relative value subtracting the relocation location. Unknown relocation types log the module name and return `-ENOEXEC`. Finalization walks the module fixup section and patches stored addresses with `m68k_memoffset` or `m68k_virt_to_node_shift`.

## State and Persistence Behavior

Relocations permanently mutate the module's loaded memory image. Fixups write architecture constants into addresses recorded by `.m68k_fixup` producers. No persistent storage is used.

## Dependencies and Integration Points

It depends on generic module loader section preparation, ELF relocation constants, `struct module`, and m68k fixup metadata. `relocate_kernel.S` uses `.m68k_fixup` records for virtual-to-physical adjustments, and modules can use the same mechanism.

## Risks and Edge Cases

Only `R_68K_32` and `R_68K_PC32` are supported. A toolchain or module that emits other relocation types will fail load. Relocation location arithmetic casts to `uint32_t *`, so unaligned targets would be dangerous if emitted. `module_finalize()` assumes fixup range pointers are valid and ordered.

## Test Signals

Load and unload a simple m68k module with absolute and PC-relative references, check `dmesg` for unknown relocation errors, and inspect loaded module memory or symbols to verify fixup values match `m68k_memoffset` and virtual node shift expectations.
