# Group Research: group_365_freebsd_src_sources_os_bsd_freebsd_src_sbin_dump_dumprmt_c_sources_o_d9c611dce488

Scope: `Docs/research_subset_a.md`, source tree `sources/os/bsd/freebsd-src`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dump/dumprmt.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/dump/dumprmt.c

Implements the client side of the historical remote tape protocol used by `dump` when RDUMP support is enabled and an output target uses `host:tape` syntax.

Key responsibilities:
- Establishes a remote shell connection to the remote `rmt` program using `rcmd()`.
- Parses optional `user@host` remote endpoint syntax and validates usernames with `okname()`.
- Wraps remote tape operations: `rmtopen`, `rmtclose`, `rmtread`, `rmtwrite`, split write phases, `rmtseek`, `rmtstatus`, and `rmtioctl`.
- Tracks remote tape state with `TS_CLOSED` / `TS_OPEN`.
- Reads protocol replies of the form `A...`, `E...`, and `F...`, mapping remote errors into local `errno`.

Important data:
- `rmtpeer`: mutable remote host string, possibly split at `@`.
- `rmtape`: socket fd to the remote `rmt` command.
- `errfd`: stderr side channel from `rcmd()`.
- `mts`: global `struct mtget` populated by bytewise reads from `rmtstatus()`.

Notable behavior:
- `rmtgetconn()` uses service `shell/tcp`, local passwd name, `RMT` environment override, and fallback `_PATH_RMT`.
- Socket buffers are sized from `ntrec * TP_BSIZE`, capped around 60 KiB plus protocol slack.
- TCP options prefer throughput and disable Nagle via `TCP_NODELAY`.
- `SIGPIPE` is treated as remote connection loss and exits with `X_ABORT`.

Risks and constraints:
- Relies on legacy `rcmd()` / remote shell semantics.
- `rmtpeer` is modified in place when parsing `user@host`.
- `rmtseek()` uses `int offset`, with a comment noting the `off_t` mismatch.
- Protocol desynchronization is fatal via `rmtconnaborted()`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dump/dumprmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dump/itime.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/dump/itime.c

Maintains `/etc/dumpdates` state for `dump`, including reading prior dump records, selecting the base time for incremental dumps, and writing updated records.

Key responsibilities:
- `initdumptimes()` opens or creates the dumpdates file and takes a shared lock while reading.
- `readdumptimes()` parses all records into an SLIST, then builds `ddatev`, an array view used by iteration macros.
- `getdumptime()` finds the most recent dump of the same filesystem at a lower level and stores it in `spcl.c_ddate`.
- `putdumptime()` takes an exclusive lock, rereads current records, updates/adds this dump level, rewrites the file, truncates trailing old data, and reports the completed dump date.

Important data:
- `dumpdates`: path to dumpdates file, defaulted in `main.c`.
- `nddates`, `ddatev`, and `dthead`: in-memory dump date database.
- `lastlevel`: previous dump level selected for the current dump.
- `recno`: parser line counter, reset in `getrecord()`.

Parsing and formatting:
- Records use `DUMPINFMT` / `DUMPOUTFMT` from `<protocols/dumprestore.h>`.
- `makedumpdate()` parses the ctime-like date with `unctime()`.
- `dumprecout()` validates name length against `DUMPFMTLEN`.

Risks and constraints:
- `recno` resets for each `getrecord()` call, so malformed line reporting does not reflect absolute file line number.
- Update path allocates a fresh record for new entries but old SLIST storage is not globally freed; acceptable for a short-lived utility.
- Time fields convert between FreeBSD dump protocol time widths and `time_t` using `timeconv.h`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dump/itime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dump/main.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/dump/main.c

Main program for UFS `dump`. It parses options, resolves the target filesystem/device, optionally creates a live filesystem snapshot, calculates dump scope and media estimates, then drives the four dump passes.

Key responsibilities:
- Defines most global state shared by the dump subsystem: maps, device/tape names, dump level, density, blocking factor, media sizing, cache size, remote host, timing, superblock pointer, and pass number.
- Parses current and obsolete dump option formats via `getopt()` and `obsolete()`.
- Handles output routing to tape path, stdout, remote tape, or a pipeline command.
- Resolves filesystem names through `fstab`, opens raw devices, and warns about dumping live read-write filesystems without `-L`.
- Creates `.snap/dump_snapshot` through `_PATH_MKSNAP_FFS` when `-L` is valid.
- Reads the UFS superblock with `sbget()` and initializes block-size shifts and inode maps.
- Runs pass I (`mapfiles`), pass II (`mapdirs` until stable), pass III directories, and pass IV regular files.
- Writes end markers, performance summaries, updates dumpdates, rewinds, broadcasts completion, and exits.

