# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_grantee_group.go

Purpose: defines AWS S3 predefined grantee group URIs and validates group URIs.

Important APIs and values: `GranteeGroupAllUsers`, `GranteeGroupAuthenticatedUsers`, and `GranteeGroupLogDelivery` are package variables. `ValidateGroup` returns true for exactly those three group URIs.

Control flow: `ValidateGroup` uses a switch over known group constants and returns false by default.

State and persistence: package-level mutable string variables only; no persistence.

Dependencies and integration: used by ACL parsing/validation and canned ACL grant construction.

Risks: variables are mutable rather than constants, so package-local or external mutation could corrupt validation. Validation is exact string matching and does not normalize URI variants.

Test signals: no direct tests in this subset.
