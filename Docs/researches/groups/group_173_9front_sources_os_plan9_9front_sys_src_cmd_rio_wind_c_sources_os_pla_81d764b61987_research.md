# Group Research: group_173_9front_sources_os_plan9_9front_sys_src_cmd_rio_wind_c_sources_os_pla_81d764b61987

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/wind.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rio/wind.c

`wind.c` is rio's core per-window implementation. It owns window lookup, z-ordering, current-input transitions, cursor selection, frame resizing/redrawing, text history storage, selections, scrolling, keyboard editing, mouse selection/chording, completion, and shell startup.

The window text model is a rune buffer with visible frame state. `winsert`, `wdelete`, `wfill`, `wsetorigin`, and `wshow` maintain the backing buffer, frame contents, origin, host read point `qh`, and selection positions. History is bounded by `HiWater`/`LoWater`, trimming old text when appending output at the tail.

The control path is centered on `winctl`, a threaded event loop using `Alt` over keyboard, mouse, cons read/write, wctl read, completion, and control-message channels. `wctlmesg` handles resize/repaint/refresh/move/raw/hold/truncate/delete/exit transitions and frees all per-window resources on `Exited`.

Input behavior is split between local rio editing and client-visible device state. Keyboard navigation works when client mouse/kbd devices are not open; raw mode queues runes directly for `/dev/cons`; hold mode suppresses cons reads; delete sends an interrupt note via `/proc/.../notepg`.

Mouse behavior includes selection, double/triple-click expansion over words, whitespace regions, lines, and bracket pairs, scroll bar handling, cut/paste chords, and cursor movement conversion from window to screen coordinates.

Filename completion is asynchronous: `namecomplete` computes a directory/path prefix, starts `completeproc`, and `winctl` consumes `Completion` results by inserting completions or displaying candidates in the window text.

`wmk`, `wresize`, `wsetname`, `wclose`, `wclunk`, and `winshell` connect the graphical window, rio file server mount, reference counting, shell process launch, `/dev/cons` setup, and cleanup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/wind.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/xfid.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rio/xfid.c

`xfid.c` implements rio's per-request 9P file operation workers. It maps file server operations onto window state and global rio devices, including `/dev/cons`, `/dev/text`, `/dev/mouse`, `/dev/kbd`, `/dev/wctl`, `/dev/snarf`, `/dev/window`, `/dev/screen`, labels, cursor data, working directory, winid, winname, and tap channels.

`xfidinit`, `xfidallocthread`, and `xfidctl` maintain a reusable pool of `Xfid` request workers. Each worker receives a handler function, sets `flushtag`, runs the operation, then decrements its refcount and returns to the free list.

`xfidflush` synchronizes Plan 9 flush requests with in-flight workers. It locates the matching old tag, arranges cancellation via `flushc`, releases the file server flush gate, and either cancels or responds to the flush.

`xfidattach` interprets attach names for existing window IDs, `none`, legacy `N...` geometry, and `new...` wctl-style window creation. It validates rectangles, allocates visible or hidden images, and binds the Fid to a `Window`.

Open/close manage single-open state for control, keyboard, mouse, wctl, and tap files. Closing `Qconsctl` drops raw/hold mode; closing `Qmouse` refreshes the window; closing writable `Qsnarf` converts temporary bytes into the global rune snarf buffer.

`xfidwrite` handles text/cons writes with UTF partial-rune carry, consctl commands (`holdon/off`, `rawon/off`), cursor binary data, label replacement, synthetic mouse movement, snarf append, window directory changes, wctl commands, and tap forwarding.

`xfidread` services blocking cons/kbd/mouse/wctl reads through window channels with flush/deletion races, and simple reads for label, snarf, text, wdir, winid, winname, image headers/pixels, and screen pixels. `readwindow` handles offset reads from image data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rio/xfid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/riow.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/riow.c

`riow.c` is a keyboard-driven rio window controller and virtual desktop helper. It reads keyboard messages from stdin, filters Mod4-based shortcuts, writes unhandled key events to stdout, and controls rio through `/dev/wsys/*/wctl`.

It models windows as `W` records with rio ID, rectangle, virtual desktop number, flags for visible/current/sticky/fullscreen, and a forced-sticky bit. `wsupdate` enumerates `/dev/wsys`, reads each window's `wctl`, preserves prior virtual desktop metadata, detects current/visible status, and marks sticky windows by label.

Supported actions include spawning a new `window`, toggling fullscreen by saving/restoring geometry, toggling sticky, deleting the current window, moving/resizing with arrow keys, directional window cycling, switching desktops, and moving the current window to another desktop.

