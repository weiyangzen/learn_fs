## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/acl/SupportedHdfsAclProvider.java

### Purpose
`SupportedHdfsAclProvider` implements real HDFS ACL read/write support for Hadoop versions with ACL APIs.

### Important APIs, Types, And Functions
`getAcl` calls `FileSystem.getAclStatus`, converts HDFS ACL entries into Alluxio `AccessControlList` and `DefaultAccessControlList`, and returns null default ACL for files. `setAclEntries` converts Alluxio ACL entries to Hadoop ACL entries and calls `FileSystem.setAcl`. Helper methods translate entry types and permissions.

### Control Flow
For reads, the provider checks whether the path is a directory, retrieves ACL status, sets owner/group, iterates entries, maps scopes to access/default ACL, and returns the pair. `AclException` from disabled NameNode ACLs returns nulls. For writes, every Alluxio entry is converted and passed as a full ACL spec.

### State, Persistence, And Dependencies
The class is stateless. Persistent effects are HDFS ACL mutations. It depends on Hadoop ACL APIs, Alluxio ACL models, and HDFS `AclException`.

### Integration Points
`HdfsUnderFileSystem` loads this class reflectively when present and delegates ACL methods to it.

### Risks
Permission conversion uses an `if/else if` chain on `FsAction.implies`, so combined permissions may only add the first matching action rather than all implied actions. UnsupportedOperationException on `setAcl` is swallowed, which can hide write failures on unsupported filesystems.

### Test Signals
No direct tests in this subset cover ACL translation. Tests should cover all FsAction combinations, named and unnamed entries, default ACLs on directories, files with null default ACL, disabled ACLs, and write conversion.
