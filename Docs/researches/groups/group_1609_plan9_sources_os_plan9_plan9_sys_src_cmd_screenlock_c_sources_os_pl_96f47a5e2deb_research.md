# Group Research: group_1609_plan9_sources_os_plan9_plan9_sys_src_cmd_screenlock_c_sources_os_pl_96f47a5e2deb

Scope verified against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/plan9/plan9`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/screenlock.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/screenlock.c

Plan 9 terminal screen locker.

Key behavior:
- Reads the current user from `#c/user`.
- Opens `/dev/vgactl` or `#v/vgactl` to blank/unblank the display.
- Creates a covering window based on `/dev/screen`, initializes draw, paints `/lib/bunny.bit`, and shows the current user/time.
- Opens `/dev/mouse` and continuously recenters the pointer to prevent interaction.
- Reads password input from `/dev/cons` in raw mode via `/dev/consctl`.
- Authenticates with `auth_userpasswd(user, password)` and exits all threads on success.

Important details:
- `-d` disables mouse grabbing.
- A background blanker blanks after activity-triggered delay.
- Password buffer is zeroed after use.
- Cursor is hidden by writing a zeroed cursor image to `/dev/cursor`.

Filesystem relevance:
- Direct use of Plan 9 device files: `/dev/screen`, `/dev/mouse`, `/dev/cons`, `/dev/consctl`, `/dev/cursor`, `/dev/vgactl`, and `#c/user`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/screenlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scuzz/cdaudio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scuzz/cdaudio.c

SCSI/MMC CD audio command wrappers.

Key behavior:
- Implements pause/resume, stop, play, load/unload, audio status, and get-configuration requests.
- Builds raw SCSI command descriptor blocks and calls `SRrequest()`.
- `SRcdplay()` can play by raw LBA/length or by track number.
- Track-number play reads the TOC with `SRTOC()`, derives track LBAs and lengths, then issues play-by-LBA.

Important details:
- Uses 10-byte and 12-byte MMC command layouts.
- Stores a small static track table for TOC-derived playback.
- If TOC read fails with `STok`, it reports likely empty media through global `bout`.

