# Group Research: group_1492_plan9_sources_os_plan9_plan9_sys_src_cmd_5c_peep_c_sources_os_plan9_5294c57f024c

This grouped report covers the requested Plan 9 ARM compiler, emulator, and linker files from `sources/os/plan9/plan9/sys/src/cmd`. I read each listed source file completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/peep.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/peep.c

## Scope

ARM backend peephole optimizer for the Plan 9 C compiler (`5c`). It operates after register-flow construction and before final object emission.

## Behavior

- Completes missing `Reg` nodes for non-pseudo instructions in the program stream.
- Repeatedly applies copy propagation, constant propagation, register substitution, and shift folding into ARM shifter operands.
- Rewrites simple instruction patterns, including `EOR $-1,x,y` to `MVN x,y`, duplicate byte/halfword moves, zero compare elimination, and indexed addressing transformations.
- Converts eligible short branch diamonds into predicated ARM instructions via `predicate()`.
- Uses `copyu()`, `copyas()`, `copyau()`, and substitution helpers to classify register use/set behavior across many ARM opcodes.

## Dependencies

Depends on `gc.h`, compiler globals (`firstr`, `zprog`, `debug`), ARM opcode/address enums, and register-flow structures from `reg.c`.

## Risks And Invariants

- Optimization correctness depends on precise single-predecessor/single-successor analysis; ambiguous branches, merges, and calls intentionally stop transformations.
- `copyu()` treats unknown opcodes conservatively as read-alter-write, which protects correctness but limits optimization.
- Predication assumes 5l encoding behavior for CPSR modification and caps predicated chains at four non-NOP instructions.
- Indexed-address rewriting must preserve base-register liveness; helper checks are local and conservative.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/peep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/reg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/reg.c

## Scope

Global register optimizer and data-flow engine for `5c`.

## Behavior

- Builds a control-flow graph of `Reg` nodes from emitted `Prog` instructions.
- Tracks variables as bitsets with `mkvar()`, including globals, parameters, constants, address-taken objects, and physical register use.
- Resolves branch targets, computes reverse postorder/dominators, detects loop structure, and propagates liveness backward.
- Propagates register/variable synchrony forward, computes candidate live regions, ranks them by cost, picks physical registers, and rewrites code with loads/stores.
- Runs the peephole optimizer and then recalculates program counters and branch offsets.

## Dependencies

Uses `gc.h`, compiler `Bits`, `Var`, `Rgn`, `Reg`, `Prog`, type tables, global register arrays, and `peep()` from `peep.c`.

## Risks And Invariants

- Fixed-size region and variable tables (`NVAR`, `NRGN`, `BITS`) bound optimization; overflow degrades or warns rather than resizing.
- `BtoR()` masks out R9/R10 because of Plan 9 ARM conventions for `m` and `g`.
- The algorithm assumes the internal `Prog` list and `Reg` graph remain consistent while inserting moves and excising NOPs.
- Recursion through flow edges can be deep for large functions, matching old compiler assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/reg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/sgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/sgen.c

## Scope

Small architecture-specific support routines for expression complexity and return-value liveness.

## Behavior

- `noretval()` emits artificial NOP uses of integer and floating return registers so later optimization keeps return values live.
- `xcom()` computes ARM addressability and expression complexity for AST nodes.
- Rewrites multiply/divide/modulo by powers of two into shifts or masks where legal.
- Normalizes commutative immediate expressions so constants land on the preferred side.

## Dependencies

Uses `gc.h`, AST `Node` layout, compiler type tables, and helpers such as `vlog()`, `com64()`, and `complex()`.

## Risks And Invariants

