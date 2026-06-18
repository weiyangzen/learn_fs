# Group Research: group_1607_plan9_sources_os_plan9_plan9_sys_src_cmd_rc_unix_c_sources_os_plan9_70127918ca1f

Scope confirmed against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/unix.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/unix.c

Read status: complete, 592 lines.

This is the Unix portability backend for Plan 9 `rc`. It supplies platform-specific implementations for environment import/export, command execution, signals, directory scanning, file descriptor wrappers, allocation, and wait-status handling.

Important entry points include `Vinit`, `execfinit`/`Xrdfn`, `mkenv`, `Waitfor`, `Execute`, `Opendir`/`Readdir`/`Closedir`, `Trapinit`, `execumask`, and the small wrappers around `read`, `write`, `lseek`, `dup`, `creat`, `unlink`, `malloc`, and `fork`.

Environment handling encodes multiword `rc` variables using separator byte `'\1'`, exports functions as Bourne-compatible-looking `#()fn ...` environment strings, and sorts exported variables for deterministic `execve` environments. `Execute` searches a supplied path list, retries `ETXTBSY`, and falls back to `/bin/sh` on `ENOEXEC`.

Signal logic maps Unix signals to `rc` trap names and wait statuses. `rfork` is reduced to `fork`, and waitpid tracking is implemented with a small dynamic integer list.

Filesystem relevance: this file adapts Plan 9 shell behavior to Unix directory and file descriptor APIs, especially `/dev/fd` naming, directory glob support, and environment-backed process execution.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/unix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/unix.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/unix.h

Read status: complete, 53 lines.

This header configures the Unix build environment for `rc`. It undefines and redefines feature-test macros, includes POSIX/BSD C headers, defines `NSIG` fallback, and declares Plan 9 compatibility constants and types.

It maps Plan 9 open modes to Unix `O_RDONLY`, `O_WRONLY`, and `O_RDWR`, defines `nil`, aliases Plan 9 integer typedef names, and provides no-op or compatibility definitions for `RFPROC`, `RFFDG`, `RFNOTEG`, and `OCEXEC`.

Filesystem relevance: this is the shim that lets code written against Plan 9-style file and process constants compile on Unix.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/unix.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/var.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/var.c

Read status: complete, 91 lines.

This file implements `rc` keyword and variable lookup. It maintains a small keyword hash table and the global/local variable hash table used by the interpreter.

Key functions are `hash`, `kenter`, `kinit`, `klook`, `gvlook`, `vlook`, and `setvar`. `kinit` registers language tokens such as `for`, `in`, `while`, `if`, `not`, `switch`, and `fn`. `klook` converts an input word token into a keyword token when appropriate.

`gvlook` interns global variables into `gvar`; `vlook` first searches `runq->local` and then falls back to globals. `setvar` replaces an existing word list and marks the variable changed.

Filesystem relevance: no direct filesystem logic, but variable state drives path lookup, environment export, and shell command execution.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/var.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/win32.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/win32.c

Read status: complete, 561 lines.

Despite the filename, this is a Plan 9 system-specific backend variant for `rc` in this tree. It uses Plan 9 APIs such as `/env`, `Dir`, `dirread`, `notify`, `exec`, `create`, `remove`, `seek`, and `exits`.

It initializes variables from `/env`, reads shell functions from `/env/fn#*`, updates changed variables/functions back into `/env`, executes commands by searching path entries, scans directories with `dirread`, and converts Plan 9 notes into `rc` trap counters.

Key functions include `Vinit`, `Xrdfn`, `execfinit`, `Waitfor`, `addenv`, `Updenv`, `Execute`, `Globsize`, `Opendir`, `Readdir`, `notifyf`, `Trapinit`, `Executable`, `Isatty`, and `Exit`.

There are visible debug prints in `ForkExecute`, and the file includes comments noting imperfect directory/glob behavior and terminal detection assumptions.

Filesystem relevance: heavy. It uses Plan 9’s file-backed environment, directory reads, executable stat checks, and namespace-visible `/dev/cons`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rc/win32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rdbfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rdbfs.c

Read status: complete, 437 lines.

