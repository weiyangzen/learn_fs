# Group Research: group_1300_nilfs_utils_sources_cow_pools_nilfs_utils_lib_sb_c_sources_cow_pool_beb53aca9f5e

Scope: `Docs/research_subset_a.md`. This grouped report covers the listed NILFS utilities files under `sources/cow-pools/nilfs-utils/`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/sb.c -->
# File Research: sources/cow-pools/nilfs-utils/lib/sb.c

## Scope

Implements NILFS superblock access helpers for user-space tools: reading primary/secondary superblocks, validating magic/size, computing CRC32, and selectively writing mutable superblock fields.

## APIs And Behavior

- `nilfs_sb_check_sum()` temporarily clears `s_sum`, computes the little-endian CRC using `s_crc_seed` over `s_bytes`, then restores the stored checksum.
- `nilfs_sb_is_valid()` validates `NILFS_SUPER_MAGIC`, caps `s_bytes` at 1024 bytes, and optionally checks the checksum.
- `__nilfs_sb_read()` allocates two 1024-byte buffers, determines block-device or regular-file size, reads the primary superblock at `NILFS_SB_OFFSET_BYTES`, reads the secondary superblock at `NILFS_SB2_OFFSET_BYTES(devsize)`, and rejects a secondary superblock whose offset is smaller than the filesystem geometry implies.
- `nilfs_sb_read()` returns the first available valid superblock buffer and frees the other.
- `nilfs_sb_write()` rereads both existing superblocks, copies only fields selected by `NILFS_SB_*` mask bits, recomputes checksums, and writes each present copy back to its known offset.

## State And Dependencies

The file depends on NILFS on-disk structures, endian helpers, Linux `BLKGETSIZE64`, `pread`/`pwrite`, regular-file sizing through `fstat`, and `crc32_le`.

## Risks And Invariants

The code validates magic and size before trusting `s_bytes`; full checksum validation is available but internal reads here pass `check_crc=0`. Writes are copy-on-existing-copy: missing superblock replicas are not recreated. Short `pwrite()` counts are treated as failure only when less than 1024 bytes, but negative and short writes share the same path.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/sb.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/segment.c -->
# File Research: sources/cow-pools/nilfs-utils/lib/segment.c

## Scope

Provides iterators and validation for NILFS segment buffers: partial segment summaries, per-file summary records, and per-block binfo records.

## APIs And Behavior

- `nilfs_psegment_init()`, `nilfs_psegment_is_end()`, and `nilfs_psegment_next()` walk partial segments inside a full segment buffer.
- `nilfs_psegment_is_valid()` checks segment summary magic, summary checksum, summary byte bounds, 8-byte header alignment, partial segment block count bounds, and summary-block sizing.
- `nilfs_file_init()`, `nilfs_file_is_end()`, and `nilfs_file_next()` walk `nilfs_finfo` records inside a partial segment summary, accounting for block-boundary padding.
- `nilfs_file_info_size()` calculates combined finfo and binfo footprint using different binfo formats for DAT versus non-DAT files.
- `nilfs_block_init()`, `nilfs_block_is_end()`, and `nilfs_block_next()` walk binfo entries for data and node blocks, again respecting padding at block boundaries.
- `nilfs_psegment_strerror()` and `nilfs_file_strerror()` expose stable messages for iterator error codes.

## State And Dependencies

The iterators operate over caller-owned `struct nilfs_segment` memory, store offsets and logical block numbers in `nilfs_psegment`, `nilfs_file`, and `nilfs_block`, and depend on NILFS on-disk summary formats plus CRC32.

## Risks And Invariants

All bounds checks depend on `sumbytes`, `ss_nblocks`, `fi_nblocks`, and `fi_ndatablk` being validated before consumers dereference deeper records. DAT files use real block offsets while other files use virtual block numbers; mixing those binfo formats would corrupt traversal. The code reports malformed data by setting iterator error fields and `errno=EINVAL`.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/segment.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/vector.c -->
# File Research: sources/cow-pools/nilfs-utils/lib/vector.c

## Scope

Implements a small generic resizable array used by NILFS utilities.

## APIs And Behavior

- `nilfs_vector_create()` allocates the vector object and an initial data array for a nonzero element size.
- `nilfs_vector_destroy()` releases the backing array and wrapper.
- `nilfs_vector_get_new_element()` appends one uninitialized element, enlarging capacity when needed.
- `nilfs_vector_delete_elements()` removes a contiguous range and compacts later elements with `memmove`.
- `nilfs_vector_clear()` resets the logical size and opportunistically shrinks capacity back to the initial size without clobbering `errno` on shrink failure.
- `nilfs_vector_insert_elements()` inserts a gap of uninitialized elements at an index, enlarging and shifting existing elements as required.

## State And Dependencies

