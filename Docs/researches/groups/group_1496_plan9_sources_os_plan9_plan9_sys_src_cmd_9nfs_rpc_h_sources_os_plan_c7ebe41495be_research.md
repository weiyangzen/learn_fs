# Group Research: group_1496_plan9_sources_os_plan9_plan9_sys_src_cmd_9nfs_rpc_h_sources_os_plan_c7ebe41495be

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/rpc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/rpc.h

RPC protocol constants and XDR packing helpers for the 9nfs RPC layer.

Key responsibilities:
- Defines ONC/RPC booleans, authentication flavors, message types, accepted/rejected reply status, accept status, reject status, and authentication failure status.
- Provides TCP/UDP protocol number constants.
- Defines 4-byte alignment via `ROUNDUP`.
- Provides byte-order marshaling/unmarshaling macros: `PLONG`, `PPTR`, `PBYTE`, `GLONG`, `GPTR`, and `GBYTE`.

Dependencies:
- Assumes caller-local `dataptr` and `argptr` cursor variables.
- Uses Plan 9 integer aliases such as `uchar` and `ulong`.

Notable risks:
- The macros mutate implicit cursor variables and are not expression-safe abstractions.
- `GPTR(n)` expands to two statements without wrapping, so caller context matters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/rpc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/server.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/server.c

Shared RPC server loop for Plan 9 NFS/portmapper-style services, supporting UDP and TCP transports.

Key responsibilities:
- Parses common server flags through `argopt`: 9P debug, no reply cache, RPC debug, reject all, TCP mode, and chatty logging.
- Daemonizes with `rfork`, starts a periodic alarm helper, initializes program maps, then serves either UDP or TCP.
- Opens UDP in header mode and accepts TCP connections, adapting TCP connections to an RPC-like header context.
- Decodes RPC calls, validates version, dispatches by program/version/procedure, and encodes accepted/denied replies.
- Maintains a small duplicate-reply cache keyed by remote IP, port, and xid.
- Implements TCP record-marker framing for RPC over TCP.
- Caches DNS reverse lookups and strips local hostname prefixes through `getdnsdom`/`getdom`.
- Installs `%I` formatting for dotted IPv4 addresses.

Dependencies:
- Uses `Rpccall`, `Progmap`, `Procmap`, `Rpccache`, `Udphdr`, `rpcM2S`, `rpcS2M`, and `rpcprint` from the 9nfs subsystem.
- Uses Plan 9 network files (`announce`, `listen`, `accept`, `/net` endpoint files), `csgetvalue`, and formatting hooks.

Notable risks:
- Fixed 9000-byte request/reply buffers bound all RPC payloads.
- Reply caching is global and small (`MAXCACHE` 64).
- The DNS cache is unbounded and never expires.
- Several paths continue after malformed or non-call messages instead of closing the client, matching UDP-style service behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/server.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/string.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/string.c

Permanent interned-string table for 9nfs.

Key responsibilities:
- Stores unique strings in a 509-bucket hash table.
- Provides `strfind` for lookup without insertion and `strstore` for lookup-or-insert.
- Moves found entries to the front of their bucket for locality.
- Provides `strprint` to dump bucket indices and stored strings.
- Allocates permanent `Strnode` storage from large bump-allocated chunks.

Dependencies:
- Requires `Strnode` from `all.h`.
- Uses `panic`, `malloc`, `memmove`, `strcmp`, and `strlen`.

Notable risks:
- Strings are never freed by design.
- Hash bucket movement is not locked; callers must avoid concurrent mutation or provide external serialization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/string.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/strparse.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/strparse.c

Small destructive whitespace parser for 9nfs configuration lines.

Key responsibilities:
- Splits a mutable string into whitespace-delimited fields.
- Stops at NUL or the global comment character `strcomment`, default `#`.
- Writes NUL terminators in-place between fields.
- Always terminates the argv array with nil.

Dependencies:
- Uses Plan 9 `<u.h>` and `<libc.h>` only.

Notable risks:
- No quoting or escaping is supported.
- Input must be mutable because separators are overwritten.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/strparse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/system.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/system.c

