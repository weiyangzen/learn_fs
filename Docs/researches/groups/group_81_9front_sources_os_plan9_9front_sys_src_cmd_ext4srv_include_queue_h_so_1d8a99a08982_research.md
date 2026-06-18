# Group Research: group_81_9front_sources_os_plan9_9front_sys_src_cmd_ext4srv_include_queue_h_so_1d8a99a08982

Scope: `Docs/research_subset_a.md`; all listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/queue.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/queue.h

## Purpose
Provides BSD-style intrusive collection macros for 9front's `ext4srv` support code.

## Key Elements
Defines `SLIST`, `STAILQ`, `LIST`, and `TAILQ` head/entry declarations plus initialization, insertion, removal, traversal, safe traversal, concatenation, swap, and predecessor/last access helpers. The implementation uses Plan 9 `nil` and `__containerof`-style pointer recovery for some reverse/last operations.

## Dependencies
No runtime dependencies; this is a macro-only header adapted from BSD queue macros. Debug/check/tracing hooks such as `QMD_TRACE_*`, `QMD_*_CHECK_*`, and `TRASHIT` are compiled as no-ops here.

## Behavior/Risks
Intrusive macros mutate caller-owned link fields and assume elements are already linked in the expected list. Singly linked arbitrary removals are linear. Since validation hooks are disabled, corrupted link state will usually fail later as pointer misuse rather than at the macro boundary.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/queue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/tree.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/tree.h

## Purpose
Provides BSD-style intrusive splay tree and red-black tree macro generators for `ext4srv`.

## Key Elements
Defines `SPLAY_HEAD`, `SPLAY_ENTRY`, splay rotations, generated insert/remove/find/next/min/max functions, and `SPLAY_FOREACH`. Defines `RB_HEAD`, `RB_ENTRY`, color/parent accessors, rotations, generated insert/remove/color-fix/find/nearest-find/next/prev/min/max functions, and forward/reverse traversal macros.

## Dependencies
Macro-only header using caller-provided comparison functions and embedded node fields. It expects Plan 9 `nil` and supports optional `RB_AUGMENT` callbacks for augmented tree metadata.

## Behavior/Risks
Generated code performs structural mutation during splay lookups and assumes comparator consistency. RB remove/color code requires valid parent/color fields; misuse can corrupt the tree silently. There is no locking or validation layer in this header.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/tree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/part.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/part.c

## Purpose
Adapts a Plan 9 block device or file into an lwext4 block device and manages mounted ext4 partitions.

## Key Elements
Implements block callbacks `bdopen`, `bdread`, `bdwrite`, and `bdclose`; probes device block size from the sibling `ctl` file; mounts, recovers, starts journaling, enables write-back caching, and loads group data from either options or `/etc/group` inside the ext4 filesystem. `openpart` deduplicates by `qid.path`, optionally formats the device with `ext4_mkfs`, and links the `Part` into a global list guarded by `QLock`.

## Dependencies
Uses Plan 9 `pread`, `pwrite`, `Dir`, `Qid`, `QLock`, and random generation, plus lwext4 APIs such as `ext4_mount`, `ext4_recover`, `ext4_journal_start`, `ext4_cache_flush`, and `ext4_mkfs`.

## Behavior/Risks
Read/write callbacks require full physical-block transfers. Error paths wrap `%r` messages but some cleanup relies on partially initialized `Part` state. `_closepart` appears suspicious because the previous-link update assigns `p->prev = p->next` instead of updating the previous node's `next` field, which can leave the global part list inconsistent.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/part.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/faces/dblook.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/faces/dblook.c

## Purpose
Small command-line helper to query the faces database for a user and domain.

## Key Elements
Requires exactly `name domain`, calls `findfile(&f, domain, name)`, and prints the selected face file path.

## Dependencies
Links against the faces database code and includes Plan 9 draw/plumb/regexp/bio headers because `faces.h` and shared objects require them.