`rdbfs` is a remote debugging filesystem. It mounts a synthetic `/proc/<proc>`-like tree backed by a serial line protocol, exposing files such as `ctl`, `kregs`, `mem`, `text`, and `status`.

The file implements a small memory-read cache keyed by address/count, with pages stored in hash buckets and recycled through a free list. Serial communication is handled in `eiaread`, which sends `r...` and `w...` commands and parses `R...` and `W...` responses.

The 9P service callbacks are `fsopen`, `fsread`, and `fswrite`. Reads and writes for `mem` and `kregs` are sent to the serial worker through `rchan`; `text` reads are served from the configured kernel text image; `ctl` accepts `kill`, `exit`, `refresh`, and `hashstats`.

`threadmain` parses options, configures the serial port, starts the serial worker, builds the synthetic tree, and mounts it before `/proc`.

Filesystem relevance: central. It is a user-level 9P filesystem that presents remote debugger state through Plan 9 file interfaces.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rdbfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/read.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/read.c

Read status: complete, 91 lines.

This is a small `read` command. It reads one line by default, or multiple lines with `-m` or `-n nlines`, from stdin or named files, writing the data to stdout.

`line` grows a buffer in 1024-byte chunks, reads byte-by-byte until newline or EOF, writes any accumulated line, and records `"eof"` status when no bytes are read. `lines` repeats `line` according to option state. `main` handles options and file opening.

Filesystem relevance: simple file input utility using `open`, `read`, `write`, and `close`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/read.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/all.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/all.h

Read status: complete, 70 lines.

This shared header for `replica` includes Plan 9 system headers and declares the replica support APIs. It defines the embedded `Avl` node, opaque AVL tree/walk types, database entry structures, and database operations.

`Entry` records a replica path plus metadata: stored name, uid, gid, mtime, mode, mark flag, and length. `Db` wraps an AVL tree and backing file descriptor.

It also declares allocation/string helpers and the reverse proto reader `revrdproto`.

Filesystem relevance: defines the metadata model used by replica database scanning and synchronization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/all.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/applychanges.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/applychanges.c

Read status: complete, 332 lines.

`replica/applychanges` pushes changes from a client tree/database to a server tree. It enumerates a proto-described client tree, compares it with the local replica database and server filesystem, detects conflicts, and copies, removes, or updates metadata.

`walk` is the main decision function. It skips excluded paths, marks database entries, detects create/create, update/remove, update/update, metaupdate/remove, and metaupdate/metaupdate conflicts, and applies additions, content changes, and metadata changes when not in dry-run mode.

After enumeration, `main` walks unmarked database entries to detect removals and remove server-side files if safe. Helpers `copyfile`, `copy1`, and `metafile` copy contents and update mode/gid/uid/mtime.

Options include dry-run/verbose behavior, uid preservation, proto selection, and exclusions.

Filesystem relevance: high. It is a two-tree synchronizer with explicit file metadata conflict checks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/applychanges.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/applylog.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/applylog.c

Read status: complete, 1235 lines.

`replica/applylog` applies a stream of replica log entries to a local tree and updates the client database. It is the most complex replica file in this group, implementing add/delete/content-change/metadata-change handling, conflict detection, forced conflict resolution, safe copying, and incremental time tracking.

The input log format is tokenized into timestamp, sequence number, operation verb, path, remote name, mode, uid, gid, mtime, and length. `main` checks each entry against the local database, local filesystem, remote filesystem, match filters, and `-s`/`-c` resolution overrides.

For `d`, it removes local files if they were not locally changed or if the resolution policy allows it. For `a`, it creates directories or copies remote files. For `c`, it updates file contents when local contents are not conflicting. For `m`, it updates metadata when local content or metadata does not conflict or is overridden.

Copying is deliberately cautious. `copytotemp` spools remote contents to a temp file and re-stats the remote file to detect changes underfoot. `copy1` uses up to `Nwork` workers with `pread`/`pwrite` offsets. `copyfile` includes a safe-install path that renames existing `bin/*` targets to `_target` before overwrite.

The `copyerr` in-memory database records transient missing/copy errors. `samecontents` compares local and remote content through a temp-spooled remote copy. `timefile` support tracks last applied log time/sequence and stops advancing when skipped changes could make later state unsafe.

