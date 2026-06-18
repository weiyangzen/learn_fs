# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/logging/RequestLoggingFilter.java

Purpose: `RequestLoggingFilter` is a Jersey `ContainerRequestFilter` for S3 proxy debugging. It logs method, URI, authorization header, media type, query parameters, path parameters, and, at debug level, all headers.

Important API: `filter(ContainerRequestContext)` builds a request string when info logging is enabled. It casts the context to Jersey's `ContainerRequest` to obtain the request URI, then chooses `LOG.debug` with full headers if debug is enabled, otherwise `LOG.info` with the shorter message. The filter is annotated with `@Provider`, `@PreMatching`, and `@Logged`.

State and persistence are absent except logs. Dependencies include Jersey server request classes, JAX-RS filter APIs, and SLF4J. Integration comes from proxy Jersey package registration in `ProxyWebServer`. Risks include logging the raw `Authorization` header and all headers in debug mode, which may expose credentials/signatures; the cast to `ContainerRequest` assumes Jersey's implementation; and high request volume can produce large logs. Test signals are absent in this subset.
