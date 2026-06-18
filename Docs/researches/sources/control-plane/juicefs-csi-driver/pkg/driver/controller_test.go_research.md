# sources/control-plane/juicefs-csi-driver/pkg/driver/controller_test.go

Purpose: tests the CSI controller service behavior implemented in the adjacent `controller.go`, including volume creation/deletion, capability reporting, validation, and snapshot/control-publish stubs. It is a broad controller unit-test file rather than production code.

Important APIs and functions: `TestNewControllerService` checks construction with patched command execution. `TestCreateVolume` covers normal dynamic volume creation, empty names, nil capabilities, duplicate/smaller capacity conflicts, and unsupported block capabilities. `TestDeleteVolume` validates dynamic PV deletion via `JfsDeleteVol`, empty volume IDs, provider errors, and static PV no-op behavior. The remaining tests exercise `ControllerGetCapabilities`, `ValidateVolumeCapabilities`, `isValidVolumeCapabilities`, unimplemented `GetCapacity`/`ListVolumes`, snapshot argument validation, and unimplemented controller publish/unpublish calls.

Control flow: most tests construct `controllerService` directly with in-memory `vols`, fake JuiceFS providers, and `dispatch.Pool` quota workers. Create/delete tests assert CSI gRPC status codes (`InvalidArgument`, `AlreadyExists`, `Internal`) after invoking service methods. Snapshot tests currently focus on missing required IDs rather than successful job creation paths.

State and persistence behavior: state is limited to the controller service `vols` map and mocked JuiceFS calls. No Kubernetes API state or filesystem state is persisted except for patched `exec.Command` behavior in construction tests.

Dependencies and integration points: depends on CSI protobufs, GoMock-generated JuiceFS mocks, gomonkey patching, GoConvey, fake Kubernetes clientsets, global config, `dispatch`, and resource volume locks. It verifies the controller-to-`juicefs.Interface` boundary for deletion/quota setup but does not run real JuiceFS or Kubernetes operations.

Risks and test signals: good signal for basic CSI validation and capability lists, but several later controller paths are only tested for unimplemented or invalid-input errors. Successful snapshot creation/deletion, restore, controller expansion, lock contention, and quota worker async completion are not deeply covered here. Tests rely on global config and monkey patching, so they are sensitive to constructor signatures and package-level state leakage.
