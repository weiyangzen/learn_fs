# Group Research: group_1518_plan9_sources_os_plan9_plan9_sys_src_cmd_disk_rd9660_c_sources_os_p_69e52cf19fc7

Scope verified against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/plan9/plan9`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/rd9660.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/rd9660.c

Debug utility for inspecting ISO 9660 CD images.

Key behavior:
- Opens an image file, reads 2048-byte sectors, and dumps volume descriptors at sectors 16 and 17.
- Sector 16 is decoded as primary ASCII ISO 9660; sector 17 is decoded as Joliet/Unicode by switching the `%T` formatter.
- Defines local ISO structures for volume descriptors, directory records, and path-table records.
- Installs custom formatters for endian-aware numbers, dual-endian ISO numeric fields, directory records, path entries, and trimmed text fields.
- Prints a short root-directory preview and both little-endian and big-endian path tables.

Filesystem relevance:
- Read-only diagnostic parser for ISO 9660 metadata; no mounting or mutation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/rd9660.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/chat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/chat.c

Small diagnostics module for `dossrv`.

Key behavior:
- `chat()` conditionally writes formatted debug output to stderr when global `chatty` is nonzero.
- `panic()` prints command name, pid, formatted panic text, and current error string, then either aborts or exits depending on `doabort`.

Filesystem relevance:
- Supports observability and fatal failure handling for the FAT 9P server.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/chat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/dat.h

Central data-definition header for `dossrv`.

Key contents:
- FAT partition type constants for FAT12, FAT16, FAT32, extended FAT variants, and DMDDO.
- On-disk structures: `Dospart`, `Dosboot`, `Dosboot32`, `Fatinfo`, and `Dosdir`.
- In-memory filesystem state: `Dosbpb` for parsed BPB/FAT geometry and allocation state.
- Directory traversal state: `Dosptr`, including current directory-entry address/offset, parent address/offset, cached sector, and cluster cursor.
- Served filesystem state: `Xfs`, with backing device name/qid/fd, root qid, FAT32 flag, offset, refcount, and parsed private state.
- Per-fid state: `Xfile`, with fid, open flags, qid, attached `Xfs`, and `Dosptr`.
- Little-endian helpers `GSHORT`, `GLONG`, `PSHORT`, and `PLONG`.
- Request/reply buffer globals and maximum 9P data size.

Filesystem relevance:
- Defines the server’s FAT disk layout, 9P fid state, qid mapping, and cached traversal model.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/devio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/devio.c

Device I/O shim for the FAT server.

Key behavior:
- `devread()` reads sectors with `pread()` at `xf->offset + sector*Sectorsize`.
- `devwrite()` writes sectors with `pwrite()` unless the backing file was opened read-only.
- `devcheck()` verifies media/backing-file liveness by reading sector zero.
- `deverror()` maps short/failed I/O to `Eio`, logs details, and closes/invalidates the backing fd on hard errors.

Filesystem relevance:
- All cached FAT sector reads/writes pass through this offset-aware backing-device layer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/devio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/dosfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/dosfs.c

Implements the 9P request handlers for the DOS/FAT filesystem server.

Key behavior:
- Handles `Tversion`, `Tauth`, `Tflush`, `Tattach`, `Twalk`, `Topen`, `Tcreate`, `Tread`, `Twrite`, `Tclunk`, `Tremove`, `Tstat`, and `Twstat`.
- `rattach()` opens or reuses the backing filesystem, parses FAT metadata via `dosfs()`, and creates a synthetic root fid.
- `rwalk()` supports cloning, `.`/`..`, long/short name lookup, directory qid assignment, and FAT directory type bits.
- `ropen()` enforces read-only attributes, `ORCLOSE`, truncate, directory/write rules, and open mode flags.
- `rcreate()` creates short or long-name directory entries, allocates first cluster for new directories, and writes `.`/`..`.
- `rread()` and `rwrite()` dispatch to directory serialization or file byte I/O.
- `rremove()` validates parent permissions and empty directories, truncates cluster chains, and marks directory entries deleted.
- `rwstat()` supports mode/mtime changes, truncation, contiguous-file conversion through `DMAPPEND`, and rename by remove-and-recreate; moved directory-entry pointers are propagated to other open fids.

Filesystem relevance:
- This is the protocol-facing mutation layer translating Plan 9 9P calls into FAT directory and allocation operations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/dosfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/dosfs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/dosfs.h

Tiny protocol constants header for `dossrv`.

Key contents:
- `Maxfdata = 8192`.
- `Maxiosize = IOHDRSZ + Maxfdata`.

Filesystem relevance:
- Caps 9P payload sizing used by request and response buffers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/dosfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/dossubs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/dossubs.c

Core FAT implementation for `dossrv`.

Key behavior:
- Detects FAT boot sectors and parses FAT12/16/32 BPB fields, FAT mirroring flags, root locations, data start, cluster counts, FAT width, and FAT32 info-sector free-space hints.
- Resolves file clusters and sectors, allocating clusters on demand for writes.
- Implements name handling: Plan 9 space/colon translation, DOS 8.3 classification, long-name alias generation, long-name entry parsing/writing, and checksum validation.
- Searches directories, finds free entry ranges for short/long names, reads directories into 9P `Dir` records, and reconstructs parent pointers for `..`.
- Reads, writes, and truncates regular files by walking FAT chains.
- Converts FAT entries to/from Plan 9 `Dir`, including read-only, directory, system/exclusive, and append/contiguous indicators.
- Reads/writes FAT12, FAT16, and FAT32 entries, updates all mirrored FATs, and maintains FAT32 info-sector free counts.
- Allocates clusters, frees chains, and can relocate system files into contiguous extents for `DMAPPEND`.
- Provides time conversion, boot-sector dump helpers, directory-entry dump helpers, case-insensitive comparison, and UTF-to-Rune conversion.

Filesystem relevance:
- This is the real FAT metadata engine: boot parsing, directory walking, long names, FAT chain mutation, allocation, truncation, and contiguity repair.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/dossubs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/errstr.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/errstr.h

Static error-string table for `dossrv`.

Key behavior:
- Maps internal error enum values such as `Eformat`, `Eio`, `Enoauth`, `Enonexist`, `Eperm`, `Econtig`, `Ebadstat`, `Etoolong`, and `Eversion` to 9P-facing error text.
- Used by `xerrstr()` in `xfssrv.c`.

Filesystem relevance:
- Defines client-visible failures for FAT parsing, permissions, allocation, protocol, and backing I/O errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/errstr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/fns.h

Function prototype header for `dossrv`.

Key contents:
- Declares FAT parsing, boot dumps, allocation, FAT entry access, directory traversal, name conversion, file read/write/truncate, qid comparison, request handlers, cache sync, and server I/O functions.
- Declares diagnostics helpers `chat()` and `panic()` with Plan 9 vararg checking.
- Declares `xfile()`/`getxfs()` lifecycle APIs and `xerrstr()`.

Filesystem relevance:
- Captures the module boundary between 9P request handling, FAT metadata routines, cache/device I/O, and fid/backing-filesystem management.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/iotrack.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/iotrack.c

Sector cache for `dossrv`.

Key behavior:
- Caches tracks of 9 sectors (`Sect2trk`) in an 80-entry LRU, with a 31-bucket hash table.
- `getsect()` returns a read-filled sector; `getosect()` returns a sector for overwrite without forcing a read; both route through `getiosect()`.
- Tracks carry dirty, immediate-write, and stale flags; individual `Iosect` objects lock sectors within tracks.
- `getiotrack()` finds cached tracks or evicts an unreferenced LRU track, writing dirty data first.
- `tread()` and `twrite()` read/write complete tracks via `devread()`/`devwrite()`.
- `purgebuf()` flushes and invalidates all tracks for a backing `Xfs`.
- `sync()` flushes all dirty tracks.
- `iotrack_init()` initializes hash/LRU lists and allocates track buffers with `sbrk()`.

Filesystem relevance:
- Provides write-back sector buffering for FAT metadata and file data, including stale partial-track handling before writes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/iotrack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/iotrack.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/iotrack.h

Cache/device I/O type header for `dossrv`.

Key contents:
- Defines `MLock`, `Iosect`, `Iotrack`, and `Track`.
- Establishes `Sectorsize = 512`, `Sect2trk = 9`, and `Trksize`.
- Defines buffer flags `BMOD`, `BIMM`, and `BSTALE`.
- Declares sector acquisition/release, track read/write/purge, cache init/sync, simple lock operations, and device I/O functions.

Filesystem relevance:
- Shared declarations for the FAT server’s sector-cache and backing-device layer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/iotrack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/lock.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/lock.c

Minimal in-process lock implementation for `dossrv`.

Key behavior:
- `mlock()` sets a one-byte lock key and panics on double lock or uninitialized values.
- `unmlock()` clears the key and panics on unlock errors.
- `canmlock()` is a nonblocking try-lock.

Filesystem relevance:
- Used by FAT allocation and sector-cache structures, but it is only a cooperative sanity lock, not an OS blocking primitive.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/lock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/xfile.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/xfile.c

Lifecycle manager for `dossrv` backing filesystems and 9P fids.

Key behavior:
- `getxfs()` opens the backing device/file, supports optional `name:sector-offset`, falls back to read-only when write-open fails, and reuses existing live `Xfs` instances by qid/name/offset after `devcheck()`.
- `refxfs()` reference-counts `Xfs`; when it reaches zero, it frees parsed FAT state, purges cached tracks, closes the device, and invalidates the fd.
- `xfile()` manages fid hash buckets, allocates/reuses `Xfile` structures, handles clunk, and refuses stale backing files.
- `clean()` drops a fid’s `Dosptr`, decrements its `Xfs`, and resets state.
- `dosptrreloc()` updates all open fids pointing at a directory entry that moved during rename.

Filesystem relevance:
- Bridges 9P fid lifetime to backing FAT-device lifetime and keeps open handles coherent across directory-entry relocation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/xfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/xfssrv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/xfssrv.c

Main program and 9P dispatch loop for `dossrv`.

Key behavior:
- Parses options for read-only mode, verbosity, default device file, stdio serving, abort-on-panic, and space/colon translation.
- Posts a service file under `#s/<name>` unless serving over stdio.
- Forks into a service process, initializes the sector cache, and dispatches 9P requests with `read9pmsg()`, `convM2S()`, handler table lookup, and `convS2M()`.
- Uses `Rerror` replies with `xerrstr()` when handlers set internal `errno`.
- Removes the posted service file at exit.
- Provides qid equality helper.