Desktop switching hides visible non-sticky windows from the old desktop, unhides windows assigned to the target desktop, restores the remembered current window per desktop, tops/current-marks it, and writes the active desktop number to fd 3.

`process` parses raw `/dev/kbd` messages, tracks modifier state from `k`/`K` events, applies shortcuts only when Mod4 is held, and preserves non-consumed key messages exactly enough for downstream consumers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/riow.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rm.c

`rm.c` is Plan 9's `rm` command with `-f` and `-r`. The main loop first tries `remove` directly and, if recursive mode is enabled and the target is a directory, calls `rmdir`.

`rmdir` opens a non-empty directory, reads all entries with `dirreadall`, tries to remove each child directly, records remaining child directories, recursively removes those directories, and finally removes the original directory.

Errors are reported through `err`, which respects `ignerr` from `-f` and stores the last system error in `errbuf`. The program exits with `errbuf`, so a successful run exits cleanly and failures carry the last error string.

The implementation avoids recursing into entries that were removed successfully by rewriting their `qid.type` to `QTFILE`, then only recursing through entries still marked `QTDIR`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rotate.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rotate.c

`rotate.c` reads a Plan 9 image, rotates or flips it in memory, and writes the transformed image to stdout. It uses `memdraw` and operates on `Memimage` objects.

`rot90` rotates an image 90 degrees clockwise by allocating a destination image with swapped dimensions and copying each pixel's bytes into the transposed/reversed position. Low-bit grayscale formats (`GREY1`, `GREY2`, `GREY4`) are temporarily expanded to `GREY8`, then converted back to the original channel.

`upsidedown` vertically flips an image in place by swapping scanlines using a temporary line buffer.

Command options are `-r degree`, `-u`, and `-l`. Rotation is implemented by fall-through cases for `270`, `180`, and `90`, applying `rot90` repeatedly. `-l` combines vertical inversion with `180` degrees, producing the complementary orientation behavior expected by the tool.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rotate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/rx.c

`rx.c` runs a command on a remote host, trying multiple remote execution protocols. It builds a shell command string from argv, dials the target service, authenticates where needed, relays stdin to the remote side in a child, and copies remote output to stdout.

Connection order is Plan 9 `rcpu`, Plan 9 `rexexec`, SSH if an SSH port is reachable, then TCP `shell`. `call` builds network addresses with `netmkaddr` and `dial`.

`rcpu` authenticates with `auth_proxy` using p9any, wraps the connection in TLS with a PSK derived from the auth secret, sends an `rx` service request, then relays data. `rex` also uses p9any auth, then writes the command as a NUL-terminated string.

`tcpexec` implements old BSD-style shell authentication by sending local user, remote user, and command strings, then reading an authentication status byte and streaming output. It optionally converts or strips carriage returns.

`sshexec` execs `/bin/ssh`, preserving `-r` and remote user options when applicable. `send` forks a stdin-forwarder and optionally writes a zero-length EOF marker when stdin closes.

Options control EOF behavior (`-e`), carriage-return handling (`-T`, `-r`), auth key pattern (`-k`), and remote user (`-l`).
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/rx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/address.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/address.c

`address.c` evaluates sam address syntax into concrete file ranges. It supports character addresses, line addresses, dot, end of file, mark, forward/backward regex search, file-name regex selection, whole file, compound comma/semicolon ranges, and relative `+`/`-` movement.

`address` walks an `Addr` parse tree and updates both the current `Address` and the current file where required. Semicolon ranges set dot after evaluating the left side, matching sam's address semantics.

`nextmatch` compiles the regex and runs forward `execute` or backward `bexecute`, avoiding zero-length self-matches at the starting position by advancing/wrapping and retrying.

`matchfile` and `filematch` implement quoted file-address matching against the menu-style representation of open files. They build a temporary menu line containing modified state, rasp state, current-file marker, and filename, then run the regex against that synthetic file.

`charaddr` applies absolute or relative rune-position addressing and checks bounds. `lineaddr` maps line counts to ranges by scanning file runes and handles forward/backward movement, line zero, EOF, and range validation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/address.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/buff.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/buff.c

`buff.c` implements sam's text buffer abstraction over temp-file-backed disk blocks. A `Buffer` stores total rune count, an array of `Block*`, and one mutable in-memory cache window.

`setcache` locates and loads the disk block containing a requested position, flushing dirty cached contents first. It preserves append-at-end locality where possible.

