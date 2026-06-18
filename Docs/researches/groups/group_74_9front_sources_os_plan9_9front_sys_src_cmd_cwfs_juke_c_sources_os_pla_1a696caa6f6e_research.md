# Group Research: group_74_9front_sources_os_plan9_9front_sys_src_cmd_cwfs_juke_c_sources_os_pla_1a696caa6f6e

Scope checked against `Docs/research_subset_a.md`: these files are within `sources/os/plan9/9front`, which is included in subset A.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/juke.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/juke.c

Purpose: Implements cwfs support for SCSI optical jukeboxes, especially HP-style robotics with WORM/labeled-WORM sides. It bridges `Device` trees to a private `Juke` structure, controls medium movement, mounts sides into drives, and exposes block read/write/size operations.

Key structures:
- `Side`: per-disc-side state, including shelf element, drive slot, loaded/unloaded status, rotation side, ordinal label, timing, native block geometry, and Plan 9 block geometry.
- `Juke`: global jukebox state: side table, drive table, offline flags, robotics `Scsi*`, element geometry, rotation/double-sided flag, and linked-list membership.

Important behavior:
- `querychanger()` opens the changer through `sdof()`/`openscsi()`, installs SCSI target state with `newscsi()`, reads changer geometry, creates side records, and records initial positions.
- `jukeinit()` validates the `j(...)` device layout, registers console commands, attaches drive devices, and stores the `Juke*` in jukebox and side devices.
- `wormunit()` is the central loader. It locks a side, selects a drive with `bestdrive()`, moves media via `mmove()`, waits for drive readiness, opens the drive data file, discovers block geometry, and for labeled worms verifies the label.
- `wormlabel()` reads or writes the label block on `Devlworm`, checks `Labmagic`, detects byte-swapped labels, validates side ordinal, and calls `cmd_wormreset()`/`panic()` on serious mismatches.
- `wormread()`/`wormwrite()` translate cwfs logical blocks to `pread`/`pwrite` against the loaded drive, with bounds checks and error counters.
- `wormsizeside()` and `wormsidestarts()` walk composite device trees to map a side number to its size/start offsets, including jukes embedded inside mcat/mlev/mirror/cw devices.
- `wormprobe()` periodically unloads inactive spinning sides after `TWORM`.

Operational interfaces:
- Console commands: `wormreset`, `wormeject`, `wormingest`, `wormoffline`, `wormonline`.
- SCSI commands issued directly here include mode sense, read element status, and move medium.

