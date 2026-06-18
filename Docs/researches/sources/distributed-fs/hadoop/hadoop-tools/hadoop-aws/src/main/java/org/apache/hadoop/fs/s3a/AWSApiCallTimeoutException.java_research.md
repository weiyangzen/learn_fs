# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSApiCallTimeoutException.java

Purpose: IOException mapping for AWS SDK API call timeout failures. It subclasses Hadoop `ConnectTimeoutException` so existing timeout handlers can catch it.

Important APIs/types: constructor `AWSApiCallTimeoutException(String operation, Exception cause)` stores the operation as the exception message and initializes the cause.

Control flow: no retry logic here; construction occurs during exception translation elsewhere, then callers handle it as an `IOException`/connect timeout.

State and persistence behavior: immutable exception state after construction, except standard Throwable cause initialization.

Dependencies and integration points: depends on `org.apache.hadoop.net.ConnectTimeoutException` and integrates with S3A exception translation and retry policy code.

Risks: only the operation string is used as the top-level message, so detailed cause text is available through the cause rather than the message.

Test signals: translation tests should assert timeout exceptions retain the SDK cause and are catchable as `ConnectTimeoutException`.
