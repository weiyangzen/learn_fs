# Group Research: group_1597_plan9_sources_os_plan9_plan9_sys_src_cmd_jpg_ycbcr_h_sources_os_pla_f33d85c495dc

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. The referenced internal group report file was not present, so this report is based on complete reads of the listed source files.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/ycbcr.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/ycbcr.h

This header is a data table module for Plan 9 JPEG/YUV color conversion. It defines `uint ycbcrmap[256]`, a 256-entry packed color lookup table, and `uchar closestycbcr[16*16*16]`, a 4096-entry quantization/nearest-color lookup table.

The file has no functions, includes, guards, or declarations beyond table definitions. It is intended to be included by exactly one C translation unit, not shared as an extern-only interface.

Key behavior is lookup-driven conversion between indexed/quantized RGB-like values and YCbCr palette entries. The final blocks of `closestycbcr` map high quantized ranges heavily to entries `254` and `255`, indicating reserved or extreme palette values.

Risks and notes: because this header defines storage directly, including it from more than one object would create duplicate symbols. Its correctness is entirely data-dependent and hard to audit mechanically without a generator or reference palette.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/ycbcr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/yuv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/yuv.c

This is the `yuv` image viewer/converter command. It reads YUV/YCbCr raw images through `readyuv(fd, CYCbCr)`, optionally displays them using libdraw/event, and optionally writes Plan 9 bitmap/rawimage output.

Command flags control output and display: `-3`, `-t`, `-c`, `-d`, `-e`, `-k`, `-v`, and `-9`. They select compressed/raw output, suppress display, disable Floyd-Steinberg diffusion, force grayscale, force RGBV/CMAP8, or output uncompressed Plan 9 bitmap data.

`show()` performs decode, colorspace conversion through `torgbv()` or `totruecolor()`, display allocation/loading, keyboard wait/quit handling, and output serialization through either a Plan 9 bitmap header plus channel bytes or `writerawimage()`.

Filesystem and OS interactions are simple file reads and stdout writes, plus graphical window attachment. Resource cleanup frees decoded raw image channels, colormap, raw image structures, and converted output buffers, though early error paths can bypass some cleanup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/yuv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ka/a.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ka/a.h

This is the SPARC assembler shared header for `ka`. It includes Plan 9 libc/Bio and `../kc/k.out.h`, then defines assembler data structures, global state, constants, and function prototypes.

Core structures are `Sym` for symbols/macros, `Io` for nested input streams, `Gen` for parsed operands, and `Hist` for source history. It defines assembler constants such as `NSYMB`, `HISTSZ`, `NHUNK`, `NHASH`, `STRINGSZ`, and input macros like `GETC()`.

The global state covers debug flags, include paths, macro definitions, symbol hash table, source history, current PC, pass number, output buffer, input stack, and active token values.

It also declares the shared compiler compatibility layer APIs from `../cc/compat.c`, making the assembler portable across Plan 9, Unix, and Windows build hosts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ka/a.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ka/a.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ka/a.y

This is the yacc grammar for the SPARC assembler. It parses Plan 9 assembly source into object-code records by calling `outcode(op, from, reg, to)`.

The grammar recognizes labels, symbol assignments, scheduler directives, SPARC integer loads/stores, floating-point loads/stores/operations, coprocessor operations, branches, calls/jumps, traps, state-register moves, `TEXT`, `GLOBL`, `DATA`, `RETURN`, `END`, `NOP`, and `WORD`/unimplemented forms.

Operand grammar builds `Gen` values for registers, floating registers, coprocessor registers, processor-state registers, immediates, string/floating constants, branch targets, SB/SP/FP-relative names, static names, ASI references, indexed addressing, and PC-relative expressions.

The file is tightly coupled to token definitions from `y.tab.h`, opcode numbers from `k.out.h`, and symbol state from `a.h`. It is intentionally two-pass: undefined labels produce pass-sensitive errors, and label values are assigned from `pc`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ka/a.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ka/l.s -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ka/l.s

Despite living under `cmd/ka`, this file is SPARC kernel assembly support code, not assembler implementation code. It defines low-level Plan 9 SPARC constants and routines used by the kernel/runtime.

The top half defines memory layout, page/MMU constants, PSR bits, special registers, kernel/user virtual address ranges, MMU segment/PMEG constants, PTE bits, ASI addresses, and boot/trap addresses.

