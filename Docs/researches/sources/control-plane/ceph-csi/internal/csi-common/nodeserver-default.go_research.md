# sources/control-plane/ceph-csi/internal/csi-common/nodeserver-default.go

Purpose: default CSI node server behavior and shared mount option construction.

Important APIs/types/functions: `DefaultNodeServer` embeds `csi.UnimplementedNodeServer` and stores driver, type, mounter, node labels, and read-affinity options. Methods are `NodeGetInfo()`, `NodeGetCapabilities()`, and `ConstructMountOptions()`.

Control flow: `NodeGetInfo()` returns node ID and accessible topology from driver state. `NodeGetCapabilities()` returns a single `UNKNOWN` node capability. `ConstructMountOptions()` appends unique mount flags from the volume capability and appends `ro` when access mode is reader-only.

State and persistence: reads in-memory driver topology and node ID. No persistent state.

Dependencies and integration points: used by driver-specific node servers; `ConstructMountOptions()` feeds mount execution paths. Uses Kubernetes mount-utils and common read-only helper.

Risks: nil driver or nil volume capability can panic in callers if not guarded before use. Returning `UNKNOWN` node capability may be minimal but not descriptive. Mount option dedupe preserves existing slice order and appends only missing flags.

Test signals: read-only helper tests indirectly cover `ro` decision but `ConstructMountOptions()` itself is not directly tested here.
