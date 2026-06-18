# sources/distributed-fs/seaweedfs/weed/s3api/s3err/error_handler_test.go

Purpose: regression test for request-id consistency in S3 error responses.

Important APIs/types: `TestWriteErrorResponseReusesRequestID` calls `WriteErrorResponse`; `extractRequestIDFromBody` extracts `<RequestId>`.

Control flow: the test creates a mux-var request with `request_id.Set`, writes `ErrNoSuchKey`, and asserts the response header and XML body use `req-123`.

State and persistence behavior: none, except `WriteErrorResponse` will call `PostLog`; with nil logger this only affects request context if tracking is present.

Dependencies and integration points: tests Gorilla mux vars and SeaweedFS request-id context integration.

Risks: coverage is narrow. It does not verify status code, content type, CORS, flush behavior, custom message override, or audit flag behavior.

Test signals: important because S3 clients depend on request IDs for support/debugging, and mismatch between header/body would break traceability.
