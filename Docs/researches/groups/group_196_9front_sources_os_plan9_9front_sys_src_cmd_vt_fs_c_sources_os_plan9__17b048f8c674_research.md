# Group Research: group_196_9front_sources_os_plan9_9front_sys_src_cmd_vt_fs_c_sources_os_plan9__17b048f8c674

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vt/fs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vt/fs.c

Synthetic 9p `/dev/cons` and `/dev/consctl` implementation for the `vt` terminal emulator. It mounts a private service before the host command starts so the command reads and writes through channels connected to the emulator.

Key behavior:
- `mountcons()` creates a 9p tree with `cons` and `consctl`, then posts it on `/dev` with `MBEFORE`.
- `fsreader()` pairs pending 9p reads with strings from `hc[0]`, handles flushes, copies partial data into the read reply, and drains queued host-input chunks.
- Writes to `cons` are converted from UTF bytes to `Rune` arrays with partial-rune carry state stored in the fid aux field, then sent to `hc[1]`.
- Writes to `consctl` toggle raw, hold, and winch state in the shared `Consstate`.
- Destroying an open `consctl` fid clears raw/hold/winch state; destroying any fid frees partial UTF state.

Notable dependencies:
- Plan 9 libthread/lib9p APIs: `Req`, `Fid`, `Srv`, channels, `threadpostmountsrv`.
- Shared terminal state and host channels from `cons.h` and `vt/main.c`.

Research notes:
- This file is the filesystem bridge for `vt`, not a persistent filesystem.
- `fsend()` sends a nil `Rune*` through `hc[1]`, which the UI side treats as host closure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vt/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vt/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vt/main.c

Main UI, process, screen-buffer, input, selection, and event-loop implementation for the Plan 9 `vt` terminal emulator. It starts the child command under the synthetic console service from `fs.c` and drives the emulator core in `vt.c`.

Key behavior:
- `threadmain()` parses terminal mode options, initializes draw/mouse/keyboard state, allocates terminal colors, creates host I/O channels, starts `runcmd()`, and enters `emulate()`.
- `runcmd()` mounts the synthetic console, wires stdio to `/dev/cons`, assembles an optional rc command line, and execs `/bin/rc`.
- Maintains character, attribute, and color buffers for the visible screen plus a circular history buffer used by scrollback replay.
- `drawscreen()`, `drawcursor()`, `clear()`, `shift()`, and `scroll()` update display image regions from the screen buffers and mark changed lines.
- Input is split between cooked canonical line editing and raw terminal mode; raw mode maps special keys through function-key tables, while cooked mode handles erase, word kill, line kill, interrupt, newline, EOT, and local echo.
- `waitio()` multiplexes mouse, resize, keyboard, outgoing host input, and incoming host output channels.
- Window resize state is reflected through `WINCH`, `XPIXELS`, `YPIXELS`, `LINES`, `COLS`, and `TERM`; optionally sends interrupt when `consctl` enabled winch behavior.
- Selection supports swept text, word-like text, non-whitespace text, block selection, snarf buffer copy/paste, and plumber messages using OSC 7 current-directory context.
- Middle/right mouse menus expose scrollback, reset, paste, snarf, plumb, page mode, 24x80 geometry, newline toggles, raw/cooked mode, block selection, and exit.

Notable dependencies:
- Plan 9 graphics/event APIs: `draw`, `mouse`, `keyboard`, menus, images, `/dev/wctl`, `/dev/snarf`, plumber.
- Shared terminal emulator variables/functions from `cons.h` and `vt.c`.

Research notes:
- This is terminal UI and process plumbing, not general filesystem code.
- The `hc[0]`/`hc[1]` channel naming is from the emulator perspective: outgoing keyboard data to the host and incoming runes from the synthetic console.
- `drawscreen()` optimizes full-window upward scrolls through `scrolloff`, then redraws changed logical lines.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vt/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vt/vt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vt/vt.c

