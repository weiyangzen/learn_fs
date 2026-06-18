# Group Research: 9front Acid Helpers and Acme Core Sources

Scope: `Docs/research_subset_a.md` includes `sources/os/plan9/9front`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/print.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acid/print.c

This file implements Acid's source-level pretty-printing and symbol-description output.

Key responsibilities:
- Maintains printable names for binary operators and Acid value type names.
- `fundefs()` collects all user-defined and builtin function names from the global hash table, sorts them, and prints them in columns.
- `whatis()` reports what a symbol is: variable with type/format, complex type definition, function definition, builtin function, or undefined.
- `pcode()` and `pexpr()` recursively render Acid AST nodes back into readable source-like text.
- `pstr()` prints Acid strings with C-style escapes for control characters, backslash, and quote.

Important dependencies:
- Uses global Acid state from `acid.h`: `hash`, `bout`, `Node`, `Lsym`, `Type`, `String`.
- Uses Plan 9 `Biobuf` output APIs (`Bprint`, `Bputc`).
- AST opcodes map directly to parser/evaluator node kinds.

Filesystem/storage relevance:
- No direct filesystem operations. This is diagnostic and introspection support for the Acid debugger, useful for understanding runtime command definitions and type metadata.

Notes:
- Pretty-printing is conservative and parenthesizes most binary expressions.
- Indentation uses a fixed tab string and precision formatting, so very deep nesting is bounded by the static tab buffer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/print.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/proc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acid/proc.c

This file manages Acid's attachment to Plan 9 processes through `/proc`.

Key responsibilities:
- `nocore()` closes existing core-map segment file descriptors and frees the current `cormap`.
- `sproc(pid)` opens `/proc/<pid>/mem`, validates it against the symbol map, attaches a process memory map, labels text/data segments, sets the Acid `pid` variable, and installs the process in Acid's table.
- `nproc(argv)` forks a new child, hangs it through `/proc/<pid>/ctl`, resets stdio to `/dev/cons`, execs the requested program, then attaches Acid to it.
- `notes(pid)` reads pending process notes from `/proc/<pid>/note` into the Acid `notes` list.
- `dostop(pid)` calls the user-defined `stopped(pid)` Acid hook if present.
- `install()` and `deinstall()` maintain `ptab`, `proclist`, process control fds, and `pid`.
- `msg(pid, msg)` sends control messages to `/proc/<pid>/ctl`.
- `getstatus(pid)` reads and tokenizes `/proc/<pid>/status`.
- `waitfor(pid)` waits specifically for a given process.

Important dependencies:
- Uses Plan 9 `/proc` files: `mem`, `ctl`, `note`, `status`.
- Uses libmach process/core-map functions such as `attachproc`, `findseg`, and `checkqid`.
- Updates Acid variables via `look()`, `al()`, `strnode()`, and `execute()`.

Filesystem/storage relevance:
- Strongly process-filesystem oriented: `/proc` is used as the debugging control and memory interface.
- Shows Plan 9's file-backed process control model in compact form.

Notes:
- `msg()` treats `"process exited"` specially by deinstalling the process before reporting the error.
- New child setup uses `rfork(RFNAMEG|RFNOTEG)` to isolate namespace and notes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acid/util.c

This file provides Acid utility routines for symbols, registers, built-in variables, register reads, and garbage-collected string allocation.

Key responsibilities:
- `unique()` resolves symbol-name collisions by prepending `$`, printing rename diagnostics when not quiet.
- `varsym()` imports text/data/bss/local symbol-table entries into Acid variables and builds the `symbols` list as `{name, type, value}` triples.
- `varreg()` creates Acid variables for machine registers and a `registers` list; also exposes breakpoint instruction bytes as `bpinst`.
- `loadvars()` initializes standard Acid variables: `proc`, `pid`, `notes`, and `proclist`.
- `rget(map, reg)` reads a register value from a map using register metadata and format width.
- `strnodlen()`, `strnode()`, `runenode()`, `stradd()`, and `straddrune()` allocate Acid `String` objects and link them into the global GC list.
- `scmp()` compares two Acid strings by length and bytes.

Important dependencies:
- Uses libmach symbol and machine descriptions (`symbase`, `getsym`, `mach->reglist`, `machdata`).
- Uses global Acid allocation and symbol helpers (`gmalloc`, `mkvar`, `look`, `enter`, `gcl`).

Filesystem/storage relevance:
- No direct filesystem operations, but it bridges executable symbol tables and register maps into Acid's scripting environment.

Notes:
- Address format switches to 64-bit display (`Y`) when `mach->szaddr == 8`.
- Symbol import skips names beginning with `.` and long names that would overflow its stack buffer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/acme.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/acme.c

