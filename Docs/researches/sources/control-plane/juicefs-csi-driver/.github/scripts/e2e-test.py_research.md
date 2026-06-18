<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/e2e-test.py -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/e2e-test.py

## Purpose
`e2e-test.py` is the CI orchestrator for JuiceFS CSI Driver e2e test cases. It loads kubeconfig, prepares a clean JuiceFS filesystem, deploys default test Secret/StorageClass, selects a test matrix based on `TEST_MODE`, and unmounts the host mountpoint afterward.

## Important APIs, Types, and Functions
The file imports many test-case functions from `test_case`, including deployment/PV/PVC, cache cleanup, delete policy, mount image, quota, expansion, multi-PVC, webhook, sidecar config, config reload, owner-reference, and controller quota tests. It imports `die`, `mount_on_host`, `umount`, `clean_juicefs_volume`, `deploy_secret_and_sc`, and `check_do_test` from `util`, plus `GLOBAL_MOUNTPOINT`, `LOG`, `IN_CCI`, and `IS_CE` from `config`.

## Control Flow, State, and Persistence
Under `__main__`, it reads `TEST_MODE` and `WITHOUT_KUBELET`. If `check_do_test()` is true, it loads kubeconfig, mounts JuiceFS on the host, cleans the test volume, deploys baseline secret/storageclass, then runs a mode-specific sequence for `pod`, `pod-mount-share`, `fs-mount-share`, `pod-provisioner`, `webhook`, `webhook-provisioner`, or `process`. It catches exceptions through `die(e)` and always unmounts `GLOBAL_MOUNTPOINT` in `finally`. Persistent effects are Kubernetes resources and JuiceFS data created by imported test cases, with cleanup delegated to those helpers.

## Dependencies and Integration Points
It depends on the Kubernetes Python client, local kubeconfig, JuiceFS host mount utilities, the `test_case` module, the model/config/util modules in the same script directory, and CI environment variables. It assumes the driver is already deployed by `deploy-csi-in-k8s.sh` and supporting services are ready from `k8s-deps.sh`.

## Risks and Test Signals
Risks include long sequential test runtime, test-order coupling through shared cluster state and cleaned filesystem, mode strings needing exact matches, skipped dynamic tests in CCI, and cleanup reliance on imported helpers. Signals are `LOG` output, exceptions passed to `die`, Kubernetes resource readiness inside individual tests, and the final host unmount.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/e2e-test.py -->
