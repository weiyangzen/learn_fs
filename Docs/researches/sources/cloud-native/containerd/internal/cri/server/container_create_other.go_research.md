# sources/cloud-native/containerd/internal/cri/server/container_create_other.go

## Purpose
This non-Linux/non-Windows build-tagged file supplies portable no-op create helpers so the CRI server package compiles on other platforms. It provides the platform hooks used by `createContainer`.

## Important APIs, Types, and Functions
`containerSpecOpts` returns an empty `[]oci.SpecOpts`; `snapshotterOpts` returns an empty `[]snapshots.Opt`. Both accept the same CRI/image config parameters as platform implementations.

## Control Flow, State, and Persistence
There is no side effect, validation, or persistence. Calls are pass-through defaults used after generic spec construction has selected a supported platform branch.

## Dependencies and Integration Points
The file depends only on CRI runtime config types, OCI spec option type, image config, and snapshot options. It integrates with `platformSpecOpts` and `createContainer` as the fallback implementation for Darwin/other build targets.

## Risks and Test Signals
The risk is under-validation on unsupported or partially supported platforms: security profiles, snapshot idmaps, and Windows rootfs labels are intentionally absent. The paired `container_create_other_test.go` verifies the portable test data and expected generic annotations/mounts.
