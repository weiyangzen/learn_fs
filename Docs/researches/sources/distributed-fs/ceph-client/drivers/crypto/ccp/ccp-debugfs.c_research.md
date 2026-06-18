# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-debugfs.c

## Purpose

`ccp-debugfs.c` exposes CCP v5 device information and per-device/per-queue statistics through debugfs when `CONFIG_CRYPTO_DEV_CCP_DEBUGFS` is enabled. It provides readouts for version, available engines, queue counts, LSB entries, interrupts, and operation counters, and allows stats reset by writing to debugfs files.

## Important APIs, Types, And Functions

- Register-info masks such as `RI_AES_PRESENT`, `RI_NUM_VQM`, and `RI_LSB_ENTRIES` decode `CMD5_PSP_CCP_VERSION`.
- `ccp5_debugfs_info_read()` formats device name, RNG name, queue/command counts, version, engine presence, hardware queue count, and LSB entries.
- `ccp5_debugfs_stats_read()` aggregates operation counters across queues.
- `ccp5_debugfs_reset_queue_stats()` clears one queue's counters.
- `ccp5_debugfs_stats_write()` clears all queue counters and total interrupts.
- `ccp5_debugfs_queue_read()` formats per-queue counters and enabled interrupt names.
- `ccp5_debugfs_queue_write()` resets one queue.
- `ccp5_debugfs_setup()` creates the root/module/device/queue debugfs hierarchy.
- `ccp5_debugfs_destroy()` removes the entire CCP debugfs tree.

## Control Flow

During v5 device init, `ccp5_debugfs_setup()` checks `debugfs_initialized()`, lazily creates the module root under a mutex, creates a per-device directory, adds `info` and `stats`, then creates `q<id>/stats` for every command queue. Reads allocate a small temporary buffer, format a snapshot with `scnprintf()`, return it through `simple_read_from_buffer()`, and free the buffer. Writes ignore user content and reset counters. Driver teardown calls `ccp5_debugfs_destroy()` when the last device is being removed.

## State And Persistence Behavior

Debugfs state consists of dentries and live counter values in `struct ccp_device`/`struct ccp_cmd_queue`. Counter resets mutate in-memory statistics only. There is no persistence across driver unload or reboot.

## Dependencies And Integration Points

This file depends on Linux debugfs, `simple_open`, `simple_read_from_buffer`, CCP v5 register offsets, and queue/device statistics maintained by v5 operation code. It is only compiled when debugfs support is enabled and called from `ccp-dev-v5.c`.

## Risks And Edge Cases

- Stats output labels include duplicate `SHA` lines, one of which prints `total_3des_ops`; this is likely a label bug and can mislead diagnostics.
- Reads snapshot counters without locking, so values can be slightly inconsistent during active operation.
- The destroy helper removes the whole root, so multi-device teardown ordering must ensure it is only called when appropriate.
- Debugfs exposes hardware feature and usage data; keeping it optional limits information exposure.

## Test Signals

Signals include debugfs tree creation under module root, correct info/version/engine fields on v5 hardware, stats counters increasing after AES/SHA/RSA/DMA workloads, reset-on-write behavior, per-queue files for all queues, and clean removal on module unload.