The vector stores raw `void *` data with element size, capacity, and length fields declared in `vector.h`. It relies on `malloc`, `realloc`, `memmove`, `SIZE_MAX`, and local `likely`/`unlikely` helpers.

## Risks And Invariants

Capacity growth checks multiplication overflow before reallocating. Deletion with `nelems == 0` would underflow `index + nelems - 1`; callers are expected to pass a positive count. Returned element pointers are invalidated after later reallocations.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/lib/vector.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/man/Makefile.am -->
# File Research: sources/cow-pools/nilfs-utils/man/Makefile.am

## Scope

Defines the manual pages distributed by the NILFS utilities build.

## Build Behavior

`dist_man_MANS` lists section 8, section 5, and section 1 manpages for `nilfs`, `mkfs.nilfs2`, mount/umount helpers, checkpoint tools, segment tools, cleaner daemon/configuration, tuning, cleaning, and resizing tools.

## Dependencies And Risks

This is packaging metadata only. Correctness depends on every listed manpage existing in the man directory at distribution time; missing files would fail Automake distribution or install targets.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/man/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/Makefile.am -->
# File Research: sources/cow-pools/nilfs-utils/sbin/Makefile.am

## Scope

Builds top-level NILFS system binaries and descends into the mount helper directory.

## Build Behavior

- `SUBDIRS = mount` includes mount/umount helper builds.
- Core system binaries are `mkfs.nilfs2` and `nilfs_cleanerd`; additional sbin programs are `nilfs-clean`, `nilfs-resize`, and `nilfs-tune`.
- `mkfs.nilfs2` builds from `mkfs.c`, `bitops.c`, and headers, and links blkid, uuid, crc32, mount-check, and feature libraries.
- `nilfs_cleanerd` builds from `cleanerd.c` and `cldconfig.c`, links POSIX message queues when needed, uuid, and static NILFS GC support.
- Other tools link against `libnilfs` plus cleaner/parser/mount-check/feature/GC libraries as appropriate.
- `fix-conflicting-dirs` removes directories whose names conflict with binary outputs.
- Optional `CREATE_COMPAT_SBIN_LINK` hooks create/remove compatibility symlinks in `$(exec_prefix)/sbin`.

## Dependencies And Risks

The Makefile encodes library ownership and install compatibility behavior. The `rm -rf "$$p"` helper is intentionally scoped to program-name conflicts in the build directory but is destructive if an unexpected directory shares a target binary name.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/bitops.c -->
# File Research: sources/cow-pools/nilfs-utils/sbin/bitops.c

## Scope

Provides portable C bitmap bit operations for mkfs-style metadata allocation.

## APIs And Behavior

When `_EXT2_HAVE_ASM_BITOPS_` is not defined:

- `ext2fs_set_bit()` sets a bit in a byte-addressed bitmap and returns the previous bit value.
- `ext2fs_clear_bit()` clears a bit and returns the previous bit value.
- `ext2fs_test_bit()` returns the current bit value.

## State And Dependencies

The code is extracted from e2fsprogs and treats bit zero as the low bit of the first byte. `mkfs.h` aliases these functions as `nilfs_set_bit`, `nilfs_clear_bit`, and `nilfs_test_bit`.

## Risks And Invariants

No bounds are checked; callers must provide a bitmap large enough for `nr`. Return values are masks, not normalized booleans.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/bitops.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/bitops.h -->
# File Research: sources/cow-pools/nilfs-utils/sbin/bitops.h

## Scope

Declares ext2-compatible bitmap helper functions.

## API Surface

The header exposes `ext2fs_set_bit()`, `ext2fs_clear_bit()`, and `ext2fs_test_bit()` for use by NILFS mkfs metadata initialization.

## Dependencies And Risks

It has a simple include guard and no external includes. Callers must match the implementation's byte-addressed bitmap assumptions and perform their own bounds validation.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/bitops.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/cldconfig.c -->
# File Research: sources/cow-pools/nilfs-utils/sbin/cldconfig.c

## Scope

Parses `nilfs_cleanerd.conf`, initializes default cleaner daemon settings, converts user units to filesystem-relative segment/block counts, and logs invalid configuration lines.

## APIs And Behavior

- Token parsing skips whitespace, supports comments beginning with `#`, and limits lines to `LINE_MAX` and tokens to `NTOKENS_MAX`.
- Numeric parsers handle unsigned integers, fractional seconds, size suffixes, and percentages.
- Size units support SI and IEC suffixes from kB/KiB through EB/EiB, plus raw counts and percentages.
- Segment thresholds convert percentages against `nilfs_get_nsegments()` and byte sizes against `block_size * blocks_per_segment`.
- Reclaimable-block thresholds convert raw, percent, or byte values to blocks per segment and clamp overlarge values.
- Keyword handlers support protection period, min/max clean segments, check/clean/retry intervals, timestamp selection policy, normal and low-space GC rates, mmap/set_suinfo toggles, log priority, and reclaimable-block thresholds.
- `nilfs_cldconfig_set_default()` computes defaults using the active NILFS geometry.
- `nilfs_cldconfig_read()` verifies the path is a regular file, loads defaults, parses overrides, and returns success even when individual invalid keywords only produced warnings.