Filesystem relevance:
- This is the server shell that exposes the FAT implementation as a Plan 9 9P service.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dossrv/xfssrv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/du.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/du.c

Plan 9 `du` implementation.

Key behavior:
- Recursively walks directories with `dirread()`, sums rounded file lengths, and prints totals.
- Options include all files, custom block size, floating output, warnings off, autoscale, byte mode, qid output, read-through mode, summary-only, mtime/atime output, and SI-prefix output selection.
- Uses a qid/type/dev cache to avoid directory cycles.
- `readflg` opens and reads file contents for every file without reporting normal totals.
- Uses Plan 9 `String` helpers to build child paths and quote-aware output formatting.

Filesystem relevance:
- User-level filesystem traversal and accounting utility; relies on qids to avoid loops.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/du.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/echo.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/echo.c

Simple `echo` command.

Key behavior:
- Supports `-n` to suppress trailing newline.
- Builds one output buffer from arguments separated by spaces.
- Writes once to fd 1 and reports write errors to stderr.

Filesystem relevance:
- Minimal command I/O; no filesystem-specific logic beyond stdout/stderr writes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/echo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ecp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ecp.c

Error-tolerant sector copy utility.

Key behavior:
- Copies a specified number of sectors from source to destination using large block transfers.
- On I/O failure, falls back to single-sector retries and reports bad-sector ranges.
- Supports confirmation, progress output, reverse copy order, input reblocking, maximum consecutive error limits, sector-size/block-size options, source/destination starting sectors, optional byte “swizzle”, and separate verification pass.
- Treats short reads as I/O errors but can reblock pipe input.
- Uses magic sentinels to detect reads that falsely report success without changing the buffer.
- Verifies by rereading source and destination after copy to avoid controller cache effects.

