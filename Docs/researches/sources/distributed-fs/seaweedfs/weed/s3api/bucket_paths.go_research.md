# sources/distributed-fs/seaweedfs/weed/s3api/bucket_paths.go

Purpose: centralizes bucket path calculation, existence lookup, and table-bucket object path validation.

Important APIs: `isTableBucket`, `bucketRoot`, `bucketDir`, `validateTableBucketObjectPath`, `bucketPrefix`, `bucketExists`, and `getBucketEntry`.

Control flow: `isTableBucket` checks registry cache, then filer entry, refreshing metadata when possible. Non-not-found lookup errors are logged and treated as non-table. Table-bucket validation trims leading slash, rejects empty keys, validates full path via `s3tables`, and requires at least four object path segments.

State and persistence: no writes; it reads filer entries and may warm bucket registry metadata.

Dependencies and integration points: uses `S3ApiServer.option.BucketsPath`, `getEntry`, bucket registry, glog, `filer_pb.ErrNotFound`, and `s3tables.IcebergLayoutError`.

Risks: transient lookup errors can bypass table-bucket validation by returning false. Layout assumptions must remain aligned with the `s3tables` validator.
