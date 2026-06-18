# Group Research: Plan 9 upas Mail Sources Group 1628

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/mbox.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/mbox.c

## Purpose
Core mailbox/message model for `upas/fs`. It creates mounted mailbox objects, parses RFC822/MIME message structure, exposes message files through the mail filesystem hash namespace, tracks deletion/refcounts, decodes bodies, converts charsets, and emits plumber notifications.

## Main Interfaces
- `newmbox`, `freembox`, `syncmbox`: mailbox lifecycle and backend dispatch.
- `parseunix`, `parseheaders`, `parsebody`, `parse`, `parseattachments`: split raw mail into headers, body, MIME parts, and exported filesystem entries.
- `newmessage`, `delmessage`, `delmessages`: message allocation and recursive deletion.
- `msgincref/msgdecref`, `mboxincref/mboxdecref`: lifetime management under mailbox locks.
- `decode`, `convert`, `decquoted`, `xtoutf`: content-transfer and charset decoding.
- `mailplumb`: sends `mailfs` plumb events for new/deleted mail.

## Behavior
`boxinit` tries IMAP4, POP3, Plan B, Plan B virtual, and Plan 9 mbox initializers in order. `parseheaders` recognizes common RFC822 and MIME headers, builds Unix `From ` fallback headers for POP3/IMAP messages, normalizes text bodies by squeezing NULs, and creates per-message file nodes such as `body`, `raw`, `header`, etc. MIME multipart parsing uses boundary scanning; `message/rfc822` parts are recursively parsed and may promote child headers to the wrapper part.

## Dependencies
Uses Plan 9 `String`, `plumb`, `libsec` SHA/base64 helpers, `tcs` for non-Latin1 charset conversion, global mailfs hash helpers (`henter/hfree`), and backend initializers declared elsewhere.

## Risks / Notes
- MIME boundary parsing is string-based and assumes boundary markers at line starts.
- `xtoutf` forks `/bin/tcs`; charset conversion failure silently leaves original bytes.
- `parseheaders` temporarily writes NUL into headers while extracting Received dates.
- Message deletion syncs only after refs drop, so stale refs delay physical purge.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/mbox.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/plan9.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/plan9.c

## Purpose
Plan 9 traditional mbox backend for `upas/fs`, reading and rewriting single-file mailboxes with `From ` separators.

## Main Interfaces
- `plan9mbox`: recognizes accessible local mailbox paths and installs `plan9syncmbox`.
- `plan9syncmbox`: locks, reads/interpolates new mail, purges deleted mail, and rewrites if needed.
- `_readmbox`: incremental mailbox read/merge using qid path/version and previous length.
- `_writembox`: rewrites non-deleted messages through `<mbox>.tmp`.
- `purgedeleted`: removes deleted, unreferenced messages.

## Behavior
Messages are read by scanning for `\nFrom ` boundaries, SHA1-digested, parsed through `mbox.c`, and deduplicated against existing message digests. If the mailbox qid path is unchanged, it seeks to the old length to append-read new messages; if old messages disappear, they are marked deleted and optionally plumbed. Physical deletion rewrites the mailbox atomically via a temp file rename.

## Dependencies
Relies on `syslock`, `sysrename`, `sysopen`, `parseunix`, `parse`, `mailplumb`, `logmsg`, and SHA1 from `libsec`.

## Risks / Notes
- Message boundary detection depends on unescaped `From ` lines.
- Incremental read assumes qid path/version/length semantics faithfully identify append-only changes.
- Rewrite removes and renames files, preserving only basic mode bits.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/plan9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/planb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/planb.c

## Purpose
Plan B/mail2fs mailbox backend for `upas/fs`, supporting directory mailboxes and virtual folders.

## Main Interfaces
- `planbmbox`: recognizes directory mailboxes containing `list`.
- `planbvmbox`: recognizes virtual folder files beginning with six digits and `/`.
- `mbsync`, `mbvsync`: sync normal and virtual Plan B mailboxes.
- `readpbmbox`, `readpbvmbox`: enumerate real directory mailboxes or virtual folder lists.
- `readpbmessage`: loads one Plan B message from `raw` and `text`.

## Behavior
A Plan B message is reconstructed from its `raw` first line and `text` body, with the message path appended to the body as a hint for attachment access. Normal directory mailboxes walk month directories and numeric message directories; virtual mailboxes parse message paths out of a listing file and map them under `/mail/box/$user/msgs`.

