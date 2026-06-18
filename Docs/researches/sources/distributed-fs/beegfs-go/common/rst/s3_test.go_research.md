# sources/distributed-fs/beegfs-go/common/rst/s3_test.go

Purpose: provides focused unit coverage for S3 provider work-request generation and completion error classification without contacting a real S3 service.

Important fixtures include `testS3Client`, a partially initialized `S3Client` with policies, and tests `TestGenerateWorkRequests` and `TestCompleteRequests`.

Control flow: `TestGenerateWorkRequests` uses a mock filesystem, writes a small local file, sets `FastStartMaxSize` to avoid multipart upload, builds upload/download sync jobs with locked info, and verifies upload generation emits one request with the right operation. It also asserts mock job type mismatch, unsupported sync operation, and external-ID precondition errors. `TestCompleteRequests` verifies completion rejects non-sync jobs and unsupported sync operations.

State behavior under test includes local mock filesystem contents, job external IDs, `LockedInfo`, and generated work request fields. Real S3 state and network calls are deliberately avoided.

Dependencies are `testing`, `testify`, mock filesystem provider, BeeRemote/Flex protobufs, and timestamps.

Integration points are S3 `GenerateWorkRequests`, common `RecreateWorkRequests`, and provider error sentinels.

Risks: download generation, object metadata, archive restore, multipart upload, ranged IO, walking, and completion success paths are not tested because `S3Client.client` is concrete. The test comments explicitly call out the need for an S3 provider interface.

Test signals: adequate smoke coverage for supported/unsupported request classification.
