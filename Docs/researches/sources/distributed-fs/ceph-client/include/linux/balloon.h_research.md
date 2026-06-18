# sources/distributed-fs/ceph-client/include/linux/balloon.h

## Purpose
Defines the common memory balloon interface, including page migration support for pages inflated by balloon drivers.

## Important APIs, types, and functions
- `struct balloon_dev_info` tracks isolated pages, the balloon page list, optional `migratepage()` callback, and managed-page accounting preference.
- Page APIs include `balloon_page_alloc()`, enqueue/dequeue helpers, and list enqueue/dequeue helpers.
- `balloon_devinfo_init()` initializes counters, list head, migration callback, and accounting flag.

## Control flow and state
Balloon drivers allocate pages, associate them with a balloon device via `page->private`, and enqueue them on the balloon list. Migration uses movable-ops page migration: isolation/dequeue and inflation/deflation must synchronize through the balloon page lock rules documented in the header.

## State and persistence behavior
State is volatile guest memory-management state. `page->private` indicates whether a page belongs to the balloon or is isolated for migration; clearing it means isolation is no longer possible. `isolated_pages` tracks pages removed from the list for migration.

## Dependencies and integration points
Depends on pagemap, page flags, migration, GFP allocation, error helpers, and list APIs. Integrated by virtio-balloon, Xen, Hyper-V, and compaction/migration code.

## Risks
Lockless compaction scanners can race with inflation/deflation. The documented rules around `page->private` and the balloon list are correctness-critical. Incorrect managed-page accounting can skew VM memory totals.

## Test signals
Exercise inflate/deflate under memory pressure, page migration/compaction of balloon pages, concurrent isolation and dequeue, and accounting changes when `adjust_managed_page_count` is enabled.
