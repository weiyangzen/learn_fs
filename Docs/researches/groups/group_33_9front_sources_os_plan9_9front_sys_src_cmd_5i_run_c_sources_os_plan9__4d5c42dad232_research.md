# Group Research: group_33_9front_sources_os_plan9_9front_sys_src_cmd_5i_run_c_sources_os_plan9__4d5c42dad232

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/run.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5i/run.c

This file is the ARM instruction execution core for `5i`, the Plan 9/9front ARM interpreter. It defines the instruction dispatch table `itab[]`, condition-code evaluation, the main fetch/decode/execute loop, and handlers for supported ARM data processing, multiply, swap, load/store, block transfer, branch, branch-with-link, and SWI instructions.

Key elements:
- `itab[]` maps decoded `armclass()` values to handler functions, mnemonic names, and broad instruction categories used by profiling/statistics.
- `run()` fetches from emulated `REGPC`, decodes the instruction class, evaluates the stored compare/test state against the instruction condition field, dispatches the handler if true, advances `REGPC`, and checks breakpoints.
- `runcmp()`, `runteq()`, and `runtst()` implement the interpreter’s simplified condition model using `reg.cc1`, `reg.cc2`, and `reg.compare_op`.
- `shift()` implements ARM shifter operand behavior, including carry-out maintenance.
- `dpex()` implements core data-processing operations and updates comparison/carry state when `Sbit` is present.
- `Idp0` through `Idp3` cover register, shifted-register, register-shifted-register, and rotated-immediate data processing forms.
- `Imul`, `Imula`, and `Imull` implement multiply, multiply-accumulate, and long multiply variants with undefined-instruction checks for illegal register combinations.
- `Imem1` and `Imem2` implement word/byte and halfword/signed-byte memory operations via `getmem_*` and `putmem_*`.
- `Ilsm()` implements LDM/STM for non-PC register lists and rejects PC and `S`-bit cases.
- `Ib()` and `Ibl()` implement PC-relative branch and branch-with-link, with optional call-tree tracing.

Dependencies and integration:
- Relies on global interpreter state from `arm.h`: `reg`, `memory`, tracing flags, breakpoint list, and helper routines.
- Calls `Ssyscall()` for SWI dispatch, implemented in `syscall.c`.
- Uses symbol helpers `findsym()`, `printparams()`, and `printsource()` for call-tree output.

Notable behavior:
- PC reads use ARM pipeline adjustment by adding 8 in operand fetches.
- Branch handlers set `REGPC` to target minus 4 because `run()` increments PC after handler execution.
- Unsupported instructions or illegal encodings call `undef()`, print context, and `longjmp(errjmp, 0)`.
- Several ARM operations are intentionally incomplete, for example ADC/SBC/RSC in `dpex()` trap as undefined.

Research notes:
- This is not a full ARM emulator; it is a practical user-level interpreter for old Plan 9 ARM binaries.
- Memory and syscall behavior are delegated to the emulator runtime rather than modeled here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/run.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/stats.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5i/stats.c

This file reports execution, memory, TLB, and symbol-level profiling statistics for the `5i` ARM interpreter.

Key elements:
- `isum()` walks `itab[]`, totals executed instruction counts, prints per-instruction percentages, and aggregates memory, arithmetic, branch, and syscall categories.
- `tlbsum()` reports TLB hit/miss counts if the interpreter TLB model is enabled.
- `segsum()` prints base/end/resident/reference counts for stack, text, data, and BSS segments.
- `iprofile()` builds function-level profile data from `iprof[]` buckets, maps buckets to text symbols, sorts by count, and prints cycle percentages plus source locations.
- `profcmp()` sorts profile rows descending by count.

Dependencies and integration:
- Uses `Inst itab[]` from `run.c`.
- Uses interpreter globals such as `memory`, `tlb`, `nopcount`, `iprof`, and `textbase`.
- Uses libmach symbol helpers `textsym()` and local `printsource()`.

Notable behavior:
- The instruction-cycle summary treats memory instructions as adding data cycles, printing total “memory cycles” as `mems + total`.
- Branch delay-slot reporting is retained even though ARM itself does not have the same delay-slot semantics as MIPS; it reflects the shared historical simulator reporting style.
- `Prof prof[5000]` is fixed-size and assumes the text symbol count fits.

