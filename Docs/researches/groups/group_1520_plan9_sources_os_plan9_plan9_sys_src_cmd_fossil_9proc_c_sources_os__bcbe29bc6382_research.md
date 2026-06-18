# Group Research: group_1520_plan9_sources_os_plan9_plan9_sys_src_cmd_fossil_9proc_c_sources_os__bcbe29bc6382

Scope verified against `Docs/research_subset_a.md`: all requested files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9proc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9proc.c

Connection and 9P message dispatcher for fossil. It maintains pooled `Con` and `Msg` objects, starts per-connection reader/writer threads, queues incoming 9P requests to worker threads, dispatches through `rFcall`, and serializes replies back to the client.

The notable logic is `Tflush`: queued requests can be marked flushed, flush messages are chained to the original request, duplicate flushes are coalesced, and replies are ordered so a flush completes only after the affected request is resolved. Console commands `msg`, `con`, and `who` expose pool sizing, connection lists, and per-connection users/fids.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9srv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9srv.c

Console command support for publishing fossil services through `/srv` or `#s`. `srvFd` creates an ORCLOSE service file and writes the fd number into it, while `srvAlloc` tracks live service registrations and refuses duplicate non-stale names.

The `srv` command lists services, deletes services, publishes normal 9P connections, or publishes raw console connections with `-p`. Flags control auth bypass, IP checks, `none` access, permission bypass, wstat allowance, and service file mode.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9srv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9user.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9user.c

In-memory user and group database plus console commands for `/active/adm/users`. Users live in a `Ubox` with uid/uname hash tables and a sorted linked list used for stable writeback.

The parser strips whitespace/comments, validates `uid:uname:leader:members`, rejects duplicates and invalid names, enforces mandatory `adm`, `none`, `noworld`, and `sys`, and fills group memberships on a second pass. Lookup helpers translate uid/uname, test group membership and leadership, and implement the optional `write` group read-only policy. `uname` edits users/groups and can create home directories; `users` dumps, rereads, resets defaults, and writes the database.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/Ccli.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/Ccli.c

Small command-line dispatcher for fossil's interactive console. It registers commands in a dynamically grown table, tokenizes input, ignores empty and `#` comment lines, dispatches by command name, and prints `vtGetError()` when a command fails.

`cliError` is the common helper for formatting console command errors into the Venti/fossil error buffer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/Ccli.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/Ccmd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/Ccmd.c

Built-in fossil console commands, including an internal 9P client. The `9p` command constructs selected T-messages, writes them through a private pipe-backed console connection, reads the reply, and prints both formatted request and response.

Other commands source command files (`.`), toggle `Dflag`, echo text, and call Plan 9 `bind`. `cmdInit` creates the private pipe, allocates a console `Con`, marks it as console, and registers the command set.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/Ccmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/Ccons.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/Ccons.c

Interactive fossil console implementation. It owns shared input/output ring queues, supports multiple console opens, and starts reader/writer threads for each attached console.

`consProc` assembles command lines, echoes input, handles control editing (`^D`, backspace, newline, `^U`, `^W`, delete), executes completed lines through `cliExec`, and redraws the prompt. `consTTY` attaches `/dev/cons` or `#c/cons` in raw mode, while `consWrite` falls back to fd 2 when no console is open.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/Ccons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/Clog.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/Clog.c

Console print wrappers. `consVPrint` formats into a fixed buffer and writes through `consWrite`; `consPrint` is its varargs wrapper.

A disabled `syslog` block shows the intended logging path but is kept off to avoid noisy filesystem-check output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/Clog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/archive.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/archive.c

Background archiver that converts local fossil blocks into Venti content. `archThread` claims pending archive roots from the superblock, recursively walks the snapshot tree, writes blocks to Venti, builds a `vac` root, records the resulting score in `super.last`, and reports `archive vac:<score>`.

`archWalk` rewrites parent entries or pointer slots from local pseudo-scores to Venti scores after children are stored. It can fake no-archive entries in a private copy, marks real archived blocks `BsVenti`, and schedules local unlink bookkeeping for reclaimed children.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/archive.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/buildsh -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/buildsh

Plan 9 `rc` helper for constructing a test namespace. It mounts `ehime`, sets a test root, defines a local `bind` wrapper, binds terminal devices, root, kernel device filesystems, bin directories, and starts interactive `rc` under `/sys/src`.

This is an operator/developer helper, not compiled fossil runtime code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/buildsh -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/bwatch.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/bwatch.c

Optional debug lock-order watcher for fossil blocks. It derives parent-child dependencies from block contents, tracks the blocks currently locked by each thread, and stops the process through `/proc` control if a thread tries to lock an ancestor after a descendant or violates sibling ordering.

The file documents that it is very slow and unreliable once snapshots turn the block tree into a DAG, but useful for catching development-time lock-order bugs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/bwatch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/cache.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/cache.c

