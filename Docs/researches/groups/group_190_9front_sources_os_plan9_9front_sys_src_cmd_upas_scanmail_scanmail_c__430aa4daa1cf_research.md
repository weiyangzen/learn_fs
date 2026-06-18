# Group Research: group_190_9front_sources_os_plan9_9front_sys_src_cmd_upas_scanmail_scanmail_c__430aa4daa1cf

Subset scope: `Docs/research_subset_a.md`; source tree covered here: `sources/os/plan9/9front`.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/scanmail/scanmail.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/scanmail/scanmail.c

`scanmail` is an SMTP/mail queue filter that canonicalizes incoming mail, applies configured spam patterns, and either passes the message to `upas/qer`, holds it, dumps it, saves a copy, or logs matched lines. It reads pattern data from `UPASLIB/patterns`, line logs to `UPASLOG/lines`, uses `/mail/box/<user>/nospamfiltering` for per-recipient opt-out, and rewrites the queue destination when a hold rule fires.

The main flow parses flags, collects sender and recipients, builds a lower-case sender/recipient command string, calls `canon()` to prepare header/body scan buffers, evaluates `Lineoff`, `Dump`, `HoldHeader`, `Hold`, and `SaveLine` actions in priority order, then streams the original raw message onward through `qmail()`. The scanner deliberately only scans bounded canonical buffers (`Hdrsize`, `Bodysize`) while preserving the original message for delivery.

Important behaviors include `Dump` switching `tflag` so the message is not queued, optional dump/copy files with hash-plus-random filenames, sender-domain queue naming under `-h -q`, and full bypass when all recipients opt out. Notable risks are pointer mutation in `matcher()` during dump and sender temporary mutation for domain queueing; both are local but require care when changing matching code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/scanmail/scanmail.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/scanmail/spam.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/scanmail/spam.h

This header defines the scanmail spam-pattern model shared by `scanmail`, `testscan`, and the pattern parser/matcher implementation. Actions are ordered by severity: `Dump`, `HoldHeader`, `Hold`, `SaveLine`, `Lineoff`, with `Lineoff` required last for control-flow assumptions in `scanmail.c`.

The core structures distinguish literal-string matchers (`Spat` hash buckets) from compiled regex matchers (`Reprog`) under `Pattern`, grouped by action in `Patterns`. Constants set scan limits, hash size, pattern type tags, and HTML/header/body read bounds.

The header also publishes the global pattern table, debug/header/cmd globals, and helper APIs for message reading, canonical conversion, base64 conversion, pattern parsing, matching, and match printing. It is a narrow contract for the spam scanner subsystem.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/scanmail/spam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/scanmail/testscan.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/scanmail/testscan.c

`testscan` is an offline driver for the scanmail pattern engine. It loads the configured pattern file or a `-p` override, reads one or more messages from a file or stdin, canonicalizes them with the same `readmsg`/`convert`/`conv64` path, and reports matched actions.

It supports debug, verbose canonical body/header dumping, and an `-a` mode that controls repeated-message handling. `dumppats()` can enumerate regex and string buckets, including alternate patterns, though it is not invoked from `main`.

The file mirrors scanmail allocation wrappers and match iteration but does not queue, hold, dump, or log messages. Its value is as a regression/manual diagnostic tool for pattern parsing and matching semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/scanmail/testscan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/authorize.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/authorize.c

`authorize()` runs a rewrite-rule authorization command stored in `dest.repl1`. A zero exit status authorizes forwarding; a nonzero status records stderr in `dest.repl2` and changes status to `d_noforward`.

The function marks `dp->authorized` before starting the command to avoid repeated authorization loops. It uses the shared process API, reads stderr to completion, waits, and frees process state. Failure to start the process is treated as forwarding disallowed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/authorize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/bind.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/bind.c

`up_bind()` resolves a list of destination addresses into concrete delivery actions. It first escapes addresses, checks forwarding loops in both destination and sender paths, rejects shell metacharacters, then iteratively applies rewrite rules, authorization, alias expansion, local mailbox expansion, and translation commands.

The resolution loop alternates between two work lists for up to 32 passes; unresolved entries after that become `d_loop`. Successful terminal entries are grouped with `d_same_insert()` so similar local or pipe deliveries can be batched.