Notable details:
- `SCSInone` is defined as `SCSIread` because move-medium has no payload but still uses the scsi wrapper.
- `bestdrive()` prefers a drive already holding the other side of the same platter, then an empty online drive, then the oldest eligible loaded drive.
- `wormsize()` hides the last block from `Devlworm` users because it stores the label.
- The file assumes serialized robotics changes through `Juke` and `Side` locks; label I/O temporarily unlocks the side because `wormread()` re-enters `wormunit()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/juke.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/main.c

Purpose: Main entry point for the user-mode cached-WORM file server. It parses options, initializes global configuration, posts 9P and command services, starts network/listener/server workers, and runs background copy/sync loops.

Key globals:
- `devmap`: optional device remapping table loaded from `-m`.
- `bin`: console input `Biobuf` used by confirmation prompts.
- `chatty`: diagnostic verbosity.
- `sfd`: stdio service fd for `-s`.

Important behavior:
- `confinit()` sets default counts for users, server workers, files, message buffers, path table size, and calls platform-specific `localconfinit()`.
- `mapinit()` reads a two-column device map file, validates source configs, and maps config strings either to device configs or replacement files.
- `postservice()` posts the filesystem service to `/srv/<name>` and command service to `/srv/<name>.cmd`; with `-s`, it first serves 9P on inherited stdio.
- `main()` initializes formatting, memory, queues, message buffers, networking, SCSI, file/path/user tables, iobufs, system config, services, console command handling, and worker processes.
- `serve()` is the multi-worker 9P dispatch loop. It receives `Msgbuf`s from `serveq`, locks channel/main state, detects or reuses the protocol handler, and frees messages.
- `rahead()` batches and sorts readahead requests by device/address before issuing `getbuf(..., Brd)`.
- `wormcopy()` schedules automatic daily dumps, copies dirty cache blocks to WORM, and calls `wormprobe()` for jukebox idle handling.
- `synccopy()` writes sync blocks periodically.
- `inqsize()` reads an sd-style `ctl` file and extracts the reported geometry block size.

Notable details:
- `maxsize()` computes maximum addressable file size with overflow detection, based on direct and indirect block fanout.
- `nextdump()` computes the next automatic dump time using `nextime()`.
- `exit()` marks the server as exiting, prints halt time, posts a process-group note, and exits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/malloc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/malloc.c

Purpose: Permanent allocation and iobuf pool setup for cwfs.

Key behavior:
- `memsize()` estimates available memory from `/dev/swap`, optionally scaled by `fsmempercent`; fallback is `16*MB`.
- `ialloc()` is a simple permanent allocator using `sbrk()`/`brk()`, with alignment adjustment and `mainmem` pool locking.
- `iobufinit()` computes the number of I/O buffers and hash buckets, rounds hash count upward to a prime, allocates `Hiob`, `Iobuf`, and raw block storage, then links buffers into per-hash circular LRU chains.
- `iobufmap()` and `iobufunmap()` expose or hide the raw backing pointer by toggling `Iobuf.iobuf`.

Notable details:
- `HWIDTH` targets eight buffers per hash bucket.
- The file deliberately allocates long-lived storage only; normal malloc/free lifecycle is avoided for server core structures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/malloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/mworm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/mworm.c

Purpose: Implements composite block devices used by cwfs: concatenation, interleaving, partitions, and mirrors.

Key behavior:
- `mcatinit()` initializes all child devices, records `ndev`, stores a child pointer array in `private`, and caches child sizes.
- `mcatsize()`, `mcatread()`, and `mcatwrite()` concatenate child devices by cumulative block ranges.
- `mlevinit()`, `mlevsize()`, `mlevread()`, and `mlevwrite()` implement striped/interleaved devices: logical block `b` maps to child `b % ndev`, child block `b / ndev`.
- `partinit()`, `partsize()`, `partread()`, and `partwrite()` expose percentage-based partitions of an underlying device.
- `mirrinit()`, `mirrsize()`, `mirrread()`, and `mirrwrite()` implement mirror devices. Reads try mirrors in order until one succeeds; writes recurse through links so mirrors are written before the main device.

Notable details:
- Mirror writes are synchronous and deliberately ordered so a crash does not leave the main copy ahead of mirror copies.
- Composite sizes are cached on child `Device.size` but lazily filled if zero.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/mworm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/net.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/net.c

Purpose: User-mode network listener layer for cwfs 9P service connections.

Key behavior:
- `annstrs[]` holds announce strings gathered from `main.c -a`.
- `netinit()` announces each configured network address and records announce/listen directories.
- `netstart()` starts one `neti` process per announced network.
- `neti()` loops on `listen()`/`accept()`, obtains remote address info with `getnetconninfo()`, and hands accepted fds to `srvchan()`.

Context:
- Comments explain the shift from the old kernel fileserver’s Ethernet/IL packet queues to user-mode per-connection stream handling.
- Actual 9P message framing is handled by `srv.c`, not here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/net.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/portdat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/portdat.h

Purpose: Central cwfs data layout and global type definition header. It defines both on-disk structures and in-memory server structures.

On-disk structures:
- `Tag`: block tag footer with tag type and qid path.
- `Qid9p1`: old qid format.
- `Super1`/`Superb`: superblock/free-list metadata.
- `Centry`, `Cache`, `Bucket`: cached-WORM map/cache structures.
- `Dentry`: directory entry layout, including name, uid/gid/mode, qid, size, direct blocks, indirect blocks, and times.
- `Label`: `Devlworm` label stored in the last block with `Labmagic`, side ordinal, and service string.

In-memory structures:
- `Device`: polymorphic device tree node with unions for wren/worm, composite devices, cw, juke, read-only, fake worm, partitions, and byte-swapped devices.
- `Chan`, `Msgbuf`, `Queue`: connection and message queue machinery.
- `File`, `Wpath`, `Tlock`: fid/path/lock bookkeeping.
- `Filsys`, `Conf`, `Cons`, `Uid`, `Iobuf`, `Hiob`, `Rabuf`, `Truncstate`: filesystem, configuration, users, buffer cache, readahead, and truncation state.

Constants:
- `SUPER_ADDR` and `ROOT_ADDR` set fixed super/root block addresses.
- Derived block constants include `BUFSIZE`, `DIRPERBUF`, `INDPERBUF`, `FEPERBUF`, and cache bucket sizing.
- Device types include `Devwren`, `Devworm`, `Devlworm`, `Devfworm`, `Devjuke`, `Devcw`, `Devro`, `Devmcat`, `Devmlev`, `Devpart`, `Devswab`, and `Devmirr`.
- Block tags include super, directory, file, free, bucket, cache, config, labeled-WORM label, and variable-depth indirect tags.

Notable details:
- Packed sections are marked “DONT TOUCH”; changing them changes disk format.
- Under non-`COMPAT32`, deeper indirect block tags up to `Tind4` are supported.
- Global `conf` and `cons` are defined here, so this header contributes storage, not just declarations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/portdat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/portfns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/portfns.h

Purpose: Function prototype header for cwfs.

Coverage:
- Filesystem operations: attach/clone/create/open/read/write/walk/remove/stat/session helpers.
- Device dispatch and implementations: cw, wren, worm/juke, fake worm, mcat/mlev/mirror/part/swap devices.
- Buffer/cache operations: `getbuf`, `putbuf`, allocation/freeing, tags, indirect addressing, readahead.
- Server/concurrency operations: queues, message buffers, `serve`, `srvchan`, `newproc`, network init/start.
- User/group operations: uid parsing, formatting, group checks, user commands.
- Console/command operations: command install/exec, config printing, checks.
- SCSI and time operations: SCSI command wrappers, `toytime`, `nextime`, formatting.
- Recovery/ream/dump/sync operations.

Notable details:
- The header exposes cross-file contracts for nearly every `.c` in `cwfs`.
- Some declared juke helper names such as `jukeread`/`jukewrite`/`jukesize` are not the primary implementations in `juke.c`, which provides `wormread`/`wormwrite`/`wormsize` for worm side devices.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/portfns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/proc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/proc.c

Purpose: Small process-spawning wrapper for cwfs.

Key behavior:
- `newproc()` forks with `RFPROC|RFMEM|RFNOWAIT`.
- In the child, it sets the process name with `procsetname()`, invokes the supplied function, and exits with `"child returned"` if the function returns.
- Parent continues immediately.

Notable details:
- `RFMEM` means worker processes share memory, matching cwfs’s lock-based shared-state design.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/scsi.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/scsi.c

Purpose: SCSI adapter layer for cwfs, using Plan 9 `scsi(2)`/sd interfaces rather than old direct host-adapter commands.

Key structures:
- `Ctlr`: controller table containing `Target target[NTarget]`.
- `Target` fields are defined elsewhere but used here for locking, id strings, inquiry/sense buffers, target numbers, ok flag, and attached `Scsi*`.

Important behavior:
- `scsiinit()` initializes all controller/target records, allocates inquiry/sense buffers, and enables SCSI verbosity.
- `newscsi()` attaches an opened `Scsi*` handle to a cwfs `Device` target.
- `scsitarget()` maps a `Device`’s `wren.ctrl`/`wren.targ` to the static controller table.
- `doscsi()` executes a command with `scsi()`, and on failure sends request-sense to classify the error.
- `sense2stcode()` and `scsireqsense()` translate sense keys and additional sense codes into `STok`, `STblank`, `STcheck`, or hard errors.
- `scsiprobe()` tests readiness, handles reset/unit attention, attempts spin-up for becoming-ready devices, runs inquiry, and marks the target ok.
- `scsiio()` lazily probes, retries commands up to ten times, treats blank reads as zero-filled success, and prints retry diagnostics.

Notable details:
- LUN is preserved in `cmd[1]` and reused for request-sense.
- `lastcmd` is saved for sense diagnostics.
- This file is critical for `juke.c` robotics commands.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/scsi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/srv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/srv.c

Purpose: Per-connection 9P stream handling for cwfs.

Key structures:
- `Srv`: reference-counted per-channel state with `Chan*` and fd.
- `freechans`: global free list of preallocated channels.

Important behavior:
- `srvinit()` preallocates `Nchans` channels, each with embedded `Srv` state.
- `srvchan()` takes an accepted fd/name, removes a channel from the free list, initializes connection metadata, creates a reply queue/output process if needed, and starts an input process.
- `srvi()` reads a byte stream, frames 9P2000 messages by their little-endian size header, allocates small or large `Msgbuf`s, and sends them to `serveq`.
- `srvo()` receives replies from a channel reply queue and writes them back to the connection fd, handling interrupts and hangups.
- `chanhangup()` frees file state for the channel and attempts to write `hangup` to the connection ctl file.
- `srvput()` decrements refs, closes fd, frees files, and returns the channel to the free list.

Notable details:
- `srv.c` owns transport framing; protocol dispatch happens in `main.c:serve()`.
- Reference counting keeps the fd alive while queued replies are outstanding.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/srv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/sub.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/sub.c

Purpose: Large shared utility layer for cwfs. It handles filesystem lookup helpers, fid/path management, permissions, file locks, free-list allocation, message queues, device dispatch, reaming/recovery/init routing, formatting, and byte swapping.

Important behavior:
- Filesystem/fid helpers: `fsstr()`, `dev2fs()`, `fs_chaninit()`, `fileinit()`, `filep()`, `newfp()`, `freefp()`.
- Access control: `iaccess()` checks owner/group/other bits, special uid/group behavior, `duallow`, and privileged console/allowed user access. `isallowed()` gates console or configured allowed uid.
- Temporary locks: `tlocked()` manages `Tlock` entries with expiration.
- Path allocation: `newwp()` and `freewp()` manage fixed `Wpath` pool refs.
- Allocation/freeing: `bufalloc()`, `buffree()`, `truncfree()`, and `addfree()` manage superblock free lists and recursive indirect block freeing.
- Formatting: `%Z` prints device config syntax, `%G` prints tags, `%T` installed elsewhere for times.
- Reaming: `rootream()` creates the root directory block; `superream()` initializes super/free metadata.
- Message buffers: `mbinit()`, `mballoc()`, `mbfree()` manage large/small preallocated message buffers and readahead buffers.
- Queues: `newqueue()`, `fs_send()`, `fs_recv()` implement semaphore-backed circular queues.
- Device dispatch: `devread()`, `devwrite()`, and `devsize()` route by `Device.type`.
- Device setup: `devream()`, `devrecover()`, and `devinit()` recursively initialize or format device trees.
- Byte swapping: `swab2()`, `swab4()`, `swab8()`, and `swab()` convert on-disk block types between native and foreign endianness.

Notable details:
- `devwrite()` returns success immediately when global `readonly` is set, preventing actual writes.
- `sdof()` converts device config to `/dev/sdXY` names.
- `superaddr()` and `getraddr()` defer to cw-specific root/superblock addresses for cached-WORM devices.
- `swab()` understands all disk tags except data-like byte arrays, which are intentionally left unchanged.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/sub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/time.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/time.c

Purpose: Time helpers and time formatting for cwfs.

Key behavior:
- `toytime()` returns `time(nil)`.
- `datestr()` formats a `Timet` as `YYYYMMDD`.
- `prdate()` prints current time using cwfs `%T`.
- `Tfmt()` formats `Timet` values as `Day Mon DD HH:MM:SS YYYY`, with `"The Epoch"` for zero.
- `nextime()` computes the next time after `t` matching an hour and not excluded by a weekday bitmask; used for automatic dump scheduling.
- `delay()` wraps `sleep()` in milliseconds.

Notable details:
- The formatter manually fills a fixed string template with day/month names and two-digit fields.
- `nextime()` includes DST/hour-adjustment handling by rechecking the resulting local hour.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/time.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/uidgid.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/uidgid.c

Purpose: User/group database loading, lookup, editing, and permission helper support for cwfs.

Key behavior:
- `cmd_users()` loads `/adm/users` or a supplied file through the cwfs console path. It parses uid/name/leader/member records in two passes: first users, then group memberships.
- `setminusers()` installs a minimal built-in user table when `users default` is requested.
- `cmd_newuser()` and `do_newuser()` implement console user/group edits: create user/group, query, rename, set/remove leader, add/remove group member, then rewrite `/adm/users`.
- `uidpstr()`, `uidtop()`, `strtouid()`, and `uidtostr()` perform name/id lookup using the sorted uid table.
- `ingroup()` and `leadgroup()` support permission checks from `sub.c`.
- `pentry()` serializes a `Uid` back to `/adm/users` format.
- `readln()` and `fchar()` read `/adm/users` via console file operations and a temporary `Iobuf`.

Notable details:
- Group space is a single `gidspace` array; edits that add members copy the group table to the current tail.
- Built-in users include `adm`, `none`, `tor`, `sys`, `map`, `doc`, `upas`, `font`, and `bootes`.
- Names reject characters from `"?=+-/:"` and enforce `NAMELEN`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/uidgid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/wren.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/wren.c

Purpose: Plain disk/file-backed block device implementation for cwfs `Devwren`.

Key structures:
- Private `Wren`: native block size, native block count, multiplier to cwfs `RBUFSIZE`, and max logical block count.

Key behavior:
- `dataof()` maps a configured path to either the path itself or `path/data` if it is a directory.
- `wreninit()` allocates private geometry, resolves `/dev/sdXX/data` or configured file, opens it read-write, finds block size via `inqsize()`, falls back to 512-byte sectors when needed, and derives logical block count.
- `wrensize()` returns logical block capacity.
- `wrenread()` and `wrenwrite()` bounds-check logical blocks and use `pread`/`pwrite` of `RBUFSIZE` bytes.

Notable details:
- Errors increment `cons.nwrenre` and `cons.nwrenwe`.
- This is the normal I/O path for disks and for jukebox optical drives once media is loaded.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/wren.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/date.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/date.c

Purpose: Plan 9 `date` command.

Key behavior:
- Supports `-n` normalized seconds output, `-u` UTC/no local timezone, `-t` ISO-like timestamp, `-i` date-only, and `-f fmt`.
- With no argument, uses `nsec()` for current seconds and nanoseconds.
- With one argument, treats it as epoch seconds.
- Loads local timezone with `tzload("local")` unless `-u`.
- Converts with `tmtimens()` and formats via `tmfmt()`.

Notable details:
- Default format is `WW MMM _D hh:mm:ss ZZZ YYYY`.
- `-n` prints `tmnorm(&tm)` rather than formatted calendar text.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/date.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/command.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/db/command.c

Purpose: Top-level command decoder for the Plan 9 `db` debugger.

Key behavior:
- `command()` parses optional address, optional count, and command character, preserving last command defaults.
- `/`, `?`, and `=` dispatch to `acommand()` for memory/symbol/literal examination.
- `>` writes current dot value to a register.
- `!` executes a shell command.
- `$` runs debugger meta commands through `printtrace()`.
- `:` runs process-control commands through `subpcs()`, guarded by `executing`.
- `acommand()` handles map display (`m`), search (`l`/`L`), writes (`w`/`W`), or format scanning.
- `cmdsrc()` searches memory for 16-bit or 32-bit values with optional mask.
- `cmdwrite()` writes 16-bit or 32-bit values to the selected map and prints the resulting value.
- `regname()` parses multi-character register names.
- `shell()` executes `/bin/rc -c` with the rest of the input line.

Notable details:
- Default formats are `eqformat = "z"` and `stformat = "zMi"`.
- `dot`, `dotinc`, `adrval`, `cntval`, and related flags are global debugger cursor state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/command.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/defs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/db/defs.h

Purpose: Shared definitions for the `db` debugger.

Contents:
- Includes Plan 9 base headers, bio, ctype, and `mach.h`.
- Defines debugger scalar types: `WORD` as `ulong`, `ADDR` as `uvlong`, and `BOOL`.
- Defines command constants, input sizes, run modes, breakpoint states, standard fds, and default include directory.
- Defines `BKPT`, holding address, saved instruction bytes, counts, flag, command text, and list link.
- Declares common globals for expression values, dot, files, process state, maps, breakpoints, and input state.

Notable details:
- `CMD_VERBS` is used to identify debugger command delimiters and file-location parsing.
- The header is intentionally broad; implementation prototypes live in `fns.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/defs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/expr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/db/expr.c

