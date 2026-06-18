# Group Research: group_31_9front_sources_os_plan9_9front_sys_src_cmd_1l_span_c_sources_os_plan9_645c3b4e1e7f

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1l/span.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1l/span.c

Purpose: linker span/symbol-table support for the 68000-family `1l` linker. It assigns final text PCs, resolves branch instruction sizes, computes symbol/line/stack-map output streams, and defines special linker symbols.

Key behavior:
- `span()` iteratively assigns instruction PCs from `INITTEXT`, expands branches when displacements outgrow short forms, rewrites `AADJSP` into concrete stack adjustment instructions, aligns `INITDAT`, and defines `etext` and `a6base`.
- `andsize()` computes operand extension-word size from addressing mode, symbol class, displacement range, constants, FPU constants, special registers, and A6-relative data addressing.
- `asmsym()` emits text, data, bss, file, auto, and parameter symbols via `putsymb()`.
- `asmsp()` emits compressed PC-to-stack-offset deltas; `asmlc()` emits compressed PC-to-line-number deltas.
- Uses globals from `l.h`: `firstp`, `textp`, `optab`, `mmsize`, `INITTEXT`, `INITDAT`, `A6OFFSET`, debug flags, and output macros.

Research notes:
- The branch sizing loop is bounded at 60 passes and treats zero displacement specially by forcing a 4-byte branch form.
- Static/external non-text data may use compact A6-relative forms when within signed 16-bit range.
- Symbol output supports Plan 9 path-encoded `z`/`Z` file symbols.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1l/span.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2a/a.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2a/a.h

Purpose: shared declarations for the 68020 assembler `2a`.

Key contents:
- Includes Plan 9 libc/Bio headers, the shared 68020 object ISA header `../2c/2.out.h`, and common compiler compatibility support.
- Defines assembler constants for symbol table size, hash buckets, include depth, macro depth, buffers, EOF/IGN sentinels, and lexer input macro `GETC()`.
- Declares core data structures: `Sym`, `Ref`, `Io`, `Addr`, `Gen`, `Gen2`, and `Hist`.
- `Gen` extends `Addr` with floating/string constants, indexed-address displacement, scale, field metadata, and secondary type.
- Declares global assembler state for lexer, macro/include stack, output file, symbols, histories, current pass, PC, and object output buffer.
- Prototypes assembler phases and helpers: initialization, parsing, lexing, macro handling, symbol lookup, object record output, history output, and file assembly.

Research notes:
- This header is the contract between `a.y`, `lex.c`, and common `../cc/lexbody`/`macbody`.
- Address types and opcode IDs intentionally match `2c/2.out.h`, so assembler and compiler produce compatible `.2` object streams.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2a/a.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2a/a.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2a/a.y

Purpose: Yacc grammar for the 68020 assembler language accepted by `2a`.

Key behavior:
- Parses labels, symbol assignments, instructions, and semicolon-terminated lines.
- Maps lexer token classes `LTYPE1` through `LTYPEB` to instruction operand forms, then calls `outcode()` with a populated `Gen2`.
- Supports no-operand, source-only, destination-only, source/destination, data pseudo-op, bit-field, text, relative branch, and DBcc-style instruction forms.
- Expression grammar supports constants, variables, unary sign/complement, arithmetic, shifts, bitwise operators, and parentheses.
- Addressing grammar covers constants, `$` immediates, string/floating immediates, TOS offsets, register direct modes, predecrement/postincrement address registers, symbol references through `SB`/`SP`/`FP`, statics with `<>`, branches through `PC`, and 68020 indexed addressing forms.
- Indexed forms encode `.W`/`.L` width and `*1/*2/*4/*8` scale into `Gen.index`, `Gen.scale`, and `Gen.displace`.

Research notes:
- Undefined labels are tolerated in pass 1 but diagnosed in pass 2.
- `DATA` and `TEXT` use special productions to carry width/frame metadata in `Gen.displace`.
- Bit-field syntax stores offset/width metadata in `field` fields used later by object writers/linkers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2a/a.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2a/lex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2a/lex.c

Purpose: driver, symbol/opcode initialization, and object emission for the 68020 assembler `2a`.

