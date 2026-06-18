<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestAnnotations.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestAnnotations.java

Purpose: Ensures every public method exposed through `NamenodeProtocols` has retry semantics annotations.

Important APIs/types/functions: Reflection over `NamenodeProtocols.class.getMethods`, `Idempotent`, and `AtMostOnce`.

Control flow: Single test iterates all public protocol methods and asserts each has either `@Idempotent` or `@AtMostOnce`.

State and persistence behavior: No mutable state or persistence. It is a static API contract check.

Dependencies and integration points: Guards NameNode RPC protocol declarations used by Hadoop IPC retry handling.

Risks: Reflection includes inherited public methods from the protocol aggregate, so newly added public methods must be annotated immediately. The test does not validate annotation correctness, only presence.

Test signals: Passing means protocol retry metadata is complete for all public NameNode protocol methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestAnnotations.java -->
