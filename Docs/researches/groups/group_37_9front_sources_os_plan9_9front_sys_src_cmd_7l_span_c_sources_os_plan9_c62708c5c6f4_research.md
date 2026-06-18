# Group Research: group_37_9front_sources_os_plan9_9front_sys_src_cmd_7l_span_c_sources_os_plan9_c62708c5c6f4

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/span.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7l/span.c

This is the span and instruction-selection support for the Plan 9/9front `7l` linker, covering ARM64 text layout, literal pool placement, operand classification, and opcode-table lookup.

Key responsibilities:
- Assigns final `pc` values to linked `Prog` instructions in `span()`, accounting for alignment, instruction widths from `oplook()`, function boundaries, and `etext`/`textsize`.
- Maintains ARM64 literal pools through `addpool()`, `checkpool()`, and `flushpool()`, inserting branch-over-pool sequences when PC-relative literal references approach range limits.
- Classifies operands in `aclass()` into linker-internal classes such as register, stack/auto offset classes, add-immediate constants, bitmask constants, branch classes, external symbols, and large constants.
- Implements constant-shape recognizers for ARM64 encodings: add immediates, logical bitmask immediates, MOVK/MOVN-compatible fields, and scaled load/store offsets.
- Builds and caches opcode lookup ranges in `buildop()`, mapping many instruction aliases to shared optab entries.

Integration points:
- Depends on `l.h` definitions for `Prog`, `Adr`, `Sym`, `Optab`, opcode/class constants, and linker global state.
- `oplook()` is central to both span-time sizing and later machine-code emission.
- `aclass()` sets global `instoffset`, so callers rely on its side effect as well as its return class.

Risks and invariants:
- Literal pool range logic is architecture-sensitive; comments note an unresolved limitation that old literal values should remain referenceable until actually out of range.
- `findmask64()` contains a debug `print()` when a mask is found, which is unusual in production compiler/linker code.
- Incorrect operand class widening in `cmp()` or alias setup in `buildop()` can silently select invalid encodings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7l/span.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8a/a.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8a/a.h

This is the shared header for the 386 assembler `8a`.

Key responsibilities:
- Includes Plan 9 libc/bio headers, the 386 object/opcode definitions from `../8c/8.out.h`, and shared compatibility definitions.
- Defines assembler constants for symbol tables, include depth, macro storage, IO buffering, and lexer sentinel values.
- Declares core assembler data structures:
  - `Sym` for symbols/macros/labels.
  - `Ref` for macro reference classes.
  - `Io` for nested file/input stack buffers.
  - `Gen` and `Gen2` for assembler operands.
  - `Hist` for source history records.
- Exposes global assembler state via `EXTERN`: debug flags, include paths, input stack, history, current pc/line/pass, symbol hash table, output buffer, and current token.
- Declares lexer, parser, macro, output, include, and assembly entry-point functions.

Integration points:
- Used by both `a.y` and `lex.c`.
- The `Gen` layout must match object emission expectations in `zaddr()` and linker object readers.
- The header bridges assembler syntax parsing to the shared 386 object format in `8.out.h`.

Risks and invariants:
- Fixed-size arrays such as `NSYM`, `NSYMB`, `NINCLUDE`, and `NMACRO` are traditional Plan 9 limits; overflow handling depends on code in shared lexer/macro bodies.
- `GETC()` directly manipulates global `fi`, so lexer correctness depends on consistent buffer state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8a/a.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8a/a.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8a/a.y

This yacc grammar defines the 386 assembly language accepted by `8a`.

Key responsibilities:
- Parses labels, variable definitions, instruction lines, and expression syntax.
- Maps lexer token families such as `LTYPE0`, `LTYPE3`, `LTYPED`, `LTYPET`, and `LTYPEC` to instruction operand templates, then calls `outcode()`.
- Handles special pseudo-instructions:
  - `DATA name/size, imm`
  - `TEXT mem, [flags,] frame`
  - `GLOBL mem, [flags,] size`
  - `JMP/CALL` forms
  - `NOP`, shifts, MOVW/MOVL segment forms, SIMD compare/shuffle forms, and `CMPXCHG8B`.
- Builds `Gen` operands for registers, immediates, branches, memory references, indexed addressing, symbol references, constants, string constants, floating constants, and two-part constants.
- Supports arithmetic/bitwise constant expressions with yacc precedence.

Integration points:
- Depends on tokens and semantic types from `a.h`/`lex.c`.
- Emits parsed instructions through `outcode(int, Gen2*)`.
- Uses `pc` and pass number to resolve labels and detect undefined labels on pass 2.

