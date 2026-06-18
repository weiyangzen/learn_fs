# sources/control-plane/ceph-csi/internal/nvmeof/volume.go

Purpose: Defines the controller-to-node NVMe-oF volume data model and parses StorageClass/CreateVolume parameters into that model.

Important APIs/types/functions: `NVMeoFVolumeData`, `NVMeoFSecurityConfig`, `SetListenersWithDefaults`, `SetupListeners`, and `SetFromParameters`.

Control flow: `SetFromParameters` fills subsystem NQN, gateway management address/port, DH-CHAP mode, authentication KMS ID, and listener info. If subsystem NQN is absent it defaults to `nqn.2016-06.io.ceph:subsystem.<volumeID>`. Listener JSON may be absent, but if present must be non-empty and each listener needs hostname. Missing listener address defaults to `0.0.0.0`; missing port defaults to 4420. DH-CHAP without KMS ID defaults to `"metadata"`.

State and persistence behavior: Pure data construction. The controller later persists these values in RBD metadata and CSI volume context.

Dependencies and integration points: Used by controller `createNVMeoFResources`, node server context parsing, and gateway listener/subsystem creation. Depends on JSON parsing and DH-CHAP constants.

Risks: Default metadata KMS is marked by surrounding code as test-oriented, but this model applies it automatically for DH-CHAP. `SetupListeners("")` is valid only because `networkMask` can drive auto-listeners; request validation must enforce that separately. Listener address default `0.0.0.0` requires node-side hostname resolution before connect.

Test signals: `volume_test.go` covers listener defaults, setup validation, gateway parsing, DH-CHAP default KMS, invalid port/listeners, and default subsystem NQN.
