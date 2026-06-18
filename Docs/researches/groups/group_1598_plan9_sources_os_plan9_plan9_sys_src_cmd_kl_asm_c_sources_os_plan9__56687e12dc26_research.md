# Group Research: group_1598_plan9_sources_os_plan9_plan9_sys_src_cmd_kl_asm_c_sources_os_plan9__56687e12dc26

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/asm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/asm.c

Read fully: 1242 lines, 26122 bytes. SHA-256 prefix: `06243f0af240915d`.

This is the final assembly/output backend for the Plan 9 SPARC linker `kl`. It writes text, data, symbols, line tables, and executable headers. `asmb()` drives emission: it seeks past the header, walks `firstp`, validates phase/PC consistency, calls `oplook()` and `asmout()` for instruction encoding, writes data blocks with `datblk()`, emits symbols with `asmsym()`, emits line number compression with `asmlc()`, then rewrites the executable header for boot, Plan 9, or Javastation formats.

Important routines:
- `entryvalue()` resolves `INITENTRY` as either numeric address or text symbol.
- `lput()`/`cflush()` implement buffered big-endian word output.
- `putsymb()` serializes Plan 9 symbol-table entries, including filename symbols.
- `datblk()` materializes initialized data from `ADATA`/`AINIT`/`ADYNT`, handling integer, string, and IEEE float constants with host-to-target byte order tables.
- `asmout()` maps `Optab.type` cases to SPARC encodings, including synthetic long constant/address sequences, loads/stores, ASI accesses, branches/calls, floating-point operations, division/modulus expansions, and annulled delay-slot optimizations.
- `opcode()` maps linker opcodes to SPARC op/op2/op3/floating/trap/branch encodings.

Dependencies are almost entirely linker-global state from `l.h`: `firstp`, `datap`, `curtext`, `autosize`, `textsize`, `datsize`, `symsize`, `lcsize`, endian tables, and debug flags. It depends on `oplook()`/`Optab` from `span.c`/`optab.c`, symbol lookup from `obj.c`, and IEEE conversion helpers.

Risk notes: encoding is table-driven but many `asmout()` cases assume exact operand classes and register conventions. Branch-delay-slot filling calls `asmout(..., aflag)` speculatively and only works for encodings that can safely be lifted. Data initialization detects overlapping non-`AINIT` writes but uses a fixed scratch allowance (`n+100`).
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/asm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/compat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/compat.c

Read fully: 65 lines, 704 bytes. SHA-256 prefix: `d7e14d473640839e`.

This file provides linker-local compatibility shims for allocation and file existence. It overrides `malloc()`, `calloc()`, `free()`, `realloc()`, `mysbrk()`, `setmalloctag()`, and `fileexists()`.

The allocator is a simple bump allocator over linker hunks: `malloc()` rounds to 8-byte alignment, calls `gethunk()` until enough space exists, then advances `hunk` and reduces `nhunk`. `calloc()` zeroes the allocated region. `free()` is a no-op. `realloc()` is deliberately unsupported and aborts if called. `mysbrk()` delegates to `sbrk()`. `fileexists()` uses `stat()` into a fixed buffer and treats any successful stat as existence.

Integration: `obj.c` and the linker’s symbol/program constructors rely on this hunk allocator, so normal libc allocation semantics do not apply inside `kl`.

Risk notes: there is no deallocation and no `realloc()`. This is appropriate for a one-shot linker but unsafe for code that expects general-purpose heap behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/cputime.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/cputime.c

Read fully: 30 lines, 336 bytes. SHA-256 prefix: `d89655368e1a7bc8`.

This is a small Unix compatibility file for the linker. `cputime()` calls `times()`, sums user/system child and process slots, and returns hundredths as seconds. `seek()` wraps `lseek()`. `create()` wraps `creat()` but only accepts mode `1`, returning `-1` otherwise.

Integration: used by verbose timing logs in the linker pipeline and by `obj.c`/`asm.c` output creation and seeking. The wrappers preserve Plan 9-style names expected elsewhere in the code.

Risk notes: `create()` is intentionally narrow and does not emulate all Plan 9 open modes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/cputime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/l.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/l.h

Read fully: 330 lines, 5406 bytes. SHA-256 prefix: `16ad6b39ab26511e`.

This is the central private header for the SPARC linker. It defines the core IR structures `Adr`, `Prog`, `Sym`, `Auto`, and `Optab`; operand classes; symbol types; scheduler mark flags; global linker state; and function prototypes.

Key structures:
- `Adr`: instruction operand, with offset/string/IEEE payload, symbol/auto link, type, register, name, and cached class.
- `Prog`: instruction node with `from`, `to`, branch/linear links, PC, register-use metadata, line, mark flags, optab cache, opcode, and auxiliary register.
- `Sym`: linker symbol with name, type, version, become/frame metadata, value, and hash link.
- `Optab`: instruction-selection table row used by `oplook()` and `asmout()`.

It also declares all shared globals: text/data lists, symbol hash, output buffers, debug flags, endian tables, header/layout constants, profiling helper program pointers, and scheduling/assembly state.

Integration: every `kl/*.c` file includes this header. It is the contract between object loading, patching, data layout, scheduling, span, and assembly.

Risk notes: this codebase relies on global mutable state and cached operand classes. Any mutation of `Adr` operands after classification must clear or recompute class fields.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/l.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/list.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/list.c

Read fully: 258 lines, 4502 bytes. SHA-256 prefix: `c64a84e2e8647b3a`.

This file installs and implements Plan 9 `Fmt` printers for linker diagnostics and assembly listings. `listinit()` registers `%A`, `%D`, `%P`, `%S`, and `%N`. `prasm()` prints a single `Prog`.

