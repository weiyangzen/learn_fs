# Group Research: group_32_9front_sources_os_plan9_9front_sys_src_cmd_2l_pass_c_sources_os_plan9_de42f163838c

Scope: `Docs/research_subset_a.md`, specifically `sources/os/plan9/9front`. I read all 34 listed source files completely.

This group covers Plan 9/9front architecture tools around the old toolchain: the `2l` linker layout/span pass, ARM assembler `5a`, ARM C compiler backend `5c`, ARM user-mode emulator `5e`, and ARM interpreter/debugger `5i`.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2l/pass.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2l/pass.c

This file implements major post-parse linker passes for `2l`: data/BSS layout, branch resolution and code following, stack-offset repair, numeric parsing, and undefined-symbol reporting.

Key routines:
- `dodata()` validates data initializers, packs small data symbols first, lays out remaining data, optionally pads/shuffles BSS under debug `j`, then assigns BSS offsets and defines `bdata`, `edata`, and `end`.
- `brchain()` follows chains of unconditional `ABRA` branches up to a fixed depth.
- `follow()` builds a new instruction order by calling `xfol(textp)`, initializes `BCASE` data symbols, and seeds per-instruction `stkoff`.
- `xfol()` performs branch-following layout, marks reachable code, copies short instruction runs to avoid branches, inverts conditional branches where useful, and inserts synthetic `ABRA` nodes.
- `relinv()` maps branch opcodes to their inverse condition, including floating branch conditions.
- `patch()` builds forward links, resolves `ABSR`/`ARTS` symbol references, maps `D_BRANCH` offsets to target `Prog` nodes, and collapses branch loops with `brloop()`.
- `mkfwd()` creates logarithmic-ish forward skip links for faster PC-to-`Prog` lookup.
- `dostkoff()` tracks logical stack offsets, inserts `AADJSP` instructions at function entry and control-flow joins, rewrites `D_AUTO`/`D_PARAM` offsets, and repairs returns with outstanding stack adjustment.
- `atolwhex()` parses signed decimal, octal, and hex constants.
- `undef()` emits diagnostics for unresolved `SXREF` symbols.

Dependencies and interactions:
- Uses global linker state from `l.h`: symbol hash table, `datap`, `textp`, `firstp`, `lastp`, `optab`, debug flags, and address constants.
- Feeds `span.c`: branch targets, instruction order, stack offsets, and symbol data layout are prerequisites for instruction sizing and output.

Research relevance:
- This is core linker control-flow and data-layout machinery. Changes here affect binary layout, stack metadata, branch target validity, and symbol addresses.

Risk notes:
- `xfol()` rewrites control flow destructively; branch inversion and instruction copying depend on exact opcode semantics.
- `dostkoff()` assumes stack effects from `optab`; incorrect `srcsp`/`dstsp` values propagate into bad auto/param addresses.
- `patch()` uses symbol `exit` as fallback for undefined calls/returns, so diagnostics may still leave a patched branch target.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2l/pass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2l/span.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2l/span.c

This file computes final instruction sizes and PCs for `2l`, defines key linker symbols, and emits symbol, stack-pointer, and line-number tables.

Key routines:
- `span()` converts pseudo `AADJSP` instructions into real stack-pointer adjustments, iteratively sizes instructions and branches until `textsize` stabilizes, aligns data start with `INITRND`, defines `etext` and `a6base`, then writes final text symbol PCs.
- `xdefine()` defines a linker symbol only when undefined or suitable for STEXT zero replacement.
- `andsize()` computes extra bytes required by an addressing mode, including indexed modes, text/static/extern references, stack/autos/params, constants, FP constants, special registers, and long displacements.
- `putsymb()` writes one symbol-table entry, with special handling for file symbols encoded as `Z`/`z`.
- `asmsym()` emits data, BSS, file, text, auto, and param symbols in Plan 9 symbol-table format.
- `asmsp()` encodes stack-pointer delta tables in compact bytecode form.
- `asmlc()` encodes line-number delta tables similarly.

Dependencies and interactions:
- Consumes `firstp`, `textp`, `optab`, `mmsize`, `simple`, and layout constants such as `INITTEXT`, `INITDAT`, `A6OFFSET`, and `INITRND`.
- Follows work done by `pass.c`: branch targets and `stkoff` are expected to be established before symbol/debug table emission.

Research relevance:
- This is the final sizing and debug-metadata pass for `2l`. It determines final PCs, branch encodings, text/data split, and symbol records.

Risk notes:
- Branch-size iteration has a hard loop limit of 60; size oscillations or bad branch marks abort the link.
- `andsize()` is architecture-encoding sensitive; small mistakes can desynchronize PC assignment from emitted code.
- Stack and line tables assume a minimum instruction location counter quantum of 2 bytes.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2l/span.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5a/a.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5a/a.h

This header defines shared state and interfaces for the ARM assembler `5a`.

Key contents:
- Includes Plan 9 user, libc, bio, ARM object format `../5c/5.out.h`, and common compiler compatibility support.
- Defines constants for alignment, symbol counts, buffer sizes, include nesting, macro counts, hash size, and token helpers.
- Defines `Sym`, assembler symbol records with macro text, value, type, name, and object symbol index.
- Defines input buffering structures: `fi` and `Io`.
- Defines symbol cache `h[NSYM]` for object-file name references.
- Defines `Gen`, the assembler’s generic operand representation: symbol, offset, type, register, name, float value, and string constant.
- Defines `Hist` for file/line history.
- Declares global assembler state: debug flags, symbol hash, include paths, macro/io stacks, current line, pass number, PC, output file, object character/string, and `Biobuf obuf`.
- Declares parser, lexer, macro, object emission, history, include, error, and assembly-entry functions.

Dependencies and interactions:
- Used by `a.y` and `lex.c`.
- Shares operand and opcode constants with `5c/5.out.h`, ensuring assembler output matches compiler/linker expectations.

Research relevance:
- This is the central ABI between assembler grammar, lexer/macro preprocessor, and object writer.

Risk notes:
- Many globals are shared through `EXTERN`; initialization order in `lex.c:cinit()` matters.
- `Gen.sval` is fixed at 8 bytes via `NSNAME`, matching object format assumptions.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5a/a.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5a/a.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5a/a.y

This yacc grammar parses ARM assembly syntax for `5a` and emits object instructions through `outcode()`.

Main grammar behavior:
- Handles labels, variable/equate definitions, empty lines, instructions, and syntax-error recovery.
- Recognizes ARM data-processing instructions, `MVN`, `MOV*`, branches, `BX`, conditional branches, `SWI`, compare/test ops, `MOVM`, swap/exclusive ops, `RET`/`RFE`/`CLREX`, `TEXT`, `GLOBL`, `DATA`, `CASE`, `WORD`, floating-point ops, coprocessor `MCR`/`MRC`, multiply-long forms, `MULA`, `END`, and barriers `DMB`/`DSB`/`ISB`.
- Builds `Gen` operands for registers, register pairs, shifts, immediates, float constants, string constants, names, static symbols, PC-relative branches, indirect registers, and register lists.
- Encodes `MCR`/`MRC` directly as an `AWORD` with assembled coprocessor instruction bits.
- Supports ARM condition suffixes and S/P/W/U/F bit modifiers via `cond`.
- Supports expression evaluation with unary signs, complement, arithmetic, shifts, bitwise and/or/xor, variables, and parentheses.

Important operand forms:
- `rel` supports `offset(PC)`, unresolved labels, and resolved labels.
- `ximm` supports `$const`, `$oreg`, `$*$oreg`, `$"..."`, and floating immediates.
- `reglist` supports single registers, ranges, and comma-separated lists.
- `shift` encodes logical left/right, arithmetic right, and rotate syntax into `D_SHIFT` fields.
- `name` handles `offset(SB/SP/FP)`, symbol offsets, and `name<>+off(SB)` statics.

