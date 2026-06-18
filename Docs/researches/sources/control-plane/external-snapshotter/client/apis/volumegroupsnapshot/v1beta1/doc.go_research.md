# sources/control-plane/external-snapshotter/client/apis/volumegroupsnapshot/v1beta1/doc.go

## Purpose
Package markers for deprecated beta `groupsnapshot.storage.k8s.io/v1beta1` group snapshot API generation.

## Important APIs, Types, and Functions
- `+k8s:deepcopy-gen=package`.
- `+groupName=groupsnapshot.storage.k8s.io`.
- Declares package `v1beta1`.

## Control Flow
No runtime control flow; code generators consume the markers.

## State and Persistence Behavior
No direct state. It supports generated helpers for persisted v1beta1 CRD objects.

## Dependencies and Integration Points
Integrates with code generation, conversion, and clients that still need v1beta1 compatibility.

## Risks
Removing or changing the markers would break generated beta client/deepcopy output and migration support.

## Test Signals
Generated client/scheme/deepcopy output should continue to include `v1beta1` resources until compatibility is intentionally removed.