`forward_loop()` detects repeated appearances of the local system in bang paths, guarding against external forwarding cycles. This file is the central address-binding state machine for `upas/send`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/bind.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/cat_mail.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/cat_mail.c

`cat_mail()` handles local mailbox delivery. It unescapes the mailbox path, supports dry-run output modes, treats `/dev/null` as successful discard, opens the target folder with `openfolder()`, appends the message with mailbox `From ` escaping, writes a trailing newline, closes the folder, and logs delivery.

Failures to create or write the mail file are converted to `refuse()` calls. The final receiver name is derived from the last bang component for logging.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/cat_mail.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/dest.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/dest.c

This file implements destination objects and their circular list mechanics. `dest` entries can be queued by `next` and grouped by `same`; grouped entries share a delivery command/mailbox and cap batch size with `MAXSAME` and `MAXSAMECHAR`.

`d_new`, `d_free`, `d_rm`, `d_insert`, `d_rm_same`, and `d_same_insert` form the destination container API. `d_same_insert()` also suppresses duplicate delivery arguments and groups only local mailbox or pipe actions.

`d_to()` synthesizes a `To:` header from destination groups, with special handling for `local!`. `s_to_dest()` parses whitespace-separated destination strings, preserving quoted fields, rejects shell characters, creates child destinations, and inherits authorization from the parent.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/dest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/filter.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/filter.c

`upas/filter` is a small delivery helper that reads a message, optionally matches sender/header/body regex rules, rewrites the target mailbox path, and delivers via `cat_mail()`. Flags select dry-run, header matching, and body matching.

It strips a leading local system from the parsed sender before matching. Each regexp/replacement pair is applied in order; first matching sender or selected message region rewrites the mailbox filename using `regsub()`.

The local `refuse()` exits immediately after printing the error, making this utility a simple command-line filter rather than a full bounce-capable mailer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/filter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/gateway.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/gateway.c

`gateway()` normalizes the message sender by removing leading systems listed as equivalent to the local host. It calls `skipequiv()` and replaces `mp->sender` only if the returned pointer advanced.

This is used early in `send/main.c` so gatewayed mail does not preserve redundant local routing prefixes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/gateway.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/local.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/local.c

`expand_local()` resolves local mailbox destinations into forwarding, pipe, local append, or unknown-user outcomes. It constructs mailbox paths, rejects `/../` path traversal, reads `forward` files unless already descended from a local forward, detects executable `pipeto` files, and checks mailbox writability before leaving `d_cat`.

The file contains mailbox access logic that approximates permission checks from directory metadata, with comments documenting known Plan 9 mailbox/group limitations. `pipeto` commands are built with `upasname`, original address, and mailbox path arguments.

This is the local-delivery policy bridge between rewrite rules and final mailbox/pipe actions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/local.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/log.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/log.c

This file centralizes syslog output for deliveries, remote forwards, and refusals. It unescapes sender/receiver strings, traces parent alias roots, includes dates and message size, and formats multi-line refusal text with `error+` prefixes.

`logdelivery()` logs one local delivery, `loglist()` drains and logs a list of remote/grouped destinations, and `logrefusal()` builds a bounded refusal log record. The functions mutate destination lists where they remove entries, so callers should treat passed lists as consumed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/main.c

This is the main `upas/send` mail delivery program. It parses dry-run, raw/rmail, debug, interactive, and address-list flags; reads or synthesizes a message; loads rewrite rules; normalizes sender routing; sets a safe reply address; rejects excessive `Received:` loops and overlarge messages; binds destinations; and dispatches to local append, pipe, or refusal paths.

`send()` delegates address resolution to `up_bind()` and adds a `To:` header when needed. Pipe delivery can detach asynchronously for user-submitted mail, batches same-command destinations, sends message text to the child process, captures stderr, and logs or refuses based on process status.

The refusal path builds human-readable bounce text, logs first, then either reports to SMTP/rmail, saves to `dead.letter`, or sends a multipart bounce from postmaster when asynchronous delivery owns the message. This file orchestrates the full send lifecycle and failure semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/message.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/message.c

`message.c` owns message allocation, reading, RFC 822 header normalization, sender/date extraction, large-message spillover, and output formatting. It keeps the first `VMLIMIT` bytes in memory and stores additional data in an ORCLOSE temp file, rejecting above `MSGLIMIT`.

