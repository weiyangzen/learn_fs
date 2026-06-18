# Group Research: group_170_9front_sources_os_plan9_9front_sys_src_cmd_qa_lex_c_sources_os_plan9_1e8fc9333456

Scope checked: `Docs/research_subset_a.md` includes `sources/os/plan9/9front`. The referenced internal group report path was not present, so this report is derived from complete reads of the listed source files.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qa/lex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qa/lex.c

Power/PowerPC assembler front-end for `qa`. It sets `thechar='q'`, initializes assembler symbols and instruction/register names, runs a two-pass assembly over `.s` input, and writes Plan 9 object records.

Key responsibilities:
- `main` parses `-o`, `-D`, `-I`, supports parallel multi-file assembly via `NPROC`, and blocks multi-file assembly on Windows.
- `assemble` sets include paths, output name, pass 1/pass 2 parsing, preprocessor definitions, and history emission.
- `itab` maps Power register names, condition registers, special registers, directives, and opcodes to parser token classes and opcode values.
- `zname`, `zaddr`, `outcode`, and `outgcode` serialize symbols, operands, two-operand instructions, and three-operand/fused instructions to object output.
- `outhist` emits source history/path metadata, including Windows path handling.

Dependencies and coupling:
- Includes `a.h`, `y.tab.h`, and shared compiler bodies `../cc/lexbody`, `../cc/macbody`, `../cc/compat`.
- Uses opcode/address constants from the Power assembler/linker world.
- Shares object encoding conventions with `qc/swt.c`.

Filesystem/OS relevance:
- Mostly toolchain code, but directly handles pathnames, include search paths, output object creation, and source history records used by Plan 9 tools.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qa/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/cgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qc/cgen.c

Core expression code generator for the Power C compiler backend. It lowers C AST nodes into target-neutral backend calls such as `gmove`, `gopcode`, `gbranch`, `patch`, and structure copy helpers.

Key responsibilities:
- `cgen` handles scalar expressions, assignments, arithmetic, calls, indirection, casts, conditionals, increments/decrements, bitfields, and 64-bit dispatch.
- `genasop` implements compound assignments while preserving left-side side effects.
- `reglcgen` and `lcgen` compute lvalues/addresses.
- `boolgen` and `bcgen` generate conditional branches and boolean materialization.
- `sugen` handles structure/union copies, structure literals, function returns by hidden pointer, and rathole temporaries.
- `layout` emits unrolled word-copy loops for larger aggregate copies.
- `cmpv`, `testv`, `cgen64`, and helpers implement `vlong`/`uvlong` comparison, constants, casts, calls, and register-pair handling.

Dependencies and coupling:
- Relies heavily on `txt.c` for actual instruction selection/emission and `swt.c` for bitfield support.
- Depends on common `cc` AST/type metadata and `gc.h` backend structures.
- Uses Power-specific 32-bit halves for 64-bit values, with endian checks via `align(..., Aarg1)`.

Notable behavior:
- Complex function-call subexpressions are spilled to stack temporaries to protect evaluation order.
- Some comments mark rough edges, such as function returns clobbering ratholes and incomplete float/vlong conversion handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/cgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/gc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qc/gc.h

Shared header for the Power C compiler backend. It defines target sizes, object operand/program structures, register-allocation graph structures, global backend state, and cross-file function prototypes.

Key contents:
- Target data model: 32-bit `char/short/int/long/pointer`, 64-bit `vlong/double`.
- `Adr`, `Prog`, `Case`, `C1`, `Multab`, `Hintab`, `Var`, `Reg`, and `Rgn`.
- Backend globals for instruction list, switch cases, register allocation, string emission, rathole temporaries, and liveness bitsets.
- Power register policy: `REGRET`, `REGARG`, `REGMIN..REGMAX`, `REGEXT`, `REGTMP`, floating return/constants/register-variable ranges.
- Prototypes for `sgen.c`, `cgen.c`, `txt.c`, `swt.c`, `list.c`, `reg.c`, `peep.c`, and `com64.c`.

Dependencies and coupling:
- Includes the common C compiler header `../cc/cc.h` and Power object definitions `q.out.h`.
- Defines macros used by register allocation (`LOAD`, `STORE`, `BLOAD`, `BSTORE`) and register-variable bit mappings.

Filesystem/OS relevance:
- Toolchain support header; no direct filesystem behavior, but central to compiling Plan 9 Power binaries.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/gc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qc/list.c

