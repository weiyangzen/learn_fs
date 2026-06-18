# sources/control-plane/rook/pkg/operator/ceph/object/bucket.go

## Purpose
`bucket.go` exposes object package helpers for reading RGW bucket metadata and usage statistics through `radosgw-admin`, returning Rook-friendly bucket structs and RGW error codes.

## Important APIs, Types, and Functions
`ObjectBucketMetadata` stores owner and creation time. `ObjectBucketStats` stores total size and object count. `ObjectBucket` combines name, metadata, and stats. `rgwBucketStats` mirrors the subset of `bucket stats` JSON needed by Rook. `bucketStatsFromRGW()` sums usage categories. `GetBucketStats()`, `getBucketMetadata()`, and `GetBucket()` are the exported/internal lookup flow.

## Control Flow, State, and Persistence
`GetBucketStats()` runs `radosgw-admin bucket stats --bucket <name>` through `runAdminCommand`, treats `exit status 2` as not found, unmarshals usage, and sums all usage entries. `getBucketMetadata()` runs `metadata get bucket:<name>`, detects the RGW "can't get key" not-found text, extracts JSON, unmarshals owner and `creation_time`, and parses it using nanosecond UTC layout. `GetBucket()` first gets stats, then metadata, and maps not-found or unknown failures to RGW error codes. It only reads RGW state; it does not persist changes.

## Dependencies and Integration Points
The file depends on the admin command helpers in `admin.go`, JSON unmarshalling, time parsing, and package RGW error constants. It is useful to code paths that need bucket inspection without using S3 or go-ceph Admin Ops bucket APIs.

## Risks
Not-found detection is string based: `exit status 2` and "can't get key" could change across Ceph versions or localization. `getBucketMetadata()` reports command errors as "failed to list buckets", which is misleading for metadata get failures. The time layout requires a specific fractional UTC format. Stats summing assumes all usage categories should be aggregated and does not validate that returned bucket name matches the requested bucket.

## Test Signals
No direct test for this file is in the requested set. Related admin tests cover JSON extraction, but bucket-specific stats/metadata parsing, not-found mapping, date parsing, and multi-category summing would benefit from dedicated unit tests with mocked `runAdminCommand` behavior.
