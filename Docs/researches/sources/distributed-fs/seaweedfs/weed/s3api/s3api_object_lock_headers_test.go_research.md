# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_lock_headers_test.go

## Purpose

This test file covers S3 Object Lock header extraction, response-header rendering, request validation, error-code mapping, and documented PUT permission rules. It protects the integration between HTTP headers and `filer_pb.Entry.Extended` metadata used by object retention and legal hold enforcement.

## Important APIs, Types, and Functions

The tests exercise `extractObjectLockMetadataFromRequest`, `addObjectLockHeadersToResponse`, `validateObjectLockHeaders`, and `mapValidationErrorToS3Error`. They assert use of `s3_constants.AmzObjectLockMode`, `AmzObjectLockRetainUntilDate`, `AmzObjectLockLegalHold`, and the internal extended keys for object lock mode, retention-until timestamp, and legal hold.

## Control Flow

Request-side tests build PUT requests with Object Lock headers, call the extractor, and check `Entry.Extended`. Response-side tests translate extended metadata back into HTTP headers, including RFC3339 retention formatting and default legal hold. Validation tests cover versioning requirements, mode/date pairing, future dates, bypass headers, and S3 error-code mapping.

## State and Persistence Behavior

The test state is in-memory `httptest` requests, recorders, and `filer_pb.Entry` values. The persistent contract being tested is serialization of object lock state into extended metadata for later enforcement and HEAD/GET response headers.

## Dependencies and Integration Points

The tests depend on `filer_pb.Entry`, `s3_constants`, `s3err`, `httptest`, `time`, `strconv`, and `testify/assert`. They integrate with PUT, HEAD, GET, and object-lock handler helpers.

## Risks and Edge Cases

Risks covered include partial extraction on invalid retention dates, invalid legal hold persistence, missing legal-hold response defaults, object-lock headers on non-versioned buckets, past retention dates, mode/date mismatch, and incorrect S3 error mapping.

## Test Signals

Strong test signals are the round-trip tests, validation matrix, and response-header nil/invalid metadata cases. Remaining gaps are real filer/IAM governance-bypass integration tests.
