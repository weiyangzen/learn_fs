# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/TestIAMInstanceCredentialsProvider.java

## Purpose

`TestIAMInstanceCredentialsProvider.java` unit-tests S3A's IAM/container instance credentials provider without requiring the test host to be EC2 or a container.

## Important APIs, Types, and Functions

The class uses `IAMInstanceCredentialsProvider`, `AwsCredentials`, and `NoAwsCredentialsException`. It defines expected disabled-IMDS text and tests provider close and credential resolution.

## Control Flow

The close test constructs and closes the provider. The instantiation test tries `resolveCredentials()`: if credentials are available, it asserts a nonblank access key and repeats resolution; if not, it verifies fallback state and that the cause is either an `IOException` or an IMDS-disabled message.

## State and Persistence Behavior

Provider state is external-environment dependent: it may select container or EC2 metadata providers. No credentials are persisted by the test.

## Dependencies and Integration Points

This covers S3A's wrapper around AWS SDK metadata credential providers and environment/system-property handling for disabled IMDS resolution.

## Risks and Edge Cases

Outcome varies by host. The test intentionally accepts both in-EC2/container success and non-EC2 failure paths while still checking provider fallback semantics.

## Test Signals

Signals are successful close, nonblank access key when credentials exist, provider not using container provider on generic failure, and acceptable exception cause classification.
