# sources/control-plane/rook/pkg/operator/ceph/csi/config.go

## Purpose
`config.go` creates and updates ceph-csi-operator `ClientProfile` custom resources for default CSI access, RBD rados namespaces, and CephFS subvolume groups.

## Important APIs, Types, and Functions
Package globals hold derived CSI driver names and config keys. `CreateUpdateClientProfileRadosNamespace`, `CreateUpdateClientProfileSubVolumeGroup`, and `CreateDefaultClientProfile` construct `csiopv1.ClientProfile` specs. `generateProfileSubVolumeGroupSpec` builds the CephFS profile and applies mount options. `createUpdateClientProfile` handles get/create/update. `applyCephFSMountOptions` and `parseMountOptions` translate comma-separated `key=value` CephFS mount options into maps expected by ceph-csi-operator.

## Control Flow, State, and Persistence
Profile CRs are named by the cluster namespace, rados namespace, or subvolume group cluster ID and are created in `POD_NAMESPACE`. Specs reference the `CephConnection`, CSI secret names in the Ceph namespace, and optional CephFS/RBD settings. Updates replace the existing profile spec.

## Dependencies and Integration Points
The file integrates Rook cluster info, `cephv1.CSIDriverSpec`, ceph-csi-operator APIs, Kubernetes secret references, and env-driven operator namespace selection.

## Risks
`applyCephFSMountOptions` uses `else if`, so kernel options take precedence and fuse options are skipped if both are provided. `parseMountOptions` silently ignores options without `=`, which may hide invalid user input. Missing `POD_NAMESPACE` can place profiles in an empty namespace.

## Test Signals
Tests cover rados namespace and subvolume group profile creation, CephFS rados namespace pointers, kernel mount option parsing, multiple options, whitespace handling, and empty input.
