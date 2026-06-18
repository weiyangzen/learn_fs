# subset-b-007023 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/cfs.cc -->
# sources/distributed-fs/coda/coda-src/vtools/cfs.cc

## Purpose

`cfs.cc` implements the primary Coda client administration command, `cfs`. It is a table-driven CLI that dispatches subcommands to Venus `pioctl` operations for cache management, volume state inspection, ACL changes, mount point handling, disconnected operation controls, reintegration, local-repair actions, and version-vector conflict manipulation.

## Important APIs, Types, and Functions

The central API is `struct command cmdarray[]`, whose entries bind command names, abbreviations, handler functions, usage text, help text, and optional danger prompts. `main()` uses `findslot()` and invokes the selected `PFV3` handler. Shared helpers include `simple_pioctl()`, `repair_pioctl()`, `pioctl_GetFid()`, `pioctl_SetVV()`, `parseHost()`, `getlongest()`, `dirincoda()`, ACL helpers `parseacl()`, `fillrights()`, `getrights()`, and closure helpers `doclosure()`, `findclosures()`, and `validateclosurespec()`. The command handlers cover `_VIOCCKSERV`, `_VIOC_CHECKPOINTML`, `_VIOC_CLEARPRIORITIES`, `_VIOC_REDIR`, `_VIOC_DISCONNECT`, `_VIOC_RECONNECT`, `_VIOC_FLUSHCACHE`, `_VIOCFLUSH`, `_VIOC_FLUSHVOLUME`, repair pioctls, ASR pioctls, fid/path lookup, mount pioctls, ACL get/set, volume status get/set, CML purge/sync/write-disconnect settings, lookaside cache management, and HDB/local-repair repair commands.

## Control Flow

Execution is linear: parse a subcommand, optionally ask the user to confirm dangerous operations through `brave()`, then run the handler. Most handlers validate argument count, populate `struct ViceIoctl`, call `pioctl()`, and print either structured output or `perror()` diagnostics. Multi-object commands loop over paths or fids and continue after per-item failures. `ListVolume()` decodes Venus' packed volume-status buffer in field order. `ListCache()` asks Venus to write results to a temporary file, then copies and unlinks that file. Closure replay/examination parses closure filenames, validates the target volume root, changes directory there, then shells out to `tar tvf` or `tar xvf`.

## State and Persistence Behavior

The program itself keeps only process-local buffers, mostly the global `piobuf`. Persistent effects are delegated to Venus or the filesystem: cache flushes, disconnection state, CML checkpoint/purge/reintegration, volume quota, ACLs, mount points, repair exposure, version-vector flags, local record preservation/discard, lookaside database state, and zone limits. `ListCache()` and local-repair listing create transient Venus output files and delete them after copying. Closure replay extracts tar content into the selected Coda volume root and may delete the closure with `-r`.

## Dependencies and Integration Points

The file depends on Coda headers and ABI contracts from `venusioctl.h`, `vice.h`, `prs.h`, `codaconf.h`, `inconsist.h`, and platform networking/filesystem headers. It is tightly coupled to Venus `pioctl` opcodes and output buffer layouts, Coda fid/version-vector structures, Coda ACL bit masks, `/usr/coda/spool` closure naming, `venus.conf` `checkpointdir`, and build-time `SYSTYPE`/`CPUTYPE` definitions.

## Risks

Several handlers mutate high-risk state and are guarded only by an interactive prompt or usage text. Fixed-size `sprintf()`, `strcpy()`, and global buffer packing can overflow if Venus or user inputs exceed expected sizes. `dirincoda()` changes process cwd and does not restore it on all paths. Closure replay builds shell commands with filenames, exposing command-injection risk for hostile closure names. ACL parsing allocates entries without cleanup, acceptable for short CLI lifetime but fragile in libraries. Some packed-buffer decoders assume exact Venus layout and integer sizes. `GetPFid()` and `GetPath()` parse fids with `%x` into Coda fields and append realm strings into `piobuf` without length checks. `ListCache()` opens output with `O_EXCL`, so repeated paths fail instead of replacing. Several comments mark commands as untested or dubious.

## Test Signals

Useful tests include command-table abbreviation dispatch, usage errors, confirmation bypass/decline behavior, ACL round-trip parsing and rights encoding, fid string parsing with malformed realms, mocked `pioctl()` input/output packing for each handler, volume-status buffer decoding, mount path edge cases, `lookaside` command construction at buffer limits, closure filename validation, and integration tests against a test Venus for cache, ACL, mount, repair, write-disconnect, and reintegration commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/cfs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/cmon.cc -->
# sources/distributed-fs/coda/coda-src/vtools/cmon.cc

## Purpose

`cmon.cc` is a curses-based Coda server monitor. It periodically binds to one or more Coda file servers, calls `ViceGetStatistics`, and renders per-server CPU, RPC, uptime, binding, workstation, and disk utilization counters.

## Important APIs, Types, and Functions

`struct server` stores per-server LWP id, name, clock tick rate, curses window, bind/probe timestamps, state, and old/new `ViceStatistics`. `struct printvals` contains the computed display values. `main()` initializes curses and RPC2/LWP, creates one `srvlwp()` per server plus `kbdlwp()`, and waits indefinitely. `GetArgs()` parses `-t`, `-a`, `-c`, and `server[:hz]`. `InitRPC()` initializes LWP, SFTP, and RPC2 with IPv6 option support. `srvlwp()` manages `RPC2_NewBinding`, `ViceGetStatistics`, state transitions, and unbinds. `ComputePV()` converts raw counters into absolute or relative display values. `PrintServer()`, `DrawCaptions()`, `when()`, `CmpDisk()`, `ValidServer()`, and `ShortDiskName()` support rendering and validation.

