# subset-b-008144 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestCompleteMultipartUploadRequestUnmarshaller.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestCompleteMultipartUploadRequestUnmarshaller.java

## Purpose
Unit test coverage for `CompleteMultipartUploadRequestUnmarshaller`, the JAX-RS message-body reader that turns S3 CompleteMultipartUpload XML into a `CompleteMultipartUploadRequest`.

## Important APIs, types, and functions
The tests call `readFrom(...)` directly with `ByteArrayInputStream` bodies. They validate `CompleteMultipartUploadRequest.getPartList()`, nested `Part.getETag()`, and XML namespace handling with `S3Consts.S3_XML_NAMESPACE`.

## Control flow
Two basic tests feed XML with and without the S3 namespace, unmarshal it, and assert the parsed part order and ETag values. `concurrentParse` reuses one unmarshaller instance across 40 `CompletableFuture` tasks to catch unsafe shared parser state.

## State and persistence behavior
No persistent state is written. The relevant state is parser-local or unmarshaller-instance state that must not leak between concurrent reads.

## Dependencies and integration points
This protects multipart completion request parsing before `ObjectEndpoint.completeMultipartUpload` receives the part list. It depends on JAXB/JAX-RS unmarshalling behavior and the S3 XML namespace contract.

## Risks and edge cases
Coverage is focused on happy XML and thread reuse; malformed XML, missing fields, duplicate part numbers, and very large part lists are left to other layers.

## Test signals
Passing signals that namespaced and non-namespaced XML both produce two parts in order and that shared unmarshaller use is thread-safe for this request shape.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestCompleteMultipartUploadRequestUnmarshaller.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestEndpointBase.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestEndpointBase.java

## Purpose
Focused tests for common `EndpointBase` metadata parsing used by S3 endpoint implementations.

## Important APIs, types, and functions
The file exercises `EndpointBase.getCustomMetadataFromHeaders(MultivaluedMap)`, `S3Consts.CUSTOM_METADATA_HEADER_PREFIX`, `OzoneConsts.GDPR_FLAG`, and `OS3Exception` error reporting.

## Control flow
Tests build synthetic request header maps, instantiate an anonymous `EndpointBase`, and call the metadata extraction helper. Assertions verify accepted custom metadata, rejected reserved GDPR metadata, maximum metadata-size enforcement, and case-insensitive matching of the `x-amz-meta-` prefix.

## State and persistence behavior
No Ozone state is created. The method returns a new metadata map derived from request headers; server-controlled metadata such as GDPR must be excluded so callers cannot persist it through user headers.

## Dependencies and integration points
This helper feeds object creation, copy, and multipart initiation paths that persist metadata into Ozone key metadata. It also maps S3 metadata size rules to `MetadataTooLarge`.

## Risks and edge cases
The size test uses one oversized value and does not cover many small headers whose aggregate size crosses the limit. Header casing is covered for the prefix, but duplicate values and non-ASCII byte accounting are not deeply exercised.

## Test signals
Signals are exact map membership and an `OS3Exception` whose code contains `MetadataTooLarge`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestEndpointBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestInitiateMultipartUpload.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestInitiateMultipartUpload.java

## Purpose
Verifies S3 multipart-upload initialization through `ObjectEndpoint.initializeMultipartUpload`.

## Important APIs, types, and functions
Uses `EndpointTestUtils.initiateMultipartUpload`, `EndpointBuilder.newObjectEndpointBuilder`, `OzoneClientStub`, `OzoneConsts.S3_BUCKET`, `OzoneConsts.KEY`, mocked `HttpHeaders`, `STORAGE_CLASS_HEADER`, and `ECReplicationConfig`.

## Control flow
The normal test creates an S3 bucket in the stub client, builds an object endpoint, initiates upload twice for the same bucket/key, and asserts different upload IDs. The EC test sets an EC replication config on the bucket and verifies initiation does not reject EC-backed keys.

## State and persistence behavior
State is held in `OzoneClientStub`: S3 bucket metadata and pending multipart upload records. Upload IDs must be unique per initiation and must capture bucket replication settings without committing object data.

## Dependencies and integration points
This is the entry point for later `put` part and complete calls. It integrates storage-class header parsing, bucket replication defaults, and Ozone multipart initiation.

## Risks and edge cases
The tests do not assert response XML fields beyond upload ID uniqueness, nor invalid buckets, storage classes, owner conditions, or metadata headers.

## Test signals
Passing means repeated initiation returns distinct IDs and EC bucket defaults are accepted.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestInitiateMultipartUpload.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestListDirectoryBuckets.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestListDirectoryBuckets.java

## Purpose
Tests S3 Express-style directory bucket listing from `RootEndpoint`, backed by Ozone FSO buckets.

