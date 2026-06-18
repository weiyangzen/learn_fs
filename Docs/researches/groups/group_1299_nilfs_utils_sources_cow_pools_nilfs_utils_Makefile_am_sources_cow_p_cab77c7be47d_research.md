# Group Research: group_1299_nilfs_utils_sources_cow_pools_nilfs_utils_Makefile_am_sources_cow_p_cab77c7be47d

Scope: `Docs/research_subset_a.md` / `sources/cow-pools/nilfs-utils`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/Makefile.am -->
# File Research: sources/cow-pools/nilfs-utils/Makefile.am

Top-level Automake entry for `nilfs-utils`.

- Sets `ACLOCAL_AMFLAGS = -I m4`.
- Builds subdirectories in order: `lib`, `bin`, `sbin`, `include`, `man`, `etc`, `scripts`.
- Distributes bootstrap and ignore files: `autogen.sh`, `.gitignore`, and `m4/.gitignore`.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/autogen.sh -->
# File Research: sources/cow-pools/nilfs-utils/autogen.sh

Autotools bootstrap script.

- Runs `aclocal`, `autoheader`, `libtoolize -c --force`, `automake -a -c`, and `autoconf`.
- Uses `die()` to print the failed step and exit.
- Ends with guidance to run `./configure` and `make`.

Risk/notes: no option handling; assumes required autotools are installed and in `PATH`.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/autogen.sh -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/bin/Makefile.am -->
# File Research: sources/cow-pools/nilfs-utils/bin/Makefile.am

Automake definition for user-facing NILFS commands.

- Builds `chcp`, `dumpseg`, `lscp`, `lssu`, `mkcp`, and `rmcp`.
- Applies `-Wall`, includes `include`, and links most tools against `libnilfs.la`.
- Adds helper libraries where needed: parser for checkpoint parsing, segment parsing for `dumpseg`, GC/parser for `lssu`, and POSIX semaphore support for cleaner-locking tools.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/bin/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/bin/chcp.c -->
# File Research: sources/cow-pools/nilfs-utils/bin/chcp.c

Implements `chcp`, changing NILFS checkpoint mode between normal checkpoint and snapshot.

- Accepts `cp` or `ss`, optional device/node, and one or more checkpoint numbers.
- Parses checkpoint numbers with `nilfs_parse_cno()` and rejects malformed, negative, overflowing, or out-of-range values.
- Opens NILFS read-write with cleaner-lock and optional device lookup.
- Blocks `SIGINT`/`SIGTERM`, locks the cleaner semaphore, calls `nilfs_change_cpmode()` for each checkpoint, then unlocks and restores signals.
- Reports missing checkpoints separately from other ioctl failures.

Risk/notes: device-vs-checkpoint argument detection depends on parsing the next argument as a valid checkpoint number.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/bin/chcp.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/bin/dumpseg.c -->
# File Research: sources/cow-pools/nilfs-utils/bin/dumpseg.c

Implements `dumpseg`, a raw NILFS segment inspection command.

- Accepts optional device/node and one or more segment numbers.
- Opens raw NILFS access, attempts mmap-backed segment reads, and reads each segment with `nilfs_get_segment()`.
- Walks segment summaries, partial segments, file records, and block records through `segment.h` iterators.
- Prints segment sequence, next segment, partial-segment creation time, file metadata, and virtual or real block descriptors.
- Includes detailed diagnostics for malformed partial segment headers, oversized summaries, bad file block counts, and summary overruns.

Risk/notes: intended for inspection/debugging; output correctness depends on segment summary parsing in the segment library.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/bin/dumpseg.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/bin/lscp.c -->
# File Research: sources/cow-pools/nilfs-utils/bin/lscp.c

Implements `lscp`, the checkpoint/snapshot listing command.

- Supports all checkpoints, block count vs increment count, reverse order, snapshots only, start index, line limit, help, and version.
- Uses `nilfs_get_cpstat()` and batched `nilfs_get_cpinfo()` calls with a 512-entry buffer.
- Forward listing walks checkpoints or the snapshot chain from a start index.
- Reverse checkpoint listing uses INIT/NORMAL/ACCEL/DECEL state to avoid scanning every checkpoint in sparse histories.
- Output includes checkpoint number, date/time, mode (`cp` or `ss`), minor flag, block/increment count, and inode count.

