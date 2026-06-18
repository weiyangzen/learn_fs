# Research: sources/cloud-native/nydus-snapshotter/pkg/index/manager_test.go

This test file exercises `Manager.CheckIndexAlternative` cache-hit behavior. It constructs a manager, inserts an OCI descriptor under a manifest digest, and verifies the call returns that descriptor without error. A second subtest inserts nil under the digest and verifies the manager returns an error containing `no alternative nydus descriptor found in index`.

The tests are small but important because the manager intentionally caches both positive and negative detection results. They protect the type assertion path for positive descriptors and the sentinel-style error path for cached misses. There is no registry, auth, singleflight contention, or metadata fetch in these tests.

Coverage gaps include detector invocation on cache miss, failure wrapping, cache eviction behavior, concurrent calls, and `TryFetchMetadata`. Persistent state is absent; the LRU is in-memory. The tests support filesystem behavior indirectly because `Filesystem.CheckIndexAlternative` relies on this cache to avoid repeated remote index scans.
