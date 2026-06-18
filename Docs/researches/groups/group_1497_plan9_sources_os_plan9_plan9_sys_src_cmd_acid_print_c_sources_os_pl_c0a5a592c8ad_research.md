# Group Research: group_1497_plan9_sources_os_plan9_plan9_sys_src_cmd_acid_print_c_sources_os_pl_c0a5a592c8ad

Scope verified against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/plan9/plan9`. Each listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/print.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/print.c

This file implements pretty-printing and introspection output for the Acid debugger language. It prints function definitions, symbol/type metadata, expression trees, statement trees, and string literals.

Key behavior:
- `fundefs()` scans the Acid symbol hash, collects built-in and user-defined procedures, sorts names, and prints them in columns.
- `whatis()` reports variable types/formats, complex type layouts, procedure definitions, builtins, or undefined symbols.
- `pcode()` and `pexpr()` recursively print Acid AST nodes, covering control flow, local declarations, complex declarations, calls, indexing, casts, formatting, assignments, unary/binary operators, list constructs, and `whatis`.
- `pstr()` emits escaped string literals.

Important details:
- Output is routed through global `bout` using Plan 9 `Biobuf`.
- The printer depends on `acid.h` node op codes, type tags, symbol layout, and global hash table.
- Binary operator spellings are table-driven by Acid op enum values.
- Formatting is mostly diagnostic/source-like, not a general parser round-trip guarantee.

Filesystem relevance:
- Indirect: supports debugger interaction with symbols and values, not filesystem code itself.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/print.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/proc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/proc.c

This file manages Acid’s attachment to Plan 9 processes through `/proc`.

Key behavior:
- `sproc(pid)` opens `/proc/<pid>/mem`, validates text identity, builds `cormap` with `attachproc`, renames text/data segments, records `pid`, and installs the process in Acid’s process table.
- `nproc(argv)` forks a child, hangs it through `/proc/<pid>/ctl`, execs the target, then attaches Acid to the stopped child.
- `msg(pid, msg)` writes process-control commands to stored `/proc/<pid>/ctl` fds.
- `notes(pid)` reads pending notes from `/proc/<pid>/note` into Acid variable `notes`.
- `getstatus(pid)` parses `/proc/<pid>/status`.
- `waitfor(pid)` waits for a specific child wait message.

Important details:
- Attached process state is tracked in `ptab` and mirrored in Acid variables `pid` and `proclist`.
- `nocore()` closes segment fds in the current `cormap`.
- If control writes fail with `"process exited"`, `msg()` deinstalls the pid before reporting the error.

Filesystem relevance:
- Direct use of Plan 9’s process filesystem: `/proc/<pid>/mem`, `ctl`, `note`, and `status` are core interfaces.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/util.c

This file initializes Acid variables from symbols/register metadata and provides string/value helpers.

Key behavior:
- `varsym()` imports linker/debug symbols into Acid variables, renaming collisions by prefixing `$`, and builds a `symbols` list of `{name,type,value}` triples.
- `varreg()` exports machine register names as Acid variables and populates a `registers` list; also creates `bpinst` from architecture breakpoint instruction bytes.
- `loadvars()` initializes default variables: `proc`, `pid`, `notes`, and `proclist`.
- `rget()` reads 32-bit or 64-bit register values from a `Map` depending on register format.
- String constructors allocate GC-linked `String` objects for byte strings, rune strings, concatenation, rune append, and equality.

Important details:
- Symbol name conflicts are resolved conservatively but stop warning after repeated renames.
- String lengths are byte lengths in this Acid representation, including rune-copy paths that store raw rune bytes.
- `rget()` relies on register offsets placed in variables by `varreg()`.

Filesystem relevance:
- Indirect: prepares debugger state used when reading process/core maps.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/acme.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/acme.c

This is Acme’s main program: initialization, event threads, plumber integration, process tracking, font cache, icon colors, and snarf bridge.

Key behavior:
- `threadmain()` parses flags, initializes environment, fonts, display, mouse/keyboard, timers, regex engine, channels, plumber fds, 9P filesystem service, disk backing store, rows/columns/windows, and worker threads.
- `mousethread()` is the main UI dispatcher for mouse input, resize, plumber messages, and queued warnings.
- `keyboardthread()` routes keyboard input to the row/window under the mouse or bart mode target, with delayed tag commit.
- `waitthread()` tracks external commands, updates the row tag command list, reports exits, and handles `Kill`.
- `xfidallocthread()` allocates/recycles `Xfid` workers for the Acme 9P filesystem.
- `newwindowthread()` allows the filesystem server to request a new GUI window without drawing from the server proc.
- `rfget()`/`rfclose()` maintain reference-counted font cache and default fixed/variable font state.
- `putsnarf()`/`getsnarf()` synchronize Acme’s internal snarf buffer with `/dev/snarf`.

Important details:
- Acme binds `/acme/bin` and `/acme/bin/$cputype` before `/bin`.
- Shutdown dumps the row layout unless killed/exited explicitly.
- `/srv/acme.$user.$pid` is created as an error service pointing at an internal pipe.
- External command lifecycle is coordinated through `Command` records and channels.

Filesystem relevance:
- Central: starts `fsysinit()`, creates the Acme 9P service, uses `/dev/snarf`, plumber ports, `/srv`, `/tmp`, and per-command process handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/acme.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/addr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/addr.c

This file parses and evaluates Acme address expressions over text buffers.

Key behavior:
- `isaddrc()` and `isregexc()` define conservative address/regexp character classes for expansion.
- `number()` converts line or character numeric addresses into `Range`s, handling forward/backward relative movement.
- `regexp()` compiles and searches regex addresses forward or backward.
- `address()` evaluates address syntax including `.`, `$`, `#n`, line numbers, `+`, `-`, `/re/`, `?re?`, `,`, and `;`.