Risk/notes: `-i` and `-n` are parsed with `atoll()` and do not reject malformed numeric suffixes.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/bin/lscp.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/bin/lssu.c -->
# File Research: sources/cow-pools/nilfs-utils/bin/lssu.c

Implements `lssu`, the segment-usage listing command.

- Supports all segments, start index, line limit, latest live-usage assessment, protection period, help, and version.
- Normal mode prints segment number, last-modified time, active/dirty/error status, and written block count.
- Latest-usage mode opens raw plus cleaner-lock access and uses `nilfs_assess_segment()` as a dry-run GC assessment.
- Computes a protection checkpoint via `nilfs_cnormap_track_back()` when a protection period is supplied.
- Marks protected segments with `p` and treats protected segments as fully live.

Risk/notes: latest mode can be relatively expensive because it parses and assesses each dirty segment.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/bin/lssu.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/bin/mkcp.c -->
# File Research: sources/cow-pools/nilfs-utils/bin/mkcp.c

Implements `mkcp`, the checkpoint creation command.

- Options create a snapshot (`-s`) and/or print the created checkpoint number (`-p`).
- Opens NILFS read-write with cleaner-lock support and calls `nilfs_sync()` to force a new checkpoint.
- If snapshot mode is requested, blocks `SIGINT`/`SIGTERM`, locks the cleaner, changes the new checkpoint to `NILFS_SNAPSHOT`, unlocks, and restores signals.
- Prints the checkpoint number only after all requested operations succeed.

Risk/notes: snapshot conversion is separate from checkpoint creation, so failures after `nilfs_sync()` can leave a normal checkpoint.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/bin/mkcp.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/bin/rmcp.c -->
# File Research: sources/cow-pools/nilfs-utils/bin/rmcp.c

Implements `rmcp`, the checkpoint removal command.

- Supports force, interactive confirmation, help, and version options.
- Accepts optional device/node followed by checkpoint numbers or ranges parsed by `nilfs_parse_cno_range()`.
- Opens NILFS read-write, reads checkpoint stats, clamps ranges to oldest/current checkpoint bounds, and deletes checkpoints with `nilfs_delete_checkpoint()`.
- Tracks snapshots separately; snapshots produce `EBUSY` unless force mode suppresses the warning.
- Non-force mode prints guidance to convert snapshots with `chcp` before removal.

Risk/notes: range removal iterates checkpoint by checkpoint, which may be costly for very large ranges.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/bin/rmcp.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/configure.ac -->
# File Research: sources/cow-pools/nilfs-utils/configure.ac

Autoconf configuration for NILFS utils version `2.4.0-dev`.

- Initializes autotools, libtool, `config.h`, `m4`, compiler checks, and optional git revision embedding via `NILFS_UTILS_USE_GITID`.
- Defines helper macros for pkg-config/library detection and `HAVE_LIB*` config defines.
- Detects UUID, POSIX message queue, semaphore, timer, headers, functions, and large-file support.
- Optional features cover libmount, SELinux, blkid, pkg-config output, UAPI header installation, and usrmerge install layout.
- Determines `/sbin`/`/usr/sbin` install policy, architecture-specific `libdir`, `/etc` and `/var` defaults, Makefile outputs, and optional `nilfs.pc`/`nilfsgc.pc`.

Risk/notes: some install-directory probing is Linux-distribution-specific.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/configure.ac -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/etc/Makefile.am -->
# File Research: sources/cow-pools/nilfs-utils/etc/Makefile.am

Automake rule for configuration data.

- Installs `nilfs_cleanerd.conf` as system configuration data via `dist_sysconf_DATA`.
- No custom generation or validation logic is present.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/etc/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/etc/nilfs_cleanerd.conf -->
# File Research: sources/cow-pools/nilfs-utils/etc/nilfs_cleanerd.conf

Default configuration for the NILFS cleaner daemon.

- Sets protection period, minimum/maximum clean segment thresholds, check interval, timestamp selection policy, segments per clean, cleaning intervals, retry interval, minimum reclaimable block thresholds, mmap usage, `set_suinfo` usage, and log priority.
- Supports percentage and binary/decimal suffix syntax for segment/block thresholds.
- Comments document HUP reload behavior and refer to `nilfs_cleanerd.conf(5)`.

