# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/routing_test.go

Purpose: tests that AutoConf can supply delegated routing endpoint configuration and that daemon startup remains healthy when endpoints are empty or offline-mode routing cannot be exercised fully.

Important types/functions: `mockRoutingServer`, `newMockRoutingServer`, `handleProviders`, `testDelegatedRoutingWithAuto`, and `testRoutingErrorHandling`. The mock routing server serves NDJSON provider records at `/routing/v1/providers/{cid}` and records requested CIDs. `providerFunc` allows normal provider records or empty responses.

Control flow creates AutoConf JSON with a `DelegatedEndpoints` entry supporting providers, peers, and IPNS read paths, configures a node with `Routing.DelegatedRouters=["auto"]`, and starts the daemon with `--offline`. It then confirms stored config still shows `auto` and the daemon accepts `version`. The error-handling variant uses empty provider responses but the same startup/config assertions. State is node config/cache and mock request history, though actual routing calls are not deeply exercised. Dependencies include `httptest`, JSON, harness, and delegated routing HTTP response format. Risks include limited behavioral coverage because offline mode avoids real routing queries. Test signal is startup/config preservation rather than provider retrieval correctness.
