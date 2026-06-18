# Research: sources/cloud-native/containerd/client/snapshotter_opts_unix.go

## Purpose
Implements Unix snapshotter options for user namespace ID remapping and fallback snapshot creation when a snapshotter cannot perform ID-mapped mounts directly.

## Important APIs, Control Flow, And State
`WithRemapperLabels` and `WithUserNSRemapperLabels` encode UID/GID maps into snapshot labels. `resolveSnapshotOptions` fetches snapshotter capabilities, returns the parent unchanged if `remap-ids` is supported or no remap labels are requested, rejects `only-remap-ids` hosts without idmap mount support, unmarshals labels into a `userns.IDMap`, validates a root mapping, computes a stable `remappedSnapshot` digest ID, reuses an existing remapped snapshot when present, otherwise prepares a temporary `-remap` snapshot, calls `remapRootFS`, commits it, and returns the new parent ID. Persistent state is a committed snapshot keyed by the digest of parent and sorted ID maps.

## Dependencies And Integration
Uses snapshots, internal user namespace helpers, OCI runtime ID mappings, digest generation, JSON, and `slices`. It is invoked during snapshot option resolution for task/container rootfs preparation.

## Risks And Test Signals
Risks include expensive fallback chown/remap, partial prepared snapshots after commit failure, mutable sorting of IDMap slices in `ID`, capability interpretation errors, and missing root mapping. Tests should cover capability branches, label parsing failures, stable ID generation, existing snapshot reuse, prepare/remap/commit cleanup, and root-map validation.
