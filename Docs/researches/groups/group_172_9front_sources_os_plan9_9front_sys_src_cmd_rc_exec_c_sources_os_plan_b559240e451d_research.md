# Group Research: group_172_9front_sources_os_plan9_9front_sys_src_cmd_rc_exec_c_sources_os_plan_b559240e451d

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/exec.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/exec.c

Core interpreter and entry point for `rc`. It initializes flags, traps, variables, bootstrap code, then dispatches bytecode through `runq`.

Defines the runtime thread stack, word/list stack helpers, redirection stack helpers, status handling, error reporting, and most opcode handlers: assignment, variable expansion, subscripting, glob invocation, conditionals, loops, functions, redirections, here-doc execution, parsing loop, and shell exit/trap behavior.

Important contracts: `thread` frames own copied code vectors; `start()` pushes frames; `Xreturn()` unwinds redirections and frames; `Xrdcmds()` invokes `yyparse()` and starts compiled `codebuf`; redirections are stacked in reverse and later applied by `simple.c`.

Filesystem relevance: implements shell-level file descriptor redirection semantics, temporary here-doc files under `/tmp`, pipe wait status propagation, and command source location reporting.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/exec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/exec.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/exec.h

Interpreter interface header for `rc`. Declares opcode entry points, stack/value helpers, redirection types, thread state, builtin dispatch, and status helpers.

Defines `word`, `list`, `redir`, and `thread`, including code pointer, pc, argv stack, redirection stack, local variables, lexer, child pid, saved status, and return frame.

The header is the shared contract between compiler/parser output and runtime execution, especially the `X*` opcode functions used in generated `code` vectors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/exec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/fns.h

Shared prototype header for `rc`. It centralizes platform abstraction calls, allocator helpers, parser/compiler hooks, glob/match helpers, I/O formatting helpers, variable/environment initialization, trap dispatch, and command execution helpers.

Key abstraction boundary: generic shell code calls exported names such as `Open`, `Creat`, `Fork`, `Waitfor`, `Opendir`, `Readdir`, `Errstr`, and `Exec`; `plan9.c` and `unix.c` provide platform-specific implementations.

This file documents the shell’s internal module graph without implementation details.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/getflags.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/getflags.c

Small command-line flag parser used by `rc`. It scans bundled single-letter options, supports fixed argument counts through a compact flag specification, records values in global `flag[NFLAG]`, and stops at the first non-option when requested.

It mutates `argv` in place, moving flag arguments toward the end and returning the remaining argc. Duplicate flags, unknown flags, bad flag syntax, and too few arguments are recorded for `usage()`.

`usage()` prints direct low-level errors via `Write(2, ...)`, sets shell status to `bad flags`, then exits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/getflags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/getflags.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/getflags.h

Header for the flag parser. Defines `NFLAG` as 128 and exposes `flag`, `cmdname`, `flagset`, and `getflags()`.

Used by `exec.c`, `lex.c`, platform files, and other `rc` modules to test shell options.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/getflags.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/glob.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/glob.c

Implements `rc` glob expansion and pattern matching. Uses an internal `GLOB` marker inserted by the lexer before glob metacharacters.

`globword()` replaces a word in-place with sorted filesystem matches; unmatched words are deglobbed literally. `globdir()` recursively opens directories and filters entries, with Plan 9-specific directory-only filtering for intermediate slash components.

`match()` is UTF-aware and supports `*`, `?`, character classes/ranges, complement classes with `~`, and stop characters such as `/`. It avoids matching `.` and `..` unless the pattern starts with `.`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/glob.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/havefork.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/havefork.c

Implements fork-dependent opcodes for systems with process creation: async blocks, pipelines, backquote command substitution, pipefd forms, subshells, and external command fork/exec.

Maintains a dynamic `waitpids` list so `Waitfor()` only consumes children owned by this shell context. Child paths clear the wait list before running nested code.

Filesystem/process relevance: creates OS pipes, maps them into shell redirection stacks, returns `/fd/N` pipe names for pipefd expressions, and coordinates parent-side wait/status handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/havefork.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/here.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/here.c

Handles here-document collection and substitution. `heredoc()` queues parser redirection nodes; `readhere()` consumes queued here-doc bodies after a complete parsed line.

