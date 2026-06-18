# Group Research: group_1608_plan9_sources_os_plan9_plan9_sys_src_cmd_sam_mesg_c_sources_os_plan_ec993ac38a54

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/mesg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/mesg.c

Implements the host side of the `sam`/`samterm` binary message protocol.

Key responsibilities:
- Receives terminal-originated `Tmesg` records from stdin with a 3-byte header and dispatches in `inmesg`.
- Handles terminal requests for file starts, edits, cut/paste/snarf, search, write/close, double-click, plumbing, and shutdown.
- Maintains host-side protocol buffers: `indata`, `outdata`, `inp`, `outp`, `outmsg`, `waitack`, `outbuffered`, and terminal protocol version `tversion`.
- Serializes host-originated `Hmesg` messages with helpers such as `outTs`, `outTslS`, `outTsll`, `outTsv`, and `outflush`.

Behavior notes:
- Flow control uses `Hack`/`Tack`: buffered output is flushed by sending `Hack` and reading until `Tack`.
- `Trequest` fills terminal rasp holes by finding available spans with `rdata` and sending `Hdata`.
- `Ttype`, `Tcut`, and `Tpaste` update file logs, file sequence state, terminal dot assumptions, and command execution when command text ends in newline.
- `Tstartsnarf`/`Tsetsnarf` bridge the internal rune snarf buffer and terminal snarf exchange, capped by `SNARFSIZE`.
- `Tplumb` builds a Plan 9 `Plumbmsg` from the selected text or clicked word and sends packed data back via `Hplumb`.

Risk/maintenance notes:
- Message parsing uses static receiver state, global buffers, and panics on malformed lengths.
- Many protocol paths assume valid file tags and call `hiccough`/`panic` on mismatch.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/mesg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/mesg.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/mesg.h

Defines the shared `sam`/`samterm` wire protocol.

Key contents:
- `VERSION` is `2`; comments record version 1 plumbing support and version 2 snarf-size expansion.
- `TBLOCKSIZE`, `DATASIZE`, and `SNARFSIZE` define text chunk and protocol buffer limits.
- `Tmesg` enumerates terminal-to-host messages such as `Tstartfile`, `Ttype`, `Tcut`, `Tpaste`, `Tsearch`, `Tplumb`, and `Texit`.
- `Hmesg` enumerates host-to-terminal messages such as `Hbindname`, `Hgrow`, `Hdata`, `Hsetdot`, `Hsetsnarf`, `Hack`, `Hexit`, and `Hplumb`.
- `Header` is the packed protocol header: one-byte type, two-byte little-endian count, and variable data.

Behavior notes:
- The comment includes a Holzmann-style protocol model for grow/data/check/request flow control and notes a non-progress-cycle proof.
- The enum values are positional wire values; host and terminal code must stay in lockstep.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/mesg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/moveto.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/moveto.c

Implements selection movement, terminal dot/origin notification, and double-click selection logic.

Key functions:
- `moveto` updates file dot and sends `Hmoveto` when the file has a terminal rasp.
- `telldot` sends `Hsetdot` only when the host dot differs from terminal-known `tdot`.
- `tellpat` pushes the last search pattern with `Hsetpat`.
- `lookorigin` chooses a nearby display origin around a requested position, bounded by line count and `CHARSHIFT`.
- `alnum`, `clickmatch`, `strrune`, and `doubleclick` implement word, quote, bracket, and newline expansion for double-click selections.

Behavior notes:
- Double-click uses `left[]`/`right[]` delimiter tables from `plan9.c`.
- `lookorigin` walks backward from a requested point to find a stable terminal origin without scanning unbounded text.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/moveto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/multi.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/multi.c

Manages the host-side open-file list and menu ordering.

Key functions:
- `newfile` opens a `File`, assigns a monotonically increasing tag, inserts it into `file`, and notifies the terminal with `Hnewname`.
- `whichmenu` maps a `File*` to its menu index.
- `delfile` removes a file from the list, sends `Hdelname`, and closes storage.
- `fullname` and `fixname` canonicalize names relative to `curwd` and `cleanname`.
- `sortname` keeps the command file first, warns on duplicate names, and sends `Hmovname`.
- `state` changes clean/dirty/unread state and emits `Hclean`/`Hdirty`.
- `lookfile` finds a file by exact `String` name.

Behavior notes:
- File tags are protocol identifiers independent of menu order.
- Canonical display names are shortened relative to current working directory when possible.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/multi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/parse.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/parse.h

Defines parsed command and address structures for the `sam` command language.

