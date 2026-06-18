<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/HeaderProcessing.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/HeaderProcessing.java

## Purpose

`HeaderProcessing` implements S3A extended-attribute reads backed by S3 object and bucket headers, and provides metadata cloning for copy operations.

## Important APIs, Types, and Functions

It defines many `header.*` XAttr names, content-type constants, `getXAttr()`, `getXAttrs()` overloads, `listXAttrs()`, `encodeBytes()`, `decodeBytes()`, `extractXAttrLongValue()`, and static `cloneObjectMetadata()`.

## Control Flow

Header retrieval converts the path to an S3 key. Root uses `HeadBucket` and synthesizes content length zero. Non-root uses `HeadObject`, retrying with a trailing slash when the bare key is not found. User metadata is prefixed with the XAttr header prefix, standard HTTP/AWS fields are added when non-null, and public XAttr methods filter or return the resulting map. Metadata cloning copies selected HTTP/SSE headers and user metadata except the magic-marker header.

## State and Persistence Behavior

The operation stores callbacks and inherited context/span. It does not persist data; it reads S3 metadata and returns encoded byte arrays.

## Dependencies and Integration Points

It integrates with S3A xattr APIs, S3 HEAD bucket/object responses, statistics duration tracking, AWS header constants, and rename/copy metadata handling.

## Risks and Edge Cases

Directory fallback relies on appending `/` after not found. Header names are case-sensitive after mapping. Copy metadata can miss newly added SDK fields if not updated. `extractXAttrLongValue()` logs and returns empty on invalid or negative numbers.

## Test Signals

Test root bucket headers, file and directory marker metadata, user metadata prefixing, selected header encoding, named XAttr filtering, content-range extraction from HTTP headers, long parsing, and magic-marker exclusion during clone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/HeaderProcessing.java -->