Important details:
- `;` updates the base address for the right side; `,` does not.
- Character addresses use `#`; line addresses are default.
- Missing left side of `,` defaults to start, and missing right side defaults to end.
- Invalid addresses can warn and set `evalp = FALSE` rather than aborting, depending on caller context.

Filesystem relevance:
- Indirect but important for Acme’s file-opening syntax like `file:addr`, and for `addr` pseudo-file behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/addr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/buff.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/buff.c

This file implements Acme’s rune buffer abstraction backed by disk blocks and a single active cache.

Key behavior:
- `bufinsert()` inserts runes, splitting or growing blocks up to `Maxblock`.
- `bufdelete()` removes ranges across cached/disk-backed blocks.
- `bufread()` reads arbitrary ranges through `setcache()`.
- `bufload()` and generic `loadfile()` convert UTF input from fd into runes, eliding NULs.
- `bufreset()` and `bufclose()` release disk blocks and cache memory.

Important details:
- Buffer data is stored in `Block`s allocated from global `disk`.
- `setcache()` flushes dirty cache before moving to the block containing a requested offset.
- `flush()` writes dirty cache or deletes an empty cached block.
- Insertions at block boundaries avoid unnecessary splits; interior insertions split the right suffix into a new block.

Filesystem relevance:
- Core text-storage layer: file contents, undo logs, edit logs, warnings, snarf buffer, and 9P data all build on this buffer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/buff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/cols.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/cols.c

This file manages Acme columns and windows within columns.

Key behavior:
- `colinit()` creates a column tag with commands `New Cut Paste Snarf Sort Zerox Delcol`.
- `coladd()` inserts or creates a window, splitting existing window space if needed.
- `colclose()` removes a window and resizes neighbors to fill the gap.
- `colresize()` resizes all contained windows proportionally.
- `colsort()` sorts windows by body file name.
- `colgrow()` grows a selected window, makes it full size, packs siblings, or normalizes sizing.
- `coldragwin()` handles window drag, shuffle, grow, and cross-column moves.
- `colwhich()` maps mouse points to column tag, window tag, or body text.
- `colclean()` checks whether all windows are clean.

