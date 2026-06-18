<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/namenode_info.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/namenode_info.cc

## Purpose
Implements namenode endpoint resolution and resolved-namenode formatting for HA and default filesystem connection logic.

## Important APIs, Types, And Functions
`ResolvedNamenodeInfo::operator=` copies base `NamenodeInfo` fields. `str()` formats nameservice, node name, URI, host, port, scheme, and resolved endpoints. `ResolveInPlace` refreshes one resolved node. `BulkResolve` asynchronously resolves all input nodes. Internal `ScopedResolver` owns an Asio resolver and promise/future status bridge.

## Control Flow
`BulkResolve` creates one `ScopedResolver` per namenode, starts async resolution for all of them on the supplied `IoService`, then joins each future and copies endpoints into the corresponding result if resolution succeeded. `ResolveInPlace` delegates to `BulkResolve` and copies endpoints back when exactly one node resolves with non-empty endpoints.

## State And Persistence
Resolved endpoints are stored in returned `ResolvedNamenodeInfo` values. `ScopedResolver` state is temporary and cancels the resolver on destruction.

## Dependencies And Integration Points
Depends on `NamenodeInfo`, `IoService`, Boost.Asio DNS resolver, logging, and `ToStatus`. It feeds filesystem failover and connection selection.

## Risks
Resolution requires `IoService` worker activity; otherwise `Join()` can block forever. `BulkResolve` logs failures but still returns entries with empty endpoints, despite the header comment saying only successful lookups will be placed in the result set. The callback captures `this`, so resolver lifetime must outlive completion, which is enforced only by joining before destruction.

## Test Signals
Tests should resolve localhost and invalid hosts, verify parallel resolution with multiple nodes, check empty endpoint behavior, exercise `ResolveInPlace`, and run with stopped or unstarted `IoService` to catch hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/namenode_info.cc -->
