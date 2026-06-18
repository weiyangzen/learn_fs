# Group Research: group_186_9front_sources_os_plan9_9front_sys_src_cmd_tl_span_c_sources_os_plan_82039648c76e

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/span.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tl/span.c

Read completely: 1262 lines, 21791 bytes.

This is the ARM/Thumb linker span and operand-classification pass for the Plan 9 `tl` linker. It assigns program counters, sizes instructions through `oplook`, resolves branch sizing, handles Thumb padding/alignment, emits literal pools, defines `etext`/`textsize`, and builds ARM optab ranges.

Key behavior:
- `span` walks `firstp`, calls `setarch`, sizes each `Prog`, updates text symbol values, flushes literal pools, and reruns passes when large branches or Thumb branch alignment change instruction sizes.
- `checkpool`, `flushpool`, and `addpool` manage PC-relative literal pools and insert branch-around-pool instructions.
- `aclass` classifies ARM operands, computes `instoffset`, resolves external/static/auto/param addressing, and diagnoses undefined externals.
- `oplook`, `cmp`, `ocmp`, and `buildop` build and search instruction encoding tables.
- `dynreloc` and `asmdyn` collect sorted dynamic relocation records and write import/relocation metadata.

Dependencies:
- Includes `l.h` and relies on linker globals such as `firstp`, `thumb`, `blitrl`, `elitrl`, `curtext`, `autosize`, symbol tables, `optab`, `oprange`, `thumboptab`, and output helpers.

Reliability notes:
- This file is central to link correctness: branch range, literal pool distance, and Thumb/ARM interworking calculations are stateful and order-sensitive.
- Several paths diagnose then continue by assigning default symbol types, which is normal for old Plan 9 toolchains but fragile for malformed inputs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/span.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/thumb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tl/thumb.c

Read completely: 1636 lines, 39963 bytes.

This implements Thumb instruction support for the `tl` linker. It classifies Thumb operands, defines the Thumb optab, builds optab ranges, emits 16-bit Thumb instruction sequences, handles long branches and literal-pool expansions, counts emitted opcode sizes, and includes a debug Thumb disassembler.

Key behavior:
- `thumbaclass` maps Plan 9 addressing modes into Thumb classes, computes branch displacement classes, sets alignment needs for long branches, and handles function pointer interworking/T-bit adjustments.
- `thumboptab` lists accepted instruction forms, emitted sizes, emitter cases, and literal-pool flags.
- `thumbasmout` emits cases for arithmetic, moves, loads/stores, branch/call expansions, large constants, stack-relative forms, `AWORD`, and `ADWORD`.
- Helper functions validate low/high register use, alignment multiples, immediate ranges, and Thumb opcode bit encodings.
- `dis` decodes emitted 16-bit instructions for debug output.

Dependencies:
- Includes `l.h`, shares `ocmp`, `isbranch`, `fninc`, `fnpinc`, literal-pool state, `instoffset`, output buffer pointers, and architecture constants with the linker backend.

Reliability notes:
- The code contains deliberate diagnostics for unsupported ARM-only operand classes in Thumb mode.
- Some large-immediate construction uses `rand()` to choose a decomposition, which can make emitted instruction sequences non-obvious though still intended to be equivalent.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/thumb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tlsclient.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tlsclient.c

Read completely: 174 lines, 3108 bytes.

Standalone TLS client wrapper. It opens a dial string or existing file, optionally performs Plan 9 auth, starts a TLS client session, verifies a server certificate against thumbprints, optionally dumps the server certificate, then either execs a command over the TLS fd or shuttles stdin/stdout.

Key behavior:
- Flags cover debug trace, auth key spec, thumbprint allow/exclude files, client certificate, server-name/SNI, certificate dump path, and `-o` for opening a file instead of dialing.
- Uses `tlsClient`, `initThumbprints`, `okCertificate`, `readcert`, and `auth_proxy`.
- For no command, forks one transfer direction and copies the other in the parent.