## Important APIs, types, and functions
Uses `RootEndpoint.get`, `ListDirectoryBucketsResponse`, `DirectoryBucketMetadata`, `BucketArgs` with `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `SignatureInfo` credential scopes, and query params `MAX_DIRECTORY_BUCKETS` and `CONTINUATION_TOKEN`.

## Control flow
Setup creates an `OzoneClientStub`, a root endpoint with a V4 `s3express` credential scope, and the default S3 volume. Tests cover empty output, filtering object-store buckets out of directory-bucket output, pagination over five FSO buckets, zero/invalid max values, credential-scope region selection, and max capping above the supported limit.

## State and persistence behavior
The stub object store holds created volumes and buckets. Only FSO buckets should appear in the directory bucket response. Continuation tokens encode list position; response metadata includes name, creation time, region, and generated bucket ARN.

## Dependencies and integration points
This bridges S3 root listing, S3 Express signing metadata, Ozone bucket layout, and ARN construction through `RootEndpoint.buildDirectoryBucketArn`.

## Risks and edge cases
The tests assume deterministic bucket listing order from the stub. They do not cover malformed continuation tokens, mixed owner IDs, or live OM pagination behavior.

## Test signals
Assertions check bucket counts, names, region extraction (`us-west-2` or `aws-global`), continuation token presence, and invalid max-bucket exception behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestListDirectoryBuckets.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestListParts.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestListParts.java

## Purpose
Validates S3 ListParts behavior for in-progress multipart uploads.

## Important APIs, types, and functions
The class uses `EndpointTestUtils.initiateMultipartUpload`, `uploadPart`, `listParts`, `ListPartsResponse`, `OzoneClientStub`, and S3 error `NO_SUCH_UPLOAD`.

## Control flow
Setup creates a bucket, starts one multipart upload, and uploads three numbered parts. `testListParts` requests all three parts and checks non-truncation. `testListPartsContinuation` requests two, uses the returned next part marker, and verifies the final page has one part. Unknown upload ID/key produces an S3 error.

## State and persistence behavior
Multipart part state is stored in the stub bucket under upload ID. Listing must expose ordered part metadata and preserve the continuation marker contract without completing or mutating the upload.

## Dependencies and integration points
This protects `ObjectEndpoint.listParts` and Ozone bucket `listParts` integration, including query-parameter conversion for `max-parts` and `part-number-marker`.

## Risks and edge cases
It does not inspect individual part ETags, timestamps, sizes, owner fields, or boundary values such as zero max parts.

## Test signals
Signals are `getTruncated`, list size, next marker behavior, and `NO_SUCH_UPLOAD` translation for unknown uploads.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestListParts.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestMultiDeleteRequestUnmarshaller.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestMultiDeleteRequestUnmarshaller.java

## Purpose
Tests custom XML unmarshalling for S3 multi-object delete requests.

## Important APIs, types, and functions
Exercises `MultiDeleteRequestUnmarshaller.readFrom`, `MultiDeleteRequest.getObjects()`, and XML namespace handling via `S3Consts.S3_XML_NAMESPACE`.

## Control flow
Two tests build compact delete XML with three object entries, once with the S3 namespace and once without it, then invoke `readFrom` and assert the resulting request contains three objects.

## State and persistence behavior
No persistent state is involved. The parser must create an independent request object from the request body so `BucketEndpoint.multiDelete` can later apply deletes.

## Dependencies and integration points
This parser is the request-body adapter for the bucket multi-delete endpoint. Correct parsing affects deletion response content and quiet-mode behavior downstream.

## Risks and edge cases
The test body uses `<Object>key</Object>` rather than validating all S3 nested `<Object><Key>...` variants. It does not cover malformed XML, quiet flags, whitespace, duplicate objects, or invalid encodings.

## Test signals
Passing means namespaced and non-namespaced delete bodies both produce the expected object count.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestMultiDeleteRequestUnmarshaller.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestMultipartUploadComplete.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestMultipartUploadComplete.java

## Purpose
End-to-end unit tests for completing multipart uploads through the S3 object endpoint.

## Important APIs, types, and functions
Uses `EndpointTestUtils.initiateMultipartUpload`, `uploadPart`, `completeMultipartUpload`, `CompleteMultipartUploadRequest.Part`, `ObjectEndpoint.head`, and custom metadata headers with `CUSTOM_METADATA_HEADER_PREFIX`.

## Control flow
Setup creates an S3 bucket and object endpoint. The happy test initiates upload, uploads two parts, and completes. Metadata coverage initiates upload with custom metadata, uploads one part, completes, then checks `HEAD` response metadata. Error tests tamper with requested part order and ETag to assert `INVALID_PART_ORDER` and `INVALID_PART`.

## State and persistence behavior
Stub bucket state moves from pending multipart upload to a committed key after completion. Metadata attached at initiation must persist onto the final key. Invalid completion requests must not silently commit corrupted part lists.

## Dependencies and integration points
This covers `ObjectEndpoint.completeMultipartUpload`, Ozone multipart validation, response closing through `Response`, and metadata propagation from request headers to completed object metadata.

## Risks and edge cases
It does not read final object content, test missing upload IDs, duplicate parts, empty part completion behavior beyond metrics use, or minimum part-size constraints.

## Test signals
Signals are successful completion, custom metadata visible through `HEAD`, and exact S3 error codes for bad part ordering and wrong ETag.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestMultipartUploadComplete.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestMultipartUploadWithCopy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestMultipartUploadWithCopy.java

## Purpose
Tests multipart upload where individual parts are created by copying existing object data, including range copy and conditional timestamp headers.

## Important APIs, types, and functions
Uses `ObjectEndpoint.put` as UploadPart/UploadPartCopy, `COPY_SOURCE_HEADER`, `COPY_SOURCE_HEADER_RANGE`, `COPY_SOURCE_IF_MODIFIED_SINCE`, `COPY_SOURCE_IF_UNMODIFIED_SINCE`, `CopyPartResult`, `CompleteMultipartUploadRequest.Part`, and `OzoneMultipartUploadPartListParts`.

## Control flow
`@BeforeAll` creates a source key with a known ETag and derives before/after/future timestamp strings. The main multipart test uploads one normal part, full-copy and range-copy parts, and a copy with timestamp preconditions, then completes and reads final content. `testMultipartTSHeaders` iterates an enum of modified/unmodified-since combinations to assert which combinations should fail with `PreconditionFailed`. A final test confirms range-copy part size is the copied byte range length.

## State and persistence behavior
Source key data remains unchanged. Pending multipart state accumulates copied part data and metadata until completion commits the destination key. Range copy must persist a part with content length equal to the selected range.

## Dependencies and integration points
This integrates object copy, RFC-style timestamp parsing, multipart part registration, final completion, and Ozone stub key reads.

## Risks and edge cases
The timestamp matrix is time-sensitive and sleeps to avoid future-time ambiguity. It does not cover ETag preconditions for copy part or cross-bucket owner checks.

## Test signals
Signals include final concatenated object content, copy-part ETag/last-modified fields, expected `PRECOND_FAILED` codes, and persisted copied part size of four bytes for `bytes=0-3`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestMultipartUploadWithCopy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectDelete.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectDelete.java

## Purpose
Minimal test for S3 object delete behavior.

## Important APIs, types, and functions
Uses `EndpointTestUtils.delete`, `EndpointTestUtils.assertStatus`, `ObjectEndpoint`, `OzoneClientStub`, `OzoneBucket.createKey`, and HTTP status `204 No Content`.

## Control flow
The test creates a stub S3 bucket, writes one zero-length key, builds an object endpoint, invokes delete, and verifies the bucket no longer lists any keys.

## State and persistence behavior
State is the in-memory key table in `OzoneClientStub`. Delete should remove the key and return a no-content S3 response.

## Dependencies and integration points
This covers `ObjectEndpoint.delete` integration with the Ozone bucket delete path and the S3 response status contract.

## Risks and edge cases
Only one success path is covered. Nonexistent keys, nonexistent buckets, versioned deletes, permission failures, and directory keys are tested elsewhere or not here.

## Test signals
Signals are HTTP 204 and an empty `bucket.listKeys("")` iterator after deletion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectDelete.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectEndpoint.java

## Purpose
Tests static helper parsing for the S3 copy-source header.

## Important APIs, types, and functions
Exercises `ObjectEndpoint.parseSourceHeader(String)` and its returned Apache Commons `Pair<String,String>`.

## Control flow
One test parses `bucket1/key1`, and another parses `/bucket1/key1`. Both assert the bucket name is `bucket1` and key is `key1`.

## State and persistence behavior
No state is persisted. The helper normalizes request-header syntax before copy operations interact with Ozone buckets.

## Dependencies and integration points
CopyObject and UploadPartCopy depend on this parsing to identify source bucket/key from `x-amz-copy-source`.

## Risks and edge cases
The file does not cover URL-encoded keys, keys containing slashes, empty bucket/key segments, or malformed headers. Those are risk areas for copy-source compatibility.

## Test signals
Passing means both leading-slash and no-leading-slash header forms resolve to the same bucket/key pair.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectGet.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectGet.java

## Purpose
Validates `GET Object` response behavior for content metadata, conditionals, range requests, tags, and FSO directory handling.

## Important APIs, types, and functions
Uses `EndpointTestUtils.get/put`, `ObjectEndpoint`, `OzoneClientStub`, `OzoneClientTestUtils.assertKeyContent`, conditional headers (`If-Match`, `If-None-Match`, `If-Modified-Since`, `If-Unmodified-Since`), `RANGE_HEADER`, response override query params, and `TAG_COUNT_HEADER`.

## Control flow
Setup creates a bucket, a normal key, and a tagged key. Tests assert basic headers, valid and failing ETag preconditions, not-modified status for time/ETag conditions, precedence of ETag conditions over date conditions, tag-count header inclusion only for tagged objects, response header inheritance/override, range content length/content range/status 206, and FSO directory lookup behavior when directory creation is enabled.

## State and persistence behavior
Object data, metadata, modification time, and tags are stored in the stub bucket. GET must not mutate object state, but it must expose stored metadata through HTTP headers and stream selected byte ranges.

## Dependencies and integration points
This covers S3 conditional request evaluation, RFC1123 date formatting, range parsing, response header override query handling, and FSO directory semantics.

## Risks and edge cases
Streaming response bodies are not fully consumed in every test. Multi-range requests, invalid ranges, and timezone edge cases are only indirectly covered.

## Test signals
Signals include exact HTTP status codes, content-length/range headers, parseable `Last-Modified`, tag count values, and expected `PreconditionFailed`/`NoSuchKey` errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectGet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectHead.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectHead.java

## Purpose
Tests `HEAD Object` metadata response behavior and conditional handling.

## Important APIs, types, and functions
Uses `ObjectEndpoint.head`, `EndpointTestUtils.put`, `assertStatus`, `assertErrorResponse`, condition headers (`IF_MATCH_HEADER`, `IF_NONE_MATCH_HEADER`, `IF_UNMODIFIED_SINCE_HEADER`), `TAG_HEADER`, `TAG_COUNT_HEADER`, `RFC1123Util`, and FSO directory creation config.

## Control flow
Setup creates a stub bucket and endpoint. Tests create keys, call `head`, and assert status, content length, `Last-Modified`, and tag-count behavior. Conditional tests verify matching ETag success, `If-None-Match` not-modified, failed `If-Unmodified-Since`, and precedence when `If-Match` succeeds. FSO tests distinguish file paths, directory paths with slash, directory paths without slash, and file path with trailing slash.

## State and persistence behavior
Stub key metadata includes content length, modification time, ETag, and tags. `HEAD` reads this state without returning a body and applies path interpretation for FSO directories.

## Dependencies and integration points
This protects metadata presentation shared with GET, S3 conditional request logic, and directory-key compatibility.

## Risks and edge cases
Date parsing is tested through generated values only; invalid condition dates and custom response overrides are not covered here.

## Test signals
Signals are HTTP 200/304/404, `PRECOND_FAILED`, content-length equality, parseable last-modified, and `x-amz-tagging-count` inclusion only for tagged objects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectHead.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectMultiDelete.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectMultiDelete.java

## Purpose
Tests S3 multi-object delete execution and quiet-mode response shaping.

## Important APIs, types, and functions
Uses `BucketEndpoint.multiDelete`, `MultiDeleteRequest`, nested `DeleteObject`, `MultiDeleteResponse`, `OzoneClientStub`, and bucket key listing through `OzoneKey`.

## Control flow
`initTestData` creates a bucket with keys `key1`, `key2`, and `key3`. The normal test requests deletion of `key1`, `key2`, and missing `key4`, then checks only `key3` remains and deleted-object response entries are populated. The quiet test sets `quiet=true` and verifies the same bucket mutation but no deleted-object entries.

## State and persistence behavior
Deletes mutate the stub bucket key set. Missing keys are treated as deleted for S3-compatible idempotency in this test, and quiet mode only affects response contents, not deletion behavior.

## Dependencies and integration points
This verifies `BucketEndpoint.multiDelete` mapping from parsed request objects into Ozone `deleteKeys` behavior and S3 response assembly.

## Risks and edge cases
It does not cover per-key errors, access denied, malformed XML, version IDs, or very large delete batches.

## Test signals
Signals are final key set equality, deleted-object count, and error list count for both normal and quiet modes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectMultiDelete.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectPut.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectPut.java

## Purpose
Large unit suite for S3 `PUT Object` and `CopyObject` behavior across metadata, tags, conditionals, checksums, signed chunks, replication, and FSO directory creation.

## Important APIs, types, and functions
Uses `ObjectEndpoint.put`, `EndpointTestUtils.put/putDir`, `OzoneClientStub`, `OzoneBucket`, `OzoneKeyDetails`, `S3Consts` headers for tags/copy/storage/signed payload, `S3Utils.parseETag/urlEncode`, `S3ErrorTable`, `EndpointBase.getMD5DigestInstance`, and `S3ConditionalRequest`-driven headers.

## Control flow
Setup creates source, destination, and FSO buckets. Parameterized PUT verifies RATIS and EC replication with zero/nonzero content. Tag tests cover valid tags, key-only tags, duplicates, length limits, and tag count limits. Signed-chunk PUT decodes chunk framing. CopyObject tests cover metadata COPY/REPLACE, tag COPY/REPLACE, source/destination errors, invalid directives, source and destination ETag preconditions, and destination `If-Match`/`If-None-Match`. Additional tests cover invalid storage class, empty object, incomplete body rejection, content MD5 success/failure, digest reset on exceptions, FSO directory creation/no-overwrite, and ETag parsing.

## State and persistence behavior
The stub bucket persists object bytes, size, replication config, ETag metadata, custom metadata, and tags. Failure paths must avoid committing partial destination keys and must reset thread-local digest instances for reuse.

## Dependencies and integration points
This is central coverage for S3 object write semantics, Ozone key creation/copy, checksum validation, AWS signed payload decoding, tag parsing, storage-class mapping, FSO directory APIs, and conditional write enforcement.

## Risks and edge cases
The suite is broad but stub-based; real stream failure timing, large object copies, encryption, and concurrent conditional writes are not covered. Some mock header state is reused within tests, so ordering changes can affect expectations.

## Test signals
Signals include persisted content/metadata/tags/replication, S3 error codes/messages, ETag equality, absence of partial keys after failures, digest `reset()` verification, and HTTP success response checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectPut.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectTaggingDelete.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectTaggingDelete.java

## Purpose
Tests `DELETE Object tagging` behavior.

## Important APIs, types, and functions
Uses `EndpointTestUtils.deleteTagging`, `put`, `ObjectEndpoint`, `OzoneClientStub`, `OzoneKeyDetails.getTags`, S3 errors `NO_SUCH_KEY`, `NO_SUCH_BUCKET`, and `NOT_IMPLEMENTED`.

## Control flow
Setup creates a tagged key. The success test deletes tags, expects HTTP 204, and verifies the key's tag map is empty. Error tests cover missing key and missing bucket. A mocked FSO-directory path throws `OMException.NOT_SUPPORTED_OPERATION`, which must map to S3 `NotImplemented`.

## State and persistence behavior
Only object tag metadata changes; object data remains. Unsupported directory tagging should not mutate mocked bucket state.

## Dependencies and integration points
This verifies `ObjectEndpoint.deleteTagging` integration with Ozone bucket `deleteObjectTagging`, OM exception translation, and S3 response status.

## Risks and edge cases
It does not verify idempotent delete on untagged existing objects or permission-denied paths, which are covered by permission tests.

## Test signals
Signals are HTTP 204, empty persisted tags, and expected S3 errors for not found and unsupported directory cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectTaggingDelete.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectTaggingGet.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectTaggingGet.java

## Purpose
Tests `GET Object tagging` response conversion from Ozone tag maps to S3 XML model objects.

## Important APIs, types, and functions
Uses `EndpointTestUtils.getTagging`, `put`, `S3Tagging`, `S3Tagging.Tag`, `TAG_HEADER`, and S3 errors `NO_SUCH_KEY` and `NO_SUCH_BUCKET`.

## Control flow
Setup creates a bucket and endpoint. A success test writes a key with two tags, retrieves tagging, and validates HTTP 200 plus tag keys and values. Another success test writes tags in reverse lexical order and asserts the response is sorted by key. Error tests cover missing key and bucket.

## State and persistence behavior
Tags are stored on `OzoneKeyDetails` in the stub bucket. GET tagging must read and sort them without mutating object metadata.

## Dependencies and integration points
This protects S3 XML marshalling model `S3Tagging` and Ozone object tag retrieval used by `ObjectEndpoint.getTagging`.

## Risks and edge cases
The tests do not cover empty tag sets on existing keys, XML serialization text, duplicate tag keys, or tag limits.

## Test signals
Signals are HTTP 200, non-null `S3Tagging.TagSet`, expected size and values, sorted key order, and not-found error mappings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectTaggingGet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectTaggingPut.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectTaggingPut.java

## Purpose
Tests `PUT Object tagging` XML parsing, validation, persistence, and unsupported FSO directory mapping.

## Important APIs, types, and functions
Uses `EndpointTestUtils.putTagging`, `S3Consts.S3_XML_NAMESPACE`, `OzoneKeyDetails.getTags`, `ObjectEndpoint`, S3 errors `MALFORMED_XML`, `NO_SUCH_KEY`, `NO_SUCH_BUCKET`, `NOT_IMPLEMENTED`, and `OMException.ResultCodes.NOT_SUPPORTED_OPERATION`.

## Control flow
Setup creates a bucket and empty object. Tests cover empty body, valid two-tag XML, malformed XML structure, missing `TagSet`, empty tags, missing key, missing value, missing object, missing bucket, and mocked FSO directory unsupported operation.

## State and persistence behavior
Valid tagging mutates only the key's tag map. Invalid XML and missing resources should not create or modify keys. Unsupported FSO directory behavior is translated without state change.

## Dependencies and integration points
This protects S3 tagging request XML unmarshalling and Ozone `putObjectTagging` integration.

## Risks and edge cases
Tag count, duplicate keys, and length constraints are mostly covered in PUT object tag-header tests rather than this XML endpoint.

## Test signals
Signals include exact persisted tag map for valid XML and expected S3 error categories for malformed, missing, and unsupported cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectTaggingPut.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestPartUpload.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestPartUpload.java

## Purpose
Tests S3 multipart `UploadPart` for regular and datastream-enabled paths.

## Important APIs, types, and functions
Parameterized class runs with `HDDS_CONTAINER_RATIS_DATASTREAM_ENABLED` false and true. It uses `EndpointTestUtils.put`, `initiateMultipartUpload`, `OzoneMultipartUploadPartListParts`, `S3StorageType`, `DECODED_CONTENT_LENGTH_HEADER`, `Content-MD5`, `EndpointBase` digest providers, and `FailingInputStream`.

## Control flow
Setup creates a bucket, endpoint, and config, then asserts datastream mode. Tests upload a part, replace the same part and require a changed ETag, accept `STANDARD_IA`, reject wrong upload IDs, reject incomplete bodies without recording parts, handle signed-chunk decoded length, reset MD5/SHA-256 digests after read failure, and validate Content-MD5 success and bad/invalid digest failures.

## State and persistence behavior
Part state remains under the pending upload ID. Uploading the same part number overwrites previous part metadata. Failed body reads and checksum failures must not persist a part. Digest instances are reset for future requests.

## Dependencies and integration points
This covers upload-part request query parameters, Ozone multipart part storage, datastream configuration, checksum validation, signed payload decoding, and storage-class handling.

## Risks and edge cases
It does not complete uploads, test very large parts, or exercise concurrent part replacement.

## Test signals
Signals include ETag presence/change, persisted part size, zero parts after failure, specific S3 error codes, and digest `reset()` calls in exception paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestPartUpload.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestPermissionCheck.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestPermissionCheck.java

## Purpose
Verifies OM permission-denied exceptions are translated into S3 access-denied responses across gateway endpoints.

## Important APIs, types, and functions
Uses mocked `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `ClientProtocol`, `OMException(PERMISSION_DENIED)`, `EndpointBuilder`, `S3ErrorTable.ACCESS_DENIED`, and `EndpointTestUtils` for object/tag operations.

