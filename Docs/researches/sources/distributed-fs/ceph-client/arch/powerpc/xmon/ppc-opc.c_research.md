# Research: sources/distributed-fs/ceph-client/arch/powerpc/xmon/ppc-opc.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000810`: lines 1-5814, `Docs/researches/chunks/subset-b-000810_research.md`
- `subset-b-000811`: lines 5815-7276, `Docs/researches/chunks/subset-b-000811_research.md`

## Chunk Research

### subset-b-000810: lines 1-5814

# sources/distributed-fs/ceph-client/arch/powerpc/xmon/ppc-opc.c lines 1-5814

## Scope

This chunk covers the beginning and large middle of the PowerPC xmon opcode database. It includes:

- File setup, local prototypes, and the complete `powerpc_operands[]` table.
- All local operand insertion/extraction helpers used by that table.
- Opcode-construction macros for PowerPC, POWER, BookE, embedded, VLE-style, Altivec, VSX, SPE, paired-single, and special-purpose instruction forms.
- Short alias macros for CPU/dialect flags and branch/trap condition encodings.
- The start of `powerpc_opcodes[]`, from major opcode 0 through part of major opcode 31, ending at the `subfo` row on line 5814.

The source is copied from the GNU binutils/GDB opcode model into the kernel xmon debugger. In this tree it is support code for xmon disassembly, not Ceph distributed-filesystem logic directly.

## Purpose

`ppc-opc.c` provides the declarative instruction metadata that `arch/powerpc/xmon/ppc-dis.c` uses to disassemble raw PowerPC instructions inside the kernel debugger. The two central exported data sets in this chunk are `powerpc_operands[]` and the covered portion of `powerpc_opcodes[]`.

The operand table defines how each operand index maps to instruction bits, how the disassembler should print it, and when special validation is needed. The opcode table maps instruction names to opcodes, masks, supported CPU dialect flags, deprecated/anti-dialect flags, and operand-index lists. `ppc-dis.c` linearly scans `powerpc_opcodes`, checks `(insn & mask) == opcode`, filters by dialect, invokes operand extractors for validation, and then prints operands according to the flags in `powerpc_operands`.

## Important APIs, Types, And Functions

The public data in this chunk is `const struct powerpc_operand powerpc_operands[]`, `const unsigned int num_powerpc_operands`, and the first 2,780 lines of `const struct powerpc_opcode powerpc_opcodes[]`.

`struct powerpc_operand` and `struct powerpc_opcode` are declared in `ppc.h`. Operand entries carry `bitm`, `shift`, optional `insert`, optional `extract`, and syntax/semantic flags such as `PPC_OPERAND_SIGNED`, `PPC_OPERAND_FAKE`, `PPC_OPERAND_GPR`, `PPC_OPERAND_RELATIVE`, `PPC_OPERAND_OPTIONAL`, `PPC_OPERAND_VR`, and `PPC_OPERAND_VSR`. Opcode entries carry `name`, `opcode`, `mask`, `flags`, `deprecated`, and an up-to-8-byte operand-index list terminated by zero.

`powerpc_operands[]` defines named operand indexes with local `#define`s, not an enum. Important families include branch fields (`BO`, `BOE`, `BI`, `BD`, `BDA`, `BDM`, `BDP`, `LI`, `LIA`), condition-register fields (`BA`, `BB`, `BT`, `BF`, `BFA`, `CR`, `CRD32`), general registers (`RA`, `RA0`, `RAL`, `RAM`, `RAS`, `RB`, `RBS`, `RS`, `RT`, `RX`, `RY`), floating-point registers (`FRA`, `FRB`, `FRC`, `FRS`/`FRT`), vector and VSX registers (`VA`, `VB`, `VC`, `VD`/`VS`, `XS6`/`XT6`, `XA6`, `XB6`, `XC6`), immediates and displacements (`D`, `DS`, `DQ`, `SI`, `UI`, `IMM20`, `DXD`, `SCI8`, VLE split immediates), special registers (`SPR`, `SPRG`, `TBR`, `PMR`, `TMR`), and embedded/APU operands (`FSL`, `FCRT`, `URT`, `URA`, `URB`, `URC`).

