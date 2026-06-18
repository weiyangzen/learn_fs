# Group Research: group_1619_plan9_sources_os_plan9_plan9_sys_src_cmd_tcs_tcs_c_sources_os_plan9_b9650b8b6b5e

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/tcs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/tcs.c

Main driver and central charset registry for Plan 9 `tcs`, a text character-set converter.

Key responsibilities:
- Parses `-c`, `-f`, `-l`, `-s`, `-t`, and `-v`.
- Selects input and output converters through `conv()`.
- Reads stdin or named files, then dispatches to table-based or function-based input conversion.
- Maintains global conversion accounting: input bytes, output bytes, runes, and errors.
- Implements UTF-16/native, UTF-16BE, UTF-16LE input and output helpers.
- Implements generic 8-bit table input and table output, including reverse-map construction.
- Defines built-in maps for ASCII, legacy MS-DOS variants, and the `convert[]` registry covering ISO-8859, JIS, Big5, GB, Korean, UTF, Unicode, Windows code pages, Tamil TUNE, Cyrillic variants, HTML, and aliases.

Important behavior:
- `clean` drops unmappable or malformed input; otherwise bad data maps to `BADMAP` or `Runeerror`.
- `squawk` controls diagnostics, while verbose mode forces diagnostics and prints counts.
- UTF-16 native mode handles BOM and byte swapping; BE/LE modes force byte order.
- Table output rebuilds the reverse Unicode-to-byte table on each call.

Notable risks:
- Many converter implementations are referenced externally, so the registry is a hard compatibility surface.
- Table output assumes `NRUNE` indexing covers all mapped runes.
- Native `unicode_out()` writes host-endian `Rune` values and a BOM, matching historical Plan 9 assumptions rather than modern UTF-16 portability expectations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/tcs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/tune.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/tune.c

Tamil TUNE encoding converter for `tcs`.

Key responsibilities:
- Defines mapping tables from Unicode Tamil vowels, consonants, virama/vowel marks, and special forms to TUNE private-use code points.
- Provides lookup helpers for TUNE-to-Unicode, Unicode-to-TUNE, and mark-index lookup.
- `tune_in()` reads UTF runes with `Bgetrune`, converts TUNE private-use glyphs into Unicode Tamil sequences, and passes output to the selected converter.
- `tune_out()` is a state machine that combines Tamil base characters and following marks into TUNE glyphs.

Important behavior:
- Handles special Tamil ligature-like sequences such as ksha and shri.
- Handles composite vowel signs by delaying emission until enough context is seen.
- Leaves non-TUNE runes unchanged, except unknown TUNE private-use code points are diagnosed or cleaned.

Notable risks:
- `tune_out()` preserves state across calls and must receive a zero-length flush to emit a pending glyph.
- It uses fixed `obuf` inherited from the `tcs` core; output expansion depends on the shared batch size.
- Many mappings are encoded as literal private-use values, so behavior is table-sensitive and hard to infer without the font/encoding convention.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/tune.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/utf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/utf.c

UTF-8 and historical UTF-1 conversion support for `tcs`.

Key responsibilities:
- `utf_in()` reads byte streams, preserves incomplete tails between reads, validates UTF-8, and emits runes.
- `utf_out()` emits runes as UTF-8.
- `isoutf_in()` and `isoutf_out()` implement ISO 10646 Annex A UTF-1 style conversion.
- `isochartorune()`, `runetoisoutf()`, and `fullisorune()` implement UTF-1 decoding, encoding, and completeness checks.
- `our_wctomb()` and `our_mbtowc()` implement portable UTF-8 encode/decode without relying on platform `wchar_t`.

Important behavior:
- UTF-8 validation rejects bad continuation bytes and overlong encodings.
- Supports old 1 to 6 byte UTF-8 form, reflecting historical FSS-UTF rather than current Unicode scalar-value limits.
- Bad input increments `nerrors`; with `clean`, bad bytes are skipped.

Notable risks:
- Six-byte UTF-8 support is obsolete by modern UTF-8 rules.
- `utf_in()` counts consumed bytes, not necessarily total bytes read until tail handling completes.
- UTF-1 code is compatibility-oriented and assumes the historical encoding ranges and escape tables.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/utf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tee.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tee.c

Plan 9 `tee` implementation.

