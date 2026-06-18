# sources/control-plane/rook/.github/workflows/encryption-pvc-kms-ibm-kp/action.yml

## Purpose

Composite action that runs the encrypted PVC IBM Key Protect KMS canary path.

## Important APIs, Types, and Functions

Inputs are IBM instance ID, IBM API key, artifact name, Ceph image, and Kubernetes version. Steps validate credentials, set up cluster resources, rewrite Ceph image, prepare disks and local PVs, generate IBM KMS manifests via `envsubst`, deploy an encrypted PVC cluster, wait for OSD readiness, collect logs, and delete the CephCluster.

## Control Flow

The caller supplies secrets and matrix values. The action performs cluster setup, injects IBM credentials into generated manifest files, appends and merges KMS spec content into `test-cluster-on-pvc-encrypted.yaml`, creates the cluster, deploys toolbox, waits, inspects pods/secrets/block devices, uploads logs, and tears down.

## State and Persistence Behavior

State lives in generated manifest files, Kubernetes secrets, CephCluster resources, local PVs, and remote IBM KMS keys. Final teardown is intended to remove keys from KMS.

## Dependencies and Integration Points

It integrates with IBM Key Protect secrets, `integration-test-setup-cluster-resources`, `collect-logs`, `tests/scripts/github-action-helper.sh`, `localPathPV.sh`, `envsubst`, `yq`, `kubectl`, and Ceph encrypted PVC manifests.

## Risks and Edge Cases

The credential guard prints an error but exits `0`, so callers rely on an outer `if` to skip missing secrets. Remote KMS cleanup depends on successful cluster deletion. Generated manifest mutation happens in-place, so order matters.

## Test Signals

Readiness of two OSDs, visible pods/secrets, successful log upload, and successful CephCluster deletion indicate the path worked.