Filesystem relevance:
- Indirect: operates on SCSI raw device handles opened elsewhere by `scsireq.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scuzz/cdaudio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scuzz/cdr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scuzz/cdr.c

SCSI/MMC CD-R and older CD writer command wrappers.

Key behavior:
- Implements blanking, sync cache, read TOC, read disc info, read track info.
- Implements older writer commands: first writable address, reserve track, track info, write track, media load, and fixation.
- Validates write and reservation sizes against `rp->lbsize` and `maxiosize`.
- Updates `rp->offset` after successful track writes.

Important details:
- Commands are constructed directly into local CDB byte arrays.
- Read-style commands fill caller-provided buffers.
- Write-style/control commands set `rp->data.write = 1` even when no payload is transferred.

Filesystem relevance:
- Indirect: provides media-writing operations over raw SCSI device files managed by the surrounding scuzz tool.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scuzz/cdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scuzz/changer.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scuzz/changer.c

SCSI medium-changer command wrappers.

Key behavior:
- `SReinitialise()` issues element status initialization.
- `SRmmove()` moves media from source to destination using a transport element, with optional invert bit.
- `SRestatus()` reads element status data for a given element type into a caller buffer.

Important details:
- Uses 6-byte and 12-byte changer CDBs.
- `SRestatus()` requests all elements by setting start element bytes to `0xFFFF`.

Filesystem relevance:
- Indirect: command helpers for changer devices opened through `/dev/sdXX/raw`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scuzz/changer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scuzz/scsireq.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scuzz/scsireq.c

Core SCSI request library for `scuzz`.

Key behavior:
- Builds common SCSI commands: test unit ready, rewind, request sense, format, read block limits, read/write, seek, filemark, space, inquiry, mode select/sense, start/stop, and read capacity.
- Chooses 6-byte versus 10-byte direct-access read/write and seek commands based on offset, transfer count, and `Frw10`.
- Handles sequential devices with fixed or variable block modes.
- Issues requests by writing a CDB to the raw device fd, transferring data, then reading a textual status.
- On check condition, automatically requests sense data and reports `Status_SD`.
- Opens `/dev/sdXX/raw`, performs inquiry, and initializes device-specific flags/block size for direct, sequential, printer, WORM, and changer devices.

Important details:
- Old Exabyte tape quirks are controlled by globals `exabyte` and `force6bytecmds`.
- Sequential reads handle ILI/filemark sense data as short records.
- Direct devices use read capacity to set `lbsize` and may force 10-byte commands for large block addresses.
- USB mass storage can route through `umsrequest()` when `Fusb` is set.

Filesystem relevance:
- Direct: this is the abstraction layer over Plan 9 raw SCSI device files such as `/dev/sdXX/raw`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scuzz/scsireq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scuzz/scsireq.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scuzz/scsireq.h

Shared SCSI request definitions.

Key contents:
- Defines `ScsiPtr` and `ScsiReq`, including unit path, lun, block size, offset, fd, command/data buffers, status, sense, inquiry, and flags.
- Defines software flags for device type/state, raw USB routing, 6-byte mode select, and 10-byte read/write.
- Defines SCSI status constants and internal status values.
- Defines sense-data bit masks and big-endian get/put macros.
- Declares all request helpers from `scsireq.c`, CD audio, CD-R, changer, and sense modules.

Important details:
- Header notes it is also included by USB disk and CDFS code.
- `Max24off` limits 24-bit command offsets.
- `maxiosize` is extern and shared with `scuzz.c`.

Filesystem relevance:
- Indirect but central to raw block/media device access in the scuzz subsystem.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scuzz/scsireq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scuzz/scuzz.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scuzz/scuzz.c

Interactive Plan 9 SCSI utility.

Key behavior:
- Parses command-line options for raw open, quiet mode, max transfer size, Exabyte quirks, and forced 6-byte commands.
- Opens an optional target device, then reads commands from stdin and dispatches them through a command table.
- Supports general SCSI operations, tape operations, direct read/write/seek/capacity, mode sense/select, CD-R/CD audio commands, changer commands, probe, open, close, and help.
- `read` and `write` can transfer to files or to shell pipelines prefixed with `|`.
- Dumps decoded inquiry, mode pages, TOC, disc info, track info, element status, and sense data.

Important details:
- Uses `Biobuf` for command input and output.
- Maintains a global `rwbuf` up to 240 KiB.
- `probe` scans likely `/dev/sd*` unit names and prints inquiry data.
- Parser supports quoted tokens with doubled single quotes.
- Some old writer commands are present but disabled in the command table.

Filesystem relevance:
- Direct: user-facing tool for Plan 9 `/dev/sdXX` raw SCSI devices, plus file and pipe I/O for device data transfer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scuzz/scuzz.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scuzz/sense.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/scuzz/sense.c

Sense-data formatter for scuzz.

Key behavior:
- Maps SCSI sense key values to human-readable descriptions.
- Uses `scsierror()` from libdisk to decode additional sense code and qualifier.
- Prints the sense key, optional detailed text, and raw sense bytes to global `bout`.

Important details:
- Prints `8 + sense[7]` bytes, matching fixed-format sense additional length.
- Relies on `/sys/lib/scsicodes` indirectly through libdisk.

Filesystem relevance:
- Indirect: diagnostic support for failures returned by raw SCSI device requests.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/scuzz/sense.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/seconds.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/seconds.c

Date parser that converts absolute date strings to seconds since epoch.

Key behavior:
- Accepts one or more date/time strings and prints unsigned seconds for each.
- Parses month names, day/month/year fields, time fields, AM/PM, named time zones, numeric time zones, and ignored weekday/filler words.
- Supports alternate delimiter handling for DEC-style dates.
- Converts parsed `Tm` through `tm2sec()` after validation.

Important details:
- Years must be representable in an unsigned 32-bit epoch range, effectively 1970 through 2106.
- Time zone token values are compressed in the token table by dividing minutes by 10.
- Numeric tokens are classified by position: first short number is day, later short number is year.
- Missing year/month/day invalidates the date.

Filesystem relevance:
- None directly; small time/date command.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/seconds.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sed.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sed.c

Plan 9 stream editor implementation.

Key behavior:
- Parses sed programs from `-e`, `-f`, or a positional script.
- Supports addresses by line number, `$`, regular expression, and last regular expression.
- Implements command compilation for append/change/insert, branch/test, delete, hold/get/exchange, next, print, quit, read, substitute, write, transliterate, labels, and grouped blocks.
- Executes commands over concatenated input streams with a pattern space and hold space.
- Uses Plan 9 rune regex APIs for Unicode-aware matching and substitution.

Important details:
- Program storage and buffers are fixed-size arrays.
- Labels are resolved after compilation by `dechain()`.
- Substitution supports `g`, `p`, `P`, and `w file`.
- Pending `a` and `r` commands are queued and emitted after the current cycle.
- `l` command escapes non-printing runes with `\xNNNN` style output.

Filesystem relevance:
- Direct file I/O for script files, input files, `r` command reads, and `w` command output files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sed.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/seq.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/seq.c

Numeric sequence generator.

Key behavior:
- Parses `seq [-fformat] [-w] [first [incr]] last`.
- Defaults to first `1.0`, increment `1.0`, and `%g\n`.
- `-f` supplies a printf-style format, adding a newline if absent.
- `-w` builds a constant-width decimal format and replaces leading spaces with zeroes.
- Handles positive and negative increments.

Important details:
- Rejects zero increment.
- Width inference refuses exponential `%g` forms.
- Uses double arithmetic for sequence values.

Filesystem relevance:
- None directly; stdout-only command.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/seq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sha1sum.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sha1sum.c

SHA digest command.

Key behavior:
- Computes SHA1 by default.
- `-2 bits` switches to SHA2-224, SHA2-256, SHA2-384, or SHA2-512.
- Reads stdin when no files are supplied; otherwise hashes each named file.
- Prints hex digest alone for stdin or digest plus filename for files.

Important details:
- Installs custom `%M` formatter for digest bytes.
- Uses libsec digest functions incrementally over 8192-byte reads.
- Continues past files that fail to open or read.

Filesystem relevance:
- Direct read-only file hashing utility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sha1sum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/size.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/size.c

Plan 9 executable size reporter.

Key behavior:
- Opens each supplied file and parses an executable header with `crackhdr()`.
- Prints text, data, bss, total, and filename.
- Defaults to `8.out` when no arguments are provided.
- Reports non-a.out inputs as errors.

Important details:
- Uses libmach `Fhdr`.
- Exits with `"error"` if any input fails.

Filesystem relevance:
- Direct read-only inspection of executable files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/size.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sleep.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sleep.c

Small sleep command.

Key behavior:
- Sleeps for integer seconds from `argv[1]`.
- Supports a fractional part up to milliseconds without using floating point.
- Exits successfully even with no argument.

Important details:
- Fraction parsing scales one, two, or at least three digits to milliseconds.
- Comment explains avoiding floating point so the command remains useful during machine bootstrap.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sleep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/snap/read.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/snap/read.c

Reader for serialized process snapshot files.

Key behavior:
- Validates the `process snapshot` header.
- Reads per-process sections into `Proc` records.
- Decodes `/proc` metadata sections, text segments, and memory segment lists.
- Reconstructs pages from raw data, zero markers, or references to previously read text/memory pages.
- Provides `findpage()` for locating a page by pid, type, and offset.

Important details:
- Snapshot numeric fields are fixed-width decimal strings.
- Page references can point to previous process text or memory pages.
- Bad references and malformed segment records call `panic()`.

Filesystem relevance:
- Indirect: reconstructs process filesystem snapshots previously captured from `/proc`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/snap/read.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/snap/snap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/snap/snap.c

CLI entry point for taking process snapshots.

Key behavior:
- Usage: `snap [-o snapfile] pid...`.
- Writes to stdout by default or `-o` output path.
- Emits a snapshot header with time, user, system, architecture, kernel root mtime, and terminal.
- Skips snapshotting itself.
- Calls `snap(pid, 1)` and `writesnap()` for each target process.

Important details:
- Uses `dirstat("#/")` to record kernel compilation/root metadata.
- Defaults unknown user/system/arch/terminal fields to placeholder strings.

Filesystem relevance:
- Direct: writes snapshot files and starts capture from Plan 9 `/proc`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/snap/snap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/snap/snap.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/snap/snap.h

Shared definitions for the `snap` tools.

Key contents:
- Defines process pseudo-file indexes: `segment`, `fd`, `fpregs`, `kregs`, `noteid`, `ns`, `proc`, `regs`, and `status`.
- Defines internal snapshot page size as 1024 bytes.
- Defines `Data`, `Seg`, `Page`, and `Proc`.
- Declares capture, read, write, page lookup, and allocation helpers.

Important details:
- `Page` records whether it has already been written and where it was first emitted, enabling deduplicated page references.
- `Proc` stores both memory segments and optional text image.

Filesystem relevance:
- Foundational data model for serializing and serving process filesystem snapshots.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/snap/snap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/snap/snapfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/snap/snapfs.c

9P filesystem server exposing a snapshot as a `/proc`-like tree.

Key behavior:
- Reads a snapshot file with `readsnap()`.
- Builds an in-memory 9P tree with one directory per pid.
- Creates files such as `ctl`, `text`, `mem`, and captured pseudo-files.
- Implements reads from `Data` blobs or memory/text pages via `findpage()`.
- Mounts by default before `/proc`, or after with `-a`, or at a custom mount point with `-m`.

Important details:
- `ctl` is created but has no custom write/control implementation here.
- `mem` and `text` reads are page-limited to one 1024-byte page segment.
- `-D` enables chatty 9P diagnostics and `-d` enables snapshot debug.

Filesystem relevance:
- Direct: serves snapshot data as a synthetic Plan 9 9P filesystem resembling `/proc`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/snap/snapfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/snap/take.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/snap/take.c

Process snapshot capture implementation.

Key behavior:
- Reads selected `/proc/<pid>` pseudo-files into `Data` blobs.
- Reads `/proc/<pid>/text` and memory segments from `/proc/<pid>/mem`.
- Parses `/proc/<pid>/segment` to discover segment names and address ranges.
- Splits text and memory into 1024-byte pages and deduplicates identical pages.
- Handles stack specially by using the saved register set to find the stack pointer and capture only live tail pages when possible.

Important details:
- Page deduplication uses a small checksum hash plus full byte comparison.
- All-zero pages are emitted as zero pages immediately.
- Uses libmach to decode the architecture-specific stack pointer from the register file.
- Warns but continues when individual `/proc` sections cannot be read.

Filesystem relevance:
- Direct: captures process state through Plan 9 `/proc` files and memory/text image files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/snap/take.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/snap/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/snap/util.c

Allocation helpers for snap.

Key behavior:
- `emalloc()` allocates and zeroes memory or exits.
- `erealloc()` reallocates or exits.
- `estrdup()` duplicates strings or exits.

Important details:
- Errors are fatal and print `out of memory`.

Filesystem relevance:
- None directly; shared utility support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/snap/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/snap/write.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/snap/write.c

Snapshot serialization writer.

Key behavior:
- Defines `pfile[]` names for process pseudo-file sections.
- Writes `Data` sections as pid/name header, fixed-width length, then raw bytes.
- Writes text and memory segments with offset, length, and page encodings.
- Emits each page as raw data (`r`), zero marker (`z`), or reference to an already written text/memory page.

Important details:
- Page references carry type, pid, and original offset.
- Validates page counts and short non-final pages with `abort()`.
- Marks pages as written as they are first emitted to enable deduplication.

Filesystem relevance:
- Direct serialization of `/proc`-derived data for later replay through `snapfs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/snap/write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sort.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/sort.c