Security/reliability notes:
- Without `-t`, certificate thumbprint verification is not performed here.
- Auth mode uses `p9secret` PSK material from `auth_proxy`.
- The child shutdown note string is fixed and non-semantic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tlsclient.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tlssrv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tlssrv.c

Read completely: 147 lines, 2413 bytes.

Standalone TLS server wrapper. It accepts an already-open fd 0 connection, optionally authenticates the peer through Plan 9 auth, loads a certificate chain, starts `tlsServer`, then execs a command with stdin/stdout attached to the TLS connection.

Key behavior:
- Flags cover debug tracing, auth with or without `auth_chuid`, key spec, timeout, certificate file, syslog file, and remote system label.
- Requires either certificate material or PSK secret material.
- When full auth is selected, it changes user and attempts to chown the network connection to the authenticated user.

Dependencies:
- Uses `libsec`, `auth`, `readcertchain`, `tlsServer`, `auth_proxy`, `auth_chuid`, `syslog`, and Plan 9 fd operations.

Reliability notes:
- TLS failure exits success unless debug logs the failure, matching service-wrapper behavior but potentially hiding failed handshakes from callers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tlssrv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/touch.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/touch.c

Read completely: 65 lines, 960 bytes.

Plan 9 `touch` implementation. It updates file modification time through `dirwstat`; if that fails and `-c` is not set, it creates the file with mode `0666` and sets its mtime through `dirfwstat`.

Key behavior:
- `-t time` sets the timestamp with `strtoul`.
- `-c` suppresses creation but still reports a failed `wstat`.
- Processes all path arguments and exits `"touch"` if any failed.

Dependencies:
- Uses `Dir`, `nulldir`, `dirwstat`, `create`, `dirfwstat`, and `time`.

Reliability notes:
- It sets only `mtime`; it does not attempt POSIX-style access-time preservation.
- Creation uses `OREAD|OEXCL`, so existing-file races fail cleanly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/touch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/touchfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/touchfs.c

Read completely: 66 lines, 1120 bytes.

Filter for Plan 9 `mkfs` archive streams. It reads archive header lines from stdin, rewrites the fifth field to a supplied timestamp, copies each file payload unchanged, and stops at `end of archive`.

Key behavior:
- Expects exactly one argument: seconds timestamp.
- Uses `tokenize` on each archive header and requires six fields.
- `Bpass` copies the following payload byte count exactly, diagnosing corrupt or premature archives.

Dependencies:
- Uses `Biobuf`, `quotefmtinstall`, `Brdline`, `Bprint`, `Bread`, and `Bwrite`.

Reliability notes:
- The archive parser assumes header lines have no embedded newline surprises after quote tokenization.
- Payload size is trusted after `strtoul`; malformed sizes can desynchronize the stream.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/touchfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tprof.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tprof.c

Read completely: 147 lines, 2737 bytes.

Time profiler report tool for Plan 9 process profile data. It reads an executable’s symbol table and `/proc/<pid>/profile`, aggregates profile ticks into text symbols, sorts by time, and prints milliseconds/percentage/symbol.

Key behavior:
- With one argument, uses `/proc/<pid>/text`; with two, uses the supplied binary.
- Uses `crackhdr`, `machbytype`, `syminit`, and `textsym` from `<mach.h>`.
- Converts profile words through `machdata->swal`.
- Uses `PCRES` of 8 bytes to map profile buckets to symbol address ranges.

Reliability notes:
- Assumes profile data layout begins with total and secondary count, followed by PC buckets.
- `compar` sorts ascending and output walks backward for descending time.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tprof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tput.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tput.c

Read completely: 72 lines, 1234 bytes.

Throughput meter. It reads stdin in a configurable buffer, optionally writes data to stdout, and a shared-memory child reports byte rate once per second.

