# sources/cloud-native/containerd/core/runtime/v2/shim.go

## Purpose
Defines shim connection, bootstrap parsing, cleanup on shim death, shim instance lifecycle, and the `runtime.Task` adapter backed by the shim task service.

## APIs, Flow, State, Dependencies, Risks, And Tests
Important APIs include timeout constants, `loadShim`, `cleanupAfterDeadShim`, `ShimInstance`, `clientVersionDowngrader`, `parseStartResponse`, `writeBootstrapParams`, `readBootstrapParams`, `makeConnection`, `grpcDialContext`, `shim`, `grpcConn`, `newShimTask`, and all `shimTask` runtime task methods. `parseStartResponse` accepts current protobuf bootstrap output and legacy JSON/raw-address output, normalizing to version/protocol/address while rejecting future versions. `makeConnection` creates ttrpc or gRPC clients and wires close callbacks.

`shimTask` methods convert runtime operations to task v3 API calls: create, start, pause, resume, kill, exec, pids, resize, close IO, wait, checkpoint, update, stats, process lookup, state, delete, and shutdown. Delete carefully handles duplicate event risks, sandboxed shim shutdown rules, connection close waiting, and bundle deletion. Create can unpack a checkpoint rootfs diff archive before restoring.

State persists through bundle directories and `bootstrap.json`; live state is client connection, version, address, and shim-owned task state. Dependencies span bootstrap/task APIs, events, errdefs, ttrpc/gRPC, OpenTelemetry interceptors, archive/compression, atomicfile, shim dialer, timeout, and runtime interfaces.

Risks include duplicate exit/delete events, leaked shim processes after shutdown failures, incorrect v2/v3 downgrade behavior, unsupported future bootstrap versions, rootfs diff unpack errors, and different close semantics between transports. Test signals include bootstrap parsing/migration tests, connection integration tests, task method mapping, shim death cleanup event tests, and restore/checkpoint paths.