This is Acme's main program: startup, global event threads, window layout initialization, plumbing integration, command-process tracking, font cache, icons, and snarf interaction.

Key responsibilities:
- `threadmain()` parses flags, initializes namespace bindings, fonts, draw/mouse/keyboard state, timers, regex, channels, plumbing, 9P file server, temp disk, row/columns/windows, and worker threads.
- `readfile()` creates an initial window and loads a named file or directory.
- `shutdown()` handles notes, dumps layout on non-kill exit, and terminates.
- `killprocs()` closes the file server, posts hangup to child commands, and removes the Acme error service.
- `acmeerrorinit()` exposes an error pipe through `/srv/acme.<user>.<pid>`.
- `plumbproc()` reads plumber messages from the `edit` port.
- `keyboardthread()` dispatches keyboard input to row/window text handling and delayed tag commit.
- `mousethread()` handles resize, plumbing, warning flushes, focus logging, selection, execute, look, scroll, drag, and chord behavior.
- `waitthread()` tracks child command start/exit, Kill requests, command names in the row tag, and error reporting.
- `xfidallocthread()` pools `Xfid` workers for the 9P file server.
- `newwindowthread()` lets the 9P server create windows from a graphics-safe thread.
- `rfget()`/`rfclose()` manage reference-counted fonts and the font cache.
- `iconinit()` builds tag/text colors and scroll/button images.
- `putsnarf()`/`getsnarf()` synchronize Acme's snarf buffer with `/dev/snarf`.

Important dependencies:
- Coordinates most modules in this group: row/column/window/text, fsys, exec, look, log, regex, disk, timer.
- Uses Plan 9 services: `/dev/snarf`, plumber ports, `/srv`, namespace bind, draw, keyboard, mouse, thread channels.

Filesystem/storage relevance:
- Starts Acme's synthetic 9P filesystem via `fsysinit()`.
- Creates a per-session temp disk through `diskinit()`.
- Reads initial files/directories and dumps/restores layout through row code.
- Exposes `/srv/acme.user.pid` for external error integration.

Notes:
- Child command lifecycle is asynchronous and robust against races where wait messages arrive before command registration.
- `mousethread()` logs `"focus"` events when active windows change, feeding the global `/mnt/acme/log` mechanism.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/acme.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/addr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/addr.c

This file evaluates Acme address syntax over `Text` buffers.

Key responsibilities:
- `isaddrc()` identifies characters that can participate in an address.
- `isregexc()` identifies likely regex characters during click expansion.
- `nlcounttopos()` maps saved line-plus-rune offsets back into a text position, bounded by file length and line end.
- `number()` evaluates numeric line or character addresses with forward/backward/absolute direction.
- `regexp()` evaluates forward or backward regex address components using Acme's regex engine.
- `address()` parses and evaluates compound address strings including `.`, `$`, `#n`, line numbers, `+`, `-`, `/re/`, `?re?`, `,`, and `;`.

Important dependencies:
- Uses `textreadc()`, `rxcompile()`, `rxexecute()`, `rxbexecute()`, `rxnull()`, and warning reporting.
- Address evaluation operates on `Range` and accepts an arbitrary `getc` callback, so it can parse addresses from text, plumbing attributes, or command strings.

Filesystem/storage relevance:
- Address parsing is central to Acme's file interface: external clients write addresses to synthetic files like `addr` and use those ranges for `data`, `xdata`, and edit operations.

Notes:
- `;` updates the base address for the right side, matching Sam/Acme semantics.
- Empty regex reuse is guarded: no previous regex emits a warning and leaves the range unchanged.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/addr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/buff.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/buff.c

This file implements Acme's rune buffer abstraction backed by temporary disk blocks with a single in-memory cache.

Key responsibilities:
- `sizecache()` grows the in-memory rune cache with slop.
- `addblock()`/`delblock()` manage the buffer's array of disk `Block*` entries.
- `flush()` writes dirty cache content to disk or deletes empty blocks.
- `setcache()` locates, flushes, and loads the block containing a requested position.
- `bufinsert()` inserts runes, splitting or adding blocks as needed while respecting `Maxblock`.
- `bufdelete()` deletes ranges across cached disk blocks.
- `loadfile()` reads bytes from an fd, converts UTF to runes, handles partial UTF sequences between reads, and delegates insertion to a callback.
- `bufload()` loads into a `Buffer`.
- `bufread()` copies runes from arbitrary positions.
- `bufreset()` and `bufclose()` clear buffer storage.

