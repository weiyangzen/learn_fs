# Group Research: group_160_9front_sources_os_plan9_9front_sys_src_cmd_ka_lex_c_sources_os_plan9_4a8db937a0f2

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ka/lex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ka/lex.c

SPARC assembler front-end for the `ka` tool. It initializes target identity (`thechar='k'`, `thestring="sparc"`), parses assembler options, supports parallel assembly of multiple files on non-Windows hosts, and runs the assembler in two passes. The large `itab` table binds register names, pseudo-registers, opcodes, branches, traps, floating-point operations, and scheduling controls into the lexer symbol table.

Object output is encoded through `zname`, `zaddr`, and `outcode`, using compact symbol cache slots and little byte writes for offsets/floating constants. `outhist` serializes source history path elements as `ANAME`/`AHISTORY` records, with Windows path handling. The file ends by including shared C compiler lexer/macro/compat bodies from `../cc`, so this is architecture-specific setup around common Plan 9 compiler infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ka/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kbmap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kbmap.c

Graphical Plan 9 keyboard map selector. It enumerates keyboard map files from `/sys/lib/kbmap` unless explicit files are passed, lays them out as clickable rectangles, and writes the selected map into `/dev/kbmap`. The UI uses `draw`/`event` primitives, two blue image fills for normal/current state, and mouse button 3 release-on-same-item selection semantics.

`writemap` copies map files to `/dev/kbmap` without writing partial lines, buffering until a newline is available. `geometry`, `redraw`, and `eresized` keep the map grid responsive to window size. Keyboard input only handles quit (`q` or delete). This is a user-facing wrapper around the kernel keyboard map device, not a filesystem component.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kbmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kbremap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kbremap.c

Small keyboard-map cycling filter. It installs an initial map, appends a synthetic `Kswitch` mapping to `/dev/kbmap`, then reads keyboard event records from stdin. When it sees a `c` event whose rune equals `Kswitch`, it advances to the next map file argument and rewrites `/dev/kbmap`; all other events are passed through unchanged.

Options `-m` and `-k` choose the modifier and scancode for the switching key. The program `chdir`s to `/sys/lib/kbmap`, so map names can be relative. Like `kbmap.c`, its writer avoids half-line updates. It is useful in a pipeline where keyboard events flow through the remapper.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kbremap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/cgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kc/cgen.c

Main expression and structure code generator for the SPARC C compiler backend. `cgen` handles scalar expression lowering: assignment, arithmetic, compound assignment, function calls, indirection, comparisons, boolean operators, casts, conditional expressions, and pre/post increment. It coordinates evaluation order using node complexity, allocates temporary registers, preserves function-call results through stack temporaries when needed, and delegates bitfields and structures to helper paths.

`boolgen` emits compare/branch sequences and optional materialized boolean values. `lcgen`/`reglcgen` compute l-values and fold small constant offsets into indirect references. `sugen` copies structures/unions, handles struct literals and function-returned aggregates, and emits looped or unrolled longword copies through `layout`. This file is central to SPARC-specific C AST-to-`Prog` lowering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/cgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/gc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kc/gc.h

Shared SPARC compiler backend header. It defines target sizes, object address and instruction records (`Adr`, `Prog`), switch-case metadata, multiply-constant tables, register allocator variables (`Var`, `Reg`, `Rgn`), global backend state, bitset macros, cost constants, and function prototypes for all backend modules.

The header binds this compiler to `../kc/k.out.h` opcode/address enums and `../cc/cc.h` frontend types. Its declarations describe the backend phases: code generation (`cgen`, `sugen`), instruction emission (`txt.c`), switch/bitfield/data output (`swt.c`), listing formatters, register allocation, peephole optimization, and 64-bit helper code. It is the integration point for this architecture port.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/gc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/k.out.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kc/k.out.h

Object-format and architecture enum header for SPARC `k` tools. It defines symbol-name and register counts, special general and floating registers, all assembler/compiler opcodes (`A*`), address name/type constants (`D_*`), ranlib `SYMDEF`, and the `Ieee` split-double representation used when serializing floating constants.

The register comments document compiler allocation policy: integer temporaries grow upward from `R7`, external integer registers grow downward from `R6`, and floating register variables occupy even F registers. These constants are shared by assembler, compiler, linker, and related diagnostics, making enum stability important for object compatibility.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/k.out.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kc/list.c

Formatting support for SPARC compiler backend diagnostics and debug dumps. `listinit` installs Plan 9 `Fmt` converters for instructions, opcodes, addresses, string constants, symbolic names, and bitsets. `Pconv` renders `Prog` instructions with special formatting for `ADATA` and `ATEXT`; `Dconv` and `Nconv` print address modes and symbolic offsets.

