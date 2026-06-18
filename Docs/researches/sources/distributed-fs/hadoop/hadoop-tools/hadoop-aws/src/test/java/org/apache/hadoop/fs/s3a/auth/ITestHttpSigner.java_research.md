# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestHttpSigner.java

## Purpose

`ITestHttpSigner.java` integration-tests the newer HTTP signer SPI by enabling a custom HTTP signer class and running normal S3A operations under two different UGIs.

## Important APIs, Types, and Functions

The class configures `HTTP_SIGNER_ENABLED`, `HTTP_SIGNER_CLASS_NAME`, and removes custom S3 signer overrides. It uses `CustomHttpSigner`, `UserGroupInformation.doAs()`, `disableFilesystemCaching()`, and standard S3A file operations.

## Control Flow

Setup determines endpoint and region from the active filesystem. The test creates separate configurations for two identifiers, opens a filesystem under each UGI, creates directories/files, lists status, deletes and recreates files, and optionally exercises magic-commit cleanup/rename/delete paths.

## State and Persistence Behavior

Each test creates real S3 paths and two UGI-scoped filesystems. Teardown closes all filesystems for both UGIs.

## Dependencies and Integration Points

This covers S3A HTTP signer plugin loading, region propagation, UGI-specific filesystem instances, and interaction with normal filesystem and magic committer operations.

## Risks and Edge Cases

The class validates operation success rather than inspecting signer internals, so it primarily detects gross signer wiring failures. Region discovery can make a real S3 call.

## Test Signals

Signals are successful filesystem creation and S3 operations under both UGIs with the custom HTTP signer enabled and no filesystem caching.