Minimal Plan 9 process-launch helpers for 9nfs.

Key responsibilities:
- `system(name, argv)` forks, execs a command in the child, and waits for that specific child.
- Child exits with the exec error string if `exec` fails.
- Parent ignores unrelated wait messages until the target pid exits.
- `systeml` provides a varargs wrapper using the argument list after `name`.

Dependencies:
- Uses Plan 9 `fork`, `exec`, `wait`, `Waitmsg`, `errstr`, and `_exits`.

Notable risks:
- `systeml` relies on C varargs layout by taking `&name+1`, matching old Plan 9 style but not portable C.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/system.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/testit -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/testit

Small rc script for manually starting 9nfs services.

Key responsibilities:
- Mounts `nslocum` via `9fs`.
- Kills existing `8.portmapper` and `8.nfsserver`.
- Removes old service chat files.
- Starts `8.nfsserver` with auth and config options, logging stderr to `/tmp/nfsserver`.
- Starts `8.portmapper`, logging stderr to `/tmp/portmapper`.
- Notes a Unix-side NFSv2 mount command.

Dependencies:
- Plan 9 rc shell, `9fs`, `Kill`, `8.nfsserver`, and `8.portmapper`.

Notable risks:
- Hard-coded hostnames, service names, config path, and mount example make this a local test harness rather than a reusable script.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/testit -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/unixnames.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/unixnames.c

Unix user/group identity mapping support for 9nfs.

Key responsibilities:
- Maps a server/client-IP pair to a `Unixidmap` by matching server and client domain regexes.
- Caches successful server/client-IP-to-map lookups in `Unixscmap`.
- Reads the main Unix map configuration, optionally executing lines beginning with `!`.
- Tracks stale map entries and clears their loaded user/group lists when config entries disappear.
- Reloads Unix id files when their timestamp indicates they changed.
- Converts between Unix names and numeric ids with move-to-front list caching.
- Reads passwd/group-style files in Plan 9-style (`3:tom:...`) or Unix-style (`name:*:uid:gid:...`) formats.
- Reuses freed `Unixid` nodes through a free list.

Dependencies:
- Uses `strparse`, `system`, `strstore`, `regcomp`, `regexec`, `getdom`, `dirstat`, `Bopen`, and `Brdline`.
- Shares `Unixidmap`, `Unixmap`, `Unixid`, and `Unixscmap` definitions from 9nfs headers.

Notable risks:
- Regexes are compiled from configuration strings without additional anchoring except explicit full-match checks.
- `checkunixmap` compares `u->timestamp > dir->mtime`, so equal timestamps trigger reload.
- Global lists are not locked.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/unixnames.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/xfile.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/xfile.c

Cached NFS-export file and per-user fid table.

Key responsibilities:
- `xfile` hashes `(qid->path, session pointer)` into 127 buckets and returns, creates, or removes an `Xfile`.
- Moves recently used `Xfile` records to the bucket front.
- `xfid` manages per-user state hanging off an `Xfile`, including user root and open fids.
- Removal of an `Xfid` clunks active 9P fids before recycling.
- `xfpurgeuid` clears all cached fids for a user within a session.

Dependencies:
- Uses `Qid`, `Xfile`, `Xfid`, `Session`, `Lock`, `listalloc`, `strstore`, `clunkfid`, and `xfclear`.
- Uses bucket locks for `xfile` and purge traversal.

Notable risks:
- Hashing truncates session pointers through `u32int`, reflecting old 32-bit assumptions.
- `xfid` itself is not internally locked; callers must protect per-file user lists where needed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/xfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aan.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aan.c

`aan` is an always-available network relay for preserving a byte stream, commonly a 9P connection, across disconnect/reconnect events.

Key responsibilities:
- Runs in client or server mode over a dial string or network directory.
- Wraps payload chunks in a 12-byte little-endian header containing byte count, message number, and acked count.
- Buffers unsent and unacknowledged messages through Plan 9 thread channels.
- Runs separate client-reader, network-reader, and timer processes.
- Periodically sends synchronization/ack-only messages.
- Reconnects automatically and retransmits unacknowledged messages.
- Reads endpoint metadata from Plan 9 network connection directories for logging.
- Exits on client EOF or server-side listen timeout.

