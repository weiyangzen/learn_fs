# Group Research: group_188_9front_sources_os_plan9_9front_sys_src_cmd_upas_bayes_regcomp_c_sour_fe5aa4945d62

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/regcomp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/regcomp.c

This is a local copy/adaptation of Plan 9 `libregexp`'s regular expression compiler for the upas Bayesian filter code. It compiles a regexp string into a `Reprog` instruction program made of `Reinst` nodes and `Reclass` character classes.

Key behavior:
- Implements a stack-based regexp parser with implicit concatenation and operator precedence for grouping, alternation, concatenation, `*`, `+`, and `?`.
- Lexes UTF runes, backslash quoting, anchors, `.`, and bracket classes.
- Character classes are parsed into sorted/merged rune spans; negated classes automatically include newline as excluded from matching.
- `regcomp1` allocates a generously sized `Reprog`, builds the instruction graph, appends `END`, detects unmatched parentheses, and compacts the allocation through `optimize`.
- Exports `regcomp`, `regcomplit`, and `regcompnl`; `regcompnl` makes `.` include newline.

Integration and risks:
- Relies on `regexp.h` for public structs and `regcomp.h` for internal instruction constants.
- Error handling calls external `regerror` and then `longjmp`s through `regkaboom`.
- The file comment notes the copied implementation “leaks extra classes when it runs out”; `newclass` allocates an extra 128-class block when the embedded `Reprog.class` pool is exhausted, but `optimize` only relocates classes tied into instructions. This is acceptable for the command’s short-lived compilation path but important for long-lived use.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/regcomp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/regcomp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/regcomp.h

This private header defines regexp compiler/executor constants and internal execution-list structs shared by the bayes regexp implementation.

Key contents:
- Defines `NSUBEXP` and `Resublist`, a fixed array of `Resub` match captures.
- Defines `Reinst.type` values: operands such as `RUNE`, `ANY`, `ANYNL`, `BOL`, `EOL`, `CCLASS`, `NCCLASS`, `END`, plus parser operators `START`, `LBRA`, `RBRA`, `OR`, `CAT`, `STAR`, `PLUS`, `QUEST`.
- Defines `Relist` and `Reljunk`, used by regexp execution routines outside this group for active NFA thread state.
- Declares internal helpers such as `_renewthread`, `_renewmatch`, and empty-thread variants.

Integration and risks:
- The numeric values encode both operator class and precedence, so changes must match compiler assumptions in `regcomp.c`.
- `LISTSIZE` and `BIGLISTSIZE` are fixed-size execution limits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/regcomp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/regen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/regen.c

This command generates DFA tables for the Bayesian tokenizer/classifier regexp set.

Key behavior:
- Defines three regexp classes: a `^From ` detector, keyword token regexp(s), and a large ignore-pattern regexp list for HTML/comment/mail-noise/base64/uuencoded/minor tokens.
- `strcpycase` rewrites lowercase ASCII outside character classes into case-insensitive bracket alternatives.
- `dregcomp` compiles regexps with `regcomp`, converts them to DFA programs via `dregcvt`, then frees the original `Reprog`.
- `buildre` builds the three DFA regexps, and `main` prints them with `Bprintdfa`.
- Provides `regerror` as `sysfatal`, making regexp compilation failures fatal.

Integration and risks:
- Includes `regexp.h` and `dfa.h`; it is a generator for data used by the bayes spam filter pipeline.
- Uses a fixed 16 KiB buffer for combined regexp alternations. The current patterns fit, but adding many patterns can overflow unless checked.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/regen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/regexp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/regexp.h

This public regexp header defines the data model exposed by the local bayes regexp compiler/runtime.

Key contents:
- Defines `Resub` as start/end pointers for byte strings or rune strings.
- Defines `Reclass` as up to 64 rune span endpoints.
- Defines `Reinst`, whose first union stores class/rune/subexpression/right-branch data and whose second union stores left branch or next instruction.
- Defines `Reprog` with a `startinst`, embedded class storage, and flexible first instruction array.
- Declares `regcomp`, `regcomplit`, `regcompnl`, `regerror`, `regexec`, `regsub`, rune variants, and substitution helpers.

Integration and risks:
- `Reinst` union layout is relied on by compiler relocation code and execution code.
- `Reprog.firstinst[5]` is used as a flexible trailing array in practice; callers must allocate larger blocks, as `regcomp.c` does.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/regexp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/aux.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/aux.c

This file provides small common mail utility helpers for unsafe-character handling, mailbox path behavior, and temporary-error detection.

Key behavior:
- `shellchars` detects carriage-return/newline characters in a C string.
- `escapespecial` percent-escapes shell-special characters using `%%HH`, replacing and freeing the input `String`.
- `unescapespecial` reverses those escapes when they decode to non-high-bit values.
- `hexchar` and `hex2uint` implement nibble conversion.
- `returnable` treats `/dev/null` as non-returnable.
- `temperror` checks the current error string for transient upas activity/problem messages.

Integration and risks:
- Uses Plan 9 `String` routines from `<String.h>` through `common.h`.
- Escape decoding has loose validation: bad hex returns large unsigned values and is handled as non-decodable high-bit-ish data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/aux.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/become.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/become.c

This file implements a minimal privilege-drop helper.