`Bconv` prints variable bitsets using the global `var[]` table. `Sconv` escapes fixed-width string constants using Plan 9-style escapes. This file has no code-generation logic, but is essential for readable debug output under backend debug flags.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/mul.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kc/mul.c

Constant-multiply sequence generator for the compiler. It searches for short shift/add/sub instruction strings that multiply by a constant, caches recent constants in `multab`, and falls back to a large curated hint table for constants the search misses. The mini-language encodes shifts as letters and arithmetic as `+`/`-` plus operand selection digits.

`mulcon0` normalizes negative constants, checks cache, probes hints, searches up to bounded sequence length, and recursively handles trailing powers of two. `docode`, `gen1`, `gen2`, and `gen3` perform the constrained search and validate candidate sequences against `mulval`. The result is consumed by `swt.c:mulcon` to emit real SPARC operations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/mul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/peep.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kc/peep.c

Peephole and copy-propagation optimizer over the register flow graph produced by `reg.c`. It first fills gaps in the `Reg` graph for non-data pseudo instructions, then repeatedly removes redundant register moves via `copyprop` and `subprop`. It also eliminates repeated sign/zero extension moves such as `MOVB x,R; MOVB R,R`.

The optimizer classifies instruction register effects with `copyu`: read, write, read-alter-write, or untouched. Helper functions detect direct and indirect register use (`copyas`, `copyau`, `copyau1`) and substitute registers in operands. It is conservative around jumps, calls, returns, and unknown opcodes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/peep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/reg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kc/reg.c

Global register allocator and liveness optimizer for SPARC compiler output. `regopt` builds a control-flow graph from `Prog` instructions, maps branch targets, detects loops, propagates live references/call-saved requirements, identifies profitable live ranges, assigns available integer or floating registers, rewrites memory operands into registers, runs peephole optimization, recalculates PCs, fixes branches, and removes nops.

The allocator tracks variables through `mkvar`, liveness through `prop`, register/value divergence through `synch`, and candidate regions through `paint1`/`paint2`/`paint3`. Loop weights raise region cost. `RtoB`/`BtoR` and `FtoB`/`BtoF` encode allocatable register sets. This is the backend’s main optimization pass.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/reg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/sgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kc/sgen.c

Addressability and complexity analysis for backend expression trees. `xcom` computes `addable` classes and register complexity, rewrites multiply/divide/modulo by powers of two into shifts/masks, normalizes immediate operands to the right side for commutative and comparison operations, and marks function calls as high-complexity barriers.

The comments define the compact addressability lattice used by `cgen`: constants, names, registers, indirect registers, address-of combinations, and constant-offset additions. After local rewrites, it invokes `com64` for 64-bit transformations. This file feeds evaluation-order decisions and direct-address emission in later codegen phases.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/sgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/swt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kc/swt.c

Mixed backend support file covering switch lowering, bitfields, string/data emission, final object serialization, and type alignment. `swit1`/`swit2` emit binary-search switch dispatches with direct small-constant comparisons where possible. `bitload` and `bitstore` generate masking/shifting sequences for signed and unsigned bitfields.

`mulcon` consumes `mul.c` sequences to replace integer multiply-by-constant with shifts/add/subs. `outcode`, `zwrite`, `zname`, `zaddr`, and `outhist` serialize the final instruction stream and history records. `gextern`, `sextern`, and `outstring` generate initialized data records. `align` and `maxround` encode SPARC ABI layout and stack/argument alignment policy.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/swt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/txt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kc/txt.c

Instruction emission, register allocation helpers, calling convention support, moves/conversions, branches, pseudo-ops, and target type tables for the SPARC C compiler backend. `ginit` initializes target globals, special nodes (`.safe`, `.rathole`, `.ret`), register reservations, and 64-bit support; `gclean` flushes pending strings/globals and writes `AEND`.

`gmove` is the large conversion/move matrix for integer, pointer, float, double, memory, and constant cases, including special floating constants and rathole-mediated conversions. `gopcode` maps frontend operations to SPARC opcodes and compare-branch pairs. The file also defines argument placement, stack temporaries, external register assignment, small-immediate tests, and target width/cast compatibility tables.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kc/txt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/bpt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ki/bpt.c

Breakpoint management for the `ki` SPARC interpreter/debugger. It supports instruction breakpoints plus memory read, write, access, and “equal value” watchpoints. `breakpoint` parses the breakpoint modifier, evaluates the address expression, stores pass counts, and links into `bplist`; `delbpt` removes by address.

