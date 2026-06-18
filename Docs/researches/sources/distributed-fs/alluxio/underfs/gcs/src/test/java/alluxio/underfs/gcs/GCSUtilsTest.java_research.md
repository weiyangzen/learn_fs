## sources/distributed-fs/alluxio/underfs/gcs/src/test/java/alluxio/underfs/gcs/GCSUtilsTest.java

### Purpose
`GCSUtilsTest` verifies translation from jets3t GCS ACL grants to Alluxio owner-mode bits.

### Important APIs, Types, And Functions
Setup builds a `GSAccessControlList` and a canonical user grantee. Tests call `GCSUtils.translateBucketAcl` with matching and nonmatching user ids and with group grantees.

### Control Flow
Each test grants one or more permissions and asserts the expected octal mode. Read maps to `0500`, write to `0200`, read plus write to `0700`, and full control to `0700`.

### State, Persistence, And Dependencies
The ACL is in-memory only. Dependencies are JUnit and jets3t ACL classes.

### Integration Points
This test protects `GCSUnderFileSystem` permission inheritance from bucket ACLs.

### Risks
It does not cover null grantees, null ACLs, duplicate grants beyond simple OR behavior, or interaction with configured default modes.

### Test Signals
Passing tests show that user, all-users, and authenticated-users ACL grants are treated as owner permissions as intended by the GCS UFS.