Key behavior:
- `become` currently only has special behavior for target user `"none"`.
- For `"none"`, it calls `procsetuser("none")`, then installs a new namespace with `newns("none", nil)`.
- On failure it sets an explanatory `%r` error string and returns `-1`.

Integration and risks:
- Called by process-launching helpers in `process.c`.
- Non-`none` users are accepted as no-ops, which is important for understanding privilege expectations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/become.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/common.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/common.h

This common header ties together Plan 9 mail constants, flag definitions, common helpers, folder operations, formatting hooks, and process helper types.

Key contents:
- Defines mailbox/path sizing constants and includes `sys.h` plus `<String.h>`.
- Defines mail flag bits `Fanswered`, `Fdeleted`, `Fdraft`, `Fflagged`, `Frecent`, `Fseen`, `Fstored`, and `Fields`.
- Declares flag helpers, auxiliary helpers, folder append/open helpers, RFC 2047 formatting install, and process/stream helpers.
- Defines `stream` and `process` abstractions around pipes, `Biobuf`s, child pids, and wait status.

Integration and risks:
- Shared by common tools, filterkit commands, and upas/fs support code.
- `Timefmt` is shared with folder append date handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/config.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/config.c

This file defines global path defaults for the upas mail system.

Key values:
- `MAILROOT` and `SPOOL` default to `/mail`.
- Logs default to `/sys/log`.
- Libraries default to `/mail/lib`.
- Binaries default to `/bin/upas`.
- Temporary mail files default to `/mail/tmp`.
- Shell path defaults to `/bin/rc`.

Integration and risks:
- These globals are declared in `sys.h` and consumed throughout common/filterkit/upas/fs code.
- They are mutable global pointers, so local builds or tests can override them if linked accordingly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/config.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/flags.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/flags.c

This file converts between compact textual mail flag strings and internal flag bits.

Key behavior:
- `flagtab` maps characters `a D d f r s S` to answered/deleted/draft/flagged/recent/seen/stored.
- `flagbuf` emits a fixed-width flag string, using `-` for unset flags.
- `buftoflags` parses a fixed-position buffer into bits.
- `txflags` applies a stream of flag operations with optional `+` or `-` prefixes and returns `"bad flag"` for unknown characters.

Integration and risks:
- Used by upas/fs info files, control writes, IMAP flag mapping, and helper utilities.
- `buftoflags` assumes the input has enough positions for all known flags.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/flags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/fmt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/fmt.c

This file installs an RFC 2047-ish formatter for non-ASCII header strings.

Key behavior:
- `rfc2047fmt` returns ASCII-only strings unchanged.
- If any byte is >= `0x80`, it emits `=?utf-8?q?...?=` encoding.
- Spaces become `_`; `_`, tab, `=`, `?`, and high-bit bytes become `=HH`.
- `mailfmtinstall` registers this formatter as `%U`.

Integration and risks:
- Used by upas tools that need safe mail header display/output.
- It treats input as bytes and labels as UTF-8; callers must provide UTF-8-compatible data for strict correctness.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/fmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/folder.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/folder.c

This file implements appending mail into either traditional mbox files or Plan 9 mail directories.

Key behavior:
- Tracks up to five open `Folder` records with type, lock, output fd, `Biobuf`, and timestamp.
- `openfolder` creates a directory if the target does not exist; directories use mdir-style files, non-directories use mbox append.
- `mboxopen` locks with `syslock`, opens/creates appendable mbox, seeks to end.
- `mdiropen` creates a unique `<time>.<seq>.tmp` file in a directory and `closefolder` renames it to `<time>.<seq>`.
- `appendfolder` reads an optional Unix `From ` line, writes one if missing, normalizes CRLF, escapes leading `From ` body lines, and flushes.
- `foldername` and `ffoldername` map user/mailbox/recipient strings to safe mailbox paths while refusing special files.
- `fappendfile` copies raw file data to a new target file.

Integration and risks:
- Must stay synced with send-side and imap4d mailbox safety checks per comments.
- Locks are described as traditional and partially best-effort; mdir writes rely on exclusive temporary file creation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/folder.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/libsys.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/libsys.c

This is the main Plan 9 system abstraction layer for upas mail commands.

Key behavior:
- Date/user/system/domain helpers: `thedate`, `getlog`, `sysname_read`, `alt_sysname_read`, `sysnames_read`, `domainname_read`.
- Lock helpers: per-directory `L.mbox` naming, `syslock`, `trylock`, `syslockrefresh`, `sysunlock`.
- File helpers: `sysopen`, `sysclose`, `sysmkdir`, `sysrename`, `sysexist`, create/open/unlock locked wrappers.
- Process/session helpers: `syskill`, `syskillpg`, `sysdetach`, pipe-write note handling through `pipesig`.
- Terminal helpers: console detection, hold-on/hold-off, `sysopentty`.
- Mailbox path and identity helpers: `mboxpathbuf`, `username`, `createfolder`, `creatembox`.

Integration and risks:
- Heavily shared by common mail tools and filterkit.
- Lock creation is intentionally tolerant: some lock errors are logged and then mail proceeds without a lock.
- `sysopen` mode string parsing is compact but non-obvious; callers depend on Plan 9 permission bits such as `DMAPPEND` and `DMEXCL`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/libsys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/process.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/process.c