- Addressability is encoded as legacy numeric classes (`2`, `3`, `10`, `11`, `12`, `20`) shared with the rest of `5c`.
- Power-of-two rewrites rely on type semantics and are bypassed for 64-bit composite cases via `com64()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/sgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/swt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/swt.c

## Scope

Switch lowering, bit-field access, constant multiply expansion, object serialization, history emission, and alignment logic for `5c`.

## Behavior

- `swit1()`/`swit2()` lower switch statements to linear compares, binary-search branches, or dense `ACASE`/`ABCASE` jump tables.
- `bitload()` and `bitstore()` load, mask, shift, merge, and store C bit-fields.
- `outstring()` batches string data into `ADATA` records.
- `mulcon()` expands multiplication by selected constants using precomputed add/shift recipes.
- `outcode()` emits Plan 9 object records with symbol cache entries, `ANAME`/`ASIGNAME`, instruction encodings, and source history.
- `align()` implements ARM ABI-ish layout for structs, arguments, and automatics.

## Dependencies

Uses `gc.h`, `Biobuf`, compiler object format constants, `Node`, `Sym`, `Prog`, `Hist`, and floating conversion helpers.

## Risks And Invariants

- Object encoding uses small rolling symbol indices (`NSYM`); collisions are handled by re-emitting names.
- `zaddr()` uses fixed buffer assumptions sized for the largest encoded address.
- Dense switch selection is simple range-vs-count heuristics, not profile-aware.
- `align()` encodes little-endian behavior directly and has special pack-flag paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/swt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/txt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/txt.c

## Scope

ARM code emission support for `5c`: initialization, register allocation, address conversion, moves, opcodes, branches, pseudo-ops, and type tables.

## Behavior

- `ginit()` initializes target identity, pseudo nodes, reserved registers, `.safe`, `.rathole`, `.ret`, and 64-bit codegen support.
- `gclean()` checks leaked registers, flushes strings, emits globals, appends `AEND`, and calls `outcode()`.
- Provides temporary and argument register/stack allocation helpers.
- Converts AST nodes to ARM object `Adr` values with `naddr()`/`raddr()`.
- `gmove()` handles loads, stores, integer/floating conversions, sign/zero extension, and unsigned-to-float expansion.
- `gopcode()` maps generic C operations to ARM opcodes and branch conditions.
- Defines scalar type widths and cast compatibility masks.

## Dependencies

Uses `gc.h`, ARM register constants, compiler globals, type tables, `com64init()`, `outcode()`, and Plan 9 object format definitions.

## Risks And Invariants

- Register allocation is simple reference-counted global state; imbalance is caught only at cleanup or `regfree()` diagnostics.
- Some conversions intentionally emit longer compatibility sequences for old ARM/VFP behavior.
- `sconst()` currently accepts most integer constants and delegates actual immediate fit to the linker.
- Stack and argument layout is tied to `align()` in `swt.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/txt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/5i.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/5i.c

## Scope

Main program and process setup for `5i`, the Plan 9 ARM emulator/debugger.

## Behavior

- Opens an ARM executable, initializes Mach symbol/header state, maps text/data/bss/stack segments, builds an emulated Plan 9 stack, and enters the debugger command loop.
- `initmap()` builds lazy-paged segment descriptors and instruction profile storage.
- `initstk()` writes a guest `Tos`, `argc`, `argv`, and strings into emulated memory.
- Provides diagnostics, tracing, register dumps, and zeroing allocation wrappers.

## Dependencies

Uses Plan 9 `libc`, `bio`, `mach`, `tos.h`, and shared emulator definitions from `arm.h`.

## Risks And Invariants