Purpose: Expression parser and numeric/symbol token reader for `db`.

Key behavior:
- `expr()` parses left-associative dyadic expressions using `+`, `-`, `#` round-up, `*`, `%`, `&`, and `|`.
- `term()` handles monadic dereference from core (`*`), text/symbol map (`@`), negation, bitwise complement, and parenthesized expressions.
- `item()` parses symbols, local symbols, file:line references, numeric literals, dot/current function locals, ditto (`"`), next/previous dot, registers (`<reg`), and quoted character constants.
- `getnum()` supports decimal, octal, hex (`#` or `0x`), explicit decimal (`0t`), explicit octal (`0o`), and floating input coerced into `WORD`.
- `readsym()` and `readfname()` parse UTF-aware symbol and escaped filename tokens.
- `symchar()` and `convdig()` classify symbol/numeric characters.

Notable details:
- File references like `path:line` are detected before colon-command interpretation and converted through `file2pc()`.
- Local symbol lookup uses `localaddr()` against either a named function or the current function found from `mach->pc`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/expr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/db/fns.h

Purpose: Function prototype header for the `db` debugger.

Coverage:
- Command parsing and command helpers.
- Expression parsing and token reading.
- Output and input redirection.
- Map setup and manipulation.
- Register access and printing.
- Breakpoint/process control.
- Stack trace, symbol, source, local/parameter printing.
- Process attach/run/kill/note handling.

