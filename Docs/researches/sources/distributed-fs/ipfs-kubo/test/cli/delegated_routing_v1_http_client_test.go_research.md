# sources/distributed-fs/ipfs-kubo/test/cli/delegated_routing_v1_http_client_test.go

Purpose: client-side HTTP delegated routing coverage for custom routing config, provider parsing, metrics, and provider address advertisement.

Important APIs/functions: `TestHTTPDelegatedRouting`, `TestHTTPDelegatedRoutingProviderAddrs`, fake `httptest.Server`, `captureProviderAddrs`, `customRoutingConf`, `ToJSONStr`, and `JSONObj`.

Control flow: the first test verifies default no-router behavior, daemon startup failures for missing/unsupported methods, JSON and NDJSON provider responses from an HTTP router, `routing findprovs` ordering, and Prometheus metrics. The provider-address test captures `/routing/v1/providers` payloads and checks `Addresses.Announce`, `AppendAnnounce`, and wildcard bind address resolution.

State/persistence: node config is repeatedly mutated and daemon restarted; mock servers capture request bodies under mutex protection.

Dependencies/integration: `config.Routing` custom schema, HTTP routing client, provider record serialization, metrics endpoint, address resolution logic, and CLI `routing provide/findprovs`.

Risks/test signals: strong for config validation and provider-record correctness. Reusing one node across early subtests requires careful daemon stop/start sequencing.