`readhere1()` prompts as needed, tracks lexer line numbers, rejects NUL bytes, and stops when the tag line matches. `psubst()` performs `$name`, `$n`, and `$$` substitution for unquoted here-doc bodies, preserving multibyte sequences carefully.

The executor later writes bodies into temporary files in `exec.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/here.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/io.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/io.c

Buffered I/O and minimal formatter for `rc`. Supports file-backed buffers and expandable in-memory string buffers.

Provides `pfmt()`/`vpfmt()` with shell-specific verbs for commands, words, values, quoted strings, pointers, decimal/octal values, and opcode names. Provides `rchr()` and `rstr()` for lexer and command-substitution reads.

`flushio()` either writes pending bytes to an fd or grows memory buffers. Write failures can trigger pending trap delivery.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/io.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/io.h

Defines the `io` buffer structure and declares all `rc` I/O helpers.

The abstraction is deliberately small: fd, buffer pointers, EOF constant, constructors for fd/string/core input, read/write primitives, flushing, closing, and formatted printing hooks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/lex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/lex.c

Lexer for the `rc` grammar. It recognizes words, keywords, comments, quotes, variable forms, operators, pipes, and detailed redirection syntax.

Important behavior: after a word, `(` becomes subscript syntax and adjacent word starts synthesize `^` concatenation. Globbing characters are marked with `GLOB` in token strings. Backslash-newline continues non-comment input.

`yyerror()` reports source file/line and token, consumes to newline/EOF, increments `nerror`, and sets shell status.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/pcmd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/pcmd.c

Pretty-printer for parse trees. `pcmd()` recursively emits textual `rc` syntax for every tree type: pipelines, redirections, functions, loops, conditionals, assignments, backquotes, subshells, lists, and words.

Used for function serialization, debugging, and `whatis`. It deglobs unquoted words for display and quotes quoted words with shell quoting rules.

Also renders here-doc bodies after their redirection syntax.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/pcmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/pfnc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/pfnc.c

Debug printer for bytecode execution. Maps opcode function pointers to human-readable names and prints the current source location, pid, code vector, pc, opcode, and argv stack.

Enabled from the main interpreter when `flag['r']` is set. Useful for tracing compiled `rc` programs at opcode granularity.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/pfnc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/plan9.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/plan9.c

Plan 9-specific runtime backend for `rc`. Defines builtins, default `Rcmain`, fd path prefix, signal names, environment import/export, process creation, wait handling, directory iteration, file operations, and prompts.

Environment variables and functions are synchronized through `/env` and `/env/fn#*`. `Vinit()` imports `/env`; `Updenv()` writes changed variables/functions back.

`Fork()` uses `rfork(RFPROC|RFFDG|RFREND)`. `Waitfor()` handles Plan 9 `Waitmsg` status strings and routes unrelated child statuses to waiting pipeline frames.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/plan9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/rc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/rc.h

Primary shared header for `rc`. Selects Plan 9 vs Unix includes, defines parser depth, core typedefs, parse tree layout, code-vector convention, lexer state, variable structure, glob/UTF helpers, and global state declarations.

Important code-vector convention: `code[0]` is a reference count, `code[1]` is a source-file string, executable bytecode starts at pc 2, and vectors must be copied/freed through `codecopy()`/`codefree()`.

Defines redirection rtypes, variable hash size, token buffer size, pipe end constants, and global UI/runtime variables.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/rc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/simple.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/simple.c

Executes simple commands and builtins. Resolves function calls, explicit `builtin`, builtins, external programs, and optimized tail `exec`.

Contains redirection application, path search, argv construction, `exec`, function invocation, `cd`, `exit`, `shift`, `eval`, dot-source, flag manipulation, `whatis`, and `wait`.

`execcmds()` creates a small code vector around `Xrdcmds` for parsing command streams. `execdot()` opens scripts through `$path`, sets local `$*` and `$0`, and configures interactive/bootstrap/quiet modes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/simple.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/subr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/subr.c

Small utility module for `rc`: checked allocation, strdup, source-location printing, integer-to-ASCII conversion, and panic handling.

`panic()` prints through the shell’s `err` stream and calls the platform `Abort()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/syn.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/syn.y

Yacc grammar for `rc`. Defines command syntax, precedence, compound commands, assignments, redirections, pipelines, conditionals, loops, functions, subshells, backquotes, variable expansion, quoting, concatenation, and word lists.

On a completed line, it reads queued here-docs and compiles the parse tree. Grammar actions build tree nodes through `tree1/tree2/tree3`, attach redirections with `mung*`, and propagate glob markers.

It distinguishes `for(i)` from `for(i in )` with an explicit empty `PAREN` node.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/syn.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/trap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/trap.c

Trap dispatcher for `rc`. Maintains global pending trap counts by signal and total `ntrap`.

`dotrap()` runs pending signal handlers by looking up variables such as `sigint`; if a handler function exists it starts it with a copy of `$*`. In child processes it exits. For unhandled interactive interrupt/quit, it unwinds to the command-reading loop; other unhandled traps exit except ignored `sigwinch`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/tree.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/tree.c

Parse tree allocator and mutator. Uses a free-list of tree nodes and a per-parse `treenodes` list cleared by `freenodes()`.

Provides constructors, child attachment helpers, redirection epilogue attachment, simple-command normalization, function string generation, glob propagation, and token creation.

`simplemung()` wraps argument trees in `SIMPLE`, saves a printable function body string, and pulls redirections up to the command root.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/unix.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/unix.c

Unix portability backend for `rc`. Mirrors the Plan 9 backend with Unix syscalls and environment representation.

Variables become environment strings using `=` and an internal separator for list values; functions are exported as special `#()fn name body` strings. `finit` reads compatible function definitions from `environ`.

Implements Unix signal setup, wait status conversion, `execve`, `fork`, `opendir/readdir`, fd operations, temporary unlink-on-open behavior for here-docs, and tty/prompt handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/unix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/var.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rc/var.c

Variable and keyword table implementation for `rc`. Provides hash function, keyword initialization/lookup, global variable lookup, local-over-global lookup, set, allocation, and free.

Keywords are represented as tokenized tree nodes with `iskw` set. Variables store word-list values and optional function code vectors plus changed flags for environment synchronization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rc/var.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rdbfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rdbfs.c

Remote debugging 9P filesystem. Mounts a synthetic `/proc/<procname>` tree backed by serial debugger commands.

Exposes files like `ctl`, `kregs`, `mem`, `text`, and `status`. Reads/writes to `mem` and `kregs` are sent over the serial port as textual `rADDR`/`wADDR VALUE` commands; `text` proxies a local kernel text file.

Includes a 4-byte memory page cache keyed by address/count to reduce serial traffic, plus `ctl` commands for `kill`, `exit`, `refresh`, and `hashstats`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rdbfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/read.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/read.c

Implementation of the Plan 9 `read` command. Copies requested input from files or stdin to stdout by lines, bytes, or runes.

Options: `-m` reads multiple lines indefinitely, `-n nlines`, `-c nbytes`, and `-r nrunes`. Rune mode preserves whole UTF sequences and warns on partial trailing runes.

Exit status is `eof` only when no data is read before EOF.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/read.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/reform/audio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/reform/audio.c

MNT Reform audio-control filesystem for an I2C codec. Programs codec registers through `#J/i2c3/i2c.1a.data` and exposes synthetic `/dev/audioctl` and `/dev/volume`.

Tracks master DAC, headphone, speaker, volume pairs, output on/off state, sample rate, and 3D setting. Supports reset, speed 44100/48000, 3d percentage, output toggles, and relative/absolute volume changes.

Can run once with `-1` to initialize hardware without mounting the 9P service.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/reform/audio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/reform/pm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/reform/pm.c

MNT Reform power-management filesystem. Exposes `/dev/battery`, `/dev/cputemp`, `/dev/light`, `/dev/kbdoled`, and `/dev/pmctl`.

Controls LCD PWM brightness, keyboard backlight, trackball LEDs, keyboard OLED image upload, CPU temperature sensor setup/readout, LPC battery/firmware/voltage queries over SPI, and poweroff requests.

Uses HID control discovery through `/dev/usb/ctl`, raw HID commands for keyboard/trackball, memory-mapped hardware segments for TMU/PWM/SPI, and a request queue for potentially slow LPC reads with flush support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/reform/pm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/reform/shortcuts.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/reform/shortcuts.c

Keyboard shortcut filter for Reform devices. Reads NUL-delimited keyboard records from stdin and writes filtered records to stdout.

Consumes control-key multimedia runes for brightness, mute, volume, media previous/next/play-pause, writing to `/dev/light`, `/dev/volume`, `/dev/audioctl`, or sending plumber messages.

Unrecognized input is passed through unchanged; records with only consumed shortcut runes are suppressed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/reform/shortcuts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/replica/all.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/replica/all.h

Shared header for replica tools. Includes Plan 9 libraries and declares the database `Entry`/`Db` structures plus shared helpers.

The database is an AVL-indexed map from logical replica path to metadata: server name, uid, gid, mtime, mode, mark, and length.

Also declares memory/string helpers, `unroot()`, and reverse proto traversal.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/replica/all.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/replica/applychanges.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/replica/applychanges.c

Pushes local/client changes to a server tree using a replica client database and proto traversal.

For each proto file, compares client metadata, server metadata, and database metadata to detect create/create, update/remove, update/update, metadata, and removal conflicts. Applies adds, content changes, metadata changes, and deletes when safe.

Supports dry-run/verbose, uid syncing, proto selection, exclusion paths, and path filters. File copy preserves mode, gid, optional uid, and mtime.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/replica/applychanges.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/replica/applylog.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/replica/applylog.c

Applies server change logs to a local replica tree. It reads log records from stdin, compares against local filesystem and client database, detects conflicts, and updates files/database/time cursor.

Handles verbs `d` delete, `a` add, `c` content change, and `m` metadata change. Conflict resolution can prefer server (`-s path`) or client (`-c path`). Path filters intentionally gate filesystem changes while still allowing the replay timestamp to advance only when safe.

Copying uses temp spooling by default, parallel worker processes, remote-file stability checks, optional safe install behavior for binaries, permission fallback, copy-error tracking, and content comparison through temporary snapshots.

Special safety: copies itself to `/tmp/_applylog_*` and re-execs to avoid overwriting the running binary during updates.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/replica/applylog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/replica/compactdb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/replica/compactdb.c

Compacts a replica database by loading it through the AVL-backed database layer and writing one canonical record per live entry to stdout.

This removes append-only tombstones and superseded records while preserving current metadata.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/replica/compactdb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/replica/db.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/replica/db.c

Append-only replica database implementation. Loads records into an AVL tree keyed by logical name, handles tombstone records marked `REMOVED`, and appends insert/remove records back to the backing fd.

Uses a small free-list allocator for `Entry`. Public operations: `opendb`, `finddb`, `markdb`, `insertdb`, and `removedb`.

`markdb()` is used by walkers to identify database entries visited in the current scan.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/replica/db.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/replica/revdump.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/replica/revdump.c

Utility that dumps reverse-proto traversal results. For each enumerated file it prints new path, mode flags, uid, gid, and old path.

Despite the usage string saying `protodump`, the file calls `revrdproto()` and accepts `-r root`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/replica/revdump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/replica/revproto.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/replica/revproto.c

Reverse proto reader/enumerator. Parses proto files, walks a source root, maps paths into an external/rooted namespace, and invokes a callback for each discovered file.

Supports explicit entries, recursive `+`, one-level `*`, uid/gid/mode overrides, old path aliases, environment-variable expansion, indentation-based hierarchy, directory skipping after stat/open failures, and warnings through a callback.

Used by replica tools to enumerate client/server paths while preserving proto-derived metadata.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/replica/revproto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/replica/updatedb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/replica/updatedb.c

Scans a root using a proto file and updates or logs a replica database. Emits change log records for adds, content changes, metadata changes, and deletes.

Options support changes-only mode, log-only mode, proto/root/time/uid overrides, excludes, and path filters. The database mark bit distinguishes visited entries from removals.

Warnings that look like network/I/O failures abort to avoid treating an unavailable tree as mass deletion.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/replica/updatedb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/replica/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/replica/util.c

Shared replica utility code. Provides fatal checked allocation, strdup, atomized string interning, and root-prefix stripping.

The atom table never frees strings and allows interned metadata fields to be reused cheaply across many database entries.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/replica/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/resample.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/resample.c

Image resizer using Plan 9 `memdraw`. Implements separable resampling with a precomputed Kaiser-windowed kernel.

Supports `-x`, `-y`, and compatibility `-a` dimensions, with integer or percentage values. Preserves aspect ratio when only one dimension is supplied.

Handles common byte-per-channel formats directly and converts indexed/packed or alpha-containing images to suitable temporary formats before converting back.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/resample.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/resize.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/resize.c

Simpler image resizer using bilinear interpolation by default and nearest-neighbor with `-n`.

Supports `-x`, `-y`, `-a`, absolute or percentage dimensions, stdin or one image file, and aspect-ratio preservation.

Like `resample.c`, converts unsupported channel formats through byte-per-channel temporary images and writes a Plan 9 memimage to stdout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/resize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rio/dat.h

Central data header for `rio`. Defines qid constants, control message types, window/fid/xfid/filesystem/timer structures, globals, and window operation prototypes.

`Window` combines frame state, images, mouse/keyboard/control channels, text buffer, scroll state, selection, process info, cursor state, labels, and working directory.

The qid layout encodes window id and file id in one path, supporting `/dev` and `/dev/wsys/<id>` file views.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/data.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rio/data.c

Static visual data and color initialization for `rio`. Defines cursor bitmaps for crosshair, box, sight, arrow, query, resize corners/edges, and skull.

`iconinit()` allocates background and UI color images, including reverse-video variants and hold/selection/title colors.

No event logic lives here; it is shared visual state for the window manager.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rio/fns.h

Function prototype header for `rio`. Declares window visibility, screen temp cleanup, wctl parsing/writing, window creation, cursor setting, timers, errors, memory helpers, menu handlers, rune conversion, snarf I/O, and geometry helpers.

Also defines rune allocation/move convenience macros.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/fsys.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rio/fsys.c

9P filesystem server for `rio`. Posts `/srv/rio.<user>.<pid>`, serves `/dev` files, and supports per-window directories under `wsys`.

Implements manual dispatch for version, attach, walk, open, read, write, clunk, stat, and flush. Directory reads synthesize stat records for global files and window ids. Non-directory reads/writes are delegated to xfid worker handlers.

Special behavior: skips serving `snarf`, `screen`, or `kbd` if already supplied externally; mounts `/mnt/wsys` and binds it before `/dev` for child window namespaces.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/fsys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/rio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rio/rio.c

Main `rio` window manager. Handles startup, display/mouse/keyboard initialization, menus, snarf integration, keyboard tap routing, mouse event routing, window resize/move/sweep, hide/unhide, screen resize, child shell startup, and shutdown.

Creates windows around shell processes, tracks current/input windows, routes mouse/keyboard events to window channels, and exposes controls through the filesystem server.

Button menus implement New/Resize/Move/Delete/Hide/Exit and Cut/Paste/Snarf/Plumb/Look/Send/Scroll. Screen resize rescales existing windows and preserves z order.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/rio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/scrl.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rio/scrl.c

Scrollbar drawing and mouse-scroll behavior for `rio` windows.

`wscrdraw()` computes thumb position from `org`, visible chars, and total runes, drawing through a reusable temporary image. `wscroll()` handles button-specific scrolling modes: page/back line scrolling, absolute thumb dragging, and forward scrolling with debounce timers.

`freescrtemps()` releases cached scroll drawing storage after screen changes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/scrl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/time.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rio/time.c

Timer service for `rio`. A timer process tracks active timers, decrements them using millisecond time from `nsec()`, sends nonblocking expiry notifications, and recycles canceled/expired timers.

Public API: `timerinit()`, `timerstart(dt)`, `timercancel()`, and `timerstop()`. Used by scroll debounce/sleep behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/time.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rio/util.c

General `rio` utilities. Converts UTF bytes to runes while tracking consumed bytes/runes/nulls, converts runes to UTF strings, provides checked memory allocation, fatal error handling, rune classification, rune search, and integer min/max.

`error()` aborts or exits all threads depending on `errorshouldabort`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/wctl.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rio/wctl.c

Parser and executor for `rio` `wctl` commands. Supports `new`, `resize`, `move`, `scroll`, `noscroll`, `set`, `top`, `bottom`, `current`, `hide`, `unhide`, and `delete`.

Parses geometry and parameters such as `-r`, min/max coordinates, deltas, `-pid`, `-id`, `-hide`, `-scroll`, `-noscroll`, and `-cd`. Validates rectangles with `goodrect()` and constrains them onscreen.

`writewctl()` dispatches commands either globally or to a target window id, creating windows or sending control messages to existing windows.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/wctl.c -->