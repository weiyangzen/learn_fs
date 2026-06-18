# sources/distributed-fs/alluxio/underfs/s3a/pom.xml

## Purpose
This Maven descriptor builds the AWS S3A under file system module.

## Important APIs, Types, And Functions
The artifact is `alluxio-underfs-s3a`. Dependencies include AWS SDK v2 `s3` and `netty-nio-client`, AWS SDK v1 core/S3/STS, JAXB runtime binding, Commons Codec, Commons Collections, and Alluxio core common with a test-jar dependency.

## Control Flow
The module inherits parent build behavior and configures shade and copy-rename plugins. Having both AWS SDK generations supports synchronous object operations with SDK v1 and async listing/status with SDK v2.

## State And Persistence
The POM controls compile/runtime/test classpaths and packaging. It has no runtime state.

## Dependencies And Integration Points
It plugs into the underfs parent module and packages S3A implementation/factory/service resources.

## Risks
Dual AWS SDK generations increase dependency conflict and configuration drift risk. Netty async client configuration must remain compatible with SDK v2 versions.

## Test Signals
Module tests include stream unit tests, mock-server S3Proxy integration tests, factory tests, ACL translation tests, and exception/permission unit tests.
