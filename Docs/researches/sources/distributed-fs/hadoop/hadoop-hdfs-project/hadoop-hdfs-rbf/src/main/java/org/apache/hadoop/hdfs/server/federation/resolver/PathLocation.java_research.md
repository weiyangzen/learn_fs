# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/PathLocation.java

Purpose: immutable-ish mapping from a global federation source path to one or more remote destinations plus a destination ordering policy.

Important APIs: constructors accept source path, destinations, and optional `DestinationOrder` defaulting to `HASH`. `prioritizeDestination` returns a new `PathLocation` with a selected namespace moved first. Getters expose source path, destination namespaces, destinations, order, multi-destination flag, and default location.

Control flow and state: wraps destination lists as unmodifiable at construction and when reordering. `orderedNamespaces` preserves relative order except moving matching namespace(s) to the front. `getDefaultLocation` throws if no valid first destination exists.

Dependencies and integration points: created by mount resolvers and consumed by Router RPC paths and ordered resolvers.

Risks: `getNamespaces` returns a `HashSet`, so random resolver order is intentionally not stable. If multiple destinations share a nameservice, `addFirst` can reverse their relative order. Source path may be null for default namespace fallback.

Test signals: prioritization, multi-destination behavior, default location errors, string rendering with order suffix, and immutability of destination lists.