Core block cache, allocator, write-order manager, and flush/unlink daemon layer for fossil. It caches local disk blocks and Venti blocks, hashes them by address or score, tracks clean/dirty/read/write states, and keeps an unreferenced-block heap for victim selection.

Allocation scans label blocks for free or reclaimable closed blocks, writes labels, zero-extends new data, and updates free-list accounting. Dirty blocks record dependencies so labels, copied blocks, parents, and superblock updates reach disk safely; `blockRollback` can write an older safe image while preserving the current dirty block.

Copy-on-write and snapshot lifetime semantics are encoded through label epochs, `BsCopied`, `BsClosed`, `BsVenti`, dependency lists, and delayed unlink queues. Background threads process unlink closure, flush dirty blocks, and periodically kick cache sync.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/check.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/check.c

Filesystem checker used by `flchk` and repair-oriented callers. It walks block graphs for every epoch from high to low, validating epoch interval rules, active-tree uniqueness, copy-on-write join constraints, labels, entries, pointer blocks, and leaks.

It then walks the directory/source tree to verify metadata blocks, sorted directory entries, source references, source generations, file data readability, and unreferenced source entries. Repair actions are callback-driven (`clre`, `clrp`, `close`, `clri`), with default no-op hooks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/check.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/dat.h

Central private data header for fossil storage code. It defines constants for headers, superblocks, labels, block states, block types, I/O states, disk partitions, and tunables such as dirty and flush thresholds.

The main structures are `Fs`, `Super`, `Entry`, `Source`, `Header`, `Label`, `Block`, `WalkPtr`, and `Fsck`. Comments document epoch-locking rules and fossil's hybrid local/Venti model: local entries extend Venti entries with tags, snapshot/archive state, and local pseudo-scores, while blocks carry cache-private dependency and I/O metadata.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/deadlock -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/deadlock

Plan 9 `rc` helper for running an acid deadlock inspection against fossil processes. It locates `8.fossil` or `fossil` pids when none are supplied, generates an acid script that includes `fossil-acid`, runs `deadlocklist`, and filters the marked output range.

This is a debugging script outside the compiled server.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/deadlock -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/disk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/disk.c

Asynchronous raw disk I/O layer over a fossil-formatted file or device. `diskAlloc` reads and validates the fossil header, initializes queues and rendezvous objects, and starts `diskThread`.

Raw reads/writes translate partition-relative block numbers through header partition offsets and use `pread`/`pwrite`. Queued I/O is sorted into current/next address scans; the disk thread locks blocks, performs reads or dependency-safe writes via `blockRollback`, updates block I/O state, and wakes flow/flush waiters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/disk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/dump.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/dump.c

Small daemon-style helper for periodic fossil snapshots and archives. It opens a fossil console, changes into a mounted fossil namespace, forks into the background, optionally waits for clock stabilization, and periodically writes console commands.

It creates daily archival snapshots when the expected `/archive/yyyy/mmdd` path is absent and, unless archive-only mode is selected, creates regular snapshots at the configured interval.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/dump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/epoch.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/epoch.c

Standalone tool for reading or editing the low epoch in a fossil superblock. It opens the image read-only or read-write, unpacks the header, reads the superblock, prints `epoch <low>`, and optionally writes a new `epochLow`.

It bypasses the cache/filesystem layer and directly uses `headerUnpack`, `superUnpack`, and `superPack`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/epoch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/error.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/error.c

Definitions of fossil's shared error string constants. The strings cover bad addresses, corrupted labels/entries/meta/superblocks, illegal modes and paths, read-only state, removed files, snapshot errors, Venti I/O, and common file operation failures.

These constants are passed to `vtSetError` throughout the cache, file, fs, formatter, and checker layers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/error.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/error.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/error.h

Extern declarations for the shared fossil error strings defined in `error.c`.

This header lets the rest of the fossil source tree refer to common stable error text without duplicating definitions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/error.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/file.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/file.c

High-level file and directory object layer built over `Source` streams. Each `File` holds directory metadata, a data source, and for directories a metadata source containing packed directory entries.

It implements walk/open, create, read, write, append, truncate, stat/wstat, remove, clri, refcounting, directory enumeration, metadata flushing, qid-space persistence, and temporary/no-archive propagation. It enforces root immutability, read-only modes, file-vs-directory checks, empty-directory removal, lock ordering, and source generation checks.

Snapshot support copies source entries into snapshot directories with epoch/archive metadata, and `fileWalkSources` forces copy-on-write down to the source-entry blocks before snapshot linking.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/flchk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/flchk.c

Command-line wrapper around `fsCheck`. It parses cache size, Venti host, local-only checking, and directory-printing flags, connects to Venti when required, opens the fossil image read-only, installs formatters, and runs the checker.