Notable details:
- Includes vararg checking for `dprint`.
- Exposes `rget()`/`rput()` used by libmach callbacks and expression evaluation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/format.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/db/format.c

Purpose: Format-string execution for `db` memory, symbol, and literal printing.

Key behavior:
- `scanform()` repeats an entire format over a count, updating `dotinc`.
- `exform()` executes individual format modifiers, reads from a `Map` unless in literal mode, prints values, and updates `dot`.
- Supports address/symbol formats, signed/unsigned/octal/hex 16-bit and 32-bit formats, 64-bit formats, bytes/chars/runes/strings, instructions, hex instructions, floats/doubles, newlines, quoted text, cursor movement, and source-line format `z`.
- Instruction formats call `machdata->das()` and `machdata->hexinst()`.
- Float formats call machine-specific float conversion helpers.
- `printesc()` prints non-printable bytes as `\xNN`.
- `inkdot()` advances `dot` with wraparound detection.

Notable details:
- First-pass logic prints a symbol/address prefix and warns on unaligned instruction addresses.
- Literal mode treats `dot` itself as the value rather than reading memory.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/format.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/input.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/db/input.c

Purpose: Input buffering and token mechanics for `db`.

Key behavior:
- Maintains a UTF `Rune line[LINSIZ]`, current pointer `lp`, `peekc`, `lastc`, and `eof`.
- `readrune()` reads UTF-8 from fd one byte at a time until a full rune is available.
- `readchar()` reads from `peekc`, from the current in-memory line, or fills a new line from `infile`; backslash-newline joins lines.
- `rdc()` skips spaces/tabs.
- `reread()` pushes back the last character.
- `clrinp()` clears input and flushes output.
- `nextchar()` returns the next non-space char unless at end of command.
- `quotchar()` handles quoted character constants.
- `getformat()` reads a format string through end-of-line/semicolon, preserving quoted sections.
- `isfileref()` looks ahead to distinguish `filename:line` from `:` process commands.

