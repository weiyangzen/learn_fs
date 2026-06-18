# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ErasureCoding.java

Purpose: Router RPC helper implementing ClientProtocol erasure-coding operations over federated namespaces.

Important APIs: all methods wrap a `RemoteMethod` and invoke through `RouterRpcClient`. Cluster-wide operations fan out to `namenodeResolver.getNamespaces`: get/list policies, codecs, add/remove/enable/disable policies, topology verification, and block group stats. Path-specific operations resolve path locations through `RouterRpcServer.getLocationsForPath`: get/set/unset erasure coding policy.

Control flow: read/write operations call `rpcServer.checkOperation` with appropriate `OperationCategory`. Concurrent namespace calls merge arrays or stats where needed. Path writes use concurrent or sequential invocation depending on `rpcServer.isInvokeConcurrent(src)`. Topology verification returns the first unsupported result, otherwise the first namespace result, and throws if no namespace is available.

Dependencies and integration points: `RouterRpcServer`, `RouterRpcClient`, `ActiveNamenodeResolver`, `FederationNamespaceInfo`, `RemoteLocation`, erasure-coding protocol classes, and `RouterRpcServer.merge`.

Risks: all-namespace writes assume policy operations should be applied everywhere. Codec maps are merged with later entries overwriting same keys. Typo in no-namespace error message is user-visible. Sequential path read returns first successful policy based on path location order.

Test signals: operation category checks, all-namespace fan-out and merge behavior, path concurrent/sequential switching, no-namespace topology error, unsupported topology short-circuit, and EC block group stats merge.
