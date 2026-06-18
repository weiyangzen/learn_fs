# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_collection_test.go

Purpose: regression-tests destination path selection for server-side copy volume assignment. It ensures copied bytes are assigned under the destination bucket's filer path so the filer maps them to the bucket collection instead of the default collection.

Important coverage is `TestCopyDestinationPathResolvesBucketCollection`, which exercises `S3ApiServer.bucketDir`, `copyPartLocation`, and `filer.Filer.DetectBucket` with a bucket root at `/buckets`.

Control flow first proves the S3 request URI shape (`/bucket/key`) does not resolve to a bucket collection. It then builds an UploadPartCopy part path under `.uploads` and a CopyObject destination object path under `/buckets/<bucket>/...`, asserting both resolve to the expected bucket.

State and persistence are in-memory path strings and a lightweight `filer.Filer` value. No filer RPCs or volume assignments are performed.

Dependencies include `filer.Filer`, `util.FullPath`, and the S3 API server bucket path option. The integration point is `assignNewVolume`, which receives `dstPath`; passing `r.URL.Path` here would silently place copied chunks into the wrong collection.

Risks: the test is path-level only and does not prove a real assign-volume RPC respects collection placement, but it pins the critical precondition used by filer collection detection.