For incoming rmail, `m_read()` parses Unix `From` lines, remote system chains, and dates using regexes. `rfc822cruft()` invokes the SMTP RFC 822 parser to discover headers, count `Received:`, mark bulk mail, preserve subject/from/reply-to metadata, and rewrite equivalent bang systems in address nodes.

Output functions print mailbox `From ` lines, synthesize `Date`, MIME UTF-8 headers, `From`, and `To` when absent, and choose escaped or raw body output. `m_get()` abstracts reading across memory and temp-file segments.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/message.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/regtest.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/regtest.c

`regtest` is an interactive Plan 9 regexp tester. It prompts for a regular expression, compiles it, then prompts for lines and prints `yes` or `no` for each match until an empty line.

It is standalone, using only libc, regexp, and bio. There is no mail-specific integration beyond living near rewrite/filter regex code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/regtest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/rewrite.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/rewrite.c

`rewrite.c` loads `/mail/lib/rewrite`, parses rewrite rules, compiles address regexes lazily, and substitutes captured fields into delivery command strings. Rule types map to pipe, mailbox append, alias, translate, and auth destination statuses.

`rule_parse()` expands `\l` to the local or alternate system name; `getrules()` duplicates such rules for `altthissys` when needed. `findrule()` skips authorization rules for already-authorized destinations and requires full-string regex matches.

`substitute()` supports numbered subexpressions, `&`, escaped backslash, `\s` reply address, and `\p` bulk/normal policy text. Regex errors are logged to syslog so broken rewrite rules are visible locally.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/rewrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/send.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/send.h

`send.h` declares the destination and message data models plus the cross-file API for `upas/send`. `d_status` enumerates every address resolution/delivery state, including pipes, local cats, aliases, auth, loops, bad mailboxes, resources, and `pipeto`.

The `dest` structure carries address, substitutions, parent alias chain, process status, authorization, and batching fields. The `message` structure carries sender/reply/date/body, storage fd, parsed-header flags, MIME/bulk state, boundary, and received count.

The header is the main integration contract between binding, rewriting, local expansion, message formatting, logging, and refusal handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/send.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/skipequiv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/skipequiv.c

`skipequiv()` removes leading bang-path systems found in `/mail/lib/equivlist`. It tokenizes the equivlist as whitespace/comma-separated names, caches the opened file, and repeatedly advances past matching path components.

The function temporarily writes NULs into the input string while testing each component, then restores `!`. It returns a pointer into the original string rather than allocating.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/skipequiv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/translate.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/translate.c

`translate()` runs a translation command from `dp->repl1`, reads stdout as a whitespace-separated destination list, recognizes `_nosummary_` control lines, converts output to child destinations via `s_to_dest()`, then reads stderr and waits.

A nonzero process status stores stderr in `dp->repl2` and returns no translated destinations. Process-start failure becomes `d_resource`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/send/translate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/greylist.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/smtp/greylist.c

This file implements SMTP greylisting for `smtpd`. It checks `/mail/grey/whitelist` for IP or subnet matches, tracks first-seen `(local IP, remote IP, recipient)` tuples under `/mail/grey/tmp`, and requires retry after `Nonspammin` and before `Nonspammax`.

If any recipient has a recent greylist entry, the remote IP is appended to the whitelist, optionally with reverse-domain metadata. Otherwise the server replies `451` and exits the transaction.

The implementation uses file creation/modification time as state and recursively creates parent directories. It rejects unsafe recipient path components before constructing greylist filenames.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/greylist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/mxdial.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/smtp/mxdial.c

`mxdial.c` resolves and dials SMTP destinations. It parses Plan 9 dial strings, expands `$host` through connection-server data, queries DNS for MX then IP records across `/net` and `/net.alt`, sorts MX records by preference per netdir, resolves MX hosts to IPs, rejects loopback MX targets, skips configured busted MX hosts, and dials each candidate with a timeout.

`mxdial0()` fills an `Mxtab` with candidates and supports a gateway-domain fallback. `mxdial()` returns the open fd and selected `Mx` metadata to the SMTP client.

DNS interaction uses `/net*/dns` files directly with timed writes and reads, so error strings determine retry/permanent behavior upstream.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/mxdial.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/parsetest.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/smtp/parsetest.c

