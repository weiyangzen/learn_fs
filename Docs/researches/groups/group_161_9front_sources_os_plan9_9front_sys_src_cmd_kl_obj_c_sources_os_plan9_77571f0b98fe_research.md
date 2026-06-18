# Group Research: group_161_9front_sources_os_plan9_9front_sys_src_cmd_kl_obj_c_sources_os_plan9_77571f0b98fe

Scope confirmed from `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/obj.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kl/obj.c

This is the main driver and object/archive reader for the Plan 9 SPARC linker variant `kl`. It parses linker flags, selects output header mode, initializes linker globals, loads object files and libraries, runs patch/data/layout/scheduling/codegen passes, and writes `k.out` by default.

Key behavior:
- Handles `-o`, `-E`, `-T`, `-D`, `-R`, `-H`, debug flags, and default output profiles for boot, Plan 9, and JavaStation boot headers.
- `objfile()` detects regular object files versus Plan 9 archives, reads archive symbol tables, and repeatedly loads members that satisfy unresolved `SXREF` symbols.
- `ldobj()` decodes Plan 9 object records into `Prog` nodes, tracks `ANAME`/`ASIGNAME` symbol tables, handles `AHISTORY`, `ATEXT`, `ADATA`, `AGLOBL`, `ADYNT`, and `AINIT`, resolves branch offsets relative to object-local pc, and synthesizes float literal data for `AFMOVF`/`AFMOVD`.
- `lookup()` owns the linker symbol hash table with per-object static symbol versions.
- `addlib()`, `addhist()`, `histtoauto()`, and `collapsefrog()` manage history/autolib path metadata.
- `doprof1()` and `doprof2()` inject profiling/tracing instructions and data.
- `nuxiinit()`, `find1()`, `ieeedtof()`, and `ieeedtod()` provide target/endian and floating conversion helpers.

Dependencies are almost entirely through `l.h`: global linker state, opcode/register constants, `Prog`, `Adr`, `Sym`, `Auto`, `Optab`, diagnostics, and later passes. The file also depends on Plan 9 archive layout from `<ar.h>` and Bio I/O.

Notable risks: the code assumes trusted Plan 9 object/archive formats and uses fixed-size buffers plus unchecked `malloc`; malformed input usually ends in diagnostics or process exit rather than recovery. It is single-process, global-state linker code, not a reusable parser.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/obj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/optab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kl/optab.c

This file defines `optab[]`, the SPARC instruction selection/encoding table used by `oplook()` and later assembly emission. Each row maps an opcode plus operand classes to an encoding case number, instruction size, and optional implicit register.

The table covers text/nop records, integer moves, constants, memory forms, ASI accesses, processor registers, arithmetic/comparison forms, jumps/branches/traps, floating-point moves/compares/ops, raw words, division/modulo helper forms, and aliases that are expanded in `buildop()`.

It has no executable logic beyond the table. Its correctness depends on class definitions and assembler emission cases in the rest of the `kl` backend matching these numeric encoding cases and sizes exactly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/optab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/pass.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kl/pass.c

This file implements major middle-end linker passes for data placement, symbol validation, branch patching, and code-following.

Key functions:
- `dodata()` validates data initializers, assigns small data before larger data/BSS, inserts literal pool entries for large constants/address constants, adjusts final data/BSS offsets, and defines linker symbols `setSB`, `bdata`, `edata`, `end`, and `etext`.
- `undef()` reports unresolved `SXREF` symbols.
- `relinv()` returns inverse conditional branch opcodes for control-flow layout.
- `follow()`/`xfol()` reorder text to follow likely control flow, copy short already-followed sequences when useful, and synthesize jumps when needed.
- `patch()` resolves branch and call targets from symbol values to `Prog.cond` pointers, using `mkfwd()` skip links for faster lookup, and collapses jump chains through `brloop()`.
- `atolwhex()` parses decimal/octal/hex command arguments.
- `rnd()` aligns addresses.

The file consumes the symbol table and program list built by `obj.c` and prepares them for `span()`/`asmb()`. It assumes global linker state and Plan 9 assembler conventions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/pass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/sched.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kl/sched.c

This file implements local instruction scheduling for SPARC delay and hazard handling. It builds a temporary `Sch` array for a basic scheduling window, annotates each instruction with registers/condition codes/memory read/write sets, then moves independent prior instructions into branch delay slots, load-use delay slots, or floating compare delay slots.

Key functions:
- `sched()` performs the reordering and inserts nops with `addnop()` where no safe candidate exists.
- `regsused()` computes dependency masks from opcode and operand classes, including integer registers, floating registers, ICC/FCC, and coarse memory regions for generic, SB-relative, and SP-relative memory.
- `depend()` and `conflict()` decide whether instructions can be interchanged or whether a load result is immediately consumed.
- `offoverlap()` refines SB/SP memory dependency checks by byte range.
- `compound()` treats multiword encodings and writes to `REGSB` as unschedulable compounds.
- `dumpbits()` is debug output for dependency masks.

This file depends on `oplook()`, `aclass()`, `regoff()`, opcode marks such as `LOAD`, `BRANCH`, `FCMP`, and global `autosize`/`curtext`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/sched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/span.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kl/span.c

This file assigns final text addresses and implements operand classification/instruction table lookup.

Key functions:
- `span()` walks the final program list from `INITTEXT`, assigns `pc`, uses `oplook()` sizes, updates text symbol values, rounds text size, and computes `INITDAT`.
- `xdefine()` conditionally defines linker symbols.
- `regoff()` and `aclass()` classify `Adr` operands into instruction classes while computing `instoffset`, resolving extern/static/auto/param addressing and constant forms.
- `oplook()` finds the matching `Optab` row for an instruction and caches it in `p->optab`.
- `cmp()` defines class subsumption rules used for operand-class matching.
- `ocmp()` and `buildop()` sort `optab`, build per-opcode ranges, and alias many SPARC opcodes to shared table ranges.

This is the bridge between symbolic linker IR and machine encoding. It depends on accurate symbol types/values from `dodata()` and text patching from `pass.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kl/span.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kprof.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/kprof.c

