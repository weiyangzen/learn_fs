# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fetch_test.go

Purpose: tests distribution fetcher configuration, HTTP retrieval, binary download/unpack, and `MultiFetcher` gateway failover behavior.

Important APIs and control flow: tests cover `GetDistPathEnv`, `NewHttpFetcher`, `HttpFetcher.Fetch`, `FetchBinary`, user-agent propagation, migration source failover from bad gateways, `NewMultiFetcher`, quarantine ordering, full-failure reset, exhaustion cap, concurrent fetches, success counter reset, and context cancellation.

State and persistence: writes binaries to temp dirs, manipulates `TMPDIR`, starts `httptest` gateways, and uses atomic counters for concurrency assertions.

Dependencies and integration: relies on the CAR-backed test gateway from `setup_test.go`, `GetMigrationFetcher`, and test fetcher stubs.

Risks and test signals: strong signal for gateway robustness and race-sensitive lock paths. It does not perform real network downloads and skips some permission behavior on Windows.
