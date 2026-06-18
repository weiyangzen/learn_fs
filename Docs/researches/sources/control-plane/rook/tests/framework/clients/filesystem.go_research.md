# sources/control-plane/rook/tests/framework/clients/filesystem.go

Purpose: `FilesystemOperation` wraps CephFS lifecycle and CSI client-resource operations for integration tests.

Important APIs/types/functions: constructor `CreateFilesystemOperation`; `Create`, `ScaleDown`, `Delete`, and `List`; CSI helpers for storage classes, PVCs, pods, snapshots, restores, and clones; subvolume group helpers `CreateSubvolumeGroup` and `DeleteSubvolumeGroup`.

Control flow: create/scale operations apply `CephFilesystem` manifests, wait for MDS pods by label, and assert expected pod counts. Delete removes the default CSI subvolume group, deletes the filesystem CR through the typed Rook client, then waits for CR deletion. Subvolume group methods apply/delete the CR, wait for status/deletion, then verify raw CephFS state through toolbox `ceph fs subvolumegroup ls`.

State and persistence behavior: manages persistent CephFilesystem CRs, MDS pods, CephFS pools, CSI storage/snapshot classes, PVC/PV resources, and CephFS subvolume groups.

Dependencies and integration points: relies on Rook typed clientsets, Ceph client filesystem listing, installer manifest templates, Kubernetes storage APIs, toolbox remote execution, and testify assertions.

Risks: many methods assert directly with `k8sh.T()`, causing test failure rather than returning rich errors. Delete assumes a `name+"-csi"` subvolume group. Pod count expectation is `activeCount*2` because active/standby MDS pods are expected; changes in operator behavior can break tests. Namespace arguments to some methods are unused because manifest settings choose namespace.

Test signals: MDS pod readiness, filesystem list output, storage class/PVC binding, snapshot/clone success, and raw Ceph subvolume group presence/absence are primary signals.