Key contents:
- `Addr` represents text addresses: character, line, regexp, dot, dollar, plus/minus, comma, semicolon, and file-qualified address forms.
- `Cmd` represents executable commands, optional address, regexp, text, target address, nested command, count, flags, and chained block member.
- `Cmdtab` describes command parser/executor metadata: textual argument, regexp argument, address argument, defaults, count handling, terminator tokens, and function pointer.
- Default address enum values are `aNo`, `aDot`, and `aAll`.
- Declares command handlers implemented in `xec.c` plus parser/executor interfaces such as `getregexp`, `newaddr`, `address`, and `cmdexec`.

Behavior notes:
- Field aliases (`are`, `left`, `ccmd`, `ctext`, `caddr`) overlay unions used by parser and executor code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/parse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/plan9.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/plan9.c

Provides Plan 9 system bindings and constants for host `sam`.

Key contents:
- Defines `samname`, bracket delimiter tables `left`/`right`, and system command/path constants: `RSAM`, `SAMTERM`, `HOME`, `TMPDIR`, `SH`, `RX`, and `SAMSAVECMD`.
- `dprint`, `print_ss`, and `print_s` route messages through `termwrite`.
- `statfile` and `statfd` wrap Plan 9 `dirstat`/`dirfstat`.
- `notifyf` handles interrupt and closed-pipe notifications.
- `waitfor` filters wait messages by pid and returns exit status text.
- `samerr`, `emalloc`, and `erealloc` centralize temp error naming and allocation failure behavior.

Behavior notes:
- `notifyf` converts interrupts into `intr()` and ignores closed-pipe notes only when `bpipeok` is set.
- Allocation wrappers zero new memory for `emalloc` and panic on failure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/plan9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/rasp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/rasp.c

Maintains the host-side rasp, the compact map of what text the terminal already has.

Key functions:
- `raspload`, `raspstart`, `raspdone`, and `raspflush` bracket batched terminal updates.
- `raspdelete` and `raspinsert` update dot/mark positions, file rasp ranges, and terminal grow/cut/data messages.
- `rcut` removes spans from the rasp piece list.
- `rgrow` inserts not-in-terminal pieces.
- `rterm` checks whether a position is inside terminal-known text.
- `rdata` locates a terminal-missing span to satisfy `Trequest`.

Implementation details:
- Rasp pieces are stored in a `List` of `Posn`; high bit `M` marks text resident in the terminal.
- Large inserts are sent as `Hgrowdata`; smaller terminal-known inserts may be sent as `Hgrow` plus `Hdata`.
- `GROWDATASIZE` controls when grow/data folding is used.

Risk/maintenance notes:
- The piece list encoding is dense and relies on bit masks over signed-looking `Posn` values.
- `raspdone` clamps dot/mark after file-size changes before flushing protocol messages.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/rasp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/regexp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/regexp.c

Implements `sam` regular expression compilation and forward/backward execution.

Key components:
- `Inst` is the compiled NFA instruction format, with literal, operator, branch, class, and subexpression marker variants.
- Parser stacks (`andstack`, `atorstack`, `subidstack`) implement precedence parsing for concatenation, alternation, repetition, grouping, and character classes.
- `compile` builds both forward `startinst` and backward `bstartinst` programs, then optimizes NOP chains.
- `execute` scans forward from a start position, with wraparound behavior for unbounded search.
- `bexecute` scans backward using a separately compiled reversed machine.
- `sel` stores selected subexpression ranges.

Supported regex features:
- Literals, escapes including `\n`, `.`, `^`, `$`, `[]`, `[^]`, `*`, `+`, `?`, `|`, and parentheses.
- Character-class ranges are encoded with `Runemax` sentinels.
- Subexpressions beyond `NSUBEXP` are silently ignored.

Risk/maintenance notes:
- Fixed limits include `NPROG`, `NLIST`, and parser `NSTACK`.
- Matching is global-state driven and reports errors by clearing `lastregexp` and calling `error`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/regexp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/sam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/sam.c

Contains the host `sam` main program, global state, lifecycle, recovery, file loading, and common edit operations.

Key responsibilities:
- `main` parses flags, initializes strings, disk storage, terminal startup, signal notifications, current directory, initial files, and enters `cmdloop`.
- `rescue`, `panic`, and `hiccough` implement crash/error recovery and save dirty buffers to `$home/sam.save`.
- `load`, `edit`, `readcmd`, `readflist`, `getfile`, `tofile`, and `closefiles` implement file input and command file-list behavior.
- `update`, `cmdupdate`, `delete`, `trytoclose`, and `trytoquit` manage file lifecycle and dirty-state safety.
- `copy`, `move`, `undo`, `undostep`, `printposn`, and `settempfile` provide shared editor operations.

Behavior notes:
- Dirty-file quit protection is mediated by `quitok`, `closeok`, and per-file `mod` state.
- File reads and writes use command-level globals `addr`, `genstr`, `genc`, and `io`.
- Recovery emits a shell script using `SAMSAVECMD` to recreate dirty files.

