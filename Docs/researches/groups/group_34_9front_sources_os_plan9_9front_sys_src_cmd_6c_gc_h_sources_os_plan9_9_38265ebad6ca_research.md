# Group Research: group_34_9front_sources_os_plan9_9front_sys_src_cmd_6c_gc_h_sources_os_plan9_9_38265ebad6ca

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included in subset A. All 20 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/gc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6c/gc.h

- Role: Central amd64 C compiler backend header for 9front `6c`, shared by code generation, register allocation, peephole optimization, switch lowering, and object emission.
- Defines target sizing constants for amd64 under Plan 9 compiler conventions: 4-byte `long`, 8-byte pointer/vlong/double, 4-byte float.
- Defines compiler backend IR structures: `Adr` for assembly operands, `Prog` for emitted instructions, `Case`/`C1` for switch cases, `Var` for register allocator variables, `Reg` for control-flow graph nodes, `Rgn` for allocation regions, and `Renv` for register environments.
- Declares global compiler state: program list pointers, `pc`, string literal buffering, case list state, register-use arrays, live-variable bitsets, and register allocator worklists.
- Provides liveness macros `BLOAD`, `BSTORE`, `LOAD`, and `STORE`, plus cost constants for allocation heuristics.
- Exposes prototypes for 6c modules: expression/code generation, 64-bit helpers, text/object output, switch/data output, listing formatters, register allocation, peephole optimization, target-bound helpers, and multiply/divide helpers.
- Important integration point: this header binds 6c to shared front-end headers `../cc/cc.h` and amd64 opcode/address definitions in `../6c/6.out.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/gc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6c/list.c

- Role: Debug/listing formatter registration and conversion routines for 6c amd64 assembly IR.
- `listinit()` installs Plan 9 `Fmt` handlers for `%A`, `%B`, `%P`, `%S`, `%D`, and `%R`.
- `Pconv()` formats `Prog` records, with special forms for `ADATA` and `ATEXT` that include width/frame scale fields.
- `Dconv()` formats `Adr` operands: registers, indirect register addressing, branches relative to `pc`, extern/static/auto/param symbols, constants, floats, strings, and address constants.
- `Rconv()` maps amd64 register address enum values to textual register names, including byte, general, x87, MMX, XMM, segment, descriptor, control, debug, and task registers.
- `Sconv()` escapes fixed-size string constants for printable assembly output.
- Dependency: relies on global `pc`, `var[]`, `anames[]`, and register enum layout from `6.out.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/machcap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6c/machcap.c

- Role: Target capability predicate for the 6c amd64 backend.
- `machcap(Node *n)` returns whether a front-end tree operation is directly supported or useful for machine-specific lowering.
- Accepts arithmetic, bitwise, shift, multiply, assignment-op, increment/decrement, cast, conditional/logical/list/comma, and comparison nodes.
- Uses type class tables such as `typechl`, `typev`, `typechlv`, and `typechlpv` to restrict support to char/short/long/vlong/pointer-like integer classes where needed.
- `n == Z` returns true as a test capability.
- Practical effect: feeds front-end/codegen decisions about which expression trees can be handled by 6c target code rather than generic fallback.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/machcap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/mul.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6c/mul.c

- Role: Strength reduction for multiplication by constants in the 6c amd64 backend.
- Defines small cached `Mparam` plans and algorithm tables used to express constants as shifts, adds/subtracts, and LEA-style scaled addressing.
- `lowbit()` finds the index of the lowest set bit in a 32-bit unsigned value.
- `mulparam()` searches candidate decomposition patterns and records an algorithm when a multiply can be done within a small cost threshold.
- `genmuladd()` builds an indexed-address expression and emits an address calculation, using amd64 addressing modes for multiply-add forms.
- `m0()`, `m1()`, and `m2()` map selected multiplier fragments to LEA scale factors.
- `shiftit()` emits either no-op, add-self, or shift-left for constant powers.
- `mulgen()` tries `mulgen1()` for optimized constant multiplication and falls back to `gopcode(OMUL, ...)` when no good decomposition exists.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/mul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/peep.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6c/peep.c

