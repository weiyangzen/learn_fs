## sources/control-plane/csi-driver-iscsi/pkg/iscsi/driver.go

Purpose: defines the iSCSI CSI driver object, static driver name/version, capabilities, and server startup.

Important APIs are `NewDriver`, `NewNodeServer`, `Run`, `AddVolumeCapabilityAccessModes`, and `AddControllerServiceCapabilities`. Control flow logs configuration, creates `/var/run/iscsi.csi.k8s.io`, enables `SINGLE_NODE_WRITER`, adds controller `UNKNOWN`, then starts a non-blocking gRPC server with identity, controller, and node services.

State is driver metadata fields and capability slices; filesystem state is the run directory for connector JSON files. Dependencies are CSI types, os, klog, and server constructors. Risks include `panic` on run directory creation failure, global hard-coded version `0.2.0`, no validation of node ID/endpoint, and confusing controller capability configuration. Test signal is mostly build and runtime smoke/sanity.