Important details:
- `c->safe` tracks whether all windows are visible or a full-size window is obscuring others.
- Window movement preserves/restores mouse placement heuristically.
- Window geometry is quantized by tag/body font heights.

Filesystem relevance:
- Indirect UI layer around file-backed `Window`/`Text` objects.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/cols.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/dat.h

This is Acme’s central data definition header.

Key contents:
- Qid constants for global and per-window 9P files: `cons`, `index`, `new`, `addr`, `body`, `ctl`, `data`, `event`, `rdsel`, `wrsel`, `tag`, `xdata`, etc.
- Storage constants: `Blockincr`, `Maxblock`, `NRange`, `Infinity`.
- Core structs: `Block`, `Disk`, `Buffer`, `Elog`, `File`, `Text`, `Window`, `Column`, `Row`, `Timer`, `Command`, `Dirtab`, `Mntdir`, `Fid`, `Xfid`, `Reffont`, `Rangeset`, `Dirlist`, `Expand`.
- Function prototypes for disk, buffer, edit log, file, text, window, row, column, xfid, and font APIs.
- Global variables for display state, row/window focus, disk, snarf buffer, fonts, plumber fds, channels, and editing flags.

Important details:
- `File` embeds `Buffer` and adds undo/redo logs plus shared text views.
- `Text` embeds `Frame`, linking storage to screen representation.
- `Window` holds per-9P-open counts, event buffers, address state, include directories, dump metadata, and lock/ref state.
- `Mntdir`, `Fid`, and `Xfid` define Acme’s in-process 9P server state.

Filesystem relevance:
- Foundational: defines the Acme pseudo-filesystem namespace and backing data model.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/disk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/disk.c

This file provides temporary disk-backed block allocation for Acme buffers.

Key behavior:
- `tempfile()` creates an ORCLOSE/OCEXEC temp file named `/tmp/X?.useracme`.
- `diskinit()` allocates a `Disk` and opens the temp file.
- `ntosize()` rounds a rune count to a block-size bucket.
- `disknewblock()` allocates/reuses a `Block` from size-specific free lists and advances the temp-file address.
- `diskrelease()` returns a block to the proper free bucket.
- `diskwrite()` writes runes to a block, replacing the block if size bucket changes.
- `diskread()` reads runes from a block with full-read checking.

Important details:
- Blocks are metadata records allocated in chunks of 100; payload lives in one temp file.
- Size classes are multiples of `Blockincr` up to `Maxblock`.
- Temp file is removed automatically on close due to `ORCLOSE`.

Filesystem relevance:
- Direct: Acme’s text buffers are disk-backed through a temporary file, reducing memory pressure for large edits.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/disk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/ecmd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/ecmd.c

This file executes Acme `Edit` language commands after parsing.

Key behavior:
- `cmdexec()` resolves default/current addresses, maps commands to handlers, and executes command blocks.
- Implements edit commands: append/insert/change/delete, file switch/open/delete, read/write, print, substitute, move/copy, undo/redo, global/looping commands, pipe commands, address reporting, and file matching.
- `runpipe()` integrates `<`, `|`, `>` edit commands with external process execution and `editout`.
- `looper()`, `linelooper()`, and `filelooper()` implement `x/y` and `X/Y` iteration over ranges or files.
- `cmdaddress()` evaluates parsed `Addr` trees against current `Address`.
- `cmdname()` resolves and optionally sets file names, warning on duplicate window names.

Important details:
- Edit commands log changes into `Elog` first, so command addresses refer to the original buffer state.
- `filelooper()` protects windows with refs and `globalincref` during cross-window edits.
- `runpipe()` temporarily changes global `editing` state to collect or insert command output, unlocks row/window around external execution, then relocks.
- Substitute supports `&` and `\1`-`\9` replacement captures with size checks.
- `e_cmd()` treats full same-file replacement as clean if the file content was re-read successfully.