Dependencies and interactions:
- Tokens are produced by `lex.c` from its instruction/register table.
- Semantic actions call `outcode()` with the object opcode, condition byte, source operand, optional register, and destination operand.

Research relevance:
- Defines the accepted ARM assembly language for 9front’s `5a` toolchain and maps syntax to object-file operands.

Risk notes:
- Some range checks use `$$` before assignment in `rcon`, but then assign from parsed operands; this is old yacc-style code worth handling carefully.
- Coprocessor and shift encodings are hand-packed; errors would produce valid-looking but wrong instructions.
- Conditional branch and `B` condition handling relies on `lex.c:outcode()` normalization.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5a/a.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5a/lex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5a/lex.c

This file is the ARM assembler driver, opcode/register table, initialization, and object-code emitter for `5a`.

Main flow:
- `main()` sets `thechar='5'`, `thestring="arm"`, initializes globals, parses `-o`, `-D`, `-I`, and `-t` options, and assembles one or more files.
- On non-Windows systems, multiple input files are assembled in parallel up to `$NPROC`.
- `assemble()` derives the output file name, sets include paths, opens the output object, runs the parser twice, emits history between passes, and finalizes with `cclean()`.

Instruction table:
- `itab[]` defines special names (`SP`, `SB`, `FP`, `PC`), integer registers `R0`-`R15`, floating registers `F0`-`F15`, coprocessor regs `C0`-`C15`, `CPSR`/`SPSR`, FP control regs, condition suffixes, address-mode suffixes, and all ARM assembler mnemonics supported by this tool.
- Includes LDREX/STREX, long exclusive forms, barriers, long multiply forms, VFP/FPA-style floating ops, and Plan 9 pseudo ops.

Object emission:
- `cinit()` initializes `nullgen`, clears symbol hash, installs `itab[]`, and records current path.
- `zname()` writes an `ANAME` record.
- `zaddr()` writes encoded operands, including integer offsets, string constants, and IEEE double constants.
- `outcode()` performs pass-sensitive emission, interns from/to symbols into the rolling `h[NSYM]` object symbol cache, writes opcode/condition/register/line and operands, and increments `pc` for real instructions.
- For `AB` with condition suffixes, `outcode()` rewrites to the corresponding conditional branch opcode.
- `outhist()` emits path components and `AHISTORY` records for debug history.

Dependencies and interactions:
- Includes yacc output `y.tab.h` and common lexer/macro bodies from `../cc/lexbody`, `../cc/macbody`, and `../cc/compat`.
- Emits the object format consumed by ARM linker tooling and shares constants with `5c/5.out.h`.

Research relevance:
- This is the operational heart of `5a`: command-line behavior, keyword set, two-pass parse strategy, and serialized object format.

Risk notes:
- The object symbol cache wraps through `NSYM`; collision handling uses a `jackpot` retry when from/to share the same slot.
- `assemble()` mutates `outfile` globally, so multi-file behavior depends on fork isolation.
- The Windows path logic and history path splitting are special-cased.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5a/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/5.out.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5c/5.out.h

This header defines the ARM object-file opcode, register, operand, and flag constants shared by `5a`, `5c`, and related tools.

Key contents:
- Defines `NSNAME`, `NSYM`, and `NREG`.
- Defines text flags: `NOPROF`, `DUPOK`, and `ALLTHUMBS`.
- Defines ARM register roles: return/argument register, compiler temp ranges, external register boundary, `REGTMP`, `REGSB`, `REGSP`, `REGLINK`, `REGPC`, and Thumb loader temp register.
- Defines floating register counts and allocation boundaries.
- Declares `enum as`, the canonical opcode IDs for integer ALU, branches, conditional branches, moves, FPA/VFP conversions, shifts, multiply/divide/mod, pseudo-ops, long multiply, `BX`, `DWORD`, signed-name records, exclusive ops, `CLREX`, rotate, and barriers.
- Notes conditional branch opcode order must not be reordered because predication depends on it.
- Defines condition-byte flags: `C_SCOND`, `C_SBIT`, `C_PBIT`, `C_WBIT`, `C_FBIT`, `C_UBIT`.
- Defines operand/name constants such as `D_BRANCH`, `D_OREG`, `D_CONST`, `D_FCONST`, `D_SCONST`, `D_PSR`, `D_REG`, `D_FREG`, `D_FILE`, `D_SHIFT`, `D_FPCR`, `D_REGREG`, `D_ADDR`, `D_EXTERN`, `D_STATIC`, `D_AUTO`, and `D_PARAM`.
- Defines `SYMDEF` and the `Ieee` double representation used by object serialization.

Dependencies and interactions:
- Included by `5a/a.h` and `5c/gc.h`.
- Opcode ordering and operand encodings are assumed throughout assembler grammar, compiler generation, peephole optimization, and object writers.

Research relevance:
- This is the shared ARM object-format contract for this toolchain.

Risk notes:
- Changing enum order breaks object compatibility and branch/predication assumptions.
- `C_FBIT` and `C_UBIT` share the same bit, so interpretation is context-dependent.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/5.out.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/cgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5c/cgen.c

This file is the central ARM code generator for C expressions, boolean/control expressions, 64-bit operations, and structure copies.

Main expression generation:
- `cgen()` delegates to `cgenrel()`.
- `cgenrel()` handles assignments, bitfields, integer and floating arithmetic, division/modulo, compound assignment, address generation, function calls, indirection, comparisons, logical operators, casts, struct field access, conditional expressions, and pre/post increment/decrement.
- Uses `addable` and `complex` from `sgen.c:xcom()` to choose between direct moves, address-generation registers, temporary registers, and saved temporaries for function-call-heavy expressions.
- Performs ARM-specific shortcuts:
  - direct immediate arithmetic for constant right operands,
  - signed division/mod by power-of-two constants,
  - multiply-by-constant via `mulcon()`,
  - displacement folding for `OIND`/`OINDREG` when offset fits ARM addressing range.

Compound and bitfield behavior:
- `genasop()` centralizes non-bitfield compound assignments by loading LHS, applying RHS, storing back, and optionally returning the value.
- Bitfield paths use `bitload()` and `bitstore()` from `swt.c`.

Address and boolean generation:
- `reglcgen()` and `lcgen()` compute lvalue addresses, including conditional and comma lvalues.
- `bcgen()` and `boolgen()` emit branch-oriented or value-producing boolean code, including short-circuiting, comparison inversion, floating comparison handling, and constant booleans.

64-bit support:
- `cgen64()` uses register pairs for `vlong`/`uvlong`.
- Handles casts between 32-bit and 64-bit values, assignment operators, shifts, add/sub/and/xor/or, signed/unsigned long multiply into pairs, and multiply-accumulate optimization when adding a 32x32 product to an existing 64-bit pair.
- Uses `freepair()`/`unfreepair()` to temporarily release pair registers while evaluating complex subexpressions.

Structure and block generation:
- `sugen()` handles structure/union and `vlong` movement.
- Supports constants, field extraction, struct literals, structure assignment, function returns by hidden destination pointer, conditional/comma structure expressions, 64-bit direct pair copies, and general block copy.
- General block copy uses `MOVM` register masks in chunks and may emit a loop for larger copies.

Dependencies and interactions:
- Calls register helpers and instruction emitters from `txt.c`.
- Uses `machcap()` to decide when 64-bit lowering is supported.
- Uses `mulcon()` from `swt.c`/`mul.c`, bitfield helpers from `swt.c`, and type/AST helpers from the common C compiler front end.