Important dependencies:
- Uses `disknewblock()`, `diskwrite()`, `diskread()`, and `diskrelease()` from `disk.c`.
- Uses `cvttorunes()` for UTF conversion and `fbufalloc()`/`runemalloc()` helpers.

Filesystem/storage relevance:
- This is Acme's core text storage layer. Large files and undo/edit logs are buffered as rune blocks in a temp file rather than held fully in memory.

Notes:
- The buffer cache is write-back and position-based; edits mutate logical block layout while disk blocks are recycled through `Disk`.
- `loadfile()` is generic enough to feed both buffers and edit logs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/buff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/cols.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/cols.c

This file manages Acme columns and the windows inside them.

Key responsibilities:
- `colinit()` initializes a column tag and draws its controls (`New Cut Paste Snarf Sort Zerox Delcol`).
- `coladd()` inserts a new or existing window into a column, splitting available vertical space.
- `colclose()` removes a window and expands neighboring windows into the freed area.
- `colcloseall()` closes all windows and frees the column.
- `colresize()` resizes the column and proportionally resizes windows.
- `colsort()` sorts windows by file name and lays them out.
- `colgrow()` expands a window, makes it full-column, or repacks surrounding windows based on button action.
- `coldragwin()` handles moving/resizing windows by mouse drag, including moving across columns.
- `colwhich()` maps a point to a column tag, window tag, body, or scroll area.
- `colclean()` checks whether every window in the column is clean.

Important dependencies:
- Calls window functions (`wininit`, `winresize`, `winclose`, `windelete`, `winclean`), text functions, row hit testing, and mouse helpers.
- Uses draw primitives to repaint background and borders.

Filesystem/storage relevance:
- Indirect: columns own windows, and windows expose files through Acme's synthetic 9P namespace. Column operations can close windows and therefore release file references.

Notes:
- `c->safe` tracks whether the layout is fully packed or temporarily obscured by a full-column window.
- Window creation here does not always log itself; callers are responsible for `xfidlog(..., "new")` except in specific flows.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/cols.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/dat.h

This is Acme's central data-definition header.

Key contents:
- Qid/file enum for the Acme 9P namespace: global files (`cons`, `index`, `log`, `new`, etc.) and per-window files (`addr`, `body`, `ctl`, `data`, `event`, `tag`, `xdata`, etc.).
- Constants for buffer block sizing, regex range count, UI dimensions, event size, and booleans.
- Core structs:
  - `Block`, `Disk`, `Buffer` for temp-file-backed text storage.
  - `Elog` for pending edit-command changes.
  - `File` for text contents, undo/redo buffers, names, stat metadata, text views, and modification state.
  - `Text` for visible frame state, selection, cache, scroll rectangle, and owning window/row/column.
  - `Window`, `Column`, `Row` for Acme's UI hierarchy.
  - `Command` for external child processes.
  - `Dirtab`, `Mntdir`, `Fid`, `Xfid` for the synthetic 9P server.
  - `Reffont`, `Rangeset`, `Dirlist`, `Expand`, `Timer`.
- Function prototypes for buffer, disk, file, text, window, column, row, 9P, font, and regex operations.
- Global variables for UI state, channels, filesystem state, font names, snarf, disk, active selections, and process-control channels.

Filesystem/storage relevance:
- Defines the synthetic filesystem contract and the storage model used by Acme.
- `File` records `qidpath`, `mtime`, and `dev` to detect on-disk modifications before writing.
- `Mntdir` captures per-command mount context and include paths.

Notes:
- `QID(w,q)`, `WIN(q)`, and `FILE(q)` encode/decode window id and file id in Qid paths.
- `File` embeds `Buffer`, making text content and buffer operations share layout directly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/disk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/disk.c

This file implements Acme's temporary disk block allocator.

Key responsibilities:
- `tempfile()` creates a per-process temp file `/tmp/X<pid>.<user-prefix>acme` with `ORCLOSE|OCEXEC`.
- `diskinit()` allocates a `Disk` and opens the temp file, exiting if creation fails.
- `ntosize()` rounds a rune count up to the block allocation bucket size.
- `disknewblock()` allocates or reuses a `Block` from size-class free lists, assigning offsets in the temp file.
- `diskrelease()` returns a block to its size-class free list.
- `diskwrite()` rewrites a block, reallocating if the rounded size class changes.
- `diskread()` reads a block range fully with `pread`.

Important dependencies:
- Used by `Buffer` in `buff.c`.
- Uses `emalloc()`, `error()`, and Plan 9 pread/pwrite/create APIs.

Filesystem/storage relevance:
- This is the physical backing store for Acme's in-memory text model: text buffers and logs live in a temporary file with recyclable block metadata.