## Dependencies
Uses `readmessage`, `parseunix`, `parse`, `mailplumb`, `delmessage`, Plan 9 `Dir` operations, and mailbox fields from `dat.h`.

## Risks / Notes
- File comment documents a known limitation: raw attachment text is not reconstructed, so IMAP/other clients cannot access attachments through this backend.
- Deleted non-virtual messages are archived by renaming message directories to `s.<id>`.
- Virtual folder input is capped at 2 MiB and logs a “folder too big” warning.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/planb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/pop3.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/pop3.c

## Purpose
POP3 mailbox backend for `upas/fs`, fetching remote mail into the mail filesystem view and deleting remote messages when local messages are marked deleted.

## Main Interfaces
- `pop3mbox`: parses `/pop`, `/apop`, TLS, SSL, and no-TLS mailbox paths.
- `pop3sync`: dial/login/read/purge/hangup cycle.
- `pop3login`, `pop3capa`, `pop3pushtls`: authentication and security negotiation.
- `pop3read`: UIDL-based mailbox reconciliation.
- `pop3download`: retrieves and parses one message.
- `pop3purge`: issues `DELE` for deleted messages.
- `pop3ctl`: mailbox control commands for debug, thumbprint, refresh.

## Behavior
The backend prefers APOP when available unless plain POP is requested, negotiates STLS or SSL variants, records UIDLs to match existing messages, downloads only new messages, parses them through `mbox.c`, and schedules refresh via `waketime`. It supports POP3 pipelining by forking a writer process that batches `LIST/RETR` or `DELE`.

## Dependencies
Uses Plan 9 auth/factotum (`auth_respond`, `auth_getuserpasswd`), TLS (`tlsClient`, thumbprints), `Biobuf`, `dial`, SHA1, and mailfs parser/message APIs.

## Risks / Notes
- Certificate thumbprint checking is compiled out with `if(0)`, so TLS currently verifies only that a certificate exists.
- POP3 size claims are treated as unreliable; buffers grow during `RETR`.
- UIDL longer than RFC limits is ignored.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/pop3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/readdir.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/readdir.c

## Purpose
Tiny diagnostic program that opens `/mail/fs`, calls `dirread`, and prints directory entry names.

## Behavior
It loops over `dirread(fd, &d, sizeof(d))`, prints each `Dir.name`, and then prints the final read count.

## Dependencies
Plan 9 libc `open`, `dirread`, `print`.

## Risks / Notes
No error handling for failed `open`; likely an ad hoc test utility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/readdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/strtotm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/strtotm.c

## Purpose
Heuristic RFC822-ish date string parser used by mailfs to convert mail dates into Plan 9 `Tm`.

## Main Interfaces
- `strtotm(char *p, Tm *tmp)`: scans free-form date text for month, day, year, time, zone, and numeric offset.

## Behavior
The parser tokenizes by whitespace, recognizes `hh:mm[:ss]`, three-letter month names case-insensitively, three-letter all-caps zones ending in `T`, numeric `+/-HHMM` offsets, day numbers, and years. It converts with `tm2sec` minus the offset and returns localtime of the resulting epoch.

## Dependencies
Plan 9 `Tm`, `localtime`, `tm2sec`; C `ctype`.

## Risks / Notes
- Time zone abbreviations are copied but only numeric offsets affect conversion.
- Two-digit years are not accepted as years.
- Parsing is permissive and order-insensitive, intended as a fallback heuristic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/strtotm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/tester.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/tester.c

## Purpose
Standalone mailbox parser test utility.

## Behavior
Creates a root message, reads a mailbox file via `readmbox`, and recursively prints message/part metadata: sizes, Unix from/date, address headers, subject, filename, type, and charset.

## Dependencies
`message.h`, `String`, `newmessage`, `readmbox`, and message fields from the mailfs parser.

## Risks / Notes
Hard-coded default `./mbox`; exits success even on read error after printing `boom`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/tester.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/marshal/marshal.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/marshal/marshal.c

## Purpose
User-facing message composer/generator. It reads headers/body/attachments, expands aliases, emits MIME/RFC822 output, optionally runs PGP, and streams the result into `upas/send`.