Research relevance:
- This is the main lowering layer from C AST to ARM `Prog` instructions. It is the highest-risk backend file in this group.

Risk notes:
- Register-pair lifetime handling is subtle; errors in `freepair()`/`unfreepair()` or complex-expression ordering can corrupt 64-bit values.
- Several optimizations mutate AST nodes temporarily, such as zeroing constants to fold addressing offsets.
- Structure copy generation depends on available temp registers and correct `MOVM` masks.
- Floating comparisons deliberately adjust branch conditions for NaN semantics.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/cgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/gc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5c/gc.h

This header defines ARM backend data structures, globals, and function prototypes for `5c`.

Key contents:
- Includes common C compiler state from `../cc/cc.h` and ARM object definitions from `5.out.h`.
- Defines ARM C type widths, `FNX` complexity threshold, and `BTRUE` boolean-generation flag.
- Defines backend structures:
  - `Adr`: object operand address.
  - `Prog`: emitted instruction node.
  - `Case`/`C1`: switch case lists.
  - `Multab`/`Hintab`: multiply-by-constant optimization metadata.
  - `Var`: tracked variable for register allocation.
  - `Reg`: control-flow/data-flow graph node.
  - `Rgn`: candidate register-allocation region.
- Declares global backend state for control-flow targets, case lists, constants, emitted programs, registers, string data, safe temporaries, register allocation bitsets, CFG nodes, dominance helpers, and optimization flags.
- Defines liveness macros `BLOAD`, `BSTORE`, `LOAD`, `STORE`, and `bset`.
- Declares prototypes for code generation, text emission, switch/bitfield/string/output helpers, listing formatters, register allocation, peephole optimization, register-bit mapping, and predication helpers.
- Registers Plan 9 formatter pragmas for backend custom formats.

Dependencies and interactions:
- Included by all `5c` backend implementation files.
- Coordinates the common compiler front end with ARM-specific code generation and optimization.

Research relevance:
- This is the backend’s shared contract and data model.

Risk notes:
- `Prog.as`, registers, names, and condition bytes are narrow character fields, matching object format expectations.
- Global state is pervasive; backend functions depend on implicit current `p`, `pc`, `reg[]`, `cursafe`, and type tables.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/gc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5c/list.c

This file installs and implements diagnostic/listing formatters for ARM backend objects.

Key routines:
- `listinit()` registers formatters for instructions, opcodes, symbols, names, bitsets, operands, and register lists.
- `Bconv()` prints variable bitsets using the backend `var[]` table.
- `Pconv()` prints a `Prog`, including condition suffixes and special cases for long multiply, `MOVM`, `DATA`, `TEXT`, and optional middle register operands.
- `Aconv()` prints opcode names from `anames[]`.
- `Dconv()` prints `Adr` operands: constants, shifts, offset registers, register pairs, integer/floating registers, PSR, branches, float constants, and string constants.
- `Rconv()` formats `MOVM` register masks as `[R...]`.
- `Sconv()` escapes 8-byte string constants.
- `Nconv()` prints symbol/name addressing forms for extern, static, auto, and parameter operands.

Dependencies and interactions:
- Uses `gc.h`, `anames[]`, `var[]`, `pc`, `zprog`, and ARM operand constants.
- Used by debug flags and diagnostics throughout code generation, register allocation, and peephole optimization.

Research relevance:
- Important support code for understanding and debugging backend output.

Risk notes:
- `Dconv()` branch display uses global `pc`, so context matters.
- `Rconv()` assumes it is passed a constant register mask; default path can return an uninitialized string if misused.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/machcap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5c/machcap.c

This file decides whether the ARM backend can directly handle selected AST operations, especially for 64-bit lowering.

Behavior:
- `machcap(Node *n)` returns true for:
  - integer/vlong add/sub/and/xor/or and their assignment forms when operands and result are vlong-compatible,
  - `OMUL`/`OLMUL` when result is vlong and operands are integer/long with matching signedness,
  - constant shifts and shift-assigns over vlong-compatible operands,
  - casts between integer/pointer-like types and vlong-compatible types.
- Returns false for unsupported nodes or null test calls.

Dependencies and interactions:
- Used by `cgen64()` in `cgen.c` to decide whether to handle 64-bit operations inline.
- Relies on common type-class arrays such as `typev`, `typeil`, `typeu`, and `typeilp`.

Research relevance:
- Small file but important gatekeeper for 64-bit code generation.

Risk notes:
- If it returns true too broadly, `cgen64()` may see unsupported shapes.
- If it returns false too often, operations fall back to slower or unsupported generic paths.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/machcap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/mul.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5c/mul.c

This file searches for short shift/add/sub instruction sequences to replace integer multiplication by constants.

Key behavior:
- Encodes multiply plans as compact two-character operation pairs:
  - letters `a`-... mean left shift by a count,
  - `+` and `-` mean add/sub combinations,
  - numeric suffix bits select source/destination temporary roles.
- `mulcon0(long v)` normalizes negative constants, checks a small cache, tries a sorted hint table, searches up to `maxmulops`, then tries factoring powers of two recursively.
- `docode()` validates and materializes a candidate hint/search sequence against the target multiplier.
- `gen1()`, `gen2()`, and `gen3()` recursively search possible shift/add/sub sequences under operation-count bounds.
- `hintab[]` contains exceptional constants whose sequences are known because the search misses them.
- `hintabsize` exposes the table size.

Dependencies and interactions:
- Consumed by `swt.c:mulcon()` and `cgen.c` multiplication paths.
- Uses `Multab` and `Hintab` from `gc.h`.

Research relevance:
- This is an old-school strength-reduction engine for ARM, where short shift/add/sub sequences can beat multiply.

Risk notes:
- Search is bounded and heuristic; `hintab` entries are required for known failures.
- The cache stores negative constants as positive absolute values, with sign handled later.
- The compact sequence language is non-obvious; changes need cross-checking against generated instructions.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/mul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/peep.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5c/peep.c

This file implements ARM peephole and local CFG optimizations over the `Reg` graph.

Main optimization flow:
- `peep()` fills missing `Reg` nodes between optimizer graph nodes, then repeatedly applies:
  - shift folding into later `D_SHIFT` operands,
  - constant propagation,
  - register copy propagation,
  - substitution propagation,
  - redundant sign/zero-extension move removal,
  - `EOR $-1,x,y` to `MVN x,y`,
  - extra ARM addressing modes for pre/post-indexed loads/stores,
  - `CMP $0,R` elimination by setting the CPSR on a prior producer,
  - short conditional predication.
- `excise()` turns an instruction into `ANOP`.

Copy and constant propagation:
- `uniqp()`/`uniqs()` identify unique predecessor/successor cases.
- `subprop()` swaps registers backward to enable copy elimination.
- `copyprop()` and recursive `copy1()` remove redundant register moves across simple CFG paths.
- `constprop()` substitutes register-held constants into subsequent moves.

Shift/address-mode optimization:
- `shiftprop()` folds standalone `ASLL`/`ASRL`/`ASRA`/`AROR` into a later data-processing instruction’s `D_SHIFT` source operand when safe.
- `findpre()`, `findinc()`, `nochange()`, `finduse()`, and `xtramodes()` detect address increments suitable for ARM pre-indexing, post-indexing, register offset, scaled-register offset, and immediate offset modes.

Use/set modeling:
- `copyu()` classifies or substitutes operand use for each opcode: unused, used, read-alter-rewrite, set, or set-and-used.
- Handles multiply-long, `MOVM`, moves, arithmetic, branches, returns, calls, and text pseudo ops.
- `copyas()`, `copyau()`, `copyau1()`, `copysub()`, and `copysub1()` implement direct/indirect matching and substitution.

