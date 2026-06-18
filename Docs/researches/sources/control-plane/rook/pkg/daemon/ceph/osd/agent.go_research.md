# sources/control-plane/rook/pkg/daemon/ceph/osd/agent.go

This file defines the OSD provisioning agent state container and a few helpers used by OSD prepare flows.

`OsdAgent` carries the cluster info, node name, desired devices, metadata device, store config, ConfigMap key/value store, PVC-backed flag, replacement OSD info, force-format behavior, and whether devices from other clusters should be wiped. `NewAgent()` initializes this struct from operator-provided device and storage settings. `getDeviceLVPath()` shells out to `pvdisplay -C -o lvpath --noheadings <device>` and returns an empty string on failure after logging. `GetReplaceOSDId()` returns the replacement OSD ID when the provided block path matches `replaceOSD.BlockPath`, otherwise `-1`.

State is in-memory agent configuration plus external LVM metadata queried by `pvdisplay`. Integration points include `daemon.go` provisioning, operator OSD config types, Kubernetes ConfigMap status storage, and replacement OSD workflows.

Risks include `GetReplaceOSDId()` assuming `replaceOSD` is non-nil when called, failure masking in `getDeviceLVPath()`, and no direct tests in this work item for constructor field propagation or replacement lookup. Most behavioral coverage arrives indirectly through `daemon.go` tests that build `OsdAgent` values.