Key responsibilities:
- Parses `-a`, `-i`, and ignored legacy `-u`.
- Opens or creates each output file, appending when `-a` is set.
- Always includes stdout as the final output target.
- Copies stdin to all open outputs using an 8192-byte buffer.
- Installs a note handler for `-i` that ignores interrupt notes.

Notable behavior:
- Write errors are ignored after opening; the loop exits only on read EOF or read error.
- Append mode opens existing files write-only and seeks to end, otherwise creates them.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tee.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/telco/telco.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/telco/telco.c

A user-level 9P file server that exposes modem devices under `/net/telco` for data and fax use.

Key responsibilities:
- Publishes `/srv/telco`, mounts itself under `/net`, and serves a hierarchy containing `telco`, `clone`, per-modem directories, `data`, and `ctl`.
- Tracks Fids, queued read requests, modem devices, circular receive buffers, ownership, and permissions.
- Implements 9P handlers for version, attach, walk, open, read, write, clunk, stat, and wstat.
- Treats writes to `ctl` beginning with `connect ` as dial requests; other control writes pass through to the serial device control file.
- Monitors modem input in per-device background processes, buffering incoming bytes and auto-answering RING events when enabled.
- Detects modem type/speed, applies Hayes-style commands, configures data or fax class, dials numbers, receives calls, and starts service programs.
- Supports modem-specific command tables for Rockwell, AT&T, MultiTech, and Vocal variants.

Important behavior:
- The filesystem uses simple permission emulation rather than reading `/adm/users`.
- `clone` picks a free modem and redirects the opened fid to that modem's `ctl`.
- `data` reads can be deferred by queuing a `Request`; `serve()` replies later when monitor input arrives.
- Incoming data calls exec `/bin/service/telcodata`; fax calls exec `/bin/service/telcofax`.
- `onhook()` toggles serial control lines and reinitializes the modem for fax-capable answering.

Notable risks:
- `serve()` compares `r->count` to `sizeof(buf)`, where `buf` is a pointer, so large reads can be truncated to pointer size.
- The receiver child passes `dev->t->name` instead of `d->t->name`, which likely reports the first device's modem type.
- Protocol, modem command timing, circular-buffer state, and 9P reply ordering are tightly coupled.
- `rflush()` removes queued reads but does not appear to send an explicit flushed read response for a removed request.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/telco/telco.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/telco/telcodata -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/telco/telcodata

Small rc service script for incoming data calls.

Key behavior:
- Prints a message identifying the line as the incoming fax line.
- Asks callers not to make data calls to it.

Notable context:
- `telco.c` execs this as `/bin/service/telcodata` when an answered call appears to be a data call.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/telco/telcodata -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/telco/telcofax -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/telco/telcofax

Small rc service script for incoming fax calls.

Key behavior:
- Runs `/bin/aux/faxreceive`.

Notable context:
- `telco.c` execs this as `/bin/service/telcofax` after detecting a fax connection response.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/telco/telcofax -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/test.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/test.c

Plan 9 implementation of POSIX `test` and `[`, with Plan 9 file-mode extensions.

Key responsibilities:
- Parses recursive expressions with precedence for `-o`, `-a`, `!`, and parentheses.
- Implements string tests, integer comparisons, file existence/access tests, type tests, tty tests, and timestamp comparisons.
- Adds Plan 9 tests `-A` append-only, `-L` exclusive-use, and `-T` temporary.
- Uses `dirstat`, `dirfstat`, `access`, and Plan 9 mode bits.

Important behavior:
- `[` mode requires the final argument to be `]`.
- `-t` defaults to fd 1 if no fd argument is provided.
- `-older` accepts absolute or relative time syntax with suffixes `y`, `M`, `d`, `h`, `m`, `s`.
- `-ot` and `-nt` are implemented by reversed helper calls so the final semantics match shell expectations.

Notable risks:
- Some POSIX primaries (`-c`, `-b`, `-u`, `-g`) are present but always return false.
- The post-parse unexpected-token check is disabled because short-circuit operators may leave unconsumed arguments.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/time.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/time.c

Plan 9 `time` command.

Key responsibilities:
- Forks and execs the requested command, falling back to `/bin/<cmd>` for relative simple names.
- Waits for the child, retrying wait on interrupt notes.
- Prints user, system, and real time from `Waitmsg->time[]`.
- Echoes up to the first few command arguments in the timing line.
- Includes child exit status text when present.
- Ignores interrupt notes in the parent through `notifyf()`.

