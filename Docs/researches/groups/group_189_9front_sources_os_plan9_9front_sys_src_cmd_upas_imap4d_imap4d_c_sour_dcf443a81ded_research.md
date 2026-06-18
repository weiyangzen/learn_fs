# Group Research: group_189_9front_sources_os_plan9_9front_sys_src_cmd_upas_imap4d_imap4d_c_sour_dcf443a81ded

Scope: `Docs/research_subset_a.md` source tree `sources/os/plan9/9front`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/imap4d.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/imap4d.c

Implements the top-level IMAP4rev1 daemon command loop, parser, and command handlers for 9front `upas/imap4d`. It is a protocol facade over `/mail/fs`, with mailbox state delegated to `mbox.c`, message rendering to fetch/search/store helpers, authentication to companion auth code, and mailbox naming/listing helpers.

Key responsibilities:
- Initializes `Biobuf` input/output, formatters, authentication flags, server/site identity, and optional preauthentication.
- Maintains IMAP session state tables for non-authenticated, authenticated, and selected mailbox states.
- Dispatches IMAP commands including `CAPABILITY`, `AUTHENTICATE`, `LOGIN`, `APPEND`, `SELECT`/`EXAMINE`, `LIST`/`LSUB`, `FETCH`, `STORE`, `SEARCH`, `COPY`, `EXPUNGE`, `UID`, `IDLE`, `NAMESPACE`, and quota commands.
- Parses IMAP atoms, quoted strings, literals, flags, fetch attributes, store attributes, search keys, sequence sets, dates, and UID sets using a `Bin` allocation arena so parse failures can discard per-command allocations.
- Tracks selected mailbox status, unsolicited `EXISTS`/`RECENT`/`FETCH FLAGS`/`EXPUNGE` updates, and an `IDLE` polling child process.
- Handles UIDPLUS responses for `APPENDUID` and `COPYUID`.

Important implementation details:
- `imap4()` uses `setjmp(parsejmp)` and `parseerr()` for parser recovery.
- `status(expungeable, uids)` carefully avoids sending illegal `EXPUNGE` responses during non-UID `FETCH`/`STORE`/`SEARCH`.
- `idlecmd()` forks an `RFMEM` child that periodically calls `check()` and flushes untagged updates while coordinated by `imaplock`.
- `appendcmd()` accepts optional flags and date, validates mailbox existence, synthesizes a Unix `From ` line, and calls `appendsave()`.
- `searchucmd()` handles `CHARSET`, emits `BADCHARSET` for unsupported charsets, and includes an Apple Mail optimization for immediately searching the last message by `Message-ID`.
- `uidcmd()` supports `UID COPY/FETCH/SEARCH/STORE/EXPUNGE`.
- Literal parsing sends `+ Ready for literal data` and reads exact byte counts from `bin`.

Filesystem relevance:
- Uses mailbox names resolved by `mboxname()` and upas mailbox directories rooted in global `mboxdir`.
- Relies on `checkbox()`, `openbox()`, `closebox()`, `deletemsg()`, `expungemsgs()`, `creatembox()`, `renamebox()`, and `removembox()` to mutate `/mail/fs` state.
- IMAP-visible UID/flag state is not native to `/mail/fs`; it is maintained through `.imp` files elsewhere.

Notable risks and quirks:
- Several comments mark partial or workaround behavior, especially `RENAME`, Apple Mail `Message-ID` search, and mailbox deletion of selected boxes.
- `deletecmd()` contains a suspicious expression `!removembox(mbox) == -1`, likely relying on unintended precedence/boolean behavior.
- Parser is strict ASCII for atoms/quoted strings and has custom handling for line-buffered input.
- `cleaner()` manipulates fds and process notes to stop the idle child and must be called under `imaplock`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/imap4d.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/imap4d.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/imap4d.h

Central header for `imap4d`. It defines mailbox/message state, IMAP parser node structures, flag/search/fetch/store enums, global variables, and imports `fns.h`.

Major data structures:
- `Box`: selected/open mailbox state, including mailbox name, `/mail/fs` handle, `.imp` path, writability, dirty flags, qids, mtimes, message counters, UID counters, linked messages, and `fstree`.
- `Msg`: message or MIME part node with parent/child links, upas/fs directory path, cached headers, IMAP flags, expunge state, UID/sequence/id, raw body size/line counts, info fields, and parsed addresses.
- `Header`: cached RFC822/MIME header buffer plus parsed MIME header fields.
- `Maddr` and `Mimehdr`: parsed address and MIME parameter lists.
- `Mblock`: lock wrapper for mail file operations.
- `Fetch`, `Store`, `Search`, `Msgset`, `Nlist`, `Slist`: per-command parse trees allocated from `parsebin`.
- `Uidplus`: UIDPLUS response chain for append/copy operations.