Research notes:
- This file is reporting-only and does not alter execution except clearing the used profile rows after `iprofile()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/symbols.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5i/symbols.c

This file provides source-location printing, local/parameter display, and stack tracing for `5i`.

Key elements:
- `printsource()` maps a program counter to `file:line` text via `fileline()`.
- `printlocals()` walks local symbols for a function and prints automatic variables read from the emulated stack frame.
- `printparams()` prints function parameters from the frame pointer, skipping the saved PC.
- `stktrace()` walks frames from emulated `PC` and `SP`, stopping at `_main` or after 40 frames.

Dependencies and integration:
- Uses libmach `Symbol` records and helpers such as `findsym()`, `findlocal()`, `localsym()`, `symoff()`, and `fileline()`.
- Reads emulated memory using `getmem_4()`.
- Called by branch tracing in `run.c` and profiling in `stats.c`.

Notable behavior:
- Stack unwinding depends on Plan 9 symbol metadata, especially `.frame`.
- Leaf functions or first-instruction PCs are handled specially using link register `R14`.
- With modifier `'C'`, `stktrace()` also prints locals.

Research notes:
- This is debugger-style support code, tightly coupled to Plan 9 symbol conventions and ARM stack-frame layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/symbols.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/syscall.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5i/syscall.c

This file implements SWI/system-call handling for the `5i` ARM interpreter by translating guest Plan 9 syscall arguments from the emulated stack/registers into host Plan 9 libc calls.

Key elements:
- `sysctab[]` names supported syscall numbers from `/sys/src/libc/9syscall/sys.h`.
- `systab[]` maps syscall numbers to local handler functions.
- `Ssyscall()` reads the call number from `REGARG`, validates it, optionally traces, invokes the handler, and flushes output.
- Implemented syscalls include errstr/errstr variants, bind, fd2path, chdir, close, dup, exits, open, read/pread, seek/oseek, sleep, old/new stat and fstat, write/pwrite, pipe, create, brk, remove, and notify.
- Many syscalls are hard stubs that print “No system call” and exit: wait/await, rfork, wstat/fwstat, noted, segattach/detach/free/flush, rendezvous, unmount, fork/forkpgrp, segbrk, mount, alarm, exec, fsession, fauth, fversion.

Dependencies and integration:
- Uses guest memory helpers `getmem_w()`, `getmem_v()`, `putmem_w()`, `putmem_v()`, and `memio()`.
- Updates `reg.r[REGRET]` with syscall return values.
- Uses interpreter memory segment metadata for `sysbrk_()`.

Notable behavior:
- `sysread()` special-cases guest fd 0, reading from `bin` after printing a `stdin>>` prompt; other reads use `pread()`.
- `syswrite()` reads guest memory into a temporary host buffer before `pwrite()`.
- `sysbrk_()` grows the emulated BSS segment table and enforces data/stack bounds.
- Error text is stored in global `errbuf` and returned through errstr handlers.
- `sysfd2path()` appears suspicious: after successful `fd2path()`, it writes from `errbuf` to guest memory rather than the local `buf` that received the path.

Research notes:
- This is a pragmatic syscall subset, not a full Plan 9 process model.
- Unimplemented calls terminate the interpreter instead of returning `ENOSYS`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5i/syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/asm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5l/asm.c

This file is the final output and machine-code emission stage for the ARM linker `5l`. It writes executable headers, text, data, symbols, line tables, dynamic relocation data, and ARM instruction encodings.

Key elements:
- `entryvalue()` resolves `INITENTRY` to either a numeric address, text symbol, or DLM data symbol.
- `asmb()` emits text instructions, string constants in text, initialized data blocks, symbol/line/dynamic tables, and the selected executable header.
- Header formats include raw/no-header, AIF, Plan 9, NetBSD boot, IXP1200 raw, iPAQ, and ELF.
- `cput()`, `wput()`, `lput()`, `lputl()`, and `cflush()` implement buffered byte/word/long output with endian choices.
- `asmsym()` writes Plan 9 symbol records for text, data, BSS, string, file, frame, auto, and parameter symbols.
- `asmlc()` emits compressed line-number deltas.
- `datblk()` materializes initialized data and text-string blocks from `ADATA`, `AINIT`, and `ADYNT`.
- `asmout()` maps `Optab` cases to one to six ARM words.
- Helpers such as `oprrr()`, `opbra()`, `olr()`, `olhr()`, `osr()`, `ofsr()`, `omvl()`, and `chipfloat()` build specific ARM, old ARM FPA, and VFP encodings.

Dependencies and integration:
- Consumes `Prog` lists and `Optab` classifications from earlier linker passes.
- Uses data layout from `dodata()`, symbol types from `l.h`, and operand classes from `span.c`.
- Adds DLM relocation records through `dynreloc()` when required.

Notable behavior:
- `asmout()` is table-type driven: each `Optab.type` encodes a small code-generation recipe.
- Long constants and long addresses are loaded through literal pools via `omvl()` when `p->cond` points to a pool entry.
- VFP support is selected by global `vfp`; otherwise old ARM 7500-style coprocessor floating-point encodings are used.
- `datblk()` checks for multiple initialization except for DLM init/dynt and duplicate-ok symbols.
- Some emitted ELF comments still refer to PPC flags, but the machine field is ARM.

Research notes:
- This file is the most architecture-specific part of `5l`.
- It assumes earlier passes have resolved PC values, branches, literal pools, data placement, and operand classes correctly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/asm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/compat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5l/compat.c

This file is a tiny compatibility bridge for `5l`.

Key elements:
- Includes `l.h`.
- Includes the shared compiler compatibility implementation from `../cc/compat`.

Dependencies and integration:
- Provides the linker build with common compatibility functions/macros used across Plan 9 compiler tools.

Research notes:
- There is no local logic in this file; it exists to pull shared compatibility code into the `5l` build.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/l.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5l/l.h

This header defines the central data structures, enums, globals, macros, and function prototypes for the ARM linker `5l`.

Key elements:
- `Adr` represents operands, including offset/string/IEEE payloads and auto/symbol links.
- `Prog` represents linker IR instructions with operands, branch condition pointers, PC, line, opcode, condition flags, and register fields.
- `Sym` represents linker symbols with type, version, frame, value, signature, duplicate-ok state, and hash linkage.
- `Autom`, `Optab`, `Oprang`, `Opcross`, and `Count` support auto variables, opcode selection, and reporting.
- Symbol type enum includes `STEXT`, `SDATA`, `SBSS`, `SXREF`, `SLEAF`, `SFILE`, `SCONST`, `SSTRING`, `SUNDEF`, `SIMPORT`, and `SEXPORT`.
- Operand class enum defines register, constants, branch ranges, stack/external/base-offset classes, auto/extern offset widths, and address classes.
- Global state covers output header/layout parameters, text/data lists, symbol hash, library queues, endian maps, opcode ranges, debug flags, DLM/import/export state, literal pools, and division helper symbols.
- Prototypes expose all major linker phases: object loading, patching, data layout, following, no-op/prologue processing, span, assembly, symbol output, operand classification, relocation, profiling insertion, and diagnostics.

Dependencies and integration:
- Includes Plan 9 `u.h`, `libc.h`, `bio.h`, ARM object format `../5c/5.out.h`, and shared compiler compatibility declarations.
- Shared by every `5l` source file in this group.

Research notes:
- `l.h` is the architectural contract between parser/object reader, linker passes, scheduler, span/operand classifier, and assembler output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/l.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5l/list.c

This file implements formatting and diagnostics for `5l` internal instructions and operands.

Key elements:
- `listinit()` installs custom formatters `%A`, `%C`, `%D`, `%P`, `%S`, and `%N`.
- `Pconv()` prints a `Prog` in assembly-like form, handling special forms such as `SWP`, `DATA`, `INIT`, and `DYNT`.
- `Aconv()` maps opcode numbers to names via `anames[]`.
- `Cconv()` formats ARM condition/suffix bits such as `.EQ`, `.S`, `.P`, `.W`, and `.U`.
- `Dconv()` formats operand types: constants, shifts, memory operands, registers, register pairs, F registers, PSR/FPCR, branches, floating constants, and string constants.
- `Nconv()` formats symbol-relative names for extern, static, auto, and parameter operands.
- `Sconv()` escapes string constants.
- `diag()` prints contextual linker diagnostics and aborts after more than 10 errors.

Dependencies and integration:
- Uses globals `curp`, `curtext`, `nerrors`, and `noname`.
- Called by most linker passes for debugging and error reporting.

Notable behavior:
- Branch formatting uses `curp->cond->pc` when branch target has been resolved.
- Versioned symbols are printed using Plan 9 linker conventions.
- `diag()` prefixes messages with current text symbol where available.

Research notes:
- This file is essential for readable linker debug output and error messages, not for output binary semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/noop.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5l/noop.c

This file rewrites the `5l` instruction stream after branch following and before final span. It removes no-ops, detects leaf functions, expands prologues/returns, handles `BECOME`, and lowers integer division/modulo pseudo-ops into helper calls.

Key elements:
- `noops()` performs all main transformations.
- First pass:
  - Tracks maximum frame usage and `BECOME` requirements per text symbol.
  - Marks functions as leaf until calls or division helper needs disprove it.
  - Removes `ANOP` instructions.
  - Retargets branches that point at NOP chains.
- Second pass:
  - Increases caller frame sizes when calls may require max become space.
- Third pass:
  - Emits link-register save/prologue stores for non-leaf or framed functions.
  - Rewrites `RET` into branch-to-link for leaf/no-frame functions or stack-pop-to-PC for normal functions.
  - Rewrites `BECOME` into stack restore plus branch.
  - Patches an old 5c/VFP compatibility sequence around unsigned-to-double conversion.
  - Expands `DIV`, `DIVU`, `MOD`, and `MODU` register operations into stack argument setup, `BL` to helper, result move, and stack cleanup.
- `initdiv()`, `divsig()`, `sigdiv()`, and `sdiv()` resolve or mark division helper symbols `_div`, `_divu`, `_mod`, and `_modu`.
- `nocache()` clears cached optab and operand class fields after mutation.

Dependencies and integration:
- Uses text/prog/symbol state from `l.h`.
- Relies on helper routines from object loading and branch patching.
- Division helper targets are later resolved by `patch()`/`span()`/`asmout()`.

Notable behavior:
- Leaf functions with no autosize can avoid saving the link register.
- `ALEFbecome` is defined to the maximum become space discovered.
- DLM mode can import division helpers instead of requiring local text definitions.

Research notes:
- Despite the filename, this is a major code-shaping pass, not just no-op cleanup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/noop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/obj.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5l/obj.c

This file contains `5l` program startup, command-line handling, object/archive loading, symbol-table management, autolib resolution, profiling insertion, endian initialization, IEEE conversion, and import/export seed handling.

Key elements:
- `main()` parses linker flags, chooses output format/header defaults, initializes global state, loads objects and libraries, then runs the linker pipeline: `patch()`, profiling, `dodata()`, `follow()`, `noops()`, `span()`, `asmb()`, `undef()`.
- `isobjfile()` distinguishes regular object files from archives or other files.
- `loadlib()` repeatedly loads queued autolibraries until no unresolved references are resolved.
- `objfile()` opens a regular object or archive. Archive mode reads `__.SYMDEF`, scans unresolved symbols, and loads only needed members.
- `ldobj()` decodes Plan 9 ARM object records, including `ANAME`, `ASIGNAME`, `AHISTORY`, `AEND`, `AGLOBL`, `ADYNT`, `AINIT`, `ADATA`, `ATEXT`, and normal instructions.
- `zaddr()` decodes serialized operands and registers auto/param symbols for current text.
- `addlib()` expands `$O`/`$M` in autolib paths and queues unique libraries.
- `addhist()`, `histtoauto()`, and `collapsefrog()` preserve source history path metadata.
- `lookup()` manages linker symbols in a versioned hash table.
- `doprof1()` and `doprof2()` insert two styles of profiling/tracing instrumentation.
- `nuxiinit()`, `ieeedtof()`, and `ieeedtod()` handle byte order and floating conversion.
- `readundefs()` marks symbols as import/export candidates from user-provided lists.

Dependencies and integration:
- Uses Plan 9 archive format from `<ar.h>`.
- Produces `Prog` lists and `Sym` entries consumed by all later linker passes.

Notable behavior:
- Duplicate text with `DUPOK` is skipped by replacing instructions with NOPs.
- Floating constants unsupported as immediate chip floats are materialized as data literals.
- Static symbols are versioned per object to avoid name collision.
- `INITENTRY` defaults to `_main` or `_mainp` for profiling.

Research notes:
- This file is the front half and orchestration center of `5l`.
- It tightly couples Plan 9 object-stream encoding with the linker’s in-memory IR.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/obj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/optab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5l/optab.c

This file defines the ARM linker opcode-selection table `optab[]`.

Key elements:
- Each `Optab` row maps an opcode plus operand classes to:
  - an emission recipe type used by `asmout()`,
  - instruction size in bytes,
  - optional base register parameter,
  - flags such as `LFROM`, `LTO`, `LPOOL`, `V4`, and `VFP`.
- Covers ARM data processing, constants, shifts, branches, SWI, words, byte/half/word loads/stores, MOVM, SWP/LDREX/STREX, RFE/CLREX, barriers, old FPA, VFP, case dispatch, and address-relocation forms.
- Final row `{ AXXX, ... }` terminates the table.

Dependencies and integration:
- Consumed by `buildop()` and `oplook()` in `span.c`.
- Emission recipe numbers are interpreted by `asmout()` in `asm.c`.

Notable behavior:
- Long-offset or relocatable forms deliberately expand to multi-instruction sequences.
- ARMv4 and VFP rows can be disabled depending on debug flags processed in `buildop()`.
- Some aliases share opcode ranges after `buildop()` copies `oprange[]` entries.

Research notes:
- This table is declarative machine-code policy for `5l`.
- Correctness depends on consistency among operand classes in `l.h`, classification in `span.c`, and recipe handling in `asm.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/optab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/pass.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5l/pass.c