Repair hooks emit commented console-style commands such as `# clre`, `# clrp`, `# clri`, and `# bclose`; they do not apply changes directly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/flchk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/flfmt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/flfmt.c

Fossil filesystem formatter and initializer. It validates/partitions a target file or device, writes the fossil header, zeros labels, creates root/source/meta blocks, initializes the superblock, and reopens the new filesystem to create `/active`, `/archive`, and `/snapshot`.

It supports block-size selection, label naming, overwrite confirmation bypass, Venti-root restoration, and optional ISO9660 embedding. Restoring from Venti validates the supplied root score, imports root/source entries, recovers qid space from root metadata, and builds a new local top-level source.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/flfmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/flfmt9660.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/flfmt9660.c

Optional ISO9660 import/embedding support for `flfmt`. It validates an ISO image, checks the requested offset against fossil data layout, reserves ISO-used fossil data blocks by writing labels, and then maps ISO file extents into fossil files.

Directory copying parses ISO directory records plus Plan 9 system-use metadata for name, uid, gid, mode, and timestamps. File data is not copied byte-for-byte into new blocks; `fileMapBlock` maps existing reserved disk blocks into fossil file sources using local pseudo-scores.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/flfmt9660.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/flfmt9660.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/flfmt9660.h

Small header declaring the ISO9660 helper entry points used by `flfmt.c`: initialization, label reservation, and filesystem copy/import.

It keeps the ISO9660-specific implementation isolated from the main formatter.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/flfmt9660.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/fns.h

Private function declaration header for fossil storage modules. It exposes the cross-file APIs for filesystem lifecycle, file operations, directory enumeration, source streams, cache/block operations, disk I/O, packing/unpacking, periodic workers, archiving, block watching, tree walking, snapshots, and `fsCheck`.

It also declares formatters and Plan 9 vararg checks for labels and scores.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/fossil.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/fossil.c

Main fossil server entry point. It isolates the process namespace/environment, redirects stdio to `/dev/null`, attaches Venti support, parses command-line commands or embedded config commands from a fossil partition, initializes console/CLI/9P/fsys/service/listener/user subsystems, and executes startup commands.

The `-f` path reads a config block near 127 KiB and expands standalone `*` arguments to the current partition path. `-t` attaches an interactive raw console after initialization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/fossil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/fs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/fs.c

Top-level filesystem lifecycle, snapshot, archive, sync, and scheduling logic. `fsOpen` opens the disk, allocates the cache, reads the superblock, opens the root source/file tree, repairs a copy-on-write root case, and starts metadata flush and snapshot timers in read-write mode.

Snapshot creation freezes the epoch lock, bumps epochs, forces source copy-on-write, creates destination snapshot directories, links source entries with snapshot/archive metadata, optionally creates an archive-ready second epoch, and kicks the archiver. The file also builds vac roots, syncs/halts/unhalts the fs, allocates qids, cleans expired snapshots by low epoch, removes old snapshot entries, and manages periodic snapshot/archive timing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/fs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/fs.h

Public-facing filesystem/file API declarations used by the 9P-facing fossil code. It forward-declares `Fs`, `File`, and `DirEntryEnum`, defines open modes (`OReadOnly`, `OReadWrite`, `OOverWrite`), and declares filesystem lifecycle, file operations, directory enumeration, snapshot cleanup, sync/halt, and vac export functions.

It also exposes `currfsysname` and `foptname` globals used by console/main initialization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/last.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/last.c

Tiny utility that reads a fossil disk image and prints the last archived Venti score as `vac:<score>`. It manually validates the header magic at 131072, extracts block size and superblock address, then reads the `Super.last` score field at the fixed packed offset.

It does not use the full fossil packing/cache layer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/last.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/nobwatch.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/nobwatch.c

No-op implementation of the block watch API. It provides empty `bwatchReset`, `bwatchInit`, `bwatchSetBlockSize`, `bwatchDependency`, `bwatchLock`, and `bwatchUnlock` functions.

This lets fossil build without the expensive debug lock-order watcher in `bwatch.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/nobwatch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/pack.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/pack.c

Binary packing/unpacking routines for fossil on-disk structures. It encodes/decodes headers, labels, entries, and superblocks using explicit big-endian integer macros and validates magic/version/state invariants.

It also maps local block addresses to fossil's pseudo-global score representation, maps scores back to local addresses, computes entry block types, and preserves fossil-specific local entry fields (`tag`, `snap`, `archive`) inside the Venti entry layout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/pack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/periodic.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/periodic.c

Small periodic callback thread abstraction. `periodicAlloc` records a callback, argument, and minimum 10 ms period, then starts a worker thread; `periodicKill` marks it for shutdown.

The worker sleeps in bounded intervals, calls the callback when due, advances the next deadline to avoid drift backlog, and frees its own state on exit.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/periodic.c -->