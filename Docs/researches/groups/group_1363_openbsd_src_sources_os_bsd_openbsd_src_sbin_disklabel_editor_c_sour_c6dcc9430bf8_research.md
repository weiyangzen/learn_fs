# Group Research: group_1363_openbsd_src_sources_os_bsd_openbsd_src_sbin_disklabel_editor_c_sour_c6dcc9430bf8

Scope: `Docs/research_subset_a.md`, source tree `sources/os/bsd/openbsd-src`.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/disklabel/editor.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/disklabel/editor.c

## Purpose
Implements the interactive `disklabel(8)` partition editor. It manages label mutation, undo state, OpenBSD area bounds, free-space discovery, auto-allocation policy, fstab mountpoint naming, size parsing, and partition alignment.

## Key Behavior
- `editor()` is the command loop. Commands include add, delete, modify, change size, set bounds, auto-partition, reset to defaults, write, quit, undo, restore original, save to file, print, show manual, and edit disklabel UID.
- Keeps three disklabel/mountpoint snapshots: original, last, and temporary undo buffers. If a command makes no effective change, undo state is restored.
- Ensures a raw `c` partition exists and covers the disk if absent.
- Refuses to start when existing partitions overlap unless overlaps can be resolved interactively by disabling one side.
- `editor_allocspace()` and allocation helpers apply OpenBSD default layouts (`alloc_big`, `alloc_medium`, `alloc_small`, `alloc_stupid`) or parsed custom auto-allocation tables.
- Auto-allocation picks the largest free chunk, assigns fstypes from mountpoint semantics (`swap`, `raid`, `/path`), and adjusts swap/var sizing based on physical memory.
- `editor_resize()` supports resizing auto-allocated FFS/swap layouts and repacks subsequent partitions.
- `free_chunks()`, `sort_partitions()`, `max_partition_size()`, and `editor_countfree()` provide the editor’s free-space model within `starting_sector` and `ending_sector`.
- `getuint64()`, `parse_sizespec()`, `apply_unit()`, `parse_sizerange()`, and `parse_pct()` parse sizes, ranges, percentages, relative changes, and units.
- `alignpartition()` centralizes offset/size rounding and overlap checks.
- `mpsave()` writes fstab entries, sorting mountpoints so parents precede children and optionally using DUID device names.

## Interfaces And Dependencies
- Depends on global state declared in `extern.h`: `lab`, `dkname`, `specname`, `fstabfile`, `mountpoints`, flags, display helpers, and `writelabel()`.
- Uses OpenBSD disklabel macros and structures from `<sys/disklabel.h>`.
- Uses UFS/FFS constants for fragment/block defaulting.
- Uses `DIOCGPDINFO` to reload prototype/default label data.

## Notes
This file is the behavioral center of `disklabel` editing. It mixes UI prompting, storage geometry policy, fstab generation, and disklabel structure mutation in one module.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/disklabel/editor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/disklabel/extern.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/disklabel/extern.h

## Purpose
Shared declarations for the `disklabel` utility.

## Key Contents
- Defines `MEG()` and `GIG()` size macros in disk blocks.
- Defines `DISCARD` and `KEEP` actions for `mpfree()`.
- Declares display, checksum, scaling, DUID, editor, mountpoint, auto-table, and write-label routines.
- Exposes global command/editor state: disk names, fstab path, mountpoints, flags, verbosity, quiet mode, and active `struct disklabel lab`.

## Notes
This header is the link between `editor.c` and the rest of `disklabel`, especially display, write, and global option state.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/disklabel/extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/disklabel/pathnames.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/disklabel/pathnames.h

## Purpose
Path constants for `disklabel`.

## Key Contents
- Includes `<paths.h>`.
- Defines `_PATH_TMPFILE` as `/tmp/EdDk.aXXXXXXXXXX`.
- Defines `_PATH_LESS` as `/usr/bin/less`.

## Notes
Used by editor/manual/tempfile behavior; intentionally minimal.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/disklabel/pathnames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dmesg/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/dmesg/Makefile

## Purpose
Builds the `dmesg` utility.