## State And Dependencies

The parser writes `struct nilfs_cldconfig`, calls NILFS geometry accessors, and reports through `syslog`. It is consumed by `cleanerd.c`.

## Risks And Invariants

Most keyword handler parse failures are warning-tolerant and leave the previous/default value in place. `use_mmap` and `use_set_suinfo` are enable-only flags in the configuration grammar. Byte-unit conversions use unsigned arithmetic and do not explicitly detect overflow for very large suffix values.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/cldconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/cldconfig.h -->
# File Research: sources/cow-pools/nilfs-utils/sbin/cldconfig.h

## Scope

Declares NILFS cleaner daemon configuration structures, units, defaults, policy IDs, and the public configuration reader.

## Key Structures

- `struct nilfs_param` holds a parsed number plus unit.
- `enum nilfs_size_unit` defines raw, percentage, SI, and IEC units.
- `struct nilfs_cldconfig` stores GC policy, protection/check/clean/retry intervals, min/max clean segment thresholds, normal and low-space cleaning rates, mmap/set_suinfo booleans, syslog priority, and minimum reclaimable block thresholds.

## API Surface

`nilfs_cldconfig_read()` initializes a `nilfs_cldconfig` from defaults plus a configuration file, using a `struct nilfs` handle for filesystem geometry.

## Risks And Invariants

Defaults are expressed partly as percentages, so final numeric values depend on the mounted filesystem's segment and block geometry. `NILFS_CLDCONFIG_NSEGMENTS_PER_CLEAN_MAX` caps cleaning batch size at 32.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/cldconfig.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/cleanerd.c -->
# File Research: sources/cow-pools/nilfs-utils/sbin/cleanerd.c

## Scope

Implements `nilfs_cleanerd`, the NILFS garbage-collection daemon responsible for selecting reclaimable segments, invoking NILFS GC/reclaim operations, handling control commands, and coordinating daemon lifecycle.

## APIs And Behavior

- Command-line parsing supports config file, help/version, obsolete nofork, and protection-period override.
- Startup canonicalizes device/mount paths, daemonizes with double fork, opens syslog, adjusts OOM killer score, opens NILFS raw read-write GC-lock handle, creates checkpoint reverse mapper, loads config, and creates a POSIX message queue named from device identity.
- Signal handling uses `siglongjmp` for SIGTERM/SIGINT shutdown, SIGHUP reload, and SIGUSR1 debug dump.
- Cleaner control messages support get-status, run, suspend, resume, reload, stop, shutdown, and NACK unimplemented tune/wait commands.
- Automatic mode pauses/resumes based on clean segment thresholds plus reserved-segment allowance.
- Manual mode tracks remaining passes and segments, accepts per-run protection period, speed, interval, and reclaimable-block overrides.
- Segment selection scans segment usage records, filters reclaimable segments outside the protection time or with future timestamps, ranks by timestamp-derived importance, and picks the least important segments.
- Cleaning builds `nilfs_reclaim_params` with protection sequence, protection checkpoint, and minimum reclaimable blocks, calls `nilfs_xreclaim_segment()`, handles cleaned/deferred counts, falls back on ENOMEM by reducing batch size, and retries after shrinking the protected region when needed.
- The main loop alternates state checks, selection, cleaning, interval recalculation, signal handling, and `ppoll()`/message-queue waits.

## State And Dependencies

`struct nilfs_cleanerd` combines NILFS library handle, checkpoint reverse map, config, runtime mode flags, timing state, cleaner speed, message queues, client UUID, manual-run state, and job ID. Dependencies include `libnilfsgc`, `nilfs_cleaner` message definitions, POSIX mqueue, syslog, uuid, `nilfs_get_sustat()`, `nilfs_get_suinfo()`, `nilfs_xreclaim_segment()`, freeze/thaw/sync helpers, and `cnormap`.

## Risks And Invariants

The daemon has several state encodings in `running`: negative for manual suspend, zero idle, one automatic running, two manual run. Correct cleaner restart/control depends on mount helpers preserving `gcpid`, `pp`, and `nogc` attributes. `nilfs_cleanerd_manual_resume()` sets `mm_prev_state = 0` before assigning `running`, so resume always returns to idle rather than the saved state. Message validation checks aggregate byte sizes but command-specific handlers still cast to extended request structures after validating their own argument length.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/cleanerd.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mkfs.c -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mkfs.c

## Scope

Implements `mkfs.nilfs2`, creating an initial NILFS2 filesystem image: superblocks, initial segment, root directory, ifile, cpfile, sufile, DAT, segment summary, super root, checksums, and device erase/write behavior.

