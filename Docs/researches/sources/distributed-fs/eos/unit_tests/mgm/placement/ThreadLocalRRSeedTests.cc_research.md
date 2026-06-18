# sources/distributed-fs/eos/unit_tests/mgm/placement/ThreadLocalRRSeedTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/placement/ThreadLocalRRSeedTests.cc

Purpose: tests `ThreadLocalRRSeed`, the per-thread seed source for thread-local round-robin placement.

Important APIs and types: `ThreadLocalRRSeed` and its random/seed retrieval behavior.

Control flow: the `random` test obtains seed values and checks that the API returns usable values. It intentionally avoids deterministic ID assertions because thread-local round-robin starts from randomized per-thread positions.

State and persistence: state is thread-local in process memory. No external persistence.

Dependencies and integration: feeds `PlacementStrategyT::kThreadLocalRoundRobin`, reducing cross-thread contention while preserving local round-robin behavior.

Risks and test signals: coverage is light; it mostly catches construction or gross API failures. Distribution quality and independence are tested indirectly in scheduler loop tests.
