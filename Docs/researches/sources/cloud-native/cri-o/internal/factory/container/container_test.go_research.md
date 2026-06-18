# sources/cloud-native/cri-o/internal/factory/container/container_test.go

## Purpose
Exercises the factory-level container object that builds OCI specs from CRI container and pod sandbox input. The tests document expected behavior for mounts, annotations, image command resolution, privilege/capability setup, Linux resources, SELinux label generation, read-only and restore flags, and systemd detection.

## Important APIs, Types, And Functions
- Uses the package-level `sut container.Container` from `suite_test.go`, especially `SetConfig`, `Spec`, `SpecAddMount`, `SpecAddAnnotations`, `DisableFips`, `UserRequestedImage`, `ReadOnly`, `SetRestore`, `SelinuxLabel`, `AddUnifiedResourcesFromAnnotations`, `SpecSetProcessArgs`, `WillRunSystemd`, `SpecSetupCapabilities`, `SpecSetPrivileges`, and `SpecSetLinuxContainerResources`.
- Builds CRI `types.ContainerConfig` and `types.PodSandboxConfig`, OCI `rspec` mounts/resources, image-spec `v1.Image`, CRI-O `sandbox.Builder`, and storage image reference objects.
- Uses CRI-O annotation constants as the contract for `SpecAddAnnotations`.

## Control Flow
Each Ginkgo `Describe` block sets up minimal CRI input, calls a single container factory method, and asserts the resulting OCI generator state. Annotation tests construct a realistic sandbox, image result, log path, metadata JSON, and volume JSON before validating every generated annotation. Process argument tests cover command, args, image entrypoint/cmd inheritance, and empty-command failure. Capability tests cover add/drop semantics including `ALL`, invalid capability names, inheritable propagation, and privileged all-capability setup.

## State And Persistence
The tests do not persist data to disk, but they verify state mutations inside the in-memory OCI spec generator: mounts are de-duplicated, annotations are populated, process args/capabilities/resources are written, unified cgroup entries are stored under `Linux.Resources.Unified`, and restore/read-only/FIPS decisions are derived from config state. The annotation test also validates that serialized CRI metadata/labels/volumes/annotations survive as JSON strings in the OCI spec.

## Dependencies And Integration Points
Integrates factory code with CRI API types, OCI runtime spec generation, image metadata, CRI-O storage reference parsing, sandbox builder output, kubelet labels, CRI-O annotation packages, hostport port mapping types, and Linux capability discovery from `moby/sys/capability`.

## Risks And Edge Cases
The suite highlights risks around missing image specs, invalid/empty process command resolution, invalid capability names, capability ordering/count assumptions, cgroup v2 unified resource decoding, minimum memory enforcement, swap less than memory, and annotation correctness for downstream OCI/runtime consumers. Some expectations depend on host capability discovery and runtime-spec defaults.

## Test Signals
This file is itself the primary signal for the factory container behavior. It asserts broad positive and negative paths and should catch regressions in OCI spec annotations, command resolution, resource validation, privilege handling, and default behavior.