This file implements core linker middle-end passes: data layout, unresolved-symbol checks, branch resolution, instruction following/reordering, numeric parsing, rounding, and import/export table construction.

Key elements:
- `dodata()` validates data initializers, optionally marks string constants, lays out small data first, then larger data, then BSS, and defines `setR12`, `bdata`, `edata`, `end`, and `etext`.
- `undef()` reports remaining `SXREF` symbols.
- `patch()` resolves branch/call/return targets from symbols to `Prog.cond` pointers and branch offsets.
- `mkfwd()` creates skip-forward links to accelerate PC-to-`Prog` lookup during patching.
- `brloop()` and `brchain()` collapse chains of unconditional branches.
- `follow()` and `xfol()` reorder text for fallthrough, copy small followed blocks where helpful, and invert conditional branches to improve layout.
- `relinv()` maps conditional branch opcodes to their inverse.
- `atolwhex()` parses decimal, octal, and hex numeric options.
- `rnd()` rounds addresses/sizes upward.
- `import()` converts selected undefined signed symbols into import records.
- `export()` builds `_exporttab` and `.string` data containing signatures, addresses, and symbol names.

Dependencies and integration:
- Consumes symbols and `Prog` lists from `obj.c`.
- Produces data layout and control-flow state for `noops()`, `span()`, and `asmb()`.

