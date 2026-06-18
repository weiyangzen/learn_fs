# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSStatus500Exception.java

Purpose: typed service IOException for HTTP 5xx server-side failures.

Important APIs/types: extends `AWSServiceIOException` with only an operation/cause constructor. Class comments document that 500s are considered retryable by the AWS SDK and conditionally retried in S3A based on `fs.s3a.retry.http.5xx.errors`.

Control flow: created during exception translation after SDK retries are exhausted. Actual retry decisions are external in S3A retry policy.

State and persistence behavior: standard wrapped exception state only.

Dependencies and integration points: integrates with S3A retry configuration and server-error handling for AWS and third-party object stores.

Risks: third-party stores may use 5xx for permanent configuration failures; repeated retries can increase load and latency.

Test signals: retry-policy tests should cover behavior with HTTP 5xx retry enabled and disabled.
