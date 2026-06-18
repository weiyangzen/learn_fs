# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AWSHeaders.java

## Purpose
Central constant interface for HTTP and S3-specific header names used by S3A.

## Important APIs, Types, And Functions
Defines standard headers such as `Content-Length`, `Content-Type`, `ETag`, `If-Match`, and `Range`; S3 headers such as version ID, storage class, archive status, server-side encryption, requester pays, replication status, object lock fields; and client-side encryption metadata headers such as material description, wrapping algorithm, CEK algorithm, and unencrypted content length.

## Control Flow
No executable control flow; consumers reference string constants when building requests or processing responses.

## State And Persistence
No state. Header strings shape persisted object metadata and request/response interpretation.

## Dependencies And Integration Points
Used by S3A request factories, encryption support, header processing, object status extraction, and conditional/ranged operations.

## Risks
Header spelling and casing are compatibility-sensitive. Deprecated encryption headers remain for legacy envelope encryption behavior and should not be removed without migration coverage.

## Test Signals
Request/response tests should assert expected headers for range reads, versioned objects, encryption, requester-pays, storage class, restore/archive status, object lock, and client-side encryption metadata.
