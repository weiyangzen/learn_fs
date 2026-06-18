# sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSUnderFileSystem.java

## Purpose
`OSSUnderFileSystem` adapts Aliyun OSS buckets to Alluxio's `ObjectUnderFileSystem` contract.

## Important APIs, Types, And Functions
Important methods include `createInstance`, the protected constructor, `cleanup`, `copyObject`, `createEmptyObject`, `createObject`, `deleteObject`, `deleteObjects`, `getObjectListingChunk`, `getObjectStatus`, `getPermissions`, `initializeOSSClientConfig`, `openObject`, and `close`.

## Control Flow
Construction either creates an STS-backed client, uses an injected client, or builds a static-credential client from required OSS properties. Object operations call OSS SDK copy/put/delete/list/metadata APIs. Listing normalizes prefixes, chooses delimiter by recursive flag, and wraps paginated `ObjectListing` in `OSSObjectListingChunk`. Writes choose streaming multipart or temp-file output from configuration.

## State And Persistence
The UFS holds an OSS client, bucket name, optional STS provider, memoized streaming upload executor, and memoized permissions. Persistent data lives in OSS objects and multipart uploads; cleanup aborts old multipart uploads.

## Dependencies And Integration Points
It depends on Alluxio object-UFS base behavior, Aliyun OSS SDK, STS provider, `PathUtils`, `ModeUtils`, and `UnderFileSystemUtils`.

## Risks
`close` calls `mClientProvider.close()` without a null guard even though `mClientProvider` is only initialized in STS mode. Metadata exceptions in `getObjectStatus` return null for all `ServiceException`s, potentially hiding authorization or service failures.

## Test Signals
`OSSUnderFileSystemTest` covers delete/rename failure handling and folder suffix. Stream tests cover read/write paths; STS behavior is tested separately.
