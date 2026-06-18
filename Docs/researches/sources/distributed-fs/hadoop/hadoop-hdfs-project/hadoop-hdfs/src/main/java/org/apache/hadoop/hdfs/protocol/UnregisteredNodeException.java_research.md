# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/UnregisteredNodeException.java

Purpose: Reports attempts by unregistered NameNode-adjacent servers or DataNodes to access the NameNode, including storage UUID conflicts where a different DataNode claims an existing storage identity.

Important APIs and types: Constructors accept `JournalInfo`, `NodeRegistration`, or a conflicting `DatanodeID` plus stored `DatanodeInfo`, and format diagnostic messages.

Control flow: No custom flow beyond selecting the message for each registration failure case.

State and persistence behavior: Exception state is diagnostic text and stack trace. No registration state is changed by the exception itself.

Dependencies and integration points: Depends on `JournalInfo`, `NodeRegistration`, `DatanodeID`, and `DatanodeInfo`. Used by NameNode registration, heartbeat, block report, and journal protocol validation.

Risks: Message construction exposes node identifiers and must be accurate for operators diagnosing duplicate UUID/storage conflicts. Generic IOException handling may obscure registration-specific remediation.

Test signals: Tests should attempt unregistered journal/node access, duplicate DataNode UUID/storage reporting, and verify exception messages and RPC propagation.