Formatting/debug printing support for the Power compiler backend.

Key responsibilities:
- `listinit` installs custom formatters for opcodes, programs, symbols, operands, nodes, and bitsets.
- `Bconv` prints liveness/variable bitsets using `var[]`.
- `Pconv` formats `Prog` instructions, including `DATA`, `TEXT`, normal two-operand, and `from3` three-operand instructions.
- `Aconv` maps opcode numbers through `anames`.
- `Dconv`, `Sconv`, and `Nconv` format addressing modes, string constants, and symbol-relative names.

Dependencies and coupling:
- Depends on `gc.h`, `anames`, `pc`, and register/address constants.
- Used by debug flags in codegen, register allocation, and peephole optimization.

Notable behavior:
- Handles Power-specific register classes (`R`, `F`, `C`) and Plan 9 symbol names (`SB`, `SP`, `FP` style).
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/machcap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qc/machcap.c

Target capability filter for the Power backend. `machcap` tells the common compiler which operations this backend can lower directly.

Key responsibilities:
- Accepts 64-bit arithmetic/logical/shift support for selected operations.
- Accepts multiply and compound multiply in several cases.
- Accepts boolean, comparison, conditional, comma/list, logical, increment/decrement, and many compound assignment operations.
- Rejects division/modulo and compound division/modulo for direct target handling, forcing generic/runtime paths.
- Allows casts between vlong and non-floating types.

Dependencies and coupling:
- Uses common type predicates such as `typev`, `typefd`, `typechl`, and `mixedasop`.
- Influences earlier compiler lowering before `cgen.c`.

Notable behavior:
- Conservative around mixed compound assignments and floating/vlong casts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/machcap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/mul.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qc/mul.c

Constant-multiply sequence generator. It replaces multiplication by constants with shifts/adds/subtracts when a short sequence is available.

Key responsibilities:
- `mulcon0` looks up cached multiply sequences, checks exception hints, searches for shift/add/sub recipes, and handles powers of two recursively.
- `docode` validates compact hint strings against a target constant.
- `gen1`, `gen2`, and `gen3` search candidate operation sequences.
- `hintab` stores constants that the search algorithm fails to find efficiently.
- `hintabsize` exposes the hint table size.

Dependencies and coupling:
- Used by `swt.c:mulcon`, which translates compact sequence strings into generated instructions.
- Uses `Multab`/`Hintab` from `gc.h`.

Notable behavior:
- The compact code language encodes shift counts as letters and add/sub operand routing as digits.
- Negative constants are normalized during sequence lookup, then negated in emission.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/mul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/peep.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qc/peep.c

Peephole optimizer for Power instructions after global register allocation. It works over the `Reg` control-flow graph and mutates `Prog` instructions in place.

Key responsibilities:
- Completes missing `Reg` nodes for instructions between flow graph nodes.
- Repeatedly performs copy propagation and substitution propagation for register moves.
- Converts constant zero moves to `R0` references when the target treats `R0` as zero.
- Removes redundant byte/halfword sign/zero extension pairs.
- Folds `OP x,y,R; CMP R,$0; branch` into condition-code-setting `OPCC` instructions where safe.
- `copyu`, `copyas`, `copyau`, `copysub`, and related helpers classify and rewrite instruction uses/sets.

Dependencies and coupling:
- Called from `reg.c` unless register debug suppresses it.
- Depends on Power opcode semantics and `R0ISZERO`.
- Uses `Reg` graph predecessor/successor helpers `uniqp` and `uniqs`.

Notable behavior:
- Floating condition-code folding is intentionally disabled in comments.
- Unknown instructions are treated conservatively as read-alter-rewrite barriers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/peep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/q.out.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qc/q.out.h

Power object-code ABI header for assembler/compiler/linker coordination.

Key contents:
- Symbol/register constants: `NSNAME`, `NSYM`, `NREG`, text flags `NOPROF`, `DUPOK`.
- Register numbering conventions for general and floating registers, return registers, argument register, compiler temporaries, register variables, external registers, and fixed float constants.
- Full `enum as` opcode list for Power instructions, Plan 9 pseudo-ops, embedded PowerPC instructions, optional 32-bit instructions, and secondary/parallel floating-point opcodes.
- Address/name kinds such as `D_EXTERN`, `D_STATIC`, `D_AUTO`, `D_PARAM`, `D_BRANCH`, `D_OREG`, `D_CONST`, `D_REG`, `D_FREG`, `D_SPR`, `D_FILE`, `D_DCR`.
- `Ieee` serialized floating-constant representation.