## Main Interfaces
- `main`: option parsing and full compose/send pipeline.
- `readheaders`: preserves and classifies user-supplied headers, strips `Bcc`, optionally extracts recipients from headers.
- `body`, `body64`, `attachment`: body and attachment MIME generation.
- `sendmail`: forks `upas/send` or user `pipefrom`, optionally files a copy.
- `pgpfilter`: inserts `/bin/pgp` between marshal and send.
- `readaliases`, `expand`, `expandline`: personal alias and RFC822 address expansion.
- `rfc2047fmt`, `mksubject`: UTF-8 subject header encoding.

## Behavior
`marshal` can send with command-line recipients or `-8` recipient headers, add default Date/From/To/Cc/Subject/MIME headers, infer attachment content types from builtins, `/sys/lib/mimetype`, or `/bin/file`, construct multipart/mixed messages, and append in-reply-to from a mailfs message directory. It protects typed messages with `holdon/holdoff` and cleans up child processes on fatal errors.

## Dependencies
Plan 9 `Biobuf`, `String`, `Fmt`, mailbox path helpers, `/bin/upas/send`, optional `/bin/pgp`, optional `/bin/file`, and `/sys/lib/mimetype`.

## Risks / Notes
- RFC822 parsing is intentionally partial; malformed address headers set `rfc822syntaxerror`.
- Attachment type inference depends on extension and external `file`.
- The compose path can fork several processes; failures are propagated through wait messages.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/marshal/marshal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/misc/mail -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/misc/mail

## Purpose
Plan 9 `rc` wrapper for the `mail` command.

## Behavior
With no arguments it execs `upas/nedmail`. For flags matching reader-style options (`-f*`, `-r*`, `-c*`, `-m*`) it also execs `upas/nedmail`; otherwise it execs `upas/marshal` to compose/send mail.

## Dependencies
Plan 9 `rc`, `upas/nedmail`, `upas/marshal`.

## Risks / Notes
This is dispatch glue; behavior is entirely determined by first argument shape.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/misc/mail -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/misc/qmail -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/misc/qmail

## Purpose
Queue-and-run helper for remote mail.

## Behavior
Takes sender/address arguments, invokes `qer /mail/queue mail ...` to enqueue the message, then runs `runq /mail/queue /mail/lib/remotemail` if queueing succeeds.

## Dependencies
Plan 9 `rc`, `qer`, `runq`, `/mail/lib/remotemail`.

## Risks / Notes
No argument validation beyond positional shell assignments.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/misc/qmail -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/misc/remotemail -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/misc/remotemail

## Purpose
Remote SMTP delivery wrapper used by the mail queue.

## Behavior
Shifts queue/control arguments to isolate sender and destination address, then runs `/bin/upas/smtp -g research.research.bell-labs.com $addr $sender $*`.

## Dependencies
Plan 9 `rc`, `/bin/upas/smtp`.

## Risks / Notes
Gateway host is hard-coded.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/misc/remotemail -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/misc/unix/gone.fishing.sh -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/misc/unix/gone.fishing.sh

## Purpose
Unix vacation/autoreply-style shell script.

## Behavior
Reads a message from stdin, appends it to `$HOME/gone.mail` with `From ` escaping, extracts the return sender from the first `From ` line, records senders in `$HOME/gone.addrs`, and sends a one-time auto-reply using `mail`.

## Dependencies
POSIX shell, `sed`, `tee`, `grep`, `mail`.

## Risks / Notes
Sender extraction is simplistic and based only on Unix `From ` line format.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/misc/unix/gone.fishing.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/misc/unix/mail.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/misc/unix/mail.c

## Purpose
Unix C wrapper for `/bin/mail` compatibility in the upas Unix port.

## Behavior
Chooses `edmail` for no arguments or reader flags such as `-m`, `-f`, `-r`, `-p`, `-e`; exits immediately for `-n`; otherwise chooses `send`. It constructs the target path from `UPASROOT` and `execv`s the selected program.

## Dependencies
External `UPASROOT`, `edmail`, `send`, Unix `execv`.

## Risks / Notes
Old K&R C style; assumes `UPASROOT` is defined by linked configuration.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/misc/unix/mail.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/misc/unix/mail.sh -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/misc/unix/mail.sh

## Purpose
Shell version of the Unix `/bin/mail` compatibility wrapper.

## Behavior
Dispatches `-n` to `LIBDIR/notify`, reader-style flags or empty invocation to `LIBDIR/edmail`, and all other invocations to `LIBDIR/send`.

## Dependencies
POSIX shell; install-time substitution of `LIBDIR`.

## Risks / Notes
Uses `$*`, so shell word preservation depends on caller/legacy expectations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/misc/unix/mail.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/misc/unix/makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/misc/unix/makefile