## Control Flow

After setup, each server LWP loops forever. If dead, it attempts an RPC2 binding to the `codasrv` UDP service and `SUBSYS_SRV`; when bound, it snapshots old statistics, fetches new statistics, derives tick rate from `Spare4` if needed, and prints the server column. The keyboard LWP waits on stdin and toggles absolute or relative display with `a` and `r`, then clears/redraws the active window.

## State and Persistence Behavior

State is in memory only: server status, counters, timestamps, and curses windows. There is no durable persistence. In debug builds it writes `/tmp/cmon_dbg`; otherwise RPC2 logs are sent to `/dev/null`. Runtime control is interactive through keypresses.

## Dependencies and Integration Points

It integrates with Coda's RPC2, SFTP, LWP, `ViceGetStatistics`, `ViceStatistics`, `ViceDisk`, `coda_getservbyname`, and `coda_getaddrinfo`, plus curses/ncurses. It assumes server statistics fields and service naming remain compatible.

## Risks

`main()` passes the address of loop variable `i` into each `LWP_CreateProcess`, so LWP startup timing can cause multiple workers to observe the same index. The UI assumes 24-row windows and fixed column widths. Counter differences are unsigned-style arithmetic over fields that may wrap. `ComputePV()` assumes 10 disk slots. Signal cleanup only handles `SIGINT`; other failures can leave terminal modes dirty. Server names are mutated in-place when parsing `server[:hz]`.

## Test Signals

Tests should cover argument parsing, `ValidServer()` failure handling, absolute/relative `ComputePV()` math including zero totals and counter wrap, disk sorting, short-name truncation, and a mocked RPC2/Vice statistics loop. Manual integration tests need live Coda servers and terminal resize/interrupt checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/cmon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/coda_replay.cc -->
# sources/distributed-fs/coda/coda-src/vtools/coda_replay.cc

## Purpose

`coda_replay.cc` replays or lists Coda closure streams encoded as tar-like records with Coda-specific operations in the tar `linkflag` field. It can execute the stream, list it without changes, or reject deprecated stripping behavior.

## Important APIs, Types, and Functions

Global flags `rflag`, `sflag`, `tflag`, `vflag`, `hflag`, and `trailers` drive mode. `main()` requires exactly one of replay/list/deprecated strip mode and reads from stdin or a named file. `ValidateHeader()` parses octal metadata, validates operation kind, logs records under verbose/list modes, detects trailers, and verifies checksum. `HandleRecord()` applies operations for `STOREDATA`, `LINK`, `SYMLINK`, `STORESTATUS`, `REMOVE`, `RENAME`, `MKDIR`, and `RMDIR`. Helpers `checksum()`, `makeprefix()`, `setmode()`, `setowner()`, `setlength()`, `settimes()`, `readblock()`, `writeblock()`, and `usage()` implement tar-block I/O and filesystem effects.

## Control Flow

The tool reads 512-byte headers until two empty trailer records are seen. Every header is validated before handling. In replay mode, data records create parent directories, redirect `stdout` to the target file, copy full tar blocks, close the file, and apply metadata. Other operations call POSIX link, symlink, truncate, chmod, chown, utimes, unlink, rename, mkdir, or rmdir. In list mode, it validates and logs but helper functions suppress mutations because they check `rflag`.

## State and Persistence Behavior

Replay mode mutates the current filesystem tree according to the stream: creates directories/files/links, removes names, renames paths, changes mode/owner/timestamps, and truncates status-only records. There is no checkpointing or rollback. Non-harsh mode logs some failures and continues; harsh mode exits on supported errors.

## Dependencies and Integration Points

It depends on `coda_replay.h` for the tar header layout and operation constants, and POSIX file APIs. It is used by Coda repair/reintegration closure workflows that need non-tar operations represented in otherwise tar-like streams.

## Risks

Input paths are trusted and can write outside the intended directory if the stream contains absolute paths or `..`. `STOREDATA` writes whole 512-byte blocks and does not call `setlength()`, so non-block-aligned file sizes can retain tar padding unless upstream formats avoid this. It uses `freopen()` on global `stdout`, making error handling and further diagnostics fragile. UID/GID and octal size parsing use `uint32_t`, limiting large sizes. `makeprefix()` modifies the path buffer in place. There is no symlink traversal protection, atomicity, or replay transaction boundary.

## Test Signals

Tests should feed synthetic blocks for every `linkflag`, bad checksums, malformed operation codes, one and two trailer records, non-multiple-of-512 data sizes, harsh versus non-harsh failures, path traversal inputs, metadata changes, and list mode no-op behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/coda_replay.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/coda_replay.h -->
# sources/distributed-fs/coda/coda-src/vtools/coda_replay.h

## Purpose

`coda_replay.h` defines the tar-compatible block layout and Coda-specific operation codes consumed by `coda_replay.cc`.

## Important APIs, Types, and Functions

