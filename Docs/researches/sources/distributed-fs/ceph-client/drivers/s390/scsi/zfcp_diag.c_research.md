# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_diag.c`

## Purpose

`zfcp_diag.c` implements adapter diagnostic-buffer storage and refresh logic. It caches exchange-port-data and exchange-config-data QTCB bottoms behind small headers, rate-limits refreshes by age, serializes concurrent refresh attempts, and exposes synchronous update functions used by sysfs/diagnostic consumers. The actual data acquisition is delegated to FSF exchange commands; this file owns cache lifecycle and concurrency.

## Important APIs And Functions

- `zfcp_diag_adapter_setup()` allocates `struct zfcp_diag_adapter`, initializes the port/config diagnostic headers, points headers at embedded data buffers, sets buffer sizes, initializes spinlocks, and seeds timestamps so the first freshness check fails.
- `zfcp_diag_adapter_free()` frees the adapter diagnostics block and nulls the adapter pointer.
- `zfcp_diag_update_xdata()` publishes newly captured data into a diagnostic buffer under `access_lock`, records timestamp and incomplete flag, and refuses to move timestamps backward.
- `zfcp_diag_update_port_data_buffer()` synchronously runs `zfcp_fsf_exchange_port_data_sync()` and treats `-EAGAIN` as success with incomplete data already recorded in the header.
- `zfcp_diag_update_config_data_buffer()` is the config-data counterpart using `zfcp_fsf_exchange_config_data_sync()`.
- `__zfcp_diag_update_buffer()` is the serialization helper. If another caller is updating, it performs an interruptible wait under the lock; otherwise it marks `updating`, drops the lock for the sleeping update function, reacquires, clears `updating`, and wakes waiters.
- `__zfcp_diag_test_buffer_age_isfresh()` checks for future timestamps and max-age expiration.
- `zfcp_diag_update_buffer_limited()` loops until the buffer is fresh enough or the current caller performed an update. It returns `0`, `-EINTR`, or the underlying update error.

## Control Flow

A diagnostic reader calls `zfcp_diag_update_buffer_limited(adapter, hdr, update_fn)`. The function locks the header, checks whether cached data is fresh relative to `adapter->diagnostics->max_age`, and either returns quickly or enters update serialization. Only one caller executes the supplied update function. Other callers sleep on the global `__zfcp_diag_publish_wait` wait queue and retry freshness when the active updater finishes. FSF completion handlers publish new QTCB-bottom data via `zfcp_diag_update_xdata()`, including the incomplete flag for link-down/incomplete exchange data.

`zfcp_diag_update_xdata()` captures `jiffies` before locking so the timestamp reflects acquisition time. It only writes when the captured timestamp is not older than the existing one, preventing older concurrent results from replacing newer data.

## State And Persistence

State is per adapter in `adapter->diagnostics`:

- `max_age` defaults to 5000 ms.
- Each diagnostic buffer has `access_lock`, `updating`, `incomplete`, `timestamp`, `buffer`, and `buffer_size`.
- Port and config data are embedded in the diagnostics allocation, so there is one stable cache address for each.

The global wait queue is shared across all diagnostic headers and adapters. It does not store data; it coordinates waiters.

## Dependencies And Integration

The file depends on Linux spinlocks, jiffies, errno, slab allocation, and zfcp FSF exchange APIs. It integrates with:

- `zfcp_fsf_exchange_config_data_handler()` and `zfcp_fsf_exchange_port_data_handler()`, which publish data into these buffers.
- SCSI host update code, because exchange handlers may update SCSI host state while also updating diagnostics.
- Sysfs or other diagnostic consumers that need fresh but rate-limited hardware data.

## Risks And Edge Cases

- `zfcp_diag_adapter_setup()` overwrites `adapter->diagnostics` only after allocation succeeds, but callers must avoid double setup leaks or concurrent readers during replacement.
- `__zfcp_diag_publish_wait` is global; wakeups are broad. Correctness relies on rechecking each header's `updating` and freshness state under its own lock.
- Waiters receive `-EAGAIN` when another thread completed an update; `zfcp_diag_update_buffer_limited()` intentionally loops to recheck freshness. Incorrect callers of the internal helper would misinterpret it.
- Update functions sleep, so the lock must be dropped. Any new update function must publish through the expected FSF handler path or directly call `zfcp_diag_update_xdata()`.
- Freshness uses jiffies; wraparound is handled through time macros, but future timestamps are treated as stale.

## Test Signals

Validation should cover:

- First update is forced after setup because timestamps are seeded old.
- Concurrent callers result in one FSF exchange and waiters either return fresh data or `-EINTR` if interrupted.
- Incomplete FSF exchange data maps to `hdr->incomplete` with a `0` public diagnostic update return.
- Older concurrent publish attempts do not overwrite newer timestamps/data.
- Freeing diagnostics nulls `adapter->diagnostics` and tolerates partial setup.