Filesystem relevance:
- High: implements editor commands that read/write real files, open named buffers, and pipe selections through Acme’s mounted namespace.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/ecmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/edit.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/edit.c

This file parses Acme’s structural `Edit` command language and manages parse-time objects.

Key behavior:
- `cmdtab` defines command syntax, default addresses, regexp/text/address operands, counts, terminators, and executor function.
- `editcmd()` prepares command text, starts `editthread()`, waits for parse/exec completion, and applies edit logs to all affected windows.
- Lexer helpers read runes from command text, parse numbers, skip blanks, collect regexps/text/tokens, and validate delimiters.
- `parsecmd()` builds `Cmd` trees including nested `{}` blocks, command defaults, regexps, substitution RHS, and movement addresses.
- `simpleaddr()` and `compoundaddr()` build address parse trees.
- List/string/cmd allocation is tracked in global lists and freed by `freecmd()`.

Important details:
- Commands are automatically newline-terminated.
- Last regular expression is remembered for empty regexp reuse.
- Errors call `editerror()`, which frees parse objects, truncates edit logs, sends error text on `editerrc`, and exits the edit thread.
- Input length is capped relative to `RBUFSIZE`.

Filesystem relevance:
- Indirect but central to batch file editing through Acme’s `Edit` command.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/edit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/edit.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/edit.h

This header defines the parse-tree structures and public parser/executor interfaces for Acme `Edit`.

Key contents:
- `String`: mutable rune string with allocation size.
- `Addr`: address AST node supporting numeric, regexp, dot/dollar, relative, comma, semicolon, and file-match forms.
- `Address`: evaluated range plus target `File`.
- `Cmd`: command AST node with optional address, regexp, text, move/copy target address, nested command, next command, count, flags, and command char.
- `cmdtab` declaration describing command syntax and executor callback.
- `List`: growable typed pointer list used for parse allocation tracking.
- Default address enum: `aNo`, `aDot`, `aAll`.
- Function prototypes for command handlers, parser helpers, and edit execution.

Filesystem relevance:
- Defines the command structures used for file/range edits and file selection in Acme.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/edit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/elog.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/elog.c

This file implements Acme’s edit-command change log, separate from normal undo/redo.

Key behavior:
- `eloginit()`, `elogreset()`, `elogterm()`, and `elogclose()` manage per-file edit log state.
- `elogreplace()`, `eloginsert()`, and `elogdelete()` record pending changes against original buffer coordinates.
- `elogflush()` serializes current pending edit into `elogbuf`.
- `elogapply()` applies serialized changes to the current text/file, marking the file and updating display/selection.

Important details:
- The design explicitly preserves original-address semantics for edit commands and merges nearby changes to reduce I/O.
- Out-of-sequence changes warn once, flush the current change, and continue.
- Insert/replace text is chunked at `RBUFSIZE`.
- `elogapply()` constrains possibly stale/overlapping addresses before calling `textdelete()`/`textinsert()`.

Filesystem relevance:
- Important for safe scripted edits to file-backed buffers before writes happen.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/elog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/exec.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/exec.c

This file implements tag command execution and external command launching.

Key behavior:
- `exectab` maps built-in commands: `Cut`, `Del`, `Dump`, `Edit`, `Exit`, `Font`, `Get`, `Kill`, `Look`, `New`, `Paste`, `Put`, `Redo`, `Send`, `Snarf`, `Sort`, `Tab`, `Undo`, `Zerox`, and more.
- `execute()` expands clicked text, sends events to external clients if needed, runs built-ins, or launches external commands.
- Built-ins implement window/column creation/deletion, file get/put, dump/load, cut/paste/snarf, search, edit, font selection, include path management, indentation, tabstop, kill, and command send.
- `putfile()` writes file ranges with qid/mtime/dev conflict checks and append-only rejection.
- `runproc()` creates the child namespace, mounts `/mnt/acme`, sets `%`, `winid`, `acmeaddr`, wires stdin/stdout/stderr for pipes, tries direct exec, then falls back to `rc -c`.
- `run()` starts command execution and a wait task without blocking Acme’s 9P mount path.