`parsetest` is a diagnostic driver for the RFC 822 header parser. It reads up to 128 KiB from each file argument, calls `yyinit()`/`yyparse()`, prints reconstructed parsed headers, frees `Field`/`Node` structures, and flushes output.

It is useful for validating parser normalization and memory cleanup without involving SMTP delivery.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/parsetest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/rfc822.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/smtp/rfc822.y

This yacc grammar parses RFC 822-style mail headers and Unix `From ` lines into `Field` and `Node` lists. It recognizes originator, destination, date, subject, precedence, MIME/content, message-id, received, and generic optional fields while preserving original tokens and whitespace.

The lexer handles quoted strings, comments, folded continuation lines, delimiters, null removal, and keyword classification. Parser actions mark address nodes, count `Received:` headers, capture Unix sender/date/system nodes, and insert `BadHeader:` fields for skipped malformed material.

Downstream code uses this parser to rewrite addresses, detect header presence, add missing headers, and warn on forged domains. The parser preserves enough source offsets (`start`, `end`) for SMTP code to print parsed headers and then resume from unparsed body text.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/rfc822.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtp.c

This is the outbound SMTP client. It parses delivery, TLS, auth, filtering, gateway, host, ping, and busted-MX flags; resolves the destination via `mxdial`; performs greeting/EHLO/HELO; optionally negotiates STARTTLS or direct TLS; optionally authenticates with CRAM-MD5, LOGIN, or PLAIN; sends MAIL FROM, RCPT TO, DATA, and QUIT; and maps replies to retry or permanent failure.

`data()` reads and parses message headers, converts bang addresses to `@`/route form, adds `Message-ID`, `From`, `To`, and `Date` when absent, prints headers with CRLF, dot-escapes body lines, and logs successful bytes sent. Filter mode writes converted message text to stdout without network SMTP commands.

Security-relevant paths include certificate thumbprint checking unless `-C`, no cleartext password auth unless encrypted or `-i`, zeroing password buffers, loopback MX rejection, and robust timeout/closed-pipe handling via `atnotify`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtp.h

`smtp.h` defines shared parser and MX dialing types. `Node` stores token text, token type, address marker, whitespace, and source offsets; `Field` links parsed header fields; `DS`, `Mx`, and `Mxtab` describe dial strings and resolved mail exchangers.

It exports parser globals, parser helper functions, MX dialing functions, and a debug-print macro. This header is shared by the outbound client, inbound server, RFC 822 parser, and parser tests.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtpd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtpd.c

`smtpd.c` is the inbound SMTP server implementation. It initializes connection metadata, policy configuration, TLS/auth flags, blocked/trusted IP state, parser state, and a long alarm, then delegates protocol parsing to `smtpd.y`.

It implements SMTP verbs, relay checks, sender/recipient validation, sender-domain verification, greylisting, blocked-message dumping, message piping to `upas/send`, header parsing and rewriting, forged-domain warnings, received-line insertion, dot unescaping, UTF header validation, rejection throttling, TLS server wrapping, and AUTH PLAIN/LOGIN/CRAM-MD5.

Policy integrates `/mail/lib/smtpd.conf`, `/mail/ratify`, `/mail/lib/senders`, `/mail/lib/names.blocked`, optional `validateaddress`, optional `validatesender`, optional `validateattachment` via other tools, per-user spam opt-out, and trusted-network handling. The file is the main inbound mail security boundary.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtpd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtpd.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtpd.h

`smtpd.h` declares SMTP server policy states, linked-list helpers, globals shared between the C server and yacc command parser, and handler prototypes for SMTP commands and policy checks.

The state enum distinguishes accepted, refused, denied, dialup-blocked, delayed, trusted, and none/error classifications. Exports include connection info, sender/receiver lists, trusted flag, remote IP bytes, greylist, auth, data, reset, and spam-policy APIs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtpd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtpd.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtpd.y

This yacc grammar parses SMTP command conversations. It recognizes HELO/EHLO, MAIL FROM, RCPT TO, DATA, RSET, SEND/SOML/SAML aliases, VRFY/EXPN, HELP, NOOP, QUIT, STARTTLS, and AUTH with or without an initial response.

The grammar converts SMTP path syntax to Plan 9 bang paths, including route-addresses, mailbox domains, local parts, quoted strings, IPv4/IPv6 literals, anonymous `<>` as `/dev/null`, and optional spaces. Lexer input is 7-bit normalized, case-insensitive for alpha commands, and CRLF-aware.