Dependencies:
- Uses Plan 9 threads, channels, `Alt`, `dial`, `listen`, `accept`, `/net` endpoint files, `readn`, `syslog`, and `fcallfmt`.

Notable risks:
- Fixed 8 KiB payload buffers and 10-buffer channel pools bound in-flight data.
- Header packing is explicitly little-endian.
- Message counters are `ulong`/`int` style and can wrap on long sessions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/charsets.awk -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/charsets.awk

Generator for Abaco charset alias table entries.

Key responsibilities:
- Reads IANA `character-sets` text and a Plan 9 `tcs` mapping file.
- Records each charset `Name:` and non-`none` `Alias:`.
- Emits C initializer pairs mapping aliases to Plan 9 `tcs` encoding names.
- Lowercases charset names and aliases.

Dependencies:
- Intended to generate data included by `tcs.h`.
- Expects exactly two input files.

Notable risks:
- Parsing is line-oriented and depends on IANA text formatting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/charsets.awk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/cols.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/cols.c

Column management for Abaco’s Acme-like browser layout.

Key responsibilities:
- Initializes column tags and window arrays.
- Adds, clones, closes, and closes all windows in a column.
- Resizes windows when the column rectangle changes.
- Sorts windows by vertical position.
- Implements grow and drag behavior for resizing or moving windows.
- Dispatches pointer/key events to column tag or contained windows.
- Reports column cleanliness by checking all windows.

Dependencies:
- Uses `Window`, `Text`, `Row`, global mouse state, drawing primitives, and helpers from `dat.h`/`fns.h`.
- Coordinates with `wininit`, `winresize`, `winclose`, `winmouse`, `wintype`, and row layout.

Notable risks:
- Much of the behavior is interactive geometry code; correctness depends on rectangle invariants and mouse-button state.
- Window arrays are manually reallocated and compacted.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/cols.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/dat.h

Central Abaco data model and UI/API declaration header.

Key contents:
- Defines `Runestr`, editable `Text`, layout `Line`/`Box`/`Lay`, cached image `Cimage`, URL `Url`, `Page`, `Window`, `Column`, `Row`, command `Exec`, and `Timer`.
- Declares text, box, layout, page, window, column, and row operations.
- Defines UI constants for margins, scrollbars, box sizes, tab spacing, buffer sizes, stack size, and colors.
- Declares global mouse, keyboard, image, font, row, selection, active column, webfs mount, plumbing, charset, and refresh channels.

Dependencies:
- Relies on Plan 9 draw/frame/plumb/html types such as `Frame`, `Image`, `Font`, `Docinfo`, `Item`, `Table`, and `Kidinfo`.

Notable risks:
- Many globals are declared in this header, so compilation units share mutable UI state broadly.
- `Url` uses manual reference counting; page/window history code must balance it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/exec.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/exec.c

Command execution and text-action dispatcher for Abaco.

Key responsibilities:
- Maps tag commands such as `New`, `Del`, `Get`, `Go`, `Back`, `Forward`, `Paste`, `Snarf`, `Stop`, `Sort`, `Debug`, and `Newcol` to handlers.
- Parses executable command text from tags or selections.
- Implements browser navigation commands and page lookup/open behavior.
- Handles snarf/cut/paste over text widgets.
- Expands selections around URL-like or word-like text.
- Implements search across text buffers.
- Handles plumber look events by opening URLs or matching pages.

Dependencies:
- Uses `Text`, `Window`, `Page`, `Runestr`, Plan 9 plumbing messages, and page/window functions.
- Depends on `pageget`, `pageload`, `winaddhist`, `wingohist`, `rowadd`, `coladd`, `putsnarf`, and `getsnarf`.

Notable risks:
- Command parsing is intentionally Acme-like and selection-sensitive.
- URL expansion/open behavior depends on `validurl` and `urlcombine`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/exec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/fns.h

Cross-file function declarations and small macros for Abaco.

