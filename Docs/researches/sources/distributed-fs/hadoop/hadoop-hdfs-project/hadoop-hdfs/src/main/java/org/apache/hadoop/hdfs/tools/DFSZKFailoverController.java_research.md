# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DFSZKFailoverController.java`

## Purpose

`DFSZKFailoverController` is the HDFS-specific `ZKFailoverController` implementation used by NameNode HA. It maps HDFS NameNode identity into ZooKeeper active-node records, binds the ZKFC RPC endpoint, logs in as the NameNode principal, enforces HDFS admin ACLs, and adds diagnostics such as local NameNode thread dumps on health failures.

## Important APIs, Types, and Functions

- `dataToTarget` parses `ActiveNodeInfo` protobuf data from ZooKeeper, reconstructs an `NNHAServiceTarget`, verifies the stored host/port matches current configuration, and restores the peer ZKFC port.
- `targetToData` serializes the active target address, ZKFC port, nameservice ID, and NameNode ID into `ActiveNodeInfo`.
- `getRpcAddressToBindTo` chooses the ZKFC bind host from service RPC bind host, NameNode RPC bind host, or the local target address, and combines it with `dfs.ha.zkfc.port`.
- `create` validates HA is enabled for the local nameservice, discovers the local NameNode ID, initializes generic NameNode keys, applies ZKFC config keys, and constructs the local target.
- `initRPC` stores the actual bound RPC port back into the local target.
- `loginAsFCUser` logs in using NameNode keytab/principal settings.
- `checkRpcAdminAccess` allows callers in `dfs.admin` or the ZKFC login user and rejects others with `AccessControlException`.
- `getLocalNNThreadDump` fetches the local NameNode `/stacks` HTTP endpoint when health changes to unhealthy/not responding.
- `getAllOtherNodes` constructs `NNHAServiceTarget`s for other NameNodes in the same nameservice.
- `isSSLEnabled` checks common and HDFS-specific ZooKeeper client SSL keys.

## Control Flow

`main` prints startup/shutdown messages, handles help, parses generic options into `HdfsConfiguration`, creates the controller, and runs inherited ZKFC logic. Controller creation is local-NameNode oriented: it must determine the nameservice and NameNode ID of the daemon host, then build an `NNHAServiceTarget` for that local NN.

The inherited ZKFC election/health loop calls `targetToData` when publishing active identity, `dataToTarget` when reading another active from ZooKeeper, `getRpcAddressToBindTo` while starting RPC, and `checkRpcAdminAccess` on incoming admin RPCs. Health state transitions route through `setLastHealthState`, which invokes thread-dump capture when the new state is unhealthy or not responding.

## State and Persistence Behavior

Local state includes `adminAcl`, `localNNTarget`, and a test-visible `isThreadDumpCaptured` flag. Cluster/persistent state lives outside the class: active-node identity is stored in ZooKeeper as `ActiveNodeInfo`, ZKFC RPC server state is in the inherited controller, and diagnostics are written to logs. The thread-dump capture is read-only against NameNode HTTP and writes only to ZKFC logs.

## Dependencies and Integration Points

The class integrates with ZooKeeper HA machinery through `ZKFailoverController`, HDFS HA target metadata via `NNHAServiceTarget`, NameNode config initialization, `HDFSPolicyProvider` for RPC service authorization, Kerberos login via `SecurityUtil`, HTTP diagnostics through `DFSUtil.getInfoServer`, and protobuf `ActiveNodeInfo`.

## Risks and Edge Cases

- `dataToTarget` deliberately fails fast if ZooKeeper active-node data conflicts with local config; this catches stale/misconfigured ZK records but can make failover unavailable until corrected.
- If `dfs.ha.zkfc.nn.http.timeout` is zero, thread-dump capture is disabled; otherwise unhealthy transitions synchronously attempt HTTP connection/read with the configured timeout.
- ACL checks rely on short username equality for the ZKFC login user and configured `dfs.admin` ACLs.
- Bind-host selection must match deployment network expectations; a wrong bind host can make graceful failover RPC unreachable.
- `setZkfcPort` in the target requires auto-failover enabled.

## Test Signals

Tests should verify protobuf round-trip, mismatch detection, bind-host fallback order, HA-disabled/local-NN-ID failure cases, admin ACL acceptance/rejection, thread-dump capture success/failure/timeouts, `getAllOtherNodes` construction, and SSL key precedence.
