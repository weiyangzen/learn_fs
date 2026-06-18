# sources/distributed-fs/ceph-client/arch/alpha/kernel/module.c

**Purpose:** Implements Alpha-specific kernel module section preparation and ELF64 relocation application. It sizes and allocates module GOT entries for `R_ALPHA_LITERAL`, records GOT offsets in relocation metadata, and applies Alpha relocation types at load time.

**Important APIs/types/functions:** Exposes `module_frob_arch_sections()` and `apply_relocate_add()`. Internal type `struct got_entry` tracks per-symbol/addend GOT allocation. Important relocation cases include `R_ALPHA_REFLONG`, `REFQUAD`, `GPREL32`, `LITERAL`, `GPDISP`, `BRSGP`, `BRADDR`, `SREL32`, `SREL64`, `GPRELHIGH`, `GPRELLOW`, and `GPREL16`.

**Control flow:** `module_frob_arch_sections()` locates `.symtab` and `.got`, allocates one `got_entry` chain head per symbol, resets `.got` to an 8-byte-aligned `SHT_NOBITS` area, scans all `SHT_RELA` sections, and for each `R_ALPHA_LITERAL` assigns/deduplicates a GOT slot by symbol plus addend. It stores the GOT offset in high bits of `r_info` for later use. `apply_relocate_add()` computes `got` and GP (`got + 0x8000`), iterates relocations for a target section, computes symbol value plus addend, patches the target instruction/data, writes GOT entries for literals, and reports overflow/unknown relocation errors.

**State and persistence behavior:** Mutates module ELF section headers before allocation, relocation records in memory, the module GOT, and loaded text/data. Temporary GOT chains are allocated and freed during section frobbing. No persistent state.

**Dependencies and integration points:** Hooks into the Linux module loader. Depends on Alpha ELF relocation definitions, module `arch.gotsecindex`, and the Alpha GP/GOT code model.

**Risks:** Co-opting high bits of `r_info` for GOT offsets depends on relocation type width assumptions. Overflow checks are critical for branch, GP-relative, and literal relocations. Misaligned `REFQUAD` handling intentionally writes as two 32-bit halves because `BUG()` can produce misalignment.

**Test signals:** Load modules containing literals with same/different addends, GP-relative data, long branches, local `BRSGP`, section-symbol relocations, and intentionally overflowing relocations. Confirm `.got` size/alignment, GP value, relocation patch bytes, and clear errors for unknown/overflow cases.