Key contents:
- Rune allocation/move helpers.
- HTML layout/table declarations.
- Timer declarations.
- Text command operations.
- Scroll, font, charset, URL, drawing, image, execution, refresh, mouse, and window-helper declarations.
- Selection hit-testing and layout hit-testing helpers.

Dependencies:
- Complements `dat.h`; both are included by most Abaco C files.
- Uses Plan 9 and libhtml types.

Notable risks:
- Functions are grouped by subsystem but not namespace-scoped; symbol collisions are possible in the old C style.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/fonts.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/fonts.h

Static font path list for Abaco.

Key contents:
- Lists Lucida Sans normal, italic, and bold Unicode bitmap fonts at several sizes.
- Lists fixed-width Unicode bitmap fonts at several sizes.

Dependencies:
- Included by `util.c` inside font path setup.

Notable risks:
- Paths are hard-coded to Plan 9 `/lib/font/bit/...`; missing fonts affect rendering.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/fonts.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/html.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/html.c

HTML item sizing, drawing, hit-testing, and flow layout for Abaco.

Key responsibilities:
- Computes sizes for text, rules, images, form fields, buttons, selects, tables, floats, and spacers.
- Draws text, rules, images, form fields, tables, and null boxes.
- Handles link clicks, form submission, radio groups, select widgets, and form keyboard input.
- Creates and initializes layout boxes.
- Maps points to lines/boxes, including table-contained lines.
- Implements line justification, newline creation, item placement, and line fixing.
- Builds a `Lay` tree from libhtml items and renders it.
- Frees layout/table structures.
- Extracts page text into a `Runestr` for snarfing.

Dependencies:
- Uses Plan 9 draw/frame APIs and libhtml item types.
- Calls page navigation/submission helpers, `urlcombine`, `getimage`, `getfont`, `getcolor`, and table helpers from `tabs.c`.

Notable risks:
- HTML layout is custom and stateful; tables, floats, and form controls rely on many geometry invariants.
- Unsupported or incomplete HTML/CSS behavior is expected for this era of browser.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/html.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/main.c

Abaco program entry point, UI initialization, event threads, plumbing, and snarf integration.

Key responsibilities:
- Parses options for charset, webfs mount point, and stderr handling.
- Initializes draw, mouse, keyboard, colors, fonts, icons, timers, channels, and the top-level row.
- Starts mouse, keyboard, plumbing, and refresh/event processing threads.
- Loads initial pages into columns.
- Handles shutdown notices.
- Processes plumb messages into browser look/open actions.
- Dispatches keyboard and mouse events to the selected text/page/window/row objects.
- Provides snarf buffer read/write helpers using Plan 9 `/dev/snarf`.

Dependencies:
- Uses Plan 9 thread, draw, mouse, keyboard, regexp, plumb, and html libraries.
- Coordinates every Abaco subsystem through globals from `dat.h`.

Notable risks:
- UI state is global and event-thread driven.
- Startup depends on the webfs mount point being present and usable.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/page.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/page.c

Page lifecycle, loading, image fetching, rendering, selection, scrolling, and refresh handling for Abaco.

Key responsibilities:
- Loads child frames recursively from libhtml `Kidinfo`.
- Fetches and decodes images through webfs plus external image filters (`gif`, `jpg`, `png`, `ppm`, optional `resample`).
- Maintains a global cached image list with reference counts.
- Opens URLs through `urlopen`, reads response bodies, converts charset, parses HTML/plain text, fixes text, loads frames/images, and updates page state.
- Spawns page-loading work in a separate proc.
- Closes pages, child pages, layouts, images, docs, and URL/title state.
- Renders layouts and child frames, draws scrollbars, and redraws page backing images.
- Implements page selection, double-click, hit testing, mouse dispatch, key dispatch, snarfing, refresh scheduling, and meta-refresh.

Dependencies:
- Uses `urlopen`, `convert`, `parsehtml`, `laypage`, `laydraw`, `loadimages`, `addrefresh`, `flushrefresh`, `winaddhist`, and Plan 9 proc/thread APIs.
- Uses external image conversion commands through `execproc`.

