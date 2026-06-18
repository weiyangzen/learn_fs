# Group Research: group_1505_plan9_sources_os_plan9_plan9_sys_src_cmd_aux_antiword_xml_c_sources_2a689647e2d8

Scope verified against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/plan9/plan9`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/xml.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/xml.c

This file implements Antiword's DocBook/XML output backend.

Key behavior:
- Maintains a DocBook tag stack for `book`, `chapter`, `sectN`, `para`, tables, lists, emphasis, footnotes, and inline super/subscript.
- Escapes XML-sensitive characters and emits UTF-8 converted special characters through Antiword's character translation layer.
- Builds book metadata from Word document properties: title, subject, author, date, company, and language.
- Converts Word paragraphs, headings, lists, page breaks, tables, and footnote markers into DocBook structures.
- Tracks output state globally, including open paragraph/list/table/header levels and current table column count.

Important details:
- Empty Word headings and lists are patched with empty DocBook paragraphs/items because DocBook disallows empty structural elements.
- Tables are emitted as `informaltable` with `tgroup`, `colspec`, `tbody`, `row`, and `entry`.
- List style codes are mapped to DocBook ordered/itemized list attributes.
- Footnote insertion temporarily closes super/subscript tags and restores them after the footnote.

Filesystem relevance:
- Indirect: document conversion output layer; consumes parsed Word/OLE content but does not implement filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/xml.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/apm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/apm.c

This file implements a 9P filesystem interface to PC APM power-management BIOS calls.

Key behavior:
- Opens `/dev/apm`, `#P/apm`, or a user-specified APM device and issues BIOS-style calls by reading/writing `Ureg`.
- Exposes a mounted namespace containing `event`, `battery`, and `ctl`.
- `battery` reports per-battery status, percentage, and remaining time.
- `ctl` reports AC status, capabilities, and device power states; writes issue commands such as `enable`, `disable`, `standby`, `on`, and `suspend`.
- A background event polling path queues APM notifications for blocking reads of `event`.

Important details:
- Serializes APM calls with `apmlock`.
- Requires APM version 1.2 or newer.
- Event reads are cancellable through 9P flush handling.
- Supports pipe/stdin mode with `-i`, mount point with `-m`, service name with `-s`, no-poll mode with `-P`, and debug flags.

Filesystem relevance:
- Direct: a synthetic 9P filesystem mapping firmware power state and events into ordinary Plan 9 files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/apm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/astarld.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/astarld.c

This file loads firmware or memory images into an `astar` device.

Key behavior:
- Supports Intel HEX-style load records and raw image loading.
- Opens `#G/astarNctl` and `#G/astarNmem`, requests `download`, writes memory, then optionally sends `run`.
- Can operate on a temporary local file instead of hardware with `-n`.
- Clears the 64 KiB target memory before loading hex input.
- Verifies writes by reading memory back and comparing.

Important details:
- Supports device units `-0` through `-3`.
- Parses data, EOF, and segment records with checksums.
- Enforces a 64 KiB memory limit.
- Options include dump, image, no-load, and no-start modes.

Filesystem relevance:
- Indirect: uses Plan 9 device files as firmware loading endpoints.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/astarld.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/cddb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/cddb.c

This file queries a CDDB/freedb server for album and track metadata.

Key behavior:
- Connects to the configured server on TCP port 888.
- Sends CDDB hello, protocol negotiation, query, and read commands.
- Accepts exact or close matches, using the first returned match.
- Parses `DTITLE` and `TTITLEn` fields and prints title/track listings.
- Can print track durations and total time.

Important details:
- Default server is `freedb.freedb.org`.
- Protocol level 6 is requested for UTF-8.
- Input format is `query diskid ntrack offsets... leadout`.
- Text continuations are appended to existing title strings.

Filesystem relevance:
- Indirect: network metadata utility; no filesystem implementation logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/cddb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/clog.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/clog.c

This file implements a simple console logger.

Key behavior:
- Opens a console-like input file and an append log file.
- Reads complete newline-terminated lines with `Biobuf`.
- Prefixes each line with a timestamp and appends it to the log.
- Reopens the log on write failure and retries.

Important details:
- Creates the log file with `DMAPPEND|0666` if needed.
- Drops overlong partial-line fragments by reading and discarding extra buffered data.
- Stops on true EOF or read error.

