# sources/cloud-native/cri-o/internal/factory/container/container.go

Purpose: defines CRI-O’s container factory abstraction and most of the logic that translates CRI container/sandbox config, image metadata, annotations, capabilities, privileges, and resources into an OCI runtime spec generator.

Important APIs/types/functions: public `Container` interface; hidden `container` struct; `New`, `SpecAddMount`, `SpecAddAnnotations`, `Spec`, `SetConfig`, `SetNameAndID`, getters, `SetRestore`, `SetPrivileged`, `LogPath`, `DisableFips`, `UserRequestedImage`, `ReadOnly`, `AddUnifiedResourcesFromAnnotations`, `SpecSetProcessArgs`, `WillRunSystemd`, `SpecSetupCapabilities`, `SpecSetPrivileges`, and `SpecSetLinuxContainerResources`.

Control flow: construction creates a runtime-tools generator for `runtime.GOOS`. `SetConfig` validates metadata/name and sandbox config exactly once. `SetNameAndID` generates or reuses an ID and constructs the Kubernetes container name. Annotation setup writes CRI-O/Kubernetes/image/sandbox metadata, labels, volumes, IPs, seccomp reference, stop signal, and systemd properties. Process args merge Kubernetes command/args with image entrypoint/cmd. Capability setup clears defaults, handles add/drop `ALL`, validates against kernel-supported capabilities, and writes bounding/effective/permitted/inheritable sets. Privileges set privileged mode or normal capabilities/masked paths. Resources apply CPU, memory, swap, cpusets, hugepages, and cgroup v2 unified settings.

State and persistence behavior: all state is in-memory on `container` and its OCI generator. It reads no files directly, but log path validation and node cgroup helpers consult host state through imported utilities.

Dependencies/integration points: integrates CRI API types, OCI image/runtime specs, runtime-tools generator, CRI-O annotations/constants/storage/config, capabilities, cgroup manager checks, node capability detection, nsmgr, kubelet labels, and logging.

Risks: very broad integration surface. `WillRunSystemd` assumes process args exist. `ReadOnly` dereferences `GetSecurityContext` through generated getters and relies on protobuf nil behavior. Capability and resource behavior are host-dependent. Annotation keys are security/compatibility sensitive. `Load`-time config validation must prevent inconsistent inputs where possible.

Test signals: focused tests cover config validation, name/ID generation, privileged gating, and log path behavior; many spec-generation paths are tested elsewhere or not in this subset.
