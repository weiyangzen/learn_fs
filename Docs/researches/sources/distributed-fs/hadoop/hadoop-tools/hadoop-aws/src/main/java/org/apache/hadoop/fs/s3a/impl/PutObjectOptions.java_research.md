# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/PutObjectOptions.java

## Purpose
`PutObjectOptions` is an immutable option bundle for S3 PUT and multipart create/complete operations, carrying metadata headers, write flags, and conditional overwrite eTag state.

## Important APIs and Types
Fields include `storageClass`, `headers`, `EnumSet<WriteObjectFlags>`, and `etagOverwrite`. `isNoObjectOverwrite()` checks `ConditionalOverwrite`; `isEtagOverwrite()` checks `ConditionalOverwriteEtag`; `hasFlag()` exposes flag membership; `defaultOptions()` returns a shared empty option instance.

## Control Flow
Constructors validate that if conditional eTag overwrite is enabled, the eTag is non-empty. Request-building code checks these flags to set `If-None-Match: *` or `If-Match: <etag>` headers and attaches metadata headers to PUT/multipart requests.

## State and Persistence
The object is immutable by reference, though the provided map and `EnumSet` are not defensively copied. It does not persist state itself; it alters object-store write conditions and metadata when passed to request factories.

## Dependencies and Integration Points
It depends on `WriteObjectFlags` and Apache commons string helpers. It integrates directly with `RequestFactoryImpl` and write operations.

## Risks and Edge Cases
Lack of defensive copying means external mutation of headers or flag set after construction can change behavior. `storageClass` is stored and printed but request factory storage-class behavior is mostly controlled by factory-level configuration, so callers should confirm intended propagation. Conditional overwrite and eTag overwrite semantics must remain mutually sensible at request construction time.

## Test Signals
Tests should validate constructor rejection for empty eTag with eTag flag, default options immutability expectations, request factory conditional header output, and behavior when null headers are supplied.