Risks and invariants:
- Scale validation is delegated to `checkscale()` and permits only 1, 2, 4, or 8.
- Some syntax-specific constraints are enforced in actions, for example double-precision shifts and moves cannot already have conflicting index fields.
- Branch operands may carry unresolved symbols during pass 1 and become concrete during pass 2.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8a/a.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8a/lex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8a/lex.c

This file is the main driver, opcode/register table, initialization, and object emitter for the 386 assembler.

Key responsibilities:
- `main()` parses `-o`, `-D`, `-I`, debug flags, and supports parallel assembly of multiple files on non-Windows hosts using `NPROC`.
- `assemble()` runs the assembler in two passes: pass 1 resolves labels and pc counts, pass 2 writes history and object records.
- `itab[]` defines assembler names for pseudo-registers, x86 general registers, FPU/MMX/XMM registers, segment/control/debug/task registers, instruction mnemonics, aliases, x87 ops, conditional moves, MMX/SSE instructions, and pseudo-ops.
- `cinit()` initializes null operands, IO state, hash table, predefined symbols, and current working directory.
- `zname()`, `zaddr()`, `outcode()`, and `outhist()` write Plan 9 object records with compact symbol caching and source-history records.
- Includes shared `../cc/lexbody`, `../cc/macbody`, and `../cc/compat` for lexical scanning, macro processing, and host compatibility.

Integration points:
- Consumes grammar from `a.y`.
- Emits object format defined by `8.out.h`.
- Shares source history encoding conventions with `8c/swt.c`.

Risks and invariants:
- The symbol cache is limited by `NSYM` and wraps from slot 1.
- `outfile` is global and mutated from input filename; multi-file assembly uses child processes to isolate state.
- Object encoding depends on `Gen` fields being consistently initialized to `nullgen`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8a/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/8.out.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8c/8.out.h

This header defines the Plan 9 386 object-code instruction namespace, operand namespace, and compact object-address encoding flags.

Key responsibilities:
- Declares all assembler/linker opcode enum values from base x86 through x87, conditional moves, MMX/SSE/media instructions, far jumps, atomic ops, pseudo-ops, and `ALAST`.
- Defines operand/register codes for byte registers, word/long registers, FPU registers, segment registers, descriptor/control/debug/task registers, symbolic operands, constants, address operands, file records, indirection, MMX/XMM registers, and internal linker size markers.
- Defines object address field flags such as `T_TYPE`, `T_INDEX`, `T_OFFSET`, `T_FCONST`, `T_SYM`, `T_SCONST`, `T_OFFSET2`, and `T_GOTYPE`.
- Sets ABI register constants: no register argument (`REGARG = -1`), integer return in `AX`, floating return in `F0`, stack pointer in `SP`, and temp register `DI`.
- Defines Plan 9 archive symbol name `__.SYMDEF` and simulated IEEE double layout `Ieee`.

Integration points:
- Included by `8a`, `8c`, and `8l`.
- Any opcode order change affects assembler tables, compiler generation, linker decoding, and disassembly formatting.
- Object encoding flags are consumed by both assembler/compiler emitters and linker object readers.

Risks and invariants:
- Comment explicitly states new operations should be added only at the enum tail; stable numbering is part of the object ABI.
- `D_INDIR` is additive, so many address computations depend on arithmetic relationships among operand constants.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/8.out.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/cgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8c/cgen.c

This is the main 386 C expression and aggregate code generator.

Key responsibilities:
- `cgen()` lowers scalar expressions, assignments, calls, casts, comparisons, boolean expressions, pointer indirection, increments/decrements, bitfields, arithmetic, shifts, division, multiplication, and floating operations.
- Handles special x86 register constraints, especially `CX` for variable shifts and `AX`/`DX` for multiply/divide.
- Optimizes constant multiply/divide/modulo using helpers from `mul.c` and `div.c`.
- Delegates 64-bit/vlong operations to `cgen64()` when needed.
- `lcgen()` and `reglcgen()` compute lvalues and indirectable addresses.
- `boolgen()` lowers boolean control flow and optionally materializes boolean results.
- `sugen()` handles structure/union and 64-bit-sized copy/generation, including function returns and string-copy style aggregate moves.

