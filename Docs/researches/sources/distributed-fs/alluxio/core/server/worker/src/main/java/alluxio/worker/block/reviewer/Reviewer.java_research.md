# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/reviewer/Reviewer.java

Purpose: Public experimental policy interface for accepting or rejecting allocator placement decisions.

Important APIs: `acceptAllocation(StorageDirView)` and nested `Factory.create()` using `WORKER_REVIEWER_CLASS`.

Control flow: Allocators ask the reviewer after a candidate directory satisfies location and space constraints. False means the allocator should try another candidate.

State and persistence: Interface only; implementations decide local state. No persistence contract.

Dependencies and integration: Used by `Allocator` implementations, especially `RoundRobinAllocator`.

Risks and test signals: Factory reflection errors surface at allocator construction. Tests should cover configured class creation and allocation behavior when reviewer rejects all candidates.