Risk/notes: comments state only timestamp selection policy is supported for NILFS 2.0.0.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/etc/nilfs_cleanerd.conf -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/Makefile.am -->
# File Research: sources/cow-pools/nilfs-utils/include/Makefile.am

Automake header installation list.

- Public installed headers are `nilfs.h` and `nilfs_gc.h`.
- Internal headers include parser, segment, cleaner, compatibility, path, CRC, and helper APIs.
- Kernel UAPI mirror headers `linux/nilfs2_api.h` and `linux/nilfs2_ondisk.h` are installed only when `CONFIG_UAPI_HEADER_INSTALL` is enabled; otherwise they remain noinst headers.

Risk/notes: public headers include Linux NILFS ioctl definitions, so install policy affects downstream builds.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/check_mount.h -->
# File Research: sources/cow-pools/nilfs-utils/include/check_mount.h

Small internal header declaring `check_mount(const char *device)`.

- Used by mount/status tooling to determine whether a device or backing file is mounted.
- No types or inline helpers beyond the include guard.

Risk/notes: behavior is implemented in `lib/check_mount.c`.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/check_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/cleaner_exec.h -->
# File Research: sources/cow-pools/nilfs-utils/include/cleaner_exec.h

Header for older cleaner daemon process-control routines.

- Defines daemon name `nilfs_cleanerd` and mount-option PID key `gcpid`.
- Declares launch, ping, and shutdown helpers.
- Exposes logger/printf/flush function pointers used by cleaner control code.

Risk/notes: process launch path depends on configured `CORE_SBINDIR`.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/cleaner_exec.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/cleaner_msg.h -->
# File Research: sources/cow-pools/nilfs-utils/include/cleaner_msg.h

Defines POSIX message-queue protocol structures for controlling `nilfs_cleanerd`.

- Lists cleaner commands: status, run, suspend, resume, tune, reload, wait, stop, and shutdown.
- Defines request header with command, argument size, and client UUID.
- Provides request payload variants for cleaner args, pathnames, and job IDs.
- Defines ACK/NACK response with cleaner status, errno value, and job ID.
- Sets high/normal message priorities and maximum path/request sizes.

Risk/notes: request structs are IPC ABI between library and daemon; layout changes require coordinated updates.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/cleaner_msg.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/cnormap.h -->
# File Research: sources/cow-pools/nilfs-utils/include/cnormap.h

Header for checkpoint-number reverse mapping by time period.

- Declares opaque `struct nilfs_cnormap`.
- Exposes create/destroy and `nilfs_cnormap_track_back()`, which maps a protection period to the oldest checkpoint number that should remain protected.

Risk/notes: consumed by `lssu` and cleaner logic that converts time-based protection to checkpoint boundaries.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/cnormap.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/compat.h -->
# File Research: sources/cow-pools/nilfs-utils/include/compat.h

Compatibility header for portability across libc/kernel header versions.

- Pulls selected configured headers and defines GCC, Sparse, byte-order, NILFS magic, `offsetof`, freeze/thaw ioctl, clock constants, timespec helpers, `PATH_MAX`, major/minor, and `getprogname()` fallbacks.
- Provides little/big-endian conversion macros using `byteswap`.
- Maps kernel-style byte-order helper names for Sparse checks under `__CHECKER__`.

Risk/notes: normal builds require either `getprogname()` or `program_invocation_short_name`; otherwise compilation errors intentionally.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/compat.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/crc32.h -->
# File Research: sources/cow-pools/nilfs-utils/include/crc32.h

Header for little-endian CRC32 calculation.

- Declares `crc32_le(uint32_t seed, const unsigned char *data, size_t length)`.
- Used by NILFS superblock/segment integrity handling elsewhere in the library.

Risk/notes: implementation is table-driven in `lib/crc32.c`.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/crc32.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/linux/nilfs2_api.h -->
# File Research: sources/cow-pools/nilfs-utils/include/linux/nilfs2_api.h

User-space NILFS2 ioctl API mirror.

- Defines checkpoint, segment-usage, segment-usage-update, checkpoint-mode, vector argument, checkpoint period, checkpoint stat, segment stat, virtual block info, virtual block descriptor, and disk block descriptor structs.
- Provides flag enums and inline helpers for checkpoint, segment-usage, and segment-usage-update bits.
- Defines checkpoint/snapshot mode constants.
- Defines NILFS ioctl numbers for checkpoint mode changes, checkpoint deletion/listing/stat, segment usage/stat, virtual info, block descriptors, cleaning, sync, resize, allocation range, and segment usage updates.

