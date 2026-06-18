# Research: sources/cloud-native/containerd/internal/cri/store/container/metadata.go

This file defines immutable container metadata and versioned JSON encoding. `Metadata` records container ID, name, sandbox ID, CRI `ContainerConfig`, image reference, log path, stop signal, and SELinux process label. Comments note metadata is immutable after creation and checkpointed as a containerd container label, while resource limits are updatable elsewhere with containerd as source of truth.

`MarshalJSON` wraps the unversioned metadata in `versionedMetadata{Version: metadataVersion, Metadata: ...}` to avoid recursive marshaling. `UnmarshalJSON` decodes the wrapper and accepts only current version `v1`, returning an unsupported-version error otherwise. `metadataInternal` is the alias used to break recursive method calls.

State/persistence behavior is JSON serialization intended for labels/checkpoints outside this file. Dependencies include Go JSON and CRI runtime container config. Risks include strict version rejection during upgrades if migration is not added, pointer-valued `Config` being mutable despite metadata immutability convention, and consumers needing to preserve this wrapper format. Tests cover JSON marshal/unmarshal paths and unsupported versions.