Option highlights:
- Levels `0` through `9`, incremental base via dumpdates unless `-T`.
- `-a`, `-B`, `-b`, `-c`, `-d`, `-s` control media sizing.
- `-f` and `-P` are mutually exclusive output destinations.
- `-r`/`-R` provide rsync-friendly level-0 dumps by suppressing volatile times.
- `-W`/`-w` delegate to `lastdump()`.

Important logic:
- `getmntpt()` scans mounted filesystems by source device.
- `numarg()` validates numeric option ranges.
- `sig()` rewrites the current volume on recoverable signals and aborts on `SIGSEGV`.
- `rawname()` now accepts only existing character devices.
- `obsolete()` transforms legacy clustered flags and positional arguments into normal `getopt()` form.

Risks and constraints:
- UFS-specific: expects UFS superblocks and UFS inode layout.
- Snapshot creation uses `system()` with constructed command strings and fixed `.snap/dump_snapshot` naming.
- Live read-write dumping without `-L` is permitted but warned as unsafe.
- Many globals couple this file tightly to `tape.c`, `traverse.c`, `itime.c`, and `optr.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dump/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dump/optr.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/dump/optr.c

Operator interaction and status reporting support for `dump`.

Key responsibilities:
- `query()` asks yes/no questions on `/dev/tty`, periodically reprinting prompts through `SIGALRM`.
- `alarmcatch()` handles repeated attention prompts and optional operator broadcast mode.
- `interrupt()` asks whether to abort after `SIGINT`.
- `broadcast()` sends messages to the operator group through `wall -g operator`.
- `timeest()` computes percent complete and estimated finish time from `blockswritten`, `tapesize`, and elapsed write time.
- `infosch()` forces the next progress report.
- `msg()`, `msgtail()`, and `quit()` implement dump-specific diagnostic formatting and last-message tracking.
- `dump_getfstab()`, `fstabsearch()`, and `allocfsent()` build and search a UFS-only fstab table.
- `lastdump()` implements `dump -w` and `dump -W`.

Important data:
- `lastmsg`: retained for broadcast repetition.
- `timeout` and `attnmessage`: query prompt state.
- `tschedule`: next progress-report time.
- SLIST `table`: copied fstab entries used by dump lookup and lastdump.

Notable behavior:
- Query prompt repeats every 120 seconds.
- With `notify`, attention messages are sent to users in group `operator`.
- `lastdump()` sorts dumpdates by filesystem name and newest dump date before reporting.

Risks and constraints:
- Uses terminal interaction, alarms, and process title changes; behavior is intentionally operator-centric.
- `lastdump()` mutates the string returned by `ctime()` by truncating seconds/year display.
- `datesort()` subtracts `time_t` values into an `int`, which is historically common but width-sensitive.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dump/optr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dump/pathnames.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/dump/pathnames.h

Defines fixed path constants for `dump`.

Constants:
- `_PATH_DEFTAPE`: default output tape device `/dev/sa0`.
- `_PATH_DUMPDATES`: default dump date database `/etc/dumpdates`.
- `_PATH_LOCK`: lock template `/tmp/dumplockXXXXXX`.
- `_PATH_RMT`: remote tape command path `/etc/rmt`.

Notes:
- Includes `<paths.h>` for common FreeBSD path constants.
- `_PATH_LOCK` is not used by the files in this group but remains part of dump path definitions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dump/pathnames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dump/tape.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/dump/tape.c

Implements dump output buffering, tape/media volume handling, worker process I/O, write recovery, and tape-level checkpoints.

Key responsibilities:
- Allocates tape buffers and request arrays with `alloctape()`.
- Accepts logical tape records from traversal via `writerec()` and disk block references via `dumpblock()`.
- Flushes full tape records to worker processes with `flushtape()`.
- Handles end-of-tape, volume changes, rewinds, and roll-forward replay.
- Creates a checkpointing child per tape volume in `startnewtape()` so a failed volume can be rewritten from saved process state.
- Creates three worker processes with `create_workers()` to overlap disk reads and tape writes.
- Implements worker-side disk read and tape write loop in `worker()`.

Important data:
- `u_spcl`: dump protocol header union shared with `traverse.c`.
- `curino`, `newtape`: current inode and volume state used globally.
- `workers[WORKERS+1]`: per-worker request and data buffers, with one extra buffer for roll-forward reconstruction.
- `wp`, `nextblock`, `trecno`: current master-side buffer position.
- `lastspclrec`, `blocksthisvol`, `asize`: media accounting.

Concurrency model:
- Parent/master sends `struct req` arrays through socketpairs.
- Workers reopen the disk for independent seek pointers.
- Workers synchronize write order with a `SIGUSR2` ring and `setjmp`/`longjmp`.
- Tape errors signal the master with `SIGUSR1`; aborts signal `SIGTERM`.

Output modes:
- stdout pipe.
- `popen()` pipeline, with `DUMP_VOLUME` environment variable set per volume.
- local file/device.
- remote tape through `rmtopen()`/`rmtwrite()` when RDUMP is enabled.

Recovery behavior:
- Short writes are treated as EOT.
- `rollforward()` reconstructs pending requests after EOT and starts the next volume.
- `tperror()` asks the operator whether to restart; successful restart exits with `X_REWRITE` to parent checkpoint logic.

Risks and constraints:
- Heavy reliance on global state and fork-time process snapshots.
- Worker synchronization depends on signals and process ordering.
- EOT in final tape records is largely punted with an error asking for larger media or no size estimate.
- Pointer arithmetic on `void *`-like buffers is C-extension-friendly but not purely ISO C.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dump/tape.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dump/traverse.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/dump/traverse.c

Implements UFS inode traversal, dump map generation, inode serialization, block emission, extended attribute dumping, and disk read recovery.

Key responsibilities:
- `mapfiles()` scans allocated inodes, marks used inodes, directories, and changed inodes to dump.
- `mapdirs()` repeatedly prunes or adds directories based on whether they contain dumped files/subdirectories and propagates `UF_NODUMP`.
- `dumpino()` emits one inode and its file data or special-file metadata.
- `dmpindir()`, `ufs1_blksout()`, and `ufs2_blksout()` walk direct and indirect block trees and emit tape block maps.
- `appendextdata()` and `writeextdata()` append or separately emit UFS2 extended attribute data.
- `dumpmap()` writes inode maps as dump records.
- `writeheader()` fills dump protocol checksums and writes control records.
- `getino()` caches inode blocks and returns UFS1/UFS2 dinodes.
- `blkread()` reads filesystem blocks with recovery from short/hard errors.

Important macros:
- `DIP` / `DIP_SET`: abstract UFS1 versus UFS2 inode field access.
- `CHANGEDSINCE` and `WANTTODUMP`: incremental-dump selection with optional `UF_NODUMP` handling.
- `HASDUMPEDFILE` / `HASSUBDIRS`: directory search results.

Pass behavior:
- Pass I maps changed files and all directories, estimating tape blocks.
- Pass II repeats directory analysis until no parent/child inclusion changes remain.
- Pass III and IV are driven from `main.c` using maps produced here.

UFS details:
- Supports UFS1 and UFS2 inode layouts.
- Handles sparse files by clearing absent blocks in `spcl.c_addr`.
- Snapshot files are dumped as zero-length files and have `SF_SNAPSHOT` stripped in the dumped metadata.
- Root inode is always forced into `dumpinomap` because restore expects it.

Read recovery:
- `blkread()` handles non-sector-aligned reads by reading whole sectors and copying subranges.
- After repeated failures it asks the operator whether to continue, then retries sector-by-sector with zero-filled fallback data.

Risks and constraints:
- Deeply tied to FFS/UFS on-disk layout and dump protocol constants.
- `appendextdata()` contains a suspicious address test `&dp->dp2.di_extb[...] != 0`, which is always true for valid `dp`; this appears inherited and effectively marks ext blocks present based on address rather than block value.
- Error recovery may continue with zero-filled sectors, producing a restorable but incomplete dump.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dump/traverse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dump/unctime.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/dump/unctime.c

Provides `unctime()`, a small parser converting `ctime(3)`-style strings into `time_t`.

Behavior:
- Uses `strptime(str, "%a %b %e %T %Y", &then)`.
- Accepts strings ending immediately or at a newline.
- Sets `tm_isdst = -1` before `mktime()` so libc determines DST.
- Returns `(time_t)-1` on parse failure.

Usage:
- Used by dumpdates parsing in `itime.c`.
- Used by `main.c` for the `-T date` option.

Constraints:
- Locale-sensitive through `strptime()` weekday/month names.
- Input must match the ctime-style format without timezone.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dump/unctime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dumpfs/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/dumpfs/Makefile

Build definition for `dumpfs`.

Configuration:
- `PACKAGE=ufs`
- `PROG=dumpfs`
- `WARNS?=2`
- Links `libufs` through `LIBADD=ufs`
- Installs `dumpfs.8`
- Includes `<bsd.prog.mk>`

Role:
- Builds the UFS filesystem inspection utility implemented by `dumpfs.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dumpfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dumpfs/dumpfs.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/dumpfs/dumpfs.c

