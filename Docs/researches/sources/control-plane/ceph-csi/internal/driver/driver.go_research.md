# sources/control-plane/ceph-csi/internal/driver/driver.go

Purpose: defines the minimal interface implemented by Ceph-CSI driver types.

Important APIs/types/functions: `Driver` interface has one method, `Run(conf *util.Config)`, expected to start the driver and not return.

Control flow: none in this file; it is an abstraction boundary for concrete driver packages.

State and persistence: no state. Implementations decide their own server lifecycle and persistence.

Dependencies and integration points: imports common `internal/util.Config`. Driver binaries or dispatchers can depend on this package instead of concrete RBD/CephFS/NFS/NVMe-oF driver types.

Risks: because `Run()` is expected not to return, implementations must handle fatal errors and shutdown consistently. The interface has no context or error return, so graceful composition must happen through config/signals inside implementations.

Test signals: no direct tests needed for the interface. Compile-time implementation assertions in concrete drivers would be useful.