Filesystem relevance:
- Indirect: consumes and writes ordinary files, typically device console streams and log files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/clog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/consolefs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/consolefs.c

This file implements `consolefs`, a 9P filesystem presenting configured serial consoles as files.

Key behavior:
- Reads console definitions from `/lib/ndb/consoledb` or a configured NDB file.
- Exposes a one-level namespace with up to three files per console: data, `ctl`, and `stat`.
- Opens serial devices, configures baud rate, and launches a reader process per active console.
- Broadcasts console output to all open data fids using per-fid circular buffers and delayed read replies.
- Writes to data files go to the console device, except `/dev/null` "chat" consoles broadcast user-tagged messages.

Important details:
- Supports open-on-demand consoles that close when no client is attached.
- Access control is based on `uid`/`gid` fields in the NDB console entry.
- Directory entries are generated dynamically from configured consoles and existing control/status fds.
- Flush removes pending read requests by tag.
- Mounts through a pipe and posts `#s/consoles`.

Filesystem relevance:
- Direct: full user-level 9P filesystem for multiplexing and controlling console devices.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/consolefs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/conswdir.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/conswdir.c

This file filters console output for xterm-style title escape sequences that encode working-directory changes.

Key behavior:
- Detects sequences of the form ESC `] ; path` BEL.
- Removes those in-band messages from the byte stream passed to stdout.
- Runs `/bin/rwd` or a supplied program with the extracted path.
- Saves and restores `/dev/label` and `/dev/wdir`.

Important details:
- Uses a small state machine over buffered input.
- Gives up and passes bytes through if an escape sequence grows too long without termination.
- Handles interrupts by continuing and restores state on exit.

Filesystem relevance:
- Indirect: updates Plan 9 window/device state via `/dev/label` and `/dev/wdir`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/conswdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/data2s.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/data2s.c

This file converts stdin bytes into Plan 9 assembler `DATA`/`GLOBL` directives.

Key behavior:
- Emits eight-byte string chunks as `DATA namecode+offset(SB)/8`.
- Escapes nonzero bytes as octal and zero bytes as `\z`.
- Pads the generated data to an eight-byte boundary.
- Emits globals for the data and a separate `namelen` length word.

Important details:
- Takes exactly one symbol-name prefix argument.
- Original unpadded byte length is preserved in `namelen`.

Filesystem relevance:
- Indirect: build utility for embedding binary file data into assembly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/data2s.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/depend.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/depend.c

This file implements a 9P filesystem that exposes `.depend` dependency graphs as virtual tar files.

Key behavior:
- Posts a service in `#s/<svc-name>` and serves a filesystem rooted at a supplied directory.
- Real directories are walked normally, but symbols from each directory's `.depend` file appear as `<symbol>.tar` files.
- Parses `.depend` records: `F` source file, `D` defined symbol, and `R` referenced symbol.
- Resolves transitive dependencies into bit vectors of required files.
- Reads of a virtual tar stream synthesize tar headers, source file contents, padding, and trailing zero blocks.

Important details:
- Caches parsed dependency files by path and invalidates them when their qid changes.
- Source filenames may resolve to `.Z` or `.gz` variants if the plain file is absent.
- Directory reads include subdirectories first, then virtual tar dependency files.
- Service is read-only; create, write, remove, and wstat are denied.
- Multiple `fsrun` processes share the mounted pipe with an I/O lock.

Filesystem relevance:
- Direct: synthetic filesystem overlay that materializes dependency closure archives on demand.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/depend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/disksim.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/disksim.c

This file implements a synthetic disk device filesystem resembling `/dev/sdXX`.

Key behavior:
- Exposes a root directory containing an `sdXX` directory, with `ctl` and partition files underneath.
- `ctl` reads print inquiry, geometry, and partition table data.
- `ctl` writes accept `part`, `delpart`, `inquiry`, and `geometry` commands.
- Partition files support bounded reads and writes over sparse in-memory block storage.
- Can back storage with a real file, reading blocks lazily and writing dirty blocks back unless read-only.

Important details:
- Uses 8192-byte blocks and triple-indirect pointer tables for sparse addressing.
- Default partition is `data`.
- Partition qid versions change on replacement to catch stale fids.
- Supports service posting, mount point selection, read-only mode, and debug 9P logging.

