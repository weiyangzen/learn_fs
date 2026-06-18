# Group Research: group_1592_plan9_sources_os_plan9_plan9_sys_src_cmd_htmlroff_roff_c_sources_os_146fbf9ccd13

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/roff.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/roff.c

`roff.c` is the central htmlroff interpreter loop. It owns the dispatch tables for normal requests (`Req`), raw requests (`Raw`), and escape handlers (`Esc`), plus global parser controls such as `dot`, `tick`, `backslash`, `inputmode`, conditional state, output paragraph state, and current line position.

Key behavior:
- `addreq`/`delreq`/`renreq`, `addraw`/`delraw`/`renraw`, and `addesc` register troff request and escape handlers used by the `t*.c` modules.
- `getnext` reads logical input characters, expands registered escapes depending on mode, handles `Uformatted`/`Uunformatted` diversion sentinels, and preserves escapes in argument/copy contexts when needed.
- `copyarg`, `readline`, and `parseargs` implement request argument reading, quote handling, and troff comment stripping.
- `dotline` dispatches control lines to raw handlers, regular builtins, or user-defined macros.
- `runinput` is the main lexer/interpreter loop; it recognizes request lines at beginning of line, handles newline semantics, starts paragraph output, and emits runes.
- `startoutput` maps current number registers into HTML paragraph style attributes for line height, margins, indent, and alignment.
- `outrune` and `outhtml` convert internal pseudo-runes and normal runes into escaped HTML output.

Important dependencies:
- Requires `t1init` through `t20init`, `htmlinit`, macro support, number/string registers, input stack helpers, and output globals from `a.h` and sibling files.
- `run()` intentionally does not call `t9init` and `t12init`, with comments noting those source files.

Notable risks/quirks:
- Dispatch tables have fixed caps (`MAXREQ`, `MAXRAW`, `MAXESC`) and only warn on overflow.
- Output formatting is approximate troff-to-HTML translation, not layout-faithful.
- `ungetnext` only pushes one rune and admits it cannot fully undo compound escape reads.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/roff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t1.c

`t1.c` implements early troff numeric parsing support and initializes date-related number registers.

Key behavior:
- `scale2units` maps troff scale suffixes (`i`, `c`, `P`, `m`, `n`, `p`, `u`, `v`) plus htmlroff’s `x` pixel unit into internal units.
- `eval`, `evalscale`, and recursive `eval0` parse numeric expressions with arithmetic, comparisons, `&`, and `:` logical-style operations.
- Handles signed numbers, decimals, parentheses, and explicit unit suffixes.
- `t1init` sets `dw`, `dy`, `mo`, and `yr` from local time.

Important dependencies:
- Reads `.s` and `.v` number registers for em/en/vertical scaling.
- Uses `UPI`, `UPX`, and Plan 9 rune utilities from `a.h`.

Notable risks/quirks:
- Expression parsing is simple and effectively left-associative rather than a full precedence parser.
- Division/modulo by zero prints diagnostics and substitutes divisor `1`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t10.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t10.c

`t10.c` implements input/output convention controls and character translation-related escapes.

Key behavior:
- `.ec` changes the escape character; `.eo` disables it.
- `.cc` changes the control character; `.c2` changes the no-break control character.
- `\!` reads and outputs a copied line directly.
- `\X'...'` emits device-control contents until quote/newline.
- `\"` is a comment outside argument mode, but is preserved for argument parsing in `ArgMode`.
- Registers no-op or warning handlers for unsupported features like `.tr`, `.lg`, `.ul`.

Important dependencies:
- Mutates global `backslash`, `dot`, and `tick` used by `roff.c`.
- Uses `readline`, `out`, `outrune`, and `warn`.

Notable risks/quirks:
- Output translation `.tr` is not implemented.
- `\X` is treated as raw output-ish text, not a structured device command.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t10.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t11.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t11.c

`t11.c` implements local motion and width-function escapes.

Key behavior:
- `dv` tracks vertical displacement in `.dv` and maps nonzero displacement to internal HTML insertion state using `<sub>` or `<sup>`-style tags encoded through pseudo-runes.
- `\v'...'`, `\u`, `\d`, and `\r` adjust vertical displacement.
- `\h'...'` consumes horizontal motion but does not affect output.
- `\w'...'` returns the rune-string length as a crude width and clears `st`, `sb`, and `ct`.
- `\0` returns a digit-width space approximation.
- `\k` warns that marking horizontal position is unavailable.

Important dependencies:
- Uses `getqarg`, `eval`, `nr`, `getnr`, `pushinputstring`, and `ihtml`.

Notable risks/quirks:
- Width is rune count, not rendered width.
- Horizontal motion and named position capture are mostly ignored.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t11.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t12.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t12.c

`t12.c` contains handlers for overstrike, bracket, line drawing, graphics, and zero-width functions.

Key behavior:
- `\o'...'` and `\b'...'` push their quoted argument back into input, approximating overstrike/bracket by just emitting content.
- `\z` consumes one logical character and emits nothing.
- `\l`, `\L`, and `\D` consume quoted drawing arguments and emit nothing.
- `t12init` registers these escapes.