Important enums:
- IMAP message flags: `Fseen`, `Fanswered`, `Fflagged`, `Fdeleted`, `Fdraft`, `Frecent`.
- Upas/fs `info` fields: sender/recipient/date/subject/type/digest/message-id/size fields.
- Fetch operators: `Fenvelope`, `Fflags`, `Frfc822`, `Fbody`, `Fbodysect`, `Fbodypeek`, etc.
- Fetch body section parts: `FPall`, `FPhead`, `FPheadfields`, `FPmime`, `FPtext`.
- Store operators: `Stflags`, `Stflagssilent`.
- Search keys: full IMAP search key set used by parser and evaluator.
- Status items: `Smessages`, `Srecent`, `Suidnext`, `Suidvalidity`, `Sunseen`.

Filesystem relevance:
- Constants such as `Pathlen`, `Filelen`, and lock timing shape all mailbox/path handling.
- `Box` explicitly bridges IMAP metadata with `/mail/fs` mailbox qids and `.imp` state files.

Notable constraints:
- Header comments state mailbox/message structures are manually allocated and freed.
- Parser nodes are intentionally arena-allocated so a parse error can discard the whole command parse tree.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/imap4d.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/imp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/imp.c

Implements `.imp` file parsing and writing. `.imp` is the IMAP-specific sidecar format that maps upas/fs message digests to IMAP UIDs and flags.

Key responsibilities:
- Defines `.imp` magic string: `imap internal mailbox description\n`.
- Maps compact on-disk flag characters to IMAP flag bits.
- Parses existing `.imp` files, validates magic/version headers, and applies UID/flag state to currently visible messages by digest.
- Writes current non-expunged messages back to `.imp`.
- Appends or updates a `.imp` entry for copied/appended messages while returning UIDPLUS metadata.

Important functions:
- `parseflags()` converts fixed-width flag strings to bitmasks.
- `impflags()` applies flags, handles `\Recent` cleanup for IMAP-opened boxes, and marks changed flags for unsolicited updates.
- `verscmp()` validates the `.imp` header and advances `uidvalidity`/`uidnext`.
- `parseimp()` builds an AVL digest lookup over current messages, then applies `.imp` entries.
- `wrimp()` writes the complete `.imp` file.
- `appendimp()` opens or creates a mailbox `.imp`, detects duplicates by digest, appends or overwrites the matching entry, and fills `Uidplus`.

Filesystem relevance:
- `.imp` files live under `mboxdir` and are opened via `cdopen()`/`cdcreate()`.
- `.imp` state is keyed by message digest from upas/fs `info`.
- Uses qid/version checks in callers to decide whether `.imp` must be reparsed.

Notable risks and quirks:
- `sreason()` has an off-by-one style condition `r <= nelem(rtab)`.
- Duplicate digest handling logs anomalies and may skip conflicting UIDs.
- `appendimp()` sets `u->uid = box.uidnext` even for duplicate entries, while writing duplicate UID to disk; callers should interpret carefully.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/imp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/list.c

Implements IMAP `LIST`, `LSUB`, and subscription file operations.

Key responsibilities:
- Traverses user mailbox directories under `mboxdir`.
- Encodes/decodes filesystem mailbox names and IMAP modified UTF-7 display names.
- Matches IMAP wildcard patterns `*` and `%` against mailbox paths.
- Determines whether directory entries are selectable mailboxes, folders, or ignored files.
- Maintains `imap.subscribed`.

Important functions:
- `mopen()` and `mdirstat()` open/stat mailbox-relative paths with path traversal checks.
- `chkmbox()` classifies paths as mailbox files, mailbox directories, or nonselectable folders.
- `dirskip()` mirrors upas/fs mailbox-directory heuristics by recognizing message directories.
- `output()` emits IMAP list responses with `\Noselect`, `\Noinferiors`, and `\Marked`.
- `lmatch()` recursively matches live mailbox hierarchy.
- `listboxes()` handles normal `LIST`.
- `opensubscribed()`, `trim()`, `pmatch()`, and `lsubboxes()` handle subscription file matching.
- `subscribe()` appends or removes entries in `imap.subscribed`.

Filesystem relevance:
- Performs mailbox discovery directly from `mboxdir`, using encoded filesystem names via `encfs()`/`decfs()`.
- Uses mailbox mtimes and `.imp` mtimes to decide `\Marked`.
- Locks subscription updates with `mblock()`.