## Purpose
Unix makefile for building/installing the mail wrapper and notification/vacation utilities.

## Behavior
Builds `mail` and `notify`, generates `sed.file` substitutions for `LIBDIR` and `HOSTNAME`, installs `gone.fishing`, `gone.msg`, `/bin/mail`, and optional compiled binaries, then provides cleanup targets.

## Dependencies
Unix `make`, C compiler, upas config object, shell tools, `/usr/lib/upas`.

## Risks / Notes
Install targets perform privileged copies/chown/chmod and assume legacy filesystem layout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/misc/unix/makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/ml/common.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/ml/common.c

## Purpose
Shared mailing-list support routines for list delivery, membership storage, notifications, and address extraction.

## Main Interfaces
- `getaddrs`: extracts `From`/`Sender` from parsed RFC822 fields.
- `readaddrs`, `addaddr`, `remaddr`, `writeaddr`: maintain append-only address-list files with `!addr` removals.
- `startmailer`: forks `/bin/upas/send` to distribute to all current list members.
- `sendnotification`: sends add/remove notices to subscribers.

## Behavior
Address-list files are append-only and replayed at read time, where comments are ignored and `!` entries remove earlier addresses. `startmailer` sets `upasname` to `<list>-owner` so list mail has a non-empty sender. Membership changes trigger notification unless the address line begins with `#`.

## Dependencies
`common.h`, `dat.h`, Plan 9 `String`, `Biobuf`, `upas/send`, parsed SMTP/RFC822 fields.

## Risks / Notes
Membership uniqueness is exact string equality only. `putenv(smprint(...))` allocations are not reclaimed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/ml/common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/ml/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/ml/dat.h

## Purpose
Shared declarations for the mailing-list programs.

## Contents
Defines `Addr` linked-list nodes, globals for parsed headers and list addresses (`from`, `sender`, `firstfield`, `na`, `al`), includes SMTP parser headers, and declares helper functions from `common.c`.

## Dependencies
`../smtp/smtp.h`, `../smtp/y.tab.h`, `String`, parser `Field`/`Node`.

## Risks / Notes
Globals are shared across small single-purpose programs rather than encapsulated.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/ml/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/ml/ml.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/ml/ml.c

## Purpose
Mailing-list remailer for normal list submissions.

## Behavior
Reads a message from stdin, discards the Unix `From ` line, reads up to 2 MiB, parses headers, determines sender, rejects mail from the list address itself, adds sender to in-memory recipients, starts `upas/send`, writes a modified message, waits for the mailer, and appends to the list mailbox archive if it exists.

## Key Functions
- `printmsg`: suppresses original `Reply-To` and `Precedence`, rewrites subject with `[list]`, adds `Reply-To` and `Precedence: bulk`.
- `appendtoarchive`: appends original first line and message to list mbox if present.
- `printsubject`: prefixes subject with `[list]` unless already present.

## Dependencies
Mailing-list common helpers, RFC822 parser globals, `/bin/upas/send`.

## Risks / Notes
Only the first 2 MiB are read, so larger submissions are truncated.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/ml/ml.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/ml/mlmgr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/ml/mlmgr.c

## Purpose
Command-line manager for creating mailing lists and adding/removing members.

## Behavior
Supports mutually exclusive `-c listname`, `-a listname addr`, and `-r listname addr`. Creation makes mailboxes for the list and owner, creates `pipeto` scripts pointing to `ml` and `mlowner`, and seeds the address-list file with a comment. Add/remove append entries to the address-list file.

## Key Function
- `createpipeto`: creates executable rc scripts in mailbox `pipeto` files.

## Dependencies
`creatembox`, `mboxpath`, `writeaddr`, Plan 9 `Dir`/`dirfwstat`.

## Risks / Notes
Creation uses simple file writes for executable scripts and reports some stat/wstat failures into the script file itself.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/ml/mlmgr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/ml/mlowner.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/ml/mlowner.c

## Purpose
Owner-command processor for mailing-list subscribe/unsubscribe requests.

## Behavior
Reads one message from stdin, discards Unix `From `, reads up to 128 KiB, parses headers, extracts sender, then removes the sender if the message contains `remove` or `unsubscribe`, or adds the sender if it contains `subscribe`.

## Dependencies
Mailing-list common helpers, SMTP/RFC822 parser.

