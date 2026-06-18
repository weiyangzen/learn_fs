# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3ObjectTask.java

`S3ObjectTask` implements servlet-v2 object operations: get/head/put/copy/delete, object tagging, multipart initiation/list/upload/copy/complete/abort, plus shared creation/copy helpers. The factory routes by verb, query parameters, and copy headers.

PUT writes normal or AWS-chunked bodies to Alluxio, computes MD5, validates `Content-MD5`, persists ETag xattrs, and stores content type/tags as xattrs. GET resolves `Range`, uses positioned reads for small ranges, otherwise `RangeFileInStream`, and can wrap streams with `RateLimitInputStream`. Copy and upload-part-copy reuse range-limited reads and propagate metadata/tagging according to directives.

Multipart state uses temporary part directories plus metadata files under S3 metadata storage. Completion validates requested parts, merges part files into a temp object, stores ETag and upload id xattrs, renames with S3 overwrite semantics, and deletes part/metadata state. It has an async keepalive path for long-running completion.

High-value tests: route matrix, range GET, copy ranges, MD5 mismatch cleanup, chunked encoding, tag/content-type xattrs, self-copy rejection, upload ID validation, minimum multipart part size, idempotent complete retry, temp cleanup, and async keepalive. Risks include extra uploaded parts being merged because validation returns the full uploaded part list, and missing uploadId precondition checking the wrong variable.
