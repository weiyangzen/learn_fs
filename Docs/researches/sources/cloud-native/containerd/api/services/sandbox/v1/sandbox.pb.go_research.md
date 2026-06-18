# sources/cloud-native/containerd/api/services/sandbox/v1/sandbox.pb.go

## Purpose

This generated Go protobuf file materializes `services/sandbox/v1/sandbox.proto` for containerd's sandbox API package. It exposes Go message types for the sandbox metadata `Store` service and runtime `Controller` service, plus the protobuf file descriptor used by reflection, serialization, and transport bindings.

## Important APIs, Types, and Functions

The store messages wrap `containerd.types.Sandbox` metadata: `StoreCreateRequest/Response`, `StoreUpdateRequest/Response` with update `Fields`, `StoreDeleteRequest`, `StoreListRequest/Response`, and `StoreGetRequest/Response`. Controller messages model runtime instance calls: `ControllerCreateRequest` carries `sandbox_id`, rootfs mounts, runtime `Any` options, network namespace path, annotations, a sandbox object, and `sandboxer`; `ControllerStartResponse` returns pid, creation time, labels, endpoint address, version, and runtime spec; status, wait, platform, stop, shutdown, metrics, and update messages carry the remaining runtime state. Every type has standard generated `Reset`, `String`, `ProtoReflect`, deprecated `Descriptor`, and nil-safe `Get*` methods.

## Control Flow

There is no business logic. Runtime flow is protobuf machinery: `init` calls `file_services_sandbox_v1_sandbox_proto_init`, which builds a descriptor with 31 message infos and two service descriptors. Message `Reset` stores message info when unsafe proto support is enabled; getters return zero values for nil receivers.

## State and Persistence Behavior

The file does not persist data itself. It defines serialized state for durable sandbox records and live sandbox controller responses. Unknown protobuf fields are retained in generated message state, and raw descriptors are compressed once through `sync.Once`.

## Dependencies and Integration Points

It depends on `types.Sandbox`, `types.Mount`, `types.Platform`, `types.Metric`, `google.protobuf.Any`, and timestamps. The descriptor is consumed by the sibling gRPC and ttrpc generated files and by callers using protobuf reflection.

## Risks

Field numbers are wire compatibility commitments, especially the reserved-looking `sandboxer = 10` placement across controller requests. `Any` payloads require caller/provider agreement on concrete types. Map fields have nondeterministic Go iteration unless callers request deterministic marshaling.

## Test Signals

Useful signals are protobuf round-trip tests, descriptor golden checks after regeneration, nil getter behavior, and integration tests that exercise sandbox create/start/status/update payloads through both transports.