## Behavior/Risks
No nil check after `findfile`; a missing face path prints through `%s` with a null pointer depending on Plan 9 formatting behavior. Provides a dummy `killall` to satisfy shared code paths that may report bad regexps.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/faces/dblook.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/faces/facedb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/faces/facedb.c

## Purpose
Finds, caches, and decodes 48x48 face images for mail senders.

## Key Elements
Caches text files by mtime/read time, translates domains through `.machinelist`, maps `domain/user` entries through `.dict`, recursively searches `/lib/face` and `$home/lib/face`, and falls back to `unknown`. It caches decoded `Facefile` images with reference counts, reads legacy hex face masks, Plan 9 image files, greyscale masks, and 8-bit images converted to 1-bit masks.

## Dependencies
Uses Plan 9 draw images, regexps, directory traversal, environment variables `facedom` and `home`, and the shared `Face`/`Facefile` structures.

## Behavior/Risks
The lookup cache intentionally tolerates stale reads for up to 30 seconds. Recursive directory search skips `512x*` and orders `48x48x8` down to `48x48x1`. `readfile` can leak a newly read buffer if allocating the cache node fails. Bad `.machinelist` regexps call `killall`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/faces/facedb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/faces/faces.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/faces/faces.h

## Purpose
Declares shared data structures and functions for the `faces` mail notification program.

## Key Elements
Defines face string slots (`Suser`, `Sdomain`, `Sshow`, `Sdigest`), `Facesize` as 48, `Face` runtime records, and cached `Facefile` image records. Exposes mailbox globals and cross-file functions for plumbing, lookup, rendering, deletion, allocation, and mailbox registration.

## Dependencies
Requires Plan 9 draw `Image`, time `Tm`, and the implementation files in `faces`.

## Behavior/Risks
The structures share ownership across UI and image-cache code: `Face.bit` usually aliases `Facefile.image`, and `freeface` must distinguish aliases from separately allocated fallback images.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/faces/faces.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/faces/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/faces/main.c

## Purpose
Implements the graphical `faces` mail monitor UI.

## Key Elements
Initializes draw state, fonts, arrow images, plumb ports, and mailbox list; displays sender face tiles with sender name, time/date, and unknown-domain label; handles scrolling, deletion, and opening mail; tracks recent timestamps; supports history mode, initial mailbox load, click-remove mode, and multiple maildirs.

## Dependencies
Uses Plan 9 draw/event/mouse device APIs, plumbing via `initplumb`/`nextface`, face lookup through `findbit`, and multiple rforked processes for main, time updates, and mouse handling.

## Behavior/Risks
Processes share memory with `RFMEM`, so display/list state is protected mainly by `lockdisplay`, not a broader data lock. UI geometry depends on fixed 48-pixel faces and font heights. `killall` posts notes to sibling processes on failure or exit.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/faces/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/faces/plumb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/faces/plumb.c

## Purpose
Connects `faces` to Plan 9 plumbing and converts mail notifications into `Face` records.

## Key Elements
Opens `send` and `seemail` ports, stores watched maildirs, sends `showmail` plumb messages, parses plumb attributes, normalizes sender names into user/domain, parses multiple mail date formats, receives new/delete/modify notifications, and can synthesize faces from upas/fs mailbox `info` files for initial loading.

## Dependencies
Uses libplumb, Plan 9 time parsing (`tmparse`, `tzload`), mailbox info file layout, and shared functions from `faces.h`.

## Behavior/Risks
Duplicate detection uses mail digest when present. `setname` lowercases the sender buffer in place and supports both `user@domain` and `domain!user`; simple unqualified senders may leave domain unset for default-domain lookup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/faces/plumb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/faces/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/faces/util.c

## Purpose
Provides checked allocation helpers for the `faces` program.

## Key Elements
Implements `emalloc`, `erealloc`, and `estrdup`, exiting on allocation failure and tagging allocations/reallocations with caller PCs.

## Dependencies
Uses Plan 9 libc allocation tagging and `exits`.