Notable risks:
- Network/body loading accumulates full response contents in memory before parsing.
- Image filters are shell commands, so command strings and available tools matter.
- Page loading is asynchronous and relies on flags such as `loading`, `changed`, and `aborting`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/page.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/rows.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/rows.c

Top-level row and column layout management for Abaco.

Key responsibilities:
- Initializes the row tag and column array.
- Adds columns at a given x position and redistributes available width.
- Resizes all columns when the row rectangle changes.
- Supports dragging column boundaries.
- Closes columns and compacts the column array.
- Hit-tests points against row tag or columns.

Dependencies:
- Uses `Column`, `Row`, `Text`, drawing APIs, and column functions from `cols.c`.

Notable risks:
- Geometry is manually redistributed; small widths and edge cases are guarded but remain layout-sensitive.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/rows.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/scrl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/scrl.c

Scrollbar rendering and scrolling logic for text widgets and pages.

Key responsibilities:
- Resizes scrollbar scratch resources.
- Converts content positions to scrollbar rectangles.
- Draws text and page scrollbars.
- Sleeps while preserving UI responsiveness.
- Implements mouse-button scrolling for text frames.
- Implements vertical and horizontal page scrolling, including panning.
- Scrolls pages to absolute x/y positions.

Dependencies:
- Uses global mouse state, `Text`, `Page`, `Frame`, and Plan 9 draw APIs.
- Coordinates with `textsetorigin`, `textshow`, `pageredraw`, and `pagescrldraw`.

Notable risks:
- Scroll behavior is button-driven and depends on Plan 9 mouse semantics.
- Page and text scrolling use different coordinate models.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/scrl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/tabs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/tabs.c

HTML table sizing, row/column fixing, and table layout for Abaco.

Key responsibilities:
- Draws table boxes by drawing contained cell layouts.
- Initializes table cell layout metadata.
- Computes cell widths and heights, including spans and separators.
- Distributes table widths across fixed, percentage, and flexible dimensions.
- Computes row heights and total table height.
- Sizes a table for available width.
- Lays out table cells into rectangles and creates per-cell `Lay` structures.

Dependencies:
- Uses libhtml `Table`, `Tablecell`, `Itable`, and `Dimen`.
- Calls `layitems`, `laydraw`, `dimwidth`, `frdims`, and drawing helpers.

Notable risks:
- Column/row span calculations are compact and sensitive to malformed tables.
- Table width allocation uses heuristic distribution rather than full browser layout rules.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/tabs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/tcs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/tcs.h

Generated charset alias table consumed by Abaco’s charset conversion code.

Key contents:
- Maps IANA and common charset aliases to Plan 9 `tcs` names.
- Covers ISO-8859 variants, ASCII aliases, Big5, IBM code pages, Windows-125x, EUC-KR, GB2312, ISO-2022-JP, KOI8-R, Macintosh, Shift-JIS, Swedish ISO646 variants, Thai, EUC-JP, UTF-1, and VISCII aliases.

Dependencies:
- Included inside `tcstab[]` in `util.c`.
- Generated by `charsets.awk` and supplemented in `util.c`.

Notable risks:
- Static table can drift from IANA charset registry and installed `tcs` support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/tcs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/text.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/text.c

Editable text buffer and frame interaction layer for Abaco tags, URL fields, status fields, and form inputs.

Key responsibilities:
- Initializes, redraws, resizes, and closes `Text` objects.
- Maintains backing rune storage, frame contents, origin, and selection.
- Inserts/deletes runes and refills the visible frame.
- Implements typing, backspace/delete behavior, tab/newline handling, and selection replacement.
- Implements frame scrolling and visible-range selection.
- Implements primary, secondary, and tertiary mouse selection.
- Supports double-click matching for quotes/brackets/words and newline backing.
- Shows ranges by adjusting origin and selection.
- Dispatches text mouse actions into selection or execute/look behavior.

Dependencies:
- Uses Plan 9 `Frame` API heavily.
- Coordinates with `execute`, `look3`, `putsnarf`, `getsnarf`, scrollbar code, and global selection state.