`membogus` copies and re-execs `applylog` from `/tmp` to avoid overwriting itself during updates.

Filesystem relevance: central replica application engine for local filesystem mutation, remote file reads, metadata writes, conflict policy, and safe installation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/applylog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/avl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/avl.c

Read status: complete, 415 lines.

This file implements an in-memory AVL tree used by the replica database. It provides rotations, insertion, lookup, deletion, predecessor/successor walking, and iterator adjustment when nodes are deleted during traversal.

The tree stores caller-owned structs containing an embedded `Avl` node. `insertavl` replaces equal keys and returns the old node. `deleteavl` invokes `walkdel` so active `Avlwalk` iterators remain usable when their current node is deleted.

Traversal uses `avlwalk`, `avlnext`, `avlprev`, and `endwalk`. The database code relies on reverse traversal while deleting entries.

Filesystem relevance: indirect but important. It indexes replica path metadata efficiently while tools scan and mutate filesystem state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/avl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/compactdb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/compactdb.c

Read status: complete, 42 lines.

`replica/compactdb` rewrites a replica database in compact canonical form. It opens the database, walks the AVL tree in sorted order, and prints each live entry to stdout.

Removed tombstones and superseded entries are naturally omitted because `opendb` replays the append-only database into current in-memory state first.

Filesystem relevance: maintenance tool for replica metadata databases, reducing append-only log growth.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/compactdb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/db.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/db.c

Read status: complete, 181 lines.

This file implements the replica metadata database. The backing file is append-only text; `opendb` replays it into an AVL tree keyed by path. Entries have seven fields: path, stored name, mode or `REMOVED`, uid, gid, mtime, and length.

`insertdb` appends a quoted metadata line and updates the in-memory AVL. `removedb` appends a tombstone line and deletes the AVL entry. `finddb` and `markdb` retrieve metadata, with `markdb` setting the in-memory mark bit used during scans.

`allocentry` uses a small free-list allocator for `Entry` objects. String values are atomized by `util.c`, allowing shared stable pointers.

Filesystem relevance: core persistent state for replica tools, tracking file identity and metadata across synchronization runs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/db.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/revdump.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/revdump.c

Read status: complete, 40 lines.

This small utility dumps a reverse proto enumeration. Callback `enm` prints new path, mode flags, uid, gid, and old path for each enumerated file.

`main` accepts `-r root` and one proto file, calls `revrdproto`, and exits. The usage string says `protodump`.

Filesystem relevance: inspection/debug tool for proto-file expansion and metadata enumeration.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/revdump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/revproto.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/revproto.c

Read status: complete, 512 lines.

`revproto.c` implements reverse proto-file enumeration. It parses proto syntax, walks the source tree under `root`, maps paths to an external/rooted destination under `xroot`, applies uid/gid/mode overrides, and calls a callback for every enumerated file.

`revrdproto` sets up parser state and invokes `domkfs`. `getfile`, `getname`, `getmode`, and `getpath` parse indented proto entries. `mktree` expands `+` and `*` recursive/nonrecursive directory wildcards. `copyfile` stats files, adjusts default ownership and permissions, handles explicit proto metadata, and calls the supplied enumerator.

The parser uses indentation depth to model hierarchy and `skipdir` to skip nested proto regions when a directory cannot be read or statted.

Filesystem relevance: high. It is the proto traversal adapter that feeds replica scans and reverse mappings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/revproto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/updatedb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/updatedb.c

Read status: complete, 214 lines.

`replica/updatedb` scans a tree described by a proto file, compares it to a replica database, writes change log records, and optionally updates the database.

It logs additions (`a`), content changes (`c`), metadata changes (`m`), and deletions (`d`). It can emit only changes, only log output, choose root/proto, override uid, seed timestamp/sequence values, and exclude paths.

`walk` compares current `Dir` metadata with database state. After `rdproto`, `main` walks unmarked database entries and logs/removes deletions unless `-c` changes-only mode is active. `warn` treats suspected network or I/O errors as fatal to avoid logging mass deletions caused by failed remote reads.

Filesystem relevance: central scanner for generating replica update logs and maintaining client/server metadata state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/updatedb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/util.c

Read status: complete, 137 lines.