Filesystem relevance:
- Direct: user-level simulated block-storage namespace with dynamic partitions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/disksim.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/aux.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/aux.c

This file provides small allocation helpers for the flashfs code.

Key behavior:
- `emalloc9p` allocates zeroed memory or exits on failure.
- `erealloc9p` reallocates or exits on failure.
- `estrdup9p` duplicates a string or exits on failure.

Important details:
- Sets Plan 9 malloc/realloc tags from caller PCs.
- Error messages go to stderr and terminate the process with `"mem"`.

Filesystem relevance:
- Supporting utility for flashfs and its bundled 9P service code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/aux.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/aux.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/aux.h

This header declares flashfs allocation helpers.

Key behavior:
- Declares `emalloc9p`, `erealloc9p`, and `estrdup9p`.
- Defines `DMDIR` as `CHDIR` for compatibility with older directory-mode naming.

Filesystem relevance:
- Supporting header for the flashfs user-level filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/aux.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/conv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/conv.c

This file serializes and deserializes flashfs journal records.

Key behavior:
- Converts `Jrec` structures to compact on-flash byte records with `convJ2M`.
- Converts byte records back to normalized `Jrec` structures with `convM2J`.
- Encodes creates, chmods, removes, writes, append-style writes, truncates, and summary markers.
- Uses compact one-, two-, or three-byte integer encoding through `putc3`/`getc3`.
- Provides `%J` formatting for debugging journal records.

Important details:
- Public logical operations such as `FT_create`, `FT_chmod`, and `FT_trunc` are lowered to smaller mode-specific record variants.
- Write sizes are stored as `size - 1`.
- Names are capped by `MAXNSIZE`.

Filesystem relevance:
- Direct: defines flashfs's persistent journal record wire format.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/conv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/devfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/devfs.c

This file abstracts flashfs block storage over either a flash device or a plain file.

Key behavior:
- Opens a data file/device and optionally a matching `ctl` file.
- Reads flash geometry from the control file when using a flash device.
- Falls back to plain-file mode with explicit or stat-derived sector count/size.
- Erases sectors either by writing all-ones blocks or by issuing `erase` to the device control file.
- Provides sector-relative `readdata` and `writedata`.

Important details:
- Requires reasonable sector counts and sector sizes.
- Plain-file erase uses a cached all-ones sector buffer.
- `writedata` can either return failure for recoverable write attempts or fatal on short/error writes.

Filesystem relevance:
- Direct: storage backend layer for the flashfs journal filesystem.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/devfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/dreq.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/dreq.c

This file is an alternate or dummy 9P request layer for flashfs.

Key behavior:
- Defines fid state holding an `Entry` and optional directory reader.
- Implements attach, open, create, read, write, remove, stat, wstat, and walk handlers.
- Directory reads use `edirread`.
- Metadata operations delegate to entry routines such as `ecreate`, `etrunc`, `eremove`, `echmod`, and `estat`.
- Mounts with `postmountsrv` under service name `brzr`.

Important details:
- Regular file reads return zero bytes and regular file writes only acknowledge bytes, so payload I/O is not implemented here.
- `flwalk` rejects all walks when `readonly` is set, which makes read-only traversal unusable in this version.
- The complete journaled request path appears in `request.c`.

Filesystem relevance:
- Direct but incomplete: skeletal flashfs 9P server layer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/dreq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/dummy.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/dummy.c

This file starts an in-memory/dummy flashfs service.

Key behavior:
- Sets program name to `dummyfs`.
- Defaults mount path to `/n/brzr`.
- Sets `limit` to 100 KiB.
- Initializes the entry tree and serves the filesystem.

Important details:
- Supports `-m` to choose the mount point.
- Does not load a backing flash journal.

Filesystem relevance:
- Direct test harness for the flashfs namespace logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/dummy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/entry.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/entry.c

This file implements flashfs's in-memory file tree and extent model.

Key behavior:
- Creates the root entry and an integer map from file numbers to entries.
- Manages directory hash tables, directory child lists, and active directory readers.
- Creates, truncates, removes, walks, stats, chmods, and destroys entries.
- Represents file data as extent lists in two generations/parities.
- Reads file ranges by overlaying extents and zero-filling holes.
- Supports sector renumbering after journal sector copying.

