<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestAclCLIWithPosixAclInheritance.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestAclCLIWithPosixAclInheritance.java

Purpose: Repeats the ACL CLI suite with POSIX ACL inheritance enabled.
Important APIs/types/functions: `TestAclCLIWithPosixAclInheritance` extends `TestAclCLI`, overrides `initConf()` and `getTestFile()`, and exposes `testAll()`.
Control flow: It calls the parent ACL configuration, flips `DFS_NAMENODE_POSIX_ACL_INHERITANCE_ENABLED_KEY` to true, and runs `testAclCLIWithPosixAclInheritance.xml` through the inherited cluster and command execution flow.
State and persistence behavior: Uses the parent cluster/FS fields; persistent effects are only transient ACL namespace changes inside MiniDFSCluster.
Dependencies and integration points: Depends on the parent ACL CLI harness and the POSIX ACL inheritance NameNode option.
Risks and edge cases: Regression risk is that parent setup changes could accidentally override the inheritance flag. XML expectations must track inheritance semantics exactly.
Test signals: Signals are XML expectations that default ACL inheritance follows POSIX rules under the enabled flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestAclCLIWithPosixAclInheritance.java -->