Filesystem relevance:
- Block-device/file image copy tool for damaged media and low-level filesystem/device recovery workflows.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ecp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ed.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ed.c

Plan 9 line editor implementation.

Key behavior:
- Maintains the edited buffer as line addresses pointing into a temporary file under `/tmp/eXXXXX`.
- Stores runes in 4096-byte blocks with separate input/output block caches.
- Implements classic `ed` commands: append, change, delete, edit/read/write, filename, global/inverse global, insert, join, mark, move/copy, print/list/number, quit, shell escape, substitute, undo-last-substitution, and line addressing.
- Uses Plan 9 `Biobuf` and rune-aware I/O for files and terminal input.
- Handles regular expressions via `regexp.h`, including substitutions with `&` and numbered submatches.
- On hangup, writes current buffer to `ed.hup` if possible.
- Warns on append-only input files and supports append writes via `W`.

Filesystem relevance:
- File editor with explicit temp-file storage, read/write/create/append behavior, and crash/hangup rescue path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ed.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/diacrit.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/diacrit.c

Builds eqn boxes with accents and bars.

Key behavior:
- Adds vector, dyad, hat, tilde, dot, double-dot, bar, high/low bar, underbar, and utilde decorations to an existing box.
- Computes vertical and horizontal shifts from tuning parameters and current point size.
- Uses temporary string/number registers, width measurements, and troff motion commands.
- Updates box height for above-text accents and adjusts classes/fonts.

