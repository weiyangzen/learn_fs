<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/balloon.h -->
# sources/distributed-fs/ceph-client/include/xen/balloon.h

## Purpose
This header declares Xen balloon memory-management state and APIs for changing domain memory targets and allocating/freeing ballooned pages.

## Important APIs, Types, And Functions
- `RETRY_UNLIMITED` encodes no retry limit.
- `struct balloon_stats` tracks current and target pages, target unpopulated pages, low/high balloon pages, total pages, schedule delay, max delay, retry count, and max retry count.
- `balloon_stats` is the global stats instance.
- `balloon_set_new_target()` updates the target allocation.
- `xen_alloc_ballooned_pages()` and `xen_free_ballooned_pages()` manage pages taken from or returned to the balloon.
- `xen_balloon_init()` is real under `CONFIG_XEN_BALLOON` and a no-op otherwise.

## Control Flow
Balloon control paths set a target, worker logic inflates/deflates toward it, and grant/DMA/users needing unpopulated pages call the allocation helpers. Initialization registers balloon machinery only when configured.

## State And Persistence
`balloon_stats` persists domain memory accounting and retry scheduling state. Allocated ballooned pages persist until returned through `xen_free_ballooned_pages()`.

## Dependencies And Integration Points
It integrates with Xen memory reservation hypercalls, Linux page allocation, memory hotplug/pressure behavior, grant table page allocation, and optional balloon driver configuration.

## Risks And Edge Cases
Incorrect accounting can leak pages or over-balloon the domain. Retry values and schedule delays must avoid livelock under memory pressure. Stub `xen_balloon_init()` means callers must tolerate disabled balloon support.

## Test Signals
Signals include target changes reflected in stats, successful page allocation/free cycles, stable behavior under low/high memory pressure, bounded retry scheduling, and no-op initialization when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/balloon.h -->