The converters format:
- `Pconv()`: complete instruction, including data pseudo-ops, explicit registers, special memory forms, and NOSCHED marker.
- `Aconv()`: opcode name via `anames`.
- `Dconv()`: operand by type, including registers, constants, branches, strings, IEEE constants, and offset/address forms.
- `Nconv()`: symbol-qualified names for extern, static, auto, and parameter addressing.
- `Sconv()`: string constants with C-style escapes.
- `diag()`: emits errors with current text symbol context and aborts after too many errors.

Integration: diagnostics throughout the linker use these formatters, especially illegal instruction combinations, bad object records, and debug listings.

Risk notes: `Pconv()` assigns `curp = p`, so formatting has side effects used by branch operand formatting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/noop.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/noop.c

Read fully: 650 lines, 11140 bytes. SHA-256 prefix: `2a573be829dbf241`.

This file performs major late IR cleanup and expansion before scheduling. `noops()` identifies leaf functions, computes frame and `BECOME` sizes, removes `ANOP`, marks labels/branches/synchronization points, expands prologues/epilogues, lowers `RETURN` and `BECOME`, optionally expands integer multiply/divide/modulo into calls to runtime helper symbols, and finally schedules bounded basic blocks with `sched()`.

Important behavior:
- Marks text symbols as `SLEAF` where no call/prologue save is needed.
- Inserts stack adjustment and saved link register stores for non-leaf functions.
- Converts returns into `AJMP` through link registers or restores link from stack.
- Tracks maximum `BECOME` space and defines `ALEFbecome`.
- Uses `initmuldiv()` to locate `_mul`, `_div`, `_divl`, `_mod`, `_modl`.
- Splits scheduling regions at labels, branches, sync instructions, NOSCHED spans, and `NSCHED` size.

Risk notes: transformation order matters. `ANOP` stripping assumes `q` is a preceding non-nop. Helper expansion mutates the original arithmetic instruction into stack adjustment and inserts a call sequence after it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/noop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/obj.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/obj.c

Read fully: 1379 lines, 23646 bytes. SHA-256 prefix: `917b12c34dcad30f`.

This is the main driver and object/archive loader for the SPARC linker. `main()` parses options, initializes header defaults, library paths, output file, instruction table, symbol state, endian tables, and the initial program list. It loads input objects and libraries, then runs the full linker pipeline: `patch()`, optional profiling insertion, `dodata()`, `follow()`, `noops()`, `span()`, `asmb()`, and `undef()`.

Core components:
- `objfile()` loads regular object files or Plan 9 archives, resolving archive members through the `__.SYMDEF` index and unresolved `SXREF` symbols.
- `ldobj()` decodes `.k` object records, including `ANAME`, `AHISTORY`, `AGLOBL`, `ADATA`, `ADYNT`, `AINIT`, `ATEXT`, and normal instructions.
- `zaddr()` decodes serialized operands and records auto/param metadata.
- `addlib()` interprets history records for autolib paths, replacing `$O` and `$M`.
- `lookup()`, `prg()`, and `gethunk()` allocate symbols and program nodes from linker hunks.
- `doprof1()` and `doprof2()` inject profiling/tracing instrumentation.
- `nuxiinit()`, `ieeedtof()`, and `ieeedtod()` support target byte order and floating constants.

Integration: this file owns the lifecycle of the linker’s global state and supplies allocation and symbol lookup for all other `kl` passes.

Risk notes: archive loading loops until no new xrefs resolve. Object parsing is byte-oriented and treats malformed records as fatal. Duplicate `TEXT` handling respects `DUPOK` by turning skipped code into nops.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/obj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/optab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/optab.c

Read fully: 199 lines, 7369 bytes. SHA-256 prefix: `53cca30ee5ca727a`.

This file is the SPARC linker’s instruction-selection table. `optab[]` maps abstract opcodes and operand classes to an `asmout()` type, emitted byte size, and optional base register parameter.

The table covers pseudo-ops, moves, immediate constants, short and long memory references, ASI loads/stores, processor register moves, byte/halfword extension moves, arithmetic/logical ops, compare variants, jumps/calls/branches/traps, floating-point loads/stores/ops, word literals, division/modulus synthetic sequences, and annulable conditional branches.

Integration: `span.c` sorts and indexes this table in `buildop()`, `oplook()` caches matching rows in each `Prog`, and `asm.c` interprets `type` values to emit actual SPARC words.

Risk notes: the numeric `type` values are an implicit contract with the large `asmout()` switch. Any table edit must keep size/type/operand-class semantics consistent.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/optab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/pass.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/pass.c

Read fully: 551 lines, 9340 bytes. SHA-256 prefix: `99e4622eb545f572`.

This file implements middle linker passes for data layout, undefined-symbol checks, branch inversion, control-flow following, branch patching, and numeric parsing/alignment.

Key behavior:
- `dodata()` validates data initializers, lays out small data first, then large data, then BSS; creates literal data symbols for large constants or symbolic addresses; defines `setSB`, `bdata`, `edata`, `end`, and `etext`.
- `undef()` reports remaining unresolved xrefs.
- `relinv()` returns inverse conditional branches where safe.
- `follow()`/`xfol()` reorder code into a followed control-flow order, cloning short sequences when useful and inserting jumps where needed.
- `patch()` resolves branch and call targets, converts symbolic calls to `D_BRANCH`, builds forward pointers with `mkfwd()`, and collapses branch chains with `brloop()`.
- `atolwhex()` parses decimal, octal, and hex with sign handling.
- `rnd()` aligns values.

Integration: runs after object loading and before no-op/prologue expansion. It establishes symbol addresses and branch `cond` pointers consumed by `noops()`, `span()`, and `asmout()`.

