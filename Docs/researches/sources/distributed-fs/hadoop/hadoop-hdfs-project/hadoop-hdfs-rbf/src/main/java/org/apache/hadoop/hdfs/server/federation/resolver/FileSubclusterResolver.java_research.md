# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/FileSubclusterResolver.java

Purpose: `FileSubclusterResolver` is the router contract for resolving a global federation path to one or more remote subcluster paths and for listing mount children.

Important APIs: `getDestinationForPath` returns a `PathLocation`, `getMountPoints` lists immediate child mount names under a path, and `getDefaultNamespace` exposes fallback namespace. The static `getMountPoints(String, Set<String>)` computes direct children from mounted path keys.

Control flow and state: interface only, with one static helper. `MountTableResolver` implements the contract using State Store mount table records and an in-memory path tree.

Dependencies and integration points: used on the `RouterRpcServer` request path to translate client HDFS paths before invoking Namenodes. Multi-destination resolution integrates with the `resolver.order` package.

Risks: path normalization and direct-child computation must match mount table semantics. Incorrect fallback/default namespace behavior can route requests outside configured mounts.

Test signals: child mount listing for root/non-root paths, default namespace behavior, and thrown `RouterResolveException` when no mount and default namespace disabled.