Important dependencies:
- Uses `getqarg`, `getnext`, `pushinputstring`, and escape registration.

Notable risks/quirks:
- `roff.c` comments out `t12init()`, so this module’s handlers are not active in the normal initialization path.
- Drawing and zero-width semantics are lossy approximations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t12.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t13.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t13.c

`t13.c` stubs hyphenation support.

Key behavior:
- Registers `.nh`, `.hy`, `.hc`, and `.hw` as no-ops.
- Registers `\%` as a no-op escape.

Important dependencies:
- Uses shared `r_nop`, `e_nop`, `addreq`, and `addesc`.

Notable risks/quirks:
- No actual hyphenation behavior is implemented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t13.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t14.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t14.c

`t14.c` handles title-length state and stubs title rendering.

Key behavior:
- `.lt` sets or adjusts the `.lt` title length register, defaulting to `6.5i`.
- `.tl` warns as unsupported.
- `.pc` is accepted as a no-op page-number-character request.

Important dependencies:
- Uses `evalscale`, `nr`, `getnr`, and `warn`.

Notable risks/quirks:
- Three-part title rendering is not implemented; only length state is maintained.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t14.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t15.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t15.c

`t15.c` stubs output line numbering.

Key behavior:
- Registers `.nm` and `.nn` as warning handlers.

Important dependencies:
- Uses shared request registration and `r_warn`.

Notable risks/quirks:
- No line numbering support is implemented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t15.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t16.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t16.c

`t16.c` implements conditional input acceptance.

Key behavior:
- Supports `.if`, `.ie`, and `.el` as raw requests with custom parsing.
- `ifeval` handles numeric truth, negation, condition letters (`o`, `t`, `h`, `n`, `e`), and quoted string comparisons.
- `.ie` pushes condition results onto `iftrue`; `.el` consumes the stack and selects/skips bodies.
- `startbody` positions input at body start; `skipbody` skips to newline while tracking `\{...\}` blocks.
- Registers `\{` and `\}` as no-op escapes in HTML/argument modes.

Important dependencies:
- Uses `copyarg`, `eval`, `getnext`, `getrune`, and global `dot`.
- Declares its own `iftrue`/`niftrue`, matching globals in `roff.c`.

Notable risks/quirks:
- Supports only a subset of troff condition grammar.
- Conditional block nesting is tracked only while skipping bodies.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t16.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t17.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t17.c

`t17.c` implements troff environment switching.

Key behavior:
- Defines an `Env` snapshot for point size, font, fill mode, adjustment, centering, vertical spacing, line spacing, and input trap count.
- `saveenv` reads current registers into an environment.
- `restoreenv` writes registers back, updates `.ev`, and runs the `font` macro.
- `.ev` without an argument pops the previous environment; `.ev N` saves current state and switches to environment `0..2`.
- `t17init` initializes three environments from `defenv`.

Important dependencies:
- Uses number registers and `runmacro1("font")`.

Notable risks/quirks:
- Many troff environment fields are explicitly omitted in comments.
- Stack is fixed at 20 entries.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t17.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t18.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t18.c

`t18.c` implements standard-input insertion and early termination.

Key behavior:
- `.rd` optionally prompts on console, reads lines from stdin until a blank line, stores them in temporary string `.rd`, and runs that string as a macro with remaining arguments.
- `.ex` pops all input sources, causing processing to end as if input reached EOF.

Important dependencies:
- Uses Plan 9 `fd2path`, `Biobuf`, `Brdstr`, `runmacro`, `ds`, and input-stack helpers.

Notable risks/quirks:
- Stdin is initialized once in static `Biobuf`.
- `.rd` uses a string/macro bridge rather than streaming inserted text directly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t18.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t19.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t19.c

`t19.c` handles input/output file switching and pipe-style input.

Key behavior:
- `.so` pushes a source file.
- `.nx` ends current/all input and optionally switches to another file.
- `.cf` copies a file’s contents directly to output as runes.
- `.inputpipe` forks `/bin/rc -c <cmd>`, sends a troff fragment into its stdin until a stop line, and waits for completion.
- `.sy` and `.pi` are raw requests that warn as unimplemented.
- Initializes number register `$$` to process id.

Important dependencies:
- Uses input-stack functions, `readline`, Plan 9 `pipe`/`fork`/`execl`/`wait`, and output rune emission.

Notable risks/quirks:
- `.inputpipe` calls `sysfatal` if the child exits with a message.
- System and output-pipe requests are not implemented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t19.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t2.c

`t2.c` implements font, character-size, and named-character escape handling.

Key behavior:
- `getqarg` reads single-quoted escape arguments.
- `\N'...'` emits the evaluated numeric character code.
- `\(xx` maps two-character troff names through `troff2rune`.
- Maintains `fonttab` for mounted fonts, with `.fp`, `.ft`, and `\f` changing `.f`/`.f0`.
- `ps`, `.ps`, and `\s` manage point size via `.s`/`.s0`.
- `t2init` mounts default fonts `R`, `I`, `B`, `BI`, `CW`, initializes `.s`, and registers requests/escapes.

