# File Research: sources/cow-pools/bcachefs-tools/fs/bcachefs.h

Core bcachefs runtime header. It pulls together subsystem type headers and defines central filesystem/device structures, logging helpers, flags, reference categories, time stats, unit conversions, and small cross-subsystem helpers.

Major contents:
- Logging prefix macros and `bch_err`/`bch_warn`/`bch_info` style wrappers.
- Error-printing helpers that suppress transaction restart noise.
- Debug static-key parameter declarations.
- `BCH_TIME_STATS()` and `enum bch_time_stats`, including allocator, journal, btree, data IO, write-buffer, nocow, and discard wait metrics.
- Device read/write enumerated ref categories.
- `struct bucket_bitmap`.
- `struct bch_dev`, the live member-device object.
- Filesystem flags in `BCH_FS_FLAGS()` and `enum bch_fs_flags`.
- Write ref categories in `BCH_WRITE_REFS()`.
- `struct bch_fs`, the main filesystem object.
- Error throwing helper `bch_err_throw()`.
- Read-only ref get/put helpers.
- Unit conversion and time conversion helpers.
- Filesystem/device name helpers.
- Discard option resolution.
- Casefold availability check.
- Structured log message RAII/class helpers.

Important `struct bch_dev` fields:
- Device lifetime refs: `ref`, `ref_outer`, and `io_ref[READ/WRITE]`.
- Backpointer to `struct bch_fs`, device index, removal state, and cached member info.
- Superblock handle and write/read scratch state.
- Per-bucket state: GC buckets, bucket generations, oldest generations, nouse bitmap, backpointer mismatch/empty bitmaps.
- Per-device usage counters.
- Allocator fields: allocation cursors, wake counter, open/partial bucket counts, invalidate/discard fast work, discard queue.
- Journal device state, IO error work, latency/congestion counters, and IO done counters.

Important `struct bch_fs` fields:
- Global lifecycle refs and state locks.
- Device arrays/masks and mount options.
- Superblock CPU/disk state and superblock lock.
- Unicode/casefold state.
- Counters, time stats, and persistent error tracking.
- Journal, journal replay, journal keys, and journal sequence blacklist.
- Recovery, btree, GC, accounting, replicas, disk groups, capacity, allocator, and discards state.
- Snapshot, compression, reconcile, copygc, EC, nocow, moving, VFS, quota, and debug state.
- Dedicated workqueues, including `write_ref_wq` used by write-ref-holding tasks.

Important helpers:
- `bucket_bytes()`, `block_bytes()`, and `block_sectors()`.
- `bch2_time_to_timespec()`, `timespec_to_bch2_time()`, `bch2_current_time()`, and `bch2_current_io_time()`.
- `bch2_discard_opt_enabled()` resolves filesystem mount discard override versus per-device discard setting.
- `bch2_fs_casefold_enabled()` validates Unicode/casefold availability.
- `bch2_log_msg` helpers build structured log output.

Role:
- This is the primary inclusion point for most bcachefs subsystems and the owner of allocator/discard/replica/disk-group state used by the files in this group.