## Key Contents
- `PROG=dmesg`
- Installs `dmesg.8`.
- Links with `libkvm`.
- Adds `-Wall`.

## Notes
`libkvm` is required for `-M/-N` kernel memory/core reading support.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dmesg/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dmesg/dmesg.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dmesg/dmesg.c

## Purpose
Prints the kernel message buffer, either from the running kernel via `sysctl(3)` or from a kernel/core image via `kvm(3)`.

## Key Behavior
- Parses `-s`, `-M core`, and `-N system`.
- Without `-M/-N`, reads live message buffers using `KERN_MSGBUFSIZE`/`KERN_MSGBUF` or startup console buffers with `KERN_CONSBUFSIZE`/`KERN_CONSBUF`.
- With `-M/-N`, locates `_msgbufp` via `kvm_nlist()`, reads the `struct msgbuf`, validates `MSG_MAGIC`, and reads backing message bytes.
- Drops to `pledge("stdio")` after acquiring buffer access.
- Walks the circular buffer starting at `msg_bufx`.
- Skips syslog priority sequences that appear as newline followed by `<...>`.
- Uses `vis()` before printing characters so non-printable data is safely escaped.

## Notes
The implementation is careful about both live and offline message sources and avoids emitting raw control bytes.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dmesg/dmesg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dump/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/dump/Makefile

## Purpose
Builds `dump` and hard-links/installs it as `rdump`.

## Key Contents
- Sources: `itime.c`, `main.c`, `optr.c`, `dumprmt.c`, `tape.c`, `traverse.c`.
- Defines `RDUMP`.
- Links with `libutil`.
- Documents debugging knobs `DEBUG` and `TDEBUG`.

## Notes
The comments accurately describe each module’s role in the dump pipeline.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dump/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dump/dump.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/dump/dump.h

## Purpose
Central shared header for the UFS `dump` program.

## Key Contents
- Declares inode state maps: `usedinomap`, `dumpdirmap`, `dumpinomap`, plus `SETINO`, `CLRINO`, and `TSTINO`.
- Declares global dump configuration and runtime state: disk/tape paths, dump level, file descriptors, tape geometry, remote host, transfer stats, superblock, output blocking, DUID, and flags.
- Declares operator interface functions, mapping functions, dumping functions, tape writing functions, remote dump functions, and utility functions.
- Defines dump exit codes:
  - `X_FINOK`
  - `X_STARTUP`
  - `X_REWRITE`
  - `X_ABORT`
- Defines dumpdates structures and iteration macro `ITITERATE`.

## Notes
This header exposes most of the program as shared global state, reflecting the historical multi-file design.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dump/dump.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dump/dumprmt.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dump/dumprmt.c

## Purpose
Implements remote tape access for `rdump` using the historical `rmt(8)` protocol over `rcmd()`.

## Key Behavior
- `rmthost()` stores remote host/user, installs a SIGPIPE handler, and opens the remote shell connection.
- `rmtgetconn()` resolves `shell/tcp`, validates optional remote username, calls `rcmd()` to run `_PATH_RMT`, and tunes socket buffers/TCP options.
- `okname()` restricts remote usernames to ASCII alnum, `_`, and `-`.
- `rmtopen()`, `rmtclose()`, `rmtread()`, `rmtwrite()`, `rmtseek()`, and `rmtioctl()` encode protocol commands.
- `rmtreply()` parses `A`, `E`, and `F` replies, maps remote errno, and closes state on fatal replies.
- `rmtgets()` reads newline-terminated protocol response lines byte-by-byte.

## Notes
The code assumes trusted legacy remote-shell semantics and treats protocol desynchronization or connection loss as dump-aborting conditions.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dump/dumprmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dump/itime.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dump/itime.c

## Purpose
Reads, interprets, updates, and writes `/etc/dumpdates`.

