# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/LruBenchmark.cc

Purpose: Command-line benchmark for concurrent `eos::LRU` cache reads.
Important APIs/types/functions: global mutex/condition variable and `gDoneWork`; dummy `Entry`; `Populate`; worker function `WokerThread` (typo in name); CLI11 `main` options `--size`, `--num_threads`, and `--num_requests`.
Control flow: populate an LRU, create worker threads, sleep briefly to let them block on a condition variable, notify all, each worker performs sequential `get()` calls starting at a random key, then main measures elapsed microseconds and prints a kHz rate.
State/persistence: all state is in-process memory; no QDB persistence.
Dependencies/integration: uses `namespace/ns_quarkdb/LRU.hh`, CLI11, C++ threading, atomics, and EOS random helper.
Risks: condition-variable wait has no predicate in workers, so missed/spurious wakeups are possible; `gDoneWork` is global and not reset for repeated in-process runs; throughput is read-only and does not measure eviction behavior.
Test signals: benchmark-only, not part of GTest assertions.