It defines `TBLOCK`, `NBLOCK`, `NAMSIZ`, and union `hblock`, whose `header` view contains tar fields `name`, `mode`, `uid`, `gid`, `size`, `mtime`, `chksum`, `linkflag`, and `linkname`. It maps `linkflag` values to operations: `STOREDATA`, `LINK`, `SYMLINK`, `STORESTATUS`, `REMOVE`, `RENAME`, `MKDIR`, and `RMDIR`.

## Control Flow

This header has no execution flow. Consumers interpret each 512-byte `hblock` as either a tar header, data block, or trailer block.

## State and Persistence Behavior

No state is stored here. Persistence semantics are determined by consumers that replay the encoded operations.

## Dependencies and Integration Points

The structure mirrors historical tar headers while extending `linkflag` beyond standard tar values. It is an ABI contract between closure producers and replay consumers.

## Risks and Test Signals

The layout assumes 512-byte packing and 100-byte path/link fields. Long names, large sizes, and nonstandard tar variants require producer-side handling. Tests should assert `sizeof(hblock) == TBLOCK`, operation constants, checksum compatibility, and compatibility with the replay parser.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/coda_replay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/codacon.cc -->
# sources/distributed-fs/coda/coda-src/vtools/codacon.cc

## Purpose

`codacon.cc` is a text monitor for Venus mariner events. It connects to the local Venus mariner socket, requests fetch/store event reporting, suppresses selected completion noise, appends timestamps, and prints human-readable event messages.

## Important APIs, Types, and Functions

`main()` parses `-tcp` and optional host, repeatedly connects, sends `set:fetch`, and calls `CheckMariner()`. `Bind()` chooses either the configured Unix-domain `marinersocket` from `venus.conf` or a TCP connection to service `venus` using `coda_getaddrinfo`. `CheckMariner()` buffers input lines up to `MARINERBUFSIZE`, trims trailing spaces, appends current local time, and calls `CheckTheMariner()`. `CheckTheMariner()` splits optional `prefix::message` records and filters `fetch`, `store`, and `mond` messages containing ` done `.

## Control Flow

The program loops forever. A failed bind sleeps five seconds and retries. A successful bind is wrapped with `fdopen()`, configured by writing `set:fetch\n`, then read until EOF. When Venus disconnects, the stream is closed and the outer loop reconnects.

## State and Persistence Behavior

It keeps only transient socket and line-buffer state. It does not persist data, but it can keep reconnecting indefinitely and continuously writes to stdout.

## Dependencies and Integration Points

It integrates with Venus' mariner Unix/TCP control protocol, `venus.conf`, `codaconf_lookup`, service name `venus`, and Coda RPC2 address wrappers.

## Risks and Test Signals

The optional `host` argument is accepted but not actually used by TCP `Bind()`, which calls `coda_getaddrinfo(NULL, "venus", ...)`. The Unix socket path is copied into `sockaddr_un.sun_path` without bounds checking. Static line buffering truncates long records near the end. Tests should mock mariner input, verify prefix filtering/timestamp formatting, exercise reconnect paths, and cover Unix/TCP address selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/codacon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/codaconfedit.c -->
# sources/distributed-fs/coda/coda-src/vtools/codaconfedit.c

## Purpose

`codaconfedit.c` is a small configuration-file lookup and rewrite utility for Coda config files. It locates a config file, optionally copies a `.ex` template, reads variable values, and rewrites variables while preserving nearby comments and older definitions.

## Important APIs, Types, and Functions

`main()` implements three modes: print resolved config path, print variable value, or set variable value. `write_val()` emits `name="value words"` lines. `match_var()` recognizes variable assignments with leading whitespace. `do_rewrite()` writes a `.bak`, writes a `.new` with previous active assignments commented out, inserts the new value after the last related line, and renames `.new` over the original. `copy_template()` locates `<confbase>.ex` using `codaconf_file()` and copies it with `copyfile_byname()`.

## Control Flow

The utility resolves the config path with `codaconf_file()`. Missing files in set/lookup modes trigger template copying. For reads, it initializes only that config file and calls `codaconf_lookup()`. For writes, it compares the existing value to the requested argv words and skips rewriting if already equal; otherwise it performs the two-pass rewrite.

## State and Persistence Behavior

It writes `<conffile>.bak`, `<conffile>.new`, and finally replaces the target config file. It sets `umask(022)` for the generated file. It may create a real config from a template even for lookup, so a read-like operation can persist data.

## Dependencies and Integration Points

It depends on Coda `codaconf_file`, `codaconf_init_one`, `codaconf_lookup`, and the local `copyfile` helper. It assumes Coda config syntax of `key=value` with optional quotes.

## Risks and Test Signals

`MAXLINELEN` truncates long lines during rewrite. `write_val()` does not escape quotes or shell metacharacters in values. The value comparison loop references `argv[i]` through `i <= argc`, which can read one past the final valid argument. `rename()` replacement is not followed by permission/ownership preservation. Tests should cover missing templates, long lines, comments, multiple existing definitions, quoted values, idempotent set, write failures, and values containing quotes or spaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/codaconfedit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/gcodacon.in -->
# sources/distributed-fs/coda/coda-src/vtools/gcodacon.in

## Purpose

`gcodacon.in` is a Python/GTK graphical monitor for Coda client volume and reintegration state. It listens to Venus mariner `volstate` events, displays per-volume state in a GTK tree, changes the application icon, and optionally emits desktop notifications.

## Important APIs, Types, and Functions