Filesystem relevance:
- Typesetting module only; no filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/diacrit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/e.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/e.h

Main shared header for `eqn`.

Key contents:
- Character classes and spacing matrix declaration.
- Debug/error macros and token/font constants.
- Global parser/layout state: point size, font stack, display mode, type setter, equation registers, heights, baselines, left/right fonts/classes, delimiters, and input stacks.
- Tables for keywords, definitions, reserved words, and tuning definitions.
- Input source, argument, and font-stack structs.
- Prototypes for parser helpers, input handling, symbol lookup, box constructors, font/size/motion operations, piles, matrices, and text conversion.

Filesystem relevance:
- No direct filesystem logic, but declares include-file input structures used by `eqn/include`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/e.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/eqn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/eqn.c

Generated yacc parser for `eqn.y`.

Key behavior:
- Defines token constants, parse tables, token remapping, parser stack, error recovery, and reductions.
- Reductions invoke semantic layout functions for text, sums/products, fractions, marks, size/font changes, square roots, subscript/superscript, integrals, from/to, delimiters, diacritics, movement, piles, matrices, and columns.
- Preserves/restores yacc globals around `yyparse()`.
- Mirrors the grammar and actions from `eqn.y`.

Filesystem relevance:
- Generated parser logic only; no filesystem operations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/eqn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/eqn.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/eqn.y

Yacc grammar for `eqn`.

Key behavior:
- Defines tokens and precedence for equation constructs.
- Grammar parses equation sequences, grouping, quoted/contiguous text, spaces, special operators, fractions, marks, font/size changes, square roots, sub/superscripts, integrals, from/to limits, left/right delimiters, diacritics, movement, piles, matrices, and column lists.
- Semantic actions call the corresponding box-building functions.
- Adjusts point size around scripts/limits with `deltaps`.

Filesystem relevance:
- Grammar source only; no filesystem operations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/eqn.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/eqnbox.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/eqnbox.c

Concatenates two equation boxes.

Key behavior:
- Computes combined height and baseline from both operands.
- Uses class-based spacing between the right class of the left box and left class of the right box.
- Supports lineup mode by measuring and aligning to register 09.
- Appends the second box’s string to the first and frees the second register.

Filesystem relevance:
- Typesetting layout only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/eqnbox.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/font.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/font.c

Font state handling for `eqn`.

Key behavior:
- `setfont()` maps R/I/B and named fonts into troff font identifiers and pushes current font state.
- `font()` applies a font change to an equation box and restores the prior font.
- `globfont()` changes global default font.
- `fatbox()` simulates bold/fat text by overprinting a shifted copy.

Filesystem relevance:
- Typesetting state only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/font.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/fromto.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/fromto.c

Implements `from`/`to` limits.

Key behavior:
- Builds a new box containing a base expression plus optional lower and upper limit boxes.
- Measures widths, centers components, adjusts point size for limits, and computes combined height/baseline.
- Frees consumed component registers.

Filesystem relevance:
- Typesetting layout only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/fromto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/funny.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/funny.c

Builds large operator boxes.

Key behavior:
- Handles sum, product, union, and intersection tokens.
- Looks up tuned troff strings for the operator glyphs.
- Assigns height, baseline, and roman font classification.

Filesystem relevance:
- Typesetting layout only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/funny.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/glob.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/glob.c

Global variable definitions for `eqn`.

Key behavior:
- Defines default typesetter, minimum size, debug flag, layout stacks/register-use state, point-size/font defaults, display mode, parse error state, equation metrics arrays, delimiter state, and mark/lineup flag.

Filesystem relevance:
- Shared process state only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/glob.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/input.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/input.c