This file provides allocation helpers, string interning, and root path trimming for replica tools. `emalloc`, `erealloc`, and `estrdup` fatal on failure.

`atom` returns a canonical pointer for equal strings using a 1024-bucket hash table and chunk allocators. Atomized strings are intentionally never freed. `unroot` strips a configured root prefix and leading slashes from a path when applicable.

Filesystem relevance: supports efficient metadata storage for many repeated path, uid, and gid strings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/replica/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/resample.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/resample.c

Read status: complete, 327 lines.

`resample` is an image resizing command for Plan 9 image files. It reads a `Memimage`, computes requested width/height from absolute values or percentages, resamples with a Kaiser-windowed kernel, and writes the result.

`i0` approximates the modified Bessel function used by `kaiser`; `main` precomputes and normalizes the kernel. `resamplex` and `resampley` resize in separable passes across byte-per-channel scan lines. Unsupported compact formats are converted to RGB24 or GREY8, resampled, and converted back.

Filesystem relevance: ordinary image file I/O through `readmemimage` and `writememimage`; not a filesystem component.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/resample.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/dat.h

Read status: complete, 342 lines.

This is `rio`’s central data header. It defines synthetic 9P qid identifiers, window control message constants, channel message structs, mouse state queues, the `Window`, `Fid`, `Xfid`, `Filsys`, and `Timer` structs, and the major global variables.

`Window` embeds `Ref`, `QLock`, and `Frame`, and owns images, mouse/keyboard/control channels, text buffers, selection state, raw input buffers, geometry, process identity, cursor state, label, and working directory.

`Filsys` tracks pipe fds, user name, xfid allocator channel, and fid hash buckets. `Xfid` wraps an in-flight 9P request and flush synchronization state.

Filesystem relevance: foundational for `rio`’s synthetic `/dev` filesystem and window-as-file model.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/data.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/data.c

Read status: complete, 180 lines.

This file defines `rio` cursor bitmap data and initializes basic drawing images. It includes crosshair, box, sight, white arrow, query, and edge/corner resize cursors, plus the `corners` table used to pick resize cursors by border region.

`iconinit` allocates the background and red single-pixel images used by the window manager.

Filesystem relevance: no file I/O; supports interactive window management visuals.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/fns.h

Read status: complete, 35 lines.

This header declares cross-file functions for `rio`, including window control parsing, new window creation, cursor setting, allocation helpers, snarf handling, timer initialization, scrollbar helpers, and basic min/max/string/rune utilities.

It also defines `runemalloc`, `runerealloc`, and `runemove` macros.

Filesystem relevance: ties together the synthetic filesystem, window operations, and utility layers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/fsys.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/fsys.c

Read status: complete, 700 lines.

`fsys.c` implements `rio`’s 9P filesystem server. It exposes window files such as `cons`, `consctl`, `cursor`, `kbdin`, `label`, `mouse`, `screen`, `snarf`, `text`, `wdir`, `wctl`, `window`, and `wsys`.

`filsysinit` creates close-on-exec pipes, posts `/srv/riowctl.*` and `/srv/rio.*`, starts the wctl and filesystem processes, and records the current user. `filsysproc` reads 9P messages, decodes them, allocates an `Xfid`, finds or creates fids, and dispatches through the `fcall` table.

`filsyswalk` handles ordinary directory entries and `wsys/<id>` window directories. Directory reads synthesize Plan 9 `Dir` records with `dostat`, including sorted window ids for `/dev/wsys`.

Unsupported operations such as create, remove, wstat, and auth are denied. Version negotiation sets the global 9P message size.

Filesystem relevance: central implementation of `rio`’s window namespace.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/fsys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/rio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/rio.c

Read status: complete, 1191 lines.

This is the main `rio` window manager program. It initializes display, mouse, keyboard, screen, background, timers, global channels, synthetic filesystem service, optional startup command, optional keyboard window, and then waits for exit.

It handles snarf import/export, startup command execution, shutdown notes, killing child process groups, keyboard dispatch, mouse dispatch, screen resize, button menus, sweeping new windows, moving/resizing by drag bands, hiding/unhiding, deleting, and creating windows.