## Control flow
Setup wires mocks and common configuration. Root, bucket, and object endpoint tests inject permission failures into volume lookup, bucket lookup/create/delete/list, multipart listing, key list, ACL get/set, key get/put/delete, multipart initiation, and object tagging get/put/delete. Multi-delete additionally checks per-key `ErrorInfo` is surfaced in the response errors list.

## State and persistence behavior
No real Ozone state is persisted; mocked calls throw or return controlled values. The important state is error propagation: forbidden operations should not be masked as missing resources or internal failures.

## Dependencies and integration points
This spans `RootEndpoint`, `BucketEndpoint`, `ObjectEndpoint`, S3 ACL parsing, multi-delete response construction, and Ozone client protocol methods.

## Risks and edge cases
The mock setup validates translation but not real ACL evaluation. It covers `PERMISSION_DENIED` but not mixed permission and not-found conditions from real OM.

## Test signals
Signals are HTTP 403 or `ACCESS_DENIED` S3 errors for each endpoint path and a multi-delete response error code of `ACCESS_DENIED`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestPermissionCheck.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestRootList.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestRootList.java

## Purpose
Tests root-level S3 bucket listing.

## Important APIs, types, and functions
Uses `RootEndpoint.get`, `ListBucketResponse`, `OzoneClientStub`, default S3 volume config, and `S3Owner.DEFAULT_S3OWNER_ID`.

