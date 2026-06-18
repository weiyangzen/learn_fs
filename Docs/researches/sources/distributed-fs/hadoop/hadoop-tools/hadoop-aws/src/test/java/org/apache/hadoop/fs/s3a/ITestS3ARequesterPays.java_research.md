# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ARequesterPays.java

Purpose: Tests requester-pays bucket support, ensuring S3A adds the requester-pays header when enabled and fails with access denied when disabled.

Important APIs/types/functions: `Constants.ALLOW_REQUESTER_PAYS`, `Constants.S3A_BUCKET_PROBE`, `PublicDatasetTestUtils.getRequesterPaysObject()`, `FSDataInputStream`, `IOStatisticAssertions`, `StreamStatisticNames.STREAM_READ_OPENED`, and `S3ATestUtils.streamType()`.

Control flow: configuration removes bucket overrides for the requester-pays bucket. Success test enables requester pays and bucket probe, opens the public requester-pays object, reads last then first byte to force one or more GET requests, checks stream-open counts according to classic vs prefetch stream, and lists the parent. Failure test disables requester pays and expects `AccessDeniedException` containing `403` when opening the object.

State and persistence: reads public requester-pays data; does not write. Uses a separate filesystem resolved from the requester-pays path.

Dependencies and integration points: public requester-pays dataset, S3A request header propagation to bucket probes, GETs, and list calls, and stream-type-specific request behavior.

Risks: public dataset or billing/config availability can change; stream-open counter expectations differ by stream type; client-side encryption is skipped for success path.

Test signals: validates requester-pays option reaches all needed S3 requests and that missing option fails clearly.