Predication:
- `predinfo[]` maps branch opcodes to true/false condition codes and inverted opcodes.
- `isbranch()`, `predicable()`, and `modifiescpsr()` classify instructions.
- `joinsplit()` finds short instruction chains that can be predicated.
- `applypred()` applies condition codes and removes or rewrites branches.
- `predicate()` transforms short if/else-like control flow into predicated instruction sequences.

Dependencies and interactions:
- Depends on accurate CFG built by `reg.c`.
- Uses opcode ordering from `5.out.h`, especially contiguous conditional branches.
- Called from `regopt()` after global register allocation.

Research relevance:
- Major final code-quality stage for ARM codegen.

Risk notes:
- `copyu()` is semantic infrastructure; missing an opcode or misclassifying use/set can produce wrong-code.
- Predication is limited to short chains and avoids instructions that set CPSR or are unsupported by linker-emulated ops.
- Address-mode folding must avoid changing base registers before later uses.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/peep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/reg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5c/reg.c

This file implements global register allocation and data-flow optimization for the ARM C backend.

Main flow in `regopt()`:
- Builds a `Reg` node graph for real instructions, skipping data/global/name pseudo records.
- Assigns synthetic PCs and `log5` skip links for branch target lookup.
- Computes per-instruction use/set bitsets with `mkvar()`.
- Converts branch target offsets to `Reg` successor pointers and back-pointers.
- Detects loop structure with reverse postorder and approximate dominators via `loopit()`.
- Propagates liveness backward with `prop()`.
- Propagates register/variable synchrony forward with `synch()`.
- Warns and removes dead sets.
- Identifies allocation regions with `paint1()`, scores them, sorts by cost, selects registers with `allreg()`/`paint2()`, and rewrites instructions with `paint3()`.
- Runs `peep()` unless disabled by debug flags.
- Recomputes PCs, fixes branches, removes `ANOP`s, and recycles `Reg` nodes.

Supporting routines:
- `rega()` allocates/reuses `Reg` nodes.
- `rcmp()` sorts regions by cost.
- `addmove()` inserts load/store moves around a region for assigned variables.
- `mkvar()` maps object addresses to variable bitsets and classifies externs, params, constants, and address-taken/punned variables.
- `prop()` performs backward reference/call propagation across branches and calls.
- `postorder()`, `rpolca()`, `doms()`, `loophead()`, `loopmark()`, and `loopit()` implement loop weighting.
- `synch()` propagates differences between memory and register state.
- `allreg()` chooses an integer or floating register based on type and availability.
- `paint1()`, `paint2()`, and `paint3()` score, collect conflicts, and rewrite a variable’s live region.
- `addreg()` rewrites an `Adr` to a selected register.
- `RtoB()`, `BtoR()`, `FtoB()`, and `BtoF()` map physical registers to bit masks.

Register policy:
- Integer allocation candidates are roughly `R2`-`R8`; `BtoR()` excludes `R9` and `R10` for `m` and `g`.
- Floating allocation candidates are `F2`-`F7`.

Dependencies and interactions:
- Uses `Bits` operations from the common compiler, ARM register constants, `var[]`, and peephole routines.
- Consumes `Prog` chains emitted by `txt.c`/`cgen.c`.

Research relevance:
- This is the global optimizer for generated ARM code.

Risk notes:
- Variable identity in `mkvar()` is based on symbol/name/offset and etype; aliasing and punning are conservatively marked through `addrs`.
- The register allocator modifies instruction operands in place and inserts loads/stores; wrong liveness propagation can produce stale memory or overwritten registers.
- Calls and returns have special liveness semantics for externs, return regs, and argument regs.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/reg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/sgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5c/sgen.c

This file computes ARM backend expression addressability and complexity, and emits no-return-value markers.

Key routines:
- `noretval(int n)` emits `ANOP` markers referencing integer and/or floating return registers so the optimizer treats return values as used or unavailable.
- `xcom(Node *n)` computes `n->addable` and `n->complex` recursively.
- Recognizes directly addressable constants, registers, indirect registers, names, address-of names/indirects, dereferences, and constant-offset additions.
- Rewrites some operations:
  - multiply or multiply-assign by powers of two becomes shift or shift-assign,
  - unsigned divide/mod by powers of two becomes logical shift or mask,
  - OR expressions may be transformed by `rolor()` for integer-like types,
  - 32-to-64 cast patterns in multiplies can be lifted so `cgen64()` can use 32x32 multiply instructions.
- Computes complexity as a register-pressure estimate, marking function calls as `FNX`.
- Moves constants to the right side for immediate-friendly operations.

Dependencies and interactions:
- Called by common compiler analysis before code generation.
- Feeds `cgen.c` decisions about direct addressing, temporary allocation, and operation selection.

Research relevance:
- This is the expression-shape normalization layer for the ARM backend.

Risk notes:
- It mutates AST nodes in place, including opcode and child swaps.
- Correct complexity estimates are important for preserving evaluation order around side effects and function calls.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/sgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/swt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5c/swt.c

This file implements switch lowering, bitfield load/store helpers, string/global data emission, multiply-by-constant emission, object writing, history output, and ABI alignment.

Switch lowering:
- `swit1()` allocates a temp and calls `swit2()`.
- `swit2()` chooses:
  - direct jump table via `ACASE`/`ABCASE` when case density is high,
  - linear compare/branch for fewer than five cases,
  - binary search over sorted cases otherwise.
- Direct tables insert default entries for holes and finish with a branch to default to keep `regopt()` stable.

Bitfields:
- `bitload()` loads, shifts, and sign/zero-extends bitfield values.
- `bitstore()` masks, shifts, merges, stores back, and optionally returns the assigned bitfield value.

Data and multiply helpers:
- `outstring()` emits string data in `NSNAME` chunks through `ADATA`.
- `mulcon()` uses `mulcon0()` to emit shift/add/sub sequences for constant multiplication.
- `sextern()` emits static string/global byte data.
- `gextern()` emits global data, including split 64-bit constants respecting target endianness.

Object output:
- `zwrite()` serializes a `Prog`.
- `outcode()` optionally lists instructions, emits history, interns symbols into the object symbol cache, writes every `Prog`, then clears the instruction list.
- `outhist()` writes path and line history records.
- `zname()` writes `ANAME` or `ASIGNAME` symbol records.
- `zaddr()` serializes object operands.

ABI layout:
- `align()` implements ARM struct, element, argument, and automatic-storage alignment.
- `maxround()` rounds and tracks maximum stack/safe-space use.

Dependencies and interactions:
- Uses switch case lists from the front end, `gopcode()`/`gbranch()`/`gpseudo()` from `txt.c`, and multiply plans from `mul.c`.
- Object writer mirrors `5a/lex.c` serialization logic.

Research relevance:
- Combines multiple backend support surfaces: switches, bitfields, constants, final object output, and ABI alignment.

Risk notes:
- Direct switch lowering depends on `ACASE` and linker/runtime interpretation of `ABCASE`.
- `bitstore()` assumes `n2`/`n3` were provided by `bitload()` and frees them.
- `align()` hardcodes little-endian argument adjustment behavior.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/swt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/txt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5c/txt.c

This file initializes and finalizes ARM code generation, manages registers and temporaries, maps AST nodes to object operands, emits moves/opcodes/branches/pseudo ops, and defines target type widths/cast compatibility.

Initialization/finalization:
- `ginit()` sets ARM target identity, initializes listing formats, zero `zprog`, constant/register template nodes, `.safe` and `.ret` nodes, 64-bit support, and reserved registers.
- Reserved registers include `REGTMP`, `REGSB`, `REGSP`, `REGLINK`, `REGPC`, and two external registers.
- `gclean()` checks leaked registers, flushes string data, emits `AGLOBL` for globals/statics, emits `AEND`, and calls `outcode()`.

