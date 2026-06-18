# sources/distributed-fs/ceph-client/mm/page_reporting.c

## Purpose
`page_reporting.c` implements free page reporting, a mechanism for a registered backend device to receive batches of free pages so it can treat them as unused, commonly for virtualized memory hinting. It scans buddy free lists, isolates unreported pages into scatterlists, calls the device callback, and marks pages reported when they return unchanged to the buddy allocator.

## Important APIs, Types, And Functions
- `page_reporting_order` is both a module parameter and exported symbol controlling the minimum order to report.
- `struct page_reporting_dev_info *pr_dev_info` is the single RCU-protected registered backend.
- `__page_reporting_notify()` schedules reporting after allocator notifications.
- `page_reporting_cycle()` scans one zone/order/migratetype free list and feeds full scatterlists to `prdev->report()`.
- `page_reporting_process_zone()` applies watermarks, iterates reportable free lists, and flushes leftovers.
- `page_reporting_process()` is the delayed work handler and state-machine driver.
- `page_reporting_register()` and `page_reporting_unregister()` are exported backend registration APIs.

## Control Flow
Registration chooses the report order from the module parameter, device preference, or `pageblock_order`, initializes work and state, requests an initial pass, publishes `pr_dev_info` with RCU, and enables the static key. Free-page notifications call `__page_reporting_notify()` only when enabled and the freed order is large enough. Requests coalesce through atomic states `IDLE`, `REQUESTED`, and `ACTIVE`, with delayed work capped to at most one pass every two seconds. Processing allocates a scatterlist, then for each zone verifies a low watermark plus reporting capacity. Each cycle locks the zone, skips already reported pages and isolate migratetypes, isolates free pages into the scatterlist, drops the lock to call `report()`, reacquires the lock, drains pages back to their migratetype lists, and sets `PageReported` only when the page remains a buddy page at the same order.

## State And Persistence Behavior
Runtime state includes the global report order, RCU backend pointer, backend delayed work and atomic state, buddy free lists, `PageReported` flags, scatterlist contents, and zone free-page ordering. There is no disk persistence. Unregister clears the RCU pointer, waits for readers, and cancels delayed work.

## Dependencies And Integration Points
The file depends on buddy allocator internals, page isolation primitives, pageblock migratetypes, scatterlists, delayed work, RCU, static keys, module parameters, and backend-defined `struct page_reporting_dev_info::report`. Its hot-path companion is `page_reporting_notify_free()` in `page_reporting.h`.

## Risks
- The backend callback runs outside the zone lock, so pages must be isolated correctly and always drained on success or error.
- Watermark checks must preserve allocation progress; too aggressive reporting can contend with allocators.
- `PageReported` is valid only when the page was not merged into a different order while being returned.
- Only one backend can register; competing drivers get `-EBUSY`.
- Failure to cancel work or synchronize RCU on unregister would leave stale backend calls.

## Test Signals
- Register/unregister a virtio-balloon or test backend repeatedly while freeing pages.
- Verify page reporting starts only for frees at or above `page_reporting_order`.
- Inject backend report errors and ensure pages are returned without `PageReported`.
- Stress buddy allocation/free during reporting and confirm no isolated-page leaks or watermark regressions.