`kprof` reads a kernel text image and a binary profiling data file, attributes tick counts to text symbols, sorts by time, and prints milliseconds/percentage/function.

It uses `<mach.h>` to parse the executable header, initialize symbols, and iterate text symbols. The data file is interpreted as big-endian `ulong` counters: total ticks, outside-kernel ticks, then address-indexed samples relative to kernel text base. It warns if `mach->kbase` differs from the first text symbol page.

The implementation is intentionally simple and assumes profiling data shape matches the kernel’s expected layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/kprof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ktrace.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ktrace.c

`ktrace` reconstructs and prints kernel stack traces from a kernel image plus `pc`, `sp`, and optional link register. It can run interactively or consume address=value stack words from stdin.

Key behavior:
- Detects executable architecture with `<mach.h>` and selects `i386trace`, `amd64trace`, generic CISC `ctrace`, or generic RISC `rtrace`.
- Uses symbol table lookups, `.frame` local symbols, `pc2sp()`, and architecture address size to step stack frames.
- Handles special interrupt-return frames for `forkret` on i386 and `noteret` on amd64.
- `printaddr()` emits output as `src(address)` commands with comments suitable for Plan 9 debugging workflows.
- `readstack()` builds a fixed table of up to 1024 address/value pairs; `getval()` looks them up or prompts interactively.

The code is diagnostic tooling and caps traces at about 40 frames to avoid runaway walks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ktrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ktrans/hash.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ktrans/hash.c

This is a small string-keyed hash map used by `ktrans`. It stores fixed-size values inline after a private `Hnode` header in a growable contiguous allocation.

Key functions:
- `shash()` hashes C strings with a simple multiplicative hash.
- `hmapalloc()` allocates bucket storage and initializes map metadata.
- `hmaprepl()` inserts or replaces entries, optionally freeing previous keys, grows capacity by `realloc`, and links overflow nodes by index.
- `hmapupd()` updates using an existing key pointer when present.
- `_hmapget()`, `hmapget()`, `hmapkey()`, and `hmapdel()` implement lookup and deletion.
- `hmaprehash()` rebuilds with a new bucket count.
- `hmapreset()` marks filled entries empty and optionally frees keys.

The map is tailored to startup-loaded transliteration/dictionary data. Deletion/reset/rehash behavior is not robust enough for arbitrary long-lived mutation because empty nodes and overflow links are only partially normalized.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ktrans/hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ktrans/hash.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ktrans/hash.h

This header declares the `Hmap` structure and hash-map API used by `ktrans`. `Hmap` records bucket count, node size, logical length, capacity, and a byte pointer to node storage.

It also defines `Hkey`, a small union for pointer/int key-like values, though the implementation uses string keys. The public API covers allocation, get, replace, update, delete, key retrieval, and reset.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ktrans/hash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ktrans/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ktrans/main.c

`ktrans` is a threaded keyboard input method/transliterator for English, Japanese hiragana/katakana, Korean Hangul, Chinese Wubi/Pinyin-style dictionary lookup, and Vietnamese Telex.

Major pieces:
- UTF helpers `pushutf()`, `peekstr()`, and `Str` operations manage bounded UTF-8 edit buffers.
- `openmap()` loads romanization maps into `Hmap`, including partial prefixes marked `leadstomore`.
- `opendict()` loads dictionaries mapping readings to candidate lists.
- Language switching uses control characters and `langtab`/`langcodetab`.
- `displaythread()` optionally opens a Draw window showing conversion candidates, selection highlight, scrollbar, and exit area.
- `dictthread()` tracks Japanese/Chinese candidate conversion state, okuri/joshi handling, selection cycling, and candidate replacement via emitted backspaces/output.
- `telexlkup()`, `dubeollkup()`, and `dubeolbksp()` implement Vietnamese and Korean composition behavior.
- `keythread()` is the main transliteration state machine: language switching, literal mode, dictionary forwarding, map lookup, backspace handling, and output replacement.
- `kbdtap()` reads keyboard messages, `kbdsink()` writes output messages, and `plumbproc()` receives language changes from plumbing.
- `threadmain()` parses `-l` and `-G`, opens keyboard or stdin/stdout, starts channels/threads, loads `/lib/ktrans` maps and dictionaries plus optional user dictionary overlays.