Implements `dumpfs`, a UFS superblock and cylinder-group inspection tool.

Key responsibilities:
- Opens each supplied filesystem/device using `libufs`.
- Finds the UFS superblock with `sbfind()`.
- Prints either filesystem ID, free-space list, reconstructable `newfs` command, superblock only, or full superblock plus cylinder groups.

Options:
- `-f`: print free block ranges; repeated `-ff` prints each free block individually.
- `-m`: marshal filesystem parameters into a `newfs` command.
- `-l`: print UFS ID path under `/dev/ufsid`.
- `-s`: print superblock only, skipping cylinder groups.

Important functions:
- `dumpfsid()` prints `/dev/ufsid/<fs_id>`.
- `dumpfs()` prints UFS1/UFS2 superblock fields, flags, check-hash flags, summary counters, and cylinder groups.
- `dumpcg()` prints per-cylinder-group metadata and bitmaps.
- `dumpfreespace()` / `dumpfreespacecg()` list free fragments.
- `marshal()` emits a `newfs` command approximating the existing filesystem.
- `pbits()` prints set-bit ranges.
- `pblklist()` prints free block ranges or individual blocks.
- `ufserr()` normalizes `libufs` and `errno` errors.

UFS details:
- Distinguishes UFS1 and UFS2 field layouts.
- Reports modern flags including soft updates, SUJ, ACL variants, TRIM, gjournal, indexed directories, and metadata check hashes.
- Uses `cgread()` to iterate cylinder groups through `libufs`.