Dependencies and coupling:
- Included by `gc.h` and shared with the Power assembler/linker object stream.
- `qa/lex.c` opcode table and `qc/txt.c` instruction selection both depend on these enumerators.

Filesystem/OS relevance:
- Defines the binary object format vocabulary used for Plan 9 Power object files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/q.out.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/reg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qc/reg.c

Global register allocator and data-flow optimizer for the Power C backend.

Key responsibilities:
- `regopt` builds a `Reg` flow graph from `Prog` instructions, records variable uses/sets, resolves branch targets, computes loops, propagates liveness, finds allocation regions, assigns registers, runs peephole optimization, recalculates PCs, fixes branches, and removes NOPs.
- `mkvar` maps memory operands/constants/symbols into bitset-tracked variables.
- `prop` propagates references and call-clobber information backward.
- `loopit`, `postorder`, `rpolca`, `doms`, `loophead`, and `loopmark` estimate loop structure using reverse postorder/dominators.
- `synch`, `paint1`, `paint2`, and `paint3` compute profitable register regions and rewrite memory references to registers.
- `addmove` inserts loads/stores around allocated regions.
- `RtoB`, `BtoR`, `FtoB`, and `BtoF` map physical registers to allocation bit masks.

Dependencies and coupling:
- Calls `peep()` after allocation.
- Depends on `Bits` operations from the common compiler and target-specific register ranges from `q.out.h`.

Notable behavior:
- Treats calls as clobbering externs and relevant register state.
- Warns and excises stores proven unused.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/reg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/sgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qc/sgen.c

Pre-codegen AST simplification and addressability analysis for the Power C backend.

Key responsibilities:
- `noretval` emits artificial uses of integer/floating return registers to suppress incorrect unused-result assumptions.
- `xcom` computes node `addable` and `complex` values.
- Recognizes directly addressable constants, names, registers, indirect registers, address-of, dereference, and constant-offset additions.
- Rewrites multiplication/division/modulo by powers of two into shifts/ands.
- Simplifies shifts and invokes `com64` for 64-bit specific canonicalization.
- Normalizes immediate-friendly operations by moving constants to the right side.

Dependencies and coupling:
- Works with common compiler transformations (`vlog`, `simplifyshift`, `complex`) and `com64.c`.
- Its complexity values drive evaluation order in `cgen.c`.

Notable behavior:
- Uses `FNX` to mark function calls/expressions requiring special ordering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/sgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/swt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qc/swt.c

Switch lowering, bitfield helpers, string/global data emission, object serialization, and type alignment for the Power compiler backend.

Key responsibilities:
- `swit1`/`swit2` emit binary-search switch dispatch with linear fallback for small case counts.
- `bitload` and `bitstore` extract/update C bitfields using shifts and masks.
- `outstring`, `sextern`, and `gextern` emit string and global data, including vlong split emission.
- `mulcon` converts `mul.c` compact multiply recipes into instruction sequences.
- `outcode`, `zwrite`, `zname`, `zaddr`, and `outhist` serialize `Prog` lists into Plan 9 object format.
- `align`, `doubled`, and `maxround` implement Power ABI alignment for structs, arrays, parameters, automatics, and double-containing aggregates.

Dependencies and coupling:
- Shares object encoding conventions with `qa/lex.c`.
- Uses `txt.c` instruction emission helpers and `mul.c` constant multiply recipes.
- Depends on `Biobuf`, symbol signatures, and common history records.

Filesystem/OS relevance:
- Emits object file records and source history path records; no runtime filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/swt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/txt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qc/txt.c

Low-level Power instruction selection and emission layer for the C compiler backend.