The program is Plan 9 UI/input infrastructure code built around libthread channels, `/dev/kbdtap`-style messages, Draw, mouse/keyboard controls, and plumbing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ktrans/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ktrans/test.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ktrans/test.c

This is a black-box regression test for the `ktrans` binary. It forks `ktrans -l jp -G`, feeds keyboard messages through pipes, collects output messages, applies emitted backspaces to a Rune stack, and compares final text against expected Rune strings.

The test set covers Japanese kana/kanji conversion, Chinese conversion, Vietnamese Telex accents, and Korean Hangul composition. It also sets `zidian` to `/lib/ktrans/pinyin.dict` for the child process.

The harness validates observable input-method behavior rather than internal functions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ktrans/test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lens.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/lens.c

`lens` is an interactive screen magnifier. It opens `/dev/screen`, reads the screen image format and geometry, samples pixels around the current pointer-selected point, magnifies them into its own Draw window, and optionally overlays a grid.

Controls include keyboard zoom/unzoom, numeric magnification, grid toggle, redraw, quit, left mouse to recenter, and right-button menu actions. It supports screen depths of at least 8 bits and uses raw screen buffer reads plus `loadimage()` to render magnified scanlines.

The code is tightly coupled to Plan 9 draw/event APIs and `/dev/screen` layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lens.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lex/header.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/lex/header.c

This file emits the generated C scanner prologue, scanner switch wrapper, tail, and generation statistics for Plan 9 `lex`.

Key functions:
- `phead1()` writes typedefs, includes, lexer macros, global declarations, scanner structs, and either Plan 9 `read`/`write`-based `input`/`output` or stdio macros.
- `phead2()` writes the `yylook()` loop and action switch header.
- `ptail()` emits switch defaults and closes `yylex`.
- `statistics()` reports parse-tree, position, state, transition, packed-class, packed-transition, and output-slot usage.

It is output-generation support for `lmain.c`/`parser.y` and depends on many global counters from `ldefs.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lex/header.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lex/ldefs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/lex/ldefs.h

`ldefs.h` is the central definition header for the Plan 9 `lex` implementation. It defines scanner constants, array sizing defaults, regex parse-tree node codes, section markers, debug switches, and external declarations for all global compiler state.

It also declares the major functions spanning parsing, action copying, parse-tree construction, follow-position computation, DFA generation, transition packing, output layout, diagnostics, and generated header emission.

The codebase relies heavily on shared globals rather than encapsulated structs; this header is the integration contract across `lmain.c`, `parser.y`, `sub1.c`, `sub2.c`, and `header.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lex/ldefs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lex/lmain.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/lex/lmain.c

This is the main driver for Plan 9 `lex`. It parses options, opens input/output, initializes global storage, runs the yacc parser, generates follow sets and DFA transitions, lays out output tables, appends the lex runtime driver template, and prints optional statistics.

Key phases:
- Options include output to stdout (`-t`/`-T`), reporting (`-v`/`-n`), and Plan 9 output mode (`-9`).
- `get1core()`, `get2core()`, and `get3core()` allocate successive work arrays for definitions, parse trees, DFA construction, and final table packing.
- `free1core()`, `free2core()`, and debug-only `free3core()` release phase-specific storage.
- Main flow: read first char, initialize `INITIAL`, `yyparse()`, emit scanner tail, `mkmatch()`, `cfoll()`, `cgoto()`, `layout()`, append `/sys/lib/lex/ncform`.

The implementation is classic batch compiler structure with explicit memory phase management.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lex/lmain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lex/parser.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/lex/parser.y

This yacc grammar parses lex input and builds the regular-expression parse tree used to generate the scanner.

Grammar coverage:
- Definitions section: macro definitions, `%` directives, `%{...%}` copied code, `%s` start conditions, and size overrides (`%p`, `%n`, `%e`, `%o`, `%a`, `%k`).
- Rules section: regex/action pairs, blank-leading action continuations, `|` action reuse, included code, and section delimiter.
- Regex operators: literals, strings, `.`, character classes, negated classes, `*`, `+`, `?`, alternation, concatenation, trailing context `/`, end anchor `$`, start anchor `^`, start conditions, null strings, and bounded repetitions `{n}`, `{n,m}`, `{n,}`.

The embedded `yylex()` is a hand-coded scanner for lex source syntax. It expands definitions, parses character classes/ranges, handles escapes, copies user action code with `cpyact()`, and emits generated scanner action cases.

This file ties syntax recognition directly to parse-tree constructors (`mn0`, `mn1`, `mn2`, `mnp`, `dupl`) and code emission (`phead2`, `ptail`).
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lex/parser.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lex/sub1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/lex/sub1.c

`sub1.c` provides lex front-end utilities, diagnostics, action copying, input buffering, parse-tree node construction, definition pushback, and debug dumps.

