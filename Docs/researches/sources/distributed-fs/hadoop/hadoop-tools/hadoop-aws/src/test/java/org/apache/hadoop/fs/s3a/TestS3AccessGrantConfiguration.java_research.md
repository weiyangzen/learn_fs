# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AccessGrantConfiguration.java

## Purpose

`TestS3AccessGrantConfiguration.java` validates that S3 Access Grants configuration controls whether S3 clients are built with the Access Grants identity provider. It covers both synchronous and asynchronous S3 clients.

## Important APIs, Types, and Functions

The key constant is `S3_ACCESS_GRANTS_EXPECTED_CREDENTIAL_PROVIDER_CLASS`, bound to `S3AccessGrantsIdentityProvider`. `testS3AccessGrantsEnabled()` and `testS3AccessGrantsDisabled()` drive the behavior through `AWS_S3_ACCESS_GRANTS_ENABLED`. Helpers create a `DefaultS3ClientFactory`, build `S3ClientCreationParameters`, and inspect `AwsClient.serviceClientConfiguration().credentialsProvider()`.

## Control Flow

Each test builds a configuration, creates either an async or sync AWS client, reads the client's configured credentials provider class name, and asserts equality or inequality with the Access Grants provider depending on whether the feature is enabled.

## State and Persistence Behavior

The only durable state is `Configuration` key/value content. Client instances are transient and are not connected to a real bucket for these assertions.

## Dependencies and Integration Points

This tests S3A's `DefaultS3ClientFactory` integration with the AWS SDK Access Grants plugin and the `AWS_S3_ACCESS_GRANTS_ENABLED` option. It also protects parity between sync and async client creation paths.

## Risks and Edge Cases

The test only checks the top-level credentials provider class, not a full request. A future provider wrapper could make the class-name check too strict even if behavior remains correct.

## Test Signals

Signals are provider class equality when explicitly enabled and non-equality for default and explicit disabled configurations across both client types.