## Risks / Notes
Command detection is a raw substring search over the message; “unsubscribe” also contains “subscribe”, but removal is checked first.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/ml/mlowner.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/ned/nedmail.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/ned/nedmail.c

## Purpose
Interactive terminal mail reader/editor built on `/mail/fs`.

## Main Interfaces
- `main`: starts `upas/fs` if needed, opens/selects mailbox, enters command loop.
- `dir2message`, `file2message`: build an in-memory tree from mailfs directories and `info` files.
- `parsecmd`, `parseaddr`, `parsesearch`: command/range/search parser.
- Command handlers: print, raw print, delete/undelete, sync, save, write attachment, reply, forward, pipe, shell, help, file-by-sender.
- `flushdeleted`: sends deletion requests to `/mail/fs/ctl`.

## Behavior
The client represents mailfs messages as nested `Message` nodes. It prints concise headers, MIME trees, raw or processed content, chooses displayable multipart alternatives, pipes HTML through `htmlfmt`, plumbs image/pdf-like attachments, and delegates replies/forwards to `/bin/upas/marshal`. Save/write commands append raw messages to mbox files or write body parts to files.

## Dependencies
`/mail/fs`, `/bin/upas/fs`, `/bin/upas/marshal`, Plan 9 plumber, regexp library, `String`, mailbox helper routines.

## Risks / Notes
- Command parsing is ed-like and compact but hand-written.
- MIME display heuristics include empirical length thresholds for bad multipart/alternative mail.
- Some command execution uses `/bin/rc -c` with user-entered text by design.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/ned/nedmail.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/pop3/pop3.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/pop3/pop3.c

## Purpose
POP3 server exposing a local upas mailbox through the POP3 protocol.

## Main Interfaces
- POP commands: `USER`, `PASS`, `APOP`, `CAPA`, `STLS`, `STAT`, `LIST`, `UIDL`, `RETR`, `TOP`, `DELE`, `RSET`, `SYNC`, `QUIT`.
- `readmbox`: starts `upas/fs -np -f <box>`, reads `/mail/fs/mbox`, and builds POP message metadata.
- `dologin`: validates APOP/factotum response, changes user identity, creates namespace, and opens mailbox.

## Behavior
The daemon advertises APOP challenge on greeting, optionally allows cleartext password only with `-p` or after TLS, supports STLS with configured certificate, computes POP byte sizes by adding CR bytes to mailfs raw lengths, dot-stuffs output, and deletes marked messages by writing `delete mbox ...` to mailfs control on sync/quit.

## Dependencies
Plan 9 auth (`auth_challenge`, `auth_response`, `auth_chuid`), TLS server, `/bin/upas/fs`, `/mail/fs`, `Biobuf`, `libsec`.

## Risks / Notes
- Cleartext password is disabled unless explicitly allowed or TLS is active.
- Auth failures exponentially back off and eventually terminate.
- `enableaddr` writes a trust marker under `/mail/ratify/trusted`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/pop3/pop3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/q/qer.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/q/qer.c

## Purpose
Queue entry writer for upas queued delivery.

## Behavior
Creates a per-user or specified queue directory, writes stdin to a generated `D.*` data file, optionally copies associated `-f` files as `F*`, then creates a locked `C.*` control file containing delivery arguments and associated file names. The data file is created before the control file so `runq` does not see incomplete entries as runnable.

## Dependencies
Plan 9 `String`, queue directory conventions (`C.*`, `D.*`, `F*`), `syscreatelocked`.

## Risks / Notes
Logs if data does not start with `From`; read errors from stdin are intentionally ignored/commented out.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/q/qer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/q/runq.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/q/runq.c

## Purpose
Queue runner for retrying and completing upas queued deliveries.

## Main Interfaces
- `main`: option parsing and queue root selection.
- `doalldirs`, `dodir`, `rundir`: scan user queue directories.
- `dofile`: process one `C.*`/`D.*` queue item.
- `returnmail`: bounce failed mail back to sender.
- `doload`: global load-file limiter.

## Behavior
`runq` scans `C.*` control files, verifies matching data files, respects retry backoff based on `E.*` error-file age, locks control files, keeps locks alive with a helper process, executes the configured delivery command with the data file on stdin and errors appended to `E.*`, and removes all matching queue files on success or permanent failure. Temporary bad systems are skipped for the rest of a run.

## Dependencies
Queue naming conventions, `Mlock`, `sysopenlocked`, `upas/marshal` for bounces, `returnable`, syslog.