Key functions:
- `getl()` reads logical input lines via `gch()`.
- `error()`/`warning()` print file/line diagnostics; fatal errors may also print statistics.
- `lgate()` lazily opens `lex.yy.c` and emits the generated prologue.
- `cclinter()` computes/intersects packed character-class partitions.
- `usescape()` decodes common and octal escapes.
- `lookup()` finds definitions/start-condition names.
- `cpyact()` copies C action code while respecting braces, comments, strings, chars, semicolon termination, and `|` action reuse.
- `gch()`, `munputc()`, and `munputs()` implement source input and macro-expansion pushback across multiple files.
- `mn0()`, `mn1()`, `mn2()`, `mnp()`, and `dupl()` create/clone parse-tree nodes and nullability metadata.
- Debug-only routines print characters, strings, definitions, start conditions, and parse trees.

The file is essential glue between parser tokens, copied user code, and regex tree construction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lex/sub1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lex/sub2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/lex/sub2.c

`sub2.c` implements follow-position computation, DFA construction, transition packing, action table construction, character-class matching, and final scanner table layout.

Key functions:
- `cfoll()`, `follow()`, `first()`, `add()`, and `padd()` compute and pack position/follow sets from the regex parse tree.
- `cgoto()` creates initial states for start conditions, enumerates transitions for each DFA state, discovers new states with `notin()`, and emits `yyvstop`.
- `nextstate()` computes the target position set for a state/character pair.
- `packtrans()` compresses transitions using character-class representative matching and fallback states.
- `member()` tests packed character-class membership.
- `acompute()` builds per-state action lists including trailing-context fallback actions.
- `mkmatch()` builds `yymatch` representative-character mapping.
- `layout()` packs transition tables into `yycrank`, emits `yysvec`, `yymatch`, and `yyextra`.

This is the automata/code-generation core of Plan 9 `lex`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lex/sub2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lnfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/lnfs.c

`lnfs` is a user-level 9P filesystem that mounts over a directory and translates long or space-containing names into short filesystem-safe names recorded in `./.longnames`.

Key behavior:
- Runs a 9P server over a pipe and mounts it with `MREPL|MCREATE`; optional `-s` posts the service in `/srv`; `-r` makes it read-only; `-d` logs fcalls.
- Tracks active fids with path strings, open fds, qids, directory-read state, attach ownership, and user.
- Implements 9P `version`, `auth`, `attach`, `walk`, `open`, `create`, `read`, `write`, `clunk`, `remove`, `stat`, and `wstat`.
- Directory reads and stat replies map short underlying names back to long names.
- Creates short names as the first `NAMELEN-1` bytes of base32-encoded MD5 of the long name and appends long names to `.longnames`.
- `readnames()` incrementally reloads `.longnames` based on qid/path and length changes.

Security/authentication is minimal: `rauth()` says auth is not required, and operations generally rely on underlying filesystem permissions plus optional read-only mode.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lnfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lock.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/lock.c

`lock` opens a Plan 9 exclusive-use lock file and keeps the lock alive while running a command, defaulting to `rc`.

It ensures the file has `DMEXCL` set, reopens it so exclusive locking takes effect, forks a keeper process that periodically writes to the lock fd, then runs the command in a separate process group/environment. When the command exits, it kills the keeper and exits with the command’s wait status.

Options:
- `-w` waits/retries opening the lock.
- `-d` sets a debug flag, though the flag is not materially used.

It is Plan 9 lock-file orchestration around exclusive files and process notes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/look.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/look.c

`look` searches a sorted text file, defaulting to `/lib/words`, for entries matching a key or keys from stdin. It supports dictionary-style canonicalization, case folding, exact matching, alternate tab field delimiter, and numeric comparison.

Key behavior:
- Converts UTF-8 arguments/input to Rune arrays.
- `rcanon()` canonicalizes by stopping at a tab, optional directory mode, optional case fold, and Latin-1 accent folding to ASCII approximations.
- `locate()` binary-searches the file to the first possible match, then scans forward.
- `acomp()` performs prefix-aware lexicographic comparison.
- `ncomp()` performs numeric comparison with sign, integer, and fractional handling under configurable base.
- `getword()` reads Rune lines through Bio.

The implementation assumes sorted input according to the selected comparison/canonicalization mode.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/look.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lp/LOCK.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/lp/LOCK.c

This helper creates an exclusive lock file for the printer subsystem, writes `hostname ppid`, forks, and lets the parent exit while the child keeps the lock alive.

The child periodically stats and zero-byte writes the file until the file disappears, becomes zero-length, or write/stat fails. It then closes the fd and sends `kill` to the supplied parent process group.

It is a specialized Plan 9 printer lock keeper using `DMEXCL` files and notes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lp/LOCK.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lp/ipcopen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/lp/ipcopen.c

`ipcopen` connects stdin/stdout to a dialed network service. It builds a Plan 9 net address from destination, network, and service, dials it, opens the connection’s `data` file for read and write, then forks bidirectional copy loops.