ANSI/VT100-style terminal emulator state machine used by `vt/main.c`. It parses input runes from `nextchar()`, handles control characters and escape sequences, updates cursor/screen state through callbacks in `main.c`, and emits terminal replies through `sendnchars()`.

Key behavior:
- Defines ANSI, VT220, xterm, and application cursor-key sequence tables plus DEC special graphics mapping.
- `emulate()` is the main parser loop, handling printable text batching, wrapping, G0/G1 graphics selection, ESC commands, CSI commands, and OSC commands.
- Supports cursor save/restore, reset, index/next-line/reverse-index, tab stops, cursor reports, terminal identification, scroll regions, line/character insertion and deletion, screen/line erase, cursor visibility, origin mode, auto-wrap mode, bracketed paste mode, and 80/132-column resize requests.
- `setattr()` implements common SGR attributes: reset, high intensity, underline, blink, reverse, invisible, and 8-color foreground/background state.
- `cursctl()` handles bell, backspace, tab, line feed, vertical/form feed, and carriage return, including raw-mode newline toggles.
- `osc()` supports title/label updates through `/dev/label` and OSC 7 working-directory capture, converting `file://host/path` into Plan 9 `/n/host/path` form and cleaning it.

Notable dependencies:
- Terminal buffer and drawing primitives from `main.c`: `clear`, `scroll`, `setdim`, `newline`, `drawstring`, `sendnchars`, `host_avail`, `rewound`.
- Plan 9 rune/ctype and path helpers.

Research notes:
- The file begins with explicit known limitations: incomplete cursor movement inside escape sequences, tab stops beyond the fixed array, reverse-video screen mode, double-width/height lines, VT220 fidelity, VT52 mode, and keypad mode behavior.
- OSC parsing intentionally ignores normal cursor-control effects inside OSC payloads via `cursctl()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vt/vt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/walk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/walk.c

Recursive Plan 9 file tree walker with selectable output fields, depth bounds, filtering, and loop detection.

Key behavior:
- Command flags select files vs directories, temporary-only entries, executable-only entries, unbuffered output, depth ranges, and stat-format fields.
- `walk()` recursively opens directories, reads `Dir` batches, skips `.`/`..`, detects already-seen directory qids/devices, and avoids descending past `maxdepth`.
- `dofile()` prints fields selected by `stfmt`, including owner/group/muid, times, name, path, qid, size, mode, device, and server type.
- `slashslash()` normalizes repeated slashes without full `cleanname()` behavior when `-C` is used.
- Default format is path-only output.

Notable dependencies:
- Plan 9 `Dir`, qid fields, `dirread`, `dirstat`, `dirmodefmt`, and libString.

Research notes:
- Cycle detection is ancestry-based and compares qid path/type plus device.
- `maxdepth` is incremented after parsing so user-facing depth semantics differ from the internal starting depth of 1.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/walk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/wc.c

Plan 9 `wc` implementation for UTF-encoded text. It counts lines, words, runes, bad runes, and bytes using a table-driven byte-state machine.

Key behavior:
- Default output is line, word, and byte counts; flags add/select line, word, rune, bad-rune, and byte columns.
- `count()` reads in `IOUNIT` chunks, increments byte/rune counters optimistically, and adjusts rune/bad-rune counts based on UTF continuation-state transitions.
- Four 256-entry state tables distinguish whitespace, word body, and pending 2/3/4-byte UTF sequences.
- A final non-ground UTF state increments the bad-rune count for trailing partial runes.
- Multiple input files accumulate totals and print a `total` row.

Notable dependencies:
- Plan 9 UTF conventions and libc I/O.

Research notes:
- The header documents known limitations: whitespace is only space/tab/newline, impossible-rune bytes are not separately counted, and non-canonical UTF encodings are not specially counted.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/webcookies.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/webcookies.c

Cookie jar 9p filesystem used by `webfs` and other clients to share HTTP cookies. Conventionally mounted at `/mnt/webcookies`, it exposes an HTTP-oriented exchange file and a raw editable cookie file.

Key behavior:
- Maintains a `Jar` of `Cookie` entries with fields for name/value/domain/path/version/comment, expiration, secure flag, explicit domain/path flags, Netscape-style flag, deletion, marking, and on-disk state.
- Formats matching cookies as an HTTP `Cookie:` header and formats individual cookies as quoted attribute records for the persistent jar.
- Adds cookies by replacing same name/domain/path entries, sorts by name/domain and longer path first, purges deleted entries, expires session cookies on exit, and synchronizes to disk with a lock file.
- Parses persistent jar records through `addtojar()` and HTTP `Set-Cookie` headers through RFC2109 plus legacy Netscape parsing.
- Enforces domain/path/security checks before accepting response cookies or returning request cookies.
- `/http` protocol: first write must be an `http://` or `https://` URL; reads return matching `Cookie:` headers; later writes append response headers, parsed into the jar when the fid is destroyed.
- `/cookies` protocol: read/write raw cookie records, with `OTRUNC` replacing the jar on close.
- `main()` loads the jar from `-f` or `$home/lib/webcookies`, creates `http` and `cookies` files, and posts the service.