## Key Behavior
- `initdumptimes()` opens the dumpdates file, creates it if missing, takes a shared lock, and reads records.
- `readdumptimes()` builds a linked list and an array view of dumpdate records.
- `getdumptime()` selects the most recent lower-level dump record for the current disk/DUID and stores it in `spcl.c_ddate`.
- `putdumptime()` takes an exclusive lock, rereads the file, updates or appends the current dump level/date, rewrites records, flushes, and truncates the file.
- `makedumpdate()` parses records using `DUMPINFMT`, canonicalizes names through DUID lookup when possible, and parses ctime-style timestamps with `strptime()`.

## Notes
The code supports both device names and DUIDs so historical dump records can match modern disk identifiers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dump/itime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dump/main.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dump/main.c

## Purpose
Main driver for UFS `dump`.

## Key Behavior
- Parses dump level and options for block size, density, tape/file target, estimated-only mode, dumpdates update, nodump honor level, tape geometry, remote output, and historical option syntax.
- Supports dumping a full mounted filesystem, a device/fstab entry, or a list of files/directories from one filesystem.
- Resolves device paths through `opendev()`, fstab lookup, raw device conversion, and DUID handling.
- Initializes `spcl` tape header metadata: host, device, filesystem name, dump level, date, and previous dump date.
- Opens the raw disk, reads disklabel info, probes UFS superblock candidates from `SBLOCKSEARCH`, and validates UFS1/UFS2.
- Allocates inode maps sized to the filesystem inode count.
- Computes dump size estimates, including map overhead, trailer blocks, tape changes, cartridge/9-track density assumptions, and blocks-per-file rounding.
- Runs the four dump passes:
  - Pass I maps regular files and directories.
  - Pass II propagates needed directory inclusion.
  - Pass III dumps directories.
  - Pass IV dumps regular files and non-directory inodes.
- Writes end headers, prints stats, updates dumpdates, rewinds/closes media, and broadcasts completion.
- `obsolete()` converts old compact dump option syntax into modern getopt-compatible arguments.

## Notes
`main.c` orchestrates the whole dump lifecycle but delegates inode walking to `traverse.c`, tape concurrency to `tape.c`, dumpdates to `itime.c`, and operator UI to `optr.c`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dump/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dump/optr.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dump/optr.c

## Purpose
Operator interaction, status reporting, fstab scanning, and “what needs dumping” reporting for `dump`.

## Key Behavior
- `query()` prompts on `/dev/tty`, repeats prompts via alarms, accepts yes/no answers, and adjusts dump timing to exclude operator wait time.
- `alarmcatch()` reprints or broadcasts attention requests every two minutes.
- `interrupt()` asks whether to abort on SIGINT.
- `broadcast()` invokes `wall -g operator` when notification is enabled.
- `timeest()` reports estimated completion every five minutes once enough blocks have been written.
- `msg()` and `msgtail()` format dump diagnostics and maintain `lastmsg` for broadcasts.
- `quit()` emits an error and aborts the dump.
- `getfstab()` collects dumpable FFS/UFS fstab entries.
- `fstabsearch()` matches by mountpoint, block device, raw device, DUID, and paths without leading slash.
- `lastdump()` implements `dump -w` and `dump -W`, sorting dumpdates and comparing against fstab frequencies.
- `datesort()` sorts by filesystem name and descending dump date.

## Notes
This file is the human recovery interface for a tool that may require tape changes or decisions after write/read failures.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dump/optr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dump/pathnames.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/dump/pathnames.h

## Purpose
Path constants for `dump`.

## Key Contents
- `_PATH_DUMPDATES` as `/etc/dumpdates`.
- `_PATH_LOCK` as `/tmp/dumplockXXXXXX`.
- `_PATH_RMT` as `/etc/rmt`.
- `_PATH_WALL` as `/usr/bin/wall`.

## Notes
The lock path is declared here even though this grouped subset’s read code primarily uses file locking on dumpdates.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dump/pathnames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dump/tape.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dump/tape.c

## Purpose
Handles dump output buffering, tape/file writes, media changes, checkpoint/rewrite recovery, and concurrent disk-read/tape-write slave processes.

