# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3Constants.java

`S3Constants` centralizes S3 proxy constants: bucket separator, HTTP and `x-amz-*` headers, signing parameter names, xattr keys, metadata directories, UTF-8 charsets, UTC date formatters, storage class, multipart part prefix, and the `Directive` enum for `COPY`/`REPLACE`.

The class is stateless and non-instantiable, but its values define persisted metadata contracts. Xattr keys such as `s3_content_type`, `s3_etag`, `s3_tags`, and multipart upload keys are stored on Alluxio files/directories, while `.alluxio_s3_api_metadata/uploads` defines hidden multipart metadata location.

Tests should treat these as compatibility constants across put/get/copy/tagging/multipart/auth paths. Changing xattr names, metadata directories, charsets, or header names can break existing stored objects or client behavior.
