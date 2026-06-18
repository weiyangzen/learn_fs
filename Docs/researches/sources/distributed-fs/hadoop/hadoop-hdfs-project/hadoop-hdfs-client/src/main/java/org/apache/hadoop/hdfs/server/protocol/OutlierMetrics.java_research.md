# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/OutlierMetrics.java

Purpose: `OutlierMetrics` captures latency outlier details for slow peer reports: median, median absolute deviation, upper latency threshold, and actual observed latency.

Important APIs/types/functions: constructor initializes four `Double` values; getters expose them. `equals` and `hashCode` use Apache Commons builders.

Control flow: DataNode slow-peer detectors construct these metrics and package them in `SlowPeerReports`.

State and persistence behavior: immutable final fields. No local persistence.

Dependencies and integration points: depends on Apache Commons Lang builders and Hadoop annotations. Integrated into slow peer diagnostics sent from DataNode to NameNode.

Risks and test signals: `Double` values may be null because no validation occurs; equality uses exact `Double` comparison rather than tolerance. Tests should cover equality/hash behavior, null handling if supported, and serialization through slow-peer protocol conversion.
