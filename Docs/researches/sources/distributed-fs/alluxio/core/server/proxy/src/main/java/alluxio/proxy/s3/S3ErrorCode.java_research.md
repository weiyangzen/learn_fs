# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3ErrorCode.java

`S3ErrorCode` binds S3 error code strings, default descriptions, and JAX-RS HTTP statuses. It defines common S3-compatible constants for bad digests, missing buckets/keys/uploads, invalid arguments/tags/XML, access denial, precondition failure, not implemented, and multipart part errors.

Instances are immutable and request-independent. `S3Exception` sometimes creates a derived `S3ErrorCode` with the same code/status but a custom message, making this class part of the client-visible response contract.

Tests should verify code/status mappings and exact strings for SDK compatibility. Custom cases such as `INVALID_NESTED_BUCKET_NAME` reusing the `BucketAlreadyExists` code with a bad-request status should be covered if nested bucket behavior is exercised.
