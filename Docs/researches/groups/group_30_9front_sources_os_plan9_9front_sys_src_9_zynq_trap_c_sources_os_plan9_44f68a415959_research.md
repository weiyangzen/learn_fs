# Group Research: group_30_9front_sources_os_plan9_9front_sys_src_9_zynq_trap_c_sources_os_plan9_44f68a415959

Scope verified against `Docs/research_subset_a.md`: all files are within `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/trap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/trap.c

Implements ARM/Zynq kernel trap, syscall, notification, and floating-point context handling for the 9front kernel.

Key responsibilities:
- Handles undefined-instruction, instruction-abort, data-abort, and IRQ traps in `trap`.
- Converts ARM fault status/address information into kernel panics or user notes via `faultarm`.
- Lazily allocates, saves, restores, and clears per-process FP state through `mathtrap`, `fpunotify`, `fpunoted`, `notefpsave`, `procsave`, `procfork`, and `procsetup`.
- Builds user notification frames in `notify` and validates/restores user register state in `noted`.
- Provides debug support through `_dumpstack`, `dumpstack`, `dumpregs`, `userpc`, and `dbgpc`.
- Sets up fork/exec/kernel-child register state with `setkernur`, `forkchild`, `kprocchild`, and `execregs`.

Important dependencies:
- Uses Plan 9 kernel globals `m` and `up`, ARM fault helpers `getifsr/getifar/getdfsr/getdfar`, scheduler hooks, note delivery, and MMU switching via `l1switch`.
- Stack dumping emits `ktrace /arm/9zynq` input for postmortem analysis.

Notable details:
- Kernel faults on addresses above `USTKTOP` panic immediately.
- FP notify handling preserves an old FP save area in `ofpsave` so note handlers can run without losing interrupted FP state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/uartzynq.c -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/uartzynq.c

Implements the Zynq UART physical driver used by the Plan 9 UART layer.

Key responsibilities:
- Defines register offsets and status bits for the Zynq UART.
- Instantiates one console UART, `UART1`, mapped at `VMAP`, IRQ `UART1IRQ`, default baud `115200`.
- `uartconsinit` binds this UART as `consuart` and configures line mode.
- `zuartkick` drains staged output into the TX FIFO.
- `zuartintr` handles RX trigger and TX empty interrupts, acknowledges interrupt status, feeds received characters to `uartrecv`, and restarts output.
- `zuartenable` waits for TX idle, disables interrupts, programs RX FIFO trigger level, and enables RX/TX interrupts if requested.
- Provides polling `getc/putc`, data-bit selection, parity control, and stubs for unsupported modem/control operations.

Notable details:
- `zuartbaud` only prints the requested baud and returns success; actual divisor programming is absent.
- `zuartparity` appears to use direct bit manipulation of the UART mode register and is the only parity implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/uartzynq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/usbehci.h -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/usbehci.h

Provides the local EHCI controller register definitions and controller state for the Zynq USB host driver.

Key contents:
- Overrides USB debug macros to use `ehcidebug` and endpoint debug flags.
- Defines EHCI link tags, command/status/interrupt/port bits, and Zynq-specific no-op handoff/line macros.
- Declares `Eopio`, matching the controller operational register layout starting around offset `0x140`.
- Declares `Poll` and `Ctlr`, the controller object used by the shared EHCI code.
- `Ctlr` stores locks/rendezvous objects, register pointers, DMA allocator callbacks, periodic frame data, async queue heads, interrupt stats, poll state, base address, IRQ, and mapped register base.
- Declares shared EHCI entry points `ehcilinkage`, `ehcimeminit`, and `ehcirun`.

Notable details:
- This header adapts the common Plan 9 EHCI implementation to the Zynq register layout rather than implementing the full EHCI scheduler itself.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/usbehci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/usbehcizynq.c -->
# File Research: sources/os/plan9/9front/sys/src/9/zynq/usbehcizynq.c

Implements Zynq-specific EHCI host-controller registration and reset glue.

Key responsibilities:
- Defines Zynq USB mode, OTG, and ULPI register offsets.
- Registers two possible controllers, `USB0_BASE/USB0IRQ` and `USB1_BASE/USB1IRQ`.
- `ehcireset` stops the controller, performs host-controller reset, sets interrupt threshold, and determines frame-list size.
- Supplies allocator callbacks: descriptors from uncached memory via `ucalloc`, DMA buffers via aligned `mallocalign`.
- Wraps EHCI `portstatus` to derive high/low speed from Zynq port status bits.
- `reset` claims an inactive controller, maps registers, sets host mode, configures ULPI, initializes shared EHCI memory/linkage, hooks `portstatus`, and enables interrupts.
- `usbehcilink` registers this implementation as HCI type `"ehci"`.

Notable details:
- `ctlrs` has room for three entries but only two initialized controllers; the zero base sentinel terminates scans.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/zynq/usbehcizynq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1a/a.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1a/a.h

Shared header for the Plan 9 `1a` assembler front end, targeting Motorola 68000-family object code.

Key contents:
- Includes Plan 9 libc/Bio support, `../2c/2.out.h` opcode/address definitions, and compiler compatibility helpers.
- Defines assembler limits, buffered input macros, hash sizes, include/macro limits, and parser constants.
- Declares core data structures: `Sym`, `Ref`, `Io`, `Addr`, `Gen`, `Gen2`, and `Hist`.
- Declares all assembler globals for input state, include paths, symbol table, histories, pass number, current PC, output file, and object output buffer.
- Provides prototypes for parsing, macro/preprocessor handling, object serialization, symbol/history output, diagnostics, and initialization.

Role in system:
- This is the contract between the yacc grammar, lexer/preprocessor, and object writer in `cmd/1a`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1a/a.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1a/a.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1a/a.y

Yacc grammar for the Plan 9 `1a` assembler.

Key responsibilities:
- Parses labels, variable definitions, instruction forms, operands, addressing modes, constants, expressions, branch targets, `DATA`, `TEXT`, and bit-field instruction syntax.
- Emits object records through `outcode` during parse actions.
- Tracks label definitions and reports duplicate or undefined labels on pass 2.
- Builds `Gen2` source/destination operand pairs for instruction classes `LTYPE1` through `LTYPEB`.
- Supports 68000 addressing syntax including registers, indirect, predecrement, postincrement, `SB/SP/FP/PC/TOS`, static `<>`, constants, string constants, and floating constants.
- Evaluates integer expressions in grammar actions with arithmetic, shifts, and bitwise operators.

Notable details:
- The assembler is two-pass; branch symbols may remain unresolved in pass 1 but are diagnosed in pass 2.
- `TEXT` and `DATA` have specialized productions to capture frame/displacement metadata.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1a/a.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1a/lex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1a/lex.c

Main program, opcode table, initialization, and object writer for `1a`.

Key responsibilities:
- Parses command-line options `-o`, `-D`, `-I`, debug flags, and supports parallel assembly of multiple files on non-Windows systems.
- Runs two assembler passes in `assemble`, initializing include paths, preprocessing defines, parsing, and writing final object output.
- Defines `itab`, mapping reserved names, registers, special registers, and all 68000/68881 mnemonics to parser token classes and opcode values.
- Initializes the symbol table, default `nullgen`, target identifiers `thechar='1'`, `thestring="68000"`, and working directory state.
- Serializes object names, addresses, instructions, and file history records with `zname`, `zaddr`, `outcode`, and `outhist`.
- Includes shared compiler lexer, macro, and compatibility bodies from `../cc`.

Notable details:
- Object encoding uses compact bit flags such as `T_FIELD`, `T_INDEX`, `T_OFFSET`, `T_SYM`, `T_FCONST`, `T_SCONST`, and `T_TYPE`.
- `outcode` increments assembler `pc` for real instructions but not for `AGLOBL` and `ADATA`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1a/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1c/cgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1c/cgen.c

Expression, lvalue, boolean, and aggregate code generator for the Plan 9 `1c` 68000 C compiler backend.

Key responsibilities:
- `cgen` emits code for scalar expressions, assignments, arithmetic, casts, calls, comparisons, increments/decrements, bitfields, conditionals, comma expressions, and address/indirect operations.
- Handles register allocation/evaluation order around function calls and complex expressions.
- Uses 68000-specific register pairs for long division/modulo and emits optimized constant multiplication/shift sequences when possible.
- `lcgen` generates lvalue addresses into address registers, stack operands, or temporaries.
- `boolgen` lowers boolean expressions and relational operators into branches or materialized 0/1 values.
- `sugen` copies or constructs structs/unions and handles aggregate returns, struct constants, `OSTRUCT`, aggregate assignment, calls returning aggregates, and conditional/comma aggregate expressions.

Important dependencies:
- Calls target helpers from `txt.c` such as `gmove`, `gopcode`, `gbranch`, `patch`, `regalloc`, `regpair`, and `regaddr`.
- Uses bitfield helpers from `swt.c`.

Notable details:
- The file carefully preserves stack argument offsets around nested calls.
- Non-interruptable temporaries through `.rathole` are explicitly warned for some struct/member cases.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1c/cgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1c/gc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1c/gc.h

Primary backend header for the Plan 9 `1c` 68000 compiler.

Key contents:
- Defines target type sizes: 8-bit char, 16-bit short, 32-bit int/long/pointer, 64-bit vlong/double.
- Declares backend IR/address structures `Adr`, `Prog`, `Txt`, `Case`, register-flow structures `Reg`, `Rgn`, `Var`, constant-multiply table `Multab`, and switch case helper `C1`.
- Defines liveness/register-allocation cost constants and bitset helper macros.
- Declares all backend globals: instruction lists, register usage arrays, flow graph nodes, data/string symbols, cases, stack offsets, variables, and optimization metadata.
- Prototypes code generation, register allocation, peephole optimization, switch/bitfield helpers, object output, alignment, and 64-bit support hooks.
- Installs vararg formatting checks for backend debug printers.

Role in system:
- Shared by all `cmd/1c` backend files and ties the generic Plan 9 C front end to the 68000 object format.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1c/gc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1c/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1c/list.c

Debug/listing formatter support for the `1c` backend.

Key responsibilities:
- Installs formatters for registers, opcodes, addresses, instructions, string constants, and bitsets.
- `Bconv` prints compiler variable bitsets using `var[]`.
- `Pconv` prints a `Prog` as mnemonic plus operands, including bitfield widths/shifts.
- `Aconv` maps opcode numbers through `anames`.
- `Dconv` formats `Adr` values including indirect, pre/post increment/decrement, address constants, branches, extern/static/auto/param, constants, floats, and strings.
- `Rconv` formats data/address/FP registers and special 68000 registers.
- `Sconv` escapes fixed-size string constants.

Notable details:
- These formatters are used by debug flags throughout code generation and optimization, so correctness here affects diagnostics and developer visibility.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1c/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1c/mul.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1c/mul.c

Constant multiplication recipe table for the `1c` 68000 backend.

Key contents:
- Defines `multab[]`, mapping selected integer constants to compact character-coded instruction sequences.
- Sequence codes describe moves, adds, subtracts, and shifts between two scratch registers.
- Supports small constants and selected larger constants up to `9800`.
- Exposes `multabsize`.

Role in system:
- Used by `mulcon1` in `swt.c` and `cgen.c` to replace multiplication by constants with faster add/sub/shift sequences when profitable or available.

Notable details:
- The table assumes all generated sequences start from an initial copy unless the sequence begins with `i`, which suppresses the leading move.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1c/mul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1c/peep.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1c/peep.c

Peephole and local copy-propagation optimizer for `1c`.

Key responsibilities:
- Completes the `Reg` flow structure by inserting flow nodes for raw `Prog` instructions between existing nodes.
- Repeatedly propagates register-to-register moves and removes redundant moves using `copyprop` and `subprop`.
- Folds address-register add/sub increments into 68000 auto-increment or predecrement addressing modes.
- Removes unnecessary condition-code save/restore pairs.
- Removes redundant `TST` instructions when prior condition-code settings are equivalent.
- Rewrites the pattern `TSTB (A); BLT/GE; ORB $128,(A)` into `TAS (A)` where legal.
- Provides operand compatibility, use/set classification, copy substitution, and instruction-size helpers.

Notable details:
- Conservative handling exists for divide, subroutine calls, partial-register writes, return registers, and FP/address registers.
- Many decisions depend on 68000 condition-code behavior and addressing-mode legality.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1c/peep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1c/reg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1c/reg.c

Global register optimizer and flow/liveness engine for `1c`.

Key responsibilities:
- Builds a `Reg` flow graph from the generated `Prog` list, recording use/set sets for variables and registers.
- Resolves branch targets and builds predecessor/successor links.
- Computes loop structure using reverse postorder and approximate dominators.
- Propagates reference/call liveness backward and register/variable synchrony forward to fixed point.
- Warns on used-before-set and set-not-used variables, excising dead stores.
- Identifies profitable live regions, assigns data/address/FP registers, and rewrites memory references to registers.
- Inserts load/store moves at region boundaries and preserves CCR around inserted moves when needed.
- Runs peephole optimization after register allocation and recalculates final PCs/branches.

Important dependencies:
- Uses `mkvar` to classify optimizable extern/static/auto/param variables.
- Uses target register bit masks for D, A, and F registers.

Notable details:
- The optimizer accounts for 68040 denormal FP load behavior by forcing initialization moves for some auto FP variables.
- Address registers are chosen when cheaper than data registers for eligible integer/pointer variables.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1c/reg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1c/sgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1c/sgen.c

Statement-level code generation and addressability analysis for `1c`.

Key responsibilities:
- `codgen` emits a function `ATEXT`, generates its body, checks missing returns, emits return cleanup, and invokes register optimization.
- `gen` lowers statements: lists, returns, labels, gotos, cases, switches, loops, breaks/continues, if/else, and used/set pseudo-ops.
- Maintains `breakpc`, `continpc`, `nbreak`, `retok`, stack markers, and case lists.
- `xcom` computes addressability and expression complexity, folding address patterns, constants, power-of-two multiply/divide into shifts, and simple assignment/addressable cases.
- Reorders symmetric and relational expressions to simplify right operands or exploit short immediate encodings.
- `bcomplex` prepares boolean tests and emits branch setup.
- `nodconst` encodes small constants through pointer casts used by backend helper APIs.

Notable details:
- Addressability classes are target-specific and drive later `cgen` decisions.
- Short/byte multiply/divide assignment is widened to long/unsigned long because the target lacks direct byte/short forms.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1c/sgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1c/swt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1c/swt.c

Switch lowering, bitfield code, string/data object output, constant multiplication expansion, and ABI alignment for `1c`.

Key responsibilities:
- `doswit` collects, sorts, validates, and emits switch case dispatch.
- `swit1` emits linear dispatch for small switches and binary-search dispatch for larger switches.
- `bitload` and `bitstore` extract/update bitfields through shifts, masks, and memory writes.
- `outstring` and `outlstring` emit byte and Rune string data into `ADATA` records.
- `doinc` schedules pre/post increments around expression evaluation.
- `setsp` and `adjsp` emit stack-adjust pseudo-instructions.
- `outcode`, `zwrite`, `zname`, `zaddr`, and `outhist` serialize generated programs and histories into Plan 9 object format.
- `ieeedtod` serializes native doubles to target IEEE representation.
- `mulcon`, `shlcon`, and `mulcon1` expand constant multiplication using `multab`.
- `sextern`, `gextern`, `align`, and `maxround` handle external data emission and target ABI layout.

Notable details:
- `align` implements big-endian argument adjustment for sub-word parameters.
- Object writing mirrors the assembler’s compact address encoding so compiler output feeds the same linker.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1c/swt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1c/txt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1c/txt.c

Target initialization and low-level instruction selection/emission helpers for `1c`.

Key responsibilities:
- `ginit` initializes target identity, register pools, move/conversion tables, opcode tables, string/static/rathole symbols, and 64-bit support.
- `gclean` verifies register balance, flushes string data, emits globals, and writes final object code.
- `oinit` maps generic C operations and types to 68000/68881 opcodes.
- `nextpc`, `prg`, `gpseudo`, and `gpseudotree` allocate and emit `Prog` records.
- `naddr` converts compiler AST nodes into target `Adr` operands.
- `regalloc`, `regaddr`, `regpair`, `regret`, and `regfree` manage scratch data/address/FP registers.
- `gmove` handles type conversions, extension/truncation, integer/FP conversions, unsigned-to-FP edge cases, and FPCR rounding control.
- `gopcode` emits typed opcodes and bitfield metadata.
- `asopt` applies small local emission optimizations such as `MOV $0` to `CLR`, stack push via `PEA`, and small immediate materialization.
- Defines target width and cast tables.

Notable details:
- `exreg` reserves external register candidates near the high end of each register class.
- The backend explicitly initializes A6/A7 as address registers in use.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1c/txt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1l/asm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1l/asm.c

Final assembler/emitter for the Plan 9 `1l` 68000 linker.

Key responsibilities:
- `entryvalue` resolves numeric or symbolic entry points.
- `asmb` writes text, data, symbols, stack/line tables, relocations, and output headers for supported `HEADTYPE`s.
- Supports Plan 9 a.out variants, boot formats, NeXT boot/Mach-style headers, and Pilot relocatable output.
- `asmins` encodes each `Prog` into 68000/68881 instruction words using `optab`.
- Handles special control registers, CCR/SR/USP/move-control, FP control registers, branches, moves, arithmetic, shifts, FP ops, bitfields, movem/fmovem, traps, and pseudo-ops.
- `asmea` converts `Adr` operands into effective-address encodings and emits extension words.
- `datblk` materializes initialized data blocks, catches overlapping initialization, and writes constants, strings, floats, and symbol-relative values.
- `asmreloc` writes Pilot relocation records.
- Provides endian/output helpers `lput`, `s16put`, `cflush`, `gnuxi`, and `rnd`.

Notable details:
- Branch sizing supports short/word encodings and absolute long branch fallback for `BRA/BSR`.
- Data symbol addressing prefers A6-relative small-data form when possible.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1l/asm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1l/compat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1l/compat.c

Small compatibility wrapper for the `1l` linker.

Key contents:
- Includes `l.h`.
- Includes the shared `../cc/compat` implementation body.

Role in system:
- Pulls shared Plan 9 compiler-tool compatibility helpers into the linker build without duplicating their source.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1l/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1l/l.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1l/l.h

Primary header for the Plan 9 `1l` 68000 linker.

Key contents:
- Includes Plan 9 libc/Bio, 68000 object definitions from `../2c/2.out.h`, and compatibility declarations.
- Defines linker data structures: `Adr`, `Prog`, `Auto`, `Sym`, and `Optab`.
- Defines symbol classes such as `STEXT`, `SDATA`, `SBSS`, `SDATA1`, `SXREF`, `SAUTO`, `SPARAM`, and `SFILE`.
- Declares global output buffers, section sizes, header parameters, symbol tables, text/data lists, library/autolib state, endian maps, and special/simple addressing tables.
- Declares linker passes: object loading, library loading, branch patching, layout, data allocation, stack offset rewriting, span calculation, assembly, symbol/line/reloc output, diagnostics, and helpers.
- Defines `CPUT` output-buffer macro and formatting pragmas.

Role in system:
- Shared contract for all `cmd/1l` linker source files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1l/l.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1l/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1l/list.c

Listing, formatting, and diagnostics support for `1l`.

Key responsibilities:
- Installs formatters for registers, opcodes, addresses, strings, and programs.
- `Pconv` prints instructions with line number and operands, including bitfield suffixes.
- `Dconv` formats linker `Adr` values, including resolved branch targets, extern/static/auto/param, constants, quick constants, float/string constants, and indirect addressing forms.
- `Rconv` formats data, address, FP, and special registers.
- `Sconv` escapes fixed-size string constants.
- `diag` reports errors prefixed by current function text symbol and aborts after too many errors.

Notable details:
- `D_BRANCH` printing uses `bigP->pcond->pc` when available, so debug output reflects resolved branch targets.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1l/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1l/obj.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1l/obj.c

Main program, object/archive loader, autolib handling, profiling insertion, symbol table, and numeric/float conversion support for `1l`.

Key responsibilities:
- Parses linker flags for output, entry, header type, text/data bases, alignment, and debug modes.
- Sets default target identity `thechar='1'`, `thestring="68000"` and default Plan 9 output settings.
- Initializes special/simple addressing tables, output file, symbol table, and required helper symbols `_mull`, `_divsl`, `_divul`, and `_ccr`.
- Loads object files and archives, including archive symbol table lookup and iterative library extraction for unresolved `SXREF`s.
- `ldobj` parses Plan 9 object records, name/signature records, histories, text/data/global records, branch references, auto/param metadata, and instruction streams.
- Performs early canonicalizations: `JSR`/`BSR`, quick immediates, add/sub sign flips, quick shifts, address-register compare/clear tweaks, and float-constant-to-integer opcode substitutions.
- Tracks source history and autolib paths through `histfrog`, `addhist`, `addlib`, and `histtoauto`.
- Supports optional profiling/tracing instrumentation with `doprof1` and `doprof2`.
- Provides symbol lookup/allocation, program allocation/copying, endian map initialization, and IEEE double/single conversion.

Notable details:
- Archive loading repeatedly scans libraries until no new unresolved symbols are resolved.
- Static symbols use the object-file `version` to avoid collisions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1l/obj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1l/optab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1l/optab.c

Instruction metadata table for the `1l` 68000 linker/emitter.

Key contents:
- Defines `optab[]`, indexed by Plan 9 opcode enum value.
- Each entry maps an assembler opcode to:
  - optional floating/integer alternate opcode,
  - source and destination stack-size effects,
  - emitter `optype`,
  - up to four opcode words/templates.
- Covers integer arithmetic, branches, bit operations, compares, moves, shifts, multiply/divide, 68881 floating-point operations, FP branches/DBcc, movem/fmovem, traps, pseudo-ops, and unimplemented placeholders.
- Defines `mmsize[]`, a size table by emitter operation type.

Role in system:
- `asm.c` uses `optype` to choose instruction encoding logic and opcode templates.
- `dostkoff` uses stack-size metadata to track stack pointer effects.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1l/optab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1l/pass.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/1l/pass.c

Linker layout, branch following, stack-offset rewriting, and unresolved-symbol passes for `1l`.

Key responsibilities:
- `dodata` validates data initializers, lays out small data first, then regular data, optional BSS/data packing, BSS, and defines `bdata`, `edata`, and `end`.
- `patch` resolves subroutine calls and branch offsets to `pcond` pointers, reports undefined symbols, and collapses branch chains.
- `mkfwd` builds skip-forward links for faster PC-to-instruction lookup.
- `follow` and `xfol` reorder instruction flow to improve fallthrough, avoid some branches, copy short instruction sequences, and invert conditional branches when useful.
- `relinv` maps conditional branches to their inverse, including FP branches.
- `dostkoff` computes stack offsets, inserts stack adjustments where control-flow stack states merge, rewrites auto/param offsets, expands pseudo/synthetic operations, and lowers long multiply/divide calls to helper routines when needed.
- `atolwhex` parses decimal/octal/hex numeric options.
- `undef` reports unresolved external references.
- `initmuldiv1` marks helper routines as required; `initmuldiv2` locates their `ATEXT` records.

Notable details:
- Return instructions with nonzero stack offset are rewritten to adjust stack before `RTS`.
- Some operations, such as `MOVW CCR`, `EXTBL`, and long mul/div, are expanded into helper sequences before final span/assembly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/1l/pass.c -->