`start` and `startvirt` set up early virtual mapping, stack, PSR, floating-point constants, SB, MACH, WIM, and branch into `main`. Other routines implement atomic swap variants, interrupt priority control (`spllo`, `splhi`, `splx`), user transition, trap/syscall linkage, register save/restore, special register accessors, MMU/ASI byte/word access helpers, and FP register save/restore.

The file exports globals `mach0`, `fpq`, and `fsr`. It is architecture-critical and assumes SPARC register conventions such as `R6` for `m->` and `R5` for `u->`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ka/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ka/lex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ka/lex.c

This file is the main driver, keyword table, object writer, and shared lexer integration for the SPARC assembler. It sets `thechar='k'` and `thestring="sparc"`.

`main()` parses assembler flags, supports `-o`, `-D`, `-I`, runs multiple input files in parallel using `NPROC` on non-Windows hosts, and calls `assemble()`. `assemble()` derives output names, configures include paths, creates the output file, runs pass 1 and pass 2, emits history, and flushes output.

`itab[]` maps register names, special registers, coprocessor registers, floating registers, opcodes, pseudo-ops, and scheduler controls to yacc token classes and opcode values. This table is the assembler’s lexical instruction set.

`zname()`, `zaddr()`, `outcode()`, and `outhist()` serialize Plan 9 object records. The file includes shared `../cc/lexbody`, `../cc/macbody`, and `../cc/compat`, so macro processing and cross-host compatibility are inherited from the common compiler frontend.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ka/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kbmap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kbmap.c

This is an interactive libdraw/event utility for selecting and applying keyboard maps. By default it reads map files from `/sys/lib/kbmap`; alternatively, file names can be provided on the command line.

It builds an array of `KbMap` entries with display name, file path, rectangle, and current selection state. `geometry()` lays entries into columns based on screen size and font height, and `redraw()` paints selectable map rectangles.

`click()` handles mouse button 4 selection, confirms release over the same rectangle, writes `/sys/lib/kbmap/ascii` first as a base map, then writes the selected map to `/dev/kbmap`. The current map is highlighted and the screen is redrawn.

Filesystem relevance is direct: this utility reads keyboard map files and writes the kernel keyboard-map device. Error handling is user-visible via stderr, while allocation failures call `sysfatal`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kbmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/bits.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/bits.c

This file provides bitset helpers for the SPARC C compiler backend. Active functions are `bany()`, `bnum()`, `blsh()`, and an older-style `Bconv()` formatter.

Several basic bit operations (`bor`, `band`, `bnot`, `beq`, `bset`) are present but commented out, implying equivalent macros or shared implementations exist elsewhere.

`bnum()` returns the first set bit index using `bitno()` and reports a compiler diagnostic if called on an empty set. `blsh()` constructs a single-bit `Bits` value. `Bconv()` formats variable bitsets by resolving entries through the global `var[]` table.

The functionality supports liveness/register allocation diagnostics. Note that `list.c` also defines a modern `Bconv(Fmt*)`, so this file appears to be legacy or build-conditional in relation to newer Plan 9 fmt APIs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/bits.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/cgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/cgen.c

This is the main expression and aggregate code generator for the SPARC C compiler backend. It lowers compiler AST `Node`s into backend `Prog` instructions through `gopcode()`, `gmove()`, and register allocation helpers.

`cgen()` handles scalar expressions, assignments, compound assignments, arithmetic/logical ops, shifts, multiplication/division/modulo, function calls, indirection, address generation, comparisons, boolean operators, casts, comma expressions, conditional expressions, increments/decrements, and bitfields.

`lcgen()` and `reglcgen()` compute lvalues and addresses, including indirection, conditional lvalues, and optimized constant-offset addressing. `boolgen()` emits branch-based boolean code with short-circuit handling and optional materialization into a target register.

`sugen()` handles structures/unions and wide constants. It emits fieldwise aggregate initialization, function-returned structures via hidden destination pointers, rathole temporaries for complex cases, and word-copy loops or unrolled copies. `layout()` performs the word move scheduling used by aggregate copies.

The file is central to correctness for C expression semantics. It relies heavily on the prior addressability/complexity pass and uses Plan 9 compiler conventions such as `nodrat`, `.safe`, and SPARC register-return rules.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/cgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/enam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/enam.c

This file defines `anames[]`, the textual names for SPARC backend opcode enum values from `k.out.h`.

