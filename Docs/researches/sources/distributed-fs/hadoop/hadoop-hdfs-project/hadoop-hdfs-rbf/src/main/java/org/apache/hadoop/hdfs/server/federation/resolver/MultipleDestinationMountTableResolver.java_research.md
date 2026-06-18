# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/MultipleDestinationMountTableResolver.java

Purpose: extends `MountTableResolver` to support mount table entries with multiple destinations and to prioritize those destinations by policy.

Important APIs and state: constructor registers `OrderedResolver` implementations in an `EnumMap`: `HASH`, `LOCAL`, `RANDOM`, `HASH_ALL`, `SPACE`, and `LEADER_FOLLOWER`. `getDestinationForPath` delegates to the base resolver, then, for multi-destination results, asks the configured ordered resolver for the first namespace and returns a prioritized `PathLocation`.

Control flow: no persistence beyond inherited mount tree/cache. Ordering is applied per resolution after base path translation. Test helpers allow injecting/retrieving policy resolvers.

Dependencies and integration points: integrates the mount resolver with the `resolver.order` package and `Router` service for policies that need runtime data.

Risks: missing resolver mapping logs an error and leaves original order. Policy failure returning null also leaves original ordering. Order policies can be nondeterministic (`RANDOM`, probabilistic `SPACE`, observer/local runtime data).

Test signals: each `DestinationOrder` should reorder as expected, unknown/missing resolver behavior, and inheritance of base resolver path/trash/default behavior.
