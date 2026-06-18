# Group Research: group_40_9front_sources_os_plan9_9front_sys_src_cmd_9nfs_portmapper_c_sources__7072bae066dd

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/portmapper.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/portmapper.c

SunRPC portmapper service for the 9nfs suite.

Key responsibilities:
- Defines static RPC program/version/protocol-to-port mappings for NFSv2, mount, and pcnfsd.
- Exports RPC program `100000` version `2` on UDP port `111`.
- Implements portmapper procedures: null, set, unset, getport, dump, and callit.
- Delegates daemon setup and packet serving to the shared `server()` RPC framework.

Important behavior:
- `pmapset()` always returns false and `pmapunset()` always returns true; the static map is not mutated.
- `pmapgetport()` decodes four 32-bit arguments but only uses program, version, and protocol.
- `pmapdump()` serializes the full static mapping list.
- `pmapcallit()` only answers when the mapped procedure is zero and returns the mapped port plus an empty result, not a proxied RPC call.

Dependencies:
- Uses `all.h`, `rpc.h` XDR-style macros, `Progmap`, `Procmap`, `Rpccall`, and shared logging/error helpers.

Notable risks:
- Hard-coded ports must stay aligned with the actual NFS/mount/pcnfsd services.
- Request length checks are strict but parsing assumes `rpcM2S()` already supplied a sane argument buffer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/portmapper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/rpc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/rpc.c

RPC/XDR marshaling, unmarshaling, diagnostics, and common reply helpers for 9nfs daemons.

Key responsibilities:
- `rpcM2S()` decodes UDP-header-prefixed SunRPC messages into `Rpccall`.
- `rpcS2M()` serializes `Rpccall` replies/calls back into UDP-header-prefixed network buffers.
- `auth2unix()` decodes `AUTH_UNIX` credentials into `Authunix`.
- `string2S()` decodes counted XDR strings, NUL-terminates them, and interns them.
- `rpcprint()` and `showauth()` provide debug formatting.
- `garbage()` and `error()` set common RPC failure/result payloads.

Important behavior:
- IPv4 addresses are extracted from Plan 9 `Udphdr` IPv4-mapped address tails.
- XDR pointer fields are aliases into the original packet buffer, except strings interned by `string2S()`.
- Variable-length fields advance by 4-byte-rounded XDR sizes.
- `auth2unix()` skips surplus gids beyond the fixed local `gids` array.

Dependencies:
- Uses `rpc.h` constants/macros, Plan 9 UDP headers, `strstore()`, and logging helpers.

Notable risks:
- Decode macros do not perform local bounds checks on every individual field; callers rely on final byte-count validation.
- `string2S()` trusts the encoded length enough to allocate `n+1`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/rpc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/rpc.h

Shared SunRPC protocol constants and XDR helper macros for 9nfs.

Key contents:
- Defines boolean, auth flavor, message type, accepted/rejected reply, and auth-status enums.
- Defines protocol numbers for TCP and UDP.
- Defines `ROUNDUP()` for 4-byte XDR alignment.
- Defines output macros `PLONG`, `PPTR`, `PBYTE`.
- Defines input macros `GLONG`, `GPTR`, `GBYTE`.

Role:
- Centralizes protocol numbers and serialization primitives used by portmapper, NFS, mount, and RPC support code.

Notable risks:
- Macros depend on caller-local variables named `dataptr` and `argptr`.
- `GPTR(n)` has statement-like expansion and should be used carefully in expression contexts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/rpc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/server.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/server.c

Shared SunRPC server runtime for 9nfs daemons, with UDP/TCP listeners, dispatch, DNS cache, and duplicate-reply cache.

Key responsibilities:
- Parses common daemon flags through `argopt()`.
- Daemonizes, initializes program maps, and starts UDP or TCP service.
- Announces UDP sockets with header mode or accepts TCP connections and synthesizes UDP-style endpoint headers.
- `servemsg()` decodes RPC calls, validates RPC version/auth policy, dispatches to `Progmap`/`Procmap`, serializes replies, and caches them.
- Supports TCP record-mark read/write framing.
- Maintains a small DNS name cache and maps client IPs to domain names.
- Maintains an LRU cache of up to 64 replies by host, port, and XID.

Important behavior:
- `rejectall` forces `AUTH_TOOWEAK`.
- Program mismatch replies report observed low/high versions.
- Procedure handlers return negative length to suppress reply.
- The alarm helper process sets `alarmflag`; `servemsg()` invokes `rpcalarm` lazily between messages.
- TCP children process one accepted connection until EOF/error.

Dependencies:
- Uses Plan 9 network APIs (`announce`, `listen`, `accept`), `ndb` lookup, `rpcM2S()`, `rpcS2M()`, `rpcprint()`, and global buffers from this file.

Notable risks:
- Global buffers and reply cache fit the single-threaded UDP path but require care around forked TCP children.
- Reply-cache keys ignore RPC program/procedure and depend on XID uniqueness per client endpoint.
- `getdnsdom()` writes `name[len] = 0` after copying `len-1`, which is off by one for the passed buffer length.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/server.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/string.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/string.c