Risk/maintenance notes:
- Error recovery uses `setjmp`/`longjmp` and extensive global state.
- `rescue` skips the command file, empty files, and clean files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/sam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/sam.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/sam.h

Defines the host `sam` core data model, constants, prototypes, and globals.

Key types:
- `Posn`, `Mod`, `Range`, `Rangeset`, `Address`, and `String` model positions, selections, and rune strings.
- `List` is a generic list union used for pointers, positions, strings, and files.
- `Block`, `Disk`, and `Buffer` model temp-file-backed text storage.
- `File` embeds `Buffer` and adds undo buffers, name/stat data, dirty state, dot/mark ranges, terminal rasp, protocol tag, and undo snapshots.

Key constants:
- `BLOCKSIZE`, `NDISC`, `NBUFFILES`, `NSUBEXP`, `INFINITY`, `STRSIZE`, buffer sizes, and log operation markers.

API surface:
- Declares disk, buffer, file, rasp, utility, regex, command, shell, string, protocol, terminal, and system functions.
- Declares major global state: `seq`, `disk`, `file`, `tempfile`, `cmd`, `curfile`, `addr`, `sel`, `snarfbuf`, `plan9buf`, `lastpat`, `lastregexp`, `downloaded`, `termlocked`, and `outbuffered`.

Behavior notes:
- Includes `mesg.h` at the end because protocol definitions depend on common constants and are used by `outT*` prototypes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/sam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/shell.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/shell.c

Executes external Plan 9 shell commands for `!`, `<`, `>`, and `|` editor commands.

Key functions:
- `plan9` prepares command text, optional pipes, error redirection, fork/exec of `rc`, and data movement between files and commands.
- `checkerrs` reads and reports the downloaded-terminal error file after a shell command.

Behavior notes:
- `|` first snarfs the selected text into `plan9buf`, forks a writer process into a secondary pipe, and runs the command with that pipe as stdin.
- `<` and `|` capture command stdout back into the file through `readio`.
- `>` sends selected file text to the command.
- `!` runs the command with output routed to terminal/error handling.
- In downloaded mode, stderr is redirected to a temporary `sam.err` file for later display.

Risk/maintenance notes:
- Uses nested forks, pipes, and `setjmp(mainloop)` to recover from write-side errors.
- Command text is cached in global `plan9cmd`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/shell.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/string.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/string.c

Implements mutable `Rune` string helpers used throughout host `sam`.

Key functions:
- `Strinit`, `Strinit0`, `Strclose`, and `Strzero` manage allocation and reset.
- `Strlen`, `Straddc`, `Strinsure`, `Strinsert`, `Strdelete`, `Strcmp`, and `Strispre` implement basic string operations.
- `Strtoc` converts a `String` to malloced UTF-8 bytes.
- `tmprstr`, `tmpcstr`, and `freetmpstr` build and release temporary `String` wrappers.

Behavior notes:
- `Strinsure` enforces `STRSIZE` and grows with slack.
- `Strzero` shrinks overly large buffers back toward `MAXSIZE`.
- `tmprstr` returns a static wrapper over caller-owned rune storage; callers must not free it with `freetmpstr`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/string.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/sys.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/sys.c

Provides error-aware wrappers around basic file-descriptor operations.

Key functions:
- `resetsys` clears the reentrant error guard.
- `syserror` prints operation context, converts the current error string to `Eio`, and avoids recursive error storms.
- `Read` requires an exact byte count; on short read it marks `lastfile` rescuing, reports, calls `rescue`, and exits.
- `Write` requires an exact write count and reports `write` errors through `syserror`.
- `Seek` wraps `seek` and reports failure through `syserror`.

Behavior notes:
- Read failure is considered fatal and triggers rescue rather than returning partial data.
- `inerror` prevents recursive `syserror` handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/sys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/util.c

Contains small host utility functions.

Key functions:
- `cvttorunes` converts UTF-8 bytes to `Rune` data, reporting consumed bytes, produced runes, and optional NUL count.
- `fbufalloc` and `fbuffree` allocate/free fixed-size file buffer memory.
- `min` returns the smaller of two unsigned integers.

Behavior notes:
- `cvttorunes` assumes the input byte count ends on a complete rune boundary.
- NUL runes are skipped from output but counted when `nulls` is provided.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/xec.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/xec.c

Executes parsed `sam` commands.