Important dependencies:
- Uses `runmacro1("font")` after font/size changes so HTML font state can update.

Notable risks/quirks:
- Unknown fonts fall back to font position 1 with a warning.
- Several character features are delegated elsewhere or warned as unsupported.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t20.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t20.c

`t20.c` implements miscellaneous requests.

Key behavior:
- `.pm` prints macro/string sizes, total size, or named macro/string bodies.
- `.tm` emits a copied line to stderr.
- `.ab` emits a message and exits.
- `.lf` updates source line/file tracking.
- `.fl` flushes the output buffer.
- `.mc` is registered as a warning handler.

Important dependencies:
- Uses string-register functions, `readline`, `setlinenumber`, and output `bout`.

Notable risks/quirks:
- `.pm` is diagnostic rather than document-output behavior.
- `.ab` exits the whole process.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t20.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t3.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t3.c

`t3.c` handles limited page-control state.

Key behavior:
- `po` maintains current and previous page offset in `.o` and `.o0`.
- `.po` sets, restores, increments, or decrements page offset.
- Initializes `.o`, `.o0`, and `.p`.
- Registers page requests such as `.pl`, `.bp`, `.pn`, `.ne`, `.mk`, `.rt`, mostly as warnings/no-ops.

Important dependencies:
- Uses numeric expression scaling and register helpers.

Notable risks/quirks:
- Page geometry is mostly irrelevant to htmlroff and not faithfully implemented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t4.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t4.c

`t4.c` implements filling, centering, adjustment, and several text escapes.

Key behavior:
- `\ ` emits non-breaking space.
- `\&` emits internal empty pseudo-rune.
- `\c` consumes the next raw rune, resets beginning-of-line state, and suppresses output.
- `.br` breaks current paragraph.
- `.fi`/`.nf` toggle fill mode register `.fi`.
- `.ad` sets adjustment mode register `.j`; `.na` clears adjustment.
- `.ce` sets number of centered lines via `.ce`.

Important dependencies:
- `startoutput` in `roff.c` reads `.fi`, `.j`, and `.ce`.

Notable risks/quirks:
- Filling/adjustment affects generated paragraph style only; no real troff line-breaking is performed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t5.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t5.c

`t5.c` handles vertical spacing.

Key behavior:
- `.vs` manages vertical baseline spacing `.v` and previous `.v0`.
- `.ls` manages line spacing `.ls` and previous `.ls0`.
- `sp` closes any active paragraph and emits an empty HTML paragraph with `margin-bottom`.
- `.sp` and `.sv` emit vertical space unless no-space mode `.ns` is set.
- `.ns` and `.rs` set/clear no-space mode.
- Initializes `.v`, `.v0`, `.ls`, `.ls0`.

Important dependencies:
- `startoutput` uses `.v` and `.ls` for HTML line height.

Notable risks/quirks:
- Large spacing is capped/fallbacked to one vertical unit.
- Absolute `.sp |...` is ignored with an optional warning.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t6.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t6.c

`t6.c` implements line length and indenting state.

Key behavior:
- `.ll` sets/restores/increments/decrements line length `.l` with previous `.l0`.
- `.in` breaks output and sets/restores/increments/decrements indent `.i`, tracking previous `.i0`.
- `.ti` breaks output and sets temporary indent `.ti`.
- Initializes `.l` to `6.5i`.

Important dependencies:
- `startoutput` uses `.l`, `.i`, `.ti`, and `.o` to compute paragraph margins.

Notable risks/quirks:
- No actual line wrapping is done; state only influences generated CSS.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t7.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t7.c

`t7.c` implements macros, strings, diversions, and traps.

Key behavior:
- `runmacro` looks up a string by name, pushes it onto the input stack, tracks arguments on a macro stack, and sets `.$`.
- `runmacro1` invokes a macro synchronously from output/context callbacks using `setjmp`/`longjmp` around `runinput`.
- `.de`, `.am`, and `.ig` define, append, or ignore macro bodies until a terminator.
- `.ds`/`.as` define or append strings as raw requests.
- `.rm` removes requests/raw handlers/strings; `.rn` renames them.
- `.di`/`.da` divert output into strings through `outcb`.
- `.wh`, `.ch`, `.dt`, `.it`, and `.em` implement simplified traps/end macros.
- Escapes include macro/string expansion `\*`, macro args `\$`, tab/bell in copy mode, escaped backslash, and escaped dot.
- Initializes default `eof` and `..` strings.

Important dependencies:
- Depends heavily on `t8.c` string/register storage, input stack notification, and global output callback.

Notable risks/quirks:
- Only trap at position 0 is meaningfully supported.
- Diversion sizing and page offset semantics are mostly ignored.
- Macro stack and diversion stack are fixed size.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t7.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t8.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t8.c

`t8.c` implements string and number registers.