Risks and constraints:
- Output is human-readable and stable enough for diagnostics, not a structured API.
- `marshal()` intentionally leaves some `newfs` options unimplemented.
- Some printed values are legacy UFS1-only fields and are conditional on `disk.d_ufs`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dumpfs/dumpfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dumpon/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/dumpon/Makefile

Build definition for `dumpon`.

Configuration:
- Includes `src.opts.mk`.
- `PACKAGE=runtime`
- `PROG=dumpon`
- Installs `dumpon.8`.
- If `MK_OPENSSL != no`, links `libcrypto` and defines `HAVE_CRYPTO`.
- Sets `OPENSSL_API_COMPAT=0x10100000L`.

Role:
- Builds the kernel dump-device configuration utility implemented by `dumpon.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dumpon/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dumpon/dumpon.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/dumpon/dumpon.c

Implements `dumpon`, configuring kernel crash dump targets, optional dump compression/encryption, priority insertion/removal, listing, and netdump.

Key responsibilities:
- Parses block-device dump targets, `off`, list mode, netdump parameters, compression flags, encryption key options, priority index, and remove mode.
- Opens dump devices under `/dev` if a bare name is supplied.
- Checks that local dump device size can hold physical memory unless minidumps are enabled or compression/removal applies.
- Configures kernel dump state through `DIOCSKERNELDUMP`.
- Lists current dump devices through `kern.shutdown.dumpdevname`.
- Lists verbose netdump configuration from `_PATH_NETDUMP` via `DIOCGKERNELDUMP`.

Netdump behavior:
- Requires server and client IPv4 addresses; gateway is optional.
- Resolves server names with `getaddrinfo()`.
- Finds default gateway on an interface using `getifaddrs()` plus routing-table `sysctl(NET_RT_DUMP)`.
- Warns if the configured interface is down.

Crypto behavior when built with OpenSSL:
- Supports `-k <pubkey>` and optional `-C chacha|aes-cbc`.
- Generates a random one-time kernel dump key.
- Encrypts it with RSA OAEP using the supplied public key.
- Rejects RSA keys below approximately 112 symmetric security bits.
- Rejects AES-CBC with compression.
- Runs key generation in a child that enters Capsicum capability mode, returning the configured structure and encrypted key via pipe.
- Explicitly zeroes key material before freeing.

Compression behavior:
- `-z` selects gzip; `-Z` selects zstd.
- Mutually exclusive.
- If kernel rejects compression with `EINVAL`, retries without compression and warns.

Risks and constraints:
- IPv4-only netdump configuration in this implementation.
- Encryption support depends on OpenSSL build option.
- Uses legacy OpenSSL RSA APIs guarded by compatibility defines.
- `find_gateway()` assumes route messages contain expected destination, mask, and gateway sockaddr fields.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/dumpon/dumpon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/etherswitchcfg/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/etherswitchcfg/Makefile

Build definition for `etherswitchcfg`.

Configuration:
- `PACKAGE=runtime`
- `PROG=etherswitchcfg`
- `SRCS=etherswitchcfg.c ifmedia.c`
- Adds kernel headers include path with `CFLAGS+= -I${SRCTOP}/sys`
- Installs `etherswitchcfg.8`
- Includes `<bsd.prog.mk>`

Role:
- Builds the userspace ioctl tool for Ethernet switch device configuration.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/etherswitchcfg/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/etherswitchcfg/etherswitchcfg.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/etherswitchcfg/etherswitchcfg.c

Implements `etherswitchcfg`, a command-line control utility for `/dev/etherswitchN`.

Key responsibilities:
- Opens a control device, default `/dev/etherswitch0`.
- Reads switch info and configuration via `IOETHERSWITCHGETINFO` and `IOETHERSWITCHGETCONF`.
- Prints switch configuration, port state, VLAN groups, media status, and supported media.
- Sets per-port PVID, media subtype, media options, LED style, and port flags.
- Sets VLAN group VID and membership/untagged masks.
- Sets global VLAN mode.
- Reads/writes raw switch registers and PHY registers.
- Dumps or flushes the address translation table.

Command model:
- Maintains a current mode: none, config, port, VLAN group, register, PHY register, or ATU.
- Mode transitions print the just-modified object before returning to command mode.
- `cmds[]` maps subcommands to modes, expected argument counts, and handler functions.

Important data:
- `struct cfg`: fd, verbosity, media listing flag, control path, switch configuration, switch info, current mode, and selected unit.
- `ledstyles[]`: maps user LED style strings to enum order.
- VLAN IDs validated against `IEEE802DOT1Q_VID_MAX`.

Notable behavior:
- Port flags support positive and negative forms such as `addtag` and `-addtag`.
- VLAN members use strings like `1,2t,3`, with suffix `t` meaning tagged.
- Media parsing/printing delegates to helpers in `ifmedia.c`.
- ATU dump iterates table entries with `IOETHERSWITCHGETTABLEENTRY`.

Risks and constraints:
- Mostly thin ioctl plumbing; correctness depends on kernel driver support.
- Some handlers do minimal parse validation, e.g. `strtol()` without full end-pointer checks in several command paths.
- Usage string starts with `etherswitchctl`, likely a stale name, while the program is `etherswitchcfg`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/etherswitchcfg/etherswitchcfg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/etherswitchcfg/ifmedia.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/etherswitchcfg/ifmedia.c

Provides media-word parsing and formatting helpers for `etherswitchcfg`, derived from ifconfig/ifmedia code.

Key responsibilities:
- Maps top-level media types to subtype, alias, option, and mode description tables.
- Parses user media subtype strings with `get_media_subtype()`.
- Parses media mode strings with `get_media_mode()`.
- Parses comma-separated option lists with `get_media_options()`.
- Performs case-insensitive lookup with `lookup_media_word()`.
- Prints media words in compact switch-config format via `print_media_word()`.
- Prints ifconfig-style media words via `print_media_word_ifconfig()`.

Important data:
- Description arrays initialized from kernel macros such as `IFM_TYPE_DESCRIPTIONS`, `IFM_SUBTYPE_ETHERNET_DESCRIPTIONS`, and related aliases/options.
- `ifmedia_types_to_subtypes[]` supports Ethernet, IEEE80211, and ATM style mappings plus shared types/options.

Notable behavior:
- `get_media_options()` copies the input because it tokenizes with `strtok()`.
- Unknown subtypes and types terminate with `errx()`.
- Unknown mode returns `-1`, letting callers decide behavior.
- Printers suppress alias entries when rendering canonical names.

Risks and constraints:
- Contains a large `#if 0` block of copied ifconfig functionality retained as reference but not compiled.
- The type-to-subtype table must remain consistent with `IFM_TYPE_DESCRIPTIONS` order.
- This is duplicated logic rather than linking a shared media parser.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/etherswitchcfg/ifmedia.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fdisk/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/fdisk/Makefile

