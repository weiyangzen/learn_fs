# sources/control-plane/ceph-csi/internal/csi-common/controllerserver-default.go

Purpose: default CSI controller and group-controller capability endpoints shared by Ceph-CSI drivers.

Important APIs/types/functions: `DefaultControllerServer` embeds unimplemented CSI controller, group controller, and snapshot metadata servers and stores `*CSIDriver`. Methods are `ControllerGetCapabilities()` and `GroupControllerGetCapabilities()`.

Control flow: each method logs, checks that `Driver` is not nil, then returns the controller or group capability slices stored on the driver. Nil driver maps to `Unimplemented`.

State and persistence: reads in-memory capability state from `CSIDriver`.

Dependencies and integration points: used by driver-specific controller servers to satisfy standard CSI capability RPCs. Capabilities are populated via `CSIDriver.AddControllerServiceCapabilities()` and `AddGroupControllerServiceCapabilities()`.

Risks: if driver capabilities are not initialized, the server returns empty slices and callers may disable behavior. Nil driver is handled, but nil capability entries are not filtered.

Test signals: no direct tests in this item. Capability population tests should verify expected driver-specific values.