Notable risks and quirks:
- Comments explicitly say mailbox identification duplicates upas/fs logic and must stay in sync with `../fs/mdir.c`.
- `subscribe()` opens a truncating `tfd` but writes through `fd`, which is suspicious.
- Pattern matching mutates strings temporarily and is recursive; malformed paths are mostly rejected through `mokmbox()`/`okmbox()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/mbox.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/mbox.c

Implements mailbox open/check/close, message discovery, `.imp` synchronization, expunge, create/rename/remove operations, and mailbox name validation.

Key responsibilities:
- Talks to `/mail/fs/ctl` to open, create, rename, remove, close, and delete messages.
- Builds `Box` state from `/mail/fs/<handle>` directories.
- Detects new/deleted messages and marks pending expunges.
- Opens/creates/parses/writes `.imp` state under mailbox lock.
- Assigns UIDs and sequence numbers.
- Deletes messages marked `\Deleted`, then removes expunged `Msg` objects.

Important functions:
- `fsinit()` opens `/mail/fs/ctl`.
- `openbox()` opens a mailbox in upas/fs, reads message directories, opens `.imp`, sequences messages, and returns a `Box`.
- `readbox()` scans upas/fs message directories, creates `Msg` records, calls `msginfo()`, and updates `fstree`.
- `openimp()` locks and synchronizes `.imp` state, creating it when absent.
- `checkbox()` refreshes a box based on qid/mtime changes and optionally keeps the `.imp` lock open.
- `closeimp()` writes dirty `.imp` state.
- `closebox()` optionally deletes and expunges messages, closes the upas/fs handle, and frees all state.
- `deletemsg()` batches `/mail/fs/ctl` delete commands.
- `expungemsgs()` emits IMAP `EXPUNGE` and unlinks freed messages.
- `okmbox()` rejects reserved or dangerous mailbox names.
- `creatembox()`, `renamebox()`, `removembox()` call upas/fs control operations.

Filesystem relevance:
- This is the core filesystem bridge for IMAP. It models `/mail/fs` message directories and sidecar `.imp` files.
- Locks mailbox metadata with `mblock()` and uses qids/mtimes as change detectors.
- Maintains an AVL tree from upas/fs numeric message id to `Msg`.

Notable risks and quirks:
- Comments document the `.imp` file format and its locking assumptions.
- `readbox()` uses a `Gone` bit overlay in `expunged` to track unseen messages during refresh.
- `sequence()` sorts by UID, not filesystem order, and aborts if existing sequence numbers conflict.
- `renamebox()` notes the lock may be needed and relies on upas/fs moving `.imp`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/mbox.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/msg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/msg.c

Implements message loading, MIME/header parsing, RFC822 address parsing, body sizing, and memory cleanup for IMAP messages.

Key responsibilities:
- Lazily reads upas/fs `info`, `rawheader`, `mimeheader`, `rawbody`, and child part directories.
- Normalizes headers to CRLF and caches them with size/line counts.
- Parses MIME headers into `Mimehdr` chains.
- Parses RFC822 address headers into `Maddr` lists.
- Builds MIME/message child trees from upas/fs part directories.
- Computes raw body sizes adjusted for missing CR before LF, matching IMAP octet semantics.
- Selects header fields for partial body fetch/search.

Important functions:
- `msgreadfile()` reads a named file from a message directory.
- `msginfo()` parses fixed upas/fs `info` fields.
- `msgstruct()` constructs message/MIME tree and handles `message/rfc822` nesting.
- `msgbodysize()` counts raw body bytes and line count with CRLF correction.
- `msgheader()` reads and normalizes headers, then parses content and address fields.
- `selectfields()` emits selected header fields for `BODY[HEADER.FIELDS...]`.
- `headaddress()`, `headaddrspec()`, `headdomain()`, and related helpers implement a permissive RFC822-ish address parser.
- `freemsg()` recursively frees message state.

Filesystem relevance:
- Message files are opened relative to `m->fsdir` and `m->fs`.
- Subparts are modeled by appending path components under upas/fs message directories.
- `msgdead()` checks whether a message path still exists and marks it expunged.

Notable risks and quirks:
- Parser intentionally extends address syntax to handle `!` and local names.
- Several comments call out “BOTCH” around `message/rfc822` path manipulation and upas/fs behavior.
- Header parser tolerates 8-bit characters in atoms for UTF data.
- `mimelanguage()` loops while `headchar(0) != ','`, which can run through line ends via `headchar(1)` behavior; malformed headers rely on parser termination.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/msg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/mutf7.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/mutf7.c

Implements IMAP modified UTF-7 mailbox-name encoding and decoding.

Key responsibilities:
- Builds modified base64 tables using `,` instead of `/`.
- `encmutf7()` encodes non-ASCII/control runs as `&...-` and special-cases `&` as `&-`.
- `decmutf7()` decodes `&...-` runs back to UTF-8 Runes and validates trailing unused bits.

Filesystem relevance:
- Used by IMAP `LIST`/`LSUB` formatting and mailbox-name parsing to bridge client mailbox names and local filesystem names.

Notable constraints:
- Comment states it is not compatible with characters outside the Unicode basic plane.
- Decoder rejects literal control/non-ASCII bytes outside encoded sections.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/mutf7.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/nlisttst.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/nlisttst.c

Small standalone test harness for mailbox list matching code.

Key responsibilities:
- Includes `nlist.c` directly, supplies globals expected by the list implementation, and provides local `bye()`/`okmbox()` implementations.
- Runs `listboxes("list", ref, pat)` or `lsubboxes("lsub", ref, pat)` depending on `-l`.
- Prints the match count to stdout.

Filesystem relevance:
- Exercises the same mailbox name validation rules as `mbox.c`.
- Intended to test IMAP list pattern traversal over mailbox directories.

Notable quirks:
- Uses a Unicode arrow in output text.
- Duplicates the stoplist and `okmbox()` logic from production code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/nlisttst.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/nodes.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/nodes.c

Implements small parser-node constructors and message-set iteration helpers.

Key responsibilities:
- Tests sequence/UID membership with `inmsgset()`.
- Iterates message sets by UID or sequence using `formsgs()`, preserving mailbox order and avoiding duplicate operations from overlapping ranges.
- Builds `Store`, `Fetch`, and `Slist` nodes in the `parsebin` arena.
- Reverses fetch/string lists into protocol order.
- Prints numeric and string lists to `Biobuf`.

Important functions:
- `formsgsu()` iterates selected messages and matches UID ranges.
- `formsgsi()` iterates sequence ranges and reports missing sequence numbers as errors.
- `mkstore()`, `mkfetch()`, `mkslist()` allocate parser nodes.
- `revfetch()`, `revslist()` reverse linked lists.

Filesystem relevance:
- Supports IMAP operations over mailbox message lists from `Box`.
- Non-UID operations treat missing expunged sequence references as errors, while UID operations ignore missing messages per IMAP behavior.

Notable quirks:
- Comment notes short-circuiting UID iteration provides little value because expected mailbox sizes are only tens of thousands.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/nodes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/print.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/print.c

Defines custom formatters used by IMAP command handlers.

Key responsibilities:
- `Ffmt`: formats mailbox paths as quoted `/mail/box/<user>/...` paths unless already `/imap` or `/pop`.
- `Zfmt`: formats IMAP strings, choosing quoted strings, literals, `NIL`, or empty quoted strings; `%Y` additionally decodes fs names and encodes modified UTF-7.
- `Xfmt`: decodes modified UTF-7, cleans path names, and encodes filesystem names.
- `Dfmt`: formats RFC822-style dates or IMAP internal dates, using `%δ` as non-quoted date output.

Filesystem relevance:
- Central to safe mailbox-path display and conversion between IMAP mailbox names and filesystem encodings.

Notable constraints:
- Literal output is used for strings requiring non-ASCII/control handling unless alternate formatting rejects them.
- `%#Z` alternate avoids quoting if possible and logs bad literal cases.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/print.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/quota.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/quota.c

