# sources/distributed-fs/ceph-client/mm/balloon.c

## Purpose
`balloon.c` provides common helper code for memory balloon drivers, including page allocation, enqueue/dequeue accounting, and optional migration support for inflated balloon pages.

## Important APIs, types, and functions
Exported helpers are `balloon_page_list_enqueue`, `balloon_page_list_dequeue`, `balloon_page_alloc`, `balloon_page_enqueue`, and `balloon_page_dequeue`. Internal migration helpers include `balloon_page_device`, `balloon_page_isolate`, `balloon_page_putback`, `balloon_page_migrate`, and the `balloon_mops` `movable_operations`. Shared state is protected by `balloon_pages_lock`.

## Control flow
Drivers allocate pages via `balloon_page_alloc`, enqueue them after inflation, and dequeue them before returning memory to the guest. Enqueue marks pages offline, optionally stores the owning balloon device in `page_private`, adjusts managed page counts, and updates VM events and node page state. Dequeue removes pages from the balloon list, restores accounting, clears private migration state, and returns pages to the caller. With migration enabled, compaction can isolate a balloon page, ask the driver to migrate it, install the replacement page into the balloon list, or handle deflation.

## State and persistence
State lives in each `balloon_dev_info`: page list, isolated-page count, optional accounting callback, and driver migration callback. Individual pages persist offline state until freed to buddy; migration mode uses `page_private` to locate the owning balloon device.

## Dependencies and integration points
It depends on page allocator, page flags, VM event accounting, node page state, movable page operations, migration/compaction, and `linux/balloon.h`. It integrates with virtio or hypervisor balloon drivers that own actual inflate/deflate protocol behavior.

## Risks and test signals
Risks include losing pages when dequeue races isolation, incorrect managed-page accounting across zones, stale `page_private`, driver migration callback failures, and the hard `BUG()` path when accounting says pages exist but none are listable or isolated. Test signals include inflate/deflate loops, list enqueue/dequeue batching, compaction-induced balloon migration, migration failure paths, zone-crossing migration, and VM counters for inflate/deflate/migrate.
