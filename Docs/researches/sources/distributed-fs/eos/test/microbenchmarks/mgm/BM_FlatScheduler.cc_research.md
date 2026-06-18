# sources/distributed-fs/eos/test/microbenchmarks/mgm/BM_FlatScheduler.cc

## Purpose
Benchmarks EOS MGM flat placement scheduler strategies under varying group counts, replica counts, and thread counts. It measures scheduling throughput for round-robin, thread-local round-robin, random, fid-seeded random, weighted random, and weighted round-robin placement.

## Important APIs, types, and functions
Benchmark functions build `eos::mgm::placement::ClusterMgr` data with root/group buckets and `Disk` entries, instantiate `FlatScheduler` with a `PlacementStrategyT`, then call `schedule()`. Weighted variants use `eos::common::pickIndexRR()` and `PlacementArguments` with incrementing fids.

## Control flow
Each benchmark constructs a synthetic cluster once, then in the benchmark loop obtains immutable cluster data and calls the scheduler with the requested replica/stripe count. Google Benchmark registrations run 1, 8, 64, 128, and 256 threads across group counts 32-512 and placement widths 2, 3, and 6.

## State and persistence
State is in-memory synthetic cluster topology and scheduler counters. No persistent metadata is modified.

## Dependencies and integration points
Depends on Google Benchmark, placement `ClusterMap`, `PlacementStrategy`, `FlatScheduler`, and common container utilities. It tracks performance for code used by production file placement.

## Risks and test signals
This is a performance signal, not a correctness test. Risks include unrealistic topology, shared scheduler state under high thread counts, and excessive benchmark runtime. Useful signals are throughput regressions, scalability differences between global and thread-local seeds, and weighted placement overhead.
