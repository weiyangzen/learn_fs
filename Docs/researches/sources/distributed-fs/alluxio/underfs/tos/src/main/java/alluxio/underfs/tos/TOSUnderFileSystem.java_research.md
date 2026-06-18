# sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSUnderFileSystem.java

## Purpose
`TOSUnderFileSystem` adapts Volcengine TOS into Alluxio's object-store UFS abstraction. It handles credential-based client construction, object CRUD, listing, ranged reads, buffered or streaming writes, multipart cleanup, and default object-store permissions.

## APIs and Control Flow
`createInstance` validates access key, secret key, region, and endpoint configuration, builds `TOSClientConfiguration` with `initializeTOSClientConfig`, and constructs a `TOSV2` client. `cleanup` pages through multipart uploads and aborts uploads older than the configured clean age. `copyObject`, `createEmptyObject`, `deleteObject`, and `deleteObjects` translate Alluxio operations to SDK requests. `createObject` chooses `TOSLowLevelOutputStream` when streaming upload is enabled, otherwise `TOSOutputStream`. Listing builds `ListObjectsType2Input` with delimiter based on recursion and wraps output in `TOSObjectListingChunk`.

## State, Persistence, and Dependencies
Persistent data is stored as TOS objects with `/` folder markers. Runtime state includes `TOSV2`, bucket name, and a memoized streaming-upload executor. The class depends on Alluxio object-store UFS classes, Volcengine TOS SDK, Guava suppliers, Alluxio executor factories, path utilities, and retry/open options.

## Risks and Test Signals
`close()` closes `mClient` without null protection, though production construction supplies a client. `copyObject` returns false for all TOS errors and may hide permission or service problems. `cleanup` mutates server-side multipart uploads and throws runtime exceptions on SDK failure. Tests cover delete-directory behavior when listing throws, 404 vs non-404 status handling, rename error propagation, prefix stripping, and folder suffix; many real SDK paths remain mock-only.
