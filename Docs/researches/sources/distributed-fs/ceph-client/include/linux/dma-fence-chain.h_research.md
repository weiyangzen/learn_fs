<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-fence-chain.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-fence-chain.h

## Purpose
Defines a DMA fence container that chains fences into a timeline while avoiding deep recursion.

## Important APIs, Types, And Functions
The main type is `struct dma_fence_chain`, which embeds a base fence, RCU previous pointer, previous seqno, contained fence, lock, and callback or IRQ work union. Helpers include `to_dma_fence_chain()`, `dma_fence_chain_contained()`, `dma_fence_chain_alloc()`, `dma_fence_chain_free()`, `dma_fence_chain_for_each`, `dma_fence_chain_walk()`, `dma_fence_chain_find_seqno()`, and `dma_fence_chain_init()`.

## Control Flow
A new chain node wraps a current fence and points to a previous chain/fence. Walkers hold references while traversing. Finding by seqno walks backward until it reaches the requested timeline point. Signaling uses callbacks or IRQ work to avoid lock inversion.

## State And Persistence
Runtime state is the chain node graph and referenced fences. `prev_seqno` preserves ordering when previous nodes are garbage-collected. There is no persistence.

## Dependencies And Integration Points
Depends on `dma-fence.h`, IRQ work, slab allocation, and RCU. Used by GPU and DMA reservation code to publish timeline dependencies compactly.

## Risks And Edge Cases
Reference handling in `dma_fence_chain_for_each` requires callers to drop references when breaking out. Initialized chains must be released through `dma_fence_put()`, while uninitialized allocations can use `dma_fence_chain_free()`. RCU previous pointers and sequence comparisons must handle garbage-collected nodes.

## Test Signals
Tests should cover chain initialization, walking, early loop break reference cleanup, find-by-seqno before/after garbage collection, contained-fence extraction, signaling order, and release paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-fence-chain.h -->