- `reset()` has `for(i = 0; i > Nseg; i++)`, which never iterates; intended segment cleanup appears skipped.
- Stack/Tos construction assumes a 32-bit ARM Plan 9 ABI and host-compatible `Tos` knowledge.
- Segment pages are lazy-loaded from the executable by `mem.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/5i.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/arm.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/arm.h

## Scope

Shared declarations, constants, structs, and globals for the `5i` emulator/debugger.

## Contents

- Defines breakpoint types, instruction classes, register numbers, TLB/cache structures, instruction dispatch entries, CPU register state, memory segments, and memory-copy modes.
- Declares emulator APIs for memory, execution, breakpoints, symbols, commands, syscall dispatch, profiling, and initialization.
- Declares global emulator state: `reg`, `memory`, `text`, `trace`, `sysdbg`, `calltree`, `itab`, `icache`, `tlb`, breakpoints, I/O buffers, profile data, and symbol map.
- Defines Plan 9 ARM constants such as page size, stack top, stack size, condition-code modes, and FP condition bits.

## Dependencies

Includes are supplied by each C file; this header depends conceptually on Plan 9 `Map`, `Biobuf`, `jmp_buf`, and Mach symbol types.

## Risks And Invariants

- Globals are declared through the `EXTERN` macro; exactly one compilation unit (`syscall.c`) defines them.
- Several declared functions are stubs or legacy names, reflecting partial emulator coverage.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/arm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/bpt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/bpt.c

## Scope

Breakpoint management for `5i`.

## Behavior

- Lists instruction, read, write, access, and equality breakpoints with symbolized addresses.
- Adds breakpoints from debugger command text, defaulting to instruction breakpoints.
- Deletes breakpoints by evaluated address.
- `brkchk()` tests address/type matches, handles countdowns, and stops execution by setting `count = 1` and `atbpt = 1`.

## Dependencies

Uses command expression parsing, memory access for equality breakpoints, and shared global breakpoint list from `arm.h`.

## Risks And Invariants

- `delbpt()` increments `membpt` for deleted non-instruction breakpoints; this looks like it should decrement, so memory-breakpoint checks may remain enabled.
- Breakpoints are address exact-match only; no range or symbolic lifetime tracking.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/bpt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/cmd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/cmd.c

## Scope

Interactive debugger command parser and formatter for `5i`.

## Behavior

- Parses expressions from symbols, `#hex`, decimal/octal forms, and one binary operator.
- Handles debugger commands: break/delete/run/continue/step, register/stat dumps, trace flags, memory examine, expression evaluate, and register assignment.
- `pfmt()` prints guest memory or values in numeric, character, string, address, disassembly, source, and global-symbol formats.
- Installs interrupt handler that stops emulation and resumes command processing.

## Dependencies

Uses `bio` I/O, Mach symbol/disassembly APIs, emulator memory APIs, and command helpers from other `5i` files.

## Risks And Invariants

- String memory formats copy into fixed 1024-byte buffers until a guest NUL byte; no explicit bound check in that loop.
- Expression grammar is intentionally minimal.
- Repeating an empty line reuses `lastcmd`; `buf` and `lastcmd` are fixed 128-byte arrays.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/float.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/float.c

## Scope

Placeholder floating-point/cop1 dispatch support for `5i`.

## Behavior

- Defines a table of floating operations and trap helpers.
- Most operation handlers are empty stubs: arithmetic, moves, conversions, load/store, branches, and comparisons do not emulate FP effects.
- `unimp()`, `inval()`, and `ifmt()` report faults and longjmp back to the debugger.

## Dependencies

Uses `arm.h`, `bioout`, and `errjmp`.

## Risks And Invariants

- Floating-point emulation is effectively incomplete; programs depending on FP instructions will run incorrectly unless they trap through unimplemented paths.
- The `cop1` naming is MIPS-like legacy terminology in an ARM emulator source tree.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/float.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/icache.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/icache.c

## Scope

Instruction-cache hook stubs for `5i`.

## Behavior

- `icacheinit()` is empty.
- `updateicache()` accepts an address and marks it used, but performs no cache accounting.

## Dependencies

Uses `arm.h`.

## Risks And Invariants

- `ifetch()` calls `updateicache()` when `icache.on`, but this file provides no implementation, so instruction cache statistics are unavailable.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/icache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/mem.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/mem.c

## Scope

Guest memory and lazy segment paging for `5i`.

## Behavior

- Fetches instructions and reads/writes guest bytes, halfwords, words, and 64-bit values in ARM little-endian order.
- Enforces alignment for instruction fetches and stores; unaligned reads emulate ARM rotation behavior.
- `memio()` copies between host buffers and guest memory, including bounded string reads.
- `dotlb()` maintains simple random-replacement TLB hit/miss stats.
- `vaddr()` maps guest addresses to lazily allocated pages backed by executable text/data or zeroed bss/stack.

## Dependencies

Uses segment setup from `5i.c`, profiling array `iprof`, breakpoint checks, and global `text` file descriptor.

## Risks And Invariants

- `ifetch()` indexes `iprof[(addr-textbase)/PROFGRAN]` without segment-bound checks before `vaddr()` validation.
- Data page partial-read zeroing assumes `foff + n > fileend` captures the final data page case.
- Guest memory faults longjmp to debugger rather than returning errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/run.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/run.c