Notes:
- Blocks are allocated in chunks of 100 `Block` structs to reduce malloc overhead.
- It checks for temp-file address overflow when allocating new disk space.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/disk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/ecmd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/ecmd.c

This file implements execution of Acme/Sam-style edit commands after parsing.

Key responsibilities:
- Maintains edit execution globals: current address, nesting, current file, regex selection, and collected pipe output.
- `cmdexec()` resolves default addresses and dispatches parsed commands.
- `edittext()` is the insertion/collection entry point used by external edit-command output.
- `filelist()` supports command file-list arguments, including collection from `<` pipes.
- Implements edit commands:
  - `a`, `i`, `c`, `d` for insert/change/delete through edit logs.
  - `e`/`r` for reading files into ranges.
  - `f` for setting/printing file names.
  - `g`/`v`, `x`/`y`, `X`/`Y` for regex/file looping.
  - `m`/`t` for move/copy.
  - `s` substitution with `&` and numeric submatch replacements.
  - `u` undo/redo.
  - `w` writing ranges to disk.
  - `<`, `|`, `>` pipe integration.
  - `=`, newline, `p`, `b`, `B`, `D`.
- `runpipe()` invokes shell commands in edit mode and coordinates with `cedit`.
- Address support includes `cmdaddress()`, `charaddr()`, `lineaddr()`, `nextmatch()`.
- File matching helpers resolve explicit files and regex-matched file names.
- `cmdname()` computes and optionally sets file names, with duplicate-name warnings.

Important dependencies:
- Relies on `edit.c` parse trees (`Cmd`, `Addr`, `String`) and `cmdtab`.
- Uses `elog.c` to defer and apply modifications safely.
- Uses `exec.c` for external commands and `look.c` path helpers.
- Uses `regx.c` for regex execution.

Filesystem/storage relevance:
- Reads files (`open`, `dirfstat`, `loadfile`), writes files through `putfile()`, and invokes external commands through Acme's mounted 9P namespace.
- Protects writes when a file has pending modifications in the current sequence.

Notes:
- Edit changes are logged before application so addresses refer to the original buffer state.
- `X`/`Y` file loops temporarily add references to all windows to keep targets alive during cross-window editing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/ecmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/edit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/edit.c

This file parses Acme's edit command language and orchestrates edit-thread execution.

Key responsibilities:
- Defines `cmdtab`, mapping command characters to parse requirements, default addresses, default commands, token rules, and executor functions.
- `editcmd()` prepares command text, initializes edit logs on all windows, starts `editthread()`, waits for errors, then applies pending edit logs.
- `editthread()` repeatedly parses and executes commands.
- `editerror()` frees parse state, terminates all edit logs, reports the error through `editerrc`, and exits the edit thread.
- Lexer/parser utilities: `getch()`, `nextc()`, `ungetch()`, `getnum()`, `cmdskipbl()`, `okdelim()`, `atnl()`.
- Dynamic list helpers manage parse allocations for commands, addresses, and strings.
- String helpers allocate and grow command strings.
- `collecttext()`, `collecttoken()`, `getrhs()`, `getregexp()` parse command arguments.
- `parsecmd()` parses addresses, commands, grouped blocks, regexes, counts, text, tokens, and default commands.
- `simpleaddr()` and `compoundaddr()` parse address ASTs.

Important dependencies:
- Execution is delegated to `ecmd.c`.
- Uses `elogterm()`/`elogapply()` to manage deferred changes.
- Uses `allwindows()` to initialize/apply edits across all open windows.

Filesystem/storage relevance:
- Indirect but central to file editing: this parser drives edits that may read, write, and pipe file content through `ecmd.c`.

Notes:
- Command input is rune-based and NUL-terminated.
- There is a command length guard based on `RBUFSIZE`.
- Last regex is remembered for empty regex reuse.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/edit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/edit.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/edit.h

This header defines Acme edit-command parser data structures and prototypes.

Key contents:
- `String`: mutable rune string with length and allocation size.
- `Addr`: parsed address node for character/line/regex/current/end/range forms.
- `Address`: evaluated `Range` plus owning `File`.
- `Cmd`: parsed command node with optional address, regex, nested command, text, move/copy target address, count, flags, command character, and next command.
- `cmdtab` declaration describes command parsing and dispatch metadata.
- `List`: generic growable pointer list used to track parser allocations.
- Default address enum: `aNo`, `aDot`, `aAll`.
- Prototypes for command functions, string allocation, parser helpers, address evaluation, execution, and error reporting.