The array covers integer arithmetic/logical ops, branches, coprocessor ops, data/pseudo ops, floating-point ops, loads/stores, traps, `TEXT`, `GLOBL`, `HISTORY`, `NAME`, `END`, dynamic/init/signature records, and `LAST`.

It is used by listing and diagnostic formatting, especially `%A` conversion in `list.c`. Correct ordering must remain synchronized with `enum as` in `k.out.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/enam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/gc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/gc.h

This is the SPARC C compiler backend master header. It includes the shared C compiler header and SPARC object format header, then defines target sizes, backend IR structures, global state, macros, and function prototypes.

Important structures include `Adr` for instruction operands, `Prog` for generated instructions, `Case`/`C1` for switch lowering, `Multab`/`Hintab` for multiply optimization, `Var` for register-allocation variables, `Reg` for control-flow/data-flow graph nodes, and `Rgn` for allocatable live regions.

Global state covers code lists, string data, rathole temporaries, switch cases, register allocation regions, live-variable bitsets, used registers, flow graph nodes, and target-specific external register offsets.

The prototypes define the backend modules: simple generation, expression generation, text/instruction emission, switch/bitfield/object output, listing, global register allocation, peephole optimization, and 64-bit helper lowering.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/gc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/k.out.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/k.out.h

This header defines the Plan 9 SPARC object-code ABI used by the assembler, compiler, and linker. It includes register constants, opcode enum values, operand type/name constants, and IEEE double layout.

Register definitions identify fixed roles: `REGZERO`, `REGSP`, `REGSB`, `REGEXT`, `REGRET`, `REGTMP`, `REGLINK`, `REGARG`, and floating return/external/special constant registers.

`enum as` lists all SPARC backend opcodes and pseudo-ops, including integer operations, condition branches, floating branches/arithmetic/conversions, moves, traps, `TEXT`, `DATA`, `GLOBL`, `HISTORY`, `NAME`, `WORD`, and object metadata records.

Operand constants distinguish names (`D_EXTERN`, `D_STATIC`, `D_AUTO`, `D_PARAM`) and types (`D_BRANCH`, `D_OREG`, `D_ASI`, `D_CONST`, `D_FCONST`, `D_SCONST`, `D_REG`, `D_FREG`, `D_CREG`, `D_PREG`, `D_FILE`). This file is the synchronization point for `ka`, `kc`, and object consumers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/k.out.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/list.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/list.c

This file installs and implements Plan 9 fmt conversions for SPARC compiler backend diagnostics and listings.

`listinit()` registers `%A`, `%P`, `%S`, `%N`, `%D`, and `%B`. `Pconv()` formats full instructions with special handling for `DATA` and `TEXT`. `Aconv()` maps opcodes through `anames[]`.

`Dconv()` formats addresses by operand type, including constants, memory references, registers, branches, floating constants, and string constants. `Nconv()` formats symbol-relative names as SB/SP/FP forms. `Sconv()` escapes fixed-size string constants.

The file is non-semantic but essential for debugging generated code, register allocation, and compiler diagnostics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/mul.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/mul.c

This file implements multiply-by-constant strength reduction for the SPARC C compiler backend. It searches for compact shift/add/subtract instruction sequences and caches results in `multab`.

The encoded sequence language uses letters for shifts and `+`/`-` operations with small register-selection digits. `docode()` validates and expands candidate hints against a target multiplier. `gen1()`, `gen2()`, and `gen3()` recursively search sequences up to a small length.

`mulcon0()` handles negative multipliers, cache lookup, exception hint-table lookup, recursive factorization by powers of two, and search fallback. The large `hintab[]` records constants the search would otherwise miss or handle poorly.

This optimization is called from switch/code generation through `mulcon()` in `swt.c`. It trades compiler complexity for faster generated integer multiplication on SPARC hardware where general multiply may be expensive.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/mul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/peep.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/peep.c

This file implements peephole and local copy-propagation optimization over the backend `Reg` control-flow list.

`peep()` first completes the `Reg` structure by adding missing nodes for instructions between flow graph nodes, then repeatedly removes redundant register-to-register and zero-register moves when `copyprop()` or `subprop()` proves it safe. It also removes redundant repeated byte/halfword sign/zero-extension moves.

`subprop()` rewrites register usage around a copy to improve copy propagation opportunities. `copyprop()` and `copy1()` recursively propagate substitutions through successor paths while respecting merges and sets.

`copyu()`, `copyas()`, `copyau()`, `copyau1()`, `copysub()`, and `copysub1()` encode per-instruction read/write behavior. Calls, returns, branches, and unknown instructions are treated conservatively.

This pass is tightly coupled to SPARC instruction semantics and the register allocator’s flow graph. Its main risk is semantic misclassification of instruction operands, which would make propagation unsafe.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/peep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/reg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/reg.c

This is the SPARC backend global register allocator and data-flow optimizer. It builds a flow graph from generated instructions, computes liveness, identifies profitable live ranges, assigns registers, rewrites instructions, then runs peephole optimization.

`regopt()` performs the full pipeline: build `Reg` nodes, record variable use/set bits, resolve branch targets, detect loop structure, propagate liveness backward, propagate register/variable synchronization forward, isolate allocation regions, cost them, assign available integer/FP registers, insert load/store moves, recalculate PCs, patch branches, and remove nops.

Loop analysis uses reverse postorder and approximate dominators following the Hecht-Ullman method. Region costing weights references by loop nesting, penalizes loads/stores, excludes unsafe variables, and handles calls/external variables conservatively.

`mkvar()` maps operands to optimizable variables and classifies externs, params, constants, and address-taken/punned variables. `paint1()`, `paint2()`, and `paint3()` evaluate and apply allocation over live regions. `RtoB`/`BtoR` and `FtoB`/`BtoF` map physical registers to bit masks.

The allocator is performance-critical and assumes exact instruction semantics from `mkvar()` and peephole helpers. It intentionally avoids allocating special registers and respects SPARC integer/FP register classes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/reg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/sgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/sgen.c

This file provides simple generation helpers, especially AST addressability and complexity analysis via `xcom()`.

`noretval()` emits dummy uses of return registers when a function has no return value but the compiler needs to model register clobbering. `xcom()` classifies nodes as constants, names, registers, indirect registers, address expressions, indirections, and constant-offset additions.

`xcom()` also rewrites optimizable arithmetic: multiplication by a power of two becomes shift left, unsigned division by a power of two becomes logical shift right, and modulo by a power of two becomes bitwise and. It canonicalizes constants to the right side for comparisons and commutative integer ops.

This file feeds `cgen.c`: its `addable` and `complex` values determine whether expressions can be emitted directly, need registers, or require function-call-safe temporaries.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/sgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/swt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/swt.c

This file combines switch lowering, bitfield access, string/global data emission, object serialization, and target alignment.

`swit1()`/`swit2()` lower switch cases into either linear comparisons for small case sets or a recursive binary decision tree. `bitload()` and `bitstore()` implement signed/unsigned bitfield extraction and insertion with masks and shifts.

`outstring()` emits fixed-size string chunks as `ADATA` records. `mulcon()` uses `mulcon0()` from `mul.c` to replace constant multiplication with shift/add/sub sequences. `gextern()` emits global initializer data, including 64-bit constants in target byte order.

`outcode()`, `zwrite()`, `zname()`, `zaddr()`, and `outhist()` serialize the generated `Prog` list into Plan 9 object records with rotating symbol slots and source history.

`align()` defines SPARC ABI layout for structs, arguments, and automatics, including big-endian parameter adjustment. This is a major ABI correctness point.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/swt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/txt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/txt.c

This is the SPARC backend initialization, register management, instruction emission, typed move lowering, opcode selection, and cleanup file.

`ginit()` sets target identity, initializes registers, listing formats, special nodes (`.safe`, `.rathole`, `.ret`), string/rathole state, and 64-bit support. `gclean()` validates register state, flushes string data, emits globals, appends `AEND`, and calls `outcode()`.

The file provides temporary/register allocation (`regalloc`, `regfree`, `regret`, `regsalloc`, `regaalloc`), argument generation (`gargs`, `garg1`), address conversion (`naddr`, `raddr`), and branch/pseudo-op emission.

`gmove()` is the largest semantic section: it handles loads, stores, integer/floating conversions, special floating constants, memory-register staging, sign/zero extension, unsigned long to float adjustment, and rathole use for conversion through memory. `gopcode()` maps compiler ops to SPARC opcodes and emits comparisons plus branches.

The file also defines target type widths, cast compatibility masks, small immediate checks, external register allocation, branch patching, and pseudo-op creation. It is the backend’s instruction-selection core.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kc/txt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/bpt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/bpt.c

This file implements breakpoint management for the `ki` SPARC emulator/debugger.

`dobplist()` prints instruction, access, read, write, and equal-value breakpoints with symbolic locations. `breakpoint()` parses breakpoint type suffixes, evaluates the address expression, stores count/done values, and links the breakpoint into `bplist`.

`delbpt()` removes a breakpoint by evaluated address. `brkchk()` checks execution or memory access against the list, handles equal-value breakpoints by reading memory, decrements pass counts, and stops execution by setting `count=1` and `atbpt=1`.

Memory breakpoints increment `membpt`, causing memory access helpers to call `brkchk()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/bpt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/cmd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/cmd.c

