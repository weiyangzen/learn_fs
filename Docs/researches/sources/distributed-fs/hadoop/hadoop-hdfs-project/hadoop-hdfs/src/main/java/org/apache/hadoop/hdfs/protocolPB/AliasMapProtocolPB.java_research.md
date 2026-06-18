# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/AliasMapProtocolPB.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocolPB/AliasMapProtocolPB.java

Purpose: protobuf RPC interface for the NameNode/DataNode alias map used by Provided storage. It extends `AliasMapProtocolProtos.AliasMapProtocolService.BlockingInterface`.

Important API: the interface carries `@ProtocolInfo` with protocol name `org.apache.hadoop.hdfs.server.aliasmap.AliasMapProtocol`, version 1, and `@KerberosInfo` using the NameNode principal. It is marked private and unstable.

Control flow and state: no implementation. Hadoop RPC uses the annotations and inherited protobuf blocking methods to bind clients and server-side translators.

Dependencies and integration: depends on generated alias map protobuf service, `DFSConfigKeys`, Hadoop IPC protocol metadata, and security annotations. It is consumed by `AliasMapProtocolServerSideTranslatorPB` and `InMemoryAliasMapProtocolClientSideTranslatorPB`.

Risks and test signals: protocol-name, version, or Kerberos principal changes can break wire compatibility or secure RPC setup. Tests should cover alias map proxy creation and basic read/write/list/getBlockPoolId calls through the PB translators.