## Key Behavior
- `alloctape()` allocates per-slave request buffers and aligned tape buffers sized by `ntrec * TP_BSIZE`.
- `writerec()` queues special/header records into the current tape block.
- `dumpblock()` queues filesystem data blocks as disk read requests translated to device blocks.
- `flushtape()` sends request batches to slaves, receives write results, detects EOT/short writes, advances tape counters, starts new media when size limits are reached, and updates estimates.
- `startnewtape()` implements checkpointing by forking. The parent preserves state and reforks on `X_REWRITE`; the child opens the output and continues.
- Supports comma-separated output device lists for successive volumes.
- `enslave()` forks three slave processes connected by socketpairs. Slaves coordinate write turns through SIGUSR2.
- `doslave()` reopens the disk, reads requested blocks into tape buffers, waits for its turn, writes to local or remote output, and reports byte counts to the master.
- `rollforward()` replays buffered records after EOT so the next volume starts at a coherent point.
- `trewind()` drains slave responses, closes/waits for slaves, closes/reopens tape devices as needed, and handles remote close/open checks.
- `tperror()`, `sigpipe()`, `dumpabort()`, and `Exit()` handle write failures and abort paths.
- `do_stats()` and `statussig()` report per-volume timing and transfer rate.

## Notes
This is the program’s most complex operational module. It combines historical tape behavior, process checkpointing, signal coordination, and partial-write/EOT recovery.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dump/tape.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dump/traverse.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dump/traverse.c

## Purpose
Traverses UFS metadata, builds dump inclusion maps, estimates dump size, and emits inode/data records.

## Key Behavior
- Defines a `union dinode` abstraction over UFS1 and UFS2 inode formats with `DIP()` field access.
- `blockest()` estimates tape blocks for an inode, accounting for holes and indirect block overhead.
- `mapfileino()` marks allocated inodes, directories, and modified files based on mtime/ctime versus previous dump date, with `UF_NODUMP` policy.
- `fs_mapinodes()` scans cylinder groups and initialized inode ranges.
- `mapfiles()` implements pass I for full filesystems or FTS-based file/directory subsets; ensures root inode is dumped.
- `mapdirs()` implements pass II, repeatedly scanning directories to include parents needed for modified descendants and propagate nodump exclusion.
- `dirindir()` and `searchdir()` walk direct and indirect directory blocks to detect dumped children/subdirectories.
- `dumpino()` emits headers and data for directories, regular files, symlinks, device nodes, FIFOs, sockets, and empty files.
- Short symlinks stored in inode data are dumped as inline data records.
- `dmpindir()`, `ufs1_blksout()`, and `ufs2_blksout()` walk direct/indirect block pointers and emit TS_ADDR/data records.
- `dumpmap()` writes inode bitmaps to tape.
- `writeheader()` fills magic/checksum fields for UFS1/UFS2 dump headers.
- `getino()` caches one inode block and returns the requested inode.
- `bread()` performs sector-aligned reads using disklabel geometry, retries hard reads sector-by-sector, zero-fills failed regions, and asks the operator after too many errors.

## Notes
This module is tightly coupled to UFS on-disk structures and the dump tape format. It is responsible for making incremental dumps restorable by preserving directory context.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dump/traverse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dumpfs/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/dumpfs/Makefile

## Purpose
Builds `dumpfs`.

## Key Contents
- `PROG=dumpfs`
- Installs `dumpfs.8`.
- Links with `libutil`.

## Notes
`libutil` is used for OpenBSD device-opening helpers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dumpfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dumpfs/dumpfs.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dumpfs/dumpfs.c

## Purpose
Prints detailed UFS/FFS superblock and cylinder-group information, or emits a `newfs` command approximation with `-m`.

## Key Behavior
- Parses `-m`; otherwise dumps filesystem internals.
- Resolves fstab mountpoint arguments through `getfsfile()`.
- Uses `pledge("stdio rpath disklabel")`.
- `open_disk()` opens a device with `opendev()` and probes superblock locations from `SBLOCKSEARCH`, validating UFS1/UFS2 magic, UFS2 self-location, and block size.
- `dumpfs()` prints superblock metadata:
  - magic/time/id
  - geometry and block/fragment sizes
  - optimization/minfree/symlink length
  - cylinder group counts
  - free block/inode summaries
  - allocation layout fields
  - flags, mountpoint, volume name, and swuid