## Control flow
Setup creates the default S3 volume and root endpoint. The test first lists with no buckets and expects zero. It then creates ten S3 buckets and verifies the response count and owner display/id fields.

## State and persistence behavior
The stub object store persists volume and bucket names. Root listing should reflect current buckets without mutating state.

## Dependencies and integration points
This covers the root endpoint's object-store list integration and response owner metadata.

## Risks and edge cases
Pagination, directory bucket filtering, permissions, and ordering are not covered here; directory bucket listing is covered separately.

## Test signals
Signals are bucket counts of zero and ten plus owner display name `root` and default owner ID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestRootList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestS3ObjectWriteGuard.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestS3ObjectWriteGuard.java

## Purpose
Tests close-time commit guards that prevent S3 object writes from committing after failed input reads, failed writes, or content-length mismatches.

## Important APIs, types, and functions
Uses `S3ObjectWriteGuard`, `S3ObjectStreamingWriteGuard`, `OzoneOutputStream`, `OzoneDataStreamOutput`, `KeyMetadataAwareOutputStream`, `KeyMetadataAwareByteBufferStreamOutput`, and reflection over `writtenLength`.

## Control flow
Tests inject `IOException` and runtime exceptions from input reads and assert close fails with the original cause. A failing output stream verifies write failures do not advance written length. Early EOF copies fewer bytes and then fails content-length validation with `OS3Exception`. The datastream variant injects a ByteBuffer write failure and checks close blocking.