Permanent string interning table for 9nfs.

Key responsibilities:
- `strfind()` looks up an already-interned string.
- `strstore()` interns strings and returns stable storage.
- `strprint()` dumps hash buckets for diagnostics.
- Allocates `Strnode` objects from permanent chunk storage.

Important behavior:
- Hash buckets are move-to-front on lookup/store hits.
- Storage is never individually freed; chunks grow from `STRSIZE` upward to fit large strings.
- String payloads are 4-byte aligned inside `Strnode` allocations.

Dependencies:
- Uses `Strnode` from shared headers and Plan 9 allocation/logging helpers.

Notable risks:
- Unbounded lifetime is intentional for daemon caches, but dynamic or hostile names can grow memory permanently.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/string.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/strparse.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/strparse.c

Small whitespace tokenizer for 9nfs configuration lines.

Key responsibilities:
- Splits a mutable string into argv-style fields separated by spaces or tabs.
- Stops parsing at NUL or the configurable comment character `strcomment`.
- NUL-terminates fields in place and returns the argument count.

Important behavior:
- Leaves `arv[arc]` as nil.
- Reserves one argv slot for the terminating nil by stopping at `arsize-1`.

Dependencies:
- Standalone Plan 9 libc file.

Notable risks:
- Does not support quoting or escaping; config files using spaces inside fields cannot be represented.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/strparse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/system.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/system.c

Minimal fork/exec/wait wrapper for 9nfs helper command execution.

Key responsibilities:
- `system()` forks, execs a named command with argv, and waits for the matching child `Waitmsg`.
- Child exits with the exec error string if `exec()` fails.
- `systeml()` varargs convenience wrapper passes `&name+1` as argv.

Dependencies:
- Plan 9 process APIs: `fork`, `exec`, `wait`, `errstr`, `_exits`.

Notable risks:
- Name collides with standard C `system()` concept but uses Plan 9 `Waitmsg*` semantics.
- `systeml()` relies on varargs layout idiom and caller-supplied nil terminator.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/system.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/testit -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/testit

Rc script for manually starting and testing 9nfs services.

Key responsibilities:
- Mounts or prepares the `nslocum` namespace via `9fs`.
- Kills existing `8.portmapper` and `8.nfsserver` processes.
- Removes service chat files.
- Starts `8.nfsserver` with address/config options and `8.portmapper`, redirecting stderr logs.

Role:
- Developer/operator smoke-test helper for NFS server and portmapper setup.

Notable risks:
- Hard-coded host/service names and architecture-prefixed binaries make it environment-specific.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/testit -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/unixnames.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/unixnames.c

Unix uid/gid and hostname mapping support for 9nfs authentication.

Key responsibilities:
- Maps `(server, client IP)` pairs to `Unixidmap` entries using regexes and DNS-domain lookup.
- Reads mapping config files and refreshes user/group maps when backing files change.
- Supports config lines that execute helper commands prefixed with `!`.
- Parses Unix-style passwd/group-like files and Plan 9-style id files.
- Provides `name2id()`, `id2name()`, and `idprint()` lookup/debug helpers.
- Reuses freed `Unixid` nodes through a local free list.

Important behavior:
- Uses client IP rather than hostname because some clients omit host identity.
- Server and client patterns are compiled regexes and must match the entire string.
- Stale mappings are invalidated when config entries disappear.
- `checkunixmap()` reloads when file mtime is newer than the stored timestamp.

Dependencies:
- Uses `strparse()`, `system()`, regex APIs, DNS helper `getdom()`, `strstore()`, and Plan 9 `bio`.

Notable risks:
- Helper command execution from config is powerful and depends on trusted config files.
- Domain lookup/cache behavior affects auth mapping correctness.
- `pair2idmap()` returns `r` after the scan; if no regex matches, `r` is nil by loop termination but this is implicit.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/unixnames.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/xfile.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/xfile.c

Qid/session and user-fid cache for 9nfs file objects.

Key responsibilities:
- `xfile()` finds, creates, or removes `Xfile` objects keyed by qid path and session pointer.
- `xfid()` finds, creates, or removes per-user `Xfid` objects under an `Xfile`.
- Removed `Xfid` entries clunk associated user/root and open fids.
- `xfpurgeuid()` clears all cached fids for a user within a session.

Important behavior:
- `xfile()` uses 127 hash buckets protected by per-bucket locks.
- Recently-used file/fid entries are moved to the front of their lists.
- Free lists are batch-allocated with `listalloc()`.

Dependencies:
- Uses `Xfile`, `Xfid`, `Session`, `Qid`, `clunkfid()`, `xfclear()`, and string interning.

Notable risks:
- Hashing casts session pointers down through `u32int`, which is architecture-sensitive.
- `xfid()` itself is not locked; callers must rely on surrounding `Xfile`/session locking discipline.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/9nfs/xfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aan.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aan.c

Authenticated/reconnecting stream relay that preserves ordered buffered messages across reconnects.