Key behavior:
- Maintains linked lists for string definitions (`dslist`) and number registers (`nrlist`) using `Reg`.
- `ds`, `as`, and `getds` manage strings.
- `nr`, `_nr`, `_getnr`, and `getnr` manage numeric/string-valued registers.
- `.nr`, `.af`, and `.rr` define, format, and remove registers.
- Supports increment values for `\n+R`/`\n-R`.
- Formats register values as decimal with width, roman numerals, or alphabetic counters.
- `getname` parses one-character, two-character, and bracketed names.
- `\n` expands registers; `\g` expands register format.

Important dependencies:
- `eval` parses register values when numeric access is requested.
- Macro/string code in `t7.c` depends on `ds`/`getds`.

Notable risks/quirks:
- `alpha` and roman conversion are simple and not robust for all edge cases.
- Some registers can intentionally store strings, so `getnr` and `_getnr` have distinct semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t8.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t9.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t9.c

`t9.c` is a placeholder for tabs, leaders, and fields.

Key behavior:
- Contains only a section comment and literal `XXX`.

Important dependencies:
- `roff.c` comments out `t9init()`.

Notable risks/quirks:
- This file is not valid implemented C logic and appears intentionally excluded from normal initialization/build.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/t9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/util.c

`util.c` provides allocation, formatting, warning, and rune literal helpers for htmlroff.

Key behavior:
- `emalloc`, `estrdup`, `erunestrdup`, `erealloc`, `esmprint`, and `erunesmprint` wrap allocation/formatting with fatal out-of-memory behavior.
- `warn` emits htmlroff diagnostics with current location `%L`.
- `L` converts C string literals to cached `Rune*` strings, keyed by source string pointer.

Important dependencies:
- Used across all htmlroff modules.

Notable risks/quirks:
- `L` assumes string literals can be identified by pointer identity and are immutable.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/iconv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/iconv.c

`iconv.c` is an image channel converter for Plan 9 memory images.

Key behavior:
- Usage: `iconv [-u] [-c chanstr] [file]`.
- Reads a `Memimage` from stdin or a named file.
- Converts to requested channel descriptor via `allocmemimage` and `memimagedraw`.
- Writes compressed Plan 9 image output by default via `writememimage`.
- With `-u`, emits uncompressed image header plus raw scanlines from `unloadmemimage`.

Important dependencies:
- Uses `<draw.h>` and `<memdraw.h>` APIs.

Notable risks/quirks:
- Does not free image objects before exit, relying on process teardown.
- `writeuncompressed` validates exact scanline unload/write sizes and fatal-exits on mismatch.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/iconv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/idiff.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/idiff.c

`idiff.c` is an interactive diff merger inspired by Kernighan and Pike.

Key behavior:
- Usage: `idiff [-bw] file1 file2`.
- Validates both inputs are non-directories, opens them with `Biobuf`, and runs `/bin/diff -n`.
- Stores diff output and merged result in temporary ORCLOSE files.
- `idiff` walks normal diff hunks and prompts the user:
  - `<` keeps file1 side.
  - `>` takes file2 side.
  - `=` inserts diff text.
  - `q<`, `q>`, `q=` select a default for all remaining hunks.
  - `!cmd` runs a shell command.
- Copies selected line ranges into output, then writes final merged output to stdout.

Important dependencies:
- Relies on Plan 9 `/bin/diff -n` output format and Biobuf line helpers.

Notable risks/quirks:
- Temporary creation loops over `mktemp` up to 10 tries.
- Diff parser is strict and fatal on unexpected format.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/idiff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/import.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/import.c

`import.c` mounts a remote exported Plan 9 filesystem.

Key behavior:
- Supports mount flags, old 9P compatibility, authentication disable, encryption selection, AAN filtering, `/srv` posting, passive/backwards mode, and no-tree mode.
- `connect` dials `exportfs`, performs auth (`p9any` or `p9sk2`), sends requested tree, and optionally wraps old servers through `srvold9p`.
- For SSL mode, exchanges random key material, derives two textual secrets from SHA1, optionally runs filter, and calls `pushssl`.
- `passive` authenticates on stdin/stdout as a server-side passive import.
- `filter` reads a remote port, constructs a filtered connection command, forks it, and returns the pipe fd.
- Final fd is mounted at requested mount point or posted in `/srv`.

Important dependencies:
- Uses Plan 9 auth, libsec, network dialing, mount, and namespace APIs.

Notable risks/quirks:
- TLS option exists but fatal-errors as unimplemented.
- Encryption default algorithms are old (`rc4_256 sha1`).
- Timeout is implemented with an alarm note.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/import.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/init.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/init.c

`init.c` is the Plan 9 user-level init process.

Key behavior:
- Closes leftover boot fds, sets priority, initializes environment (`objtype`, `service`, `timezone`), creates a new namespace, and determines CPU vs terminal service.
- On CPU service without manual mode, runs `/rc/bin/cpurc` once.
- Then repeatedly starts `/bin/rc`, with terminal service using `termrc` and profile setup.
- `fexec` forks child exec functions and waits, handling notes and fatal exec failures.
- `pass` prompts for and verifies a DES-key password from a key fd, though it is not used by `main` in this file.
- `readenv`, `setenv`, and `cpenv` operate directly on Plan 9 environment files.

