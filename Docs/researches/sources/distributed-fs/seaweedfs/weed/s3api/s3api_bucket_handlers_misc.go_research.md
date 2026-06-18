# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_handlers_misc.go

Purpose: Implements smaller bucket subresource handlers for policy status, request payment, acceleration, and logging.

Important APIs/types/functions: `putBucketRequestPaymentMaxBodyBytes`, `policyStatusResponse`, `accelerateConfigurationResponse`, `bucketLoggingStatusResponse`, `GetBucketPolicyStatusHandler`, `isPolicyPublic`, `PutBucketRequestPaymentHandler`, `GetBucketAccelerateConfigurationHandler`, and `GetBucketLoggingHandler`.

Control flow: all bucket-dependent handlers call `checkBucket`. Policy status loads the stored bucket policy and reports public when an unconditional `Allow` has `Principal="*"`. Request payment caps body size at 64 KiB, XML-decodes `RequestPaymentConfiguration`, accepts only `BucketOwner`, and rejects `Requester` as malformed. Acceleration returns static `Suspended`; logging returns empty `BucketLoggingStatus`.

State and persistence: no new persistent state is written. Policy status reads policy metadata through `getBucketPolicy`; request payment intentionally does not store requester-pays configuration because only bucket-owner mode is supported. Acceleration/logging are static compatibility responses.

Dependencies and integration: depends on policy engine document types, S3 constants/errors, XML helpers, and core bucket access checks. It fills compatibility gaps for SDKs expecting these subresources.

Risks: public policy detection is intentionally conservative and treats conditional public policies as non-public. Request payment error mapping uses `MalformedXML` for unsupported payer values, which may differ from some clients' expectations but is tested. Static acceleration/logging can hide unsupported feature state.

Test signals: `s3api_bucket_handlers_misc_test.go` exercises explicit ACL detection, policy public classification, request payment accept/reject, and static acceleration/logging XML responses.