- Role: Peephole and local copy-propagation optimizer over 6c `Reg` control-flow nodes.
- `peep()` first completes the `Reg` graph for instructions not represented in earlier allocator passes, then repeatedly applies local transformations.
- Optimizations include redundant MOV elimination, register substitution, collapsing repeated sign/zero extension moves, converting load-after-LEA patterns, rewriting `ADD/SUB ±1` to `INC/DEC` when flags are not needed, and deleting redundant compare-with-zero after flag-setting operations.
- `needc()` conservatively detects whether carry-sensitive later instructions prevent arithmetic-to-inc/dec rewrites.
- `uniqp()` and `uniqs()` identify unique predecessor/successor paths for safe local reasoning.
- `subprop()` attempts backward register substitution to enable later copy elimination.
- `copyprop()`, `copy1()`, and `copyu()` implement flow-sensitive copy propagation with instruction-specific use/set/read-alter-write classification.
- `copyas()`, `copyau()`, and `copysub()` compare and substitute direct/indirect register or stack references.
- `storeprop()` exists for local-variable load reuse after stores but is disabled by `if(0)`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/peep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/reg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6c/reg.c

- Role: Global-ish register optimizer and liveness engine for 6c amd64.
- `regopt()` builds a `Reg` flow graph from emitted `Prog` instructions, assigns pseudo PCs, records predecessor/successor edges, and computes variable use/set bits via `mkvar()`.
- Tracks special implicit register uses for x86 instructions such as multiply/divide using AX/DX, string ops using SI/DI/CX, and I/O ops using DX.
- Performs branch target resolution, loop weighting, backward liveness propagation (`prop()`), forward register/variable synchrony propagation (`synch()`), region discovery, allocation cost calculation, register selection, code rewriting, peephole cleanup, PC recomputation, branch fixup, and NOP removal.
- Loop discovery uses reverse postorder plus approximate dominators based on the Hecht/Ullman data-flow algorithm, implemented by `postorder()`, `rpolca()`, `doms()`, `loophead()`, `loopmark()`, and `loopit()`.
- Region allocation is split into `paint1()` for cost, `paint2()` for forbidden register collection, `allreg()` for choosing an integer or XMM register, and `paint3()` for replacing memory references with register references plus inserted loads/stores.
- `mkvar()` records optimizable extern/static/param/auto variables while excluding unsafe address-taken, type-punned, or unsupported type cases.
- Register bit helpers map Plan 9 register enum values to allocator bitmasks: `RtoB()`, `BtoR()`, `FtoB()`, `BtoF()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/reg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/sgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6c/sgen.c

- Role: Expression complexity/addressability analysis and selected codegen setup helpers for 6c.
- `noretval()` emits dummy NOP references to integer and/or floating return registers to mark return-value liveness.
- `xcom()` recursively annotates expression trees with `addable` and `complex` scores used by code generation and register scheduling.
- Addressability model recognizes constants, names, registers, indirections, address-of forms, folded pointer-plus-constant expressions, and amd64 indexed addressing forms.
- Converts multiply/divide/modulo by powers of two into shifts/masks when valid, and commutes expressions to put more complex operands first.
- Builds OINDEX address expressions through `indx()` and global `idx` state, including base/index/scale extraction.
- `indexshift()` marks small left shifts as scaled-index candidates.
- Complexity penalties are added for calls, casts involving unsigned vlong to floating types, multiply/divide/modulo, and shifts/rotates.
- Comparison normalization moves constants to the left and inverts relation operators to match backend compare expectations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/sgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/swt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6c/swt.c

- Role: Switch lowering, bit-field load/store helpers, string/data literal emission, and object-code serialization for 6c.
- `swit1()` emits either linear compare/jump sequences for small switches or recursive binary-search comparisons for larger case tables.
- `bitload()` extracts C bit-fields by loading the containing cell, shifting, and masking/sign-extending according to field metadata.
- `bitstore()` masks, shifts, merges, writes back bit-field values, and optionally preserves the assigned value.
- `outstring()`, `sextern()`, and `gextern()` emit string chunks and global/static initializer DATA records.
- `outcode()` writes the compiler’s `Prog` list to the Plan 9 object format, including symbol caching with `zname()` and operand serialization with `zaddr()`.
- `outhist()` serializes file/line history records, including Windows path handling compatibility.
- `zaddr()` uses compact type flags for index, symbol, offset, 64-bit offset, float constant, string constant, and address type fields.
- `align()` and `maxround()` implement amd64 ABI/layout rules for struct elements, arguments, autos, and stack rounding.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/swt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/txt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6c/txt.c

- Role: Main amd64 code-emission support for 6c: initialization, temporary/register allocation, argument placement, node-to-address lowering, moves/conversions, opcode selection, branches, pseudo-ops, and type sizing.
- `ginit()` initializes target identity, type-class tables, synthetic nodes, string state, program state, and allocatable register sets; reserves SP, temp external registers, and selected XMM/general registers.
- `gclean()` validates register balance, flushes string literals, emits `AGLOBL` for globals/statics, emits `AEND`, and calls `outcode()`.
- `gargs()`/`garg1()` evaluate call arguments, materializing complex function calls into temporaries, placing structures by address, and using `REGARG` for the first register argument where supported.
- Register helpers include `regalloc()`, `regfree()`, `regret()`, `regsalloc()`, `regaalloc()`, `regaalloc1()`, `regialloc()`, and `regind()`.
- `naddr()` translates compiler `Node` forms into `Adr` operands, including registers, indirections, indexed addressing, names, constants, address-of, and constant-offset additions.
- `gmove()` implements load, store, integer widening/narrowing, signed/unsigned conversion, float/integer conversions, float/float moves, zero float constant optimization via XORPD, and unsigned 64-bit to float handling.
- `doindex()` and `gins()` prepare indexed operands and append emitted instructions.
- `gopcode()` maps compiler operators to amd64 opcodes by operand type, including arithmetic, bitwise ops, shifts, rotates, multiply/divide, comparisons, and floating variants.
- `gbranch()`, `patch()`, and `gpseudo()` emit control-flow and pseudo instructions; `exreg()` allocates external register numbers; `ewidth[]` and `ncast[]` define target type sizes and legal casts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/txt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6l/asm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6l/asm.c

- Role: Final executable/object image writer for the amd64 linker `6l`.
- `entryvalue()` resolves numeric or symbolic entry point, validating that symbolic entries are text unless dynamic-load-module data semantics apply.
- Provides endian-specific byte writers: `wputl()`, `wput()`, `lput()`, `llput()`, `lputl()`, and `strnput()`.
- `asmb()` writes text bytes by calling `asmins()` over each `Prog`, verifies phase consistency, writes data blocks, symbols, line tables, optional dynamic tables, and finally writes executable headers.
- Supports Plan 9 header type 2 fat header, Plan 9 32-bit header type 3, and ELF32-style header type 5 with amd64/386 machine selection.
- `datblk()` constructs initialized data blocks from DATA/INIT/DYNT records, handling float constants, string constants, integer/address constants, duplicate-init checks, symbol relocation, and endianness maps.
- `cflush()` flushes buffered output bytes.
- `rnd()` rounds signed 64-bit values to positive alignment boundaries.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6l/asm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6l/compat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6l/compat.c

- Role: Tiny compatibility include unit for the amd64 linker.
- Includes `l.h` and shared `../cc/compat`.
- This gives 6l access to common Plan 9 compiler compatibility support without duplicating implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6l/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6l/l.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6l/l.h

- Role: Central header for the amd64 linker `6l`.
- Defines linker-side `Adr`, `Prog`, `Auto`, `Sym`, `Optab`, and `Movtab` structures.
- Enumerates symbol types (`STEXT`, `SDATA`, `SBSS`, `SXREF`, `SUNDEF`, import/export types), operand classes (`Y*`), encoding templates (`Z*`), opcode prefixes (`P*`), and REX flag bits.
- Declares global linker state: output buffers, header constants, data/text sizes, symbol hash table, instruction tables, register maps, current program/text pointers, dynamic relocation state, library lists, import/export counters, and formatting strings.
- Provides prototypes for all linker phases: object loading, library loading, branch patching, code following, data layout, stack fixup, spanning/encoding, output assembly, symbol/line table emission, dynamic relocation, import/export handling, and diagnostics.
- Couples 6l to `../6c/6.out.h`, meaning compiler, assembler, and linker share amd64 opcode/address enum definitions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6l/l.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6l/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6l/list.c

- Role: Debug/listing formatting and diagnostics for 6l.
- Registers `%R`, `%A`, `%D`, `%S`, and `%P` format handlers.
- `Pconv()` formats `Prog` records with line number and special DATA/INIT/DYNT/TEXT/GLOBL scale formats.
- `Dconv()` formats linker operands, including resolved branch targets via `pcond`, external/static/auto/param symbols, constants, floats, strings, addresses, indirect operands, and indexed operands.
- `Rconv()` maps amd64 register enums to printable names, paralleling the compiler formatter.
- `Sconv()` escapes fixed-size string constants.
- `diag()` prefixes diagnostics with current text symbol when available, increments `nerrors`, and exits after too many errors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6l/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6l/obj.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6l/obj.c

- Role: Main program and object/archive reader for the amd64 linker.
- `main()` parses options, configures header defaults, initializes opcode index, operand-class coverage, register maps, buffers, defaults, and pipeline state, then loads objects/libraries and runs linker passes through `asmb()`.
- Supports Plan 9 output defaults, dynamically loadable module mode, export table generation, profiling/tracing insertion, and alternate entry/header/text/data/rounding options.
- `objfile()` loads raw object files or archives; archive loading reads the symbol table and pulls members only for unresolved external references.
- `ldobj()` decodes Plan 9 object records, handles `ANAME`/`ASIGNAME`, histories/autolibs, `ATEXT`, `AGLOBL`, `ADATA`, dynamic import/export pseudo-ops, float literal pooling, branch PC adjustment, duplicate `DUPOK` text skipping, and mode changes.
- `zaddr()` decodes compact serialized operands from object files and builds auto/param metadata for stack symbols.
- Symbol and program allocation helpers: `lookup()`, `prg()`, `copyp()`, and `appendp()`.
- Profiling helpers `doprof1()` and `doprof2()` inject counter or call-based profiling/tracing code.
- Endianness/float helpers include `nuxiinit()`, `find1()`, `find1v()`, `find2()`, `ieeedtof()`, and `ieeedtod()`.
- Import/export helpers: `undefsym()`, `zerosig()`, and `readundefs()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6l/obj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6l/optab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6l/optab.c