Important dependencies:
- Uses Plan 9 `/dev`, `#e`, `#c`, authsrv DES key helpers, and namespace setup.

Notable risks/quirks:
- `setenv` calls `fprint(fd, val)` directly, so values are treated as format strings.
- The process intentionally loops forever restarting shell sessions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/iostats/iostats.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/iostats/iostats.c

`iostats.c` launches a command under a proxy root filesystem and reports 9P/file I/O statistics.

Key behavior:
- Usage: `iostats [-d] [-f debugfile] cmds [args ...]`.
- Forks a child command in a namespace where `/` is mounted from a pipe to the stats filesystem.
- Forks a server process that handles 9P messages from the pipe and proxies them to the real filesystem.
- Allocates shared work queues, stats, and fid hash tables.
- Dispatches 9P request types to handlers from `statsrv.c`, using blocking slave processes for open/read/write.
- On command exit, kills slave children and prints aggregate read/write/protocol throughput, per-RPC timing/counts, and per-file activity.
- Provides fid allocation, file tree caching, root initialization, path construction, fatal cleanup, path-based exec lookup, and file report aggregation.

Important dependencies:
- Includes `statfs.h` with `Extern` defined to allocate globals.
- Depends on `statsrv.c` for protocol handlers.

Notable risks/quirks:
- Fixed-size work queue and max slave process count.
- Uses shared-memory rfork patterns and intentionally simple locking assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/iostats/iostats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/iostats/statfs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/iostats/statfs.h

`statfs.h` is the shared contract for the iostats 9P proxy.

Key contents:
- Constants for debug file, process limits, fid hash size, max data size, max RPC array size, work buffer count, and fid chunking.
- Defines:
  - `Frec` for per-file aggregate opens/reads/writes/bytes.
  - `Rpc` and `Stats` for per-message timing and byte counters.
  - `Fsrpc` as a work item containing one `Fcall`, buffer, pid, busy/interrupt/flush state.
  - `Fid` as active fid state, backing fd, file pointer, counters, and directory offset.
  - `File` as cached tree node with qid and parent/child links.
  - `Proc` as blocking slave process state.
- Declares globals through `Extern`.
- Declares 9P service handlers and shared helpers.

Important dependencies:
- Consumed by both `iostats.c` and `statsrv.c`; `Extern` controls definition vs declaration.

Notable risks/quirks:
- `Maxrpc` is 20000 even though normal 9P message type ids are sparse and small.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/iostats/statfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/iostats/statsrv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/iostats/statsrv.c

`statsrv.c` implements the iostats proxy 9P server handlers.

Key behavior:
- Handles version/auth/flush/attach/walk/create/clunk/remove/stat/wstat directly.
- Uses `slave` and `blockingslave` to run blocking open/read/write operations in worker processes.
- `okfile` blocks unsafe/special paths like most `/fd`, `/net/ssl`, `/net/tls`, and writable `/srv`.
- `update` accumulates per-RPC latency stats.
- `Xwalk` maintains the synthetic file tree and qids.
- `slaveopen`, `slaveread`, and `slavewrite` perform real filesystem I/O and update totals plus fid counters.
- Flush handling can interrupt workers via notes and defer flush replies.

Important dependencies:
- Uses globals from `statfs.h` and reply/path/fid helpers from `iostats.c`.

Notable risks/quirks:
- Comments acknowledge races due to no locks around some shared fid/open state.
- Directory reads maintain sequential offset state and reject nonzero offset jumps.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/iostats/statsrv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/6in4.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/6in4.c

`6in4.c` implements an IPv6-in-IPv4 tunnel client, including automatic 6to4 defaults.

Key behavior:
- Usage: `6in4 [-ag] [-x mtpt] [local6[/mask]] [remote4 [remote6]]`.
- Derives default `2002:v4::1/48` local address from local IPv4 when not supplied.
- Defaults remote IPv4 to RFC 3068 anycast `192.88.99.1`.
- Opens an `ipmux` endpoint for IPv4 protocol 41/ICMPv6 and a local IPv6 packet interface.
- Optionally installs a `2000::/3` route through remote IPv6 with `-g`.
- Forks two loops:
  - `ip2tunnel` validates outgoing IPv6 packets, encapsulates in IPv4, and chooses direct 6to4 destination where applicable.
  - `tunnel2ip` validates incoming encapsulated packets and writes local-net-destined IPv6 packets to the packet interface.
- Includes filters for bad private/reserved IPv4-derived addresses, link-local, multicast, unspecified, and off-subnet inbound traffic.

Important dependencies:
- Uses Plan 9 `/net` IP interface files, `ipmux`, `ipifc`, and route control.

Notable risks/quirks:
- Packet parsing assumes Plan 9 IP header layouts and `read` framing.
- Security model is filtering-focused but not authenticated.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/6in4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/arp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/arp.h

`arp.h` defines shared ARP/RARP packet and cache structures.

Key contents:
- `Arppkt` maps Ethernet ARP packet layout.
- `ARPSIZE` is defined as 42.
- `Arpentry` maps an Ethernet address to IPv4 address for user-level ARP interactions.
- `Arpstats` tracks hits, misses, and failed lookups.
- Defines EtherType and ARP/RARP operation constants.