## Behavior/Risks
Allocation failure is fatal by design. `emalloc` zeroes memory, while `erealloc` does not initialize newly extended bytes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/faces/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/factor.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/factor.c

## Purpose
Prints prime factors for numbers supplied as arguments or stdin lines.

## Key Elements
Uses floating-point `double` arithmetic, divides out 2, 3, 5, and 7, then walks candidate factors using a wheel increment table. Prints the original number, each factor indented, and a blank line per input.

## Dependencies
Uses Plan 9 Bio for stdin and libc math functions `sqrt`, `modf`, and `atof`.

## Behavior/Risks
Precision is limited by `double`, so large integers can be misrepresented or factored incorrectly. Stdin mode stops on EOF or non-positive input.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/factor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/fax2modem.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/fax/fax2modem.c

## Purpose
Parses Class 2 fax modem status/result lines into `Modem` state.

## Key Elements
Initializes fax mode and phase, extracts comma-separated numeric parameters after `:`, handles `+FCON`, `+FTSI`, `+FDCS`, `+FCFR`, `+FPTS`, `+FET`, and `+FHNG`, and sets validity bits for captured fields.

## Dependencies
Uses the shared `Modem` structure and error/result constants from `modem.h`.

## Behavior/Risks
Parsing assumes modem responses match expected syntax. `ftsi` stores only the first remote ID seen. `fhng` returns `Rhangup` after recording termination status.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/fax2modem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/fax2receive.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/fax/fax2receive.c

## Purpose
Receives Class 2 fax pages from an already answered modem and writes them into the fax spool.

## Key Elements
Starts page reception with `AT+FDR`, waits for `CONNECT`, creates a page file, sends DC2, copies DLE-escaped page data until DLE/ETX, waits for final modem status, validates `FPTS`/`FET`/`FHNG`, retries failed pages, increments page/document counters, and logs document boundaries.

## Dependencies
Uses modem command/response helpers, `createfaxfile`, `faxrlog`, and `Modem` validity bits.

## Behavior/Risks
The receiver expects `+FCON` has already happened and calls `fcon` to move phase. Multi-document receipt is only partly handled; a comment notes there is no way to run the received hook for a new document, so it remains queued.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/fax2receive.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/fax2send.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/fax/fax2send.c

## Purpose
Sends one or more prepared fax page files over a Class 2 fax modem.

## Key Elements
Initializes fax mode, waits for dialing success, enables XON/XOFF flow control, opens each fax file, sends page geometry via `AT+FDT`, DLE-stuffs page data, handles rough flow control and abort characters, sends DLE/ETX, waits for `OK`, sends `AT+FET`, verifies `FPTS`, and cleans up with `AT+FK` on error.

## Dependencies
Uses `openfaxfile`, Bio input, modem I/O helpers, and `Modem` FDCS-derived geometry fields.

## Behavior/Risks
Flow control is deliberately rough and modem-specific. Error cleanup calls `Bterm(m->bp)` even along some paths where open state must be valid. The label name for error cleanup is informal but functionally just abort cleanup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/fax2send.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/file.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/fax/file.c

## Purpose
Creates received fax spool files and opens outgoing fax files in supported formats.

## Key Elements
Builds page IDs as `spool/time.pid.page`, writes Plan 9 picture-style headers for received CCITT G3 pages, detects Ghostscript fax output by its fixed header, and parses picture headers for `TYPE=ccitt-g31`, `WINDOW`, and `FDCS` metadata.

## Dependencies
Uses Bio input, Plan 9 file creation, and `Modem` fields for width, resolution, length, data format, sender ID, and validity bits.

## Behavior/Risks
Outgoing page validation requires a recognized type and width on the first page. The width table is fixed to five known fax widths. Some phone-number parsing code is disabled.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/modem.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/fax/modem.c

## Purpose
Implements low-level modem I/O and response parsing for the fax tools.

## Key Elements
Maps terse and verbose modem result codes to internal results, initializes modem descriptors, buffers raw input, polls available bytes through `dirfstat(fd)->length`, reads single characters and CRLF-terminated lines with timeouts, writes AT commands, parses responses including fax status callbacks, and toggles XON/XOFF through the connection control fd.

