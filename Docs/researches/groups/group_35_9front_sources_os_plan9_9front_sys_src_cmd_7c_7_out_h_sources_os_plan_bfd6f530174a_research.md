# Group Research: group_35_9front_sources_os_plan9_9front_sys_src_cmd_7c_7_out_h_sources_os_plan_bfd6f530174a

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/7.out.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7c/7.out.h

ARM64 object/instruction interface header shared by the 7c compiler backend and related tooling. It defines target register numbers, compiler allocation ranges, assembler opcode IDs, operand/addressing classes, special processor register encodings, archive symbol metadata, and the local `Ieee` floating representation.

Key contents:
- Defines ARM64 general and floating register counts and ABI roles: return/argument register `R0`, compiler temps around `R17`, SB/FP/LINK/SP/ZERO aliases, and compiler-allocatable ranges.
- `enum as` is the central opcode namespace for ARM64 instructions and Plan 9 pseudo-ops such as `ATEXT`, `ADATA`, `AGLOBL`, `ABCASE`, `ACASE`, and `AEND`.
- Conditional branch opcodes are explicitly kept contiguous because predicate/condition logic depends on their order.
- Operand classes include constants, external/static/auto/param names, indirect/register modes, pre/post-indexed memory, shifts, register pairs, ADRP/ADR low reloc forms, condition operands, and SIMD/vector lane/set forms.
- `SYSARG5`/`SYSARG4` encode ARM64 system-register fields; constants define named SPRs such as `NZCV`, `FPSR`, `FPCR`, `SPSR_EL1`, `ELR_EL1`, and DAIF set/clear immediates.
- `Ieee` stores Plan 9’s split double representation used when serializing floating constants.

Filesystem relevance: indirect. This is part of the 9front ARM64 toolchain needed to build OS/userland components, not filesystem logic itself.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/7.out.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/cgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7c/cgen.c

Expression and aggregate code generator for the ARM64 Plan 9 C compiler backend. It lowers C AST nodes into backend `Prog` instructions via `gopcode`, `gmove`, branches, register allocation helpers, switch/bitfield helpers, and structure-copy code.

Key functions:
- `cgen`/`cgenrel` handle scalar expression generation, including assignments, arithmetic, shifts, calls, indirection, address taking, casts, conditionals, pre/post increment/decrement, logical operators, and bitfield assignment paths.
- The generator uses node complexity and `FNX` to decide when to evaluate function-call-heavy subexpressions into temporaries before continuing.
- Arithmetic has special cases for immediates, power-of-two signed division/modulo, and constant multiplication via `mulcon`.
- `reglcgen` and `lcgen` generate lvalues/addresses, including offset folding when `usableoffset` says ARM64 addressing can represent the displacement.
- `boolgen` and `bcgen` lower comparisons and boolean expressions into branch sequences or materialized `0/1` results.
- `sugen` emits structure/union and vlong aggregate movement, including structure literals, function returns through hidden pointers, conditional aggregate expressions, and explicit copy loops.
- `layout` unrolls small structure copies and seeds loop counters for larger copies.
- `castup`, `hardconst`, and `cond` provide cast and predicate classification helpers.

Important interactions:
- Depends heavily on `txt.c` for instruction emission and register management.
- Calls `bitload`/`bitstore`, `mulcon`, `sugen`, `nullwarn`, `regsalloc`, and `regaalloc`.
- Mutates AST nodes in narrow cases to simplify lvalue and offset generation.

Filesystem relevance: indirect compiler backend infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/cgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/gc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7c/gc.h

Primary ARM64 backend header for `7c`. It includes common compiler definitions and `7.out.h`, defines target C type sizes, core backend structs, globals, register-allocation bitset macros, pass constants, and function prototypes across the backend files.

Key contents:
- Target data model: `char=1`, `short=2`, `int=4`, `long=4`, pointer/vlong/double `=8`, float `=4`.
- Defines `Adr`, `Prog`, `Case`, `C1`, `Multab`, `Hintab`, `Var`, `Reg`, and `Rgn`.
- `Prog` carries `from`, optional `from3`, `to`, opcode, register field, source line, and link pointer.
- `Reg` is the optimizer CFG node with use/set bitsets, liveness/synchrony bitsets, predecessor/successor links, loop weight, and attached `Prog`.
- Global state includes instruction list pointers, current PC, switch cases, constant nodes, register-use counters, string literal buffers, external register offsets, register optimizer variables, and variable tables.
- Declares all cross-file backend entry points for generation, emission, switch handling, listing, register optimization, and peephole optimization.
- Installs `#pragma varargck` format contracts for Plan 9 custom formatters such as `%A`, `%P`, `%D`, `%B`.

