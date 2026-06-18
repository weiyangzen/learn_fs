# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_retention.go

## Purpose

This implementation file provides S3 Object Lock retention, legal hold, and bucket Object Lock configuration helpers.

## Important APIs, Types, and Functions

Key types are `ObjectRetention`, `ObjectLegalHold`, `ObjectLockConfiguration`, `ObjectLockRule`, and `DefaultRetention`. Important functions include XML parsers, object entry lookup, retention/legal-hold getters and setters, metadata extractors, governance bypass authorization, enforcement, and availability checks.

## Control Flow

XML parsing uses a generic decoder. Object lookup selects a specific version, latest version, or regular object depending on `versionId` and bucket versioning. Setters resolve the target path, validate existing retention restrictions, mutate extended metadata, and persist with `mkFile`. Enforcement skips unlocked buckets, loads the target entry, tolerates not-found deletes, rejects active legal hold and compliance retention, and requires prevalidated governance bypass for governance retention.

## State and Persistence Behavior

Object Lock state is stored in `filer_pb.Entry.Extended`: mode, retain-until Unix timestamp, legal hold, default-retention config, and version metadata. `setObjectRetention` also updates `WormEnforcedAtTsNs`. Full extended-map rewrites can race with concurrent metadata updates.

## Dependencies and Integration Points

The file depends on filer entries, S3 constants/errors, IAM authorization, bucket versioning, version lookup helpers, `mkFile`, logging, and object-lock REST/delete/overwrite paths.

## Risks and Edge Cases

Risks include corrupted timestamps, concurrent metadata rewrites, governance bypass policy drift, versioned/null/unversioned lookup differences, and wall-clock active-retention decisions.

## Test Signals

Companion tests cover XML parsing, validation, default retention, header round trips, and stale day/year cleanup; real handler/IAM/concurrency tests remain important.