## Scope

ARM instruction dispatch and execution engine for `5i`.

## Behavior

- Defines the `itab[]` decode-class table for data processing, multiply, swap, load/store, block transfer, branch, branch-link, syscall, and multiply-long classes.
- `run()` fetches, decodes, tests condition codes, executes handlers, advances PC, and checks instruction breakpoints.
- Implements ARM condition evaluation using remembered compare/test operands.
- Implements shifts, ALU operations, multiply/multiply-accumulate, long multiply, swap, word/byte/halfword memory transfers, block load/store, branches, and call tracing.

## Dependencies

Uses `armclass()` from Mach support, memory APIs from `mem.c`, syscall dispatch from `syscall.c`, and symbol helpers for call tracing.

## Risks And Invariants

- Several ARM operations are deliberately unsupported and call `undef()`, including ADC/SBC/RSC and some LDM/STM modes.
- Carry/condition modeling is partial and based on later condition evaluation from saved operands.
- Instruction table indexes depend on external `armclass()` matching the exact table layout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/run.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/stats.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/stats.c

## Scope

Runtime statistics and profiling reports for `5i`.

## Behavior

- `isum()` summarizes instruction counts by operation and broad class.
- `tlbsum()` prints TLB access/hit/miss rates.
- `segsum()` prints segment base/end/resident/reference counts.
- `iprofile()` aggregates per-PC instruction profile buckets into text symbols and prints sorted hot functions.

## Dependencies

Uses `itab`, `tlb`, `memory`, `iprof`, Mach symbol iteration, and source printing.

## Risks And Invariants

- Static `Prof prof[5000]` limits profileable text symbols.
- Division by total count in `iprofile()` assumes at least one profiled count once symbols exist.
- Branch delay-slot counters are carried over from older simulator conventions and are not meaningfully updated by ARM handlers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/symbols.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/symbols.c

## Scope

Source, parameter, local, and stack-trace formatting for `5i`.

## Behavior

- Prints source file/line for guest PCs through Mach symbol APIs.
- Prints locals and parameters by reading guest stack memory according to symbol metadata.
- `stktrace()` walks frames from guest PC/SP until `_main`, printing function calls, parameters, source locations, and optional locals.

## Dependencies

Uses Mach symbols (`findsym`, `findlocal`, `localsym`, `fileline`, `symoff`) and guest memory reads.

## Risks And Invariants

- Stack walking assumes Plan 9 ARM frame conventions and `.frame` local metadata.
- Stops after 40 frames to avoid runaway traces.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/symbols.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/syscall.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/syscall.c

## Scope

Plan 9 syscall emulation layer for `5i`.

## Behavior

- Defines `arm.h` globals and maps guest syscall numbers to host wrapper functions.
- Implements core file/process-memory calls: errstr, bind, fd2path, chdir, close, dup, exits, open, read/pread, seek/oseek, sleep, old/new stat/fstat, write/pwrite, pipe, create, brk, remove, notify.
- Many more complex syscalls are stubs that print “No system call” and exit.
- `Ssyscall()` dispatches from guest R0 (`REGARG`) and flushes debugger output.

## Dependencies

Includes Plan 9 syscall numbers from `/sys/src/libc/9syscall/sys.h`, uses guest memory APIs, and calls host Plan 9 libc syscalls directly.

## Risks And Invariants

- This is a convenience emulator, not a sandbox: guest open/read/write/remove/bind/chdir operate on the host namespace.
- Several wrappers use fixed 1024-byte path buffers and `memio(..., MemReadstring)` for bounded guest strings.
- `sysfd2path()` appears to write `errbuf` rather than the actual `buf` to guest memory on success.
- Unsupported syscalls terminate the emulator instead of returning `ENOSYS`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5i/syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/asm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/asm.c

## Scope

Final assembler/output writer for the Plan 9 ARM linker (`5l`).

## Behavior

- `asmb()` writes text, literal/string text data, data segment, symbols, line tables, dynamic module records, and executable headers for multiple head types.
- Provides buffered byte/word/long writers in big- and little-endian variants.
- Emits Plan 9 symbols and line number tables.
- `datblk()` materializes initialized data/string blocks with endian conversion, floating constants, symbol relocation, and duplicate-initialization checks.
- `asmout()` maps linker `Optab` encoding types to concrete ARM, old FPA, and VFP machine words.
- Helper encoders build ALU, branch, load/store, halfword, VFP memory, literal-load, and floating immediate encodings.

