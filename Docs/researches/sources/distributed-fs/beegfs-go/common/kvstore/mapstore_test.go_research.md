# sources/distributed-fs/beegfs-go/common/kvstore/mapstore_test.go

Purpose: this file is the main behavioral and performance test suite for the generic Badger-backed `MapStore`. It validates key legality, create/get/update/delete flows, lock release semantics, iteration, concurrency behavior, auto-generated keys, and the Badger value-log garbage-collection runner.

Important APIs exercised include `NewMapStore[T]`, `CreateAndLockEntry`, `GetAndLockEntry`, `GetEntry`, `GetEntries`, `DeleteEntry`, release options such as `WithValue`, `WithAllowExisting`, `WithUpdateOnly`, and `WithDeleteEntry`, plus garbage-collection helpers such as `StartRunner`, `attemptGarbageCollection`, `runGarbageCollection`, and `systemLoad.isSystemLoadHigh`.

Control flow is test-driven around temporary Badger directories under `/tmp`. Entries are created, mutated through locked pointers, committed through release callbacks, and then read or iterated in lexicographic Badger key order. Several tests intentionally hold locks across goroutines to prove the in-memory `entryLocks` cache and `keepLock` counter preserve serialization.

State and persistence behavior centers on BadgerDB records plus transient per-key locks. Tests assert that deleted entries disappear from both DB and cache, auto-generated keys are fixed-width base-36 strings, iterators can be cleaned up repeatedly, and GC delays change depending on system load and Badger `ErrNoRewrite`.

Dependencies include Badger v4, `testify/assert`, `testify/require`, `testify/mock`, OS temp directories, runtime CPU counts, and package-local mock GC/system-load types. Integration points are the production `MapStore` implementation and Badger's value-log GC.

Risks: benchmarks contain acknowledged races around concurrent create/delete timing and use sleeps for synchronization. Tests also inspect private fields such as `entryLocks`, making them sensitive to internal refactors. System-load parsing is Linux `/proc/loadavg` shaped.

Test signals: coverage is broad for CRUD, reserved-key rejection, iterator boundaries, locking, concurrent access, GC scheduling, and load detection. Performance benchmarks cover create, lock/get, delete, iteration, and two-DB concurrent flows.