Risk notes: `dodata()` mutates constants into literal memory references. `xfol()` clones instructions in followed blocks and relies on mark flags to avoid infinite traversal.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/pass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/sched.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/sched.c

Read fully: 672 lines, 10796 bytes. SHA-256 prefix: `8bab760459cf4c11`.

This is the local instruction scheduler for SPARC delay slots and hazards. It models a bounded block as `Sch` entries containing a copied `Prog`, sets/uses dependency masks, memory offset/size, and flags for inserted nops or compound instructions.

`sched()` builds side structures for a block, then scans backward to:
- fill branch delay slots with earlier safe instructions,
- separate load/use pairs when a non-conflicting instruction is available,
- handle floating compare followed by branch delays,
- insert nops when no safe fill exists.

`regsused()` classifies instruction dependencies over integer registers, floating registers, condition codes, and memory spaces (`MEM`, `SP`, `SB`). `depend()`, `conflict()`, and `offoverlap()` decide reorder safety. `compound()` treats multiword encodings and `REGSB` writes as not freely movable.

Integration: called by `noops()` for block ranges split by labels, branches, sync instructions, and scheduler-size limits. Uses `aclass()`, `regoff()`, and `oplook()` from `span.c`.

Risk notes: memory aliasing is conservative but offset-based only within recognized SP/SB spaces. Compound instruction detection depends on final `Optab.size`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/sched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/span.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/span.c

Read fully: 524 lines, 10152 bytes. SHA-256 prefix: `6a16438fc5ae21db`.

This file assigns final PCs, classifies operands, and builds optimized opcode lookup ranges.

Important routines:
- `span()` walks the final instruction list from `INITTEXT`, assigns `pc`, consults `oplook()` for size, updates text symbol values, rounds text size, and computes `INITDAT`.
- `xdefine()` defines linker-generated symbols if not already defined.
- `regoff()` and `aclass()` compute effective offsets and classify operands into constants, registers, branches, stack/global memory forms, extern/static/auto/param addressing, ASI, and special registers.
- `oplook()` matches a `Prog` to a cached `Optab` row using operand classes and comparison matrix `xcmp`.
- `cmp()`, `ocmp()`, and `buildop()` build compatibility and sorted opcode ranges, also aliasing related opcodes to shared table ranges.

Integration: used by scheduling, span, and assembly. `aclass()` depends on symbol types and layout values from `dodata()` and text values from `patch()`/`span()`.

Risk notes: there is a commented-out alternative for external constants and an unconditional `return C_LCON` for one case, indicating a known historical workaround. Cached operand classes can become stale if operands are mutated later.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kl/span.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kprof.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/kprof.c

Read fully: 142 lines, 2664 bytes. SHA-256 prefix: `33efe7aa4b8ad1e6`.

This command reads a kernel text binary and profiling data, attributes PC-bucket counts to text symbols, sorts by time, and prints a profile table.

`main()` opens the text file, parses its executable header with `crackhdr()`, initializes symbols with `syminit()`, reads big-endian counter data, prints total/in-kernel/outside counts, compares kernel base against the first text symbol, then walks text symbols accumulating buckets at `PCRES` resolution. Nonzero totals become `COUNTER` entries sorted by `compar()` and printed as milliseconds, percentage, and symbol name.

Dependencies: Plan 9 `mach` library for executable headers and symbols, `bio` for buffered output.

Risk notes: assumes profiling data begins with total and outside-kernel counters, followed by PC buckets. Sorting is ascending and printed backward for descending output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/kprof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ktrace.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ktrace.c

Read fully: 403 lines, 7222 bytes. SHA-256 prefix: `85c621c4c9617472`.

This command reconstructs kernel stack traces from a kernel binary, initial PC/SP, optional link register, and either interactive or stdin-provided memory values.

`main()` parses `[-i] kernel pc sp [link]`, initializes the executable header/symbol table, chooses a trace routine based on magic, reads stack address/value pairs from stdin unless interactive, and calls the selected walker. Trace implementations cover RISC-style frame/link handling (`rtrace()`), generic CISC `pc2sp()` unwinding (`ctrace()`), i386 interrupt-frame special cases, and amd64 `_intrr` interrupt-frame handling. `printaddr()` emits `src(...)`-style lines with symbol comments.

Dependencies: Plan 9 `mach` symbols, frame symbol `.frame`, `pc2sp()`, `findsym()`, `findlocal()`, and `symoff()`.

Risk notes: stops after 40 frames and uses architecture-specific heuristics. Noninteractive stack lookup is exact address matching in fixed arrays of 1024 entries.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ktrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lens.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/lens.c

Read fully: 268 lines, 5109 bytes. SHA-256 prefix: `cabfdd68436c1136`.

This is an interactive graphical screen magnifier. It opens `/dev/screen`, reads the screen image metadata, allocates a backing buffer and output image, then lets mouse/keyboard events choose the magnified center, zoom level, grid visibility, redraw, or exit.

Key routines:
- `drawit()` redraws the red border and magnified image.
- `makegrid()` builds an optional checker-pattern grid scaled to zoom.
- `eresized()` reattaches/resizes the window and reallocates the temporary image.
- `magnify()` reads the relevant screen rows, expands pixels by `mag`, loads scanlines into the temp image, and overlays the grid.

Dependencies: Plan 9 `draw` and `event` libraries plus `/dev/screen` layout.

Risk notes: requires screen depth of at least 8 bits and assumes bytes-per-pixel is `depth/8`. `out[8192]` bounds depend on window width and pixel depth.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lens.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lex/header.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/lex/header.c

Read fully: 114 lines, 3368 bytes. SHA-256 prefix: `495c3f667c6aea23`.

