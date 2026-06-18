# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouter.java

## Purpose

`TestRouter` validates core Router service lifecycle and basic RPC behavior without a full federated state-store cluster. It checks startup states for different service combinations, RPC shutdown, no-subcluster error paths, router id propagation, disabled metrics, and heartbeat service switches.

## Important APIs, types, and functions

The file uses `Router`, `RouterConfigBuilder`, `RouterServiceState`, Hadoop `Service.STATE`, `MockResolver`, `ActiveNamenodeResolver`, `FileSubclusterResolver`, `DFSClient`, `RemoteMethod`, `RouterRpcServer`, `RouterHeartbeatService`, and `NamenodeHeartbeatService`. `create()` builds a static base `Configuration` with mock resolvers, ephemeral RPC/admin/HTTP ports, and a simulated co-located nameservice.

## Control flow

`testRouterStartup()` is the central helper: instantiate Router, assert `NOTINITED` and `UNINITIALIZED`, initialize, assert `SAFEMODE` or `INITIALIZING` depending on safemode config, start, assert `SAFEMODE` or `RUNNING`, then stop and close. `testRouterService()` applies that helper to admin-only, HTTP-only, RPC-only, safemode, metrics, state store, heartbeat, and all-services configs.

Other tests verify stopping the Router stops `RouterRpcServer`; creating a file and requesting datanode reports with no subclusters return expected errors; `RouterRpcClient.invokeSingle()` includes the router id in exceptions; disabled namenode metrics throw an initialization error; and heartbeat service objects exist or not based on `DFS_ROUTER_HEARTBEAT_ENABLE` and `DFS_ROUTER_NAMENODE_HEARTBEAT_ENABLE`. A default-value test ties namenode heartbeat enablement to the router heartbeat switch when not explicitly configured.

## State and persistence behavior

State is in-memory service state and configuration-driven service composition. No state-store records are persisted. The tests do create ephemeral RPC listeners and clients.

## Dependencies and integration points

This file protects Router lifecycle contracts used by all higher-level RBF tests. It also verifies error contracts for empty topology and heartbeater initialization logic.

## Risks and test signals

The strongest signals are service-state transitions and absence/presence of subservices. Because the cluster is mocked, it does not validate real membership, mount-table lookup, or end-to-end data operations.