## Dependencies

Uses linker globals from `l.h`, opcode tables from `optab.c`, addressing classification from span logic, dynamic relocation helpers, and ELF writer support.

## Risks And Invariants

- `asmout()` relies on `Optab.type` numbers staying synchronized with `optab.c`.
- Relocation and literal handling uses `p->cond` both for branch targets and literal pool entries.
- Output buffering does not check write return values.
- ARM immediate and offset span diagnostics are late, during final encoding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/asm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/compat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/compat.c

## Scope

Compatibility allocation and file-existence helpers for `5l`.

## Behavior

- Replaces `malloc()` with a hunk allocator backed by `gethunk()`.
- `free()` is a no-op; `calloc()` zeroes hunk allocations.
- `realloc()` aborts if used.
- `mysbrk()` wraps `sbrk()`.
- `fileexists()` checks existence through `stat()`.

## Dependencies

Uses linker hunk globals and `gethunk()` from `obj.c`.

## Risks And Invariants

- Memory is intentionally arena-style and never freed.
- `calloc()` multiplies sizes without overflow checks.
- `realloc()` is unsupported; caller code must not depend on it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/l.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/l.h

## Scope

Central header for `5l`.

## Contents

- Defines linker core structs: `Adr`, `Prog`, `Sym`, `Autom`, `Optab`, `Oprang`, and `Count`.
- Defines symbol types, opcode classification classes, mark flags, buffer sizes, hash limits, hunk size, relocation bit packing, and globals.
- Declares all major linker passes: object loading, patching, data layout, flow ordering, no-op/prologue work, span/literal work, assembly output, imports/exports, diagnostics, and formatting.

## Dependencies

Includes Plan 9 `u.h`, `libc.h`, `bio.h`, ARM object constants from `../5c/5.out.h`, and ELF definitions from `../8l/elf.h`.

## Risks And Invariants

- Uses union field macros heavily; many fields have context-dependent meaning.
- Many global variables are shared across passes, making pass order strict.
- Relocation packing limits are fixed by `Roffset` and `Rindex`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/l.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/l.s -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/l.s

## Scope

Small ARM assembly syntax sample/test file.

## Contents

- Defines a `main` text symbol and exercises ARM instruction syntax accepted by the toolchain.
- Covers shifted operands, conditional instructions, MRC, CPSR/SPSR moves, SWI, SWP, MOVM, and RFE.

## Dependencies

Uses Plan 9 ARM assembler syntax and constants from the assembler/linker pipeline.

## Risks And Invariants

- This is not runtime support code; it is a compact syntax/encoding exercise.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/list.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/list.c

## Scope

Formatting and diagnostics for `5l`.

## Behavior

- Installs custom formatters for opcodes, conditions, addresses, programs, symbols, and string constants.
- `Pconv()` formats linker instructions.
- `Dconv()`/`Nconv()` render ARM address modes, symbols, stack references, constants, shifts, branches, FP constants, and string constants.
- `diag()` prints errors with current function context and exits after too many errors.

## Dependencies

Uses `l.h`, `anames[]`, linker globals, and floating conversion helpers.

## Risks And Invariants

- Formatting uses fixed `STRINGSZ` local buffers.
- `Sconv()` prints only `sizeof(long)` bytes from string constants, matching old object string constant conventions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/noop.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/noop.c

## Scope

Late instruction-list normalization for `5l`.

## Behavior

- Removes NOPs, follows through branch targets past NOPs, detects leaf functions, records frame/become sizes, and emits prologue/epilogue sequences.
- Expands `RET` and special `BECOME` forms into ARM branch/load sequences.
- Rewrites integer division/modulo pseudo-ops into calls to helper routines `_div`, `_divu`, `_mod`, and `_modu`.
- Includes compatibility fixup for old unsigned-to-double code compiled with earlier `5c`.
- Initializes division helper symbols for static and dynamically loadable module modes.

## Dependencies