Key behavior:
- `-b buflen` sets read buffer size; default is `iounit(0)` or `IOUNIT`.
- `-p` passes input through to stdout.
- `-w` reports a one-second windowed rate by atomically swapping byte count; otherwise reports cumulative average.
- Uses `rfork(RFPROC|RFMEM)` so the child sees shared atomic counters.

Reliability notes:
- The reporting child runs until killed by parent with `postnote`.
- Write errors in pass-through mode are not checked; read errors are fatal.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tput.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tr.c

Read completely: 354 lines, 5975 bytes.

Plan 9 UTF-aware `tr` implementation. It supports delete, complement, squeeze, range syntax, octal escapes, and `\x` hexadecimal escapes over `Rune` values up to `Runemax`.

Key behavior:
- `delete` builds a bitset for characters to delete, with optional squeeze set.
- `translit` maps runes from string1 to string2, repeats the last target rune when string2 is shorter, and detects ambiguous source mappings.
- `complement` builds a mapping for all runes not in string1 up to the highest rune mentioned.
- `readrune` buffers stdin until a full UTF rune is available; `writerune` buffers output.
- `canon` expands `a-b` ranges while validating ordering.

Reliability notes:
- Bitsets are sized for all Plan 9 runes, so memory is fixed but large.
- Complement allocation is proportional to highest specified rune, which can be large.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/trace.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/trace.c

Read completely: 758 lines, 17892 bytes.

Interactive graphical scheduler trace viewer. It enables tracing for optional pids, reads binary `Traceevent` records from `/proc/trace` or another device, groups events by pid, and draws per-task timelines in a Plan 9 draw window.

Key behavior:
- Flags select trace device, new window, verbose event logging, and trigger process.
- `newtask` creates task rows and names them from `/proc/<pid>/status`.
- `doevent` appends events, calculates run intervals, totals, per-release runtime, and removes dead tasks.
- `redraw` scrolls prior timeline content, draws events, run/EDF spans, interrupts, grid ticks, labels, and elapsed time.
- Keyboard controls reset counters, pause, zoom, quit, and toggle verbose mode.

Dependencies:
- Uses Plan 9 thread/draw/mouse/keyboard APIs, `/proc/trace`, `/proc/<pid>/ctl`, `/dev/wctl`, and `trace.h`.

Reliability notes:
- It asserts event read sizes align to `Traceevent`.
- Task/event arrays are grown with `realloc` and assert success.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/dwbinit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/dwbinit.c

Read completely: 275 lines, 8008 bytes.

DWB pathname initialization helper for troff/nroff. It calculates the DWB home directory from environment/defaults, optionally reads debug configuration, and rewrites path pointer/array entries listed in `dwbinit` arrays.

Key behavior:
- `DWBhome` determines the active DWB root, using `DWBHOME` and defaults.
- `DWBdebug` emits path-debug information controlled by `DWBDEBUG`.
- `DWBinit` walks `dwbinit` entries, prefixes relative paths with the DWB home, preserves absolute paths, allocates replacement strings for pointer entries, and copies into bounded arrays where possible.
- Supports `\*(.P` prefix semantics for DWB-relative paths.

Dependencies:
- Includes `tdef.h` and `dwbinit.h`; used by `n1.c` for `DWBfontdir`, `DWBntermdir`, `DWBalthyphens`, `DWBhomedir`, and `nextf`.

Reliability notes:
- Bounded array entries are checked for room.
- Pointer entries are reallocated and can fatal-error on allocation failure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/dwbinit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/dwbinit.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/dwbinit.h

Read completely: 19 lines, 491 bytes.

Header for DWB pathname initialization. It defines `dwbinit`, where each entry either names a string pointer to replace or a fixed array to fill, plus the array length for bounded copies.

Declared API:
- `DWBinit(char *, dwbinit *)`
- `DWBhome(void)`
- `DWBprefix(char *, char *, int)`