Button 3 drives global window operations; button 2 drives per-window cut/paste/snarf/plumb/send/scroll actions. Mouse handling decides when to send events into a client window versus when to top, move, resize, scroll, or invoke menus.

`new` constructs a `Window`, starts its control thread, optionally starts a shell through `winshell`, and records pid/label/working directory.

Filesystem relevance: orchestrates the `rio` filesystem server and creates the windows whose state is exposed as `/dev` files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/rio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/scrl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/scrl.c

Read status: complete, 183 lines.

This file implements window scrollbar drawing and scrollbar interaction. `scrpos` maps visible text range to scrollbar thumb rectangle, with scaling for very large buffers. `wscrdraw` redraws the scroll gutter using a temporary image.

`wscroll` handles button-specific scrolling: button 2 maps thumb position proportionally to buffer origin; button 1 and button 3 scroll by line/page-like positions. `wscrsleep` uses the timer subsystem and mouse movement to pace repeated scrolling.

Filesystem relevance: no filesystem logic, but it controls visual navigation over the text exposed through window files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/scrl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/time.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/time.c

Read status: complete, 124 lines.

This file provides a small timer service for `rio`. `timerinit` creates a channel and starts `timerproc`; `timerstart` allocates or reuses a `Timer`, sets duration, and sends it to the timer process. `timercancel` marks a timer canceled; `timerstop` returns it to a free list.

`timerproc` tracks active timers, decrements them based on millisecond time from `nsec`, sends nonblocking expiration notifications, handles cancellation, and receives newly scheduled timers.

Filesystem relevance: no direct filesystem logic; supports UI timing such as scrollbar repeats.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/time.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/util.c

Read status: complete, 149 lines.

This utility file provides UTF conversion, fatal error handling, allocation helpers, rune classification/search, min/max, and rune-to-byte conversion.

`cvttorunes` converts byte buffers into runes while eliding NULs and reporting them. `runetobyte` allocates a UTF-8 byte string from a rune slice. `isalnum` is intentionally broad for non-ASCII characters to support word selection.

Filesystem relevance: supports text conversion for `/dev/cons`, `/dev/text`, `/dev/snarf`, and other byte-oriented window files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/wctl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/wctl.c

Read status: complete, 515 lines.

`wctl.c` parses and applies `rio` window control commands. It supports commands such as `new`, `resize`, `move`, `scroll`, `noscroll`, `set`, `top`, `bottom`, `current`, `hide`, `unhide`, and `delete`, with parameters for rectangle, pid, id, hidden state, scrolling state, and working directory.

`parsewctl` tokenizes command strings and computes the target rectangle. `goodrect` enforces minimum, canonical, and manageable window geometry. `writewctl` applies commands written to a window’s `wctl` file. `wctlproc` reads commands from the global wctl pipe and `wctlthread` applies global `new` requests.

Filesystem relevance: this is the command parser behind `/dev/wctl` and the global `/srv/riowctl.*` interface.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/wctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/wind.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/wind.c

Read status: complete, 1699 lines.

`wind.c` implements the `Window` object and most per-window behavior. It creates windows, manages frame drawing, text buffers, selections, command editing, raw/hold modes, console read/write coordination, mouse selection, scrolling, resize/move/delete messages, process note delivery, shell startup, double-click matching, and history trimming.

`wmk` constructs a `Window` with channels and frame geometry. `winctl` is the per-window event loop, multiplexing keyboard, mouse, console reads/writes, mouse reads, and `wctl` reads. It buffers console output into the window text, services shell input reads line-by-line or raw, queues mouse events, and reports window geometry/state to `wctl` readers.

Editing support includes filename completion, erase character/word/line handling, interrupt delivery to `/proc/<pid>/notepg`, snarf/cut/paste, plumbing, double-click bracket/quote/word selection, visible-origin tracking, selection repainting, and high-water trimming of window history.

Lifecycle functions include `wresize`, `wclose`, `wclosewin`, `wsetpid`, and `winshell`, which mounts the per-window filesystem before executing a shell.

Filesystem relevance: central. It provides the backing state and synchronization semantics for `rio`’s per-window files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/wind.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/xfid.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/xfid.c

Read status: complete, 846 lines.

