# File Research: sources/block-storage/lvm2/lib/device/dev-io.c

## Purpose
Implements low-level device open/close and ioctl helpers for size, readahead, discard, direct block sizes, flushing, and open flag management.

## Main APIs
- `dev_get_size()` returns cached sector size for regular files or block devices.
- `dev_size_seqno_inc()` invalidates cached size values globally.
- `dev_get_read_ahead()` reads BLKRAGET for block devices.
- `dev_discard_blocks()` issues BLKDISCARD unless in test mode.
- `dev_get_direct_block_sizes()` reads physical/logical block sizes.
- `dev_flush()` uses BLKFLSBUF, then `fsync`, then `sync`.
- `dev_open_flags()` opens devices with direct IO, noatime, read/write, exclusive, and quiet-mode handling.
- `dev_open*()` wrappers select common open modes.
- `dev_close()` and `dev_close_immediate()` manage reference-counted closing.

## Core Behavior
Block-device size is read with `BLKGETSIZE64` through an existing bcache fd if available or through a temporary read-only open. Regular-file size is read with `stat`. Results are cached in the device with a sequence number.

`dev_open_flags()` reuses an already-open fd if it satisfies requested access/exclusive requirements; otherwise it may close and reopen to upgrade. It tests/falls back from `O_NOATIME` and `O_DIRECT`, validates that the opened fd still refers to the expected `dev_t`, and records open mode flags.

## Integration
Used by all device probing, metadata IO, label scanning, wiping, discard, and signature detection paths.

## Risk Notes
- Opening while in a critical section is logged but not rejected.
- Reopening to upgrade access can interact badly with references; comments note unresolved concerns around allocated device lifetime.
- Without `O_DIRECT_SUPPORT`, block devices are flushed after open.
- `dev_flush()` falls back to global `sync()` if device-specific flushing fails.