## Risks / Notes
- Give-up default is 2 days unless `-R` disables permanent give-up.
- Control-file argument parsing is whitespace/quote aware but simple.
- Bounce suppression avoids postmaster and unreturnable senders.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/q/runq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/scanmail/common.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/scanmail/common.c

## Purpose
Shared canonicalization and pattern-matching engine for spam/scanning tools.

## Main Interfaces
- `readmsg`: reads full headers plus at least a body prefix for scanning.
- `convert`, `conv64`: canonicalize header/body text, lowercasing, whitespace folding, HTML stripping, MIME escape handling, and base64 body conversion.
- `parsepats`: loads pattern files into regexp and hashed literal structures.
- `matchpat`: matches literal or regexp patterns with alternate exclusions.
- `xprint`: prints match context.

## Behavior
Headers are detected with care for fractured headers and embedded NULs. Body canonicalization removes most HTML tags while preserving URLs/forms/images of interest. Patterns can be actions such as `DUMP`, `HEADER`, `HOLD`, `LINE`, and `LINEOFF`, with string patterns introduced by `*` and alternate exclusions separated by `~~`.

## Dependencies
`regexp.h`, `bio.h`, `spam.h`, global `header` and `cmd` buffers supplied by callers, Plan 9 `dec64`.

## Risks / Notes
- Only bounded canonical buffers are produced (`Hdrsize`, `Bodysize`, `Maxread`).
- The file ends with a static base64 decode table; local conversion uses `dec64`.
- HTML handling is heuristic and intentionally lossy for spam matching.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/scanmail/common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/scanmail/scanmail.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/scanmail/scanmail.c

## Purpose
Mail scanner/filter that canonicalizes incoming mail, applies spam/hold/dump patterns, and then queues or drops/copies mail.

## Main Interfaces
- `main`: parses scanner options, loads patterns, canonicalizes message, evaluates actions, and calls `qmail`.
- `qmail`: streams buffered and remaining message data into `qer` or `/dev/null`.
- `matchaction`, `matcher`: apply action-specific patterns to command, header, and body.
- `saveline`, `opendump`, `opencopy`: logging/copy side effects.
- `optoutofspamfilter`: per-recipient opt-out check.

## Behavior
The scanner builds a lowercased command string from sender and recipients, canonicalizes header/body, skips filtering if all recipients have `nospamfiltering`, runs `Lineoff` first, then applies actions in priority order. `Hold` changes queue directory to hold queue; `Dump` suppresses queueing and optionally saves a dump; `SaveLine` logs matched context.

## Dependencies
`qer`, `UPASLIB/patterns`, `UPASLOG/lines`, spool directories, common scanner engine.

## Risks / Notes
- Opt-out is all-recipient based: if every recipient opts out, patterns are skipped.
- `Dump` mutates the match buffer by writing NUL at match end for logging.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/scanmail/scanmail.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/scanmail/spam.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/scanmail/spam.h

## Purpose
Shared constants, action IDs, pattern data structures, globals, and prototypes for scanmail.

## Contents
Defines action order (`Dump`, `HoldHeader`, `Hold`, `SaveLine`, `Lineoff`), hash and buffer sizes, pattern types (`regexp`, `string`), `Spat`, `Pattern`, and `Patterns` structures, plus externs for scanner globals and common functions.

## Dependencies
Plan 9 regexp `Reprog`/`Resub` and `Biobuf`.

## Risks / Notes
Action order is semantically important: `Dump` has highest priority and `Lineoff` must be last.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/scanmail/spam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/scanmail/testscan.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/scanmail/testscan.c

## Purpose
Standalone tester for scanmail pattern parsing and canonical matching.

## Behavior
Loads a pattern file, reads messages from a file or stdin, canonicalizes header/body using shared functions, optionally prints canonical text, applies all patterns, prints match context, and exits with the last matched action string.

## Dependencies
`sys.h`, `spam.h`, scanner common functions.

## Risks / Notes
Uses static raw-message state in `canon` to process the first message with headers and subsequent reads without header processing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/scanmail/testscan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/authorize.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/authorize.c

## Purpose
Runs an authorization command for destinations that match `auth` rewrite rules.

## Behavior
Marks destination authorized, starts the configured process, drains stderr, and if the process exits nonzero changes status to `d_noforward` with stderr as the refusal message.

## Dependencies
`proc_start`, `proc_wait`, `stream`, `dest` status fields.

