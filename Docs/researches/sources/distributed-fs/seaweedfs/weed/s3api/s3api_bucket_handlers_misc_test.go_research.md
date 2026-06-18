# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_handlers_misc_test.go

Purpose: Unit-tests miscellaneous bucket helpers and compatibility handlers.

Important APIs/types/functions: `newMiscTestServer`, `newBucketRequest`, `TestHasExplicitBucketACL`, `TestGetBucketPolicyStatusIsPublic`, `TestPutBucketRequestPaymentBucketOwner`, `TestPutBucketRequestPaymentRequesterRejected`, `TestPutBucketOwnershipControlsRejectsRuleWithoutObjectOwnership`, `TestGetBucketAccelerateConfiguration`, and `TestGetBucketLogging`.

Control flow: tests construct cached bucket configs to avoid filer I/O, then call handlers with mux bucket vars. Assertions cover status codes and key XML/error snippets.

State and persistence: test state is in-memory only. The ownership-controls negative test uses bucket registry metadata with owner account data to reach validation before persistence.

Dependencies and integration: uses AWS S3 grant/policy types, `policy_engine`, `s3_constants`, `gorilla/mux`, and `httptest`. It protects compatibility response formats and helper classification behavior.

Risks: does not cover missing buckets, IAM denial, successful ownership-control persistence, request-payment oversized body behavior, or policy status handler response end-to-end. XML assertions are substring-based.

Test signals: good focused regression coverage for utility behavior that SDK compatibility depends on.