Integration points:
- Emits `Prog` records via `gins()`, `gopcode()`, `fgopcode()`, `gmove()`, `gbranch()`, and `patch()` from `txt.c`.
- Uses addressability/complexity results from `sgen.c`.
- Uses bitfield helpers from `swt.c`, register allocation from `txt.c`, and 64-bit helpers from `cgen64.c`.

Risks and invariants:
- Correctness depends on balancing `regalloc()`/`regfree()` across many control-flow paths.
- Several paths temporarily reserve hard registers by incrementing `reg[]`.
- Complex subexpressions with function calls are rewritten into temporaries to preserve evaluation order.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/cgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/cgen64.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8c/cgen64.c

This file implements 64-bit integer operations for the 32-bit 386 compiler backend.

Key responsibilities:
- Represents 64-bit values as register pairs (`OREGPAIR`) or two 32-bit memory words.
- Provides endian-aware `hi64v()`, `lo64v()`, `hi64()`, and `lo64()` helpers.
- Implements `loadpair()` and `storepair()` for moving vlong values between memory, constants, and register pairs.
- Uses a compact table-driven interpreter, `biggen()`, to emit instruction sequences for 64-bit add/sub/and/or/xor, shifts, comparisons, increment/decrement, casts, and multiplication.
- Handles hard-register hazards around `AX`, `DX`, and `CX`.
- `cgen64()` is the main dispatcher for vlong operations and returns whether it handled a node.
- `testv()` emits truth tests for 64-bit expressions.

Integration points:
- Called from `cgen.c`, `sugen()`, and boolean generation.
- Uses 386 instruction emission from `txt.c`, multiplication lowering from `mul.c`, and type/addressability helpers from `gc.h`.
- `machcap()` can choose whether direct 64-bit comparison/test code paths are available.

Risks and invariants:
- The mini bytecode tables are dense and fragile; table opcode mistakes can generate subtly wrong carry, shift, or sign-extension behavior.
- Register-pair lazy allocation requires careful cleanup through `freepair()`/`zapreg()`.
- Some paths temporarily mutate node types and offsets, then restore them.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/cgen64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/div.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8c/div.c

This file optimizes integer division and modulo by invariant constants for 386 code generation.

Key responsibilities:
- Implements Granlund-Montgomery style magic-multiplier calculation in `multiplier()`.
- `sdiv()` and `udiv()` compute signed/unsigned magic multipliers, shifts, and adjustment flags.
- `sdivgen()` and `udivgen()` emit quotient-generation instruction sequences using multiply-high results in `DX`.
- `sext()` obtains sign-extension masks, using `CDQ` when possible.
- `sdiv2()` and `smod2()` optimize signed division/modulo by powers of two, including correction for negative dividends.

Integration points:
- Called from `cgen.c` for constant `ODIV`, `OMOD`, `OLDIV`, and assignment variants.
- Emits instructions through `gins()` and uses register allocation from `txt.c`.
- Assumes x86 multiply/divide conventions around `AX`/`DX`.

Risks and invariants:
- Correctness depends on unsigned/signed edge cases, especially negative divisors and `0x80000000`.
- Power-of-two signed modulo must preserve C semantics for negative operands.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/div.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/gc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8c/gc.h

This is the shared private header for the 386 C compiler backend.

Key responsibilities:
- Includes common C compiler definitions and the 386 object format.
- Defines 386 data-model sizes and `FNX` complexity marker for function-call expressions.
- Declares backend structures:
  - `Adr` and `Prog` for generated object instructions.
  - `Case`/`C1` for switch lowering.
  - `Var`, `Reg`, and `Rgn` for register optimization.
  - `Renv` for register/environment save state.
- Exposes backend globals for code stream, pc, cases, string literal buffer, register usage, register allocation analysis, live-variable sets, loop data, and optimizer regions.
- Declares function prototypes across `sgen.c`, `cgen.c`, `cgen64.c`, `txt.c`, `swt.c`, `list.c`, `reg.c`, `peep.c`, and arithmetic helpers.
- Defines bitset/liveness helper macros such as `LOAD`, `STORE`, `CLOAD`, `CREF`, and `LOOP`.

Integration points:
- Included by nearly every `8c` backend file.
- Couples the compiler backend tightly to `8.out.h` instruction and operand constants.
- `#pragma varargck` entries align Plan 9 formatters with custom conversion functions.

Risks and invariants:
- Many globals are shared mutable state; backend phases must run in expected order.
- The `rplink` macro reuses a generic node field, documented as a deliberate field steal.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/gc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8c/list.c

This file installs and implements debug/listing format conversions for the 386 compiler backend.