Important details:
- External command execution uses per-command `Mntdir` state and exposes Acme through `/mnt/acme` and `/dev`.
- `Cut`/`Paste` coordinate with undo sequence numbers and snarf buffer.
- `Putall` skips scratch, directories, nameless files, and windows with external event clients.
- `Get` refuses unsafe reloads and handles directory windows specially.
- Direct exec path rejects shell-special characters; complex commands run under `rc`.

Filesystem relevance:
- Very high: real file I/O, Acme pseudo-files, namespace construction, `/dev`, `/mnt/wsys`, plumber notifications, and safe-write semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/exec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/file.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/file.c

This file wraps `Buffer` with file identity, shared text views, modification state, and undo/redo logs.

Key behavior:
- `fileaddtext()` and `filedeltext()` manage the list of `Text` views sharing a file.
- `fileinsert()` and `filedelete()` modify the buffer and emit inverse records when undo is active.
- `fileundelete()`, `fileuninsert()`, and `fileunsetname()` write undo records to delta/epsilon buffers.
- `fileundo()` replays undo or redo records backward, updating all associated text views.
- `filesetname()`, `fileload()`, `filereset()`, `fileclose()`, and `filemark()` manage lifecycle and sequence state.

Important details:
- Undo records are stored after associated data so the log can be read backward.
- `delta` is undo history; `epsilon` is redo history.
- Sequence numbers group simultaneous changes across files/windows.
- A `File` acts like a plain `Buffer` while `seq == 0`.

Filesystem relevance:
- Represents file-backed editor buffers and tracks state needed for safe writes/reloads.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/fns.h

This header declares cross-module Acme functions and convenience macros.

Key contents:
- Warning/error, plumber, snarf, temp file, scroll, font, command argument, new/undo/cut/paste/get/put/font APIs.
- Window/error-window helpers, command runner, fsys lifecycle, regex/address helpers, text search/expansion helpers.
- Allocation helpers: `emalloc`, `erealloc`, `estrdup`, `runemalloc`, `runerealloc`, `runemove`.
- Generic helpers: `cvttorunes`, `runeeq`, `min`, `max`, rune/byte conversion, whitespace scanners.
- 9P server hooks: `fsysinit`, `fsysmount`, `fsysincid`, `fsysdelid`, `respond`.

Filesystem relevance:
- Connects all Acme modules, including pseudo-filesystem, real-file operations, and buffer loading.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/fsys.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/fsys.c

This file implements Acme’s 9P filesystem front end.

Key behavior:
- Defines global and per-window directory tables for `/mnt/acme`.
- `fsysinit()` creates a pipe-backed 9P service and starts `fsysproc()`.
- `fsysproc()` reads 9P messages, decodes them, allocates `Xfid`s, dispatches by fcall type, and delegates opened-file operations to xfid workers.
- `fsysmount()` mounts the service into a child namespace and binds it over `/mnt/wsys` and before `/dev`.
- `fsyswalk()` supports root, numeric window directories, `new`, global files, and per-window files.
- `fsysread()` serves directory listings and delegates normal file reads.
- `fsysopen()`, `fsysclunk()`, `fsysstat()`, and others enforce permissions and lifecycle.
- `Mntdir` refcount helpers manage per-command mount identity, working directory, and include paths.

Important details:
- `messagesize` is negotiated by `Tversion`.
- Attach checks `uname` against `/dev/user`.
- Walking `new` asks GUI thread to create a window via `cnewwindow`.
- Root directory listing includes sorted numeric window ids.
- Create/remove/wstat/auth are denied.