This file implements the interactive debugger command language for `ki`. It is adb-like, with address expressions, repeat counts, format modifiers, run/step/continue commands, register display, stack traces, and breakpoint control.

Expression handling resolves symbols, `.` current address, hex literals with `#`, numeric literals, and simple binary operators. `colon()` implements run/continue/step and breakpoint commands. `dollar()` implements register dumps, stack traces, breakpoint listing, tracing flags, summaries, profiling, and quit.

`pfmt()` formats memory or expression values as octal, decimal, hex, bytes/chars/strings, addresses, globals, disassembly, and source lines. `quesie()` prints memory with repeat counts and line wrapping. `setreg()` writes emulated registers.

`cmd()` runs the read-evaluate loop, stores the last command for blank-line repeat, handles interrupts through `notify()`, and uses `setjmp(errjmp)` as the debugger recovery boundary.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/float.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/float.c

This file implements SPARC floating-point instruction behavior for `ki`.

It supports single and double floating loads/stores (`ldf`, `lddf`, `stf`, `stdf`), including immediate/register addressing, double alignment checks, and odd-register traps for double operations.

`fcmp()` implements SPARC floating compare variants, updates floating condition codes in `fpsr`, and handles NaN/invalid cases. `fbcc()` implements all floating branch conditions, annul behavior, taken counters, and delay-slot execution.

