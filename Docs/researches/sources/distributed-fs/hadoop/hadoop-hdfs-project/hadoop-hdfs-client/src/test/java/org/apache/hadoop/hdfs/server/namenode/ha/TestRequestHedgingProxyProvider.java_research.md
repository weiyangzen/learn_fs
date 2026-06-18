## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestRequestHedgingProxyProvider.java

Purpose: this JUnit 5 test validates `RequestHedgingProxyProvider<ClientProtocol>`, the HA client proxy provider that fans an RPC out to multiple NameNode proxies until one succeeds and then prefers the last successful proxy.

Important APIs and types: it builds HA config keys under `HdfsClientConfigKeys`, injects mock `ClientProtocol` instances through a custom `HAProxyFactory`, calls `getProxy().proxy`, `performFailover()`, `getStats()`, and `getBlockLocations()`, and checks `MultiException`, `RemoteException.unwrapRemoteException()`, `StandbyException`, `FileNotFoundException`, `ConnectException`, and `EOFException`.

Control flow: setup creates a unique nameservice with two NameNodes. Tests cover first-call hedging where one proxy is slow or failing, both-proxy failure aggregation, cached use of the winner after success, failover that removes the current proxy from the preferred set, one-proxy exhaustion, and a three-proxy rotation. File-not-found and standby cases verify that terminal active-side exceptions are not hidden by standby errors.

State and persistence: all state is in memory: mock invocation counts, provider current-used proxy state, failover-excluded proxies, and per-test configuration. The helper factory consumes proxies from an iterator in configured address order; no durable state is touched.

Dependencies and integration points: integrates HDFS HA client configuration, dynamic Java proxies/RPC invocation handlers, Hadoop `MultiException`, UGI-aware proxy creation, Mockito answers, and `SubjectInheritingThread` for the multithreaded regression.

Risks: sleeps make winner ordering timing-sensitive, and the iterator-backed factory assumes the provider creates proxies exactly once per configured address. Assertions on exception type/message exercise subtle failover semantics and can break if RPC wrapping changes.

Test signals: verifies hedged fan-out, winner stickiness, failover pruning/reselection, exception aggregation, single-proxy no-valid-proxies behavior, and HDFS-14088 where failover racing an exception path must not dereference a cleared current proxy.