## Dependencies
Uses Plan 9 file descriptors, Bio buffering, syslog-style verbose hooks, and the fax-specific response handlers in `fax2modem.c`.

## Behavior/Risks
Input readiness depends on Plan 9 device length semantics. `response` ignores unknown lines until timeout and treats checksum-free modem text as trusted. The comment notes line lengths/newlines are not fully checked.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/modem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/modem.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/fax/modem.h

## Purpose
Declares the fax modem state structure, result/error codes, validity flags, and cross-module functions.

## Key Elements
`Modem` stores data/control fds, modem ID/type, response/error buffers, fax phase, remote ID, FDCS/FPTS/FET/FHNG status, page spool identity, input buffer, Bio page input, and current page geometry. Enumerations define response classes, public error codes, and valid-field bits.

## Dependencies
Requires Bio and the fax C modules that implement modem parsing, sending, receiving, file handling, and logging.

## Behavior/Risks
The header advertises `setflow`, `setspeed`, and `faxxlog`, but this file group only contains `xonoff`, `faxrlog`, and other helpers. Error strings are indexed by enum value in `subr.c`, so enum/table consistency matters.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/modem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/receive.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/fax/receive.c

## Purpose
Command entry point for receiving a fax from stdin/stdout modem descriptors and running the post-receive hook.

## Key Elements
Parses `-v` and `-s spool`, initializes a single `Modem` on fd 0, calls `faxreceive`, logs completion, and on success executes `/sys/lib/fax/receiverc` with document id, success flag, page count, and optional FTSI.

## Dependencies
Uses `faxreceive`, `faxrlog`, Plan 9 `exec`, and the `receiverc` rc script.

## Behavior/Risks
The default control fd is `-1`, so flow-control writes are not expected during receive entry. If the receive hook `exec` fails, the program exits with `"can't exec"` after a successful fax.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/receive.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/receiverc -->
# File Research: sources/os/plan9/9front/sys/src/cmd/fax/receiverc

## Purpose
Post-processing rc script for received faxes.

## Key Elements
Binds the fax queue from the file server, expects `time Y|N pages [ftsi]`, special-cases likely New York Times faxes based on sender, page count, day, and hour, copies those pages to `/n/fs/lib/nyt`, removes originals, otherwise mails recipients from `faxrecipients` with a command to view pages.

## Dependencies
Uses Plan 9 rc, `9fs`, `bind`, `date`, `sed`, `seq`, `cp`, `rm`, and `mail`.

## Behavior/Risks
Hard-coded local policy and paths dominate behavior. It removes `/srv/fs` and rebinds `/mail/faxqueue`, so it is site-specific and assumes the file server namespace is available.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/receiverc -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/send.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/fax/send.c

## Purpose
Command entry point for dialing and sending fax page files.

## Key Elements
Parses `-v`, requires a number and at least one page, dials the number through `telco` service `fax!9600`, initializes the `Modem`, invokes `faxsend`, prints/logs failure or success, and exits with an appropriate status.

## Dependencies
Uses Plan 9 networking `netmkaddr`/`dial`, syslog, and the fax send stack.

## Behavior/Risks
Dial failure exits with a retry-oriented message. Success/failure syslog formatting references the remaining `argv` after the number has been consumed, so logged page names depend on caller arguments.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/send.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/subr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/fax/subr.c

## Purpose
Provides logging and error-string helpers for the fax tools.

## Key Elements
Defines global verbose flag, syslog-backed `verbose`, fatal stderr `error`, enum-to-string `seterror`, and receive summary logging in `faxrlog`.

## Dependencies
Uses Plan 9 `syslog`, varargs formatting, and `Modem` error/status fields.

## Behavior/Risks
`seterror` assumes every error enum used has an entry in the static string table. `error` exits immediately and also prints to stdout when verbose is enabled.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fax/subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fcp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/fcp.c