## APIs And Behavior

- Option parsing supports block size, blocks per segment, badblocks scan, force overwrite, discard suppression, label, reserved-segment percentage, dry-run, quiet/verbose, feature set, passive creation time, and version.
- Device checks verify regular/block device, not currently mounted, optional blkid signature confirmation, and optional badblocks scan with dropped privileges.
- `init_disk_layout()` determines device size, block bits, creation time, random CRC seed, first segment block, segment count, and minimum segment requirement.
- Layout helpers count required blocks for block-grouped files, cpfile, sufile, and DAT, then place all initial files in the first segment.
- Disk buffering lazily allocates block-aligned blocks and preserves the disk header before writing superblock data.
- Erase logic optionally issues `BLKDISCARD`, skips zeroing if discard guarantees zeroes, otherwise wipes the beginning and end of the device while preserving a boot sector area when present.
- Metadata construction initializes root directory entries, reserved inodes, block-grouped allocation descriptors/bitmaps, ifile inodes, checkpoint state, segment usage state, DAT mappings, segment summary finfo/binfo records, super root, and on-disk inode bmaps.
- `fill_in_checksums()` computes segment summary, super root, and full segment data checksums.
- `commit_super_block()` fills last checkpoint/partial-segment/sequence/free-block fields and superblock CRC.
- `write_disk()` writes initial segment blocks, fsyncs, writes primary and secondary superblocks, and fsyncs again unless dry-run is set.

## State And Dependencies

Global option state controls formatting choices. `struct nilfs_disk_info`, `struct nilfs_segment_info`, `struct nilfs_file_info`, and global `struct nilfs_fs_info nilfs` track the planned filesystem image. Dependencies include NILFS on-disk structures, libuuid, optional libblkid, block-device ioctls, `check_mount`, CRC32, feature parsing, and local bitmap helpers.

## Risks And Invariants

Many validation failures terminate via `perr()`. The code assumes one initial segment in `seginfo[1]`. Block size must be a power of two, between 1024 and page size; blocks per segment must be a power of two and at least `NILFS_SEG_MIN_BLOCKS`. Superblock CRC is computed after `raw_sb` was zeroed and populated; checksum fields inside segment/super-root must be written after all metadata content is stable.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mkfs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mkfs.h -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mkfs.h

## Scope

Defines constants and small helpers used by `mkfs.nilfs2`.

## API Surface

- Defines disk header/erase sizes, default block size, default blocks per segment, default check interval, reserved segment percentage, minimum block size, minimum user segments, and initial inode bounds.
- Aliases ext2-style bit operations to NILFS bitmap helper names.
- Provides fallback `BLKGETSIZE64`.
- Defines directory file-type constants matching Linux mode file type bits.
- Provides `nilfs_rec_len_from_disk()` and `nilfs_rec_len_to_disk()` conversions for directory entry record lengths, including the NILFS max-record-length sentinel for 64 KiB.

## Dependencies And Risks

The header includes NILFS on-disk structures through `compat.h`. The record length conversion asserts lengths are not above 64 KiB; callers must validate directory record sizing before writing.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mkfs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/Makefile.am -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/Makefile.am

## Scope

Builds NILFS mount and umount helper binaries in either libmount or legacy util-linux compatibility mode.

## Build Behavior

- Always builds core sbin programs `mount.nilfs2` and `umount.nilfs2`.
- Common headers include `mount.nilfs2.h`; libmount builds add `mount_attrs.c`, `libmount_compat.h`, and `mount_attrs.h`.
- Legacy builds use `fstab.c`, `mount_mntent.c`, `mount_opts.c`, `sundries.c`, `xmalloc.c`, and related headers.
- Both helper variants link realpath and cleaner-exec libraries plus configured mount, SELinux, and POSIX timer libraries.
- Optional compatibility symlink install/uninstall hooks mirror helpers into `$(exec_prefix)/sbin`.

## Dependencies And Risks

The conditional `CONFIG_LIBMOUNT` switch selects distinct source trees with similar semantics. Packaging must keep both variants compiling because the same program names are emitted from different source files.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/fstab.c -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/fstab.c

## Scope

Legacy util-linux-derived fstab/mtab support for NILFS mount helpers: reading mount tables, finding entries, locking mtab, and updating mtab records.

## APIs And Behavior

- `mtab_does_not_exist()`, `mtab_is_writable()`, and internal symlink detection decide whether `/etc/mtab` can be updated.
- `mtab_head()` and `fstab_head()` lazily read `/etc/mtab` or `/proc/mounts`, and `/etc/fstab`, into circular doubly linked lists.
- Lookup helpers search by mountpoint/device, backward by directory/device, loop option, fstab spec/file, UUID, and label declarations.
- `lock_mtab()` creates a per-process link target, links it to the mtab lock path, then uses `fcntl` locking with a monotonic-clock timeout.
- Signal handlers are installed while locking so lock files are removed on fatal signals.
- `update_mtab()` rereads mtab under lock, removes an entry for umount, replaces options for remount, or appends a new entry, writes a temporary mtab, fixes mode/ownership, and renames it over the real mtab.

