# sources/distributed-fs/ceph-client/mm/page_reporting.h

## Purpose
`page_reporting.h` is the internal hot-path interface between the buddy allocator and the free page reporting implementation. It provides compile-time stubs when page reporting is disabled and a static-key-gated notification helper when enabled.

## Important APIs, Types, And Functions
- `DECLARE_STATIC_KEY_FALSE(page_reporting_enabled)` exposes the runtime branch key.
- `extern unsigned int page_reporting_order` shares the reporting threshold.
- `__page_reporting_notify()` is the slow-path worker request function.
- `page_reported(page)` checks both the static key and `PageReported`.
- `page_reporting_notify_free(order)` screens `__free_one_page()` notifications by enable state and minimum order.

## Control Flow
In enabled builds, free-page code calls `page_reporting_notify_free(order)`. The helper returns immediately if the static key is disabled or the free order is below `page_reporting_order`; otherwise it calls the out-of-line notifier that schedules delayed work. In disabled builds, `page_reported()` is a constant false macro and notification is an empty inline.

## State And Persistence Behavior
The header itself owns no storage. It reads the static key, report order, and page flag state managed by `page_reporting.c` and the allocator.

## Dependencies And Integration Points
It includes MM zone, pageblock, page-isolation, jump-label, slab, page-table, and scatterlist headers because it is consumed in allocator internals and shares types with `page_reporting.c`.

## Risks
- This helper is on the allocator free hot path, so static-key and order checks must stay minimal.
- Incorrect stubbing would either add overhead in disabled builds or hide reported-page state from allocator logic.
- `page_reporting_order` must be initialized before the static key is enabled.

## Test Signals
- Build with `CONFIG_PAGE_REPORTING=y` and `n`, verifying identical callers compile.
- Confirm low-order frees do not schedule work and high-order frees do after backend registration.
- Check branch-key state with page reporting enabled and after backend unregister.
