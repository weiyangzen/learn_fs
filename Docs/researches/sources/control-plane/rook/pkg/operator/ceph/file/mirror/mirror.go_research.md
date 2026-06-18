<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mirror/mirror.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/mirror/mirror.go

## Purpose
This file starts and updates the single CephFS mirror daemon deployment managed by `CephFilesystemMirror`. It bridges CR intent to Kubernetes Deployment state, including keyring generation, owner references, rollout annotations, memory validation, and update-or-recreate behavior.

## Important APIs and control flow
The main API is `(*ReconcileFilesystemMirror).start(filesystemMirror)`. It validates mirror pod memory with `controller.CheckPodMemory` using a 512 MiB minimum, builds a dataless daemon config for `rook-ceph-fs-mirror`, generates a CephX keyring, builds the Deployment via `makeDeployment`, annotates the pod template with the CephX secret resource version, sets the CR as controller owner, and records the last-applied hash. It first tries to create the deployment. If it already exists, it calls the package-level `updateDeploymentAndWait` hook, and if that update fails, it deletes and recreates the deployment to handle immutable selector changes.

## State and persistence
Persistent state is Kubernetes state: a Deployment owned by the `CephFilesystemMirror` CR plus a keyring Secret created by `generateKeyring` in adjacent mirror code. The Deployment template annotation `keyring.CephxKeyIdentifierAnnotation` forces restart when the keyring resource version changes. No Ceph on-disk daemon data is persisted by this path.

## Dependencies and integration points
The file depends on Rook controller helpers for labels, data path maps, owner references, keyrings, and deployment update orchestration. It integrates with Kubernetes AppsV1 deployments and with Banzai objectmatcher annotations. It uses `mon.UpdateCephDeploymentAndWait` through a variable for test stubbing.

## Risks and test signals
The delete-and-recreate fallback is operationally important but can briefly remove the daemon. Correctness depends on `makeDeployment` labels remaining compatible with selectors and with the update helper. Test coverage for this file is indirect through `spec_test.go`, which validates the generated pod/deployment shape, but the create/update/recreate branch itself is not directly exercised in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mirror/mirror.go -->
