# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_grantee_type.go

Purpose: centralizes S3 ACL grantee type strings.

Important APIs and values: package variables `GrantTypeCanonicalUser`, `GrantTypeAmazonCustomerByEmail`, and `GrantTypeGroup`.

Control flow: no functions.

State and persistence: mutable package variables only.

Dependencies and integration: consumed by canned ACL grants and ACL XML/parsing logic elsewhere.

Risks: because these are variables, accidental mutation can affect ACL serialization and validation globally.

Test signals: no direct tests in this subset.
