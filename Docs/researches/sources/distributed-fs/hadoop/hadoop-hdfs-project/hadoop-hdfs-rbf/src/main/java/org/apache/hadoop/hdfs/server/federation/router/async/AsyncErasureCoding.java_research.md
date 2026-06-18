# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/AsyncErasureCoding.java

## Purpose
`AsyncErasureCoding` is the async-mode implementation of erasure coding Router operations. It extends the synchronous `ErasureCoding` module and rewrites selected calls with `AsyncUtil` continuation style.

## Important APIs and Types
Overrides include `getErasureCodingPolicies`, `getErasureCodingCodecs`, `addErasureCodingPolicies`, `getErasureCodingPolicy`, `getECTopologyResultForPolicies`, and `getECBlockGroupStats`. It uses `RouterRpcServer`, `RouterRpcClient`, `ActiveNamenodeResolver`, `RemoteMethod`, `RemoteParam`, `asyncApply`, `asyncReturn`, and merge helpers.

## Control Flow
Global read/write operations fan out to all namespaces with `rpcClient.invokeConcurrent` and then merge results. `getErasureCodingPolicy(src)` resolves the path and invokes target locations sequentially. `getECTopologyResultForPolicies` fans out, returns the first unsupported result when present, otherwise returns the first namespace result. Stats are merged through `ECBlockGroupStats.merge`.

## State and Persistence
No local persistent state is kept. Policy mutations and lookups affect or read Namenode state. Async results live in the per-call async context.

## Dependencies and Integration Points
It is selected by `RouterRpcServer` indirectly through async client protocol paths and depends on normal Router location resolution and namespace discovery.

## Risks
Cluster-wide EC policy definitions are assumed compatible enough to merge. `getECTopologyResultForPolicies` throws a misspelled "No namespace availaible." error when the namespace set is empty and otherwise uses iteration order for the positive result. Async casts to raw `Map`/array classes require translator expectations to remain aligned.

## Test Signals
Tests should cover merge of EC policies/codecs/stats across namespaces, unsupported topology precedence, empty namespace failure, path-specific policy lookup, and async exception propagation.