The custom helpers handle cases where `bitm`/`shift` alone is insufficient:

- `insert_bat`, `extract_bat`, `insert_bba`, `extract_bba`, `insert_rbs`, `extract_rbs`, and `insert_xb6s`, `extract_xb6s` implement fake operands for extended mnemonics where two fields must match, such as `crnot`, `crclr`, `mr`, and `xvmov*`.
- `insert_bdm`, `extract_bdm`, `insert_bdp`, `extract_bdp`, `insert_bo`, `extract_bo`, `insert_boe`, and the `valid_bo_*` helpers encode branch prediction hints and reject invalid BO encodings. They distinguish pre-ISA-v2 y-bit semantics from ISA-v2-and-newer `a/t` hint bits.
- `insert_fxm` and `extract_fxm` enforce `mfcr`/`mtcrf` mask rules, including the Power4 single-field form and the sentinel `-1` used by optional `mfcr`.
- `insert_mbe` and `extract_mbe` translate a rotate mask operand into MB/ME fields. Extraction intentionally marks such operands invalid so normal disassembly prefers canonical MB/ME forms rather than this assembler-only shorthand.
- `insert_spr`, `extract_spr`, `insert_sprg`, `extract_sprg`, `insert_tbr`, and `extract_tbr` handle flipped XFX SPR/TBR encodings and dialect-dependent SPRG ranges.
- `insert_li20`, `extract_li20`, `insert_dcmxs`, `extract_dcmxs`, `insert_dxd`, `extract_dxd`, VSX split-register helpers, and VLE split-immediate helpers pack fields that are scattered across non-contiguous instruction bits.
- Register validity helpers such as `insert_ral`, `insert_ram`, `insert_raq`, `insert_ras`, `insert_rbx`, and `insert_nbi` enforce architectural hazards like update-address register restrictions or load-range overlap.

The macro section defines compact constructors and masks used by opcode rows: `OP`, `OPTO`, `OPL`, `B`, `BD8`, `BD15`, `BD24`, `X`, `XL`, `XO`, `A`, `M`, `MD`, `MDS`, `VX`, `VXA`, `VXR`, `XX2`, `XX3`, `XX4`, `XSPR`, `XFXM`, `DSO`, `DQX`, `SCI8`, `SD4`, `SE_R`, `SE_RR`, and many mask variants with fixed operands. The flag aliases (`PPC`, `PPCCOM`, `POWER4`, `PPC64`, `PPCVEC`, `PPCVSX3`, `PPCSPE`, `BOOKE`, `E500MC`, `PPCVLE`, etc.) keep opcode rows readable while preserving the `ppc_cpu_t` bitmask contract from `ppc.h`.

## Control Flow

This file is mostly static data. Runtime control flow comes from consumers in `ppc-dis.c`:

1. `print_insn_powerpc()` builds a dialect bitmask from kernel configuration and CPU features such as 64-bit mode, TM, Altivec, and VSX.
2. `lookup_powerpc()` scans `powerpc_opcodes[]` in table order.
3. Each candidate row must match its opcode/mask and must be supported by the current dialect while not matching its deprecated mask.
4. The lookup then calls any operand-specific `extract` functions. If any sets `invalid`, the row is skipped.
5. The first valid row wins, so table order is semantically significant. More-specific extended mnemonics must precede more-general base instructions.
6. Operand printing uses the operand flags: registers get `r`, `f`, `v`, or `vs` prefixes; relative and absolute branches call `print_address`; optional operands are suppressed when they match default values; fake operands are not printed.

Inside this chunk, control flow in helper routines is limited to validation and bit packing. Branch helpers choose between old y-bit and ISA-v2 `a/t` encodings based on `dialect`. SPRG helpers reject unavailable SPRG4-7 forms unless the dialect supports them. `insert_sci8()` classifies a signed byte immediate shifted into one of four byte lanes and records sign-fill state; `extract_sci8()` reverses that representation.

