# sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/StreamCacheTest.java

Purpose: `StreamCacheTest` verifies the proxy stream cache used to hold open `FileInStream` and `FileOutStream` instances across REST calls.

Important tests are `operations`, `concurrentOperations`, `expiration`, and `size`. Control flow in `operations` adds mocked input/output streams, confirms typed retrieval rejects the wrong stream type, invalidates both streams, verifies repeated invalidation returns null, and verifies both streams are closed. `concurrentOperations` launches 200 threads performing put/get/invalidate cycles across input and output streams and expects final cache size 0. `expiration` uses a zero timeout and verifies streams are closed immediately. `size` checks size transitions.

State and persistence under test are in-memory stream IDs and cache invalidation/expiration side effects; there is no disk persistence. Dependencies include JUnit, Mockito, Alluxio stream classes, and `Constants.HOUR_MS`. Integration signal: `ProxyWebServer` injects a `StreamCache` into servlet context for proxy REST endpoints. Risks covered include type confusion, leaking streams, concurrency races, and expiry cleanup. Remaining gaps include no test for ID wraparound, exception thrown by close, or long-running scheduled eviction behavior beyond zero timeout.
