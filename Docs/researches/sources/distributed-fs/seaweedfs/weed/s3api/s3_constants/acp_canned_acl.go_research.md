# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_canned_acl.go

Purpose: defines S3 canned ACL names and prebuilt grant lists for common canned ACLs.

Important APIs and values: constants include `CannedAclPrivate`, `CannedAclPublicRead`, `CannedAclPublicReadWrite`, `CannedAclAuthenticatedRead`, `CannedAclLogDeliveryWrite`, `CannedAclBucketOwnerRead`, `CannedAclBucketOwnerFullControl`, and `CannedAclAwsExecRead`. Grant variables include `PublicRead`, `PublicReadWrite`, `AuthenticatedRead`, and `LogDeliveryWrite`.

Control flow: no functions. Grant slices are constructed from AWS SDK `s3.Grant` and `s3.Grantee` values using group URI/type/permission constants from sibling files.

State and persistence: package-level mutable slices of pointers; no persistence.

Dependencies and integration: used by ACL handling to translate canned ACL headers into grant sets. Depends on AWS SDK S3 structs and constants from ACP grantee/permission files.

Risks: grant slices are mutable globals; callers should not modify them in place. Some canned ACL constants have no prebuilt grant list here and must be handled elsewhere or treated as unsupported/default.

Test signals: no direct tests in this subset.
