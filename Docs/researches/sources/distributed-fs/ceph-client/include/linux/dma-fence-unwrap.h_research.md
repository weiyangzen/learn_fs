<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-fence-unwrap.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-fence-unwrap.h

## Purpose
Declares helpers to flatten nested DMA fence containers such as arrays and chains.

## Important APIs, Types, And Functions
Defines `struct dma_fence_unwrap`, `dma_fence_unwrap_first()`, `dma_fence_unwrap_next()`, `dma_fence_unwrap_for_each`, `__dma_fence_unwrap_merge()`, `dma_fence_dedup_array()`, and macro `dma_fence_unwrap_merge()`.

## Control Flow
The iterator starts from a head fence, descends through chain and array containers, and returns concrete underlying fences one at a time. Merge unwraps several input fences, deduplicates them, and returns a flat fence array representing the combined dependency set.

## State And Persistence
Iterator state is the current chain, current array, and array index. Merge uses stack cursor arrays through the macro and returns a refcounted fence object. No persistence exists.

## Dependencies And Integration Points
Depends conceptually on `dma-fence`, array fences, and chain fences. It integrates users that need to wait on or merge dependencies without recursive container handling.

## Risks And Edge Cases
Deduplication must preserve correct dependency coverage without leaking references. Deeply nested containers should not recurse on the C stack. Stack allocation in `dma_fence_unwrap_merge()` is proportional to argument count.

## Test Signals
Tests should cover plain fences, arrays, chains, nested array-chain combinations, duplicate fences, empty merge inputs, allocation failure, and iterator correctness after container children signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-fence-unwrap.h -->