Key responsibilities:
- `listinit()` registers custom formatters for opcodes, programs, symbols/strings, operands, registers, and bitsets.
- `Pconv()` formats `Prog` instructions, including special `DATA` and `TEXT` pseudo-op layout.
- `Aconv()` maps opcode numbers to `anames[]`.
- `Dconv()` formats `Adr` operands, including indirect forms, branches, extern/static/auto/param references, constants, floating constants, string constants, and address constants.
- `Rconv()` maps register operand codes to textual register names.
- `Sconv()` escapes fixed-size string constants for debug printing.
- `Bconv()` formats register optimizer bitsets as variable names or offsets.

Integration points:
- Used by diagnostics and debug flags throughout `8c`.
- Depends on `anames[]`, `var[]`, `pc`, and `zprog` conventions.
- Formatting must track operand encodings from `8.out.h`.

Risks and invariants:
- `Dconv()` temporarily mutates `Adr` fields when formatting `D_ADDR`, then restores them.
- Register-name coverage must remain aligned with `D_*` numeric ranges.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/machcap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8c/machcap.c

This small file declares which operations the 386 backend can handle directly, especially for long and vlong expressions.

Key responsibilities:
- `machcap()` returns whether a node operation is supported by machine-specific generation.
- Enables direct support for multiply, bitwise/arithmetic ops, shifts, casts, conditionals, logical expressions, assignment arithmetic, increments/decrements, and comparisons.
- Handles special mixed-assignment cases by rejecting some `mixedasop()` combinations.
- A `Z` node query returns true as a general capability test.

Integration points:
- Used by shared compiler logic to decide whether machine-specific code generation is available.
- Works with `cgen64.c` and `sgen.c` decisions around vlong operations and addressability.

Risks and invariants:
- Overstating capability can route unsupported nodes into backend paths.
- Understating capability can force less optimal or unavailable generic handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/machcap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/mul.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8c/mul.c

This file optimizes multiplication by constants for the 386 compiler backend.

Key responsibilities:
- Searches compact shift/add/sub algorithms for a constant multiplier in `mulparam()`.
- Caches recent multiplier plans in `multab`.
- `lowbit()` finds the lowest set bit in a constant.
- `genmuladd()` emits LEA/index-address based multiply-add patterns.
- Helper tables/functions `m0()`, `m1()`, and `m2()` map small algorithm constants to x86 scale factors.
- `shiftit()` emits shift-left or add-doubling for small shifts.
- `mulgen()` emits optimized constant multiplication when possible, otherwise falls back to normal multiply.

Integration points:
- Called from `cgen.c` and `cgen64.c`.
- Uses `gopcode()`, `gins()`, `gmove()`, `regalloc()`, and `regfree()` from `txt.c`.
- Relies on x86 scaled-index addressing for efficient LEA sequences.

Risks and invariants:
- Algorithm selection is cost-based and limited to a hand-coded set of patterns.
- Invalid mapping in `m0`/`m1`/`m2` triggers diagnostics but would indicate internal table corruption.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/mul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/peep.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8c/peep.c

This file implements peephole and copy-propagation optimizations over the backend control-flow graph.

Key responsibilities:
- Fills missing `Reg` nodes for non-control pseudo-free instruction gaps.
- Iteratively removes redundant register-to-register `MOVL` instructions via `copyprop()` and `subprop()`.
- Simplifies sign/zero-extension chains when consecutive moves make the second extension redundant.
- Rewrites `LEAL` followed by matching load into a direct `MOVL` where safe.
- Converts add/sub by ±1 to inc/dec when condition-code users do not require carry.
- Removes compare-with-zero instructions when previous arithmetic already produced usable flags.
- Provides dataflow helpers:
  - `uniqp()`/`uniqs()` for unique predecessor/successor.
  - `copyu()` for use/set classification.
  - `copyas()`, `copyau()`, and `copysub()` for operand substitution.

Integration points:
- Invoked by `regopt()` after register allocation.
- Uses `copyu()` semantics also needed by register allocation to determine register use/set behavior.
- Emits removal by converting instructions to `ANOP`.

Risks and invariants:
- x86 implicit-register instructions are conservatively treated as blockers.
- Flag-sensitive transformations rely on `needc()` to avoid breaking carry-dependent code.
- Unknown opcodes default to unsafe read-alter-write behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/peep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/reg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8c/reg.c

This file is the 386 backend register optimizer and liveness/dataflow engine.