Notable behavior:
- Data layout aligns symbols to 4 bytes and segment totals to 8 bytes.
- `follow()` may duplicate a small instruction sequence to avoid awkward control flow.
- Branches to undefined dynamic symbols become `UP` sentinel branches for later relocation handling.
- Export names are packed into `NSNAME`-sized string data chunks.

Research notes:
- This is the architecture-neutral-looking but ARM-specific linker middle-end for `5l`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/pass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/sched.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5l/sched.c

This file implements a local instruction scheduler for `5l`, focused on avoiding ARM load, branch, and floating-compare stalls by reordering instructions or inserting NOPs.

Key elements:
- `Sch` wraps a `Prog` plus computed dependency sets, memory offset/size, NOP count, and compound-instruction flag.
- `Dep` stores integer register, floating register, and condition/memory dependency bitsets.
- `sched()` builds scheduling metadata for a basic block, runs prepasses to group independent loads and move useful instructions near loads, then fills delay/stall slots or inserts NOPs.
- `regused()` computes used/set dependency bits from opcode and operand classes.
- `depend()` determines whether two instructions may be interchanged.
- `conflict()` checks adjacent hazard conflicts.
- `offoverlap()` determines memory overlap for stack/SB-offset references.
- `compound()` treats multiword optab forms or writes to `REGSB` as compound.
- `dumpbits()` prints dependency sets for debug output.

