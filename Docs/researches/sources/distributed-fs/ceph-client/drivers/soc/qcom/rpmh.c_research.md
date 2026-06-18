# sources/distributed-fs/ceph-client/drivers/soc/qcom/rpmh.c

## Purpose

`rpmh.c` is the client-facing Qualcomm RPMh request layer. It provides synchronous, asynchronous, and batched write APIs for active/sleep/wake resource votes, caches sleep/wake values, and flushes cached low-power votes to the RSC driver during PM transitions.

## Important APIs, Types, and Functions

Exported APIs are `rpmh_write_async()`, `rpmh_write()`, `rpmh_write_batch()`, and `rpmh_invalidate()`. Internal state uses `struct cache_req` for per-resource sleep/wake cached values and `struct batch_cache_req` for cached batched requests. Core helpers include `get_rpmh_ctrlr()`, `rpmh_tx_done()`, `cache_rpm_request()`, `__rpmh_write()`, `__fill_rpmh_msg()`, `flush_batch()`, `send_single()`, and `rpmh_flush()`.

## Control Flow

All write APIs build one or more `rpmh_request` objects. Normal writes cache each command; active-only writes are sent immediately to `rpmh_rsc_send_data()`, while sleep/wake writes complete locally and mark the cache dirty. Synchronous active writes wait up to 10 seconds for `rpmh_tx_done()`. Batched active writes send each message and wait for all completions; batched sleep/wake writes cache the full batch for later flush. `rpmh_flush()` is called with interrupts disabled from RSC PM paths, invalidates stale TCSes if dirty, writes cached batches, emits changed sleep/wake pairs, clears dirty, and updates next wakeup.

## State and Persistence Behavior

The RPMh cache persists per controller. A resource is flush-valid only once both sleep and wake values are known and differ. `dirty` tracks whether TCS hardware needs refresh. Batch cache entries persist until `rpmh_invalidate()` frees them. Hardware persistence occurs through `rpmh-rsc.c` programming TCSes.

## Dependencies and Integration Points

It depends on device-parent drvdata pointing to `struct rsc_drv`, RPMh public TCS structures, completions, spinlocks, waitqueues, and `rpmh-rsc.c` internals. Client device drivers call the exported APIs; RSC PM paths call `rpmh_flush()`.

## Risks and Edge Cases

`rpmh_write_async()` allocates with `GFP_ATOMIC` and relies on `rpmh_tx_done()` to free active requests; non-active requests are immediately completed and freed. `rpmh_write_batch()` allocates one combined object and warns that timed-out completions may later signal freed stack/heap completion storage. `__fill_rpmh_msg()` rejects more than `MAX_RPMH_PAYLOAD` but `rpmh_write_batch()` ignores its return while filling each batch. Cache growth is unbounded by resource count except memory. `rpmh_flush()` uses `spin_trylock()` and can return busy during low-power entry.

## Test Signals

Tests should cover async active completion/free, sync timeout, sleep/wake caching and dirty transitions, same value sleep/wake skipping, batch active success and timeout, batch sleep/wake cache flush, invalid payload counts, allocation failures, `rpmh_invalidate()`, and PM flush with lock contention.
