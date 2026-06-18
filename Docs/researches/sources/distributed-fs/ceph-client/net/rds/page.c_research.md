# sources/distributed-fs/ceph-client/net/rds/page.c

## Purpose
`page.c` provides a small page-fragment allocator for RDS scatterlists. It reduces memory waste for sub-page payload fragments by caching the unused remainder of one page per CPU.

## Important APIs, Types, and Functions
The local `struct rds_page_remainder` stores a cached page, current offset, and `local_lock_t`. Public APIs are `rds_page_remainder_alloc()` and `rds_page_exit()`.

## Control Flow
For full-page-or-larger requests, `rds_page_remainder_alloc()` allocates a page directly and returns it as a full-page SG entry. For smaller requests, it disables bottom halves, locks the per-CPU remainder, discards an existing page if the remaining space is too small, returns a fragment from the cached page when possible, increments the page reference for the caller, advances the offset aligned to 8 bytes, and frees the cached holder reference when the page is exhausted. If no cached page exists, it temporarily drops the local lock and BH disable, allocates a highmem page, then installs it if another caller did not race to fill the slot.

`rds_page_exit()` walks all possible CPUs and frees any cached remainder page.

## State and Persistence
State is per-CPU volatile cache state. Each cached page is retained by the allocator until exhausted, discarded, or module exit. Returned SG fragments hold their own page references and are freed by message or receive cleanup.

## Dependencies and Integration Points
`message.c` uses this for copied user payloads. `ib_recv.c` uses it for receive fragments. Statistics `s_page_remainder_hit` and `s_page_remainder_miss` provide runtime insight.

## Risks
The allocator assumes transmit users treat page regions as read-only while devices own them. Incorrect caller freeing or missing page puts can leak highmem pages. Local locking/BH behavior must remain valid for callers from softirq-adjacent paths. Tiny unusable remainders are intentionally discarded, which affects memory efficiency but simplifies fragmentation.

## Test Signals
Exercise small allocations across CPUs, alignment behavior, exact page exhaustion, direct full-page allocation, allocation failure propagation, and `rds_page_exit()` freeing cached pages. Monitor hit/miss counters and page refcount leaks.