Input-source and macro expansion engine for `eqn`.

Key behavior:
- Maintains a stack of sources: file, macro, string, single-character pushback, and free-on-pop string.
- Expands macro arguments `$1..$n`.
- `dodef()` collects macro call arguments and switches input to the definition body.
- `input()` reads from current source, tracks file line numbers, closes included files on EOF, and records error context.
- `unput()` implements pushback through a character source.
- Error reporting prints command/file/line context and injects a safe `.EN`.

Filesystem relevance:
- Reads included input files opened by the lexer and closes them on EOF.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/input.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/integral.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/integral.c

Integral layout helper.

Key behavior:
- `setintegral()` constructs the integral sign box from tuned definition text.
- `integral()` composes an integral sign with optional lower and upper limits using `fromto()`.

Filesystem relevance:
- Typesetting layout only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/integral.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/lex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/lex.c

Lexer and directive handler for `eqn`.

Key behavior:
- Tokenizes equation input, quoted strings, contiguous identifiers, spaces, thin spaces, braces, keywords, and inline delimiters.
- Expands user definitions from `deftbl`, including macro calls with arguments.
- Handles directives: `define`, `tdefine`, `ndefine`, `ifdef`, `delim`, `gsize`, `gfont`, `include`/`copy`, and `space`.
- `include()` opens an input file with `fopen()`, pushes it onto the input stack, and emits `.lf` line directives.
- `delim()` configures inline equation delimiters.

Filesystem relevance:
- Directly opens include/copy files for nested equation input.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/lookup.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/lookup.c

Symbol tables for `eqn`.

Key behavior:
- Defines keyword table mapping eqn syntax words to parser tokens.
- Defines reserved-word translations for mathematical symbols, Greek letters, relation operators, functions, and named output strings.
- Implements simple additive string hash, lookup, install/update, and table initialization.
- `init_tbl()` installs keywords/reserved words and initializes tuning definitions.

Filesystem relevance:
- In-memory parser table logic only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/main.c

Main program and output driver for `eqn`.

Key behavior:
- Parses options for debug, point size, equation delimiters, font, device type, and output mode.
- Processes input files/stdin, detects `.EQ`/`.EN` display equations and inline equations, and calls `yyparse()`.
- Emits troff setup/output strings, line directives, marks, height adjustments, and final equation strings.
- Manages string-register allocation/freeing and width measurement.
- Provides point-size formatting helpers and em conversion.

Filesystem relevance:
- Opens input files specified on the command line and reads them line by line; otherwise stdin.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/mark.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/mark.c

Implements equation marks and lineup points.

Key behavior:
- `mark()` records the current horizontal position in troff register 09.
- `lineup()` either marks that a lineup directive exists or emits horizontal motion to align with register 09.
- Sets `markline` state for display output.

Filesystem relevance:
- Typesetting state only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/mark.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/matrix.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/matrix.c

Matrix column assembly for `eqn`.

Key behavior:
- `startcol()` reserves entries in `lp[]` for a column and returns its start offset.
- `column()` records column type, entry count, and separation.
- `matrix()` converts multiple column boxes into a matrix, using tuned inter-column spacing and `eqnbox()` concatenation.

Filesystem relevance:
- Typesetting layout only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/matrix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/move.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/move.c

Manual motion helper for `eqn`.

Key behavior:
- Applies horizontal forward/backward or vertical up/down troff motion around a box.
- Converts hundredths of em to current-size em units.
- Keeps the moved box register as the result.

Filesystem relevance:
- Typesetting layout only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/move.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/over.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/over.c

Fraction layout for `eqn`.

Key behavior:
- Builds a numerator-over-denominator box with tuned gap, bar width, and overline padding.
- Measures both sides, centers them around a temporary width register, draws the fraction line, and updates height/baseline.
- Frees denominator and temporary register.

Filesystem relevance:
- Typesetting layout only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/over.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/paren.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/paren.c

Scalable delimiter construction for `eqn`.

Key behavior:
- Wraps a box with left/right delimiters including parentheses, brackets, braces, floor/ceiling, vertical bars, arbitrary characters, or nothing.
- Computes delimiter height from enclosed box metrics and typesetter-specific tuning.
- Builds tall delimiters from top/middle/bottom pieces using troff bracket construction.
- Adjusts baseline and optional vertical centering for unbalanced boxes.