Instruction and argument construction:
- `nextpc()` appends a zeroed `Prog` and advances `pc`.
- `gargs()`/`garg1()` evaluate function arguments, precomputing complex arguments to safe temporaries, passing first scalar argument in `REGARG`, and placing others on stack.
- `nodconst()`, `nod32const()`, `nodfconst()`, `nodreg()`, and `regret()` build reusable node templates.

Register/temp allocation:
- `tmpreg()` finds a free integer temp.
- `regalloc()` allocates integer, floating, or register-pair temps.
- `regialloc()`, `regfree()`, `regsalloc()`, `regaalloc1()`, `regaalloc()`, and `regind()` support pointer temps, safe stack temps, argument registers, argument stack slots, and indirect register nodes.
- `exreg()` reserves external integer/floating registers.

Addressing:
- `raddr()` extracts a register operand into a `Prog.reg`.
- `naddr()` maps AST nodes to `Adr` forms for registers, indirects, names, constants, address-of, and constant addition.

Move and opcode emission:
- `gmovm()` emits `AMOVM` with increment/writeback flags.
- `gmove()` handles loads, stores, type conversions, 64-bit register-pair moves, integer/floating conversions, sign/zero extension, and unsigned-to-float conversion via a correction sequence.
- `gmover()` emits narrower sign/zero-extending moves for relational conversion cases.
- `gins()` emits raw opcodes.
- `gopcode()` maps C ops to ARM opcodes, including arithmetic, shifts, rotate, calls, multiply/divide/mod, comparisons, `ACMP`/`ACMN`, conditional branches, and `ACASE`.
- `gbranch()` emits `ARET` or `AB`.
- `patch()` fills branch target offsets.
- `gpseudo()` emits `ATEXT`, `ADATA`, and `AGLOBL` pseudo instructions.

Utility/type tables:
- `samaddr()` suppresses redundant register-pair/self moves.
- `sconst()` and `sval()` classify constants.
- `ewidth[]` defines target type widths.
- `ncast[]` defines native cast compatibility sets.

Dependencies and interactions:
- Called throughout `cgen.c`, `swt.c`, `reg.c`, and common compiler flow.
- Emits `Prog` chains later optimized by `regopt()` and serialized by `outcode()`.

Research relevance:
- This is the low-level instruction emission layer and target ABI configuration for `5c`.

Risk notes:
- `gmove()` contains many type-crossing cases; missing a conversion leads to `bad opcode in gmove`.
- Register-pair allocation order is normalized so low/high words are stable.
- Unsigned integer to float conversion emits multi-instruction code and branch patching, so it is sensitive to register lifetimes.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5c/txt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/5e.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5e/5e.c

This file is the main program for the ARM user-mode emulator `5e`.

Main behavior:
- Defines global flags: VFP enabled by default, namespace adjustment `-n`, procfs exposure `-p`, abort-on-suicide `-b`, and FPA/VFP selection `-F`/`-f`.
- `dump()` prints all 16 ARM general registers.
- `adjustns()` binds `/arm/bin` and `/rc/bin` into `/bin` and sets `cputype=objtype=arm`.
- `cleanup()` clears exclusive monitor state, removes the process from the emulator process list, frees segments, fd table, path, and `Process`.
- `suicide()` reports an emulator failure and exits or aborts.
- `notehandler()` converts host notes into emulator notes, except `sys:` and `emu:` notes.
- `dotext()` loads an absolute/relative/# path directly or searches `/bin`.
- `main()` parses flags, verifies private storage support, forks a private namespace/env, optionally adjusts namespace and starts procfs, initializes process state, loads text, installs note handler, then repeatedly executes `step()` and drains queued notes.

Dependencies and interactions:
- Uses process/memory/syscall/instruction helpers declared in `fns.h`.
- `P` is a thread-private pointer to current `Process`.

Research relevance:
- Entry point and run loop for the ARM emulator.

Risk notes:
- The run loop is infinite until emulated program exit or fatal note.
- Namespace rewriting is skipped with `-n`; this changes program lookup behavior significantly.
- Cleanup assumes `P` points to a fully initialized `Process`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/5e.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/arm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5e/arm.c

This file implements ARM instruction fetch/decode/execute for `5e`.

Instruction support:
- `invalid()` and `evenaddr()` report undefined instructions and alignment faults.
- `doshift()` implements ARM shifter operand decoding for immediate/register shifts, logical/arithmetic shifts, rotate, and rotate-through-carry.
- `single()` handles single word/byte load/store with immediate or register-shift offset, pre/post indexing, writeback, PC-relative behavior, and segment locking.
- `swap()` emulates `SWP`/`SWPB` with host `cas()`.
- `add()` computes add/subtract with carry and overflow.
- `alu()` executes ARM data-processing ops, updates CPSR for S-bit ops, blocks unsupported PSR transfers, and handles PC operand quirks.
- `branch()` implements branch/link.
- `halfword()` handles halfword and signed byte/halfword load/store.
- `block()` handles block load/store without R15.
- `multiply()` and `multiplylong()` implement multiply, multiply-accumulate, and long signed/unsigned multiply variants.
- `singleex()` emulates `LDREX`/`STREX` with a per-process linked-load address/value approximation.
- `clrex()` clears exclusive state.
- `barrier()` provides a host lock/unlock memory barrier approximation.

Decode loop:
- `step()` fetches one instruction, advances PC, checks ARM condition codes, handles unconditional `CLREX`/barriers, and dispatches to swap, exclusive, multiply, load/store, halfword, ALU, branch, syscall, block transfer, FPA, or VFP handlers.

Dependencies and interactions:
- Uses `P->R`, `P->CPSR`, `vaddr()`, `segunlock()`, `syscall()`, FPA/VFP helpers, and emulator fault handling.
- Reads instructions from emulated memory segments.

Research relevance:
- Core CPU emulator for running ARM Plan 9 binaries on the host.

Risk notes:
- Exclusive-store emulation only checks whether the memory value changed from the linked value, not whether another core modified and restored it.
- Some instruction classes are intentionally unsupported and call `invalid()`/`sysfatal()`.
- `multiplylong()` flag handling appears unusual: it sets `flN` on zero and `flV` on high sign, reflecting historical emulator behavior rather than normal ARM NZ flags.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/arm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5e/dat.h

This header defines the process, segment, and fd-table state for `5e`.

Key contents:
- Type declarations for `Process`, `Segment`, `Fdtable`, and `Fd`.
- Constants:
  - stack size, process name max, note ring length, segment count, floating register count,
  - CPSR flag bits `flN`, `flZ`, `flC`, `flV`, and `FLAGS`,
  - segment IDs `SEGTEXT`, `SEGDATA`, `SEGBSS`, `SEGSTACK`.
- `Process` contains:
  - process-list links and pid/name/path,
  - segment array,
  - LL/SC emulation state,
  - 16 general registers and CPSR,
  - FPSR and long-double FP register file,
  - per-process error buffer,
  - OCEXEC fd table,
  - note handler state, jump buffer, queued notes, and note ring indexes.
- Defines global VFP flag and thread-private process access macro `P`.
- `Segment` contains refcount, flags, optional lock, address range, backing data, and shared data ref.
- `Fd` contains lock, refcount, OCEXEC bitmap, and bitmap length.
- Debug compile-time macros are all currently disabled: `fulltrace`, `havesymbols`, `ultraverbose`, and `systrace`.

Dependencies and interactions:
- Included by every `5e` source file.
- The `P` macro depends on Plan 9 thread private storage.

Research relevance:
- Central runtime data model for the emulator.

