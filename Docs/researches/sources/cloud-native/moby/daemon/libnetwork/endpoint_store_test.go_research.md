# Research: sources/cloud-native/moby/daemon/libnetwork/endpoint_store_test.go

Purpose: tests controller endpoint store/cache synchronization. Important test is `TestEndpointStore`.

Control flow: the test creates a controller with a temp data directory, stores two endpoints belonging to a synthetic network, finds endpoints by network ID, sorts them for deterministic assertions, deletes one endpoint, confirms only the second remains, and stores the second again. It asserts that found endpoints are the same pointers, not copies.

State/dependencies: the test exercises real controller datastore plumbing via `New`, `storeEndpoint`, `findEndpoints`, and `deleteStoredEndpoint`, plus in-memory cache behavior. Dependencies include `config.OptionDataDir`, slices sorting, and `gotest.tools` comparisons. Risks covered include cache deletion and idempotent-ish re-store of an existing endpoint. Gaps include datastore failure paths, concurrent access, and filter behavior with nil networks.