`State` defines state descriptions, notification urgency, colorized XPM icon variants, and predicates over CML count plus flags. `parse_codaconf()` reads `/etc/coda/venus.conf`. `MarinerListener` connects to the mariner socket or TCP service, sends `set:volstate`, and dispatches complete lines. `VolumeList` wraps `Gtk.ListStore` with state lookup/update helpers. `VolumeView` renders icon, realm, volume, and state columns. `GlobalState` throttles notifications via `NOTIFICATION_INTERVAL`. `App` wires the mariner listener to GTK widgets, filters clean volumes, handles context menu actions, parses `volstate::...` messages, and computes aggregate status.

## Control Flow

Startup parses CLI options, builds the GTK UI, optionally starts a test timer, otherwise initializes the mariner connection. Mariner reconnect attempts run through GLib timeouts. Readable socket events append bytes to `self.buf`, split newline-delimited messages, update volume rows, then recompute global state and notifications. Right-click opens a menu for dirty-only filtering, notifications, about, and quit.

## State and Persistence Behavior

Runtime state lives in GTK models, the current global state, pending notification messages, and the socket buffer. There is no durable persistence. It reads `venus.conf` to locate the Unix socket and consumes live mariner data.

## Dependencies and Integration Points

It depends on Python GI bindings for Gtk 3, Gdk, GdkPixbuf, GLib, GObject, and Notify; Venus mariner protocol; `/etc/coda/venus.conf`; and service name `venus` for TCP mode. The script template uses `@PYTHON@` substitution.

## Risks

`VolumeList.values()` uses `STATES(row[1])` instead of indexing and appears broken if called. In `App.data_ready()`, `self.vols.__delitem__(vol)` is subject to Python name mangling inside the `App` class and should be `del self.vols[vol]`; deleted-volume events can fail. `parse_codaconf()` does not close files explicitly and handles only simple unescaped quoted values. Mariner bytes are decoded as ASCII, so non-ASCII paths can fail. Socket reconnects do not close failed sockets in all paths. The deprecated status-icon menu callback code suggests GTK API drift risk.

## Test Signals

Tests should cover state-priority ordering, each `volstate` regex branch, dirty-only filtering, deleted-volume handling, mariner reconnect behavior, notification throttling, config parsing, ASCII decode failures, and `--test` state cycling. Manual tests need a running Venus and desktop notification daemon.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/gcodacon.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/hoard.cc -->
# sources/distributed-fs/coda/coda-src/vtools/hoard.cc

## Purpose

`hoard.cc` implements the Coda hoard database front-end. It parses user commands for hoard-priority entries and sends HDB pioctls to Venus to clear, add, delete, list, walk, verify, enable, or disable hoard database behavior.

## Important APIs, Types, and Functions

The file defines wrapper classes around HDB messages: `clear_entry`, `add_entry`, `delete_entry`, `listentry`, `walk_entry`, `enable_entry`, `disable_entry`, and `verify_entry`. `ParseCommandLine()` chooses command input from `-f`, stdin, or direct argv text. `ParseHoardCommands()` tokenizes and builds `olist` queues. `canonicalize()`, `vol_getwd()`, and `GetVid()` resolve paths to Coda volume id, realm, and volume-relative name. `MetaExpand()` and `ExpandNode()` expand children/descendants. `DoClears()`, `DoAdds()`, `DoDeletes()`, `DoLists()`, `DoWalks()`, `DoVerifies()`, `DoEnables()`, and `DoDisables()` execute pioctls. `RenameOutFile()` copies Venus output files to user targets under the real UID.

## Control Flow

Startup parses input, records cwd and uid, parses all commands into separate lists, initializes `venus.conf`, then executes lists in a fixed order: clear, add, delete, list, walk, verify, enable, disable. Parser commands support abbreviations: `clear`, `add`, `delete`, `list`, `walk`, `verify`, `on`, and `off`. Adds canonicalize the target, parse priority/attribute fields such as children/descendants/inherit, optionally meta-expand, and append symlink entries discovered during canonicalization.

## State and Persistence Behavior

Durable state changes are in Venus' hoard database through `_VIOC_HDB_*` pioctls. List and verify ask Venus to write temporary output files and then copy them to user-requested destinations. `walk`, `on`, and `off` affect hoard-walk execution. The tool changes directories during canonicalization and expansion but attempts to return to the original cwd.

## Dependencies and Integration Points

It depends on Coda `venusioctl.h`, `hdb.h`, `vice.h`, `codaconf.h`, `olist`, `pioctl`, `VolumeId`, `ViceFid`, and Coda symlink limits. It also depends on Unix process APIs, `cat`, real/effective uid behavior, and Coda mountpoint configuration.

## Risks

The code uses `tmpnam()` for output files, which is race-prone. Many `strcpy()`/`strcat()` operations assume `MAXPATHLEN` bounds. `canonicalize()` manually follows symlinks and can loop or overflow with hostile paths. `ExpandNode()` constructs `tname` for each child but recursively calls `ExpandNode(..., name, ...)` rather than `tname`, likely breaking descendant expansion and potentially recursing incorrectly. `RenameOutFile()` forks and execs `cat` instead of copying directly. Parser memory allocated with `new` is not released, acceptable for process lifetime but not reusable. Commands that partly fail continue, so batch updates can leave mixed HDB state.

## Test Signals