Important dependencies:
- Comment notes use by kernel, arpd, snoopy, and tboot.

Notable risks/quirks:
- IPv4/Ethernet-specific fixed layout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/arp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcp.h

`dhcp.h` defines DHCP/BOOTP protocol constants and the packet structure shared by client/server tools.

Key contents:
- Lease/time constants, DHCP states, BOOTP operation values, flags, and option numbers.
- Includes standard BOOTP options, DHCP options, PXE options, deprecated Plan 9 v4 vendor options, and textual Plan 9 vendor options.
- `Bootp` embeds a Plan 9 UDP header, fixed BOOTP fields, magic cookie, and option data.
- Defines `Lforever` as an infinite lease marker.

Important dependencies:
- Used by `dhcpclient.c` and `dhcpd` sources.

Notable risks/quirks:
- `Maxoptlen` is fixed to `312-4`.
- Plan 9 vendor options are integrated directly into the shared protocol enum.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpclient.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpclient.c

`dhcpclient.c` is a DHCPv4 client that prints acquired configuration and renews leases.

Key behavior:
- Usage: `dhcpclient [-x netextension]`.
- Maintains global `dhcp` state protected by `QLock`.
- Initializes xid from `/dev/random` or time/pid, constructs client id from `sysname.pid`.
- Opens UDP port 68 in header mode.
- Sends Discover, waits for Offer, sends Request, waits for Ack, then prints `ip=`, `mask=`, `end`.
- Keeps lease alive by sleeping half the lease, reopening the listener, and renewing.
- `timerthread` handles retransmission and state transitions.
- `stdinthread` waits for stdin EOF and sends Release before killing the process group.
- Implements option add/get helpers, packet validation, and verbose packet dump.

Important dependencies:
- Uses `dhcp.h`, Plan 9 UDP header mode, and IP formatting utilities.

Notable risks/quirks:
- Debug packet dump is unconditional in `dhcprecv` (`if(1)`).
- `stdinthread` checks `if(dhcp.client)`, but `dhcp.client` is an array and always truthy in C.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpclient.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/dat.h

`dat.h` is the DHCP server shared header.

Key contents:
- `Binding` tracks an IP lease: bound/offered client ids, lease/offer expiry, touch/complaint/probe timestamps, and qid of persisted lease file.
- `Info` holds NDB-derived host/network/server metadata: domain, boot files, TFTP, address/mask/net, Ethernet, gateway, fs/auth servers, rootpath, DHCP group, vendor data.
- Declares cross-file functions for lease database, NDB lookup, ICMP probing, logging, and globals.

Important dependencies:
- Includes `../dhcp.h`.
- Shared by server, helpers, and tests.

Notable risks/quirks:
- Mixes production declarations with test/helper-facing globals.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/db.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/db.c

`db.c` implements DHCP lease binding storage and allocation.

Key behavior:
- Lease files live under `binddir` (`/lib/ndb/dhcp` by default), named by IP address.
- `tohex` and `toid` convert client identifiers to printable strings.
- `syncbinding` lock-opens a lease file, rereads if qid changed, and lets the file win over cache.
- `initbinding` pre-populates binding cache for configured ranges.
- `iptobinding` finds/creates cached bindings by IP.
- `idtobinding` prefers previous matching bindings, then oldest expired/offered-free bindings on the requester’s network, optionally ICMP-probing candidates.
- `mkoffer`, `idtooffer`, `commitbinding`, and `releasebinding` implement offer/lease lifecycle.

Important dependencies:
- Uses global `now`, `minlease`, `blog`, `binddir`, and `icmpecho`.
- Uses `samenet` with `Info` network fields.

Notable risks/quirks:
- Uses exclusive lease files as a distributed coordination mechanism among servers.
- If lock cannot be acquired, it assumes someone else is using the binding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/db.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/dhcpd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/dhcpd.c

`dhcpd.c` is the main Plan 9 DHCP/BOOTP server.

Key behavior:
- Usage supports debug, mute, no-BOOTP, PPTP-only, slow response modes, lease tuning, v6 Plan 9 vendor options, network mount point, NDB file, and dynamic address ranges.
- Maintains per-request `Req` state with parsed BOOTP/DHCP data, relay/client addresses, requested options, NDB info, and reply buffer state.
- `proto` validates packet shape, detects Plan 9/generic option cookies, parses options, derives client id, looks up gateway/client info, and dispatches DHCP vs BOOTP.
- DHCP handlers implement Discover, Request, Decline, Release, and Inform behavior, using static NDB bindings or dynamic lease database bindings.
- `sendoffer`, `sendack`, and `sendnak` construct replies, choose unicast/broadcast/relay destinations, update ARP for direct replies, and emit options.
- `bootp` handles legacy BOOTP, Plan 9 vendor fields, generic RFC1048 options, boot file selection, TFTP server selection, and reply padding.
- `parseoptions` handles requested IP, lease, type, server id, message, max message, client id, params, and vendor class.
- `miscoptions` supplies mask/router/domain/rootpath and requested server options from NDB; adds Plan 9-specific vendor data for Plan 9 clients.
- Provides option encoding helpers, logging, passive queue-draining read logic, ARP entry insertion, and access to system name.

