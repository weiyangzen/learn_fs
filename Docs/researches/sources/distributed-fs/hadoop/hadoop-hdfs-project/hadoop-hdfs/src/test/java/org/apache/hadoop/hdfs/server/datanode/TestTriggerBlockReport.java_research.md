# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestTriggerBlockReport.java

Purpose: This HA integration test verifies manual DataNode block-report triggering for full versus incremental reports and for all NameNodes versus one specified NameNode.

Important APIs/types/functions: `DataNode.triggerBlockReport`, `BlockReportOptions.Factory`, `MiniDFSNNTopology.simpleHATopology`, `InternalDataNodeTestUtils.spyOnBposToNN`, `StorageBlockReport`, `StorageReceivedDeletedBlocks`, `IbrManager.addRDBI`, and `DatanodeProtocolClientSideTranslatorPB`.

Control flow: The helper configures very long automatic block-report and heartbeat intervals, starts a one-DataNode HA cluster, spies on both NameNode protocol proxies, creates a file and waits for the initial IBR to both NameNodes, verifies no automatic full reports follow, injects a fake deleted-block IBR into each BP service actor, and calls `triggerBlockReport` with incremental/full and optional target NameNode address. Tests run all four combinations.

State and persistence behavior: The file creates one HDFS file and mutates each actor’s IBR queue with a synthetic deleted block. Report routing is asynchronous and uses DataNode’s internal BPOS state.

Dependencies and integration points: It covers client-facing block-report admin options, HA NameNode routing, BP service actor IBR queues, and DataNode protocol RPCs.

Risks and test signals: Signals are exact Mockito counts on full and incremental RPCs. Risks include long timeout reliance, asynchronous trigger return, and target-address matching against service RPC address.
