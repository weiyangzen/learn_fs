# sources/distributed-fs/eos/test/microbenchmarks/mgm/BM_RRSeed.cc

## Purpose
Benchmarks the basic round-robin seed generator against the thread-local variant used by placement scheduling. It isolates seed generation overhead from full scheduler topology traversal.

## Important APIs, types, and functions
`BM_RRSeed` constructs `eos::mgm::placement::RRSeed seed(10)` and repeatedly calls `seed.get(1, 0)`. `BM_ThreadLocalRRSeed` initializes `ThreadLocalRRSeed::init(10)` and calls `ThreadLocalRRSeed::get(1, 0)`. Both use Google Benchmark counters.

## Control flow
Each benchmark iteration performs ten seed reads and reports operation rate as `iterations * 10`. Registrations use `ThreadRange(1, 64)` and real time to observe contention effects.

## State and persistence
State is transient seed state. `ThreadLocalRRSeed` has static/thread-local state initialized before the loop. No persistent data is touched.

## Dependencies and integration points
Depends on Google Benchmark and MGM placement seed classes. It supports performance decisions for scheduler round-robin state management.

## Risks and test signals
Signals are throughput and contention differences. Risks include benchmark sensitivity to static initialization, insufficient coverage of multiple bucket keys, and not validating sequence correctness. Correctness tests should separately cover wraparound and concurrent uniqueness.