Risk/notes: this is a kernel/userspace ABI mirror; struct layout and ioctl numbers are externally significant.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/linux/nilfs2_api.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/linux/nilfs2_ondisk.h -->
# File Research: sources/cow-pools/nilfs-utils/include/linux/nilfs2_ondisk.h

NILFS2 on-disk format definition mirror.

- Defines inode layout, super-root layout, superblock layout, revision/features, special inode numbers, segment/block limits, directory entries, segment summaries, B-tree node headers, persistent allocator descriptors, DAT entries, checkpoint records, cpfile header, segment usage records, and sufile header.
- Provides offset/size macros and endian-aware inline flag setters/testers for checkpoints and segment usage.
- Encodes supported feature masks, filesystem states, mount flags, and magic constants.

Risk/notes: this file describes durable disk format; field offsets, endian conversions, and minimum structure sizes are compatibility-sensitive.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/linux/nilfs2_ondisk.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/lookup_device.h -->
# File Research: sources/cow-pools/nilfs-utils/include/lookup_device.h

Internal header for resolving a filesystem node to its backing block device.

- Declares `nilfs_lookup_device(const char *node, char **devpath)`.
- Return convention is implemented as: `1` found allocated backing device path, `0` input is already a block device, `-1` error.

Risk/notes: caller owns `*devpath` only on positive return.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/lookup_device.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/nilfs.h -->
# File Research: sources/cow-pools/nilfs-utils/include/nilfs.h

Primary public `libnilfs` API header.

- Defines checkpoint number type/ranges, filesystem type, superblock update masks, layout struct, open flags, option/lock inline helpers, and segment object.
- Declares NILFS object lifecycle, device/root accessors, layout access, superblock read/write, raw segment access, checkpoint APIs, segment usage APIs, GC ioctl wrapper, sync, resize, allocation range, freeze, and thaw.
- Provides cleaner-lock convenience functions via generated inline wrappers.

Risk/notes: callers must open with compatible flags; many functions require either raw device FD, ioctl FD, or cleaner semaphore to be available.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/nilfs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/nilfs_cleaner.h -->
# File Research: sources/cow-pools/nilfs-utils/include/nilfs_cleaner.h

Public cleaner controller API.

- Declares cleaner launch/open/close, ping, PID/device accessors, status, run, suspend/resume, tune, reload, wait, stop, and shutdown.
- Defines open flags for gcpid and queue access.
- Defines `nilfs_cleaner_args`, argument units, valid-field flags, and cleaner status values.
- Exposes logger/printf/flush function pointers shared with cleaner execution.

Risk/notes: several argument fields are reserved by comments; consumers should set valid bits carefully.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/nilfs_cleaner.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/nilfs_feature.h -->
# File Research: sources/cow-pools/nilfs-utils/include/nilfs_feature.h

Header for NILFS feature flag parsing/editing.

- Defines feature compatibility type enum for compat, read-only-compat, incompat, and negation marker.
- Declares conversions between feature masks and strings.
- Declares `nilfs_edit_feature()` for applying comma/space-separated feature edits with allowed-set validation.

Risk/notes: feature arrays are indexed by `NILFS_MAX_FEATURE_TYPES`.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/nilfs_feature.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/nilfs_gc.h -->
# File Research: sources/cow-pools/nilfs-utils/include/nilfs_gc.h

Public NILFS garbage collection library header.

- Defines reclaim parameter flags for protected sequence, protected checkpoint, and minimum reclaimable blocks.
- Defines `nilfs_reclaim_params` and `nilfs_reclaim_stat`.
- Declares normal and enhanced segment reclaim APIs plus segment-protection test.
- Provides `nilfs_assess_segment()` dry-run wrapper.
- Provides helpers for reclaimable and empty segment-usage states.

Risk/notes: `protseq` is mandatory for enhanced reclaim; `nilfs_suinfo_empty()` is only meaningful together with reclaimability checks.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/nilfs_gc.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/nls.h -->
# File Research: sources/cow-pools/nilfs-utils/include/nls.h

