<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/utils/ConsistentHashRing.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/utils/ConsistentHashRing.java

## Purpose
Thread-safe consistent hash ring for assigning items to Router federation locations while minimizing movement when locations change.

## APIs, Types, and Functions
Constructor accepts a set of locations. Public methods are `addLocation(String)`, `addLocation(String,int)`, `removeLocation(String)`, `getLocation(String)`, `getHash(String)`, and `getLocations()`. Virtual node keys use `location/index`, with 100 virtual nodes by default.

## Control Flow, State, and Persistence
State is an in-memory `TreeMap` from MD5 hash string to virtual node and a map from location to virtual node count. Writes take the write lock to add/remove all virtual nodes; reads take the read lock, hash the item, choose the first ring hash at or after the item hash, wrap to the first key if needed, and strip the virtual-node suffix to return the real location.

## Dependencies and Integration
Depends on `MD5Hash` and Java concurrent locks/maps. Used by destination ordering or routing logic that needs stable hash distribution across namespaces.

## Risks and Test Signals
`removeLocation()` can throw `NullPointerException` if the location was never added. `getLocations()` returns the live key set without locking/copying. Tests should cover empty ring, wraparound, add/remove movement, duplicate add, and concurrent access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/utils/ConsistentHashRing.java -->