`xfid.c` maps decoded 9P requests onto `rio` window operations. It manages a pool of `Xfid` worker threads, request flushing, attach/open/close/read/write behavior, and byte-level handling for synthetic files.

`xfidattach` attaches to an existing window id or creates a new window from old `N...` or new `wctl` syntax. `xfidopen` enforces single-open rules for `consctl`, `mouse`, and readable `wctl`. `xfidclose` resets raw/hold/mouse/cursor/snarf state on close.

`xfidwrite` implements writes to `cons`, `consctl`, `cursor`, `label`, `mouse`, `snarf`, `wdir`, `kbdin`, and `wctl`. It handles partial UTF runes for console writes and appends snarf data until close commits it.

`xfidread` implements reads from `cons`, `label`, `mouse`, `snarf`, `text`, `wdir`, `winid`, `winname`, `window`, `screen`, and `wctl`. Image reads return a textual header followed by raw image bytes. Long-running reads support 9P flush via `flushtag` and per-request channels.

Filesystem relevance: direct implementation of most file read/write semantics in `rio`’s synthetic namespace.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rio/xfid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rm.c

Read status: complete, 102 lines.

This is the Plan 9 `rm` command. It supports `-r` recursive removal and `-f` ignore-errors behavior.

`main` attempts `remove` on each argument. If that fails and `-r` is set on a directory, `rmdir` recursively reads all entries, first tries to remove each child, then recurses into child directories that could not be removed directly, and finally removes the parent.

Errors are stored in `errbuf` and printed unless `-f` is active; the process exits with `errbuf`.

Filesystem relevance: direct filesystem mutation utility for file and recursive directory deletion.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/rx.c

Read status: complete, 266 lines.

`rx` runs a command on a remote host. It tries Plan 9 `rexexec` authentication using `p9any` and `p9sk2`, then SSH, then TCP shell service. It forwards stdin to the remote connection in a child process and writes remote output to stdout.

Options control EOF sending, CR-to-NL conversion, CR stripping, auth key pattern, and remote username. `tcpexec` implements BSD-style shell authentication, `rex` uses `auth_proxy`, and `sshexec` execs `/bin/ssh`.

Filesystem relevance: network/process utility rather than filesystem code, but it is used by `sam` remote startup paths and interacts with file descriptors/pipes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/rx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/address.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/address.c

Read status: complete, 240 lines.

This file evaluates `sam` addresses. It supports character and line addresses, dot, end-of-file, mark, forward/backward regexp search, file-name matching, whole-file selection, comma/semicolon ranges, and relative `+`/`-` movement.

`nextmatch` compiles and executes regexps with wrap behavior for zero-length matches. `matchfile` and `filematch` match file menu entries against a regexp. `charaddr` and `lineaddr` implement bounds-checked character and line range movement.

Filesystem relevance: editor addressing over in-memory file buffers; indirect filesystem relation through file selection by name/menu.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/address.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/buff.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/buff.c

Read status: complete, 302 lines.

`buff.c` implements `sam`’s block-based rune buffer on top of a temporary disk store. A `Buffer` maintains block pointers plus a cached block that is flushed to disk when dirty or empty.

`bufinsert` inserts runes, growing or splitting blocks as needed. `bufdelete` removes ranges. `bufload` reads bytes from a file descriptor, converts UTF to runes while handling partial runes and NULs, and inserts into the buffer. `bufread`, `bufreset`, and `bufclose` provide range reads and cleanup.

The implementation avoids keeping whole edited files in contiguous memory and uses `Maxblock`-sized chunks backed by `disk.c`.

Filesystem relevance: core editor storage layer for file contents, backed by a temporary file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/buff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/cmd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/cmd.c

Read status: complete, 607 lines.

This file parses `sam` commands. `cmdtab` defines command characters, whether they take text/regexp/address/count/token operands, default commands, default addresses, and executor functions.

Input can come from stdin or the downloaded terminal protocol. `inputc`, `inputline`, `getch`, `ungetch`, `skipbl`, and `getnum` implement rune-aware command input. `cmdloop` repeatedly parses and executes commands, updating the terminal state when downloaded.

`parsecmd` parses addresses, command names, nested `{}` blocks, regexps, substitution RHS text, command text blocks, and tokens. `getregexp`, `simpleaddr`, and `compoundaddr` implement regexp reuse and address grammar.