## State and persistence behavior
The guard tracks copied/written length and first transfer failure. Once a transfer fails, close must not commit the underlying key stream; instead it throws a commit-blocking exception with the original cause.

## Dependencies and integration points
This protects object PUT and UploadPart write paths, including streaming/datastream output wrappers from `OzoneBucketStub`.

## Risks and edge cases
The test uses test stub streams rather than real datanode streams. Reflection makes it sensitive to private field renaming.

## Test signals
Signals include exact propagated failures, blocked close message, preserved cause, zero written length after output failure, early EOF validation text, and write attempt counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestS3ObjectWriteGuard.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestS3Owner.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestS3Owner.java

## Purpose
Unit tests expected bucket owner validation for normal and copy operations.

## Important APIs, types, and functions
Exercises `S3Owner.hasBucketOwnershipVerificationConditions`, `verifyBucketOwnerCondition`, `verifyBucketOwnerConditionOnCopyOperation`, headers `EXPECTED_BUCKET_OWNER_HEADER` and `EXPECTED_SOURCE_BUCKET_OWNER_HEADER`, and error `BUCKET_OWNER_MISMATCH`.

## Control flow
Parameterized tests check when owner verification is enabled based on non-empty headers. Null headers and null server owner IDs are allowed. Direct bucket validation succeeds on matching owner and fails on mismatch. Copy validation checks source and destination owners independently and verifies the failing resource is the source or destination bucket.

