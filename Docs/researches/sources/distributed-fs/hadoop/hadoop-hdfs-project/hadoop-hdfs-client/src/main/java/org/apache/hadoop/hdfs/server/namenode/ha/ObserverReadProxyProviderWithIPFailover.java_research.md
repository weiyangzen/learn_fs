# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ObserverReadProxyProviderWithIPFailover.java

Purpose: `ObserverReadProxyProviderWithIPFailover<T extends ClientProtocol>` combines observer-read routing over physical NameNode addresses with active failover through a configured virtual IP URI.

Important APIs/types/functions: the default constructor creates an `IPFailoverProxyProvider` using `dfs.client.failover.ipfailover.virtual-address.<nameservice>`. `getFailoverVirtualIP()` validates and parses that URI. `cloneDelegationTokenForVirtualIP()` clones the logical nameservice token to the virtual-IP address. `useLogicalURI()` returns true even though the inner active provider is IP-based.

Control flow: observer-read behavior is inherited from `ObserverReadProxyProvider`. Active fallback and writes go through the virtual IP provider, while observer scans use configured physical NameNode addresses from the superclass.

State and persistence behavior: no additional persistent state. It mutates current user token aliases for the virtual IP.

Dependencies and integration points: integrates with HA virtual-IP deployments, `HAUtilClient` token cloning, and `ClientProtocol` observer-read routing.

Risks and test signals: missing virtual-IP config throws `IllegalArgumentException` at construction. Token cloning must include the virtual IP or secure clients can fail after failover. Tests should cover missing/malformed virtual URI, token alias creation, logical URI reporting, and correct active fallback target.
