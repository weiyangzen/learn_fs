# sources/distributed-fs/seaweedfs/weed/s3api/copy_source_decode_test.go

Purpose: regression tests for `X-Amz-Copy-Source` parsing, special-character decoding, same-source/destination detection, and traversal rejection.

Important tests: `TestCopySourceWithExclamationMark`, `TestCopySourceDecodingPlusSign`, `TestCopySourceRejectsTraversal`, and `TestCopySourceRoutingWithSpecialChars`.

Control flow: copy source decoding must use `url.PathUnescape`, preserving literal `+`. Encoded/unencoded `!`, encoded slashes, lowercase `%2f`, and version IDs should parse consistently. Traversal validation rejects dot/dot-dot segments after decoding, including encoded slash, backslash, dot-dot bucket, and traversal in versionId.

State and persistence: in-memory request/router simulations only.

Dependencies and integration points: `pathToBucketObjectAndVersion`, `validateCopySource`, `s3_constants.GetBucketAndObject`, and Gorilla mux with `SkipClean(true)`.

Risks and test signals: protects object-key correctness and path traversal security. It does not execute actual filer copy operations.
