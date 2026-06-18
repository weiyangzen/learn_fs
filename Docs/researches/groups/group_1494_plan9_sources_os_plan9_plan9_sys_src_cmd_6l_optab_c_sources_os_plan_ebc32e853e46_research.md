# Group Research: group_1494_plan9_sources_os_plan9_plan9_sys_src_cmd_6l_optab_c_sources_os_plan_ebc32e853e46

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/plan9` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6l/optab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6l/optab.c

## Purpose
Defines the AMD64 (`6l`) linker/assembler opcode table used by instruction selection and encoding. It maps Plan 9 abstract assembly opcodes (`A*`) to operand class prototypes, prefix requirements, and raw x86/x86-64 opcode byte sequences.

## Key Contents
- Operand prototype arrays such as `yxorl`, `ymovq`, `yjcond`, `ycall`, `yxmov`, and floating/SSE/MMX prototypes.
- `Optab optab[]`, the central dispatch table from opcode enum to:
  - accepted operand classes,
  - prefix class (`Px`, `Pw`, `Pe`, `Pm`, `Pf2`, etc.),
  - opcode bytes and ModR/M extension fields.
- `Optab* opindex[ALAST+1]`, later populated for fast lookup.

## Important Behavior
- Covers scalar integer, branch, call, return, stack, system, x87, MMX, SSE/SSE2, conditional move, and privileged instructions.
- Contains AMD64-specific variants such as `AMOVQ`, `AADDQ`, `ACALL`, `AJMP`, REX-width operations, and 64-bit save/restore forms.
- Encodes pseudo-ops (`ATEXT`, `ADATA`, `AGLOBL`, `ABYTE`, `ALONG`, `AQUAD`) alongside real machine instructions.
- Operand prototype arrays are tightly coupled to `span.c`’s `oclass()`, `doasm()`, and `Z*` encoding actions.

## Research Notes
This file is declarative but foundational: adding or changing an instruction requires matching enum names, assembler lexer names, operand class coverage, and `span.c` encoder support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6l/optab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6l/pass.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6l/pass.c

## Purpose
Implements major linker passes for AMD64 `6l`: data layout, branch threading, call/branch patching, stack-frame adjustment, import/export metadata, and undefined-symbol handling.

## Key Functions
- `dodata()` lays out `SDATA` and `SBSS`, handles small data packing, alignment, `edata`, and `end`.
- `follow()` / `xfol()` reorder instruction flow, follow branches, invert conditional branches, and insert jumps when needed.
- `relinv()` maps conditional jumps to their inverse.
- `doinit()` resolves data initializers referencing symbols.
- `patch()` resolves calls and branches, builds forward links with `mkfwd()`, and collapses jump chains through `brloop()`.
- `dostkoff()` computes frame/become sizes, inserts stack adjustments, and rewrites `AUTO`/`PARAM` offsets.
- `import()` / `export()` generate dynamic import/export metadata.
- `newdata()` emits linker-side `ADATA` records for export tables.

## Important Behavior
- `follow()` is a layout optimizer: it tries to avoid branches by copying short instruction sequences and reversing conditional jumps.
- `patch()` resolves `ACALL` and `ARET` symbol references, supports `SUNDEF` dynamic references, and diagnoses unresolved or out-of-range branches.
- `dostkoff()` rewrites abstract `AADJSP` stack operations and checks balanced push/pop state around returns.
- `export()` creates `EXPTAB` plus a `.string` data symbol containing sorted exported names and signatures.

## Research Notes
This file bridges symbolic object input and addressable executable layout. It depends on instruction sizes later computed by `span.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6l/pass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6l/span.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/6l/span.c

## Purpose
Performs instruction sizing, address assignment, symbol emission, line table emission, x86-64 instruction encoding, and dynamic relocation table generation for `6l`.