Key responsibilities:
- `ginit` initializes target globals, pseudo nodes, rathole/string storage, register reservations, and 64-bit codegen.
- `gclean` validates register balance, flushes strings, emits globals and `AEND`, and calls `outcode`.
- `nextpc`, `gins`, `gins3`, and `gins4` allocate and populate `Prog` instructions.
- `gargs`/`garg1` implement argument passing and temporary spilling for complex call arguments.
- `regalloc`, `regfree`, `regsalloc`, `regaalloc`, `regret`, and related helpers manage scratch, return, stack, and argument registers.
- `naddr` and `raddr` translate compiler `Node` addressing into object `Adr` operands.
- `gmove` handles loads, stores, casts, integer/float moves, float conversions, constants, and vlong register-pair moves.
- `gopcode` maps C operators to Power opcodes; `gopcode64`, `gori64`, and `gandi64` implement 64-bit arithmetic/logical/shift operations over register pairs.
- `gbranch`, `patch`, `gpseudo`, `sconst`, `uconst`, `exreg`, `ewidth`, and `ncast` provide branch patching, pseudo-ops, immediates, external registers, and type metadata.

Dependencies and coupling:
- Central implementation behind `cgen.c`, `swt.c`, and `reg.c`.
- Uses object opcodes/address types from `q.out.h` and ABI alignment from `swt.c`.

Notable behavior:
- Several float/integer conversions are hand-built via Power floating constants and stack temporaries.
- `R0ISZERO` influences zero constant emission.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qc/txt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/bpt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qi/bpt.c

Breakpoint management for the `qi` Power instruction simulator/debugger.

Key responsibilities:
- `dobplist` prints instruction, memory access, read, write, and equality breakpoints with symbol offsets.
- `breakpoint` parses breakpoint subtype suffixes and installs a `Breakpoint`.
- `delbpt` removes a breakpoint by evaluated address.
- `brkchk` checks executed/accessed addresses, handles hit counts, equality checks, and stops the run loop.

Dependencies and coupling:
- Uses `expr` for address parsing, `symoff` for display, and `getmem_4` for equality breakpoints.
- Updates global `membpt`, `count`, and `atbpt`.

Notable behavior:
- `delbpt` increments `membpt` for non-instruction breakpoint deletion; this appears counterintuitive and may be a latent bug, since add also increments it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/bpt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/branch.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qi/branch.c

Power branch and condition-register instruction handlers for `qi`.

Key responsibilities:
- Defines extended opcode group 19 table `op19`.
- `condok` evaluates branch condition fields and count-register behavior.
- `dobranch`, `bcctr`, `bclr`, `bcx`, and `bx` implement conditional/unconditional branches, link-register updates, and trace strings.
- `crop` implements condition-register boolean operations.
- `mcrf` moves condition-register fields.
- `call` and `ret` support optional call-tree tracing using symbols and stack parameter printing.
- `isync` is treated as a traced no-op.

Dependencies and coupling:
- Uses `reg` state, `bits[]`, `ci->taken`, `undef`, symbol functions, and command tracing globals.
- Hooks into `run.c` opcode dispatch through `ops19`.

Notable behavior:
- Branch handlers set `reg.pc = target - 4`; the run loop increments PC after each instruction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/branch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/cmd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qi/cmd.c

Interactive debugger command parser for `qi`.

Key responsibilities:
- Parses expressions and symbols via `numsym`/`expr`.
- Supports colon commands for breakpoints, delete, run, continue, and step.
- Supports dollar commands for stack traces, breakpoint listing, registers, quit, tracing modes, and instruction/memory summaries.
- `pfmt` formats memory or scalar values in many Plan 9 debugger styles, including disassembly via `machdata->das`.
- `quesie` implements memory examination commands.
- `setreg` writes selected CPU registers from evaluated expressions.
- `cmd` is the REPL loop, including last-command repetition and interrupt notification handling.

Dependencies and coupling:
- Uses `bioout`, `bin`, `run`, `reset`, `initstk`, memory accessors, symbol functions, breakpoints, and register state.
- Uses `setjmp(errjmp)`/`longjmp` recovery path shared with instruction faults.

Filesystem/OS relevance:
- Debugger shell around simulated process state; can indirectly read host stdin and symbol tables.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/float.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qi/float.c

Floating-point instruction support for the `qi` Power simulator.

Key responsibilities:
- Defines opcode tables for groups 59 and 63 floating-point/FPSCR instructions.
- `fpreginit` initializes simulated floating registers, including compiler-known constants.
- Implements `lfs/lfd/stfs/stfd` and indexed/update forms.
- Implements FPSCR moves and bit updates: `mcrfs`, `mffs`, `mtfsb1`, `mtfsb0`, `mtfsf`, `mtfsfi`.
- Implements `fcmp`, single/double arithmetic (`fariths`, `farith`), unary moves/abs/neg (`farith2`), and condition/FPSCR updates.
- Converts between double and raw 64-bit words with `v2fp`/`fp2v`.