Tests should cover command parsing, priority/attribute combinations, canonicalization of absolute/relative paths and symlinks, volume-boundary detection, meta-expansion over children/descendants, HDB message packing, output copy failure paths, uid switching, and partial-failure behavior. Integration tests need a Coda mount and Venus HDB pioctl support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/hoard.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/logbandwidth.in -->
# sources/distributed-fs/coda/coda-src/vtools/logbandwidth.in

## Purpose

`logbandwidth.in` is a Tcl/Tk/Tix strip-chart monitor for Venus connection bandwidth messages.

## Important APIs, Types, and Functions

It maintains three rolling 200-sample lists, a canvas, and label state. `strip_draw()` logs current values, draws logarithmic vertical bars for three bandwidth measures, labels modem/ISDN/Wavelan/Ethernet/Fast Ethernet scale lines, and reschedules itself. `updatestats()` reads mariner socket lines. `checkline()` matches `connection::bandwidth` messages for an optional peer filter and updates graph values plus bit-per-second label.

## Control Flow

The script creates UI elements, connects to `localhost venus`, sends `set:fetch`, configures nonblocking reads with `fileevent`, and starts periodic drawing every 100 ms.

## State and Persistence Behavior

All state is in Tcl globals. No files are written. It consumes live Venus mariner messages and renders transient UI history.

## Dependencies and Integration Points

It requires `+TIXWISH+`, Tcl/Tk/Tix, a resolvable `venus` service, and mariner `set:fetch` bandwidth events.

## Risks and Test Signals

The graph uses `log10()` and clamps values below 100, hiding low-rate detail. Socket disconnect exits immediately. Parsing is based on positional `lindex` fields. Tests can feed mock lines into `checkline`, verify clamping and label math, and simulate EOF handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/logbandwidth.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/logcmls.in -->
# sources/distributed-fs/coda/coda-src/vtools/logcmls.in

## Purpose

`logcmls.in` is a Tcl/Tk/Tix strip-chart monitor for reintegration queue size. It visualizes active and inactive CML entries reported by Venus.

## Important APIs, Types, and Functions

It stores two 200-sample logs and draws stacked vertical bars on a canvas. `strip_draw()` rescales to the current maximum combined count. `updatestats()` handles nonblocking socket reads. `checkline()` parses `reintegrate::<volume>, <active>/<total>` and updates active, inactive, title, and label text.

## Control Flow

The script initializes the chart, connects to `localhost venus`, sends `set:fetch`, registers a readable callback, and repeatedly redraws.

## State and Persistence Behavior

State is in process-local Tcl variables only. It does not persist data or change Coda state.

## Dependencies and Integration Points

It depends on Tix, the `venus` socket service, and Venus mariner reintegration messages.

## Risks and Test Signals

Malformed numeric fields can break `expr`. The dynamic scale can make historical values visually jump. Disconnect exits instead of reconnecting. Tests should feed representative reintegration lines, zero totals, one-change labels, malformed lines, and EOF behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/logcmls.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/logprogress.in -->
# sources/distributed-fs/coda/coda-src/vtools/logprogress.in

## Purpose

`logprogress.in` is a Tcl/Tk/Tix meter for fetch progress messages from Venus.

## Important APIs, Types, and Functions

The script creates a label and `tixMeter`. `updatemeter()` reads mariner lines and matches `progress::fetching (<path>) <percent>x`, converting percent to a 0.0-1.0 meter value and updating the label.

## Control Flow

It connects to `localhost venus`, sends `set:fetch`, makes the socket nonblocking, registers a readable callback, and updates the meter when matching fetch progress lines arrive.

## State and Persistence Behavior

It stores only the last meter value in process memory. It does not write files or alter Coda state.

## Dependencies and Integration Points

It requires Tcl/Tk/Tix, the `venus` service, and Venus mariner fetch progress message format.

## Risks and Test Signals

The regex accepts arbitrary percent text and relies on `expr double(...)`. It exits on EOF with no reconnect. Tests should cover valid progress lines, nonmatching lines, percent bounds, unusual paths, and EOF handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/logprogress.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/logreintegration.in -->
# sources/distributed-fs/coda/coda-src/vtools/logreintegration.in

## Purpose

`logreintegration.in` is a Tcl/Tk/Tix progress meter for reintegration fragment upload progress.

## Important APIs, Types, and Functions

It creates a label and `tixMeter`. `updatemeter()` reads Venus mariner lines, matches `store::SendReintFragment ...(<offset>/<size>)`, maps offset to a fraction, treats `-1` as zero, and sets full completion when `store::CloseReintHandle` appears.

## Control Flow

The script connects to `localhost venus`, sends `set:fetch`, registers a nonblocking readable callback, and updates the meter on reintegration store messages.

## State and Persistence Behavior

Only current meter value is in memory. It has no durable persistence and does not mutate Coda state.

## Dependencies and Integration Points

It depends on Tcl/Tk/Tix, the `venus` service, and specific Venus mariner store/reintegration message strings.

## Risks and Test Signals

Division by zero is possible if message size is zero. The parser is tightly coupled to message text and exits on disconnect. Tests should cover normal fragments, offset `-1`, close handle completion, zero/malformed sizes, and nonmatching lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/logreintegration.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/mkcodabf.c -->
# sources/distributed-fs/coda/coda-src/vtools/mkcodabf.c

## Purpose

`mkcodabf.c` converts a large regular file into a Coda "big file" directory containing numbered data hunks and a `_Coda_BigFile_` metadata marker.

