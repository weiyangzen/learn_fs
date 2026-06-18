# Group Research: group_1593_plan9_sources_os_plan9_plan9_sys_src_cmd_ip_ftpfs_proto_c_sources_o_0503cc66b977

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ftpfs/proto.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ftpfs/proto.c

Core FTP protocol adapter for `ftpfs`. It opens the control connection, handles optional FTP-over-TLS setup, authenticates interactively or through auth keys, detects the remote OS, and initializes the mirrored remote root/current directory model.

The file implements active/passive data connections, FTP commands for listing, reading, writing, creating, and removing files/directories, and protocol reply parsing. Directory listing parsing covers Unix/Plan 9, Windows NT, VMS, VM, TOPS, NetWare, TSO/MVS-like formats, with path builders for Unix, VMS, and MVS remote names.

It also owns transfer type switching, keepalive, password input with console raw mode, Latin-1-to-UTF conversion for foreign listings, and helpers for safely reallocating `Dir` structures used by the local 9P mirror.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ftpfs/proto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/glob.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/glob.c

Standalone glob implementation used by Plan 9 IP commands. It expands path patterns without fixed path-element size limits by converting each path component into a regular expression and walking candidate directories one component at a time.

It supports absolute and relative patterns, `*`, `?`, escaped regexp metacharacters, directory-only `.` matching, incremental result construction through `Globlist`, and iterator-style result consumption with `globiter`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/glob.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/glob.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/glob.h

Public interface for the local glob implementation. It defines linked-list result structures `Glob` and `Globlist`, plus constructors/append/free/iterator entry points used by commands that need filesystem pattern expansion.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/glob.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/gping.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/gping.c

Graphical IPv4 ping monitor. It opens Draw/Event windows, sends ICMP echo requests to up to 32 machines, receives replies in helper processes, tracks outstanding requests, RTT, packet loss, and unreachable markers, then plots per-host graphs.

The UI supports adding/dropping RTT and loss graphs from a mouse menu, resizing, colored scrolling graph panes, hash marks, and click-to-inspect historical points. It schedules pings across machines at a configurable interval and uses logarithmic RTT scaling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/gping.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/hogports.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/hogports.c

Small daemon that reserves TCP/UDP-style port ranges by announcing each specified `proto!start-end` address. It forks into the background, closes standard descriptors, announces every port, and sleeps forever so other services cannot bind those ports.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/hogports.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/anonymous.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/anonymous.c

Common helper for httpd magic programs. It binds `webroot` over `/` with `MREPL`, changes to `/`, and returns HTTP internal failure if the anonymous web namespace cannot be installed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/anonymous.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/authorize.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/authorize.c

Basic-auth gate for protected httpd directories. It searches the requested path’s directory for `.httplogin`, tokenizes the file as realm plus username/password pairs, and compares those against parsed request credentials.

If authentication is missing or invalid, it emits a `401 Unauthorized` response with `WWW-Authenticate: Basic`, content length, connection handling, and access-log entry. If no `.httplogin` exists, access is allowed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/authorize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/classify.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/classify.c

Domain/country classifier for whois or access-policy code. It defines country-code/name tables for blocked countries, accepted countries, government labels, and all known country codes.

`classify` inspects NDB tuples for `country`, `dom`, and verified `ip` entries. It returns unknown, bad-country, bad-government, or OK classifications based on explicit country data, domain suffixes, government domain components, and forward-lookup verification.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/classify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/content.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/content.c

MIME/content classification support for httpd. `contentinit` tracks `/sys/lib/mimetype` by qid, reloads it when changed, strips comments, and builds a suffix table containing type, subtype, and optional encoding.

`uriclass` classifies by filename suffix chain, including encodings such as compressed extensions, while `dataclass` sniffs an initial data buffer and returns `text/plain` only if the bytes are printable valid UTF.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/content.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/emem.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/emem.c

Fatal allocation wrappers for httpd helpers. `ezalloc` mallocs and zeroes memory, and `estrdup` duplicates strings; both terminate with `sysfatal` on out-of-memory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/emem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/hints.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/hints.c

