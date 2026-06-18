# sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/RateLimitInputStreamTest.java

Purpose: `RateLimitInputStreamTest` validates that S3 download throttling respects both per-stream and global `RateLimiter` limits while preserving bytes.

Important tests are `testSingleThreadRead`, `testMultiThreadReadWithBiggerGlobalRate`, and `testMultiThreadReadWithSmallerGlobalRate`. Setup creates a deterministic 1 MiB byte array from UUID bytes. Single-thread tests copy through `RateLimitInputStream` with two randomly chosen rates and assert elapsed time is at least `size / min(rate1, rate2)` and within one second over that estimate. Multi-thread tests share one global limiter across three streams and assert elapsed time follows `totalSize / min(globalRate, threadNum * perStreamRate)`.

State under test is in-memory stream read position and Guava limiter token consumption. Dependencies are Guava `RateLimiter`, Apache Commons IO, JUnit, executors, and byte streams. Integration signal: `ProxyWebServer` creates a global limiter and S3 handlers wrap reads with per-request/global limiters. Risks covered include global limiter sharing and byte corruption. Risks not fully covered include timing flakiness under overloaded CI, interruption behavior, close propagation, and reads smaller than the copy buffer.