Key behavior:
- `main()` handles flags, include paths, `-D` defines, output selection, and parallel multi-file assembly on non-Windows systems using `NPROC`.
- `assemble()` performs two passes: pass 1 parses and resolves labels; pass 2 emits history records and object code.
- `itab[]` maps register names, special registers, width suffixes, and every assembler mnemonic to parser token class and `2.out.h` opcode.
- `cinit()` initializes `nullgen`, hash table, special symbols, opcode/register symbols, and working directory state.
- `zname()`, `zaddr()`, and `outcode()` serialize names, addresses, and instructions into Plan 9 object format with compact symbol-cache slots.
- `outhist()` writes path/history records, including Windows drive/path handling.
- Includes common `../cc/lexbody`, `../cc/macbody`, and `../cc/compat` for lexical scanning and preprocessor-like macro behavior.

Research notes:
- `outcode()` increments assembler `pc` for all non-`AGLOBL`/`ADATA` records during both passes.
- Address serialization mirrors compiler output in `2c/swt.c`, making hand assembly and compiler output link-compatible.
- FPU constants are converted through `ieeedtod()` into simulated IEEE fields.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2a/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/2.out.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2c/2.out.h

Purpose: shared 68020 object instruction/address ABI for assembler, compiler, and linker.

Key contents:
- Defines object symbol-name constants `NSYM`, `NSNAME`, register export limits, and `SYMDEF`.
- `enum as` enumerates all pseudo-ops, integer instructions, branch conditions, bit-field operations, 68020 control-register operations, and 68881/68040 FPU opcodes used by `2a`, `2c`, and `2l`.
- Addressing enum defines data/address/FPU registers, special registers, constants, stack/tree/internal compiler operands, symbol classes, file symbols, and 68040 MMU/control registers.
- Defines direct/indirect/address/index mode bit ranges through `D_MASK`, `I_MASK`, `I_INDIR`, `I_ADDR`, `I_INDEX1/2/3`, etc.
- Defines serialized-address tags: `T_FIELD`, `T_INDEX`, `T_TYPE`, `T_OFFSET`, `T_FCONST`, `T_SYM`, `T_SCONST`.
- Provides `Ieee` simulated floating-point storage used in object files.

Research notes:
- This file is the critical cross-toolchain contract. Any opcode/address change must be synchronized with assembler parser tables, compiler emission tables, and linker `optab`.
- `D_MASK = 63/(D_SRP>=63?0:1)` is a compile-time guard ensuring address base types fit under 63.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/2.out.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/cgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2c/cgen.c

Purpose: expression-level code generator for the 68020 C compiler backend.

Key behavior:
- `cgen()` recursively lowers C expression trees into `Prog` instructions, respecting addability, register pressure, side effects, function-call complexity, bit-fields, and requested result location.
- Handles scalar assignments, compound assignments, bit-field assignment/update, casts, conditional expressions, indirection, function calls, arithmetic, logical ops, comparison-to-bool generation, comma expressions, address-of, unary ops, and pre/post increment/decrement.
- Uses `regalloc()`, `regaddr()`, `regpair()`, `regret()`, `regfree()`, `gmove()`, `gopcode()`, `gbranch()`, `patch()`, `doinc()`, and bit helpers from sibling files.
- Optimizes constant multiply/shift through `mulcon()`/`shlcon()`, folds some address arithmetic into stack/TOS addressing, and chooses evaluation order from node complexity.
- `lcgen()` computes lvalues/addresses; `bcgen()` and `boolgen()` produce branch or materialized boolean results.
- `sugen()` handles structure/union and wide-value generation, including copies, compound struct literals, function returns by hidden result pointer, and rathole temporaries.

Research notes:
- `D_TOS` is used as an evaluation spill/argument-stack location when both sides contain calls or when argument order requires stack preservation.
- Division/modulo use register pairs for integer results, with quotient/remainder selected from adjacent registers.
- Several code paths warn about “non-interruptable temporary” when using `nodrat` rathole storage.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/cgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/gc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2c/gc.h

Purpose: central 68020 compiler-backend header for `2c`.