Prefetch hint subsystem for httpd. It loads `/sys/log/httpd/url` into hash-indexed URL tables and `/sys/log/httpd/pathstat` into compact per-URL hint arrays, refreshing only when file length changes and files are old enough to be stable.

`urlcanon` normalizes URL paths and applies site-specific Bell Labs rewrites. `hintprint` looks up likely next URLs, filters by probability threshold and already-held client hints, stats files under `webroot`, and emits `Fresh:` headers with probability, ETag, size class, and path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/hints.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/httpd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/httpd.c

Main Plan 9 httpd listener. It parses certificate, namespace, address, domain, and webroot options; daemonizes; opens logs and rewrite/content/hint tables before namespace reduction; becomes user `none`; and announces HTTP or HTTPS service.

Each accepted connection runs in a forked child, optionally wrapped with TLS. Requests flow through overload throttling, request parsing, `/magic` extraction, rewrite/virtual-host redirects, header parsing, directory/index normalization, `.httplogin` authorization, and `sendfd` static transfer.

Magic requests exec `/bin/ip/httpd/<program>` with reconstructed request state, buffered input, log descriptors, remote address, netdir, scheme, port, webroot, method, version, URI, and query string. Parent processes periodically refresh redirects, MIME tables, and prefetch hint databases.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/httpd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/httpsrv.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/httpsrv.h

Shared private header for the httpd listener and magic helper programs. It defines `HSPriv`, timeout and redirect modifier constants, redirect flags, global log/webroot/netdir state, allocation helpers, static-file functions, MIME functions, init, redirect, logging, authorization, anonymous namespace, and hint prototypes.

This is the coupling point between the standalone listener, `/magic` programs, and common support modules.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/httpsrv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/imagemap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/imagemap.c

Magic helper for server-side image maps. It reconstructs the request, binds the anonymous webroot, validates GET/HEAD and expectation headers, parses query coordinates, opens the map file named by the URI, and chooses a redirect target.

The parser supports NCSA and CERN-style map records with rectangles, circles, polygons, closest points, and defaults. If no target matches, it returns a small HTML “Nothing Found” page; otherwise it redirects to the selected destination.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/imagemap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/init.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/init.c

Initializer used by httpd magic helper programs after exec. It parses inherited command-line state including buffered input, domain, local port, remote host, scheme, webroot, log fds, netdir, original request line, method, version, URI, and optional search string.

It initializes `HConnect`, input/output `Hio` streams, HTTP formatters, syslog, default remote/domain/webroot values, HTTP version fields, close-after-response behavior, and approximate request time.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/log.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/log.c

Logging implementation for httpd. `logit` writes syslog entries, prefixing the remote system when available from `HSPriv`.

`writelog` writes a verbose alternating daily trace log containing request metadata and headers, and a Common Log Format-style file for `Reply:` messages. It extracts status and response size from the reply formats used by static and helper responses.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/man2html.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/man2html.c

Magic helper and standalone converter for Plan 9 manual pages. It serves section indexes, resolves man-page names through `/sys/man/*/INDEX`, handles query-based page and keyword searches, redirects lowercase or directory variants, and rejects `..` in URIs.

Conversion is performed by piping `troff -manhtml` into `troff2html`. In magic mode it validates GET/HEAD and expectations, binds `/usr/web/sys/man` over `/sys/man`, emits HTML response headers, and logs generated output length.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/man2html.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/netlib_find.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/netlib_find.c

Netlib search magic helper invoked from web search forms. It parses `db` and `pat` query fields, chooses a configured searchfs database, mounts it at `/mnt`, writes a `search=` request, and streams matching records as HTML.

Database entries define log labels, maximum hits, backing `/srv/netlib_*` service, record formatter, and page trailer. Formatters preserve plain records, add links for Netlib `file:`/`lib:` fields, and link BibNet URL fields.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/netlib_find.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/netlib_history.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/netlib_history.c

Netlib history magic helper. It parses `file` and optional `diff` query fields, rejects parent-directory traversal and oversized names, changes into `/usr/web/historic`, then walks backward through dated snapshots to list historical versions.

In diff mode it limits the result count, gunzips `.gz` snapshots into temporary files, runs `diff -nb` between adjacent versions, and embeds the diff output in HTML. HEAD requests emit headers without a body.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/netlib_history.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/redirect.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/redirect.c