- Role: amd64/x86 instruction encoding table for 6l.
- Defines operand pattern arrays (`y*`) mapping accepted from/to operand classes to encoding templates and opcode widths.
- `optab[]` maps Plan 9 assembly opcodes to operand patterns, prefix rules, and raw opcode bytes.
- Covers integer arithmetic/logical ops, shifts/rotates, moves and extensions, branches/calls/returns, stack ops, string ops, segment/control/debug/task register moves, x87 FPU, MMX, SSE/SSE2/SSE3-style media operations, system instructions, fences, syscall/sysret, cmpxchg/xadd, and pseudo/data ops.
- Prefix codes express operand-size override, 0x0f opcode escape, REX.W, byte mode, SSE prefixes F2/F3, 32-bit-only, and 64-bit-only constraints.
- `opindex[]` is the runtime opcode-to-table index populated in `obj.c`.
- This file is data-centric: behavioral correctness depends on `span.c` interpreting `Y*`, `Z*`, and `P*` consistently.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6l/optab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6l/pass.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6l/pass.c

- Role: Middle linker passes: data layout, branch patching/following, stack-frame rewrite, import/export tables, and undefined checks.
- `dodata()` validates DATA records, lays out small data first, then remaining data, optionally pads with BSS under debug `j`, lays out BSS, and defines `edata`/`end`.
- `patch()` builds forward links, resolves call/jump symbols to text or imports, converts offsets to branch targets, and follows jump chains.
- `follow()`/`xfol()` reorder code by following branches, invert conditional branches where profitable, and copy short instruction runs to reduce jumps.
- `dostkoff()` computes per-function frame/become sizes, inserts stack adjust pseudo-ops, rewrites AUTO/PARAM offsets to SP-relative output form, tracks push/pop deltas, and rewrites special `RET const` become forms into stack-adjust plus jump.
- `doinit()` resolves data initializers that reference static/extern symbols.
- `import()` marks unresolved imported symbols as `SUNDEF` and assigns relocation/import indices.
- `export()` builds `_exporttab` and `.string` DATA records containing signatures, addresses, and names of exported symbols.
- Utility functions include `brchain()`, `relinv()`, `mkfwd()`, `brloop()`, `atolwhex()`, `undef()`, `ckoff()`, and local `newdata()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6l/pass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6l/span.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6l/span.c

- Role: Final instruction sizing, PC assignment, operand classification, amd64 byte emission, symbol/line table emission, and dynamic relocation output for 6l.
- `span()` iteratively encodes instructions until branch sizes stabilize, updates `INITDAT` alignment, defines `etext`, and writes final text symbol PCs.
- `oclass()` classifies operands into `Y*` classes used by `optab[]`, including immediates, registers, memory, branches, constants, special registers, XMM/MMX/x87 registers, and mode-specific register validity.
- Address encoding functions `asmidx()`, `asmandsz()`, `asmand()`, and `asmando()` emit ModRM/SIB/displacement bytes, handle REX bits, symbol relocation via `vaddr()`, and special SP/BP/R12/R13 addressing cases.
- `doasm()` interprets `Optab` patterns and `Z*` templates to emit instruction bytes, branch displacements, immediates, media op escapes, MOV special cases from `ymovtab`, byte-register rewrites for non-64-bit modes, and data pseudo bytes.
- `asmins()` wraps `doasm()` and inserts the REX prefix in the correct position after legacy prefixes and before opcode escape bytes.
- `asmsym()` and `putsymb()` emit Plan 9 symbol tables, including text, data, bss, constants, file history, frames, autos, and params.
- `asmlc()` emits compressed line-number tables.
- Dynamic relocation support is implemented by `dynreloc()`, relocation-array growth, and `asmdyn()` import/relocation table serialization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6l/span.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7a/a.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7a/a.h

- Role: Central header for the ARM64 assembler `7a`.
- Includes Plan 9 runtime headers, ARM64 object/opcode definitions from `../7c/7.out.h`, and compiler compatibility definitions.
- Defines assembler structures: `Sym` for symbols/macros, `Io` for input stack buffers, `Gen` for parsed operands, and `Hist` for file history.
- Declares constants for symbol table size, buffers, include depth, macro count, lexer EOF/IGN sentinels, and hash size.
- Declares global assembler state: lexer input, symbol hash, debug flags, include paths, macro/input stacks, line number, pass number, current `pc`, output buffer, and history lists.
- Prototypes cover two-pass assembly, lexer/parser entry points, symbol handling, macro/preprocessor support, file history, object emission, and diagnostics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7a/a.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7a/a.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7a/a.y

- Role: Yacc grammar for the ARM64 assembler syntax accepted by `7a`.
- Defines semantic value types for symbols, integer constants, floating constants, string constants, and `Gen` operands.
- Instruction grammar maps token classes (`LTYPE*`, `LMOVK`, `LDMB`, `LSTXR`, etc.) to `outcode()` or `outcode4()` calls with parsed operands and optional middle register fields.
- Covers ARM64 integer ALU, MOV/MOVK/MOVZ/MOVN, branches, conditional branches, compare/test aliases, conditional select/set, test-bit branches, system instructions, barriers/hints, load/store exclusive, text/global/data directives, word directives, floating point, fused multiply-add, SIMD/vector operands, pair moves, and END.
- Operand grammar handles immediates, float/string constants, labels/branches, static/extern/auto/param names, SP/SB/FP/PC pointer spaces, pre/post-indexed memory, register-offset addressing, shifts, extended registers, system-register args, scalar/vector/floating registers, vector lanes, and vector register sets.
- Expression grammar supports unary sign/complement and binary arithmetic, shifts, bitwise ops, and parentheses.
- Performs validation for register numbers and shift ranges in grammar actions.
- Produces Plan 9 object records indirectly through the output routines in `lex.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7a/a.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7a/lex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/7a/lex.c