Plan 9 sort implementation with external merge support.

Key behavior:
- Parses classic and POSIX-style sort options, including fields, `-k`, `-t`, `-o`, `-T`, `-c`, `-u`, `-bdfgiMnrw`, and debug `-v`.
- Reads input lines from files or stdin, ensuring final newline if needed.
- Builds binary sort keys per line based on global and field-specific options.
- Sorts in memory with radix sort for larger sets and insertion/bubble cleanup for small partitions.
- Spills sorted runs to temporary files when line count exceeds `-l`/default limit, then merges runs.
- Supports order checking with `-c` and unique output with `-u`.

Important details:
- Temporary files are named `sort.<pid>.<n>` under `/tmp` or `-T`.
- At most 10 temporary runs are merged at once; additional merge passes create more temp files.
- Numeric key generation normalizes sign, decimal point position, exponent, and reverse order into byte-sortable keys.
- Month sorting maps three-letter month names.
- `kcmp()` compares only the common key length, reflecting key encodings with terminators.

Filesystem relevance:
- Direct: reads input files, writes optional output file, and uses temporary files for external sorting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/sort.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spell/code.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spell/code.h

Affix-code bit definitions for Plan 9 spell.

Key contents:
- Defines bit masks for suffix/prefix classes such as `ED`, `ADJ`, `NOUN`, `ACTOR`, `ION`, `N_AFFIX`, `V_AFFIX`, `MAN`, `ADV`, `STOP`, `NOPREF`, `MONO`, `IN`, and `_Y`.
- Defines combined masks such as `COMP`, `VERB`, and `ALL`.

