# sources/distributed-fs/ceph-client/drivers/dma-buf/st-dma-fence-chain.c

Purpose: selftests dma-fence-chain behavior, including sequence lookup, signaling order, waiting, garbage collection, and concurrent lookup/signaling races.

Important APIs/types/functions: defines mock fences backed by a `KMEM_CACHE` with RCU-safe slab flags, helper `mock_chain()`, `struct fence_chains`, chain construction/destruction helpers, and top-level `dma_fence_chain()`.

Control flow: `fence_chains_init()` builds an array of mock fences and a chain tail of requested length, enabling software signaling on each chain node. Subtests validate `dma_fence_chain_find_seqno()` for exact, zero, future, previous, gap, signaled, and out-of-order cases. Race tests spawn per-CPU kthreads that randomly find seqnos and signal fences in a long chain. Signaling tests complete fences forward/backward and verify chain nodes only signal when predecessors are complete. Wait tests run a waiter on the tail and signal contained fences in forward, backward, or randomized order.

State and persistence behavior: temporary chain/fence arrays are allocated with `kvmalloc`; each test releases fences/chains through `fence_chains_fini()`. The slab cache exists for the duration of `dma_fence_chain()` and is destroyed after subtests.

Dependencies and integration points: depends on dma-fence core, dma-fence-chain APIs, kthreads, random number helpers, RCU-safe slab allocation, and the selftest harness.

Risks and test signals: race test timing is bounded and may be sensitive to CPU count/scheduling. The tests exercise long chains (`CHAIN_SZ` is 4096), which is important for stack-safety and garbage collection. Passing signals include no incorrect seqno lookup, no premature chain signaling, waiter completion under varied signal orders, and no race errors under concurrent find/signal.
