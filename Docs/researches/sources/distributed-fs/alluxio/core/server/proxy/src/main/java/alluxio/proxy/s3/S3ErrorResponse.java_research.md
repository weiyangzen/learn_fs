# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3ErrorResponse.java

`S3ErrorResponse` translates exceptions into HTTP `Response` objects for S3 clients. The public dispatcher handles `AlluxioStatusException`, `AlluxioRuntimeException`, `S3Exception`, `IOException`, and generic throwables. S3 exceptions map directly through their embedded `S3ErrorCode`; Alluxio and IO exceptions are mapped to common S3 codes and XML messages.

The class is stateless and creates a fresh `XmlMapper` per response. It logs type-to-status mappings for non-S3 conversions. It integrates with auth filtering, Jersey exception mapping, servlet handler creation failures, and stream-copy exception handling.

Risks: generic exceptions return plain text rather than XML, and many storage failures collapse to `InternalError`. Tests should cover each dispatch branch, XML serialization failure fallback, message overrides, resource propagation, and behavior when response streaming has already started.
