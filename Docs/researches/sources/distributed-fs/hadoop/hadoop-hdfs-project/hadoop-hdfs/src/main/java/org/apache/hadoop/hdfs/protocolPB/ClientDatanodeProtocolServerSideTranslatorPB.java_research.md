# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/ClientDatanodeProtocolServerSideTranslatorPB.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/ClientDatanodeProtocolServerSideTranslatorPB.java

Purpose: server-side translator for client-to-DataNode administrative and diagnostic RPCs, forwarding `ClientDatanodeProtocolPB` calls to `ClientDatanodeProtocol`.

Important APIs: handles replica length, local path lookup, refresh/delete/shutdown/evict, DataNode info, reconfiguration operations, block report trigger, balancer bandwidth, disk balancer plan submit/cancel/query/settings, and volume report. It builds protobuf responses from native values such as `BlockLocalPathInfo`, `DatanodeVolumeInfo`, `DiskBalancerWorkStatus`, and reconfiguration status.

Control flow and state: holds only the `impl` delegate and cached empty response protos. Each RPC converts request fields, invokes the delegate, and wraps `IOException` or disk-balancer `Exception` in `ServiceException`.

Dependencies and integration: depends on `PBHelperClient`, `ReconfigurationProtocolServerSideUtils`, `BlockReportOptions`, `NetUtils`, and generated `ClientDatanodeProtocolProtos`.

Risks and test signals: optional disk-balancer fields default to version 1, empty plan file, and false ignore-date-check. `triggerBlockReport` parses an optional NameNode address. Tests should cover default optional fields, volume report conversion, disk-balancer exception wrapping, and reconfiguration response parity.
