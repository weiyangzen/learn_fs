<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/gen-hyprel.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/gen-hyprel.c

## Purpose
`gen-hyprel.c` is a host build tool that scans the relocatable nVHE ELF object and emits assembly for `.hyp.reloc`, allowing the final kernel link to record absolute kernel virtual addresses embedded in hyp sections so they can be converted to hyp virtual addresses at runtime.

## Important APIs, Types, and Functions
Global `elf` stores the mmaped ELF, section table, and string table. `init_elf()` opens and validates an ELF64 AArch64 relocatable object with the configured endianness. `emit_prologue()` and `emit_epilogue()` wrap output in `.hyp.reloc`. `emit_rela_section()` filters relocations whose target section begins with `.hyp`, accepts known PC-relative and data relocation types, and calls `emit_rela_abs64()` for `R_AARCH64_ABS64`. `emit_rela_abs64()` emits one `.word` plus a `R_AARCH64_PREL32` relocation against `__hyp_section_<section> + offset`. `emit_all_relocs()` rejects `SHT_REL` and processes all `SHT_RELA` sections.

## Control Flow, State, and Persistence
The program is a one-shot build-time transformer: `main()` validates one input path, maps it read-only, emits fixed assembly to stdout, and exits. It persists no repository state itself; generated assembly becomes part of the vmlinux link. Its only mutable state is the process-local `elf` descriptor and the static `reloc_offset` used to place generated PREL32 relocations.

## Dependencies and Integration Points
It integrates the nVHE partial link, `hyp.lds.S` section symbols, the vmlinux linker, and runtime hyp relocation code that consumes `.hyp.reloc`. It depends on `<generated/autoconf.h>` for endianness and carries local definitions for AArch64 relocation constants missing from older host toolchains.

## Risks and Test Signals
Risks include rejecting newly emitted relocation types after compiler/toolchain upgrades, relying on section-name prefixes, lack of deep bounds validation beyond assertions, and only tracking ABS64 absolute addresses. Test signals are successful builds across little/big endian configurations, deliberate object files with ABS64/ABS32/PC-relative relocations, failure on SHT_REL or unexpected relocation types, and link-time presence of `.hyp.reloc` entries for hyp absolute data references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/gen-hyprel.c -->
