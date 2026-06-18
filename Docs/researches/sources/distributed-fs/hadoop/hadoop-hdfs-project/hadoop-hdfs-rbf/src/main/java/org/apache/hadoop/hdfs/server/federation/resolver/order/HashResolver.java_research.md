# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/HashResolver.java

Purpose: `OrderedResolver` that selects the first namespace by consistent hashing over the request path.

Important APIs and state: maintains a concurrent map from namespace-set hash to `ConsistentHashRing`. `getFirstNamespace` normalizes temporary file names with `extractTempFileName`, obtains a hash ring for `loc.getNamespaces`, and returns the ring location. Temp patterns handle `.COPYING`, `._COPYING_`, `.tmp`, `_temp`, UUID `_temporary`, and MapReduce attempt temporary paths.

Control flow: hash ring creation is cached per namespace set hash. Temporary name extraction concatenates non-null regex capture groups from the matched alternative so temp writes hash like final target names.

Dependencies and integration points: used by multi-destination resolver policies and Hadoop federation consistent-hash utility.

Risks: cache key uses only `namespaces.hashCode`, so rare set hash collisions can reuse the wrong ring. Temp regex behavior is complex and should be guarded by tests. Namespace set order is irrelevant to hashing but affects hash-code collision risk.

Test signals: temp name extraction matrix, stable namespace selection for same path/set, different namespace set ring creation, and null return logging when ring lookup fails.
