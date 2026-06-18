<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_test.go

Purpose: small smoke/documentation tests for XML encoding of copy responses.

Important APIs/functions: `TestCopyObjectResponse` creates `CopyObjectResult` and prints encoded XML; `TestCopyPartResponse` does the same for `CopyPartResult` using `s3err.EncodeXMLResponse`.

Control flow: tests instantiate result structs with an ETag and current time, encode, and print. They contain no assertions.

State and persistence behavior: no state beyond transient timestamps.

Dependencies and integration: depends on copy response types defined elsewhere in S3 API handlers and the S3 XML response encoder.

Risks: because there are no assertions, these tests are weak as regressions; they only fail on panic/build failure. `println` output can add noise but documents expected XML interactively.

Test signals: minimal smoke signal that copy result structs still marshal without panic. Stronger tests should assert XML element names, LastModified format, and ETag placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_test.go -->