Parser actions call the C handlers in `smtpd.c` directly. `cat()` builds `String` values from token fragments and frees consumed strings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/smtpd.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/spam.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/smtp/spam.c

Despite the filename, this is the SMTP daemon policy/configuration helper. It reads ratify actions, trusted IPs, `smtpd.conf`, local domains, relay settings, blocked sender/account actions, and names blocked lists. It also implements forwarding/masquerade checks, blocked-message dump filenames, and per-recipient spam-filter opt-out.

Actions come from `/mail/ratify/<action>/<type>/<value>` and can allow, block, deny, dial, or delay. `forwarding()` prevents untrusted relay unless the recipient is local or uses loopback syntax. `masquerade()` detects untrusted use of local domains in envelope or headers.

This file supplies much of `smtpd`'s local policy surface and filesystem-backed configuration behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/smtp/spam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/spf/dns.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/spf/dns.c

`dns.c` wraps DNS lookups for the SPF tool. `vdnsquery()` applies a 15-second alarm timeout, debug logging, recursion/query count limits, and delegates to `dnsquery()` under `netroot`.

It also provides `dnreverse()` for IPv4 reverse lookup names and `dncontains()` for suffix-style domain containment checks. The query limits differ from strict SPF spec comments but prevent runaway DNS recursion.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/spf/dns.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/spf/macro.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/spf/macro.c

`macro.c` expands SPF macro strings. It supports sender/local/domain/IP/PTR/version/helo macros, digit truncation, reverse ordering, delimiter selection, percent escapes, and defaults for unset sender/domain/helo/IP values.

IPv6 `%{i}` expansion emits nibble-dot form; `%{p}` performs reverse lookup validation via PTR plus forward address confirmation. The macro engine writes into bounded internal buffers and returns a newly allocated string, or nil for malformed macro syntax.

The implementation includes helper chopping/reversing logic that follows SPF macro field manipulation rules closely enough for local evaluation and the included testsuite.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/spf/macro.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/spf/mtest.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/spf/mtest.c

`mtest` is a command-line SPF macro expansion tester. It accepts optional debug/verbose flags and arguments for macro format, sender, domain, HELO, and IP, then prints `macro()` output.

It initializes IP formatting and defaults `netroot` to `/net`. It is paired with the `testsuite` rc script.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/spf/mtest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/spf/spf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/spf/spf.c

`spf.c` is a standalone SPF evaluator. It fetches SPF records from TXT/SPF DNS records or `-t`, parses mechanisms/modifiers into a flat `spftab`, recursively expands `include`/`redirect`, performs A/MX/PTR/exists/IP4/IP6 lookups, applies macro expansion, supports CIDR matching, and walks the resulting mechanism list against an IP.

The result is expressed through exit status: with sender/IP arguments it exits `fail` on SPF failure; with only a domain it prints records by default. Flags control debug, strict end failure, no macro expansion, print, recursion tracing, netroot, and verbose matching.

Notable caveats are called out in comments: query/recursion limits are pragmatic, `exists` and PTR behavior are ad hoc, and root-domain fallback is heuristic for several ccTLDs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/spf/spf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/spf/spf.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/spf/spf.h

`spf.h` includes Plan 9 system, bio, ndb, and IP headers and declares the shared SPF macro/DNS helper functions. It is the small common header for `spf`, `mtest`, `macro`, and `dns`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/spf/spf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/spf/testsuite -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/spf/testsuite

This rc script exercises SPF macro expansion examples for sender/domain/local-part/IP cases. It runs `mtest` across `%{s}`, `%{o}`, `%{d}` variants, local-part reversal/delimiters, IPv6 `%{i}`, and compound SPF DNS macro forms for both IPv6 and IPv4.

It is a lightweight manual regression fixture rather than a pass/fail harness.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/spf/testsuite -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/unesc/unesc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/unesc/unesc.c

`upas/unesc` decodes a simplified RFC 2047-like `=?charset?encoding?text?=` token stream from stdin to stdout. It skips the charset and encoding names, decodes `=XX` hex escapes inside the encoded text, and writes other bytes literally.

It does not implement full RFC 2047 semantics or charset conversion; it is a small stream utility for encoded-word unescaping.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/unesc/unesc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/vf/vf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/vf/vf.c