## Purpose
Parallel file copy utility with optional metadata preservation.

## Key Elements
Accepts `-g`, `-u`, and `-x` metadata flags; validates destination directory usage; rejects directories and same-file copies; creates destination with source mode; spawns up to eight shared-memory worker processes; assigns offsets through a `QLock`-protected global counter; copies using `pread`/`pwrite`; and optionally wstats mtime, mode, uid, and gid.

## Dependencies
Uses Plan 9 `Dir`, `rfork(RFPROC|RFMEM)`, `wait`, notes, `iounit`, and `dirfwstat`.

## Behavior/Risks
Parallel writes assume the destination supports positional writes correctly. Worker allocation failure exits success-like via `_exits(nil)` after printing an error, so the parent may not treat that specific failure as copy failure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/file.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/file.c

## Purpose
Determines file types and optionally emits MIME types.

## Key Elements
Reads up to 6000 bytes, handles UTF BOM conversion, builds character and word histograms, runs a classifier cascade for fixed magics, offset magics, ELF/native executables, scripts, tar, strings, IFF/RIFF, unified diffs, email/mbox, compiler intermediates, source-language heuristics, Plan 9 fonts/images/subfonts, RTF/MS-DOS/icon/face/TGA/Ogg/MP4/MP3, entropy-like compressed/encrypted detection, and English/text fallbacks.

## Dependencies
Uses Plan 9 libc/Bio, libmach executable parsing (`crackhdr`, `objtype`), Rune/UTF support, and Plan 9 file metadata.

## Behavior/Risks
Classifier order is significant and heuristic fallbacks can misclassify short or ambiguous files. Some MIME strings are historical or nonstandard. Several routines mutate the read buffer temporarily while parsing headers or words.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/flambe.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/flambe.c

## Purpose
Interactive flame graph viewer for Plan 9 profile data.

## Key Elements
Loads symbols from an executable with libmach, reads profile records from `pr\x0f` data files, decodes big-endian record fields, draws proportional call graph bars, supports hover details, click-to-zoom, reset, quit, resize, and plumbing a selected program counter to an editor location.

## Dependencies
Uses Plan 9 draw/thread/mouse/keyboard/plumb APIs and libmach symbol/file-line support.

## Behavior/Risks
Assumes profile records are well-formed and recursively traversable by `down`/`right` indices. Drawing stores clickable rectangles per record and aborts on corrupt indices. The profile frequency header drives displayed seconds.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/flambe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fmt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/fmt.c

## Purpose
Formats text into wrapped paragraphs with optional indentation and join behavior.

## Key Elements
Parses `-i`, `-j`, `-l`/`-w`, reads stdin or files, tokenizes lines into `Word` nodes with indentation and beginning-of-line state, preserves paragraph breaks and indent changes, emits tabs/spaces for indentation, wraps at configured width, and inserts two spaces after sentence-ending punctuation unless it looks like a short uppercase abbreviation.

## Dependencies
Uses Plan 9 Bio and UTF length functions.

## Behavior/Risks
`-j` disables joining across original line starts. Blank whitespace-only lines use prior indentation state. Memory for queued words is freed as emitted, but line buffers from `Brdstr` are consumed by pointer adjustment and are not explicitly freed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fontsel.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/fontsel.c

## Purpose
Graphical font selector and preview tool.

## Key Elements
Scans `/lib/font/bit` and `/lib/font/ttf`, builds sorted font directories and face lists, previews default multilingual and code sample text or user-provided text, uses button menus to select font families/faces, uses `+`/`-` to change size or face index, redraws on resize, and prints the selected font path on exit.

## Dependencies
Uses Plan 9 draw/thread/mouse/keyboard menu APIs, bitmap fonts, and mounted TTF font paths under `/n/ttf`.

## Behavior/Risks
TTF handling assumes the external `/n/ttf/name.size/font` namespace exists. Text input is capped at 256 lines. Some key handling reuses `ifont` as TTF size through a union field.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fontsel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/forp/cvt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/forp/cvt.c

