# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/HostSet.java

## Purpose

`HostSet` stores resolved host/port entries and implements the wildcard-port matching semantics used by HDFS include and exclude files. Port `0` represents all datanodes on the host.

## Important APIs, Types, and State

The class wraps a Guava `HashMultimap<InetAddress, Integer>` from host address to ports. Methods are `matchedBy(InetSocketAddress)`, `match(InetSocketAddress)`, `isEmpty()`, `size()`, `add(InetSocketAddress)`, `iterator()`, and `toString()`.

## Control Flow

`add()` logs and ignores unresolved addresses, otherwise stores address and port. `match(addr)` answers whether the set contains either the exact port or wildcard port zero for the address. `matchedBy(addr)` is the opposite partial-order query used when generating dead-node reports: a wildcard query address matches any stored port, while a non-wildcard query requires exact stored port. Iteration returns unmodifiable socket addresses built from entries.

## State and Persistence Behavior

The set is in-memory only and usually held as a snapshot inside `HostFileManager`. It does not perform synchronization; callers use it under higher-level synchronization or as an immutable-after-refresh object.

## Dependencies and Integration Points

`HostFileManager` uses it for includes and excludes. `DatanodeManager.getDatanodeListForReport()` uses `matchedBy()` to avoid synthesizing dead report entries for included hosts already represented by known nodes.

## Risks and Edge Cases

Unresolved addresses are silently not added beyond a warning. The two matching directions are easy to confuse: `match()` means incoming datanode address is covered by a set entry; `matchedBy()` means a known/found address covers an include entry for reporting. Port zero semantics are central to correctness.

## Test Signals

`TestHostSet` and `TestHostFileManager` directly cover this behavior. Tests should cover exact ports, wildcard ports, unresolved add rejection, iterator contents, and `matchedBy()` vs `match()` differences.
