# sources/control-plane/rook/.github/workflows/canary-integration-test.yml

## Purpose

Reusable GitHub Actions workflow for broad Rook/Ceph canary coverage. It is invoked by other workflows through `workflow_call` and matrixes over Ceph images and Kubernetes versions to exercise raw device, partitioned device, LVM, PVC, encryption, KMS, mirroring, Multus, object, and NVMe-oF scenarios.

## Important APIs, Types, and Functions

The workflow exposes `ceph_images` and `kubernetes-version` JSON string inputs. Jobs include `canary`, `raw-disk-with-object`, `two-osds-in-device`, metadata-device variants, encryption and encrypted PVC variants, Vault and IBM Key Protect KMS paths, `lvm-pvc`, `multi-cluster-mirroring`, `rgw-multisite-testing`, `nvmeof-protocol`, `multus-public-and-cluster`, and `two-object-one-zone`. It depends heavily on local composite actions `tmate_debug`, `upterm_debug`, `integration-test-setup-cluster-resources`, `collect-logs`, and `encryption-pvc-kms-ibm-kp`.

## Control Flow

Each job checks out the full repository, optionally opens pre-job debugging, provisions cluster resources, rewrites manifests for the selected Ceph image, prepares block devices or PVCs, deploys Rook/Ceph manifests, waits for readiness, runs scenario-specific checks, collects logs on `always()`, and optionally opens post-job debugging. The main `canary` job also validates `create-external-cluster-resources.py` idempotency, dry-run behavior, restricted auth, topology flags, rados namespaces, RGW endpoint validation, multisite flags, key rotation, csi-addons, owner references, and OSD purge behavior.

## State and Persistence Behavior

State is external to the YAML and lives in the GitHub Actions runner, Kubernetes cluster, Ceph cluster, local disks, loop devices, generated manifests, secrets, and uploaded artifacts. Some jobs intentionally delete and redeploy clusters to verify cleanup policies and persistence or removal of disk headers. KMS jobs create external secrets and must delete the CephCluster to clean up remote keys.

## Dependencies and Integration Points

The file integrates with `tests/scripts/github-action-helper.sh`, `tests/scripts/validate_cluster.sh`, `tests/scripts/create-bluestore-partitions.sh`, Vault validation scripts, Multus scripts, Kubernetes `kubectl`, `yq`, `jq`, Ceph CLI, `rbd`, `radosgw-admin`, minikube, and GitHub secrets for tmate and IBM Key Protect. It is called from nightly and release workflows and supplies check names that Mergify references for backport automerge.

## Risks and Edge Cases

The workflow is large and shell-heavy, so manifest mutations can leak between steps if reset logic is incomplete. Many waits assume specific labels, namespace names, object names, device sizes, service names, and Ceph output formats. Debug actions can expose interactive sessions when enabled. External services and secrets make IBM and Vault paths conditional and potentially flaky. The matrix creates many long-running jobs, so check-name changes can break Mergify rules.

## Test Signals

Successful job completion signals a live end-to-end Rook deployment across the covered scenarios. Failure artifacts from `collect-logs` and per-step `kubectl`/Ceph output are the primary diagnostics. Scenario checks include readiness waits, Ceph CLI assertions, key existence checks, object replication tests, CSI workload restart tests, and explicit negative tests that expect bad inputs to fail.