This file wraps child process launch and pipe management.

Key behavior:
- `instream` creates a parent-write/child-read pipe with a `Biobuf`.
- `outstream` creates a child-write/parent-read pipe with a `Biobuf`.
- `stream_free` closes both child fd and buffered parent fd.
- `noshell_proc_start` forks, optionally detaches, wires standard fds from streams, closes extra fds, optionally calls `become`, and execs argv.
- `proc_start` runs a command through `/bin/rc -c`.
- `proc_wait` waits for the tracked pid and stores status.
- `proc_free` frees streams, waits if needed, and releases wait message.

Integration and risks:
- The child fd-closing loop uses `sysfiles()` from `libsys.c`.
- `proc_free` waits for live children, so callers must avoid deadlocks with unconsumed pipe output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/process.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/sys.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/sys.h

This header declares system-facing mail helper types, globals, and functions implemented mainly in `libsys.c` and `config.c`.

Key contents:
- Includes Plan 9 base, libc, and Bio headers.
- Defines `Mlock`, the lock-file handle containing fd, keeper pid, and lock name.
- Declares configurable global paths such as `MAILROOT`, `SPOOL`, `UPASLOG`, `UPASLIB`, `UPASBIN`, `UPASTMP`, `SHELL`.
- Declares file, lock, namespace, terminal, user, and mailbox creation helpers.
- Defines `Mboxmode = 0622`.

Integration and risks:
- Consumed by `common.h`; broad visibility makes these globals de facto configuration ABI for upas tools.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/common/sys.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/dkim/dkim.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/dkim/dkim.c

This command signs a mail message from stdin with a DKIM-Signature header written to stdout.

Key behavior:
- Signs selected headers: from, to, subject, date, message-id.
- Reads headers, strips existing `DKIM-Signature:`, canonicalizes lines with CRLF, and hashes selected headers.
- Reads body, suppressing extra trailing blank lines per simple canonicalization behavior.
- Computes SHA-256 body hash, constructs a DKIM header with `rsa-sha256` and `simple/simple`, hashes it with selected headers, and signs via factotum RPC.
- Writes DKIM header, original headers, blank line, then body.
- Options: `-d domain` required, `-s selector` optional default `dkim`.

Integration and risks:
- Uses factotum key spec `proto=rsa service=dkim role=sign hash=sha256 domain=...`.
- `usehdr` uses `realloc(*hs, strlen(*hs)+strlen(*p)+1)` then `strcat`, which leaves no separator and appears short by one if multiple header names are concatenated without accounting for previous NUL only; current behavior deserves caution.
- Header continuation handling signs continuations only while `use` remains set.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/dkim/dkim.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/dat.h

This small header defines a linked-list address type for filterkit commands.

Key contents:
- `Addr` contains `next` and string `val`.
- Declares `readaddrs(char*, Addr*)`, which appends parsed addresses from a file.

Integration and risks:
- Shared by `deliver`, `list`, `mbappend`, `mbcreate`, `mbremove`, `readaddrs`, and `token`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/deliver.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/deliver.c

This command appends stdin to a target mailbox for a recipient, using a from-address file.

Key behavior:
- Usage: `deliver recipient fromaddr-file mbox`.
- Extracts local recipient after last `!`.
- Reads first address from the from-address file via `readaddrs`.
- Appends stdin fd `0` to target mailbox with `fappendfolder`.
- Logs delivery result with recipient, from address, current date, original recipient argument, return code, and error string.

Integration and risks:
- Depends on common folder append semantics and locking.
- Exits with empty status even after logging `r`; failures are not directly propagated through a non-empty exit string.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/deliver.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/list.c

This command manages simple address allow/block lists backed by pattern files.

Key behavior:
- Usage: `list add|check patternfile [addressfile ...]`.
- Pattern file supports exact patterns prefixed by `=`, regex patterns prefixed by `~`, optional leading `!` for negative match, and `#include`.
- `simplify` lowercases addresses and generates an exact local match or a domain regex covering significant domain suffixes.
- `check` reads addresses, tests them against patterns, and exits nil on positive match, `!match` on only negative match, or `no match`.
- `add` appends simplified patterns for addresses not already matched and updates in-memory pattern state.
- Regexes are compiled on each check using Plan 9 regexp.

Integration and risks:
- Pattern parsing is line/token based and case-insensitive.
- `regerror` is stubbed to ignore regexp compilation errors, so bad regexes are silently skipped.
- Includes a hard-coded `.uk` domain depth special case.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/mbappend.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/mbappend.c

This command appends stdin or listed files to a mailbox/folder owned by the current user.

Key behavior:
- Usage: `mbappend [-t time] [-f from] mbox [file ...]`.
- Resolves the target with `foldername(from, getuser(), mb)`.
- Calls `fappendfolder` with provided timestamp and optional from string.
- Logs each append through syslog and exits `fail` on append error.
- With no files, appends stdin; otherwise opens each file and appends it.

Integration and risks:
- The first argument to `foldername` is named `from` in this command but is the `mb` base parameter in common folder code; that naming is confusing and should be traced carefully when modifying.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/mbappend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/mbcreate.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/mbcreate.c

This command creates mailboxes or folders for the current user.

