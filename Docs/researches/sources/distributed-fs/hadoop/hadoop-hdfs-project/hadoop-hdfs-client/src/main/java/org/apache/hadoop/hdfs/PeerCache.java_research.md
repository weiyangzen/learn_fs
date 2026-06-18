# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/PeerCache.java

`PeerCache` caches idle DataNode `Peer` connections for HDFS reads, keyed by DataNode identity and whether the connection uses a domain socket. It reduces read-path connection setup cost while expiring old or closed peers.

Public APIs are `get(DatanodeID, boolean)`, `put(DatanodeID, Peer)`, and `size()`, with testing-visible `clear()` and `close()`. Internal `Key` combines `DatanodeID` and domain flag; `Value` stores a `Peer` and insertion time. Eviction helpers are `evictExpired()` and `evictOldest()`, and a lazy daemon runs periodic expiry.

When disabled by zero capacity, `get()` returns null and `put()` closes peers. Otherwise `put()` starts the daemon, evicts the oldest entry at capacity, and records the peer. `get()` removes inspected entries for the requested key until it finds a non-expired, open peer or exhausts candidates. The daemon periodically removes globally oldest expired entries and clears all peers on interruption.

State is an in-memory synchronized `LinkedListMultimap<Key, Value>` plus optional daemon thread. Dependencies include `Peer`, `DatanodeID`, relocated Guava `LinkedListMultimap`, `IOUtilsClient`, `Daemon`, and `Time`.

Risks include constructor rejection of enabled cache with zero expiry, insertion-order assumptions for global expiry, inspected peers being removed even when unusable, and `close()` converting interrupted join to runtime exception. Test signals include disabled mode, get/put by key and domain flag, closed peer rejection, expiry cleanup, capacity eviction, daemon startup, clear/close closing peers, and concurrent access.
