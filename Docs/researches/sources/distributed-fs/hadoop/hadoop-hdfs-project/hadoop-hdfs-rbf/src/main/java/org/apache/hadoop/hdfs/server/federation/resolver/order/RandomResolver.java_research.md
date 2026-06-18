# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/RandomResolver.java

Purpose: `OrderedResolver` that randomly chooses a namespace among a location's destination namespaces.

Important API: `getFirstNamespace` validates the namespace set with `CollectionUtils.isEmpty`, chooses an index with `ThreadLocalRandom`, and returns the indexed element via Guava `Iterables`.

Control flow and state: stateless and intentionally nondeterministic. The source path is ignored.

Dependencies and integration points: registered for `DestinationOrder.RANDOM`; `DestinationOrder.FOLDER_ALL` includes random because folders may need to exist everywhere.

Risks: `PathLocation.getNamespaces` uses a `HashSet`, so index-to-namespace ordering is arbitrary before random selection. Randomness complicates tests and reproducibility.

Test signals: empty/null location returns null and logs; repeated calls should only return configured namespaces.