Key responsibilities:
- Builds a `Reg` control-flow graph from generated `Prog` instructions, excluding data/name/signature pseudo-ops.
- Tracks variable uses, sets, calls, references, register usage, and branch edges.
- Converts branch pc offsets to CFG edges and builds predecessor/successor links.
- Computes loop structure using reverse postorder and approximate dominators.
- Propagates liveness backward with `prop()` and register/variable synchrony forward with `synch()`.
- Finds profitable variable live ranges in `paint1()`, computes unavailable registers in `paint2()`, and rewrites instructions in `paint3()`.
- Inserts load/store moves around allocated regions using `addmove()`.
- Removes unused sets and runs peephole optimization.
- Recomputes pc values and branch offsets after optimization, then removes nops.

Integration points:
- Called by the compiler after initial code generation.
- Uses `mkvar()` to map `Adr` operands to tracked variables.
- Uses peephole helpers from `peep.c` and bitset helpers from common compiler code.

Risks and invariants:
- Only a bounded number of variables (`NVAR`) can be optimized.
- Punned or address-taken variables are marked in `addrs` and avoided.
- Correctness depends on accurate `copyu()` classification for implicit-register x86 instructions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/reg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/sgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8c/sgen.c

This file computes expression complexity and addressability for the 386 backend.

Key responsibilities:
- `noretval()` emits synthetic use markers for integer and floating return values to prevent incorrect unused-return assumptions.
- `commute()` reorders commutative operands by complexity.
- `indexshift()` detects shift-left patterns usable as x86 scaled indexes.
- `xcom()` is the main complexity/addressability pass, classifying constants, names, registers, addresses, indirections, indexed addressing, arithmetic, shifts, multiply/divide/modulo simplifications, comparisons, calls, and 64-bit operations.
- Rewrites power-of-two multiply/divide/modulo into shifts or masks where valid.
- Folds address constants into base expressions.
- Builds `OINDEX` nodes for x86 base/index/scale addressing.
- `indx()` chooses base and index trees and records them in global `idx`.

Integration points:
- Runs before `cgen()` to guide register allocation and addressing choices.
- Depends on shared compiler helpers like `vlog()`, `side()`, `simplifyshift()`, `rolor()`, `com64()`, and type tables.
- `txt.c` later consumes `idx` through `doindex()`/`naddr()`.

Risks and invariants:
- `addable` numeric classes are local compiler conventions; many later code paths assume their exact meanings.
- Some transformations mutate tree structure and type fields.
- Indexed addressing is skipped for expressions with side effects.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/sgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/swt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8c/swt.c

This file groups several backend support tasks: switch lowering, bitfields, string/global data output, object emission, history records, and alignment.

Key responsibilities:
- `swit1()` emits switch dispatch as linear comparisons for small case counts and binary-search comparisons for larger sets.
- `bitload()` and `bitstore()` load, mask, sign/zero extend, and write packed bitfields.
- `outstring()` accumulates string literals into `ADATA` chunks.
- `sextern()` and `gextern()` emit static/global data initializers, including vlong constants split into low/high words.
- `outcode()` writes compiler-generated object instructions to the output file with symbol caching.
- `outhist()`, `zname()`, and `zaddr()` emit source history, symbol-name, and operand records in the Plan 9 object format.
- `align()` and `maxround()` implement 386 ABI layout rules for structs, params, and autos.

Integration points:
- Shares object encoding behavior with `8a/lex.c`.
- Used by front-end global initializer logic and backend code emission.
- Depends on `gc.h`, `8.out.h`, source history globals, and type layout tables.

Risks and invariants:
- `outcode()` appends to an already-open output path and then clears `firstp`/`lastp`.
- Alignment is little-endian-specific for arguments.
- Bitfield operations assume 32-bit container arithmetic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/swt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/txt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8c/txt.c

This is the 386 backend instruction emitter, register allocator, argument placer, move/conversion generator, and backend initializer/finalizer.

Key responsibilities:
- `ginit()` initializes architecture identity, listing formats, code stream state, special nodes, string state, 64-bit support, and register availability.
- `gclean()` validates register balance, flushes string literals, emits `GLOBL` records, writes `AEND`, and calls `outcode()`.
- `nextpc()` allocates new `Prog` records.
- `gargs()`/`garg1()` evaluate and place call arguments, using temporaries for function-valued subexpressions.
- Provides register helpers: `regalloc()`, `regfree()`, `regret()`, `regsalloc()`, `regaalloc()`, `regind()`, and `nodreg()`.
- `naddr()` translates compiler `Node` addressing forms into object `Adr` operands.
- `gmove()` emits loads, stores, integer conversions, float conversions, and float/integer conversion sequences.
- `gins()`, `gopcode()`, `fgopcode()`, `gbranch()`, `patch()`, and `gpseudo()` are the primary instruction emission APIs.
- Defines type widths and cast masks for the 386 ABI.