Filesystem relevance:
- Typesetting layout only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/paren.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/pile.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/pile.c

Vertical pile/column layout for `eqn`.

Key behavior:
- Builds left-, right-, center-, or default-aligned vertical stacks.
- Computes gap, total height, and baseline based on number of elements and tuned pile parameters.
- Measures maximum width and emits troff vertical/horizontal motion for each element.
- Frees all component registers.

Filesystem relevance:
- Typesetting layout only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/pile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/prevy.tab.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/prevy.tab.h

Generated yacc token header for `eqn`.

Key contents:
- Numeric token definitions for text tokens, matrix/column constructs, operators, definitions, delimiters, font/size directives, motion directives, diacritics, and special symbols.

Filesystem relevance:
- Parser build artifact only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/prevy.tab.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/shift.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/shift.c

Subscript and superscript layout for `eqn`.

Key behavior:
- Dispatches to single sub/sup or combined sub-and-sup layout.
- Computes script vertical shifts, point-size changes, spacing adjustments, height, and baseline.
- Handles special italic spacing cases and right-class propagation.
- Frees consumed script registers and temporary registers.

Filesystem relevance:
- Typesetting layout only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/shift.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/size.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/size.c

Point-size control for `eqn`.

Key behavior:
- `setsize()` parses relative and absolute size specifications, tracks absolute-size stack state, and updates current point size.
- `size()` wraps a box in the size transition and restores the prior size.
- `globsize()` changes global equation size and recomputes default script-size delta.

Filesystem relevance:
- Typesetting state only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/size.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/sqrt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/sqrt.c

Square-root layout for `eqn`.

Key behavior:
- Estimates radical glyph size from enclosed box height and device type.
- Updates result height and emits troff strings for radical and overbar.
- Uses width measurement of enclosed box and font-size changes.

Filesystem relevance:
- Typesetting layout only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/sqrt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/text.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/text.c

Text token conversion and spacing logic for `eqn`.

Key behavior:
- Defines class spacing matrix used between mathematical text classes.
- Converts quoted text, spaces, thin spaces, tabs, reserved words, and ordinary tokens into troff strings.
- Handles UTF input via multibyte conversion and classifies letters, digits, punctuation, relations, arrows, spaces, troff escapes, and special italic `f`/`j`.
- Emits font changes, roman overrides, padding, and escaped troff sequences.
- Tracks left/right fonts and classes for later spacing.

Filesystem relevance:
- Text conversion only; no filesystem operations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/text.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/tuning.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/tuning.c

Tuning constants for `eqn` layout.

Key behavior:
- Defines numeric parameters for script spacing, diacritics, fat text, large operators, integrals, matrices, fractions, delimiters, piles, sub/sup layout, and square roots.
- Defines default string expansions for accents, large operators, and integral symbol.
- Initializes tuning definitions into `deftbl` and tunable names into `ftunetbl`.
- `ftune()` allows definitions to adjust `Subbase` and `Supshift`.

Filesystem relevance:
- Typesetting configuration only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/eqn/tuning.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/execnet/client.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/execnet/client.c

Client/process state engine for the `execnet` synthetic network filesystem.

Key behavior:
- Allocates reusable `Client` records with reader/writer I/O procs and command state.
- Implements queued 9P read requests, queued write requests, and queued process-output messages; `matchmsgs()` pairs reads with buffered output.
- `ctlwrite()` accepts `connect <addr>` and `hangup`; connect converts `host!svc`-style text into `exec <addr>` and starts `/bin/rc -c`.
- `execproc()` creates a pipe, attaches it to child stdin/stdout, closes inherited fds, and execs rc.
- Separate read/write threads transfer between 9P `data` reads/writes and the command pipe.
- Flush handling removes queued reads/writes or interrupts active I/O.
- Close/hangup kills the child process and responds to pending requests with hangup.

Filesystem relevance:
- Implements the dynamic behavior behind `/net/exec/N/{ctl,data,...}` files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/execnet/client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/execnet/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/execnet/dat.h

Shared state header for `execnet`.

Key contents:
- `Msg` buffers process output for pending reads.
- `Client` tracks process lifecycle, command string, pipe fds, pid, status, queued 9P read/write requests, message queues, I/O procs, writer kick channel, and pending exec request.
- Declares client APIs, filesystem initialization, and exec directory naming.
- Defines stack size and client status enum: `Closed`, `Exec`, `Established`, `Hangup`.