Key contents:
- Includes common C front-end state `../cc/cc.h` and target object ABI `../2c/2.out.h`.
- Defines target sizes for char/short/int/long/pointer/float/vlong/double and backend constants such as `FNX`, `INDEXED`, and side-effect flags.
- Declares backend structures: `Adr`, `Prog`, `Txt`, `Cases`, `Var`, `Reg`, `Rgn`, `Multab`, `C1`, and `Index`.
- Declares global compiler backend state for instruction list, switch cases, register allocation, variables, static/string/rathole areas, loop/dataflow arrays, register usage masks, and opcode conversion tables.
- Defines dataflow cost constants and macros for load/store/ref/call bit operations.
- Prototypes all target backend functions across expression codegen, listing, peephole, register allocation, statement generation, switch/object output, and text emission.
- Registers Plan 9 `Fmt` format specifiers for target-specific printing.

Research notes:
- `Adr` here matches object/linker address semantics but carries compiler-only `etype`.
- `Reg` is both CFG node and dataflow record for global register allocation.
- `Txt txt[NTYPE][NTYPE]` and `opxt[ALLOP][NTYPE]` are initialized in `txt.c` and drive type-dependent instruction choice.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/gc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2c/list.c

Purpose: debug/listing formatters for the 68020 compiler backend.

Key behavior:
- `listinit()` installs custom `Fmt` converters for registers, opcodes, addresses, programs, strings, bitsets, and indexed operands.
- `Bconv()` prints optimizer variable bitsets by resolving bit numbers through `var[]`.
- `Pconv()` prints a `Prog` as opcode plus formatted source/destination operands, including bit-field widths.
- `Aconv()` resolves opcode names through `anames`.
- `Dconv()` renders all compiler/linker addressing forms, including 68020 indexed modes, pre/post increment, indirection, symbol classes, constants, stack, floating constants, and string constants.
- `Rconv()` maps numeric register/special-register IDs to human-readable names.
- `Sconv()` escapes fixed 8-byte string constants.

Research notes:
- This file is non-emitting diagnostic infrastructure, but it is heavily used by debug flags and optimizer warnings.
- `Dconv()` temporarily mutates `Adr` fields while recursively formatting, then restores them.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/mul.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2c/mul.c

Purpose: multiplication-by-constant expansion table for the 68020 compiler backend.

Key contents:
- `Multab multab[]` maps selected positive integer constants to compact operation strings that synthesize multiplication using moves, adds, subtracts, and shifts.
- The comment defines the mini-language:
  - `0` copy register,
  - `1`/`2` subtract variants,
  - `3`/`4` add variants,
  - `5`/`6` self/add shifts by one,
  - letters encode larger shifts on either temporary register.
- `multabsize` exposes table length for binary search in `mulcon1()` in `swt.c`.

Research notes:
- Used by `cgen.c` for `OMUL`/`OLMUL` and by `shlcon()` for constant left shifts.
- The table favors hand-tuned short sequences for common constants up to 100 and selected larger round constants.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/mul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/peep.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2c/peep.c

Purpose: peephole and local dataflow optimizer over the compiler’s `Reg` CFG.

Key behavior:
- `peep()` first fills missing `Reg` nodes for non-pseudo instructions between optimizer CFG nodes.
- Repeatedly performs copy propagation and substitution propagation for `MOVL`, `FMOVEF`, and `FMOVED`, deleting redundant moves as `ANOP`.
- Folds `(A)` plus nearby `AADDL/ASUBL` into 68020 autoincrement/autodecrement addressing where safe.
- Removes redundant CCR save/restore pairs and redundant `TST` instructions whose condition codes are already established.
- Recognizes `TSTB (A); BLT/GE; ORB $128,(A)`-style idiom and turns it into `TAS`.
- Helper routines classify instruction sizes, condition-code behavior, register/reference usage, direct/indirect operand equivalence, and substitution legality.