Notable dependencies:
- Plan 9 lib9p, Bio, ndb `ipattr`, time parsing, and quote formatting.

Research notes:
- Persistent jar synchronization uses `L.<file>` lock naming and retries before reporting lock acquisition failure.
- Header parsing mutates the input buffers in place.
- Raw cookie editing is bounded by `MaxCtext` to avoid unbounded memory growth.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/webcookies.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/webfs/buq.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/webfs/buq.c

Bounded queue implementation connecting 9p reads/writes to HTTP worker streams in `webfs`.

Key behavior:
- `Buq` stores buffered byte chunks, blocked write requests, queued read/open requests, response URL/header metadata, close/error state, and a rendezvous for backpressure.
- `buwrite()` appends data and sleeps when queued bytes exceed the limit.
- `buread()` blocks until data or closure, consumes bytes, wakes writers, and returns queued errors as read failures.
- `bureq()` adapts 9p `Tread`, `Twrite`, and `Topen` requests into the queue, responding immediately when possible or queueing the request.
- `matchreq()` pairs pending reads/opens with buffered data or closure; `kickwqr()` releases queued write requests when data is consumed or the queue closes.
- `buflushreq()` interrupts queued 9p reads/opens or flushes queued writes.

Notable dependencies:
- Plan 9 libthread locking/rendezvous and lib9p `Req`.
- `Url` and `Key` metadata from `dat.h`.

Research notes:
- The queue is reference-counted; `bufree()` owns queued buffers, URL, headers, and error text.
- Queued writes initially point into the request payload and are compacted into owned buffers when accepted.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/webfs/buq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/webfs/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/webfs/dat.h

Shared data definitions for `webfs`.

Key contents:
- Declares `Url`, `Buq`, `Buf`, `Key`, and `Str2`.
- `Url` splits scheme, user, password, host, port, path, query, and fragment.
- `Buf` is an internal queued data chunk with read/end pointers and optional blocked write request.
- `Key` is a linked header key/value record with inline key storage and value pointer.
- `Buq` is a reference-counted, qlocked bounded stream with URL/header metadata, close/error state, queued buffers, queued 9p reads, and rendezvous.
- Defines global `debug`, `proxy`, `timeout`, and `whitespace`, plus `Domlen`.

Notable dependencies:
- Uses lib9p `Req`, Plan 9 `Ref`, `QLock`, and `Rendez`.