Implements quota usage reporting for IMAP quota commands.

Key responsibilities:
- Runs `/bin/du -s <mboxdir>` through a pipe.
- Parses the first tab-separated field as storage usage.
- Returns usage as a `vlong` byte/block value to `imap4d.c` quota handlers.

Filesystem relevance:
- Reports mailbox-directory disk usage for IMAP `GETQUOTA`/`GETQUOTAROOT`.
- Quota limit is hardcoded by the caller as `256*1024`.

Notable quirks:
- Uses a child process instead of direct tree traversal.
- `openpipe()` duplicates stdout to the pipe and logs exec failure through `ilog()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/search.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/search.c

Evaluates parsed IMAP search trees against `Msg` objects.

Key responsibilities:
- Performs case-insensitive substring searches over files, headers, addresses, and metadata.
- Determines whether a search requires only flags, `info`, or full message body/header structure.
- Evaluates flag, size, address, subject, date, UID/sequence set, header, body, text, `NOT`, and `OR` criteria.

Important functions:
- `filesearch()` scans a message file in overlapping buffers.
- `headersearch()` selects matching header fields and searches the value.
- `addrsearch()` formats parsed addresses and searches them.
- `datecmp()` compares parsed message dates against search dates.
- `searchld()` is intended to compute load depth, but currently always returns `0` at the end despite setting `r`.
- `msgidsearch()` optimizes `Message-ID` matching.
- `searchmsg()` evaluates all search keys.

Filesystem relevance:
- Opens message files such as `body` through `msgfile()`.
- Triggers `msginfo()` or `msgstruct()` depending on needed data.

Notable risks:
- `searchld()` appears buggy: it accumulates `r` but returns `0`, preventing intended lazy loading hints.
- Date searches assume relevant `info` date fields are present and parseable.
- Header/text search does not decode MIME encoded words, as noted by comment.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/search.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/store.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/store.c

Implements IMAP flag store/update behavior.

Key responsibilities:
- Maps IMAP system flags to internal bitmasks.
- Applies `STORE FLAGS`, `+FLAGS`, `-FLAGS`, and `.SILENT` variants.
- Prevents clients from modifying `\Recent`.
- Marks dirty `.imp` state and queues unsolicited flag updates when needed.
- Emits `FETCH FLAGS` updates.

Important functions:
- `storemsg()` applies a parsed `Store` operation to a message.
- `setflags()` updates message flags and mailbox recent count.
- `sendflags()` emits pending flag updates.
- `writeflags()` serializes flags.
- `msgseen()` marks messages seen when fetched.
- `mapflag()` maps parser flag names to bits.

Filesystem relevance:
- Any flag change marks `.imp` dirty; `closeimp()` later persists it.
- Does not directly mutate upas/fs message files except through `.imp`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/store.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/utils.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/utils.c

General utility functions for IMAP daemon support.

Key responsibilities:
- String helpers: `strrev()`, `isdotdot()`, `issuffix()`, `isprefix()`.
- `readfile()` reads an fd into the current `parsebin`.
- `imaptmp()` creates a lock-protected temporary file in the user mailbox directory.
- `openlocked()` repeatedly opens/creates locked files, recognizing Plan 9 filesystem lock error strings.
- `fqid()` extracts qids.
- `mapint()` case-insensitively maps names to integers.
- Memory helpers `emalloc()`, `ezmalloc()`, `erealloc()` exit via `bye()` on OOM.
- `setname()` rewrites `/proc/<pid>/args` for process display.

Filesystem relevance:
- Provides lock-aware file open behavior for mailbox metadata.
- `imaptmp()` targets `/mail/box/<username>/mbox.tmp.imp`.
- `setname()` changes process args to selected mailbox names.

Notable quirks:
- `readfile()` uses `parsebin`, so callers must ensure that arena lifetime is suitable.
- Lock retry error matching is string-based across multiple filesystem implementations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/marshal/marshal.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/marshal/marshal.c

Implements `upas/marshal`, the outbound mail message assembler and sendmail front-end.

Key responsibilities:
- Parses command-line recipients, CC/BCC, subject, content type, attachments/includes, PGP options, save-to folder, reply message path, and sendmail flags.
- Reads and normalizes user-supplied headers from stdin, optionally extracting recipients from RFC822 headers with `-8`.
- Expands user aliases from the `names` mailbox file.
- Adds missing headers such as `Date`, `From`, `To`, `Cc`, `Subject`, `In-Reply-To`, and `MIME-Version`.
- Detects body content transfer encoding as `US-ASCII`/`UTF-8` and builds multipart MIME output for attachments.
- Optionally filters the body through `/bin/pgp`.
- Starts sendmail, optionally tees the outgoing message into a local folder.
- Encodes non-ASCII header text with RFC2047 quoted-printable style.

Important functions:
- `main()` orchestrates parsing, header/body processing, attachments, PGP, and subprocess cleanup.
- `readheaders()` coalesces multiline headers, classifies known fields, removes Bcc, expands aliases, and handles `Attach:`/`Include:`.
- `body()` writes message body, ensuring leading newline and adding text content headers.
- `attachment()` copies MIME or emits MIME part headers and base64 encodes non-display attachments.
- `mkattach()` determines attachment type from explicit type, extension, `/sys/lib/mimetype`, or `/bin/file -m`.
- `sendmail()` forks `/bin/upas/send` or local hooks and optionally saves a copy.
- `pgpfilter()` interposes `/bin/pgp`.
- `readaliases()`, `expand()`, `expandline()` implement alias expansion and RFC822-ish address preservation.
- `doublequote()` and `rfc2047fmt()` are custom formatters.

Filesystem relevance:
- Reads user `headers` and `names` files from mailbox paths.
- Saves sent messages with `openfolder()`/`fappendfolder()` paths via common upas helpers.
- Uses attachment paths directly and can include message/rfc822 raw files.

Notable risks and quirks:
- `readheaders()` only recognizes likely headers in strict mode; uncommon headers at the top of a body may terminate header parsing.
- Attachment MIME type detection forks `/bin/file`.
- Alias expansion is recursive up to 32 iterations and de-duplicates by string equality.
- Error paths use `fatal()` to kill sendmail/PGP subprocesses and release any hold.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/marshal/marshal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/ml/common.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/ml/common.c

Shared support for simple mailing-list tools.

Key responsibilities:
- Extracts sender addresses from parsed RFC822 header nodes.
- Maintains an in-memory linked list of subscribed addresses.
- Reads append-only address-list files where removals are represented as `!addr`.
- Writes additions/removals to the address-list file and sends notification mail.
- Starts `/bin/upas/send` addressed to all list members.
- Sends subscription/removal notification messages.

Important functions:
- `getaddr()` returns the first parsed address node.
- `getaddrs()` sets globals `from` and `sender`.
- `writeaddr()` appends add/remove records and sends notifications.
- `readaddrs()` applies address-list history into current membership.
- `startmailer()` sets `upasname` to `<list>-bounces` and forks sendmail.
- `sendnotification()` sends owner-style subscription status mail.

Filesystem relevance:
- Address-list file is append-only and permission-adjusted with `DMAPPEND`.
- Mail delivery is delegated to `/bin/upas/send`.

Notable quirks:
- Removal entries do not rewrite the file; history is replayed.
- Notifications are skipped for addresses beginning with `#` on add.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/ml/common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/ml/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/ml/dat.h

