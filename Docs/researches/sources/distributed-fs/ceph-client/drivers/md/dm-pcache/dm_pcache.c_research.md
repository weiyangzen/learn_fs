# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/dm_pcache.c

## Purpose
Defines the `pcache` device-mapper target. It parses the target table, opens cache and backing devices, starts the cache-device/backing-device/cache subsystems, maps bios into `pcache_request` objects, handles temporary `-EBUSY` deferral, exposes status and messages, and registers/unregisters the target module.

## Important APIs, Types, And Functions
The public target callbacks are `dm_pcache_ctr()`, `dm_pcache_dtr()`, `dm_pcache_map_bio()`, `dm_pcache_status()`, and `dm_pcache_message()` in `dm_pcache_target`. Module setup calls `pcache_backing_init()`, `pcache_cache_init()`, and `dm_register_target()`.

Request lifetime is managed by `pcache_req_get()` and `pcache_req_put()` around the per-bio `struct pcache_request`. Deferred work is handled by `defer_req()`, `pcache_defer_reqs_kick()`, `defered_req_fn()`, and `defer_req_stop()`. Argument parsing is split into `parse_cache_dev()`, `parse_backing_dev()`, and `parse_cache_opts()`.

## Control Flow
Construction rejects table loading for a live mapped device, allocates `struct dm_pcache`, creates a per-target workqueue, parses `<cache_dev> <backing_dev> [options]`, and starts `cache_dev`, `backing_dev`, then `pcache_cache` in dependency order. The target advertises one flush bio, flush support, and `per_io_data_size = sizeof(struct pcache_request)`.

Mapping initializes the per-bio request with byte offset and length, increments `inflight_reqs`, and calls `pcache_cache_handle_req()`. A normal return completes through `pcache_req_put()`. `-EBUSY` places the request on `defered_req_list`; deferred work retries until the cache can accept it or teardown forces `-EIO`. Destruction marks the target stopping, drains deferred requests, waits for all in-flight requests, stops subsystems in reverse order, releases devices, drains/destroys the workqueue, and frees the context.

## State And Persistence
This file owns target-level volatile state: target pointer, cache/backing/cache subobjects, options, deferred-request list, target workqueue, `state`, `inflight_reqs`, and waitqueue. Persistent cache metadata is managed by the cache-device and cache layers, not directly here. The `state` atomic gates deferred processing and writeback so teardown does not accept new background work.

Status reports cache-device flags, segment counts, used segment count, GC percent, cache flags, and key/dirty-tail positions for `STATUSTYPE_INFO`; `STATUSTYPE_TABLE` emits reconstructable table arguments with cache mode and CRC option. The `gc_percent` message updates runtime GC threshold through `pcache_cache_set_gc_percent()`.

## Dependencies And Integration Points
The target integrates with device-mapper core APIs, `dm_get_device()`/`dm_put_device()`, per-bio target data, target status/message hooks, and block flush support. It depends on pcache submodules `cache_dev`, `backing_dev`, and `cache`; the cache layer is the actual I/O policy engine. The singleton target feature means only one live table instance is supported.

## Risks
The constructor forbids live table reloads, so operational workflows depending on table replacement are unsupported. Request refcounting and `inflight_reqs` must stay balanced across direct completion, deferred retry, and teardown; otherwise teardown can hang or complete a bio twice. The deferred-list spelling is consistent but easy to misread. Only `cache_mode writeback` is accepted despite table/status vocabulary that hints at more modes.

## Test Signals
Exercise valid/invalid table arguments, cache/backing device open failures, subsystem start failure unwinds, normal reads/writes/flushes, cache-full `-EBUSY` deferral and later wakeup, target removal under load, and `gc_percent` messages. `dmsetup status` should show coherent segment/key-tail fields and `dmsetup table` should round-trip the configured devices and CRC option.
