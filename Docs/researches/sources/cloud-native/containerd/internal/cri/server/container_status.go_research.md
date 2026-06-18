# sources/cloud-native/containerd/internal/cri/server/container_status.go

## Purpose
This file implements CRI `ContainerStatus` and conversion of internal container metadata/status into CRI status and optional verbose JSON info.

## Important APIs, Types, and Functions
Key functions/types are `ContainerStatus`, `toCRIContainerStatus`, `ContainerInfo`, and `toCRIContainerInfo`. It uses image store lookup, `util.ParseImageReferences`, container spec/info, runtime options extraction, and platform-specific `toCRIContainerUser`.

## Control Flow, State, and Persistence
`ContainerStatus` resolves the container, derives image tag/ref semantics from the image store when available, preserves local image config digest as `ImageId`, converts internal status, fills missing `CreatedAt` from containerd info, and optionally marshals verbose `ContainerInfo`. The conversion maps timestamps by state, derives default exit reasons, includes mounts/log path/resources/user/stop signal, and serializes runtime spec/runtime metadata for verbose mode.

## Dependencies and Integration Points
It integrates container store metadata, image store references, containerd container spec/info, runtime options, CRI stop-signal conversion, platform user extraction, and Kubernetes CRI status fields.

## Risks and Test Signals
Risks include image reference compatibility for multi-arch images, zero CreatedAt rejection, verbose JSON failures, stop-signal mapping drift, and losing user data on platform helper errors. `container_status_test.go` covers state/reason/image/ref conversion and verbose false behavior; Linux user tests cover user extraction.
