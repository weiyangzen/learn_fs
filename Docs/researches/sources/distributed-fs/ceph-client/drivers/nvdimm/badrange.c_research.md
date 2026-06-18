# sources/distributed-fs/ceph-client/drivers/nvdimm/badrange.c

## Purpose
Maintains NVDIMM bad physical address ranges and converts them into namespace-relative `badblocks` entries for pmem regions. This supports persistent-memory error tracking discovered during bus initialization or ARS processing.

## Important APIs, Types, And Functions
- `badrange_init()` initializes the badrange list and spinlock.
- `badrange_add()` adds or updates a physical bad range; duplicates by start address update length.
- `badrange_forget()` removes a cleared physical interval from the badrange list, deleting, trimming, or splitting entries.
- `__add_badblock_range()` converts byte offsets and lengths to 512-byte sectors and handles ranges larger than `INT_MAX` sectors.
- `badblocks_populate()` intersects global bad ranges with a namespace resource range and adds matching sector ranges.
- `nvdimm_badblocks_populate()` validates the region is pmem, locks the NVDIMM bus, and populates a supplied `struct badblocks`.

## Control Flow
NVDIMM bus setup initializes and adds ranges as they are discovered. When errors are cleared, `badrange_forget()` walks all list entries under spinlock and mutates the list based on overlap with the clear interval. When a namespace/region needs badblocks, `nvdimm_badblocks_populate()` finds the parent bus, takes the bus guard, and calls `badblocks_populate()` to translate physical address intersections into namespace-relative sector entries.

## State And Persistence
The main state is the `struct badrange` list of `struct badrange_entry { start, length }`, protected by `badrange->lock`. Entries persist for the lifetime of the bus or until forgotten. The derived `badblocks` state is populated separately for block-layer consumers.

## Dependencies And Integration Points
Depends on libnvdimm bus/region structures, `badblocks`, block-sector conventions, `struct range`, device guards, and internal `nd-core.h` / `nd.h` helpers such as `walk_to_nvdimm_bus()` and `is_memory()`.

## Risks And Edge Cases
- `add_badrange()` drops the spinlock for allocation and reacquires it; concurrent additions are handled by duplicate search after reacquire, but ordering remains append-only.
- `badrange_forget()` split path ignores allocation failure from `alloc_and_append_badrange_entry(..., GFP_NOWAIT)`, so clearing the middle of a range can lose the right half if allocation fails.
- Address arithmetic uses inclusive end values (`start + len - 1`); zero lengths would underflow and should not be passed.
- Overlapping ranges are intentionally not normalized on insertion; consumers must tolerate overlap when converting to badblocks.
- `nvdimm_badblocks_populate()` is only valid for pmem regions and warns otherwise.

## Test Signals
Unit tests should add duplicate, overlapping, adjacent, and very large ranges; forget intervals covering head, tail, full, and middle splits; and populate namespaces with ranges inside, outside, and straddling the namespace. Runtime logs from `set_badblock()` and `badblocks_set()` failures help validate conversion behavior.
