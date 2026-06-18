# sources/distributed-fs/ceph-client/drivers/dma-buf/dma-fence-unwrap.c

Purpose: provides utilities to flatten dma-fence array/chain containers and merge multiple fence inputs into a minimal fence or fence array.

Important APIs/types/functions: exports `dma_fence_unwrap_first()`, `dma_fence_unwrap_next()`, `dma_fence_dedup_array()`, and `__dma_fence_unwrap_merge()`. Internal `fence_cmp()` sorts by context and newest sequence number.

Control flow: unwrap starts by taking a reference to the head, treating the current chain-contained fence as a possible array, and returning its first member. Next advances within the current array, then walks the chain when the array is exhausted. Merge first counts unsignaled unwrapped fences and tracks the latest signaled timestamp. If none are pending it returns a private signaled stub with that timestamp; if one is pending it returns that fence directly; otherwise it collects unsignaled fences, deduplicates by context keeping the latest, and returns either the remaining single fence or a new `dma_fence_array`.

State and persistence behavior: no global state. Merge owns temporary arrays and carefully transfers fence references to either returned objects or releases duplicates.

Dependencies and integration points: depends on dma-fence, array, chain, sorting, and allocation helpers. Used by sync-file import and reservation singleton/merge paths where container fences must be decomposed before adding to reservation objects.

Risks and test signals: callers must understand reference ownership for returned fences and iterated members. Signaled fences are collapsed into timestamped private stubs, which preserves completion time but not original identity. Test signals include flattening arrays, chains, and chain-of-array shapes; deduplicating duplicate contexts by latest seqno; preserving deterministic order after sort; filtering signaled fences; and returning NULL only on allocation failure.
