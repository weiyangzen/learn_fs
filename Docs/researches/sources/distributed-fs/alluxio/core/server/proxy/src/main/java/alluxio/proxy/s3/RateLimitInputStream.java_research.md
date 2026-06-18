# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/RateLimitInputStream.java

`RateLimitInputStream` wraps an `InputStream` and applies one or more Guava `RateLimiter`s before read operations. `read()` acquires one permit; `read(byte[], int, int)` acquires permits for the requested byte count and then delegates; null limiters are ignored. It is used by object GET paths when global or single-connection S3 read limits are configured.

The class has no persistence and holds only the wrapped stream plus limiter references. Shared limiter state may come from servlet context, while per-request limiters are created from `PROXY_S3_SINGLE_CONNECTION_READ_RATE_LIMIT_MB`.

Risk signals: permits are acquired before the actual read, so EOF and short reads can over-consume rate capacity. Tests should cover single-byte and bulk reads, null limiter handling, close propagation, EOF, and short-read behavior.