## Key Functions
- `span()` iteratively assigns PCs and resizes branch encodings until stable.
- `xdefine()`, `putsymb()`, `asmsym()`, and `asmlc()` emit linker symbols and line-number tables.
- `oclass()` classifies operands into `Y*` classes used by `optab.c`.
- `asmidx()`, `asmandsz()`, `asmand()`, and `asmando()` encode ModR/M, SIB, displacement, and register addressing.
- `vaddr()`, `put4()`, and `put8()` compute absolute values and generate dynamic relocations when needed.
- `doasm()` interprets `Optab` entries and emits machine bytes for each `Z*` encoding form.
- `asmins()` inserts REX prefixes at the correct byte position.
- `dynreloc()` and `asmdyn()` collect and emit dynamic relocation/import records.

## Important Behavior
- Branch sizing is iterative because short vs long conditional jumps affect downstream PCs.
- `AADJSP` pseudo-instructions are rewritten into `ADD/SUB SP` before sizing.
- Address classification rejects 64-bit-only registers outside 64-bit mode and distinguishes immediates by signed/unsigned width.
- Special `ymovtab` handles segment/control/debug/task descriptor moves and other irregular x86 instructions.
- REX prefix placement is carefully adjusted after legacy prefixes.

## Research Notes
This is the executable encoder. It consumes `optab.c`’s declarative table and produces bytes, relocation records, symbols, and line metadata.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/6l/span.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8a/a.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8a/a.h

## Purpose
Main header for the Plan 9 386 assembler (`8a`). It defines assembler data structures, globals, constants, and prototypes.

## Key Structures
- `Sym`: symbol table entry with type, value, name, macro text, and object symbol slot.
- `Io`: input stack buffer used by file/include/macro processing.
- `Gen`: assembled operand representation, including offset, symbol, type, index, scale, string constant, and floating value.
- `Gen2`: instruction pair of `from` and `to` operands.
- `Hist`: source history entries for object debug/history records.

## Key Globals
Tracks input state (`fi`, `iostack`, `peekc`), symbol table (`hash`), include paths, current `pc`, pass number, output file, line number, macro definitions, and `Biobuf obuf`.

## Important Behavior
- Includes `../8c/8.out.h`, so assembler opcodes and operand codes are shared with the 386 compiler and linker.
- Declares parser, lexer, macro, object emission, and compatibility functions.
- Defines platform compatibility hooks imported from `../cc/compat.c`.

## Research Notes
This header is the contract among `a.y`, `lex.c`, shared compiler definitions, and Plan 9 object output encoding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8a/a.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8a/a.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8a/a.y

## Purpose
Yacc grammar for the 386 assembler syntax accepted by `8a`.

## Key Grammar Areas
- `line` handles labels, blank statements, instructions, and parse errors.
- `inst` handles symbol assignment and instruction classes (`LTYPE0`, `LTYPE1`, `LTYPE2`, `LTYPE3`, `LTYPE4`, `LTYPER`, `LTYPED`, `LTYPET`, etc.).
- `spec1` through `spec8` describe special forms:
  - `DATA`,
  - `TEXT`,
  - `JMP/CALL`,
  - `NOP`,
  - shifts,
  - `MOVW/MOVL` with segment operands,
  - variable operand-count forms,
  - `GLOBL`.
- Operand rules cover registers, immediates, memory, names, branches, scaled index addressing, static symbols, and offsets.
- Expression grammar supports arithmetic, shifts, bitwise operators, unary sign, complement, constants, and assembler variables.

## Important Behavior
- Labels are resolved through a two-pass assembler model; unresolved labels during pass 2 are reported.
- Branch operands may be PC-relative constants or symbolic labels.
- Address forms support Plan 9 syntax such as `name+off(SB)`, `name<>+off(SB)`, `off(REG)`, and scaled indexed addressing.
- `checkscale()` validates index scales of 1, 2, 4, or 8.

