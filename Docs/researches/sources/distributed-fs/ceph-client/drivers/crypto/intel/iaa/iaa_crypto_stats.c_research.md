# sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto_stats.c

## Purpose
This file implements optional debugfs statistics for the Intel IAA crypto compression driver. It tracks global compression/decompression counters, completion error counters, per-IAA-device counters, and per-workqueue counters, then exposes them through debugfs files under `iaa_crypto`.

## Important APIs, Types, And Functions
- Global update APIs: `update_total_comp_calls()`, `update_total_comp_bytes_out()`, `update_total_decomp_calls()`, `update_total_sw_decomp_calls()`, `update_total_decomp_bytes_in()`, and the three `update_completion_*_errs()` helpers increment `atomic64_t` global counters.
- Workqueue update APIs: `update_wq_comp_calls()`, `update_wq_comp_bytes()`, `update_wq_decomp_calls()`, and `update_wq_decomp_bytes()` use `idxd_wq_get_private()` to find the driver-private `struct iaa_wq`, then update both the workqueue and owning `struct iaa_device`.
- Debugfs show functions: `global_stats_show()` prints global atomics; `wq_stats_show()` takes `iaa_devices_lock`, iterates `iaa_devices`, and calls `device_stats_show()`/`wq_show()`.
- Reset path: `iaa_crypto_stats_reset()` clears global counters and, while holding `iaa_devices_lock`, clears each device and workqueue counter.
- Lifecycle: `iaa_crypto_debugfs_init()` creates `global_stats`, `wq_stats`, and `stats_reset`; `iaa_crypto_debugfs_cleanup()` removes the whole debugfs subtree.

## Control Flow
Fast-path compression/decompression code calls the update helpers directly. Debugfs reads enter `single_open()`, use `seq_file` output helpers, and return a point-in-time atomic snapshot. Writing `stats_reset` through the `DEFINE_DEBUGFS_ATTRIBUTE` write callback clears all visible counters.

## State And Persistence
State is in static `atomic64_t` counters plus counters embedded in runtime `iaa_device` and `iaa_wq` objects. It is kernel-memory-only diagnostic state and is lost on module unload/reload. Per-device traversal is protected by `iaa_devices_lock`; individual counters use atomics and can change while a debugfs read is in progress.

## Dependencies And Integration Points
The file depends on the IAA crypto driver's internal `iaa_crypto.h` structures, IDXD workqueue private data, the global `iaa_devices` list and lock, Linux debugfs, and `seq_file`. It integrates with the header `iaa_crypto_stats.h`, which compiles these functions out when stats support is disabled.

## Risks
- `iaa_crypto_debugfs_init()` does not check each debugfs creation return value; missing files are not reported.
- Reset races are intentionally weak: fast-path updates can occur during or immediately after reset, so reset is not a strict quiescent boundary.
- Workqueue update helpers assume `idxd_wq_get_private()` returns a valid `struct iaa_wq` with a valid owning `iaa_device`.

## Test Signals
- With `CONFIG_CRYPTO_DEV_IAA_CRYPTO_STATS`, exercise IAA compression/decompression and verify counter increments in `/sys/kernel/debug/iaa_crypto/global_stats` and `wq_stats`.
- Trigger software fallback decompression and error paths, then verify the matching counters.
- Write to `stats_reset` and confirm global, device, and workqueue counters return to zero without warnings while I/O is active.
