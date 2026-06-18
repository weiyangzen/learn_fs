# sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3AUnderFileSystemFactory.java

## Purpose
This factory registers S3 and S3A URI support with Alluxio.

## Important APIs, Types, And Functions
It implements `UnderFileSystemFactory`. `create` checks for non-null path and constructs `S3AUnderFileSystem`. `supportsPath` accepts `Constants.HEADER_S3A` and `Constants.HEADER_S3`, but not `s3n://`.

## Control Flow
Creation wraps any construction exception into an `IllegalArgumentException` with path context. Support checks are prefix-based and null-safe.

## State And Persistence
The factory is stateless.

## Dependencies And Integration Points
It integrates with `UnderFileSystemFactoryRegistry` and delegates to `S3AUnderFileSystem.createInstance`.

## Risks
Prefix-based matching is simple and can accept malformed URI strings with the right prefix. Creation builds real clients, so tests using default config may trigger environment-dependent credential/provider behavior if not isolated.

## Test Signals
`S3AUnderFileSystemFactoryTest` verifies registry lookup for `s3a://` and `s3://`, rejection of `s3n://`, null path error, create success, and supports-path negatives.
