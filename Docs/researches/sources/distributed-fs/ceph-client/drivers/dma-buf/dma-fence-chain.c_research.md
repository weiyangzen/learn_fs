# sources/distributed-fs/ceph-client/drivers/dma-buf/dma-fence-chain.c

Purpose: implements dma-fence chains, a timeline-like container where each node wraps a current fence and links to a previous fence/chain, allowing ordered waiting and sequence-number lookup without large arrays.

Important APIs/types/functions: exports `dma_fence_chain_walk()`, `dma_fence_chain_find_seqno()`, `dma_fence_chain_ops`, and `dma_fence_chain_init()`. Internal helpers include RCU-safe previous-node lookup, chain callback rearming through irq_work, and release-time recursive unlink avoidance.

Control flow: `dma_fence_chain_init()` stores references to previous and current fences, chooses a context/sequence number, initializes the base fence with 64-bit seqno support, and assigns a separate lockdep class. `enable_signaling()` walks the chain and arms a callback on the first unsignaled contained fence; the callback queues irq_work, which tries to rearm on the next unsignaled fence or signals the chain base when all are complete. `dma_fence_chain_walk()` advances to the previous link and opportunistically garbage-collects already signaled chain nodes by replacing `prev`. `find_seqno()` advances from a chain head to the node covering a requested seqno.

State and persistence behavior: each chain node owns references to `prev` and `fence`. Release manually unlinks single-referenced chain nodes to avoid recursive put/free paths, then drops the contained fence and frees the base object. Garbage collection can shorten chains as signaled prefixes are traversed.

Dependencies and integration points: depends on dma-fence core, RCU-safe fence gets, irq_work, and public chain iteration macros. Used by sync/fence users that need timeline composition and by fence unwrap utilities.

Risks and test signals: contained fences must not themselves be chain containers; chain nesting is allowed only through `prev`. Sequence-number lookup semantics for gaps and out-of-order completion are subtle. Test signals include forward/backward/random signaling, wait on long chains, sequence lookup for exact/gap/future values, concurrent lookup/signaling races, deadline propagation, and release without recursive stack overflow.