`upas/vf` is a MIME attachment filter. It parses multipart and forwarded-message structures, reads content headers, classifies content type and filename against `/sys/lib/mimetype`, rejects or wraps suspicious executable attachments, optionally saves rejected mail, and can delegate deeper inspection to `/mail/lib/validateattachment`.

The parser recursively handles boundaries, content type/disposition/encoding headers, RFC 2047 filename tokens, base64 and quoted-printable metadata, latin1-to-UTF conversion, Unix `From ` headers, and temporary diversion files. Dangerous attachments may be wrapped in a new multipart message with explanatory text and renamed `.suspect`; class `r` filenames are refused.

Flags select reject-only behavior and savefile. The filter is a defensive transformation stage intended to prevent automatic execution while preserving suspicious content when configured.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/vf/vf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/urlencode.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/urlencode.c

`urlencode` encodes stdin or a file to application/x-www-form-urlencoded style output, or decodes with `-d`. Encoding preserves alphanumerics and selected punctuation, maps space to `+`, and emits `%XX` uppercase hex for other bytes.

Decoding recognizes valid `%XX` pairs and `+` as space; malformed percent sequences are passed through conservatively. The tool uses buffered Plan 9 I/O and exits after flushing stdout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/urlencode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/va/a.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/va/a.h

`a.h` is the shared header for the MIPS assembler variant `va`. It defines symbol, operand (`Gen`), input stack, and history structures; assembler constants; global parser/lexer state; symbol tables; include/macro state; and prototypes for lexing, preprocessing, assembly passes, object emission, and diagnostics.

It includes MIPS object definitions from `../vc/v.out.h` and compiler compatibility helpers. The header binds the yacc grammar and lexer/body include files into one old-style Plan 9 assembler architecture.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/va/a.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/va/a.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/va/a.y

`a.y` is the yacc grammar for MIPS assembly syntax. It parses labels, variable assignments, scheduling directives, instruction forms, registers, memory operands, branch relatives, immediates, static/extern/auto/param symbols, constants, and arithmetic/bitwise expressions.

Each instruction production emits object code through `outcode()` with `Gen` operands and optional register fields. The grammar covers integer, load/store, branch/jump, TEXT/GLOBL/DATA, floating point, coprocessor, WORD, NOP, BREAK/CACHE-overloaded, and scheduler directives.

It is architecture-specific parser glue; instruction semantics and binary encoding are downstream in object emission/linker conventions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/va/a.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/va/lex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/va/lex.c

`lex.c` is the main driver, symbol initializer, object emitter, and lexer/preprocessor integrator for the `va` MIPS assembler. It parses command-line flags, handles multiple input files in parallel where supported, runs two assembly passes, emits history/name/address/object records, initializes register/instruction symbols, and includes shared compiler lexer and macro bodies.

The instruction table maps textual registers, special registers, floating registers, and opcodes to yacc token classes and architecture opcodes. `outcode()` emits object records only on pass 2, interns symbols in a bounded table, and increments `pc` for non-DATA/GLOBL instructions.

The file relies on Plan 9 compiler compatibility routines for filesystem, process, include, macro, and lexical behavior. It is the executable core around the grammar in `a.y`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/va/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vac/dat.h

`dat.h` defines internal metadata block structures for the vac archive filesystem tools. It sets constants for maximum block size, estimated directory-entry bytes, block fullness threshold, flush size, and dirty percentage.

`MetaEntry` points at an entry payload and size. `MetaBlock` tracks allocated/used/free metadata block space, index table capacity/use, an `unbotch` flag, and the backing buffer. `VacDirEnum` stores directory enumeration state over a `VacFile`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/error.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vac/error.c

`error.c` defines shared vac error strings such as missing directory entry, no file, bad path, corrupted metadata, not directory/file, I/O error, bad offset, too big, read-only, removed, illegal block address, directory not empty, existing file, and root removal.

The strings are exported as mutable global char arrays matching declarations in `error.h`, allowing code to compare or pass stable Plan 9-style error text.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/error.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/error.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vac/error.h

`error.h` declares the vac error-string globals and undefines `EIO` first to avoid collisions with host `<errno.h>` on Mac OS X. It is included by vac implementation files that need shared textual error identifiers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vac/error.h -->