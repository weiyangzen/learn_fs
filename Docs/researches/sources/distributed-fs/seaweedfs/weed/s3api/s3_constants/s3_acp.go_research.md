# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/s3_acp.go

Purpose: defines canonical account IDs used by S3 ACP/ACL logic.

Important APIs and values: `AccountAnonymousId = "anonymous"` and `AccountAdminId = "admin"`.

Control flow: no functions.

State and persistence: constants only.

Dependencies and integration: consumed by ACL/account ownership code to represent anonymous and admin principals.

Risks: changing these constants changes identity semantics for ACLs and possibly persisted ownership data.

Test signals: no direct tests in this subset.
