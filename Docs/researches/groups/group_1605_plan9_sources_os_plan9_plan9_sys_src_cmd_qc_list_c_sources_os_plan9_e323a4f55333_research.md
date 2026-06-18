# Group Research: group_1605_plan9_sources_os_plan9_plan9_sys_src_cmd_qc_list_c_sources_os_plan9_e323a4f55333

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/list.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/list.c

PowerPC compiler backend listing/formatting support.

Key responsibilities:
- Installs custom Plan 9 format verbs for assembler diagnostics and debug output.
- Formats bitsets of optimization variables, instructions, opcodes, addresses, string constants, and symbol-relative names.
- Handles PowerPC address classes including integer, floating, condition-register, branch, string, and floating constants.
- Prints symbolic storage names for extern/static/auto/param references.

Dependencies:
- Uses backend globals from `gc.h`: `anames`, `var`, `pc`, `Bits`, `Prog`, `Adr`, and symbol/type conventions.
- Shared with optimizer/debug flags that print `%P`, `%D`, `%B`, `%A`, `%N`, and `%S`.

Notable risks:
- Formatting is diagnostic infrastructure, so wrong output can make backend debugging misleading.
- `Bconv` truncates long bitsets silently at `STRINGSZ`.
- `Pconv` depends on the backend’s three-address `from/from3/reg/to` encoding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/machcap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/machcap.c

Machine-capability predicate for the PowerPC C compiler backend.

Key responsibilities:
- Reports which AST operations the target backend can lower directly.
- Accepts integer/logical arithmetic, multiply, shifts, casts between 32-bit and 64-bit families, boolean/control expression nodes, assignment operators, increments/decrements, and comparisons.
- Rejects divide/modulo operations and their assignment forms, forcing generic or runtime handling elsewhere.

Dependencies:
- Uses `Node` operation codes and type classification tables from `gc.h`, including `typev`, `typefd`, and `typechl`.

Notable risks:
- This is a policy gate for code generation. Incorrectly returning true for unsupported operations can route code into missing backend paths.
- Division/modulo are explicitly not machine-capable despite the backend containing low-level PowerPC divide opcodes in other contexts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/machcap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/mul.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/mul.c

Constant-multiply sequence generator for replacing multiplication by constants with shifts, adds, and subtracts.

Key responsibilities:
- Caches generated multiply sequences in `multab`.
- Searches for short expression sequences using an internal two-register model.
- Uses an exception hint table for constants the bounded search does not find efficiently.
- Supports recursive handling of even constants by generating a sequence for the odd factor and appending a shift.
- Encodes sequence steps compactly as two-character operations consumed later by `mulcon()` in `swt.c`.

Dependencies:
- Uses `Multab`, `Hintab`, `Node`, diagnostics, and `gc.h` globals.
- The generated mini-language is interpreted by `qc/swt.c`.

Notable risks:
- Only searches up to short fixed lengths, with special hints for gaps.
- Negative constants are normalized for search and handled during code emission.
- Correctness relies on `docode()` validating generated and hinted sequences against the desired constant.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/mul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/peep.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/peep.c

Late peephole optimizer for PowerPC compiler output.

Key responsibilities:
- Completes the `Reg` flow graph by inserting missing nodes for non-data instructions between register-allocation nodes.
- Eliminates redundant register-to-register moves through copy propagation.
- Performs substitution propagation to swap register names and expose removable moves.
- Converts `$0` constants to `REGZERO` when the target treats R0 as a zero register.
- Removes redundant byte/halfword extension move pairs.
- Folds `CMP reg,$0` followed by conditional branches into condition-code-setting forms of the producer instruction when legal.
- Tracks instruction register use/set behavior through `copyu`, `copyau`, `copysub`, and related helpers.

Dependencies:
- Depends on `Reg`, `Prog`, `Adr`, PowerPC opcode enums, zero-register policy, and backend flow graph links from `reg.c`.

Notable risks:
- Copy propagation is conservative around calls, returns, branches, read-alter-write operations, and ambiguous opcodes.
- Many instruction semantics are hand-classified; missing a use/kill case can miscompile.
- Floating-point compare folding is intentionally disabled/commented out.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/peep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/q.out.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/q.out.h

PowerPC object/instruction ABI header shared by the compiler backend and associated tools.

