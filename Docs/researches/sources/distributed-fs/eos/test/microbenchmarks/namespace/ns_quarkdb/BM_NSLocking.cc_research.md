# sources/distributed-fs/eos/test/microbenchmarks/namespace/ns_quarkdb/BM_NSLocking.cc

## Purpose
Benchmarks namespace metadata locking paths for QuarkDB-backed namespace objects. It compares a single container write lock against bulk write locking of multiple namespace objects.

## Important APIs, types, and functions
The fixture creates `eos::ns::testing::NsTests`, namespace containers/files, `MDLocking::ContainerWriteLock`, and `MDLocking::BulkMDWriteLock`. `simulateWork()` burns CPU while locks are held to mimic protected work.

## Control flow
For each benchmark, thread 0 initializes global test namespace objects. `ContainerMDLock` repeatedly locks one container, changes an attribute, and updates the container store. `BulkNSObjectLocker` adds two containers and one file to a bulk locker, acquires all locks, and simulates work. Both run over `ThreadRange(1, 5000)`.

## State and persistence
State is an in-memory/test QuarkDB namespace fixture and global shared object pointers. The benchmark mutates test metadata attributes but not production state.

## Dependencies and integration points
Depends on Google Benchmark, namespace locking APIs, bulk locker, QuarkDB namespace test harness, and hierarchical view classes.

## Risks and test signals
Global fixture pointers and thread-0 setup can race if other threads enter before initialization is visible. Signals include lock contention scalability and bulk-lock overhead. Tests/benchmarks should watch for deadlocks, lock ordering regressions, update-store cost, and unrealistic CPU work dominating lock behavior.