Filesystem relevance:
- Primary Acme pseudo-filesystem implementation; exposes editor state and control surfaces as 9P files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/fsys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/look.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/look.c

This file implements button-3 look/open/search behavior, plumber integration, filename expansion, and window lookup.

Key behavior:
- `look3()` expands clicked text, notifies external event clients, tries plumber send, then opens files or searches text.
- `plumblook()` opens files from plumber messages with optional address attributes.
- `plumbshow()` creates a new window containing supplied plumber data.
- `search()` performs wraparound literal rune search in a text.
- `expandfile()` recognizes file names and optional `:addr` suffixes, including include-file syntax `<name>`.
- `dirname()` resolves relative names against a window tag path.
- `openfile()` reuses an existing window or creates/loads a new one and jumps to an address.
- `new()` implements the `New` built-in for unnamed or named windows.

Important details:
- External event clients receive pre- and post-expansion look events.
- File recognition checks existing Acme windows first, then `access()`.
- Include resolution checks window include dirs, `/sys/include`, and `/$objtype/include`.
- Directory names are normalized with `cleanname`.

Filesystem relevance:
- High: resolves paths, opens files/directories into Acme windows, and integrates plumber file messages.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/look.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/regx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/regx.c

This file implements Acme’s regular expression compiler and forward/backward NFA executor.

Key behavior:
- `rxinit()` initializes the compile channel and empty last regexp.
- `rxcompile()` compiles a null-terminated rune regexp into both forward and backward programs, caching the last regexp.
- Parser supports literals, escapes, `.`, `^`, `$`, `[]`, `[^]`, grouping, alternation, concatenation, `*`, `+`, and `?`.
- `rxexecute()` runs the forward machine over either `Text` or rune string input.
- `rxbexecute()` runs the backward machine over `Text`.
- Captures are stored in `Rangeset` slots up to `NRange`.

Important details:
- Program size is fixed at `NPROG`.
- Active NFA list size is fixed at `NLIST`; overflow warns and fails.
- Backward compilation reverses concatenation where needed.
- Character classes support ranges and escaped `\n`.
- `lastregexp` supports empty regexp reuse elsewhere.

Filesystem relevance:
- Indirect: powers address searches and edit commands across file-backed buffers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/regx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/rows.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/rows.c

This file manages Acme’s top-level row, columns, workspace dump/load, and all-window traversal.

Key behavior:
- `rowinit()` creates the row tag with commands `Newcol Kill Putall Dump Exit`.
- `rowadd()`, `rowclose()`, `rowresize()`, and `rowdragcol()` manage column layout.
- `rowwhich()` and `rowtype()` route mouse/keyboard events to row, column, tag, or body text.
- `rowdump()` serializes current working directory, fonts, column positions, windows, tags, dirty file contents, zerox relationships, and external command windows.
- `rowloadfonts()` preloads font choices from a dump file.
- `rowload()` reconstructs layout from a dump file, reopens files, restores dirty dumped contents, fonts, and selections.
- `allwindows()` applies a callback to every window.

Important details:
- Dump format uses line records starting with `f`, `F`, `x`, and `e`.
- Dirty buffers can be embedded in the dump; clean files are reopened by name.
- External event windows can be skipped or restored through command metadata.
- Column positions are stored as percentages.

Filesystem relevance:
- High: implements Acme session persistence via dump files and reloads real or embedded file contents.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/rows.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/scrl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/scrl.c

This file implements body scrollbar drawing and mouse scrolling.

Key behavior:
- `scrpos()` computes scrollbar thumb rectangle from visible range and total file length.
- `scrlresize()` allocates a temporary image for scrollbar drawing.
- `textscrdraw()` redraws a body scrollbar only when the position changes.
- `scrsleep()` waits for a timer or mouse activity during scroll repeat.
- `textscroll()` handles button 1, 2, and 3 scrolling: page/back-line style, absolute proportional jump, and forward scrolling.