Important details:
- Used by both dictionary encoder `pcode.c` and runtime analyzer `sprog.c`.
- `ALL` excludes stop/no-prefix/do-not-touch/mono/in flags.

Filesystem relevance:
- None directly; spell dictionary metadata.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spell/code.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spell/pcode.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spell/pcode.c

Compiler for annotated spelling lists into compact binary dictionaries.

Key behavior:
- Reads lines of `word<TAB>affixcode[,affixcode...]`.
- Maps named affix codes to bit masks from `code.h`.
- Interns distinct bit-mask combinations in `encodes[]`.
- Sorts words alphabetically.
- Emits a big-endian binary dictionary: number of code masks, code masks, then prefix-compressed word entries.

Important details:
- Fixed arrays allow up to 200000 words, 500000 bytes of word storage, and 4094 distinct encodings.
- Word entries store affix-code index plus count of common prefix bytes with the previous word.
- Reports word/space/code counts and output byte count on stderr.

Filesystem relevance:
- Direct dictionary file generator; reads source word lists and writes binary dictionary to stdout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spell/pcode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spell/sprog.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spell/sprog.c

Runtime spelling checker and affix analyzer.

Key behavior:
- Loads compressed dictionaries from `/sys/lib/amspell`, `/sys/lib/brspell`, or `-f file`.
- Reads words from stdin and prints words not accepted by the dictionary/affix rules.
- Supports British spelling mode, OCR/correction classification modes, verbose derivation output, x/debug lookup output, and Acme-style id prefixes.
- Tests dictionary words directly, then recursively strips prefixes and suffixes according to large prefix/suffix tables.
- Uses affix bit masks to decide whether a base word can accept a transformation.