Important details:
- File numbers are assigned monotonically unless restored from journal records.
- Directory removal adjusts active readers so they do not point at removed entries.
- Writes prepend extents and update size/mtime.
- `esum` moves surviving extents between parity lists during summarization.
- `used` tracks live extent payload bytes.

Filesystem relevance:
- Direct: core flashfs vnode/inode-equivalent layer and file data extent map.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/entry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/errors.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/errors.c

This file defines shared flashfs error strings.

Key behavior:
- Provides messages for non-empty directory removal, existing file, nonexistent file, directory/type errors, permission denial, and read-only filesystem.

Filesystem relevance:
- Direct support code for flashfs 9P responses.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/errors.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/flash.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/flash.c

This file is the main executable for mounting a journaled flashfs instance.

Key behavior:
- Parses options for read-only mode, sector count, sector size, mount point, backing file/device, and 9P debug.
- Initializes the storage backend, sector buffer, entry tree, and journal state.
- Loads the filesystem from flash sectors.
- Serves the mounted namespace.

Important details:
- Defaults to backing device `/dev/flash/fs` and mount point `/n/brzr`.
- Uses `loadfs(ro)` before serving.
- Requires storage geometry from arguments or the backend.

Filesystem relevance:
- Direct: flashfs server entry point.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/flash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/flashfs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/flashfs.h

This header defines flashfs's on-disk format constants, core structs, globals, and function interfaces.

Key behavior:
- Defines sector magic, format version, journal record type codes, record-size limits, name/file-size limits, hash-table sizes, and write sizing.
- Declares `Extent`, `Exts`, `Entry`, `Dirr`, `Jrec`, and `Renum`.
- Declares storage, conversion, journal, serving, and entry-tree APIs.
- Exposes global geometry, buffers, root entry, readonly state, generation parity, and accounting variables.

Important details:
- Maximum file size is 2 MiB and maximum filename size is 28 bytes.
- Journal record types include create variants, chmod variants, remove, write, trunc variants, summary begin/end, and summary.
- `Entry` uses a union for directory children/readers or file generation extent lists.

Filesystem relevance:
- Direct: central interface and format definition for the flashfs filesystem.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/flashfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/journal.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/journal.c

This file implements flashfs's flash journal loading, recovery, allocation, and compaction.

Key behavior:
- Scans sectors into two generations and a free-sector list.
- Replays journal records into the in-memory entry tree and extent lists.
- Recovers several interrupted-write "window" cases by freeing duplicates, duplicating sectors, or adjusting generations.
- Allocates new sectors and appends journal records safely.
- Summarizes old generation data into the current generation to reclaim sectors.
- Computes write space needs and switches to read-only on generation exhaustion.

Important details:
- Sector headers store magic, generation number, and sequence number with compact integers.
- Record append writes payload first and commits by writing the type byte.
- Time deltas are stored relative to sector time; `now()` manages clock rollback by applying `delta`.
- Summary records preserve live metadata and extents while freeing old sectors.
- `maxwrite` is bounded by sector size and `WRSIZE`.

Filesystem relevance:
- Direct: persistence, crash recovery, and garbage collection engine for flashfs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/journal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/mkfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/mkfs.c

This file formats a flashfs image/device.

Key behavior:
- Parses sector count and sector size.
- Initializes the storage backend.
- Writes generation 0 sequence 0 header to sector 0.
- Erases intermediate sectors.
- Writes generation 1 sequence 0 header to the final sector.

Important details:
- Uses flashfs magic and compact integer encoding.
- Requires exactly one target file/device path.

Filesystem relevance:
- Direct: flashfs format/initialization tool.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/mkfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/mkit -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/mkit

This is a tiny rc script for creating a sample flashfs file image.

Key behavior:
- Writes fake flash geometry to `fs.filectl`.
- Runs `8.mkflashfs -n 16 -z 16384 -f fs.file`.

Filesystem relevance:
- Direct helper script for preparing a flashfs test image.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/mkit -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/request.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/request.c

This file implements the complete flashfs 9P request handler layer.