Notable details:
- Interrupt handling uses `mkfault` to abort the current input read through `error()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/input.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/db/main.c

Purpose: Main loop, argument parsing, fault handling, and error recovery for `db`.

Key behavior:
- Supports `-k` kernel mode, `-w` writable mode, `-I dir` include path, and `-m machine`.
- Accepts optional symbol file and optional pid. If a pid is supplied, it defaults symbol/core files to `/proc/<pid>/text` and `/proc/<pid>/mem`.
- Initializes output, machine/symbol map, dot map, core map, and prints current exception/pc when attached.
- Runs a persistent command loop using `setjmp`/`longjmp` recovery.
- `error()` records a pending message, closes redirected input/output, removes breakpoints, and jumps back to the main loop.
- `fault()` catches Plan 9 interrupt notes, seeks current input to end, and resumes.

Notable details:
- Default symbol file is `8.out`.
- In kernel mode with only a pid and no symbol file, it guesses `/386/9<terminal>` using `$cputype` and `$terminal`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/output.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/db/output.c

Purpose: Output buffering, column tracking, and debugger input/output redirection.

Key behavior:
- `outputinit()` initializes buffered stdout and installs `%t` tab formatting.
- `dprint()` formats to a local buffer, writes through `Biobuf`, and tracks display column by runes/newlines.
- `flushbuf()`, `flush()`, `printc()`, `prints()`, and `newline()` wrap output operations.
- `iclose()` manages nested input redirection stack for `$<`/`$<<`.
- `redirout()` appends to or creates output redirection targets.
- `oclose()` restores stdout output buffering.
- `endline()` emits a newline when the current column exceeds `maxpos`.

Notable details:
- `%t` no longer does calculated tab stops; it prints a literal tab.
- On `mkfault`, `dprint()` suppresses output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/output.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/pcs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/db/pcs.c

Purpose: User command layer for process control in `db`.

Key behavior:
- `subpcs()` implements `:` commands:
  - `:b`/`:B` set normal/temporary breakpoints with optional commands.
  - `:d`/`:D` delete breakpoints.
  - `:r`/`:R` restart/run.
  - `:s` single-steps instructions.
  - `:S` steps source lines.
  - `:c`/`:C` continues.
  - `:n` manages pending notes.
  - `:h` stops/grabs a process.
  - `:x` resumes/ungrabs.
  - `:k` kills.
- After runs, it removes installed breakpoints, prints current pc, and prints pending notes.

Notable details:
- Breakpoint commands with no explicit count become effectively infinite by setting `HUGEINT`.
- Source-line stepping uses `pc2line()` and loops until the line changes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/pcs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/print.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/db/print.c

Purpose: `$` meta-command implementation and higher-level printing for `db`.

Key behavior:
- `printtrace()` handles:
  - input/output redirection,
  - attach by pid,
  - kernel mapping adjustment,
  - quit,
  - line width and symbol offset settings,
  - map display,
  - register and floating-register printing,
  - C stack traces and locals,
  - extern/global symbol values,
  - breakpoint listing,
  - machine selection.
- `ptrace()` is the stack trace callback used by `machdata->ctrace()`.
- `printmap()` prints map segments and backing files.
- `printsym()` dumps raw symbol table entries.
- `printsource()` prints file:line for an address.
- `printpc()` prints current pc source, symbol offset, and disassembled instruction.
- `printlocals()` and `printparams()` print local variables and parameters from symbol metadata.
- `redirin()` opens command input files, falling back under `Ipath`.

Notable details:
- `$C` stack tracing prints locals after each frame.
- `printparams()` assumes parameters are at offsets from frame pointer after saved pc.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/print.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/regs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/db/regs.c

Purpose: Register lookup, read/write, and printing for `db`.

Key behavior:
- `rname()` finds a register in `mach->reglist`.
- `getreg()` reads register values from a map according to register format: 16-bit, 32-bit, or 64-bit.
- `rget()` resolves a register name and returns its value.
- `rput()` writes a register unless marked read-only.
- `printregs()` prints integer registers in rows and, with `R`, includes floating registers except special unsupported formats; then prints exception text and current pc.

Notable details:
- Register offsets are “magic” offsets understood by the active machine/map backend.
- Errors are reported through `error("%r")`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/regs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/runpcs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/db/runpcs.c

Purpose: Breakpoint lifecycle and run-loop logic for `db`.

Key behavior:
- `runpcs()` drives single-step or continue loops, handles current breakpoint skip logic, installs/removes breakpoints, processes notes, executes breakpoint commands, and returns whether execution stopped at a breakpoint.
- `endpcs()` kills or detaches current process state and resets temporary breakpoints.
- `setup()` starts a debugged process and marks process-control active.
- `execbkpt()` single-steps over a breakpoint then restores it.
- `scanbkpt()` finds a breakpoint by address.
- `setbp()` installs all active breakpoints into process memory.
- `delbp()` removes installed breakpoints.

Notable details:
- Breakpoints transition through `BKPTSET`, `BKPTSKIP`, `BKPTTMP`, and `BKPTCLR`.
- Actual process `/proc` control is in `trcrun.c`; this file orchestrates debugger semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/runpcs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/setup.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/db/setup.c

Purpose: Symbol/core file opening and map setup for `db`.

Key behavior:
- `setsym()` opens the symbol file, cracks the executable header, selects machine type, loads text/data maps, initializes symbols, and records static-base register value if available.
- `setcor()` opens the core/process memory file, builds a process map through `attachproc()` when debugging a live pid, or creates text/data maps for static core/image access.
- `dumbmap()` creates a fallback single data map and defaults machine data to i386.
- `cmdmap()` edits map segment base/end/file offsets from debugger commands and can alias symbol/core maps.
- `getfile()` opens or creates files according to debugger mode and handles read-only fallback.
- `kmsys()` adjusts maps for kernel-style addressing.
- `attachprocess()` attaches to a pid specified by address expression and warns if text images differ.

Notable details:
- `setcor()` closes prior map fds before replacing a core map.
- Kernel mapping adjusts text/data using `mach->ktmask` and `mach->kbase`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/setup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/trcrun.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/db/trcrun.c

Purpose: Low-level Plan 9 `/proc` control for `db`.

Key behavior:
- `setpcs()` opens `/proc/<pid>/ctl` and `/proc/<pid>/note` for the current pid.
- `msgpcs()` writes control messages, ending process state on non-interrupt failures.
- `unloadnote()` reads pending notes, discarding breakpoint notes.
- `loadnote()` re-sends saved notes.
- `notes()` prints pending notes.
- `killpcs()`, `grab()`, and `ungrab()` send `kill`, `stop`, and `start`.
- `doexec()` parses run command arguments and `<`/`>` redirection, then execs `symfil`.
- `startpcs()` forks the target, hangs it, execs, maps `/proc/<pid>/mem`, waits for stop, and optionally sets pc.
- `runstep()` computes follow addresses with `machdata->foll()`, plants temporary breakpoints, runs, then removes them.
- `runrun()` starts/stops the process, preserving or discarding notes as requested.
- `bkput()` installs/restores machine-specific breakpoint instruction bytes.

Notable details:
- Single-step is implemented with temporary breakpoints at possible next instruction addresses, not hardware stepping.
- `bkput()` applies optional `machdata->bpfix()` to adjust breakpoint address.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/db/trcrun.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dc.c

Purpose: Arbitrary-precision reverse-polish desk calculator.

Core representation:
- `Blk` is a growable byte buffer with read/write/begin/end pointers.
- Numbers are stored in base-100 digits, with the last byte used as scale in stack values.
- Negative values use a sign/complement convention manipulated by `chsign()`.
- Stack is `Blk *stack[STKSZ]`; registers/symbols use `Sym` lists and `stable[TBLSZ]`.
- Arrays are stored as pointer blocks through `Wblk` overlay operations.

Important behavior:
- `main()` initializes bio and calls `init()` then `commnds()`.
- `commnds()` is the command interpreter. It handles numeric input, arithmetic, scale/base changes, stack ops, register save/load, arrays, macro strings, macro execution, conditional execution, shell escapes, and printing.
- Arithmetic includes `add()`, `subt()`, `mult()`, `div()`, `dcsqrt()`, and `dcexp()`.
- Scale handling uses `eqk()`, `dscale()`, `add0()`, `removc()`, `removr()`, `scale()`, and `scalint()`.
- Output supports decimal, arbitrary output base, base 1/0 special cases, and character/string printing through `dcprint()`, `tenot()`, `oneot()`, `hexot()`, and `bigot()`.
- Input/macro execution uses `readc()`, `unreadc()`, `readstk`, strings `[ ... ]`, and command `x`.
- Shell escape `!` runs `/bin/rc -c`.
- Memory management uses `salloc()`, `copy()`, `more()`, `seekc()`, `release()`, and a free-list of `Blk` headers.

Notable details:
- Debug command `Y` prints allocator and stack statistics.
- `init()` can read commands from a file argument after checking it is not a directory.
- `garbage()` is a stub; allocation failures retry once and then call `ospace()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dd.c

