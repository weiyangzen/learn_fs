<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAclTransformation.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAclTransformation.java

Purpose: pure unit tests for `AclTransformation` algorithms, cross-validated against Linux ACL behavior, covering removal/filter, default filtering, merge, and replace semantics.

Important APIs/types/functions: statically imports `AclTransformation.filterAclEntriesByAclSpec()`, `filterDefaultAclEntries()`, `mergeAclEntries()`, and `replaceAclEntries()`. Test data uses `AclEntry`, scopes `ACCESS`/`DEFAULT`, entry types `USER`/`GROUP`/`MASK`/`OTHER`, and `AclTestHelpers.aclEntry()`.

Control flow: each test builds immutable existing ACL lists, mutable ACL specs, expected lists, and compares transformation output or asserts `AclException`. The suite enumerates unchanged paths, entry removal, named user/group ordering, access and default mask recalculation/preservation, automatic default base entries, empty specs, input/result size limits, duplicate entries, named mask/other rejection, and missing required base entries for replace.

State and persistence: no filesystem or NameNode state is used. State is local Java ACL lists only.

Dependencies and integration points: directly validates the transformation layer consumed by NameNode ACL mutation operations before metadata is persisted to inodes.

Risks and test signals: risks are subtle POSIX ACL compatibility regressions: wrong ordering, mask calculation, default ACL completion, duplicate detection, or maximum-entry enforcement. Signals are exact list equality and expected `AclException` on invalid ACL specs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAclTransformation.java -->