The covered opcode-table range starts with trap immediates and major opcode 4 paired-single/vector/SPE/APU instructions, proceeds through immediate arithmetic and all covered conditional/unconditional branch families, then enters the large major opcode 31 table. By line 5814 it has covered many integer, memory, cache, synchronization, SPR/DCR move, vector/VSX, BookE, POWER, 40x/440/476, e500/e6500, and POWER7/8/9 rows, but the `powerpc_opcodes[]` array continues beyond this chunk.

## State And Persistence Behavior

There is no durable persistence and no mutable runtime state in this chunk. The tables are `const` and intended to live in read-only kernel memory when `CONFIG_XMON_DISASSEMBLY` includes `ppc-opc.o`.

The only state-like behavior is encoded in table order and in compile-time constants. Operand index numbers are persistent ABI within this file because opcode rows store operand indexes as bytes. Optional-default sentinel entries immediately following operands such as `FXM4`, `TBR`, and `SXL` are part of that index contract and must remain adjacent to the optional operand entry. CPU dialect masks in opcode rows determine whether xmon prints an instruction for the running CPU feature set.

Insertion functions are present because the file derives from a shared assembler/disassembler opcode table, but in this kernel xmon path only extraction and printing are used. Even so, insert-side warnings document legality rules and mirror the validation expected by extraction-side code.

## Dependencies And Integration Points

Direct includes are Linux kernel headers plus xmon-local headers: `linux/stddef.h`, `linux/kernel.h`, `linux/bug.h`, `nonstdio.h`, and `ppc.h`. `ARRAY_SIZE` comes from the kernel headers. `ppc.h` supplies the `ppc_cpu_t` typedef, opcode and operand structs, dialect bit definitions, operand flag bits, `PPC_OP()`, and `PPC_OPSHIFT_INV`.

The build integration is `arch/powerpc/xmon/Makefile`, where `ppc-dis.o` and `ppc-opc.o` are included under `CONFIG_XMON_DISASSEMBLY`. The runtime integration is `xmon.c`, whose instruction dump path calls `generic_inst_dump(..., print_insn_powerpc)`. `ppc-dis.c` is the immediate consumer of `powerpc_operands`, `powerpc_opcodes`, and `powerpc_num_opcodes`.

The tables are also integrated with kernel CPU feature detection indirectly. `print_insn_powerpc()` combines base `PPC_OPCODE_PPC | PPC_OPCODE_COMMON` with `PPC_OPCODE_64`, POWER4-POWER9, HTM, Altivec, and VSX flags depending on the running kernel and CPU. Rows in this chunk rely on those flags to distinguish generic PPC/POWER names, 64-bit-only names, embedded variants, deprecated forms, and newer ISA additions.

## Risks And Edge Cases

The largest risk is table ordering. The disassembler uses first match wins, so moving a generic row before a specific extended mnemonic changes visible disassembly without changing masks or code. This is especially sensitive for branch aliases, trap aliases, `mr` versus `or`, `crnot`/`crclr`/`crset` versus CR logical operations, special SPR names versus generic `mfspr`/`mtspr`, and overlapping SPE/vector/APU encodings under major opcode 4.

Operand indexes are fragile because they are generated by chained `#define`s and interspersed sentinel entries. Inserting, removing, or reordering an operand definition without updating all dependent macros can silently change the meaning of every opcode row that follows.

Mask precision is critical. A mask that omits a fixed field can cause an extended mnemonic to match too broadly; a mask that includes an operand field can prevent a valid instruction from matching. The many `*_MASK` variants intentionally include or clear specific fields for optional operands, fixed registers, Rc bits, BO hint bits, and split VSX/VLE encodings.

Dialect and deprecated flags are another high-risk area. A row can be syntactically valid but should be hidden for a specific CPU family or xmon dialect. Examples in this chunk include VLE exclusions, BookE/e500/Titan differences, Power4 branch-hint handling, POWER versus PowerPC mnemonic aliases, and POWER9 additions such as `addpcis`, `stop`, `cnttzw`, and `cmpeqb`.

The helper functions often set `*invalid` rather than returning an impossible value. `lookup_powerpc()` depends on this side channel to reject rows with invalid fake operands, invalid BO encodings, invalid SPRG/TBR values, and assembler-only negative/immediate forms. Any caller that extracts operands without initializing or checking `invalid` can produce misleading output.