- Role: Main program, symbol/instruction table, initialization, and object-output support for the ARM64 assembler `7a`.
- `main()` parses assembler options, supports `-o`, `-D`, `-I`, and parallel assembly of multiple files using `NPROC` on non-Windows systems.
- `assemble()` selects output name, configures include paths, opens the output, runs the assembler in two passes, emits history on pass 2, applies command-line defines each pass, and flushes output.
- Large `itab[]` initializes built-in symbols: register aliases, SP/SB/FP/PC names, general/floating/vector registers, system registers, condition codes, extension suffixes, barrier/system names, and ARM64 mnemonics mapped to parser token classes and opcode constants.
- `cinit()` initializes `nullgen`, clears errors/input stacks/hash table, interns built-ins, and records current working directory for history output.
- `syminit()` initializes new symbols as unresolved names.
- `cclean()` emits final `AEND` and flushes the object file.
- `zname()` and `zaddr()` serialize symbols and ARM64 operands to Plan 9 object format, including 64-bit constants, OREG/pre/post/branch/shift/ext/register-offset operands, string constants, and IEEE float constants.
- `outsim()`, `outcode()`, and `outcode4()` maintain the small symbol cache and emit two- or three-operand object records; pass 1 advances `pc` without output.
- `outhist()` emits file history records with path splitting and Windows path handling.
- Ends by including shared `../cc/lexbody`, `../cc/macbody`, and `../cc/compat`, so lexer, macro processor, include handling, and compatibility functions are shared with other Plan 9 toolchain components.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/7a/lex.c -->