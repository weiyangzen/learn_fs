# sources/distributed-fs/eos/unit_tests/mgm/tgc/TapeGcTests.cc

Purpose: GoogleTest coverage for EOS MGM tape garbage collection (`eos::mgm::tgc::TapeGc` and `TestingTapeGc`). It validates construction defaults, worker-thread startup, one-file garbage collection decisions, JSON rendering, and `MaxLenExceeded` handling.

Important APIs and fixtures: `TgcTapeGcTest` is an empty `::testing::Test` fixture. Tests instantiate `DummyTapeGcMgm`, `TapeGc`, and `TestingTapeGc`; call `getStats()`, `startWorkerThread()`, `tryToGarbageCollectASingleFile()`, `fileAccessed()`, and `toJson()`; and check `DummyTapeGcMgm` call counters such as `getNbCallsToGetTapeGcSpaceConfig()`, `getNbCallsToGetFileSizeBytes()`, and `getNbCallsToEvictAsRoot()`.

Control flow: `constructor` verifies a fresh collector has zero evicts, empty LRU, empty space stats, and a query timestamp near `time(nullptr)`. `startWorkerThread` only asserts no crash. `tryToGarbageCollectASingleFile` progressively changes fake MGM space stats and tape-GC config: no config, one accessed file, sufficient availability, then low total-bytes threshold; only the final state should fetch file size and evict once. JSON tests populate three FIDs and assert MRU-to-LRU hexadecimal ordering, then force a max-length exception.

State and persistence: All state is in-memory fake MGM state plus collector LRU state. The tests intentionally set `maxConfigCacheAgeSecs = 0`, forcing every GC attempt to refresh configuration, which explains the exact config call-count assertions.

Dependencies and integration: Depends on EOS MGM tape-GC test helpers and metadata IDs (`eos::IFileMD::id_t`) plus GoogleTest. It integrates with the tape-GC abstraction through the same public/test-only hooks used by MGM code.

Risks: The worker-thread test lacks assertions or synchronization, so regressions in actual worker behavior may pass. Timestamp assertions allow only a small future skew. JSON comparison is intentionally strict but brittle if formatting changes while semantics remain acceptable.

Test signals: This file itself is the test signal for `TapeGc`. It is strongest for decision gating and serialization order, weaker for concurrency, repeated eviction, namespace-filtering, and error propagation paths.