Key responsibilities:
- Runs as client (`-c`) dialing a dialstring or server accepting from an existing net directory.
- Spawns threads for stdin-to-buffer, network-to-stdout, and timer ticks.
- Frames payloads with message number and cumulative ack fields.
- Buffers unsent/unacked messages in Plan 9 channels.
- Detects hung links via periodic sync headers and reconnects for up to `maxto`.
- Resends unacked messages after reconnect through `synchronize()`.

Important behavior:
- `Hdr.nb == 0` with `msg == -1` is a keepalive/sync ack-only frame.
- Incoming messages must match `inmsg`; out-of-order messages are skipped.
- Ack processing returns completed buffers from `unacked` to `empty`.
- EOF from stdin sends a zero-length final message and shuts down after transmission.
- `catch()` exits the process on reconnect timeout alarm.

Dependencies:
- Uses Plan 9 threads/channels, `dial`, `listen`, `accept`, `getnetconninfo`, and big-endian bit macros.

Notable risks:
- Shared globals such as `netfd`, `done`, and counters are manipulated by multiple procs without explicit locks.
- Skipped out-of-order frames rely on retransmission after reconnect rather than local reordering.
- The fixed channel depth limits in-flight buffered data to `Nbuf * Bufsize`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/cols.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/cols.c

Column-level layout and window management for the Abaco browser UI.

Key responsibilities:
- Initializes column tags and column background/borders.
- Adds, removes, closes, resizes, sorts, grows, and drags windows in a column.
- Maintains `Column.w[]`, `Column.nw`, and `Column.safe` layout state.
- Routes mouse/keyboard hits inside a column to column tags or contained windows.
- Checks column cleanliness through contained windows.

Important behavior:
- New windows split an existing window or steal half of the last window by default.
- `colgrow()` supports fixed repair, full-column expansion, maximum expansion, and incremental growth.
- Dragging can move a window to another column, reorder it, or resize the boundary with the previous window.
- `Column.safe == FALSE` represents an obscured/full-size layout state that must be repaired before some operations.

Dependencies:
- Uses `Text`, `Window`, `Row`, screen drawing, mouse state helpers, and window resize/tag APIs.

Notable risks:
- Manual rectangle arithmetic must maintain non-overlap and minimum usable heights.
- `realloc(c->w, c->nw*sizeof(Window*))` with zero count depends on Plan 9 libc behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/cols.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/dat.h

Core Abaco type definitions, UI object model, globals, constants, and function declarations for text/page/window/row/column layout.

Key contents:
- Defines `Runestr`, `Text`, `Line`, `Box`, `Lay`, `Cimage`, `Url`, `Page`, `Window`, `Column`, `Row`, `Exec`, and `Timer`.
- Declares text editing, layout, page loading/rendering, URL, window, column, row, and timer APIs.
- Defines UI constants for scrollbars, margins, borders, tab space, font index calculation, buffer sizes, and stack size.
- Declares global images, fonts, cursors, controllers, row state, selection state, plumbing fds, channels, charset, and webfs mount point.

Role:
- Shared structural contract across the Abaco browser implementation.

Notable risks:
- Many globals couple event handling, rendering, page loading, and selection state.
- `Page` holds both rendered layout and asynchronous loading/refresh state, so lifetime/refcount discipline matters.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/exec.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/exec.c

Abaco command dispatch, selection commands, search/look behavior, new window creation, and plumber integration.

Key responsibilities:
- Defines the tag command table (`Back`, `Cut`, `Del`, `Get`, `Google`, `New`, `Paste`, `Stop`, etc.).
- Expands clicked text into executable command names or search/look terms.
- Implements editing commands using `Text` and page selection state.
- Implements navigation/history commands and page loading from URL tags.
- Sends look targets to plumber or searches selected text.
- Opens pages in existing matching windows or newly made windows.
- Handles incoming plumb messages for web targets.

Important behavior:
- Middle-click executes commands; right-click looks/plumbs/searches.
- `Cut`/`Snarf` operate on page selection if `selpage` is set, otherwise on text selection.
- `Get` reloads or loads from the URL tag and records history only when URL changes.
- `Google` builds a query URL with percent-encoded argument text.

Dependencies:
- Uses `Text`, `Page`, `Window`, `Column`, `Row`, snarf/plumb helpers, URL validation, and page loading.

Notable risks:
- Command lookup is prefix/word based after whitespace trimming; tag contents must avoid ambiguity.
- `look3()` falls back from plumber to local search, so plumber availability changes user-visible behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/exec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/fns.h

Shared Abaco helper prototypes and rune convenience macros.

Key contents:
- Defines `runemalloc`, `runerealloc`, `runemove`, `hasbrk`, and `istrue`.
- Declares functions for plumbing, snarf, table layout, timers, command execution, search, scrolling, font/color utilities, URL composition, refresh, image loading, forms, layout lookup, and window creation.

Role:
- Complements `dat.h` with cross-file function declarations.

