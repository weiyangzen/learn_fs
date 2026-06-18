# sources/cloud-native/containerd/core/diff/diff.go

Purpose: core diff comparison/application interfaces and option definitions.

Important APIs/types: `Config`, `Opt`, `Comparer`, `ApplyConfig`, `ApplyOpt`, and `Applier`. Options include `WithCompressor`, `WithMediaType`, `WithReference`, `WithLabels`, `WithPayloads`, `WithSyncFs`, `WithProgress`, and `WithSourceDateEpoch`.

Control flow and state: no implementation; defines contracts. `Comparer.Compare` computes diff content between lower/upper mounts. `Applier.Apply` applies descriptor content to mounts. Options mutate config structs used by implementations.

Dependencies and integration: mount types, OCI descriptors, `typeurl.Any` for processor payloads, and time for reproducible source date epoch.

Risks: compressor and media type must be coherent; comments require media type when custom compressor is used, but enforcement is in implementations. Progress semantics are implementation-defined except start/final expectation. Source date epoch only affects diff generation implementations that honor it.

Test signals: behavior is tested in concrete diff implementations/proxies rather than this contract file.
