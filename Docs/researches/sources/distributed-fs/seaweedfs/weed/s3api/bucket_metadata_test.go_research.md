# sources/distributed-fs/seaweedfs/weed/s3api/bucket_metadata_test.go

Purpose: tests bucket metadata construction and concurrent registry cache-miss behavior.

Important APIs/fixtures: `BucketMetadataTestCase`, filer entry fixtures for valid/invalid `Extended` metadata, `TestBuildBucketMetadata`, and `TestGetBucketMetadata`. The test overrides `loadBucketMetadataFromFiler`.

Control flow: table cases cover malformed entries, valid ACLs, empty/valid ownership, empty/unknown owners, and empty grants. Expected defaults use AccountAdmin owner and default object ownership. The concurrency test starts 40 goroutines repeatedly reading five bucket names while the fake loader sleeps, proving each bucket is loaded once.

State and persistence: in-memory only, but it mutates package-level loader and load-count globals.

Dependencies and integration points: exercises IAM config loading, `filer_pb.Entry`, AWS S3 grant/owner structs, S3 metadata constants, and `BucketRegistry.GetBucketMetadata`.

Risks and test signals: demonstrates lock effectiveness under concurrent cache misses. Because the loader override is global and not restored, parallel or later tests that rely on the default loader could be affected.