Header for mailing-list utilities.

Key contents:
- Includes SMTP/RFC822 parser headers.
- Defines linked-list `Addr`.
- Declares shared globals: `from`, `sender`, `firstfield`, `naddrlist`, `addrlist`.
- Declares shared helper functions from `common.c`.

Filesystem relevance:
- Supports the list tools that read/write address-list files and invoke upas delivery.

Notable constraints:
- Depends on parser types `Field`, `Node`, and token constants from `../smtp/rfc822.tab.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/ml/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/ml/ml.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/ml/ml.c

Main remailer for a simple mailing list.

Key responsibilities:
- Reads a queued/delivered message from stdin, discarding the Unix `From ` line.
- Parses RFC822 headers to identify sender.
- Reads subscriber address-list file.
- Optionally enforces private-list membership.
- Rewrites headers: removes `Reply-To` and `Precedence`, prefixes subject with `[listname]`, adds list `Reply-To`, and sets `Precedence: bulk`.
- Starts a mailer to all list members.
- Archives the message to the list mailbox if the archive exists.

Important functions:
- `printsubject()` preserves existing subject while avoiding duplicate list prefix.
- `printmsg()` streams original message with selected headers filtered/replaced.
- `appendtoarchive()` appends to `listname/mbox` if present.
- `main()` coordinates parsing, membership check, sending, waiting, and archiving.

Filesystem relevance:
- Reads address-list file.
- Appends to list archive mailbox through folder helpers if it exists.
- Uses upas mailbox conventions for list-owned mailboxes.

Notable quirks:
- Reads up to 2 MiB of message content.
- Prevents remailing messages apparently from the list itself.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/ml/ml.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/ml/mlmgr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/ml/mlmgr.c

Mailing-list management command for creating lists and adding/removing members.

Key responsibilities:
- Creates list, owner, and bounces mailboxes for `-c`.
- Creates `pipeto` scripts for list delivery, owner commands, and bounce sink.
- Adds or removes addresses by appending records to the list address file.
- Handles optional domain in `listname@domain` for reply-to flag generation.

Important functions:
- `createpipeto()` writes executable rc scripts into each mailbox’s `pipeto`.
- `main()` enforces mutually exclusive `-c`, `-a`, and `-r`.

Filesystem relevance:
- Creates mailboxes with `creatembox()`.
- Writes mailbox `pipeto` files and address-list file under mailbox paths.
- Sets executable-ish mode on `pipeto`.

Notable quirks:
- Bounces mailbox `pipeto` script simply exits successfully.
- Writes marker comments to address-list file before management operations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/ml/mlmgr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/ml/mlowner.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/ml/mlowner.c

Owner-command processor for list subscription requests.

Key responsibilities:
- Reads a delivered message from stdin.
- Parses headers to identify `From` or `Sender`.
- Searches message text for subscription keywords.
- Appends remove or subscribe records to the address-list file.

Important behavior:
- If message contains `remove` or `unsubscribe`, calls `writeaddr(..., rem=1)`.
- Else if it contains `subscribe`, calls `writeaddr(..., rem=0)`.

Filesystem relevance:
- Mutates the append-only list address file through shared `writeaddr()`.

Notable constraints:
- Reads only first 128 KiB after the Unix `From ` line.
- Keyword matching is plain substring matching over the whole buffered message.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/ml/mlowner.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/ned/nedmail.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/ned/nedmail.c

Large interactive mail reader/client for upas mailboxes. It opens mailboxes through `/mail/fs`, builds a local message tree, supports command-address ranges/searches, displays MIME parts, mutates flags, deletes/saves/forwards/replies, and can invoke external commands.

Key responsibilities:
- Starts `/bin/upas/fs` if needed and opens a mailbox or singleton message.
- Builds `Message` trees from `/mail/fs/<mbox>` directories and nested MIME part directories.
- Maintains headers, info fields, flags, missing/deleted state, and display metadata.
- Parses interactive commands with message ranges, searches, and command arguments.
- Displays headers, raw messages, processed bodies, MIME trees, HTML via `htmlfmt`, and attachments through plumber.
- Marks messages seen, deleted, answered, stored, and flagged.
- Flushes deletions through `/mail/fs/ctl`.
- Saves messages/parts to folders or files.
- Replies/forwards by constructing `upas/marshal` invocations.
- Supports piping message parts to shell commands and running shell commands with `%` set to message path.

Important components:
- `Message` models top-level messages and MIME children.
- `Ctype` table maps MIME types to display/plumb behavior and file extensions.
- `cmdtab` defines commands such as `p`, `P`, `h`, `H`, `d`, `u`, `q`, `x`, `i`, `y`, `r`, `R`, `a`, `m`, `s`, `w`, `|`, `||`, `!`, `mb`, `k`, `K`, `F`.
- `switchmb()` opens or maps mailboxes and sets `root`, `mbname`, and working directory behavior.
- `dir2message()` synchronizes top-level message lists and detects new/deleted messages.
- `mdir2message()` loads MIME children.
- `parsecmd()` handles address/range/search parsing and command dispatch.
- `pcmd0()` chooses how to render MIME content.
- `flushdeleted()` batches delete commands to `/mail/fs/ctl`.
- `tomailer()`, `rcmd()`, `acmd()`, and `mcmd()` integrate with `upas/marshal`.

Filesystem relevance:
- Deeply tied to `/mail/fs`: message directories expose `info`, `raw`, `rawbody`, `body`, `header`, `flags`, `unixheader`, and other part files.
- Uses qid/path/version checks in `skipscan()` to avoid unnecessary rescans.
- Opens arbitrary mailbox paths by instructing `/mail/fs/ctl`.
- Saves using upas folder/file append helpers.
- Uses plumber paths rooted back to `/mail/fs/<mbox>`.

Notable risks and quirks:
- Many comments document legacy behavior and known botches around ordering, sorting, and mailbox opens.
- `itsallsapesfault()` contains suspicious digit comparison `c <= 9` rather than `c <= '9'`.
- Command parser is powerful but custom; address/search parsing mutates strings and uses global `sstring`.
- Running shell commands and plumb operations are intentional user-facing behaviors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/ned/nedmail.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/pop3/pop3.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/pop3/pop3.c

Implements a POP3 daemon backed by upas/fs.

Key responsibilities:
- Handles POP3 commands: `CAPA`, `USER`, `PASS`, `APOP`, `STLS`, `STAT`, `LIST`, `UIDL`, `RETR`, `TOP`, `DELE`, `RSET`, `NOOP`, `SYNC`, `QUIT`.
- Performs APOP challenge/response authentication and optional cleartext password login only after TLS or `-p`.
- Starts `/bin/upas/fs -np -f <box>` after login and reads `/mail/fs/mbox`.
- Builds an in-memory message table with upas message numbers, digest, octet counts, and deletion marks.
- Converts line endings to CRLF and dot-stuffs output.
- Deletes marked messages on `SYNC`/`QUIT` via `/mail/fs/ctl`.
- Supports TLS server mode with a configured certificate.

Important functions:
- `readmbox()` starts upas/fs, scans message dirs, reads `digest`, counts header/body lines, and computes POP octet sizes.
- `getcrnl()` reads protocol lines.
- `retrcmd()` and `topcmd()` stream raw messages with POP dot-stuffing.
- `stlscmd()` upgrades fd 0/1 with `tlsServer()`.
- `hello()`, `setuser()`, `dologin()`, `passcmd()`, `apopcmd()` implement authentication.
- `enableaddr()` writes a trusted peer address marker under `/mail/ratify/trusted`.

Filesystem relevance:
- Uses `/mail/fs/mbox` as POP mailbox view.
- Message deletion is a batched `delete mbox <ids>` command to `/mail/fs/ctl`.
- Mailbox path is `/mail/box/<user>/mbox`.

Notable risks and quirks:
- Anti-bruteforce behavior exits or delays on malformed/bad auth and logs likely guessers after repeated failures.
- `CAPA` advertises `STLS` unconditionally even if no cert is configured, though `STLS` then returns an error.
- `readmbox()` unmounts `/mail/fs` before starting its own instance.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/pop3/pop3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/q/qer.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/q/qer.c

Queues a mail delivery job into the upas queue directory.

Key responsibilities:
- Creates per-user queue directory under a queue root.
- Creates a temporary data file `D.XXXXXX` and writes stdin into it.
- Copies optional associated files supplied by `-f` into `F...` queue files.
- Creates a locked control file `C...` containing description, reply-to, argument list, and associated files.
- Supports `-q dir` for explicit queue subdirectory, with broader permissions when queueing as `none`.

Filesystem relevance:
- Queue job is represented by matching `C.*`, `D.*`, optional `F*` files.
- Uses `mktemp()`, `create()`, `syscreatelocked()`, and `sysunlockfile()`.
- Directory/file permissions vary based on user or queue-dir mode.

Notable quirks:
- Logs if the first data chunk does not begin with `From`.
- The read error on stdin is commented out and not fatal.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/q/qer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/q/runq.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/q/runq.c

Runs queued mail jobs from upas queue directories.

Key responsibilities:
- Scans one user queue or all queue subdirectories.
- Locks a queue directory with `./rundir`.
- Finds `C.*` control files, validates matching `D.*`, applies retry/give-up policy, and starts delivery subprocesses.
- Runs up to `-n` concurrent jobs.
- Keeps control-file locks alive while jobs run.
- Redirects queued data file to command stdin and appends stderr to `E.*`.
- Removes all matching queue files on success or permanent failure.
- Returns failed mail to sender unless retry is requested or return is disabled.

Important functions:
- `rundir()` scans a queue directory and manages live jobs.
- `dofile()` validates a queue entry, parses control args, checks retry windows, locks, forks, and execs the configured command.
- `donefile()` interprets child status and removes/retries/returns mail.
- `remmatch()` removes all queue files sharing the base suffix.
- `returnmail()` invokes upas marshal with the original data file as an attachment.
- `file()` maps `C.*` names to `D.*`/`E.*`.

Filesystem relevance:
- Queue state is entirely file-based: `C`, `D`, `E`, `F` prefix files in per-user dirs.
- Uses Plan 9 file locks and keeps them fresh with a child reading the fd.
- Cleans empty queue dirs and logs queue operations.

Notable risks and quirks:
- Control-file parsing is whitespace-oriented with minimal quoted-string handling.
- `badsys` suppresses repeated attempts to the same system during one run.
- Give-up defaults to 2 days unless `-R`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/q/runq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/qfrom/qfrom.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/qfrom/qfrom.c

Small filter that quotes Unix mbox `From ` separator lines.

Key responsibilities:
- Reads stdin or named files with `Biobuf`.
- For each line beginning with `From `, writes an extra leading space.
- Writes all content to stdout without changing character encoding.

Filesystem relevance:
- Useful when storing messages in mbox-like files where body lines beginning `From ` must not be interpreted as separators.

Notable constraints:
- Processes files sequentially and writes all output to stdout.
- Does not report per-file errors beyond `sysfatal()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/qfrom/qfrom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/scanmail/common.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/scanmail/common.c