`bufinsert` inserts runes by using the current cache if the result fits, allocating new blocks at cache boundaries, or splitting a block when insertion occurs in the middle and the block would overflow `Maxblock`.

`bufdelete` removes a range by repeatedly loading the affected cache block, shifting remaining cache contents left, shrinking the block, and adjusting total rune count. Empty dirty blocks are dropped on flush.

`bufload` reads bytes from a file descriptor, handles partial UTF sequences across reads, converts bytes to runes with `cvttorunes`, elides NULs, and inserts runes into the buffer.

`bufread`, `bufreset`, and `bufclose` provide range reads, destructive reset with block release, and final cleanup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/buff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/cmd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/cmd.c

`cmd.c` is sam's command reader and parser. `cmdtab` defines the command language: command character, whether it accepts text/regex/address/count/token arguments, default command/address, and execution function.

Input comes from command-buffer replay, the downloaded terminal protocol, or stdin. `inputc`, `inputline`, `getch`, `nextc`, and `ungetch` provide rune-level parsing, while `cmdloop` repeatedly parses, executes, updates files, and synchronizes the terminal.

The parser builds `Cmd`, `Addr`, and `String` objects into temporary lists so `freecmd` can release all parse artifacts after each command.

`parsecmd` handles addresses, command lookup, two-character `cd`, regex arguments, substitution right-hand sides, destination addresses for move/copy, default nested commands, text collection, token collection, braced command groups, and newline validation.

`getregexp` preserves the last non-empty regex as sam's implicit pattern. `simpleaddr` and `compoundaddr` parse address syntax and insert implicit `+` where sam grammar requires it between adjacent address terms.

The command input path also integrates with downloaded `samterm`: `termcommand` copies new command-file text into `termline`, and `cmdloop` unlocks terminal UI state and emits pattern/current-file updates.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/disk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/disk.c

`disk.c` provides sam's temporary storage allocator for buffer blocks. It creates an ORCLOSE temp file under `/tmp` and assigns byte offsets within that file to `Block` descriptors.

Blocks are bucketed by rounded size using `Blockincr`, with `Maxblock` as the largest supported block. `ntosize` maps a rune count to an allocation size and free-list bucket.

`disknewblock` reuses a block from the right free list or allocates `Block` descriptors in chunks of 100. New disk space is append-only within the temp file and checked for address overflow.

`diskrelease` returns a block to the appropriate free list. `diskwrite` rewrites a block in place if the rounded size is unchanged or reallocates a block if the size class changed. `diskread` validates the requested size and reads runes from the block's temp-file address.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/disk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/error.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/error.c

`error.c` maps `Err` and `Warn` enum values to user-facing sam diagnostics and provides formatted error/warning helpers.

Fatal editor errors call `hiccough`, which unwinds the current command, rolls back in-progress edits, updates the terminal, and longjmps back to the main command loop. Variants include plain enum errors, string-argument errors, rune-command errors, and system-error-enhanced errors.

Warnings print to the command/terminal output through `dprint` and do not unwind command execution.

`termwrite` is the common output path. In downloaded mode it inserts text into the command file buffer and advances `cmdptadv`; otherwise it writes directly to fd 2. This keeps diagnostics visible in `samterm`'s command window.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/error.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/errors.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/errors.h

`errors.h` defines sam's `Err` and `Warn` enums. The enum order is significant because `error.c` indexes static message tables by these values.

`Err` includes open/create/menu/modified/I/O/write-sequence errors, command-character errors, delimiter and operand errors, address/search/regex/substitution/range/order errors, command execution and pipe errors, dirty-file exit checks, file-search ambiguity, temporary-file overflow, append-only writes, plumbing failures, and buffer-load failures.

`Warn` covers duplicate names/files, missing files, possible stale writes, NUL elision, current-directory lookup failure, missing final newline, and non-empty shell command exit status.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/errors.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/file.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/file.c

`file.c` layers sam file semantics over `Buffer`: file naming, modification state, undo/redo logs, edit merging, dot/mark state, and terminal rasp synchronization.

Undo records are stored backwards in `delta` and `epsilon` buffers as `Undo` structs, optionally preceded by associated rune data. This allows reversing the most recent grouped edit by reading from the end.

`loginsert` and `logdelete` log edits, merge nearby changes into a `Merge` accumulator, enforce sequence ordering through `hiposn`, and mark files dirty. `flushmerge` emits pending merged insert/delete records.

`logsetname`, `fileunsetname`, `fileunsetdot`, and `fileunsetmark` log metadata changes so file names, dot, and mark participate in undo/redo.