Dependencies:
- Consumed by `dwbinit.c` and troff startup code.

Reliability notes:
- The header documents the ownership distinction: pointer values are reallocated, fixed arrays are only overwritten if there is room.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/dwbinit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/ext.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/ext.h

Read completely: 184 lines, 3497 bytes.

Global extern declaration header for the troff/nroff program. It exposes shared process state across the historically split `n*.c` and `t*.c` translation units.

Key contents:
- Input/output buffers, file stacks, macro/string storage offsets, diversion state, environments, registers, traps, page ranges, fonts, special character names, terminal paths, and flags.
- Externs for `Numtab *numtabp`, `Diver *dip`, `Stack` frames, `Wcache`, translation table, and special-character integer IDs.
- DWB pathname globals: `DWBfontdir`, `DWBntermdir`, and `DWBalthyphens`.

Dependencies:
- Definitions are primarily in `ni.c`, with behavior spread across `n1.c` through `n10.c` and troff-specific files.

Reliability notes:
- This is a shared-state architecture; correctness depends on disciplined global mutation rather than encapsulation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/ext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/fns.h

Read completely: 379 lines, 7219 bytes.

Function prototype hub for troff/nroff. It declares routines from input handling, output, macro/string management, registers, requests, line filling, hyphenation, drawing, terminal output, font loading, and nroff/troff-specific implementations.

Key contents:
- Prototypes for `n1.c` through `n10.c` request handlers and helpers.
- Troff-specific `t6.c`, `t10.c`, and `t11.c` declarations.
- Nroff-specific `n6.c` and `n10.c` declarations.
- Indirect function pointer externs used to dispatch through `TROFF`/`NROFF`, such as `width`, `setch`, `ptout`, `setfont`, `vmot`, and `hmot`.

Dependencies:
- Included by most troff/nroff source files after `tdef.h`.

Reliability notes:
- The header reflects a large C89-style shared program, including some legacy untyped declarations elsewhere in the implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/hytab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/hytab.c

Read completely: 126 lines, 7232 bytes.

Static hyphenation digram tables for legacy troff/nroff hyphenation. It defines unsigned-char matrices such as `bxh`, `hxx`, `bxxh`, `xhx`, and `xxh`, used by `n8.c` scoring logic.

Key behavior:
- Contains no functions; it is data-only.
- Tables encode pair/trigram-like hyphenation desirability values for alphabetic contexts.

Dependencies:
- Used by `dilook`/`digram` style hyphenation logic in `n8.c`.

Reliability notes:
- The tables are opaque historical data; changing values would directly affect line breaking and hyphen insertion.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/hytab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/mbwc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/mbwc.c

Read completely: 22 lines, 400 bytes.

Compatibility implementation of `mbtowc` for Plan 9 runes. It decodes a UTF sequence into a `Rune` with `chartorune`.

Key behavior:
- If `s == nil`, returns 0.
- If `len <= 0`, returns -1.
- Calls `chartorune`; returns -1 when decoded byte count exceeds supplied length.
- Stores decoded rune through `rp` and returns byte length.

Dependencies:
- Includes `<u.h>` and `<libc.h>`.

Reliability notes:
- This is minimal and does not implement full C library conversion state; it is enough for the local troff code paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/mbwc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/n1.c

Read completely: 1126 lines, 20443 bytes.

Troff/nroff startup, main input loop, file stack, input character fetching, escape interpretation, and selected requests. It decides troff vs nroff, initializes DWB paths and global tables, parses command options, then repeatedly dispatches requests or text.

Key behavior:
- `main` handles options for nroff mode, font dir, stdin after files, initial page number, emboldening, stop mode, register definitions, macro packages, page list, device, ascii output, eqn mode, quiet tty mode, version, and trace.
- `init2` initializes translation tables, terminal output, environments, line/word buffers, macro storage, and built-in strings `.T`/`.P`.
- `getch` and `getch0` implement escape processing for registers, strings, motion, fields, ligatures, comments, special characters, drawing, copy-through, and pushback.
- `nextfile`, `caseso`, `casenx`, `casecf`, and `caself` manage input inclusion and file/line tracking.
- `control` dispatches requests or macro invocation via `contab`.