Important details:
- Dictionary lookup uses a two-character index table into decompressed word storage.
- Suffix tables are stored reversed, matching from the word end.
- Derivation messages are accumulated for verbose output.
- `ise()` Britishizes relevant suffix rules by replacing `z` with `s`.
- Ordinal numbers such as `21st` and `12th` are accepted specially.

Filesystem relevance:
- Direct: reads binary spelling dictionary files from `/sys/lib` or a caller-supplied path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spell/sprog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/dstep.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/dstep.c

SPIN deterministic-step code generator.

Key behavior:
- Generates verifier C code for Promela `d_step` sequences.
- Collects and emits guard tests for deterministic selections.
- Rejects constructs illegal inside `d_step`, including nested `d_step`, nested atomic, process termination, `run`, and remote references.
- Tracks generated labels and goto targets inside d_step sequences.
- Emits save/restore-related verifier code and reached-state bookkeeping.

Important details:
- Maintains arrays of source labels and destination labels with a `MAXDSTEP` cap.
- Detects gotos that break out of a `d_step`.
- Special-cases break destinations and selection options.
- Uses global flags such as `GenCode`, `IsGuard`, `TestOnly`, and `NextLab`.

Filesystem relevance:
- None directly; vendored SPIN model-checker code generation logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/dstep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/flow.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/flow.c