Rewrite-table loader and lookup engine for httpd. `redirectinit` monitors `/sys/lib/httpd.rewrite` by qid, strips comments, and rebuilds separate hash tables for URI redirects and virtual-host-to-webroot-prefix mappings.

Replacement fields may be decorated for silent, permanent, subordinate, or exact-only behavior. `redirect` finds the longest path prefix match and constructs a per-request replacement path or URL; `masquerade` maps Host headers to implicit webroot prefixes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/redirect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/save.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/save.c

Magic helper for simple form logging. GET uses the query string, POST reads the request body after optional `100 Continue`, truncates at the first newline, caps each entry at 24 KiB, and appends `at <time> <data>` to `/usr/web/save/<uri>.data`.

It serves `/usr/web/save/<uri>.html` as the response through `sendfd`. Data files may use Plan 9 exclusive-use locking; `openLocked` retries briefly when files are locked to avoid interleaved appends.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/save.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/sendfd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/sendfd.c

Static-file response engine for httpd. It classifies content by URI suffix or data sniffing, generates ETags from qid path/version, checks Accept and Content-Encoding, evaluates conditional request headers, handles If-Range, and emits 200, 206, 304, 406, 412, or 416 responses.

It supports HEAD, full transfers, single ranges, and multipart byte ranges with MIME boundaries. `fixrange` normalizes suffix ranges, clamps to file length, drops invalid ranges, and merges adjacent/overlapping ranges while keeping useful request order.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/sendfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/webls.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/webls.c

Magic helper and standalone tool for HTML directory listings. It loads allow and deny regular expressions from `/sys/lib/webls.allowed` and `/sys/lib/webls.denied`, then permits listings according to those rules while rejecting `..` traversal.

`dols` binds webroot to `/` in magic mode, reads and sorts directory entries, computes formatting widths, renders Plan 9 mode/type/dev/uid/gid/length/mtime fields, links subdirectories back through `/magic/webls?dir=...`, and includes parent navigation only when permitted.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/webls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/wikipost.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/wikipost.c

POST-only magic helper for wiki edits. It reads form data, decodes URL escapes with a Latin-1 fallback heuristic, removes carriage returns, and extracts title, version, text, service, comment, author, and base URL fields.

It validates required fields and dangerous service/title/comment content, caps text size, mounts a private or `/srv/wiki.<service>` wiki filesystem at `/mnt/wiki`, writes an edit record to `/mnt/wiki/new`, commits with a zero-length write, reads the resulting page name, and returns a `303 See Other` redirect.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/wikipost.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpfile.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpfile.c

9P filesystem that exposes an HTTP or HTTPS URL as a read-only file. It parses the URL, uses HEAD to discover content length, and serves a synthetic root directory containing one file named from the URL or `-f`.

Reads are satisfied from 64 KiB cached blocks fetched via HTTP Range GETs. The server maintains cache and in-progress block queues, serializes range fetches through worker threads, serves queued 9P reads when blocks arrive, supports flush interruption, and can post a srv file or mount at a mount point.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/httpfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/icmp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/icmp.h

Shared ICMP definitions for IPv4 and IPv6 users. It defines ICMPv4 message types, ICMPv6 error/informational/router/neighbor message types, common header size, an IPv4 header layout, and an echo-style ICMP payload header shared by IPv4 and IPv6.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/icmp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/auth.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/auth.c

Authentication and user setup for `imap4d`. It supports CRAM-MD5 challenge/response, optional password verification by synthesizing the CRAM response, and setup through `auth_chuid`, user namespace construction, mailbox directory selection, and `upas/fs` initialization.

It also contains a ratifier-filesystem forwarding hack that periodically records the remote peer under `/mail/ratify/trusted` so authenticated IMAP sessions can enable outgoing SMTP forwarding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/copy.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/copy.c

Message copy and append storage support for `imap4d`. It verifies source messages, reads unix headers and raw bodies from upas/fs, spools APPEND literals through a temporary file while normalizing CRLF and escaping `From ` lines, then appends to the target mailbox.

