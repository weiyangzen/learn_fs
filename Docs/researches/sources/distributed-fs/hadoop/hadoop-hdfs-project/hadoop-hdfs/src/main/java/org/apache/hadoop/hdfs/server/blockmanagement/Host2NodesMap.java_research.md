# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/Host2NodesMap.java

## Purpose

`Host2NodesMap` indexes datanode descriptors by IP address and hostname for quick lookup during registration, reports, block-location sorting, and slow-peer mapping. It supports the rare case of multiple datanode processes on one host.

## Important APIs, Types, and State

State consists of `mapHost`, mapping hostname to IP address, `map`, mapping IP address to an array of `DatanodeDescriptor`s, and a `ReentrantReadWriteLock`. Methods are `contains()`, `add()`, `remove()`, `getDatanodeByHost()`, `getDatanodeByXferAddr()`, `getDataNodeByHostName()`, and `toString()`.

## Control Flow

`add()` rejects null or already-contained descriptors, stores hostname-to-IP mapping, and appends to the IP array. `remove()` deletes a descriptor by identity, removing the IP and hostname entry when the last descriptor for that IP is gone, or compacting the array otherwise. `getDatanodeByHost()` returns null for no entry, the single descriptor for normal hosts, or a random descriptor when multiple nodes share the IP. `getDatanodeByXferAddr()` disambiguates by transfer port.

## State and Persistence Behavior

The map is runtime-only and mirrors `DatanodeManager.datanodeMap` plus current registration addresses. It is rebuilt by datanode registration and removal.

## Dependencies and Integration Points

`DatanodeManager` uses it for registration conflict detection, block-location sorting client lookup, host reports, slow-peer IP mapping, and descriptor resolution from host entries. Tests use it directly.

## Risks and Edge Cases

The read/write lock is reentrant, so `add()` can call `contains()` while holding the write lock. Hostname mapping removal is simple and may be lossy if multiple hostnames map to the same IP with multiple datanodes; the class assumes the common one-hostname case. Random selection for multiple nodes is acceptable for host-only lookup but should not be used when the transfer port is known.

## Test Signals

`TestHost2NodesMap`, `TestDatanodeManager`, `TestDatanodeRegistration`, and located-block sorting tests are relevant. Coverage should include duplicate add, identity-based remove, multiple datanodes per IP, hostname lookup, and transfer-port lookup.
