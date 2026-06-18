# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestHostSet.java

## Purpose
`TestHostSet` is a regression test for unresolved address handling in `HostSet.add`. It ensures unresolved datanode addresses are skipped without throwing and without preventing subsequent resolved addresses from being added.

## Important APIs, Types, and Functions
The test uses `HostSet`, `InetSocketAddress.createUnresolved`, and ordinary resolved `InetSocketAddress` construction. The primary method under test is `HostSet.add`.

## Control Flow
`testAddUnresolvedAddressDoesNotThrow` creates an unresolved hostname and adds it to a new `HostSet`, expecting no exception and no entry. `testAddResolvedAddressSucceeds` adds `127.0.0.1:50010` and expects one entry. `testAddMixedAddressesSkipsUnresolved` adds two resolved loopback addresses with a skipped unresolved entry between them and expects only the resolved addresses in the set.

## State and Persistence Behavior
State is an in-memory host set. The unresolved address is constructed without network access, making the regression deterministic.

## Dependencies and Integration Points
This protects callers such as `dfsadmin -report` and the NameNode web UI from failing when one datanode hostname is no longer resolvable.

## Risks and Edge Cases
The covered regression is an uncaught `IllegalArgumentException` or full batch abort when an unresolved address appears in host data. It also guards against the fix accidentally rejecting resolved addresses.

## Test Signals
Assertions verify unresolved state, resolved state, no thrown exception, and final set sizes of zero, one, and two for the three scenarios.