## Purpose
Converts parsed `forp` bit-vector expressions into SAT variables and clauses.

## Key Elements
Maps symbols and numeric constants to bit vectors, assigns lvalues, implements equality, bitwise logic, logical operators, complement, negation, addition/subtraction, comparisons, indexing, shifts, ternary, multiplication, absolute value, division/modulo constraints, `assume`, `obviously`, and SAT initialization with constants false/true.

## Dependencies
Uses Plan 9 `mpint`, libsat primitives, AST definitions from `dat.h`, parser nodes, and helper SAT logic combinators from `logic.c`.

## Behavior/Risks
Arithmetic is encoded at bit level with sign extension for signed values and an extra sign/zero bit for unsigned symbols. Division introduces quotient/remainder variables and constraints rather than computing directly. Unsupported operators call `error` or abort.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/forp/cvt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/forp/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/forp/dat.h

## Purpose
Defines the core data model for the `forp` formula prover.

## Key Elements
Declares source `Line`, compressed-trie symbol table nodes, `Symbol` records for bit vectors, AST `Node` records, symbol/AST/operator enums, signed-symbol flag, and fmt type checks for expression, AST, and operator formatting.

## Dependencies
Requires Plan 9 `mpint` for numeric literals and the other `forp` modules for construction/conversion.

## Behavior/Risks
`Symbol` embeds `TrieHead`, allowing trie leaves to be cast to symbols. Operator enum values are shared across parser, converter, and formatting tables and must stay synchronized.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/forp/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/forp/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/forp/fns.h

## Purpose
Declares cross-module functions for `forp`.

## Key Elements
Exposes allocation helpers, parsing, error reporting, AST construction, symbol lookup, expression conversion, assertion handling, solver driver, SAT assumptions, and Boolean/SAT logic constructors.

## Dependencies
Forward-declares `SATSolve` and depends on `dat.h` types being visible to users.

