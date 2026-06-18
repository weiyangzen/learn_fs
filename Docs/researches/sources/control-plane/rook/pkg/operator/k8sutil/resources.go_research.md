# sources/control-plane/rook/pkg/operator/k8sutil/resources.go

## Purpose
`resources.go` groups owner-reference helpers, resource requirement merge logic, and YAML parsers for container resource settings.

## Important APIs, Types, and Functions
`OwnerInfo` abstracts owner reference setting from either a live owner object/scheme or a raw `OwnerReference`. `SetOwnerReference()` appends non-duplicate owner refs. `SetControllerReference()` validates namespace/controller ownership and sets controller plus default `BlockOwnerDeletion`. `GetUID()` exposes owner UID. `MergeResourceRequirements()` lets the first requirements override the second when present. `SetOwnerRefsWithoutBlockOwner()` copies owner refs without controller/block flags. `ContainerResource`, `YamlToContainerResourceArray()`, and `YamlToContainerResource()` parse YAML into Kubernetes resource requirements.

## Control Flow, State, and Persistence
Functions mutate Kubernetes object metadata or return parsed objects in memory. Namespace validation prevents namespaced owners from owning cluster-scoped or cross-namespace resources. Duplicate detection compares group, kind, and name rather than UID.

## Dependencies and Integration Points
It depends on controller-runtime `controllerutil`, Kubernetes metadata/runtime/schema/resource APIs, and YAML-to-JSON conversion. It integrates with most resource builders that need garbage collection ownership and configurable requests/limits.

## Risks
`SetControllerReference()` can append the same controller ref more than once after validation if called repeatedly with the same raw owner reference. Duplicate owner comparison ignores UID. YAML parsing relies on Kubernetes resource quantity unmarshal errors for validation.

## Test Signals
`resources_test.go` covers merge behavior, YAML parsing success/failure, namespaced owner validation, controller conflict validation, and owner-reference duplicate handling for non-controller refs.
