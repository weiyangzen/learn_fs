# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AExceptionTranslation.java

## Purpose

Unit suite for translating AWS SDK, S3 service, credential, audit, timeout, and HTTP channel exceptions into Hadoop/S3A exception classes, and for verifying retry policy decisions on translated channel/timeouts.

## Important APIs, Types, and Functions

It exercises `S3AUtils.translateException()`, `extractException()`, `containsInterruptedException()`, `AWSCredentialProviderList.maybeTranslateCredentialException()`, `AuditIntegration.maybeTranslateAuditException()`, `ErrorTranslation.maybeExtractChannelException()`, and `S3ARetryPolicy.shouldRetry()`.

## Control Flow

Tests map HTTP statuses: 301 with bucket-region header to `AWSRedirectException`, 400 to bad request, 401/403 to access denied, 404/410 to not found, NoSuchBucket to `UnknownStoreException`, 416 to `RangeNotSatisfiableEOFException`, generic S3/service/client errors to S3A IO wrappers, and 504/API call timeouts to `AWSApiCallTimeoutException`. Additional tests unwrap interrupted exceptions, translate nested credential/audit failures, extract shaded and unshaded no-response channel errors, recognize OpenSSL stream-closed text, and map S3 Express precondition failure to `RemoteFileChangedException`.

## State, Dependencies, and Integration Points

State is limited to a retry policy initialized per test and synthetic AWS SDK exception objects. It integrates AWS SDK v2 error details and HTTP response headers, S3A audit and credential layers, shaded/unshaded Apache HTTP exceptions, and Hadoop IO/retry contracts.

## Risks and Test Signals

The suite is sensitive to exact AWS SDK exception hierarchies, error-code strings, and message content. Strong signals include translated class, preserved status code, region text in redirect messages, unwrapped causes for credential/audit errors, and retry decisions for timeout/channel EOF exceptions.