`brkchk` is called from instruction fetch/memory access paths and stops execution by setting `count=1` and `atbpt=1` when counts expire or equal-watch values match. `dobplist` formats active breakpoints using `symoff` against text or data symbols.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/bpt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/cmd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ki/cmd.c

Interactive command interpreter for `ki`. It parses simple address expressions, repeats the last command on blank input, supports breakpoint/run/continue/step commands via `:`, debugger summaries and register dumps via `$`, memory examination via `/` and `?`, expression evaluation via `=`, and register assignment via `>`.

`pfmt` implements output formats for octal/decimal/hex integers, bytes, characters, strings, symbols, globals, disassembly, source locations, and line breaks. `colon` integrates with execution control and reports stopped/breakpoint locations. `catcher` maps interrupts into debugger stops. This file is the user interface over the simulator core.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/float.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ki/float.c

Floating-point instruction emulation for `ki`. It implements single/double FP loads and stores, alignment checks, FP comparisons with ordered/unordered condition encoding in `fpsr`, floating branches with annul and delay-slot behavior, and arithmetic/conversion operations for add, sub, mul, div, integer/float conversion, move, negate, abs, and single/double conversion.

The code updates simulated FP register unions directly and uses `longjmp(errjmp, 0)` for exceptions such as alignment faults, invalid FP registers, and divide-by-zero. It cooperates with `run.c` dispatch tables through `fcmp`, `fbcc`, and `farith`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/float.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/icache.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ki/icache.c

Placeholder instruction-cache hook file for `ki`. `icacheinit` is empty, and `updateicache` only marks its address parameter used. The simulator’s memory fetch path still checks `icache.on` and calls `updateicache`, but this backend does not model cache state or stalls here.

This file exists to satisfy the shared simulator interface declared in `sparc.h` and used by `mem.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/icache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/ki.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ki/ki.c

Program entry and process/image initialization for the SPARC interpreter/debugger. `main` opens a SPARC executable or attaches to a process ID, initializes symbols and memory maps, builds the simulated stack, seeds special FP constants, and enters the command loop.

`initmap` creates lazy paged text, data, bss, and stack segments. `inithdr` reads Plan 9 executable headers and symbol maps through `mach` APIs. `procinit` snapshots `/proc/<pid>` memory and register state for debugging a live process. Utility routines reset state, build argc/argv/Tos stack layout, print registers, allocate memory, and emulate 32x32-to-64 multiplication.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/ki.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/mem.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ki/mem.c

Memory access layer for `ki`. `ifetch` enforces instruction alignment, triggers icache hooks, profiles text addresses, and fetches big-endian 32-bit instructions. Data accessors provide byte, halfword, word, and vlong reads/writes with SPARC big-endian layout and alignment checks.

`memio` copies between simulated memory and host buffers for syscall emulation, including bounded string reads. `vaddr` translates simulated virtual addresses into lazily allocated segment pages, loading text/data from the executable via `pread` and zero-filling bss/stack. Invalid addresses raise simulated MMU misses through the debugger error path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/run.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ki/run.c

Core SPARC instruction dispatch and integer/control instruction emulator for `ki`. It defines opcode tables for format-0, format-2, and format-3 instruction classes, then `run` repeatedly fetches, dispatches, increments PCs, and checks instruction breakpoints. `delay` executes branch delay slots, and branch handlers implement annul semantics.

The file covers arithmetic/logical ops, condition-code variants, shifts, Y register access, `mulscc`, loads/stores, `ldstub`, `swap`, `sethi`, calls, jumps, and integer/FP branches. It tracks instruction counts, taken branches, delay-slot use, nops, and load interlocks. Unsupported encodings call `undef` and return to the debugger.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/run.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/sparc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ki/sparc.h

Central simulator header for `ki`. It defines SPARC user-address constants, breakpoint types, instruction categories, instruction-cache metadata, decoded instruction descriptors, CPU register state, memory segment structures, syscall/memory IO directions, and Plan 9 stack/text constants.

It declares all simulator, debugger, memory, syscall, breakpoint, profiling, and symbol-trace functions, plus global state such as `reg`, `memory`, `bplist`, `icache`, `iprof`, `symmap`, and tracing flags. Macros decode SPARC operand fields, sign-extend immediates, define PSR condition bits, and name FP compare outcomes. The header also documents portability assumptions for FP register layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/sparc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/stats.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ki/stats.c

Runtime statistics and profiling output for `ki`. `isum` walks all instruction tables, prints per-op counts, aggregates loads/stores/arithmetic/FP/special-register/syscall/branch counts, and reports estimated instruction, data, stall, annulled, and delay-slot cycles.

`segsum` prints resident bytes and reference counts for stack/text/data/bss segments. `iprofile` aggregates instruction-profile counters by text symbol, sorts hot functions by count, prints cycle percentages with source locations, and clears the profile array. This file is diagnostic-only and consumes counters maintained by `run.c` and `mem.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/symbols.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ki/symbols.c

