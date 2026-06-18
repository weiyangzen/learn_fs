# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CompleteMultipartUploadResult.java

## Purpose
`CompleteMultipartUploadResult` is the XML response model for S3 multipart completion. It can represent either a successful completion with object location metadata or an error payload with code and message.

## Important APIs, Types, and Functions
The class is annotated with `@JacksonXmlRootElement("CompleteMultipartUploadResult")`, ordered fields `Location`, `Bucket`, `Key`, `ETag`, and non-empty inclusion. It exposes getters and setters for success fields and `Code`/`Message`, plus `toString`, `equals`, and `hashCode`.

## Control Flow, State, and Persistence
Constructors initialize either empty success fields, success values, or error values. `hashCode` switches between success and error field sets depending on whether `mCode` is null. The class has no persistence or external side effects.

## Dependencies and Integration Points
It is serialized by `CompleteMultipartUploadHandler` through Jackson XML and compared in tests. It follows S3 response field names and is part of proxy S3 REST compatibility.

## Risks
The same root type is used for error responses, which may not match AWS's usual error XML shape in all clients. Empty-string defaults combined with `NON_EMPTY` affect which fields appear. Equality includes both success and error fields, so partially populated objects can behave unexpectedly.

## Test Signals
Signals should verify XML for success and error forms, equality/hash behavior, omitted empty fields, and correct ETag/bucket/key values from multipart completion.
