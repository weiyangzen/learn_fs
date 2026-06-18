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
