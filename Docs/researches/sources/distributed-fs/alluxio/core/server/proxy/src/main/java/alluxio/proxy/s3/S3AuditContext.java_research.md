# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3AuditContext.java

`S3AuditContext` implements Alluxio `AuditContext` for S3 requests. It records allowed/succeeded flags, command, user/group string, client IP, bucket, object, creation time, and execution time. Fluent setters populate fields, and `close()` computes elapsed time and appends the context to `AsyncUserAccessAuditLogWriter` when audit logging is enabled.

The object is request-local. Persistence is delegated to the async audit writer, which consumes the tab-separated `toString()` representation. When no writer is provided, `close()` is a no-op.

Integration points are `S3Handler.createAuditContext`, `S3RestServiceHandler.createAuditContext`, and bucket/object tasks that mark failed or denied operations before exception translation. Tests should verify disabled logging, append-on-close, elapsed time calculation, formatted fields, failure/denied mutations, and behavior when creation time is omitted.