Dependencies and integration:
- Uses `aclass()`, `regoff()`, `oplook()`, `addnop()`, and `Count nop` globals from the larger linker.
- Operates on `Prog` sequences after earlier rewriting and before final emission.

Notable behavior:
- Memory dependencies distinguish generic memory, SP-relative memory, and SB-relative memory.
- Loads from the same hardware-like address are not allowed to pass each other.
- It counts missed scheduling opportunities in verbose mode.
- It may insert two NOPs for PSR use-then-set hazards.

Research notes:
- This scheduler is conservative and local; it avoids changing semantics with bitset dependency checks rather than global analysis.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/sched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/span.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/5l/span.c

This file assigns final PCs, manages literal pools, classifies operands, selects optab rows, builds opcode lookup ranges, and emits dynamic relocation records for `5l`.

Key elements:
- `span()` walks the final instruction list, assigns PCs, selects optab rows, adds literal pool entries for long constants/addresses, flushes pools when needed, computes text size, and sets `INITDAT`.
- `checkpool()`, `flushpool()`, and `addpool()` manage PC-relative literal pools and insert branch-around-pool instructions when required.
- `xdefine()` defines special symbols if still undefined.
- `regoff()` returns the computed effective offset for an address operand.
- `immrot()`, `immaddr()`, `immfloat()`, and `immhalf()` classify immediate encodability.
- `aclass()` maps `Adr` operands to the operand classes used by `optab[]`.
- `oplook()` selects the best matching `Optab` row for a `Prog`, caching the result.
- `cmp()` defines class compatibility and widening relationships.
- `ocmp()` and `buildop()` sort `optab[]`, disable unsupported V4/VFP rows, build `oprange[]`, and populate alias ranges.
- `dynreloc()` records sorted dynamic relocation entries.
- `asmdyn()` writes import and relocation metadata for dynamically loadable modules.

