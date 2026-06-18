# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ListAllMyBucketsResult.java

## Purpose
`ListAllMyBucketsResult` is the XML response model for listing S3 buckets. It converts Alluxio `URIStatus` entries into S3 bucket name and creation-date elements.

## Important APIs, Types, and Functions
The constructor accepts a list of `URIStatus` objects and maps each to a nested `Bucket`. `getBuckets` serializes as XML `Buckets` containing repeated `Bucket` elements. Each `Bucket` exposes `Name` and `CreationDate`.

## Control Flow, State, and Persistence
Construction streams over statuses, using `URIStatus.getName` and `getCreationTimeMs`, converting timestamps through `S3RestUtils.toS3Date`. State is the in-memory bucket list only.

## Dependencies and Integration Points
It integrates Alluxio filesystem status objects with S3 bucket-list XML serialization through Jackson.

## Risks
There is no default constructor, so this is response-only. The nested `Bucket` is a non-static inner class, which carries an implicit reference to the outer result. Creation date accuracy depends on `URIStatus` values supplied by the caller.

## Test Signals
Signals should verify bucket list XML structure, timestamp formatting, empty-list behavior, and mapping of Alluxio directory statuses to bucket names.
