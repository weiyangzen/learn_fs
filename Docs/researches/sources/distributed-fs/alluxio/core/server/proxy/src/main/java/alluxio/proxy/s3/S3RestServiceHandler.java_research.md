# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RestServiceHandler.java

`S3RestServiceHandler` is the older JAX-RS implementation of the Alluxio S3 API. It exposes annotated methods for bucket listing/head/get/post/put/delete and object put/post/head/get/delete flows, covering tagging, copy, range reads, multipart initiation/list/upload/abort, and bulk delete.

The constructor initializes `FileSystem`, configuration, audit writer, bucket naming patterns, rate limiter, and multipart metadata directory. Bucket state maps to Alluxio directories. Object state maps to files or convenience directories. ETags, content type, tags, and multipart metadata are stored as xattrs. A static bucket path cache mirrors the servlet-v2 handler.

The large `createObjectOrUploadPart` method multiplexes PutObject, PutObjectTagging, CopyObject, UploadPart, and UploadPartCopy. GET delegates to list parts, get object tags, unsupported ACL, or object streaming. Object streaming uses `S3RangeSpec`, positioned reads for small ranges, `RangeFileInStream`, optional `RateLimitInputStream`, ETag/content-type/tag-count headers, and XML DTOs for metadata operations.

Dependencies include JAX-RS annotations, servlet context, Alluxio client/gRPC options, `S3AuthenticationFilter` user headers, Jackson XML, Guava utilities, `S3RestUtils`, `MultipartUploadCleaner`, and result DTOs. Tests should cover unsupported ACL/policy/location branches, parameter exclusivity, bucket naming, delimiter restrictions, copy directives, MD5 mismatch cleanup, range behavior, multipart upload lifecycle pieces, tag xattrs, cache invalidation, and drift versus servlet-v2 task behavior.
