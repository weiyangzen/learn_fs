<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/nexus.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/nexus.rs

Purpose: High-level v1 gRPC test builder and helpers for nexus lifecycle, child operations, snapshots, NVMe reservation settings, and NVMf I/O validation.

Important APIs/types: `NexusBuilder` stores RPC handle, name, UUID, size, controller ID range, reservation/preemption settings, children, nexus info key, and serial. Fluent methods set name/uuid/size/children/replicas/reservation policy. Async methods create, shutdown, destroy, publish, resize, add/remove/online/offline children, wait for states, create nexus snapshots, list snapshots, get rebuild history, and add child fault injection. Free functions list/find nexuses, run write/fio tests against a nexus, and derive nexus serial/NQN.

Control flow: all remote operations lock the shared v1 RPC handle and send generated requests. Local versus remote replica URIs are selected by comparing `SharedRpcHandle` endpoints.

State and dependencies: mutates remote nexus state, child state, snapshot state, and fault-injection state. Depends on replica builders, NVMf helpers, io-engine snapshot params, and tonic status codes.

Risks and test signals: required fields are enforced with `expect`, so incomplete builders panic. Polling waits use 100 ms sleeps and return `Cancelled` on timeout. Useful assertions include child state/reason, list/find by UUID, rebuild history, and NVMf I/O success.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/nexus.rs -->