## State And Dependencies

The file uses global cached mount/fstab lists and lock state. It depends on custom `mount_mntent.c` parsing/writing, path constants, `xmalloc`, and `sundries` fatal/error helpers.

## Risks And Invariants

The lock-file protocol must always call `unlock_mtab()` through `atexit` or signal cleanup. The table cache is stale after update unless reread under lock as `update_mtab()` does. Symlinked mtab is deliberately treated as non-writable to avoid writing to `/proc/mounts`.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/fstab.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/fstab.h -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/fstab.h

## Scope

Declares legacy fstab/mtab data structures and helper functions.

## API Surface

- `struct mntentchn` links parsed `struct my_mntent` entries in circular lists.
- Exposes mtab writability/existence checks, lookup functions for mount and fstab entries, lock/unlock functions, and `update_mtab()`.

## Dependencies And Risks

The header depends on `mount_mntent.h`. Callers receive pointers into cached linked lists and must not free them directly except through implementation-managed paths.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/fstab.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/libmount_compat.h -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/libmount_compat.h

## Scope

Provides compatibility definitions for libmount exit-status macros.

## API Surface

Includes `<libmount.h>` and defines `MNT_EX_SUCCESS`, `MNT_EX_USAGE`, `MNT_EX_SYSERR`, `MNT_EX_SOFTWARE`, `MNT_EX_USER`, `MNT_EX_FILEIO`, `MNT_EX_FAIL`, and `MNT_EX_SOMEOK` when absent.

## Dependencies And Risks

This keeps source compatible with older libmount headers. Values mirror traditional mount helper exit bit meanings; mismatches with a platform libmount would affect process exit semantics.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/libmount_compat.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount.nilfs2.c -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount.nilfs2.c

## Scope

Legacy implementation of `mount.nilfs2`, using direct `mount(2)`, custom option parsing, and mtab updates while coordinating NILFS cleaner daemon lifecycle.

## APIs And Behavior

- Parses `-f`, `-v`, `-n`, `-t`, `-o`, `-r`, `-w`, and `-V`; converts options into mount flags and extra kernel options.
- Rejects unknown filesystem types and non-root helper execution.
- Checks `/etc/mtab` availability unless `-n`, verifies writable mounts do not target read-only devices, and installs SIGTERM/SIGINT handlers.
- `prepare_mount()` rejects mounting over an already mounted target, finds an existing read-write NILFS mount for the device, enforces single read-write mount semantics, and handles rw-to-ro/rw-to-rw remounts by stopping the recorded cleaner daemon.
- `do_mount_one()` removes user-facing `pp` and `nogc` from kernel option string, invokes `mount(2)`, and restarts cleanerd if a remount failed after stopping it.
- `update_mount_state()` starts cleanerd for read-write non-bind mounts unless `nogc` is set, records `gcpid` and `pp` in mtab options, and updates or appends the mtab entry.
- Optional SELinux warning reports when mounting an unlabeled filesystem on SELinux systems.

## State And Dependencies

Global mount flags (`verbose`, `readonly`, `readwrite`, `nomtab`, `fake`) are shared with legacy option helpers. Dependencies include `fstab.c`, `mount_opts.c`, `sundries.c`, `mount_mntent.c`, direct `mount(2)`, `BLKROGET`, and cleaner execution APIs.

## Risks And Invariants

Correct GC control depends on preserving/removing `gcpid`, `pp`, and `nogc` consistently in mtab. On remount, the code stops cleanerd before the syscall and attempts restart on failure. Multiple read-write mounts of the same NILFS device are explicitly forbidden, but read-only overlapping mounts are allowed.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount.nilfs2.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount.nilfs2.h -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount.nilfs2.h

## Scope

Defines shared constants for NILFS mount helpers.

## API Surface

- `NILFS2_FS_NAME` is `"nilfs2"`.
- `PPOPT_NAME` is `"pp"` for cleaner protection period mount attribute.
- `NOGCOPT_NAME` is `"nogc"` for suppressing cleaner daemon startup.

## Dependencies And Risks

The constants are shared between legacy and libmount helpers and must stay synchronized with cleaner-control option parsing.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount.nilfs2.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount_attrs.c -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount_attrs.c

## Scope

Implements NILFS-specific mount attribute parsing and updating for libmount-based helpers.

## APIs And Behavior

