# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/RouterObserverReadProxyProvider.java

Purpose: `RouterObserverReadProxyProvider<T>` wraps an inner failover provider to inject automatic `msync()` calls before read-only RPCs when using routers with observer reads. It does not choose observer NameNodes itself; it prepares client state alignment before forwarding to the inner proxy.

Important APIs/types/functions: constructors create `ClientGSIContext`, set it on the factory, create a dynamic proxy with `RouterObserverReadInvocationHandler`, read `observer.auto-msync-period.<nameservice>`, and enable observer-read behavior only for `ClientProtocol`. `autoMsyncIfNecessary()` performs active `msync()` when the configured period is 0 or elapsed. `isRead(Method)` mirrors observer-read classification by checking `@ReadOnly` and excluding `activeOnly`.

Control flow: `getProxy()` returns the wrapper. Each invocation auto-msyncs before read-only methods when enabled, invokes `innerProxy.getProxy().proxy`, unwraps `InvocationTargetException`, and returns the result. Failover and close delegate to `innerProxy`.

State and persistence behavior: keeps `alignmentContext`, `innerProxy`, `wrapperProxy`, `observerReadEnabled`, `autoMsyncPeriodMs`, and volatile `lastMsyncTimeMs`. No durable state.

Dependencies and integration points: integrates with routers, `ClientProtocol.msync`, `ReadOnly`, `ClientGSIContext`, and either IP or configured failover inner providers.

Risks and test signals: unlike `ObserverReadProxyProvider`, there is no initial msync flag, so negative auto-msync disables sync entirely and positive periods compare against `-1` on the first read. Tests should cover auto-msync period semantics, non-ClientProtocol disabling, activeOnly methods, exception unwrapping, connection ID delegation, and close/failover delegation.