The child copies remote data to stdout, while the parent copies stdin to remote. Each side calls `hangup()` and closes fds when done. A single leading NUL byte from remote is treated as an immediate termination condition in `pass()`.

This is simple datakit/network plumbing for older lp workflows.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lp/ipcopen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lp/lpdaemon.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/lp/lpdaemon.c

`lpdaemon` is a portable C inbound print daemon that accepts remote print protocol requests, stores received control/data files in temporary files, derives job metadata, and invokes local `lp`.

Supported flows:
- BSD/lpr-style control bytes for queue/status/kill/send operations.
- Control file records provide host (`H`) and user (`P`) metadata.
- Data files are acknowledged with NUL ACK bytes and read to temp files under platform-specific temp directories.
- `forklp()` builds and logs an `lp` command line, redirects input from a temp data file, and waits for the child.
- Alarms guard protocol stalls and log debug state.

It contains compatibility sections for Plan 9, V10, SYSV, and BSD. Notable fragility includes fixed argument/data arrays, temp-file naming by pid/index, limited varargs logging style, and no explicit bound check on the `datafd[400]` job count.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lp/lpdaemon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lp/lpdsend.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/lp/lpdsend.c

`lpdsend` sends jobs to an LPD-style printer service. It supports sending a print job, checking queue status, and killing a job.

Key behavior:
- Options include printer name, user, host, sequence number, file type, debug, queue status, and kill target.
- For stdin jobs, it copies input to a temporary local file before opening the network connection.
- Dials `tcp!host!printer` using privileged-style source ports 721-731.
- Sends RFC1179-like receive-job, data-file, and control-file records, waiting for NUL ACKs after each stage.
- Status and kill paths send the corresponding control request and copy the response to stderr.
- `copyfile()` reports progress every 5 percent when total size is known and is guarded by a long alarm timeout.

This is portable C with Plan 9 networking compatibility. It assumes cooperative printer protocol behavior and uses `tmpnam()` for stdin staging.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lp/lpdsend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lp/lpsend.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/lp/lpsend.c

`lpsend` is a simpler print relay sender. It reads one options line from stdin, spools the rest of stdin to a temp file to know its size, dials a supplied network address, sends the options line, sends the byte count, waits for ACK, sends data, ACKs completion, waits for final ACK, then copies any response to stdout.

It has Plan 9 and non-Plan 9 compatibility sections, uses alarm timeouts for network reads/writes, and temp files under `/tmp`. The protocol is paired with `lpdaemon`’s non-BSD path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/lp/lpsend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ls.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ls.c

This is Plan 9 `ls`. It stats files or reads directories, accumulates `Dir` entries, sorts them unless `-n`, computes column widths, and formats output.

Supported flags include long format, directory-as-file, muid, no sort, full path prefixing, qid/version/type, reverse, block size, time sort, temporary flag display, access-time selection, executable/directory suffixes, and unquoted output.

Important functions:
- `ls()` handles stat/open/dirreadall and prefix cleanup.
- `output()` sorts and flushes pending entries.
- `dowidths()` computes field widths for aligned output.
- `format()` prints one entry with selected metadata.
- `compar()` sorts by name/prefix or time, with reverse support.
- `asciitime()` chooses time/year display based on age.
- `xcleanname()` collapses duplicate and trailing slashes.

It is a direct Plan 9 filesystem metadata formatter using `Dir` and qid fields.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/index.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/index.c

This file registers map projections by name. It defines small adapter functions that normalize constructor signatures to `proj (*)(double,double)`, then fills `struct index index[]`.

Each entry names the projection, constructor, number of parameters, cut function, default flags/parameters, spheroid flag, and optional limb callback. Registered projections include Aitoff, Albers, azimuthal variants, conic/cylindrical variants, Guyou, hex, homing/mecca, Mercator, orthographic/perspective, polyconic, tetra, trapezoidal, Vander Grinten, and others.

This is the projection dispatch table used by the map command/library front end.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/index.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/iplot.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/iplot.h

`iplot.h` is an alternate plotting macro header for V8/V9-style systems. It maps plot operations to textual commands printed with `print()`: open/close, erase, point, range, text, vector, move, pen style, and color.

It also defines color abbreviations and a `colorcode()` helper. There is no state or function implementation beyond macros.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/iplot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/aitoff.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/aitoff.c

Implements the Aitoff projection. `Xaitoff()` halves longitude, recomputes sine/cosine, normalizes around an equatorial pole, applies azimuthal equal-area projection, then doubles x. `aitoff()` initializes the pole at `(0,0)` and returns the projection function.