Filesystem/storage relevance:
- Indirect: edit commands operate on `File` and `Text`, and this header defines the parse tree passed to file-changing logic.

Notes:
- Uses Plan 9 vararg checking for `editerror`.
- `INCR` controls parser allocation-list growth.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/edit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/elog.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/elog.c

This file implements deferred edit logs for Acme edit commands.

Key responsibilities:
- `eloginit()` initializes a file's edit log buffer and scratch rune buffer.
- `elogclose()` releases the edit log buffer.
- `elogreset()`/`elogterm()` reset or fully tear down pending log state.
- `elogflush()` serializes the pending in-memory `Elog` entry into the log buffer.
- `elogreplace()`, `eloginsert()`, and `elogdelete()` record deferred modifications and merge nearby compatible changes when possible.
- `elogapply()` replays the log into the file's current text, marking undo state once, applying text insert/delete operations, adjusting selections, and restoring window ownership.

Important dependencies:
- Uses `Buffer` to store serialized `Buflog` entries and replacement/insert strings.
- Uses `textinsert()`, `textdelete()`, `textconstrain()`, `filemark()`, and `winsettag()` via update paths.
- Called by `edit.c` and `ecmd.c`.

Filesystem/storage relevance:
- This is Acme's transaction layer for editing file buffers. It avoids applying edits while addresses are still being interpreted against the old file state.

Notes:
- Warns once for out-of-sequence changes but attempts to continue.
- Merges replacements when gaps are small and total merged text fits in `RBUFSIZE`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/elog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/exec.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/exec.c

This file implements Acme tag commands, command execution, snarf/cut/paste, file Get/Put, process launching, and command argument handling.

Key responsibilities:
- Defines `exectab`, mapping tag command names (`Cut`, `Del`, `Dump`, `Edit`, `Get`, `Put`, `Undo`, `Zerox`, etc.) to functions and flags.
- `execute()` expands clicked text, sends events to external clients when appropriate, runs built-in commands, or launches external commands.
- Argument helpers `getarg()`, `getbytearg()`, `getname()`, and `printarg()` collect selected/file/address arguments.
- Window/layout commands: `newcol()`, `delcol()`, `del()`, `sort()`, `zeroxx()`.
- File commands:
  - `get()` reloads file content while preserving selections by line/rune coordinates when the same name is reloaded.
  - `putfile()` writes buffer ranges to disk, checks qid/dev/mtime to avoid overwriting externally modified files, rejects append-only files, updates clean state, and sends plumber `put` messages.
  - `put()`, `putall()`, `dump()`.
- Editing commands: `cut()`, `paste()`, `sendx()`, `edit()`, `undo()`.
- Search and view commands: `look()`, `fontx()`, `incl()`, `indent()`, `tab()`, `id()`, `local()`, `kill()`, `exit()`.
- `runproc()`, `runwaittask()`, and `run()` create child processes, mount Acme's namespace for them, wire stdin/stdout/stderr to Acme files depending on pipe command form, and notify the wait thread.

Important dependencies:
- Uses almost every Acme subsystem: text/file/window/layout, fsys mounting, plumber, snarf, edit parser, row dump/load, font cache.
- External execution mounts `/mnt/acme`, binds it to `/mnt/wsys` and `/dev`, sets `winid`, `%`, and optionally `acmeaddr`.

Filesystem/storage relevance:
- Major file-facing code:
  - Reads and reloads files/directories.
  - Writes Acme buffers back to disk with external-modification checks.
  - Exposes selected text and command I/O through synthetic files like `rdsel`, `wrsel`, and `editout`.
  - Uses plumber messages for close/put events.

