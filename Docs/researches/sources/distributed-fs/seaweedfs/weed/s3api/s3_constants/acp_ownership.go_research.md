# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_ownership.go

Purpose: defines S3 object ownership modes and validates configured ownership strings.

Important APIs and values: `OwnershipBucketOwnerPreferred`, `OwnershipObjectWriter`, `OwnershipBucketOwnerEnforced`, `DefaultOwnershipForCreate`, `DefaultOwnershipForExists`, and `ValidateOwnership`.

Control flow: `ValidateOwnership` rejects empty strings and any value outside the three known ownership modes.

State and persistence: mutable package-level strings only. Actual ownership persistence is outside this file.

Dependencies and integration: used by bucket ACL/object ownership handling and metadata defaults.

Risks: defaults differ for newly created versus existing buckets, so migration paths must choose the correct default. Variables are mutable.

Test signals: no direct tests in this subset.