Notable risks:
- Selection code is intricate and depends on mouse timing/buttons.
- Text buffer edits manually resize rune arrays and must keep frame and logical indices synchronized.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/text.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/time.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/time.c

Timer facility for Abaco.

Key responsibilities:
- Provides millisecond time from `nsec`.
- Starts a timer server process.
- Maintains a linked list of active timers.
- Lets callers start, stop, or cancel timers.
- Wakes timer channels when their delay expires.
- Uses cancellation flags so stopped timers are not delivered.

Dependencies:
- Uses Plan 9 threads/channels and `sleep`.

Notable risks:
- Timer list is global and simple; correctness depends on the timer process serializing updates through its channel protocol.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/time.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/urls.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/urls.c

URL object management and webfs-backed URL opening for Abaco.

Key responsibilities:
- Allocates, duplicates, reference-counts, and frees `Url` objects.
- Opens `webfs` clone files, writes requested URL commands, writes POST bodies when needed, opens response body files, and reads content type/parsed URL attributes.
- Canonicalizes path components by removing empty, `.`, and resolvable `..` elements.
- Combines base and relative URLs, including protocol-relative, absolute-path, query, fragment, and sibling-path forms.

Dependencies:
- Uses Plan 9 webfs file hierarchy under `webmountpt`.
- Uses `Runestr`, `HGet`/`HPost`, `copyrunestr`, `validurl`, and rune string helpers.

Notable risks:
- `urlcombine` is explicitly marked as a hack and mutates temporary portions of the base string while finding query boundaries.
- Error handling calls `error` for some failures but returns `-1` for others.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/urls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/util.c

General utilities for Abaco: allocation, runes, dimensions, colors, fonts, process execution, charset conversion, image fixups, refresh messages, and mouse helpers.

Key responsibilities:
- Provides checked allocation/reallocation/string helpers.
- Converts bytes to runes and manages `Runestr` lifetime/copy/equality.
- Provides word/blank scanning and item classification helpers.
- Resolves dimension values and distributes flexible dimensions.
- Looks up page background/base URL metadata.
- Allocates colors/images, draws 3D rectangles/ellipses, initializes fonts, and caches colors/fonts.
- Parses plumb attributes into runes.
- Validates URLs using a compiled regex.
- Executes shell commands with redirected pipes via `/bin/rc -c`.
- Converts charsets via built-in Latin-1/Windows control mapping or external `tcs`.
- Detects charset from HTTP content type, XML declaration, or HTML meta tags.
- Maps x coordinates to text indices and tests whether a rectangle contains selected text.
- Loads images into draw images, rewrites/merges text items, queues refresh messages, and saves/restores/clears mouse state.
- Creates a new browser window in the current column.

Dependencies:
- Includes `fonts.h` and `tcs.h`.
- Uses Plan 9 draw, memdraw, thread, regexp, and process APIs plus external `tcs`.

Notable risks:
- Several helpers shell out or depend on installed Plan 9 commands.
- Charset detection is heuristic and comment notes servers may lie.
- Global caches for fonts/colors/refresh/mouse state need disciplined lifecycle handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/wind.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/wind.c

Window object management for Abaco.

Key responsibilities:
- Initializes windows with tag, URL field, page, status field, and history.
- Resizes window subregions and page area.
- Closes windows and associated page/history/text state.
- Provides window locking.
- Builds tag text from page/window state.
- Updates URL and status text fields.
- Adds and navigates history entries.
- Hit-tests points to tag, URL, status, or page.
- Dispatches typing and mouse events to the correct subcomponent.
- Reports cleanliness and emits debug info.

Dependencies:
- Uses `Text`, `Page`, `Url`, column layout, Plan 9 draw/frame APIs, and history helpers.

Notable risks:
- History owns `Url` references and must release them correctly.
- Window layout assumes minimum heights for tag, URL, status, and page regions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/abaco/wind.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/acid.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/acid.h

Core shared declarations for the Acid debugger interpreter.