Risk notes:
- `Process.notes` is declared as `char notes[ERRMAX][NNOTE]`, while indexing treats the outer dimension like the note slot. This is large enough but dimensionally surprising.
- Segment sharing/copying uses separate segment refcount and backing-data refcount.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5e/fns.h

This header declares `5e` emulator functions.

Covered interfaces:
- Allocation: `emalloc`, `emallocz`, `erealloc`.
- Process and executable loading: `initproc`, `loadtext`, `cleanup`, process list management.
- Memory/segment management: `newseg`, `vaddr`, `vaddrnol`, `freesegs`, `segunlock`, `copyifnec`, `bufifnec`, `copyback`.
- CPU execution: `step`, `syscall`, `clrex`.
- Error/note handling: `cherrstr`, `noteerr`, `suicide`, `donote`, `addnote`, `dump`.
- Fd table: `newfd`, `copyfd`, `fddecref`, `iscexec`, `setcexec`, `fdclear`.
- Procfs service: `initfs`.
- Floating point: FPA and VFP reset, transfer, and operation functions.
- Stack top-of-stack initialization: `inittos`.

Dependencies and interactions:
- Complements `dat.h`; all implementation files include both.

Research relevance:
- Public internal API map for the emulator.

Risk notes:
- Function signatures encode emulated 32-bit ARM addresses as `u32int`; host pointers must not leak into emulated state except through explicit copies.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/fpa.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5e/fpa.c

This file implements legacy ARM FPA floating-point emulation for `5e`.

Key routines:
- `resetfpa()` initializes `FPSR` to `0x81000000` and clears the first eight FP registers.
- `fpatransfer()` handles FPA memory transfers for float/double loads and stores with pre/post-indexing and writeback.
- `fpasecop()` maps encoded secondary operands to FP constants or FP registers.
- `fpaoperation()` implements arithmetic and unary FPA operations: add, multiply, subtract, reverse subtract, divide, reverse divide, move, negate, absolute, integer conversion, and sqrt, then stores at selected precision.
- `fparegtransfer()` transfers between ARM registers and FP registers/FPSR, and handles FP compare-to-CPSR when destination is R15.

Dependencies and interactions:
- Used by `arm.c:step()` for FPA instruction classes.
- Uses `P->F`, `P->FPSR`, `P->CPSR`, segment memory helpers, and `invalid()`.

Research relevance:
- Provides the non-VFP floating-point path selected by `5e -F`.

Risk notes:
- Only selected FPA operations are implemented; unknown opcodes fatal.
- FP compare sets ARM flags using host long-double comparisons, including unordered behavior through the final `else`.
- Transfers assume compatible host memory layout for float/double.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/fpa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/fs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5e/fs.c

This file exposes `5e` emulator processes through a proc-like 9P filesystem.

Main structures:
- Defines qid IDs for proc entries such as `args`, `ctl`, `fd`, `fpregs`, `kregs`, `mem`, `note`, `regs`, `segment`, `status`, `text`, `wait`, `profile`, and `syscall`.
- `Dirtab procdir[]` lists supported entries, permissions, and nominal sizes.
- `Aux` stores selected `Process`, opened fd, and directory entry for a fid.

Main behavior:
- `readin()` reads data from the host `/proc/<pid>/<file>`.
- `calcmem()` computes non-stack memory usage in KB.
- `copymem()` copies bytes from emulator segments for `mem` reads.
- `segments()` formats segment layout/refcount info.
- 9P callbacks:
  - `procattach()` initializes root fid aux state.
  - `procwalk()` walks root pid directories and per-process entries.
  - `procclone()` copies fid aux.
  - `procopen()` opens the process text file for `text`.
  - `procdestroyfid()` frees aux state.
  - `procgen()` and `procsubgen()` enumerate process and file directories.
  - `procread()` serves directory listings, `status`, `segment`, `text`, `mem`, and `regs`.
  - `procwrite()` proxies writes to host `/proc/<pid>/note` for `note`.
  - `procstat()` fills directory metadata.
- `initfs()` posts and mounts the service at the requested mount point.

Dependencies and interactions:
- Enabled by `5e -p`, called from `5e.c`.
- Reads emulator state directly and delegates unsupported proc entries to placeholder errors.

Research relevance:
- Bridges emulator state to Plan 9 tooling through a familiar `/proc` surface.

Risk notes:
- Many listed proc entries are not actually readable/writable beyond the handled cases.
- `copymem()` walks segments without segment locks.
- `procwrite()` is present but not installed in `procsrv`, which only sets attach/walk/clone/destroyfid/open/read/stat.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/proc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5e/proc.c

This file manages emulator process state, executable loading, stack initialization, fd-table state, errors, and Plan 9 note delivery.

Process setup:
- Defines packed `Tos`, matching Plan 9 top-of-stack layout enough to populate pid/profiling fields.
- `initproc()` allocates current `Process`, sets pid, fd table, process list, and resets FPA/VFP state.
- `addproc()`, `remproc()`, and `findproc()` maintain the global process list under `plistlock`.
- `copyname()` updates process display name and shared executable path reference.

Stack and executable loading:
- `initstack()` builds initial ARM user stack with argc, argv pointers, strings, top-of-stack pointer in R0, clock pointer in R1, and SP in R13.
- `inittos()` writes pid into emulated `Tos`.
- `loadscript()` handles `#!` scripts by parsing interpreter and reinvoking `loadtext()`.
- `loadtext()` opens and validates an ARM executable, resets process memory/register/note state, creates text/data/BSS/stack segments, reads file contents, sets PC to entry, clears OCEXEC fds, initializes stack, and resets FP state.

Fd table:
- `newfd()`, `copyfd()`, `fddecref()`, `iscexec()`, `setcexec()`, and `fdclear()` manage a refcounted bitmap of close-on-exec file descriptors.

Errors and notes:
- `cherrstr()` sets per-process error string.
- `noteerr()` records host error text on failed syscalls.
- `addnote()` queues host notes into the emulated process note ring.
- `donote()` builds a user-register frame and note string on the emulated stack, jumps to the emulated notify handler, runs until `noted()`, then restores registers depending on noted action.

Dependencies and interactions:
- Uses `mach` executable headers, memory helpers from `seg.c`, syscall note constants, and FPA/VFP reset functions.
- Used by `5e.c`, `sys.c`, and `fs.c`.

Research relevance:
- This is the emulator’s process and exec model.

Risk notes:
- `loadscript()` tokenizes the shebang line in-place and has simple whitespace parsing.
- `donote()` runs nested `step()` calls under `setjmp`/`longjmp`, so state restoration is delicate.
- Segment copies during `rfork()` are implemented in `sys.c`, while base segment allocation lives here/`seg.c`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/seg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5e/seg.c

This file implements emulator segment allocation, address translation, and safe host-buffer copying for locked segments.

Key routines:
- `newseg()` allocates a segment and backing `Ref`+data buffer, sets address range, marks BSS as lock-protected, and installs it in `P->S[idx]`.
- `freesegs()` releases all process segments and shared backing buffers.
- `vaddr()` resolves an emulated address/length to a host pointer, optionally read-locking lock-protected segments, and reports faults through `suicide()`.
- `vaddrnol()` resolves and immediately unlocks.
- `segunlock()` releases a segment read lock if needed.
- `copyifnec()` returns a direct pointer for unlocked memory or copies out locked memory into a host buffer, with string-length support for `len < 0`.
- `bufifnec()` returns a direct pointer for unlocked memory or allocates a temporary output buffer for locked memory.
- `copyback()` writes a temporary buffer back to emulated memory and frees it.

Dependencies and interactions:
- Used heavily by instruction execution and syscall marshalling.
- Locking is designed around BSS/heap growth and host syscalls that may block or mutate memory.

Research relevance:
- Core memory safety and address translation layer for the emulator.