## State and persistence behavior
No persistence. The state is request header values and server-known owner strings used to gate operations.

## Dependencies and integration points
These helpers are used by object and copy endpoints to implement AWS expected-owner guard headers.

## Risks and edge cases
The tests do not exercise full endpoint flows or real owner lookup. Empty-string handling is covered, but whitespace-only values are not.

## Test signals
Signals are boolean condition detection, absence of exceptions for disabled checks, and `OS3Exception` message/resource for owner mismatches.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestS3Owner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestUploadWithStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestUploadWithStream.java

## Purpose
Tests object upload through datastream-enabled S3 write paths.

## Important APIs, types, and functions
Uses `ObjectEndpointStreaming.put`, `ObjectEndpoint.isDatastreamEnabled`, `OZONE_FS_DATASTREAM_AUTO_THRESHOLD`, `HDDS_CONTAINER_RATIS_DATASTREAM_ENABLED`, `MultiDigestInputStream`, `FailingInputStream`, `AuditLogger.PerformanceStringBuilder`, and copy-source header handling.

## Control flow
Setup enables datastream and sets a one-byte auto threshold. Tests assert streaming is enabled, perform a normal PUT, directly invoke streaming PUT with a failing body and verify no key commit, and create a source stream key then copy it via `COPY_SOURCE_HEADER`.

## State and persistence behavior
Stub bucket state should contain keys only after successful uploads. A body read failure must leave no destination key. Copy via streaming path should persist a new key with the same data size as the source.

## Dependencies and integration points
This covers the S3 gateway streaming write implementation, Ozone datastream output, digest-wrapped input, conditional write parsing, and copy handling with streaming enabled.

## Risks and edge cases
The tests use stub streams and small content. They do not cover backpressure, large buffers, partial datanode failures, or checksum mismatch in datastream mode.

## Test signals
Signals are `isDatastreamEnabled`, successful PUT/copy, exact failure message `upload interrupted`, missing key after failure, and matching source/destination data sizes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestUploadWithStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/package-info.java

## Purpose
Package documentation marker for S3 endpoint unit tests.

## Important APIs, types, and functions
Declares package `org.apache.hadoop.ozone.s3.endpoint` and documents it as unit tests for REST endpoint implementations.

## Control flow
There is no executable control flow; Java compilers use this file for package-level documentation.

## State and persistence behavior
No runtime state or persistence behavior.

## Dependencies and integration points
The package contains tests for `RootEndpoint`, `BucketEndpoint`, `ObjectEndpoint`, endpoint helpers, multipart handling, tagging, permissions, and owner validation.

## Risks and edge cases
Risk is limited to stale documentation if package scope changes.

## Test signals
No tests run from this file; its signal is package-level organization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/exception/TestOS3Exceptions.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/exception/TestOS3Exceptions.java

## Purpose
Tests XML serialization for `OS3Exception`.

## Important APIs, types, and functions
Uses `S3ErrorTable.newError(S3ErrorTable.ACCESS_DENIED, "bucket")`, `OS3Exception.setRequestId`, `OzoneUtils.getRequestID`, and `OS3Exception.toXml()`.

## Control flow
The test creates an AccessDenied exception, assigns a request ID, serializes it to XML, formats the expected XML string with code, message, resource, and request ID, and asserts exact equality.

## State and persistence behavior
No persistence. Exception state includes code, message, resource, and request ID; serialization must be deterministic.

## Dependencies and integration points
S3 error responses returned by Jersey exception mappers or endpoints depend on this XML shape for client compatibility.

## Risks and edge cases
The exact-string assertion is sensitive to formatting changes. Escaping special XML characters in fields is not covered.

## Test signals
Passing means `toXml()` emits the expected XML declaration and `Error` body fields for a representative S3 error.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/exception/TestOS3Exceptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/exception/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/exception/package-info.java

## Purpose
Package documentation marker for S3 exception tests.

## Important APIs, types, and functions
Declares `org.apache.hadoop.ozone.s3.exception` and documents the package as tests for `OS3Exception`.

