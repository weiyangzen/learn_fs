## sources/control-plane/csi-driver-iscsi/pkg/iscsi/controllerserver.go

Purpose: provides the CSI ControllerServer surface for the iSCSI plugin, mostly as explicit unimplemented methods.

Control flow returns `codes.Unimplemented` for create/delete/publish/list/capacity/snapshot/expand/get-volume operations. `ControllerGetCapabilities` logs and returns the driver's configured `cscap`, which is initialized to `UNKNOWN` in `NewDriver`.

State is read-only access to `Driver.cscap`. Dependencies are CSI generated interfaces, gRPC status codes, and klog. Integration point is driver registration in `Run`, and the `CSIDriver` manifest disables attach so controller publish is normally skipped. Risks include advertising controller service plugin capability from identity while all useful controller RPCs are unimplemented, and returning `UNKNOWN` capability. Test signal is compile coverage and potential csi-sanity behavior.
