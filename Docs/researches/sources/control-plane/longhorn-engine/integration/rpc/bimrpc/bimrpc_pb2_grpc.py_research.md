# sources/control-plane/longhorn-engine/integration/rpc/bimrpc/bimrpc_pb2_grpc.py

## Purpose
This generated gRPC module defines client stubs, server base classes, registration helpers, and experimental static RPC helpers for `bimrpc.BackingImageManagerService`.

## Important APIs, types, and functions
- `BackingImageManagerServiceStub` exposes unary RPCs `Delete`, `Get`, `List`, `VersionGet`, `Sync`, `Send`, `Fetch`, `PrepareDownload`, `BackupCreate`, `BackupStatus`, and streaming `Watch`.
- `BackingImageManagerServiceServicer` provides unimplemented method stubs that set `grpc.StatusCode.UNIMPLEMENTED`.
- `add_BackingImageManagerServiceServicer_to_server` registers all service handlers with serializers/deserializers from `bimrpc_pb2` and `empty_pb2`.
- `BackingImageManagerService` offers experimental static wrappers for direct calls.

## Control flow
Stub construction binds channel methods to fully qualified RPC paths such as `/bimrpc.BackingImageManagerService/Delete`. Server registration builds a method handler dictionary and adds it as a generic handler. Base servicer methods only raise `NotImplementedError` until subclassed.

## State and persistence behavior
The module has no persistent storage. It stores bound callables on stub instances and registers service handlers against a supplied gRPC server.

## Dependencies and integration points
Depends on `grpc`, generated `bimrpc_pb2`, and `google.protobuf.empty_pb2`. It is the transport layer for backing image manager operations represented in `bimrpc_pb2.py`.

## Risks and edge cases
- Generated imports require the local `bimrpc` package path to be available, usually via package path setup.
- The watch method is `unary_stream`, so callers must handle iterator lifecycle.
- Hand edits would be lost on regeneration and could desynchronize serializers from message classes.

## Test signals
Import success, successful stub construction with a gRPC channel, correct method paths, and service calls against a backing image manager implementation validate this file.