Key behavior:
- Attaches fids to the root entry and keeps per-fid `Entry`/directory-reader state.
- Enforces open permissions, read-only mode, and directory write restrictions.
- Handles create, remove, chmod-like wstat, truncating open, reads, writes, stats, walks, and fid destruction.
- Reads regular files through `eread`.
- Writes regular files by splitting data into journal-sized chunks, allocating extents, appending `FT_WRITE` records, and updating the entry tree.
- Logs create, trunc, remove, and chmod operations into the flash journal.

Important details:
- Uses `need()` before writing journal records to trigger compaction or fail when full.
- Rejects names longer than `MAXNSIZE`.
- OTRUNC is journaled as `FT_trunc` and assigns a new file number.
- Partial walks clear errors when at least one element succeeds, matching Plan 9 walk semantics.
- Mounts service name `brzr`.

Filesystem relevance:
- Direct: production flashfs user-facing 9P server operations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/request.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/testld.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/testld.c

This file is a load/replay test utility for flashfs images.

Key behavior:
- Parses sector count, sector size, and file path.
- Validates minimum geometry.
- Initializes storage and entry tree.
- Calls `loadfs(1)` to load the filesystem read-only.

Important details:
- Program name is set to `testldfs`.
- Does not serve the filesystem; it tests loading and recovery.

Filesystem relevance:
- Direct test utility for flashfs journal loading.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/testld.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/utils.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/utils.c

This file defines flashfs global state and compact integer helpers.

Key behavior:
- Defines `prog`, sector geometry globals, sector buffer, read-only state, clock delta, generation parity, and magic bytes.
- Encodes unsigned values below 2^21 into one to three bytes with continuation high bits.
- Decodes that compact form.
- Reads and writes little-endian 32-bit values.

Important details:
- `putc3` aborts if the value cannot fit in three bytes.
- The magic bytes are `ROO0`.

Filesystem relevance:
- Direct support for flashfs on-disk format encoding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/getflags.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/getflags.c

This file parses command flags according to the `flagfmt` environment variable and emits rc assignments.

Key behavior:
- Reads `$flagfmt`.
- Initializes all declared `flagX=()` variables.
- Parses command-line flags with Plan 9 `ARGBEGIN`.
- Emits scalar `flagX=1` for boolean flags and list assignments for flags with arguments.
- Emits remaining positional arguments as `*=()` and clears `status`.

Important details:
- Uses rc-compatible quoting through `quotefmtinstall`.
- Prints `status=usage` on usage and `exit 'missing flagfmt'` if the environment is absent.

Filesystem relevance:
- Indirect shell utility; no filesystem implementation logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/getflags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/gps/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/gps/dat.h

This header defines shared GPS utility types and prototypes.

Key behavior:
- Defines `Place` with longitude and latitude.
- Defines `Undef` and default NMEA baud rate `Baud`.
- Declares `nowhere`, `debug`, `%L` formatter support, and coordinate parsers.

Filesystem relevance:
- Supporting header for GPS utilities and `gpsfs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/gps/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/gps/gpsevermore.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/gps/gpsevermore.c

This file initializes/configures EverMore GPS receivers over a serial line.

Key behavior:
- Opens a serial data file and matching control file.
- Sets baud and serial framing.
- Builds EverMore binary packets with DLE escaping and checksum.
- Sends an initialization packet containing GPS week/time, approximate location, altitude, datum, warm start, NMEA output mask, and baud selector.
- Contains helpers for baud and message-output configuration packets.

Important details:
- Default serial device is `/dev/eia0`.
- Position can be supplied with `-l`.
- `-n` chooses a new receiver baud rate while `-b` chooses current line baud.
- Uses shared GPS coordinate parsing and `%L` formatting.

Filesystem relevance:
- Indirect: controls serial device files used by GPS hardware.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/gps/gpsevermore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/gps/gpsfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/gps/gpsfs.c

This file implements `gpsfs`, a 9P filesystem exposing live GPS data.

Key behavior:
- Creates `/gps/time`, `/gps/position`, `/gps/satellites`, `/gps/stats`, and `/gps/raw`.
- Opens and configures a serial GPS stream.
- Background parser reads NMEA lines, checks checksums, parses common GPS sentence types, and updates the current fix.
- Exposes formatted current fix, time correlation, satellite table, parser statistics, and raw line ring buffer.
- Can periodically correct `#r/rtc` from GPS time.

