# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterMasterServiceHandler.java

## Purpose
`MetaMasterMasterServiceHandler` exposes the leader meta-master RPCs used by standby masters. It handles standby master ID allocation, registration, and periodic heartbeat commands.

## Important APIs and Types
- Extends `MetaMasterMasterServiceGrpc.MetaMasterMasterServiceImplBase`.
- Holds `MetaMaster mMetaMaster`.
- `getMasterId(GetMasterIdPRequest, StreamObserver<GetMasterIdPResponse>)` delegates address-to-ID assignment.
- `registerMaster(RegisterMasterPRequest, StreamObserver<RegisterMasterPResponse>)` registers standby master metadata and configuration.
- `masterHeartbeat(MasterHeartbeatPRequest, StreamObserver<MasterHeartbeatPResponse>)` returns a `MetaCommand`.

## Control Flow
Each RPC is wrapped in `RpcUtils.call`. `getMasterId` extracts a wire `Address`, `registerMaster` passes the master ID and options, and `masterHeartbeat` passes heartbeat options to `mMetaMaster.masterHeartbeat`, placing the resulting command in the response.

## State and Persistence
This handler owns no state. Master identity, liveness, configuration records, and journal metrics are stored in `MetaMaster`/`DefaultMetaMaster` internals.

## Dependencies and Integration Points
It is the server-side counterpart to `RetryHandlingMetaMasterMasterClient` used by standby masters. It integrates with gRPC generated request/response types and Alluxio's meta master HA management.

## Risks and Edge Cases
- Incorrect master IDs or missing registrations are handled by `MetaMaster`; the handler does not prevalidate beyond protobuf parsing.
- Heartbeat errors are surfaced through the RPC wrapper.
- The class is annotated `NotThreadSafe`; the gRPC framework may call handlers concurrently, so thread safety must come from the delegated `MetaMaster` methods.

## Test Signals
Tests should exercise ID assignment, registration option propagation, heartbeat command propagation, and error conversion when the underlying meta master throws.