`fileupdate` flushes merged edits, records dot/mark state, runs redo-style application from `epsilon` into the main buffer and rasp, and updates dirty/close state. `fileundo` performs both undo and redo depending on which transcript is treated as source and whether reverse records are emitted.

`fileload`, `filereadc`, `filesetname`, `fileclose`, `filereset`, and `filemark` provide file lifecycle, character access, initial load, and per-command sequence checkpointing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/io.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/io.c

`io.c` handles file I/O and startup of local or remote `samterm`.

`writef` writes the selected address range to the filename in `genstr`, checks for stale same-name files by device/qid/mtime, rejects append-only targets with existing length, updates clean sequence and file identity after write, and warns about missing final newline.

`readio` loads bytes from `io` into a `File`, either via `bufload` for unread files or by streaming through `loginsert` for existing files. It converts UTF, elides NULs, records file identity, and can load the terminal rasp.

`writeio` writes a file range by reading rune chunks, converting them to bytes, and writing them to `io`. `closeio` closes the descriptor and reports byte/rune count.

`bootterm` starts `samterm` locally using two pipes or execs it over already-connected remote fds. `connectto` starts a remote `sam` via `rx machine rsamname -R ...`, wiring pipes so host and terminal can speak the sam protocol.

`startup` coordinates remote connection, local terminal boot unless `-R`, marks the session downloaded, and sends the protocol version.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/list.c

`list.c` is a small generic growable-list implementation used throughout sam for pointer lists and position lists.

`growlist` lazily allocates storage in `INCR` chunks and expands when full, zeroing the new tail. List type `'p'` stores `void*`; type `'P'` stores `Posn`.

`inslist` inserts at an index using varargs to receive either a pointer or `Posn`, shifts later entries right, and increments `nused`.

`dellist` removes an indexed element, shifts later entries left, and decrements `nused`. `listalloc` creates an empty typed list; `listfree` frees storage and the list object.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/mesg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/mesg.c

`mesg.c` is the host-side sam protocol engine. It receives `Tmesg` records from `samterm`, mutates host files, and emits `Hmesg` records back to the terminal.

`rcv` incrementally parses message headers and payloads from stdin. `inmesg` dispatches terminal messages including version negotiation, command-file start, file binding/start/work selection, data requests, origin requests, typed inserts, cuts, paste/snarf, new files, writes, closes, look/search/send, double/triple-click expansion, snarf exchange, plumb, custom menu commands, ack, and exit.

The file-data protocol is lazy: terminal rasps may contain holes; `Trequest` asks the host for a range, and the host replies with `Hdata`. `Hcheck`/`Hcheck0` and `Hack` provide consistency and flow control.

`snarf` copies file ranges into a `Buffer`. `setgenstr` populates `genstr` from a range or from the snarf buffer, enforcing `TBLOCKSIZE`.

Outbound helpers (`outT0`, `outTs`, `outTslS`, etc.) serialize host messages into `outdata`; `outflush` sends buffered data and waits for `Tack` when flow-control thresholds are hit.

Plumbing support packages selected text or clicked word into a `Plumbmsg`, preserving working directory and click offset, then sends the packed message to the terminal for delivery.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/mesg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/mesg.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/mesg.h

`mesg.h` defines the sam host-terminal wire protocol. `VERSION` is 4, reflecting plumbing, larger snarf buffers, triple click, and `M` menu-command support.

It defines message size constants: `TBLOCKSIZE` for largest text piece sent to the terminal, `DATASIZE` for encoded packet capacity, and `SNARFSIZE` for exchanged snarf text.

`Tmesg` enumerates terminal-to-host messages for versioning, file/window start, check/request/origin, typing/cut/paste/snarf/write/close/look/search/send, click expansion, snarf exchange, acks, exit, plumbing, and custom menu commands.

`Hmesg` enumerates host-to-terminal messages for versioning, menu/file binding/current/name movement, rasp grow/cut/data/check/origin, unlocks, dot/moveto, clean/dirty state, close, snarf, ack, exit, plumb, and custom menu updates.

The trailing comment records a protocol model for the grow/data/check/request interaction and notes a Spin proof for lack of non-progress cycles.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/mesg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/moveto.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/moveto.c

`moveto.c` handles host-side selection movement, terminal dot notifications, origin selection, and double/triple-click expansion.

`moveto` updates a file's dot range and, if the file is bound to a terminal rasp, sends `Hsetdot`/`Hmoveto` behavior through `telldot` and `outTsl(Hmoveto, ...)`.