Purpose: Plan 9 `dd` byte/block copy utility with conversions.

Key behavior:
- Parses key/value arguments like `-ibs`, `-obs`, `-bs`, `-cbs`, `-if`, `-of`, `-skip`, `-seek`, `-iseek`, `-oseek`, `-count`, `-files`, `-trunc`, `-quiet`, and `-conv`.
- Supports conversions: `ebcdic`, `ibm`, `ascii`, `block`, `unblock`, `lcase`, `ucase`, `swab`, `noerror`, and `sync`.
- `number()` parses suffix multipliers `m`, `k`, `b`, and multiplication with `x`.
- Main copy loop reads input blocks, handles count/files, noerror/sync behavior, byte swapping, fast path when ibs==obs and no conversion, and output buffering.
- `flsh()` writes pending output and counts full/partial records.
- Conversion functions handle case conversion, EBCDIC/IBM tables, fixed-length record padding/truncation, and newline conversion.
- `stats()` prints records in/out and truncated records unless quiet.

Notable details:
- Buffers are allocated with `sbrk()`.
- `dotrunc=0` opens output without truncation.
- Read errors with `noerror` seek past the failed input block and continue.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/deroff.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/deroff.c

Purpose: Strips troff/nroff, eqn, tbl, pic, and macro constructs from text, optionally emitting one word per line.

