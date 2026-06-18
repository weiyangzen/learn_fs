# sources/cloud-native/containerd/api/services/containers/v1/containers.proto

Protocol definition for containerd's container metadata service. It defines a state-independent container object used for management, resource pinning, and as base parameters for task/process creation.

The `Containers` service exposes `Get`, `List`, server-streaming `ListStream`, `Create`, `Update`, and `Delete`. `Container` is the central type: immutable `id`, mutable label map, image reference, `Runtime` name/options, runtime-specific `spec`, snapshotter, GC-pinning `snapshot_key`, creation/update timestamps, extension map, and sandbox id. Requests wrap ids, filters, full container payloads, and `FieldMask` updates.

Control flow is declarative RPC schema. Implementations must enforce the documented behavior: list filters are ORed using containerd filter syntax, empty filters return all containers, `id` cannot be updated, label updates replace the whole map unless a map-key field path is used, and empty update masks apply all fields.

The proto itself has no persistence, but it defines durable metadata shape. Snapshot references affect garbage collection because `snapshot_key` pins snapshots. Dependencies are well-known protobuf `Any`, `Empty`, `FieldMask`, and `Timestamp`. Integration points include container metadata stores, runtime task creation, snapshot services, image metadata, sandbox orchestration, generated Go protobuf bindings, and gRPC/ttrpc transports.

Risks center on overloading the container object with runtime state, incorrect field-mask application, stale snapshot/image/spec combinations after updates, unbounded/oversized labels or extensions if implementations skip validation, and cross-version `Any` type compatibility. Test signals should cover CRUD semantics, filter OR behavior, list streaming equivalence to list, immutable id rejection, map-key field mask updates, snapshot GC pinning, and generated-code regeneration.