Dependencies and coupling:
- Uses memory accessors, `reg.fd[]`, FPSCR constants from `power.h`, `getfsr`, and trace/error globals.
- Connected to `run.c` through `ops59`, `ops63a`, and `ops63b`.

Notable behavior:
- Comments explicitly warn that NaN, infinity, exception, and rounding behavior is approximate.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/float.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/icache.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qi/icache.c

Instruction-cache hooks for `qi`.

Key responsibilities:
- `icacheinit` is an empty initializer.
- `updateicache` accepts an address and marks it used, but has no behavior.

Dependencies and coupling:
- `mem.c:ifetch` calls `updateicache` when `icache.on` is enabled.

Notable behavior:
- This is currently a stub implementation; cache modeling fields exist in `power.h`, but no cache simulation is implemented here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/icache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/iu.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qi/iu.c

Integer, logical, load/store, special-register, trap, and cache-control instruction handlers for `qi`.

Key responsibilities:
- Defines extended opcode group 31 table `op31`.
- Implements arithmetic with carry/overflow state: add/sub variants, multiply/divide, negate.
- Implements logical and rotate/mask operations: and/or/xor/nor/nand/eqv, rlwimi/rlwinm/rlwnm, shifts.
- Implements compares and condition-register updates.
- Implements loads/stores for bytes, halfwords, words, byte-reversed forms, string load/store, multiple load/store, and reservation approximations.
- Implements special register moves for XER/LR/CTR/TB/DEC and condition-register moves.
- Handles traps and no-op style control/cache instructions (`sync`, `icbi`, `dcb*`).

Dependencies and coupling:
- Uses instruction decode macros from `power.h`, memory accessors from `mem.c`, and trace/error globals.
- Calls floating indexed load/store handlers declared from `float.c`.

Notable behavior:
- Some semantics are approximate or buggy by comments, especially overflow and reservation behavior.
- Byte-reversal helpers appear suspicious: `lhbrx`/`sthbrx` duplicate low byte in both positions, and `stwbrx` writes from a zero local instead of `reg.r[rd]`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/iu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/mem.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qi/mem.c

Virtual memory and memory access layer for `qi`.

Key responsibilities:
- `ifetch` fetches big-endian instructions, checks alignment, updates instruction profile counters, and optionally updates icache.
- `getmem_*` and `putmem_*` implement big-endian byte/halfword/word/vlong loads and stores with alignment checks.
- Memory breakpoints are checked on reads and writes.
- `memio` copies between host buffers and simulated memory for syscall argument/result handling.
- `vaddr` translates simulated virtual addresses to lazily allocated segment pages and demand-loads text/data from the executable.

Dependencies and coupling:
- Uses `memory.seg[]`, `text` fd, `textbase`, profile globals, `brkchk`, and `longjmp(errjmp)`.
- Segment definitions come from `qi.c:initmap`.

Filesystem/OS relevance:
- This is the simulator’s virtual memory subsystem, including lazy file-backed text/data paging and zero-backed bss/stack.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/power.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qi/power.h

Shared header for the `qi` Power simulator/debugger.

Key contents:
- Includes `/power/include/ureg.h` and defines user/ureg address helpers.
- Defines `Registers`, `Segment`, `Memory`, `Inset`, `Inst`, `Icache`, and `Breakpoint`.
- Enumerates breakpoint types, instruction classes, memory copy directions, and segment types.
- Declares all major simulator functions and global state.
- Defines Plan 9 Power layout constants: page size, user text base, stack top/size, profiling granularity, NOP encoding, sign bit.
- Defines condition-register, FPSCR, XER, and instruction decode macros.

Dependencies and coupling:
- Included by all `qi/*.c` files.
- Depends on Plan 9 `mach` library types (`Map`, `Symbol`) and Power kernel ureg layout.

Filesystem/OS relevance:
- Encodes the simulated process memory model and syscall/debugger shared state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/power.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/qi.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qi/qi.c

Main program and process/executable setup for `qi`.

