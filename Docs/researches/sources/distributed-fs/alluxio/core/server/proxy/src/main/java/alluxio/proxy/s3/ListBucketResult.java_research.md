# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ListBucketResult.java

## Purpose
`ListBucketResult` builds the XML response for S3 ListObjects and ListObjectsV2. It filters Alluxio child statuses by prefix, marker or continuation token, delimiter, start-after, and max-keys, then formats contents, common prefixes, truncation flags, and next tokens.

## Important APIs, Types, and Functions
The main constructor accepts bucket name, child `URIStatus` list, and `ListBucketOptions`. Core helpers are `buildListBucketResult`, `isVersion2`, `encodeToken`, and `decodeToken`. Response accessors expose `Name`, `KeyCount`, `MaxKeys`, `IsTruncated`, `Prefix`, `Delimiter`, `EncodingType`, `Marker`, `NextMarker`, `ContinuationToken`, `NextContinuationToken`, `StartAfter`, repeated `Contents`, and repeated `CommonPrefixes`. Nested DTOs are `CommonPrefix` and `Content`.

## Control Flow, State, and Persistence
Construction validates non-empty bucket name and non-negative max keys, initializes v1 or v2 fields, handles `maxKeys == 0`, and builds results from sorted children. The builder strips the bucket prefix from each status path, applies prefix/marker/start-after filters, converts folders to keys with trailing slash and size `0`, rolls keys into unique common prefixes when delimiter is set, counts both contents and common prefixes against `maxKeys`, and marks truncation when the count limit is hit. URL encoding is applied to keys, common prefixes, and start-after when encoding type is `"url"`. V2 continuation tokens encode the last marker as hex plus a SHA-256 digest separated by `-`.

## Dependencies and Integration Points
The class integrates Alluxio `URIStatus` with S3 XML response semantics, S3 date formatting, Apache Commons Hex/Digest/StringUtils, Java URL encoding, and Jackson XML/JSON inclusion annotations.

## Risks
The stream uses `.limit(mMaxKeys + 1)` after filtering that already flips truncation when `keyCount == maxKeys`; edge cases around exactly `maxKeys` versus more than `maxKeys` require careful tests. URL encoding uses `URLEncoder`, which encodes spaces as `+` and may not match all S3 expectations. Continuation tokens are reusable and not session-bound by design TODO. Delimiter support assumes string matching and comments note only `/` is effectively supported. The constructor mutates the supplied `children` list by sorting it.

## Test Signals
Important tests include empty bucket names, negative and zero max keys, v1 marker pagination, v2 continuation token pagination and invalid token rejection, prefix filtering, delimiter common-prefix grouping, URL encoding, folder key formatting, truncation flags, and key-count sanity checks.