`telldot` suppresses redundant dot messages by comparing host dot with terminal-known `tdot`. `tellpat` sends the last regex to the terminal search menu and clears `patset`.

`lookorigin` computes a useful terminal origin near a requested position and line count, scanning backwards up to a bounded character count to avoid pathological long lines.

The file-local `isalnum`, `isspace`, `inmode`, `clickmatch`, `strrune`, and `stretchsel` implement sam's click selection expansion across bracket pairs, quoted strings, newlines, words, and non-whitespace regions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/moveto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/multi.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/multi.c

`multi.c` manages sam's global list of open files and the terminal file menu metadata.

`newfile` creates a `File`, inserts it into the menu list, assigns a protocol tag, and emits `Hnewname` when downloaded. `delfile` removes a file, emits `Hdelname`, and closes file resources.

`fullname`, `fixname`, and `sortname` normalize paths relative to `curwd`, clean names, shorten names by stripping the current directory prefix, maintain sorted menu order, and warn on duplicate names.

`state` transitions a file between clean and dirty display states, sends `Hclean`/`Hdirty` as needed, clears unread state, and avoids marking the command file.

`lookfile` searches the open file list by exact `String` filename.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/multi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/parse.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/parse.h

`parse.h` defines sam's parsed command/address structures and command-table metadata.

`Addr` represents address parse nodes: type, optional regex or left-side address, numeric argument, and next/right-side pointer. `Cmd` represents commands with an address, regex, command/text/address union argument, command-list chaining, numeric argument, flag, and command code.

`Cmdtab` describes each command's grammar and execution function: command character, text/regex/address/count/token requirements, default nested command, default address behavior, and function pointer.