Important dependencies:
- Uses `db.c` for dynamic leases, `ndb.c` for host/network lookups, `ping.c` for address probing, and `dhcp.h` protocol definitions.

Notable risks/quirks:
- Single-threaded server intentionally stops listening while sleeping in slow modes.
- Uses filesystem lease files for synchronization rather than in-process locks.
- Some BOOTP/vendor behavior is highly Plan 9-specific.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/dhcpd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/dhcpleases.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/dhcpleases.c

`dhcpleases.c` lists active DHCP leases.

Key behavior:
- Opens `binddir`, reads all directory entries, parses each name as an IP, syncs its binding, and prints leases with expiry time if still active.
- Initializes IP formatters and global `now`.
- Defines required globals `blog` and `minlease`.

Important dependencies:
- Uses `syncbinding` and `Binding` from the DHCP server database.

Notable risks/quirks:
- Reuses a stack `Binding` and relies on `syncbinding` populating it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/dhcpleases.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/ndb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/ndb.c

`ndb.c` integrates DHCP server decisions with Plan 9’s network database.

Key behavior:
- `opendb` lazily opens `ndbfile` and periodically reloads when changed.
- `findlifc` finds a local interface whose network contains an IP.
- `forme` tests whether an IP is one of the server’s interface addresses.
- `lookupip` uses `ndbipinfo` to populate `Info` for a given IP, including mask, gateway, fs/auth/tftp servers, boot files, domain, DHCP group, vendor, rootpath, and Ethernet.
- `lookup` maps a BOOTP client to host info, preferring `ciaddr` when valid, otherwise hardware address lookup.
- `lookupinfo`, `lookupserver`, and `lookupname` expose NDB result helpers for option construction.

Important dependencies:
- Uses global `ipifcs`, `now`, `blog`, `debug`, and `ndbfile`.
- Relies on Plan 9 `ndb` APIs.

Notable risks/quirks:
- Comments note Ethernet matching is likely wrong for machines with multiple Ethernet addresses.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/ndb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/ping.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/ping.c

`ping.c` probes whether an IPv4 address is already in use before leasing it.

Key behavior:
- `icmpecho` returns 0 immediately for non-IPv4 addresses.
- Dials ICMP echo service for the target.
- Sends up to three echo requests with message `"dhcp probe"`.
- Uses short alarms to wait for replies.
- Validates echo reply type, sequence, and payload before reporting address is live.

Important dependencies:
- Uses `../icmp.h`, Plan 9 `dial`, alarms, and note handler.

Notable risks/quirks:
- TODO comment notes no IPv6 ping.
- Sequence is derived from pid and time, not random.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/ping.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/testlook.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/testlook.c

`testlook.c` is an older/test utility for NDB IP information lookup.

Key behavior:
- Contains helper functions to find values in NDB tuples, resolve names to IPs, and recursively inspect subnet records.
- A large `ipinfo` implementation is wrapped in `#ifdef foo`, so it is disabled in this file.
- `main` opens NDB, selects lookup by IP-looking argument or Ethernet-looking argument, calls `ipinfo`, and prints address/mask/net/bootfile/Ethernet.

Important dependencies:
- Uses Plan 9 NDB and IP formatting APIs.

Notable risks/quirks:
- As written, it calls `ipinfo` even though its local implementation is disabled; it depends on an external/library `ipinfo` symbol.
- Includes debug `print("%s->", ip)` in subnet recursion.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/testlook.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/testlookup.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/testlookup.c

`testlookup.c` is a test utility for server lookup resolution.

Key behavior:
- Opens NDB and gets `Ipinfo` by IP or Ethernet argument.
- Implements `lookupserver` to find named server attributes directly on the host entry or recursively from subnet entries.
- Resolves server names to IPs, preferring addresses on the same subnet.
- Prints host info, then auth and DNS lookup results.

Important dependencies:
- Uses Plan 9 `ipinfo`, NDB APIs, and IP formatting.

Notable risks/quirks:
- Contains a likely inverted/buggy duplicate-name handling branch in `recursesubnet`.
- Uses global `Ndb *db`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/testlookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/testping.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/testping.c

`testping.c` is a tiny ICMP probe test wrapper.

Key behavior:
- Initializes IP formatters.
- Exits silently without an argument.
- Calls `icmpecho(argv[1])` and prints whether the address answers.

Important dependencies:
- Includes `dat.h` and defines `blog` for `ping.c`.

Notable risks/quirks:
- Passes `argv[1]` directly to `icmpecho`, whose signature expects `uchar *` IP bytes, so this test appears type-inconsistent unless built with a different declaration context.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/testping.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ftpd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ftpd.c

`ftpd.c` is a Plan 9 FTP daemon.

