# sources/control-plane/rook/pkg/operator/discover/discover_test.go

Purpose: validates discover DaemonSet construction and device-selection behavior against fake Kubernetes clients.

Important APIs/types/functions: `TestStartDiscoveryDaemonset` and `TestGetAvailableDevices`.

Control flow: `TestStartDiscoveryDaemonset` sets operator env vars, creates a fake operator pod, starts discovery, fetches the DaemonSet, and asserts namespace/name, service account, priority class, privileged root container, volumes/mounts/env count, image, and tolerations. It then sets YAML tolerations and calls `Start` again to exercise update-on-already-exists behavior. `TestGetAvailableDevices` creates a discovery ConfigMap with local disk JSON, calls `ListDevices`, then calls `GetAvailableDevices` twice for a requested `sdc` plus missing `foo`.

State and persistence behavior: fake ConfigMaps and DaemonSets persist in the fake client. `GetAvailableDevices` writes a claimed-device ConfigMap, and the second call confirms idempotent behavior returns the same selected device.

Dependencies/integration: uses Rook test fake client, discovery daemon label/data constants, `k8sutil` env var names, Ceph device API types, and large realistic `sys.LocalDisk` JSON.

Risks: tests do not cover node affinity, pod label override, loop-device env, malformed YAML, no configmaps timeout, in-use filtering, regex-only selection, use-all-devices, full-path matching, or Stop deletion.

Test signals: establishes the core DaemonSet shape and validates the discovery ConfigMap to selected Ceph device path.
