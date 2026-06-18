# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/debugfs.c

## Purpose
Implements optional debugfs support for inspecting and controlling a live b43legacy device. It exposes TSF read/write, ucode register dumps, shared-memory dumps, TX status history, manual restart, and dynamic debug booleans.

## Important APIs, Types, and Functions
Public functions are `b43legacy_debugfs_init`, `b43legacy_debugfs_exit`, `b43legacy_debugfs_add_device`, `b43legacy_debugfs_remove_device`, `b43legacy_debugfs_log_txstat`, and `b43legacy_debug`. Internal file handlers include `tsf_read_file`, `tsf_write_file`, `ucode_regs_read_file`, `shm_read_file`, `txstat_read_file`, and `restart_write_file`. `struct b43legacy_debugfs_fops` binds read/write callbacks to fields inside `struct b43legacy_dfsentry`.

## Control Flow
Module init creates a root debugfs directory. Per-device attach allocates a dfs entry, allocates a circular TX status log, creates files under a wiphy-named directory, and registers dynamic debug booleans. Generic debugfs read allocates a 16 KiB buffer on first read, optionally takes `wl->irq_lock`, calls the selected read callback, serves data with `simple_read_from_buffer`, and frees the buffer when fully consumed. Writes copy at most one page from userspace, optionally take `irq_lock`, and call the selected writer.

## State and Persistence
Debugfs state is runtime-only. `dev->dfsentry` owns per-file buffers, dynamic debug booleans, and a 100-entry TX status circular log protected by its own spinlock. TSF writes and restart writes mutate hardware state. Debugfs files are not persistent across module unload or device detach.

## Dependencies and Integration Points
Uses Linux debugfs, file operations, mutexes, spinlocks, page allocation, and copy-to/from-user helpers. It calls main-device helpers for TSF, SHM, restart, DMA/PIO debug flags, and TX status structures from xmit.

## Risks
Debugfs read buffers are per-file-entry and must be freed after EOF; interrupted reads can retain temporary pages until the next full read or detach. `shm_read_file` dumps a fixed 0x1000 words bounded by the 16 KiB buffer. Manual restart can race with device teardown unless status and locks are respected. The TX status logger expects IRQs disabled when called.

## Test Signals
With `CONFIG_B43LEGACY_DEBUG`, verify debugfs directory creation/removal, successful reads of `tsf`, `ucode_regs`, `shm`, `txstat`, TSF writes, restart writes with `1`, dynamic debug toggles, and detach after partial reads. Lockdep and KASAN are useful for buffer lifetime and locking issues.
