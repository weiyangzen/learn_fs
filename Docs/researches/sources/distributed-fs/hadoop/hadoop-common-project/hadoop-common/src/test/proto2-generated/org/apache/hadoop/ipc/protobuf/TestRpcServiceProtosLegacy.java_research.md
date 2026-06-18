# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto2-generated/org/apache/hadoop/ipc/protobuf/TestRpcServiceProtosLegacy.java

## Purpose
`TestRpcServiceProtosLegacy.java` is generated protobuf Java code for `test_rpc_service_legacy.proto`. It supplies Hadoop IPC tests with legacy proto2 `com.google.protobuf.Service`, asynchronous stubs, blocking stubs, reflective services, method dispatch, request/response prototypes, and file descriptors for several test RPC services. The file is test-only generated infrastructure and intentionally mirrors the protobuf compiler output rather than hand-written Hadoop style.

## Important APIs, Types, And Functions
The outer `TestRpcServiceProtosLegacy` class is a non-instantiable namespace with `registerAllExtensions(ExtensionRegistry)` and `getDescriptor()`.

Seven generated service wrappers are present:
- `TestProtobufRpcProto`: the main service with 18 RPCs: `ping`, `echo`, `error`, `error2`, `slowPing`, `echo2`, `add`, `add2`, `testServerGet`, `exchange`, `sleep`, `lockAndSleep`, `getAuthMethod`, `getAuthUser`, `echoPostponed`, `sendPostponed`, `getCurrentUser`, and `getServerRemoteUser`.
- `TestProtobufRpc2Proto`: smaller service with `ping2`, `echo2`, and `sleep`.
- `OldProtobufRpcProto`: compatibility service with `ping` and `echo`, both using empty request/response messages.
- `NewProtobufRpcProto`: compatibility-evolution service with `ping` and an `echo` that uses `OptRequestProto`/`OptResponseProto`.
- `NewerProtobufRpcProto`: another two-method compatibility service using empty request/response messages.
- `CustomProto`: single-method `ping` service.
- `TestProtobufRpcHandoffProto`: single-method `sleep` service using `SleepRequestProto2` and `SleepResponseProto2`.

Each service exposes an asynchronous `Interface`, `newReflectiveService(Interface)`, `newStub(RpcChannel)`, a `BlockingInterface`, `newReflectiveBlockingService(BlockingInterface)`, and `newBlockingStub(BlockingRpcChannel)`. Message types come from `TestProtosLegacy`, and dispatch uses protobuf runtime types such as `RpcController`, `RpcCallback`, `RpcChannel`, `BlockingRpcChannel`, `Descriptors.MethodDescriptor`, and `ServiceException`.

## Control Flow
Asynchronous calls flow through `callMethod(MethodDescriptor, RpcController, Message, RpcCallback<Message>)`. The method descriptor is first checked against the service descriptor, then `method.getIndex()` drives a switch that casts the generic `Message` to the generated request type and specializes the callback to the generated response type.

Blocking calls follow the same descriptor validation and method-index switch in `callBlockingMethod`, returning the concrete response `Message` from the provided `BlockingInterface`. Client stubs invert that flow: each generated method calls `channel.callMethod(...)` or `channel.callBlockingMethod(...)` with `getDescriptor().getMethods().get(index)`, the concrete request, the response default instance, and generalized callback plumbing.

The static initializer builds the file descriptor from serialized descriptor data and declares `TestProtosLegacy.getDescriptor()` as its dependency. Service descriptors are selected by ordinal from `getDescriptor().getServices().get(0..6)`, so the generated service order is part of the runtime contract.

## State And Persistence
The file has no durable application state. It has static protobuf descriptor state initialized once per classloader. Stub instances retain only an RPC channel reference. Request and response prototypes are immutable protobuf default instances.

## Dependencies And Integration Points
This class integrates Hadoop IPC tests with the legacy protobuf service API. It depends on `TestProtosLegacy` message classes, protobuf runtime service descriptors, and Hadoop test RPC implementations that implement the generated interfaces. The generated descriptor name, method ordinals, and request/response classes must stay synchronized with `test_rpc_service_legacy.proto` and `test_legacy.proto`.

## Risks
Because this is generated code, manual edits are brittle and likely to be overwritten. The largest behavioral risk is descriptor ordinal drift: adding, removing, or reordering proto services or methods changes method indexes and could break reflective dispatch or stubs compiled against old expectations. Wrong method descriptors intentionally throw `IllegalArgumentException`; wrong request message types fail via casts. The legacy `com.google.protobuf.Service` API is older than modern protobuf lite/gRPC patterns, so tests depend on keeping the generated proto2 runtime available.

## Test Signals
The file itself is test infrastructure. Useful signals are compilation of generated sources, Hadoop IPC protobuf tests that instantiate reflective services and stubs, compatibility tests around old/new service descriptors, and tests that exercise delayed responses, authentication user methods, errors, blocking calls, and handoff sleep behavior.
