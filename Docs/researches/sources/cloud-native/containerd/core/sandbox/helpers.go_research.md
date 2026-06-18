# sources/cloud-native/containerd/core/sandbox/helpers.go

## Purpose
Converts between internal `sandbox.Sandbox` metadata and API protobuf `types.Sandbox`.

## APIs, Flow, State, Dependencies, Risks, And Tests
`ToProto` maps ID, runtime name/options, sandboxer, labels, timestamps, extensions, and spec to protobuf. Extensions and options/spec are converted through typeurl/protobuf `Any`. `FromProto` reverses the mapping into internal structs.

There is no persistence here; it transforms metadata objects passed to stores/controllers. Dependencies include containerd API types, protobuf timestamp helpers, gogo `Any`, and typeurl.

Integration points are sandbox store proxy, sandbox controller proxy, metadata store implementations, and API services. Risks include nil `Runtime` in protobuf causing panic, unregistered or opaque typeurl extensions, and shallow map reuse. Test signals should round-trip sandbox metadata with labels, timestamps, spec, runtime options, and extensions.