Key functions:
- `cmdexec` resolves default addresses, loads unread files, selects the current file, and dispatches through `cmdtab`.
- Command handlers implement append/change/delete, file open/read/edit/write, global/ inverse-global, insert, mark, move/copy, print, quit, substitute, undo/redo, shell commands, file loops, line loops, and address display.
- `append` inserts command text and updates `ndot`.
- `display` emits selected text to terminal or stdout.
- `looper`, `linelooper`, and `filelooper` implement `x/y`, line iteration, and `X/Y` file iteration.

Behavior notes:
- `s_cmd` supports `&` and `\1`-style replacement expansion from regex submatches.
- `g_cmd` uses `execute(...) ^ cp->cmdc=='v'` to implement both `g` and `v`.
- Nested command execution is tracked with `nest`; file-loop nesting is guarded by `Glooping`.

Risk/maintenance notes:
- Editing operations depend on shared globals `addr`, `sel`, `genstr`, and `seq`.
- Substitution explicitly avoids infinite loops on empty matches by tracking the previous match endpoint.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sam/xec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/flayer.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/flayer.c

Implements `samterm` layered text windows backed by Plan 9 `Frame`.

Key responsibilities:
- Maintains front-to-back layer list `llist`.
- Initializes color palettes for command and file text layers in `flstart`.
- Creates, initializes, closes, raises, resizes, and redraws `Flayer` instances.
- Bridges frame operations with text loading via `textfn`.
- Computes visibility of overlapped layers and refreshes partially covered windows.

Key functions:
- `flnew`, `flinit`, `flclose`, `flborder`, `flwhich`, `flupfront`.
- `flinsert`, `fldelete`, `flselect`, `flsetselect`, `flfp0p1`.
- `flresize`, `flprepare`, `visibility`, and `flrefresh`.

Behavior notes:
- `flprepare` lazily builds a frame image for visible layers and loads text through `textfn`.
- Selection and scrolling coordinates are adjusted by `origin`.
- Visibility can be `None`, `Some`, or `All`; partially visible layers refresh through recursive clipping against layers above them.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/flayer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/flayer.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/flayer.h

Defines the `Flayer` abstraction for terminal text windows.

Key contents:
- `Vis` enum: `None`, `Some`, `All`.
- `Clicktime` is one second for multi-click timing.
- `Flayer` embeds a `Frame` and tracks text origin, selection endpoints, click time, text fetch callback, user fields, full rectangle, scrollbar rectangle, last scrollbar mark, and visibility.
- Declares flayer lifecycle, drawing, selection, refresh, resize, and lookup functions.
- Defines layout constants `FLMARGIN`, `FLSCROLLWID`, and `FLGAP`.
- Externs shared command/file color arrays `maincols` and `cmdcols`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/flayer.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/icons.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/icons.c

Defines cursor bitmaps and initializes a shared color.

Key contents:
- `bullseye`, `deadmouse`, and `lockarrow` Plan 9 `Cursor` bitmaps.
- `darkgrey` image for UI drawing.
- `iconinit` allocates `darkgrey` as a 1x1 image.

Behavior notes:
- Cursor objects are global and referenced by terminal UI state, especially lock/error states.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/icons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/io.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/io.c

Multiplexes terminal input from host, keyboard, mouse, plumb, external-load, and resize sources.

Key responsibilities:
- `initio` initializes mouse/keyboard controls, starts the host reader, and starts plumb or external-load support.
- `waitforio` uses Plan 9 `Alt` over resource channels and control channels.
- `rcvchar`, `rcvstring`, and `getch` expose host bytes to message parsing.
- `externload` and `externchar` feed plumb/external text into normal keyboard typing.
- `ecankbd`, `ekbd`, `kbdchar`, and `qpeekc` manage keyboard lookahead.
- `RESIZED` reattaches to the resized window.

Behavior notes:
- `got` is a bitmask over `RHost`, `RKeyboard`, `RMouse`, `RPlumb`, and `RResize`.
- `block` can suppress keyboard/plumb while host reads are required.
- Host and plumb buffers are double-buffered through `hostbuf` and `plumbbuf`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/main.c

Contains the `samterm` UI main loop and interactive editing behavior.

Key responsibilities:
- `threadmain` initializes screen, icons, I/O, command rasp/flayer, sends protocol `Tversion`, starts the command file, and runs the event loop.
- Handles host messages, plumb inserts, keyboard typing, mouse selection, scrolling, menus, window creation/duplication/resize/close.
- Maintains active layer globals `which` and `work`, typing coalescing (`typestart`, `typeend`, `typeesc`), snarf length, and host lock state.

Key functions:
- `resize`, `current`, `closeup`, `findl`, `duplicate`, `getr`.
- `snarf`, `cut`, `paste`, `scrorigin`.
- `ctlw`, `ctlu`, `center`, `onethird`, `flushtyping`, `nontypingkey`, and `outcmd`.
- `gettext`, `scrtotal`, and `alloc`.

