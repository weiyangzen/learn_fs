# Research: sources/cloud-native/containerd/internal/cri/store/sandbox/metadata.go

This file defines immutable CRI sandbox metadata and versioned JSON encoding. `Metadata` records sandbox ID, name, CRI `PodSandboxConfig`, netns path, primary IP, additional IPs, runtime handler, CNI result, and SELinux process label. Comments note metadata is immutable after creation and checkpointed as a containerd container label.

`MarshalJSON` wraps the metadata in `versionedMetadata` with version `v1`; `metadataInternal` avoids recursive calls to `MarshalJSON`. `UnmarshalJSON` decodes the wrapper, accepts only `v1`, and returns an unsupported-version error otherwise. The metadata includes pointer-rich CRI config and CNI result data, so immutability is a convention enforced by store usage rather than by deep-copying here.

State/persistence behavior is serialization for labels/checkpoints outside this package; there is no direct disk write in this file. Dependencies include JSON, go-cni result type, and CRI runtime sandbox config. Risks include strict version rejection during upgrade without migration, mutable pointer fields, CNI result serialization compatibility, and preserving additional IPs/runtime handler for status reporting and network teardown. Tests cover wrapper JSON round-trips and unsupported versions.
