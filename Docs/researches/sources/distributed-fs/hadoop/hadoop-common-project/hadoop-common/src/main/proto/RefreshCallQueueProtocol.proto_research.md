# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/RefreshCallQueueProtocol.proto

## Purpose
`RefreshCallQueueProtocol.proto` defines the RPC for refreshing an IPC server's call queue configuration without restarting the daemon.

## Important APIs, types, and functions
The schema contains empty `RefreshCallQueueRequestProto` and `RefreshCallQueueResponseProto` messages. The service `RefreshCallQueueProtocolService` exposes `refreshCallQueue`.

## Control flow
An administrative client invokes `refreshCallQueue`; the server reloads queue settings and swaps or reconfigures the call queue as its implementation allows. Transport-level success returns an empty response; failures surface as RPC exceptions.

## State and persistence
The proto carries no payload. Runtime state changes in the target IPC server's call queue. Persistent settings live in configuration files outside the message.

## Dependencies and integration points
It generates `org.apache.hadoop.ipc.proto.RefreshCallQueueProtocolProtos` and integrates with IPC server administration and call queue manager code.

## Risks and test signals
Risks include changing queues while calls are in flight, losing fairness/priority settings, unauthorized refresh calls, and empty response ambiguity. Test signals include call queue refresh integration tests, active-load refresh tests, authorization checks, and invalid configuration handling.
