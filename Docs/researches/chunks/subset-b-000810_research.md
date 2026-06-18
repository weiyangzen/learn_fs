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