Key behavior:
- Parses FTP commands from stdin, strips CR/LF, handles telnet IAC prefixes and a GatorFTP delimiter quirk, dispatches through `cmdtab`.
- Supports anonymous/none-only modes, debug logging, namespace selection, and auth via Plan 9 challenge/response or noworld login.
- Maintains current directory, transfer type/mode/structure, active/passive data address, restart offset, and transfer child pid.
- Implements login (`USER`/`PASS`), directory navigation (`PWD`, `CWD`, `CDUP`), type/mode/structure, active `PORT`, passive `PASV`, listings (`LIST`, `NLST`), file metadata (`SIZE`, `MDTM`), restart (`REST`), retrieve/store/append/unique store, mkdir/delete, abort, system/help, rename, and `SITE CHMOD`.
- `transfer` runs external commands such as `/bin/tar` through a pipe for directory retrieval.
- `list` implements Unix-style FTP listing output using Plan 9 `Dir` metadata and globbing.
- `retrieve` and `store` perform data connection I/O, converting LF/CRLF for ASCII mode and requiring image mode for high-bit data.
- `abspath` cleans paths, strips shell-special characters, and enforces `.httplogin` access restrictions via cached recursive checks.
- `dialdata` temporarily binds the right network namespace and supports active or passive data connections.

Important dependencies:
- Uses Plan 9 auth, namespace, netconninfo, String, glob, syslog, and process-note APIs.

Notable risks/quirks:
- Plain FTP plus legacy Plan 9 auth behavior; no modern FTP TLS path in this file.
- Anonymous uploads are restricted to `/incoming/`.
- Path sanitization truncates at special characters rather than rejecting the command.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ftpd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ftpfs/file.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ftpfs/file.c

`file.c` implements local caching for `ftpfs` remote files.

Key behavior:
- Maintains up to 128 cached `File` entries.
- `fileget` returns an existing cache for a node or allocates/reuses a clean least-recently-used slot.
- `filefree` closes/removes temp files, frees memory, and detaches cache from the node.
- First 1024 bytes are cached in memory; later content spills to a temp file.
- `fileread` reads from memory or temp file based on offset.
- `filewrite` writes into memory/temp storage, grows cached length, and updates node length.
- `filedirty`, `fileclean`, and `fileisdirty` track writeback state.
- `uncachedir` frees clean temp-backed child caches to limit temp file count.

Important dependencies:
- Uses `Node` from `ftpfs.h` and `uncache`/`seterr`.

Notable risks/quirks:
- Temp files are created with `mktemp` and ORCLOSE.
- Only clean files can be evicted automatically.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ftpfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ftpfs/ftpfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ftpfs/ftpfs.c

`ftpfs.c` exposes a remote FTP server as a local 9P filesystem.

Key behavior:
- Parses options for mount root, password, mount point, NLST mode, extension suffix, TLS flag, OS type override, root path, quiet mode, key spec, and keepalive.
- Connects/logs into FTP server via protocol functions, builds remote tree, then forks a 9P server and mounts it.
- Maintains active fids mapped to `Node` path tree entries.
- Implements 9P handlers for version, attach, walk, open, create, read, write, clunk, remove, stat, and wstat/auth stubs.
- `rwalk` traverses cached/remote paths, supports `.flush.ftpfs`, handles TOPS/VM/VMS top-level quirks, and probes unknown paths by attempting `changedir`.
- `ropen` caches directories with `readdir` and files with `readfile`; `rcreate` creates dirs remotely or marks files dirty.
- `rread` serializes directory entries or reads cached file content.
- `rwrite` writes to local cache and marks dirty.
- `rclunk` writes dirty files back via `createfile`.
- Tree helpers manage `Node` creation, path extension, cache invalidation, special top-level directories, and symlink type fixing.

Important dependencies:
- Uses FTP protocol functions declared in `ftpfs.h` and caching functions from `file.c`.

Notable risks/quirks:
- `-t` sets `usetls`, but TLS behavior depends on protocol-side implementation not in this file.
- `rwstat` and `rauth` are unimplemented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ftpfs/ftpfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ftpfs/ftpfs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ftpfs/ftpfs.h

`ftpfs.h` defines shared structures and APIs for the FTP-backed 9P filesystem.

Key contents:
- Declares opaque `File`, tree `Node`, and remote OS descriptor `OS`.
- `Node` mirrors the remote directory tree with remote name, Plan 9 `Dir`, parent/sibling/child links, cache pointer, depth, open count, and directory-type uncertainty.
- Enumerates remote OS kinds: Unix, Tops, Plan9, VM, VMS, MVS, NetWare, OS/2, TSO, NT, Unknown.
- Declares temp-file cache API, FTP protocol API, and miscellaneous tree/cache helpers.
- Exposes globals such as `remdir`, `remroot`, `os`, `debug`, `usenlst`, `nosuchfile`, `ext`, `defos`, `quiet`, `user`, and `net`.
- Defines cache/validity macros using fields in `Dir`.

Important dependencies:
- Included by `ftpfs.c`, `file.c`, and protocol implementation files outside this group.

Notable risks/quirks:
- Cache and validity state are encoded into `Dir.type`, `Dir.atime`, and `Dir.dev`, which are normally filesystem metadata fields.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ftpfs/ftpfs.h -->