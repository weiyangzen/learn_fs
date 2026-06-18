# sources/distributed-fs/ceph-client/drivers/dma-buf/st-dma-fence-unwrap.c

Purpose: selftests fence unwrap and merge helpers across arrays, chains, duplicate fences, sequence-number deduplication, signaled filtering, and mixed container shapes.

Important APIs/types/functions: defines `struct mock_fence`, `__mock_fence()`, `mock_fence()`, `mock_array()`, `mock_chain()`, and top-level `dma_fence_unwrap()`. Subtests cover unwrap and merge variants.

Control flow: mock helpers create fences, arrays, and chains with explicit contexts/seqnos. `unwrap_array`, `unwrap_chain`, and `unwrap_chain_array` verify every original fence appears exactly once during unwrap iteration. Merge tests combine fences and containers, then iterate the result and validate deduplication/order: duplicate same fence collapses, later seqno per context wins, reversed arrays/chains merge deterministically, signaled stub fences are filtered, and complex context/seqno mixtures return only latest unsignaled fences.

State and persistence behavior: all state is temporary per subtest. Ownership transfer is a key part of the tests: arrays/chains take references, merge returns a fence/container, and tests drop references after validation.

Dependencies and integration points: depends on dma-fence, fence-array, fence-chain, fence-unwrap APIs, variadic test helpers, and the selftest harness.

Risks and test signals: tests are sensitive to reference ownership; failure paths must put all allocated fences to avoid leaks during module load. Passing signals include complete iteration coverage, no unexpected fences, correct context/seqno ordering, duplicate release behavior, and allocation-failure paths returning `-ENOMEM`.