This file emits the generated C scanner prelude and trailer for Plan 9 `lex`. `phead1()` writes typedefs, includes, macros, scanner globals, `yywork`/`yysvf` structures, and either Plan 9 `read`/`write` based `input()`/`output()` helpers when `-9` is active or stdio macros otherwise. `phead2()` emits the main `yylook()` switch loop. `ptail()` closes the generated `yylex()` action switch once. `statistics()` reports table usage and generation counts.

Integration: called from `parser.y` during section transitions and from `lmain.c` after parsing. It writes to global `fout`.

Risk notes: output is generated with raw `Bprint()` fragments, so correctness depends on exact ordering from parser actions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lex/header.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lex/ldefs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/lex/ldefs.h

Read fully: 181 lines, 4151 bytes. SHA-256 prefix: `01f36996af8d6595`.

This is the shared header for the Plan 9 `lex` implementation. It defines scanner-generator constants, token/tree node codes, default table sizes, packed-table feature flags, section identifiers, booleans, and all global variables used across `lmain.c`, `parser.y`, `sub1.c`, `sub2.c`, and `header.c`.

Major definitions include character count `NCH=256`, token/tree limits, regex node tags such as `RCCL`, `RSTR`, `RCAT`, `STAR`, `FINAL`, `S1FINAL`, and `S2FINAL`, and generated-table arrays such as `gotof`, `nexts`, `state`, `verify`, `advance`, and `stoff`.

Integration: it is the full internal ABI of the lexer generator. Most source files rely on shared globals rather than passing state.

Risk notes: static array limits are user-tunable through `%` directives, but allocation and overflow checks remain manual.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lex/ldefs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lex/lmain.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/lex/lmain.c

Read fully: 296 lines, 6173 bytes. SHA-256 prefix: `ead3db77e0529ab7`.

This is the main program and storage manager for Plan 9 `lex`. It defines the generator’s global state, parses options (`-t`, `-v`, `-n`, `-9`, debug options under `DEBUG`), opens input and output, initializes the default `INITIAL` start condition, runs `yyparse()`, generates follow sets and DFA states, packs tables, appends the runtime driver from `/sys/lib/lex/ncform`, and optionally prints statistics.

Memory setup is staged:
- `get1core()` allocates definitions, start conditions, and character-class storage.
- `get2core()` allocates DFA construction arrays after parsing.
- `get3core()` allocates final packed output tables.
- matching `free*core()` routines release earlier stages.

Integration: orchestrates parser actions from `parser.y`, helper logic from `sub1.c`/`sub2.c`, and output routines from `header.c`.

Risk notes: global state and staged frees mean later phases assume earlier arrays are no longer needed except where explicitly retained.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lex/lmain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lex/parser.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/lex/parser.y

Read fully: 653 lines, 14273 bytes. SHA-256 prefix: `dd3ce82327374264`.

This is the yacc grammar and lexical front-end for the `lex` specification language. The grammar parses definitions, delimiters, rules, actions, regular expressions, start conditions, right context, anchors, character classes, strings, alternation, concatenation, repetition, and counted iteration. Semantic actions build regex parse trees with `mn0()`, `mn1()`, `mn2()`, `mnp()`, and `dupl()`.

`yylex()` is a hand lexer for the lex input file. It handles:
- definition section directives like `%p`, `%n`, `%e`, `%o`, `%a`, `%k`, `%{...%}`, and `%s`,
- transition to rules at `%%`,
- action copying and generated case labels,
- quoted strings, character classes, escaped characters, definitions `{name}`, counted iterations, and start-condition lists `<...>`,
- section-three passthrough after the second delimiter.

`freturn()` exists under debug builds to report tokens.

Integration: produces parse-tree arrays consumed by `sub1.c` and `sub2.c`, and emits generated scanner action code through `fout`.

Risk notes: token buffers and generator tables have fixed limits with explicit errors. Action copying and section handling are sensitive to newline/indentation conventions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lex/parser.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lex/sub1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/lex/sub1.c

Read fully: 621 lines, 10306 bytes. SHA-256 prefix: `778a1977c48bb5a9`.

This file contains front-half helpers for `lex`: diagnostics, input buffering, escapes, definition lookup, action copying, parse-tree construction, character-class intersection, duplication, and debug dumps.

Important routines:
- `printerr()`, `error()`, and `warning()` format source-aware messages.
- `lgate()` emits the generated header once.
- `cclinter()` refines packed character classes when a new class is seen.
- `usescape()` decodes C-style escapes and octal escapes.
- `lookup()` finds definitions/start conditions.
- `cpyact()` copies user action code, tracking braces, strings, comments, and `|` fallthrough pseudo-actions.
- `mn0()`, `mn1()`, `mn2()`, `mnp()` allocate parse-tree nodes and compute nullable state.
- `munputc()`/`munputs()` implement pushback.
- `dupl()` clones regex subtrees.
- debug-only routines print chars, strings, sections, and trees.

Integration: used directly by `parser.y` and later phases for parse-tree manipulation.

Risk notes: manual lexical copying of C actions is heuristic and must correctly handle comments/strings/braces to avoid corrupting generated scanner code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lex/sub1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lex/sub2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/lex/sub2.c

Read fully: 851 lines, 17044 bytes. SHA-256 prefix: `87e0fc10f8d6afdc`.

This file is the DFA construction and table-packing backend for `lex`. It computes follow sets, initial states, transitions, fallback states, action tables, character-class compression, and final `yycrank`, `yysvec`, `yymatch`, and `yyextra` output.

Key routines:
- `cfoll()`, `follow()`, and `first()` compute regex follow/first-position sets.
- `add()` and optional `padd()` store position sets.
- `cgoto()` creates DFA states for each start condition and line-begin variant, computes transitions, and emits `yyvstop`.
- `nextstate()` calculates destination position sets for a state/character.
- `notin()` interns/reuses existing states.
- `packtrans()` compresses transitions, optionally using character-class representatives and fallback states.
- `acompute()` generates ordered action lists for final states and right-context handling.
- `mkmatch()` creates fallback character representatives.
- `layout()` packs transition tables into the final generated C arrays.