Filesystem relevance:
- Defines in-memory state for the synthetic `/net/exec` 9P filesystem.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/execnet/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/execnet/fs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/execnet/fs.c

9P filesystem implementation for `execnet`.

Key behavior:
- Exposes `/exec`, `/exec/clone`, and per-client directories containing `ctl`, `data`, `local`, `remote`, and `status`.
- Encodes qid paths with object type and client number.
- Implements stat generation, directory generators, reads, writes, flushes, attach, walk, open, and fid destruction.
- Opening `clone` allocates a new client and retargets the fid to that client’s `ctl`.
- `data` reads/writes delegate to `client.c`; metadata files expose pid, command, and status.
- Serializes lib9p callbacks through `fsthread` channels to simplify flush/clunk coordination.

Filesystem relevance:
- Defines the synthetic file tree and 9P behavior for executing commands through a network-like interface.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/execnet/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/execnet/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/execnet/main.c

Entry point for `execnet`.

Key behavior:
- Parses debug and `-n` name options.
- Defaults mount point to `/net`.
- Initializes the synthetic filesystem and posts/mounts it before the existing mount point with `threadpostmountsrv()`.
- Disables note group inheritance with `rfork(RFNOTEG)`.

Filesystem relevance:
- Mounts the `/net/exec` 9P service.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/execnet/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/execnet/note.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/execnet/note.c

Custom libthread note handling for `execnet`.

Key behavior:
- Maintains per-process note handler slots and delayed note records.
- `threadnotify()` registers/unregisters a handler for the current proc.
- `_threadnote()` captures incoming notes, queues them for the current proc, and defers handling while `splhi` is set.
- Delivers queued notes to registered handlers or exits/aborts/defaults when unhandled.
- `_procsplhi()` and `_procsplx()` control deferred delivery.

Filesystem relevance:
- Supports robust process/thread interruption for pending 9P I/O and child-command handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/execnet/note.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/exportfs/exportfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/exportfs/exportfs.c

Main process and shared infrastructure for Plan 9 `exportfs`.

Key behavior:
- Parses options for authentication, debugging, encryption/filtering, message size, namespace file, root service path, readonly mode, posted service fd, exclusion patterns, announce string, and back-calling import address.
- Optionally authenticates with p9any, changes user namespace, disallows `none`, and supports SSL negotiation for new import protocol.
- Establishes service root from `-s`/`-r`, posted service fd, back-call import, or path read from the network connection.
- Initializes root `File` records and qid uniquification tables.
- Reads 9P messages with `localread9pmsg()`, decodes to `Fcall`, and dispatches through `fcalls`.
- `reply()` serializes `Fcall` replies to the network fd.
- Manages fid hash table allocation/freeing, including unmounting per-fid mount points.
- Maintains `File` tree cache with refcounts, parent/child lists, path construction, exclusion checks, and fresh `dirstat()` data.
- Maps real `Dir` qids to unique exported qids, resolving qid collisions by using high path bits.
- `filter()` negotiates an auxiliary listener and execs an external filter such as `aan`.
- `fatal()` kills slave worker processes before exiting.

Filesystem relevance:
- Core export server setup, connection negotiation, fid/cache management, and qid mapping for exporting a Plan 9 namespace over 9P.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/exportfs/exportfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/exportfs/exportfs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/exportfs/exportfs.h

Shared definitions for `exportfs`.

Key contents:
- Structures:
  - `Fsrpc`: work buffer, active pid, interrupt/flush metadata, incoming `Fcall`, and data buffer.
  - `Fid`: exported fid state, local fd, cached `File`, open mode, mount id, directory read cache, and directory offset state.
  - `File`: cached namespace node with name, refcount, qid, qid-table entry, invalid flag, parent/child links.
  - `Proc`: slave worker process list.
  - `Qidtab`: refcounted mapping from real qids to exported unique qid paths.
- Constants for worker counts, fid hash size, qid hash size, and mount map size.
- Global variables for work queue, root files, fid hash/free list, worker process list, mount map, qid table, message size, service fd, and exclusion pattern file.
- Prototypes for 9P handlers, slave I/O operations, fid/file/qid lifecycle, filters, note handling, exclusions, and directory read filtering.

Filesystem relevance:
- Defines the exported namespace cache, fid table, qid-translation layer, and 9P dispatch interface used by `exportfs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/exportfs/exportfs.h -->