Important details:
- Supports GGA, GLL, GSA, GSV, RMC, VTG, and some Rockwell/Astral proprietary messages.
- Maintains validation counters for bad/good/suspect latitude, longitude, and time.
- Raw buffer is 64 KiB and read through exclusive `raw` file mode.
- Estimates first-character timestamp from serial baud and bytes read.
- If serial control open fails, marks output as playback/invalid.

Filesystem relevance:
- Direct: synthetic 9P namespace translating serial GPS data into readable files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/gps/gpsfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/gps/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/gps/util.c

This file provides shared GPS coordinate formatting and parsing helpers.

Key behavior:
- Defines `nowhere`.
- Implements `%L` formatting for degrees/minutes/seconds with hemisphere suffixes.
- Parses latitude/longitude inputs with decimal or colon-separated degree/minute/second syntax.
- Supports explicit N/S/E/W suffixes and fallback positional latitude then longitude parsing.
- Contains an unused/static RTC correction helper.

Important details:
- Western longitude is made negative by default in the two-number fallback path.
- Duplicate lat or lon fields cause parse failure.

Filesystem relevance:
- Indirect support for GPS utilities and `gpsfs`; no filesystem operations except unused RTC helper.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/gps/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/lines.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/lines.c

This file copies complete newline-terminated lines from files or stdin to stdout.

Key behavior:
- Reads with `Brdline`.
- Writes each complete line as read.
- Processes stdin when no filenames are supplied.
- Opens and copies each named file otherwise.

Important details:
- Partial final lines without newline are not emitted by this implementation.
- Reports write and open errors with `sysfatal`.

Filesystem relevance:
- Indirect simple file utility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/lines.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/lis -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/lis

This is a short rc wrapper for `aux/listen`.

Key behavior:
- Runs `aux/listen -t /sys/src/cmd/aux tcp`.

Filesystem relevance:
- Indirect service-start helper using trusted service directory configuration.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/lis -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/listen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/listen.c

This file implements Plan 9's service listener supervisor.

Key behavior:
- Scans service directories for files named with the selected protocol prefix.
- Announces network addresses derived from service filenames.
- Accepts incoming calls and execs matching service programs.
- Supports trusted and untrusted service directories; untrusted listeners become user `none` and enter a new namespace.
- Periodically rescans service directories unless immutable mode is requested.

Important details:
- Disabled services are represented by missing or zero-length service files.
- Rejects service names containing `/`, beginning with `.`, or too long.
- Binds connection data to `/dev/cons` and dup's it to fd 0, 1, and 2 before exec.
- Logs service starts, calls, and errors to `listen`.
- Handles address-in-use failures without repeated noisy logs.

Filesystem relevance:
- Direct to Plan 9 service namespace conventions: discovers executable service files and uses network control/data files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/listen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/listen1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/listen1.c

This file implements a one-address listener that runs a supplied command per connection.

Key behavior:
- Announces a given network address.
- Optionally becomes user `none` unless trusted mode is selected.
- Accepts each call in a child process.
- Binds the connection's data file to `/dev/cons`, dup's the accepted fd to stdio, and execs the command.
- Optionally prints verbose call information.

Important details:
- Supports `-t` trusted and `-v` verbose.
- Falls back to executing `/bin/<cmd>` if direct exec fails.

Filesystem relevance:
- Indirect: service launcher built around Plan 9 network connection files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/listen1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/mklatinkbd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/mklatinkbd.c

This file converts keyboard composition data into a Latin keyboard table.

Key behavior:
- Parses `/lib/keyboard`-style lines containing Unicode code points and composition sequences.
- Builds a trie of byte sequences up to length two.
- Emits table rows sorted so longer prefix-dependent sequences appear before shorter ones.
- Can emit rune integer arrays with `-r` instead of wide string literals.

Important details:
- Warns on duplicate sequence definitions.
- Escapes generated C string bytes safely.
- Input defaults to stdin unless a file is provided.

Filesystem relevance:
- Indirect build utility for keyboard input tables.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/mklatinkbd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/mnihongo/mnihongo.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/mnihongo/mnihongo.c

This file post-processes troff output to render Japanese glyphs as embedded PostScript imagemasks.

