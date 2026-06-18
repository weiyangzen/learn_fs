# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/S3ATestConstants.java

## Purpose

Central interface of test-only configuration keys, defaults, timeouts, scale-test controls, and feature flags used across Hadoop S3A tests.

## Important APIs, Types, and Functions

Constants cover test filesystem naming (`test.fs.s3a.name`), feature gates for encryption, storage class, ACL, list-v1, content encoding, performance, scale tests, STS/session settings, requester-pays/public data inputs, huge-file sizes, root tests, multipart compatibility, and analytics accelerator settings. It also defines default operation counts, directory/file counts, read buffer size, session duration, timeouts, and common regions.

## Control Flow

There is no executable control flow. Consumers read keys from `Configuration` and system properties through utilities such as `S3ATestUtils.getTestProperty*()` and use defaults when not explicitly enabled.

## State, Dependencies, and Integration Points

The interface has no runtime state, but it encodes cross-suite configuration contracts. It depends on `PublicDatasetTestUtils` for deprecated public dataset defaults and `Duration` for test session duration.

## Risks and Test Signals

Changing names or defaults can silently skip or enable expensive/live tests. Deprecated constants remain to ease cherry-picks and compatibility. These constants are also risk points for third-party store test behavior, especially root tests, MPU semantics, and analytics accelerator tuning.