Integration: consumes parse-tree arrays from parser/sub1 and writes generated code to `fout`.

Risk notes: this is table-size sensitive. `nextstate()` is called for every state/character pair and is noted as the dominant CPU cost.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lex/sub2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lnfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/lnfs.c

Read fully: 781 lines, 13332 bytes. SHA-256 prefix: `15660ed50240b787`.

This is a user-level 9P filesystem that overlays a directory and maps long or space-containing names to short filesystem-safe names. It mounts over a mountpoint, serves 9P requests over a pipe, and maintains `./.longnames` as the translation database. Long names are shortened to the first `NAMELEN-1` bytes of base32-encoded MD5.

9P handlers include version, attach, walk, open, create, read, write, clunk, remove, stat, and wstat. Directory reads translate short names back to long names. Creates and wstats translate long names to short names, adding entries to `.longnames` when writable. `readnames()` refreshes the translation cache based on `.longnames` qid/length.

Integration: uses Plan 9 `fcall`, `String`, `libsec` MD5/base32, mount/srv posting, and local filesystem syscalls.

Risk notes: explicitly no authentication. `-r` enforces read-only behavior for creates/writes/wstats and namefile mutation. Fid state is manually managed and reused.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lnfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lock.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/lock.c

Read fully: 170 lines, 2728 bytes. SHA-256 prefix: `5c4a83a46bb8c95d`.

This command keeps an exclusive lock file open while running a command. It ensures the named lock file has `DMEXCL`, opens it read/write, forks a keeper process that periodically writes to maintain activity, then runs the requested command or `rc` by default in a child with a custom prompt.

Options:
- `-d` increments debug flag, though it is not otherwise used.
- `-w` waits until the lock opens instead of failing immediately.

After the command exits, it posts a note to kill the keeper, waits for it, reports nonempty status, and exits with the command’s status.

Dependencies: Plan 9 exclusive files, `rfork`, environment file `/env/prompt`, notes, and wait messages.