Risk notes:
- `vaddr()` rejects accesses crossing segment boundaries.
- `copyifnec()` with `len < 0` calls `strlen()` on emulated memory after translating only a zero-length access.
- Callers must pair locked direct pointers with `segunlock()` or use copy/buffer helpers correctly.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/seg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/sys.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5e/sys.c

This file translates emulated Plan 9 ARM syscalls into host Plan 9 syscalls.

Argument handling:
- `arg(n)` reads 32-bit syscall arguments from the emulated stack.
- `argv(n)` combines two 32-bit words into a 64-bit argument.
- Syscall return values are written to `P->R[0]`.
- `noteerr()` is used to capture host error strings into `P->errbuf`.

Implemented syscalls:
- File operations: `open`, `create`, `close`, `pread`, `pwrite`, `seek`, `fd2path`, `stat`, `fstat`, `wstat`, `fwstat`, `remove`.
- Process/control: `exits`, `brk`, `errstr`, `chdir`, `notify`, `noted`, `rfork`, `exec`, `await`, `sleep`, `rendezvous`, `alarm`.
- Namespace/mount: `bind`, `mount`, `unmount`, `fauth`.
- IPC/fd: `pipe`, `dup`.
- Synchronization: `semacquire`, `semrelease`.

Memory marshalling:
- String and read-only buffers use `copyifnec()` when memory may be lock-protected.
- Output buffers use `bufifnec()` and `copyback()` for safe mutation.
- `sysbrk()` resizes the BSS segment under write lock, zero-filling new memory.
- `sysexec()` copies the emulated argv vector and strings into host memory before calling `loadtext()`.

`rfork()` behavior:
- Validates mutually exclusive flag combinations.
- For non-`RFPROC`, updates fd-table sharing/clearing then calls host `rfork()`.
- For `RFPROC`, allocates a copied `Process`, duplicates or shares segments according to flags, handles fd table sharing/copy/clear, forks with `RFMEM|flags`, installs child `P`, updates pid/Tos, and adds to process list.

Dispatcher:
- `syscall()` uses `P->R[0]` as the syscall number and dispatches through a static function table included from Plan 9 syscall numbers.

Dependencies and interactions:
- Called by `arm.c` on SWI/syscall instructions.
- Uses memory helpers from `seg.c`, process loading from `proc.c`, fd helpers, and Plan 9 syscall constants.

Research relevance:
- This is the emulator’s OS compatibility layer.

Risk notes:
- Unsupported syscall numbers fatal the emulator.
- Syscall tracing is compile-time disabled unless `systrace` macro changes.
- `rfork()` state copying is complex and must keep segment/data refs, fd refs, path refs, process list, and thread-private `P` consistent.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/sys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5e/util.c

This file provides fatal allocation wrappers for `5e`.

Functions:
- `emalloc(size)` calls `malloc`, `sysfatal()`s on failure, and records malloc tag.
- `emallocz(size)` allocates with `emalloc`, zeroes the block, and records tag.
- `erealloc(old, size)` calls `realloc`, `sysfatal()`s on failure, and records realloc tag.

Dependencies and interactions:
- Used throughout `5e` for all dynamic runtime structures.

Research relevance:
- Small utility layer but central to emulator memory allocation assumptions.

Risk notes:
- Allocation failure terminates the emulator.
- `erealloc()` does not preserve old pointer on failure because it exits immediately.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/vfp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5e/vfp.c

This file implements VFP floating-point emulation for `5e`.

Key routines:
- `resetvfp()` clears `FPSR` and all FP registers.
- `vfpregtransfer()` moves between ARM registers and VFP registers/FPSR; if reading FPSR into R15, it copies FPSR to CPSR.
- `vfprmtransfer()` handles VFP memory load/store of float or double values at aligned addresses.
- `vfparithop()` implements selected binary operations: multiply, add, subtract, and divide.
- `vfpotherop()` implements compare with zero/register, int-to-float, float-to-int, move, absolute, negate, and sqrt.
- `vfpoperation()` dispatches operation encodings to arithmetic or other operation handlers.

Dependencies and interactions:
- Called by `arm.c:step()` when VFP is enabled and instruction masks match.
- Uses `P->F`, `P->FPSR`, `P->CPSR`, memory helpers, and host `fabs()`/`sqrt()`.

Research relevance:
- Default floating-point path for `5e`.

Risk notes:
- Only a subset of VFP encodings is implemented; unsupported forms fatal.
- FP registers are stored as `long double`, but memory/register transfers treat them partly as float/double/int through casts.
- FPSR-to-CPSR transfer copies the whole FPSR, not only condition bits.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5e/vfp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/5i.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5i/5i.c

This file is the main program and loader for the older interactive ARM interpreter/debugger `5i`.

Main flow:
- Defaults to loading `5.out` unless a file argument is supplied.
- Initializes bio input/output, a simulated TLB, opens the text file, prints banner, reads executable header, initializes stack, then enters `cmd()`.

Executable/memory setup:
- `initmap()` lays out simulated text, data, BSS, and stack segments, with lazy page tables and instruction profiling array `iprof`.
- `inithdr()` validates the executable as ARM (`FARM`), initializes symbols and maps, sets `machdata` to ARM disassembly data, and captures SB if available.
- `reset()` clears registers, frees memory structures, resets profiling, and resets breakpoint counters.
- `initstk()` builds a Plan 9 ARM initial stack, including zeroed Tos area, pid field for `nsec()`, argc/argv, R0 top-of-stack pointer, R1 profiling clock pointer, SP, and PC from the header.

Diagnostics/utilities:
- `fatal()` exits with formatted error.
- `itrace()` prints trace lines.
- `dumpreg()` prints PC/SP and all integer registers.
- `dumpfreg()` and `dumpdreg()` are stubs.
- `emalloc()` and `erealloc()` allocate zeroed memory or fatal.

Dependencies and interactions:
- Uses `arm.h` global state and declarations.
- Depends on `cmd.c` for interactive shell, `mem.c` for lazy memory, and architecture decode/execute files not in this group.

Research relevance:
- Entry point for a debugging-oriented ARM interpreter distinct from `5e`.

Risk notes:
- `reset()` loop condition `for(i = 0; i > Nseg; i++)` never iterates, so segment freeing there appears ineffective.
- `erealloc()` allocates new memory but does not free old memory.
- Stack/Tos setup assumes specific 32-bit Plan 9 layout.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/5i.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/arm.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5i/arm.h

This header defines the global model for the `5i` ARM interpreter/debugger.

Key structures:
- `Breakpoint`: type, address, count/value, done counter, and next link.
- `Tlb`: simulated TLB status, size, entries, hits, and misses.
- `Icache`: simulated instruction cache settings, line array, hash function, and stats.
- `Inst`: decoded instruction table entry: function, name, type, count, taken, and delay use.
- `Registers`: current address/instruction, instruction pointer, 16 integer regs, condition/compare bookkeeping, class, carry fields.
- `Segment`: simulated memory segment metadata, lazy page table, ref counters, and file offsets.
- `Memory`: array of segments.

Constants:
- Breakpoint types: instruction/read/write/access/equal.
- Instruction classes: memory, arithmetic, branch, syscall.
- Registers: argument/return, PC, link, SP.
- Segment IDs: stack, text, data, BSS.
- Plan 9 constants: page size, word size, user text base, stack top/size, profiling granularity, S bit, sign bit, FP condition constants.

Declarations:
- Interpreter execution, command shell, breakpoints, memory access, fetch, stack/source printing, profiling summaries, TLB/cache, syscall, arithmetic helpers, and allocation functions.
- Globals for registers, memory, trace flags, instruction tables, cache/TLB, breakpoints, command state, symbol map, and profiling.