Filesystem relevance: indirect; it is the backend contract binding the 9front ARM64 compiler.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/gc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7c/list.c

Formatting and listing support for ARM64 backend instructions, operands, bitsets, registers, and short strings.

Key functions:
- `listinit` installs Plan 9 `fmt` converters for opcodes, programs, operands, names, bitsets, strings, and register lists.
- `Pconv` formats a full `Prog`, including opcode, source operand, data/text size fields, register operand, optional `from3`, and destination.
- `Aconv` maps opcode numbers to `anames`.
- `Dconv` formats `Adr` operands across constants, shifted operands, offset/pre/post-indexed memory, extended registers, GPR/FPR/SP/SPR names, branches, floating constants, and short strings.
- `Rconv` formats register-list constants.
- `Sconv` escapes fixed-width short string constants.
- `Nconv` formats symbolic names for extern/static/auto/param references.

Important details:
- Has specific display support for `FPSR`, `FPCR`, and `NZCV`.
- Uses current `pc` for branch offset formatting.
- The `conds` table is present but unused in the active formatting path.

Filesystem relevance: indirect debugging/listing support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/machcap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7c/machcap.c

Small target capability gate for the ARM64 backend. `machcap(Node *n)` reports whether a node operation is directly manageable by this machine backend.

Behavior:
- Returns true for null test probes.
- Accepts scalar integer/pointer/vlong multiply and assignment multiply when the node type is in `typechlv`.
- Accepts add/sub/and/or/xor and shifts when the left operand is in `typechlv`.
- Accepts casts, conditionals, comma/list/logical nodes, compound assignments, shifts, increments/decrements, comparisons, and signed negation for supported scalar classes.
- Explicitly rejects unsupported operations such as bitwise complement unless handled elsewhere.

Filesystem relevance: indirect compiler target capability metadata.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/machcap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/mul.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7c/mul.c

Constant-multiplication recipe generator. It finds short shift/add/sub sequences that can replace multiplication by constants.

Key functions:
- `mulcon0` normalizes negative constants, checks a small cache, consults the exception hint table, recursively searches for a recipe up to `maxmulops`, and handles trailing power-of-two factors.
- `docode` interprets hint strings into concrete two-character encoded operations while tracking two virtual registers.
- `gen1`, `gen2`, and `gen3` recursively search the space of shifts, additions, and subtractions.
- `hintab` contains sorted exception recipes for constants the generic search fails to find under the operation limit.
- `hintabsize` exports the table length.

Recipe encoding:
- Letters `a` and up represent left shifts by letter offset.
- `+` and `-` represent add/sub combinations.
- The following digit encodes which virtual source/destination registers are used.

Important interaction:
- `swt.c:mulcon` consumes `Multab.code` and emits actual backend operations.

Filesystem relevance: indirect compiler optimization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/mul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/peep.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7c/peep.c

Peephole optimizer for emitted ARM64 backend instructions. It completes the `Reg` chain for inserted instructions, then repeatedly performs local copy/constant/store propagation, redundant move removal, selected opcode simplification, and simple instruction scheduling.

Key active behavior:
- `peep` inserts missing `Reg` nodes for instructions added after global register optimization.
- Propagates stores to later loads from the same local variable through `storeprop`.
- Simplifies redundant sign/zero-extension moves when prior definitions already have the right width.
- Runs copy propagation through `copyprop`, `copy1`, `copyu`, `copyas`, `copyau`, and substitution helpers.
- Runs constant propagation from constant-to-register moves through `constprop`.
- Converts `EOR -1,x,y` into `MVN x,y` forms.
- Removes duplicate extension/move chains such as `MOVB x,R; MOVB R,R`.
- Performs a small load scheduling transform by swapping an independent instruction between a load and the first consumer.

Key helper logic:
- `independent` checks whether two instructions can be swapped without register or memory hazards.
- `subprop` tries register substitution around copies so one copy can later disappear.
- `shiftprop` can fold a shift into a `D_SHIFT` operand, but the top-level call is disabled with `if(0 && shiftprop(r))`.
- `regzer` is currently disabled by an early `return 0`, so zero-register canonicalization is inactive.
- `xtramodes` and predicate conversion logic are compiled out under `NOTYET`/`XXX`.

Predicate-related dead/disabled code:
- Defines conditional branch metadata, predicability checks, CPSR modification checks, join/split analysis, and `predicate`, but the actual call is disabled.
- `modifiescpsr` currently returns true unconditionally before checking opcodes, which would make predicate analysis conservative if enabled.

Filesystem relevance: indirect compiler optimizer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/peep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/reg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7c/reg.c

