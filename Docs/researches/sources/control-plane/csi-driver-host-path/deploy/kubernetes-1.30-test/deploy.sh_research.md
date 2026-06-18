# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/deploy.sh

## Purpose
This script is the authoritative hostpath CSI deployment workflow for the Kubernetes 1.30 family and the shared util path. It applies sidecar RBAC, optionally applies snapshot-metadata service resources, renders every `hostpath/*.yaml` manifest with image/tag and kubelet path substitutions, waits for the deployed StatefulSet set to become ready, and can emit a Prow `test-driver.yaml` file.

## Important APIs, Types, And Functions
The shell entry points are environment-variable driven. `rbac_version()` extracts image tags from YAML and maps canary tags to RBAC branches. `version_gt()` compares release-style versions. `volume_mode_conversion()` and `snapshot_metadata()` gate optional manifest patches. `update_image()` excludes images such as `socat` from image override substitution. `run()` logs and executes commands. Readiness is handled by `check_statefulset()` and `check_statefulsets()`.

The most important variables are `BASE_DIR`, `TEMP_DIR`, `KUBELET_DATA_DIR`, `UPDATE_RBAC_RULES`, `IMAGE_REGISTRY`, `IMAGE_TAG`, per-image `*_REGISTRY` and `*_TAG`, `VOLUME_MODE_CONVERSION_TESTS`, `SNAPSHOT_METADATA_TESTS`, `CSI_*_RBAC`, `CSI_PROW_TEST_DRIVER`, and `INSTALL_CRD`. RBAC URLs are derived from sidecar versions for provisioner, attacher, snapshotter, resizer, health monitor, and optional snapshot metadata.

## Control Flow
The script creates a temporary directory and removes it on exit. It derives RBAC URLs from manifest image tags, fetches or copies each RBAC file, creates a small kustomization that applies standard `app.kubernetes.io` labels, and runs `kubectl apply --kustomize`. When snapshot metadata is enabled, it also fetches TLS secret, service CR, and service manifests from external-snapshot-metadata and labels/applies them.

For every sorted YAML file under `hostpath/`, the script copies it into the temp directory, applies optional `sed` patches for volume mode conversion and snapshot metadata, replaces `/var/lib/kubelet/` with `KUBELET_DATA_DIR`, rewrites configurable image registry/tag components, prints the resolved image lines, and pipes the rendered manifest to `kubectl apply -f -`. After applying, it discovers all labeled StatefulSets and polls readiness for up to roughly five minutes. On failure it describes labeled resources and prints pod logs. If `CSI_PROW_TEST_DRIVER` is set, it copies the local test driver config and appends `ClientNodeName` from `csi-hostpathplugin-0` for same-node late-binding tests.

## State, Persistence, And Dependencies
The script persists Kubernetes resources through `kubectl apply` and hostpath PV data through the manifest's hostPath directories. Temporary RBAC/kustomization files live only under `TEMP_DIR`. It depends on `bash`, `sed`, `grep`, `sort -V`, `curl`, `wget`, `diff`, `kubectl`, the Kubernetes kustomize integration, and network access to GitHub raw content unless RBAC URLs are overridden to local files.

## Integration Points
It integrates with the deployment-specific `hostpath` manifest directory, external CSI sidecar RBAC repositories, external-snapshot-metadata test resources, Prow storage e2e via `CSI_PROW_TEST_DRIVER`, and the hostpath driver socket under the kubelet plugin directory. The labels it injects are also the contract used by the destroy script and readiness diagnostics.

## Risks
The script applies live cluster-wide RBAC and privileged hostPath workloads. Version extraction is based on simple `sed`/`grep` parsing of image lines, so unusual manifest formatting can produce wrong RBAC branches. Image overrides can decouple sidecar images from checked-in RBAC unless `UPDATE_RBAC_RULES` remains true. The `sed` patches depend on marker comments in the plugin manifest. `KUBELET_DATA_DIR` replacement assumes all nodes use one kubelet data directory. Readiness waits for any labeled StatefulSet names; missing or mislabeled manifests can make diagnostics misleading.

## Test Signals
Useful checks include running with default manifests, overridden image tags, overridden RBAC URLs, `IMAGE_TAG=canary` with blacklist behavior, `VOLUME_MODE_CONVERSION_TESTS=true`, `SNAPSHOT_METADATA_TESTS=true`, and non-default `KUBELET_DATA_DIR`. Cluster-level validation should confirm labeled RBAC exists, sidecars use the expected images, all StatefulSets become ready, Prow driver output includes `ClientNodeName`, and destroy removes every labeled resource.