Important details:
- Large totals are shifted down to avoid integer overflow.
- Scroll thumb is at least two pixels tall.
- Button 2 maps mouse y position proportionally to file character offset.
- Mouse is warped to the scroll bar center during active scrolling.

Filesystem relevance:
- Indirect UI support for navigating file-backed text.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/scrl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/text.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/text.c

This file implements Acme’s text/frame behavior: loading, drawing, insertion/deletion, typing, selection, scrolling, completion, and directory display.

Key behavior:
- `textinit()`, `textredraw()`, `textresize()`, and `textclose()` manage frame lifecycle.
- `textload()` loads regular files or directories; directory windows are columnated and sorted.
- `textinsert()`/`textdelete()` update file storage, all shared views, frame display, selections, dirty state, and event streams.
- `texttype()` handles keyboard editing, navigation, scrolling keys, completion, backspace variants, ESC selection, and autoindent.
- `textcommit()` flushes typed cache to the underlying file.
- Selection functions handle normal selection, chording cut/paste, button 2/3 selection, double-click word/bracket matching, and frame scrolling.
- `textshow()`, `textsetorigin()`, and `textbacknl()` keep selections visible.
- `textcomplete()` performs filesystem completion using `complete()` and window-relative paths.
- `textreset()` clears text/file state without building undo records.

Important details:
- Typed characters are cached in each shared `Text` and committed later for efficiency.
- Body edits mark file/window dirty and invalidate UTF read cache.
- Directory windows use a narrower tab width and rebuild columns on resize.
- Multi-view files propagate edits to all views.
- Selection drawing has custom overlap restoration to avoid unnecessary repainting.

Filesystem relevance:
- Very high: loads files/directories, performs filename completion, represents directory listings, and synchronizes display with file-backed buffers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/text.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/time.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/time.c

This file implements a lightweight timer service for Acme threads.

Key behavior:
- `timerinit()` creates the timer channel and starts `timerproc()`.
- `timerstart(dt)` allocates/reuses a `Timer`, initializes deadline state, and sends it to the timer proc.
- `timercancel()` marks a timer canceled.
- `timerstop()` returns a timer to the freelist.
- `timerproc()` ticks roughly every millisecond, decrements active timers, nonblocking-sends on expired timer channels, recycles canceled timers, and accepts newly started timers.

Important details:
- Uses millisecond values derived from `nsec()`.
- Handles wrap by dropping a tick.
- Expiry sends are nonblocking to avoid deadlock if a client is simultaneously sending/receiving.

Filesystem relevance:
- Indirect: supports UI delays, tag commit timing, and scroll sleeps.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/time.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/util.c

This file provides Acme utility functions for UTF conversion, warnings, error windows, allocation, rune helpers, mouse restore, and new-window placement.

Key behavior:
- `cvttorunes()` converts byte input to runes while eliding NULs and reporting consumed bytes/runes.
- `error()` reports fatal error, removes the Acme error service file, and aborts.
- `errorwin()`/`errorwinforwin()` create or find `+Errors` windows, preserving directory/include context.
- `warning()` queues warning text by `Mntdir`; `flushwarnings()` writes queued warnings into error windows in buffered chunks.
- `runetobyte()` and `bytetorune()` convert between rune arrays and UTF strings.
- `isalnum()`, `skipbl()`, `findbl()`, `rgetc()`, and `tgetc()` support parsers/searchers.
- `emalloc()`, `erealloc()`, and `estrdup()` are checked allocation helpers.
- `makenewwindow()` chooses the active/best column and split point for new windows.

Important details:
- Warning buffers are per mount directory, and `Mntdir` refs are held until warnings flush.
- `flushwarnings()` is called with the row locked and writes through `textbsinsert()` to process backspaces.
- `isalnum()` treats most non-control non-punctuation runes as alphanumeric.
- New-window placement prefers active column, selection column, caller column, then last column.

Filesystem relevance:
- Supports error reporting for filesystem-mounted commands and path-aware `+Errors` windows.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/util.c -->