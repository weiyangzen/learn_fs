# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/extend_key.go

Purpose: defines SeaweedFS extended metadata keys for S3 ownership, ACL, versioning, multipart, lifecycle, checksums, bucket policy, and object lock/retention/legal hold.

Important APIs and values: keys include owner/ACL/ownership/version IDs/delete markers/latest-version cache fields, multipart key, noncurrent lifecycle timestamp, lifecycle TTL fast-path flag, checksum metadata, `ExtBucketPolicyKey`, object lock retention/legal hold keys, and object-lock configuration component keys. It also defines retention modes, legal hold values, object lock enabled status, and bucket versioning statuses.

Control flow: no functions.

State and persistence: these constants are the persistence contract for entry extended attributes and bucket metadata fields.

Dependencies and integration: used throughout S3 metadata storage, versioning, lifecycle, checksum, bucket policy, multipart, and object lock code.

Risks: renaming or changing any key can orphan existing metadata or break backward compatibility. Several keys are optimized caches, so writers and readers must keep them consistent.

Test signals: no direct tests in this subset, but policy and existing-object-tag tests rely on extended metadata patterns in adjacent constants.