Behavior notes:
- Typing is buffered locally and flushed as `Ttype`/selection updates to reduce protocol chatter.
- Command text gets special handling for send, newline execution, and plumb injection.
- Non-typing keys implement navigation, deletion, line start/end, paging, and control-editing behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/menu.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/menu.c

Implements `samterm` button-2 and button-3 menus plus the terminal file-name list.

Key responsibilities:
- Global arrays `name`, `text`, and `tag` maintain menu entries and associated `Text` objects.
- `menu2hit` handles cut, paste, snarf, plumb, look, exchange/send, and search.
- `menu3hit` handles new, zerox, resize, close, and write.
- `sweeptext` creates a new window by mouse rectangle selection.
- `menuins`, `menudel`, and `whichmenu` maintain menu entries.
- `setpat`, `paren`, `genmenu2`, `genmenu2c`, and `genmenu3` generate dynamic menu labels.

Behavior notes:
- Menu entries are decorated with dirty-state prefixes and parenthesized when no live text window is attached.
- The command menu uses `Send` where file windows use `Search`.
- Plumb menu is disabled when protocol version or plumb fd does not support it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/menu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/mesg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/mesg.c

Implements the terminal side of the `sam` protocol.

Key responsibilities:
- `rcv` parses host-originated `Hmesg` records and dispatches `inmesg`.
- Handles host messages for version, names, current file, grow/cut/data, check/request flow, unlock, setdot, origin, move-to, clean/dirty, snarf, ack, exit, and plumb.
- Serializes terminal-originated `Tmesg` records through `outT*` helpers.

Key functions:
- `setlock`/`clrlock` update host lock state and cursor.
- `startfile` and `startnewfile` initiate host binding for terminal text.
- `hsetdot`, `horigin`, `hmoveto`, `hcheck`, `hgrow`, `hdata`, `hdatarune`, and `hcut` mutate local rasps and flayers.
- `hsetsnarf` swaps with `/dev/snarf`; `hplumb` unpacks and stores plumb messages.

Behavior notes:
- `Hcheck` scans visible flayers for missing data and sends `Trequest` for holes.
- `Hgrowdata` folds a resize and data payload into one terminal update.
- Terminal locks defer local edits while host-side commands are in progress.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/mesg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/plan9.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/plan9.c

Provides Plan 9 terminal integration for screen, snarf, plumbing, external files, and host I/O.

Key functions:
- `getscreen` parses `-a`, initializes draw, tab width, and clears the screen.
- `screensize` reads `/dev/screen` dimensions for scrollbar backing allocation.
- `snarfswap` exchanges host snarf text with `/dev/snarf`, respecting protocol-version snarf limits.
- `extstart`/`extproc` provide fallback external file loading when plumbing is unavailable.
- `plumbstart`, `plumbproc`, and `plumbformat` read edit plumbing messages and format them as command text.
- `hoststart`/`hostproc` continuously read host bytes into double buffers.

Behavior notes:
- `plumbopen("send")` may fail without disabling editor startup; edit input is the important receive side.
- External-load fallback creates a `/srv` endpoint name and removes it through `removeextern`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/plan9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/rasp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/rasp.c

Implements the terminal-side rasp, a linked list of known text sections and holes.

Key functions:
- `rinit` and `rclear` initialize/free a rasp.
- `rsinsert`, `rsdelete`, `splitsect`, and `findsect` manage `Section` boundaries.
- `rresize` applies host grow/cut operations.
- `rdata` stores received rune data into a hole.
- `rclean` coalesces adjacent compatible sections.
- `rload` loads available text into `scratch` and reports rune count.
- `rmissing` and `rcontig` find missing or contiguous spans for host requests.

Behavior notes:
- `Section.text == nil` marks text the terminal knows exists but has not loaded.
- Data sections allocate `TBLOCKSIZE+1` runes so text is NUL-terminated for frame use.
- `findsect` can split sections to align operations exactly on requested offsets.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/rasp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/samterm.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/samterm.h

Defines shared `samterm` structures, globals, and function prototypes.

Key types:
- `Section` is a rasp segment with rune count, optional text, and next pointer.
- `Rasp` tracks total runes and the section list.
- `Text` owns one file/command rasp, up to `NL` flayers, a protocol tag, lock count, and active front window.
- `Readbuf` is the host/plumb double-buffer payload.

Key constants and enums:
- `RUNESIZE`, `MAXFILES`, `READBUFSIZE`, `NL`, `Untagged`.
- Direction enum `Up`/`Down`.
- Resource enum `RHost`, `RKeyboard`, `RMouse`, `RPlumb`, `RResize`, `NRes`.