Notes:
- `runproc()` chooses direct `procexec` for simple commands and falls back to `/bin/rc -c` for shell syntax.
- For edit commands using pipes, stdout can be directed into window `editout` to feed `edittext()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/exec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/file.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/file.c

This file implements `File` lifecycle, text-view association, undo/redo logs, name changes, and low-level buffer mutation.

Key responsibilities:
- `fileaddtext()` creates a `File` if needed and associates a `Text` view.
- `filedeltext()` removes a `Text`; closes the file when the last view is gone.
- `fileinsert()`/`filedelete()` mutate file content and record inverse operations in `delta` when undo is active.
- `fileuninsert()` and `fileundelete()` serialize undo records and deleted text.
- `filesetname()` and `fileunsetname()` change names and record undo information.
- `fileload()` loads from fd into the file buffer when undo is inactive.
- `fileredoseq()` reports the sequence number pending in redo state.
- `fileundo()` replays `delta` or `epsilon` records, updating all associated text views.
- `filereset()`, `fileclose()`, and `filemark()` reset/close/mark undo state.

Important dependencies:
- Uses `Buffer` for content and undo logs.
- Uses `textinsert()`/`textdelete()` to keep all views synchronized during undo/redo.
- Uses global `seq` for grouping simultaneous changes.

Filesystem/storage relevance:
- `File` tracks on-disk identity metadata but this file mainly handles in-memory/buffer state and undo.
- Provides the mutation layer used by text editing and disk I/O callers.

Notes:
- Undo records are stored after their associated data so the log can be read backward.
- Multiple `Text` views over the same `File` are first-class and updated together.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/fns.h

This header declares cross-module Acme functions and helper macros.

Key contents:
- Warning/error, plumbing, snarf, temp-file, scroll, font, argument, command, file, search, edit, execution, fsys, regex, allocation, address, and conversion prototypes.
- `fbufalloc()`/`fbuffree()` macros for fixed-size rune/byte work buffers.
- Rune allocation macros wrapping `emalloc`/`erealloc`.
- 9P server prototypes including `fsysinit()`, `fsysmount()`, `respond()`, xfid handlers, and log handlers.
- Address and regex helpers used by both UI and file server paths.

Filesystem/storage relevance:
- Declares the public surface for Acme's synthetic filesystem, text loading, file putting, and buffer-backed editing.

Notes:
- This file is the coupling point among otherwise separate Acme translation units.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/fsys.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/fsys.c

This file implements the front dispatcher for Acme's synthetic 9P filesystem.

Key responsibilities:
- Defines global and per-window directory tables:
  - Global: `.`, `acme`, `cons`, `consctl`, `draw`, `editout`, `index`, `label`, `log`, `new`.
  - Window: `.`, `addr`, `body`, `ctl`, `data`, `editout`, `errors`, `event`, `rdsel`, `wrsel`, `tag`, `xdata`.
- `fsysinit()` creates the server pipe, installs 9P formatting, opens `/dev/time`, sets `user`, and starts `fsysproc()`.
- `fsysproc()` reads 9P messages, allocates/reuses `Xfid` workers, decodes `Fcall`s, validates fids, and dispatches by request type.
- `fsysaddid()`, `fsysincid()`, and `fsysdelid()` manage per-mounted-command `Mntdir` records and include directories.
- `fsysmount()` mounts Acme's server on `/mnt/acme`, binds `/mnt/wsys`, and binds Acme before `/dev` for child commands.
- `fsysclose()` closes server endpoints.
- `respond()` serializes replies or errors.
- Implements core 9P operations:
  - `version`, `auth`, `flush`, `attach`, `walk`, `open`, `create`, `read`, `write`, `clunk`, `remove`, `stat`, `wstat`.
- `fsyswalk()` resolves numeric window directories, `new` window creation, global names, and per-window names.
- `fsysread()` handles directory listing and delegates file reads to xfid workers.
- `newfid()` manages a small hash table of fids.
- `dostat()` synthesizes `Dir` metadata.

Important dependencies:
- Delegates actual file open/read/write/close behavior to `xfid*` functions implemented elsewhere.
- Uses row/column/window state to enumerate windows and resolve IDs.
- Uses Qid encoding macros from `dat.h`.

Filesystem/storage relevance:
- This is the primary Acme-as-filesystem implementation. It exposes editor state as a 9P namespace and lets programs control windows via file operations.

Notes:
- `create`, `remove`, and `wstat` are denied.
- `walk` to `new` creates a new Acme window through `newwindowthread()` because graphics work must happen outside the server process context.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/fsys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/logf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/logf.c

This file implements Acme's global event log file, exposed through the synthetic namespace.

Key responsibilities:
- Defines `Log`, containing a queued event list, reader fids, blocked read xfids, sequence offset, and synchronization state.
- `xfidlogopen()` registers a fid and positions it at the current log end.
- `xfidlogclose()` unregisters a fid.
- `xfidlogread()` blocks until a new event is available or the read is flushed, then responds with one event line.
- `xfidlogflush()` marks matching blocked reads as flushed and wakes readers.
- `xfidlog(w, op)` appends an event line of the form `<winid> <op> <name>\n`, compacts events all readers have consumed, grows storage as needed, and wakes readers.

Important dependencies:
- Uses `Window`, `File`, `Fid`, `Xfid`, `respond()`, `runetobyte()`, and locking/rendezvous primitives.
- Called by window lifecycle, Get/Put, focus, and Zerox paths.

Filesystem/storage relevance:
- Provides `/mnt/acme/log` style event streaming for external programs.
- Tracks file/window operations without reading individual per-window event files.

Notes:
- Expected operations include `new`, `zerox`, `get`, `put`, `del`, and `focus`.
- Log retention is bounded by slowest active reader; when all readers advance, consumed entries are freed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/logf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/look.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/look.c

This file implements button-3 look/open behavior, plumbing integration, path expansion, search, and new-file opening.

Key responsibilities:
- `look3()` expands a clicked range, sends events to external clients if they own the window, tries plumber `send`, then falls back to internal open/search.
- `plumblook()` opens files from plumber `showfile` messages and optional address attributes.
- `plumbshow()` creates a new window from plumber `showdata` content.
- `search()` finds a rune string in a text, wrapping once, and shows/selects the match.
- `isfilec()`, `cleanrname()`, `includefile()`, `includename()`, and `dirname()` implement filename/path recognition and normalization.
- `expandfile()` identifies file names and optional Acme addresses around a click.
- `expand()` chooses file or alphanumeric expansion.
- `lookfile()` and `lookid()` locate existing windows by file name or id/dump id.
- `openfile()` opens an existing or new window, loads file content, applies address selection, copies include/indent settings from the originating window, and logs new windows.
- `new()` implements the `New` command over one or more file arguments.

Important dependencies:
- Uses address parser, text buffers, row/column/window logic, plumber, filesystem access (`access`), and file loading.

Filesystem/storage relevance:
- Central to path-to-window resolution, include search, opening files from disk, and plumber-driven file/data display.
- Recognizes `file:addr` syntax and evaluates the address in the target file.

Notes:
- Include lookup searches window include dirs, `/sys/include`, and `/<objtype>/include`.
- Directory-relative expansion derives from the window tag's file name prefix.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/look.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/regx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/regx.c

This file implements Acme's regular expression compiler and executor.

Key responsibilities:
- Defines regex VM `Inst` instructions and NFA thread-list `Ilist`.
- `rxinit()` initializes the regex compile channel and last-regexp buffer.
- `rxcompile()` compiles a rune regex into forward and backward programs, caching the last regex.
- `realcompile()` parses regex tokens into VM instructions using operator/operand stacks.
- Supports literals, `.`, `^`, `$`, grouping, alternation, concatenation, `*`, `+`, `?`, character classes, negated classes, and submatch ranges.
- Character class support: `nextrec()`, `bldcclass()`, `classmatch()`.
- VM support: `newinst()`, `operand()`, `operator()`, `evaluntil()`, `optimize()`.
- `rxexecute()` runs forward search over `Text` or rune string input.
- `rxbexecute()` runs backward search over `Text`.
- `newmatch()` and `bnewmatch()` select best forward/backward match ranges.
- `rxnull()` reports no compiled regex.

Important dependencies:
- Reads text through `textreadc()` when searching buffers.
- Reports compile/runtime warnings via `warning()` and uses a worker thread for compilation.

Filesystem/storage relevance:
- Regexes drive Acme addresses, edit commands, and search. Those operations select and mutate file-backed buffers and external file-server ranges.

Notes:
- Program size is fixed at `NPROG` instructions and active thread list at `NLIST`.
- Backward compilation reverses concatenation order, enabling reverse search rather than scanning all forward matches.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/regx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/rows.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/rows.c

This file manages the top-level Acme row, columns, session dump/load, and all-window traversal.

Key responsibilities:
- `rowinit()` initializes the row tag with `Newcol Kill Putall Dump Exit`.
- `rowadd()` inserts or creates a column, splitting horizontal space.
- `rowresize()` resizes the row and proportionally resizes columns.
- `rowdragcol()` handles column drag/reorder/resize.
- `rowclose()` removes a column and expands neighbors.
- `rowwhichcol()`/`rowwhich()` map screen points to columns/texts.
- `rowtype()` routes keyboard input to the relevant text/window under locking.
- `rowclean()` checks all columns.
- `rowdump()` writes Acme session state to a dump file:
  - working directory
  - font names
  - column percentages
  - window records
  - control state
  - tags
  - dumped body content for dirty/unnamed files
  - external command reconstruction data
- `rowloadfonts()` preloads font names from a dump file.
- `rowload()` restores columns, windows, fonts, file windows, dumped contents, Zerox relationships, external windows, selections, scroll positions, and tags from a dump file.
- `allwindows()` visits every window in every column.

Important dependencies:
- Uses `Biobuf`, file create/open, temp files, window/text/file APIs, command `run()`, and logging.

Filesystem/storage relevance:
- Implements Acme session persistence via `$home/acme.dump` by default.
- Restores real files from disk or dumped buffer contents depending on dirty/availability state.
- Uses temp files when restoring dumped window bodies.

Notes:
- Multiline tag newlines are encoded as byte `0xff` in dump files and decoded on load.
- Windows with open event files are treated specially to avoid dumping externally controlled state unless `dumpstr` is present.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/rows.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/scrl.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/scrl.c

This file implements text scrollbar drawing and mouse-driven scrolling.

Key responsibilities:
- `scrpos()` maps visible text range (`p0..p1`) onto a scrollbar rectangle within total text length.
- `scrlresize()` allocates a temporary image buffer sized for scroll drawing.
- `textscrdraw()` redraws a body's scrollbar if its position changed.
- `scrsleep()` sleeps for a duration but cancels early on mouse input.
- `textscroll()` handles button-based scrolling:
  - button 2 jumps proportionally through the file.
  - button 1 scrolls backward.
  - button 3 scrolls forward.
  - debounces initial repeated scrolling.

Important dependencies:
- Uses `Text`, draw images, timer API, mouse channel, `textbacknl()`, `frcharofpt()`, and `textsetorigin()`.

Filesystem/storage relevance:
- Indirect: scroll position controls visible ranges over file-backed `Text` buffers.

Notes:
- Large totals are shifted down to avoid arithmetic overflow in scrollbar scaling.
- Scrollbar drawing is only for window bodies, not tags.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/scrl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/text.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/text.c

This file implements Acme `Text` display, editing, selection, scrolling, completion, loading, and text-view synchronization.

Key responsibilities:
- `textinit()`, `textredraw()`, `textresize()`, and `textclose()` initialize, redraw, resize, and release text frames.
- Directory display:
  - `dircmp()` sorts directory entries.
  - `textcolumnate()` lays directory entries out in tabbed columns.
  - `textload()` loads either regular files or directories, sets file stat metadata, fills frames, handles NUL bytes, and updates all views.
- Text mutation:
  - `textinsert()` and `textdelete()` update the underlying `File` when requested, synchronize all views sharing the file, update frame contents, dirty flags, UTF cache invalidation, scrollbars, and external events.
  - `textbsinsert()` handles backspace characters in inserted streams.
  - `textcommit()` commits typed cache content to the file.
  - `textreadc()` reads from the typing cache or backing buffer.
- Keyboard editing:
  - `texttype()` handles navigation, paging, completion, ESC selection, erase-char/line/word, tab-as-spaces, autoindent, cached typing, and newline commit.
  - `textcomplete()` performs filename completion with `complete()`.
  - `textbswidth()` and helpers calculate erase extents.
- Selection and mouse:
  - `textselect()`, `textselect2()`, `textselect3()`, `textselect23()`, `xselect()`, `textstretchsel()`, and `textclickmatch()` implement click/drag/chord/double-click selection.
  - `framescroll()` and `textframescroll()` support frame-library auto-scroll during selection.
- Visibility:
  - `textshow()`, `textsetselect()`, `selrestore()`, `textbacknl()`, and `textsetorigin()` maintain visible origin and selection drawing.
- `textreset()` resets a text/file display without building undo records.

Important dependencies:
- Uses frame library, draw, completion library, buffer/file/window APIs, scroll drawing, command cut/paste, warning, and path helpers.

Filesystem/storage relevance:
- Primary bridge between loaded files/directories and visible/editable text.
- Directory windows are generated from `dirread()` results.
- Regular files are loaded through `fileload()` and stored in temp-backed buffers.
- External clients observe text insert/delete events through `winevent()` calls.

Notes:
- Typing is cached in each `Text` and committed on newline, ESC, movement, or explicit commit.
- Shared-file views are carefully updated so Zerox windows see consistent edits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/text.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/time.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/time.c

This file implements Acme's lightweight timer service.

Key responsibilities:
- `msec()` returns current time in milliseconds from `nsec()`.
- `timerstart(dt)` allocates/reuses a `Timer`, resets state, and sends it to the timer process.
- `timerstop(t)` returns a timer to the free list.
- `timercancel(t)` marks a timer canceled.
- `timerinit()` creates the timer channel and starts `timerproc()`.
- `timerproc()` tracks active timers, decrements them based on elapsed milliseconds, wakes expired timers with nonblocking sends, reclaims canceled/expired timers, and receives new timers.

Important dependencies:
- Uses Plan 9 thread channels and `sleep(1)`.
- Used by keyboard tag-commit delay and scroll sleep cancellation behavior.

Filesystem/storage relevance:
- No direct filesystem operations. It supports UI/event timing for Acme's file editor.

Notes:
- Uses nonblocking send on timer expiry to avoid deadlock with clients.
- Timer structs are recycled through a simple free list.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/time.c -->