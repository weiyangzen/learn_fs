# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_lifecycle_response_test.go

Purpose: Tests lifecycle handler responses for stored lifecycle XML and request body error mapping.

Important APIs/types/functions: `TestGetBucketLifecycleConfigurationHandlerUsesStoredLifecycleConfig`, `TestGetBucketLifecycleConfigurationHandlerDefaultsTransitionMinimumObjectSize`, `TestPutBucketLifecycleConfigurationHandlerRejectsOversizedBody`, `TestPutBucketLifecycleConfigurationHandlerMapsReadErrorsToInvalidRequest`, and `failingReadCloser`.

Control flow: GET tests seed bucket config cache with lifecycle extended attributes and call the GET handler, asserting 200, exact XML body preservation, and transition-minimum header value/default. PUT tests call the handler with an oversized body and a failing body reader, asserting `EntityTooLarge` and `InvalidRequest` respectively.

State and persistence: tests avoid filer I/O by using cache entries. PUT tests stop before persistence due to request-body failures.

Dependencies and integration: uses mux URL vars, `httptest`, in-memory IAM test server, bucket config cache, and S3 error registry. It guards lifecycle storage contract in extended attributes.

Risks: does not test successful lifecycle PUT/DELETE persistence, transition-rule rejection, legacy filer.conf cleanup, or cache invalidation after storing/clearing.

Test signals: strong coverage for AWS response shape of stored lifecycle config and for body-size/read error mapping.