Build definition for legacy `fdisk`.

Configuration:
- `PACKAGE=runtime`
- `PROG=fdisk`
- `SRCS=fdisk.c fdisk_mbr_enc.c`
- `WARNS?=4`
- Installs `fdisk.8`
- Links `libgeom`
- Includes `<bsd.prog.mk>`

Extra target:
- `test` builds the program and runs `runtest.sh`.

Role:
- Builds the deprecated MBR partition table editor.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fdisk/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fdisk/fdisk.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fdisk/fdisk.c

Implements deprecated FreeBSD MBR partition editor `fdisk`.

Key responsibilities:
- Prints a deprecation warning recommending `gpart`.
- Opens a target disk with `libgeom`.
- Detects media sector size by probing reads.
- Reads and writes MBR sector zero, including boot code and four DOS partition entries.
- Prints summary/configuration output.
- Initializes a whole-disk FreeBSD MBR slice with `-I`.
- Supports interactive partition editing, active partition selection, and boot code replacement.
- Supports non-interactive config files through `-f`.
- Infers root disk when no disk argument is supplied.

Important data:
- `struct mboot`: boot code buffer/size and decoded `struct dos_partition parts[4]`.
- Geometry globals: real and DOS/BIOS cylinders, heads, sectors, sectors per cylinder.
- Global option flags for `-B`, `-I`, `-a`, `-b`, `-f`, `-i`, `-p`, `-q`, `-s`, `-t`, `-u`, `-v`.
- `part_types[256]`: static MBR partition type descriptions.

