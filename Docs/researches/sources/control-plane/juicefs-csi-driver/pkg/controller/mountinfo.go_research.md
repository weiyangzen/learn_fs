# sources/control-plane/juicefs-csi-driver/pkg/controller/mountinfo.go

Purpose: parses `/proc/self/mountinfo` and classifies kubelet CSI target paths so the pod driver can recover or clean mount/bind state.

Important types/functions: `mountInfoTable`, `mountItem`, and `targetItem` hold mount records and status. `parse`, `setPodStatus`, `resolveTarget`, `resolveTargetItem`, `targetItem.check`, `getPodUid`, and `getPVName` are central. Statuses distinguish not-exist, mounted, not-mounted, corrupt, and unexpected.

Control flow/state: `resolveTarget` validates CSI target layout, extracts pod UID/PV, resolves the base target exactly, and resolves subPath targets by prefix. `resolveTargetItem` groups mountinfo rows by mount point, counts duplicates, tracks inconsistent roots, and calls `os.Stat` under timeout.

Dependencies/integration: Kubernetes mount utils, `os.Stat`, util timeout helpers, and path conventions. `pod_driver.go` consumes these statuses during ready-pod recovery and deletion cleanup.

Risks: tightly coupled to Linux kubelet path layout. SubPath result order is map-driven. Timeout detection compares a string literal. Real mount propagation behavior is difficult to fully unit test.

Test signals: `mountinfo_test.go` covers synthetic normal, invalid, not-mounted, corrupt, missing, unexpected, and inconsistent cases.