Key behavior:
- Supports `-w`, `-_`, `-m m|s|l`, and `-i`.
- Maintains an input file stack for `.so` includes and `.nx` next-file directives unless `-i`.
- `work()` loops over regular lines and command lines.
- `regline()` reads ordinary text lines, strips backslash constructs, preserves selected table text, and emits raw line, macro-filtered line, or words.
- `putwords()` tokenizes output into words using custom character classes.
- `comline()` recognizes and skips/interprets troff commands: comments, `.EQ/.EN`, `.TS/.TE`, macro definitions, `.so`, `.nx`, `.tm`, `.hw`, section/title/list/display macros, pic, centered text, references, etc.
- `eqn()` skips display equations and tracks inline equation delimiters.
- `skeqn()` skips inline equations delimited by configured eqn delimiters.
- `tbl()`/`stbl()` skip table control.
- `sdis()`, `sce()`, `refer()`, and `inpic()` handle macro package display, centered text, references, and pic quoted text.
- `backsl()` skips troff escape constructs and handles selected escapes such as em dash under ms mode.

Notable details:
- Character classes distinguish special, apostrophe, punctuation, digit, letter, and extended runes.
- Include-loop prevention uses a linked list of seen file names.
- `msflag` changes behavior substantially for ms/mm macro packages.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/deroff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/derp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/derp.c

Purpose: Three-way directory/file difference classifier, likely for replica-style synchronization planning.

Key behavior:
- Compares local (`myfile`), ancestor (`oldfile`), and remote (`yourfile`) paths.
- Options control quiet/continue-on-error, user checks, time checks, dump qid optimization, size-only behavior, and permission mask.
- `statdir()` obtains a `Dir` and stores the full path in `name`.
- `samefile()` compares Plan 9 qid identity and, for dump directories, can treat equal atime as unchanged subtree.
- `dcmp()` compares dirs/files by qid, type, permissions, users, size, time, or full file content via `cmpfile()`.
- `diffdir()` reads and sorts directories, then merge-walks child names from local/remote/ancestor and recurses.
- `diffgen()` classifies add/delete/modify conflicts and emits two-letter operation codes with optional `!` conflict marker.
- `diff3()` sets up the three initial `Dir` structures and resolves cases where ancestor equals local or remote.