Key contents:
- Defines global interpreter state, execution flags, maps, symbols, process ids, IO stack state, and parser state.
- Defines operation codes, type tags, and format metadata.
- Defines `Type`, `Frtype`, `Ptab`, `Rplace`, `Gc`, `Store`, `List`, `Value`, `Lsym`, `Node`, and `String`.
- Declares expression, list, symbol, process, module, type, memory-indirection, debugger, lexer, parser, and GC functions.
- Defines the `expr(n,r)` dispatch macro over `expop`.

Dependencies:
- Built around Plan 9 libmach concepts: `Map`, `Symbol`, registers, process control, and executable text maps.
- Shared by parser, lexer, evaluator, builtins, and main program.

Notable risks:
- Many globals are declared through the `Extern` macro pattern.
- Node/list/string lifetime is managed by a custom mark/sweep GC.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/acid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/builtin.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/builtin.c

Builtin Acid functions for process control, file access, formatting, regex, tracing, conversion, and printing.

Key responsibilities:
- Installs builtins into the symbol table.
- Provides process operations: `newproc`, `startstop`, `waitstop`, `start`, `stop`, `kill`, `status`, `reason`, `setproc`.
- Provides stack/symbol operations: `follow`, `funcbound`, `filepc`, `pcfile`, `pcline`, `strace`.
- Provides script/module operations: `interpret`, `include`, `rc`.
- Provides file and access helpers: `readfile`, `getfile`, `access`, `error`.
- Provides conversions: `atof`, `atoi`, `itoa`, `fmt`, `fmtof`, and `fmtsize`.
- Converts libmach memory maps to Acid lists.
- Implements regex matching and list flattening for builtin argument handling.
- Implements Acid printing through `print`, `printto`, and atom/list formatting.

Dependencies:
- Uses libmach process/memory/symbol APIs, Plan 9 `/proc` controls through helper functions, regex library, Bio, and Acid AST/list helpers.

Notable risks:
- Builtins expect strict argument counts/types and report errors through the interpreter’s longjmp path.
- `rc` and process/file operations interact with the host namespace and target process state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/builtin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/dbg.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/dbg.y

Yacc grammar for the Acid debugger language.

Key responsibilities:
- Defines parser semantic value types for nodes, symbols, integers, floats, and strings.
- Defines precedence for statements, assignment, formatting, logical/bitwise/arithmetic operators, increments, indirection, field access, indexing, and calls.
- Parses top-level statements, function definitions, function deletion, and complex type definitions.
- Parses control flow: `if/then/else`, `loop`, `while`, `return`, and `local`.
- Parses expressions including casts, unary indirection, arithmetic, shifts, comparisons, logical operations, format suffixes, assignment, list construction, indexing, increment/decrement, field access, calls, builtins, constants, strings, and `what`.
- Constructs Acid AST nodes with `an` and constants with `con`.
- Executes top-level statements immediately and triggers GC afterward.

Dependencies:
- Uses tokens from `lex.c`, AST/node helpers from `main.c`, and evaluator from `exec.c`.

Notable risks:
- Grammar directly constructs executable ASTs; parser and evaluator operation-code enums must stay synchronized.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/dbg.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/dot.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/dot.c

Acid complex type definition and field-selection support.

Key responsibilities:
- Searches type member lists by name.
- Evaluates dot/arrow-style field access by adding offsets and applying member format/type metadata.
- Builds nested `Type` structures from parsed complex declarations.
- Defines complex types in the symbol table.
- Handles declarations binding names to type metadata.

Dependencies:
- Uses `Type`, `Node`, `Lsym`, `gmalloc`, `look`, `mkvar`, and expression evaluation helpers.

Notable risks:
- Type layout is script-defined and must match target ABI/debugger expectations.
- Field offsets/formats are stored in parsed nodes and transferred into custom type structures.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/dot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/exec.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/exec.c

Acid AST evaluator, memory indirection, assignment, and function-call execution.

Key responsibilities:
- Reports interpreter errors and unwinds through `longjmp`.
- Executes AST nodes by dispatching through `expop`.
- Evaluates truthiness for integers, floats, strings, and lists.
- Converts floating values to integer words for memory stores.
- Reads target memory through libmach maps in many format sizes.
- Writes target memory for assignable indirection expressions.
- Handles function calls with parameter/local binding and return unwinding.