Notable behavior:
- Output is written to stderr.
- The parent exits with the child's wait message.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/time.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tlsclient.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tlsclient.c

Simple TLS client wrapper around a dialed network connection.

Key responsibilities:
- Parses optional trusted thumbprint file `-t` and exclusion file `-x`.
- Dials the supplied Plan 9 dialstring.
- Upgrades the connection with `tlsClient`.
- Optionally verifies the server certificate SHA-1 thumbprint.
- Forks bidirectional copy loops between stdin/stdout and the TLS fd.
- Posts a note to the process group when one direction finishes.

Notable behavior:
- `-x` without `-t` is rejected.
- Verification requires the server to provide a certificate.
- Uses Plan 9 libsec thumbprint handling rather than a full PKI validation path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tlsclient.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tlssrv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tlssrv.c

TLS server wrapper that serves TLS on fd 1 and connects cleartext to stdin/stdout or a child command.

Key responsibilities:
- Parses certificate `-c`, debug `-D`, syslog name `-l`, and remote-system label `-r`.
- Reads a PEM certificate chain and passes it to `tlsServer`.
- Optionally traces libsec TLS messages through `reporter`.
- Optional `-D -D` style dumping can hex-dump traffic through a pipe wrapper.
- If a command is supplied, forks it with stdin/stdout connected to a pipe.
- Runs bidirectional cleartext-to-TLS copy loops and tears down the process group on EOF or error.

Notable risks:
- `xfer()` forks and returns in the child, with the parent doing copy work; this is subtle and easy to misread.
- `death()` repeatedly posts notes to the current process group and exits, so shutdown is intentionally broad.
- In no-command mode, cleartext fd 0 and TLS fd 1 assumptions are central to correct use.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tlssrv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/touch.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/touch.c

Plan 9 `touch` implementation.

Key responsibilities:
- Parses `-c` no-create and `-t time`.
- Uses current time by default, or an integer timestamp from `-t`.
- Updates file mtime through `dirwstat`.
- Creates missing files unless `-c` is set.
- Applies the selected mtime to newly created files via `dirfwstat`.

Notable behavior:
- Reports per-file errors and exits with `"touch"` if any file failed.
- `touch()` lacks an explicit return type in the old C style, effectively returning int.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/touch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tprof.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tprof.c

Per-function profiler report tool for Plan 9 process profile data.

Key responsibilities:
- Accepts `pid` and optional binary path.
- Reads symbols from `/proc/<pid>/text` or the supplied binary using libmach.
- Reads raw profiling counters from `/proc/<pid>/profile`.
- Swaps counter endianness using selected machine data.
- Maps PC bucket counts to text symbols using page-aligned text base and `PCRES`.
- Accumulates time per function, sorts by count, and prints milliseconds, percentage, and symbol.

Important behavior:
- `data[0]` and `data[1]` are used to compute total and delta.
- If total count is zero, exits without a report.
- Requires text symbols; errors if none are found.

Notable risks:
- Percentage uses `delta = data[0] - data[1]`, so malformed profile data can distort output.
- Function ranges are inferred from symbol order and PC bucket offsets.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tprof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tr.c

Unicode-aware Plan 9 `tr` implementation.

Key responsibilities:
- Parses `-c`, `-d`, and `-s`.
- Parses rune specifications, escapes, hex escapes, octal escapes, and ranges.
- Implements deletion, squeezing, transliteration, and complement transliteration.
- Uses bitsets sized for `Runemax+1`.
- Reads and writes UTF-8 runes with buffering.

Important behavior:
- Ranges are expanded by `canon()` using parser state.
- Repeated destination exhaustion uses the last destination rune.
- `-s` squeezes runs of output runes found in the destination set.
- `-c` builds a complement mapping up to the highest rune seen in either specification.

Notable risks:
- Complement transliteration maps runes above the computed high-water mark to the last destination rune.
- Large ranges can allocate large mapping arrays.
- Ambiguous repeated source mappings in transliteration are rejected.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/trace.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/trace.c

Graphical scheduler trace viewer for Plan 9 process trace events.