Dependencies and interactions:
- Included by all `5i` files.
- Uses Plan 9 `mach` symbol/disassembly interfaces.

Research relevance:
- Defines the state contract for the interpreter/debugger.

Risk notes:
- Some function names and FP constants reflect inherited MIPS interpreter code, while the target is ARM.
- Many globals are shared mutable state across command, memory, breakpoint, and execution layers.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/arm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/bpt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5i/bpt.c

This file implements breakpoints for `5i`.

Key routines:
- `dobplist()` prints all breakpoints with address, count/done state, type-specific prefix, and symbolized location.
- `breakpoint(addr, cp)` parses breakpoint subtype:
  - default instruction breakpoint,
  - `r` read,
  - `a` access,
  - `w` write,
  - `e` equal-value watchpoint.
  It evaluates the address, records `cmdcount`, initializes `done`, and prepends to `bplist`.
- `delbpt(addr)` removes a breakpoint at an evaluated address.
- `brkchk(addr, type)` checks breakpoints against an access/instruction event, handles equal-value watchpoints through `getmem_4()`, decrements count-based breakpoints, and stops execution through `count=1` and `atbpt=1`.

Dependencies and interactions:
- Memory accessors in `mem.c` call `brkchk()` for read/write watchpoints.
- Execution loop calls it for instruction breakpoints elsewhere in `5i`.
- Command parser in `cmd.c` drives breakpoint creation/deletion.

Research relevance:
- Interactive debugging control for `5i`.

Risk notes:
- `delbpt()` increments `membpt` instead of decrementing for non-instruction breakpoints; this keeps checks enabled but looks like a counter bug.
- Equal breakpoints use `count` as comparison value, unlike count-based breakpoints.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/bpt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/cmd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5i/cmd.c

This file implements the interactive command shell, expression parser, formatting, run/step commands, register setting, tracing toggles, and memory/source inspection for `5i`.

Parsing and expressions:
- `nextc()` skips spaces/tabs and terminates newline.
- `numsym()` parses a symbol, `.`, `#hex`, or numeric constant.
- `expr()` evaluates one binary operation over symbols/numbers: `+`, `-`, `%` as division, `&`, or `|`.
- `buildargv()` tokenizes command strings for restart arguments.

Command groups:
- `colon()` handles:
  - `:b` set breakpoint,
  - `:d` delete breakpoint,
  - `:r` reset/restart with args and run,
  - `:c` continue,
  - `:s` step optional count.
  It reports stopped or breakpoint address and optionally source.
- `dollar()` handles stack traces, breakpoint list, register dumps, quit, summaries, trace mode toggles, and instruction/TLB/segment/profile summaries.
- `eval()` prints expression values.
- `quesie()` implements memory/executable inspection with format sequences.
- `setreg()` writes PC, SP, or `rN`.

Formatting:
- `pfmt()` supports octal/decimal/hex signed/unsigned 16/32-bit output, bytes/chars/escaped chars, strings, escaped strings, time, address symbolization, globals, disassembly, newline, direction modifiers, and source-line display.
- Updates global `dot`, `fmt`, and `inc` for repeated inspection.

Main shell:
- `cmd()` installs interrupt handler, initializes `dot`, recovers through `setjmp(errjmp)`, reads commands from `bin`, repeats last command on blank line, parses optional address/count, and dispatches by command character `$`, `:`, `/`, `?`, `=`, or `>`.

Dependencies and interactions:
- Uses `run()`, `reset()`, memory accessors, symbol lookup/disassembly, source printing, breakpoints, summaries, and register state.
- Driven after `5i.c` loads the executable.

Research relevance:
- User-facing debugger shell for `5i`.

Risk notes:
- Command parsing is simple and buffer-limited.
- `expr()` supports only one binary operator, not full expression precedence.
- Some output calls pass dynamic strings as format strings to `Bprint`, following Plan 9 conventions but requiring trusted symbol text.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/float.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5i/float.c

This file contains floating-point instruction table scaffolding and mostly stubbed floating-point handlers for `5i`.

Key contents:
- Declares many FP operation handlers.
- `cop1[]` maps operation slots to names such as `add.f`, `sub.f`, `mul.f`, `div.f`, `abs.f`, `mov.f`, `neg.f`, conversions, and FP comparisons.
- `unimp()` reports an unimplemented floating-point trap and jumps back through `errjmp`.
- `inval()` reports invalid operation and jumps through `errjmp`.
- `ifmt()` reports invalid FP data format.
- Most execution handlers are empty stubs:
  - arithmetic/conversion/move/compare handlers,
  - load/store FP handlers,
  - coprocessor transfer handlers,
  - branch-on-FP-condition handler,
  - `Icop1()` dispatcher.

Dependencies and interactions:
- Included in `5i` build as part of interpreter instruction support.
- Names and `cop1[]` look inherited from a MIPS-style coprocessor model despite ARM target context.

Research relevance:
- Indicates FP support in `5i` is incomplete/stubbed.

Risk notes:
- Programs relying on floating-point execution through `5i` likely do not run correctly.
- Unimplemented handlers either do nothing or trap depending on which path is reached.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/float.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/icache.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5i/icache.c

This file contains empty instruction-cache hooks for `5i`.

Functions:
- `icacheinit()` does nothing.
- `updateicache(ulong addr)` ignores the address.

Dependencies and interactions:
- `mem.c:ifetch()` calls `updateicache()` when `icache.on` is enabled.
- `arm.h` declares `initicache()`, but this file defines `icacheinit()`; naming mismatch may be intentional legacy or unused.

Research relevance:
- Simulated I-cache support is effectively disabled/stubbed.

Risk notes:
- I-cache statistics or stall modeling will not work unless implemented elsewhere.
- The `initicache`/`icacheinit` name mismatch is suspicious.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/icache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/mem.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5i/mem.c

This file implements instruction fetch, memory loads/stores, debugger memory I/O, simulated TLB, and lazy paging for `5i`.

Instruction and data access:
- `ifetch()` enforces word-aligned instruction fetch, updates I-cache/profiling, translates address, and returns little-endian 32-bit instruction word.
- `getmem_4()` and `getmem_2()` assemble multi-byte values through byte reads.
- `getmem_w()` handles unaligned word reads by rotating the aligned word, checks read breakpoints, and returns little-endian words.
- `getmem_h()` handles unaligned halfword reads similarly, checks read breakpoints, and returns halfwords.
- `getmem_b()` reads a byte and checks read breakpoints.
- `getmem_v()` returns a 64-bit value from two words.
- `putmem_h()`, `putmem_w()`, `putmem_b()`, and `putmem_v()` write little-endian values and check write breakpoints; halfword/word stores reject unaligned addresses.
- `memio()` copies between debugger buffers and simulated memory, including bounded C-string reads.

TLB and paging:
- `dotlb()` tracks simulated page hits/misses and randomly replaces a TLB entry.
- `vaddr()` translates a virtual address to a lazily allocated page:
  - text pages are read from executable text offset,
  - data pages are read from executable data offset and zero-filled past file data,
  - BSS and stack pages are zero-allocated.
- On unmapped address, reports user TLB miss and longjmps to command loop.

Dependencies and interactions:
- Uses `memory.seg[]` laid out by `5i.c:initmap()`.
- Breakpoint checks go through `brkchk()`.
- Command shell and instruction execution use these accessors.

Research relevance:
- Core simulated memory subsystem for `5i`.

Risk notes:
- `getmem_4()`/`getmem_2()` assemble via byte reads while `getmem_w()`/`getmem_h()` have special unaligned behavior; callers need the right accessor.
- Lazy text/data reads operate page-at-a-time and assume file offsets derived in `initmap()`.
- TLB replacement uses `lnrand()` and only models statistics, not permissions.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/mem.c -->