Global register optimizer for the ARM64 compiler backend. It builds a control-flow graph over emitted `Prog` instructions, performs liveness and synchronization propagation, identifies profitable variable live ranges, assigns hardware registers, rewrites instructions, runs peephole optimization, and repairs PCs/branches.

Key phases in `regopt`:
- Builds `Reg` nodes while skipping data/name pseudo-ops.
- Computes variable use/set bitsets through `mkvar`.
- Resolves branch targets into CFG successor/predecessor links using `log5` skip links for faster lookup.
- Computes loop weights using reverse postorder, approximate dominators, and loop-head marking.
- Propagates references and call-live sets backward through `prop`.
- Propagates register/variable divergence forward through `synch`.
- Finds candidate allocation regions using `paint1`, scores them, sorts by cost with `rcmp`, computes occupied register masks with `paint2`, chooses registers with `allreg`, and rewrites with `paint3`.
- Runs `peep` unless disabled by debug settings.
- Recalculates PCs, fixes branch offsets, removes NOPs, and recycles `Reg` nodes.

Important helpers:
- `addmove` inserts spill/reload moves around regions.
- `mkvar` tracks symbolic variables and classifies externs, params, constants, and address-taken/punned variables.
- `addreg` rewrites an address to a chosen register.
- `RtoB`, `BtoR`, `FtoB`, and `BtoF` map ARM64 register numbers to allocator bit masks.

Constraints:
- Register candidates are limited to backend-defined allocatable ranges.
- Variables with funny punning, excessive variable count, or unsafe address identity are excluded from optimization.

Filesystem relevance: indirect compiler optimizer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/reg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/sgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7c/sgen.c

Early shape/complexity analysis and simple lowering preparation for ARM64 code generation.

Key functions:
- `noretval` emits `ANOP` markers identifying unused integer and/or floating return values.
- `xcom` computes `Node.addable` and `Node.complex`, classifying constants, names, registers, indirect registers, address-taking, dereferences, and address arithmetic.
- Rewrites multiplication/division/modulo by powers of two into shifts or masks where legal.
- Calls `simplifyshift` for shift normalization.
- Calls `rolor` for unsigned OR patterns that can become rotates.
- Marks function calls as `FNX` complexity.
- Reorders immediate constants to the right side for comparisons and commutative integer operations when useful.

Addressability model:
- Constants, names, registers, indirect registers, address-of-name, address-of-indirect-register, and dereferenced address constants receive compact numeric addressability classes used by `cgen.c`.

Filesystem relevance: indirect compiler frontend/backend bridge.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/sgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/swt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7c/swt.c

Mixed backend support file for switch lowering, bitfields, constant multiplication emission, global data emission, object serialization, history records, and ABI alignment.

Key functions:
- `swit1`/`swit2` generate switch dispatch as linear compares, binary decision trees, or direct jump tables via `OCASE`/`ABCASE`.
- `bitload` extracts bitfields with masking and sign/zero-extending shifts.
- `bitstore` masks, shifts, merges, and stores bitfield values back into containing storage.
- `outstring` buffers string data into fixed `NSNAME` chunks emitted as `ADATA`.
- `mulcon` consumes recipes from `mulcon0` and emits shift/add/sub instruction sequences for multiplication by constants.
- `gextern` emits global data initialization, with special handling for vlong constants and endianness.
- `outcode`, `zwrite`, `zname`, and `zaddr` serialize compiler `Prog` records and symbol table references to the object stream.
- `outhist` emits source history/path records.
- `align` and `maxround` implement target struct/argument/automatic storage alignment.

Important details:
- Object symbol references use a small `NSYM` rolling cache.
- `zaddr` upgrades too-large `D_CONST` offsets to `D_DCONST`.
- Alignment treats parameters and aggregates according to this backend’s 64-bit ABI expectations, while preserving Plan 9 compiler conventions.

Filesystem relevance: indirect compiler/object emission support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/swt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/txt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7c/txt.c

Central ARM64 code emission and backend setup file for `7c`. It initializes target state, manages temporary/register allocation, emits instructions, selects move/cast/arithmetic opcodes, handles branches/pseudo-ops, validates immediates/offsets, and defines target type tables.

