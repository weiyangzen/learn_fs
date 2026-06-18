# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/HashFirstResolver.java

Purpose: variant of consistent-hash ordering that hashes only the immediate child under the mount point.

Important APIs: overrides `getFirstNamespace` to trim the full path to at most one component below `PathLocation.getSourcePath`, then delegates to `HashResolver`. Private `trimPathToChild` handles parent equality, slash joining, and root-like cases.

Control flow and state: no extra state beyond inherited hash-ring cache. Trimming ensures an entire first-level subtree maps to the same namespace.

Dependencies and integration points: used for `DestinationOrder.HASH`, while `HashResolver` itself is used for `HASH_ALL`.

Risks: correctness depends on source path normalization. If `sourcePath` is null, this policy would fail; multi-destination mount entries should have non-null source paths.

Test signals: trimming examples such as `/a/b/c` under `/a`, exact parent path, trailing slash parent, and hash stability across children below the same first component.
