# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/NameNodeConnector.java

## Purpose

`NameNodeConnector` is the balancer's NameNode-facing utility. It creates protocol proxies, discovers block pool identity, fetches live DataNode and block-location data, manages the single-balancer lock file in HDFS, owns the `KeyManager`, tracks movement counters, and decides when repeated idle iterations should stop.

## Important APIs, Types, and Functions

Static `newNameNodeConnectors()` overloads create one connector per NameNode URI or URI-to-target-path mapping and start each connector's key updater. Test hooks `setWrite2IdFile()` and `checkOtherInstanceRunning()` control lock-file behavior. Constructors initialize `BalancerProtocols`, `DistributedFileSystem`, block pool ID, server defaults, key manager, getBlocks rate limiter, target paths, and optional namespace ID.

Important methods include `getBlocks()`, `getLiveDatanodeStorageReport()`, `isUpgrading()`, `getProxy()`, `shouldContinue()`, `checkAndMarkRunning()`, `close()`, movement counter accessors, `addBytesMoved()`, `getFallbackToSimpleAuth()`, and `getNNProtocolConnection()`.

## Control Flow

Connector construction creates an RPC proxy to the configured NameNode, opens the DFS, requests namespace information, creates a `KeyManager`, and optionally calls `checkAndMarkRunning()`. The lock path is handled by deleting stale files that can be appended, creating a replicated recursive file, writing the local hostname, hflushing, and keeping the stream open until close. If the create fails with `AlreadyBeingCreatedException`, another balancer is considered running.

`getBlocks()` optionally rate-limits, selects a proxy with `getProxy()`, and when configured for HA standby reads, discovers the standby `ClientProtocol` for the namespace and creates a `NamenodeProtocol` proxy to its address; otherwise it uses the main `BalancerProtocols` proxy. `getLiveDatanodeStorageReport()` follows the same standby selection for client protocol calls. `shouldContinue()` resets idle count on moved bytes and exits after `maxNotChangedIterations` zero-progress iterations.

## State and Persistence Behavior

Persistent external state is the HDFS id lock file at `idPath`, deleted on close or filesystem exit. In-memory state includes NameNode URI, block pool ID, protocol proxies, HA standby-read flags, namespace ID, configuration, key manager, DFS handle, target paths, atomic counters for bytes/blocks moved and failed, idle iteration count, and optional getBlocks rate limiter. Movement counters are process-local and reset by process restart.

## Dependencies and Integration Points

It depends on `NameNodeProxies`, `BalancerProtocols`, `NamenodeProtocol`, `ClientProtocol`, `DistributedFileSystem`, HA utilities, rolling-upgrade APIs, `DatanodeStorageReport`, `BlocksWithLocations`, Guava `RateLimiter`, and `KeyManager`. `Dispatcher` uses it for block listings, storage reports, block pool ID, tokens, counters, and continuation decisions. `Balancer` uses connector factory methods across federated or HA NameNodes.

## Risks and Edge Cases

The lock-file mechanism assumes append/create semantics accurately detect an active writer and that `hflush`/`hsync` capability exists. Static test flags are global mutable state. Standby getBlocks routing silently falls back to active behavior if no standby proxy is found. The `finally` log in `getBlocks()` says success for standby requests even if the call threw after proxy selection. Rate limiting applies only to getBlocks, not storage reports. `close()` best-effort deletes the id file and logs deletion failures.

## Test Signals

Tests should cover lock-file acquisition, already-running detection, stale id-file deletion, test flags, target path defaults, getBlocks QPS limiting, HA standby proxy selection and fallback, rolling-upgrade detection, live storage report retrieval, idle-iteration exit behavior, counter increments, key-manager lifecycle, and close cleanup.
