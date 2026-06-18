# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/DfsClientShm.java

Purpose: `DfsClientShm` is the DFSClient-specific shared-memory segment used for short-circuit reads. It extends `ShortCircuitShm` and reacts to associated UNIX domain socket closure by invalidating slots.

Important APIs/types/functions: constructor receives `ShmId`, shared-memory stream, owning `EndpointShmManager`, and `DomainPeer`. `isDisconnected()` reports DataNode connection loss. `handle(DomainSocket)` implements `DomainSocketWatcher.Handler`: unregisters the segment, marks it disconnected, invalidates all allocated slots, and frees immediately if no slots remain.

Control flow: `DfsClientShmManager` creates it after receiving an shm file descriptor from the DataNode and registers it with `DomainSocketWatcher`. When the socket closes, watcher callback invalidates all slots so replicas using them become stale.

State and persistence behavior: in-memory `disconnected` flag is synchronized. Slot validity lives in the shared mmap segment. No durable persistence.

Dependencies and integration points: integrates `ShortCircuitShm`, `DfsClientShmManager.EndpointShmManager`, `DomainPeer`, `DomainSocket`, and `DomainSocketWatcher`.

Risks and test signals: lock ordering matters because watcher callbacks interact with the manager. Tests should cover socket-close invalidation, free-on-empty, stale slot detection by `ShortCircuitReplica`, and no double-disconnect.