Key behavior:
- Usage: `mbcreate [-f] ...`.
- Default operation calls `creatembox(getuser(), name)`.
- With `-f`, calls `createfolder(getuser(), name)`.
- Accumulates errors across all arguments and exits `errors` if any creation fails.

Integration and risks:
- Creation semantics and permissions are in `common/libsys.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/mbcreate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/mbremove.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/mbremove.c

This command removes or truncates user mailboxes/folders without using upas/fs.

Key behavior:
- Usage: `mbremove [-fpqrtv] ...`.
- Default removes mailboxes; `-f` removes folders.
- `-r` recurses, `-t` truncates instead of deleting, `-p` prints/dry-runs removal effects, `-v` prints removed paths, `-q` redirects stderr to `/dev/null`.
- `idiotcheck` only allows directories, lock files, index files when appropriate, message files, or mbox-looking files to be removed.
- Removes `.idx` and `.imp` sidecars, or only truncates `.idx` during truncation.

Integration and risks:
- Contains its own `dirskip` and mbox detection logic, parallel to upas/fs `remove.c`.
- `isindex` condition uses `if(strcmp(p, ".idx") || strcmp(p, ".imp")) return 1;`, meaning it returns true for almost every suffix except impossible simultaneous equality; this mirrors code in `fs/remove.c` and looks suspicious.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/mbremove.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/readaddrs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/readaddrs.c

This file parses address files into `Addr` linked lists.

Key behavior:
- `emalloc` and `estrdup` fatal on allocation failure.
- `tokenize822` splits on space/tab/newline but honors double-quoted strings.
- `readaddrs` appends parsed tokens from a file to the end of an existing `Addr` list.
- Reads at most 8191 bytes from the address file.

Integration and risks:
- The tokenizer mutates the buffer in place.
- Quoted-string handling is minimal and not a full RFC 822 parser.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/readaddrs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/token.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/token.c

This command creates or validates short time-window HMAC tokens.

Key behavior:
- Usage: `token key [tokenfile]`.
- With one arg, prints a 5-character base64 prefix of HMAC-SHA1 over a normalized current ctime string.
- The time string has the HH:MM:SS field replaced with colons, making tokens day-granular.
- With two args, reads a file and checks for tokens generated for today and the prior 13 days.
- Exits nil on match/create, `no match` otherwise.

Integration and risks:
- Token space is short by design; suitable only for low-stakes filtering workflows.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/token.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/cache.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/cache.c

This file manages message caching for `upas/fs`, including header/body fetching, LRU eviction, digesting, and index readiness.

Key behavior:
- Tracks cached byte counts per message and mailbox and maintains an LRU list of top-level messages.
- `cachefree` releases message body/header buffers, MIME metadata, references, and mailbox-specific decache hooks.
- `fetch` grows message buffers, calls mailbox backend `fetch`, squeezes embedded NUL and CR bytes, and handles Gmail size shifts.
- `cacheheaders` fetches enough data to parse headers, using partial fetch for large messages.
- `cachebody` fetches complete message content, adjusts size for stripped bad chars, computes SHA1 digest, counts lines, and parses MIME/body structure.
- `ensurecache` forces indexed cache state and digest/npart availability for serving and indexing.

Integration and risks:
- Central to all backends with `Mailbox.fetch`, especially IMAP and mdir.
- Uses `Maxmsg`, `cachetarg`, `Cidx/Cheader/Cbody` state flags from `dat.h`.
- Several paths assume pointer arithmetic is valid and assert heavily; malformed backend size data can trip fatal assertions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/dat.h

This header defines the central `upas/fs` mailbox/message data model, constants, backend vtable, qid layout, and shared prototypes.

Key contents:
- Defines cache state flags, content-transfer encodings, content dispositions, deletion states, limits, and mailbox remove flags.
- `Idx` stores indexed top-level message metadata such as digest, flags, fileid, headers, MIME info, size, raw body size, bad char count, and backend aux data.
- `Message` embeds `Idx` and adds cache pointers, MIME tree linkage, reference counts, deletion/in-mailbox state, Unix header fields, charset/boundary, and backend-specific union.
- `Mailbox` stores global mailbox state, root message, digest AVL tree, qids, backend callbacks, LRU cache data, and sync state.
- Declares backend initializers for plan9 mbox, POP3, IMAP4, and mdir.
- Defines qid file IDs for message pseudo-files and `PATH/FILE` macros.
- Declares hash-table lookup helpers and many cross-file functions.

Integration and risks:
- This is the ABI between `fs.c`, `mbox.c`, backends, index code, remove/rename, and MIME parsing.
- `PATH(id, f)` packs file type in low 10 bits; adding more `Q*` values must respect that.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/fd2path.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/fd2path.c

This test/helper command prints kernel paths for file descriptors.

Key behavior:
- Usage: `fd2path path ...`.
- With no args, prints `fd2path(0)`.
- With args, opens each path and prints the resolved path for the fd.

Integration and risks:
- Simple diagnostic for Plan 9 fd/path behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/fd2path.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/idxtst.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/idxtst.c

This helper tests exclusive index-file opening behavior.

Key behavior:
- `exopen` retries opening/truncating or creating `testingex` with exclusive/temp lock-style mode.
- Distinguishes expected lock/not-found/already-exists errors from fatal errors.
- After opening exclusively, attempts `Bopen` for reading and reports whether both opened.

Integration and risks:
- Diagnostic for Plan 9 lock semantics used by `idx.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/idxtst.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/infotst.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/infotst.c

