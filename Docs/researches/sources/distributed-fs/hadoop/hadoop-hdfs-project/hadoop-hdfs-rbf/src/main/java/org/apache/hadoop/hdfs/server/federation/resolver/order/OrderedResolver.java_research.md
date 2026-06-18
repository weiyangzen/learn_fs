# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/OrderedResolver.java

Purpose: common policy interface for choosing the first namespace when a `PathLocation` has multiple destinations.

Important API: `getFirstNamespace(String path, PathLocation loc)` returns the namespace ID to prioritize, or null if no decision can be made.

Control flow and state: interface only. Implementations are hash, local, random, space-biased, and leader/follower strategies.

Dependencies and integration points: invoked by `MultipleDestinationMountTableResolver`, which rewrites destination order through `PathLocation.prioritizeDestination`.

Risks: returning null leaves original order and logs errors at the caller. Implementations must use namespace identifiers compatible with `RemoteLocation.getNameserviceId`.

Test signals: resolver implementations should be tested through this interface and through multi-destination mount resolution.