Key responsibilities:
- Optionally enables tracing on supplied process ids by writing `trace 1` to `/proc/<pid>/ctl`.
- Reads binary `Traceevent` records from `/proc/trace` or `-d profdev`.
- Maintains per-task event lists and runtime statistics.
- Opens a draw window, initializes mouse and keyboard controls, and renders a scrolling timeline.
- Displays run/EDF intervals, releases, deadlines, admits, expels, yields, slices, user events, and interrupt markers.
- Supports keyboard controls for reset, pause, zoom in/out, quit, and verbose toggling.
- Supports `-w` new window and `-t triggerproc` pause-on-trigger behavior.

Important behavior:
- Time scales range from sub-millisecond through seconds.
- Per-task height is recalculated on resize unless a fixed new window is managed.
- Runtime intervals are closed when sleep, yield, ready, or slice events arrive.
- Task death frees its event list and compacts the task array.

Notable risks:
- Event history grows with `realloc` per event and is pruned only during redraw.
- Drawing and event ingestion share global mutable state.
- Uses raw binary trace records, so structure ABI must match `trace.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/dwbinit.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/dwbinit.c

DWB pathname initialization helper used by troff and related document tools.

Key responsibilities:
- Finds the DWB home directory through `DWBhome()`.
- Reads a simple config file for `DWBENV=...`, falling back to an environment variable and then compiled default.
- Rewrites configured pointer paths and fixed-size array paths to be rooted under the current DWB home.
- Provides optional debug dumps through `DWBDEBUG=ON`.
- Provides `DWBprefix()` to replace a leading DWB prefix token in an already stored path.

Important behavior:
- The config parser is intentionally simple and only recognizes variable assignments at the first non-space token.
- Pointer path entries are newly allocated; array entries must have enough room or the program exits.
- Double leading slashes in the home path are collapsed by advancing the returned pointer.

Notable risks:
- `DWBhome()` may return malloc-owned, environment-owned, or static strings depending on path source.
- `DWBinit()` does not free old pointer values when replacing them.
- Absolute paths are still rewritten; debug only warns about them.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/dwbinit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/dwbinit.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/dwbinit.h

Header for DWB pathname initialization.

Key contents:
- Defines `dwbinit`, which describes either a pointer pathname or a fixed-size array pathname.
- Declares `DWBinit()`, `DWBhome()`, and `DWBprefix()`.

Important behavior:
- For pointer entries, `address` is set and `value` is null.
- For array entries, `value` is set and `length` must be the array capacity.
- The list is terminated by an entry with both `address` and `value` null.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/dwbinit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/ext.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/ext.h

Global external declarations for the troff/nroff program.

Key responsibilities:
- Declares shared state for input stacks, buffers, page ranges, diversions, environments, number registers, macro state, output state, fonts, terminal tables, special character ids, and DWB path strings.
- Exposes the central indirect function pointers that switch behavior between troff and nroff back ends.
- Bridges definitions from files such as `ni.c`, `n1.c`, `n2.c`, `n3.c`, `n4.c`, `n5.c`, `n7.c`, `n10.c`, and troff-specific `t*.c` files.

Important behavior:
- This header is a shared-state contract, not an abstraction boundary.
- Many globals are updated by multiple subsystems during input parsing, layout, and output.
- Historical names and declarations include state used only by troff or only by nroff.

Notable risks:
- Type and storage mismatches across old C files would produce subtle corruption.
- The program architecture relies heavily on global mutable state and indirect function variables.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/ext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/fns.h

Function prototype hub for troff/nroff.

Key responsibilities:
- Declares prototypes for initialization, input, control dispatch, output, macro/string storage, number registers, request handlers, text layout, hyphenation, drawing, device output, font loading, and nroff-specific routines.
- Declares the indirect function pointers selected by troff or nroff initialization.
- Groups functions by historical source modules (`c1.c`, `c3.c`, etc.) even though this tree uses `n*.c` and `t*.c` names.

Important behavior:
- Includes prototypes for both troff and nroff implementations, including many functions not in this group.
- Carries legacy declarations for non-standard C library functions used by the program.
- Acts as the compile-time connection point for the whole formatter.

Notable risks:
- Some declarations preserve old K&R-era assumptions and names.
- Several prototypes correspond to functions whose implementations are outside this grouped batch, so changing signatures here has broad impact.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/hytab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/hytab.c

Static hyphenation digram scoring tables for troff.

Key contents:
- Defines `Uchar`.
- Provides 26 by 13 packed scoring tables used by `n8.c`: `bxh`, `hxx`, `bxxh`, `xhx`, and `xxh`.

Important behavior:
- Scores are packed as two 4-bit values per byte for letter-pair lookup.
- `dilook()` in `n8.c` selects the high or low nibble based on the second letter.

Notable risks:
- The tables assume 26-letter ASCII alphabetic indexing.
- Values are opaque heuristic data; correctness depends on preserving exact bytes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/hytab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/n1.c

Troff/nroff startup, option parsing, main input loop, input stack management, and escape interpretation.

Key responsibilities:
- Determines troff versus nroff mode, initializes DWB paths, macro/register namespaces, device state, environments, and buffers.
- Parses options for macro packages, page ranges, device/font directories, initial registers, tracing, quiet mode, ASCII mode, and nroff forcing.
- Runs the main loop, dispatching requests through `control()` or sending normal input to `text()`.
- Implements `getch()`, `getch0()`, `getach()`, pushback, include-file handling, `.nx`, `.so`, `.cf`, `.lf`, `.sy`, and page-list parsing.
- Interprets escape sequences for number registers, strings, arguments, fonts, sizes, motions, special characters, drawing helpers, fields, comments, copy-through, and repeat counts.

Important behavior:
- `DWBinit()` rewrites font, terminal, hyphenation, home, and macro directory paths before initialization.
- Request lookup goes through the dynamically hash-backed macro/request table.
- Macro invocation collects arguments and pushes a new input frame.
- `getch()` handles both copy mode and normal mode, which changes how escapes are interpreted.

Notable risks:
- The main loop depends on `setjmp/longjmp` exit/restart flow.
- Input state spans pushback buffers, macro storage offsets, file include stacks, and global flags.
- `getch0()` contains a comment noting an EOF-test bug workaround with `if (nx || 1)`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n10.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/n10.c

Nroff terminal/device interface.

Key responsibilities:
- Reads nroff terminal tables and character-width/output definitions.
- Initializes nroff function pointers for motion, width, font, size, output, and pause behavior.
- Sets default nroff environment values: page length, offsets, fonts, tabs, line length, spacing, hyphenation, and ASCII output.
- Installs special character names.
- Buffers output lines and renders terminal control sequences for movement, bold, italic/underline, overstrikes, plot mode, and multibyte characters.
- Restores terminal state at completion.

Important behavior:
- `parse()` decodes terminal table escapes and tags output strings by type.
- `getnrfont()` builds the nroff character-width table and output strings.
- `n_ptout()` delays output until newline, then `move()` and `ptout1()` emit terminal actions.
- `move()` converts accumulated horizontal and vertical movement into terminal control strings, spaces, backspaces, tabs, or plot-mode moves.

Notable risks:
- Terminal table parsing assumes a strict file format.
- The output path mixes physical terminal movement with logical troff motions.
- Some comments call out poorly understood behavior for large/special characters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n10.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/n2.c

Troff/nroff character output, flushing, piping, and program termination.

Key responsibilities:
- `pchar()` and `pchar1()` route internal `Tchar` values to diversions, transparent output, ASCII output, troff output, or nroff output.
- Maintains output buffering through `obuf` and `obufp`.
- Converts internal special characters to best-effort ASCII when needed.
- Starts pipe output for `.pi`.
- Implements `.ex`, `done*()` cleanup stages, `edone()`, trailers, flushing, and final exit.

Important behavior:
- Diversion output is written with `wbf()` instead of sent to the device.
- `XON`/`XOFF` copy-through affects whether nroff emits content.
- `flusho()` starts the `.pi` pipe lazily when output first appears.
- Termination can trigger end macros, page ejection, output trailers, nroff restoration, and pipe close.

Notable risks:
- Exit flow uses global flags and `longjmp`.
- `Pipe` supports accumulated command strings but has manual growth logic.
- Output behavior depends heavily on `dip`, `tflg`, `print`, `ascii`, `TROFF`, and `xon`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n3.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/n3.c

Macro, string, diversion, input-frame, and block-storage subsystem for troff.

Key responsibilities:
- Builds and hashes the macro/request namespace.
- Implements `.de`, `.am`, `.ds`, `.as`, `.ig`, `.rm`, `.rn`, `.di`, `.da`, `.dt`, `.tl`, `.pc`, `.pm`, and `.gd`.
- Stores macro/string/diversion bodies in dynamically allocated fixed-size blocks.
- Allocates, frees, writes, and reads block-chain offsets.
- Pushes and pops macro/string input frames.
- Collects macro arguments and expands `$1` through `$9`.
- Tracks diversion sizes and diversion traps.

Important behavior:
- Built-in request table entries are copied into `contabp`, then dynamic macro/string slots are appended.
- Block zero is deliberately kept unusable because offset zero is overloaded.
- Appending to existing macros uses `apptr` and `emx`.
- Diversions are nested through the `d[]` stack, with `dip` selecting current output target.

Notable risks:
- Macro argument storage is placed in the same manually managed stack area as input frames.
- Comments call out design issues around offset zero and storage allocation.
- Diversion self-invocation and removal during definition are explicitly guarded because they can corrupt state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n4.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/n4.c

Number registers, numeric expression parsing, formatting, and arithmetic for troff.

Key responsibilities:
- Implements number-register expansion via `\n`, including predefined dot registers.
- Maintains dynamic hashed number-register namespace.
- Implements `.nr`, `.rr`, `.af`, and `\g`.
- Formats numbers as decimal, roman, alphabetic, and zero-padded decimal.
- Parses arithmetic and logical numeric expressions with scaling units.
- Handles horizontal, vertical, and default numeric parsing through `hnumb`, `vnumb`, and `inumb`.
- Quantizes values to output resolution.

Important behavior:
- Dot registers expose current formatter state such as point size, font, page length, indent, line length, current file, tab stops, and available registers.
- Numeric expressions support `+`, `-`, `*`, `/`, `%`, `&`, `:`, comparisons, and parentheses.
- Units include `u`, `v`, `m`, `n`, `p`, `i`, `c`, and `P`.
- Absolute forms using `|` are relative to horizontal position or vertical line position.

Notable risks:
- Numeric parsing uses global scaling flags (`dfact`, `dfactd`, `res`, `vflag`, `noscale`) that must be restored correctly.
- Division by zero reports a warning and resets the accumulator.
- Register lookup creates registers on demand, so accidental names consume namespace.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n5.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/n5.c

Miscellaneous troff request handlers and formatter state controls.

Key responsibilities:
- Handles adjustment/fill/no-fill, spacing, indents, line lengths, title lengths, page offset/length, page numbers, traps, breaks, and centering.
- Handles terminal messages, file messages, pipe flushing, environment switching, conditionals, reads from terminal, escape-character control, tabs, translation, underlining, input traps, margin characters, marks, saved vertical space, and line numbering.
- Implements `.if`, `.ie`, `.el` block skipping and string/numeric comparisons.
- Implements `.rd` by pushing a special input source that reads stdin.
- Contains stubbed nroff tty save/restore/echo functions.

Important behavior:
- Conditional false branches are skipped by `eatblk()` with nested `\{...\}` handling.
- `.tm`, `.fm`, and `.ab` reconstruct printable strings for diagnostics or files.
- `.ev` copies and switches formatter environments.
- `.ta` supports left, center, and right tab stops.
- `.nm` configures line numbering using several numeric parameters and current character bits.

Notable risks:
- Many handlers temporarily suppress numeric warnings by changing global trace flags.
- File message caching in `.fm` is capped at 15 streams.
- TTY handling is intentionally removed but call sites remain.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n6.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/n6.c

Nroff width, font, size, and motion functions.

Key responsibilities:
- Implements nroff character width calculation using terminal font width data.
- Provides nroff-specific wrappers or simplified behavior for special characters and absolute characters.
- Finds fonts by numeric position or font label.
- Maintains current font bits and space width.
- Parses and discards point-size and height/slant requests that nroff does not truly render.
- Implements nroff font switching, width measurement, horizontal/vertical motions, half-line motions, font-position mapping, bold settings, vertical spacing, and extra line space.

Important behavior:
- Motions are encoded as internal `Tchar` motion cookies.
- Width of unavailable font characters falls back to terminal character width.
- `n_setwd()` computes width and vertical extents while restoring saved font/size state.
- `n_xlss()` encodes extra line space as `HX` followed by a vertical motion.

Notable risks:
- This file intentionally ignores or simplifies several troff graphical attributes for nroff.
- It depends on `t_setch()` and `t_setabs()` from troff-specific character lookup code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n7.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/n7.c

Text collection, line breaking, filling, justification, line output, page traps, and hyphenation integration.

Key responsibilities:
- Builds words and output lines from input characters.
- Implements filled and no-fill text modes.
- Breaks lines with adjustment, centering, indentation, margin characters, line numbering, and line spacing.
- Emits newlines, handles page boundaries, page numbers, output range selection, traps, and ejection.
- Moves words into lines, tries hyphenation when needed, and inserts discretionary hyphens.
- Grows line and word buffers dynamically.
- Handles nroff underlining/cuu behavior through `gettch()`.

Important behavior:
- `tbreak()` is the core line finalization routine.
- `newline()` updates diversion or main page vertical position and triggers traps.
- `movword()` asks `hyphen()` for hyphenation points when a word overflows.
- `getword()` suppresses hyphenation for numeric-looking words.
- `chkpn()` implements page range printing controls.

Notable risks:
- The fill algorithm depends on many shared globals: `nel`, `ne`, `nwd`, `pendw`, `linep`, `wordp`, traps, diversions, and hyphen pointers.
- Buffer growth carefully rebases internal pointers; mistakes here would corrupt layout.
- Page ejection loops until the vertical position returns to top or a trap fires.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n7.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n8.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/n8.c

Hyphenation engine for troff.

Key responsibilities:
- Identifies alphabetic word spans inside buffered words.
- Applies hyphenation exceptions from `.hw`.
- Supports a TeX-pattern hyphenation path using `hyphen.tex`.
- Falls back to suffix rules and digram scoring.
- Provides `.ha` algorithm selection and `.ht` threshold selection.
- Stores hyphenation exception words with embedded hyphen-point bits.

Important behavior:
- Words shorter than four alphabetic characters are not hyphenated.
- Hyphenation attempts proceed in order: exceptions, TeX patterns, suffix rules, digram heuristic.
- TeX pattern loading is lazy and cached, with failure cached as disabled.
- `texit()` builds odd/even hyphenation weights from matched patterns.
- Digram scoring uses the packed tables from `hytab.c`.

Notable risks:
- Much of the non-TeX logic assumes 7-bit ASCII letters.
- TeX pattern storage is a fixed 50000-byte array.
- The parser expects a narrow `hyphen.tex` format and is documented as not robust across variants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n8.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n9.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/n9.c

Miscellaneous escape helpers for zero-width characters, rules, overstrikes, brackets, vertical lines, drawing functions, and fields.

Key responsibilities:
- Implements `\z`, `\l`, `\o`, `\b`, `\L`, `\D`, `.fc`, tabs, leaders, and field padding.
- Builds internal pushback sequences for horizontal rules, overstrikes, brackets, vertical lines, and drawing functions.
- Encodes troff drawing functions as internal `DRAWFCN` cookies and motion pairs.
- Implements field filling for plain, center, right, and padded fields.
- Temporarily rewires special-character flags in `gchtab` while parsing fields.

Important behavior:
- Horizontal and vertical rules are constructed from repeated characters and motions.
- Overstrike sorts glyphs by width to center them around a shared position.
- Drawing supports line, circle, ellipse, arc, spline-like functions, and built-up characters.
- Field expansion restores tab/leader/field state before returning.

Notable risks:
- Most routines operate by pushing synthetic `Tchar` sequences back into the input stream.
- Drawing buffers have fixed limits and clamp motion deltas to `MAXMOT`.
- Field parsing is stateful and temporarily disables normal tab/leader recognition.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/n9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/ni.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/ni.c

Global data definitions and built-in request table for troff/nroff.

Key responsibilities:
- Defines terminal/font directory strings, default device name, initial number registers, page-range globals, output globals, input globals, environment arrays, diversion arrays, special-character ids, and indirect function pointers.
- Defines the built-in `contab[]` mapping request names to handler functions.
- Provides the initial environment `env[0]`.
- Defines special-name mappings such as hyphen, em dash, rule, minus, ligatures, accents, underline, root extender, box rule, and dagger.
- Defines global state for macro stacks, pushback, traps, line layout, hyphenation, output motion, and device mode.

Important behavior:
- Request names are two-character packed names created by `PAIR`.
- `mnspace()` copies `contab[]` into dynamic `contabp` during initialization.
- The indirect function pointers are assigned by troff or nroff device initialization.

Notable risks:
- This is the storage anchor for most globals declared in `ext.h`.
- Any request table change affects parser dispatch and macro-name collision behavior.
- The program depends on the initial environment values matching historical troff defaults.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/ni.c -->