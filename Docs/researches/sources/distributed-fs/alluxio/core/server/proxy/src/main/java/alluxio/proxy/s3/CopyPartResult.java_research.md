# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CopyPartResult.java

## Purpose
`CopyPartResult` is the XML response model for S3 upload-part-copy. It contains the ETag of the copied multipart part.

## Important APIs, Types, and Functions
The class is annotated with `@JacksonXmlRootElement("CopyPartResult")`, stores a final `mETag`, and exposes `getEtag` as XML `ETag`.

## Control Flow, State, and Persistence
Construction captures the ETag. There are no setters, side effects, or persistence.

## Dependencies and Integration Points
It integrates with the S3 multipart copy path and Jackson XML serialization.

## Risks
No default constructor means this is serialization-oriented only. It does not validate ETag formatting.

## Test Signals
Signals should verify XML element naming and correct propagation of the copied part ETag.
