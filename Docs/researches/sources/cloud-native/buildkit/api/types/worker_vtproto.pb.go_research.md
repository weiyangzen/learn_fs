# sources/cloud-native/buildkit/api/types/worker_vtproto.pb.go

Purpose: generated vtprotobuf fast-path implementation for the worker schema. It avoids some reflection overhead for clone, equality, size, marshal, and unmarshal operations.

Important APIs/types/functions: every message has `CloneVT`, `CloneMessageVT`, `EqualVT`, `EqualMessageVT`, `MarshalVT`, `MarshalToVT`, `MarshalToSizedBufferVT`, `SizeVT`, and `UnmarshalVT`. Map fields such as `WorkerRecord.Labels` and `CDIDevice.Annotations` are deep-cloned and marshaled as map-entry messages. Repeated message fields clone element-by-element.

Control flow: marshal methods precompute size, write fields in reverse sized-buffer order, emit map entries as nested messages, and encode varints manually. Unmarshal methods scan wire fields, switch on field numbers/wire types, allocate nested messages or maps as needed, and skip unknown fields with generated skip helpers.

State and persistence behavior: it serializes the same wire format as `worker.pb.go`; no separate state is introduced. Nil receivers are handled conservatively for clone/equality. Unknown fields are skipped rather than retained in these vt paths.

Dependencies and integration points: imports protobuf `proto` interfaces plus generated worker message types from the same package. Higher-throughput API paths can call these methods directly or through vtproto interfaces.

Risks: generated manual parsing is sensitive to schema changes and must be regenerated with the standard protobuf output. Map iteration order is Go-map dependent unless callers enforce deterministic marshaling elsewhere. Incorrect size calculations would corrupt wire output, so manual edits are high risk.

Test signals: no direct file-specific tests in this subset; confidence comes from generated-code conformance, compilation, and consumers using protobuf round trips.
