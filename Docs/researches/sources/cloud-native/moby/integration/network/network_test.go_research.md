<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/network_test.go -->
# sources/cloud-native/moby/integration/network/network_test.go

Purpose: general API-level network integration tests covering invalid JSON handling, network list endpoints, default network presence, filtering, and scope-aware inspection.

Important APIs/types/functions: `TestNetworkInvalidJSON`, `TestNetworkList`, `TestAPINetworkGetDefaults`, `TestAPINetworkFilter`, and `TestNetworkInspectWithScope` use low-level request helpers, API client filters, swarm helper, and containerd errdefs not-found matching.

Control flow: invalid JSON test iterates POST endpoints and subcases for content type, malformed JSON, trailing content, and empty body. Network list checks `/networks` and `/networks/`. Default/filter tests vary expected network names by OS. Scope test creates a swarm overlay network, verifies default inspect returns swarm scope and ID, then verifies local-scope inspect returns not found.

State/persistence: creates a temporary swarm daemon and overlay network in the scope test; other tests are mostly read-only HTTP/API calls.

Dependencies/integration: `internal/testutil/request`, Docker API client, network API types, swarm helper, `cerrdefs.IsNotFound`, and package harness. Some tests are platform-sensitive through `testEnv.DaemonInfo.OSType`.

Risks: exact HTTP error text for JSON parsing/content type is asserted and can change with API decoder behavior. Empty-body assertion only guards against 5xx, not exact client error. Scope behavior depends on swarm overlay creation.

Test signals: passing tests show network endpoints reject bad request bodies predictably, list endpoints are backward-compatible with trailing slash, default networks exist, name filters work, and scope selection disambiguates swarm vs local network inspect.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/network_test.go -->