Dependencies and integration:
- Consumes `optab[]` from `optab.c`.
- Feeds selected `Optab` rows to `asmout()` in `asm.c`.
- Uses symbol/data layout from `pass.c` and DLM import state from `obj.c`.

Notable behavior:
- External/static addresses normally become SB-relative offsets using `BIG`; DLM mode uses different absolute/relocatable classification.
- Literal pool flushing is driven by 12-bit PC-relative span limits.
- The literal-pool logic contains an explicit historical BUG comment: after flush, it no longer refers back to prior values until out of range.
- Dynamic relocation addresses must be word-aligned and are delta-encoded later by `asmdyn()`.

Research notes:
- This file is the bridge between abstract linker IR and concrete ARM encoding constraints.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/5l/span.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6a/a.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6a/a.h

This header defines the shared assembler state and data structures for `6a`, the amd64 assembler.

Key elements:
- `Sym` stores assembler symbols, macro text, values, lexical type, and object-file symbol cache index.
- `Gen` is the assembler operand structure with floating/string constants, offset, symbol, type, index register, and scale.
- `Gen2` packages source and destination operands for grammar reductions.
- `Io` and `Hist` track input streams and source history.
- Global state includes debug flags, symbol hash, `-D` definitions, include directories, input stack, line number, output path, program counter, token text, architecture identity, and output buffer.
- Function prototypes cover input/macro handling, parsing, symbol lookup, operand/object encoding, history emission, diagnostics, and assembly entry points.

Dependencies and integration:
- Includes amd64 object definitions from `../6c/6.out.h`.
- Includes shared compiler compatibility declarations.

Research notes:
- This is the contract among `a.y`, `lex.c`, generated parser code, and shared lexer/macro bodies.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6a/a.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6a/a.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6a/a.y

This file is the yacc grammar for the amd64 assembler `6a`.

Key elements:
- Defines token value types for symbols, integers, floats, string constants, operands, and operand pairs.
- `prog` and `line` parse labels, statements, blank lines, and error recovery.
- `inst` handles symbol assignment and dispatches instruction token classes to specialized operand grammars.
- Operand pair nonterminals normalize instruction forms into `Gen2`.
- Special grammar forms handle:
  - `DATA` as `name/size, immediate`,
  - `TEXT`/`GLOBL` as memory plus flags/frame,
  - `JMP`/`CALL` style relative or indirect targets,
  - `NOP`,
  - shifts with optional double-precision register suffix,
  - MOVW/MOVL with optional index suffix,
  - SIMD compare/shuffle immediate forms,
  - far returns with optional immediate.
