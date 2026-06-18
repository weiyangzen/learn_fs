# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSServiceIOException.java

Purpose: base IOException wrapper for AWS `AwsServiceException` with direct accessors for service metadata.

Important APIs/types: extends `AWSClientIOException`; narrows `getCause()` to `AwsServiceException`; exposes `requestId()`, `awsErrorDetails()`, `statusCode()`, and `extendedRequestId()`.

Control flow: constructed by S3A translation for service-side responses; subclasses specialize status classes such as throttling, bad request, redirects, and unsupported features.

State and persistence behavior: immutable operation and wrapped service exception.

Dependencies and integration points: bridges AWS SDK v2 service exceptions to Hadoop public IO exception behavior. Consumers can log or branch on HTTP status and AWS request IDs without unpacking the cause.

Risks: methods delegate directly to the cause; malformed or third-party SDK exceptions with missing details can return null details.

Test signals: wrapper tests should verify metadata delegation and compatibility with the `AWSClientIOException` message and retryable behavior.