- Reads and prints cylinder summary arrays.
- Iterates all cylinder groups via `dumpcg()`.
- `dumpcg()` prints cylinder group metadata, free summaries, fragment summaries, cluster summaries, inode-use bits, and block-free bits.
- `marshal()` prints a best-effort `newfs` command using values from the existing filesystem.
- `pbits()` prints compact ranges from bitmap fields.

## Notes
This is a diagnostic/introspection tool, not a repair tool. It directly formats UFS structures for operator inspection.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dumpfs/dumpfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/Makefile

## Purpose
Builds OpenBSD `fdisk`.

## Key Contents
- Sources include command handling, user interface, disk I/O, MBR, partition formatting, manual embedding, and GPT support.
- Generates `manual.c` from `fdisk.8` compressed into a byte array, or a placeholder when `NOMAN` is set.
- Links with `libutil`.
- Defines `HAS_MBR` on amd64, i386, and landisk.
- Adds a SH architecture workaround disabling builtin memcpy.

## Notes
The Makefile embeds the manual so the interactive command can display it through a pager.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/cmd.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/cmd.c

## Purpose
Implements interactive `fdisk` commands shared by GPT and MBR editing modes.

## Key Behavior
- `Xreinit()` reinitializes the current table as GPT or MBR and marks the session dirty.
- `Xswap()` swaps two GPT partition entries or two MBR partition entries.
- `Xedit()` edits a selected partition, or for GPT can recover a partition from a description string.
- `gedit()` edits GPT partition type, start LBA, end LBA/size, and name.
- `edit()` edits MBR partition type and either CHS boundaries or LBA offset/size.
- `Xsetpid()` changes only partition type/id.
- `Xselect()` descends into an extended MBR partition and edits its EMBR.
- `Xprint()` prints GPT, MBR, or geometry/no-table state.
- `Xwrite()` writes GPT or MBR, warns if multiple OpenBSD MBR partitions exist, and zaps GPT headers when writing MBR.
- `Xflag()` sets raw GPT attrs/MBR flags or marks one partition active/bootable.
- `Xmanual()` displays the embedded compressed manual through `$PAGER` or `/usr/bin/less`.
- `ask_num()`, `ask_pid()`, and `ask_uuid()` provide interactive prompts and validation.
- `parsepn()` validates partition indices based on GPT partition count or MBR slot count.
- `parseflag()` accepts decimal or hex GPT/MBR flag values.

## Notes
This file is the command adapter between user intent and the lower GPT/MBR/disk primitives. It avoids modifying protected GPT partition types.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/cmd.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/cmd.h

## Purpose
Declares command return codes and interactive command handlers for `fdisk`.

## Key Contents
- Return/status codes:
  - `CMD_EXIT`
  - `CMD_QUIT`
  - `CMD_CONT`
  - `CMD_CLEAN`
  - `CMD_DIRTY`
- Prototypes for reinit, manual, edit, setpid, select, swap, print, write, exit, quit, abort, help, flag, and update commands.

## Notes
The command return codes drive the higher-level user edit loop in files outside this grouped subset.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/cmd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/disk.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/disk.c

## Purpose
Provides disk opening, geometry normalization, and sector/byte read-write helpers for `fdisk`.

## Key Behavior
- `DISK_open()` opens the target via `opendev()`, requires a character device, reads prototype disklabel with `DIOCGPDINFO`, and derives disk geometry.
- Honors user-supplied disk size (`-l`) or geometry (`-c/-h/-s`) when provided.
- Caps MBR-visible geometry to the first `UINT32_MAX` sectors.
- Converts boot partition size/offset from DEV_BSIZE blocks to disk sectors.
- `DISK_printgeometry()` prints disk geometry and total size in requested units.
- `readsectors()` and `writesectors()` perform whole-sector I/O using `lseek()`, `read()`, and `write()`.
- `DISK_readbytes()` reads enough sectors for an arbitrary byte-sized structure and copies the requested bytes.
- `DISK_writebytes()` preserves unaffected sector bytes by read-modify-writing whole sectors.