Key behavior:
- Parses troff device-independent output commands.
- Tracks horizontal/vertical position and current font.
- Detects the Japanese font slot from `x f` device-control commands.
- For characters in that font, renders the glyph from a Plan 9 bitmap font into a GREY1 image and emits PostScript bitmap commands.
- Passes other troff commands through.

Important details:
- Uses `/lib/font/bit/pelm/unicode.9x24.font`.
- Requires `initdraw`, so it depends on draw/display/font facilities.
- Handles motion, page, font, draw, comment, and device-control commands.

Filesystem relevance:
- Indirect document-output filter; uses font files but no filesystem implementation logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/mnihongo/mnihongo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/mouse.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/mouse.c

This file probes and configures serial and PS/2 mouse devices.

Key behavior:
- Writes to `/dev/mousectl` to configure the detected mouse type.
- For serial mice, opens `#t/eiaNctl` and `#t/eiaN`, toggles RTS/DTR, tests protocol responses, and sets line parameters.
- Detects Microsoft-compatible, Logitech/type C, and type W mice.
- Can change baud rates where supported.
- Supports explicit defaults, debug tracing, and no-set mode.

Important details:
- Uses alarms to bound serial reads/writes.
- Retries detection up to six times.
- Type W 9600 baud is only used when receiver configuration indicates support.
- `ps2*` arguments are passed directly to `/dev/mousectl`.

Filesystem relevance:
- Indirect: configures Plan 9 device files for mouse input.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/mouse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/ms2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/ms2.c

This file converts executable or binary data to Motorola S-record output.

Key behavior:
- Reads Plan 9 executable headers through `mach.h` unless binary mode is selected.
- Emits text and data segments, or only data segment with `-d`.
- Supports S1, S2, and S3 record widths.
- Can output raw binary file contents as S-records.
- Optionally halfword-swaps data before emitting.

Important details:
- Default record payload size is 32 bytes.
- `-a` selects start address and `-p` page-aligns data after text.
- Emits S9/S7 termination records unless suppressed.

Filesystem relevance:
- Indirect binary conversion utility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/ms2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/msexceltables.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/msexceltables.c

This file parses Microsoft Excel BIFF workbook streams and dumps worksheet tables as text.

Key behavior:
- Reads BIFF records, dispatching on selected opcodes.
- Handles numbers, RK/MULRK values, labels, shared strings, booleans, errors, column widths, XF formats, date mode, BOF/EOF, and author/codepage metadata.
- Stores cells in sorted row/column linked lists per sheet.
- Outputs delimited, optionally quoted table rows with padding/truncation based on column widths.
- Supports worksheet/column range filters and dumping non-worksheet sheet types.

Important details:
- Supports BIFF8 Unicode strings and continuation records.
- Converts some built-in Excel number formats to date/time/percent/scientific text.
- Excel date conversion intentionally follows Excel's historical 1900 leap-year compatibility behavior.
- Default delimiter is a space; options control debug, all sheets, quoting, padding, truncation, delimiter, columns, and worksheets.

Filesystem relevance:
- Indirect: document stream parser intended for files exposed from compound documents, not filesystem implementation code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/msexceltables.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/mswordstrings.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/mswordstrings.c

This file extracts rough plain text from a Microsoft Word `WordDocument` stream.

Key behavior:
- Defines and reads an auto-generated subset of the Word FIB header.
- Seeks from `fcMin` to `fcMac`.
- Emits text bytes while translating common Word control characters to newlines, tabs, field markers, or placeholder strings.
- Prints placeholders for pictures, footnotes, animation, line numbers, drawn objects, and date/time fields.

Important details:
- Intended usage references `/mnt/doc/WordDocument`, implying use after mounting/extracting an OLE document.
- Contains comments noting incomplete handling of mixed zero-padded text and special characters.
- Does not parse full Word piece tables or formatting.

Filesystem relevance:
- Indirect document stream extractor; consumes a file from a mounted document namespace.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/mswordstrings.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/na/na.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/na/na.h

This header declares patch metadata and a script fixup routine for the `na` auxiliary code.

Key behavior:
- Defines `struct na_patch` with longword offset and patch type.
- Declares `na_fixup`, which patches a script using physical addresses, a patch table, and an external-value callback.

Filesystem relevance:
- Indirect: small support header, no filesystem implementation logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/na/na.h -->