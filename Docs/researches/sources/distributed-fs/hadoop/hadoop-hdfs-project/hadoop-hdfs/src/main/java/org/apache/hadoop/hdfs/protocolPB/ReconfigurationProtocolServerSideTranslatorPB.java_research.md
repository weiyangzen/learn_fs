# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/ReconfigurationProtocolServerSideTranslatorPB.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/ReconfigurationProtocolServerSideTranslatorPB.java

Purpose: server-side translator for generic `ReconfigurationProtocolPB` calls to a native `ReconfigurationProtocol` implementation, used by NN/DN runtime reconfiguration endpoints.

Important APIs: `startReconfiguration`, `listReconfigurableProperties`, and `getReconfigurationStatus`. The list/status methods delegate response construction to `ReconfigurationProtocolServerSideUtils`.

Control flow and state: stores only the delegate and a cached empty start response. Each RPC calls the corresponding implementation method and wraps `IOException` in `ServiceException`.

Dependencies and integration: depends on `ReconfigurationProtocol`, generated reconfiguration protos, protobuf RPC types, and the utility class that serializes status and property-change results.

Risks and test signals: behavior relies on utility conversion preserving stopped/running status, start/end times, and error messages. Tests should cover start success/failure, property list conversion, running status without end time, stopped status with per-property successes/errors, and exception wrapping.