Notable risks:
- Macro wrappers do no overflow checking on rune counts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/fonts.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/fonts.h

Default Abaco font path table included into `util.c`.

Key contents:
- Lists Lucida Sans regular, italic, and bold Unicode fonts at five sizes.
- Lists fixed-width Unicode fonts at five sizes.
- Provides exactly the default entries expected by `NumFnt`.

Role:
- Supplies fallback font paths when `$home/lib/abaco.fonts` is absent or incomplete.

Notable risks:
- This is not a standalone C header with declarations; it is an initializer fragment.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/fonts.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/html.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/html.c

HTML item sizing, layout, drawing, hit-testing, links, forms, selection extraction, and table recursion for Abaco pages.

Key responsibilities:
- Computes dimensions for text, rules, images, form controls, tables, floats, and spacers.
- Draws text with selection highlighting and underlines, rules, images, form controls, and tables.
- Creates `Box` objects inside `Line` layout rows and assigns draw/mouse/key handlers.
- Implements link clicking with target frame resolution and button-specific behavior.
- Implements form submission, radio/checkbox/select/text field interaction, and form text input.
- Lays out item streams into wrapped lines and nested table layouts.
- Provides line/box hit-testing and `laysnarf()` text extraction from selections.

Important behavior:
- Form text fields lazily allocate embedded `Text` objects and store them in item `aux`.
- Link button 1 loads, button 2 copies URL to status, button 3 sends to plumber.
- Submit builds either query-string GET URL or POST body depending on form method.
- Table and form layout owns nested `Lay` and `Text` cleanup in `layfree()`.

Dependencies:
- Uses libhtml item structs, Abaco page/window utilities, image cache, URL helpers, text editing, and drawing APIs.

Notable risks:
- `boxinit()` tests `if(b->i->anchorid)` rather than `>= 0`, which may skip anchor id 0 while treating negative ids as true unless overridden.
- Selection and layout state are tightly coupled to rectangle coordinates; stale layout after resize/load can affect hit testing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/html.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/main.c

Abaco process entry point, display/webfs initialization, event threads, icon/color setup, and snarf support.

Key responsibilities:
- Parses options for initial column count, webfs mount point, charset, font, and stderr behavior.
- Opens webfs control, snarf device, display, mouse, keyboard, and plumber fds.
- Initializes icons, timers, fonts, global row/columns, and initial URL pages.
- Spawns keyboard and mouse event threads.
- Handles window resize, plumb messages, refresh channel, mouse buttons, and keyboard input.
- Implements snarf read/write helpers.

Important behavior:
- Uses `rfork(RFENVG|RFNAMEG)` to isolate environment/name space.
- Initial URLs are distributed up to `WPERCOL` per column.
- Keyboard input updates `activecol` except for scroll/navigation keys.
- Mouse thread locks the global row around hit dispatch.
- Large snarf buffers are not written to avoid rio truncation.

Dependencies:
- Uses Plan 9 draw/thread/plumb APIs, Abaco row/page/text command code, and webfs at `/mnt/web` by default.

Notable risks:
- `putsnarf()` writes chunks but formats from `rs->r` rather than `rs->r+i`, so repeated chunks would duplicate the beginning for large selections.
- Event threads depend on global mouse pointer state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/page.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/page.c

Page loading, image loading/cache, frames, rendering, selection, scrolling dispatch, refresh metadata, and page lifecycle for Abaco.

Key responsibilities:
- Loads pages asynchronously through webfs and `uhtml`, then parses HTML/plain text with libhtml.
- Loads and caches images through MIME-specific filter pipelines.
- Handles framesets by recursively creating child `Page` objects from `Kidinfo`.
- Closes/aborts pages and recursively frees documents, layouts, children, images, titles, and refresh state.
- Renders pages into page rectangles and child frame rectangles.
- Handles page mouse and keyboard input, including links/forms, text selection, and scrollbars.
- Extracts selected page text to snarf.
- Parses meta-refresh URL/time and triggers refresh reloads.

Important behavior:
- Empty content type is treated as HTML.
- Unsupported non-text MIME types become status errors.
- Image cache entries are refcounted and shared by source URL.
- `pageabort()` recursively marks aborting and waits while `loading` is nonzero.
- `pageredraw()` renders into a global temporary image, then copies to the screen.

Dependencies:
- Uses webfs, external filters (`uhtml`, image decoders, `resize`), libhtml parser, layout/draw code, URL helpers, and refresh channel.

Notable risks:
- Page loading and UI refresh share mutable `Page` fields across procs with limited locking.
- `loadimg()` returns partially initialized `Cimage` objects on error for placeholder rendering.
- `pageabort()` busy-waits in 100 ms intervals until loader clears state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/page.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/rows.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/rows.c

Top-level row and column management for Abaco.

Key responsibilities:
- Initializes the root row tag and starting rectangle.
- Adds columns by splitting existing column rectangles.
- Resizes all columns proportionally on screen resize.
- Drags columns to reorder or resize adjacent column boundaries.
- Closes columns and expands neighbors into freed space.
- Locates columns/text by point for event dispatch.