Small gettext compatibility header borrowed from util-linux.

- Defines `LOCALEDIR` fallback.
- If NLS is enabled, maps `_()` to `gettext()` and `N_()` to `gettext_noop()` or identity.
- If NLS is disabled, stubs `bindtextdomain`, `textdomain`, `_`, and `N_`.

Risk/notes: header guard is absent; intended as a lightweight macro include.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/nls.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/parser.h -->
# File Research: sources/cow-pools/nilfs-utils/include/parser.h

Header for common NILFS command-line parsers.

- Declares checkpoint number parser, checkpoint range parser, and protection-period parser.
- Used by checkpoint commands and segment-usage tooling.

Risk/notes: parser behavior and numeric bounds are implemented in `lib/parser.c`.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/parser.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/pathnames.h -->
# File Research: sources/cow-pools/nilfs-utils/include/pathnames.h

Path constants header based on old BSD/util-linux conventions.

- Overrides default user/root `PATH` values to include `/usr/local`.
- Defines common system paths for login, shutdown, passwd/group files, mount tables, `/proc` files, `/dev`, loop devices, and udev by-label/by-uuid/by-id/by-path directories.
- Provides fallbacks for `_PATH_MOUNTED`, `_PATH_MNTTAB`, `_PATH_DEV`, and related lock/temp paths.

Risk/notes: contains many constants not specific to NILFS; only a subset is used by this package.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/pathnames.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/realpath.h -->
# File Research: sources/cow-pools/nilfs-utils/include/realpath.h

Header for bundled realpath implementation.

- Declares `myrealpath(const char *path, char *resolved_path, int m)`.
- Based on util-linux 2.12r mount code.

Risk/notes: caller supplies destination buffer and maximum length.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/realpath.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/segment.h -->
# File Research: sources/cow-pools/nilfs-utils/include/segment.h

Segment-summary iterator API.

- Defines `nilfs_psegment`, `nilfs_file`, and `nilfs_block` iterator state structs.
- Defines detailed iterator error codes for bad alignment, oversized partial segments/summaries, too many blocks, inconsistent block counts, and overruns.
- Declares init/end/next/string-error functions for partial segments, files, and blocks.
- Provides `for_each` macros and helpers to classify data vs node blocks and virtual vs real block numbering.

Risk/notes: consumers must check iterator error state after traversal.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/segment.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/util.h -->
# File Research: sources/cow-pools/nilfs-utils/include/util.h

General utility macro header.

- Defines `likely`, `unlikely`, `BUG`, `BUG_ON`, `BUILD_BUG_ON`, git revision embedding macro, type checking, alignment/rounding/array helpers, min/max macros, 64-bit counter comparisons, and `timeval_to_timespec`.
- Git ID macro emits a `.comment` section string when configured.

Risk/notes: uses GNU C extensions such as statement expressions and `typeof`.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/util.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/include/vector.h -->
# File Research: sources/cow-pools/nilfs-utils/include/vector.h

Resizable array API.

- Defines `struct nilfs_vector` with data pointer, element size, current element count, and capacity.
- Declares create/destroy, append, delete, insert, clear, and inline accessors.
- Provides inline single-element delete/insert and qsort-backed sort.

Risk/notes: inline element access performs pointer arithmetic on `void *`, a GNU C extension.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/include/vector.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/Makefile.am -->
# File Research: sources/cow-pools/nilfs-utils/lib/Makefile.am

Automake rules for shared/internal NILFS libraries.

- Builds public `libnilfs.la` and `libnilfsgc.la`.
- Builds internal convenience libraries for realpath, feature parsing, parser, mount check, CRC32, cleaner execution, segment parsing, cleaner control, and static variants.
- Sets libtool version info for `libnilfs` and `libnilfsgc`.
- Links `libnilfs` with realpath, CRC32, and POSIX semaphores; links `libnilfsgc` with `libnilfs`, segment parsing, and POSIX timers; links cleaner control with POSIX MQ, UUID, timers, and cleaner execution.
- Optionally installs pkg-config files.

Risk/notes: static convenience library dependency ordering is explicitly managed.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/check_mount.c -->
# File Research: sources/cow-pools/nilfs-utils/lib/check_mount.c

Mount-status helper derived from e2fsprogs.

