# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/MultipartUtils.java

Purpose: utility for listing outstanding S3 multipart uploads as Hadoop `RemoteIterator<MultipartUpload>` instances.

Important APIs/types: final utility class with package-private `listMultipartUploads(StoreContext, S3Client, String, int)`. Nested `ListingIterator` pages `ListMultipartUploadsResponse`; nested public `UploadIterator` flattens each response into individual `MultipartUpload` values.

Control flow: `ListingIterator` captures request factory, invoker, audit span, prefix, max keys, and immediately requests the first batch. `hasNext()` is true for the first listing or while the last response is truncated. `next()` returns the first batch or sends continuation markers for later batches. `UploadIterator` initializes a lister and current batch, then `hasNext()` returns local batch items or requests more batches until exhausted.

State and persistence behavior: transient pagination state includes current listing response, first-listing flag, list count, key/upload ID markers, and batch iterator. No uploads are modified; this only lists state stored in S3.

Dependencies and integration points: depends on AWS SDK `S3Client` multipart upload models, S3A `StoreContext`, `RequestFactory`, `Invoker`, audit spans, operation-duration statistics, and `OBJECT_MULTIPART_UPLOAD_LIST` metric.

Risks: constructor performs remote I/O, so creating the iterator can fail. Listing uses the audit span active at iterator construction for all later calls. Max-key selection affects API load and latency.

Test signals: tests should cover empty listings, truncated listings with key/upload continuation markers, prefix filtering, audit span activation, retry translation, and flattening from responses to individual upload entries.