## Research Notes
This grammar converts textual Plan 9 assembly into `Gen2` records emitted by `outcode()` in `lex.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8a/a.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8a/l.s -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8a/l.s

## Purpose
386 Plan 9 low-level assembly source defining bootstrap, paging setup, processor register helpers, interrupt entry stubs, floating-point state routines, and small runtime primitives.

## Key Areas
- Memory and machine constants: page size, kernel/user address bases, segment selectors, descriptor flags, PTE bits, and interrupt flag.
- `origin`, `lowcore`, and `mode32bit` bootstrap code:
  - optional real-mode relocation for boot builds,
  - GDT setup,
  - switch to protected mode,
  - BSS clearing,
  - temporary page-table construction,
  - paging enable,
  - jump into `KZERO`.
- Global data symbols: `mach0`, `u`, `m`, `tpt`, `tgdt`, `tgdtptr`.
- I/O primitives: `inb`, `outb`, `inss`, `outss`.
- Register/control helpers: `putidt`, `putgdt`, `putcr3`, `puttr`, `getcr0`, `getcr2`.
- Floating-point routines: `fpoff`, `fpinit`, `fpsave`, `fprestore`, `fpstatus`.
- Interrupt/trap stubs: `intr0` through selected vectors, `intrbad`, shared `intrcommon`/`intrscommon`.
- Scheduler/control primitives: `spllo`, `splhi`, `splx`, `idle`, `gotolabel`, `setlabel`, `touser`, `config`.

## Research Notes
Although located in the `8a` area in this work item, this is kernel-facing assembly using the syntax accepted by `8a`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8a/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8a/lex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8a/lex.c

## Purpose
Main driver, lexical initialization, opcode/register table, and object emission logic for the 386 assembler.

## Key Functions
- `main()` parses flags, supports parallel assembly of multiple files on non-Windows systems, and dispatches `assemble()`.
- `assemble()` establishes output path, include paths, two assembler passes, predefined macros, history output, and final cleanup.
- `cinit()` initializes assembler state, symbol table, null operand, predefined symbols, opcodes, and working directory.
- `checkscale()` validates scaled-index factors.
- `zname()` emits object-file symbol name records.
- `zaddr()` serializes an operand using `T_*` compact address flags.
- `outcode()` emits instruction records and maintains object symbol cache entries.
- `outhist()` emits source path/history records.

## Opcode/Register Table
`itab[]` maps textual names to parser token classes and opcode/register values:
- special registers: `SP`, `SB`, `FP`, `PC`;
- byte/general/floating/segment/control/debug/task registers;
- integer, branch, stack, string, floating, conditional move, and system opcodes.

## Important Behavior
- Uses two passes: pass 1 computes labels/PCs; pass 2 emits object records.
- Object records share opcode/address enums with `8.out.h`.
- Includes shared preprocessor/macro/compatibility bodies from `../cc/lexbody`, `../cc/macbody`, and `../cc/compat`.

## Research Notes
This file is where assembler text names become shared Plan 9 object opcodes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8a/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/8.out.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/8.out.h

## Purpose
Shared 386 object-format opcode and address-definition header used by `8c`, `8a`, and related tools.

## Key Contents
- Object symbol constants: `NSYM`, `NSNAME`.
- Text flags: `NOPROF`, `DUPOK`, `NOSPLIT`.
- `enum as`: all abstract 386 opcodes, including:
  - integer arithmetic/logic,
  - branches,
  - stack/string/system instructions,
  - x87 floating-point operations,
  - conditional moves,
  - compare/exchange,
  - pseudo-ops such as `ADATA`, `AGLOBL`, `AHISTORY`, `ANAME`, `AEND`.
- Operand/address constants:
  - byte/general/floating/segment/control/debug/task registers,
  - `D_NONE`, `D_BRANCH`, `D_EXTERN`, `D_STATIC`, `D_AUTO`, `D_PARAM`, `D_CONST`, `D_FCONST`, `D_SCONST`, `D_ADDR`,
  - `D_INDIR` additive indirect marker.
- Address serialization flags: `T_TYPE`, `T_INDEX`, `T_OFFSET`, `T_FCONST`, `T_SYM`, `T_SCONST`, `T_OFFSET2`, `T_GOTYPE`.
- Register ABI constants: `REGRET`, `FREGRET`, `REGSP`, `REGTMP`.

## Research Notes
This is the central numeric ABI between assembler, compiler backend, object files, and linker. Opcode order must stay synchronized with name tables and encoder tables.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/8.out.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/cgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/cgen.c

## Purpose
Main expression and structure code generator for the Plan 9 386 C compiler backend.

## Key Functions
- `cgen()` emits scalar expression code into an optional destination node.
- `reglcgen()` computes an addressable lvalue through a temporary register.
- `lcgen()` emits address generation for lvalues.
- `bcgen()` and `boolgen()` generate conditional branches and boolean materialization.
- `sugen()` copies or builds aggregate values, including structures, 64-bit values, function returns, and conditional/comma aggregate expressions.

## Important Behavior
- Delegates structures/unions and 64-bit values to `sugen()` and `cgen64()`.
- Handles assignments, compound assignments, arithmetic, shifts, multiplication/division/modulus, calls, indirection, casts, conditionals, comma expressions, bitfields, and pre/post increment/decrement.
- Uses fixed x86 registers where required:
  - `CX` for variable shifts,
  - `AX/DX` for division and some multiplication forms.
- Optimizes constant multiplication/division/modulus through `mulgen()`, `sdiv2()`, `smod2()`, `sdivgen()`, and `udivgen()`.
- Uses x87 stack registers for floating-point operations via `fregnode0` and `fregnode1`.
- Emits block copies with `CLD; REP; MOVSL/MOVSB`.

## Research Notes
This is the core lowering pass from compiler IR nodes to abstract Plan 9 386 assembly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/cgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/cgen64.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/cgen64.c

## Purpose
Implements 64-bit integer (`vlong`) lowering for the 32-bit 386 compiler backend.

## Key Concepts
- Represents 64-bit values as low/high 32-bit register pairs (`OREGPAIR`).
- `hi64v()`, `lo64v()`, `hi64()`, and `lo64()` split constants with endian awareness.
- `loadpair()` and `storepair()` move between memory/scalar nodes and register pairs.
- `biggen()` is a table-driven mini-interpreter for 64-bit operation recipes.
- `cgen64()` handles 64-bit arithmetic, shifts, comparisons, casts, compound assignments, multiply, and increments.
- `testv()` emits boolean tests for 64-bit values.

## Important Behavior
- Table recipes describe how to lower:
  - 64-bit shifts by variable and constant counts,
  - add/subtract with carry/borrow,
  - bitwise operations,
  - comparisons across high/low halves,
  - multiplication through partial products,
  - cast sign/zero extension,
  - pre/post increment/decrement.
- Carefully reserves or evacuates `AX`, `DX`, and `CX` when x86 instructions impose register constraints.
- Supports constant/known-address/hard-address operand classification to choose cheaper code paths.
- `machcap(Z)` enables a path for native 64-bit-style handling tests in this backend.

## Research Notes
This file is a dense table-driven code generator. Correctness depends on preserving low/high half offsets and register-pair ownership across `biggen()` recipes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/cgen64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/div.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/div.c

## Purpose
Generates optimized division and modulus by invariant integer constants for the 386 backend.

## Key Functions
- `multiplier()` computes magic multipliers using the Granlund-Montgomery algorithm.
- `sdiv()` and `udiv()` derive signed/unsigned multiplier and shift parameters.
- `sdivgen()` emits signed division by constant using multiply-high and correction.
- `udivgen()` emits unsigned division by constant, including pre-shift paths.
- `sext()` emits sign extension into a helper register or `DX`.
- `sdiv2()` optimizes signed division by powers of two.
- `smod2()` optimizes signed modulus by powers of two.

## Important Behavior
- Avoids expensive hardware division where constant divisors permit multiply/shift sequences.
- Handles negative signed divisors by negating the final quotient.
- Handles signed modulus correction so C semantics are preserved for negative dividends.
- Cooperates with `cgen.c`, which calls these helpers when it detects constant divisors.

## Research Notes
This is arithmetic-strength reduction for a CPU where division is relatively costly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/div.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/enam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/enam.c

## Purpose
Defines `anames[]`, the printable names for every opcode in `enum as`.

## Key Contents
- String table beginning with `"XXX"`, `"AAA"`, `"AAD"`, etc.
- Covers integer, branch, stack, string, floating-point, pseudo-op, conditional move, and final `"LAST"` names.
- Names correspond by index to `enum as` in `8.out.h`.

## Important Behavior
- Used by formatters, diagnostics, listings, and debug output.
- Must remain synchronized with opcode enum order.
- Includes names for extra post-`AEND` pseudo and extended opcodes such as `DYNT`, `INIT`, `SIGNAME`, `FCOMI`, `CMPXCHG*`, `CMOV*`, and `FCMOV*`.

## Research Notes
This file has no algorithmic logic, but it is critical for human-readable assembly output and diagnostics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/enam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/gc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/gc.h

## Purpose
Main backend header for the Plan 9 386 C compiler.

## Key Definitions
- Machine sizes: `SZ_CHAR`, `SZ_SHORT`, `SZ_INT`, `SZ_LONG`, `SZ_IND`, `SZ_FLOAT`, `SZ_VLONG`, `SZ_DOUBLE`.
- Backend structures:
  - `Adr`: abstract assembly operand.
  - `Prog`: abstract assembly instruction.
  - `Case` / `C1`: switch lowering records.
  - `Var`: optimizable variable descriptor.
  - `Reg`: control-flow/data-flow graph node.
  - `Rgn`: register-allocation live region.
  - `Renv`: register environment.
- Global backend state for programs, registers, variables, flow graph, region allocator, temporaries, string data, safe temporaries, and debug state.

## Important Interfaces
Declares functions from:
- `sgen.c` for statement generation,
- `cgen.c` and `cgen64.c` for expression lowering,
- `txt.c` for instruction emission/register allocation,
- `swt.c` for switches/bitfields/data output,
- `list.c` for formatting,
- `reg.c` and `peep.c` for optimization,
- `div.c` and `mul.c` for arithmetic strength reduction.

## Research Notes
This header is the shared backend contract tying parsing/IR from `cc` to 386-specific code generation and optimization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/gc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/list.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/list.c

## Purpose
Provides formatting functions for compiler backend diagnostics, assembly listings, and debug output.

## Key Functions
- `listinit()` installs custom formatters:
  - `%A` opcode,
  - `%B` bitset,
  - `%P` instruction,
  - `%S` string constant,
  - `%D` operand,
  - `%R` register.
- `Bconv()` prints variable bitsets using symbol names or constant offsets.
- `Pconv()` prints `Prog` instructions, with special formats for `ADATA` and `ATEXT`.
- `Aconv()` prints opcode names from `anames[]`.
- `Dconv()` formats abstract operands, including branches, extern/static/auto/param symbols, constants, addresses, indirection, and indexed addressing.
- `Rconv()` prints register names.
- `Sconv()` escapes fixed-size string constants.

## Important Behavior
- Uses Plan 9 assembly syntax in output, e.g. `name+off(SB)`, `name+off(SP)`, `$const`, and `offset(REG)`.
- `Dconv()` temporarily rewrites `D_ADDR` to print address constants recursively.

## Research Notes
This file is support code for making generated abstract instructions inspectable.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/machcap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/machcap.c

## Purpose
Reports whether the 386 backend has machine-specific support for selected IR operations, especially 64-bit and compound operations.

## Key Function
- `machcap(Node *n)`

## Important Behavior
- `machcap(Z)` returns true as a feature-test path.
- Returns true for:
  - integer and vlong multiplication forms,
  - 64-bit arithmetic/bitwise/shift operations on supported types,
  - casts to/from vlong/non-floating types,
  - conditionals, comma/list/logical/not/dot forms,
  - compound assignments,
  - pre/post increment/decrement,
  - relational operations.
- Returns false for unsupported node/type combinations.

## Research Notes
This is a small capability switch used by common compiler code and the 64-bit lowering path to decide when 386-specific codegen can handle an operation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/machcap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/mul.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/mul.c

## Purpose
Optimizes multiplication by constants for the 386 backend using shifts, adds, subtracts, and scaled addressing where cheaper than `IMUL`.

## Key Functions
- `lowbit()` finds the lowest set bit position.
- `genmuladd()` emits scaled-index address-generation multiplication/addition.
- `mulparam()` selects a multiplication algorithm for a constant.
- `m0()`, `m1()`, and `m2()` map special constants to scale factors.
- `shiftit()` emits efficient shift-left or add-for-times-two.
- `mulgen1()` emits selected optimized multiplication sequence.
- `mulgen()` falls back to `OMUL` when no optimized sequence is chosen.

## Important Behavior
- Caches recent constant multiplication parameters in `multab`.
- Recognizes constants expressible through combinations of shifts and scaled-index LEA forms.
- Handles negative multipliers by negating or subtracting as needed.
- Uses x86 scaled addressing to synthesize multiplication by small factors efficiently.

## Research Notes
This complements `div.c`: both perform arithmetic strength reduction before final instruction selection.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/mul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/peep.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/peep.c

## Purpose
Implements peephole and local copy-propagation optimizations over the backend control-flow graph.

## Key Functions
- `peep()` inserts missing `Reg` nodes for non-data instructions, then repeatedly applies optimizations.
- `needc()` checks whether later code needs carry flags before rewriting add/sub into inc/dec.
- `excise()` turns an instruction into `ANOP`.
- `uniqp()` / `uniqs()` find unique predecessor/successor nodes.
- `regtyp()` identifies general-purpose register operands.
- `subprop()` performs substitution propagation across move chains.
- `copyprop()` and `copy1()` remove redundant register copies when safe.
- `copyu()` classifies whether an instruction uses, sets, read-modify-writes, or ignores an operand.
- `copyas()`, `copyau()`, `copysub()` compare and substitute operands.

## Important Behavior
- Eliminates redundant `MOVL reg,reg` and propagated register copies.
- Converts `ADD/SUB $1` and `$-1` to `INC/DEC` only if carry flags are not needed.
- Simplifies chains of sign/zero extension moves when followed by matching extensions.
- Treats special x86 instructions conservatively because many implicitly use `AX`, `DX`, `CX`, `SI`, or `DI`.

## Research Notes
This optimizer is deliberately instruction-semantics-aware; incorrect `copyu()` classification would create miscompilations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/peep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/reg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/reg.c

## Purpose
Global register optimizer for the Plan 9 386 compiler backend.

## Key Phases in `regopt()`
- Builds `Reg` control-flow nodes for non-data instructions.
- Computes use/set bits for variables and implicit register use.
- Resolves branch targets into CFG edges.
- Computes loop weighting with reverse postorder and approximate dominators.
- Propagates liveness backward with `prop()`.
- Propagates register/variable synchrony forward with `synch()`.
- Identifies profitable live regions with `paint1()`.
- Determines available registers with `paint2()` and `allreg()`.
- Rewrites instructions and inserts loads/stores with `paint3()`.
- Runs `peep()` and recalculates PCs/branch offsets.
- Removes `ANOP`s and recycles analysis nodes.

## Key Helpers
- `mkvar()` maps memory operands to optimizable variable bits.
- `addmove()` inserts variable-register load/store moves.
- `doregbits()`, `RtoB()`, `BtoR()` convert between register numbers and bit masks.
- `loopit()`, `postorder()`, `rpolca()`, `doms()`, `loophead()`, `loopmark()` estimate loop structure.
- `regset()` and `reguse()` query register effects through `copyu()`.

## Important Behavior
- Avoids optimizing externs, params, address-taken variables, constants, and unsafe punning cases.
- Reserves stack pointer and accumulator defaults through `regbits`.
- Accounts for implicit register clobbers from division, string ops, calls, returns, floating status, and shift/string instructions.
- Uses loop depth to weight optimization profitability.

## Research Notes
This is the backend’s global data-flow pass. It rewrites abstract assembly before final object emission.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/reg.c -->