Behavior notes:
- Includes `mesg.h` with `SAMTERM` defined, so terminal code shares wire-protocol constants.
- Declares most cross-file UI, protocol, rasp, menu, scroll, and Plan 9 integration functions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/samterm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/scroll.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/scroll.c

Implements scrollbar rendering and mouse-driven scrolling for `samterm` flayers.

Key functions:
- `scrtemps` allocates temporary scrollbar backing images sized from `/dev/screen`.
- `scrpos` maps visible text range to scrollbar thumb rectangle.
- `scrmark` and `scrunmark` highlight/unhighlight scroll drag regions.
- `scrdraw` draws the scrollbar track and thumb, using offscreen temporaries when the layer is fully visible.
- `scroll` handles button-specific scroll behavior, drag tracking, and origin requests.

Behavior notes:
- Large totals are scaled down before thumb computation to avoid overflow.
- Thumb height is clamped to at least 2 pixels.
- Scroll interaction delegates actual text origin changes through protocol requests rather than directly loading arbitrary text.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/samterm/scroll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/bitinput.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/bitinput.c

Implements bitstream helpers for compressed DSS image decoding.

Key contents:
- Static Huffman decode tables `hufvals` and `huflens`.
- Static bit buffer state `buffer` and `bits_to_go`.
- `start_inputing_bits` resets bitstream state.
- `input_huffman` ensures six bits are buffered, decodes a Huffman code, and advances by the code length.
- `input_nybble` ensures four bits are buffered and returns a 4-bit value.

Behavior notes:
- Unexpected EOF is fatal and exits with `"format"`.
- Bit order is MSB-first within the accumulated buffer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/bitinput.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/desc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/desc.c

Defines `desctab`, a large abbreviation-to-prose dictionary for astronomical object descriptions.

Key contents:
- Maps Dreyer/NGC-style abbreviations and symbols to expanded prose, including brightness, size, shape, direction, Greek letters, constellation words, and object descriptors.
- Used by `prose.c` through `prdesc` to expand compact catalog descriptions.

Behavior notes:
- This is data-only C source; it exposes the global `char *desctab[][2]`.
- The table includes UTF-8/Unicode strings such as Greek letters and degree symbols.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/desc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/display.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/display.c

Displays generated sky images by piping them to `/bin/page`.

Key functions:
- `displaypic` writes a raw `k8` image header and pixel bytes from a `Picture` to a child `page -w` process.
- `displayimage` writes a Plan 9 `Image` with `writeimage` to a child `page -w` process.

Behavior notes:
- Both functions fork with `rfork(RFPROC|RFFDG|RFNOTEG|RFNOWAIT)`.
- `displaypic` frees page-aligned chunks with `segfree` when possible, then frees picture storage.
- Pipe/fork/exec/write failures are reported but generally do not abort the main process.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/display.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/dssread.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/dssread.c

Reads and decodes compressed DSS image tile files.

Key functions:
- `dssread` validates the DSS magic header, reads dimensions/scale/sum metadata, allocates `Img`, decodes pixels, rescales if needed, applies inverse H-transform, and returns the image.
- `dodecode` decodes three quadtree-compressed bitplane groups into image quadrants, validates padding nybble, and applies sign bits.
- `getlong` reads big-endian 32-bit header fields.

Behavior notes:
- The image payload is reconstructed with `qtree_decode`, `input_nybble`, and `hinv`.
- `ip->a[0]` is initialized from the header sum before inverse transform.
- Bad format or EOF exits fatally with `"format"`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/dssread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/header.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/header.c

Reads DSS plate headers, the plate list, and mounts DSS jukebox disks.

Key functions:
- `getheader` locates a region `.hhh` header, parses 80-byte/FITS-like records, fills `Header.param`, detects AMD vs PPO coordinate modes, and computes RA/Dec parameter aggregates.
- `getplates` reads plate region records from local or jukebox paths into global `plate[]`.
- `dssmount` mounts the requested DSS disk via `JUKEFS` under `/n/juke` and caches the mounted disk number.

Behavior notes:
- Header parameter names map through `Hproto` into `Header.param` indexes shared with `sky.h`.
- Fallback paths check `/lib/sky/dssheaders`, then jukebox DSS 102 and DSS 061 locations.
- Missing header/plate data exits with file errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/header.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/hinv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/hinv.c

Implements the inverse H-transform used by DSS compressed image decoding.

Key functions:
- `hinv` iteratively expands wavelet/H-transform coefficients into pixel values for arbitrary image dimensions.
- `unshuffle` and `unshuffle1` deinterleave coefficient arrays along strided and contiguous dimensions.

Behavior notes:
- Handles odd image widths/heights separately while reconstructing 2x2 blocks.
- Allocates temporary storage sized to half the maximum dimension.
- Fatal memory allocation failure exits with `"memory"`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/hinv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/image.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/image.c