It depends on `copyplace()`, `sincos()`, `norm()`, `Xazequalarea()`, and `latlon()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/aitoff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/albers.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/albers.c

Implements spherical and spheroidal Albers equal-area conic projection plus inverse/scaling helpers.

Key pieces:
- `albinit()` normalizes standard parallels, handles degenerate cases by falling back to azimuthal equal-area or cylindrical equal-area, computes constants, and returns `Xspalbers`.
- `albers()` calls `albinit()` with eccentricity zero.
- `sp_albers()` calls it with spheroid eccentricity `EC2`.
- `Xspalbers()` projects using precomputed constants and south-pole orientation.
- `albscale()` and `invalb()` support inverse Albers coordinate scaling and latitude/longitude recovery.

The implementation follows Deetz and Adams formulas and shares static state across the active projection.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/albers.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/azequalarea.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/azequalarea.c

Implements azimuthal equal-area projection centered on the north pole. `Xazequalarea()` computes radius `sqrt(1 - sin(lat))` and maps by negative longitude sine/cosine. `azequalarea()` returns that function.

This projection is also reused by Aitoff and Albers fallback paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/azequalarea.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/azequidist.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/azequidist.c

Implements azimuthal equidistant projection. `Xazequidistant()` uses colatitude `PI/2 - lat` as radius and maps by negative longitude sine/cosine. `azequidistant()` returns the projection function.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/azequidist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/bicentric.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/bicentric.c

Implements a bicentric projection parameterized by a center latitude. It rejects latitudes/longitudes near singularities, computes x from longitude tangent scaled by center cosine, y from latitude over `cos(lat)*cos(lon)`, and returns visible status based on radius squared <= 9.

`bicentric()` rejects parameters above 89 degrees, stores the absolute center latitude, and returns `Xbicentric`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/bicentric.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/bonne.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/bonne.c

Implements Bonne projection. `bonne()` falls back to sinusoidal projection for near-equatorial standard parallels, otherwise stores the standard parallel and `r0`. `Xbonne()` computes radial distance from the standard parallel and angular displacement, with special handling near the pole/zero-radius case.

It returns the shared `Xsinusoidal` function for the degenerate case.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/bonne.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/ccubrt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/ccubrt.c

Provides `ccubrt()`, a complex cube-root helper. It converts the complex input to polar form, cube-roots the radius with `cubrt()`, divides the angle by three, and returns rectangular coordinates.

Used by conformal map projections such as hex.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/ccubrt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/complex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/complex.c

This file provides complex arithmetic helpers for projection formulas:
- `cdiv()` defensive complex division.
- `cmul()` multiplication.
- `csq()` square.
- `csqrt()` square root.
- `cpow()` polar-form complex power.

These are used by conformal projections such as Guyou, Lagrange, lune, hex, and tetra.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/complex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/conic.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/conic.c

Implements a simple conic projection with one standard parallel. For near-zero parallels it falls back to cylindrical projection. `Xconic()` rejects points too far from the standard parallel, computes a radial term, maps longitude scaled by `sin(stdpar)`, and returns hidden/visible status based on radius.

Static state stores the standard parallel.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/conic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/cubrt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/cubrt.c

Provides `cubrt()`, a real cube-root routine. It handles sign, scales the argument into a near-one range by powers of eight, then uses Newton iteration until convergence.

Used by `ccubrt()` and projection formulas needing cube roots.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/cubrt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/cuts.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/cuts.c

This file supplies aborting placeholder definitions for `picut()`, `ckcut()`, and `reduce()` so the library can be self-standing when unusual projection modules reference cut helpers normally provided by `map.c`.

The comments explain that `hex.c`, `guyou.c`, and `tetra.c` need internal cut knowledge, but these duplicate symbols should not normally be loaded in the full map program.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/cuts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/cylequalarea.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/cylequalarea.c

Implements cylindrical equal-area projection. `cylequalarea()` rejects standard parallels above 89 degrees, stores `cos(par)^2` as x scale, and returns `Xcylequalarea()`, which maps longitude linearly and y to `sin(lat)`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/cylequalarea.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/cylindrical.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/cylindrical.c

Implements a cylindrical projection with x as negative longitude and y as tangent latitude (`sin/cos`). It rejects latitudes beyond about 80 degrees. `cylindrical()` returns `Xcylindrical()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/cylindrical.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/elco2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/elco2.c

Implements Bulirsch-style complex elliptic integral routine `elco2()`, used by several conformal polyhedral/square projections. It computes an integral from `0` to `x+iy` with parameters `kc`, `a`, and `b`, returning success/failure and output real/imaginary parts.

Supporting helpers:
- `cdiv2()` computes a stable partial complex division component.
- `csqr()` computes the complex square root of `|x| + iy`.

The routine is numerically specialized and rejects `kc == 0` or negative x.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/elco2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/elliptic.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/elliptic.c

Implements an elliptic projection based on distances to two foci separated by a center longitude/latitude parameter. It falls back to azimuthal equidistant for very small parameter values and rejects parameters over 89 degrees.

`Xelliptic()` computes two angular distances, derives x from squared-distance difference, and derives signed y from the remaining ellipse equation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/elliptic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/fisheye.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/fisheye.c

Implements a refractive fisheye projection parameterized by refractive index `n`. It computes a transformed radial value from latitude, rejects values near the asin limit, and maps by longitude sine/cosine.

`fisheye()` rejects parameters below 0.1.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/fisheye.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/gall.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/gall.c