This helper simulates clients reading `info` pseudo-files with varying read sizes.

Key behavior:
- Usage: `infotest n1 n2 ... nm`.
- Reads stdin repeatedly with the provided block sizes, cycling at the last size, and writes exactly what was read to stdout.
- Comments document verification workflows comparing `upas/fs` info file behavior across read patterns and old/new implementations.

Integration and risks:
- Pure test harness for client read pattern sensitivity.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/infotst.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/paw.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/paw.c

This small helper sums numeric fields from stdin.

Key behavior:
- Reads lines with Bio.
- Splits each line by spaces.
- If more than two fields are present, adds field 2 as an unsigned long to a `vlong` sum.
- Prints the final sum.

Integration and risks:
- Diagnostic utility; no direct integration with the mail FS runtime.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/paw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/prflags.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/prflags.c

This helper prints decoded flag strings from index-like input.

Key behavior:
- Reads stdin line by line.
- Tokenizes each line into `Fields` fields.
- Skips records with first field `-`.
- Parses field 1 as hex flags and prints the fixed-width `flagbuf` representation.

Integration and risks:
- Depends on `common.h` flag constants and `Fields`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/prflags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/strtotmtst.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/strtotmtst.c

This test command includes `strtotm.c` directly and prints parsed dates.

Key behavior:
- Installs time formatting.
- For each argument, calls `strtotm`.
- Prints normalized formatted time on success or `bad` on failure.

Integration and risks:
- Direct include means it tests the exact parser implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/strtotmtst.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/tokens.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/tokens.c

This file implements an IMAP-style tokenizer helper for mailbox token parsing tests.

Key behavior:
- `qtoken` handles single-quoted sections, doubled single quotes, and separators.
- `getmtokens` splits on whitespace, either collapsing multiple separators or treating one separator at a time depending on `multiflag`.

Integration and risks:
- Similar in spirit to tokenizer code in IMAP paths; likely used for testing parser edge cases.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/tokens.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/fs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/fs.c

This is the main `upas/fs` 9P file server. It exposes mailboxes and messages as a mounted file tree under `/mail/fs` or a supplied mount point.

Key behavior:
- Defines `Fid` state for active 9P fids, current qid, mailbox/message refs, open state, and directory-read finger optimization.
- `main` parses server flags, creates/mounts/posts the service, opens the default mailbox unless disabled, and forks the 9P server process.
- Implements 9P handlers for version/auth/attach/walk/open/create/read/write/clunk/remove/stat/wstat.
- Exposes top-level `ctl`, mailbox directories, message directories, and message pseudo-files such as `body`, `raw`, `rawbody`, `header`, `info`, flags, addresses, MIME fields, digest, and sizes.
- `rwrite` handles control commands: open/create/close mailbox, delete/flag/move messages, remove and rename mailboxes.
- Maintains a name/qid hash table for efficient walk lookup and a special `"xxx"` entry for message subfile lookup.
- `reader` periodically syncs mailboxes for plumbing/biff notifications.
- `readheader` filters ignored headers from `/mail/lib/ignore` and RFC2047-decodes output.

Integration and risks:
- Central coordinator for `dat.h`, cache/indexing, local/remote mailbox backends, MIME parsing, and Plan 9 9P.
- Uses global `synclock` to serialize 9P request handling and sync activity.
- `sanembmsg` contains a reference to `end` in a condition (`m->start > end`) that appears suspicious unless supplied by macro/environment; this code path should be treated carefully.
- Many reads force cache population and can trigger network fetches for IMAP/POP-backed mailboxes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/header.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/header.c

This file handles RFC 822 header length detection and RFC 2047 encoded-word decoding.

Key behavior:
- `hdrlen` returns a complete folded header line length, including continuation lines.
- `tokbegin` finds the start of an encoded word ending at a candidate position.
- `tok` decodes `=?charset?b?...?=` and `=?charset?q?...?=` tokens, converts through `xtoutf`, and appends to output.
- `rfc2047` scans a header line, decodes encoded words, optionally folds continuation whitespace, strips control chars as appropriate, and NUL-terminates output.
- Supports both base64 and quoted-printable encoded-word payloads.

Integration and risks:
- Used by `fs.c` when serving headers and by `mbox.c` while parsing headers.
- Output buffers are caller-provided; too-small encoded token conversion falls back to literal copying.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/header.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/idx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/idx.c

This file reads and writes `.idx` cache files for `upas/fs`.

Key behavior:
- Maintains interned strings for repeated MIME/type values.
- `wridxfile` writes a temporary exclusive index, prints magic/version/backend header, serializes all messages recursively, then renames to `<mailbox>.idx`.
- `pridxmsg` serializes digest, flags, fileid, lines, header fields, MIME metadata, sizes, bad-char count, backend aux, and child count.
- `rdidxfile` opens and validates index magic/backend metadata, compares qids, marks existing messages, and merges index entries into live message trees.
- `rdidx` handles recursive child messages, validates digest/fileid/size invariants, restores flags and cached metadata, and detects stale/dead entries.
- `genericidxread/write/invalid` provide default backend index metadata behavior.

Integration and risks:
- Uses digest AVL tree (`mtree`) to merge top-level indexed entries with live mailbox scans.
- Index writes can overwrite mutable information from concurrent upas/fs instances; comments call out this limitation.
- Exclusive open/rename behavior is Plan 9 specific and mirrored by test helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/idx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/imap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/imap.c

This file implements the IMAP4 client backend for `upas/fs`.

Key behavior:
- Supports `/imap/host[/user[/mailbox]]` and `/imaps/...` mailbox paths.
- Handles IMAP quoting (`%Z`), UID formatting (`%U`), tagged commands, response parsing, capabilities, status, fetch, expunge, and flags.
- Supports CRAM-MD5, NTLM, and password login via Plan 9 auth/factotum.
- Maintains `Fetchi` arrays of UID/size/date/flags state, detects new/deleted/modified messages, and maps server UIDs into message state.
- Fetches message body ranges with `uid fetch ... body.peek[]<offset.length>`, including a Gmail size workaround.
- Implements remote delete, move via `UID COPY` plus `\Deleted`/`EXPUNGE`, flag updates, mailbox rename, refresh/debug controls, and TLS-wrapped SSL connections.

Integration and risks:
- Provides `Mailbox.fetch/delete/move/sync/ctl/rename/modflags` callbacks.
- Uses `idxaux` to persist IMAP UID identity across index reloads.
- Parser is lowercase/mutating and intentionally compact; malformed or unexpected server responses often return `confused` and may abort a sync.
- No STARTTLS path here; SSL is via `/imaps/` and `wraptls`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/imap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/mbox.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/mbox.c

This file is the core mailbox/message manager and MIME parser for `upas/fs`.

Key behavior:
- `syncmbox` loads index state, calls backend sync, caches/plumbs new or modified messages, deletes removed messages, writes stale index state, and bumps mailbox versions.
- `newmbox` selects backend initializers in order: IMAP, POP3, mdir, Plan 9 mbox.
- Manages mailbox close/remove/rename, references, message allocation/freeing, and message tree deletion.
- Parses headers, dates, addresses, references, content type, transfer encoding, disposition, filename, charset, multipart boundaries, nested RFC822 messages, and MIME parts.
- Decodes base64 and quoted-printable bodies, converts charsets to UTF-8 via direct Latin-1 conversion or `/bin/tcs`.
- Sends plumb notifications for new/modified/deleted mail and optional biff output.
- Provides control helpers for deleting, flagging, and moving messages.

Integration and risks:
- Central user of `cache.c`, `idx.c`, `header.c`, `mtree.c`, and all mailbox backends.
- Address/header parsing is pragmatic rather than fully RFC-complete.
- `eprint` and `iprint` reuse a `va_list` twice after `vseprint`, which is undefined in standard C; Plan 9 compiler/runtime may tolerate this, but it is fragile.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/mbox.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/mdir.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/mdir.c

This file implements the directory-of-message-files backend for `upas/fs`.

Key behavior:
- Recognizes message files named as timestamp sequence IDs (`<seconds>.<seq>`).
- `mdirread` stats and reads directory entries, sorts by parsed fileid, merges new/deleted messages into mailbox state, and skips bad sizes/directories.
- `mdirfetch` reads byte ranges from the corresponding message file.
- `mdirdelete` removes the message file and marks it out of mailbox.
- `idxr/idxw` store directory qid/time metadata in index headers and accept fresh matching index state.
- `mdirmbox` initializes backend callbacks for directory mailboxes and can create directories with `DMcreate`.

Integration and risks:
- `dirskip` is exported and reused by removal code.
- Index freshness is accepted for up to four hours if qid metadata matches/newer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/mdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/mtree.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/mtree.c

This file maintains a digest-indexed AVL tree of top-level messages.

Key behavior:
- `mtreeinit` creates the AVL tree using SHA1 digest comparison.
- `mtreefind` looks up a message by digest.
- `mtreeadd` inserts a message and returns an existing duplicate if present.
- `mtreedelete` removes a message, with special handling for messages already marked deleted/dead.
- Uses pointer arithmetic through `messageof` because `Message` embeds the digest field at the same offset as `Mtree.digest`.

Integration and risks:
- Used for duplicate detection and index merge in `cache.c`/`idx.c`.
- Depends on `Message` layout embedding `Idx`/`Mtree`-compatible fields.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/mtree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/plan9.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/plan9.c

This file implements traditional Plan 9 flat mbox-file backend support.

Key behavior:
- Parses Unix `From ` separators, validates dates with `strtotm`, and reads messages from an mbox file.
- Supports incremental append reading when qid.path matches but qid.vers changes.
- Merges newly read messages with indexed/existing messages by digest, marks disappeared messages, and detects duplicates.
- `writembox` rewrites the mailbox through `<path>.tmp`, preserving mode when possible and omitting deleted messages.
- `plan9syncmbox` optionally locks, reads mailbox, purges deleted messages, rewrites if necessary, and unlocks.
- `plan9mbox` accepts existing mbox files or `.tmp` recovery files and initializes backend callbacks.

Integration and risks:
- Stores whole mbox messages in memory and marks `mallocd`.
- Uses lock refresh during long reads/writes.
- Parser comment notes a known bug for very long lines with `From ` at buffer boundaries.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/plan9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/pop3.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/pop3.c

This file implements the POP3/APOP backend for `upas/fs`.

Key behavior:
- Supports paths such as `/pop/`, `/pops/`, `/poptls/`, `/popnotls/`, `/apop/`, `/apops/`, `/apoptls/`, `/apopnotls/`.
- Dials POP3/POP3S, negotiates CAPA/STLS where applicable, detects PIPELINING and `EXPIRE 0`, and logs in via APOP or USER/PASS through factotum.
- Uses UIDL to match existing messages, detect deleted/disappeared messages, and create new placeholder messages.
- Downloads new messages with `LIST` and `RETR`, handles dot-stuffing, server size lies, and optional pipelining.
- Deletes marked remote messages using `DELE`.
- Provides mailbox controls for debug/nodebug and refresh interval.

Integration and risks:
- Persists UIDL in `idxaux`.
- `pop3hangup` sends QUIT even if prior protocol state is degraded.
- Message deletion on server is tied to local deleted+inmbox state during sync.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/pop3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/remove.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/remove.c

This file implements local mailbox/folder removal for `upas/fs`.

Key behavior:
- Reuses `dirskip` from mdir backend to recognize message files.
- `idiotcheck` permits removal of directories, lock files, index files when requested, message files, and mbox-looking files.
- `rm` recursively removes allowable children depending on `Rrecur`.
- `rmidx` removes `.idx` and, unless truncating, `.imp`.
- `localremove` deletes or truncates a mailbox path, removes sidecar indexes, and returns static error text on failure.

Integration and risks:
- Used as backend `Mailbox.remove` for local mdir and Plan 9 mbox.
- Shares suspicious `isindex` logic with filterkit `mbremove.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/remove.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/rename.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/rename.c

This file implements local mailbox rename/move operations, including cross-directory copy fallback.

Key behavior:
- Detects delivery mailboxes needing broader permissions.
- `rollup` creates missing parent directories with delivery-aware modes.
- Same-directory non-delivery or directory renames use `dirfwstat` name changes.
- Cross-directory operations copy files/directories recursively and then remove or truncate the source depending on `Rtrunc`.
- `localrename` wraps `rename` for a mailbox backend.

Integration and risks:
- Used by local mailbox backends and `mboxrename`.
- `copydir` uses `d->mode` inside a loop where `d` is the array base, likely intended as `d[i].mode`; that is a correctness risk for recursive directory copying.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/rename.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/strtotm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/strtotm.c

This file parses many mail date string formats into `Tm`.

Key behavior:
- Tries a list of `tmparse` patterns covering ctime-like dates, RFC-ish dates, dash-separated dates, and slash dates with optional weekdays/timezones.
- Returns `0` on first successful parse, `-1` if no format matches.

Integration and risks:
- Used by Plan 9 mbox parsing, MIME/header date logic, and the test helper.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/strtotm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/tls.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/tls.c

This file wraps a connected fd in TLS and validates server certificates for mail protocols.

Key behavior:
- Calls `tlsClient` with `serverName`.
- If global `nocertcheck` is set, logs that cert checking is ignored and returns the TLS fd.
- Otherwise loads thumbprints from `/sys/lib/tls/mail` and exclusion list `/sys/lib/tls/mail.exclude`.
- Validates the server cert with `okCertificate`; on failure closes TLS fd and returns `-1`.
- Frees TLS certificate/session resources.

Integration and risks:
- Used by IMAP and POP backends.
- Trust is thumbprint-file based rather than CA-chain based.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/fs/tls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/auth.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/auth.c

This file implements authentication and post-login setup for the IMAP4 daemon.

Key behavior:
- `enableforwarding` temporarily marks the remote peer as trusted in `/mail/ratify` for SMTP forwarding.
- `setupuser` switches/chowns to authenticated user, creates a namespace, optionally binds alternate upas binaries, changes to mailbox dir, and starts `upas/fs -np`.
- Supports CRAM-MD5 (`cramauth`), Plan 9 challenge-response (`crauth`), password-to-CRAM verification (`passauth`), and SASL PLAIN (`plainauth`).
- Handles base64 client responses and cancellation with `*`.

Integration and risks:
- Relies on globals from `imap4d.h` such as `bin`, `bout`, `username`, `remote`, `mboxdir`, `binupas`.
- Contains a hard-coded debug branch checking `argv0` for `8.out` and launching `/sys/src/cmd/upas/fs/8.out`; this is unusual production behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/copy.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/copy.c

This file implements IMAP COPY and APPEND save paths into local mailboxes.

Key behavior:
- `copycheck` verifies source messages are not expunged and have `rawunix` content.
- `opendeliver` forks `/bin/upas/mbappend` and returns a pipe to feed message data.
- `savemsg` streams a message into `mbappend`, computes SHA1 digest, then appends flags/UIDPLUS metadata to the target `.imp`.
- `copysave` and `copysaveu` copy existing message files and collect UIDPLUS results.
- `spool` reads APPEND literal data, normalizes CRLF to LF into a temporary file, and returns mapped size.
- `appendsave` prompts for literal data, spools it, then saves through `savemsg`.

Integration and risks:
- Uses mailbox lock (`mblock`) around `.imp` update, not around `mbappend`.
- Comments note this exists mainly to preserve flags and should ideally use upas/fs flags instead.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/copy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/csquery.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/csquery.c

This file queries Plan 9 connection server attributes.

Key behavior:
- `csquery(attr, val, rattr)` writes a query to `/net/cs`, then scans results for `rattr=`.
- Returns a newly duplicated value up to the next space.
- Returns nil for empty input, open/query failures, or missing attribute.

Integration and risks:
- Utility for IMAP daemon networking/address handling elsewhere in the daemon.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/csquery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/date.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/date.c

This file parses IMAP and mail date formats for the IMAP daemon.

Key behavior:
- `imap4date` parses `DD-Mon-YYYY` style IMAP dates.
- `imap4datetime` parses IMAP internal datetime variants and returns seconds or `~0` on failure/out-of-range.
- `date2tm` parses common RFC/mail date variants for FETCH envelope/internal date output.

Integration and risks:
- Shared by search/fetch/status code through declarations in `fns.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/date.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/debug.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/debug.c

This file centralizes IMAP daemon logging.

Key behavior:
- Defines `logfile` as `imap4d`.
- `debuglog` logs only when global `debug` is nonzero.
- `ilog` logs unconditionally.
- Both include username and process id in syslog messages.

Integration and risks:
- Depends on global `username` and `debug` from the daemon.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/fetch.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/fetch.c

This file implements IMAP FETCH response generation.

Key behavior:
- `fetchseen` marks messages seen for fetch operations that read bodies/text.
- `fetchmsg` validates requested fetch items, loads message structure as needed, and emits `FETCH` tuples for flags, UID, envelope, internal date, body/bodystructure, RFC822 variants, size, and body sections.
- `fetchsect` prints section selectors and resolves nested MIME message parts.
- `fetchbody` serves headers, MIME headers, raw body, text, whole body, partial ranges, and selected header fields; it maps LF to CRLF while streaming.
- `fetchbodypart` emits literal size and optional partial offset.
- `fetchenvelope`, `fetchbodystruct`, `Bmime`, `Bimapaddr` serialize IMAP envelope/bodystructure/address data.

Integration and risks:
- Uses parsed `Msg`, `Header`, MIME, and address structures from the IMAP daemon mailbox layer.
- Partial fetch over LF-to-CRLF conversion requires reading through the stop point because output position differs from file offset.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/fetch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/fns.h

This header declares the IMAP daemon’s cross-file function API.

Key contents:
- Prototypes for formatting, authentication, folder/file helpers, locks, mailbox open/close/list/create/remove/rename, `.imp` parsing/writing, message operations, fetch/search/store/copy/append, modified UTF-7, filesystem encoding, and AVL fstree helpers.
- Declares vararg checking for logging, command formatting, and custom format specifiers.
- Defines allocation convenience macros `MK` and `MKZ`, and `STRLEN`.

Integration and risks:
- This is the shared ABI across most `imap4d` C files.
- Prototypes show broader daemon capabilities beyond this group, including search/store/list/quota/parser support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/folder.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/folder.c

This file provides mailbox-directory helpers, global mail locking, and mailbox-name encoding/decoding helpers for the IMAP daemon.

Key behavior:
- Maintains cached current directory and wraps create/stat/wstat/open/remove operations after `mychdir`.
- `mblock`, `mbunlock`, `mblockrefresh`, and `mblocked` manage the shared `L.mbox` lock.
- `impname` creates the `.imp` sidecar name for a mailbox.
- `mboxname` decodes IMAP modified UTF-7, cleans the name, validates it, and encodes it for filesystem use.
- `strmutf7` and `mutf7str` convert between UTF-8 strings and IMAP modified UTF-7 using parse-bin allocation.

Integration and risks:
- Uses parse-bin allocation heavily; returned names are tied to parser allocation lifetime.
- `impname` calls `encfs` into a buffer but formats `%s.imp` from the original `name`, which appears inconsistent with intended encoded output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/folder.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/fsenc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/fsenc.c

This file maps IMAP mailbox names to filesystem-safe names and back.

Key behavior:
- Encodes tab as `#0`, space as `##`, and literal `#` as `#1`.
- Maps IMAP `INBOX` to filesystem `mbox`.
- `decfs` reverses escaping and maps filesystem `mbox` back to IMAP `INBOX`.
- Contains a disabled test `main` under comment.

Integration and risks:
- Used by folder/mailbox naming helpers.
- Only escapes a small ASCII set; other filesystem-invalid cases are handled by higher-level `okmbox`/cleaning logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/fsenc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/fstree.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/fstree.c

This file manages an AVL tree mapping upas/fs message directory IDs to IMAP daemon `Msg` objects.

Key behavior:
- `fstreecmp` compares messages by `Msg.id`.
- `fstreefind` looks up a message id in a `Box`’s `fstree`.
- `fstreeadd` inserts a new `Fstree` wrapper and asserts uniqueness.
- `fstreedelete` removes a message id and asserts that it exists.

Integration and risks:
- Used to find daemon message structures by upas/fs directory id.
- Strict assertions make tree consistency failures fatal.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/fstree.c -->