Research notes:
- Copy propagation is conservative around calls, divide instructions, returns, read-alter-write instructions, address registers, and split control-flow merges.
- `excise()` does not remove nodes immediately; it rewrites programs to `ANOP`, later cleaned by `regopt()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/peep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/reg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2c/reg.c

Purpose: global register allocator and dataflow optimizer for the 68020 compiler backend.

Key behavior:
- `regopt()` builds a CFG from emitted `Prog` instructions, skipping pseudo-ops, assigning PCs, use/set bitsets, branch edges, and logarithmic search links.
- Converts branch offsets to `Reg` edges and computes loop structure using reverse postorder and approximate dominators from the Hecht-Ullman dataflow method.
- Propagates liveness and call-clobber information backward with `prop()`, then register/variable synchrony forward with `synch()`.
- Finds candidate live regions, computes benefit costs with `paint1()`, determines blocked registers with `paint2()`, chooses data/address/FPU registers with `allreg()`, and rewrites operands plus loads/stores with `paint3()`.
- Warns on used-before-set and set-but-unused variables; can excise unused stores.
- `mkvar()` maps addressable autos, params, statics, and externs to optimizer variable bits while excluding unsafe/punned/address-taken values.
- Final pass recalculates PCs, fixes branch offsets, removes `ANOP`s, and returns `Reg` nodes to a freelist.

Research notes:
- Integer/pointer values may choose either data or address registers depending on cost; floats choose FPU registers.
- Calls mark externs and live refs as clobbered; returns and text boundaries reset flow assumptions.
- `addmove()` preserves CCR around inserted moves when needed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/reg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/sgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2c/sgen.c

Purpose: statement-level code generation and expression complexity/addressability analysis.

Key behavior:
- `codgen()` emits an `ATEXT` pseudo-op for a function, calls `gen()` for the body, warns on missing return, emits fallback return, then invokes `regopt()`.
- `gen()` handles statement trees: lists, returns, labels/gotos, cases/defaults, switches, while/do/for loops, continue/break, if/else, used/set pseudo-statements, and default expression statements.
- Maintains `breakpc`, `continpc`, `nbreak`, `cases`, `retok`, and patch lists for structured control flow.
- `usedset()` emits no-op tests to influence volatile/used/set analysis.
- `noretval()` emits dead tests of return registers so the optimizer knows which return registers are live/dead.
- `xcom()` computes `complex` and `addable` values, performs local tree rewrites, detects indexed-address opportunities, rewrites power-of-two multiply/divide to shifts, and orders operands for cheaper code.
- `indx()` selects base/index/scale pieces for 68020 indexed addressing.
- `bcomplex()` prepares boolean control-flow generation; `nodconst()` encodes small constants through pointer casts for legacy APIs.

Research notes:
- Addability classes are target-specific numeric categories used throughout `cgen.c` and `txt.c`.
- Switch generation is split: `gen()` collects cases and calls `doswit()` in `swt.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/sgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/swt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2c/swt.c

Purpose: switch lowering, bit-field access, string/data/object output helpers, constant multiply expansion, and target layout rules.

Key behavior:
- `doswit()` collects, sorts, validates, and lowers switch cases through `swit1()`.
- `swit1()` chooses linear compare chains for small case counts, direct jump-table ranges for dense regions, and binary divide-and-conquer comparisons otherwise.
- `bitload()` and `bitstore()` implement signed/unsigned bit-field extraction and insertion with shifts/masks.
- `outstring()` and `outlstring()` emit byte and Rune string data into `ADATA` records under `symstring`.
- `doinc()` schedules pre/post increment and assignment side effects around expression generation.
- `setsp()`/`adjsp()` create stack-adjust pseudo-instructions; `eval()` forces non-addable expressions into registers.
- `outcode()`, `zwrite()`, `zname()`, `zaddr()`, and `outhist()` serialize compiler-emitted `Prog` lists into `.2` object files.
- `ieeedtod()` converts native doubles into simulated IEEE object format.
- `mulcon()`, `shlcon()`, and `mulcon1()` consume `multab[]` to generate shift/add/sub multiply sequences.
- `sextern()`/`gextern()` emit initialized global/static data.
- `align()` and `maxround()` define 68020 ABI layout/alignment, including big-endian argument adjustment.