Core functions:
- `get_params()` obtains firmware heads/sectors and media size through disk ioctls/libgeom.
- `read_s0()` validates MBR signature and decodes partition entries with `dos_partition_dec()`.
- `write_s0()` encodes partition entries and writes boot sectors.
- `init_boot()` reads boot code, default `/boot/mbr`.
- `init_sector0()` initializes boot code plus a FreeBSD partition.
- `change_part()`, `change_active()`, `change_code()` implement interactive modification.
- `dos()` converts LBA start/size into legacy CHS fields.
- `parse_config_line()`, `process_geometry()`, `process_partition()`, `process_active()`, and `read_config()` implement config-file mode.
- `sanitize_partition()` warns and optionally adjusts alignment.
- `get_rootdisk()` derives a whole-disk device from `/` mount source, stripping `.eli` and `.journal`.

Config file syntax:
- `g c<CYL> h<HEADS> s<SECTORS>`
- `p <partition> <type> <start|*> <size|*>`
- `a <partition>`

Risks and constraints:
- Deprecated and unavailable in FreeBSD 16 or later per runtime warning.
- MBR/BIOS CHS assumptions are legacy and can be invalid for modern disks.
- `read_disk()` and `write_disk()` seek using `sector * 512` even while supporting variable `secsize`; the file comments acknowledge hardcoded sector-size behavior in write path.
- Many interactive inputs use simple decimal parsing and prompts, fitting legacy admin tooling rather than robust batch validation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fdisk/fdisk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fdisk/fdisk_mbr_enc.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fdisk/fdisk_mbr_enc.c

Encodes and decodes packed on-disk MBR partition entries.

Key responsibilities:
- `dos_partition_dec()` copies the 16-byte MBR partition entry byte stream into a native `struct dos_partition`.
- `dos_partition_enc()` writes a native `struct dos_partition` back into the 16-byte MBR entry format.
- Uses `le32dec()` and `le32enc()` for `dp_start` and `dp_size`.

Important fields:
- Byte fields: flag, starting CHS, type, ending CHS.
- Little-endian 32-bit fields: starting LBA and sector count.

