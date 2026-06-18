# sources/cloud-native/containerd/core/diff/proxy/differ.go

Purpose: remote diff comparer/applier that forwards operations to the diff gRPC service.

Important APIs: `NewDiffApplier` returns a `diffRemote` implementing both `Apply` and `Compare`. `Apply` converts descriptors/mounts/payloads into `ApplyRequest`; `Compare` converts mount sets and diff config into `DiffRequest`.

Control flow and state: `Apply` applies local options, marshals processor payloads with typeurl, invokes progress callback with 0 before RPC and descriptor size after success, sends `SyncFs`, and converts response descriptor. `Compare` applies options, pulls source date epoch from context when not explicitly set, converts it to protobuf timestamp, sends media type/ref/labels, and returns response descriptor.

Dependencies and integration: diff API protobufs, errgrpc, mount/OCI conversion helpers, epoch context, typeurl, protobuf `Any`, timestamp helpers.

Risks: progress is coarse for remote apply; it does not stream server progress. `NewDiffApplier` returns `any`, so callers rely on type assertions or documented dual-interface behavior. Payload marshal assumes proto-compatible typeurl payloads.

Test signals: no direct tests here; service integration should cover descriptor/mount translation and epoch propagation.