Key contents:
- Defines register numbers and register allocation ranges for integer and floating-point registers.
- Enumerates all backend assembler opcodes, including integer, branch, floating-point, cache/control, embedded PowerPC, optional 32-bit FP, and paired/secondary FP instructions.
- Defines address type/name classes such as extern/static/auto/param, branches, registers, constants, FPSCR/MSR/SPR/SREG, files, and DCRs.
- Defines object flags `NOPROF` and `DUPOK`.
- Defines the archive symbol name `__.SYMDEF`.
- Provides the simulated IEEE double layout used by object emission.

Dependencies:
- Used by `qc`, `ql`, assemblers, and tools that read/write PowerPC Plan 9 object streams.

Notable risks:
- This is an ABI-style enum header. Opcode or address-class order changes would break object compatibility with the linker and disassembler.
- Register allocation comments encode target calling/register conventions expected by `txt.c` and `reg.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/q.out.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/reg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/reg.c

Global register allocator and data-flow optimizer for the PowerPC C compiler backend.

Key responsibilities:
- Builds an auxiliary `Reg` flow graph from generated `Prog` instructions.
- Tracks variables, uses, sets, constants, externs, params, aliases, and register-bit occupancy.
- Resolves branch targets and predecessor/successor links.
- Computes approximate loop structure using reverse postorder and dominator-style analysis.
- Propagates liveness backward and register/variable synchrony forward.
- Identifies profitable live regions, chooses free integer or floating registers, inserts loads/stores, and rewrites operands.
- Runs peephole optimization afterward and recalculates program counters/branch targets.
- Eliminates dead stores and removes `ANOP`s before freeing flow structures.

Dependencies:
- Uses `gc.h` optimizer structures, bitsets, PowerPC register ranges, instruction classifications, and `peep()`.

Notable risks:
- Variable recognition in `mkvar()` deliberately excludes or marks aliased/punned/address-taken values.
- Costing depends on loop weights and constants such as `CLOAD`, `CREF`, and `CINF`.
- Correctness relies on handwritten instruction use/set classification.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/reg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/sgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/sgen.c

Expression addressability and complexity analysis for PowerPC code generation.

Key responsibilities:
- Emits synthetic no-op uses of return registers for functions with no explicit return value.
- Computes `Node.addable` classes for constants, names, registers, indirect registers, addresses, dereferences, and address-plus-constant forms.
- Computes `Node.complex`, estimating temporary register pressure.
- Rewrites power-of-two multiplies/divides/modulos into shifts or masks.
- Normalizes immediate-friendly operations by moving constants to the right side and inverting relations when needed.
- Marks function calls as high complexity.

Dependencies:
- Uses generic compiler AST/type infrastructure from `gc.h`, including `vlog`, `simplifyshift`, `com64`, and type classification tables.

Notable risks:
- Addressability classes are numeric conventions consumed by later code generation.
- Rewrites happen before final code selection, so missed simplifications can generate worse code while unsafe rewrites can miscompile.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/sgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/swt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/swt.c

Mixed backend support for switches, bitfields, static data, object serialization, and ABI layout.

Key responsibilities:
- Lowers switch statements using linear compare chains for small cases and binary search for larger case lists.
- Generates bitfield load/store sequences with shifts and masks.
- Buffers string literals into `ADATA` chunks.
- Emits multiply-by-constant code using sequences from `mul.c`.
- Emits global/static data, including special handling for 64-bit constants and endianness.
- Serializes `Prog` objects to the Plan 9 object stream with symbol-cache records, addresses, history records, signatures, and constants.
- Computes structure, argument, and automatic-variable alignment, including double-containing aggregate rules.
- Computes rounded frame/argument sizes.

Dependencies:
- Tightly coupled to `txt.c`, `mul.c`, `q.out.h`, Plan 9 object format, and generic compiler history/symbol/type systems.

Notable risks:
- Object encoding uses compact symbol slots and binary address records; compatibility depends on exact field layout.
- Alignment logic encodes PowerPC ABI and big-endian assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/swt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/txt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/txt.c

Main PowerPC code-generation backend for the Plan 9 C compiler.

Key responsibilities:
- Initializes target identity, register reservations, pseudo nodes, string/rathole symbols, and 64-bit support.
- Finalizes output by checking register leaks, flushing strings, emitting globals, and writing object code.
- Allocates/free integer, floating-point, 64-bit register-pair, argument, and stack temporary nodes.
- Converts AST nodes to `Adr` operands.
- Implements `gmove()` for scalar, floating, memory, constant, and 64-bit moves/conversions.
- Emits instructions with two-, three-, and four-operand helper forms.
- Maps generic compiler operations to PowerPC opcodes.
- Implements 64-bit arithmetic/logical/shift/multiply lowering using register pairs.
- Emits branches, patches branch targets, emits pseudo ops, checks immediate ranges, allocates external registers, and defines type width/cast tables.

Dependencies:
- Depends on `gc.h`, `q.out.h`, `swt.c` alignment/output helpers, `com64` support, register conventions, and PowerPC opcode names.

Notable risks:
- Many ABI details are hardcoded: return registers, stack argument layout, R0 zero behavior, and fixed floating constants.
- Floating/integer conversions use rathole stack temporaries and simplified sequences.
- 64-bit operations are synthesized manually and are sensitive to high/low word ordering.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/txt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/bpt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/bpt.c

Breakpoint management for the PowerPC interpreter/debugger `qi`.

Key responsibilities:
- Lists instruction, read, write, access, and equality breakpoints with symbolized addresses.
- Parses breakpoint modifiers from debugger commands.
- Creates and deletes breakpoints.
- Checks breakpoints during instruction fetch and memory access/write paths.
- Supports pass counts through `count/done`, and equality breakpoints comparing memory contents against the configured value.

Dependencies:
- Uses `power.h` globals: `bplist`, `membpt`, `cmdcount`, `count`, `atbpt`, `bioout`.
- Depends on expression parsing in `cmd.c`, memory accessors in `mem.c`, and symbol formatting from libmach.

Notable risks:
- `delbpt()` increments `membpt` when deleting non-instruction breakpoints; that appears counterintuitive and can leave memory breakpoint checks enabled.
- Equality breakpoints read memory during breakpoint checking and can trigger memory faults.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/bpt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/branch.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/branch.c

PowerPC branch and condition-register instruction emulation for `qi`.

Key responsibilities:
- Defines opcode table for primary opcode 19 extended branch/CR operations.
- Decodes branch option/condition names for trace output.
- Implements conditional branch decision logic using CTR and CR bits.
- Emulates branch-to-CTR, branch-to-LR, conditional immediate branches, absolute/relative branches, link-register updates, and PC adjustment.
- Implements CR logical operations and `mcrf`.
- Emits optional call-tree tracing for calls and returns.
- Treats `isync` as a traceable no-op.

Dependencies:
- Uses decode macros, register state, condition bits, tracing, and symbol helpers from `power.h`.

Notable risks:
- Branches update `reg.pc` to target minus 4 because the dispatcher adds 4 after execution.
- `condok()` decrements CTR and validates reserved fields, so branch option semantics are centralized and fragile.
- Return/call tracing is observational and does not affect execution semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/branch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/cmd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/cmd.c

Interactive debugger command parser and formatter for `qi`.

Key responsibilities:
- Parses simple expressions from symbols, dot, numeric constants, and one binary operator.
- Builds argument vectors for restart commands.
- Handles colon commands for break/delete/run/continue/step.
- Handles dollar commands for stack traces, breakpoint list, registers, floating registers, quit, trace toggles, and summaries/profiles.
- Formats memory/register values in multiple numeric, character, string, symbol, instruction, and source-line formats.
- Implements examine commands, expression evaluation, register assignment, command repetition, and interrupt handling.

Dependencies:
- Uses `run`, `reset`, `initstk`, breakpoint functions, memory accessors, libmach symbol/disassembly helpers, and `power.h` globals.

Notable risks:
- Expression parsing is intentionally small and not a full adb expression evaluator.
- String formats read until NUL without an explicit maximum local-buffer bound.
- Debugger control flow uses `setjmp/longjmp` shared with emulator faults.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/float.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/float.c

Floating-point instruction emulation for the PowerPC interpreter.

Key responsibilities:
- Defines opcode tables for primary opcodes 59 and 63 floating-point operations.
- Initializes floating registers, including compiler-reserved constants.
- Converts between raw 64-bit memory values and host doubles.
- Emulates floating loads/stores, indexed/update variants, FPSCR moves/field updates, comparisons, unary operations, arithmetic, fused multiply-add/subtract families, and result condition bits.
- Tracks a subset of FPSCR exception state using host floating status.

Dependencies:
- Uses `power.h` register state, memory accessors, decode macros, FPSCR constants, and Plan 9 floating conversion helpers.

Notable risks:
- Comments explicitly warn that NaN, infinity, rounding, and exception behavior are approximate.
- Single-precision stores rely on host conversion through C `float`.
- Some optional operations are routed to `unimp`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/float.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/icache.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/icache.c

Instruction-cache hook stubs for `qi`.

Key responsibilities:
- Provides `icacheinit()` and `updateicache()` symbols expected by the emulator.
- Currently performs no initialization or cache simulation.

Dependencies:
- Included through `power.h`; called by instruction fetch when `icache.on` is enabled.

Notable risks:
- Cache timing/stall behavior is not implemented despite `Icache` fields existing in `power.h`.
- Any user expecting instruction-cache profiling or invalidation fidelity will get no effect.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/icache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/iu.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/iu.c

Integer, logical, memory, special-register, trap, and cache/control instruction emulation for `qi`.

Key responsibilities:
- Defines the primary opcode 31 extended instruction table.
- Emulates integer arithmetic with carry, condition-code setting, comparisons, logical ops, rotates/masks, shifts, multiply/divide, CR/XER movement, SPR movement, and immediate forms.
- Emulates byte/half/word loads/stores, update/indexed variants, atomics, byte-reversal, string load/store, load/store multiple, and traps.
- Treats sync/cache operations mostly as traceable no-ops.
- Provides tracing for decoded instructions.

Dependencies:
- Uses `power.h`, memory accessors, floating indexed helpers, branch/syscall dispatch, XER/CR macros, and global register state.

Notable risks:
- Several comments mark overflow behavior as incomplete or approximate.
- `stwcx.` assumes reservation success.
- Some routines appear suspicious or intentionally rough for debugger use, such as byte-reversal and load/store-multiple register indexing.
- Privileged/control operations are largely unimplemented or no-op.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/iu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/mem.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/mem.c

Simulated memory subsystem for `qi`.

Key responsibilities:
- Fetches big-endian instructions with alignment checks and per-PC profiling.
- Provides big-endian byte, halfword, word, and doubleword memory accessors.
- Performs alignment checks for word/half/doubleword accesses.
- Triggers memory breakpoints on reads and writes.
- Provides `memio()` for copying between host buffers and simulated memory, including NUL-terminated strings.
- Lazily maps virtual addresses to per-segment page buffers.
- Loads text/data pages from the executable and allocates zeroed BSS/stack pages.

Dependencies:
- Uses `Memory`, `Segment`, breakpoint state, profiler arrays, executable fd `text`, and constants from `power.h`.

Notable risks:
- Address misses longjmp back to the debugger rather than returning errors.
- Segment tables are lazy and page-sized; file offset calculations must match `qi.c` layout.
- Doubleword alignment check only tests word alignment, matching the source comment uncertainty.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/power.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/power.h

Shared declarations, state, constants, and decode macros for the PowerPC interpreter/debugger.

Key contents:
- Includes PowerPC user register layout from `/power/include/ureg.h`.
- Defines breakpoint, instruction, opcode table, instruction-cache, register-file, segment, and memory structures.
- Declares emulator functions across branch, integer, float, memory, syscall, command, symbol, stats, and loader modules.
- Declares global emulator/debugger state.
- Defines Plan 9 user address, stack, page, profiling, NOP, CR, FPSCR, XER, and opcode decode constants/macros.

Dependencies:
- Consumed by all `qi` C files.
- Depends on Plan 9 libmach types and PowerPC Ureg layout.

Notable risks:
- Header comments document host assumptions for floating emulation: word/double sizes, padding, and `vlong` precision.
- Global state is broad and mutable across all modules.
- Some declared names differ from implementations (`initicache` vs `icacheinit`), reflecting old-code looseness.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/power.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/qi.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/qi.c

Program loader, process snapshot loader, stack initializer, and utility routines for the `qi` emulator/debugger.

Key responsibilities:
- Opens a PowerPC executable or attaches to a numeric `/proc` pid snapshot.
- Reads and validates executable headers with libmach, initializes symbols and maps.
- Builds text/data/BSS/stack segment tables and instruction profiling storage.
- Reads live process segments and selected registers from `/proc`.
- Resets register/memory state and breakpoint pass counts.
- Builds an initial Plan 9 user stack and `Tos` area with argv and pid.
- Provides fatal/error reporting, instruction tracing, register dumps, floating dumps, and zeroing allocators.

Dependencies:
- Uses libmach `Fhdr`, maps, symbols, Plan 9 `/proc`, `power.h`, `mem.c`, and `cmd.c`.

Notable risks:
- `reset()` has a loop condition `i > Nseg`, so segment cleanup never runs.
- `procinit()` reads `roff[i-1]` starting at `i=0`, which indexes before the register-offset array.
- Stack/Tos construction embeds 32-bit PowerPC and Plan 9 layout assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/qi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/run.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/run.c

Instruction dispatch loop for the PowerPC interpreter.

Key responsibilities:
- Defines the primary opcode table for immediate arithmetic/logical ops, branches, syscalls, loads/stores, floating loads/stores, and group dispatch markers.
- Runs the fetch/decode/execute loop for `count` instructions.
- Dispatches primary opcodes and extended opcode groups 19, 31, 59, and 63.
- Handles overflow-enabled variants for selected opcode-31 instructions.
- Increments per-instruction counters and checks instruction breakpoints after each instruction.
- Reports illegal or not-implemented instructions via `undef()` and `unimp()`.

Dependencies:
- Uses opcode tables from `branch.c`, `iu.c`, `float.c`, and syscall handling.
- Uses `ifetch`, breakpoint checks, `power.h` register state, and longjmp error handling.

Notable risks:
- PC update convention requires instruction handlers to set `reg.pc = target - 4` for branches.
- Unsupported instruction entries with names but no function are traceable but fault when executed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/run.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/stats.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/stats.c

Execution statistics and profiling reports for `qi`.

Key responsibilities:
- Aggregates instruction counts across all opcode tables.
- Reports per-instruction counts and percentages.
- Summarizes loads, stores, arithmetic, floating point, special-register operations, control instructions, syscalls, branches, and taken branches.
- Prints simple memory segment residency/reference summaries.
- Builds a symbol-level instruction profile by summing per-PC profile buckets between text symbols.

Dependencies:
- Uses opcode table globals, segment state, profiler arrays, libmach text symbols, and source-line printing.

Notable risks:
- Percent calculation assumes nonzero denominators in some subcategories; branch taken percentage can divide by branch count.
- Instruction-cycle and data-cycle model is approximate and not a full PowerPC timing model.
- Fixed `prof[5000]` limits the number of profiled symbols.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/symbols.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/symbols.c

Symbol, source, and stack-trace support for `qi`.

Key responsibilities:
- Prints file:line information for a program counter.
- Prints local variables and parameters using libmach symbol metadata and simulated stack memory.
- Walks stack frames from current PC/SP using `.frame` symbols and saved return PCs.
- Handles leaf/local function cases and stops at `_main`.
- Optionally prints locals for `$C` stack traces.

Dependencies:
- Uses libmach symbol APIs, `mach->szreg`, simulated memory access, and current register state.

Notable risks:
- Stack walking depends on correct `.frame` metadata and PowerPC frame layout.
- Local/parameter printing reads fixed 4-byte values and may not represent larger or floating types correctly.
- Trace is truncated after 40 frames.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/symbols.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/syscall.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/syscall.c

Plan 9 syscall emulation bridge for PowerPC programs running under `qi`.

Key responsibilities:
- Maps Plan 9 syscall numbers to names and handler functions.
- Copies syscall arguments from simulated stack memory.
- Implements selected calls through host Plan 9 libc: errstr, fd2path, bind, chdir, close, dup, exits, open, read/pread, seek/oseek, rfork without `RFPROC`, sleep, stat/fstat old and new forms, write/pwrite, pipe, create, brk, remove, notify, and segflush.
- Copies buffers and return values back into simulated memory.
- Maintains an emulated `errbuf`.
- Dispatches `sc` only for the expected PowerPC syscall instruction.

Dependencies:
- Uses `/sys/src/libc/9syscall/sys.h`, host libc/syscalls, `memio`, register state, and debugger tracing flags.

Notable risks:
- Many syscalls intentionally print “No system call” and exit.
- `rfork(RFPROC)` is not supported.
- Host-side syscalls affect the host namespace/files, so emulation is not sandboxed.
- Some compatibility code uses old fixed-size stat/errstr layouts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qi/syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/asm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/asm.c

PowerPC linker output writer for text, data, headers, symbols, and line tables.

Key responsibilities:
- Resolves the entry value from `INITENTRY`.
- Emits machine code by walking `Prog` instructions, consulting `oplook()` and `asmout()`, and checking phase errors.
- Handles text wrapping warnings and optional Virtex-4 boot jump injection.
- Emits data blocks from linker data initializers.
- Emits Plan 9 symbols and compressed line-number tables unless stripped.
- Writes headers for multiple `HEADTYPE` formats, including Plan 9, PEF-like, XCOFF-like, ELF, and boot-image variants.
- Provides endian-specific byte/word/long/vlong output helpers.
- Emits symbol table entries for globals, text symbols, files, frame sizes, autos, and params.

Dependencies:
- Uses linker globals and structures from `l.h`, `asmout.c`, `datap`, `textp`, dynamic linking helpers, and ELF helpers.

Notable risks:
- Output layout is controlled by `HEADTYPE`, `HEADR`, `INITTEXT`, `INITDAT`, and `dlm`.
- Data initialization performs overlap checks and relocation adjustments.
- Header constants encode historical platform formats.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/asm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/asmout.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/asmout.c

PowerPC instruction encoder for the `ql` linker.

Key responsibilities:
- Defines bitfield macros for PowerPC instruction forms.
- Converts linker optab classes into one to five emitted instruction words.
- Encodes moves, arithmetic, logical operations, loads/stores, indexed forms, branches, condition-register operations, special-register moves, FPSCR operations, traps, rotate/mask operations, and pseudo-instruction expansions.
- Synthesizes large constants and long-offset memory references using `REGTMP`.
- Handles branch target validation and dynamic relocations.
- Implements helper opcode maps: register-register, immediate-register, load, indexed load, store, and indexed store.
- Supports standard PowerPC, floating point, embedded PowerPC MAC instructions, optional FP, paired/secondary FP, DCR access, and cache/control instructions.

Dependencies:
- Uses `l.h`, optab classification, `regoff`, `dynreloc`, output helpers from `asm.c`, and opcode enums from the PowerPC object format.

Notable risks:
- Encoding depends on exact optab type contracts.
- Some pseudo-instructions such as remainder are expanded into multi-instruction sequences.
- Large constants and long offsets can fail if operands already require `REGTMP`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/asmout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/cnam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/cnam.c

Class-name table for `ql` linker diagnostics/debugging.

Key responsibilities:
- Defines string names for operand classes used by the PowerPC linker optab machinery.
- Covers register, floating register, condition register, special register, segment register, constant ranges, branch ranges, auto/extern/oreg ranges, FPSCR/MSR/XER/LR/CTR, address, any, and fallback classes.

Dependencies:
- Consumed by linker listing/diagnostic code that prints optab classes.

Notable risks:
- The table order must match the operand-class enum in `l.h`.
- This file contains data only; mismatches would produce misleading diagnostics rather than direct code generation changes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/cnam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/compat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/compat.c

Compatibility allocation and filesystem helpers for the PowerPC linker.

Key responsibilities:
- Provides a simple hunk-based `malloc()` aligned to 8 bytes.
- Implements no-op `free()`.
- Implements `calloc()` over the custom allocator.
- Rejects `realloc()` by printing and aborting.
- Wraps `sbrk()` as `mysbrk()`.
- Provides no-op `setmalloctag()`.
- Implements `fileexists()` using `stat()`.

Dependencies:
- Uses linker hunk globals and `gethunk()` from `l.h`.

Notable risks:
- Memory is arena-style and not actually freed.
- Any unexpected caller of `realloc()` aborts the linker.
- Overrides standard allocation names, so behavior differs from normal libc allocation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/cputime.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/cputime.c

Small host compatibility wrappers for linker timing and file operations.

Key responsibilities:
- Computes CPU time by summing `times()` user/system counters and dividing by 100.
- Wraps `lseek()` behind Plan 9-style `seek()`.
- Wraps host `creat()` behind Plan 9-style `create()`, accepting only mode `1`.

Dependencies:
- Used by the linker’s verbose timing and output-file creation paths.

Notable risks:
- CPU tick scaling assumes 100 ticks per second.
- `create()` is a narrow compatibility shim and returns `-1` for modes other than `1`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ql/cputime.c -->