This chunk ends mid-table at line 5814, immediately before additional opcode 31 rows. Any final per-file analysis must merge with the continuation chunks before drawing complete conclusions about `powerpc_opcodes[]`, `powerpc_num_opcodes`, `vle_opcodes[]`, or `vle_num_opcodes`.

## Test Signals

High-signal validation should focus on disassembly behavior rather than runtime filesystem behavior:

- Build a PowerPC kernel configuration with `CONFIG_XMON_DISASSEMBLY=y` and ensure `ppc-opc.o` and `ppc-dis.o` compile without duplicate macro or table-initializer regressions.
- Run xmon instruction dumps over known machine-code samples for the covered major opcodes and compare the printed mnemonics/operands to binutils `objdump` for the same ISA level.
- Exercise first-match aliases: `mr`/`or`, `crnot`/`crnor`, `crclr`/`crxor`, `crset`/`creqv`, branch-to-LR/CTR/TAR aliases, trap aliases, and named SPR rows before generic `mfspr`/`mtspr`.
- Test branch displacement printing and prediction suffixes for pre-ISA-v2 and ISA-v2 dialects, including `+`, `-`, absolute, link, LR, CTR, and CR-field forms.
- Validate optional operands and default suppression for comparison fields, `mftb`/`mftbu`, `rfebb`, sync/wait-like operands, and rows that use `PPC_OPERAND_OPTIONAL_VALUE`.
- Feed invalid encodings for fake operands, BO fields, SPRG/TBR fields, update-form register conflicts, `lswi` register ranges, split VSX registers, and VLE immediates, and verify that lookup skips the extended row or falls back to a correct generic row.
- Check dialect filtering by running or simulating PPC32, PPC64, Altivec, VSX, HTM, POWER7/8/9, BookE/e500, and embedded 40x/440/476 flag combinations.
- Include endianness-independent raw instruction tests because `ppc-opc.c` receives already fetched instruction words; byte-order handling belongs to the caller, but opcode and operand extraction should remain word-level correct.

### subset-b-000811: lines 5815-7276

# sources/distributed-fs/ceph-client/arch/powerpc/xmon/ppc-opc.c lines 5815-7276

## Scope

This chunk covers the tail of `powerpc_opcodes[]`, the complete `vle_opcodes[]` table, and the complete `powerpc_macros[]` table in the PowerPC xmon opcode database. The source is imported from the binutils/GDB PowerPC opcode tables and adapted for the kernel xmon disassembler.

The range is almost entirely declarative constant data. Its behavior comes from how `ppc-dis.c` scans these tables and how operand IDs index `powerpc_operands[]`.

## Purpose

`powerpc_opcodes[]` maps 32-bit PowerPC instruction words to printable mnemonics and operand layouts. This chunk begins in major opcode 31 extended-form entries, continues through load/store, floating-point, decimal floating-point, VSX, transactional memory, cache/TLB, and Power9 entries, then closes the main table with `powerpc_num_opcodes`.

`vle_opcodes[]` separately describes VLE 16-bit and 32-bit instruction encodings such as `se_*` and `e_*` forms. It has the same `struct powerpc_opcode` shape as the main table, but xmon's current `print_insn_powerpc()` path in `ppc-dis.c` does not call a VLE lookup routine. The main table also marks many standard opcodes as deprecated for `PPCVLE`, which prevents standard PowerPC decoding when VLE is the selected dialect.

`powerpc_macros[]` defines assembler-only macro expansions for rotate, shift, insert, extract, and VLE rotate-mask aliases. In this kernel xmon context there is no assembler path using these macros, but the table remains exported through `ppc.h`.

## Important APIs, Types, And Data

`struct powerpc_opcode` in `ppc.h` is the core contract. Each row has:

