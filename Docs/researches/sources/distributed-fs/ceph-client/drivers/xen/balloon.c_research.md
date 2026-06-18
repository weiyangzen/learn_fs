# sources/distributed-fs/ceph-client/drivers/xen/balloon.c

## Purpose
`balloon.c` implements Xen memory ballooning: returning pages to Xen, reclaiming pages from Xen, optionally hotplugging unpopulated memory ranges, and providing ballooned pages for grant/foreign mappings.

## Important APIs, types, and functions
Global state includes `balloon_stats`, `balloon_state`, `balloon_mutex`, `balloon_thread_wq`, `ballooned_pages`, `balloon_wq`, and `frame_list`. Important functions are `balloon_append`, `balloon_retrieve`, `update_schedule`, `reserve_additional_memory`, `xen_online_page`, `increase_reservation`, `decrease_reservation`, `balloon_thread`, `balloon_set_new_target`, `xen_alloc_ballooned_pages`, `xen_free_ballooned_pages`, `balloon_add_regions`, `balloon_init`, and `balloon_wait_finish`.

## Control flow
Init runs in Xen domains, computes current reservation, initializes stats, installs memory hotplug callbacks/sysctl when enabled, adds extra memory regions to the balloon list, starts the `xen-balloon` kthread, and initializes the sysfs/control side through `xen_balloon_init`. The thread waits for target/current credit changes. Positive credit retrieves ballooned pages or hotplugs additional memory; negative credit allocates pages, scrubs them, resets VA mappings, adds them to the balloon list, flushes TLBs, and decreases the Xen reservation.

## State and persistence
Ballooned pages are tracked on a global list using page `lru`, with offline page flags and `NR_BALLOON_PAGES` accounting. `balloon_stats` tracks current, target, total, low/high ballooned pages, retry delay, and unpopulated target. Xen reservation and p2m mappings are persistent hypervisor/kernel state until reversed.

## Dependencies and integration points
It depends on Xen memory reservation helpers, p2m mapping helpers, Linux memory hotplug, sysctl, kthreads, freezer, page allocator, highmem kmap flushing, TLB flushes, and exported `xen_alloc_ballooned_pages`/`xen_free_ballooned_pages` users such as grant mappings.

## Risks and test signals
Risks include accounting underflow, OOM pressure during balloon-out, deadlocks with memory hotplug locks, P2M invalidation mistakes, highmem kmap stale mappings, retry cancellation during boot ballooning, and `target_unpopulated` imbalance on allocation failure. Test signals include PV and HVM/PVH guests, Dom0 current-reservation path, balloon up/down under memory pressure, hotplug unpopulated sysctl, grant-page allocation/free, extra memory regions, initial balloon wait timeout, and fault injection in reservation hypercalls.
