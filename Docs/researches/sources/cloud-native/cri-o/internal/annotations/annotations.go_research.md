# sources/cloud-native/cri-o/internal/annotations/annotations.go

## Purpose
Central constants package for CRI-O runtime annotations stored on containers/sandboxes.

## Important APIs, Types, and Functions
Exports string constants for Kubernetes/CRI-O metadata such as ContainerID, ContainerName, ContainerType, image refs/names/digests, pod namespace/name, paths, runtime handler, IO flags, volumes, host network, CNI result, and ContainerManager; also ContainerTypeSandbox/ContainerTypeContainer and ContainerManagerLibpod.

## Control Flow
No runtime control flow; importing packages use the constants to set/read annotations consistently.

## State and Persistence
Annotations are persisted in OCI/runtime metadata by callers; this file itself has no state.

## Dependencies
No external deps.

## Integration Points
Integrates container creation, restore, checkpoint, inspection, and metadata consumers across CRI-O.

## Risks and Edge Cases
Changing constants breaks compatibility with stored containers and external tools.

## Test Signals
Compile-time usage; tests are indirect through runtime metadata behavior.