## Risks / Notes
Authorization command failure is converted into forwarding refusal rather than process-level failure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/authorize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/bind.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/bind.c

## Purpose
Destination binder for `upas/send`, resolving addresses into local delivery, pipes, aliases, translators, authorization, or errors.

## Main Interfaces
- `up_bind`: iterative binding loop over destination lists.
- `forward_loop`: detects excessive local-system hops in bang paths.

## Behavior
Initial pass escapes destinations, checks forwarding loops and shell characters, then repeatedly applies rewrite rules and expands results for up to 32 iterations. It handles authorization, local forward files, local `pipeto`, alias expansion, translator output, and grouping of bound destinations.

## Dependencies
`rewrite`, `authorize`, `expand_local`, `translate`, destination list utilities.

## Risks / Notes
Unresolved destinations after 32 passes are marked forwarding loops.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/bind.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/cat_mail.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/cat_mail.c

## Purpose
Local mailbox delivery implementation for `upas/send`.

## Behavior
Unescapes the target mailbox path, optionally prints dry-run output, locks the mailbox, opens it append-locked or falls back to `.tmp`, writes the message in mbox format via `m_print`, appends a blank line, flushes, unlocks, and logs delivery.

## Dependencies
`syslock`, `sysopen`, `m_print`, `logdelivery`, `refuse`.

## Risks / Notes
Retries open fallback up to five times, but a lock failure immediately refuses delivery.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/cat_mail.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/dest.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/dest.c

## Purpose
Destination list data structure helpers for `upas/send`.

## Main Interfaces
- `d_new`, `d_free`: destination allocation.
- `d_insert`, `d_rm`: circular queue management.
- `d_same_insert`, `d_rm_same`: group equivalent destinations for one command/mailbox.
- `d_to`: generate a `To:` header from destinations.
- `s_to_dest`: parse whitespace/quote-separated destination strings.

## Behavior
Destinations are stored as circular lists; `same` chains group destinations with identical delivery action/replacement while suppressing duplicates and limiting group size/argument length.

## Dependencies
`String`, destination status definitions, escaping helpers.

## Risks / Notes
Parsing is whitespace-oriented with basic double-quote handling, not full RFC822 address parsing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/dest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/filter.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/filter.c

## Purpose
Local filtering delivery helper that routes a message to different mailbox files based on regexps.

## Behavior
Reads a remote-style message, strips local system prefix from sender, tests sender and optionally header/body against regexp/replacement pairs, rewrites the destination file path via `regsub`, locks the normal mailbox, opens selected mailbox or `.tmp`, appends the message, and logs delivery.

## Dependencies
`m_read`, `m_print`, Plan 9 regexp, `syslock`, `sysopen`, `logdelivery`.

## Risks / Notes
The normal mailbox is always locked even when delivering to another file, by design comment.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/filter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/gateway.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/gateway.c

## Purpose
Gateway sender normalization for `upas/send`.

## Behavior
Calls `skipequiv` on the message sender and, if equivalent local systems are removed, replaces `mp->sender` with the shortened address.

## Dependencies
`skipequiv`, `String`, `message`.

## Risks / Notes
Minimal translation only; broader gateway behavior is handled elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/gateway.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/local.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/local.c

## Purpose
Local-address expansion logic for forwarding files, `pipeto`, and mailbox existence.

## Main Interfaces
- `expand_local`: resolves one local destination after rewrite produced `d_cat`.

## Behavior
Rejects `/../` paths, determines local user, fills default mailbox path if needed, optionally reads a `forward` file and returns expanded destinations, detects `pipeto` and rewrites the destination to execute that script, or marks destination `d_cat` if the mailbox directory exists.

## Dependencies
`mboxpath`, `mboxname`, `sysopen`, `sysexist`, `s_to_dest`.

## Risks / Notes
Comment notes `pipeto` shell construction is unsafe for account names with special characters, though earlier address escaping mitigates some cases.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/local.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/log.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/log.c

## Purpose
Syslog logging helpers for delivery, forwarding, and refusal events.

## Main Interfaces
- `logdelivery`
- `loglist`
- `logrefusal`

## Behavior
Unescapes sender/recipient strings, preserves original parent aliases where relevant, logs successful local deliveries, remote/pipe forwarding, and multiline refusals with `error+` continuation prefixes.

## Dependencies
`syslog`, destination list helpers, `String` escaping helpers.

