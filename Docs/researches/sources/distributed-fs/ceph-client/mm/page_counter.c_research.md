# Research: sources/distributed-fs/ceph-client/mm/page_counter.c

## Purpose

`sources/distributed-fs/ceph-client/mm/page_counter.c` implements lockless hierarchical page accounting and limiting. It is the generic counter primitive used by memory cgroups and related resource controllers to charge pages up a parent chain, enforce maximum page limits, track high-water marks and fail counts, parse user-provided memory limits, and compute effective `memory.min`/`memory.low` protection for reclaim decisions.

## Important APIs, Types, and Functions

The central type is `struct page_counter`, declared in `linux/page_counter.h`. This file operates on fields such as `usage`, `max`, `failcnt`, `watermark`, `local_watermark`, `min`, `low`, `min_usage`, `low_usage`, `children_min_usage`, `children_low_usage`, `emin`, `elow`, `parent`, `protection_support`, and `track_failcnt`.

Public functions are `page_counter_cancel()`, `page_counter_charge()`, `page_counter_try_charge()`, `page_counter_uncharge()`, `page_counter_set_max()`, `page_counter_set_min()`, `page_counter_set_low()`, `page_counter_memparse()`, and, when `CONFIG_MEMCG` or `CONFIG_CGROUP_DMEM` is enabled, `page_counter_calculate_protection()`. Internal helpers are `track_protection()`, `propagate_protected_usage()`, and `effective_protection()`.

## Control Flow

Charging without a limit check uses `page_counter_charge()`: it walks from the target counter to the root, atomically adds `nr_pages` to each `usage`, optionally propagates protected usage to parents, and updates local/global watermarks with intentionally racy but acceptable stores.

Limit-aware charging uses `page_counter_try_charge()`. It speculatively increments each counter in the hierarchy, then compares the new value to that counter's `max`. If a limit is exceeded, it subtracts the speculative charge from the failing counter, optionally increments `failcnt`, records the first failing counter through `fail`, and cancels charges already applied to descendants below the failing ancestor. The speculative add avoids a compare-and-swap loop and relies on full-barrier atomic operations to coordinate with concurrent `page_counter_set_max()`.

Uncharging uses `page_counter_uncharge()` to walk the same hierarchy and call `page_counter_cancel()` on each counter. `page_counter_cancel()` subtracts locally, warns and clamps on underflow, and updates protected usage propagation when enabled.

Limit updates use `page_counter_set_max()`. The caller must serialize updates on the same counter. The function reads usage, rejects a limit below current usage with `-EBUSY`, swaps in the new max, then rereads usage to detect races with concurrent try-charge. If a concurrent charge could have observed the old limit while pushing usage above the new one, it restores the old max and retries after `cond_resched()`.

Protection configuration uses `page_counter_set_min()` and `page_counter_set_low()` to store the configured protection and propagate current effective protected usage through ancestors. Reclaim-facing protection calculation uses `page_counter_calculate_protection()` during top-down tree walks. Immediate children of the root get their declared `min`/`low`; deeper descendants call `effective_protection()` to cap, proportionally distribute overcommitted protection, and optionally distribute unclaimed recursive protection by usage.

## State and Persistence Behavior

The state is in-memory resource accounting only. `usage`, limits, protected usage, child aggregates, fail counts, and watermarks live in `struct page_counter` instances owned by cgroups or similar controllers. There is no file-backed persistence here, although controller state may be exposed through cgroup files elsewhere.

Updates are lockless and mostly atomic. Some values, especially `watermark`, `local_watermark`, and `failcnt`, are explicitly allowed to be approximate under races because they are used for reporting rather than correctness. Protection aggregates are maintained in parent counters using atomic deltas whenever a child usage crosses its configured `min` or `low` boundary.

## Dependencies and Integration Points

Dependencies are small: `linux/page_counter.h`, atomics, scheduler rescheduling, string parsing, `memparse()`, page size definitions, and configuration gates for memcg or cgroup device memory. Integration is primarily with memory cgroup charging/un charging, cgroup v2 memory limit files, reclaim protection in `memory.min` and `memory.low`, and any controller that wants hierarchical page-count limits.

The parser `page_counter_memparse()` connects user-facing byte strings to page counts. It accepts a controller-provided max keyword and otherwise parses bytes with `memparse()`, converting to pages and clamping to `PAGE_COUNTER_MAX`.

## Risks and Edge Cases

The main correctness risk is charge/uncharge imbalance. Underflow in `page_counter_cancel()` indicates a serious caller bug and is clamped only after warning. Hierarchical rollback in `page_counter_try_charge()` must cancel exactly the counters already charged before the first failing ancestor.

Races are intentional but bounded. Watermarks and fail counts can be inaccurate, and protection propagation can observe non-atomic combinations of usage and settings. The effective protection math guards divisions by checking parent and child usage/protection relationships, but callers must still perform top-down traversal as documented; isolated calls can use stale parent effective values.

`page_counter_set_max()` depends on serialized limit writers and the ordering between atomic charge and max reads. Removing that serialization or weakening atomic ordering would allow limits below current usage or false failures. `page_counter_memparse()` truncates sub-page byte values to zero pages, which is expected but can surprise callers that do not validate minimums elsewhere.

## Test Signals

Useful validation includes memcg charge/uncharge stress under concurrency, cgroup memory.max updates racing with allocations, hierarchical limit failure tests that check `fail` points at the first limiting ancestor, underflow warning tests for negative accounting, watermark reset/read tests, `memory.min` and `memory.low` reclaim-protection scenarios with overcommitted and undercommitted siblings, recursive protection behavior, and parser tests for numeric values, suffixes, invalid trailing characters, and the controller's max keyword.