Temporary parse objects are tracked in `List` instances and freed by `freecmd`.

Filesystem relevance: controls editor commands that eventually read, write, and modify files, but this file is parser logic rather than direct I/O.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/disk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/disk.c

Read status: complete, 118 lines.

`disk.c` manages the temporary disk file used by `sam` buffers. `diskinit` creates an ORCLOSE/OCEXEC temp file under `/tmp` with a pid/user-derived name.

Blocks are allocated in size buckets rounded by `Blockincr`. `disknewblock` reuses bucket free lists or allocates new block descriptors in chunks. `diskrelease` returns blocks to free lists. `diskwrite` may reallocate a block if its rounded size class changes, then writes runes with `pwrite`; `diskread` reads runes with `pread`.

Filesystem relevance: direct temp-file-backed storage allocator for editor buffers and undo logs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/disk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/error.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/error.c

Read status: complete, 144 lines.

This file maps `sam` error and warning enums to user-facing messages. `error`, `error_s`, `error_r`, and `error_c` format fatal command errors and pass them to `hiccough`. Warning functions print terminal warnings with string or `String` arguments.

`termwrite` writes messages either into the downloaded command file state or directly to fd 2, depending on whether the graphical terminal is connected.

Filesystem relevance: indirect; includes I/O error messages and routes diagnostics through terminal/file buffers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/error.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/errors.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/errors.h

Read status: complete, 65 lines.

This header defines the `Err` and `Warn` enums used by `sam` diagnostics. The enum order matches the message arrays in `error.c`.

Errors include open/create/I/O failures, parser errors, address/search/regexp errors, command execution failures, dirty-file conditions, temp overflow, append-only writes, plumbing failures, and buffer-load failures. Warnings include duplicate names, missing files, date conflicts, NUL elision, pwd failure, missing final newline, and bad exit status.

Filesystem relevance: enumerates file and buffer failure conditions used across the editor.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/errors.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/file.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/file.c

Read status: complete, 610 lines.

`file.c` implements `sam`’s `File` object, edit logging, undo/redo, name changes, dot/mark logging, buffer loading, update synchronization, and cleanup.

Undo records are stored backward in `delta` and `epsilon` buffers, with associated inserted text or filenames preceding each `Undo` structure. `loginsert` and `logdelete` merge nearby edits into one undo record through `merge`. `filemark` snapshots sequence, dot, mark, and modification state before a new edit sequence.

`fileundo` reverses `delta` or `epsilon` records, applying deletes, inserts, filename restores, dot restores, and mark restores while syncing terminal state through rasp calls. `fileupdate` flushes pending merge state and applies logged changes to the file buffer and UI.

`filesetname`, `fileunsetname`, `fileload`, `filereadc`, `filereset`, and `fileclose` provide file lifecycle operations.

Filesystem relevance: core editor abstraction for file contents and metadata, backed by buffers and eventually used by disk/file I/O.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/io.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/io.c

Read status: complete, 279 lines.

`io.c` handles `sam` file read/write and terminal startup I/O. `checkqid` warns about multiple open files with the same underlying qid. `writef` writes the addressed range to disk, checking for stale file changes, append-only files, final newline, and updating clean sequence/stat metadata.

`readio` reads from `io` into either an unread file via `bufload` or an existing file through UTF conversion and `loginsert`. It records dev/qid/mtime when requested and warns about NULs. `writeio` converts runes to bytes in blocks and writes them.

`bootterm`, `connectto`, and `startup` set up local or remote `samterm`, using pipes and `rx` for remote execution.

Filesystem relevance: direct file read/write path for `sam`, including stale-file protection, append-only detection, qid tracking, and remote terminal process plumbing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/list.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/list.c

Read status: complete, 96 lines.

This file implements a small generic dynamic list abstraction used by `sam` for position lists and pointer lists. `growlist` allocates or extends capacity by `INCR`. `inslist` inserts a `Posn` or pointer with varargs. `dellist` removes an element. `listalloc` and `listfree` manage list lifetime.

Filesystem relevance: no direct filesystem logic, but used by editor state such as file lists, parse object lists, and ranges.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/list.c -->