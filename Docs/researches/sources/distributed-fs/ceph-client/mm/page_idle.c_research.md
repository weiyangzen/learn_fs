# sources/distributed-fs/ceph-client/mm/page_idle.c

## Purpose
`page_idle.c` implements the kernel idle page tracking sysfs bitmap at `mm/page_idle/bitmap`. Userspace can mark PFNs idle and later read the bitmap to identify pages that stayed idle after the kernel cleared CPU and device young/accessed state from all mappings.

## Important APIs, Types, And Functions
- `page_idle_get_folio(pfn)` resolves an online head page to an LRU folio and pins it with `folio_try_get()`.
- `page_idle_clear_pte_refs_one()` is the rmap callback that walks PTE or PMD mappings and clears young bits via `ptep_test_and_clear_young()`, `pmdp_test_and_clear_young()`, and MMU notifier callbacks.
- `page_idle_clear_pte_refs()` locks a mapped folio and invokes `rmap_walk()` with anon-vma locking support.
- `page_idle_bitmap_read()` and `page_idle_bitmap_write()` implement the binary sysfs bitmap protocol in `u64` chunks.
- `page_idle_init()` registers the `page_idle` attribute group under `mm_kobj`.

## Control Flow
Writes validate `u64` alignment, convert file offset to PFN, and for each set bit fetch the folio, clear existing PTE references, set the idle flag, and drop the reference. Reads use the same PFN iteration but report a bit only when the folio is still idle after another reference-clearing pass. The rmap callback treats any accessed PTE or THP PMD mapping as evidence that the whole folio is referenced, clears the idle flag, and sets the young folio flag so reclaim is not misled by the idle-tracker access-bit harvesting.

## State And Persistence Behavior
State is runtime-only: folio idle and young flags, CPU page-table accessed bits, and device/MMU-notifier young state. The sysfs file is a view and command channel, not persistent storage. Only online, non-tail, LRU folios are considered; non-user pages always read as non-idle and ignore set attempts.

## Dependencies And Integration Points
The file depends on sysfs/kobject registration, memory hotplug PFN lookup, folio/LRU state, rmap walking, THP PMD helpers, MMU notifiers, page extension idle flags, and `mm_kobj`. It is used by userspace page-idle tools and indirectly by reclaim diagnostics because it manipulates young/referenced state.

## Risks
- The bitmap ABI requires `pos` and `count` to be multiples of 8 bytes; callers that use byte-granular offsets get `-EINVAL`.
- Young-bit clearing can race with mapping changes; the code uses folio locking plus rmap locking, but the result is inherently a sampled signal.
- Only LRU folios are tracked, so isolated, reserved, slab, and most kernel pages are invisible by design.
- Clearing accessed bits must preserve reclaim behavior through `folio_set_young()`.

## Test Signals
- Read/write `/sys/kernel/mm/page_idle/bitmap` with aligned and unaligned offsets.
- Mark mapped anonymous, file-backed, THP, and unmapped LRU folios idle, then access them and verify the read bitmap clears.
- Exercise memory hotplug/offline PFN holes and concurrent reclaim/migration while scanning.
