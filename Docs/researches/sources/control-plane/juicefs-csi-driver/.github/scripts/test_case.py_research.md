# sources/control-plane/juicefs-csi-driver/.github/scripts/test_case.py

## Purpose
This Python module is the main end-to-end test case library for the JuiceFS CSI driver GitHub Actions jobs. It defines top-level `test_*` functions that exercise dynamic and static provisioning, mount pod lifecycle management, webhook sidecar mode, process mode, quota behavior, cache cleanup, path pattern deletion, mount image selection, config reloads, secret owner references, and release-specific compatibility checks. It is not a standalone runner; it is imported or invoked by the surrounding `.github/scripts/e2e-test.py` harness and relies on `config.py`, `model.py`, and helpers from `util.py`.

## Important APIs, Types, and Functions
The module exports 37 top-level test functions. The most important groups are:

- Basic storage path tests: `test_deployment_using_storage_rw`, `test_quota_using_storage_rw`, `test_deployment_using_storage_ro`, `test_deployment_use_pv_rw`, and `test_deployment_use_pv_ro`.
- Deletion and mount pod reference tests: `test_delete_one`, `test_delete_all`, `test_delete_pvc`, `test_dynamic_delete_pod`, `test_static_delete_pod`, `test_mountpod_recreated`.
- Multi-volume and shared mount tests: `test_multi_pvc`, `test_share_mount`, `test_webhook_two_volume`.
- Cache and quota tests: `test_cache_client_conf`, `test_static_cache_clean_upon_umount`, `test_dynamic_cache_clean_upon_umount`, `test_dynamic_expand`, `test_set_quota_in_controller`.
- PV mutation and webhook equivalents: `test_deployment_dynamic_patch_pv`, `test_deployment_static_patch_pv`, `test_deployment_dynamic_patch_pv_with_webhook`, `test_deployment_static_patch_pv_with_webhook`.
- Image and sidecar tests: `test_dynamic_mount_image`, `test_static_mount_image`, `test_dynamic_mount_image_with_webhook`, `test_static_mount_image_with_webhook`, `test_sidecar_config_with_node_selector`.
- Config and ownership tests: `test_config`, `test_recreate_mountpod_with_template_config`, `test_recreate_mountpod_reload_config`, `test_secret_has_owner_reference`, `test_secret_has_owner_reference_shared_mount`.

The tests depend heavily on `model.PVC`, `PV`, `Pod`, `StorageClass`, `Deployment`, `Job`, and `Secret`, which encapsulate Kubernetes object creation, deletion, polling, and inspection. Helper functions imported from `util.py` provide mount-point polling, mount-pod lookup, readiness checks, quota checks, config map patching, and random name generation.

## Control Flow
Each test follows a create-wait-assert-cleanup pattern. It creates Kubernetes resources through model wrappers, waits for binding or readiness with bounded loops, validates filesystem state through the host JuiceFS mount at `GLOBAL_MOUNTPOINT`, and deletes resources at the end. Several tests branch on `MOUNT_MODE`, `TEST_MODE`, `IS_CE`, `IN_CCI`, and feature probes such as `is_quota_supported()`.

Dynamic PVC tests create a StorageClass-backed PVC and derive the expected volume id from the bound PV. Static tests create PVs directly with `volume_handle`, then bind PVCs to those PVs. Webhook-mode tests inspect injected `jfs-mount` containers or init containers, while pod mount mode tests inspect separate mount pods in `KUBE_SYSTEM`. Some tests mutate PV mount options, delete application pods, and verify that newly created mount pods or sidecars pick up updated `subdir` options.

Config tests patch the CSI driver ConfigMap through `update_config`, annotate controller or node pods with `updatedAt` to force refresh, then create PVCs and application pods to verify the resulting mount pod templates. Upgrade-sensitive tests recreate mount pods and compare labels, host namespace settings, mount images, and resource requests against the updated config.

## State and Persistence Behavior
The tests create real Kubernetes objects and real files in the JuiceFS filesystem. Persistent state includes PV/PVC bindings, Jobs, Secrets, StorageClasses, mount pods, per-volume cache directories, and ConfigMap data. Many tests rely on global model lists such as `PVs` for teardown coordination. The module frequently validates deletion by polling for Kubernetes 404s, empty cache directories, vanished subpaths under `GLOBAL_MOUNTPOINT`, or the absence of mount pods.

The test suite mutates global cluster configuration in `test_config`, `test_sidecar_config_with_node_selector`, and the mount pod recreate tests; those tests reset the config back to `{}` afterward. Several tests depend on a host-mounted JuiceFS filesystem and assume the CSI driver, microk8s kubelet path, MinIO, Redis, and optional EE token credentials were installed by earlier CI setup steps.

## Dependencies and Integration Points
Direct dependencies include the Kubernetes Python client, `subprocess` calls to `kubectl`, host filesystem operations through `pathlib` and `os`, and helper/model modules in `.github/scripts`. It integrates with GitHub Actions workflows `go.yaml`, `nightly.yaml`, `release_check_ce.yaml`, and `release_check_ee.yaml` through the E2E runner. It also integrates indirectly with CSI driver behavior implemented in Go controllers, mount pods, webhook sidecar injection, volume deletion jobs, and ConfigMap-driven mount pod patching.

## Risks
The tests are slow and environment-sensitive: most checks use fixed loops with sleeps and can fail under overloaded runners. Some paths are microk8s-specific, especially `/var/snap/microk8s/common/var/lib/kubelet/...`, so portability to kubeadm or managed clusters is limited. Cleanup is mostly manual per test; failures before cleanup can leave PVs, PVCs, mount pods, config changes, or filesystem content behind until global teardown runs. Several assertions assume one pod or one mount pod exists, which can be brittle in shared-mount modes. There is also a likely logic bug in owner-reference checks that uses `if len(owner_references) != 1 and owner_references[0].uid != ...`; with zero references this can index out of range only if the first condition is false, and semantically it should likely be `or`.

## Test Signals
This file is itself the E2E test signal. Passing it proves CSI provisioning, node mount, webhook injection, cache cleanup, quota, volume expansion, deletion, and config reload behavior against a live Kubernetes cluster. Failure diagnostics are often collected through `kubectl get`, `kubectl logs`, and helper functions in `util.py`, but this file does not define unit tests for its own helper logic.
