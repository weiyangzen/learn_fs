# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestCustomSigner.java

## Purpose

`ITestCustomSigner.java` integration-tests the legacy/custom S3 signer SPI with AWS SDK v2, including signer initialization, per-UGI store registration, request signing, and cleanup for both bulk-delete and simple-delete modes.

## Important APIs, Types, and Functions

The parameterized class configures `CUSTOM_SIGNERS` and `SIGNING_ALGORITHM_S3`. Nested `CustomSigner` extends `AbstractAwsS3V4Signer`, implements `Signer` and `Configurable`, tracks instantiation/invocation counts, delegates S3 requests to `AwsS3V4Signer`, and delegates KMS requests to `Aws4Signer`. Nested `CustomSignerInitializer` implements `AwsSignerInitializer` and tracks registered stores by bucket and `UserGroupInformation`.

## Control Flow

Each parameterized run opens two filesystems under different UGIs with different test identifiers, performs mkdir/list/touch/delete and optional magic-commit operations, and verifies signer invocation, configuration injection, and initializer store lookup. Closing each filesystem must unregister its store.

## State and Persistence Behavior

Static counters and store maps persist within the class and are reset in setup. Real S3 paths are created. Filesystems are closed per UGI in teardown to release cached state.

## Dependencies and Integration Points

This covers S3A custom signer registration, signer initializer lifecycle, UGI isolation, path-style bucket handling, AWS SDK v2 signer delegation, checksum configuration, magic committer behavior, and multi-delete toggling.

## Risks and Edge Cases

Bucket parsing differs for path-style access and KMS endpoints. Checksum headers can break custom signing, so checksum algorithms and validation are disabled. Store registration must be exact to avoid leaking UGI/bucket mappings.

## Test Signals

Signals are increased signer instantiation/invocation counts, captured store value/config identifier, `CustomSigner.getLastConfiguration()` identity, store-map size transitions from 2 to 1 to 0, and successful filesystem operations.
