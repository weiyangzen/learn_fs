<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/NetworkBinding.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/NetworkBinding.java

## Purpose

`NetworkBinding` contains network-related S3A helpers for SSL channel binding, AWS endpoint recognition, bucket-region normalization, and DNS lookup logging.

## Important APIs, Types, and Functions

It exposes `bindSSLChannelMode(Configuration, ApacheHttpClient.Builder)`, `isAwsEndpoint(String)`, `fixBucketRegion(String)`, and `logDnsLookup(Configuration)`. It reflectively loads `ConfigureShadedAWSSocketFactory`.

## Control Flow

SSL binding reads the configured SSL channel mode and, when not default, creates an SSL socket factory and applies it to the AWS Apache HTTP builder through the reflected adapter. Endpoint recognition checks host suffixes for AWS patterns. Region normalization maps null/empty and legacy `US` to the expected region string. DNS logging emits resolver information when enabled.

## State and Persistence Behavior

The class is stateless. It mutates the supplied HTTP client builder when custom SSL mode is configured.

## Dependencies and Integration Points

It depends on Hadoop network/SSL utilities, AWS SDK Apache HTTP builder classes, S3A configuration constants, and the shaded socket factory adapter.

## Risks and Edge Cases

Reflective adapter loading can fail if shading or class names change. Endpoint suffix checks can misclassify nonstandard S3-compatible endpoints. Region normalization must preserve AWS SDK expectations.

## Test Signals

Test default and custom SSL modes, reflective adapter failure, AWS and non-AWS endpoint strings, null/empty/`US` region normalization, and DNS logging when enabled or disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/NetworkBinding.java -->
