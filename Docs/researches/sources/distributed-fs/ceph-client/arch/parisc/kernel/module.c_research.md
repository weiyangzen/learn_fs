# sources/distributed-fs/ceph-client/arch/parisc/kernel/module.c

## Purpose

`module.c` implements PA-RISC ELF module relocation, per-section PLT stub reservation, GOT and function-descriptor allocation, module unwind registration, alternative patching, ftrace callsite relocation, and function-descriptor dereferencing for loaded modules.

## Important APIs, Types, And Functions

Instruction encoding helpers include `reassemble_14()`, `reassemble_16a()`, `reassemble_17()`, `reassemble_21()`, and `reassemble_22()`. Relocation safety uses `RELOC_REACHABLE()` and `CHECK_RELOC()`.

`struct got_entry` and `struct stub_entry` vary by 32-bit versus 64-bit builds. Section-level metadata is allocated in `module_frob_arch_sections()` and freed in `module_arch_freeing_init()` or `module_finalize()`. `arch_mod_section_prepend()` tells the module loader how many bytes of stubs to reserve before each code section.

64-bit helpers include `get_got()`, `get_fdesc()`, and `dereference_module_function_descriptor()`. `get_stub()` creates 32-bit direct stubs or 64-bit GOT, millicode, and direct branch stubs.

Relocation is performed by the 32-bit or 64-bit implementation of `apply_relocate_add()`. Finalization uses `register_unwind_table()`, `deregister_unwind_table()`, `module_finalize()`, and `module_arch_cleanup()`.

## Control Flow

Before layout, `module_frob_arch_sections()` scans relocation sections, counts GOT entries, function descriptors, and branch stubs, records `.PARISC.unwind`, reserves stubs for target sections, and appends GOT and fdesc storage to `MOD_TEXT`.

During relocation, the code walks each `Elf_Rela`, finds the target location and symbol, computes `dot`, symbol value, and addend, and switches on relocation type. 32-bit relocations handle direct 32-bit values, DIR21L/DIR14R, DP-relative values, PCREL17F/22F with out-of-range stubs, PCREL32, SEGREL32, and SECREL32. 64-bit relocations handle LTOFF GOT offsets, PCREL22F with local direct reach checks or external stubs, PCREL32/64, DIR64, SEGREL32/SECREL32, and FPTR64 function descriptors.

`get_stub()` lazily initializes each section's stub area immediately before the section, aligns it, consumes one reserved entry, writes instruction sequences, and returns the stub address. `get_got()` and `get_fdesc()` deduplicate entries and enforce maximum counts.

`module_finalize()` registers unwind data, compacts allocated symbol tables by removing `.L` local labels, checks GOT overflow, applies alternatives, and relocates ftrace callsite sections when dynamic ftrace is enabled. Cleanup deregisters unwind data.

## State And Persistence Behavior

The file mutates loaded module memory: code/data relocation targets, per-section prepended stub areas, GOT entries, function descriptors, unwind registration, symbol table contents, and alternative/ftrace patch sites. State persists for the lifetime of the loaded module and is cleaned during module unload.

## Dependencies And Integration Points

It depends on generic module loader layout callbacks, ELF relocation definitions for PA-RISC, unwind tables, alternatives, dynamic ftrace, function descriptor semantics, module memory classes, and architecture section metadata stored in `mod->arch`.

## Risks

Relocation encoding is high risk because PA-RISC immediate fields are non-contiguous and branch offsets are PC-relative with instruction-queue semantics. Stub count estimation must match actual stub consumption or `BUG_ON()` fires. GOT has a hard `MAX_GOTS` limit. The SEGREL32 behavior is intentionally ABI-nonstandard for unwind entries, so changing it can break unwinding. Symbol-table compaction mutates loaded metadata and must preserve references expected by generic module code.

## Test Signals

Signals include loading modules with large text sections and far calls, XFS/IPV6-style modules that require per-section stubs, 64-bit modules with external function descriptors, unwind backtraces through module code, alternatives applying inside modules, dynamic ftrace over module callsites, and clean unload without stale unwind registrations.