- Reads `_PATH_MOUNTED`, compares mount entries to the requested block device or regular-file/directory backing object.
- For block devices, compares `st_rdev` and also checks loop-device backing files through `/sys/dev/block/<maj>:<min>/loop/backing_file`.
- For non-block files, compares `(st_dev, st_ino)`.
- Returns mounted/not-mounted/error status.

Risk/notes: loop backing detection depends on sysfs and truncates backing-file reads to a page/path-sized buffer.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/check_mount.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/cleaner_ctl.c -->
# File Research: sources/cow-pools/nilfs-utils/lib/cleaner_ctl.c

Cleaner daemon control library built on mount-table discovery and POSIX message queues.

- Resolves NILFS mount/device, extracts `gcpid` mount option, validates device identity, and optionally launches/open queues.
- Creates a per-client UUID receive queue and opens a device-derived daemon send queue.
- Implements status, run, suspend, resume, tune, reload, wait, stop, and shutdown commands using `cleaner_msg.h` request/response structures.
- Handles queue draining before commands and maps daemon NACK responses back to `errno`.

Risk/notes: `nilfs_cleaner_wait_r()` uses `memset(&pfd, 0, sizeof(0))`, which only clears an `int`-sized prefix of `struct pollfd`; this looks like a real bug and should be `sizeof(pfd)`.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/cleaner_ctl.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/cleaner_exec.c -->
# File Research: sources/cow-pools/nilfs-utils/lib/cleaner_exec.c

Older cleaner daemon process-control implementation.

- Launches `nilfs_cleanerd` from `CORE_SBINDIR`, optionally passing protection period, device, and mount directory.
- Uses a pipe to receive the final daemon PID printed as `NILFS_CLEANERD_PID=<pid>`.
- Child drops setuid/setgid privileges before exec and unblocks most signals.
- Provides process-alive ping and shutdown via `SIGTERM`.
- Waits for shutdown with exponential backoff followed by periodic progress output.

Risk/notes: launch returns success once the daemon has “already started” even if PID retrieval fails.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/cleaner_exec.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/cnormap.c -->
# File Research: sources/cow-pools/nilfs-utils/lib/cnormap.c

Checkpoint-number reverse mapper used to translate a time protection period into a checkpoint boundary.

- Maintains a vector of checkpoint spans, each tracking start/end checkpoint/time and approximate checkpoint count.
- Enumerates checkpoints forward/backward with sparse-history acceleration similar to `lscp`.
- Uses realtime and monotonic/boottime clocks, with coarse-clock feature probing and fallback.
- Initializes, extends, trims, and searches checkpoint history incrementally across repeated calls.
- Handles clock rewind by assigning a small artificial interval between spans.

Risk/notes: correctness depends on checkpoint creation timestamps being mostly monotonic; code explicitly handles rewinds but only approximately.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/cnormap.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/crc32.c -->
# File Research: sources/cow-pools/nilfs-utils/lib/crc32.c

Table-driven little-endian CRC32 implementation.

- Uses polynomial `0xedb88320`.
- `crc32_le()` updates an input seed over a byte buffer and returns the resulting CRC.
- Based on JAMlib CRC code.

Risk/notes: no bounds checks beyond the caller-supplied length.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/crc32.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/feature.c -->
# File Research: sources/cow-pools/nilfs-utils/lib/feature.c

NILFS feature flag string conversion/editing routines.

- Known feature table currently maps read-only-compatible `block_count`.
- Converts unknown feature bits to `FEATURE_Cn`, `FEATURE_Rn`, or `FEATURE_In`.
- Parses named features or `FEATURE_<type><bit>` strings.
- Applies feature edit strings, supports `none` and `^feature` negation, and validates set/clear operations against allowed masks.

Risk/notes: uses a static buffer in `nilfs_feature2string()` for unknown feature names, so returned strings are overwritten by subsequent calls.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/feature.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/gc.c -->
# File Research: sources/cow-pools/nilfs-utils/lib/gc.c

Core NILFS garbage collection library.