## Risks / Notes
Fields are truncated with `%.256s` to bound log entries.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/main.c

## Purpose
Main mail delivery program. It reads a message, normalizes sender/header context, resolves destinations, performs local/pipe delivery, and handles bounce/refusal behavior.

## Main Interfaces
- `main`: argument parsing, message read/default creation, rewrite setup, gateway normalization, loop/size checks.
- `send`: binds destinations and dispatches by status.
- `pipe_mail`: executes command deliveries.
- `complain_mail`, `refuse`, `replymsg`: refusal/bounce handling.
- `save_mail`: saves interrupted or failed interactive mail to dead.letter.

## Behavior
Supports dry-run/list modes, rmail mode, debug, no-input mode, and interrupt saving. It protects sender strings from shell characters, rejects excessive Received loops and oversized messages, groups destinations by action, optionally daemonizes before pipe delivery, logs results, and generates multipart bounce mail for non-bulk failures.

## Dependencies
`message.c`, rewrite/bind/local/dest/log modules, process/stream helpers, mailbox path helpers.

## Risks / Notes
- Asynchronous pipe delivery exits parent early to reduce user wait.
- Bulk mail is not bounced.
- Out-of-resource refusals request retry instead of permanent failure in rmail mode.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/makefile

## Purpose
Legacy Unix makefile for building and installing `upas/send`.

## Behavior
Defines source/object lists, include paths, compile/link rules, dependencies, `prcan`, `clean`, `cyntax`, and privileged install target that copies `send` to upas lib and `/bin/rmail`, strips, chowns root, and sets setuid mode.

## Dependencies
C compiler, upas common/config/libc archives, `/usr/lib/upas`.

## Risks / Notes
Install target creates setuid-root binaries; source list includes historical modules beyond this research group.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/message.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/message.c

## Purpose
Message parsing, storage, header normalization, and output formatting for `upas/send`.

## Main Interfaces
- `m_new`, `m_free`: message lifecycle.
- `default_from`: default sender/date setup.
- `m_read`: reads interactive, local, or rmail input.
- `rfc822cruft`: parses headers, records header flags, removes equivalent systems in addresses, detects bulk.
- `m_get`: chunked access to in-memory/temp-file message body.
- `m_print`, `m_bprint`: output message with remote/local/mbox formatting.

## Behavior
Messages up to about 64 KiB stay in memory; larger bodies spill to a temp file, with a 128 MiB limit. Remote `From` lines are parsed for sender/date. RFC822 parser output is used to detect existing Date/From/MIME/Subject/To fields and rewrite equivalent bang paths. Output adds Unix/remote headers, Date, From, To, and UTF-8 MIME headers when needed, and escapes `From ` lines for mbox delivery.

## Dependencies
SMTP parser (`y.tab.h`), regexps `FROMRE`/`REMFROMRE`, `skipequiv`, temp-file helpers, `String`.

## Risks / Notes
- Oversized messages are represented by `mp->size < 0` and rejected by caller.
- UTF-8 detection is any byte with high bit set, not full UTF-8 validation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/message.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/regtest.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/regtest.c

## Purpose
Interactive regexp test utility.

## Behavior
Prompts for a regexp, compiles it, then prompts for lines and prints `yes` or `no` depending on `regexec` result. Empty regexp input exits; empty line input returns to regexp prompt.

## Dependencies
Plan 9 regexp and `Biobuf`.

## Risks / Notes
No handling for `regcomp` failure before `regexec`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/regtest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/rewrite.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/rewrite.c

## Purpose
Rewrite-rule parser and matcher for `upas/send` address binding.

## Main Interfaces
- `getrules`: reads `UPASLIB/rewrite`.
- `rule_parse`: token parser with `\l` local-system substitution.
- `rewrite`: matches a destination and fills replacement fields/status.
- `dumprules`: debug dump of loaded rules.

## Behavior
Rules contain a regexp, action type (`|`, `>>`, `alias`, `translate`, `auth`), and one or two replacement expressions. Matching is case-insensitive by lowercasing the address, requires full-string match, lazily compiles regexps, and performs substitutions for capture groups, `&`, `\s` sender/reply address, and `\p` bulk/normal priority. Rules containing `\l` are duplicated for alternate system name.

## Dependencies
`regexp`, `String`, global `thissys`/`altthissys`, `message`, `dest`.

## Risks / Notes
Invalid regexp logs to `mail`; failed rule compilation silently skips that rule during matching.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/rewrite.c -->