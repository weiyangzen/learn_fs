# sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3AUnderFileSystem.java

## Purpose
`S3AUnderFileSystem` is Alluxio's AWS/S3-compatible object store adapter, implementing object operations, listing, permissions, reads, writes, and async loading.

## Important APIs, Types, And Functions
Creation APIs include `createAwsCredentialsProvider`, `createInstance`, `createAmazonS3`, `createAmazonS3Async`, and endpoint/region helpers. UFS overrides include `cleanup`, `close`, `copyObject`, `createEmptyObject`, `createObject`, `deleteObject`, `deleteObjects`, `getObjectListingChunk`, `performListingAsync`, `getObjectStatus`, `getPermissions`, `getRootKey`, and `openObject`. Inner classes wrap v1 list-object result pages.

## Control Flow
Construction builds AWS SDK v1 sync client, SDK v2 async client, transfer executor, and transfer manager from Alluxio configuration. Object operations use v1 client/transfer manager. Listing supports v1 or v2 sync APIs and async SDK v2 listing/status for load paths. Async listing optionally checks base status, handles `DescendantType`, merges common prefixes and objects into ordered `UfsStatus` streams, and returns continuation metadata.

## State And Persistence
State includes sync and async clients, bucket name, executor, transfer manager, streaming upload flag, and memoized permissions. Remote state is S3 objects and multipart uploads; `cleanup` aborts old multipart uploads.

## Dependencies And Integration Points
It integrates Alluxio `ObjectUnderFileSystem` with AWS SDK v1/v2, `S3AInputStream`, `S3AOutputStream`, `S3ALowLevelOutputStream`, `S3AUtils`, and Alluxio permission/status/load-result types.

## Risks
Dual SDK clients can diverge in endpoint, region, proxy, and credential behavior. SDK v2 async client does not support global bucket access, so missing region can break async listing. ETag substring handling assumes quoted SDK v2 ETags. Permissions are memoized and may become stale.

## Test Signals
Unit tests cover credential providers, exception conversion, metadata 404/403, permissions caching/mapping, operation mode, prefix stripping, and null last-modified time. S3Proxy integration tests cover real reads, recursive and async listings, descendant modes, and iterable listing.
