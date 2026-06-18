# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/ReconfigurationProtocolServerSideUtils.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/ReconfigurationProtocolServerSideUtils.java

Purpose: shared server-side helpers for serializing reconfiguration properties and task status into protobuf responses.

Important APIs: `listReconfigurableProperties(List<String>)` adds property names to the response. `getReconfigurationStatus(ReconfigurationTaskStatus)` sets start time, and when stopped sets end time plus one config-change proto per `PropertyChange`, including name, old value, optional new value, and optional error message.

Control flow and state: final utility class with private constructor; no mutable state. Status conversion branches on `status.stopped()` and asserts that stopped tasks have a non-null status map.

Dependencies and integration: consumed by reconfiguration server translators including client-DataNode and generic reconfiguration paths. Depends on Hadoop `ReconfigurationTaskStatus`, `PropertyChange`, Java `Optional`, and generated reconfiguration protos.

Risks and test signals: null old values become empty strings, while null new values are omitted. Error strings may contain full stack traces. Tests should verify running/stopped task encoding, null old/new value semantics, error propagation, and deterministic change counts.