- `nilfs_mount_attrs_init()` clears all attributes and sets protection period to `ULONG_MAX` as "not specified".
- `nilfs_mount_attrs_parse()` scans an option string with `mnt_optstr_next_option()`, recognizes `pp=<seconds>`, `nogc`, `pid=<gcpid>` from mtab/utab context, and dummy `none`; it can return matched NILFS attributes separately from remaining non-NILFS options.
- Invalid option forms produce warnings and `-EINVAL`, such as `nogc=value`, `pp` without value, `pid` outside mtab parsing, or nonnumeric values.
- `nilfs_mount_attrs_update()` clears libmount FS attributes and appends `nogc`, or `pid=<gcpid>` plus optional `pp=<seconds>`, or dummy `none` to force attribute removal on remount.

## State And Dependencies

The file uses libmount option string APIs and cleaner `PIDOPT_NAME`, plus shared NILFS mount option names.

## Risks And Invariants

`pid` and `none` are only valid when parsing stored mount-table attributes, not command-line options. Attribute update intentionally uses a dummy `none` when removing old attributes on remount so libmount notices the deletion.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount_attrs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount_attrs.h -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount_attrs.h

## Scope

Declares NILFS libmount attribute data and functions.

## API Surface

- `NOATTR_NAME` defines the dummy `"none"` attribute.
- `struct nilfs_mount_attrs` stores cleaner PID, `nogc` flag, and protection period.
- Declares initialization, parsing, and libmount context update helpers.

## Dependencies And Risks

The header forward-declares `struct libmnt_context` and uses `pid_t`. Callers must initialize structures before parsing so unspecified protection period is represented by `ULONG_MAX`.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount_attrs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount_constants.h -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount_constants.h

## Scope

Provides fallback mount flag definitions for legacy mount helper code.

## API Surface

Defines Linux `MS_*` constants when missing, including read-only, nosuid, nodev, noexec, synchronous, remount, dirsync, noatime, nodiratime, bind, move, recursive, relatime, and magic mask/value flags.

## Dependencies And Risks

This compatibility header allows older libc/kernel headers. Values must match Linux mount ABI; incorrect fallback values would corrupt `mount(2)` flag behavior.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount_constants.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount_libmount.c -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount_libmount.c

## Scope

Libmount-based implementation of `mount.nilfs2`, replacing legacy table/option code with `struct libmnt_context` while preserving NILFS cleaner daemon coordination and single read-write mount policy.

## APIs And Behavior

- Initializes a libmount context, sets filesystem type to `nilfs2`, disables helper recursion, parses mount options, and splits NILFS attributes from kernel/libmount options.
- Supports fake, verbose, no-mtab, type, options, read-only/read-write, and version options.
- `nilfs_prepare_mount()` calls `mnt_context_prepare_mount()`, retrieves mount flags and mtab, checks writable-device accessibility, detects whether the target is already mounted, and finds any existing read-write NILFS mount for the same source.
- Enforces no overlapping read-write mounts. For rw-to-ro or rw-to-rw remounts, it parses old stored attributes, verifies the mountpoint, and shuts down the old cleaner daemon if recorded.
- `nilfs_do_mount_one()` calls `mnt_context_do_mount()` and reports syscall/library errors; if remount fails after stopping cleanerd, it tries to restart cleanerd and finalize mount attributes.
- `nilfs_mnt_context_complete_root()` copies mount root from an existing mtab entry for remount/fake cases to avoid incomplete utab attributes.
- `nilfs_update_mount_state()` launches cleanerd for read-write non-bind mounts unless `nogc`, updates stored attributes, and finalizes the mount.

## State And Dependencies

`struct nilfs_mount_info` carries libmount context, resolved mount flags, mount type, mounted state, and old/new NILFS attributes. Dependencies include libmount, `BLKROGET`, cleaner execution APIs, and `mount_attrs.c`.

## Risks And Invariants

The stored libmount attributes are the control channel for later umount/remount cleaner operations. `mnt_context_do_mount()` returns positive errno for syscall failures and negative library errors; callers normalize this for diagnostics. If cleanerd launch fails after a successful writable mount, the mount still succeeds but GC is not running.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount_libmount.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount_mntent.c -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount_mntent.c

## Scope

Private util-linux-derived mount-table parser/writer for legacy helpers.

## APIs And Behavior

- `mangle()` escapes spaces, tabs, newlines, and backslashes as octal sequences for mtab/fstab output.
- `unmangle()` decodes octal escapes while parsing fields.
- `my_setmntent()` opens a mount table with restrictive umask and initializes parser state.
- `my_endmntent()` closes the file and frees parser state.
- `my_addmntent()` appends a formatted, escaped mount entry.
- `my_getmntent()` reads nonblank noncomment lines, parses fsname, dir, type, opts, freq, and passno, tolerates missing final newline, and skips up to `ERR_MAX` malformed lines before stopping.

## State And Dependencies

Uses a static input buffer and static `struct my_mntent` for returned records; strings inside records are freshly allocated. Depends on `xmalloc`, `xstrdup`, and NLS messages.