Reliability notes:
- This is core parser state with many globals and pushback stacks; overflow paths diagnose and exit.
- `.sy` directly invokes `system`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n10.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/n10.c

Read completely: 574 lines, 12238 bytes.

Nroff terminal initialization and output driver. It reads terminal description data, initializes nroff output characteristics, maps special names, emits characters/control sequences, and handles plot/move commands.

Key behavior:
- `parse` converts escaped description strings into internal terminal strings, including numeric escapes and multibyte characters.
- `getnrfont` reads nroff character width/string entries.
- `n_ptinit` loads the selected terminal table, sets resolution/size fields, and initializes output function pointers for nroff.
- `n_specnames` binds special-character globals to terminal character names.
- `n_ptout`/`ptout1` convert `Tchar` output into terminal bytes or escape forms.
- `plot`, `move`, `n_ptlead`, and `n_ptpause` implement terminal movement and pause behavior.

Dependencies:
- Uses globals from `ext.h`, terminal/font structs from `tdef.h`, and conversion helpers including local `mbtowc`.

Reliability notes:
- Bad or mismatched terminal tables are fatal.
- Missing glyph strings degrade to diagnostics or fallback output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n10.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/n2.c

Read completely: 319 lines, 4981 bytes.

Troff/nroff output buffering and termination logic. It accepts internal `Tchar` output, handles transparent/copy-through regions, converts unusual characters to printable forms when needed, flushes output, and performs staged shutdown.

Key behavior:
- `pchar` and `pchar1` send characters through `ptout`, preserving XON/XOFF copy-through state.
- `outweird` and `outascii` print best-effort ASCII representations for special/internal characters.
- `flusho` flushes buffered output unless output is suppressed.
- `done`, `done1`, `done2`, `done3`, and `edone` unwind processing, flush output, run end macros, and exit.
- `casepi` creates a pipe to a command for output redirection.

Dependencies:
- Uses terminal output callbacks, `popen`/`pclose`, global output state, traps, and `sjbuf`.

Reliability notes:
- Pipe command strings are buffered with fixed-size storage and checked for available space.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n3.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/n3.c

Read completely: 953 lines, 16260 bytes.

Macro, string, diversion, and input-stack storage manager. It owns the dynamic `contab` namespace, macro hash table, block storage for macro/string bodies, argument collection, and diversion-related requests.

Key behavior:
- Initializes/grows macro namespace with `mnspace`, `growcontab`, `maddhash`, `munhash`, and `mrehash`.
- Implements `.de`, `.am`, `.ds`, `.as`, `.rm`, `.rn`, `.ig`, and lookup/clear operations.
- `alloc`, `wbf`, `rbf`, `ffree`, and related offset helpers manage block-list storage for macro/string definitions.
- `collect` parses macro arguments into stack frames.
- `casedi`, `caseda`, `casegd`, `casedt`, `casetl`, `casepm`, and `stackdump` handle diversions, traps, titles, printing macro stats, and debugging.

Reliability notes:
- Many allocation failures are fatal with diagnostics.
- Diversion nesting and macro recursion are guarded by limits but depend on global stack state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n4.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/n4.c

Read completely: 319 lines, 4981 bytes.

Number register and numeric expression handling for troff/nroff. It manages dynamic number-register namespace, parses scaled numeric arguments, formats registers, and implements related requests.

