# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/reviewer/ProbabilisticBufferReviewer.java

Purpose: Reviewer that probabilistically rejects allocations as a directory approaches configured hard and soft free-space limits, preserving expansion buffer.

Important APIs: Constructor reads hard and soft byte limits; package-visible `getProbability`; `acceptAllocation` compares probability to `ThreadLocalRandom`.

Control flow: Directories above soft limit are always accepted; at or below hard limit are rejected; between limits a linear probability is calculated from available bytes and capacity.

State and persistence: Stores hard and soft limits in memory. No persistence.

Dependencies and integration: Used by `RoundRobinAllocator` through `Reviewer.Factory` unless skipped. Reads worker reviewer configuration.

Risks and test signals: Randomness makes acceptance nondeterministic; tests should focus on `getProbability` and inject repeated trials only statistically. Validate soft <= hard normalization, boundary probabilities, and allocator retry after rejection.
