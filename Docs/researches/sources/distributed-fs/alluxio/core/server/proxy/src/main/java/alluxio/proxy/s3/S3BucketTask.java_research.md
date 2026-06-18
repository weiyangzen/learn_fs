# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3BucketTask.java

`S3BucketTask` implements servlet-v2 bucket operations. The factory dispatches GET/PUT/POST/HEAD/DELETE plus query parameters to list buckets, bucket tags, multipart upload listing, object listing, bucket creation, bulk delete, head, tag deletion, and bucket deletion.

Bucket state maps to Alluxio directories. Owners are set after creation. Bucket tags are stored in xattrs under `S3Constants.TAGGING_XATTR_KEY`. Delete honors `PROXY_S3_DELETE_TYPE`. `S3Handler.BUCKET_PATH_CACHE` caches known bucket directory paths and is updated by list/create/delete flows.

Dependencies include `S3RestUtils`, Alluxio `FileSystem` and option builders, Jackson XML DTO parsing, `ListBucketResult`, `ListMultipartUploadsResult`, and `DeleteObjectsResult`. Risks and tests: only `/` delimiters are supported; invalid `max-keys` parsing can throw unchecked exceptions; bulk delete treats missing keys/non-empty directories as success; bucket naming restrictions, malformed tagging XML, xattr replacement/deletion, ownership filtering, and cache invalidation need coverage.
