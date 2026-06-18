# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSBadRequestException.java

Purpose: typed S3A IOException for HTTP 400 Bad Request service responses.

Important APIs/types: extends `AWSServiceIOException`; exposes `STATUS_CODE` equal to `SC_400_BAD_REQUEST`; constructor accepts operation and `AwsServiceException`.

Control flow: no custom behavior beyond superclass wrapping. Retryability is inherited from the underlying SDK exception unless policy code treats the type specially.

State and persistence behavior: stores operation and AWS service exception through the superclass.

Dependencies and integration points: used by S3A exception translation for malformed requests, bad headers, and incompatible parameters.

Risks: third-party object stores may use 400 for multiple misconfiguration classes; callers should not assume all 400s have identical remedies.

Test signals: exception translation should map 400 responses to this type and preserve request IDs, status code, and AWS error details through `AWSServiceIOException`.