Important behavior:
- Default new column steals about 40% of the last column.
- Column additions enforce rough minimum widths.
- Dragging a column can shuffle it before/after other columns or resize its left neighbor.
- The row tag contains top-level commands `Newcol Google Exit`.

Dependencies:
- Uses `Column`, `Text`, draw primitives, mouse state, and column APIs.

Notable risks:
- Manual width constraints are heuristic and can still produce cramped layouts on small screens.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/rows.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/scrl.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/scrl.c

Scrollbar drawing and scrolling behavior for Abaco text frames and rendered pages.

Key responsibilities:
- Allocates temporary vertical/horizontal scrollbar images on resize.
- Computes scrollbar thumb rectangles from visible range and total size.
- Draws `Text` scrollbars and page horizontal/vertical scrollbars.
- Implements mouse-driven text scrolling.
- Implements page scrollbar dragging/page jumps for horizontal and vertical axes.
- Provides pixel delta page scrolling helper `pagescrollxy()` and sleep-with-mouse-interrupt helper.

Important behavior:
- Middle button drags to absolute position; button 1/3 page or pan backward/forward.
- Scrollbar position math scales down very large totals to avoid overflow.
- Page panning accelerates based on pointer movement away from the original point.

Dependencies:
- Uses timer helpers, global mouse controller, draw images, `Text` frame APIs, and page redraw.

Notable risks:
- `pagescrollxy()` can compute negative upper bounds when layout is smaller than viewport; callers rely on max/min clamping behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/scrl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/tabs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/tabs.c

HTML table sizing, layout, and drawing support for Abaco.

Key responsibilities:
- Draws table backgrounds, borders, cells, and nested cell layouts.
- Computes per-cell min/max widths by laying out content with narrow and wide constraints.
- Computes column widths from cell constraints, colspan, specified dimensions, and available width.
- Computes row heights from cell content, rowspan, and specified heights.
- Computes total table width/height including border, padding, and spacing.
- Lays table cells into final rectangles with nested `Lay` objects.

Important behavior:
- `settables()` marks top-level table items and precomputes table constraints for all document tables.
- Colspan/rowspan of zero extends to the remaining columns/rows.
- Width distribution interpolates between min and max widths when max width exceeds available space.
- Top-level table width can expand to fill available width when specified.

Dependencies:
- Uses libhtml `Table`, `Tablecell`, `Itable`, `Dimen`, and Abaco `layitems()`.

Notable risks:
- Table layout is O(cells * repeated layout passes), which can be expensive for large/nested tables.
- Several arrays are allocated from `t->ncol`; malformed table metadata would be hazardous.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/tabs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/text.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/text.c

Abaco text widget implementation: rune storage, frame rendering, editing, selection, scrolling, and mouse commands.

Key responsibilities:
- Initializes, redraws, resizes, closes, inserts into, deletes from, and fills `Text` frames.
- Handles typed input, navigation keys, URL-enter action, textarea editing, and erase-word/line.
- Implements frame auto-scroll during selection.
- Implements single/double-click selection, chorded cut/paste, and scroll-area behavior.
- Draws and maintains selection ranges in frame coordinates.
- Implements bracket/quote/newline matching for double-click.
- Routes button 1/2/3 to select, execute, and look behavior.

Important behavior:
- Non-textarea newline in URL tag triggers `Get`.
- Tag text ignores one-line scroll wheel keys.
- `textshow()` scrolls textarea origin to keep selection visible.
- Chording can undo immediate cut/paste state while the mouse button is held.
- `textsetorigin()` reuses frame contents when scrolling by small deltas.

Dependencies:
- Uses Plan 9 frame library, Abaco command functions, scroll helpers, snarf helpers, and global selection state.

Notable risks:
- Text operations assume `Text.rs.r` has enough trailing room for NUL after deletion; insert allocation is exactly `nr+n`, so NUL writes after delete rely on prior capacity.
- Complex selection paths are stateful across globals `clicktext`, `selecttext`, `argtext`, and mouse controller state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/text.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/time.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/time.c

Small timer scheduler for Abaco event loops.

Key responsibilities:
- Maintains reusable `Timer` objects and a global timer-start channel.
- Starts a timer proc that tracks active timers in milliseconds.
- Supports starting, canceling, and stopping/recycling timers.
- Delivers timer expiration with nonblocking sends to each timer’s channel.

Important behavior:
- The timer proc sleeps at minimum increments and subtracts elapsed time from all active timers.
- Canceled timers and successfully delivered timers are removed and recycled.
- When no timers are active, the proc blocks waiting for a new timer.

Dependencies:
- Uses Plan 9 thread channels and `nsec()`.

Notable risks:
- Timer free list is not locked; code assumes timer operations occur in the process/thread model without conflicting concurrent mutation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/time.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/urls.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/urls.c

URL object allocation, webfs opening, canonicalization, and relative URL combination for Abaco.

