# sources/control-plane/juicefs-csi-driver/.github/scripts/util.py

## Purpose
This module provides shared utility functions for the Python E2E tests. It handles feature gating, failure diagnostics, host-side JuiceFS mount and unmount, mount-point polling, quota assertions, mount pod discovery, mount pod reference counting, test resource deployment and teardown, filesystem cleanup, random naming, JuiceFS UUID lookup, quota feature probing, and CSI driver ConfigMap read/write operations.

## Important APIs, Types, and Functions
`check_do_test()` gates EE tests on `TOKEN`. `die(e)` emits CSI node/controller logs and cluster object state before raising. `mount_on_host()` formats/authenticates and mounts CE or EE JuiceFS on the host. `check_mount_point()`, `wait_dir_empty()`, and `wait_dir_not_empty()` poll filesystem state. `check_quota()` and `check_quota_in_host()` parse `df -h` output from pods or host paths. `get_only_mount_pod_name()`, `wait_get_only_mount_pod_name()`, `get_mount_pods()`, and `get_voldel_job()` query Kubernetes by labels or generated job names. `check_pod_ready()` and `check_mount_pod_refs()` implement readiness and reference assertions. `deploy_secret_and_sc()`, `tear_down()`, and `clean_juicefs_volume()` manage shared test resources. `get_config()` and `update_config()` read and patch the CSI ConfigMap YAML.

## Control Flow
Most helpers are polling loops with explicit timeouts. Mount-pod discovery uses `client.CoreV1Api().list_namespaced_pod` with `volume-id=<id>` and filters out terminating pods. Volume-delete job lookup hashes the volume id with SHA-256, truncates to match the job naming convention, then polls `BatchV1Api.read_namespaced_job`. Quota checks repeatedly run `df -h`, parse lines beginning with `JuiceFS:`, and compare the reported size to the expected value.

Host mounting branches on CE versus EE: CE runs `juicefs format` and `juicefs mount` against `META_URL`, while EE runs `juicefs auth` and mounts by secret/name. Teardown walks the global model registries in a fixed order, deleting Pods, Deployments, PVCs, StorageClasses, PVs, Secrets, and then filesystem contents.

## State and Persistence Behavior
The module creates and deletes cluster resources and can mutate the CSI ConfigMap. It also touches host mount state through `mount_on_host()` and `umount()`, and filesystem contents through `clean_juicefs_volume()`. Cleanup preserves recent EE files for up to three days but removes all visible CE files with `juicefs rmr`.

## Dependencies and Integration Points
Dependencies include `kubernetes.client`, `subprocess`, `yaml`, host JuiceFS binaries under `/usr/local/bin/juicefs` or `/usr/bin/juicefs`, `kubectl`, global constants from `config.py`, and model registries from `model.py`. It integrates directly with the E2E test cases and with Kubernetes APIs for Pods, Jobs, ConfigMaps, and events.

## Risks
Many subprocess calls use `sudo` and assume exact binary paths and cluster tooling. Some commands use `shell=True` for wildcard cleanup. Polling timeouts are fixed and can be flaky under slow CI. `check_mount_pod_refs()` assumes annotation values containing `/var/lib/kubelet/pods` represent mount references, which may not cover all kubelet path variants. `wait_get_only_mount_pod_name()` returns `None` silently on timeout instead of raising.

## Test Signals
The helper functions are validated indirectly by every E2E run. There are no standalone unit tests in this file, so helper regressions usually appear as environment-level E2E failures.