- `name`: mnemonic printed by the disassembler.
- `opcode`: fixed instruction bits, usually produced by encoding macros such as `X()`, `XRC()`, `XO()`, `A()`, `XX2()`, `XX3()`, `OP()`, `DSO()`, and VLE-specific forms such as `SE_RR()`, `SCI8()`, `EBD15BI()`, and `BD8()`.
- `mask`: fixed-bit mask used by lookup; `(insn & mask) == opcode` must hold.
- `flags`: CPU/ISA feature bits required for the mnemonic.
- `deprecated`: CPU/ISA feature bits for which the mnemonic must not match.
- `operands[8]`: operand table indexes, terminated by zero, into `powerpc_operands[]`.

The main table entries in this chunk define high-density opcode families:

- Opcode 31 extended forms: arithmetic overflow aliases (`subo`, `addeo`, `mulldo`, `divwo`), shifts/sign extension (`sraw`, `srad`, `extsb`, `extsh`, `extsw`), byte-reversed loads/stores (`lhbrx`, `stwbrx`, `stdbrx`), cache/TLB operations (`tlbsync`, `tlbivax`, `tlbsx`, `tlbre`, `tlbwe`, `icbi`, `dcbz`, `dcbzl`), synchronization (`sync`, `hwsync`, `lwsync`, `ptesync`, `eieio`, `mbar`), HTM (`tbegin.`, `tend.`, `tabort*`, `treclaim.`, `trechkpt.`), and Power9 additions (`darn`, `copy`, `paste.`, `msgsync`, `modsd`, `modsw`, `slbiag`, `rmieg`).
- Vector, VSX, and Cell-specific entries: `lvtlx`, `stvepx*`, `lxsdx`, `stxsdx`, `lxvw4x`, `stxvw4x`, `lxvx`, `stxvx`, `xx*`, `xs*`, `xv*`, Cell `cct*` and `db*cyc` entries.
- Major opcodes 32-63: base integer loads/stores, floating-point loads/stores, decimal floating-point (`dadd`, `dqua`, `dctfix`, `denbcd`, and quad variants), classic floating point (`fadd`, `fmul`, `fdiv`, `fcmp*`, `mtfs*`), VSX scalar/vector arithmetic and conversion, and quad-precision VSX3 operations.

The VLE table defines a compact instruction namespace:

- 16-bit `se_*` instructions for simple control transfer, register moves, arithmetic, logical operations, immediate operations, load/store, and short conditional/unconditional branches.
- 32-bit `e_*` instructions for compare/immediate arithmetic, update-form loads/stores, multi-register moves, branch forms, rotate/mask instructions, CR logical operations, and `mtmas1`.
- `vle_num_opcodes` records the `ARRAY_SIZE(vle_opcodes)` count.

`struct powerpc_macro` rows contain `name`, operand count, feature flags, and a format string that expands to a real instruction. This chunk includes 64-bit macros such as `extldi`, `extrdi`, `insrdi`, `rotrdi`, `sldi`, `srdi`; 32-bit macros such as `extlwi`, `extrwi`, `inslwi`, `insrwi`, `rotrwi`, `slwi`, `srwi`, `clrrwi`; POWER aliases `sli`/`sri`; and VLE `e_*` rotate/mask macros.

## Control Flow And Lookup Behavior

The tables do not execute by themselves. `print_insn_powerpc()` builds a runtime `dialect` mask from the configured kernel architecture and CPU feature probes, then calls `lookup_powerpc(insn, dialect)`.

`lookup_powerpc()` linearly scans `powerpc_opcodes[]` from the start to `powerpc_num_opcodes`. A row matches only if the masked opcode bits match and the dialect includes at least one required `flags` bit while excluding all `deprecated` bits. For matching rows, any operand with a custom extractor is asked to validate the instruction. The first valid row wins.

That first-match rule is a major behavior constraint. This chunk contains many aliases and overlapping encodings: for example, PowerPC and POWER mnemonic variants, optional-operand forms, POWER7/POWER9-specific forms placed before older generic forms, `lxvd2x` versus `lxvx`, `stxvd2x` versus `stxvx`, `eieio` versus `mbar`, and fixed no-operand forms beside more general forms. Reordering rows can change disassembly output even when the encoded instruction bits are unchanged.

