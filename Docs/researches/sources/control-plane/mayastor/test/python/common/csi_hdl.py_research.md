# sources/control-plane/mayastor/test/python/common/csi_hdl.py

## Purpose
Minimal Python gRPC handle for CSI service tests. It creates stubs for CSI identity and node services over an insecure channel.

## Important APIs, Types, And Functions
Defines `CsiHandle.__init__`, `__del__`, and `close`. The active stubs are `IdentityStub` and `NodeStub`; the controller stub line is present but commented.

## Control Flow
Construction opens a gRPC channel to the supplied CSI socket and installs service stubs. `close` delegates to `__del__`.

## State And Persistence
State is the open gRPC channel and stub objects. No persistent data is written.

## Dependencies And Integration Points
Depends on generated `csi_pb2` and `csi_pb2_grpc` modules and `grpc`. It is a fixture-level utility for CSI node/identity tests outside this subset.

## Risks
The destructor only deletes the Python channel reference and does not explicitly close all gRPC resources. Controller service coverage is disabled unless a caller adds it.

## Test Signals
Successful stub calls through this handle validate CSI socket reachability and generated protobuf compatibility.