Key responsibilities:
- Allocates/refcounts/frees/duplicates `Url` objects.
- Opens URLs through webfs clone/control/body files, including POST bodies.
- Reads content type and parsed/actual URL attributes from webfs.
- Canonicalizes path components after `://`, resolving empty, `.`, and `..` elements.
- Combines base and relative URLs, including scheme-relative, absolute-path, query, fragment, and path-relative cases.

Important behavior:
- `urlopen()` writes `url <src>` to a webfs connection and returns an open body fd.
- If parsed URL is missing, actual URL falls back to source URL.
- POST body is written before opening the response body.
- `urlcombine()` duplicates already-valid absolute URLs.

Dependencies:
- Uses global `webmountpt`, rune helpers, `validurl()`, and Plan 9 webfs layout.

Notable risks:
- `getattr()` sets `Runestr.nr` to byte count rather than rune count; ASCII metadata works, but non-ASCII metadata can be inconsistent.
- `urlcanon()` mutates the URL string in place while splitting components.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/urls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/util.c

General Abaco utilities for allocation, runes, fonts, colors, forms, URL validation, external pipelines, images, text normalization, refresh batching, and new-window placement.

Key responsibilities:
- Provides checked allocation/string/rune helpers and min/max.
- Converts bytes to runes and manages `Runestr` copies.
- Computes dimension specs for frames and tables.
- Manages font path defaults/user overrides and lazy font opening.
- Caches solid-color images by RGB value.
- Sends plumber messages and percent-encodes query strings.
- Validates absolute URLs with a regexp.
- Runs external filter pipelines with `/bin/rc`.
- Parses content-type parameters.
- Converts `Memimage` image data into display `Image` or placeholder images.
- Splits wrappable text items on whitespace for better layout.
- Queues and flushes page refresh/redraw/status updates.
- Chooses a target column/window for newly opened pages.

Important behavior:
- `flushrefresh()` is called while the row is locked and updates render, status, URL, and tag state.
- `addrefresh()` increfs the page window until flush drains the refresh entry.
- `fixtext()` applies to top-level items and all table cell content.
- `makenewwindow()` prefers active column, selected page column, source page column, then last row column.

Dependencies:
- Uses libhtml types, Plan 9 draw/memdraw/thread/plumb/regexp, Abaco page/window/layout APIs, and external rc commands.

Notable risks:
- The URL regexp only recognizes schemes with `://`, excluding valid `mailto:` style URLs despite listing `mailto`.
- `getimage()` placeholder/image conversion assumes display image loading succeeds and consumes `ci->mi`.
- Refresh batching depends on correct window refcounts to avoid use-after-free during async page loading.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/wind.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/wind.c

Abaco window initialization, resizing, lifecycle, locking, tag/status/URL updates, history, and event routing.

Key responsibilities:
- Initializes a window with tag, URL, page area, status text, borders, and button image.
- Resizes window subregions and rerenders pages when page area changes.
- Closes text fields, page contents, URL history, and window storage by refcount.
- Provides `winlock()`/`winunlock()` around window event processing.
- Rebuilds window tags from title, commands, history availability, loading state, and title suffix.
- Updates URL and status text widgets.
- Maintains back/next history and loads history entries.
- Routes mouse/keyboard input to tag/url/status text or page.
- Provides debug dump.

Important behavior:
- `winsettag()` is skipped when the column is unsafe/fullscreen-obscured.
- History truncates forward entries when a new URL is added after going back.
- `wingohist()` increfs the historical URL before loading it.
- `winclean()` currently always returns true, so close prompts are effectively disabled.

Dependencies:
- Uses `Page`, `Text`, `Url`, column safety state, screen drawing, and refcount helpers.

Notable risks:
- Tag rewriting tries to preserve user selection but the preserved-bar logic is mostly disabled.
- Refcounted window lifetime depends on each lock/event/refresh path pairing incref/decref correctly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/abaco/wind.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/acid.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acid/acid.h

Central declarations, global state, data structures, and opcode definitions for the Acid debugger language.

Key contents:
- Defines interpreter limits, value types, format checking, and AST opcodes.
- Declares global debugger/interpreter state: maps, process table, symbol hash, IO stack state, current executable, GC state, return context, flags, and output buffers.
- Defines `Type`, `Frtype`, `Ptab`, `Rplace`, `Gc`, `Store`, `List`, `Value`, `Lsym`, `Node`, and `String`.
- Declares parser, evaluator, memory access, debugger process control, symbol, list, GC, module, and formatting functions.

Role:
- Shared ABI for the Acid parser, evaluator, builtins, lexer, list support, and main program.

Notable risks:
- The interpreter stores many mutable globals; reentrancy is not a design goal.
- `Store` is reused in `Node`, `List`, and `Value`, so type/fmt fields must stay coherent.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/acid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/builtin.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acid/builtin.c

Built-in Acid functions for conversion, printing, files, process control, maps, stack traces, regex, shell execution, and debugger metadata.

