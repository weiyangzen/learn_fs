# sources/cloud-native/containerd/internal/cri/server/container_start_linux.go

## Purpose
This Linux-specific start helper adjusts task creation options so IO fifo ownership matches the container process user when user namespaces are active.

## Important APIs, Types, and Functions
`updateContainerIOOwner` reads the container OCI spec, builds a `userns.IDMap`, maps `spec.Process.User` to host IDs, and returns `containerd.WithUIDOwner` and `containerd.WithGIDOwner` task options.

## Control Flow, State, and Persistence
The helper returns nil unless the config is Linux and user namespace mode is not node. It validates `spec.Linux` and `spec.Process`, computes host IDs, and supplies options used by `container.NewTask`.

## Dependencies and Integration Points
It depends on CRI user namespace options, runtime-spec UID/GID mappings, `internal/userns`, and containerd task options. It is called by `StartContainer` before task creation.

## Risks and Test Signals
Risks include invalid specs, mismatched user namespace mappings, and IO permission failures for rootless/idmapped containers. There is no direct unit test in this subset; related user namespace spec tests increase confidence in mapping setup.
