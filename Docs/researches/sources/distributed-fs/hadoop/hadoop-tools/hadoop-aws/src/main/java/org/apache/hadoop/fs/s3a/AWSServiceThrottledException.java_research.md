# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSServiceThrottledException.java

Purpose: typed IOException for AWS service throttling.

Important APIs/types: extends `AWSServiceIOException`; declares `STATUS_CODE = 503`; overrides `retryable()` to `true`.

Control flow: exception translation maps throttle responses to this class. Retry policy and metrics can distinguish throttling from generic service failures.

State and persistence behavior: no mutable state beyond wrapped AWS cause.

Dependencies and integration points: used by S3A retry policy, statistics, and throttling diagnostics.

Risks: not every 503 is semantically throttling on third-party stores; treating all mapped instances as retryable may hide persistent misconfiguration.

Test signals: retry tests should assert retryable behavior and metrics tests should count translated throttle failures accurately.