## Notes
This abstraction lets GPT/MBR code operate on structure-sized records while respecting physical/logical sector sizes.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/disk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/disk.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/disk.h

## Purpose
Declares `fdisk` disk state and disk I/O helpers.

## Key Contents
- `struct disk` stores boot partition template, device name, fd, geometry, and sector count.
- Defines `BLOCKALIGNMENT` as 64 sectors, used for 32 KiB partition alignment.
- Declares `DISK_open()`, `DISK_printgeometry()`, `DISK_readbytes()`, and `DISK_writebytes()`.
- Exposes global `disk` and disklabel `dl`.

## Notes
The `BLOCKALIGNMENT` constant is shared by initialization and partition placement logic.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/disk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/fdisk.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/fdisk.c

## Purpose
Top-level driver for `fdisk`.

## Key Behavior
- Parses options for GPT/MBR initialization, GPT partition reinitialization, bootcode update, recovery, edit mode, geometry overrides, disk size override, boot partition template, default MBR file, verbosity, and assume-yes mode.
- Loads default MBR boot code from `_PATH_BOOTDIR "mbr"` when supported or from `-f`.
- Opens disk read-only for print-only mode or read-write for editing/initialization.
- Uses pledge profiles:
  - `stdio` for read-only print.
  - `stdio disklabel proc exec rpath` for editing/init/recovery/manual display.
- Initialization modes:
  - `-g`: create GPT.
  - `-A`: recreate GPT partition entries only.
  - `-i`: create MBR.
  - `-u`: update MBR boot code.
  - `-R`: recover GPT/MBR from disk or printed file.
- `parse_bootprt()` parses `blocks[@offset[:type]]`.
- `recover_disk_gpt()` attempts to recover GPT from disk primary/secondary structures.
- `recover_file_gpt()` and `recover_file_mbr()` reconstruct partition tables from printed `fdisk` output.
- `recover()` selects disk recovery or file recovery and falls back from GPT to MBR parsing.

## Notes
This file handles mode selection and safety prompts, while actual GPT/MBR mutation lives in dedicated modules.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/fdisk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/gpt.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/gpt.c

## Purpose
Implements GPT reading, validation, printing, recovery, initialization, editing helpers, and writing.

## Key Behavior
- Maintains global GPT state: protective MBR `gmbr`, header `gh`, and partition array `gp`.
- Converts GPT UTF-16LE partition names to/from simple ASCII strings.
- `gpt_chk_mbr()` and `protective_mbr()` validate the protective MBR with a single EFI/GPT partition.
- `get_header()` reads and validates a GPT header:
  - signature and revision
  - self LBA
  - header/entry sizes
  - partition count
  - header CRC
  - usable LBA range
  - partition table location
  - GUID decoding
- `get_partition_table()` reads partition entries, verifies CRC, decodes little-endian UUIDs and numeric fields.
- Accepts wrong-endian CRCs as a compatibility concession.
- `GPT_recover_partition()` either recovers from existing GPT structures or parses printed partition lines, UUID lines, and attributes lines.
- `GPT_read()` reads protective MBR plus primary/secondary/any GPT and clears state if invalid.
- `GPT_print()` prints usable LBA range, disk GUID in verbose mode, sorted partitions, and free ranges.
- `GPT_print_part()` prints type, start/size, optional GUID/name, and decoded attributes.
- `add_partition()` places a partition in the largest free range with `BLOCKALIGNMENT`.
- `init_gh()` creates a protective MBR and primary GPT header defaults.
- `init_gp()` creates EFI system and OpenBSD area partitions, preserving protected/required entries when only regenerating partition entries.
- `GPT_zap_headers()` clears primary and secondary GPT headers when switching to MBR.
- `GPT_write()` writes protective MBR, primary header/table, secondary header/table, recomputes CRCs, and reloads the kernel disklabel via `DIOCRLDINFO`.
- `sort_gpt()` and `lba_free()` compute sorted partitions and the largest free LBA span.
- `GPT_get_lba_start()`, `GPT_get_lba_end()`, and `GPT_get_name()` are interactive field editors.
- `crc32()` is a local GPT CRC implementation adapted from Hacker’s Delight.

