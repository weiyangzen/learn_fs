# sources/cloud-native/containerd/plugins/services/sandbox/store_service.go

## Purpose
This file exposes the sandbox store over gRPC, adapting protobuf requests to the core `sandbox.Store` interface.

## Important APIs, Types, And Functions
The gRPC plugin ID is `sandboxes` and requires `plugins.SandboxStorePlugin`. `sandboxService` embeds `api.UnimplementedStoreServer` and implements `Create`, `Update`, `List`, `Get`, and `Delete`.

## Control Flow
Initialization resolves the local sandbox store. Each RPC logs the request, converts protobuf sandbox values via `sandbox.FromProto` and `sandbox.ToProto`, forwards filters or field paths, and converts errors with `errgrpc`.

## State And Persistence
Durable state lives in the sandbox store backed by metadata. The service does not cache store results.

## Dependencies And Integration Points
It integrates gRPC, protobuf sandbox service types, core sandbox store interfaces, metadata-backed local store, logging, and `errgrpc`.

## Risks
Malformed requests with nil sandbox payloads rely on `sandbox.FromProto` behavior. The service logs whole requests at debug level, which can include user-provided labels or annotations.

## Test Signals
No direct tests are in this subset. Store behavior is likely covered through metadata store tests and higher-level sandbox API tests.