## Control flow
No executable control flow.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Supports organization of tests around S3 exception and error-table behavior.

## Risks and edge cases
Only documentation staleness is relevant.

## Test signals
No runtime test signal; package metadata only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/exception/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/metrics/TestS3GatewayMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/metrics/TestS3GatewayMetrics.java

## Purpose
Broad unit suite verifying `S3GatewayMetrics` success/failure counters and latency metric registration across bucket, object, multipart, copy, ACL, and tagging endpoints.

## Important APIs, types, and functions
Uses `S3GatewayMetrics` getters, `MetricsCollectorImpl`, `BucketEndpoint`, `RootEndpoint`, `ObjectEndpoint`, `EndpointTestUtils`, `OzoneClientStub`, `S3ErrorTable`, ACL fixture XML, and query params for ACL/list parts/multipart operations.

## Control flow
Setup creates a bucket/key fixture and endpoints sharing the same metrics instance. Each test snapshots a metric counter, performs a success or intentional failure, and asserts a delta of one. Covered paths include bucket head/list/get/create/delete, bucket ACL get/put, object head/get/put/delete, multipart initiate/abort/complete/upload-part/list-parts, copy object, and object tagging get/put/delete. The final test exports metrics and checks PutObjectAcl latency metric names are present.

## State and persistence behavior
Stub object-store state is mutated to trigger endpoint behavior. Metrics state is in-process counters and latency snapshots; each endpoint call should increment exactly the matching success or failure counter.

## Dependencies and integration points
This ties endpoint exception handling to metrics accounting and Hadoop metrics2 export.

## Risks and edge cases
Exact delta assertions can break when a single user request starts incrementing additional counters. The tests validate counters, not latency values.

## Test signals
Signals are one-count deltas for each metric getter, expected S3 errors on failures, successful response statuses, and exported latency metric names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/metrics/TestS3GatewayMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/package-info.java

## Purpose
Package documentation marker for broader S3 gateway bucket-related tests.

## Important APIs, types, and functions
Declares package `org.apache.hadoop.ozone.s3` and documents it as unit tests for bucket-related REST endpoints.

## Control flow
No executable control flow.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
The package also contains non-endpoint S3 gateway tests such as filters, authorization, signed/unsigned chunk streams, and digest streams.

## Risks and edge cases
Only documentation drift if package contents evolve.

## Test signals
No runtime test signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAWSSignatureProcessor.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAWSSignatureProcessor.java

## Purpose
Tests case-insensitive key behavior in the signature processor's lower-case header map.

## Important APIs, types, and functions
Uses `AWSSignatureProcessor.LowerCaseKeyStringMap.put`, `remove`, and `containsKey`.

## Control flow
The test inserts an `Authorization` header, removes it with uppercase `AUTHORIZATION`, and asserts the value is returned and lowercase lookup no longer exists.

## State and persistence behavior
State is an in-memory map normalized for HTTP header names. No persistence.

## Dependencies and integration points
Signature parsing and canonical request construction depend on case-insensitive header lookup/removal, especially for `Authorization`.

## Risks and edge cases
Only removal is tested; iteration order, duplicate puts, and mixed-case contains/get behavior are not covered here.

## Test signals
Passing means header removal is case-insensitive and removes the normalized entry.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAWSSignatureProcessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAuthorizationV2HeaderParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAuthorizationV2HeaderParser.java

## Purpose
Tests parsing of AWS Signature V2 authorization headers.

## Important APIs, types, and functions
Exercises `AuthorizationV2HeaderParser.parseSignature`, `SignatureInfo.getAwsAccessId`, `SignatureInfo.getSignature`, and `MalformedResourceException`.

## Control flow
The valid test parses `AWS accessKey:signature`. Invalid tests cover a non-AWS prefix returning null and malformed AWS headers with empty access key, empty signature, or missing signature throwing `MalformedResourceException`.

## State and persistence behavior
No persistent state. Parser output is a `SignatureInfo` object or null for unsupported algorithms.

## Dependencies and integration points
This is part of the S3 authentication filter path for legacy V2 signatures.

## Risks and edge cases
It does not cover access keys containing colons, whitespace variants, or canonical string generation.

## Test signals
Signals are parsed access key/signature values, null for unrelated scheme, and exceptions for malformed V2 headers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAuthorizationV2HeaderParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAuthorizationV4HeaderParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAuthorizationV4HeaderParser.java

## Purpose
Tests AWS Signature V4 `Authorization` header parsing and validation.

## Important APIs, types, and functions
Uses `AuthorizationV4HeaderParser.parseSignature`, `SignatureInfo`, `Credential`, `SignatureProcessor.DATE_FORMATTER`, and `MalformedResourceException`.

## Control flow
The suite parses well-formed headers, headers without spaces after commas, and headers with current/yesterday/tomorrow credential dates. Failure tests cover missing header parts, invalid credentials, date outside accepted range or wrong format, empty region/service/request segments, invalid request suffix, invalid signed headers, invalid/empty signatures, invalid algorithms, unsupported non-AWS4 schemes returning null, and malformed credential keys.

## State and persistence behavior
No persistence. Parser state is derived from header string and request date. Date validation depends on current local date through `LocalDate.now()`.

## Dependencies and integration points
This feeds S3 authentication, signature canonicalization, and credential-scope region/service extraction used elsewhere such as S3 Express directory bucket region handling.

## Risks and edge cases
Tests are date-relative and can be sensitive near midnight or timezone differences. They assert parser-level validation, not cryptographic signature verification.

## Test signals
Signals are exact `SignatureInfo` field values for valid headers, null for unsupported schemes, and `MalformedResourceException` for invalid V4 shapes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAuthorizationV4HeaderParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAuthorizationV4QueryParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAuthorizationV4QueryParser.java

