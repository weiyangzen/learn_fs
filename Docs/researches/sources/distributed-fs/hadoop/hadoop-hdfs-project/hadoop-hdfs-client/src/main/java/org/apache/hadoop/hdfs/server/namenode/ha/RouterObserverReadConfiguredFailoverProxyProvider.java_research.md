# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/RouterObserverReadConfiguredFailoverProxyProvider.java

Purpose: `RouterObserverReadConfiguredFailoverProxyProvider<T>` is a thin router observer-read provider variant that uses `ConfiguredFailoverProxyProvider` as its inner proxy rather than IP failover.

Important APIs/types/functions: its constructor passes a new configured failover provider to `RouterObserverReadProxyProvider`.

Control flow: all invocation, msync, close, and failover behavior is inherited. Reads receive router-oriented auto-msync wrapping; actual target selection follows configured failover.

State and persistence behavior: no extra state beyond inherited wrapper/inner provider state.

Dependencies and integration points: integrates router observer-read consistency logic with logical nameservice configured NameNode addresses.

Risks and test signals: coverage should ensure it chooses configured failover rather than the router provider default `IPFailoverProxyProvider`, and that logical URI/token behavior comes from the configured inner provider.