Key areas:
- `ginit` sets target identity, register reservations, type-class tables, zero/template nodes, return/temp nodes, and compiler globals.
- `gclean` checks leaked registers, flushes string literals, emits `AGLOBL` records, appends `AEND`, and calls `outcode`.
- `nextpc`, `gins`, `gopcode`, `gbranch`, `patch`, and `gpseudo` allocate and populate `Prog` instructions.
- `gargs`/`garg1` lower call arguments, including function-call temporaries, structure pass-by-pointer handling, first argument register use, and stack argument layout.
- `regalloc`, `regfree`, `regret`, `regsalloc`, `regaalloc`, and related helpers manage backend scratch registers and stack temporaries.
- `naddr`/`raddr` convert compiler `Node` objects into assembler `Adr` operands.
- `gmove` is the large type-conversion/move selector covering integer, pointer, vlong, float, double, load/store, sign-extension, zero-extension, and float/int conversions.
- `gopcode` maps generic C operators to ARM64 opcodes and emits comparison-plus-branch sequences, including zero-compare optimizations through `zcmp`.
- `usableoffset`, `sval`, and `isaddcon` gate ARM64 immediate/addressing encodings.

Data tables:
- `ewidth` defines target type widths.
- `ncast` defines no-op cast compatibility classes.

Important constraints:
- `REGTMP`, SB, link, SP/zero, and two external registers are reserved.
- `REGARG` is `R0`, so call and return paths share register pressure decisions.
- `gmove` avoids redundant same-register moves with `samaddr`.

Filesystem relevance: indirect compiler backend.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7c/txt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/asm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7l/asm.c

ARM64 linker output writer. It emits final machine code bytes, data segments, symbol tables, line tables, dynamic module records, and Plan 9 executable headers.

Key functions:
- `entryvalue` resolves the executable entry point from `INITENTRY`, symbols, or defaults.
- `asmb` is the main output pass: emits text instructions via `asmout`, pads string/data segments, writes initialized data, emits symbols/line tables/dynamic records, and writes the final header.
- `cflush`, `cput`, `wput`, `wputl`, `lput`, `lputl`, `llput`, and `llputl` buffer output and handle endian-specific integer writes.
- `asmsym` emits global, data, bss, string, file, function, frame, auto, and parameter symbols.
- `putsymb` writes one Plan 9 symbol record and updates `symsize`.
- `asmlc` emits compressed line number/PC deltas.
- `datfill` applies `ADATA`/`AINIT`/`ADYNT` records into text-string or data buffers, detects duplicate initialization, applies relocations, and serializes constants/floats/strings.
- `chipfloat` recognizes ARM64 encodable floating immediates.

Important details:
- Supports Plan 9 header type `2`, no-header modes `0`/`6`, and DLM-specific behavior.
- Uses `PADDR` to mask entry address in the 32-bit header field while also writing a full 64-bit entry.
- Handles dynamically loadable modules with `dynreloc` and `asmdyn`.

Filesystem relevance: indirect build/link infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/asm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/asmout.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7l/asmout.c

ARM64 instruction encoder for the 9front linker. It converts linked `Prog` instructions plus `Optab` classifications into one or more 32-bit machine instructions.

Key structure:
- Defines many ARM64 encoding macros for register fields, data-processing forms, branches, system operations, load/store forms, floating-point operations, ADR/ADRP, and logical shifts.
- `asmout` is the central switch over `o->type`; it covers pseudo-ops, arithmetic/logical forms, immediates, branches, shifts, multiply/divide/remainder, conditional select/compare, loads/stores, pair loads/stores, wide moves, system registers, barriers/hints, bitfield aliases, floating-point arithmetic/compare/convert, exclusive atomics, ADR/ADRP, jump tables, relocating memory operations, and huge-offset fallbacks.
- Emits instruction words according to `o->size` through `lputl`, with debug assembly dumps when requested.

Major helper functions:
- `oprrr` maps register-register, multiply, conditional, crypto, floating, and conversion opcodes to base encodings.
- `opirr` maps immediate, logical-immediate, branch-test, move-wide, system, barrier, and bitfield immediate opcodes.
- `opbit`, `opxrrr`, `opimm`, `opbra`, `opbrr`, `op0`, `opload`, and `opstore` handle specialized opcode families.
- `brdist` computes and validates PC-relative branch distances, including relocation handling for unresolved dynamic targets.
- `olsr12u`, `olsr9s`, `opldr12`, `opldr9`, `opstr12`, `opstr9`, `opldrpp`, and `olsxrr` encode load/store addressing modes.
- `omovlit` emits literal-pool loads or immediate materialization through add-from-zero.
- `opbfm` and `opextr` encode bitfield/extract forms and validate bit ranges.
- `movesize` returns log2 byte widths for load/store offset scaling.

Important details:
- Large memory offsets are decomposed through `REGTMP` materialization plus register-offset load/store forms.
- `ACASE` emits an inline jump-table dispatch sequence; `ABCASE` entries are relative to the preceding `ACASE`.
- DLM relocations are emitted for address constants and branch/case targets where required.
- Floating constants are accepted only when `chipfloat` or zero-immediate rules can encode them.

Filesystem relevance: indirect linker machine-code backend.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/asmout.c -->