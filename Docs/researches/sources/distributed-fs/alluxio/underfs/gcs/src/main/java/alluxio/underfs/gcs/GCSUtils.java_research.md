## sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSUtils.java

### Purpose
`GCSUtils` converts jets3t GCS bucket ACL grants into Alluxio owner-mode bits.

### Important APIs, Types, And Functions
`translateBucketAcl(GSAccessControlList, String)` returns a POSIX-style `short` mode. It checks grants for read, write, and full-control permissions. `isUserIdInGrantee` treats the configured owner id, all-users group, and authenticated-users group as matches.

### Control Flow
The method iterates every ACL grant. Read grants add owner read and execute bits, write grants add owner write, and full-control grants add owner read/write/execute. Unsupported ACL permissions such as READ_ACP do not change mode.

### State, Persistence, And Dependencies
There is no retained state. It depends on jets3t ACL types and Alluxio callers that interpret the returned mode.

### Integration Points
`GCSUnderFileSystem.getPermissionsInternal` uses this helper when it can fetch the bucket ACL, falling back to default mode when ACL inheritance fails.

### Risks
Group grants are translated into owner permission bits, not group/other bits, because the GCS UFS has no group model. The helper trusts non-null ACL and grantee identifiers.

### Test Signals
`GCSUtilsTest` covers user, all-users, and authenticated-users grants for read, write, and full control, including nonmatching user ids and ignored READ_ACP.