Key behavior:
- `setn` expands `\n` number-register escapes.
- `nnspace`, `grownumtab`, `nrehash`, `nunhash`, `findr`, and `usedr` manage the `Numtab` hash table.
- `fnumb`, `decml`, `roman`, and `abc` format numeric output.
- `atoi0`, `atoi1`, `ckph`, `vnumb`, `hnumb`, `inumb`, and `quant` parse numeric arguments with scaling and arithmetic.
- Implements `.nr`, `.rr`, `.af`, and numeric-format retrieval.

Reliability notes:
- Reports numeric parse context through `numerr`.
- Register table growth is bounded by allocation success and emits clear diagnostics when exhausted.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n5.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/n5.c

Read completely: 1151 lines, 14270 bytes.

Large collection of troff/nroff request implementations for layout state, conditionals, spacing, traps, environments, tabs, translation, user interaction, and tty handling.

Key behavior:
- Alignment/fill and line state: `.ad`, `.na`, `.fi`, `.nf`, `.ce`, `.in`, `.ll`, `.lt`, `.ti`, `.ls`, `.po`, `.pl`.
- Traps/pages: `.wh`, `.ch`, `.pn`, `.bp`, `.ne`, `.sv`, `.os`, `.it`.
- Messages/files: `.tm`, `.fm`, `.rd`, `.ab`.
- Environments and conditionals: `.ev`, `.if`, `.ie`, `.el`, string comparisons, block skipping.
- Characters/tabs/translations: `.cc`, `.c2`, `.hc`, `.tc`, `.lc`, `.ta`, `.tr`, `.ec`, `.eo`.
- Underline and numbering: `.ul`, `.cu`, `.uf`, `.mc`, `.mk`, `.nm`, `.nn`.
- Quiet-mode tty echo helpers for `.rd`.

Reliability notes:
- Multiple fixed limits are enforced, including traps, streams, tab stops, and condition nesting.
- `.rd` manipulates terminal echo state and restores saved tty settings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n6.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/n6.c

Read completely: 361 lines, 4851 bytes.

Nroff character width, font, size, and motion implementation. These functions are the nroff-side implementations assigned to indirect function pointers during nroff initialization.

Key behavior:
- `n_width` computes terminal width for internal characters.
- `n_setch` and `n_setabs` resolve named/absolute characters.
- `n_findft`, `n_caseft`, `n_setfont`, and `n_casefp` manage nroff font selection.
- `n_setps`, `n_setht`, and `n_setslant` parse but mostly simplify size/height/slant behavior for nroff.
- `n_setwd` evaluates width functions.
- `n_vmot`, `n_hmot`, `n_mot`, `n_sethl`, `n_makem`, `n_casebd`, `n_casevs`, and `n_xlss` generate motion and vertical spacing.

Reliability notes:
- Nroff intentionally ignores or approximates many troff physical-device features.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n7.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/n7.c

Read completely: 832 lines, 12494 bytes.

Line filling, breaking, output-line assembly, page ejection, traps, hyphenation integration, and word collection. This is the core formatter loop after characters have been parsed.

Key behavior:
- `tbreak` finalizes current filled line with adjustment and output.
- `text` consumes text into words/lines; `nofill` handles no-fill mode.
- `storeword`, `storeline`, `getword`, `movword`, and `horiz` manage line and word buffers.
- `newline`, `findn1`, `chkpn`, `findt`, `findt1`, and `eject` handle line/page counters, traps, page transitions, and printing page ranges.
- Hyphenation is invoked when words exceed remaining line space and hyphenation flags permit it.
- `gettch` fetches characters while tracking widths and special motions.

Reliability notes:
- Buffer sizes are managed through environment line/word buffers; overrun behavior depends on helpers and global limits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n7.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n8.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/n8.c

Read completely: 550 lines, 10307 bytes.

Hyphenation engine. It combines legacy digram scoring, explicit exception words, suffix/vowel heuristics, and optional TeX-style hyphenation patterns.