## Risks And Invariants

The returned `struct my_mntent` is overwritten by the next call, but the allocated strings are transferred to callers such as `read_mntentchn()`. Long lines are treated as corruption. Classic mtab/fstab limitations around whitespace are handled only through this escape convention.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount_mntent.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount_mntent.h -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount_mntent.h

## Scope

Declares the legacy private mount-entry parser API.

## API Surface

- `struct my_mntent` mirrors core libc `mntent` fields using owned strings and integer dump/pass fields.
- `mntFILE` stores file pointer, filename, line number, and hard/soft parse error counters.
- Declares open, close, append, and read functions.

## Dependencies And Risks

No include guard around required `FILE` definition is provided here, so including source files must already include `<stdio.h>` or equivalent. Callers must free strings obtained through parsed entries after copying or storing them.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount_mntent.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount_opts.c -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount_opts.c

## Scope

Legacy util-linux-derived mount option parser and NILFS-specific option string manipulation helpers.

## APIs And Behavior

- `opt_map` maps common options like `ro`, `rw`, `noexec`, `nosuid`, `nodev`, `sync`, `remount`, `bind`, `user`, `owner`, `loop`, `noatime`, and `relatime` to mount flags, including inverted forms.
- `string_opt_map` captures options with values such as `loop=`, `vfs=`, `offset=`, `encryption=`, `speed=`, `comment=`, and `uhelper=`.
- `append_opt()` and `append_numopt()` build comma-delimited option strings.
- Optional SELinux support translates context options to raw context strings and appends quoted forms to extra options.
- `parse_opts()` splits `-o` strings while respecting quotes, sets mount flags, converts user/group names for `uid=`/`gid=`, and preserves unknown options as kernel extra options.
- `fix_opts_string()` reconstructs a canonical mtab option string from flags, string options, extra options, and optional user.
- NILFS-added helpers `find_opt()`, `replace_opt()`, and `replace_optval()` find, remove, or replace comma-delimited options while respecting quoted commas.

## State And Dependencies

The file uses global `verbose`, `mount_quiet`, `readonly`, and `readwrite` variables supplied by mount helpers. It depends on passwd/group lookup, optional libselinux, legacy mount constants, and fatal allocation helpers.

## Risks And Invariants

The parser mutates duplicated option strings and assumes comma separation except inside double quotes. Some helper functions use `sscanf()` format strings for option matching; callers must pass formats compatible with the pointed storage type. `replace_opt()` reallocates the original string and returns the new pointer, so callers must always use the returned value.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount_opts.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount_opts.h -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount_opts.h

## Scope

Declares legacy mount option flags and option string helper APIs.

## API Surface

- Defines user-space-only mount option bits such as `MS_NOAUTO`, `MS_USERS`, `MS_USER`, `MS_OWNER`, `MS_GROUP`, `MS_NETDEV`, `MS_COMMENT`, and `MS_LOOP`.
- Defines masks for options hidden from `mount(2)` or mtab, and secure defaults for user/owner mounts.
- Declares global option state expected from helper programs.
- Declares option append/parse/reconstruction helpers and NILFS-specific find/replace helpers.
- `replace_drop_opt()` macro replaces an option when a condition is true or removes it when false.

## Dependencies And Risks

The custom `MS_*` bits must not collide with real kernel flags used by the helper. Macro `replace_drop_opt()` evaluates arguments in a GNU statement expression and is not strictly ISO C.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/mount_opts.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/sundries.c -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/sundries.c

## Scope

Legacy support utilities shared by mount and umount helpers.

## APIs And Behavior

- `xstrndup()`, `xstrconcat3()`, and `xstrconcat4()` provide fatal-on-OOM string allocation/concatenation helpers.
- `block_signals()` blocks or unblocks all signals except SIGTRAP and SIGSEGV.
- `error()` prints nonfatal diagnostics unless quiet mode is active.
- `matching_type()` matches filesystem type filters with `no` negation and excludes swap.
- `matching_opts()` checks whether a full option string satisfies requested option/nooption filters.
- `canonicalize()` returns stable strings for pseudo sources like `none`, `proc`, and `devpts`, otherwise tries `myrealpath()` and falls back to the original path.

## State And Dependencies

Uses external `mount_quiet`, NLS, `xmalloc`, `xrealloc`, and local realpath helper. It is derived from util-linux mount support code.

## Risks And Invariants

`matching_opts()` uses stack allocation proportional to the test option string length. `canonicalize()` deliberately returns the input path unchanged when realpath fails, so callers must not treat it as proof of existence.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/sundries.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/sundries.h -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/sundries.h

## Scope

Declares legacy helper support functions and traditional mount exit status bits.

## API Surface