Research notes:
- Direct switch tables are emitted as `ACASEW` plus static table entries materialized through `OCASE`/`ABCASE`.
- Object serialization here mirrors `2a/lex.c`; linker decoding is in `2l/obj.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/swt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/txt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2c/txt.c

Purpose: target initialization, instruction selection tables, address lowering, register allocation primitives, and low-level instruction emission for `2c`.

Key behavior:
- `ginit()` initializes target identity, register availability, register base mapping, move/cast table `txt`, operation-to-opcode table `opxt`, string/static/rathole symbols, return node, zero program, and 64-bit helpers.
- `gclean()` verifies all registers freed, flushes pending strings, computes special symbol widths, emits `AGLOBL`s, appends `AEND`, and calls `outcode()`.
- `oinit()` populates type-indexed opcode choices for byte/word/long/float/double operations.
- `nextpc()` appends a new `Prog` and increments logical PC.
- `gargs()` evaluates function arguments onto `D_TOS`.
- `naddr()` converts compiler `Node` forms into `Adr` forms, including statics/externs/autos/params, constants, address/indirection, and indexed modes.
- `regalloc()`, `regaddr()`, `regpair()`, `regret()`, and `regfree()` manage temporary data/address/FPU registers.
- `gmove()` emits typed moves and casts, including clear/extend behavior, float/int conversions, unsigned long to float adjustment, and FPCR rounding-mode changes for float-to-int.
- `gopcode()` emits a typed instruction after lowering tree operands and optional indexed operands.
- `asopt()` rewrites simple moves to `CLR`, `PEA`, or quick-constant-through-register sequences.
- `gbranch()`, `fpbranch()`, `patch()`, `gpseudo()`, and `gpseudotree()` create branches and pseudo-ops.
- `exreg()` allocates external register variables within target register limits.

Research notes:
- `ewidth[]` and `ncast[]` at file end define target size and legal no-op cast masks.
- Address registers A6/A7 are reserved early as SB/SP.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2c/txt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2l/asm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2l/asm.c

Purpose: final binary emitter and 68020 instruction encoder for linker `2l`.

Key behavior:
- `entryvalue()` resolves numeric or symbolic entry point.
- `asmb()` writes text instructions, data blocks, symbol table, stack maps, line maps, and executable headers for supported `HEADTYPE`s: legacy, Plan 9 boot, Plan 9, NeXT boot, and preprocess pilot.
- During text emission it checks span phase consistency, calls `asmins()` for each instruction, writes big-endian words to output buffer, and supports debug assembly listings.
- `asmins()` encodes each instruction using `optab[p->as].optype`, with special handling for CCR/SR/USP/control registers, FPU control registers, branches, moves, arithmetic, compare, shifts, FPU ops, bit-fields, MOVEM/FMOVEM, trap, CASEW/BCASE, MOVES, and SWAP.
- `asmea()` converts `Adr` operands into 68020 effective-address mode bits and extension words, handling direct registers, stack/TOS, branches, constants, FPU constants, quick immediates, auto/param/static/extern references, absolute addresses, A6-relative data, text references, and 68020 full indexed addressing.
- `datblk()` materializes initialized data chunks from `ADATA` records, detects overlapping initialization, resolves symbol addresses, and writes target byte order.
- `gnuxi()` and `nuxi` tables control float/integer byte ordering; `lput()`, `s16put()`, `cflush()`, and `rnd()` support file output.

Research notes:
- `ABCASE` is converted into data-table entries relative to `casepc`.
- Some branch/call encodings are selected based on final PC range, e.g. a far branch may use long extension words.
- Undefined externals are diagnosed in `asmea()` and forced to data type to continue error collection.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2l/asm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2l/compat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2l/compat.c

Purpose: tiny compatibility inclusion unit for linker `2l`.

Key contents:
- Includes `l.h`.
- Includes shared common compiler/linker compatibility implementation from `../cc/compat`.

Research notes:
- This file exists to compile the common compatibility body into the linker with `2l`’s declarations visible.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2l/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2l/l.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2l/l.h

Purpose: shared declarations and global state for the 68020 linker `2l`.

Key contents:
- Includes Plan 9 headers, shared `2.out.h`, and common compatibility declarations.
- Defines linker `Adr`, `Prog`, `Auto`, `Sym`, and `Optab` structures.
- `Adr` stores offset/displacement, string constants, branch condition pointer, IEEE constants, auto/symbol references, bit-field width, and scale.
- `Prog` stores source/destination operands, stack offset/forward pointer, link, branch target `pcond`, final PC, line, opcode, and span marks.
- Defines symbol classes: `STEXT`, `SDATA`, `SBSS`, `SDATA1`, `SXREF`, `SAUTO`, `SPARAM`, `SFILE`.
- Declares output layout globals (`HEADR`, `HEADTYPE`, `INITTEXT`, `INITDAT`, `INITRND`, sizes, buffers), symbol/library state, program lists, history state, byte-order tables, and address-mode lookup tables.
- Declares linker phases: object loading, autolib loading, patching/following/data layout/stack offsets/span/output, instruction encoding, data block writing, symbol maps, diagnostics, lookup, profiling injection, and float conversion.

Research notes:
- `CPUT` writes to a buffered output array and flushes through `cflush()` when full.
- `TNAME` resolves current text symbol for diagnostics.
- `A6OFFSET` is the base used for compact A6-relative data addressing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2l/l.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2l/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2l/list.c

Purpose: linker debug/listing formatters and diagnostics for `2l`.

Key behavior:
- `listinit()` installs custom `Fmt` converters for registers, opcodes, addresses, strings, and programs.
- `Pconv()` prints line number, opcode, operands, and bit-field metadata for a linker `Prog`.
- `Dconv()` renders linker operands, including branch targets through `pcond`, symbol-relative operands, stack/param forms, constants, quick constants, strings, FPU constants, and indexed/pre/post modes.
- `Rconv()` maps numeric data/address/FPU/special registers to names.
- `Sconv()` escapes 8-byte string constants with linker-specific printable escaping.
- `diag()` prefixes diagnostics with current function/text symbol, increments error count, and exits after too many errors.

Research notes:
- `bigP` is a temporary global used by address formatting so branch operands can print resolved target PCs.
- Formatting code mirrors `2c/list.c` but uses linker `Adr` and final branch-target information.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2l/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2l/obj.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2l/obj.c

Purpose: main linker driver, object/archive loader, symbol table manager, autolibrary resolver, profiling injection, byte-order setup, and float conversion.

Key behavior:
- `main()` parses linker flags, selects header defaults, validates `optab`, initializes address-mode tables, creates output, loads objects/libraries, then runs link phases: `patch()`, optional profiling, `follow()`, `dodata()`, `dostkoff()`, `span()`, `asmb()`, and `undef()`.
- `loadlib()` repeatedly scans autolibraries until no unresolved `SXREF` symbols are resolved.
- `objfile()` handles direct object files and Plan 9 archives with `__.SYMDEF` symbol indexes, loading only archive members needed for unresolved symbols.
- `zaddr()` decodes serialized object addresses, including fast compact formats and full tagged formats, and records auto/param minima for current function.
- `addlib()` reconstructs autolibrary paths from encoded history components, expanding `$O` and `$M`.
- `addhist()`, `histtoauto()`, and `collapsefrog()` manage file-history records and path component overflow.
- `ldobj()` reads `.2` object streams, handles `ANAME`/`ASIGNAME`, history, end records, globals, data, text, branches, quick immediates, constant arithmetic normalization, shift quicks, address-register compare/clear tweaks, and FPU immediate-to-integer substitutions.
- `lookup()` maintains hash table symbols keyed by name plus static version.
- `doprof1()` injects `__mcount` counter increments and data records; `doprof2()` injects calls to `_profin/_profout` or tracing variants.
- `nuxiinit()`, `find1()`, `find2()`, `ieeedtof()`, and `ieeedtod()` define host-to-target byte order and floating conversions.

Research notes:
- Static symbols use incrementing `version` so same-name statics from different object files remain distinct.
- Object load phase already performs target-specific instruction canonicalization before later span/encoding.
- Autolib references are encoded as `AHISTORY` records with offset `-1`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2l/obj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2l/optab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/2l/optab.c

Purpose: declarative instruction encoding table for the 68020 linker.

Key contents:
- `optab[]` is indexed by opcode enum value from `2.out.h`; `main()` checks index/opcode phase consistency.
- Each populated row supplies:
  - assembler opcode,
  - optional alternate FPU opcode (`fas`) for integer-representable FP constants,
  - source/destination extension sizes,
  - encoding class `optype`,
  - up to four raw opcode words used by `asmins()`.
- Covers integer arithmetic, moves, branches, DBcc, bit-field operations, FPU arithmetic/conversions/moves/branches, jump/call, traps, tests, MOVEM/FMOVEM, MOVES, CASEW/BCASE, and pseudo-ops.
- `mmsize[]` maps encoding class to minimum instruction size for span calculation.

Research notes:
- Rows with sparse/unimplemented opcodes contain only `{ AOP }`; `asmins()` diagnoses unimplemented combinations when encountered.
- `optype` is the switch discriminator in `asm.c`; changing an encoding class requires corresponding `asmins()` support.
- Source/destination size fields drive immediate/FPU constant extension emission and span size prediction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/2l/optab.c -->