Key behavior:
- `hyphen` chooses the active hyphenation algorithm and marks candidate breakpoints.
- `.ha`, `.ht`, and `.hw` configure algorithm, threshold, and exception words.
- `growh`, `casehw`, and `exword` manage the exception word list.
- `suffix`, `maplow`, `vowel`, `chkvow`, `digram`, and `dilook` implement older heuristic hyphenation.
- `texhyphen`, `texit`, `readpats`, `install`, `fixup`, and `trieindex` load and apply `hyphen.tex`-style patterns from `DWBalthyphens`.

Reliability notes:
- The TeX pattern trie has fixed bounds and warns/truncates on overflow.
- Hyphenation is mostly ASCII/lowercase oriented despite Plan 9 character handling elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n8.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n9.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/n9.c

Read completely: 486 lines, 9072 bytes.

Escape sequence builders for zero-width characters, horizontal/vertical lines, overstrikes, brackets, drawing functions, field delimiters, and field padding.

Key behavior:
- `setz` creates zero-width character sequences.
- `setline` and `setvline` build horizontal and vertical line drawing using repeated or motion-based characters.
- `setov` handles overstrike sequences.
- `setbra` handles bracket escape construction.
- `setdraw` parses drawing commands and emits internal drawing cookies.
- `casefc` sets field delimiter/pad characters.
- `setfield` expands field contents with padding and alignment.

Reliability notes:
- Fixed-size internal buffers and `NC` limits constrain drawing/field construction.
- Some malformed input degrades to warnings such as ignored zero-width underline or zero field width.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/n9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/ni.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/ni.c

Read completely: 389 lines, 8475 bytes.

Global data definition file for troff/nroff. It instantiates most variables declared in `ext.h`, including built-in registers, request table, initial environment, buffers, flags, special character slots, and indirect function pointers.

Key contents:
- Initial `Numtab` entries for page number, line, date, time, and status registers.
- `contab` maps two-character request names to handlers such as `.ds`, `.sp`, `.ft`, `.if`, `.bp`, `.br`, `.so`, `.hy`, `.cf`, and many more.
- Initial `Env env[NEV]` sets default fill, adjust, font, point size, control characters, hyphenation, tab, line, and word state.
- Defines stacks, diversions, trap arrays, page lists, translation table, buffers, special-name table, and runtime-dispatch function pointers.

Reliability notes:
- This file is the shared mutable backbone of the formatter; initialization order with `n1.c` matters.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/ni.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/popen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/popen.c

Read completely: 153 lines, 3271 bytes.

Local `popen`/`pclose` implementation for Plan 9 stdio. It forks `/bin/rc -c <file>`, connects a pipe to the child depending on read/write mode, tracks child pid by file descriptor, and waits for completion.

Key behavior:
- `_pipefd` wraps a pipe fd in a `FILE *`.
- `popen` supports modes beginning with `r` or `w`.
- Child duplicates pipe end to stdin or stdout, closes pipe fds, and execs `/bin/rc`.
- `pclose` closes the stream, waits for the tracked pid, and handles interrupted waits with a note handler.

Reliability notes:
- Tracks by `fileno(fp)` in a fixed `Maxfd` table.
- Reports “no child process for fd” if `pclose` is called on an untracked stream.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/popen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/space.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/space.c

Read completely: 74 lines, 1237 bytes.

Small whitespace/word parsing helpers. It provides string-level skipping and fd-level reading of whitespace-delimited words.

Key behavior:
- `skipspace` advances past C `isspace` bytes.
- `skipword` advances past non-space bytes.
- `rdspace` reads and discards whitespace from an fd, returning the first non-space byte or EOF/error.
- `rdword` fills a buffer with a word after leading whitespace, stops at whitespace or buffer limit, and NUL-terminates.

Dependencies:
- Uses Plan 9 `read`, `<ctype.h>`, and libc types.

Reliability notes:
- `rdword` reserves one byte for NUL and stops when the buffer is full, so long words are truncated at the caller-provided maximum.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/space.c -->