Exposes signal blocking, canonicalization, diagnostics, type/option matching, fatal allocation/string helpers, `die()`, optional NFS mount prototype, and exit bit constants such as `EX_USAGE`, `EX_SYSERR`, `EX_FILEIO`, `EX_FAIL`, and `EX_SOMEOK`.

## Dependencies And Risks

The header assumes users include string functions for the `streq` macro. Exit constants are shared behavior for legacy mount and umount helpers.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/sundries.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/umount.nilfs2.c -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/umount.nilfs2.c

## Scope

Legacy implementation of `umount.nilfs2`, using direct `umount(2)`, custom mtab parsing/updating, optional read-only remount fallback, loop cleanup, and cleaner daemon shutdown/restart logic.

## APIs And Behavior

- Parses `-n`, `-l`, `-f`, `-v`, `-r`, and `-V`; force is ignored, lazy is reported unsupported.
- Rejects non-root unmounts in the current implementation.
- Resolves each mountpoint through mtab, verifies the mounted type is NILFS2, and delegates to `umount_one()`.
- Before unmounting a read-write NILFS mount, reads `pid=<gcpid>` from mtab, pings cleanerd, and asks it to shut down.
- On `EBUSY` with `-r`, attempts remount read-only and updates mtab options to `ro`.
- On `EBUSY` without `-r`, if cleanerd was alive and stopped, attempts to restart it and update `pid=` in mtab.
- On successful unmount, optionally clears loop devices recorded in old-style loop type or `loop=` option and removes the mtab entry.
- `complain()` maps common unmount errno values to user-facing diagnostics.

## State And Dependencies

Uses legacy fstab/mtab, mount option, mntent, sundries, and cleaner-exec helpers. `options` stores force/lazy/remount/suid flags.

## Risks And Invariants

Cleaner shutdown occurs before the unmount syscall for writable mounts, so failure paths must restart it when the filesystem remains mounted. Loop option parsing duplicates the option string but advances the pointer with `strtok`, leaking the original allocation in that branch. mtab updates are skipped for root and when `-n` is active.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/umount.nilfs2.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/umount_libmount.c -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/umount_libmount.c

## Scope

Libmount-based implementation of `umount.nilfs2`, coordinating libmount unmount/finalization with NILFS cleaner daemon attributes.

## APIs And Behavior

- Initializes a libmount context, parses `-f`, `-l`, `-n`, `-v`, `-r`, and `-V`, sets fstype to `nilfs2`, and disables helper recursion.
- Force is accepted but warned as ignored; lazy and read-only remount behavior are delegated to libmount context flags.
- Rejects non-root unmounts in the current implementation.
- `nilfs_prepare_umount()` calls `mnt_context_prepare_umount()`, then parses stored NILFS attributes from the selected mount entry.
- `nilfs_do_umount_one()` pings and shuts down cleanerd if a stored `gcpid` exists, runs `mnt_context_do_umount()`, and if read-only remount fallback leaves the filesystem mounted, restarts cleanerd and updates attributes.
- `nilfs_umount_one()` finalizes successful fake or real unmounts and reports normalized errno diagnostics.
- Main loops over all mountpoint arguments and returns success, failure, or some-ok exit status.

## State And Dependencies

`struct nilfs_umount_info` stores libmount context and old NILFS attributes. Dependencies include libmount, cleaner-exec APIs, and `mount_attrs.c`.

## Risks And Invariants

Stored attributes are required to find the cleaner PID; incomplete utab/mtab attributes can make cleanerd uncontrollable. As with the legacy implementation, the daemon is stopped before unmount and must be restarted if the unmount degrades to a still-mounted read-only state.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/umount_libmount.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/xmalloc.c -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/xmalloc.c

## Scope

Fatal allocation helpers for legacy mount code.

## APIs And Behavior

- Global `at_die` hook can run cleanup before fatal exit.
- `die()` prints a formatted message, runs `at_die` if set, and exits with the supplied code.
- `xmalloc()` allocates nonzero sizes and dies on failure.
- `xrealloc()` reallocates and dies on failure.
- `xstrdup()` duplicates non-NULL strings and dies on failure; NULL input returns NULL.

## State And Dependencies

Uses NLS for the out-of-memory message and `EX_SYSERR` from `sundries.h`.

## Risks And Invariants

These helpers terminate the process rather than returning errors. `xmalloc(0)` returns NULL by design, so callers must not assume non-NULL for zero-byte allocations.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/xmalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/xmalloc.h -->
# File Research: sources/cow-pools/nilfs-utils/sbin/mount/xmalloc.h

## Scope

Declares fatal allocation and exit helpers for legacy mount code.

## API Surface

Exposes `xmalloc()`, `xrealloc()`, `xstrdup()`, `die()`, and the cleanup hook `at_die`.

## Dependencies And Risks

The header includes `sys/types.h` and `stdarg.h` but has no include guard. Multiple inclusion is harmless for these extern declarations, but the style differs from the other headers in this directory.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/mount/xmalloc.h -->