When a row is selected, `print_insn_powerpc()` prints `opcode->name` and walks its operand IDs. Each operand is extracted using `powerpc_operands[]`; flags decide whether the value prints as `rN`, `fN`, `vN`, `vsN`, a CR field, an address, an immediate, or parenthesized load/store syntax. Fake and optional operands can suppress or validate output without printing.

The VLE table has matching data and count definitions, but this xmon disassembler path does not currently select `vle_opcodes[]`. The data is available to consumers that implement VLE lookup, but no such consumer appears in the local `xmon` C files.

## State And Persistence

All data in this chunk is `const` static program data. There is no mutable runtime state, allocation, locking, I/O, or persistence. The only derived state is compile-time `ARRAY_SIZE()` values stored in `powerpc_num_opcodes`, `vle_num_opcodes`, and `powerpc_num_macros`.

Operational state comes from consumers:

- `dialect` in `print_insn_powerpc()` reflects compile-time `CONFIG_PPC64` and runtime CPU features such as transactional memory, Altivec, and VSX.
- `memaddr` affects relative/absolute address printing for branch operands.
- Operand extractors can mark a candidate invalid, causing lookup to continue to a later table row.

## Dependencies And Integration Points

This chunk depends on:

- Encoding and mask macros defined earlier in `ppc-opc.c`.
- Operand ID macros and `powerpc_operands[]` entries defined earlier in `ppc-opc.c`.
- CPU feature flag definitions in `ppc.h`, with short aliases such as `PPC`, `PPCCOM`, `PPC64`, `POWER9`, `PPCVSX3`, `PPCVLE`, `PPCHTM`, `BOOKE`, and `E500MC` defined just before the opcode table.
- `ARRAY_SIZE()` from Linux headers.

The direct integration point is `ppc-dis.c`. xmon uses the opcode table to decode instructions while debugging a running kernel. The disassembler is presentation-oriented: it does not emulate instruction behavior, change CPU state, or validate memory effects.

The macro table is integrated only through declarations in `ppc.h`. The local xmon sources do not use `powerpc_macros[]`, so changes to it have little kernel runtime effect unless another consumer is added.

## Risks And Edge Cases

The primary risk is table correctness. A wrong `mask`, `opcode`, feature flag, deprecation flag, or operand list can silently produce the wrong mnemonic or operand rendering in xmon.

Ordering is fragile because lookup returns the first valid match. More specific encodings must remain before generic encodings, and preferred aliases must remain before less preferred aliases. Duplicate mnemonic names with different flags or masks are intentional.

Feature gating can hide or expose instructions unexpectedly. In this kernel path, the dialect includes base PowerPC/common bits, broad 64-bit architecture generations when `CONFIG_PPC64` is enabled, and selected runtime features for TM, Altivec, and VSX. Embedded, BookE, VLE, and many special-purpose feature flags are not dynamically added here unless represented by the fixed dialect, so some table entries may be inert in typical xmon builds.

VLE support is incomplete from the visible consumer side. The table exists and has counts, but `print_insn_powerpc()` currently initializes `insn_is_short` to false and never consults `vle_opcodes[]`. Treat VLE rows as imported opcode metadata rather than active xmon decode coverage unless another path is introduced.

The macro table is assembler-facing data retained in a disassembler-oriented kernel copy. It can drift from active needs without immediate test failures.

## Test Signals

Useful validation signals are:

- Build coverage for `arch/powerpc/xmon/ppc-opc.c`, which catches malformed initializers, missing operand IDs, bad macro references, and count definitions.
- Disassembler golden tests or manual xmon checks for representative encodings from this chunk: sync/cache/TLB operations, `darn`, HTM mnemonics, byte-reversed loads/stores, VSX/VSX3 instructions, decimal floating-point, and classic floating-point forms.
- Alias precedence checks where multiple rows can match the same fixed bits, such as `sync` variants, `eieio`/`mbar`, POWER versus PowerPC mnemonic aliases, and newer VSX names versus older names.
- CPU feature matrix checks for `CONFIG_PPC64`, TM, Altivec, and VSX to ensure expected entries become visible and deprecated entries stay hidden.
- Negative decode tests for encodings whose operand extractor should mark a candidate invalid, forcing lookup to continue.