SPIN control-flow graph construction.

Key behavior:
- Opens/closes statement sequences and assigns local/global sequence numbers.
- Builds `Element` nodes for ordinary statements, `if`, `do`, `unless`, atomic, non-atomic, and `d_step` sequences.
- Rewrites labels and tracks label scopes, inline ids, and remote label references.
- Validates that jumps do not enter or leave `d_step` improperly.
- Attaches `unless` escape sequences to normal execution paths.
- Constructs `for` and `select` loop forms by lowering them to assignments, guards, receives/sends, and `do` loops.
- Marks atomic/d_step sequences and warns about nested or invalid constructs.

Important details:
- `loose_ends()` patches nested sequence exits after parsing.
- `if_seq()` moves `else` branches to the end and warns on dubious `else` with channel I/O.
- Labels on gotos may be moved to inserted skip nodes to preserve jump targets.
- `dumplabels()` reports label-to-sequence mappings.

Filesystem relevance:
- None directly; internal graph builder for the SPIN tool.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/flow.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/guided.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/guided.c

SPIN guided simulation trail replay.

Key behavior:
- Locates a trail file using explicit `-k` name or fallback names based on the model filename.
- Warns if the source model is newer than the trail file.
- Replays trail records as process/transition steps against the parsed model.
- Handles cycle markers, claim starts, merge markers, process termination, and depth cutoff.
- Evaluates normal and `d_step` transitions while printing requested verbose/global/local state output.

Important details:
- Supports xspin and columnated output modes.
- Can skip never-claim steps when configured.
- `lost_trail()` prints remaining trail data when replay desynchronizes.
- `pc_value()` returns the current sequence number for a process id expression.

Filesystem relevance:
- Direct only for reading `.trail`/`.tra` files and checking source/trail mtimes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/guided.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/main.c

Main entry point and option driver for SPIN.

Key behavior:
- Parses SPIN options for verifier generation, simulation modes, LTL translation, preprocessing, trail replay, verbosity, slicing/dataflow, separate compilation, and xspin integration.
- Runs the C preprocessor into `pan.pre`, optionally creating temporary never-claim files.
- Initializes reserved symbols, parses the Promela model, parses generated LTL claims if needed, resolves loose ends, analyzes channel access, and schedules simulation or verifier generation.
- Handles LTL formulas from command-line or file and writes temporary never-claim sources.
- Provides fatal/nonfatal diagnostics, memory allocation, AST node construction, remote label/variable expressions, and token explanations.

Important details:
- Default preprocessor varies by platform, with override via `-P`.
- Cleans up generated `pan.*` files on fatal errors.
- `nn()` creates `Lextok` AST nodes and records file/line/source context.
- Tracks never-claim restrictions and warns on side effects or forbidden operations.
- `-Z` preprocess-only and `-I` inline-only exit before normal execution.

Filesystem relevance:
- Direct: creates/removes `pan.pre`, `_spin_nvr.tmp`, `*.nvr`, and generated `pan.*` files; reads model, LTL, and never-claim input files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/main.c -->