Symbol/source helpers for `ki` debugger output. `printsource` maps a PC to file:line text. `printlocals` and `printparams` use Plan 9 symbol APIs to locate auto variables and parameters and read their values from simulated stack memory.

`stktrace` walks SPARC stack frames from current `pc` and `sp`, using `.frame` local metadata and saved return PCs. It prints function names, parameters, source locations, callers, and optionally locals for `$C`, truncating after 40 frames. This file bridges the simulator’s memory model and libmach symbols.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/symbols.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/syscall.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ki/syscall.c

Plan 9 syscall emulation for `ki`. It maps SPARC user register/stack arguments to host Plan 9 libc calls, copying buffers through simulated memory with `memio`. Implemented calls include errstr, fd2path, bind, chdir, close, dup, exits, open, read/pread, seek/oseek, rfork without `RFPROC`, sleep, stat/fstat old and new forms, write/pwrite, pipe, create, brk, remove, notify, and segflush.

Many process/namespace/segment calls intentionally report unsupported and exit. `systab` indexes handlers by `/sys/src/libc/9syscall/sys.h` numbers, and `ta` dispatches traps using return register `R7`, with optional syscall tracing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ki/syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/asm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kl/asm.c

Assembler/output backend for the SPARC linker `kl`. `asmb` writes text, data, symbols, line tables, and executable headers for supported `HEADTYPE`s. It verifies PC phase, calls `oplook`/`asmout` for instruction encoding, emits initialized data blocks, serializes symbols and source line tables, and writes final headers with text/data/bss/symbol sizes and entry value.

`datblk` materializes initialized data with endian conversion and relocation-like symbol value resolution. `asmout` is the main lowering matrix from `Prog`/`Optab` classes to SPARC machine words, including immediates, large constants, branches, calls, traps, FP loads/stores/arithmetic, div/mod expansion, and annulled delay-slot opportunities. `opcode` maps internal `A*` opcodes to SPARC encodings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/asm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/compat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kl/compat.c

Thin compatibility inclusion unit for the SPARC linker. It includes `l.h` and then the shared compiler/linker compatibility body from `../cc/compat`.

There is no local logic here; its purpose is to compile common compatibility routines in the `kl` build with the linker’s declarations and global context available.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/l.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kl/l.h

Primary header for the SPARC linker. It defines linker-side `Adr`, `Prog`, `Sym`, `Auto`, and `Optab` structures; mark flags for scheduling/control-flow analysis; symbol classes; operand classes; buffer globals; layout configuration; linker global state; opcode range tables; and prototypes for all linker passes.

It includes `../kc/k.out.h`, so linker instruction/address enums match compiler and assembler output. The declarations cover object loading, library loading, symbol resolution, data layout, branch patching, no-op/prologue rewriting, scheduling, span computation, assembly output, symbol/line table emission, and diagnostics. This is the shared contract for the `kl` modules.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/l.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kl/list.c

Formatting and diagnostics support for the SPARC linker. It installs `Fmt` converters, prints assembly instructions, formats opcodes, addresses, branch targets, symbolic offsets, and string constants, and emits linker diagnostics with current text symbol context.

Compared with the compiler formatter, linker `Dconv` understands linker-resolved branch targets through `curp->cond`, P registers, ASI operands, and floating constants stored as split IEEE words. `diag` increments global error count and exits after too many errors. This file supports debug listings and human-readable error messages throughout `kl`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/noop.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kl/noop.c

Linker pass for pseudo-op cleanup, frame/prologue/epilogue synthesis, branch labeling, multiply/divide helper expansion, and instruction scheduling boundaries. `noops` first strips nops, marks labels/sync points/branches/floating ops, detects leaf functions, records frame and “become” sizes, and marks branch targets.

It then adjusts caller frames for `BECOME`, inserts stack adjustment and saved-link prologue code, expands returns differently for leaf and non-leaf functions, rewrites integer mul/div/mod into calls to `_mul`, `_div`, `_divl`, `_mod`, or `_modl` when hardware/debug settings require it, and invokes `sched` on bounded basic blocks. `addnop` and `initmuldiv` support those transformations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/noop.c -->