`saveMsg` holds the mailbox lock, appends message data, computes SHA1 digests for newly appended messages, refreshes the lock during long writes, and updates the `.imp` sidecar with digest, UID placeholder, and flags.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/copy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/csquery.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/csquery.c

Connection-server lookup helper. It writes a query such as `!attr=value` to `/net/cs`, scans returned NDB-style records for the requested attribute, and returns a duplicated value string when found.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/csquery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/date.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/date.c

Date formatting and parsing for IMAP and RFC 822 mail data. It formats RFC 822 dates, IMAP internal dates, and IMAP date-only strings, and parses IMAP date/time inputs into epoch seconds.

The general parser accepts common mail date forms with optional weekday, month-first or day-first ordering, two- or four-digit years, named RFC 822 zones, military zones, numeric offsets, and local timezone fallback.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/date.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/debug.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/debug.c

Debugging helpers for `imap4d`. `debuglog` writes optional per-user diagnostics to `/sys/log/imap4d`; `boxVerify` checks message sequence, UID, recent count, and mailbox counters; `openfiles` dumps open file descriptors; and `ls` recursively-style lists directory entries for inspection.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/fetch.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/fetch.c

FETCH response implementation for `imap4d`. It maps requested attributes to message flags, UIDs, internal dates, envelopes, RFC822 sizes, BODY, BODYSTRUCTURE, and BODY section literals, and implicitly marks messages seen for body-reading operations.

Body section handling maps IMAP sections to upas/fs files: raw headers, raw bodies, MIME headers, or combined body/header views. It supports partial fetches, header field selection/inversion, multipart/bodystructure recursion, message/rfc822 nesting, MIME parameters, addresses, and CRLF normalization of body literals.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/fetch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/fns.h

Central prototype header for the IMAP daemon. It declares mailbox, message, fetch, search, flag, authentication, date, MIME, modified-UTF7, locking, copy/append, list/subscribe, parsing, storage, and output helper functions, plus allocation macros and vararg checks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/folder.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/folder.c

Mailbox filesystem helper layer for `imap4d`. It caches current directory changes, wraps create/open/stat/remove operations relative to mailbox directories, manages the global mailbox lock file `L.mbox`, and refreshes the lock during long copies.

It also converts IMAP modified UTF-7 mailbox names, constructs `.imp` sidecar names, creates nested mailboxes, renames or copies mailboxes, preserves permissions/group where possible, handles INBOX/mbox naming, and removes or truncates source mailboxes after successful moves/copies.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/folder.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/imap4d.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/imap4d.c

Main IMAP4rev1 daemon. It initializes buffered stdin/stdout, parses options for preauth, plaintext/password challenge modes, site/remote/server names, and debugging, resolves server/site names, sets notification handling, and enters an IMAP command loop with non-authenticated, authenticated, and selected-state command tables.

Command handlers implement CAPABILITY, LOGIN, AUTHENTICATE CRAM-MD5, APPEND, CREATE, DELETE, RENAME, LIST, LSUB, NAMESPACE, SELECT/EXAMINE, STATUS, CLOSE, EXPUNGE, FETCH, STORE, COPY, SEARCH, UID subcommands, IDLE, NOOP, SUBSCRIBE/UNSUBSCRIBE, and LOGOUT. Selected mailbox state is checked before commands, with EXISTS/RECENT/FLAGS/EXPUNGE updates controlled to respect IMAP restrictions.

The file also owns the hand-written IMAP parser for tags, atoms, quoted strings, literals, message sets, flags, store specs, fetch specs, body sections, partial ranges, and search expressions. It uses parse-bin allocation so failed commands can discard all parse structures at once.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/imap4d.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/imap4d.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/imap4d.h

Shared data model for `imap4d`. It defines mailbox `Box`, message `Msg`, MIME/header/address structures, mailbox lock state, named integer maps, constants for buffer sizes, digest/UID/flag field widths, mailbox/message name limits, modified UTF-7 sizing, message flags, and bogus-message flags.

It also defines parse-tree structures for FETCH, BODY sections, STATUS items, STORE, SEARCH, numeric/string lists, message sets, and byte ranges, then includes `bin.h` and `fns.h` to expose parser allocation state, global I/O buffers, user/mailbox globals, and daemon helper prototypes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/imap4d.h -->