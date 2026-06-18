# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMasterClientTest.java

## Purpose
`BlockMasterClientTest` verifies worker-to-block-master client metadata, request conversion, heartbeat, registration, commit, UFS commit, worker ID lookup, and register lease behavior against an in-process mock gRPC server.

## Important APIs, Types, and Functions
`clientInfo()` checks service type/name/version. `convertBlockListMapToProtoMergeDirsInSameTier()` validates directory entries merge by tier. `commitBlock()` and `commitUfsBlock()` assert request fields reach mock RPCs. `getId()` maps worker address to ID. `heartBeat()` validates used bytes, removed blocks, added blocks, lost storage, and returned command. Lease tests cover allowed/denied `requestRegisterLease`. `registerWithoutStream()` and `registerWithStream()` exercise both registration paths.

## Control Flow, State, and Persistence
Each test creates a mock `BlockMasterWorkerService` server on a configured address, constructs a client, invokes one path, and shuts the server down in `@After`. State is in memory; persistence is simulated through recorded request maps/lists.

## Dependencies and Integration Points
It depends on gRPC server/channel helpers, master client context, Alluxio configuration, generated block-master worker service RPCs, worker net address conversion, retry policy, auth configuration, and `BlockMasterWorkerServiceTestUtils`.

## Risks and Test Signals
This is a high-value request-shape suite. Gaps include real reconnects, multi-master failover, streaming registration payload content beyond worker ID, RPC deadline behavior, authentication-enabled channels, and server-side errors after partial stream writes.