`farith()` implements floating add, subtract, multiply, divide, integer/float conversions, move, negate, absolute value, and single/double conversion operations. Division by zero raises a debugger-visible FP exception.

The implementation assumes host floating-point representation matches the constraints documented in `sparc.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/float.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/icache.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/icache.c

This file is a stub instruction-cache module for `ki`.

`icacheinit()` does nothing, and `updateicache(ulong addr)` only marks `addr` as used. The `Icache` structure exists in `sparc.h`, and `ifetch()` calls `updateicache()` when `icache.on` is set, but this implementation does not model cache behavior.

The file is a placeholder for future or platform-specific cache simulation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/icache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/ki.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/ki.c

This is the main entry point and process/binary initialization layer for the `ki` SPARC emulator/debugger.

`main()` initializes Bio streams, optionally attaches to a process id, opens the target executable, reads headers/symbols, initializes stack arguments, seeds special FP constants, and enters `cmd()`.

`initmap()` creates Text/Data/Bss/Stack segments from the executable header, allocates lazy page tables and instruction profile storage, and sets the initial PC. `inithdr()` validates SPARC magic, initializes symbols, loads maps, and configures mach disassembly data.

`procinit()` snapshots a live process through `/proc/<pid>/text`, `/proc/<pid>/segment`, and `/proc/<pid>/mem`, loading data/bss/stack pages and registers. `initstk()` builds an emulated Plan 9 exec stack and TOS area, including pid for time support.

The file also provides reset, fatal error handling, trace printing, integer/FP register dumps, zeroing allocation helpers, and software signed/unsigned 32x32 multiply returning high/low words.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/ki.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/mem.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/mem.c

This file implements instruction fetch, data memory access, user/kernel memory copy, and lazy virtual address translation for `ki`.

`ifetch()` enforces instruction alignment, updates the optional icache, resolves the page with `vaddr()`, increments instruction profile counters, and returns a big-endian 32-bit instruction. `getmem_*()` and `putmem_*()` implement big-endian byte/halfword/word access with alignment traps and memory breakpoint checks.

`memio()` copies between emulator memory and host buffers for reads, writes, and NUL-terminated strings with a maximum size. It is heavily used by syscall emulation.

`vaddr()` resolves an address to a segment page, lazily allocates pages, loads Text/Data pages from the executable file, zero-fills Bss/Stack pages, tracks resident pages and references, and raises a simulated MMU miss on invalid addresses.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/run.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/run.c

This is the core SPARC instruction emulator for `ki`.

It defines opcode dispatch tables for op0/op2/op3 instruction classes and `run()` fetches, decodes, counts, dispatches, advances PC, and checks instruction breakpoints. `delay()` executes delay-slot instructions while preserving the branch target behavior, and tracks used delay slots.

Implemented instruction families include integer arithmetic/logical ops, condition-code variants, shifts, carry add/sub behavior, Y register access, `mulscc`, loads/stores, double loads/stores, byte/halfword sign/zero loads, `ldstub`, `swap`, `sethi`, `call`, `jmpl`, integer branches, trap/syscall dispatch, and floating hooks via `float.c`.

Condition-code logic updates PSR `N/Z/V/C` for relevant arithmetic. Branches compute signed displacement targets, implement annul behavior, track taken counts, and execute delay slots correctly. `ilock()` models load-use stalls for profiling.

The file is large and semantics-heavy; correctness depends on matching SPARC v8 behavior and Plan 9 calling/syscall conventions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/run.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/sparc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/sparc.h

This is the shared header for the `ki` SPARC emulator/debugger. It documents host assumptions for integer and floating-point emulation and includes SPARC `ureg.h`.

It defines breakpoint types, instruction categories, the optional `Icache`, decoded `Inst` entries, the `Registers` structure with integer registers, PC/IR/Y/PSR/FPSR, and a union view over FP registers as doubles, floats, and words.

It defines memory segment structures (`Segment`, `Memory`), segment IDs, syscall memory-copy directions, Plan 9 kernel/user address constants, stack layout constants, NOP encoding, PSR flag bits, immediate extraction helpers, branch annul bit, and FP condition-code values.

The header also declares all emulator subsystems and global state: memory, registers, tracing flags, breakpoint list, Bio streams, current instruction, instruction profile buffer, symbol map, and counters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/sparc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/stats.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/stats.c

This file provides execution and memory statistics for `ki`.

`isum()` walks all instruction dispatch tables, prints per-instruction counts and percentages, aggregates loads, stores, arithmetic, floating point, branches, syscalls, special-register ops, delay slot use, annulled branch cycles, load/store stalls, and total estimated cycles.

`segsum()` prints segment base/end, resident bytes, and reference counts for Stack, Text, Data, and Bss.

`iprofile()` aggregates instruction profile counters by text symbol ranges, sorts by count, prints cycle percentages with symbol and source location, and clears the profile buffer afterward.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/symbols.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/symbols.c

This file provides source and symbol-aware reporting for `ki`.

`printsource()` maps a text address to `file:line` using `fileline()`. `printlocals()` prints automatic variables for a function frame by reading from emulated memory. `printparams()` prints function parameters from the frame.

`stktrace()` walks frames using symbol data, `.frame` locals, saved PC/SP conventions, and fallback handling for leaf/local symbols. It prints function calls, parameter values, source locations, callers, and optionally locals for `$C`.

The stack trace stops at `_main`, fails out if frame metadata is missing, and truncates after 40 frames.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/symbols.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/syscall.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/syscall.c

This file emulates Plan 9 syscalls for SPARC programs running under `ki` by translating arguments from emulated memory/registers into host Plan 9 libc calls.

It includes Plan 9 syscall numbers, maps them to names in `sysctab[]`, and dispatches through `systab[]` from `ta()`, using `reg.r[REGRET]` as the syscall number and return register.

Implemented calls include errstr variants, fd2path, bind, chdir, close, dup, exits, open, read/pread, seek/old seek, rfork without process creation, sleep, old/new stat and fstat, write/pwrite, pipe, create, brk, remove, notify, and segflush. Unsupported syscalls print a diagnostic and exit.

The file uses `memio()`, `getmem_w()`, and `putmem_w()` to copy strings, buffers, stat data, pipe fds, and 64-bit offsets between host and emulated memory. It maintains `errbuf` and handles Bss growth in `sysbrk_()` by resizing the Bss segment table.

Filesystem relevance is substantial: this is the emulator’s bridge for Plan 9 file namespace, fd, stat, read/write, create/remove, bind, and path operations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ki/syscall.c -->