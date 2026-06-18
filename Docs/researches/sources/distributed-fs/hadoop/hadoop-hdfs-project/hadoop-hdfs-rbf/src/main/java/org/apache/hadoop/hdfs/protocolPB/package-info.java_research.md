# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/package-info.java

Purpose: package-level metadata for Router protobuf protocol implementations.

Important APIs and types: package annotation marks `org.apache.hadoop.hdfs.protocolPB` as `@InterfaceAudience.Private` and `@InterfaceStability.Evolving`.

Control flow: no executable logic.

State and persistence: no state.

Dependencies and integration points: the documentation identifies this package as containing protobuf protocols related to HDFS Router, including Router admin, client, namenode, and refresh/user mapping translators.

Risks: annotation drift can mislead downstream users about API stability. Test signal is compilation and generated Javadocs/package metadata.
