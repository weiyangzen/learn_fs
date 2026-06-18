# sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/deploy.sh

## Purpose
This script deploys the distributed hostpath CSI variant, where a DaemonSet runs the driver and node-local provisioner on every node. It applies provisioner RBAC, detects whether CSIStorageCapacity is available, renders manifests with image/path overrides, waits for the DaemonSet to be ready, and optionally writes Prow test driver configuration.

## Important APIs, Types, And Functions
Key functions are `rbac_version()`, `version_gt()`, `update_image()`, `run()`, and `wait_for_daemonset()`. Important variables are `BASE_DIR`, `TEMP_DIR`, `KUBELET_DATA_DIR`, `UPDATE_RBAC_RULES`, `CSI_PROVISIONER_RBAC`, `CSI_PROVISIONER_TAG`, `IMAGE_REGISTRY`, `IMAGE_TAG`, and `CSI_PROW_TEST_DRIVER`. It derives external-provisioner RBAC from `hostpath/csi-hostpath-plugin.yaml`.

## Control Flow
The script fetches or copies provisioner RBAC, wraps it in a temp kustomization with standard labels, and applies it. It then probes `csistoragecapacities.v1beta1.storage.k8s.io`; if unsupported, it records `have_csistoragecapacity=false`. For each `hostpath/*.yaml`, it substitutes kubelet data paths, rewrites image registry/tag components, and removes `storageCapacity: true` plus `--enable-capacity` lines when the API is unavailable. It applies each rendered manifest, waits until the `csi-hostpathplugin` DaemonSet has all desired pods ready, and writes a test driver with the capacity capability patched to the detected cluster support.

## State, Persistence, And Dependencies
The script mutates Kubernetes API state and creates node-local hostPath state through the DaemonSet manifests. Temporary files are cleaned on exit. It depends on `bash`, `curl`, `wget`, `diff`, `kubectl`, kustomize support, and optional network access to fetch RBAC.

## Integration Points
It integrates with the distributed `hostpath` manifests, the external-provisioner sidecar, Kubernetes CSIStorageCapacity API, Prow storage e2e config, and label-based destroy cleanup.

## Risks
Only provisioner RBAC is applied because this distributed variant avoids separate attach/snapshot sidecars. The CSIStorageCapacity probe is hard-coded to v1beta1 and comments say that is always used, so future API changes can break detection. Removing capacity lines with `grep -v` is formatting-sensitive. It waits only ten 3-second retries, which may be short on slow clusters.

## Test Signals
Validate both clusters with and without CSIStorageCapacity support. Confirm rendered driver info and provisioner args match support, DaemonSet readiness reaches desired node count, fast/slow storage classes provision with topology, and the generated Prow file has the correct `capacity` boolean.
