# Group Research: group_1376_openbsd_src_sources_os_bsd_openbsd_src_sbin_mountd_mountd_c_sources_de923e0d8808

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/openbsd-src` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mountd/mountd.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/mountd/mountd.c

`mountd.c` implements OpenBSD's NFS mount protocol daemon. It parses `/etc/exports`, maintains the in-memory export tree and remote mount list, registers RPC mount protocol versions 1 and 3 over UDP/TCP, answers mount/dump/unmount/export RPCs, and pushes export rules into the kernel.

The daemon is split into an unprivileged parent and privileged child connected by `imsg`. The parent pledges `stdio rpath inet dns getpw`, handles RPC requests, parses exports, and asks the child to perform privileged `getfh()`, `mount(... MNT_UPDATE ...)`, `MNT_DELEXPORT`, and `/var/db/mountdtab` updates. The child unveils `/` read-only plus the mount list path read/write/create, then services fixed-size imsg requests.

Export parsing is centered on `get_exportlist()`, `do_opt()`, `do_mount()`, `get_host()`, `get_net()`, `parsecred()`, and directory tree helpers. It supports directory lists, host/netgroup entries, `-ro`, `-maproot`, `-mapall`, `-mask`, `-network`, and `-alldirs`. It rejects inconsistent options such as `-mapall` plus `-maproot`, `-mask` without `-network`, and `-alldirs` with multiple directories.

RPC handling in `mntsrv()` enforces reserved source ports for mount and unmount operations, canonicalizes requested paths with `realpath()`, validates file/directory existence, checks the export tree by filesystem id and client address, obtains an NFS file handle through the privileged child, and updates the remote mount list. XDR helpers serialize mount lists, export lists, paths, and NFSv2/NFSv3 file handle replies.

Notable details: only IPv4 host/network export matching is represented here; export deletion is applied to local exportable filesystem types found via `getmntinfo()`; mount-list persistence is mediated through imsg; signal state is tracked through `sig_atomic_t` flags and processed inside the RPC poll loop.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mountd/mountd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mountd/pathnames.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/mountd/pathnames.h

`pathnames.h` defines the fixed filesystem paths used by `mountd`: `_PATH_EXPORTS` as `/etc/exports`, `_PATH_RMOUNTLIST` as `/var/db/mountdtab`, and `_PATH_MOUNTDPID` as `/var/run/mountd.pid`.

It also includes `<paths.h>`. The file is small but centralizes the daemon's persistent export input, remote mount-list database, and pidfile locations.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mountd/pathnames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ncheck_ffs/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/ncheck_ffs/Makefile

This Makefile builds `ncheck_ffs`, links it with `libutil`, installs `ncheck_ffs.8`, and creates a hardlink/symlink-style installed command alias from `ncheck` to `ncheck_ffs`.

It includes `<bsd.prog.mk>` and has no custom source list because the default source is `ncheck_ffs.c`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ncheck_ffs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ncheck_ffs/ncheck_ffs.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/ncheck_ffs/ncheck_ffs.c

`ncheck_ffs.c` implements a read-only FFS inode-to-path scanner. It opens a raw device or resolves a mounted filesystem through `fstab`, reads the disklabel and FFS superblock, scans allocated inodes, caches directory inodes, and walks from `ROOTINO` to print pathnames for selected inodes.

The main controls are `-a` for dot entries, `-i` for explicit inode numbers, `-s` for setuid/special filtering, `-m` for verbose mode/uid/gid output, and `-f` for custom output formatting with escapes such as `\I` and `\P`. Without explicit inode selection it builds an inode list according to the filter and then searches directory entries.

Core routines include `findinodes()`, `getino()`, `bread()`, `scanonedir()`, `dirindir()`, `searchdir()`, `cacheino()`, and `format_entry()`. `bread()` attempts whole-block reads first, then falls back to sector-sized reads with zero fill for failed sectors, aborting after repeated errors.

The implementation supports both UFS1 and UFS2 dinodes through the `DIP()` macro. After opening and validating the device it pledges `stdio`, so the remaining work is raw file descriptor reads and stdout output.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ncheck_ffs/ncheck_ffs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/newfs/Makefile

This Makefile builds the `newfs` utility from `dkcksum.c`, `getmntopts.c`, `newfs.c`, and `mkfs.c`, installs `newfs.8`, links `libutil`, and installs `mount_mfs` as a link to `newfs`.

It compiles with `-DMFS` and includes sources from `../mount` and `../disklabel`, giving the binary both normal FFS creation and memory filesystem mount behavior.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs/mkfs.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/newfs/mkfs.c

`mkfs.c` is the FFS filesystem-construction backend used by `newfs.c`. It consumes parameters selected by the front end, validates block/fragment sizes and filesystem size, lays out the FFS superblock, chooses cylinder group geometry, writes backup superblocks and cylinder group maps, initializes inode tables, creates the root directory, writes summary information, and updates the disklabel partition fields.

It supports both FFS1 and FFS2 through `Oflag`. FFS1 compatibility fields, fake geometry values, inode sizes, indirect block counts, superblock locations, and maximum symlink lengths are selected separately from FFS2. For FFS2 creation it also invalidates an old FFS1 superblock if one is present.

Important routines are `mkfs()`, `initcg()`, `fsinit1()`, `fsinit2()`, `makedir()`, `alloc()`, `iput()`, `rdfs()`, `wtfs()`, and bitmap helpers `isblock()`, `clrblock()`, and `setblock()`. `checksz()` estimates whether `fsck_ffs` will exceed available data-size/physical-memory bounds.

When running as `mount_mfs`, writes and reads target an anonymous `mmap()` region instead of a device. `Nflag` suppresses writes for dry runs. The backend initializes generation numbers with `arc4random()` and records a random filesystem id component.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs/mkfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs/newfs.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/newfs/newfs.c

`newfs.c` is the front end for FFS filesystem creation and, when invoked as `mount_mfs`, for memory filesystem setup. It parses filesystem parameters, opens and validates target devices, checks mounted-filesystem state, reads disklabels, selects partition size and sector size, chooses defaults, and calls `mkfs()`.

The command supports FFS-specific options for dry run, FFS version, sector size, disktype, block/fragment size, cylinder group sizing, inode density, minfree, optimization preference, quiet mode, filesystem size, and helper dispatch through `-t`. If `-t` or disklabel filesystem type indicates a non-FFS filesystem, it execs `newfs_<fstype>` from `/sbin` or `/usr/sbin`.

For normal device operation it refuses block devices, warns for non-character devices, rejects targets already mounted, reads partition data from the disklabel, and pledges `stdio disklabel tty` after setup. If `mkfs()` mutates partition metadata, `rewritelabel()` writes the checksum-corrected disklabel back.

The MFS path fakes or reads a label, captures mountpoint ownership/mode, creates the in-memory filesystem, forks a child to mount it, optionally pre-populates it with `pax`, and waits for the mount to appear. Helpers cover temporary mountpoint creation, copy orchestration, child exec/wait, and mount completion polling.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs/newfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs/pathnames.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/newfs/pathnames.h

`pathnames.h` defines directories searched by `newfs` when dispatching helper binaries: `_PATH_SBIN` as `/sbin` and `_PATH_USRSBIN` as `/usr/sbin`.

It also defines `_PATH_MNT` as `/mnt`, used by the MFS temporary mountpoint fallback when `/tmp` is not writable.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs/pathnames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs_ext2fs/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/newfs_ext2fs/Makefile

This Makefile builds `newfs_ext2fs` from `newfs_ext2fs.c`, `mke2fs.c`, and `ext2fs_bswap.c`, installing `newfs_ext2fs.8`.

It adds `../../sys/ufs/ext2fs` to `.PATH` for the byte-swap support source and links against `libutil`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs_ext2fs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs_ext2fs/extern.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/newfs_ext2fs/extern.h

`extern.h` declares the shared interface between the `newfs_ext2fs` front end and `mke2fs` backend. It defines local ext2 maximum block-size constants, `nitems()` if missing, and the `mke2fs(const char *, int)` prototype.

It also declares global option/state variables populated by `newfs_ext2fs.c`: dry-run flag, ext2 format revision, verbosity, filesystem size, inode size, sector/fragment/block sizes, minfree, inode count override, and volume name.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs_ext2fs/extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs_ext2fs/mke2fs.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/newfs_ext2fs/mke2fs.c

`mke2fs.c` constructs an ext2 filesystem without depending on GPL e2fsprogs code. It validates sizes, initializes ext2 superblock fields, computes block group geometry, allocates group descriptors, writes primary and backup metadata, initializes bitmaps and inode tables, creates root and `lost+found`, and optionally prepares REV1 resize metadata.

The builder supports conservative REV0 and REV1. REV1 enables file type directory entries, sparse superblocks, large files, and resize-compatible reserved group descriptor blocks when possible. It sets the creator OS to Linux for firmware compatibility and generates a version-4 UUID with `arc4random_buf()`.

Core routines are `mke2fs()`, `initcg()`, `zap_old_sblock()`, `cgoverhead()`, `fsinit()`, `makedir()`, `copy_dir()`, `init_resizeino()`, `alloc()`, `iput()`, `rdfs()`, `wtfs()`, `ilog2()`, and `skpc()`. On-disk structures are saved through ext2 byte-order helpers, with explicit little-endian conversion for directory entries and block pointers.

Before writing, it validates access to the final sector and zaps old superblock magic values at likely ext2/FFS/LFS superblock locations to reduce fsck confusion. `Nflag` performs layout/reporting without writes.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs_ext2fs/mke2fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs_ext2fs/newfs_ext2fs.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/newfs_ext2fs/newfs_ext2fs.c

`newfs_ext2fs.c` is the command-line and device front end for `mke2fs()`. It parses options for image-file mode, ignoring partition type, dry run, ext2 revision, sector size, verbosity, zeroing, block/fragment size, inode density/count, minfree, filesystem size, and volume name.

It supports regular image creation with `-F`, including optional `ftruncate()` and pre-zeroing/de-sparsifying with `-Z`. For device targets it opens via `opendev()`, rejects mounted devices unless dry-run, reads disklabel/partition information, and requires the partition type to be `FS_EXT2FS` unless `-I` is supplied.

Default block size and inode count are selected from filesystem-size tiers. Size suffix parsing is handled by `strsuftoi64()`, with sector-count vs byte-size distinction for `-s`. After setup it calls `mke2fs()` and closes the descriptor.

The program pledges `stdio rpath wpath cpath disklabel`, reflecting its need to inspect labels and optionally create/write image files.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs_ext2fs/newfs_ext2fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs_msdos/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/newfs_msdos/Makefile

This Makefile builds the standalone `newfs_msdos` utility, installs `newfs_msdos.8`, and links against `libutil`.

There is no custom source list because the default source file is `newfs_msdos.c`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs_msdos/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs_msdos/newfs_msdos.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/newfs_msdos/newfs_msdos.c

`newfs_msdos.c` constructs FAT12, FAT16, and FAT32 filesystems. It parses geometry, FAT type, boot-sector, OEM, label, volume id, cluster, reserved-sector, FAT count, FAT size, root-directory, hidden-sector, and standard floppy-format options, then writes boot sectors, BPB/extended BPB fields, FAT headers, FAT32 info/backup sectors, and optional volume-label directory entries.

The tool opens the target with `opendev()`, rejects mounted targets unless `-N`, rejects block devices, warns for non-character devices, and derives geometry/size/hidden-sector data from disklabel when not fully supplied. Standard formats cover classic floppy sizes.

FAT type is inferred when not explicit by checking whether the requested geometry fits FAT12, FAT16, or FAT32 cluster constraints. It computes reserved sectors, root directory sectors, sectors-per-cluster, sectors-per-FAT, and cluster count, enforcing FAT-specific limits.

If a boot file is supplied with `-B`, sectors are copied from it; otherwise the file writes built-in minimal boot code and a DOS magic. FAT32-specific handling includes info and backup sectors. `-N` performs validation and reporting without writes. The program pledges `stdio rpath wpath disklabel`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/newfs_msdos/newfs_msdos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/nfsd/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/nfsd/Makefile

This Makefile builds the `nfsd` daemon and installs `nfsd.8`.

It explicitly clears `LDSTATIC`, so `nfsd` is not linked as a static binary by default.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/nfsd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/nfsd/nfsd.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/nfsd/nfsd.c

`nfsd.c` is the userland control daemon that starts kernel NFS server workers and registers UDP/TCP NFS service sockets. It parses `-n`, `-r`, `-t`, and `-u`; defaults to UDP if neither protocol is selected; and supports a legacy trailing daemon-count argument.

Normal startup daemonizes, forks up to 20 worker children that call `nfssvc(NFSSVC_NFSD)`, creates/binds the UDP NFS socket and/or TCP listener on `NFS_PORT`, registers NFSv2 and NFSv3 with portmap, and hands sockets to the kernel using `nfssvc(NFSSVC_ADDSOCK)`. TCP mode keeps a master process accepting connections and passing accepted sockets into the kernel with peer address metadata.

The `-r` mode only re-registers selected protocols with portmap and exits. Signal handlers report missing NFS syscall support on `SIGSYS` and reap child processes on `SIGCHLD`.

The daemon unveils `/` with no permissions and then locks unveil, reflecting that it should not need filesystem access after setup.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/nfsd/nfsd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/nologin/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/nologin/Makefile

This Makefile builds the `nologin` utility and installs `nologin.8`.

It has no custom source list or linker settings beyond including `<bsd.prog.mk>`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/nologin/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/nologin/nologin.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/nologin/nologin.c

`nologin.c` implements the login shell that always refuses access. It unveils `/etc/nologin.txt` read-only, pledges `stdio rpath`, tries to open that file, and writes its contents to stdout if present.

If `/etc/nologin.txt` cannot be opened, it writes the built-in default message `This account is currently not available.`. It exits with status 1 in all cases.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/nologin/nologin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/Makefile

This Makefile builds `pdisk` only on `macppc`. On that architecture it compiles `dump.c`, `file_media.c`, `io.c`, `partition_map.c`, and `pdisk.c`, links `libutil`, and enables `-Wall`.

On other architectures it sets `NOPROG=yes`. The manual page is installed under the `macppc` manual subdirectory.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/dump.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/dump.c

`dump.c` contains Apple partition map display routines for `pdisk`. It prints concise partition maps, block-zero driver-map summaries, full partition entry details, raw reserved-field hex/ascii dumps, and internal structure state.

Primary entry points are `dump_partition_map()`, `full_dump_partition_entry()`, `full_dump_block_zero()`, and `show_data_structures()`. Helper routines compute display column widths from partition type/name/base/length values and render individual partition rows.

The output highlights partition type, name, base, length, driver presence, flags, logical block ranges, boot metadata, checksums, processor identifiers, device block size/count, and driver descriptor entries. It relies on `partition_map.h` structures and linked-list ordering.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/dump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/dump.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/dump.h

`dump.h` declares the public dump/display interface for `pdisk`: `dump_partition_map()`, `full_dump_partition_entry()`, `full_dump_block_zero()`, and `show_data_structures()`.

It is guarded by `__dump__` and expects `struct partition_map` declarations from the including context.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/dump.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/file_media.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/file_media.c

`file_media.c` handles raw 512-byte sector I/O and byte-order conversion for `pdisk`'s Apple partition map structures. It defines packed byte-array representations for block zero, driver descriptor entries, and partition map entries, then copies fields to/from host structures with explicit big-endian conversion.

The low-level `read_block()` and `write_block()` wrap `pread()`/`pwrite()` at `DEV_BSIZE` sector offsets. Public functions `read_block0()`, `write_block0()`, `read_dpme()`, and `write_dpme()` translate between on-disk bytes and `partition_map.h` structures.

The file preserves reserved fields as opaque byte arrays and uses bounded string copies for partition name/type/processor id. Some write-side conversions use `betoh32()` where `htobe32()` would be expected, which is harmless on big-endian `macppc` but notable if reused elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/file_media.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/file_media.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/file_media.h

`file_media.h` declares `pdisk`'s disk-media serialization API: block-zero read/write and individual partition-map-entry read/write.

The functions operate on a file descriptor, sector number where applicable, and `struct partition_map` or `struct entry` instances supplied by the partition map layer.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/file_media.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/io.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/io.c

`io.c` provides interactive input helpers for `pdisk`. It implements a small unget buffer, command prompting, yes/no confirmation, numeric argument parsing, quoted or unquoted partition string parsing, suffix multipliers, partition modifiers, digit counting, and bad-input reporting.

Key functions include `get_command()`, `get_okay()`, `get_number_argument()`, `get_dpistr_argument()`, `get_multiplier()`, `get_partition_modifier()`, `flush_to_newline()`, and `bad_input()`. `get_string()` limits partition strings to `DPISTRLEN` and returns a freshly allocated copy.

The parser is deliberately simple and command-line oriented: whitespace is skipped, newlines can reprint prompts, quoted strings are supported, and invalid trailing characters cause parsing failure or input flushing.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/io.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/io.h

`io.h` declares the interactive parsing helpers used by `pdisk`, including numeric parsing, confirmation prompts, command reads, partition string reads, suffix multipliers, partition modifiers, digit counting, newline flushing, pushback, and formatted bad-input output.

It is the local interface between command handlers and the `io.c` stdin parser.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/io.h -->