## Purpose
Tests AWS Signature V4 presigned URL query parameter parsing and canonical string generation.

## Important APIs, types, and functions
Uses `AuthorizationV4QueryParser.parseSignature`, `StringToSignProducer.createSignatureBase`, `AWSSignatureProcessor.LowerCaseKeyStringMap`, SHA-256 `MessageDigest`, and `MalformedResourceException`.

## Control flow
Validation tests mutate a parameter map to cover missing/empty/invalid algorithm, date, expires, credential, signed headers, and signature. Expiry bounds cover invalid zero, more than seven days, and expired requests. A valid unexpired parameter set must parse. The AWS example test overrides date validation, parses credentials, sets URI/header state, builds the canonical request hash, and asserts the string-to-sign matches the expected form.

## State and persistence behavior
No persistent state. Query parser output captures access ID, date, region, service, signed headers, and signature. Validation depends on current timestamp for expiry checks.

## Dependencies and integration points
This protects presigned URL authentication and canonical request construction for S3 gateway requests.

## Risks and edge cases
Date-relative tests can be time-sensitive. The invalid credential section starts with an invalid algorithm in the map, so some failures may be caught before credential validation.

## Test signals
Signals are exceptions for malformed query auth, successful parse for unexpired headers, and exact AWS-style string-to-sign equality.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAuthorizationV4QueryParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestStringToSignProducer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestStringToSignProducer.java

## Purpose
Tests Signature V4 canonical request and string-to-sign generation plus required header validation.

## Important APIs, types, and functions
Uses `StringToSignProducer.createSignatureBase`, `AuthorizationV4HeaderParser`, `SignatureInfo`, `LowerCaseKeyStringMap`, `HeaderPreprocessor.ORIGINAL_CONTENT_TYPE`, mocked `ContainerRequestContext`/`UriInfo`, `S3_AUTHINFO_CREATION_ERROR`, and SHA-256 hashing.

## Control flow
The main test constructs headers, fixes original content type, builds a known canonical request for `GET /buckets`, hashes it, and asserts the produced string-to-sign. Parameterized request-header validation covers missing/invalid/expired/future `X-Amz-Date` and missing `X-Amz-Content-Sha256`. Canonical-header validation covers missing `host`, missing signed `x-amz-security-token`, and signed headers absent from request headers.

## State and persistence behavior
No persistence. Header maps are normalized and may be adjusted by `fixContentType`; generated signature base depends on request URI, method, query parameters, credential scope, and canonical headers.

## Dependencies and integration points
This is core to S3 request authentication and depends on JAX-RS request context data and header preprocessing.

## Risks and edge cases
The tests cover simple URI/query cases, not complex percent encoding, duplicate query parameters, or multi-value signed headers.

## Test signals
Signals are exact string-to-sign equality and expected `S3_AUTHINFO_CREATION_ERROR` codes for invalid header/canonical-header cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestStringToSignProducer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestContinueToken.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestContinueToken.java

## Purpose
Tests round-trip encoding/decoding of S3 continuation tokens.

## Important APIs, types, and functions
Uses `ContinueToken`, `encodeToString`, `decodeFromString`, `equals`, and `OS3Exception`.

## Control flow
Four tests create tokens with key plus directory, non-English key with null directory, non-English key and directory, and key with null directory. Each encodes to a string, decodes, and asserts equality with the original token.

## State and persistence behavior
No persistent state. Token contents must be serialized in a reversible form, including null directory values and non-ASCII characters.

## Dependencies and integration points
Continuation tokens are used by S3 list operations to resume pagination without exposing raw internal cursor structure.

## Risks and edge cases
The tests do not cover invalid token strings, tampering, empty key values, or compatibility with older token formats.

## Test signals
Passing means encoded tokens round-trip exactly for ASCII, non-English, and null-directory cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestContinueToken.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestRFC1123Util.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestRFC1123Util.java

## Purpose
Tests RFC1123 date parser/formatter leniency for one-digit day values.

## Important APIs, types, and functions
Uses `RFC1123Util.FORMAT.parse` and `RFC1123Util.FORMAT.format` over a `TemporalAccessor`.

## Control flow
The test parses `Mon, 5 Nov 2018 15:04:05 GMT`, formats it back, and asserts the normalized two-digit day form `Mon, 05 Nov 2018 15:04:05 GMT`.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
RFC1123 parsing is used by S3 conditional headers such as `If-Modified-Since`, `If-Unmodified-Since`, and copy-source timestamp conditions.

## Risks and edge cases
Only one one-digit-day example is covered. Other HTTP date variants, invalid zones, leap seconds, and locale issues are not tested here.

## Test signals
Passing means the formatter accepts a one-digit day and emits normalized RFC1123 output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestRFC1123Util.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestRangeHeaderParserUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestRangeHeaderParserUtil.java

## Purpose
Tests S3/HTTP byte range header parsing.

## Important APIs, types, and functions
Uses `RangeHeaderParserUtil.parseRangeHeader`, `RangeHeader.getStartOffset`, `getEndOffset`, `isReadFull`, and `isInValidRange`.

## Control flow
One test method checks normal ranges, same start/end, invalid range beyond file length, reversed ranges that fall back to full read, wrong range units, malformed negative ranges, suffix ranges, suffix longer than file length, and large long-valued ranges.

## State and persistence behavior
No persistence. Parser returns a value object describing either a bounded range, full-read fallback, or invalid range.

## Dependencies and integration points
Object GET uses this parser to set read offsets, `Content-Range`, and partial-content status.

## Risks and edge cases
Multi-range headers, whitespace variants, open-ended large ranges, and zero-length objects are not covered.

## Test signals
Signals are exact start/end offsets, full-read flags, invalid-range flags, and support for offsets above 32-bit integer range.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestRangeHeaderParserUtil.java -->
