# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/RemoteLocation.java

Purpose: value object representing a concrete destination in a remote namespace, including destination path and original federation source path.

Important APIs: constructors support namespace-only, namespace plus explicit namenode, and copying namespace/namenode from an existing location with a new path. `getNameserviceId` appends `-namenodeId` when present, while `getDest` and `getSrc` return remote and federation paths.

Control flow and state: immutable fields, no persistence. The copy-with-path constructor is used for trash path rewrites.

Dependencies and integration points: extends `RemoteLocationContext`, used in `PathLocation`, mount table destinations, router RPC remote invocation, and metrics mount-table summaries.

Risks: `getNameserviceId` conflates nameservice and namenode when `namenodeId` is present, which is intended for specific routing but can surprise policy code expecting only namespace IDs. Copy constructor sets both source and destination to the new path.

Test signals: string formatting, nameservice/namenode rendering, and trash-copy behavior.
