# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/web/ProxyWebServer.java

Purpose: `ProxyWebServer` wires the Alluxio proxy HTTP server, including S3 REST/Jersey or S3 servlet v2 routing, servlet context resources, audit logging, global S3 read rate limiting, and access logging.

Important APIs/types include constructor setup, nested `ProxyListener`, `createLightThreadPool`, `createHeavyThreadPool`, `stop`, and static `logAccess`. Control flow builds a Jersey `ResourceConfig` for `alluxio.proxy`, `alluxio.proxy.s3`, and logging packages, creates a shared `FileSystem`, optionally creates a global Guava `RateLimiter`, starts an async audit log writer and metric gauge, then installs either the newer `S3RequestServlet` path when `PROXY_S3_V2_VERSION_ENABLED` is true or the Jersey servlet plus multipart upload handler otherwise. V2 mode also installs Jetty `HttpChannel.Listener` access logging and configured light/heavy thread pools.

State and persistence include servlet-context attributes for proxy process, file system, stream cache, audit writer, rate limiter, and v2 executor pools. It owns and closes the file system/audit writer in `stop`. Dependencies include Jetty, Jersey, Alluxio metrics/config, `S3Handler`, `S3RequestServlet`, `StreamCache`, and `CompleteMultipartUploadHandler`.

Integration points are every proxy REST/S3 request, audit logs, metrics, and S3 task execution pools. Risks include duplicated access logging in Jersey path, thread-pool rejection behavior controlled only by bounded queues, audit writer always running even if audit logging is disabled at runtime, and sensitive headers emitted in debug access logs. Tests in this subset exercise `StreamCache`, rate limiting, S3 range/auth utilities, not server startup directly.
