# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/SimpleAWSCredentialsProvider.java

## Purpose
`SimpleAWSCredentialsProvider` supplies AWS basic credentials from Hadoop S3A configuration or credential providers.

## Important APIs, Types, and Functions
Public API includes constant `NAME`, constructor `(URI, Configuration)`, package-visible test constructor from `S3xLoginHelper.Login`, `resolveCredentials()`, and `toString()`.

## Control Flow and State
Construction calls `S3AUtils.getAWSAccessKeys()` and stores access/secret strings. `resolveCredentials()` returns `AwsBasicCredentials` only when both strings are non-empty; otherwise it raises `NoAwsCredentialsException`. `toString()` reports only emptiness flags, not secrets.

## State and Persistence Behavior
The provider keeps credentials in memory as strings for its lifetime and does not refresh them. It persists no data externally.

## Dependencies and Integration Points
Dependencies include AWS SDK credentials types, Hadoop `Configuration`, `S3AUtils`, `S3xLoginHelper`, Apache `StringUtils`, and `NoAwsCredentialsException`. It is referenced by configured credential provider chains and must keep its class name stable.

## Risks and Test Signals
Risks include long-lived string secrets, no refresh support, empty access/secret handling, and compatibility breakage if constructors/class name change. Tests should verify config/JCEKS lookup, missing credential exception behavior, no secret leakage in `toString()`, and provider-chain instantiation.