## Important APIs, Types, and Functions

Global options include `hunksize`, `hunkbytes`, `filesperdir`, `dirdigits`, and `verbose`. `main()` parses `-f`, `-s`, and `-v`, validates source and destination, creates the target directory, and calls `mkbigfile()`. `mkbigfile()` computes required hunk count and directory levels, creates one or two levels of numbered subdirectories, writes each chunk file as mode `0444`, and writes `_Coda_BigFile_` with `CDBGFL00 <size> <hunksize> <filesperdir> <files>`.

## Control Flow

The converter refuses non-regular files, too-small files, existing destinations, hunk sizes below 1 MB, and files requiring more than two directory levels. It streams the source file sequentially into 8192-byte buffers and writes chunks into deterministic numeric paths.

## State and Persistence Behavior

It creates a directory tree and read-only chunk files at the destination. On failure after destination creation, it exits without cleanup, leaving partial big-file state.

## Dependencies and Integration Points

It depends on POSIX stat/open/read/write/mkdir and Coda's big-file directory convention. Consumers must understand `_Coda_BigFile_`.

## Risks and Test Signals

`hfd` is declared `long` but stores file descriptors. `read()` returning zero before `temp` reaches zero would spin because `temp` is not decremented. Directory creation loops use `<= files / filesperdir`, which can create extra directories at exact boundaries. Existing partial destinations are not rolled back. Tests should cover exact hunk multiples, tiny files, maximum `filesperdir`, two-level layout, read/write short counts, metadata content, and cleanup expectations after failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/mkcodabf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/spy.cc -->
# sources/distributed-fs/coda/coda-src/vtools/spy.cc

## Purpose

`spy.cc` connects to Venus mariner and prints reports of open files, optionally filtered by uid.

## Important APIs, Types, and Functions

`main()` parses `-host`, `-tcp`, and `-uid`, calls `Bind()`, sends `reporton` or `reporton <uid>`, installs a SIGTERM flush handler, and reads events. `Bind()` chooses Unix-domain mariner socket from `venus.conf` unless `-tcp` is set; TCP mode resolves service `venus`. `CheckMariner()` buffers newline-terminated records up to `MAXPATHLEN` and prints them. `TERM()` flushes stdout/stderr and exits.

## Control Flow

Unlike `codacon`, it does not reconnect. A bind or command write failure exits. Once connected, it blocks in `CheckMariner()` until EOF.

## State and Persistence Behavior

The tool keeps only socket, stream, uid filter, and static input buffer state. It does not persist data or modify Coda state beyond sending the mariner reporting command.

## Dependencies and Integration Points

It depends on Venus mariner protocol, `venus.conf`, `codaconf_lookup`, `coda_getaddrinfo`, Unix sockets, and service name `venus`.

## Risks and Test Signals

As in `codacon`, `-host` is parsed but not used by TCP resolution. `sockaddr_un.sun_path` copying is unchecked. Line truncation occurs at `MAXPATHLEN - 2`. Only SIGTERM is handled; EOF just returns from the read loop and exits implicitly. Tests should mock `reporton` command selection, line buffering, uid option validation, bind failures, and long records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vtools/spy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vv/Makefile.am -->
# sources/distributed-fs/coda/coda-src/vv/Makefile.am

## Purpose

This Automake fragment builds the Coda version-vector helper library as an uninstalled libtool archive.

## Important APIs, Types, and Functions

It declares `noinst_LTLIBRARIES = libvv.la` and sets `libvv_la_SOURCES` to `inconsist.cc`, `inconsist.h`, `nettohost.cc`, and `nettohost.h`. `AM_CPPFLAGS` adds RPC2 flags and include paths for base and vicedep headers.

## Control Flow

There is no runtime flow. During build generation, Automake emits rules to compile the listed sources into `libvv.la`.

## State and Persistence Behavior

It affects build artifacts only. No runtime persistence.

## Dependencies and Integration Points

The library is private to the build and depends on RPC2, `lib-src/base`, and generated/source vicedep headers for Coda types such as `ViceVersionVector`.

## Risks and Test Signals

Missing generated vicedep headers or RPC2 flags will break compilation. Tests are build-oriented: run autoreconf/configure/make for this directory and link a consumer of `libvv.la`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vv/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vv/inconsist.cc -->
# sources/distributed-fs/coda/coda-src/vv/inconsist.cc

## Purpose

`inconsist.cc` implements Coda version-vector comparison, consistency checking, arithmetic, initialization, invalidation, maximum-vector synthesis, and formatting.

## Important APIs, Types, and Functions

It defines `NullSid`. `VV_Cmp_IgnoreInc()` compares vector slots and returns `VV_EQ`, `VV_DOM`, `VV_SUB`, or `VV_INC`. `VV_Cmp()` treats the `VV_INCON` flag as immediate inconsistency before delegating. `VV_Check()` and `VV_Check_IgnoreInc()` call `VV_Check_Real()` to find a dominant set in a `VSG_MEMBERS` pointer array. `VV_BruteForceCheck()` is a fallback when the fast pass sees conflicting dominance. `AddVVs()`, `SubVVs()`, `InitVV()`, `IsRunt()`, `InvalidateVV()`, `GetMaxVV()`, `SPrintVV()`, and `FPrintVV()` provide manipulation and display helpers.

## Control Flow

