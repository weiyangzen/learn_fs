# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CompleteMultipartUploadRequest.java

## Purpose
`CompleteMultipartUploadRequest` is the Jackson XML model for an S3 complete-multipart-upload request body. It carries the ordered list of parts the client wants to commit.

## Important APIs, Types, and Functions
The class is annotated with `@JacksonXmlRootElement("CompleteMultipartUploadRequest")` and `@JsonInclude(NON_EMPTY)`. It exposes `getParts` and `setParts`. The nested `Part` model exposes XML `ETag` and `PartNumber` properties. Constructors support normal validation and a unit-test-only `ignoreValidation` path.

## Control Flow, State, and Persistence
`setParts` assigns the list and calls `validateParts`. Validation requires consecutive part numbers when more than one part is present; otherwise it wraps `S3ErrorCode.INVALID_PART_ORDER` in `IllegalArgumentException` so XML parsing surfaces an underlying S3 cause. State is an in-memory list of part descriptors.

## Dependencies and Integration Points
The model is consumed by `CompleteMultipartUploadHandler.parseCompleteMultipartUploadRequest`. It depends on Jackson XML annotations and S3 exception/error types.

## Risks
The root element name differs from AWS's usual `CompleteMultipartUpload` naming, so compatibility depends on how Jackson maps incoming documents. Setter methods in `Part` are both named `setKey` despite setting ETag and part number; annotations make it work, but it is confusing and brittle for reflection or maintainers. Validation checks order but not ETag format or part number range.

## Test Signals
Signals should cover XML deserialization, consecutive and non-consecutive part order, single-part requests, the ignore-validation constructor, and propagation of `INVALID_PART_ORDER` to the handler.
