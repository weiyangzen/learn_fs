# sources/distributed-fs/alluxio/underfs/s3a/src/test/java/alluxio/underfs/s3a/S3AUnderFileSystemMockServerTest.java

## Purpose
This integration-style test validates S3A UFS behavior against an in-process S3Proxy server.

## Important APIs, Types, And Functions
The fixture creates an S3Proxy transient store, AWS SDK v1 client, SDK v2 async client, bucket, and `S3AUnderFileSystem`. Tests cover `read`, `nestedDirectory`, and `iterator`.

## Control Flow
The read test writes an object through the client and reads it through the UFS. The nested-directory test creates objects and marker directories, then compares recursive `listStatus` and async `performListingAsync` results for `ALL`, `ONE`, and `NONE`. The iterator test compares paged iterable listing with full recursive listing.

## State And Persistence
State lives in the transient S3Proxy bucket during each test. No real AWS service is used.

## Dependencies And Integration Points
It exercises real AWS SDK calls, Alluxio open/list/listStatusIterable/async-load behavior, and path-style endpoint configuration.

## Risks
S3Proxy is close but not identical to AWS S3; the fixture notes path-style behavior to close one gap. Fixed port `8001` can conflict in shared test environments.

## Test Signals
Passing tests provide strong evidence for read, directory inference, async descendant listing, continuation/last-item handling, and iterable pagination.