Notes:
- The file explicitly performs no validation or sanity checking.
- Intended to be usable in both kernel and userland contexts.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fdisk/fdisk_mbr_enc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fdisk/fdisk_mbr_enc.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/fdisk/fdisk_mbr_enc.h

Header for MBR partition entry encode/decode helpers.

Contents:
- Uses `#pragma once`.
- Forward declares `struct dos_partition`.
- Declares:
  - `dos_partition_dec(void const *pp, struct dos_partition *d)`
  - `dos_partition_enc(void *pp, struct dos_partition *d)`

Role:
- Shared by `fdisk.c` and `fdisk_mbr_enc.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fdisk/fdisk_mbr_enc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fdisk/runtest.sh -->
# File Research: sources/os/bsd/freebsd-src/sbin/fdisk/runtest.sh

Regression test script for legacy `fdisk`.

Test flow:
- Creates a 4 MiB memory disk with `mdconfig`, using geometry `-x 63 -y 16`.
- Verifies `/dev/${MD}` materializes.
- Registers a trap to destroy the md device on exit or signal.
- Creates a one-sector zero bootcode file named `tmp`.
- Runs `./fdisk -b tmp -I $MD`.
- Checks the resulting first-sector checksum against an expected MD5.
- Runs `./fdisk $MD` and checks its textual output MD5.
- Prints `PASSED` messages or exits with failure.

Risks and constraints:
- Requires FreeBSD `mdconfig`, `dd`, and `md5`.
- Depends on exact output formatting and deterministic MBR layout.
- Creates/removes a local temporary file named `tmp` in the working directory.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fdisk/runtest.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ffsinfo/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ffsinfo/Makefile

Build definition for `ffsinfo`.

Configuration:
- Reuses growfs debug support through:
  - `GROWFS= ${.CURDIR:H}/growfs`
  - `.PATH: ${GROWFS}`
- `PACKAGE=ufs`
- `PROG=ffsinfo`
- `SRCS=ffsinfo.c debug.c`
- Installs `ffsinfo.8`
- `WARNS?=1`
- Adds `-DFS_DEBUG -I${GROWFS}`
- Links `libufs`
- Includes `<bsd.prog.mk>`

Role:
- Builds a detailed UFS metadata dump tool using shared debug dumping routines from `growfs`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ffsinfo/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ffsinfo/ffsinfo.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ffsinfo/ffsinfo.c

Implements `ffsinfo`, a diagnostic utility that dumps detailed UFS/FFS metadata for comparison before/after repair or growth operations.

Key responsibilities:
- Opens a UFS device with `libufs` and locates the superblock.
- Dumps selected metadata levels through debug macros from `growfs/debug.c`.
- Supports selecting a cylinder group, inode, detail level, and output file.
- Dumps primary and backup superblocks, cylinder summaries, cylinder groups, inode maps, fragment maps, cluster maps/summaries, inodes, and indirect block trees.

Options:
- `-g cylinder_group`: select one group; `-1` means last group; omitted means all.
- `-i inode`: dump a specific inode.
- `-l level`: bitmask controlling dump detail, valid `0x1` through `0x3ff`.
- `-o outfile`: debug output destination, default `-`.

Important data:
- `disk`: global `struct uufsd`.
- `fsun`: superblock scratch buffer.
- `i1blk`, `i2blk`, `i3blk`: buffers for indirect block traversal.
- `fscs`: allocated filesystem cylinder summary copy.

Detail-level behavior:
- `0x001`: primary superblock.
- `0x002`: backup superblocks.
- `0x004`: cylinder summaries.
- `0x008`, `0x010`, `0x020`, `0x040`: cylinder group and allocation maps.
- `0x100`: inode structures.
- `0x200`: direct/indirect block pointer traversal.

Inode dumping:
- `dump_whole_ufs1_inode()` and `dump_whole_ufs2_inode()` are parallel implementations for UFS1/UFS2 pointer sizes.
- Skip inodes with `di_nlink == 0`.
- Dump inode structure when requested.
- Follow single, double, and triple indirect blocks while accounting for remaining file blocks.

Risks and constraints:
- Diagnostic output depends on debug macros from growfs, not local formatting code.
- Indirect traversal assumes nonzero indirect block pointers when remaining blocks imply indirection; corrupted filesystems may cause read errors.
- In nested triple-indirect comments, the final formatted path uses `ind3ctr` twice where one field likely intended `ind2ctr`; this affects diagnostics only.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ffsinfo/ffsinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck/Makefile

Build definition for generic `fsck` dispatcher.

Configuration:
- `PACKAGE=runtime`
- `PROG=fsck`
- `SRCS=fsck.c fsutil.c preen.c`
- Installs `fsck.8`
- Links `libutil`
- Includes `<bsd.prog.mk>`

Role:
- Builds the filesystem-check dispatcher that invokes filesystem-specific `fsck_<type>` helpers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck/fsck.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck/fsck.c

Implements the generic `fsck` front-end, selecting filesystems and invoking filesystem-specific checker binaries.

Key responsibilities:
- Parses global fsck options, type filters, per-type options, and alternate fstab path.
- If no operands are supplied, checks fstab entries through `checkfstab()`.
- If operands are supplied, resolves devices/mountpoints/fstab entries and runs appropriate `fsck_<type>`.
- Supports preen/clean modes, always-yes/no propagation, force, verbose, debug, and background-check modes.
- Guesses filesystem type from GEOM partition attribute `PART::type` if no fstab/type information is available.

Important functions:
- `isok()` decides whether an fstab entry should be checked now.
- `checkfs()` normalizes filesystem type, builds `fsck_<type>` argv, forks with `vfork()`, and runs `execvP()` in `_PATH_SYSPATH`.
- `selected()` checks `-t` type inclusion/exclusion list.
- `addoption()` stores `-T fstype:options` per-type options.
- `maketypelist()` parses `-t` and `no...` exclusion mode.
- `catopt()` appends comma-separated option strings.
- `mangle()` converts comma-separated options into argv entries, handling dash options and `-o` options.
- `getfstype()` maps partition type hints such as `ufs`, `ffs`, `fat`, and `efi`.

Background check behavior:
- `-B` performs needed background checks.
- `-F` asks filesystem checkers whether checks can be deferred.
- `-B` and `-F` are mutually exclusive.
- Read-only and `noauto` filesystems are excluded from background deferral paths.

Risks and constraints:
- Dispatch model depends on external helper binaries in `_PATH_SYSPATH`.
- Uses `vfork()`, so parent variables are treated carefully.
- Type mapping is intentionally small and heuristic.
- `fsck` itself does not repair filesystems; it orchestrates specific checkers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck/fsck.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck/fsutil.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck/fsutil.c

Utility functions shared by generic `fsck` and related fsck code.

Key responsibilities:
- `getfsopt()` tests whether an fstab mount option or its `no...` inverse is present.
- `setcdevname()` and `cdevname()` maintain current device name and preen mode.
- `pfatal()`, `pwarn()`, `perr()`, and `panic()` provide fsck-style message handling.
- `devcheck()` validates that a path exists and is a character device.
- `emalloc()`, `erealloc()`, and `estrdup()` are checked allocation wrappers.

Important behavior:
- In preen mode, fatal messages include the device name and print “UNEXPECTED INCONSISTENCY; RUN <prog> MANUALLY.” before exiting with status 8.
- `getfsopt()` handles six positive/negative mount option cases, treating `foo` and `nofoo` distinctly.
- `devcheck()` currently stats `/` and the supplied device and emits errors through `perr()`.

Risks and constraints:
- `getfsopt()` assumes `strdup()` succeeds; unlike allocation wrappers, it does not check for NULL.
- `devcheck()` returns the original name even after reporting problems, so callers must rely on fatal behavior or later errors.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck/fsutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck/fsutil.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck/fsutil.h

Header for generic fsck utility functions and option flags.

Declarations:
- `checkfstab()`
- `getfsopt()`
- `pfatal()`, `pwarn()`, `perr()`, `panic()`
- `devcheck()`
- `cdevname()`, `setcdevname()`
- `emalloc()`, `erealloc()`, `estrdup()`

Flags:
- `CHECK_PREEN`
- `CHECK_VERBOSE`
- `CHECK_DEBUG`
- `CHECK_BACKGRD`
- `DO_BACKGRD`
- `CHECK_CLEAN`

Role:
- Provides the shared API between `fsck.c`, `fsutil.c`, and `preen.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck/fsutil.h -->