<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/IPCLoggerChannelMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/IPCLoggerChannelMetrics.java

Purpose: Exposes writer-side metrics for one `IPCLoggerChannel` through Hadoop metrics.

Important APIs/types/functions: `create`, `unregister`, metric getters `isOutOfSync`, `getCurrentLagTxns`, `getLagTimeMillis`, `getQueuedEditsSize`, and latency mutators `addWriteEndToEndLatency` and `addWriteRpcLatency`.

Control flow: Construction reads percentile intervals from `HdfsConfiguration`, allocates quantile series for end-to-end write latency and RPC latency, and registers one source named from the remote address. Metric getters pull live channel values on demand.

State and persistence behavior: No durable state. Holds a volatile channel reference and in-memory quantile counters registered with `DefaultMetricsSystem`.

Dependencies/integration: Created by every `IPCLoggerChannel`; metric names depend on the JournalNode IP/port with IPv6 colons replaced for MBean compatibility.

Risks: Uses a fresh `HdfsConfiguration` rather than the channel's exact configuration, so percentile interval overrides must be visible through default config loading. Registration names collide if multiple channels target the same address in the same metrics system.

Test signals: Verify source naming for IPv4/IPv6, quantile creation with configured intervals, unregister behavior on channel close, and live reflection of channel lag/out-of-sync/queue state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/IPCLoggerChannelMetrics.java -->
