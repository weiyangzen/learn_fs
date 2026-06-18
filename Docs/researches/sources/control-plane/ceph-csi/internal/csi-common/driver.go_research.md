# sources/control-plane/ceph-csi/internal/csi-common/driver.go

Purpose: shared CSI driver metadata and capability registry for Ceph-CSI driver instances.

Important APIs/types/functions: `CSIDriver` stores name, node ID, version, instance ID, fencing flag, topology, controller capabilities, group capabilities, and volume access modes. Key methods are `NewCSIDriver()`, `GetInstanceID()`, `GetNodeID()`, `IsFencingEnabled()`, `ValidateControllerServiceRequest()`, `AddControllerServiceCapabilities()`, `AddVolumeCapabilityAccessModes()`, `GetVolumeCapabilityAccessModes()`, `AddGroupControllerServiceCapabilities()`, and `ValidateGroupControllerServiceRequest()`.

Control flow: constructor rejects missing name/node/version/instance by logging and returning nil. Add methods convert enum slices into CSI capability protobufs and replace stored slices. Validate methods allow `UNKNOWN`, otherwise scan stored capabilities and return `InvalidArgument` when unsupported.

State and persistence: purely in-memory driver state. Instance ID is used by lower layers to distinguish OMAP/journal namespaces across driver deployments.

Dependencies and integration points: consumed by default identity/controller/node servers and driver-specific validators. Uses CSI protobufs, gRPC status, klog, and common logging.

Risks: constructor returns nil rather than error, so callers must check. Capability slices are replaced, not appended. Validation only checks advertised capabilities, so initialization drift changes request acceptance.

Test signals: no direct tests here. Useful coverage would verify constructor required fields, capability replacement, and validation status codes.