Implements Gall projection. `gall()` rejects standard parallels over 80 degrees, computes a longitude scale from the parameter, and returns `Xgall()`. The projection maps x linearly and y as `tan(lat/2)`, with an alternate formula for numerical stability away from the equator.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/gall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/gilbert.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/gilbert.c

Implements Gilbert projection. It maps the sphere onto a hemisphere using `tan(lat/2)` and half longitude, then presents the hemisphere orthographically.

The file includes a derivation comment: stereographic projection to plane, square root to half-plane, then inverse stereographic projection.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/gilbert.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/guyou.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/guyou.c

Implements Guyou projection and a related square projection. Both use stereographic projection, complex transforms, and `elco2()` to map hemispheres/spherical regions to square-like domains.

Key functions:
- `guyou()` initializes elliptic constants, side length, west/east hemisphere centers, and returns `Xguyou()`.
- `Xguyou()` chooses hemisphere, normalizes coordinates, stereographically projects, maps through `dosquare()`, and offsets one hemisphere.
- `guycut()` customizes longitude cuts for Guyou.
- `square()` initializes Guyou constants and returns `Xsquare()`.
- `Xsquare()` maps north/south halves with a fourth-root-like transform and square mapping.

This file depends on complex helpers, `elco2()`, `norm()`, `Xstereographic()`, and cut helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/guyou.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/harrison.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/harrison.c

Implements Harrison perspective-like projection with radius `r` and angle `alpha`. Initialization computes view/unit constants and rejects invalid geometry. `Xharrison()` projects 3D sphere coordinates onto a plane using those constants, rejecting points behind/too near the view plane or outside radius bounds.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/harrison.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/hex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/hex.c

Implements a conformal hexagonal world projection. It uses stereographic projection, complex division/square/cube-root/square-root, and elliptic integrals to map hemispheres into a hexagonal layout with reflection for southern regions.

Key functions:
- `hex()` initializes cut longitudes, constants, centers, reflection vectors, and returns `Xhex()`.
- `Xhex()` handles near-cut/equator edge cases, normalizes to a hemisphere, applies complex transforms, calls `elco2()`, and reflects southern sections.
- `hexcut()` supplies custom cut handling along three cut longitudes.

This is one of the more numerically intricate projection files and depends on `reduce()`, `ckcut()`, `norm()`, `Xstereographic()`, and complex helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/hex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/homing.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/homing.c

Implements homing and Mecca projections based on azimuth/distance to a chosen standard latitude point.

Key functions:
- `azimuth()` computes bearing (`az`) and angular distance (`rad`) from an input place to `p0`, including pole handling and trigonometric clamping.
- `mecca()`/`Xmecca()` map longitude and bearing-derived y with clipping/visibility rules.
- `homing()`/`Xhoming()` map angular distance along the bearing vector.
- `hlimb()` and `mlimb()` generate limb outlines for homing/Mecca projections.

Static state stores the standard parallel and first-call state for limb generation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/homing.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/lagrange.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/lagrange.c

Implements Lagrange projection. It mirrors southern latitudes to the north, applies stereographic projection, complex square root and division transforms, then restores y sign for southern latitudes.

`lagrange()` returns `Xlagrange()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/lagrange.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/lambert.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/lambert.c

Implements Lambert conformal conic projection with two standard parallels. It normalizes parameter order, falls back to Mercator for opposing parallels and perspective/stereographic-like behavior for equal parallels, rejects near-pole parameters, computes cone constant `k`, and maps latitude/longitude in `Xlambert()`.

The projection rejects far-southern points and has a special case for near north pole radius zero.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/lambert.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/laue.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/laue.c

Implements Laue projection. It only accepts points above roughly 45 degrees latitude, computes radius as `tan(PI - 2*lat)`, rejects large radii, and maps by longitude sine/cosine.

`laue()` returns `Xlaue()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/laue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/lune.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/lune.c

Implements a conformal lune projection using the transform `((1+z)^A - (1-z)^A)/((1+z)^A + (1-z)^A)` after stereographic projection.

`lune(lat, theta)` initializes east/west pole reference points, validates expected stereographic symmetry, computes scale and power, then returns `Xlune()`. `Xlune()` rejects points outside the cap, applies stereographic projection, scales, computes complex powers, divides numerator by denominator, and outputs x/y.

It depends on `Xstereographic()`, `cpow()`, and `cdiv()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/lune.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/mercator.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/mercator.c

Implements spherical and spheroidal Mercator projections. `Xmercator()` maps x to negative longitude and y to the standard logarithmic Mercator formula, rejecting latitudes beyond about 80 degrees. `Xspmercator()` applies an eccentricity correction using `ECC`.

Constructors are `mercator()` and `sp_mercator()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/mercator.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/mollweide.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/mollweide.c

Implements Mollweide projection. `Xmollweide()` solves `2z + sin(2z) = PI*sin(lat)` by Newton iteration, then maps y to `sin(z)` and x to scaled longitude times `cos(z)`. It skips iteration near the poles.