`Defaddr` defines default-address classes: no address, dot, or whole file. The header also declares all command implementation entry points and parser/evaluator helpers used across `cmd.c`, `address.c`, and `xec.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/parse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/plan9.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/plan9.c

`plan9.c` holds Plan 9-specific constants and utility functions for sam.

It defines the synthetic command-file name, click-selection delimiter tables, executable paths (`samterm`, `rx`, shell), environment names, temp directory, and rescue command path.

`dprint`, `print_s`, and `print_ss` route formatted output through `termwrite`. `statfile` and `statfd` extract Plan 9 file identity, mtime, length, and append-only flag from `Dir` data.

`notifyf` handles notes: closed-pipe writes are optionally continued, interrupts continue, and other notes trigger rescue before default handling. `waitfor` waits for a specific child PID and returns its exit status message.

`samerr` constructs the downloaded-mode stderr file path. `emalloc` and `erealloc` are panic-on-failure allocation wrappers that set malloc tags.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/plan9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/rasp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/rasp.c

`rasp.c` maintains the host-side model of which file ranges the terminal knows. A rasp is a list of spans; the high bit marks spans resident in the terminal.

`raspload`, `raspstart`, `raspdone`, and `raspflush` bracket edit batches, coalesce grow/cut messages, emit `Hcheck0`, and use `outflush` for protocol flow control.

`raspdelete` updates dot/mark/cmd point positions, coalesces shrink notifications, sends `Hcut` when needed, and removes ranges from the rasp. `raspinsert` updates dot/mark/cmd point positions, grows the rasp, and either sends `Hgrow` or `Hgrowdata` depending on size and whether the insertion lands in terminal-known text.

`rcut`, `rgrow`, `rterm`, and `rdata` are low-level span-list operations. They split, merge, mark, and query terminal-known ranges while preserving the total file-length mapping.

This file is central to sam's lazy screen data protocol: the terminal can render known spans immediately and request missing spans later.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/rasp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/regexp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/regexp.c

`regexp.c` implements sam's regular expression compiler and executor. It builds a compact NFA-like instruction program and supports forward and backward execution.

The parser recognizes literals, escaped characters, `.`, `^`, `$`, character classes and negated classes, grouping, alternation, concatenation, `*`, `+`, and `?`. It uses operand/operator stacks, records subexpression boundaries up to `NSUBEXP`, and builds both forward and backward programs.

`compile` caches the last compiled regex, frees character classes, compiles forward and backward versions, optimizes away `NOP` chains, and updates `lastregexp`.

`execute` runs the forward machine from a starting position to EOF or a bound, with wrapping search semantics for unbounded search, first-character optimization, thread-list deduplication, submatch range tracking, anchors, classes, and longest-leftmost match selection.

`bexecute` mirrors execution backward, using a backward-compiled program and reversed range selection. `newmatch` and `bnewmatch` choose the best match for forward and backward searches.

Errors reset `lastregexp` before propagating through sam's `error` path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/regexp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/sam.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/sam.c

`sam.c` is the host editor's main program and high-level file/session coordinator.

`main` parses sam and samterm options, initializes strings, disk storage, terminal connection, notify handling, current directory, initial files, current file, sequence number, and command loop. Downloaded mode starts `samterm` and speaks the sam protocol; non-downloaded mode operates on stdin/stdout.

`rescue` writes dirty buffers to `$home/sam.save` as shell commands that can reconstruct file contents. `panic` and `hiccough` handle fatal/internal and command-level errors, including rollback of edits logged in the current sequence.

File/session operations include dirty-close checking, dirty-quit checking, lazy file load, command-file update, file deletion, per-command update of modified files, and current-file selection.

`edit`, `getname`, `filename`, and `writef` integration handle `e`, `r`, `I`, `f`, and file naming semantics, including clean-sequence management and modified-state updates.

The file-list helpers (`readcmd`, `cd`, `loadflist`, `readflist`, `tofile`, `getfile`, `closefiles`) implement sam's file name/menu command behavior and current-directory normalization.

Text operations include `copy`, `move`, `nlcount`, `printposn`, and `settempfile`, supporting command execution over stable snapshots of the open-file list.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/sam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/sam.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/sam.h

`sam.h` is the shared host-side sam header. It defines core constants, types, structs, function prototypes, globals, and includes `mesg.h`.

Core types include `Posn`, `Mod`, `Range`, `Rangeset`, `Address`, `String`, `List`, `Block`, `Disk`, `Buffer`, and `File`. `File` embeds `Buffer` and adds undo buffers, filename, file identity, dirty/unread state, sequence numbers, dot/mark state, terminal rasp, protocol tag, close/delete flags, and previous state for rollback.

It declares temp-disk APIs, buffer APIs, file/undo APIs, rasp APIs, command/parse/search APIs, terminal protocol output APIs, Plan 9 system wrappers, string helpers, file-list/menu helpers, and utility routines.

Important constants include `BLOCKSIZE`, `NSUBEXP`, `STRSIZE`, `Maxblock`, buffer sizes, and file state markers. It also defines rune allocation/move macros and exposes global editor state such as `seq`, `disk`, `curfile`, `cmd`, `addr`, `snarfbuf`, `file`, `downloaded`, and protocol buffers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/sam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/shell.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/shell.c

`shell.c` implements sam's `!`, `<`, `>`, `|`, `^`, and `_` Plan 9 command integration.

`plan9` stores/reuses the last shell command, sets up error capture in downloaded mode, creates pipes based on command type, forks `/bin/rc -c`, optionally pipes selected text into the command, reads command output into the file or command buffer, writes selected text to command stdin, and reports status.

For filter commands (`|`, `_`), it first snarfs the addressed text into `plan9buf`, then a child writes that buffer to a pipe feeding the shell. For insertion/replacement commands (`<`, `|`), it deletes selected text and reads command output through `readio`.

`updateenv` sets `%` and `%dot` environment variables for shell commands, describing current filename and dot range. `checkerrs` displays the first few stderr lines from the sam error file and points to the file if more remains.

`cmdbuf` and `cmdbufpos` support `^` and `_` commands that feed generated command text back into sam's command parser.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/shell.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/string.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/string.c

`string.c` implements sam's `String` rune-vector utilities.

It provides initialization with and without an initial NUL, close/free, reset with shrink for oversized buffers, rune-string length, duplication from NUL-terminated rune arrays or another `String`, append, ensure capacity with `STRSIZE` guard, insertion, deletion, comparison, prefix check, and conversion to UTF-8 C strings.

`Strcmp` intentionally treats an extra trailing NUL as equivalent in common cases because sam strings sometimes carry parser convenience NULs.

`tmprstr` wraps an existing rune slice in a static temporary `String` without copying. `tmpcstr` converts a UTF-8 C string into a newly allocated rune `String`, and `freetmpstr` releases it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/string.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/sys.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/sys.c

`sys.c` provides guarded wrappers around system calls used by sam.

`resetsys` clears the local reentrancy guard. `syserror` captures the current error string, prints the failing operation, and raises an `Eio` sam error once, avoiding recursive error storms.

`Read` requires an exact byte count. On short read or error it marks `lastfile` as rescuing, reports the read error in downloaded mode, runs `rescue`, and exits.

`Write` requires an exact write and reports via `syserror` otherwise. `Seek` wraps `seek` and raises `syserror` on failure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/sys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/util.c

`util.c` contains small shared helpers for rune conversion, temporary buffers, and unsigned min.

`cvttorunes` converts a byte buffer to runes, assuming the caller provided enough trailing bytes to avoid partial-rune ambiguity. It elides NUL runes and optionally reports that NULs were seen.

`fbufalloc` and `fbuffree` allocate/free fixed-size file buffers using sam's panic-on-failure allocator.

`min` returns the smaller of two unsigned integers and is used in buffer and window logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/xec.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sam/xec.c

`xec.c` executes parsed sam commands. `cmdexec` applies default addresses, resolves address expressions, loads unread files as needed, sets `curfile`, and dispatches to the command function from `cmdtab`.

It implements editing commands (`a`, `c`, `d`, `i`, `m`, `t`, `s`), file/menu commands (`b`, `B`, `D`, `e`, `f`, `n`, `w`, `q`, `cd`), display/address commands (`p`, newline, `=`), mark/undo commands (`k`, `u`), regex conditional/looping commands (`g`, `v`, `x`, `y`, `X`, `Y`), Plan 9 shell commands, and custom terminal menu command updates (`M`).

`append`, `display`, `move`, and `copy` perform the concrete text operations via `loginsert`/`logdelete`.

` s_cmd` handles substitution with `&` and `\1`-`\9` submatch expansion, global substitution, empty-match avoidance, and dot update.

`looper`, `linelooper`, and `filelooper` implement regex range iteration, line iteration, and file-list iteration with nesting guards and current-file restoration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sam/xec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/flayer.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/flayer.c

`flayer.c` implements samterm's overlapping text-window layer abstraction on top of `Frame`.

It maintains a front-to-back `Flayer` list, visibility classification (`None`, `Some`, `All`), per-layer backing images for partially covered windows, and separate color palettes for command and main text windows.

`flnew`, `flinit`, `flclose`, `flupfront`, `llinsert`, and `lldelete` manage layer lifetime and stacking. `newvisibilities`, `visibility`, and `flrefresh` compute obscured regions and repaint visible fragments.

`flrect`, `flresize`, and `rscale` manage layer geometry, scroll-bar area, and screen-resize scaling. Resize clears/rebuilds frames and enforces minimum window dimensions.

`flinsert`, `fldelete`, `flsetselect`, and `flfp0p1` synchronize visible frame text and selection with global file offsets. Repainting is optimized by only drawing changed selection spans where possible.

`flselect` brings a layer forward, detects double/triple clicks by time/distance, updates global `sel`, and delegates drag selection to the frame library.

`flprepare` lazily reconstructs a layer frame/backing image when it becomes visible, reloads text through the layer's `textfn`, redraws selection, and redraws scroll state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/flayer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/flayer.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/flayer.h

`flayer.h` defines samterm's layer interface.

`Flayer` wraps a `Frame` with global text origin, selection range, click time, text loading callback, user fields, full rectangle, scroll rectangle, last scroll-bar rectangle, and visibility state.

It declares all layer lifecycle, geometry, selection, refresh, resize, insertion/deletion, preparation, and hit-testing functions.

The header also defines UI constants for click timing, margins, scroll width, gap, command/main color arrays, and the global selection anchor `sel`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/flayer.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/icons.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/icons.c

`icons.c` defines samterm cursor bitmaps and one shared color.

The cursors are `bullseye` for selecting windows for menu actions, `deadmouse` for snarf exchange/wait states, and `lockarrow` for host-locked input. Each cursor provides Plan 9 cursor offset, clear mask, and set mask.

`iconinit` allocates `darkgrey`, a 1x1 image used elsewhere by the terminal UI.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/icons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/io.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/io.c

`io.c` multiplexes samterm input sources: host protocol, mouse, keyboard, resize, and plumb/external input.

`kbdproc` puts `/dev/consctl` into raw mode and forwards `/dev/kbd` records through a channel. `kbdkey` tracks character events, key-up/down events, shift state, and the current keyboard rune.

`initio` initializes mouse, keyboard, host reader, and plumb reader. `waitforio` builds an `Alt` set over all sources, honors the `block` mask, flushes display when idle, handles resize reattachment, loads host/plumb buffers, and returns readiness bits.

`rcvchar`, `rcvstring`, and `getch` feed host-protocol parsing. `externload` and `externchar` turn plumb input into typed text. `kbdchar`, `ecankbd`, `ekbd`, and `qpeekc` provide nonblocking/blocking keyboard access.

`frscroll` is the frame-library scroll callback during selection; it updates selection endpoints while scrolling and uses `forcenter` to request host-origin changes and wait for necessary host data.

`RESIZED` reattaches to the resized window with `getwindow` and clears the resize flag.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/main.c

`main.c` is samterm's main UI loop and local editing front end.

`threadmain` initializes display, icons, I/O, scratch buffer, the command window, sends version/start messages, then loops over host, plumb, keyboard, mouse, and resize events. It handles current layer selection, scrolling, selection, chording, menus, and terminal protocol calls.

`current`, `closeup`, `duplicate`, `getr`, and `resize` manage active layers, closing/duplicating text windows, interactive rectangle selection, and resize-time host checks.

Editing operations include `snarf`, `cut`, `paste`, `type`, `flushtyping`, and movement/delete helpers. Local typing is applied optimistically to the terminal rasp and frame via `hgrow`/`hdatarune`, batched as `Ttype`, and flushed on newline or size thresholds.

Keyboard handling supports arrow/page/home/end scrolling, line start/end, command-window jump, work-window cycling, escape selection of typed text, backspace/delete/ctrl-u/ctrl-w deletion, autoindent, and spaces-for-tabs indentation.

`center` requests origin changes locally or from the host. `gettext` loads frame text from a `Rasp`, `scrtotal` reports total runes, and `alloc` is a zeroing panic-on-failure allocator.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/menu.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/menu.c

`menu.c` implements samterm's button-2 and button-3 menus and the file menu state.

Button-2 actions include cut, paste, snarf, plumb, look, snarf exchange with rio, search/send, and host-defined custom menu commands. Entries are parenthesized when disabled by host/file lock.

Button-3 actions include new, zerox, resize, close, write, and file selection/opening from the file menu. Interactive actions use the bullseye cursor and mouse rectangle/window selection.

The file menu arrays (`name`, `text`, `tag`) track display names, bound `Text*`, and host tags. `menuins`, `menudel`, `whichmenu`, `setmenuhit`, and `genmenu3` maintain sorted menu display with modified/open/current markers and width-aligned names.

`sweeptext` creates a new `Text` and first `Flayer` for a new file or existing host tag, initializes its rasp, and sends the appropriate start message.

`menucmd` maintains custom `M` commands, toggling duplicate entries and emitting a command-list response when requested.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/menu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/mesg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/mesg.c

`mesg.c` is samterm's terminal-side protocol implementation. It parses `Hmesg` packets from the host, updates menu/text/rasp/layer state, and serializes `Tmesg` packets back to the host.

`rcv` incrementally parses host packets and calls `inmesg`. `inmesg` handles version, bind/current/move/new names, grow/cut/data/origin/check/unlock/setdot/moveto/clean/dirty/delete/close/pattern/snarf/ack/exit/plumb/menu-command messages.

Text synchronization is lazy and lock-aware. `hgrow`, `hdata`, `hdatarune`, and `hcut` update the terminal `Rasp` plus all open layers for a text. `hcheck` finds visible holes or missing end-of-frame text and sends `Trequest`/`Tcheck` while incrementing text locks.

`horigin`, `hmoveto`, and `hsetdot` update frame origins and selections. `flnewlyvisible` triggers `hcheck` when a previously hidden layer becomes visible.

`setlock`/`clrlock` manage host lock state and cursor changes. `startfile` and `startnewfile` initiate host binding for existing or new windows.

Outbound helpers serialize terminal messages with short, long, vlong, strings, and raw payloads. `hsetsnarf` swaps sam's snarf buffer with `/dev/snarf`; `hplumb` unpacks host-provided plumb data and sends it to the plumb port.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/mesg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/plan9.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/plan9.c

`plan9.c` is samterm's Plan 9 platform glue.

`getscreen` parses `-a` autoindent and `-i` spaces-indent options, initializes draw, reads `$tabstop`, and clears the screen. `screensize` reads `/dev/screen` geometry.

`snarfswap` exchanges sam's snarf text with `/dev/snarf`, respecting older host protocol snarf limits when `hversion < 2`.

Plumbing support opens the `edit` and `send` ports. `plumbproc` reads plumb messages, `plumbformat` converts supported `showfile` messages into command-window input beginning with `B ` plus optional address, and `plumbstart` launches the reader.

`hostproc` continuously reads host protocol bytes from stdin into double buffers and signals `hostc`; EOF is fatal unless samterm is already exiting. `hoststart` creates the channel and reader process.

`extproc` is a generic external reader using the plumb buffer structure. `dumperrmsg` reports malformed oversized host messages and consumes the current string payload for diagnostics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/plan9.c -->