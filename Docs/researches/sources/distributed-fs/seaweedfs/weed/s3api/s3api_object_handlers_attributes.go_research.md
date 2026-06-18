# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_attributes.go

## Purpose
Implements `GetObjectAttributes`, returning selected object metadata such as ETag, storage class, object size, and multipart part information. It supports versioned object resolution, delete marker handling, conditional read headers, and object-parts pagination.

## Important APIs, Types, And Functions
Response model types are `GetObjectAttributesResponse`, `ObjectAttributesChecksum`, `ObjectAttributesParts`, and `ObjectAttributesPart`. Helpers are `parseObjectAttributes`, `validateObjectAttributes`, `GetObjectAttributesHandler`, and `buildObjectAttributesParts`. The handler uses `isVersioningConfigured`, `getSpecificObjectVersion`, `getLatestObjectVersion`, `getEntry`, `fetchObjectEntry`, `parseConditionalHeaders`, `validateConditionalHeadersForReads`, `getObjectETag`, and multipart `PartBoundaryInfo` metadata.

## Control Flow
The handler parses `X-Amz-Object-Attributes` values into a set and rejects empty or unknown attributes. It parses `X-Amz-Max-Parts` and `X-Amz-Part-Number-Marker`, clamps max parts to 1000, and rejects negative or malformed values. It resolves requested `versionId`, latest version, or null version using the same `.versions` quick-check pattern as GET/HEAD. Delete markers set `x-amz-delete-marker: true` and return `NoSuchKey`; successful versioned lookups set `x-amz-version-id`. Conditional headers are evaluated against the resolved entry. The response includes only requested attributes: ETag without quotes, storage class defaulting to `STANDARD`, object size from attributes, and object parts from stored boundaries. Checksum is accepted but intentionally omitted because S3 checksum storage is not yet represented here.

## State And Persistence
The handler is read-only. It reads entry attributes, chunks, and extended metadata including storage class, delete marker, version id, multipart part boundaries, and multipart part count. It writes HTTP headers, clears `Content-Type`, and emits XML.

## Dependencies And Integration Points
This file integrates S3 object attributes API constants, versioning layout, conditional-header evaluation, multipart upload metadata stored in entry `Extended`, and common success/error writers.

## Risks And Test Signals
Risks include divergent version resolution from GET/HEAD, part-size calculation errors when boundary indexes drift from chunks, accepting checksum requests without values, and pagination edge cases for `NextPartNumberMarker` when truncation occurs. Useful tests should cover invalid attributes, malformed pagination headers, delete markers, null versions, conditional failures, storage class metadata, multipart boundaries spanning multiple chunks, and marker/max-parts truncation.