## Behavior/Risks
Varargs SAT helper prototypes rely on zero-terminated literal lists and the Plan 9 varargs conventions used in `logic.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/forp/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/forp/forp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/forp/forp.c

## Purpose
Main driver and result printer for the `forp` SAT-based formula prover.

## Key Elements
Prints model values for bit symbols, can dump SAT clauses for debugging, formats all model rows in `-m` mode, adds collected `obviously` negations as a disjunction, proves by unsatisfiability or prints a counterexample model, initializes formatters and subsystems, parses stdin or one file, and runs the solver.

## Dependencies
Uses global SAT state from `cvt.c`, symbol list from `misc.c`, parser/converter initialization, libsat solving APIs, and Plan 9 format installation.

## Behavior/Risks
If no `obviously` assertion is present, it exits with a message instead of solving. In normal mode, `satsolve(sat) == 0` is interpreted as proof; otherwise symbol values are printed with unknown bits as `?`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/forp/forp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/forp/logic.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/forp/logic.c

## Purpose
Builds compact SAT encodings for Boolean conjunction, disjunction, and arbitrary truth tables.

## Key Elements
Implements simplifying `satand1`, `sator1`, varargs wrappers, prime-implicant generation, implicant mask expansion, greedy cover selection, clause emission, and `satlogic1`/`satlogicv` for truth-table operators up to the supported arity.

## Dependencies
Uses global `satvar`, libsat `satadd1`/`sataddv`, and Plan 9 varargs adjustment via `satvafix`.

## Behavior/Risks
Constants are encoded as integer literals `1` and `2`, with negation used for complements. The truth-table minimizer uses dynamic global work arrays and a greedy cover, prioritizing compactness but not guaranteed minimum CNF.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/forp/logic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/forp/misc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/forp/misc.c

## Purpose
Provides allocation, symbol interning, AST construction, and formatting helpers for `forp`.

## Key Elements
Defines AST/operator name tables, checked allocation, fmtters for AST/operator names, an FNV-like string hash, compressed trie insertion/lookup for symbols, ordered symbol list maintenance, AST node construction by type, trie debug printing, and formatter registration.

## Dependencies
Uses Plan 9 formatting, memory tagging, `mpint`, and AST definitions from `dat.h`.

## Behavior/Risks
Hash collisions are resolved by incrementing the hash until an unused or matching symbol is found. Trie leaves are allocated as `Symbol` but traversed through `Trie` layout, making the shared prefix fields important.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/forp/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/forp/parse.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/forp/parse.c

## Purpose
Lexes and parses the `forp` input language into declarations, assumptions, proof goals, and expressions.

## Key Elements
Recognizes keywords `bit`, `signed`, `assume`, and `obviously`; parses numeric literals, symbols, comments, multi-character operators, precedence-based expressions, indexing/slices, ternary expressions, declarations with optional bit width, assumptions, proof goals, and expression statements. Installs token and expression formatters.

## Dependencies
Uses Bio input, Plan 9 `mpint`, symbol interning, AST construction, conversion, and assertion APIs.

## Behavior/Risks
Block-comment lexing scans until `*/` without explicit EOF diagnostics in the inner loop. Operators and keyword jump tables rely on sorted static tables. Undefined symbols and nonconstant indexes are rejected during parse/convert.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/forp/parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fortune.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/fortune.c

## Purpose
Prints a random fortune line, using or rebuilding an offset index for the default fortunes file.

## Key Elements
Opens a specified file or `/sys/games/lib/fortunes`; for the default file, uses `/sys/games/lib/fortunes.index` if current, otherwise creates/rebuilds it with 32-bit little-endian line offsets; selects a random indexed offset or uses reservoir sampling while scanning.

## Dependencies
Uses Plan 9 Bio, `Dir` mtimes, `truerand`, `ntruerand`, and `nrand`.

## Behavior/Risks
Index offsets are stored in four bytes, limiting practical indexed offsets. If another process is rewriting a too-short index, it falls back to scanning. Long fortune lines are truncated to the 2048-byte `choice` buffer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fortune.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fplot.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/fplot.c

## Purpose
Plots mathematical functions interactively or emits a Plan 9 RGB image.

## Key Elements
Lexes expressions over variable `x`, constants `pi`/`π`/`e`, arithmetic operators, and math functions; converts to reverse-polish code; computes stack depth; draws adaptively subdivided graph segments; computes axes/ticks/labels; supports color image output with `-c`, range `-r`, size `-s`, axis suppression `-a`, mouse zoom/unzoom/readout, and `y` auto-fit.

## Dependencies
Uses Plan 9 draw/event APIs and libc math functions, with floating-point exceptions for divide-by-zero/invalid masked.

## Behavior/Risks
Expression parser is compact and does not handle unary minus distinctly in token context beyond operator precedence. The `min` operator table entry points to `omax`, which appears to make `min` behave as max. Interactive readout finds nearest drawn pixel by scanning the full pixel map.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/fplot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/freq.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/freq.c

## Purpose
Counts byte or Rune frequencies in input files.

## Key Elements
Parses output-format flags for decimal, hex, octal, character, and Rune mode; defaults to decimal/hex/octal/character for byte mode; counts stdin or each file into a `Runemax+1` array; prints only nonzero counts.

## Dependencies
Uses Plan 9 Bio `Bgetc`/`Bgetrune` and Rune constants.

## Behavior/Risks
The count array is large enough for all Runes, so memory is fixed and substantial. In byte mode, non-byte Rune values are only possible through array capacity, not input. Read errors are reported after counting.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/freq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gdbfs/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gdbfs/dat.h

## Purpose
Declares shared state and callbacks for the `gdbfs` remote-debugging filesystem.

## Key Elements
Defines debug flag/prototype, minimum write packet size, target states, global `gdb` state with thread id, state lock, packet length, write fd, read Bio, and command channel. Declares initialization/shutdown plus memory/register/control request handlers.

## Dependencies
Requires Plan 9 thread `QLock`, Bio, and 9P `Req` types from including modules.

## Behavior/Risks
The single global `gdb` object means one remote target per filesystem instance. State transitions are guarded by the embedded `QLock`, while packet exchange is serialized through the command channel.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gdbfs/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gdbfs/gdb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gdbfs/gdb.c

## Purpose
Implements a client for the GDB remote serial protocol behind `gdbfs` 9P operations.

## Key Elements
Maps GDB register packets to Plan 9 `Ureg` layouts for ARM and AMD64, converts hex payloads, formats checksum packets, runs a dedicated packet I/O proc, negotiates `qSupported` packet size, handles memory read/write, register read, continue, stop, start-stop, wait-stop, detach/shutdown, checksums, acks, and target stopped/running state.

## Dependencies
Uses Plan 9 thread channels, Bio, 9P request helpers, libmach register metadata, and GDB remote commands `g`, `m`, `M`, `c`, `?`, `D`, and `qSupported`.

## Behavior/Risks
Register write is unimplemented. Packet I/O is mostly serialized, but interrupt writes are deliberately sent outside the main packet lock. Memory operations require target state `Stopped`. Unsupported machine register maps fail at runtime.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gdbfs/gdb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gdbfs/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gdbfs/main.c

## Purpose
Presents a GDB remote target as a Plan 9 `/proc`-style 9P filesystem.

## Key Elements
Builds files `ctl`, `fpregs`, `kregs`, `mem`, `regs`, `text`, and `status` under a process-named directory; supports reading memory/registers/text/status, writing memory/control, flushing blocking control requests, stat sizing for registers/text, command parsing for `stop`, `start`, `waitstop`, and `startstop`, and optional TCP dialing to a remote address.

## Dependencies
Uses Plan 9 lib9p, thread server APIs, libmach text or architecture selection, and the GDB protocol layer in `gdb.c`.

## Behavior/Risks
Requires either `-t text` or `-m arch`. `fpregs` and register writes are not implemented. Mounts before `/proc`, so it intentionally overlays process-like entries for debugger clients.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gdbfs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/blk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/blk.c

## Purpose
Implements GEFS block allocation, block I/O, allocation logs, deferred frees, epochs, and sync queues.

## Key Elements
Provides atomic block flags, finalization and hashing, full-block reads/writes, arena selection, free-range AVL insertion/removal/coalescing, allocation-log append/load/flush/compression, block allocation/deallocation, new/duplicate block creation, cache-backed `getblk`, reference hold/drop, block-fill measurement, limbo/deferred free handling, epoch start/end/wait/clean, dirty-block enqueue, priority sync queue heap operations, and the sync worker loop.

## Dependencies
Uses Plan 9 file I/O, atomics, `QLock`/`Rendez`, AVL trees, global `fs` state, GEFS block types and packing/hash helpers from `dat.h`/`fns.h`, and the cache layer in `cache.c`.

## Behavior/Risks
Allocation logging is central to crash recovery and must avoid recursion while appending log blocks. Deferred frees are epoch-protected so old readers can finish before reuse. Sync queue ordering by generation/op/address preserves write/free/fence ordering. Any checksum mismatch marks corruption; sync errors push the filesystem read-only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/blk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/cache.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/cache.c

## Purpose
Implements GEFS block cache hash lookup and LRU reuse.

## Key Elements
Maintains doubly linked LRU head/tail, moves unreferenced blocks to top or bottom, inserts blocks into hash buckets by address, removes cached entries, looks up and holds cached blocks, and plucks the least-recently-used unreferenced block for reuse after uncaching and clearing bookkeeping fields.

## Dependencies
Uses global `fs` cache state, GEFS block flags/refcounts, hash helper `ihash`, tracing/assertion helpers, and Plan 9 locking/rendezvous.

## Behavior/Risks
All cache hash and LRU mutations share `fs->lrulk`. Freed blocks are placed at the LRU bottom for earlier reuse. `cachepluck` sleeps until a reusable block exists and asserts the chosen block is unreferenced and not static.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gefs/cache.c -->