## Notes
The module is conservative about protected/required GPT entries and validates both primary and secondary layouts against disklabel-derived disk size.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/gpt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/gpt.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/gpt.h

## Purpose
Declares GPT operations and GPT global state for `fdisk`.

## Key Contents
- Prototypes for read, recovery, field prompts, initialization, write, header zapping, and printing.
- Exposes `gmbr`, `gh`, and `gp`.
- Defines GPT selection constants: `ANYGPT`, `PRIMARYGPT`, `SECONDARYGPT`.
- Defines verbosity constants: `TERSE`, `VERBOSE`.
- Defines initialization mode constants: `GHANDGP`, `GPONLY`.

## Notes
This header is consumed by command, driver, and MBR code to coordinate GPT/MBR transitions.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/gpt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/mbr.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/mbr.c

## Purpose
Implements MBR initialization, conversion, printing, recovery, reading, writing, and validation.

## Key Behavior
- `MBR_init()` clears GPT globals, initializes either an extended MBR shell or a primary MBR with default boot code, optional boot partition, and OpenBSD partition.
- OpenBSD partition placement starts after a configured/default boot partition, after first track aligned to a power-of-two block, or after the MBR.
- `dos_mbr_to_mbr()` decodes on-disk `struct dos_mbr` into internal `struct mbr` and `struct prt` entries, recording how many leading bytes were zero.
- `mbr_to_dos_mbr()` encodes internal state back to on-disk little-endian DOS MBR structures.
- `MBR_print()` prints geometry, offset, signature, and four partition entries.
- `MBR_recover_partition()` parses printed MBR partition lines back into partition entries.
- `MBR_read()` reads a sector and decodes it.
- `MBR_write()` writes the MBR and reloads in-kernel disklabel info with `DIOCRLDINFO`.
- `MBR_valid_prt()` accepts all-zero MBRs as editable and otherwise validates signature and plausible partition bounds.

## Notes
This file deliberately keeps MBR-specific logic small and delegates CHS/LBA partition details to `part.c` outside this group.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/mbr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/mbr.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/mbr.h

## Purpose
Declares internal MBR representation and operations.

## Key Contents
- `struct mbr` stores:
  - first EMBR LBA
  - current MBR/EMBR LBA
  - boot code
  - four internal partition entries
  - signature
  - leading zero count from original DOS MBR
- Exposes default boot MBR `default_dmbr`.
- Declares print, init, read, recover, write, and validation functions.

## Notes
The internal representation carries extended-partition context alongside ordinary MBR data.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/mbr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/misc.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/misc.c

## Purpose
Shared utility functions for `fdisk`.

## Key Behavior
- Defines supported display/input units: bytes, sectors, KiB, MiB, GiB, TiB.
- `units_size()` converts sector counts into requested display units using disklabel sector size.
- `string_from_line()` reads from stdin, trims optionally, and bounds-checks copied input.
- `ask_yn()` prompts yes/no, honoring global `y_flag`.
- `getuint64()` prompts for bounded numeric values with support for:
  - default value
  - `*` as maximum
  - relative `+`/`-`
  - units `c`, `b`, `s`, `k`, `m`, `g`, `t`
- `hex_octet()` parses one-byte hex partition IDs.
- `string_to_uuid()` wraps `uuid_from_string()` while treating `uuid_s_bad_version` as acceptable.

## Notes
`getuint64()` is explicitly adapted from `disklabel/editor.c`, giving `fdisk` similar unit-aware interactive size entry.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/misc.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/misc.h

## Purpose
Declares shared `fdisk` utility types, constants, globals, and functions.

## Key Contents
- `struct unit_type` describes display unit abbreviation, conversion factor, and long name.
- Defines `nitems()` fallback.
- Defines whitespace, trim mode, and line buffer constants.
- Exposes global `verbosity`.
- Declares unit conversion, input, yes/no prompt, hex parsing, bounded numeric prompt, and UUID parsing helpers.

## Notes
This header supports both interactive command handling and GPT/MBR display code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/misc.h -->