Research notes:
- The header is intentionally compact and is paired with function declarations in `fns.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/webfs/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/webfs/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/webfs/fns.h

Shared function declarations and format registrations for `webfs`.

Key contents:
- Memory/string/header helpers: `emalloc`, `estrdup`, `nstrcpy`, `addkey`, `delkey`, `getkey`, `lookkey`, `parsehdr`, `unquote`.
- URL formatting and parsing declarations with custom format verbs for escaped strings, IDN names, URLs, host bracket formatting, and encoded text.
- Bounded queue API: header/url metadata, read/write, close/free, allocation, 9p request attach, and flush.
- HTTP/authentication API: `authenticate`, `flushauth`, and `http`.

Notable dependencies:
- Must be included with `dat.h` so `Url`, `Key`, `Buq`, `Req`, and `Str2` are defined.

Research notes:
- The custom URL/header format verbs are installed by `webfs/fs.c` before mounting the service.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/webfs/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/webfs/fs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/webfs/fs.c

9p filesystem front end for HTTP requests. It exposes cloneable clients with control files, request/response body streams, parsed URL fields, response headers, and error bodies.

Key behavior:
- Root contains `ctl`, `clone`, and numbered client directories.
- Opening `clone` allocates a `Client` and turns the fid into that client's `ctl`.
- Client directories expose `ctl`, `body`, `postbody`, `errorbody`, `parsed`, and dynamic header files; `parsed` exposes URL, scheme, user, password, host, port, path, query, and fragment.
- `ctl` messages set URL, base URL, request method, bulk headers, `User-Agent`, and `Content-Type`; root `ctl` sets user agent, timeout, auth flushing, and preauthentication.
- Opening `body` starts a GET or custom request; opening `postbody` starts a POST-like request with a writable request body queue; `errorbody` reads response/error payloads.
- Default request headers include `Accept: */*`, `Connection: keep-alive`, and configured `User-Agent` unless supplied.
- `fswalk1()`, `fsmkdir()`, and generator callbacks build stable qids and directory listings from client state, parsed URL state, and response headers.
- `fsdestroyfid()` closes queues, marks body streams closed, releases client references, and frees copied header keys.
- `main()` installs URL/header formatters, reads `httpproxy`, sets defaults, and mounts at `/mnt/web` or a supplied mount/service.

Notable dependencies:
- Plan 9 lib9p service callbacks.
- `Buq` stream queues from `buq.c`, URL helpers from `url.c`, HTTP worker from `http.c`, and cookie service at `/mnt/webcookies/http`.

Research notes:
- `Client` objects are a fixed array of 256 entries reused by reference count.
- Header files copy the header key/value because queue-owned response headers may disappear.
- After a request starts, `cl->url` and `cl->hdr` ownership moves to the HTTP worker path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/webfs/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/webfs/http.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/webfs/http.c

HTTP/HTTPS transport, connection pooling, authentication, proxy, cookie, redirect, chunking, and body streaming implementation for `webfs`.

Key behavior:
- `hdial()` opens direct or proxy TCP connections, wraps TLS for HTTPS endpoints or HTTPS proxies, and marks HTTPS-through-proxy connections as tunnels.
- `hclose()` returns reusable keep-alive connections to a bounded idle pool, enforces per-peer and total limits, and starts a reaper process for idle connections.
- `hread()`, `hwrite()`, and `hline()` provide buffered body reads, complete writes, and line/header reads with continuation folding.
- Basic and Digest authentication are supported through Plan 9 auth mechanisms and cached by URL scope in `hauth`; digest cache entries are flushed after one use.
- `flushauth()` removes cached credentials matching URL and/or auth string.
- `http()` forks a worker process, prepares request headers, optionally spools POST bodies to a temp file for retries/content-length calculation, sends request headers/body, receives status/headers, handles redirects, 401/407 auth, proxy CONNECT, 411 retry with length, chunked bodies, and no-body statuses.
- Response headers and final URL metadata are attached to `qbody` or `qerror`; error status closes `qbody` with status text and streams the response into `qerror` until success/error routing is decided.
- Integrates with `/mnt/webcookies/http` by writing request URL to fetch cookies and later writing `Set-Cookie` headers back.

Notable dependencies:
- Plan 9 networking, TLS (`tlsClient`), auth, libsec encoding, libthread, and the local `Buq`, `Url`, and `Key` helpers.

Research notes:
- Worker retries are bounded to 12 attempts.
- For unknown-length non-chunked bodies, keep-alive is disabled because EOF delimits the body.
- Posting uses a helper process sharing memory with the worker; `h->cancel` stops it on retry/error.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/webfs/http.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/webfs/sub.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/webfs/sub.c

Small utility module for `webfs` memory allocation, bounded string copying, HTTP header key lists, header parsing, and quoted-token parsing.

Key behavior:
- `emalloc()` and `estrdup()` wrap lib9p allocation helpers, set malloc tags, and zero allocated blocks.
- `nstrcpy()` copies with guaranteed NUL termination.
- `addkey()`, `delkey()`, `getkey()`, and `lookkey()` manage case-insensitive linked header lists.
- `parsehdr()` trims trailing whitespace, splits `Key: value` lines, strips leading value whitespace, and returns a `Key`.
- `unquote()` parses either quoted strings with backslash skipping or whitespace-delimited tokens, mutating the buffer and returning the unquoted token.

Notable dependencies:
- Plan 9 ctype/case-insensitive string helpers and lib9p allocation.

Research notes:
- Deleting a header zeroes its value before freeing.
- Parsing helpers are destructive by design.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/webfs/sub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/webfs/url.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/webfs/url.c

URL parser, formatter, normalizer, matcher, and escaper for `webfs`.

Key behavior:
- Custom formatters emit percent-encoded strings, IDN/ascii domain names, bracketed IPv6-like hosts, and complete URLs.
- `url()` parses absolute and relative URLs against an optional base, splitting scheme/user/password/host/port/path/query/fragment.
- Relative URL paths are resolved through `abspath()` and `remdot()`, preserving directory semantics and removing dot components.
- Query `+` is decoded to space; host names are converted from IDN to UTF for internal use and to IDN during formatting.
- Percent decoding preserves reserved characters in path/query/fragment where required.
- `saneurl()` requires scheme, host, and path and strips default ports.
- `matchurl()` matches non-nil fields of a scope URL against a candidate URL, including path-prefix matching.
- `freeurl()` releases all URL components.

Notable dependencies:
- Plan 9 IDN helpers `utf2idn`/`idn2utf`, rune lowercasing, and custom `Fmt` verbs.

Research notes:
- `u->port` is lowercased like the host and scheme; numeric ports are unaffected.
- `saneurl()` treats a port string equal to the scheme as a default-port case.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/webfs/url.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/fs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/fs.c

9p filesystem front end for a file-backed wiki. It maps wiki page titles and numeric ids into directories containing rendered HTML/text, raw current data, edit pages, history, diffs, and historical revisions.

Key behavior:
- Qid paths encode type, page number, page version index/time, and file index.
- Root exposes `new`, `map`, and one directory per wiki page title; title lookup accepts numeric ids or normalized names.
- First-level page directories expose `index.html`, `index.txt`, `current`, `history.html`, `history.txt`, `diff.html`, `edit.html`, `werror.html`, `werror.txt`, `.httplogin`, plus second-level history directories named by revision timestamp.
- Second-level history directories expose only current-style rendered/text/raw files for that revision.
- Walking a file pre-renders the requested content into fid-local `String` storage using `tohtml`, `totext`, `doctext`, or `.httplogin` loading.
- Opening root captures a map snapshot for directory reads; opening page directories refreshes history/current document state.
- `new` is writable and accumulates a full raw wiki page until a zero-length write finalizes parsing, title allocation, conflict checking, and `writepage()`.
- Writing `map` resolves a page name to a numeric id for later reads.
- `main()` validates the wiki directory, initializes the map, optionally starts network listeners, and posts/mounts the service.

Notable dependencies:
- lib9p, wiki parser/formatter/cache APIs from `wiki.h`, Plan 9 auth/listen support.

Research notes:
- Writes use the attaching user name as author unless overridden by raw `A` metadata; network listener identity may be appended.
- `new` finalization uses a zero-length write as the commit signal.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/io.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/io.c

Storage, locking, caching, map, lookup, and write implementation for the file-backed wiki used by `wikifs`.

Key behavior:
- Stores each document as `d/nnn` current file, append-only `d/nnn.hist` history, `d/L.nnn` lock, plus append-only `d/map` title mapping protected by `d/L.map`.
- `getlock()` acquires exclusive lock files with retry and timeout.
- `readwhist()` reads history/current files under the lock using `Brdwhist()`.
- `getcache()` maintains up to 128 cached page entries, refreshing current/history data by qid/version and evicting least-recently used unreferenced entries.
- `currentmap()` loads and sorts the title map, caching by qid/version and enforcing `Maxmap`.
- `allocnum()` validates and normalizes titles, rejects reserved names and bad characters, appends a new map entry under lock, and refreshes the map.
- `nametonum()` lowercases and converts underscores to spaces, then binary-searches the sorted map; `numtoname()` does reverse lookup.
- `writepage()` appends a new revision to history, detects update conflicts by comparing the caller's base timestamp with the current file, records conflicting writes with `X`, and updates the current file only for non-conflicting writes.

Notable dependencies:
- Wiki history parser, page formatter, `wdir.c` relative file wrappers, Plan 9 locks, Bio, String library.

Research notes:
- The lock file is used for both read and write exclusion because the backing filesystem lacks read/write locks.
- `writepage()` ignores duplicate writes when the new body after metadata matches the current body.
- Cache invalidation is explicit after writes through `voidcache()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/lookup.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/lookup.c

Tiny diagnostic program for wiki title lookup.

Key behavior:
- Includes the wiki support headers and prints `nametonum(argv[1])`.

Notable dependencies:
- Requires the wiki map machinery from `io.c` and global wiki directory setup from linked objects.

Research notes:
- No argument validation is present; it assumes a title argument exists.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/map.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/map.c

Stub source file containing only the common wiki includes.

Key behavior:
- No functions, variables, or executable logic are defined in this file.

Notable dependencies:
- Includes Plan 9 libc/Bio/String/thread headers and `wiki.h`.

Research notes:
- This appears to be an empty placeholder or build artifact source for the `wikifs` tools.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/parse.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/parse.c

Wiki markup parser that converts raw wiki text lines into linked `Wpage` nodes.

Key behavior:
- `Brdpage()` reads lines from a caller-supplied line reader and emits typed page nodes: paragraph breaks, headings, bullets, links, man-page references, plain text, preformatted lines, and horizontal rules.
- Whitespace is condensed for non-preformatted content.
- Runs of adjacent plain text are merged by `wcondense()`.
- Bracketed links are parsed as `[text]` or `[text | url]`.
- Man references like `name(1)` are detected inside plain text and converted to `Wman`.
- Headings are inferred from all-uppercase text containing at least one uppercase rune and no lowercase runes.
- `printpage()` dumps parsed node types for debugging.

Notable dependencies:
- Plan 9 String/Bio/rune helpers and allocation/free helpers from `wiki.h`.

Research notes:
- Link and man-reference parsing mutate intermediate strings, then duplicate the pieces into new nodes.
- Preformatted lines start with `!`; a following space is stripped.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/parsehist.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/parsehist.c

Parser for wiki history/current files.

Key behavior:
- Reads the first line as the page title.
- Subsequent metadata lines use leading `D` for timestamp, `A` for author, `C` for comment, and `X` for conflict marker.
- Body lines are prefixed with `#`; `Brdwline()` strips the leading `#` and feeds them to `Brdpage()`.
- Builds a `Whist` with an array of `Wdoc` revisions, current revision index, title, document count, and reference count.
- The current index tracks the most recent non-conflicting revision.

Notable dependencies:
- `Brdpage()` from `parse.c`, page freeing from `io.c`, and Plan 9 Bio/String/thread support.

Research notes:
- If parsing any revision body fails, the partially built history is freed and nil is returned.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/parsehist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/testwrite.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/testwrite.c

Small test utility that reads a wiki history file and writes its latest parsed page into a numbered wiki document.

Key behavior:
- Optional `-t` supplies a base timestamp for conflict checking.
- Reads a history file with `Brdwhist()`, converts the last document to raw wiki text with `pagetext(..., dosharp=1)`, and calls `writepage()`.
- Uses default `wikidir = "."`.

Notable dependencies:
- Wiki parser, formatter, and storage writer APIs.

Research notes:
- Usage text mentions `[-d dir]` but the implemented option is `-t`, not `-d`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/testwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/tohtml.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/tohtml.c

Renderer for wiki pages, histories, diffs, edit text, and raw document text in HTML and plain text.

Key behavior:
- Template names map to HTML and text templates; templates are cached in `cache[]` with qid/time fields, though the time/qid fast paths are currently disabled by `if(0)`.
- `pagehtml()` emits headings, paragraphs, lists, links, man-page links, preformatted blocks, rules, and escaped plain text.
- `mkurl()` turns relative wiki links into parent-relative paths, supports absolute URL schemes, email auto-mailto, and old-page relative paths.
- `diffhtml()` and `s_diff()` render revision diffs by writing old/new HTML to temp files, running `/bin/diff`, and marking old/new spans.
- `historyhtml()` and `historytext()` list revisions with timestamps, authors, conflict markers, and comments.
- `tohtml()` and `totext()` splice rendered page/history/diff/edit/error content into templates, substituting `TITLE`, `VERSION`, and `DATE`.
- `pagetext()` converts parsed nodes back to wiki source, with optional leading `#` for history-file bodies and wrapping around 70 runes.
- `doctext()` serializes a `Wdoc` as wiki history metadata plus body.

Notable dependencies:
- Plan 9 String library, Bio, `/bin/diff`, temp files from `util.c`, wiki data types.

Research notes:
- The man-page HTML links point to the historical Bell Labs Plan 9 man2html URL.
- HTML escaping in non-pre text turns spaces into newlines.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/tohtml.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/util.c

Shared allocation, string, substitution, append-list, and temp-file helpers for `wikifs`.

Key behavior:
- `emalloc()`/`erealloc()` abort on allocation failure, zero new allocations, and tag allocations.
- `estrdup()` and `estrdupn()` duplicate nullable or bounded strings.
- `strlower()` lowercases ASCII letters in place.
- `s_appendsub()` appends text while replacing the earliest matching substitution tokens.
- `s_appendlist()` appends a nil-terminated list of strings to a `String`.
- `opentemp()` repeatedly applies `mktemp()`, creates an `ORCLOSE` temp file, and writes the chosen path back to the template.

Notable dependencies:
- Plan 9 String library and libc file APIs.

Research notes:
- `s_appendsub()` only considers substitutions whose replacement string is non-nil.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/wdir.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/wdir.c

Wiki-directory-relative file access wrappers.

Key behavior:
- Global `wikidir` names the backing wiki directory.
- `wname()` constructs `wikidir/file`.
- `wopen()`, `wcreate()`, `wBopen()`, `waccess()`, and `wdirstat()` wrap Plan 9 file operations after prefixing paths with `wikidir`.

Notable dependencies:
- Allocation helpers from `wiki.h` and Plan 9 file/Bio APIs.

Research notes:
- Each wrapper frees the temporary prefixed pathname after the underlying operation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/wdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/wiki.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/wiki.h

Shared data model and function declarations for `wikifs` and its helper tools.

Key contents:
- Defines cache limits: `Tcache`, `Maxmap`, and `Maxfile`.
- Enumerates parsed wiki node types (`Wpara`, `Wheading`, `Wbullet`, `Wlink`, `Wman`, `Wplain`, `Wpre`, `Whr`) and template types.
- Defines `Wpage`, `Whist`, `Wdoc`, substitution records, map elements, and reference-counted maps.
- Declares parser, formatter, cache/storage, map lookup, write, utility, and wiki-directory-relative file APIs.
- Exposes global `map`, `maplock`, and `wikidir`.

Notable dependencies:
- Uses Plan 9 `String`, `Biobuf`, `Ref`, `Qid`, and `RWLock` types from including compilation units.

Research notes:
- Header couples all wiki helper programs to the same storage and rendering API.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/wiki.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/wiki2html.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/wiki2html.c

Command-line wiki renderer/debugger for HTML output.

Key behavior:
- Options choose wiki directory, history view, old-page view, diff view, or parsed-node dump.
- Uses `gethistory()` for history/diff and `getcurrent()` otherwise, interpreting the argument as a numeric wiki id.
- `-P` prints parsed nodes with `printpage()`; otherwise writes `tohtml()` output to stdout.
- Uses private namespace rforking.

Notable dependencies:
- Wiki cache/storage and rendering APIs.

Research notes:
- `parse` is not initialized unless `-P` is supplied, so the later `if(parse)` reads an uninitialized local in the no-`-P` path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/wiki2html.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/wiki2text.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/wiki2text.c

Command-line converter from a wiki history file to raw wiki text for each revision.

Key behavior:
- Optional `-d` sets `wikidir`, though input is read directly from the provided file path.
- Reads a history file with `Brdwhist()`.
- Iterates all revisions, printing a separator and `pagetext(..., dosharp=1)` output for each.

Notable dependencies:
- Wiki history parser and text renderer.

Research notes:
- Error message on `pagetext()` failure says `wiki2html`, reflecting copy/paste from the HTML tool.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/wikifs/wiki2text.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/winwatch.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/winwatch.c

Graphical rio window watcher/switcher. It displays other windows as labeled rows, tracks visibility/current state, and lets the user rename or hide/unhide windows.

Key behavior:
- Periodically reads `/dev/wsys`, excluding its own window id and optional regexp-matched labels.
- For each window, reads label and `wctl`, extracts current/visible state, and stores a compact `Win` record.
- Computes a row/column grid based on font height and screen size, then draws colored rectangles with labels and borders.
- Middle-click on an entry prompts for a new label and writes it to `/dev/wsys/<id>/label`.
- Right-click toggles hide/unhide, raises the target to top, and marks it current through `/dev/wsys/<id>/wctl`.
- Keyboard `q` or delete exits; timer refreshes every 2.5 seconds.

Notable dependencies:
- Plan 9 draw/event/cursor/regexp/keyboard APIs and rio `/dev/wsys` control files.

Research notes:
- State colors distinguish not-visible/current/visible combinations through `statecol[state]`.
- Directory entries are processed in the order returned by `/dev/wsys`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/winwatch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/xargs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/xargs.c

Small Plan 9 `xargs` implementation that batches input lines into command arguments and runs a limited number of child processes.

Key behavior:
- `-n` controls number of input lines per command, default 10.
- `-p` controls maximum concurrent processes, default 1.
- Reads newline-delimited strings from stdin with `Brdstr()`, appends them after the fixed command argv, forks, and execs.
- If direct exec fails for a non-path command, retries with `/bin/<cmd>`.
- Frees read argument strings in the parent and waits for all children at exit.

Notable dependencies:
- Plan 9 Bio, fork/exec/wait primitives.

Research notes:
- Input splitting is strictly by line; it does not implement shell-like quoting or whitespace splitting.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/xargs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/xd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/xd.c

Hex/octal/decimal/ascii dump utility with configurable address base, data width, endian order, repeat elision, and multiple output formats.

Key behavior:
- Global flags select little-endian assembly (`-s`), unbuffered input flush behavior (`-u`), repeat-line elision (`-r`), and address base (`-a{odx}`).
- Format options select character output or 1/2/4/8-byte numeric groups in octal, decimal, or hex.
- `xd()` reads 16-byte blocks, zero-pads partial final blocks for formatting, elides repeated full blocks when requested, and prints final address after short block.
- `fmt0`/`fmt1`/`fmt2`/`fmt3` assemble and print values of different widths; `fmtc()` prints printable characters or escapes/control numeric forms.
- `flushout()` flushes stdout before blocking for more input when `-u` is used.

Notable dependencies:
- Plan 9 Bio and formatted printing.

Research notes:
- Up to 9 explicit formats are allowed because `initarg()` exits once `narg >= Narg` after increment.
- The big-endian 8-byte assembly path uses explicit 32-bit halves.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/xd.c -->