Shared scanning/canonicalization and pattern-matching engine for mail/spam scanning.

Key responsibilities:
- Reads message content into memory up to configured limits, identifying header size and ensuring a minimum body sample.
- Canonicalizes headers/body to lowercase, normalized whitespace, stripped HTML tags, decoded quoted-printable-like escapes, and optional base64 body conversion.
- Parses pattern files into regex patterns and hashed string patterns grouped by action.
- Supports pattern actions: dump, hold header, hold, save line, line off.
- Supports alternate exclusion strings with `~~`.
- Matches canonicalized messages against regex/string patterns.
- Prints match context snippets.

Important functions:
- `readmsg()` reads message data and finds end-of-header with fractured-header safeguards.
- `endofhdr()` detects header/body boundary while guarding against lines like `To:`/`Cc:` after a blank.
- `htmlmatch()`, `escape()`, `htmlchk()` strip or preserve relevant HTML tokens.
- `conv64()` decodes base64 then calls `convert()`.
- `convert()` canonicalizes text and detects `Content-Transfer-Encoding: base64`.
- `parsepats()` reads pattern definitions.
- `parsealt()` handles alternate exclusions.
- `extract()` strips comments/quotes and lowercases patterns.
- `matchpat()` matches regex or hashed string patterns and honors alternates.
- `xprint()` emits context around a match.

Filesystem relevance:
- Not a filesystem implementation file, but part of upas mail pipeline operating on message streams and pattern files.

Notable risks and quirks:
- Uses static `ishtml` in `htmlchk()`, so HTML detection state persists across calls unless process flow resets externally.
- `xprint()` backs up with `p--` without explicit lower bound checks before later whitespace search.
- Contains a static base64 decode table tail in this file; related conversion helpers likely depend on declarations from `spam.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/scanmail/common.c -->