Builds a cropped grayscale DSS `Picture` for a requested sky location and angular size.

Key flow:
- Initializes gamma defaults and derived gamma fields.
- Loads the plate list if needed and chooses the nearest plate by angular distance.
- Reads the plate header and converts requested RA/Dec to plate x/y coordinates.
- Computes crop bounds, clamps to the 14000x14000 plate extent, and allocates output bytes.
- Iterates 500x500 subplates, mounts/opens DSS tile files, decodes with `dssread`, and copies gamma-corrected pixels into the output crop.

Behavior notes:
- Region subplate names use radix-28 characters from `rad28`.
- If no width/height is supplied, a default 500x500 plate-aligned tile is chosen.
- Returns a `Picture` with crop bounds, plate name, and raw 8-bit data suitable for `displaypic`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/image.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/patch.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/patch.c

Maps sky coordinates to compact patch identifiers and back.

Key functions:
- `radec` decodes a patch id into RA hour, RA minute, and declination degree.
- `patcha` converts angular RA/Dec to a patch id.
- `patch` computes the patch id from integer RA hour/minute and declination degree.

Behavior notes:
- Patch declination boundaries are adjusted so patch ranges are lower-inclusive and upper-exclusive.
- RA bins are coarser near the poles using the `round` lookup table.
- Invalid RA/Dec inputs abort after printing diagnostics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/patch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/plate.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/plate.h

Provides an older/standalone DSS plate header interface.

Key contents:
- Defines plate parameter indexes matching the DSS header parser: PPO terms, AMD X/Y polynomial terms, plate scale, pixel sizes, and plate RA/Dec fields.
- Defines `Angle`, `Plate`, `Header`, `Type`, and a flexible `Image` record.
- Declares global plate/gamma/debug state and image/coordinate decoding functions.

Behavior notes:
- Much of this overlaps with the later `sky.h` definitions.
- Some prototypes reflect older names/types, such as `Bitmap* image(...)`, while current `scat` uses `Picture* image(...)` through `sky.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/plate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/plot.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/plot.c

Plots selected sky catalog records into a Plan 9 image and invokes `astro` for planet/observer data.

Key responsibilities:
- `plotopen` initializes draw display, colors, stipple images, and font.
- Map helpers convert RA/Dec into a stereographic projection, with optional zenith-up observer orientation.
- `bbox`, `inbbox`, and `gridra` compute plot extents and grid spacing.
- `plot` parses flags (`nogrid`, `zenithup`, `notext`, `alltext`, `dx`, `dy`, `nogrey`), flattens records, draws grid/labels, then draws planets, stars, Abell clusters, and NGC object symbols.
- `astro` runs `/bin/astro -p`, records site/sidereal data, prints output, and rebuilds the global `planet` list.
- `parseplanet` parses one astro planet output line.

Behavior notes:
- RA ranges wider than 270 degrees trigger folded plotting around 180 degrees.
- Planets are moved to the end of the record list so they render in front, with moon and shadow ordering handled specially.
- Different NGC object types use distinct symbols: galaxy ellipses, planetary nebula rings/crosses, nebula boxes, open cluster stipple, and globular cluster crosshairs.

Risk/maintenance notes:
- The file relies on map library globals/functions (`orient`, `stereographic`, `normalize`) and Plan 9 draw globals.
- `plot` contains dense rendering logic and global mutable projection state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/plot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/posn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/posn.c

Converts sky coordinates to DSS plate x/y positions.

Key functions:
- `traneqstd` converts RA/Dec to standard coordinates relative to the plate center.
- `ppoinv` applies the simpler PPO inverse transform.
- `amdinv` iteratively solves AMD polynomial plate equations with Newton-style updates.
- `xypos` selects AMD or PPO conversion based on `Header.amdflag`.

Behavior notes:
- AMD uses many header polynomial parameters for X and Y, plus magnitude/color terms.
- Iteration is bounded by `max_iterations` and stops on a small tolerance.
- Output is stored in `Header.x`, `Header.y`, `Header.xi`, and `Header.eta`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/posn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/prose.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/prose.c

Expands compact astronomical object descriptions into readable prose.

Key functions:
- `append` appends text to a buffer pointer.
- `matchlen` measures prefix matches used to choose the longest abbreviation match.
- `prose` parses symbols, punctuation, numbers, star shorthand, and table-backed abbreviations into a static prose buffer.
- `prdesc` lazily builds a first-character index over `desctab`, calls `prose`, and prints the expanded description.

Behavior notes:
- `descindex` is initialized on first use.
- Unknown fragments are copied or interpreted by local punctuation/number/star rules.
- The output buffer is fixed at 512 bytes and aborts if exceeded.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/prose.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/qtree.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/qtree.c

Decodes quadtree-compressed DSS bitplanes.

Key functions:
- `qtree_decode` decodes each bitplane either as direct packed bits or Huffman-expanded quadtree data.
- `qtree_expand` expands one quadtree level.
- `qtree_copy` expands 4-bit block values into 2x2 layout.
- `qtree_bitins` inserts decoded bit values into the output pixel array.
- `read_bdirect` reads direct packed 4-pixel nibbles for a bitplane.

Behavior notes:
- Scratch storage is sized from half-dimensions of the quadtree plane.
- Format code `0` means direct, `0xf` means Huffman quadtree; any other code is fatal.
- Uses the bit input helpers from `bitinput.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/qtree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/scat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/scat.c

