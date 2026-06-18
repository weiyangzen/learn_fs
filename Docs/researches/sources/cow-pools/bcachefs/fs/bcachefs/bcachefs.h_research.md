# File Research: sources/cow-pools/bcachefs/fs/bcachefs/bcachefs.h

Central bcachefs runtime header. It includes on-disk format definitions, subsystem type headers, logging/error macros, debug parameter declarations, time stats IDs, device and filesystem core structs, unit/time helpers, and log message RAII helpers.

Key contents:
- Logging format macros for filesystem, device, offset, and inode contexts.
- Error logging helpers that suppress transaction-restart noise.
- Debug parameter declarations for always-on and debug-only runtime knobs.
- `BCH_TIME_STATS()` enum definitions, including allocator/discard/journal/blocking time stats.
- Device read/write ref enumerations.
- `struct bch_dev`, the live member-device state.
- Filesystem flags and write-ref enumerations.
- `struct bch_fs`, the live filesystem root object.
- Error throwing helper `bch_err_throw()`.
- Read-only ref helpers.
- Unit conversion helpers for bucket and block sizes.
- bcachefs time conversion helpers.
- Discard option resolution between mount option and device option.
- Casefold availability helper.
- Log-message scoped class helpers.

Allocator/discard-related fields:
- `struct bch_dev` contains allocator cursors, `alloc_wake_counter`, open/partial bucket counters, invalidate work, fast discard work/queue/lock, and device usage state.
- `struct bch_fs` contains `replicas`, RCU `disk_groups`, `capacity`, `allocator`, and `discards`.
- `BCH_WRITE_REFS()` includes discard, fast discard, discard freespace checking, invalidate, and GC generation refs.
- `BCH_DEV_WRITE_REFS()` includes journal discard, bucket discard, fast discard, invalidation, EC, and IO write refs.

Important helper:
- `bch2_discard_opt_enabled()` resolves discard behavior: a mount-level discard option overrides per-device persisted discard setting only for the current mount.

Role:
- This header is the integration point where the allocator/discard/replicas/disk group subsystems become part of the live bcachefs filesystem object.