`mollweide()` returns `Xmollweide()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/mollweide.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/newyorker.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/newyorker.c

Implements a “newyorker” radial projection parameterized by angular cutoff `a0`. It computes colatitude `r`, maps the center specially, rejects points inside the cutoff, then uses `log(r/a)` as radial distance.

`newyorker()` stores `a0` in radians and returns `Xnewyorker()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/newyorker.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/orthographic.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/orthographic.c

Implements orthographic projection and its limb generator. `Xorthographic()` maps visible hemisphere coordinates to x/y and returns hidden status for southern/back-side latitudes. `orthographic()` returns it.

`olimb()` iterates the equatorial limb from longitude -180 to 180 using a static first-call flag.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/orthographic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/perspective.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/perspective.c

Implements perspective, stereographic, and gnomonic projections through shared `viewpt` state.

Key behavior:
- `perspective(radius)` returns orthographic for very large radius, rejects radius near 1, otherwise uses `Xperspective()`.
- `Xperspective()` computes radial scale from viewpoint and latitude, rejects singular/too-large points, and returns hidden/visible status.
- `Xstereographic()` temporarily sets `viewpt = -1` for use by other conformal projections.
- `stereographic()` and `gnomonic()` set `viewpt` to -1 and 0 respectively.
- `plimb()` generates the visible limb, delegating to `olimb()` for orthographic-like cases.

This shared static `viewpt` means only one such projection can be active safely at a time.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/perspective.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/polyconic.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/polyconic.c

Implements polyconic projection. For non-equatorial latitudes it uses cotangent latitude and longitude scaled by sine latitude. Near the equator it uses series approximations to avoid division by near-zero sine.

`polyconic()` returns `Xpolyconic()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/polyconic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/rectangular.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/rectangular.c

Implements rectangular/equirectangular projection with a standard parallel scale. `rectangular(par)` stores `cos(par)` as longitude scale and rejects near-polar scales below 0.1. `Xrectangular()` maps x to scaled negative longitude and y to latitude.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/rectangular.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/simpleconic.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/simpleconic.c

Implements a simple conic projection with two standard parallels. It falls back to rectangular when parallels sum to near zero, computes constants differently for equal versus distinct parallels, and maps by radius `r0 - lat` and longitude scale `a`.

`simpleconic()` returns `Xsimpleconic()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/simpleconic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/sinusoidal.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/sinusoidal.c

Implements sinusoidal projection. `Xsinusoidal()` maps x to negative longitude times `cos(lat)` and y to latitude. `sinusoidal()` returns it.

This projection is also used as a Bonne fallback.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/sinusoidal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/tetra.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/tetra.c

Implements a conformal map of the Earth onto a tetrahedron. The file documents a multi-stage mapping: stereographic projection of tetrahedral faces, rational complex transform, and elliptic-integral mapping of sectors.

Key functions:
- `tetra()` initializes tetrahedral poles, face transformations, elliptic constants, complete integrals, translations, and rotations.
- `twhichp()` chooses the nearest and next-nearest tetrahedron face poles for an input place.
- `Xtetra()` normalizes to the selected face, stereographically projects, applies complex transforms and `elco2()`, rotates/translates into final tetrahedral layout.
- `tetracut()` supplies custom cut behavior for face boundaries and southern cuts.

This is one of the most complex map projection implementations and depends heavily on complex arithmetic, stereographic projection, normalization, and cut helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/tetra.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/trapezoidal.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/trapezoidal.c

Implements trapezoidal projection with two standard parallels. It falls back to rectangular when absolute parallels are nearly equal, computes slope `k` and equator offset `yeq`, then maps y linearly by latitude and x as `y*k*longitude`.

`trapezoidal()` returns `Xtrapezoidal()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/trapezoidal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/twocirc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/twocirc.c

Provides common two-circle geometry for projections whose meridians and parallels are circular arcs.

Key pieces:
- `quadratic()` solves a quadratic branch used by circle intersection.
- `twocircles()` computes intersection of a meridian circle and parallel circle, handling symmetry and near-axis cases.
- `globular()`/`Xglobular()` implement globular projection using normalized longitude/latitude and circle intersections.
- `vandergrinten()`/`Xvandergrinten()` implement Van der Grinten projection with transformed latitude parameter and the same circle-intersection helper.

This file supplies two registered projections from one shared geometric primitive.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/twocirc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/zcoord.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/zcoord.c

This file provides coordinate normalization/orientation helpers for the map library.

Key functions:
- `orient()` sets global map pole, twist, and inverse transform from latitude/longitude/theta.
- `latlon()` normalizes degrees and fills a `place`.
- `deg2rad()` normalizes degrees, fills radians/sine/cosine, and handles exact +/-90 degree cases.
- `sincos()` computes sine/cosine for a `coord`.
- `normalize()` and `invert()` apply global forward/inverse orientation with `norm()`.
- `norm()` rotates a place so a selected pole/twist becomes the map coordinate frame, wrapping longitude to +/-PI.
- `copyplace()` copies a `place`.
- `printp()` debug-prints coordinate internals with stdio.

Most projection files depend on these helpers for pole orientation and safe trigonometric coordinate state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/libmap/zcoord.c -->