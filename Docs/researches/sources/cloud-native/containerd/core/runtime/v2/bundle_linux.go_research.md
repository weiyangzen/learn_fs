# sources/cloud-native/containerd/core/runtime/v2/bundle_linux.go

## Purpose
Implements Linux bundle directory permission adjustment for user-namespace-remapped containers. If container root GID 0 maps to a nonzero host GID, the bundle directory is chowned to that GID and chmodded to `0710`.

## APIs, Flow, State, Dependencies, Risks, And Tests
`prepareBundleDirectoryPermissions` calls `remappedGID`; a zero result leaves the bundle at default permissions, while a nonzero result performs `os.Chown(path, -1, gid)` and `os.Chmod(path, 0710)`. `remappedGID` unmarshals a minimal subset of the OCI spec, checks `Linux.GIDMappings`, and returns the host ID for the mapping whose `ContainerID` is zero.

State changes are filesystem ownership and mode changes on the bundle directory before config is written. No metadata is persisted beyond these mode bits. Dependencies are JSON parsing, `os.Chown`, `os.Chmod`, and runtime-spec Linux ID mapping structures.

This integrates with `NewBundle` only when the marshaled typeurl contains an OCI `specs.Spec`. Risks include malformed JSON rejecting bundle creation, root privileges required for chown, userns mappings without container ID 0 being ignored, and access failures if runtime expectations differ from `0710`.

Test signals are `TestNewBundle` under root, verifying default `0700` vs userns `0710` and GID ownership, plus `TestRemappedGID` for empty, nil, present, and missing GID mapping cases.