Key responsibilities:
- `main` initializes buffered I/O, opens either a q.out file or a `/proc` process, loads headers, initializes stack/registers, and enters the debugger.
- `inithdr` reads/cracks executable headers, initializes symbols, and sets Power machdata.
- `initmap` creates text/data/bss/stack segment descriptors and instruction profiling storage.
- `procinit` imports an existing process’s text, segment layout, selected registers, memory pages, and stack from `/proc`.
- `reset` resets register and memory state.
- `initstk` builds a Plan 9-style initial user stack and Tos area.
- `dumpreg`, `dumpdreg`, `fatal`, `itrace`, `emalloc`, and `erealloc` provide utility/debug support.

Dependencies and coupling:
- Uses Plan 9 `mach` header parsing/symbol APIs, `/proc` files, `mem.c` page accessors, and `cmd.c` REPL.
- Establishes globals consumed by every simulator subsystem.

Notable behavior:
- `procinit` contains a likely indexing bug: loop `for(i = 0; i < 32; i++) reg.r[i] = greg(m, roff[i-1]);` reads `roff[-1]` for `i == 0`.
- `reset` loop condition `for(i = 0; i > Nseg; i++)` never runs, so segment pages are not freed as intended.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/qi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/run.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qi/run.c

Instruction dispatch loop for `qi`.

Key responsibilities:
- Defines primary opcode table `op0`.
- Dispatches instruction groups 19, 31, 59, and 63 to their extended opcode tables.
- Handles OE variants in group 31 through `oemflag`.
- `run` fetches, decodes, counts, executes, advances PC, and checks instruction breakpoints until `count` expires.
- `undef` and `unimp` report illegal/unimplemented instruction faults and return to the debugger via `longjmp`.

Dependencies and coupling:
- Uses `ifetch`, `reg`, `ci`, opcode tables from other modules, and breakpoint logic.
- Relies on instruction handlers to set `reg.pc = target - 4` for branches.

Notable behavior:
- Group 63 has two decode paths: arithmetic subset by low XO bits first, then full XO FPSCR/unary table.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/run.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/stats.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qi/stats.c

Execution statistics and profiling support for `qi`.

Key responsibilities:
- `isum` prints per-instruction counts, percentages, instruction class totals, data/instruction cycle estimates, stalls, syscalls, and branch taken rates.
- `segsum` prints memory segment residency/reference summaries.
- `iprofile` aggregates instruction profile counters by text symbol and prints hot functions with source locations.
- `profcmp` sorts profile entries by descending count.

Dependencies and coupling:
- Uses opcode tables from all instruction modules.
- Uses `iprof[]` populated by `mem.c:ifetch`, symbol APIs, and segment state.

Filesystem/OS relevance:
- Reports simulated memory residency for text/data/bss/stack and source-level profiling information.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/symbols.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qi/symbols.c

Symbol, source-location, and stack-trace helpers for `qi`.

Key responsibilities:
- `printsource` maps a PC to `file:line`.
- `printlocals` prints automatic variables for a function frame.
- `printparams` prints parameter values using frame pointer offsets.
- `stktrace` walks stack frames using `.frame` symbols, link register/saved PC conventions, and prints call chains; `C` modifier includes locals.

Dependencies and coupling:
- Uses Plan 9 `mach` symbol APIs and memory accessors.
- Used by command handling and call-tree tracing.

Notable behavior:
- Stops at `_main` and truncates after 40 frames.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/symbols.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/syscall.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qi/syscall.c

Host syscall bridge for simulated Power Plan 9 programs running under `qi`.

Key responsibilities:
- Maps Plan 9 syscall numbers to names and handler functions.
- Implements supported syscalls by reading arguments from the simulated stack, copying strings/buffers via `memio`, invoking host Plan 9 libc/syscalls, writing results back, and setting `reg.r[REGRET]`.
- Supported operations include errstr, bind, chdir, close, dup, exits, open, read/pread, write/pwrite, seek/oseek, rfork without `RFPROC`, sleep, old/new stat/fstat, pipe, create, fd2path, brk, remove, notify, and segflush.
- Unsupported syscalls print “No system call” and exit.
- `sc` validates the syscall instruction encoding, dispatches through `systab`, traces if enabled, and flushes output.

Dependencies and coupling:
- Includes Plan 9 syscall number header `/sys/src/libc/9syscall/sys.h`.
- Uses simulated memory accessors, `errbuf`, `bioout`, register state, and host filesystem/process APIs.

Filesystem/OS relevance:
- This is the main OS boundary for `qi`: simulated file descriptors and filesystem calls are forwarded to the host Plan 9 environment.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qi/syscall.c -->