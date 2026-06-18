# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CopyObjectResult.java

## Purpose
`CopyObjectResult` is the XML response model for an S3 copy-object operation. It reports the copied object's ETag and last-modified timestamp.

## Important APIs, Types, and Functions
The class is annotated with `@JacksonXmlRootElement("CopyObjectResult")`. Its constructor accepts an ETag and a last-modified epoch in milliseconds, converting the timestamp with `S3RestUtils.toS3Date`. Getters expose XML `ETag` and `LastModified`.

## Control Flow, State, and Persistence
The object is immutable after construction because fields are final and there are no setters. There is no persistence or external side effect.

## Dependencies and Integration Points
It is serialized by S3 proxy copy-object handling and depends on S3 date formatting utilities and Jackson XML annotations.

## Risks
There is no default constructor, which is fine for serialization but can limit deserialization in tests or clients. Correctness depends on callers providing the already-computed ETag.

## Test Signals
Signals include XML serialization with correct element names and S3 date formatting from epoch milliseconds.