Dependencies:
- Uses `Node`, `Map`, libmach `get1/get2/get4/get8`, `put1/put2/put4/put8`, register accessors, and global interpreter state.
- Cooperates with expression operator implementations in `expr.c`.

Notable risks:
- Memory read/write format handling is central to debugger correctness.
- Error handling is nonlocal and stateful.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/exec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/expr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/expr.c

Expression operator implementations for the Acid language.

Key responsibilities:
- Determines formatted value sizes.
- Checks lvalue validity.
- Evaluates list sequencing, forced evaluation, casts, memory/code indirection, stack-frame lookup, indexing, append/delete/head/tail, constants, names, complex construction, assignment, arithmetic, shifts, comparisons, equality, bitwise/logical operators, unary not, pre/post increment/decrement, function calls, formatting, and `what`.
- Handles mixed integer/float/string/list cases where Acid defines them.
- Dispatches complex field access through `odot`.

Dependencies:
- Uses global `expop`, `Node`, `List`, `Value`, libmach maps, `indir`, `windir`, `call`, `append`, `delete`, `nthelem`, `stradd`, and string/list helpers.

Notable risks:
- Type coercion behavior is manual and old-debugger-specific.
- Many operators mutate `Node` results in place; correctness depends on exact `type`, `fmt`, and value fields.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/expr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/lex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/lex.c

Lexer and input stack for the Acid language.

Key responsibilities:
- Initializes keyword table.
- Pushes files or strings as lexer input sources.
- Restarts and pops IO sources.
- Formats symbols through `%L`.
- Provides character pushback, escaped-character decoding, string scanning, newline/comment handling, and tokenization.
- Parses identifiers, numbers, format suffixes, strings, and reserved words.
- Maintains the Acid symbol table with `enter`, `look`, and `mkvar`.

Dependencies:
- Uses Bio for file input, y.tab token definitions, Acid string/node helpers, and global parser state.

Notable risks:
- Lexer state is global and stacked manually.
- Number/symbol parsing is integrated with Acid’s format suffix syntax.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/list.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/list.c

Acid list construction, mutation, comparison, and stack-trace list helpers.

Key responsibilities:
- Constructs runtime lists from AST list nodes.
- Computes list length and marks lists for GC.
- Concatenates lists, appends values, deletes elements, compares lists, and retrieves nth elements.
- Creates single-value lists from variables.
- Builds lists of local variables and parameters from libmach symbols and frame data.
- Builds a trace list for the current stack frame with locals and parameters.

Dependencies:
- Uses `List`, `Node`, `Map`, `Symbol`, `gmalloc`, `expr`, `listvar`, libmach symbol APIs, and stack/register state.

Notable risks:
- List mutation copies value fields manually.
- Stack trace local/parameter extraction is target-symbol dependent.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/main.c

Acid debugger program entry point, module loading, target attachment, GC, and utility allocation.

Key responsibilities:
- Parses options for kernel mode, write mode, library modules, machine type, quiet mode, and remote mode.
- Selects target executable or process text file, including `/proc/<pid>/text` and kernel system image lookup.
- Initializes formatters, Bio output, lexer keywords, variables, builtins, target maps, default modules, user modules, and symbol/register variables.
- Runs the interactive parse/evaluate loop with error recovery.
- Attaches executable and process files through libmach and process helpers.
- Loads machine-specific Acid modules from `/sys/lib/acid`.
- Loads user startup Acid files from `$home/lib/acid`.
- Allocates AST nodes, list nodes, constants, and GC-managed memory.
- Implements custom mark/sweep GC over nodes, lists, symbols, and strings.
- Handles notes, qid checks for process text changes, system-image lookup, numeric argument detection, and hex formatting.

Dependencies:
- Uses Plan 9 libmach, Bio, yacc parser, lexer, builtins, process-control helpers, and the Acid runtime structures.

Notable risks:
- The interpreter relies on global mutable state and nonlocal error unwinding.
- GC correctness depends on every live node/list/string being marked from symbols and current execution roots.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acid/main.c -->