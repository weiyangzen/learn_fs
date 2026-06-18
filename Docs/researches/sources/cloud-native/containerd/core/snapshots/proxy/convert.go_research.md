# sources/cloud-native/containerd/core/snapshots/proxy/convert.go

## Purpose
Converts snapshot metadata and usage values between internal `snapshots` types and the snapshot service protobuf API.

## APIs, Flow, State, Dependencies, Risks, And Tests
`KindToProto` maps active/view to explicit proto values and defaults all other kinds to committed. `KindFromProto` maps active/view and defaults all other proto values to committed. `InfoToProto` maps name, parent, kind, created/updated timestamps, and labels. `InfoFromProto` reverses the mapping. `UsageFromProto` and `UsageToProto` convert inodes and size.

There is no persistence or side effect. Dependencies are snapshot service API, internal snapshot types, and protobuf timestamp helpers.

Integration points are proxy snapshotter RPC methods and any API service converting snapshot metadata. Risks include treating unknown kinds as committed, nil `Info` pointers panicking, and map aliasing. Test signals are round-trip conversion tests for all known kinds, timestamps, labels, and usage values, plus unknown-kind behavior tests.