Integration points:
- Used by nearly all code-generation files.
- Consumes addressability and indexed-address decisions from `sgen.c`.
- Emits opcodes defined in `8.out.h` into `Prog` records later optimized and serialized.

Risks and invariants:
- Register accounting is manual; leaks are reported in `gclean()`.
- Float conversion uses x87 control-word manipulation when truncation behavior is required.
- `doindex()` relies on global `idx` state set by `sgen.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8c/txt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8l/asm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8l/asm.c

This file writes final executable output for the 386 linker.

Key responsibilities:
- `entryvalue()` resolves numeric or symbolic entry points, validating that symbolic entries are text unless dynamic linking permits data adjustment.
- Provides endian-specific byte emitters: `wputl()`, `wput()`, `lput()`, `lputl()`, and fixed-width `strnput()`.
- `asmb()` is the main output pass:
  - Seeks past headers.
  - Emits text by walking `firstp`, checking phase consistency, calling `asmins()`, and flushing instruction bytes.
  - Emits data blocks with `datblk()`.
  - Emits symbols, stack/line tables, and dynamic-linking data when enabled.
  - Writes final headers for multiple `HEADTYPE`s: historical/COFF-like, Unix COFF, Plan 9, DOS COM/EXE, and 32-bit ELF.
- `cflush()` flushes buffered output.
- `datblk()` materializes data initializers, floats, strings, addresses, relocations, and duplicate initialization checks.
- `rnd()` rounds values to alignment boundaries.

Integration points:
- Depends on `l.h` linker globals and `asmins()` machine instruction encoding.
- Uses data layout from `dodata()`/`doinit()` and symbol tables built by object loading.
- Supports dynamic relocations through `dynreloc()` and `dlm`.

Risks and invariants:
- Phase errors indicate span/emission size mismatches.
- Header math is highly format-specific and tied to `INITTEXT`, `INITDAT`, `HEADR`, and `INITRND`.
- `datblk()` must honor Plan 9 byte-order maps (`inuxi*`, `fnuxi*`) for portable output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8l/asm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8l/compat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8l/compat.c

This tiny file includes linker definitions and the shared C compiler compatibility implementation.

Key responsibilities:
- Includes `l.h`.
- Includes `../cc/compat`, making shared compatibility routines part of the `8l` build.

Integration points:
- Allows the linker to reuse host/platform compatibility helpers used by the compiler and assembler family.

Risks and invariants:
- This is an include-wrapper source file; its behavior is entirely determined by the included compatibility body.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8l/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8l/l.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/8l/l.h

This is the shared private header for the 386 linker `8l`.

Key responsibilities:
- Includes Plan 9 libc/bio headers, 386 object definitions, and shared compatibility declarations.
- Defines linker-side structures:
  - `Adr` with unions for offsets, string constants, branches, IEEE constants, autos, and symbols.
  - `Prog` for linked instructions, pc, branch/work pointers, cached operand classes, and marks.
  - `Auto` for automatic variables.
  - `Sym` for linker symbols and metadata.
  - `Optab` for instruction encoding table entries.
- Defines symbol types, hash sizes, IO sizes, history limits, operand classes (`Y*`), encoding forms (`Z*`), prefix constants, and relocation bit allocations.
- Declares global linker state for headers, text/data sizes, buffers, symbols, libraries, pc, debug flags, instruction bytes, endian maps, dynamic linking/import/export state, and current instruction/text pointers.
- Declares functions used across linker passes: object loading, library loading, span, patch/follow, data layout, symbol output, relocation, instruction encoding, diagnostics, and conversions.

Integration points:
- Included by `8l` implementation files such as `asm.c`, `span.c`, object readers, and instruction encoders.
- Shares opcode and operand numbering with `8a`/`8c` via `8.out.h`.
- The `cput` macro and output buffer globals are consumed by `asm.c`.

Risks and invariants:
- Operand and encoding class enums must stay aligned with optab tables.
- Many fields have phase-specific meanings, for example `Prog.width` as fake DATA width and `Adr.cond` as an unused branch-shaped union member.
- Dynamic-linking state is globally shared and format-sensitive.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/8l/l.h -->