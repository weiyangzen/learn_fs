# sources/control-plane/rook/pkg/operator/discover/discover.go

Purpose: manages the rook-discover DaemonSet and provides helpers to read discovered devices and mark selected devices as in use.

Important APIs/types/functions: constants for operator settings and ConfigMap names, `Discover`, `New`, `Start`, `createDiscoverDaemonSet`, `getLabels`, `ListDevices`, `ListDevicesInUse`, `matchDeviceFullPath`, `GetAvailableDevices`, and `Stop`.

Control flow: `Start` creates or updates the DaemonSet. DaemonSet creation builds privileged pod spec with `/dev`, `/sys`, `/run/udev` host paths, discovery interval args, optional `--use-ceph-volume`, parsed resource settings, owner refs from the operator pod, tolerations from legacy and YAML settings, optional node affinity, optional pod label override preserving `app`, loop-device env, host network setting, priority class, and service account. `ListDevices` waits up to 30 attempts for discovery ConfigMaps, optionally maps hostname to node name, unmarshals local disk JSON by node, and skips malformed entries. `GetAvailableDevices` joins requested devices, regex filters, or `useAllDevices` against discovered devices, marks claimed devices in a cluster/node ConfigMap, and returns Ceph device specs.

State and persistence: persistent state is the DaemonSet and ConfigMaps labeled as discovered devices or claimed devices. Claimed device ConfigMaps are created or updated with JSON disk lists. Operator settings are read from environment/configmap through `k8sutil.GetOperatorSetting`.

Dependencies/integration: integrates Kubernetes client-go, Rook discovery daemon labels/data keys, `k8sutil` settings and object helpers, `opcontroller` pod security/network helpers, and `sys.LocalDisk` JSON.

Risks: `ListDevices` has fixed retry/sleep timings and can wait a long time. The current loop over devices in use has a TODO and does not actually filter them from `nodeDevices` because it breaks only the inner loop and still appends. Regex errors are silently treated as non-matches. ConfigMap updates for claimed devices are not conflict-retried.

Test signals: `discover_test.go` covers DaemonSet creation/update with priority class and tolerations, and available-device lookup plus claimed-device persistence for a requested device.
