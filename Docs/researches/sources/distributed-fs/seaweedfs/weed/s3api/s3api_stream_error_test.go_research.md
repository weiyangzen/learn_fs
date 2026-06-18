<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_stream_error_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_stream_error_test.go

Purpose: tests the decision logic for whether streaming read errors should be written as error responses after a stream failure.

Important APIs/functions: `TestShouldWriteStreamingErrorResponse` covers `shouldWriteStreamingErrorResponse` with nil errors, raw and wrapped `context.Canceled`, gRPC canceled status, and deadline exceeded.

Control flow: table-driven cases pass errors through the helper and assert the boolean. Canceled client connections are expected to suppress error writes; deadline exceeded remains reportable.

State and persistence behavior: no state. It models error classification for streaming handlers that may already have begun sending data.

Dependencies and integration: uses `StreamError`, context package, and gRPC status/codes. It protects object GET streaming behavior and noisy logging/client-disconnect response handling.

Risks: only cancellation and deadline cases are covered; other transport errors, EOFs, and wrapped multi-error chains may need additional classification tests. The behavior depends on how `StreamError` exposes/unpacks its wrapped error.

Test signals: passing tests indicate client-initiated cancellation should not trigger an additional S3 error response, while server-side timeout/deadline should.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_stream_error_test.go -->