Output examples:
- `an`: local added, remote unchanged/nonexistent.
- `na`: remote added.
- `mn`/`nm`: local or remote modified.
- `dn`/`nd`: local or remote deleted.
- `mm!`, `aa!`, `md!`, `dm!`: conflicts.

Notable details:
- It handles directory/file type changes specially by decomposing into delete/add where possible.
- `-L` disables size checks, forcing content comparison unless time/other checks settle it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/derp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dial/at.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dial/at.c

Purpose: Sends modem AT commands over stdin/stdout and waits for recognized responses.

Key behavior:
- Options: `-q` quiet, `-t seconds` timeout.
- For each command argument, writes `at<cmd>\r` slowly, one byte every 100 ms.
- Default timeout is 5 seconds, except dial commands starting with `d`/`D` get 2 minutes.
- Reads response lines without carriage returns.
- Echoes modem output to `/dev/cons` unless quiet.
- Recognizes successful responses `ok` and `connect`; failures include `no carrier`, `no dialtone`, `error`, `busy`, `no answer`, `delayed`, and `blacklisted`.

Notable details:
- Matching is case-insensitive via `cistrstr()`.
- `writewithoutcr()` strips carriage returns when echoing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dial/at.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dial/drain.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dial/drain.c

Purpose: Drains pending input briefly.

Key behavior:
- Sets a 100 ms alarm.
- Reads and discards stdin until read returns non-positive.
- Clears alarm and exits.

Notable details:
- `ding()` is defined to continue on alarm notes, but `main()` does not call `notify(ding)` in this file as read, so alarm behavior relies on default note handling unless installed elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dial/drain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dial/expect.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dial/expect.c

Purpose: Waits for a good string on stdin while optionally failing on any bad string.

Key behavior:
- Options: `-i` ignore case, `-q` quiet, `-t secs` timeout.
- Requires one good string and any number of bad strings.
- Opens `/dev/cons` and echoes incoming data there unless quiet, stripping carriage returns.
- Maintains a rolling buffer large enough to catch matches spanning reads.
- On good match, exits success.
- On bad match, exits with the bad string.
- On EOF, exits `"EOF"`.

Notable details:
- The timeout is implemented with `alarm(timeout*1000)` and a note handler that exits with the note string.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dial/expect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dial/pass.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dial/pass.c

Purpose: Bidirectional line-oriented pass-through between `/dev/cons` and stdin/stdout, useful for dialing scripts that need user input.

Key behavior:
- Option: `-q` suppress echoing received stdin data to console.
- Opens `/dev/cons` and tries to set raw mode through `/dev/consctl`.
- Forks shared-memory processes:
  - parent reads stdin and optionally echoes to console until done or newline/carriage return,
  - child reads one character at a time from console, writes to stdout, and stops at newline/carriage return.
- Uses a 250 ms alarm loop to let the reader notice shared `done`.

Notable details:
- Shared `done` and `alarmed` depend on `RFMEM`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dial/pass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/ahd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/ahd.c

Purpose: American Heritage Dictionary backend for the Plan 9 `dict` command, handling encrypted entry text.

Key behavior:
- `ahdprintentry()` decrypts bytes with `byte ^ (offset >> 1)`, maps selected high bytes to runes, interprets `%@tag@%` markup, and prints formatted output.
- For command `h`, it stops at tag `EH`.
- For command `r`, it preserves markup tags in output.
- Temporarily sets `breaklen` to 80 while printing.
- `ahdnextoff()` scans encrypted dictionary data for definition delimiters, tracking patterns `%@NL@%` then `%@2@%`.
- `ahdprintkey()` reports that pronunciations are unavailable.

Notable details:
- `intab` initializes special accented and symbol mappings, then fills identity mappings for other byte values on first use.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/ahd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/canonind.awk -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/canonind.awk

Purpose: Converts raw dictionary index output from `mkindex` into canonical `dict` index form.

Key behavior:
- Expects exactly one raw index file argument and tab field separator.
- For each input row, fields 2..NF are words associated with offset `$1`.
- Empty words are skipped.
- Parenthesized alternates generate two entries:
  - one without the parenthesized text,
  - one with it included.
- Non-parenthesized words generate a single `word<TAB>offset` entry.
- Writes intermediate output to `junk`, sorts it uniquely by case-folded word and numeric offset, then removes `junk`.

Notable details:
- Uses old awk `sort` key syntax: `sort -u -t'\t' +0f -1 +0 -1 +1n -2`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/canonind.awk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/comfix.awk -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/comfix.awk

Purpose: Expands comma-abbreviated dictionary raw index entries into fuller word forms.

Key behavior:
- For two-field rows with commas in field 2, splits the term list on comma+spaces.
- Prints the base word unchanged.
- For each suffix:
  - if it is one letter, replaces the last letter of the base word,
  - otherwise searches backward in the base word for the suffix’s first letter and accepts the replacement if the matched old suffix length is within three characters of the new suffix length.
- If suffix matching fails, preserves the unresolved `base, suffix` form for manual cleanup.
- Non-two-field rows pass through unchanged.

Notable details:
- Intended for raw index patterns such as `problematico, a, ci, che`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/comfix.awk -->