Key responsibilities:
- Registers builtins in the symbol table and records the default `print` call node.
- Implements conversions: `atoi`, `atof`, `itoa`, `fmt`, `fmtof`, `fmtsize`.
- Implements printing to stdout or files and atom/list formatting.
- Implements file reading as strings or lists of lines.
- Implements debugger process controls: `newproc`, `setproc`, `start`, `stop`, `waitstop`, `startstop`, `kill`, `status`.
- Implements source/PC helpers: `filepc`, `pcfile`, `pcline`, `fnbound`, `follow`, `reason`, `strace`.
- Implements map inspection/update through `map()`.
- Implements `include()` and `interpret()` for loading/evaluating Acid source.
- Implements shell command execution through `rc()`.
- Implements list membership match, regexp matching, sysr1, access checks, and field splitting.

Important behavior:
- `flatten()` converts comma/OLIST argument trees into positional arrays.
- `patom()` interprets Acid format characters and uses mach disassembly for `i`/`I`.
- `map()` can mutate existing map segment base/end/file offset when given a 4-element list.
- Builtin calls validate argument counts and types explicitly.

Dependencies:
- Uses Plan 9 `mach` library, process control helpers from other Acid files, regex, bio, and global `bout`.

Notable risks:
- `acidfmt()` has delicate percent-format rewriting logic for `itoa`.
- `readfile()` allocates based on file length or 8192 default and reads once; it may not read growing/streaming files fully.
- `printto()` replaces global `bout` temporarily, so error unwinding must restore IO state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/builtin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/dbg.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acid/dbg.y

Yacc grammar for the Acid debugger language.

Key responsibilities:
- Defines token/value types for identifiers, constants, floats, strings, statements, and expressions.
- Parses top-level statements, function definitions/deletions, and complex type definitions.
- Parses statements: blocks, if/else, loop ranges, while, return, local declarations, and complex declarations.
- Parses expressions with precedence for assignment, formatting, logic, bitwise, comparison, shifts, arithmetic, casts, indexing, field selection, calls, builtins, list literals, constants, strings, eval, head/tail/append/delete, and whatis.
- Executes top-level statements immediately through `execrec()`.

Important behavior:
- Function definitions store an AST `OLIST(args, body)` in the symbol’s `proc`.
- `fn name` without body clears a function.
- `builtin name(args)` forces lookup of a registered builtin.
- Newlines in interactive mode are converted by the lexer to semicolon-like statement terminators.

Dependencies:
- Uses `Node` allocation helpers, `defcomplex()`, `execrec()`, and lexer tokens from `lex.c`.

Notable risks:
- Grammar builds ASTs directly during parse; parse-time side effects for top-level execution affect interactive behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/dbg.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/dot.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acid/dot.c

Complex-type field lookup, field access, and type declaration support for Acid.

Key responsibilities:
- Searches type field lists by tag, preferring shallower nesting depth.
- Implements `(expr).field` by evaluating an address, finding a matching field, and reading or returning the field address.
- Builds `Type` lists from parsed complex/member ASTs.
- Defines complex types with `defcomplex()`.
- Declares variables or frame locals as complex types with `decl()`.

Important behavior:
- Field format `a` propagates nested complex type metadata and returns an address value.
- Non-address fields are read through `indir(cormap, addr, fmt, r)`.
- Frame declarations attach `Frtype` metadata to function symbols for later `frame:local` lookup.

Dependencies:
- Uses evaluator `expr()`, memory indirection, type symbols, and AST nodes from parser.

Notable risks:
- Complex member lists are append-only on the symbol’s `lt`; redefining without clearing can accumulate fields.
- Field access requires integer addresses and an existing `comt` type annotation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/dot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/exec.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acid/exec.c

Statement execution, function call frames, memory writes, indirection reads, error unwinding, and local-scope management for Acid.

Key responsibilities:
- `error()` reports interpreter errors, unwinds IO stack, resets state, and longjmps to the main loop.
- `unwind()` pops local value frames from all symbols.
- `execrec()` roots the current command for GC and executes it.
- `execute()` handles statements, loops, conditionals, returns, local declarations, complex declarations, and expression statements.
- `bool()` converts Acid values to truth.
- `indir()` reads typed values from maps using format characters.
- `windir()` writes typed values back to core/symbol maps for `*=` and `@=`.
- `call()` binds actual/formal arguments, supports by-code formal parameters, sets return context, executes function body, and restores locals.

Important behavior:
- Expression statements are auto-printed via the default `print` call unless they are empty list results.
- `ret` is a global return context and function returns are implemented with `longjmp`.
- `indir()` supports integer widths, strings, runes, disassembly, and floating formats.
- Writes to non-core maps require write mode except for `cormap`.

Dependencies:
- Uses mach map accessors, evaluator, list/value structs, parser ASTs, and global error jmp state.

Notable risks:
- Longjmp-based control flow requires every temporary global state change to be restored on error paths.
- `windir()` allows writing to debuggee memory when enabled; format/size correctness matters.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/exec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/expr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acid/expr.c

Expression evaluator dispatch table and implementations for Acid operators.