Comparison iterates all version sites and tracks whether one vector dominates or submits; mixed directions produce inconsistency. The fast group check chooses the first non-null vector as current dominator, scans forward, removes submissive vectors, updates the dominator when needed, or switches to brute force on inconsistency. The brute-force path searches for a vector that dominates or equals all others, nulling submissive entries when equality is not required.

## State and Persistence Behavior

All functions operate on caller-provided structs and arrays. There is no persistence. Some checks mutate the input pointer array by nulling non-dominant entries, which is part of the API contract.

## Dependencies and Integration Points

It depends on `ViceVersionVector`, `ViceStoreId`, `VSG_MEMBERS`, and flag macros from `inconsist.h`, plus Coda/RPC2 integer layout. It is used by repair/conflict logic and tools such as `cfs` for version-vector display and manipulation.

## Risks

`VV_Check_*` mutates `vvp`, so callers must pass a scratch array if they need the original list. `SPrintVV()` has a compile-time assumption that `VSG_MEMBERS == 8`. Arithmetic helpers do not check overflow or underflow. `GetMaxVV()` picks store ids based on `domindex` conventions that callers must understand. `IsRunt()` treats an inconsistency-only zero vector as runt, which is deliberate but subtle.

## Test Signals

Tests should cover equality, dominance, submission, mixed inconsistency, explicit incon flags, ignore-incon behavior, equality-required checks, null vector slots, dominant-set mutation, brute-force fallback cases, max-vector store-id selection for `-1`, `-2`, and explicit indices, runt detection, invalidation, and formatted output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vv/inconsist.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vv/inconsist.h -->
# sources/distributed-fs/coda/coda-src/vv/inconsist.h

## Purpose

`inconsist.h` declares Coda version-vector consistency APIs and flag macros.

## Important APIs, Types, and Functions

It defines `VV_Cmp_Result` values `VV_EQ`, `VV_DOM`, `VV_SUB`, and `VV_INC`. It defines flags `VV_INCON`, `VV_LOCAL`, `VV_BARREN`, and `VV_COP2PENDING`, plus macros to test, set, and clear each flag. `SID_EQ()` compares `ViceStoreId` values. It declares `NullSid`, comparison/check APIs, vector arithmetic/init/invalidate/max APIs, and print helpers.

## Control Flow

There is no runtime control flow in the header. Macros directly mutate the `Flags` member of a passed version-vector lvalue.

## State and Persistence Behavior

The macros mutate caller-owned `ViceVersionVector` values. No persistence exists in the header.

## Dependencies and Integration Points

It includes `vice.h` and `vcrcommon.h` for Coda version-vector and store-id types and is wrapped for C++ linkage compatibility.

## Risks and Test Signals

Macros evaluate their argument once syntactically as `(vv).Flags`, so callers must pass lvalues and understand mutation. Flag values are ABI-visible. Tests should compile from C and C++, verify flag operations, `SID_EQ`, and API linkage against `inconsist.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vv/inconsist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vv/nettohost.cc -->
# sources/distributed-fs/coda/coda-src/vv/nettohost.cc

## Purpose

`nettohost.cc` converts Coda store ids and version vectors between network byte order and host byte order.

## Important APIs, Types, and Functions

`ntohsid()` and `htonsid()` convert `ViceStoreId::HostId` and `Uniquifier`. `ntohvv()` and `htonvv()` iterate `VSG_MEMBERS` version slots starting at `Versions.Site0`, convert the embedded store id, and convert `Flags`.

## Control Flow

Each function is a straight field-by-field conversion from input pointer to output pointer. Input and output may be distinct; in-place use relies on assignment order being safe for each converted field.

## State and Persistence Behavior

There is no persistent state. The output struct is overwritten with converted values.

## Dependencies and Integration Points

It depends on `<netinet/in.h>` byte-order functions, `vice.h`, `inconsist.h`, and `nettohost.h`. It assumes version slots are contiguous `RPC2_Integer` fields.

## Risks and Test Signals

The code assumes `Flags` is the same width expected by `htonl`/`ntohl`. Layout assumptions would break if `ViceVersionVector` changes away from contiguous site fields. Tests should cover round-trip conversion, non-palindromic values, all `VSG_MEMBERS` slots, flags, store ids, and in-place conversion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vv/nettohost.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vv/nettohost.h -->
# sources/distributed-fs/coda/coda-src/vv/nettohost.h

## Purpose

`nettohost.h` declares byte-order conversion helpers for Coda store ids and version vectors.

## Important APIs, Types, and Functions

It declares `ntohsid`, `htonsid`, `ntohvv`, and `htonvv`, all using pointer parameters to `ViceStoreId` or `ViceVersionVector`.

## Control Flow

No runtime flow exists in the header.

## State and Persistence Behavior

No state is stored. Implementations overwrite caller-provided output objects.

## Dependencies and Integration Points

The header relies on the including translation unit already knowing `ViceStoreId` and `ViceVersionVector`; unlike `nettohost.cc`, it does not include `vice.h` itself.

## Risks and Test Signals

Consumers that include this header alone before Coda type definitions will fail to compile. Tests should include it in both normal library order and standalone-with-required-types order, and link against `nettohost.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/vv/nettohost.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/CMakeLists.txt -->
# sources/distributed-fs/eos/mgm/CMakeLists.txt

## Purpose

