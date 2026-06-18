<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_reporting.h -->
# sources/distributed-fs/ceph-client/include/linux/page_reporting.h

## Purpose
This header declares the free-page reporting device interface, used to report unused guest/system pages to a backing device or hypervisor.

## Important APIs, types, and functions
It defines `PAGE_REPORTING_CAPACITY`, `PAGE_REPORTING_ORDER_UNSPECIFIED`, and `struct page_reporting_dev_info`, which contains a `report()` callback, delayed work item, atomic state, and minimum reporting order. APIs are `page_reporting_register()` and `page_reporting_unregister()`.

## Control flow
A reporting device registers callbacks. Background delayed work gathers free pages into scatterlists and calls `report()`. Unregister tears down reporting work and device state.

## State and persistence
Persistent runtime state is the registered device info, delayed work, atomic reporting state, and selected reporting order. Reported page state is tracked by allocator/page flags outside this header.

## Dependencies and integration points
It depends on mmzone, scatterlists, delayed work, page allocator free lists, virtio-balloon or similar reporting devices, and `PG_reported` page flags.

## Risks and test signals
Risks include unregister races with delayed work, reporting pages that are reallocated, wrong order/capacity assumptions, scatterlist callback failures, and state-machine stalls. Test register/unregister under load, free page reporting cycles, callback error handling, page allocation races, order selection, and virt/hypervisor integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_reporting.h -->