Key responsibilities:
- Defines format sizes and `fmtsize()`.
- Evaluates constants, names, casts, eval, list expressions, pointer indirection, frame-local address lookup, indexing, list head/tail/append/delete, assignment, arithmetic, comparisons, bitwise/logical operators, increments/decrements, calls, format override, and whatis.
- Reads memory for `*`, symbol memory for `@`, and indexed pointer arithmetic.
- Implements string concatenation and string-plus-rune.
- Implements list concatenation and scalar append-to-list.
- Dispatches expression opcodes via `expop[]`.

Important behavior:
- Integer pointer increments/decrements advance by `fmtsize()` for the value’s current format.
- `i`/`I` format size is architecture instruction size from machdata.
- `OCALL` defaults to empty list return, dispatches builtin when forced or when no user proc exists, otherwise invokes `call()`.
- Equality supports ints, floats, strings, and recursive lists.

Dependencies:
- Uses memory access, list helpers, string helpers, machdata, `odot()`, `oframe()`, and builtins.

Notable risks:
- Some arithmetic preserves lhs format even when result type changes.
- Division checks integer and int/float zero, but float/int division does not check zero integer divisor.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/expr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/lex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acid/lex.c

Lexer, keyword table, input stack, string/file input management, symbol table insertion/lookup, and source-location formatting for Acid.

Key responsibilities:
- Registers reserved words through `kinit()`.
- Manages nested input sources from files and strings with `pushfile()`, `pushstr()`, `popio()`, and `restartio()`.
- Formats source stack locations with `%L`.
- Lexes strings, escapes, comments, numbers, identifiers, operators, character constants, format suffixes, and interactive newlines.
- Maintains line numbers and interactive brace stacking.
- Stores identifiers and keywords in a hash table of `Lsym`.

Important behavior:
- `//` comments are consumed through newline.
- Interactive newlines produce `;` unless inside braces.
- Numeric lexer supports binary `0b`, hex `0x`, floats, and ordinary integer constants.
- Identifiers allow `_`, `$`, alnum, and UTF-ish bytes above `~`.
- New symbols are initialized as unset integer values with default `X` format.

Dependencies:
- Uses Plan 9 `bio`, global parser `yylval`, Acid hash table, and error handling.

Notable risks:
- Numeric scanning accepts `-` and `+` inside floats broadly after float mode, which is permissive.
- `popio()` deliberately refuses to pop the base input and restarts it instead.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acid/list.c

Acid list construction, mutation, comparison, indexing, deletion, and stack-trace list materialization.

Key responsibilities:
- Builds list values from AST comma/list nodes.
- Computes list length, concatenates lists, appends values, indexes nth elements, deletes elements, and recursively compares lists.
- Builds two-element name/address variable lists.
- Builds lists of locals and parameters for stack frames using mach symbol metadata and frame pointer reads.
- `trlist()` appends stack trace frame records containing function address, caller PC, params, and locals.

Important behavior:
- Empty/out-of-range `nthelem()` returns an empty list, while delete beyond end is an error.
- `append()` allocates a new list element from the evaluated value’s `Store`.
- Stack trace records are nested lists suitable for Acid scripts to inspect.

Dependencies:
- Uses evaluator, list allocator, mach symbol APIs, map reads, and global `tracelist`.

Notable risks:
- `addlist()` mutates the left list in place.
- Delete returns a list with the target node unlinked but does not free it immediately; GC handles reachable/unreachable list cells.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acid/main.c

Acid debugger entry point, startup, target attachment, module loading, symbol/map setup, REPL loop, GC, and process-exit handling.

Key responsibilities:
- Parses command-line options for kernel mode, write mode, quiet flag, machine override, and library modules.
- Determines target executable from pid/textfile arguments.
- Initializes formatting, output, keywords, input stack, variables, builtins, machine type, maps, symbols, and register variables.
- Loads standard Acid modules, machine-specific modules, requested modules, and user init hooks.
- Runs optional `acidmap()` and then enters the interactive parse/eval loop.
- Handles target executable/header reading and symbol map setup.
- Provides AST/list allocation and mark-sweep GC.
- Handles fatal/syntax errors, interrupt notes, qid checking, kernel filename inference, and debugger exit cleanup.

Important behavior:
- `attachfiles()` runs under noninteractive error trapping and falls back to default register variables on failure.
- `die()` calls a `dying` hook and prints kill commands for processes in `proclist`.
- `readtext()` supports raw binary mapping when `-m` is given.
- GC marks procs and symbol values, then frees unmarked `Gc` objects from the global allocation chain.
- `system()` infers kernel path from `$cputype` and `$terminal`.

Dependencies:
- Uses Plan 9 `mach` library, parser/lexer/evaluator, builtins, module files under `/sys/lib/acid`, and process-control helpers elsewhere in Acid.

Notable risks:
- Startup has many recoverable `setjmp` regions; initialization failures may silently continue depending on `silent` and phase.
- GC relies on all collectible allocations being linked through `gcl`; ordinary `malloc` allocations must be freed manually.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acid/main.c -->