# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/DomainSocketFactory.java

Purpose: `DomainSocketFactory` decides whether UNIX domain sockets can be used for local DataNode communication and creates/caches domain-socket path usability state.

Important APIs/types/functions: `PathState` distinguishes `UNUSABLE`, `SHORT_CIRCUIT_DISABLED`, and `VALID`, with flags for data-transfer and short-circuit usability. `PathInfo` carries effective path and state, with `NOT_CONFIGURED` sentinel. Constructor validates feature/config/native availability and creates an expiring Guava cache. `getPathInfo()` checks configured path, feature enablement, native loading, local address, effective path, and cached state. `createSocket()` connects and sets receive timeout, marking paths unusable on failure. Disable methods update cache state; `clearPathMap()` is for tests.

Control flow: clients ask for path info before domain-socket reads. If valid, they call `createSocket`; failures are cached for `pathExpireSeconds` to avoid repeated attempts.

State and persistence behavior: path states are in-memory and expire after configured disable interval. No durable state.

Dependencies and integration points: depends on DFS client short-circuit configuration, `DomainSocket`, `DFSUtilClient.isLocalAddress`, Hadoop `PerformanceAdvisory`, and Guava cache. It gates both short-circuit local reads and domain-socket data traffic.

Risks and test signals: incorrect local-address detection or cache state can disable short-circuit reads unexpectedly. Empty domain socket path with enabled feature throws `HadoopIllegalArgumentException`. Tests should cover feature combinations, native load failure, non-local addresses, effective path formatting by port, failure caching/expiry, and short-circuit-only disable state.