This CMake file defines the EOS MGM build: protobuf generation, the HTTP plugin, the main XRootD MGM plugin object library/module, tape garbage collection sources, CTA utility integration, admin/user command sources, REST/gRPC/FUSE/server components, install rules, and support executables/static Linux build targets.

## Important APIs, Types, and Functions

Major targets are `EosMgmProto-Objects`, `EosMgmHttp-Objects`, `EosMgmHttp-${XRDPLUGIN_SOVERSION}`, `XrdEosMgm-Objects`, `XrdEosMgm-${XRDPLUGIN_SOVERSION}`, `testschedulingtree`, `eos-config-inspect`, and Linux-only `XrdEosMgm-Static`. It uses `PROTOBUF_GENERATE_CPP` for `fusex.proto`, `set_source_files_properties(... HEADER_FILE_ONLY TRUE)` for command include fragments, `MGM_TGC_SRC_FILES` for tape garbage collection and `CtaUtils.cc`, and target link/compile definitions for XRootD, protobuf, gRPC, JSON, prometheus, LDAP, ZMQ, sparsehash, xxhash, EOS common/ns libraries, and daemon uid/gid definitions.

## Control Flow

CMake first establishes include paths, generates protobuf sources, builds an object library for protocol code, builds HTTP object/module targets, defines common MGM tape-GC sources, marks command `.inc` files as header-only, builds the large `XrdEosMgm-Objects` object library from many subsystem sources plus generated fusex sources, wraps it in an XRootD module, installs modules and tools, and conditionally builds Linux static/test support.

## State and Persistence Behavior

The file controls build artifacts and install destinations. It does not define runtime persistence directly, but it chooses which runtime subsystems are compiled into the MGM plugin, including namespace, quota, recycle, CTA/tape, REST, gRPC, monitoring, bulk request, placement, and traffic shaping components.

## Dependencies and Integration Points

It is the central integration point for EOS MGM with XRootD plugin ABI, protobuf/gRPC generated code, EOS common/server/static libraries, CTA SSI protobuf objects, REST gateway objects, prometheus exporter, ZLIB, LDAP, ZMQ, JSONCPP, sparsehash, and Linux-specific static linking. `CtaUtils.cc` is included through `MGM_TGC_SRC_FILES`.

## Risks

The main object target has a very large source list, so missing files or stale renamed header-only implementations break configuration or linking. Generated protobuf sources are included in the object target and must be available before compile. Link dependencies differ between object, module, and static targets, so symbol availability can diverge. Compile definitions for daemon uid/gid are public and propagate. Linux-only static target may hide non-Linux build gaps. Manual include directories are broad and can mask include-order issues.

## Test Signals

Build tests should configure from a clean tree, verify protobuf generation, build `XrdEosMgm-Objects`, plugin modules, `eos-config-inspect`, `testschedulingtree`, and Linux static target, run install dry-runs, and check dependency closure after adding/removing MGM subsystem files. Runtime smoke tests should load the XRootD MGM module and exercise HTTP, REST, gRPC, CTA/tape, and config inspection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/CtaUtils.cc -->
# sources/distributed-fs/eos/mgm/CtaUtils.cc

## Purpose

`CtaUtils.cc` implements small EOS MGM utility functions used around CTA/tape integration: strict decimal `uint64_t` parsing, binary `timespec` reconstruction, and bounded file-descriptor reads into strings.

## Important APIs, Types, and Functions

`CtaUtils::toUint64(std::string)` trims the input, rejects empty strings, rejects any non-digit character, calls `std::stoull`, and maps exceptions to domain-specific `EmptyString`, `NonNumericChar`, `ParseError`, and `ParsedValueOutOfRange`. `CtaUtils::bufToTimespec(const std::string&)` checks `buf.size() == sizeof(timespec)`, then `memcpy`s into a `timespec`. `CtaUtils::readFdIntoStr(int fd, ssize_t maxStrLen)` rejects requests above a 4 GiB boundary, allocates a NUL-terminated buffer, reads once from the fd, throws on read errors, and returns a string copy.

## Control Flow

Each helper is synchronous and exception-based. `toUint64()` performs validation before conversion. `bufToTimespec()` fails before copying on size mismatch. `readFdIntoStr()` performs a single `read()` call, then NUL-terminates at either `readRc` or `maxStrLen`.

## State and Persistence Behavior

There is no stored state. `readFdIntoStr()` advances the supplied file descriptor's read offset and allocates temporary memory.

## Dependencies and Integration Points

It depends on `common/StringUtils.hh` for trimming, `mgm/CtaUtils.hh` for class and exception declarations, POSIX `read`, C++ strings/streams/limits/memory, and platform `timespec` ABI size.

## Risks

`readFdIntoStr()` reads only once, so it may return partial data from pipes, sockets, or large files even when more data is available. Negative `maxStrLen` is not explicitly rejected before allocation arithmetic. `bufToTimespec()` serializes native `timespec` layout, so data is not portable across architectures or libc ABIs. `toUint64()` rejects plus signs and whitespace inside values by design. The error text in `bufToTimespec()` says "does match" where it means "does not match."

## Test Signals

Tests should cover trim-only empty strings, non-digit rejection, maximum `uint64_t`, overflow, leading zeroes, valid and invalid `timespec` buffer sizes, native round-trip `timespec`, fd read errors, zero-length reads, partial pipe reads, and negative or huge `maxStrLen`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/CtaUtils.cc -->