- Operand grammar covers registers, immediates, strings, floats, memory addressing, symbol-relative names, static `<>` names, SP/FP/SB/PC pointers, and constant expressions.

Dependencies and integration:
- Emits object records by calling `outcode()`.
- Uses `checkscale()` for x86 addressing scale validation.
- Uses `pc` for PC-relative branches and `pass` for undefined-label diagnostics.

Notable behavior:
- Expressions support unary plus/minus/complement and binary arithmetic, shifts, and bitwise operators.
- Indexed memory addressing supports base plus index times scale.
- Undefined labels are tolerated in pass 1 and rejected in pass 2.

Research notes:
- This grammar converts Plan 9 assembler syntax into the compact `Gen` representation later serialized by `lex.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6a/a.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6a/lex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6a/lex.c

This file implements `6a` startup, keyword/register initialization, two-pass assembly orchestration, object-record serialization, source-history emission, and inclusion of shared lexer/macro bodies.

Key elements:
- `main()` sets architecture identity (`6`, `amd64`), initializes symbols, parses flags, supports `-o`, `-D`, and `-I`, and can assemble multiple files in parallel using `NPROC`.
- `assemble()` derives output filename, configures include paths, opens output, runs parser pass 1, then emits history and runs parser pass 2.
- `itab[]` maps names to token classes and opcode/register/address values. It includes:
  - SP/SB/FP/PC pseudo-registers,
  - byte, word, long, MMX, XMM, segment, control/debug/test registers,
  - core x86 opcodes,
  - amd64 opcodes,
  - FPU opcodes,
  - conditional jumps and conditional moves,
  - SSE/MMX/3DNow-style media opcodes,
  - instruction synonyms.
- `cinit()` initializes `nullgen`, symbol hash, predefined symbols/opcodes, and current working directory.
- `checkscale()` enforces x86 index scales of 1, 2, 4, or 8.
- `cclean()` emits `AEND` and flushes output.
- `zname()` writes `ANAME` records.
- `zaddr()` writes compact operand encodings with flags for type, index, offset, float, symbol, string, and 64-bit offset.
- `outcode()` serializes instructions in pass 2 and maintains object symbol cache slots.
- `outhist()` serializes source path history as `ANAME` and `AHISTORY` records.
- Includes `../cc/lexbody`, `../cc/macbody`, and `../cc/compat`.

Dependencies and integration:
- Parser actions from `a.y` call `outcode()`.
- Object format constants and opcode IDs come from `6.out.h`.

Notable behavior:
- `outcode()` increments `pc` for most instructions but not `AGLOBL`, `ADATA`, or `AMODE`.
- Symbol cache slots wrap within `NSYM`; if source and destination choose the same cache slot, serialization restarts.
- On Plan 9, default include path is `/<arch>/include`; environment `INCLUDE` can override/add paths.
- Multi-file assembly is disabled on Windows.

Research notes:
- This file is both lexer initialization and object writer; the actual lexical scanner and macro implementation are included from shared compiler sources.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6a/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/6.out.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6c/6.out.h

This header defines the Plan 9 amd64 object instruction and address namespace shared by `6a`, `6c`, and related tools.

Key elements:
- Defines `NSYM`, `NSNAME`, and text flags `NOPROF` and `DUPOK`.
- `enum as` lists amd64 assembler opcode IDs:
  - legacy x86 integer/control/string opcodes,
  - jumps and calls,
  - FPU instructions,
  - object pseudo-ops `ADATA`, `AGLOBL`, `AHISTORY`, `ANAME`, `ATEXT`, `AEND`, `ADYNT`, `AINIT`, `ASIGNAME`,
  - 32-bit extensions,
  - conditional move opcodes,
  - 64-bit opcodes,
  - SSE/MMX/media opcodes,
  - newer rounding/dot-product forms,
  - `ALAST` terminator.
- Address/register enum defines byte registers, general registers, high-byte registers, FPU/MMX/XMM registers, segment registers, descriptor/control/debug/task registers, addressing classes, object operand type flags, and compiler register conventions.
- Defines `SYMDEF` archive index name.
- Defines `Ieee`, the split high/low representation of IEEE floating constants.

Dependencies and integration:
- Included by `6a/a.h` and amd64 compiler/linker code.
- Values are serialized into object files, so numeric stability matters.

Research notes:
- This file is a shared ABI for Plan 9 amd64 compiler tools, not just local declarations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/6.out.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/cgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6c/cgen.c

This file is the amd64 backend expression and structure code generator for `6c`.

Key elements:
- `cgen()` emits code for scalar expressions, assignments, bitfields, unary ops, shifts, arithmetic/logical ops, multiplication/division/modulo, compound assignments, function calls, indirection, comparisons, boolean expressions, casts, field selection, conditionals, comma expressions, and pre/post increment/decrement.
- Handles evaluation order carefully when both sides may contain function calls (`complex >= FNX`) by spilling temporaries.
- Uses x86 architectural constraints:
  - variable shifts use `CX`,
  - division/modulo use `AX` and `DX`,
  - structure copies use `SI`, `DI`, and `CX`.
- Optimizes common constants:
  - zero add/sub cases,
  - shift-left-by-one as add,
  - multiply/add address forms via `genmuladd()`,
  - multiply/divide/modulo by constants through `mulgen()`, `sdiv2()`, `smod2()`, `sdivgen()`, and `udivgen()`.
- `reglcgen()` and `lcgen()` compute lvalue addresses, preserving constant offsets through indirection when possible.
- `bcgen()` and `boolgen()` generate branches or materialized boolean values.
- `sugen()` handles struct/union copies, struct literals, function-returned structs, conditional struct expressions, and block copy lowering.
- Small structure copies use scalar MOVL/MOVQ/MOVB loops; larger copies use `CLD; REP; MOVSL` plus optional byte tail copy.
- Utility functions include `layout()`, `immconst()`, `hardconst()`, `castup()`, `zeroregm()`, `vaddr()`, `hi64v()`, `lo64v()`, `hi64()`, `lo64()`, and `cond()`.

Dependencies and integration:
- Relies on backend helpers from `gc.h` and other `6c` files: register allocation, instruction emission, type tables, bitfield helpers, argument generation, branch patching, and opcode lowering.
- Calls division helper routines from `div.c`.

Notable behavior:
- The file has several historical comments marked “TO DO” and one disabled cast optimization block.
- It warns on pointer-to-shorter-integer casts.
- For comparisons involving floating point, relation mapping is adjusted through `logrel`/`invrel`.
- `vaddr()` determines whether a vlong source/destination can be accessed directly or needs address loading.

Research notes:
- This is a classic Plan 9 C backend: compact, direct, and strongly coupled to x86 register constraints.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/cgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/div.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/6c/div.c

This file implements optimized amd64 code generation for division and modulo by invariant 32-bit integer constants, based on Granlund and Montgomery’s multiplication method.

Key elements:
- `multiplier()` computes a magic multiplier and shift amount for a divisor.
- `sdiv()` derives signed-division multiplier/shift metadata and whether an add adjustment is needed.
- `udiv()` derives unsigned-division metadata, including pre-shift handling for even divisors and adjustment cases.
- `sdivgen()` emits signed constant-division code using `IMULL`, high-half result in `DX`, sign correction, shift, and optional negation.
- `udivgen()` emits unsigned constant-division code using `MULL`, optional pre-shift, adjustment add/rotate, and final shift.
- `sext()` materializes the sign extension of a value, using `CDQ` when source is `AX` and `DX` is available.
- `sdiv2()` optimizes signed division by powers of two with bias correction and arithmetic shift.
- `smod2()` optimizes signed modulo by powers of two with sign correction.

Dependencies and integration:
- Called from `cgen.c` for scalar divide/modulo and compound divide/modulo when the divisor is a suitable constant.
- Uses backend emitters and register helpers from `gc.h`.

Notable behavior:
- Power-of-two signed division/modulo is handled separately from general magic-multiplier division.
- Negative signed divisors are handled by generating a positive division then negating the quotient where needed.
- The implementation is limited to 32-bit-style constant division paths used by `typechl` cases in `cgen.c`.

Research notes:
- This file is a small but performance-sensitive backend optimization module.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/6c/div.c -->