Risk notes: lock acquisition uses file exclusivity and a keeper process rather than advisory locking. Interrupt notes are continued by `notifyf()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/look.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/look.c

Read fully: 347 lines, 6034 bytes. SHA-256 prefix: `5d1941acf5ef799d`.

This is a Plan 9 implementation of `look`, performing binary search over a sorted dictionary and printing matching entries. It supports directory-order filtering, case folding, interactive stdin keys, numeric comparison, custom field terminator, exact matching, and an alternate dictionary file.

Important routines:
- `locate()` binary searches to the first possible matching line.
- `acomp()` compares runes with prefix-aware return codes.
- `torune()` converts UTF strings.
- `rcanon()` canonicalizes through terminator, directory filtering, case folding, and Latin-1 fold table.
- `ncomp()` compares numeric fields including sign, integer and fractional parts.
- `getword()` reads newline-delimited rune records.

Integration: uses `Biobuf` rune I/O and defaults to `/lib/words`.

Risk notes: reverse numeric order is declared but not implemented beyond `rev=1`. Word buffers are fixed at `WORDSIZ`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/look.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lp/LOCK.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/lp/LOCK.c

Read fully: 57 lines, 1066 bytes. SHA-256 prefix: `9af1d14a501a58de`.

This helper creates and maintains an exclusive printer lock file. It expects `LOCK lockfile hostname ppid`, creates the lock file with `DMEXCL`, writes `hostname ppid`, forks, and lets the parent exit successfully while the child keeps the lock alive. The child polls file status and zero-length writes until the file disappears, empties, or write fails, then posts a kill note to the parent process group.

Integration: intended for the lp subsystem’s queue/daemon locking workflow.

Risk notes: kill behavior targets the supplied parent process group. The lock lifetime depends on the child process and exclusive file semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lp/LOCK.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lp/ipcopen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/lp/ipcopen.c

Read fully: 92 lines, 1607 bytes. SHA-256 prefix: `f2c732abf91a86bb`.

This command dials a Plan 9 network endpoint built as `network!destination!service`, opens its data file for reading and writing, then forks bidirectional byte copying between local stdin/stdout and the remote connection.

`pass()` copies until EOF or an initial single NUL byte. The child copies remote-to-stdout, then hangs up. The parent copies stdin-to-remote, then hangs up.

Dependencies: Plan 9 `dial()`, network device directory paths, `hangup()`.

Risk notes: minimal error handling and no protocol framing beyond raw byte pass-through. Some local variables in `pass()` are unused shadows.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lp/ipcopen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lp/lpdaemon.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/lp/lpdaemon.c

Read fully: 448 lines, 9910 bytes. SHA-256 prefix: `9416d4299d9513e4`.

This is a portable LPD/lp receiver daemon. It reads requests from stdin, accepts BSD lpr-style control/data file transfers or simpler local lp protocol input, writes jobs to temporary files, extracts user/host from control files, constructs arguments, and forks the local `lp` command.

Key routines:
- `error()` appends timestamped logs.
- `forklp()` logs and executes `LP` with parsed args.
- `tempfile()` creates unlinked temporary files.
- `readline()` and `readfile()` implement line and counted-data protocol reads with ACK/NAK and alarms.
- `getfiles()` receives LPD control and data files.
- `getjobinfo()` parses `H` and `P` control-file records.
- `main()` parses first command byte and builds the lp argument vector for queue, receive, remove, or direct print paths.

Integration: conditional paths support Plan 9, V10, SYSV, and BSD host environments.

Risk notes: manual varargs logging is nonportable. Argument and line buffers are fixed. Protocol timeouts are alarm-based.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lp/lpdaemon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lp/lpdsend.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/lp/lpdsend.c

Read fully: 439 lines, 9580 bytes. SHA-256 prefix: `731f608ac4611f2f`.

This is an LPD client sender. It connects to a remote printer service, optionally queries queue status, kills a job, or sends a print job using LPD control/data file protocol.

Important routines:
- `copyfile()` copies data with timeout and progress messages.
- `killjob()` sends LPD remove-job command.
- `checkqueue()` sends queue status command and copies response to stderr.
- `getack()` validates single-NUL acknowledgements.
- `senddata()` and `sendctrl()` send LPD data/control files.
- `sendjob()` starts a receive-printer-job request and sends data then control.
- `netmkaddr()` fills default network/service components.
- `main()` parses options, prepares stdin/file input, dials remote printer from reserved source ports 721-731, gets hostname, and dispatches action.

Risk notes: `tmpnam()` is used for stdin temp files on non-Plan 9 path. Source-port retry is hardcoded. Option `-t` switch appears to test current `filetype` rather than `optarg[0]`, which may be a historical bug.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lp/lpdsend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lp/lpsend.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/lp/lpsend.c

Read fully: 318 lines, 6064 bytes. SHA-256 prefix: `25f16e415b7663e2`.

This command sends a print job to a network lp daemon using a simple two-step protocol: read an options line from stdin, spool the remaining stdin to a temporary file to know its size, dial the destination, send options, send size, wait for ACK, send data, send ACK, wait for final ACK, then relay daemon response to stdout.

It contains compatibility branches for Plan 9 and non-Plan 9 systems. Helpers include `readline()`, `pass()`, `prereadfile()`, `tempfile()`, `recvACK()`, and alarm/error handling.

Integration: pairs naturally with `lpdaemon.c`’s non-BSD/simple protocol path.

Risk notes: temp file names are predictable (`/tmp/lp<pid>.<idx>` on non-Plan 9). Uses alarms to prevent network hangs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lp/lpsend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lp/tonet.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/lp/tonet.c

Read fully: 59 lines, 913 bytes. SHA-256 prefix: `e9b889fb221ef1f7`.

This is a minimal utility that dials a Plan 9 network address and copies stdin to the connection. `pass()` loops with a 10-minute alarm around each read/write cycle. `alarmhandler()` catches alarm notes and reports `alarm`. `main()` validates a single `network!destination!service` argument, installs the alarm handler, dials with default network `"net"`, and copies.

Risk notes: one-way only; no response is read. Timeout handling reports but returns through Plan 9 note handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/lp/tonet.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ls.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ls.c

Read fully: 326 lines, 5723 bytes. SHA-256 prefix: `2af09045bde4ef0e`.

This is Plan 9 `ls`. It supports flags for directory-as-file, long output, muid, no sort, path prefix, qid/version, reverse, size blocks, time sort, temp marker, access time, file suffixes, and unquoted names.

`ls()` stats each argument, reads directories when needed, stores `Dir` pointers plus optional prefixes, and calls `output()`. `output()` sorts unless disabled, computes column widths, and formats each entry. `format()` emits selected fields using Plan 9 formatters. `compar()` sorts by name/prefix or time and applies reverse. `asciitime()` chooses recent vs old timestamp display. `xcleanname()` compresses slashes and strips trailing slashes.

Risk notes: modifies argument strings in place when splitting path prefixes. Directory buffers are resized with `realloc()` and entries from `dirreadall()` are retained until output flush.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/index.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/index.c

Read fully: 86 lines, 4345 bytes. SHA-256 prefix: `cfdca8a35661375e`.

This file is the projection registry for the Plan 9 map program. It wraps projection constructors with uniform two-argument `Y...` adapters, then populates `struct index index[]` with projection name, constructor, parameter count, cut function, display flags, spheroid flag, and limb function.

Entries include projections such as `aitoff`, `albers`, `azequalarea`, `bonne`, `conic`, `guyou`, `hex`, `mercator`, `orthographic`, `sp_albers`, `tetra`, and others.

Integration: `map.c` likely looks up this table by projection name and uses associated cut/limb handlers.

Risk notes: many wrappers reference constructors not in this group. Table consistency depends on `map.h`’s `struct index` layout and projection function signatures.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/index.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/iplot.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/iplot.h

Read fully: 51 lines, 1398 bytes. SHA-256 prefix: `727f7ccda4947686`.

This header provides plot-style drawing macros that emit textual plotting commands via `print()`. It is an alternative to `plot.h`.

Macros include `openpl`, `closepl`, `erase`, `point`, `range`, `text`, `vec`, `move`, `pen`, color constants, `colorcode`, and `colorx`. Text is quoted only when it starts with a space.

Integration: map/plot code can include this header to target a command-stream plotting backend.

Risk notes: all drawing APIs are macros with direct `print()` side effects. Arguments may be evaluated in macro contexts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/iplot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/aitoff.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/aitoff.c

Read fully: 26 lines, 397 bytes. SHA-256 prefix: `fd7431e4ede851e2`.

Implements the Aitoff projection. `aitoff()` initializes a zero lat/lon pole and returns `Xaitoff`. The projection halves longitude, normalizes the place relative to `Xaitpole` and twist, applies azimuthal equal-area projection, then doubles x.

Dependencies: `copyplace`, `sincos`, `norm`, `latlon`, and `Xazequalarea`.

Risk notes: uses static shared projection state, so initialization is global rather than per-instance.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/aitoff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/albers.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/albers.c

Read fully: 117 lines, 2397 bytes. SHA-256 prefix: `31ad7fe8f49fa5b9`.

Implements spherical and spheroidal Albers equal-area conic projection plus inverse/scale helpers. `albinit()` normalizes standard parallels, handles degenerate cases by returning azimuthal/cylindrical alternatives, computes eccentricity-dependent constants, and returns `Xspalbers`. `sp_albers()` uses `EC2`, while `albers()` uses zero eccentricity.

`albscale()` computes inverse-based twist/scale for a reference point. `invalb()` inverts x/y back to latitude/longitude iteratively.

Dependencies: `deg2rad`, `azequalarea`, `cylequalarea`.

Risk notes: projection constants are static globals, so concurrent different Albers instances would conflict.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/albers.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/azequalarea.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/azequalarea.c

Read fully: 19 lines, 274 bytes. SHA-256 prefix: `f554c2aa78749b73`.

Implements azimuthal equal-area projection. `Xazequalarea()` computes radius `sqrt(1 - sin(latitude))` and maps west longitude sine/cosine to x/y. `azequalarea()` returns the projection function.

Dependencies: caller supplies normalized `struct place` with precomputed sine/cosine fields.

Risk notes: no parameter state and always returns success.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/azequalarea.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/azequidist.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/azequidist.c

Read fully: 19 lines, 290 bytes. SHA-256 prefix: `a23ad7335c8caf1d`.

Implements azimuthal equidistant projection. `Xazequidistant()` computes colatitude and maps it by west longitude sine/cosine. `azequidistant()` returns the projection function.

Risk notes: no clipping or failure cases; assumes normalized coordinates.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/azequidist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/bicentric.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/bicentric.c

Read fully: 25 lines, 437 bytes. SHA-256 prefix: `ffb50f5a8e758d6f`.

Implements bicentric projection parameterized by an angle `l`. `bicentric()` rejects near-polar parameters over 89 degrees, stores the center coordinate, and returns `Xbicentric`. The projection rejects points near longitude or latitude cosine zero, computes x/y by tangent-like formulas, and returns whether the point lies within radius-squared 9.

Risk notes: static `center` means one active parameterization at a time.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/bicentric.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/bonne.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/bonne.c

Read fully: 36 lines, 661 bytes. SHA-256 prefix: `74b0aaafa790df52`.

Implements Bonne projection. `bonne(par)` returns sinusoidal projection for near-zero standard parallel, otherwise stores the standard parallel and `r0`, returning `Xbonne`. `Xbonne()` computes radius and angular displacement, with special handling near the projection apex and poles, then maps to x/y.

Dependencies: `Xsinusoidal`, `deg2rad`.

Risk notes: the static function lacks an explicit return type in old C style. Uses static projection parameters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/bonne.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/ccubrt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/ccubrt.c

Read fully: 13 lines, 226 bytes. SHA-256 prefix: `044aa388b848b109`.

Provides `ccubrt()`, a complex cube-root helper. It converts input to polar form, cube-roots the radius using `cubrt()`, divides angle by three, and returns rectangular coordinates.

Integration: used by advanced projections such as `hex.c`.

Risk notes: returns one principal cube root only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/ccubrt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/complex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/complex.c

Read fully: 85 lines, 1592 bytes. SHA-256 prefix: `6c05702d6df7af8e`.

Provides complex arithmetic helpers for map projections: robust-ish division `cdiv()`, multiplication `cmul()`, square `csq()`, square root `csqrt()`, and power `cpow()`.

`cdiv()` chooses the larger denominator component to reduce overflow/underflow risk. `csqrt()` uses magnitude-based formulas and preserves imaginary sign. `cpow()` uses polar exponentiation.

Integration: used by projections with conformal/elliptic transformations.

Risk notes: comments explicitly say addition/subtraction overflow is not guarded. `cpow()` is defined on one line in K&R-compatible style but with modern parameter declaration syntax.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/complex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/conic.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/conic.c

Read fully: 27 lines, 496 bytes. SHA-256 prefix: `335fab8b286b8617`.

Implements a simple conic projection. `conic(par)` returns cylindrical projection for near-equatorial parallels, otherwise stores the standard parallel and returns `Xconic`. The projection rejects points more than 80 degrees from the standard parallel, computes radius from tangent displacement, maps longitude scaled by sine of standard parallel, and returns clipped status when radius is large.

Dependencies: `Xcylindrical`, `deg2rad`.

Risk notes: static state holds only one standard parallel.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/conic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/cubrt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/cubrt.c

Read fully: 30 lines, 329 bytes. SHA-256 prefix: `9bdbddf175662834`.

Provides real cube root `cubrt()`. It handles sign, scales the magnitude into a stable range by factors of 8, then applies Newton iteration until convergence.

Integration: used by `ccubrt()` and projection math.

Risk notes: convergence threshold is absolute (`10.e-15`) and loop has no explicit iteration cap.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/cubrt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/cuts.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/cuts.c

Read fully: 39 lines, 844 bytes. SHA-256 prefix: `7ffc05e2f067826c`.

This file provides stub definitions for `picut()`, `ckcut()`, and `reduce()` so `libmap` can stand alone. Comments explain that real implementations live in `map.c`, but unusual projections (`hex.c`, `guyou.c`, `tetra.c`) need these names.

Each stub calls `abort()` and returns a dummy value.

Risk notes: if these stubs are linked instead of the real map program versions, projections using cut logic will abort at runtime.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/cuts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/cylequalarea.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/cylequalarea.c

Read fully: 24 lines, 355 bytes. SHA-256 prefix: `72e41132551d3df2`.

Implements cylindrical equal-area projection parameterized by standard parallel. `cylequalarea(par)` rejects parallels over 89 degrees, computes scale `cos(par)^2`, and returns `Xcylequalarea`. The projection maps x to scaled longitude and y to sine latitude.

Risk notes: static scale `a` is shared globally.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/cylequalarea.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/cylindrical.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/cylindrical.c

Read fully: 19 lines, 287 bytes. SHA-256 prefix: `4d14a8a65239a8a6`.

Implements a simple cylindrical projection. `Xcylindrical()` rejects latitudes beyond 80 degrees, maps x to negative longitude, and y to tangent latitude (`sin/cos`). `cylindrical()` returns that function.

Risk notes: returns `-1` for rejected high-latitude points; caller must handle that status.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/cylindrical.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/elco2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/elco2.c

Read fully: 132 lines, 2533 bytes. SHA-256 prefix: `7835c6d81b1fb145`.

Implements a complex elliptic integral routine based on Bulirsch, plus helpers `cdiv2()` and `csqr()`. `elco2()` computes an integral from `0` to `x+iy` with parameters `kc`, `a`, and `b`, returning success/failure and output `u,v`. It rejects `kc==0` or negative `x`, handles sign of `y`, iterates arithmetic-geometric style updates until `k <= CC`, and combines stored correction terms.

Integration: used by projections such as Guyou and hex that map through elliptic functions.

Risk notes: fixed arrays of 13 correction terms assume convergence before overflow. Accuracy near branch points is documented as reduced.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/elco2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/elliptic.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/elliptic.c

Read fully: 35 lines, 627 bytes. SHA-256 prefix: `40febc9261cdbfdc`.

Implements an elliptic projection parameterized by longitude separation `l`. `elliptic(l)` rejects over 89 degrees, returns azimuthal equidistant for under 1 degree, otherwise stores `center` and returns `Xelliptic`. The projection computes two angular distances, derives x from squared-distance difference and y from remaining squared-distance sum, preserving hemisphere sign.

Risk notes: `center` is a global `struct coord`, not static, so it may be externally visible.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/elliptic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/fisheye.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/fisheye.c

Read fully: 26 lines, 407 bytes. SHA-256 prefix: `349760d971b8188d`.

Implements a refractive fisheye projection. `fisheye(par)` stores refractive parameter `n` and rejects values below `0.1`. `Xfisheye()` computes `u = sin(pi/4 - lat/2)/n`, rejects near-limit values, maps through `tan(asin(u))`, and projects by longitude sine/cosine.

Risk notes: static parameter `n`; returns `-1` when outside projection domain.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/fisheye.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/gall.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/gall.c

Read fully: 29 lines, 512 bytes. SHA-256 prefix: `fb6d1da6dcac2cde`.

Implements a Gall-style projection parameterized by standard latitude. `gall(par)` rejects absolute parameter over 80 degrees, computes an x scale from half-angle cosine, and returns `Xgall`. The projection computes y as `tan(lat/2)` using one of two formulas for numerical stability, and x as scaled negative longitude.

Risk notes: static `scale` supports only one active parameterization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/gall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/gilbert.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/gilbert.c

Read fully: 51 lines, 1210 bytes. SHA-256 prefix: `13808efe85fa2561`.

Implements Gilbert projection. `Xgilbert()` maps the sphere to a hemisphere by transforming latitude via `tan(lat/2)` and longitude by half, clamps transformed sine to `[-1,1]`, then presents the hemisphere orthographically. `gilbert()` returns this projection function.

The file includes a derivation comment explaining stereographic projection to plane, square root mapping to a half plane, and inverse stereographic projection.

Risk notes: always returns success and does not clip by hemisphere edge beyond internal clamp.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/gilbert.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/guyou.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/guyou.c

Read fully: 101 lines, 1754 bytes. SHA-256 prefix: `5393501fa448fbd7`.

Implements Guyou and square projections using stereographic mapping plus elliptic integral transformation. `guyou()` initializes constants, hemisphere centers, twist, and side length, then returns `Xguyou`. `Xguyou()` chooses east/west hemisphere, normalizes, stereographically projects, calls `dosquare()`, and offsets x. `square()` initializes Guyou state and returns `Xsquare`, which maps hemispheres to square layout with special antipodal handling.

`guycut()` delegates to map cut helpers and imposes a cut at longitude zero with extra checks near lower latitudes.

Dependencies: `cdiv`, `elco2`, `norm`, `Xstereographic`, `picut`, `ckcut`.

Risk notes: relies on real cut helpers, not `cuts.c` stubs. Static state is shared between Guyou and square.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/guyou.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/harrison.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/harrison.c

Read fully: 40 lines, 708 bytes. SHA-256 prefix: `b8d06137690124ef`.

Implements Harrison projection with view/object geometry parameters `r` and `alpha`. `harrison()` computes unit/view constants, rejects invalid geometry, and returns `Xharrison`. The projection maps a spherical point to 3D components, computes perspective divisor, rejects near/behind cases, maps x/y, and clips by sign and radius.

Risk notes: returns both `0` and `-1` for different rejection/clipping cases. Static parameters are global to the projection.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/harrison.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/hex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/hex.c

Read fully: 122 lines, 2283 bytes. SHA-256 prefix: `fd39dd8f49d25d13`.

Implements a hexagonal world projection with special cut handling. `hex()` initializes cut longitudes, elliptic constants, reference geometry, reflection centers, and returns `Xhex`. `Xhex()` handles northern/southern symmetry, equator/cut singularities, normalizes to a hemisphere, stereographically projects, applies complex algebra including cube root and square root, runs `elco2()`, and reflects southern points across hex edges. `hexcut()` tests whether an edge crossing is acceptable against three cut longitudes.

Dependencies: `reduce`, `ckcut`, `latlon`, `norm`, `Xstereographic`, `cdiv`, `csq`, `ccubrt`, `csqrt`, `elco2`.

Risk notes: requires real map cut helpers. Many static constants are initialized by calling the projection during setup; reentrancy is not supported.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/hex.c -->