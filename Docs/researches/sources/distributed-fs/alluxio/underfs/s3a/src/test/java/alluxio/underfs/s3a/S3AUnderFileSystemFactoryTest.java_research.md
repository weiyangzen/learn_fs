# sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3AUnderFileSystemFactoryTest.java

## Purpose
This test verifies S3A factory registration, URI support, and basic creation.

## Important APIs, Types, And Functions
Tests cover registry lookup for `s3a://`, `s3://`, and `s3n://`, `create` with null path, `create` with a valid path, and `supportsPath`.

## Control Flow
The registry should find a factory for S3A/S3 but not S3N. Null creation should throw a helpful `NullPointerException` wrapped in the factory error message. Valid creation should produce `S3AUnderFileSystem`.

## State And Persistence
Only global configuration and a default UFS configuration are used.

## Dependencies And Integration Points
It exercises Alluxio factory registry service loading and `S3AUnderFileSystemFactory`.

## Risks
Create success may rely on client construction not contacting AWS immediately. It does not validate credentials or endpoint behavior.

## Test Signals
Passing tests confirm that S3/S3A schemes are routed to this module and unsupported schemes are rejected.