Uses `l.h`, `prg()`, symbol lookup, text list globals, and helper symbols from object loading.

## Risks And Invariants

- Prologue/epilogue generation assumes Plan 9 ARM stack conventions and link register save/restore forms.
- Division pseudo-op expansion mutates a single instruction into a multi-instruction call sequence and uses `REGTMP`.
- DLM mode can mark helper routines as imports.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/noop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/obj.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/obj.c

## Scope

Main driver, object/archive reader, symbol table, profiling insertion, endian setup, and import/export support for `5l`.

## Behavior

- Parses linker options for output, entry, library paths, text/data addresses, head type, export table, and DLM import mode.
- Loads object files and archives, resolves autolibs, builds symbol and program lists, then runs linker passes: patch, profiling, data layout, flow ordering, noops, span, assembly, undefined checks.
- `ldobj()` reads Plan 9 object streams, handles `ANAME`/`ASIGNAME`, history, text/data/global/dynamic records, branch offsets, floating constants, and duplicate symbols.
- `lookup()` manages versioned symbols in a fixed hash table.
- `gethunk()` grows arena memory.
- `doprof1()`/`doprof2()` inject profiling or tracing instrumentation.
- `nuxiinit()` sets byte-order tables; `ieeedtof()`/`ieeedtod()` convert floating encodings.
- `readundefs()`, `import()`, and `export()` support dynamic module import/export metadata.

## Dependencies

Uses Plan 9 `ar.h`, `l.h`, object format constants, archive format constants, and host filesystem access for objects and libraries.

## Risks And Invariants

- `zaddr()` allocates `sizeof(Ieee)` but subtracts `NSNAME` from `nhunk` for `D_FCONST`, which looks inconsistent.
- Object parsing assumes bounded records and uses fixed read-buffer refill logic.
- Archive symbol-table parsing trusts old Plan 9 archive layout.
- The custom arena allocator means `free()` calls are no-ops under `compat.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/obj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/optab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/optab.c

## Scope

ARM linker opcode selection table.

## Contents

- Defines `optab[]`, the data table mapping abstract `Prog` instructions and operand classes to encoding type, output size, base register parameter, and flags.
- Covers text pseudo-ops, integer ALU, immediate moves, branches, shifts, SWI, words, byte/halfword moves, multiply/divide pseudo-ops, load/store classes, PSR moves, MOVM, SWP, RFE, old FPA, VFP, case tables, relocatable absolute loads/stores, and ARMv4 halfword forms.
- Flags such as `LFROM`, `LTO`, `LPOOL`, `V4`, and `VFP` direct literal pool and architecture-specific handling.

## Dependencies

Consumed by span/buildop/oplook logic and `asmout()` in `asm.c`.

## Risks And Invariants

- Table order and specificity matter for opcode selection.
- Encoding `type` numbers must match `asmout()` cases exactly.
- Architecture flags must match command-line/default `armv4` and `vfp` configuration.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/optab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/pass.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/pass.c

## Scope

Middle linker passes for data layout, undefined checks, branch patching, block ordering, imports, exports, and utility parsing/alignment.

## Behavior

- `dodata()` validates initializers, separates small data, large data, and bss, aligns segments, and defines boundary symbols.
- `undef()` reports unresolved external references.
- `follow()`/`xfol()` reorder text to follow branches, copy small already-followed blocks when useful, and invert conditional branches.
- `patch()` resolves branch symbols to program pointers and collapses branch chains.
- `mkfwd()` builds skip pointers for faster PC-to-program lookup.
- `atolwhex()` parses decimal/octal/hex linker arguments.
- `import()` and `export()` build dynamic linking import/export metadata and `_exporttab` data.
- `ckoff()` validates relocation offset packing.

## Dependencies

Uses global symbol/program lists from `l.h`, `prg()`, `lookup()`, `newdata()` helpers, and dynamic relocation/import helpers.

## Risks And Invariants

- Flow reordering mutates the instruction list destructively and depends on `mark` flags.
- `brloop()` has a loop cutoff to avoid infinite branch-chain following.
- Export sorting uses simple nested loops and arena allocation, appropriate for old small symbol sets.
- Relocation offsets are constrained by fixed bit packing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5l/pass.c -->