Main program and command interpreter for the `scat` sky catalog tool.

Key responsibilities:
- `main` initializes buffered stdin/stdout, optional catalog directory, initial `astro` data, then reads commands and dispatches `lookup`.
- Opens and caches catalog databases: SAO, NGC/IC, Abell, Messier index, names, Bayer names, constellation patches, and patch indexes.
- Loads records into the global dynamic `rec` array through `loadngc`, `loadsao`, `loadabell`, `loadplanet`, `loadpatch`, and `loadtype`.
- `flatten` recursively resolves symbolic records (`NGCN`, named records, constellation patches, patch lists) into concrete catalog records.
- `cull`, `sort`, `coords`, and `pplate` filter, de-duplicate, expand coordinate regions, and request DSS plate images.
- `lookup` parses user commands for object lookup, constellation lookup, `expand`, `plot`, `astro`, `plate`, `gamma`, `keep`, `drop`, named stars, and coordinate patches.
- `prrec`, `nameof`, `printnames`, and helper group functions format output.

Behavior notes:
- On-disk catalog integers are little-endian; `Long` and `Short` normalize them.
- `strings.c` is included directly for Greek, constellation, and object-name tables.
- Small result sets print full records; larger sets print a count.
- Name lookup supports quoted prose names and Bayer-style Greek/constellation names.

Risk/maintenance notes:
- Uses many fixed catalog-size constants and global file descriptors.
- `loadabell` contains a duplicated assignment to `cur->abell.ra`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/scat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/sky.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/sky.h

Primary shared header for `scat`.

Key contents:
- Documents catalog key encoding and record categories.
- Defines `Type` values for planets, patches, SAO, NGC, M, named records, Abell, NGC subtypes, and internal placeholders.
- Defines DSS plate parameter indexes.
- Defines core scalar types: `Angle`, `DAngle`, `Mag`, `Key`, and `Pix`.
- Defines on-disk/in-memory records: `NGCrec`, `Abellrec`, `Planetrec`, `SAOrec`, `Mindexrec`, `Bayerec`, `Namerec`, `Patchrec`, `Record`, `Name`, `Plate`, `Header`, `Img`, and `Picture`.
- Declares global catalog, plate, plotting, gamma, bounding-box, and output state.
- Declares cross-file functions for catalog loading, coordinate conversion, DSS decoding, plotting, display, parsing, and formatting.

Behavior notes:
- On-disk integer fields are explicitly noted as little-endian.
- `DIR` defaults catalog data to `/lib/sky`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/sky.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/strings.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/strings.c

Defines static lookup tables used by `scat`.

Key contents:
- `greek[]` maps 1-based indexes to spelled Greek letter names.
- `greeklet[]` maps the same indexes to Unicode Greek `Rune` values.
- `constel[]` maps 1-based constellation indexes to three-letter abbreviations.
- `names[]` maps object-type command strings and abbreviations to `Type` values.

Behavior notes:
- This file is included directly by `scat.c`, not compiled as an independent module.
- The tables drive Bayer-name parsing, display-name formatting, and type-based lookup/culling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/strings.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/util.c

Provides numeric parsing, angle formatting, angular distance, and gamma correction utilities for `scat`.

Key functions:
- `rint`, `rfloat`, and `sign` parse fixed-width numeric fields.
- `dangle` and `angle` convert between radians and milliarcsecond disk units.
- `hms`, `dms`, `ms`, `hm`, `hm5`, `dm`, and `deg` format angles.
- `getword`, `getra`, and related parsing helpers parse RA/Dec-style input.
- `xsqrt` clamps negative square-root inputs to zero.
- `dist` computes angular separation using spherical trig.
- `dogamma` maps pixel values through configured gamma/min/max settings to an 8-bit intensity.

Behavior notes:
- Defines global constants `PI_180`, `TWOPI`, and `LN2`.
- Formatting helpers use static buffers, so results are overwritten by subsequent calls.
- `dogamma` supports negative gamma display inversion through `gam.neg`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scat/util.c -->