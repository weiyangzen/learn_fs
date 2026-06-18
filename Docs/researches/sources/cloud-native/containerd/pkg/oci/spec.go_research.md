# sources/cloud-native/containerd/pkg/oci/spec.go

Purpose: core OCI runtime spec generation, default population, spec file reading, and descriptor conversion helpers.

Important APIs/types/functions: `Spec` aliases `specs.Spec`; `ConfigFilename = "config.json"`; `ReadSpec` loads JSON from a bundle path; `GenerateSpec` and `GenerateSpecWithPlatform` create default specs then apply `SpecOpts`; `ApplyOpts` runs options sequentially. Default helpers populate Unix, Windows, and Darwin specs with process, root, namespaces, mounts, capabilities, seccomp, masked/readonly paths, and Windows layer folders. `DescriptorFromProto` and `DescriptorToProto` convert between containerd protobuf and OCI descriptors.

Control flow: `GenerateSpecWithPlatform` seeds an empty spec, calls `generateDefaultSpecWithPlatform`, then applies options in order. Platform selection uses parsed OS strings, with Unix/Linux defaults, Windows defaults, and Darwin defaults.

State/persistence: reads existing `config.json` via `ReadSpec`; otherwise returns in-memory specs that are later persisted by runtime/bundle code.

Dependencies/integration: depends on containerd API types, platforms, runtime-spec, and image-spec. Spec options in `spec_opts.go` compose on this base.

Risks: default security settings are high impact. Option order is significant and can overwrite defaults. Platform mismatch can create invalid specs.

Test signals: `spec_test.go` validates generation, platform selection, TTY, namespaces, capabilities, privileged behavior, descriptor conversion, and user file symlink handling.