- Accumulates virtual and physical/DAT block descriptors by parsing selected segment summaries.
- Drops segments that are no longer reclaimable, empty scrapped segments, or protected by sequence number.
- Queries kernel `GET_VINFO`/`GET_BDESCS` to determine block liveness.
- Filters virtual blocks against live DAT periods, snapshots, and protected checkpoints.
- Merges deletable checkpoint periods, filters obsolete DAT blocks, and computes live/defunct statistics.
- In dry-run mode powers `nilfs_assess_segment()`.
- In reclaim mode locks cleaner, blocks termination signals, optionally defers low-yield segments by updating suinfo timestamps, then calls `nilfs_clean_segments()`.

Risk/notes: high-impact metadata path; relies on strict synchronization with cleaner semaphore and kernel ioctl semantics.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/gc.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/lookup_device.c -->
# File Research: sources/cow-pools/nilfs-utils/lib/lookup_device.c

Helper for resolving a filesystem node to its backing block device.

- If the input path is already a block device, returns `0`.
- Otherwise stats the node, reads `/sys/dev/block/<maj>:<min>` symlink, derives the kernel device name, and returns an allocated `/dev/<name>` path.
- Returns `1` when `*devpath` is populated and `-1` on failure.

Risk/notes: assumes sysfs device-name symlink maps directly to a usable `/dev/<name>` path.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/lookup_device.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/nilfs.c -->
# File Research: sources/cow-pools/nilfs-utils/lib/nilfs.c

Primary `libnilfs` implementation.

- Finds mounted NILFS filesystems in `/proc/mounts`, canonicalizing device and mount paths.
- Opens raw device and/or mounted root ioctl endpoint depending on flags, verifies mountpoint accessibility, reads superblock for raw access, and rejects unsupported incompatible features.
- Opens a POSIX semaphore named from device identity for cleaner locking.
- Implements option/lock helpers, layout accessors, checkpoint ioctls, segment usage ioctls, virtual/block descriptor ioctls, clean-segment ioctl, sync, resize, allocation range, freeze/thaw, raw segment read/mmap, segment release, segment sequence-number read, and oldest-checkpoint tracking.
- Raw segment reads handle segment zero’s first-data-block offset and optionally mmap page-aligned regions.

Risk/notes: several APIs require the correct open mode; `nilfs_get_segment()` does not verify that `pread()` returned the full segment size.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/nilfs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/nilfs.pc.in -->
# File Research: sources/cow-pools/nilfs-utils/lib/nilfs.pc.in

Pkg-config template for `libnilfs`.

- Substitutes prefix, exec prefix, libdir, includedir, and package version.
- Exposes `Libs: -L${libdir} -lnilfs`.
- Adds semaphore dependency through `Libs.private`.

Risk/notes: generated only when pkg-config output is enabled by configure.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/nilfs.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/nilfsgc.pc.in -->
# File Research: sources/cow-pools/nilfs-utils/lib/nilfsgc.pc.in

Pkg-config template for `libnilfsgc`.

- Substitutes prefix, exec prefix, libdir, includedir, and package version.
- Declares public `Requires: nilfs` because `nilfs_gc.h` includes `nilfs.h`.
- Exposes `Libs: -L${libdir} -lnilfsgc`.
- Adds timer dependency through `Libs.private`.

Risk/notes: generated only when pkg-config output is enabled by configure.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/nilfsgc.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/parser.c -->
# File Research: sources/cow-pools/nilfs-utils/lib/parser.c

Common parser implementation for NILFS command arguments.

- `nilfs_parse_cno()` wraps `strtoull()` but rejects negative inputs by returning `NILFS_CNO_MAX`.
- `nilfs_parse_cno_range()` supports `CNO`, `CNO..`, `..CNO`, and `CNO..CNO`.
- `nilfs_parse_protection_period()` parses unsigned seconds with optional suffixes: `s`, `m`, `h`, `d`, `w`, `M`, and `Y`.

Risk/notes: suffix multiplication is done before the final `ULONG_MAX` check and could overflow `unsigned long long` for extreme values.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/parser.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/realpath.c -->
# File Research: sources/cow-pools/nilfs-utils/lib/realpath.c

Bundled canonical path resolver based on util-linux mount code.

- Handles relative paths by prepending current working directory.
- Normalizes repeated slashes, `.`, and `..`.
- Resolves symlinks up to `MAX_READLINKS` by splicing link targets back into the remaining path.
- Returns the caller-provided output buffer on success.

Risk/notes: on allocation failure inside symlink expansion, it returns `NULL` without freeing a previously allocated `buf` in that branch.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/realpath.c -->